# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class MultipleInvoicePayment(models.TransientModel):
    _name = 'multiple.invoice.payment'
    _rec_name = 'partner_id'
    _description = 'To pay multiple invoice'

    payment_type = fields.Selection(
        [('outbound', 'Send Money'), ('inbound', 'Receive Money')],
        string='Payment Type')
    payment_date = fields.Date(
        string='Payment Date', default=fields.Date.context_today,
        copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner')
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one('account.journal', string='Payment Method',
                                 required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company',
                                 related='journal_id.company_id',
                                 string='Company', readonly=True)
    multi = fields.Boolean(string='Multi',
                           help='Technical field indicating if the user '
                                'selected multiple invoice.')
    total_amount = fields.Float('Total Amount')
    inv_pay_line_ids = fields.One2many(
        'multiple.invoice.payment.line', 'inv_pay_id', 'Invoices')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = \
                self.journal_id.currency_id or self.company_id.currency_id

    @api.model
    def _prepared_multi_inv_lines(self, invoices):
        """
        :return:
        """
        lines = []
        for inv_rec in invoices:
            vals = {'invoice_id': inv_rec.id,
                    'amount': inv_rec.residual,
                    'amount_to_pay': inv_rec.residual,
                    'currency_id': inv_rec.currency_id.id or False,
                    'writeoff_label': 'Write-Off'}
            lines.append((0, 0, vals))
        return lines

    @api.model
    def default_get(self, fields):
        rec = super(MultipleInvoicePayment, self).default_get(fields)
        active_ids = self._context.get('active_ids')

        # Check for selected invoices ids
        if not active_ids:
            raise UserError(_("Validation error: select at least one open "
                              "invoice to proceed."))
        invoices = self.env['account.invoice'].browse(active_ids)
        # Check all invoices are open
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(
                _("You can only register payments for open invoices"))
        # Check all invoices have the same currency
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, "
                              "they must use the same currency."))
        # Check all invoices have the same partner
        if any(inv_rec.partner_id != invoices[0].partner_id for inv_rec in
               invoices):
            raise UserError(_("In order to pay multiple invoices at once, "
                              "they must use the same Partners."))

        # Single/Multiple Invoice Payment
        multi = True if len(invoices) > 0 else False
        lines = []
        if multi:
            lines = self._prepared_multi_inv_lines(invoices)
        rec.update({
            'partner_id': invoices[0].partner_id.id,
            'communication': ' '.join([ref for ref in invoices.mapped(
                'reference') if ref]),
            'multi': multi,
            'inv_pay_line_ids': lines
        })
        return rec

    @api.multi
    def _prepare_payment_vals(self, line):
        """
        Create the payment values.
        :param line: record set contain invoice and payment amounts details
        :return: The payment values as a dictionary.
        """
        amount = line.amount_to_pay
        payment_type = line.invoice_id.type in (
            'out_invoice', 'in_refund') and 'inbound' or 'outbound'
        currency_id_rec = \
            self.currency_id or self.journal_id.currency_id or \
            self.journal_id.company_id.currency_id or \
            line.invoice_id.currency_id
        payment_methods = \
            payment_type == 'inbound' and \
            self.journal_id.inbound_payment_method_ids or \
            self.journal_id.outbound_payment_method_ids
        payment_method_id = \
            payment_methods and payment_methods[0] and payment_methods[0].id\
            or False
        payment_vals = {
            'journal_id': self.journal_id.id,
            'payment_method_id': payment_method_id,
            'payment_date': self.payment_date,
            'payment_type': payment_type,
            'communication': self.communication,
            'invoice_ids': [(6, 0, line.invoice_id.ids)],
            'amount': abs(amount),
            'currency_id': currency_id_rec.id,
            'partner_id': self.partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[
                line.invoice_id.type],
        }
        if line.payment_difference_handling == 'reconcile':
            payment_vals.update({
                'payment_difference_handling':
                    line.payment_difference_handling,
                'writeoff_account_id': line.writeoff_account_id.id or False,
                'writeoff_label': line.writeoff_label,
            })
        return payment_vals

    @api.multi
    def proceed_to_payment(self):
        """
        :return:
        """
        Payment = self.env['account.payment']
        payment_rec = Payment
        for line in self.inv_pay_line_ids:
            if line.amount_to_pay > 0:
                payment_vals = self._prepare_payment_vals(line)
                payment_rec += Payment.create(payment_vals)
        payment_rec.post()
        return {
            'name': _('Payments'),
            'domain': [('id', 'in', payment_rec.ids),
                       ('state', '=', 'posted')],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


class MultipleInvoicePaymentLine(models.TransientModel):
    _name = 'multiple.invoice.payment.line'
    _description = 'Payment line for multiple invoices'

    @api.model
    def _compute_total_invoices_amount(self):
        """ Compute the sum of the residual of invoices, expressed in the
        payment currency """
        payment_currency = \
            self.pay_currency_id or self.inv_pay_id.currency_id or \
            self.inv_pay_id.journal_id.currency_id or \
            self.inv_pay_id.journal_id.company_id.currency_id or \
            self.env.user.company_id.currency_id
        total = 0
        for inv in self.invoice_id:
            if inv.currency_id == payment_currency:
                total += inv.residual_signed
            else:
                total += inv.company_currency_id.with_context(
                    date=self.inv_pay_id.payment_date).compute(
                    inv.residual_company_signed, payment_currency)
        return abs(total)

    @api.one
    @api.depends('invoice_id', 'amount', 'amount_to_pay', 'pay_currency_id')
    def _compute_payment_difference(self):
        if not self.amount_to_pay:
            self.payment_difference = 0
        if self.invoice_id and self.amount_to_pay:
            if self.invoice_id.type in ['in_invoice', 'out_refund']:
                self.payment_difference = \
                    self.amount_to_pay - self._compute_total_invoices_amount()
            else:
                self.payment_difference = \
                    self._compute_total_invoices_amount() - self.amount_to_pay

    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    inv_pay_id = fields.Many2one(
        'multiple.invoice.payment', 'Multiple Invoice')
    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    pay_currency_id = fields.Many2one(
        'res.currency', string='Currency', related='inv_pay_id.currency_id')
    amount = fields.Monetary('Amount', currency_field='currency_id')
    amount_to_pay = fields.Monetary(
        'Amount to Pay', currency_field='pay_currency_id')
    payment_difference = fields.Monetary(compute='_compute_payment_difference',
                                         currency_field='pay_currency_id')
    payment_difference_handling = fields.Selection(
        [('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')],
        default='open', string="Payment Difference", copy=False)
    writeoff_account_id = fields.Many2one(
        'account.account', string="Difference Account", domain=[(
            'deprecated', '=', False)], copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment '
             'difference', default='Write-Off')
