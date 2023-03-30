# -*- coding:utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import ValidationError

class ProjectWipEstilo(models.Model):
    _name = 'project.wip.estilo'

    def wip_task_count(self):
        wip_task_obj = self.env['project.task']
        self.wip_task_numero = wip_task_obj.search_count([('project_id.es_proyecto_general', '=', True), ('estilo_id', 'in', [a.id for a in self])])

    def wip_especificacion_count(self):
        wip_especificacion_obj = self.env['project.wip.especificacion']
        self.wip_especificacion_numero = wip_especificacion_obj.search_count([('estilo_id', 'in', [a.id for a in self])])

    def variantes_producto_count(self):
        product_obj = self.env['product.product']
        self.variantes_producto_numero = product_obj.search_count([('default_code', '=', self.numero_estilo)])

    name = fields.Char(string='Nombre')
    numero_estilo = fields.Char(string='Número')
    cliente_id = fields.Many2one(
        comodel_name='res.partner',
        string="Cliente"
    )
    category_cliente_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoría Wip Cliente',
        default=lambda self: self.env.ref('wip_confetex.category_cliente_produccion')
    )
    agente_ventas_id = fields.Many2one(
        comodel_name='res.users',
        string='Agente de Ventas',
        default=lambda self: self.env.user,
        tracking=True
    )
    genero_ids = fields.Many2many(
        comodel_name='project.wip.estilo.genero',
        string='Genero'
    )
    active = fields.Boolean(string='Activo', default=True)
    comentario = fields.Text(string='Comentario')
    wip_task_numero = fields.Integer(string='Tareas', compute='wip_task_count', required=False)
    wip_especificacion_numero = fields.Integer(string='Especificaciones', compute='wip_especificacion_count')
    es_secuencia_automatica = fields.Boolean(string='SQ Automática', copy=False, default=False)
    tipo_secuencia_oc = fields.Selection(string='Secuencia OC', selection=[
        ('1', 'SEQOC1'),
        ('2', 'SEQOC2'),
        ('3', 'SEQOC3'),
        ('4', 'SEQOC4'),
        ('5', 'SEQOC5'),
        ('6', 'SEQOC6'),
    ], copy=False, required=False)
    tipo_estilo = fields.Selection(string='Tipo', selection=[
        ('1', 'Producción'),
        ('2', 'Muestra'),
    ], default='1', required=False)
    color_estilo = fields.Char(string="Color", required=False)
    variantes_producto_numero = fields.Integer(string='Productos', compute='variantes_producto_count', required=False)

    # @api.onchange('cliente_id')
    # def _onchange_secuencia_automatica(self):
    #     if self.cliente_id:
    #         contacto_brw = self.env['res.partner'].browse(self.cliente_id.id)
    #         self.es_secuencia_automatica = contacto_brw.es_secuencia_automatica
    #         self.tipo_secuencia_oc = contacto_brw.tipo_secuencia_oc
    #     else:
    #         self.es_secuencia_automatica = False

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + ' (Copia)'
        default['numero_estilo'] = self.numero_estilo + '_X'
        return super(ProjectWipEstilo, self).copy(default)

    _sql_constraints = [
        ('numero_estilo_unique',
         'UNIQUE(numero_estilo)',
         "El número de estilo debe de ser único, busque o vuelva " +
         "a intentarlo si no lo encuentra por favor verifique que el estilo se encuentre activo."),
    ]

    def copiar_plantilla_producto(self):
        if self.name and self.numero_estilo:
            plantilla_producto_obj = self.env['product.template']
            plantilla_producto_numero = plantilla_producto_obj.search_count([('default_code', '=', self.numero_estilo)])
            if plantilla_producto_numero > 0:
                raise UserError('No se puede crear la plantilla de producto porque ya fue creado con anterioridad, por favor verifique el número de estilo.')
            else:
                producto_copy_obj = self.env.ref('wip_confetex.wip_product_product_1')
                vals = {
                    'name': self.name,
                    'default_code': self.numero_estilo,
                    'active': True
                }
                producto_copy_obj.copy(vals)

    def name_get(self):
        # name get function for the model executes automatically
        res = []
        for rec in self:
            res.append((rec.id, '%s - %s' % (rec.numero_estilo, rec.name)))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|', ('numero_estilo', operator, name), ('name', operator, name)] + args, limit=limit)
        return recs.name_get()

class ProjectWipEstiloGenero(models.Model):
    _name = "project.wip.estilo.genero"
    _order = "name"

    name = fields.Char()