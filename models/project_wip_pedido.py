# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

class ProjectWipPedido(models.Model):
    _name = 'project.wip.pedido'
    _description = 'Orden de Pedido del Cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.depends('detalle_ids')
    def _compute_total_pedido(self):
        for record in self:
            total_pedido = 0
            for linea in record.detalle_ids:
                total_pedido += linea.cantidad_pedido
            record.total_pedido = total_pedido

    @api.depends('detalle_ids')
    def _compute_total_solicitado(self):
        for record in self:
            total_solicitado = 0
            for linea in record.detalle_ids:
                total_solicitado += linea.cantidad_solicitud
            record.total_solicitado = total_solicitado

    @api.depends('detalle_ids')
    def _compute_total_corte(self):
        for record in self:
            total_corte = 0
            for linea in record.detalle_ids:
                total_corte += linea.cantidad_corte
            record.total_corte = total_corte

    @api.depends('total_pedido','total_solicitado','total_corte')
    def _compute_porcentaje_corte(self):
       for record in self:
            porcentaje = 0.00
            if record.total_pedido != 0:
                if record.total_corte == 0:
                    porcentaje = (record.total_solicitado / record.total_pedido) * 100
                else:
                    porcentaje = (record.total_corte / record.total_pedido) * 100
            record.porcentaje_corte = porcentaje

    name = fields.Char(string='Folio', default='Nuevo')
    tarea_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea',
        required=True,
        copy=False
    )
    numero_tarea = fields.Char(string='Folio', store=True, related='tarea_id.numero_tarea')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        store=True,
        related='tarea_id.partner_id'
    )
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Dirección de entrega',
        store=True,
        related='tarea_id.partner_shipping_id'
    )
    fecha_pedido = fields.Date(string='Fecha Pedido', required=True, default=fields.Date.today())
    numero_orden = fields.Char(string='Numero Orden', store=True, related='tarea_id.numero_orden')
    numero_estilo = fields.Char(string='Numero Estilo', store=True, related='tarea_id.numero_estilo')
    numero_oc = fields.Char(string='Orden Corte', store=True, related='tarea_id.numero_oc')
    numero_linea = fields.Selection(string='Numero Línea', selection=[
        ('01', '00010'),
        ('02', '00020'),
        ('03', '00030'),
        ('04', '00040'),
        ('05', '00050'),
        ('06', '00060'),
        ('07', '00070'),
        ('08', '00080'),
        ('09', '00090'),
        ('10', '00100'),
        ('11', '00110'),
        ('12', '00120'),
        ('13', '00130'),
        ('14', '00140'),
        ('15', '00150'),
    ], store=True, related='tarea_id.numero_linea')
    mes_programacion = fields.Selection(string='Mes Programación', selection=[
        ('01', 'Enero'),
        ('02', 'Febrero'),
        ('03', 'Marzo'),
        ('04', 'Abril'),
        ('05', 'Mayo'),
        ('06', 'Junio'),
        ('07', 'Julio'),
        ('08', 'Agosto'),
        ('09', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
    ], store=True, related='tarea_id.mes_programacion')
    ayio_programacion = fields.Integer(string='Año Programación', store=True, related='tarea_id.ayio_programacion')
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Comercial',
        required=True,
        default=lambda self: self.env.user
    )
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('pedido', 'Pedido'),
        ('solicitado', 'Solicitado'),
        ('trazado', 'Trazado'),
        ('liquidado', 'Liquidado'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', string='Estado', tracking=True, copy=False)
    color_estilo = fields.Char(string="Color", store=True, related='tarea_id.color_estilo')
    detalle_ids = fields.One2many(
        comodel_name='project.wip.detalle.pedido',
        inverse_name='pedido_id',
        string='Detalle',
        copy=False
    )
    total_pedido = fields.Float(string='Total pedido', compute='_compute_total_pedido')
    total_solicitado = fields.Float(string='Total solicitado', compute='_compute_total_solicitado')
    total_corte = fields.Float(string='Total cortado', compute='_compute_total_corte')
    terminos = fields.Text(string='Términos')
    porcentaje_corte = fields.Float(string='Porcentaje', compute='_compute_porcentaje_corte', store=True)
    fecha_orden = fields.Date(string='Fecha orden', readonly=True)
    fecha_trazo = fields.Date(string='Fecha trazo', readonly=True)
    fecha_corte = fields.Date(string='Fecha corte', readonly=True)
    precio = fields.Float(string='Precio', digits='Product Price')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id
    )

    def aprobar_pedido(self):
        logger.info('********** Entro a la función aprobar_pedido')
        # ProjectWipPedido._compute_porcentaje_corte(self)
        total_pedido = 0.00
        total_solicitado = 0.00
        for productos in self.detalle_ids:
            productos.cantidad_solicitud = productos.cantidad_pedido
            total_pedido += productos.cantidad_pedido
            total_solicitado += productos.cantidad_solicitud
        self.total_pedido = total_pedido
        self.total_solicitado = total_solicitado
        self.state = 'pedido'
        self.fecha_pedido = fields.Datetime.now()
        etapa_pedido = self.env.ref('wip_confetex.project_stage_1').id
        self.env['project.task'].browse(self.tarea_id.id).write({'stage_id': etapa_pedido})
        # Creamos lista de preciosn en el módulo de ventas
        precio = self.precio
        vals = {
            'name': self.tarea_id.name,
            'numero_orden': self.numero_orden or False,
            'numero_estilo': self.numero_estilo or False,
            'numero_oc': self.numero_oc or False,
            'numero_linea': self.numero_linea or False,
            'partner_id': self.partner_id.id,
            'precio': precio,
            'currency_id': self.currency_id.id,
        }
        self.env['sale.wip.lista.precios'].create(vals)
        # Actualizo precio en productos
        productos = self.env['product.product'].search([('default_code', '=', self.numero_estilo)])
        for producto in productos:
            print(producto.name)
            producto.lst_price = precio
            producto.standard_price = precio
        self.precio = 0.00

    def solicitar_corte(self):
        logger.info('********** Entro a la función solicitar_corte')
        # ProjectWipPedido._compute_porcentaje_corte(self)
        if not self.tarea_id.especificacion_id or not self.tarea_id.producto_tela_id or not self.tarea_id.producto_pocketing_id:
            raise UserError('No se puede solicitar un corte si no hay una especificación, tela o poketin asignado a '
                            'una tarea. Por favor asigne valores para poder continuar')
        else:
            total_solicitado = 0.00
            total_corte = 0.00
            for productos in self.detalle_ids:
                productos.cantidad_corte = productos.cantidad_solicitud
                total_solicitado += productos.cantidad_solicitud
                total_corte += productos.cantidad_corte
            self.total_solicitado = total_solicitado
            self.total_corte = total_corte
            self.state = 'solicitado'
            self.fecha_orden = fields.Datetime.now()
            tarea_brw = self.env['project.task'].browse(self.tarea_id.id)
            kanban_state = 'normal'
            if self.porcentaje_corte > 105.00:
                kanban_state = 'blocked'
            correlativo = tarea_brw.numero_oc
            if not correlativo:
                tipo_secuencia_oc = tarea_brw.estilo_id.tipo_secuencia_oc
                if tipo_secuencia_oc:
                    if tipo_secuencia_oc == '1':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc1')
                    elif tipo_secuencia_oc == '2':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc2')
                    elif tipo_secuencia_oc == '3':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc3')
                    elif tipo_secuencia_oc == '4':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc4')
                    elif tipo_secuencia_oc == '5':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc5')
                    elif tipo_secuencia_oc == '6':
                        sequence_obj = self.env['ir.sequence']
                        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc6')
                    else:
                        correlativo = self.tarea_id.numero_oc
            etapa_solicitud_corte = self.env.ref('wip_confetex.project_stage_25').id
            tarea_brw.write({'stage_id': etapa_solicitud_corte,
                             'numero_oc': correlativo,
                             'fecha_orden': fields.Datetime.now(),
                             'kanban_state': kanban_state})
            detalle_linea_proceso_id = 0
            for detallelp in tarea_brw.detalle_linea_proceso_ids:
                if detallelp.es_primer_proceso:
                    detalle_linea_proceso_id = detallelp.id
                    break
            if detalle_linea_proceso_id != 0:
                detalle_linea_proceso_brw = self.env['project.wip.task.detalle.linea.proceso'].browse(
                    detalle_linea_proceso_id)
                if not detalle_linea_proceso_brw.tarea_procesada:
                    vals = {
                        'name': detalle_linea_proceso_brw.name.name + ' ' + tarea_brw.name,
                        'project_id': detalle_linea_proceso_brw.proyecto_id.id or False,
                        'user_id': detalle_linea_proceso_brw.responsable_id.id or False,
                        'parent_id': tarea_brw.id,
                        'cpo_id': tarea_brw.cpo_id.id,
                        'stage_id': detalle_linea_proceso_brw.etapa_inicial_id.id or False,
                        'fecha_cancelacion': detalle_linea_proceso_brw.fecha_cancelacion or False,
                        'date_deadline': detalle_linea_proceso_brw.fecha_cancelacion or False,
                        'kanban_state': kanban_state
                    }
                    tarea_brw.copy(vals)
                    detalle_linea_proceso_brw.write({'tarea_procesada': True})

    def liquidar_trazo(self):
        logger.info('********** Entro a la función liquidar_trazo')
        # ProjectWipPedido._compute_porcentaje_corte(self)
        total_corte = 0.00
        for productos in self.detalle_ids:
            total_corte += productos.cantidad_corte
        self.total_corte = total_corte
        self.state = 'trazado'
        self.fecha_trazo = fields.Datetime.now()
        kanban_state = 'normal'
        if self.porcentaje_corte > 105.00:
            kanban_state = 'blocked'
        etapa_en_proceso = self.env.ref('wip_confetex.project_stage_2').id
        self.env['project.task'].browse(self.tarea_id.id).write({
            'stage_id': etapa_en_proceso,
            'kanban_state': kanban_state})

    def liquidar_corte(self):
        logger.info('********** Entro a la función liquidar_corte')
        # ProjectWipPedido._compute_porcentaje_corte(self)
        total_corte = 0.00
        for productos in self.detalle_ids:
            total_corte += productos.cantidad_corte
        self.total_corte = total_corte
        self.state = 'liquidado'
        self.fecha_corte = fields.Datetime.now()

    def cancelar_corte(self):
        logger.info('********** Entro a la función cancelar_corte')
        vals = {
            'hay_pedido': False,
            'cpo_id': False
        }
        self.env['project.task'].browse(self.tarea_id.id).write(vals)
        self.state = 'cancelado'

    def unlink(self):
        logger.info('********** Se disparo la función unlink')
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se puede cancelar el resgistro porque no se encuentra en estado cancelado')
            super(ProjectWipPedido, record).unlink()

    @api.model
    def create(self, vals_list):
        logger.info('********** Variables: {0}'.format(vals_list))
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.pedido')
        vals_list['name'] = correlativo
        nuevo_id = super(ProjectWipPedido, self).create(vals_list)
        vals = {
            'hay_pedido': True,
            'cpo_id': nuevo_id.id or False
        }
        self.env['project.task'].browse(vals_list['tarea_id']).write(vals)
        return nuevo_id

    def write(self, vals):
        logger.info('********** Variables: {0}'.format(vals))
        if 'tarea_id' in vals:
            if vals['tarea_id'] != self.tarea_id.id:
                vals_old = {
                    'hay_pedido': False,
                    'cpo_id': False
                }
                self.env['project.task'].browse(self.tarea_id.id).write(vals_old)
                vals_new = {
                    'hay_pedido': True,
                    'cpo_id': self.id or False
                }
                self.env['project.task'].browse(vals['tarea_id']).write(vals_new)
        return super(ProjectWipPedido, self).write(vals)

    def crear_detalle_productos(self):
        logger.info('********** Estas dentro del método: crear_detalle_productos')
        for record in self:
            productos = self.env['product.product'].search([('default_code', '=', record.numero_estilo), ('barcode', '!=', False)])
            productos_ordenados = productos.sorted(key=lambda p: p.talla)
            detalle_p = []
            for linea in productos_ordenados:
                detalle_p.append([0, 0, {
                    'name': linea.id,
                    'barcode': linea.barcode,
                }])
            record.detalle_ids = detalle_p

    def eliminar_detalle_productos(self):
        logger.info('********** Estas dentro del método: eliminar_detalle_productos')
        for record in self:
            for linea in record.detalle_ids:
                linea.unlink()

    def eliminar_productos_cantidad_0(self):
        logger.info('********** Estas dentro del método: eliminar_productos_cantidad_0')
        for record in self:
            for linea in record.detalle_ids:
                if linea.cantidad_pedido == 0:
                    linea.unlink()

    def incrementar_cantidad_solicitada(self):
        logger.info('********** Estas dentro del método: incrementar_cantidad_solicitada')
        for record in self:
            for linea in record.detalle_ids:
                cantidad_pedido = linea.cantidad_pedido
                if cantidad_pedido > 0:
                    tabla_incrementar_pedido = self.env['project.wip.tabla.uno'].search([('cliente_id', '=', record.partner_id.id)])
                    for incremento in tabla_incrementar_pedido:
                        if cantidad_pedido >= incremento.limite_inferior  and cantidad_pedido <= incremento.limite_superior:
                            linea.cantidad_solicitud = cantidad_pedido + incremento.incremento
                            break
                        else:
                            linea.cantidad_solicitud = cantidad_pedido
                else:
                    linea.cantidad_solicitud = cantidad_pedido


class ProjectWipProductTemplate(models.Model):
    _inherit = 'product.template'

    numero_estilo = fields.Char(string='Estilo')

    def write(self, vals):
        logger.info('********** Variables: {0}'.format(vals))
        if 'default_code' in vals:
            if vals['default_code'] != False:
                self.numero_estilo = vals['default_code']
        return super(ProjectWipProductTemplate, self).write(vals)

    @api.model
    def create(self, vals_list):
        if 'default_code' in vals_list:
            vals_list['numero_estilo'] = vals_list['default_code']
        return super(ProjectWipProductTemplate, self).create(vals_list)

class ProjectWipProduct(models.Model):
    _inherit = "product.product"

    @api.depends('talla', 'largo')
    def _compute_tamayo(self):
        for record in self:
            tamayo = ''
            if record.talla != False:
                tamayo = record.talla
            if record.largo != False:
                tamayo = tamayo + ' ' + record.largo
            record.tamayo = tamayo

    def set_talla_largo(self):
        logger.info('********* entrando a acción de servidor set_talla_largo')
        for producto in self:
            producto.default_code = producto.numero_estilo
            if producto.combination_indices != False:
                micadena = producto.combination_indices.split(',')
                contador = 1
                for cadena in micadena:
                    if contador == 1:
                        product_template_attribute_value_id = int(cadena.strip())
                        product_attribute_value_id = self.env['product.template.attribute.value'].browse(product_template_attribute_value_id).product_attribute_value_id.id
                        producto.talla = self.env['product.attribute.value'].browse(product_attribute_value_id).name
                    if contador == 2:
                        product_template_attribute_value_id = int(cadena.strip())
                        product_attribute_value_id = self.env['product.template.attribute.value'].browse(product_template_attribute_value_id).product_attribute_value_id.id
                        producto.largo = self.env['product.attribute.value'].browse(product_attribute_value_id).name
                    contador = contador + 1
            else:
                print("combination_indices esta vacio")

    talla = fields.Char(string='Talla', required=False)
    largo = fields.Char(string='Largo', required=False)
    tamayo = fields.Char(string='Tamaño', store=True, compute='_compute_tamayo')


class WipProjectDetallePedido(models.Model):
    _name = 'project.wip.detalle.pedido'
    _description = 'Detalle orden de pedido del cliente'

    pedido_id = fields.Many2one(
        comodel_name='project.wip.pedido',
        string='Pedido',
        ondelete='cascade'
    )
    name = fields.Many2one(
        comodel_name='product.product',
        string='Producto'
    )
    numero_orden = fields.Char(string='Numero Orden', store=True, related='pedido_id.numero_orden')
    color_estilo = fields.Char(string="Color", store=True, related='pedido_id.color_estilo')
    cantidad_pedido = fields.Float(string='Cantidad de pedido', default=0.00, digits=(16,2))
    cantidad_solicitud = fields.Float(string='Cantidad solicitada', default=0.00, digits=(16,2))
    cantidad_corte = fields.Float(string='Cantidad cortada', default=0.00, digits=(16,2))
    barcode = fields.Char(string='UPC/EAN')
    numero_estilo = fields.Char(string='Estilo', store=True, related='pedido_id.numero_estilo')
    numero_oc = fields.Char(string='Orden Corte', store=True, related='pedido_id.numero_oc')
    talla = fields.Char(string='Talla', store=True, related='name.talla')
    largo = fields.Char(string='Largo', store=True, related='name.largo')
    tamayo = fields.Char(string='Tamaño', store=True, related='name.tamayo')
    weight = fields.Float(string='Peso', store=True, related='name.weight')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('pedido', 'Pedido'),
        ('solicitado', 'Solicitado'),
        ('trazado', 'Trazado'),
        ('liquidado', 'Liquidado'),
        ('cancelado', 'Cancelado'),
    ], related='pedido_id.state')
    numero_oc = fields.Char(string='Orden Corte', store=True, related='pedido_id.numero_oc')
    numero_linea = fields.Selection(string='Numero Línea', selection=[
        ('01', '00010'),
        ('02', '00020'),
        ('03', '00030'),
        ('04', '00040'),
        ('05', '00050'),
        ('06', '00060'),
        ('07', '00070'),
        ('08', '00080'),
        ('09', '00090'),
        ('10', '00100'),
        ('11', '00110'),
        ('12', '00120'),
        ('13', '00130'),
        ('14', '00140'),
        ('15', '00150'),
    ], store=True, related='pedido_id.numero_linea')
    sequence = fields.Integer(string='Secuencia', default=10,
                              help="Obtiene la secuencia de orden de las lineas de pedido")

    @api.onchange('name')
    def _onchance_name(self):
        if self.name:
            self.barcode = self.name.barcode


class ProjectWipTablaUno(models.Model):
    _name = 'project.wip.tabla.uno'
    _description = 'Tabla incremento en CPO'

    name = fields.Char(string='Movimiento', readonly=True)
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string="Cliente"
    )
    category_cliente_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoría Wip Cliente',
        default=lambda self: self.env.ref('wip_confetex.category_cliente_produccion')
    )
    limite_inferior = fields.Float(string='Límite inferior', digits=(16, 2))
    limite_superior = fields.Float(string='Límite superior', digits=(16, 2))
    incremento = fields.Float(string='Incremento', digits=(16, 2))
    sequence = fields.Integer(string='Secuencia', default=10)

    @api.model
    def create(self, vals_list):
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.tabla.uno')
        vals_list['name'] = correlativo
        return super(ProjectWipTablaUno, self).create(vals_list)