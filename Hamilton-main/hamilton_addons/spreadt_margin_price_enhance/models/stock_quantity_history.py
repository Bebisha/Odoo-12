# -*- coding: utf-8 -*-
from odoo import models


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    def open_table(self):
        if not self._context.get('is_consignee_location'):
            return super(StockQuantityHistory, self).open_table()
        # with margin and only is consignee location
        self.ensure_one()
        if self.compute_at_date:
            return super(StockQuantityHistory, self).open_table()
        else:
            self.env['stock.quant']._merge_quants()
            res = self.env.ref('stock.quantsact').read()[0]
            if not res['domain']:
                res['domain'] = []
            tree_view = self.env.ref('spreadt_margin_price_enhance.'
                                     'inventory_valuation_with_margin').id
            res['views'] = [(tree_view, 'tree')]
            res['domain'].append(('is_consignee_location', '=', True))
            return res
