# -*- coding:utf-8 -*-

from odoo import fields, models, api

class EstiloTaskWizard(models.TransientModel):
    _name = "estilo.task.wizard"
    _description = "Estilo Task Wizard"

    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        estilo_brw = self.env['project.wip.estilo'].browse(active_id)
        name = estilo_brw.name
        return name

    def get_cliente(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        estilo_brw = self.env['project.wip.estilo'].browse(active_id)
        cliente_id = estilo_brw.cliente_id.id
        return cliente_id

    name = fields.Char(string='Nombre de tarea', default=get_name, required=False)
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
        default=lambda self: self.env.ref('wip_confetex.project_config_project_01'),
        required=False)
    numero_orden = fields.Char(string='Numero de Orden', required=False)
    fecha_orden = fields.Date(string='Fecha Inicio', required=False, default=lambda self: fields.Datetime.now())
    dead_line = fields.Date(string='Fecha límite', required=False)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Asignado a',
        default=lambda self: self.env.uid,
        index=True,
        required=False)
    cantidad_programada = fields.Float(string='Programada',  required=False)
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string="Cliente",
        default=get_cliente
    )
    partner_shipping_id = fields.Many2one(
        comodel_name='res.partner',
        string='Dirección de entrega',
        required=False)
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

    def create_task(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        estilo_brw = self.env['project.wip.estilo'].browse(active_id)

        correlativo = False
        if estilo_brw.es_secuencia_automatica:
            if estilo_brw.tipo_secuencia_oc == '1':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc1')
            if estilo_brw.tipo_secuencia_oc == '2':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc2')
            if estilo_brw.tipo_secuencia_oc == '3':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc3')
            if estilo_brw.tipo_secuencia_oc == '4':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc4')
            if estilo_brw.tipo_secuencia_oc == '5':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc5')
            if estilo_brw.tipo_secuencia_oc == '6':
                sequence_obj = self.env['ir.sequence']
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.task.seqoc6')
        else:
            correlativo = False

        lineas_proceso = self.env['project.wip.linea.proceso'].search([('valor_por_defecto', '=', True)])
        detalle_lp = []
        for lp in lineas_proceso:
            detalle_lp.append([0, 0, {
                'name': lp.id,
                'responsable_id': lp.responsable_id.id,
                'proyecto_id': lp.proyecto_id.id,
                'etapa_inicial_id': lp.etapa_inicial_id.id,
                'es_primer_proceso': lp.es_primer_proceso or False,
                'seguimiento': lp.seguimiento or False
            }])

        vals = {
            'name': self.name,
            'numero_orden': self.numero_orden or False,
            'project_id': self.project_id.id or False,
            'user_id': self.user_id.id or False,
            'fecha_orden': self.fecha_orden,
            'date_deadline': self.dead_line or False,
            'fecha_cancelacion': self.dead_line or False,
            'partner_id': self.cliente_id.id or False,
            'partner_shipping_id': self.partner_shipping_id.id or False,
            'estilo_id': estilo_brw.id or False,
            'numero_estilo': estilo_brw.numero_estilo or False,
            'cantidad_programada': self.cantidad_programada or False,
            'numero_oc': correlativo,
            'detalle_linea_proceso_ids': detalle_lp,
            'color_estilo': estilo_brw.color_estilo,
            'numero_linea': self.numero_linea,
            'fecha_entrega': self.dead_line
        }
        self.env['project.task'].create(vals)