# -*- coding: utf-8 -*-
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_months_id = fields.Many2one('lot.months', 'Month')
    lot_year_id = fields.Many2one('lot.year', 'Year')
