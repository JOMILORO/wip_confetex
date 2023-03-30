# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

class ProjectWipNotaSalida(models.Model):
    _name = 'project.wip.nota.salida'
    _order = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    @api.depends('movimientos_ids', 'linea_ids')
    def _compute_total_nota(self):
        for record in self:
            total_nota = 0
            total_linea = 0
            for linea in record.movimientos_ids:
                total_nota += linea.cantidad_captura
            for linea in record.linea_ids:
                total_linea += linea.cantidad_captura
            record.total_nota = total_nota + (total_linea * (-1))

    name = fields.Char(string='Folio', index=True, copy=False, readonly=True)
    fecha_nota = fields.Date(string='Fecha', tracking=True, required=True, default=fields.Date.today())
    remitente_empresa_id = fields.Many2one(
        comodel_name='project.wip.nota.salida.empresa',
        string='Empresa envia',
        required=True
    )
    remitente_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Remitente',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    autoriza_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Autoriza',
        required=True,
        default=lambda self: self.env.user,
        tracking=True
    )
    destinatario_empresa_id = fields.Many2one(
        comodel_name='project.wip.nota.salida.empresa',
        string='Empresa recibe',
        required=True
    )
    destinatario_user = fields.Char(string='Destinatario', required=False, copy=False)
    observacion = fields.Text(string='Observaciones', copy=False)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', string='Estado', tracking=True, copy=False)
    active = fields.Boolean(string='Activo', default=True)
    movimientos_ids = fields.Many2many(
        comodel_name='project.wip.task.movimiento',
        string='Movimientos',
        copy=False
    )
    proyecto_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
        required=True
    )
    total_nota = fields.Float(string='Total nota', compute='_compute_total_nota', store=True)
    fecha_nota_fin = fields.Date(string='Finalización', tracking=True, required=False)
    es_complemento = fields.Boolean(string='Nota complemento', default=False)
    linea_ids = fields.One2many(
        comodel_name='project.wip.nota.salida.linea',
        inverse_name='nota_salida_id',
        string='Linea'
    )

    def confirmar_nota(self):
        logger.info('********** Entro a la función confirmar_nota')
        if self.es_complemento != True:
            if self.name:
                for movimiento in self.movimientos_ids:
                    movimiento.nota_salida = self.name
        self.state = 'confirmado'

    def finalizar_nota(self):
        logger.info('********** Entro a la función finalizar_nota')
        self.fecha_nota_fin = fields.Datetime.now()
        self.state = 'finalizado'

    def cancelar_nota(self):
        logger.info('********** Entro a la función cancelar_nota')
        if self.es_complemento != True:
            for movimiento in self.movimientos_ids:
                movimiento.nota_salida = False
        self.state = 'cancelado'

    def unlink(self):
        logger.info('********** Se disparo la función unlink')
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se puede cancelar el resgistro porque no se encuentra en estado cancelado')
            super(ProjectWipNotaSalida, record).unlink()

    @api.model
    def create(self, vals_list):
        logger.info('********** Variables: {0}'.format(vals_list))
        sequence_obj = self.env['ir.sequence']
        if 'es_complemento' in vals_list:
            if vals_list['es_complemento']:
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.nota.salida.complemento')
            else:
                correlativo = sequence_obj.next_by_code('secuencia.project.wip.nota.salida')
            vals_list['name'] = correlativo
        return super(ProjectWipNotaSalida, self).create(vals_list)


class ProjectWipNotaSalidaEmpresa(models.Model):
    _name = "project.wip.nota.salida.empresa"
    _order = "name"

    name = fields.Char(string='Nombre')


class ProjectWipNotaSalidaLinea(models.Model):
    _name = "project.wip.nota.salida.linea"
    _order = "name"

    nota_salida_id = fields.Many2one(
        comodel_name='project.wip.nota.salida',
        string='Nota de salida',
        ondelete='cascade'
    )
    name = fields.Many2one(
        comodel_name='project.wip.task.movimiento',
        string='Movimiento',
        index=True,
    )
    descripcion = fields.Text(string='Descripción', required=False)
    cantidad_captura = fields.Float(string='Cantidad', digits=(16, 2))
    uom = fields.Many2one(
        comodel_name='uom.uom',
        string='UDM',
        required=True
    )
    fecha_movimiento = fields.Date(string='Fecha', required=True, default=fields.Date.today())
    estado_movimiento = fields.Selection(string='Estado', selection=[
        ('parcial', 'Parcial'),
        ('liquidado', 'Liquidado'),
    ], related='name.state')
    numero_oc = fields.Char(string='OC', related='name.numero_oc', index=True, store=True)
    numero_orden = fields.Char(string='Orden', related='name.numero_orden', index=True, store=True)
    numero_estilo = fields.Char(string='Estilo', related='name.numero_estilo', index=True, store=True)
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
    ], store=True, related='name.numero_linea')
    tipo = fields.Selection(string='Tipo', selection=[
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ], related='name.tipo')
    tarea_id = fields.Many2one(
        comodel_name='project.task',
        string='Tarea',
        related='name.tarea_id'
    )

    @api.onchange('name')
    def _onchance_name(self):
        if self.name:
            self.descripcion = self.name.descripcion
            self.cantidad_captura = self.name.cantidad_movimiento
            self.uom = self.name.uom
