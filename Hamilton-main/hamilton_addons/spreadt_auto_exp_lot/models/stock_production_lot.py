# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.onchange('product_id')
    def _onchange_product(self):
        if self._context.get('lot_months_id') and self._context.get(
                'lot_year_id'):
            lot_month_rec = self.env["lot.months"].browse(self._context.get(
                'lot_months_id'))
            lot_year_rec = self.env["lot.year"].browse(self._context.get(
                'lot_year_id'))
            date = datetime.strptime('%s-%s-01' % (
                lot_year_rec.year, lot_month_rec.month), "%Y-%m-%d")
            exp_date = date + relativedelta(years=3)
            exp_datea = datetime.combine(exp_date, datetime.min.time())
            date_exp = exp_datea.strftime('%Y-%m-%d %H:%M:%S')
            self.life_date = date_exp
            self.use_date = date_exp
            self.removal_date = date_exp
            self.alert_date = date_exp
            self.name = lot_year_rec.code + ' - ' + lot_month_rec.code
