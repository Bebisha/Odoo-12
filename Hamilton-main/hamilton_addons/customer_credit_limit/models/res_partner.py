# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean(
        string='Check Credit Limit?',
        default=False
    )
    sale_amount = fields.Float(
        compute='sales_amount_for_partner',
        string='Sale Amount',
    )
    available_credit_limit = fields.Float(
        compute='sales_amount_for_partner',
        string="Available Limit",
        digits=(16, 2)
    )

    @api.onchange('over_credit')
    def onchange_credit(self):
        self.credit_limit = 0.0

    def sales_amount_for_partner(self):
        for partner in self:
            parent_id = self.search([('id', 'parent_of', partner.id),
                                     ('parent_id', '=', False)])
            child_ids = self.search([('id', 'child_of', parent_id.id)])
            due_limit = amount = 0.0
            if parent_id.over_credit:
                for sale in self.env['sale.order'].search(
                    [('partner_id', 'in', child_ids.ids),
                     ('state', '=', 'sale')]):
                    if sale.invoice_ids:
                        so_invoice_ids = sale.invoice_ids.filtered(
                            lambda inv: inv.state in (
                                'draft', 'cancel', 'credit_review'))
                        if so_invoice_ids:
                            amount += sale.amount_total
                    else:
                        amount += sale.amount_total
                parent_id.sale_amount = amount
                due_limit = parent_id.available_credit_limit = (
                    parent_id.credit_limit -
                    parent_id.sale_amount -
                    parent_id.credit)

        return due_limit
