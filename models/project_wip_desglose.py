# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

class ProjectWipDesglose(models.Model):
    _name = 'project.wip.desglose'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.depends('cantidad_asignada', 'cantidad_total')
    def _compute_diferencia(self):
        for record in self:
            record.diferencia = record.cantidad_asignada - record.cantidad_total

    @api.depends('bultos_ids')
    def _compute_total_cantidad_bulto(self):
        for record in self:
            total_cantidad_bulto = 0.00
            for bulto in record.bultos_ids:
                total_cantidad_bulto += bulto.cantidad_1
            record.total_cantidad_bulto = total_cantidad_bulto


    name = fields.Char(string='Folio', index=True, copy=False, readonly=True)
    categoria_id = fields.Many2one(
        comodel_name='project.wip.desglose.clasificacion',
        string='Categoría',
        required=False,
        copy=False,
        default=lambda self: self.env.ref('wip_confetex.trazo_desglose_clasificacion_03')
    )
    categoria_nombre = fields.Char(string="Nombre categoria", required=False, store=True)
    tarea_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea',
        index=True,
        tracking=True,
        required=False
    )
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
    numero_orden = fields.Char(string='Numero Orden', index=True, store=True, related='tarea_id.numero_orden')
    numero_estilo = fields.Char(string='Numero Estilo', index=True, store=True, related='tarea_id.numero_estilo')
    numero_oc = fields.Char(string='Orden Corte', index=True, store=True, related='tarea_id.numero_oc')
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
    color_estilo = fields.Char(string="Color", store=True, related='tarea_id.color_estilo')
    producto_tela_id = fields.Many2one(
        comodel_name='product.product',
        string='Tela',
        copy=False
    )
    tag_ids = fields.Many2many(
        comodel_name='project.tags',
        string='Etiquetas'
    )
    cantidad_asignada = fields.Float(string='Cantidad asignada', tracking=True, default=0.00, digits=(16, 2))
    url = fields.Char(string='URL del documento', tracking=True, copy=False)
    ancho_tela = fields.Float(string='Ancho tela', digits='Product Price', tracking=True, copy=False, default=0.00)
    uom_tela_id = fields.Many2one(
        comodel_name='uom.uom',
        string='UDM tela',
        tracking=True,
        required=False,
        default=lambda self: self.env.ref('uom.product_uom_meter')
    )
    observacion_partida = fields.Text(string='Observaciones partida', copy=False)
    partida_ids = fields.Many2many(
        comodel_name='stock.move',
        string='Partida',
        copy=False
    )
    fecha_fin = fields.Date(string='Fecha fin', readonly=True, copy=False)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('desglose', 'Desglose'),
        ('trazo', 'Trazo'),
        ('finalizado', 'Finalizado'),
        ('bulto', 'Captura bulto'),
        ('hecho', 'Hecho'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', string='Estado', tracking=True, copy=False)
    promedio = fields.Float(string='Promedio tela', digits='Product Price', copy=False)
    cantidad_total = fields.Float(string='Cantidad total', tracking=True, default=0.00, digits=(16, 2))
    proyecto_id = fields.Many2one(
        comodel_name='project.project',
        string='Projecto default',
        required=True,
        default=lambda self: self.env.ref('wip_confetex.project_config_project_02')
    )
    active = fields.Boolean(string='Activo', default=True)
    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Etapa',
        required=False,
        default=lambda self: self.env.ref('wip_confetex.project_stage_7')
    )
    diferencia = fields.Float(string='Diferencia', digits=(16, 2), compute='_compute_diferencia')
    metros_totales_tela = fields.Float(string='Metros totales 1', digits=(16, 2), tracking=True, copy=False)
    observacion_tela = fields.Text(string='Observaciones tela')
    observacion_general = fields.Text(string='Observacion general')
    bultos_ids = fields.One2many(
        comodel_name='project.wip.bulto',
        inverse_name='desglose_id',
        string='Bultos',
        copy=False
    )
    fecha_inicio_bulto = fields.Date(string='Fecha inicio bulto')
    fecha_fin_bulto = fields.Date(string='Fecha fin bulto')
    observacion_bulto = fields.Text(string='Observaciones bulto')
    total_cantidad_bulto = fields.Float(string='Cantidad Total', compute='_compute_total_cantidad_bulto', digits=(16, 2))
    promedio_final_trazo = fields.Float(string='P.F.T.', digits='Product Price', tracking=True, copy=False, default=0.00)

    def capturar_desglose(self):
        logger.info('********** Entro a la función capturar_desglose')
        if self.categoria_id.id == self.env.ref('wip_confetex.trazo_desglose_clasificacion_03').id:
            tarea_brw = self.env['project.task'].browse(self.tarea_id.id)
            etapa_desglose_corte = self.env.ref('wip_confetex.project_stage_8').id
            kanban_state = 'normal'
            if tarea_brw.kanban_state == 'blocked':
                kanban_state = tarea_brw.kanban_state
            tarea_brw.write({'stage_id': etapa_desglose_corte,
                             'kanban_state': kanban_state})
        self.state = 'desglose'

    def trazar_desglose(self):
        logger.info('********** Entro a la función trazar_desglose')
        if self.categoria_id.id == self.env.ref('wip_confetex.trazo_desglose_clasificacion_03').id:
            tarea_brw = self.env['project.task'].browse(self.tarea_id.id)
            etapa_trazo_corte = self.env.ref('wip_confetex.project_stage_9').id
            kanban_state = 'normal'
            if tarea_brw.kanban_state == 'blocked':
                kanban_state = tarea_brw.kanban_state
            tarea_brw.write({'stage_id': etapa_trazo_corte,
                             'kanban_state': kanban_state})
        self.state = 'trazo'

    def finalizar_desglose(self):
        logger.info('********** Entro a la función finalizar_desglose')
        if self.categoria_id.id == self.env.ref('wip_confetex.trazo_desglose_clasificacion_03').id:
            tarea_brw = self.env['project.task'].browse(self.tarea_id.id)
            kanban_state = 'done'
            if tarea_brw.kanban_state == 'blocked':
                kanban_state = tarea_brw.kanban_state
            tarea_brw.write({'kanban_state': kanban_state})
        self.state = 'finalizado'
        self.fecha_fin = fields.Datetime.now()

    def capturar_bulto(self):
        logger.info('********** Entro a la capturar_bulto')
        self.fecha_inicio_bulto = fields.Datetime.now()
        self.state = 'bulto'

    def finalizar_bulto(self):
        logger.info('********** Entro a la finalizar_bulto')
        self.fecha_fin_bulto = fields.Datetime.now()
        self.cantidad_total = self.total_cantidad_bulto
        self.onchange_promedio()
        self.state = 'hecho'

    def cancelar_desglose(self):
        logger.info('********** Entro a la función cancelar_desglose')
        if self.categoria_id.id == self.env.ref('wip_confetex.trazo_desglose_clasificacion_03').id:
            tarea_brw = self.env['project.task'].browse(self.tarea_id.id)
            etapa_programacion_corte = self.env.ref('wip_confetex.project_stage_0').id
            kanban_state = 'done'
            if tarea_brw.kanban_state == 'blocked':
                kanban_state = tarea_brw.kanban_state
            tarea_brw.write({'stage_id': etapa_programacion_corte,
                             'kanban_state': kanban_state})
        self.state = 'cancelado'

    def generar_subtotales_bulto(self):
        logger.info('********** Entro a la función generar_subtotales_bulto')
        total_bft = 0.00
        total_bftl = 0.00
        for bulto in self.bultos_ids:
            total_bft += bulto.cantidad_1
            total_bftl += bulto.cantidad_1
            if bulto.nemo == 'BFT':
                bulto.cantidad_2 = total_bft
                total_bft = 0.00
            if bulto.nemo == 'BFTL':
                bulto.cantidad_2 = total_bft
                bulto.cantidad_3 = total_bftl
                total_bft = 0.00
                total_bftl = 0.00

    def unlink(self):
        logger.info('********** Se disparo la función unlink')
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se puede cancelar el resgistro porque no se encuentra en estado cancelado')
            super(ProjectWipDesglose, record).unlink()

    @api.model
    def create(self, vals_list):
        logger.info('********** Variables: {0}'.format(vals_list))
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.desglose')
        vals_list['name'] = correlativo
        return super(ProjectWipDesglose, self).create(vals_list)

    @api.onchange('tarea_id')
    def _onchance_tarea_id(self):
        if self.tarea_id:
            self.cantidad_asignada = self.tarea_id.total_solicitado
            self.cantidad_total = self.tarea_id.total_solicitado
        if self.categoria_id.id == 3:
            self.producto_tela_id = self.tarea_id.producto_tela_id.id
        elif self.categoria_id.id == 1:
            self.producto_tela_id = self.tarea_id.producto_pocketing_id.id
        else:
            self.producto_tela_id = False

    @api.onchange('metros_totales_tela', 'cantidad_total')
    def onchange_promedio(self):
        promedio = 0.00
        if self.cantidad_total > 0:
            promedio = self.metros_totales_tela / self.cantidad_total
        self.promedio = promedio

    @api.onchange('categoria_id')
    def onchange_categoria_nombre(self):
        categoria_nombre = ''
        if self.categoria_id:
            categoria_nombre = self.categoria_id.name
        self.categoria_nombre = categoria_nombre
        if self.categoria_id.id == 3:
            self.producto_tela_id = self.tarea_id.producto_tela_id.id
        elif self.categoria_id.id == 1:
            self.producto_tela_id = self.tarea_id.producto_pocketing_id.id
        else:
            self.producto_tela_id = False


class ProjectWipDesgloseClasificacion(models.Model):
    _name = "project.wip.desglose.clasificacion"
    _order = "name"

    name = fields.Char(string='Clasificación')

class ProjectWipBulto(models.Model):
    _name = 'project.wip.bulto'
    _order = 'desglose_id, sequence, id'

    @api.depends('sequence', 'desglose_id')
    def _compute_bulto_numero(self):
        for bulto in self:
            if not bulto.bulto_no:
                bulto_numero = 1
                for linea in bulto.mapped('desglose_id').bultos_ids:
                    linea.bulto_no = bulto_numero
                    bulto_numero += 1

    desglose_id = fields.Many2one(
        comodel_name='project.wip.desglose',
        string='Desglose',
        ondelete='cascade'
    )
    name = fields.Char(string='Identificador', index=True, copy=False, readonly=True)
    letra = fields.Char(string='Letra', required=False)
    sequence = fields.Integer(string='Secuencia', help="Obtiene la secuencia de orden de los bultos", default=10)
    talla = fields.Char(string='Talla', required=False)
    cantidad_1 = fields.Float(string='Cantidad', default=0.00, digits=(16, 2))
    trazo_numero = fields.Integer(string='Trazo', required=True, default=0)
    largo = fields.Char(string='Largo', required=False)
    nemo = fields.Selection(string='Nemo', selection=[
        ('B', 'B'),
        ('BFT', 'BFT'),
        ('BFTL', 'BFTL'),
    ], required=True, default='B')
    bulto_no = fields.Integer(string='Bulto#', compute='_compute_bulto_numero', store=True)
    numero_orden = fields.Char(string='Numero Orden', index=True, store=True, related='desglose_id.numero_orden')
    numero_estilo = fields.Char(string='Numero Estilo', index=True, store=True, related='desglose_id.numero_estilo')
    numero_oc = fields.Char(string='Orden Corte', index=True, store=True, related='desglose_id.numero_oc')
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
    ], store=True, related='desglose_id.numero_linea')
    color_estilo = fields.Char(string="Color", store=True, related='desglose_id.color_estilo')
    cantidad_2 = fields.Float(string='Total trazo', digits=(16, 2))
    cantidad_3 = fields.Float(string='Total largo', digits=(16, 2))
    barcode = fields.Char(string='UPC/EAN')
    proporcion = fields.Integer(string='Proporción', required=True, default=1)

    @api.model
    def create(self, vals_list):
        logger.info('********** Variables: {0}'.format(vals_list))
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.bulto')
        vals_list['name'] = correlativo
        return super(ProjectWipBulto, self).create(vals_list)

    @api.onchange('trazo_numero')
    def onchange_trazo_numero(self):
        if 0 < self.trazo_numero < 100:
            letras = (
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',
                'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ',
                'CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU'
            )
            self.letra = letras[self.trazo_numero - 1]
        else:
            self.letra = 'ZZzz'

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            productos = self.env['product.product'].search([('barcode', '=', self.barcode)], limit=1)
            for producto in productos:
                self.talla = producto.talla
                self.largo = producto.largo
