# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################


from odoo import api, models, _
from odoo.exceptions import UserError


class ReportVatFta(models.AbstractModel):
    _name = 'report.spreadt_tax_reports.report_vat_fta'
    _description = 'Abstract class for VAT FTA Report'

    @api.multi
    def _get_tax_values(self):

        res = {
            'abu_dhabi': (0, 0, 0),
            'dubai': (0, 0, 0),
            'sharjah': (0, 0, 0),
            'ajman': (0, 0, 0),
            'umm_al_quwain': (0, 0, 0),
            'ras_al_khaimah': (0, 0, 0),
            'fujairah': (0, 0, 0),
            'tax_refunds': (0, 0, 0),
            'supply_reverse_charge': (0, 0, 0),
            'zero_rated': (0, 0, 0),
            'exempt_supplies': (0, 0, 0),
            'uae_goods': (0, 0, 0),
            'uae_adjust_goods': (0, 0, 0),
            'supply_total': (0, 0, 0),
            'standard_rated_expense': (0, 0, 0),
            'expense_reverse_charge': (0, 0, 0),
            'expense_total': (0, 0, 0),
            'total_tax': (0, 0, 0),
        }

        supply_tax = []
        amount = []
        zero_rated_tax_amount = []
        vat_tax_amt = []
        vat_amount = []
        docs = self.env[self.model].browse(self.env.context.get('active_ids',
                                                                []))
        for invoice_tax_rec in self.env['account.invoice'].search(
            [('state', 'in', ('paid', 'open')),
             ('date_invoice', '>=', docs.start_date),
             ('date_invoice', '<=', docs.end_date),
             ('type', 'in', ('out_invoice', 'out_refund')),
             ('company_id', '=', docs.company_id.id)]):
            supply_tax.append(invoice_tax_rec.amount_tax)
            if invoice_tax_rec.amount_tax:
                amount.append(invoice_tax_rec.amount_total)
            for tax_rec in invoice_tax_rec.tax_line_ids:
                if tax_rec.amount_total == 0.0:
                    zero_rated_tax_amount.append(invoice_tax_rec.amount_total)
        zero_tax = sum(zero_rated_tax_amount)
        supply_tax = sum(supply_tax)
        d_amount = sum(amount)
        total_amount = zero_tax + d_amount
        for expense_tax_rec in self.env['account.invoice'].search(
            [('state', 'in', ('paid', 'open')),
             ('date_invoice', '>=', docs.start_date),
             ('date_invoice', '<=', docs.end_date),
             ('type', 'in', ('in_invoice', 'in_refund')),
             ('company_id', '=', docs.company_id.id)]):
            vat_tax_amt.append(expense_tax_rec.amount_tax)
            vat_amount.append(expense_tax_rec.amount_total)
        tax = sum(vat_tax_amt)
        expense_amount = sum(vat_amount)
        tot_tax = supply_tax - tax
        res['dubai'] = (d_amount, supply_tax, 0)
        res['zero_rated'] = (zero_tax, 0, 0)
        res['supply_total'] = (total_amount, supply_tax, 0)
        res['standard_rated_expense'] = (expense_amount, tax, 0)
        res['expense_total'] = (expense_amount, tax, 0)
        res['total_tax'] = (supply_tax, tax, tot_tax)
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(
            self.env.context.get('active_ids', []))
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'get_tax_values': self._get_tax_values,
        }
