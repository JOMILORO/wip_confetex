# -*- coding:utf-8 -*-

from datetime import datetime

from odoo import fields, models, api

class ProjectWipTask(models.Model):
    _inherit = "project.task"

    @api.depends('date_deadline')
    def _compute_programacion(self):
        for record in self:
            if record.date_deadline:
                meses = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
                record.mes_programacion = meses[record.date_deadline.month - 1]
                record.ayio_programacion = record.date_deadline.year

    @api.depends('fecha_orden', 'fecha_cancelacion')
    def _compute_dias_proceso(self):
        for record in self:
            if record.fecha_cancelacion:
                if record.fecha_cancelacion >= record.fecha_orden:
                    record.dias_proceso = (record.fecha_cancelacion - record.fecha_orden).days
                else:
                    record.dias_proceso = 0
            else:
                record.dias_proceso = 0

    @api.depends('movimiento_ids')
    def _compute_cantidad_recibida_liquidada(self):
        for record in self:
            cantidad_recibida = 0.00
            cantidad_liquidada = 0.00
            for movimiento in record.movimiento_ids:
                if movimiento.tipo == 'entrada':
                    cantidad_recibida += movimiento.cantidad_movimiento
                if movimiento.tipo == 'salida':
                    cantidad_liquidada += movimiento.cantidad_movimiento
            record.cantidad_por_liquidar = cantidad_recibida + cantidad_liquidada
            record.cantidad_recibida = cantidad_recibida
            record.cantidad_liquidada = cantidad_liquidada

    @api.depends('cantidad_liquidada', 'total_corte')
    def _compute_puntuacion(self):
        for record in self:
            porcentaje_proceso = 0
            if record.total_corte > 0:
                porcentaje_proceso = ((record.cantidad_liquidada * (-1)) / record.total_corte) * 100
            record.puntuacion = porcentaje_proceso

    estilo_id = fields.Many2one(
        comodel_name='project.wip.estilo',
        string='Nombre Estilo',
        required=False)
    numero_tarea = fields.Char(string='Folio',  readonly=True, copy=False, index=True)
    numero_linea = fields.Selection(string='Num. Linea', selection=[
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
    ], default='01')
    numero_orden = fields.Char(string='Num. Orden', tracking=True, index=True)
    numero_estilo = fields.Char(string='Num. Estilo', tracking=True, index=True)
    numero_oc = fields.Char(string='OC', tracking=True, index=True)
    fecha_orden = fields.Date(string='Fecha Inicio', tracking=True, required=True, default=fields.Date.today())
    fecha_cancelacion = fields.Date(string='Fecha Finalización', required=False)
    fecha_corte = fields.Date(string='Fecha Corte', readonly=True, store=True, related="cpo_id.fecha_corte")
    fecha_trazo = fields.Date(string='Fecha Trazo', readonly=True, store=True, related="cpo_id.fecha_trazo")
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
    ], compute='_compute_programacion', store=True, required=False)
    ayio_programacion = fields.Integer(string='Año Programación', compute='_compute_programacion', store=True, required=False)
    cantidad_programada = fields.Float(string='Cantidad Programada', tracking=True, required=False)
    dias_proceso = fields.Integer(string='Dias proceso', compute='_compute_dias_proceso', required=False, )
    especificacion_id = fields.Many2one(
        comodel_name='project.wip.especificacion',
        string='Especificación',
        tracking=True,
        required=False)
    especificacion_url = fields.Char(string='Url especificación', related='especificacion_id.url')
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Dirección de entrega',
        tracking=True,
        required=False)
    detalle_linea_proceso_ids = fields.One2many(
        comodel_name='project.wip.task.detalle.linea.proceso',
        inverse_name='tarea_id',
        string='Detalle proceso',
        required=False
    )
    hay_pedido = fields.Boolean(string='Hay pedido', default=False)
    cpo_id = fields.Many2one(
        comodel_name='project.wip.pedido',
        string='CPO',
        required=False
    )
    color_estilo = fields.Char(string='Color', required=False, copy=True)
    fecha_orden2 = fields.Date(string='Fecha orden', store=True, related="cpo_id.fecha_orden")
    total_pedido = fields.Float(string='Cantidad de pedido', store=True, related="cpo_id.total_pedido")
    total_solicitado = fields.Float(string='Cantidad solicitada', store=True, related="cpo_id.total_solicitado")
    total_corte = fields.Float(string='Cantidad cortada', store=True, related="cpo_id.total_corte")
    editar_tarea = fields.Boolean(string='Editar tarea', related="project_id.es_proyecto_general")
    movimiento_ids = fields.One2many(
        comodel_name='project.wip.task.movimiento',
        inverse_name='tarea_id',
        string='Movimientos',
        required=False
    )
    cantidad_por_liquidar = fields.Float(string='Por liquidar', store=True, compute='_compute_cantidad_recibida_liquidada', digits=(16, 2))
    cantidad_recibida = fields.Float(string="Recibido", store=True, compute='_compute_cantidad_recibida_liquidada', digits=(16,2))
    cantidad_liquidada = fields.Float(string="Liquidado", store=True, compute='_compute_cantidad_recibida_liquidada', digits=(16,2))
    es_tarea_liquidada = fields.Boolean(string="Liquidada", readonly=True)
    es_primera_parcialidad = fields.Boolean(string="Primera parcialidad",  default=False)
    puntuacion = fields.Integer(string="Avance", store=True, compute='_compute_puntuacion')
    fecha_entrega = fields.Date(string='Cancelación', tracking=True)
    descripcion_corta = fields.Char(string='Descripción corta', required=False)
    producto_tela_id = fields.Many2one(
        comodel_name='product.product',
        string='Tela',
        tracking=True
    )
    producto_pocketing_id = fields.Many2one(
        comodel_name='product.product',
        string='Pocketing',
        tracking=True
    )

    @api.model
    def create(self, vals_list):
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.task')
        vals_list['numero_tarea'] = correlativo
        return super(ProjectWipTask, self).create(vals_list)

    def crear_subtareas(self):
        kanban_state = 'normal'
        if self.cpo_id.porcentaje_corte > 105.00:
            kanban_state = 'blocked'
        for detallelp in self.detalle_linea_proceso_ids:
            nombre_subtarea = detallelp.name.name + ' ' + self.name
            if not detallelp.tarea_procesada:
                vals = {
                    'name': nombre_subtarea,
                    'project_id': detallelp.proyecto_id.id or False,
                    'user_id': detallelp.responsable_id.id or False,
                    'parent_id': self.id,
                    'stage_id': detallelp.etapa_inicial_id.id or False,
                    'fecha_orden': detallelp.fecha_orden,
                    'fecha_cancelacion': detallelp.fecha_cancelacion or False,
                    'date_deadline': detallelp.fecha_cancelacion or False,
                    'kanban_state': kanban_state
                }
                self.copy(vals)
                detallelp.tarea_procesada = True

    def enviar_cantidad_parcial(self):
        if self.es_tarea_liquidada is not True:
            for movimiento in self.movimiento_ids:
                if (movimiento.tipo == 'salida') and (movimiento.enviado is not True):
                    vals = {
                        'name': movimiento.name,
                        'tarea_id': movimiento.subtarea_destino_id.id,
                        'subtarea_destino_id': movimiento.tarea_id.id,
                        'fecha_movimiento': movimiento.fecha_movimiento or False,
                        'cantidad_captura': movimiento.cantidad_captura,
                        'enviado': True,
                        'tipo': 'entrada',
                        'state': 'parcial',
                        'descripcion': movimiento.descripcion or False
                    }
                    self.env['project.wip.task.movimiento'].create(vals)
                    if self.es_primera_parcialidad is not True:
                        self.env['project.task'].browse(movimiento.subtarea_destino_id.id).write({
                            'fecha_orden': fields.Date.today(),
                            'kanban_state': 'done'
                        })
                        self.es_primera_parcialidad = True
                    else:
                        self.env['project.task'].browse(movimiento.subtarea_destino_id.id).write({
                            'kanban_state': 'done'
                        })
                    movimiento.enviado = True

    def liquidar_cantidad(self):
        if self.es_tarea_liquidada is not True:
            ProjectWipTask.enviar_cantidad_parcial(self)
            for movimiento in self.movimiento_ids:
                movimiento.state = 'liquidado'
            self.fecha_cancelacion = fields.Date.today()
            self.stage_id = self.env.ref('wip_confetex.project_stage_7').id
            self.kanban_state = 'done'
            self.es_tarea_liquidada = True

    @api.onchange('date_deadline')
    def _onchance_date_deadline(self):
        for rec in self:
            tarea_padre = rec._origin.id
            sub_tareas = self.env['project.task'].search([('parent_id', '=', tarea_padre)])
            for st in sub_tareas:
                st.date_deadline = self.date_deadline

    @api.onchange('fecha_entrega')
    def _onchance_fecha_entrega(self):
        for rec in self:
            tarea_padre = rec._origin.id
            sub_tareas = self.env['project.task'].search([('parent_id', '=', tarea_padre)])
            for st in sub_tareas:
                st.fecha_entrega = self.fecha_entrega

    @api.onchange('especificacion_id')
    def _onchange_especificacion_id(self):
        for rec in self:
            tarea_padre = rec._origin.id
            sub_tareas = self.env['project.task'].search([('parent_id', '=', tarea_padre)])
            for st in sub_tareas:
                st.especificacion_id = self.especificacion_id

    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping_id(self):
        for rec in self:
            tarea_padre = rec._origin.id
            sub_tareas = self.env['project.task'].search([('parent_id', '=', tarea_padre)])
            for st in sub_tareas:
                st.partner_shipping_id = self.partner_shipping_id

    @api.onchange('cantidad_programada')
    def _onchange_cantidad_programada(self):
        for rec in self:
            tarea_padre = rec._origin.id
            sub_tareas = self.env['project.task'].search([('parent_id', '=', tarea_padre)])
            for st in sub_tareas:
                st.cantidad_programada = self.cantidad_programada

    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.numero_tarea, rec.name)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|', '|', ('numero_oc', operator, name), ('numero_tarea', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()


class ProjectWipProject(models.Model):
    _inherit = "project.project"

    es_proyecto_general = fields.Boolean(string='Proyecto general', default=False)

class ProjectWipTaskDetalleLineaProceso(models.Model):
    _name = "project.wip.task.detalle.linea.proceso"

    name = fields.Many2one(
        comodel_name='project.wip.linea.proceso',
        string='Linea Proceso'
    )
    tarea_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea',
        ondelete='cascade'
    )
    responsable_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsable',
    )
    proyecto_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
        required=False
    )
    fecha_orden = fields.Date(string='Fecha Inicio', required=True, default=fields.Date.today())
    fecha_cancelacion = fields.Date(string='Fecha Cancelacion', required=False)
    tarea_procesada = fields.Boolean(string="Procesado", default=False, readonly=True)
    sequence = fields.Integer(string='Secuencia', default=1)
    etapa_inicial_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Etapa inicial'
    )
    es_primer_proceso = fields.Boolean(string='Primer proceso')
    seguimiento = fields.Boolean(string='Seguimiento')

    @api.onchange('name')
    def _onchance_name(self):
        if self.name:
            self.responsable_id = self.name.responsable_id
            self.proyecto_id = self.name.proyecto_id
            self.etapa_inicial_id = self.name.etapa_inicial_id
            self.seguimiento = self.name.seguimiento

class ProjectWipTaskMovimiento(models.Model):
    _name = 'project.wip.task.movimiento'
    _description = 'Movimientos de entrada y salida asociados a una tarea'

    @api.depends('numero_tarea_padre')
    def _compute_numero_tarea_padre(self):
        for record in self:
            folio_tarea = ''
            if record.numero_tarea_padre:
                folio_tarea = record.numero_tarea_padre
            else:
                folio_tarea = record.tarea_id.numero_tarea
            record.folio_tarea_padre = folio_tarea

    @api.depends('cantidad_captura')
    def _compute_cantidad_movimiento(self):
        for record in self:
            cantidad_movimiento = 0.00
            if (record.tipo == 'salida') and (record.cantidad_captura > 0):
                cantidad_movimiento = record.cantidad_captura * (-1)
            else:
                cantidad_movimiento = record.cantidad_captura
            if record.tipo == 'entrada':
                cantidad_movimiento = record.cantidad_captura
            record.cantidad_movimiento = cantidad_movimiento

    name = fields.Char(string='Movimiento', index=True)
    tarea_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea',
        index=True,
        required=False
    )
    fecha_movimiento = fields.Date(string='Fecha', required=True, default=fields.Date.today())
    cantidad_captura = fields.Float(string='Cantidad', default=0.00, digits=(16,2))
    cantidad_movimiento = fields.Float(string='Cantidad Mov', digits=(16,2), compute='_compute_cantidad_movimiento', store=True)
    tipo = fields.Selection(string='Tipo', selection=[
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ], required=True, default='salida')
    nota_salida = fields.Char(string='Nota de salida', required=False)
    enviado = fields.Boolean(string='Enviado', readonly=True)
    state = fields.Selection(string='Estado', selection=[
        ('parcial', 'Parcial'),
        ('liquidado', 'Liquidado'),
    ], required=True, default='parcial', readonly=True)
    numero_oc = fields.Char(string='OC', related='tarea_id.numero_oc', index=True, store=True)
    subtarea_destino_id = fields.Many2one(
        comodel_name='project.task',
        string='Destino',
        required=False)
    numero_tarea_padre = fields.Char(string='Numero tarea padre', related='tarea_id.parent_id.numero_tarea')
    folio_tarea_padre = fields.Char(string='Folio tarea padre', compute='_compute_numero_tarea_padre')
    uom = fields.Many2one(
        comodel_name='uom.uom',
        string='UDM',
        required=True,
        default=lambda self: self.env.ref('uom.product_uom_unit')
    )
    numero_orden = fields.Char(string='Orden', related='tarea_id.numero_orden', index=True, store=True)
    numero_estilo = fields.Char(string='Estilo', related='tarea_id.numero_estilo', index=True, store=True)
    numero_linea = fields.Selection(string='Num. Línea', selection=[
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
    proyecto_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
        store=True,
        related='tarea_id.project_id'
    )
    descripcion = fields.Text(string='Descripción', required=False)


    @api.model
    def create(self, vals_list):
        tipo_mov = vals_list['tipo']
        if tipo_mov == 'salida':
            sequence_obj = self.env['ir.sequence']
            correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.movimiento')
            vals_list['name'] = correlativo
        return super(ProjectWipTaskMovimiento, self).create(vals_list)

    @api.onchange('subtarea_destino_id')
    def onchange_cantidad_captura(self):
        if self.subtarea_destino_id:
            acumulado = self.tarea_id.cantidad_por_liquidar
            if acumulado < 0:
                self.cantidad_captura = acumulado * (-1)
            else:
                self.cantidad_captura = acumulado

    @api.onchange('subtarea_destino_id')
    def onchange_descripcion(self):
        if self.subtarea_destino_id:
            self.descripcion = str(self.tarea_id.numero_tarea) + ' - ' + str(self.tarea_id.name) + ' Estilo: ' + str(self.numero_estilo) + ', Orden: ' + str(self.numero_orden) + ', OC: ' + str(self.numero_oc) + ', Linea: ' + str(self.numero_linea)