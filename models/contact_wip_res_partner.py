# -*- coding:utf-8 -*-

from odoo import fields, models, api

class ContactWipResPartner(models.Model):
    _inherit = 'res.partner'

    extension_telefono = fields.Char(string="Extensión telefónica", required=False)
    email_corporativo = fields.Char(string="Correo corpotativo", required=False)
