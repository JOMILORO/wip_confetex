from odoo import fields, models, api

class StockMoveWip(models.Model):
    _inherit = "stock.move"

    partida = fields.Char(string='Partida', required=True, default="ZZZZzzzz")

class StockMoveLineWip(models.Model):
    _inherit = "stock.move.line"

    @api.model
    def create(self, values):
        # Add code here
        if 'move_id' in values:
            if 'lot_name' in values:
                lot_name = values['lot_name']
                stock_move = self.env['stock.move'].browse(values['move_id'])
                if (stock_move.partida != False) and (lot_name != False):
                    values['lot_name'] = stock_move.partida + '-' + lot_name
        return super(StockMoveLineWip, self).create(values)