# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

class ProjectWipEspecificacion(models.Model):
    _name = "project.wip.especificacion"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    def wip_task_count(self):
        wip_task_obj = self.env['project.task']
        self.wip_task_numero = wip_task_obj.search_count([('especificacion_id', 'in', [a.id for a in self])])

    name = fields.Char(string='Nombre', tracking=True, index=True)
    estilo_id = fields.Many2one(
        comodel_name='project.wip.estilo',
        string='Nombre del estilo'
    )
    nombre_estilo = fields.Char(string="Nombre", related='estilo_id.name')
    numero_estilo = fields.Char(string='Numero', store=True, related='estilo_id.numero_estilo')
    cliente_estilo = fields.Char(string='Cliente', related='estilo_id.cliente_id.name')
    num_especificacion = fields.Char(string='Folio', copy=False, index=True)
    url = fields.Char(string='URL del documento', copy=False)
    categoria = fields.Many2one(
        comodel_name='project.wip.especificacion.tags',
        string='Categoría',
        default=lambda self: self.env.ref('wip_confetex.config_especificacion_tag_01'),
        tracking=True,
        required=False)
    nombre_corto_categoria = fields.Char(string='Nombre corto', related='categoria.nombre_corto')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', tracking=True, string='Estados', copy=False)
    fch_aprobado = fields.Datetime(string='Aprobado en', copy=False)
    version_id = fields.Many2one(
        comodel_name='project.wip.especificacion.version',
        string='Temporada',
        default=lambda self: self.env.ref('wip_confetex.config_especificacion_version_01')
    )
    es_archivo = fields.Boolean(string='Es archivo', copy=False)
    archivo_pdf = fields.Binary(string='Archivo PDF', copy=False)
    nombre_archivo = fields.Char(string='Nombre del archivo', required=False, copy=False)
    descripcion = fields.Html(string='Descripción', copy=False)
    tag_ids = fields.Many2many(
        comodel_name='project.tags',
        string='Categorías')
    wip_task_numero = fields.Integer(string='Tareas', compute='wip_task_count', required=False)

    def aprobar_especificacion(self):
        logger.info('********** Entro a la función aprobar_especificacion')
        self.state = 'aprobado'
        self.fch_aprobado = fields.Datetime.now()

    def cancelar_especificacion(self):
        logger.info('********** Entro a la función cancelar_especificacion')
        self.state = 'cancelado'

    def cambiar_borrador_especificacion(self):
        logger.info('********** Entro a la función cambiar_borrador_especificacion')
        self.state = 'borrador'

    def unlink(self):
        logger.info('********** Se disparo la función unlink')
        for record in self:
            if record.state != 'cancelado':
                raise UserError('No se puede cancelar el resgistro porque no se encuentra en estado cancelado')
            super(ProjectWipEspecificacion, record).unlink()

    @api.model
    def create(self, vals_list):
        logger.info('********** Variables: {0}'.format(vals_list))
        sequence_obj = self.env['ir.sequence']
        correlativo = sequence_obj.next_by_code('secuencia.project.wip.especificacion')
        vals_list['num_especificacion'] = correlativo
        return super(ProjectWipEspecificacion, self).create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + ' (Copia)'
        return super(ProjectWipEspecificacion, self).copy(default)

    @api.onchange('estilo_id','version_id','categoria')
    def _onchange_name(self):
        nombre_espec = ''
        if self.categoria:
            nombre_espec = self.nombre_corto_categoria
        if self.estilo_id:
            nombre_espec = nombre_espec + ' ' + self.numero_estilo + ' ' + self.nombre_estilo
        if self.version_id:
            nombre_espec = nombre_espec + ' Temporada ' + self.version_id.name
        self.name = nombre_espec

    _sql_constraints = [
        ('nombre_especificacion_unique',
         'UNIQUE(name)',
         "El nombre de la especificación debe de ser único, busque o vuelva " +
         "a intentarlo si no lo encuentra por favor verifique que el nombre de la especificación se encuentre activo."),
    ]

class ProjectWipEspecificacionVersion(models.Model):
    _name = "project.wip.especificacion.version"
    _order = "name"

    name = fields.Char()
