# -*- coding:utf-8 -*-

from odoo import fields, models, api

class ProjectWipLineaProceso(models.Model):
    _name = 'project.wip.linea.proceso'
    _description = 'Lineas de proceso por la que un producto pasa'
    _order = "sequence"

    name = fields.Char(string='Proceso', required=True)
    responsable_id = fields.Many2one(comodel_name='res.users',
                                     string='Responsable',
                                     required=False)
    descripcion = fields.Text(string='Descripción', required=False)
    valor_por_defecto = fields.Boolean(string='Programable', default=False)
    sequence = fields.Integer(string='Secuencia', default=10, help="Obtiene la secuencia de orden de las lineas de proceso")
    proyecto_id = fields.Many2one(
        comodel_name='project.project',
        string='Proyecto',
        required=False
    )
    etapa_inicial_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Etapa inicial'
    )
    es_primer_proceso = fields.Boolean(string='Primer proceso')
    active = fields.Boolean(string='Activo', default=True)
    seguimiento = fields.Boolean(string='Seguimiento', default=True)

