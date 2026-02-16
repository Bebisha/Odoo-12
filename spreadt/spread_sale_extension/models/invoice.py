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

    @api.depends('invoice_line_ids.product_id')
    def get_product_export_data(self):
        """
        compute data for export order
        :return:
        """
        for rec in self:
            hs_code = []
            country_origin = []
            for line in rec.invoice_line_ids:
                if line.product_id:
                    if line.country_origin_id and \
                            line.country_origin_id.name not in country_origin:
                        country_origin.append(line.country_origin_id.name)
                    if line.hs_code and line.hs_code not in hs_code:
                        hs_code.append(line.hs_code)
                    if line.product_id.weight and line.quantity:
                        total_weight = line.quantity * line.product_id.weight
            rec.hs_code = ', '.join(hs_code)
            rec.country_origin = ', '.join(country_origin)

    local_export = fields.Selection(
        [('local', 'Local'),
         ('export', 'Export')], default='local', required=True, string='Local/Export'
    )
    country_origin = fields.Char(compute='get_product_export_data',
                                 string="Country Of Origin")
    no_of_box = fields.Float(string="Number Of Box")
    hs_code = fields.Char(compute='get_product_export_data', string='HS Code')
    net_weight = fields.Float(string='Net Weight(KG)')
    gross_weight = fields.Float('Gross Weight(KG)')
    total_cbm = fields.Float('Total Value(CBM)')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        '''
        Reset Reseller/Retailer to False when customer is False
        :return:
        '''
        res = super(AccountInvoice, self)._onchange_partner_id()
        if self.partner_id and self.partner_id.local_export:
            self.local_export = self.partner_id.local_export
        return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """
        update local export information
        :return:
        """
        values = super(AccountInvoice, self)._prepare_refund(
            invoice=invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id)
        values['local_export'] = invoice.local_export
        values['no_of_box'] = invoice.no_of_box
        values['country_origin'] = invoice.country_origin
        values['hs_code'] = invoice.hs_code
        values['net_weight'] = invoice.net_weight
        values['gross_weight'] = invoice.gross_weight
        values['total_cbm'] = invoice.total_cbm
        return values


    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if invoice.type in ('in_invoice', 'in_refund') and not invoice.account_id:
                invoice.account_id = invoice.partner_id.property_account_payable_id.id
        res = super(AccountInvoice, self).action_invoice_open()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    hs_code = fields.Char(related="product_id.hs_code", string="HS Code")
    country_origin_id = fields.Many2one(
        related="product_id.country_origin_id", string='Country Origin')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        self.name = self.product_id.name
        return res