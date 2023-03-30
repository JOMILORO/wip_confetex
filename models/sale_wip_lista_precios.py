# -*- coding:utf-8 -*-

import logging

from odoo import fields, models, api

class SaleWipListaPrecios(models.Model):
    _name = 'sale.wip.lista.precios'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Nombre', required=True, default='Nuevo precio', index=True, tracking=True)
    numero_orden = fields.Char(string='Numero Orden', tracking=True)
    numero_estilo = fields.Char(string='Numero Estilo')
    numero_oc = fields.Char(string='Orden Corte')
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
    ])
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        required=True
    )
    precio = fields.Float(string='Precio', digits='Product Price', required=True, tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id.id,
        required=True,
        tracking=True
    )
    category_partner_id = fields.Many2one(
        comodel_name='res.partner.category',
        string='Categoría Wip Cliente',
        default=lambda self: self.env.ref('wip_confetex.category_cliente_produccion')
    )
