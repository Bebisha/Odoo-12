# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('partner_id')
    def _get_available_credit_limit(self):
        '''
        Set available credit limit on sale order based on customer
        :return: Set available credit limit
        '''
        for order in self:
            order.available_credit_limit = \
                order.partner_id.available_credit_limit
            if order and order.partner_id.parent_id:
                order.available_credit_limit = \
                    order.partner_id.parent_id.available_credit_limit

    confirm_check = fields.Boolean(
        compute="get_check_confirm",
        string='Is credit limit Over?'
    )

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('credit_review', 'CREDIT REVIEW')],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        track_visibility='onchange',
        default='draft'
    )
    credit_review_ids = fields.One2many(
        'credit.review.log',
        'sale_order_id',
        "Credit Review Log"
    )
    credit_limit = fields.Float(
        related='partner_id.credit_limit',
        string='Credit Limit'
    )
    credit = fields.Monetary(
        related='partner_id.credit',
        string='Total Receivable'
    )
    credit_due = fields.Float(
        compute="get_credit_due",
        string="Credit Due")
    available_credit_limit = fields.Float(
        compute='_get_available_credit_limit',
        string='Available Credit Limit', readonly=True)

    def get_credit_due(self):
        for sale in self:
            sale.credit_due = sale.partner_id.sales_amount_for_partner()

    @api.multi
    def action_confirm(self):
        for sale in self:
            parent_id = self.env['res.partner'].search(
                [('id', 'parent_of', sale.partner_id.id),
                 ('parent_id', '=', False)])
            if parent_id.over_credit:
                if self.env.context.get('review_log', False):
                    self.env['credit.review.log'].generate_credit_review_log(
                        user=sale.write_uid.id,
                        date=sale.write_date, sale_id=sale.id, inv_id=False)
        return super(SaleOrder, self).action_confirm()

    @api.depends('partner_id', 'order_line')
    def get_check_confirm(self):
        for sale in self:
            parent_id = self.env['res.partner'].search(
                [('id', 'parent_of', sale.partner_id.id),
                 ('parent_id', '=', False)])
            sale.confirm_check = False
            if parent_id:
                parent_id.sales_amount_for_partner()
                if parent_id.over_credit:
                    if sale.credit_due - \
                            sale.amount_total < 0:
                        sale.confirm_check = True

    @api.multi
    def action_credit_review(self):
        for sale in self:
            sale.state = 'credit_review'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if res:
            res.update({'sale_order_id': self.id})
        return res


class CreditReviewLog(models.Model):
    _name = 'credit.review.log'
    rec_name = 'review_user_id'
    _description = 'Log for credit review'

    review_user_id = fields.Many2one(
        'res.users',
        'Credit Review By',
        readonly=True
    )
    review_date = fields.Datetime(
        string="Credit Review Date",
        readonly=True
    )
    sale_order_id = fields.Many2one(
        'sale.order',
        'Sale Order Ref'
    )
    invoice_order_id = fields.Many2one(
        'account.invoice',
        'Invoice Ref')

    @api.multi
    def generate_credit_review_log(self, user, date, sale_id=False,
                                   inv_id=False):
        return self.create({'review_user_id': user,
                            'review_date': date,
                            'sale_order_id': sale_id,
                            'invoice_order_id': inv_id})
