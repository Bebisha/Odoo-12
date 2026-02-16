# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models
from odoo.tools.misc import formatLang


class account_journal(models.Model):
    _inherit = "account.journal"

    @api.multi
    def get_journal_dashboard_datas(self):
        number_credit_review = 0.0
        so_total_amt = 0.0
        currency = self.currency_id or self.company_id.currency_id
        res = super(account_journal, self).get_journal_dashboard_datas()
        sale_ids = self.env['sale.order'].search(
            [('state', '=', 'credit_review')])
        for sale in sale_ids:
            number_credit_review += 1
            so_total_amt += currency.compute(sale.amount_total, currency) * 1
        res.update({'number_credit_review': number_credit_review,
                    'so_total_amt': formatLang(
                        self.env, currency.round(so_total_amt) + 0.0,
                        currency_obj=currency)})
        return res

    @api.multi
    def open_so(self):
        ctx = self._context.copy()
        ctx.update({'tree_view_ref':
                    'customer_credit_limit.view_order_for_credit_tree'})
        action_rec = self.env['ir.model.data'].xmlid_to_object(
            'sale.action_orders')
        if action_rec:
            action = action_rec.read([])[0]
            action['context'] = ctx
            action['domain'] = [('state', '=', 'credit_review')]
            return action
