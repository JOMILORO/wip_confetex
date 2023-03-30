# -*- coding:utf-8 -*-

from odoo import fields, models, api
from random import randint

class ProjectWipEspecificacionTags(models.Model):
    _name = "project.wip.especificacion.tags"
    _description = "Especificación Tags"
    _order = "name"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Nombre', required=True)
    nombre_corto = fields.Char(string='Nombre corto', required=False)
    carpeta_drive = fields.Char(string='Carpeta URL', required=False)
    color = fields.Integer(string='Color', default=_get_default_color)
    descripcion = fields.Text(string="Descripción de categoría", required=False)
    directorio_unidad_compartida = fields.Char(string="Directorio GDUC", required=False)
    categoria_id = fields.Many2one(
        comodel_name='project.wip.canal.categoria',
        string='Categoría',
        required=False
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la etiqueta ya existe"),
    ]

class ProjectWipCanalCategoria(models.Model):
    _name = "project.wip.canal.categoria"
    _order = "name"

    name = fields.Char()