# -*- coding:utf-8 -*-

from odoo import fields,models, api

class EspecificacionWizard(models.TransientModel):
    _name = 'especificacion.wizard'
    _description = 'Especificación Wizard'

    def get_name(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        estilo_brw = self.env['project.wip.estilo'].browse(active_id)
        name = 'NUEVA ' + estilo_brw.numero_estilo + ' ' + estilo_brw.name
        return name

    name = fields.Char(string='Nombre de especificación', default=get_name)
    categoria_id = fields.Many2one(
        comodel_name='project.wip.especificacion.tags',
        string='Categoría')
    version_id = fields.Many2one(
        comodel_name='project.wip.especificacion.version',
        string='Versión')
    url = fields.Char(string='URL del documento')

    def create_especificacion(self):
        ctx = dict(self._context or {})
        active_id = ctx.get('active_id')
        estilo_brw = self.env['project.wip.estilo'].browse(active_id)

        vals = {
            'name': self.name or False,
            'estilo_id': estilo_brw.id or False,
            'categoria': self.categoria_id.id or False,
            'version_id': self.version_id.id or False,
            'url': self.url or False
        }
        self.env['project.wip.especificacion'].create(vals)