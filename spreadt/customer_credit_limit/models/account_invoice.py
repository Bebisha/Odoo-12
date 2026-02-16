# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    sale_order_id = fields.Many2one(
        'sale.order',
        'Sale Ref.',
        copy=False
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('proforma', 'Pro-forma'),
         ('proforma2', 'Pro-forma'),
         ('open', 'Open'),
         ('paid', 'Paid'),
         ('cancel', 'Cancelled'),
         ('credit_review', 'CREDIT REVIEW'), ],
        string='Status',
        index=True,
        readonly=True,
        default='draft',
        track_visibility='onchange',
        copy=False,
        help=" * The 'Draft' status is used when a user "
                "is encoding a new and unconfirmed Invoice.\n"
             " * The 'Pro-forma' status is used when the invoice "
                "does not have an invoice number.\n"
             " * The 'CREDIT REVIEW' status is used when the "
                "invoice when customer credit limit < 0 .\n"
             " * The 'Open' status is used when user creates invoice, an "
                "invoice number is generated. It stays in the open status "
                "till the user pays the invoice.\n"
             " * The 'Paid' status is set automatically when the invoice is "
                "paid. Its related journal entries may or may not "
                "be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice."
    )
    inv_confirm_check = fields.Boolean(
        compute="get_inv_check_confirm",
        string='Is credit limit Over?'
    )
    credit_review_ids = fields.One2many(
        'credit.review.log',
        'invoice_order_id',
        "Credit Review Log"
    )

    @api.multi
    def action_credit_review(self):
        for sale in self:
            sale.state = 'credit_review'

    @api.depends('partner_id', 'invoice_line_ids')
    def get_inv_check_confirm(self):
        for inv in self:
            parent_id = self.env['res.partner'].search(
                [('id', 'parent_of', inv.partner_id.id),
                 ('parent_id', '=', False)])
            inv.inv_confirm_check = False
            if parent_id:
                parent_id.sales_amount_for_partner()
                if parent_id.over_credit:
                    if inv.sale_order_id:
                        if parent_id.available_credit_limit + \
                                inv.sale_order_id.amount_total - \
                                inv.amount_total < 0:
                            inv.inv_confirm_check = True
                    else:
                        if parent_id.available_credit_limit - \
                                inv.amount_total < 0:
                            inv.inv_confirm_check = True

    @api.multi
    def action_invoice_open(self):
        for inv in self:
            parent_id = self.env['res.partner'].search(
                [('id', 'parent_of', inv.partner_id.id),
                 ('parent_id', '=', False)])
            if parent_id.over_credit:
                if self.env.context.get('review_log', False):
                    self.env['credit.review.log'].generate_credit_review_log(
                        user=inv.write_uid.id,
                        date=inv.write_date, sale_id=False, inv_id=inv.id)
                    inv.state = 'draft'
        return super(AccountInvoice, self).action_invoice_open()
