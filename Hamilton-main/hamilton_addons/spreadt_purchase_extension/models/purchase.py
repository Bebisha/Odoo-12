# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, fields, _
from odoo.tools import float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        return res

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        warning = {}
        title_credit = message_shipment = title_shipment = message_credit = \
            False
        partner_list = list()
        if self.partner_id and self.partner_id.id:
            partner_list.append(self.partner_id.id)
            if self.partner_id and self.partner_id.parent_id:
                partner_list.append(self.partner_id.parent_id.id)

            domain = [
                ('account_id', '=',
                 self.partner_id.property_account_payable_id.id),
                ('partner_id', 'in', partner_list),
                ('reconciled', '=', False), '|',
                ('amount_residual', '!=', 0.0),
                ('amount_residual_currency', '!=', 0.0),
                ('credit', '=', 0), ('debit', '>', 0)]
            info = {'content': []}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id.id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = \
                            line.company_id.currency_id.with_context(
                                date=line.date).compute(
                                abs(line.amount_residual), line.currency_id)
                    if float_is_zero(
                            amount_to_show,
                            precision_rounding=line.currency_id.rounding):
                        continue
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                    })

            if info.get('content', False):
                amount = 0.0
                reference = str()
                currency = False
                for rec in info.get('content'):
                    amount += rec.get('amount')
                    reference = reference + rec.get('journal_name') + ', '
                    currency = rec.get('currency')
                message_credit = \
                    _("Vendor %s has credit amount %s %s with reference of \n "
                      "%s Please look into that.") % (
                        self.partner_id.name, amount, currency, reference)
                title_credit = 'Outstanding credits '
            # find picking for related partner
            user_company = self.env.user.company_id
            picking_type_id = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id.company_id', '=', user_company.id)])
            if picking_type_id:
                pickings = self.env['stock.picking'].search(
                    [('partner_id', 'in', partner_list),
                     ('picking_type_id', '=', picking_type_id[0].id),
                     ('state', 'in', ('assigned',))])
            picking_msg = str()
            new_pickings = ''
            if self.order_line and pickings:
                products = self.order_line.mapped('product_id')
                new_pickings = pickings.filtered(
                    lambda x: x.move_lines.filtered(lambda y: y.product_id in
                                                              products))
                for pick in new_pickings:
                    picking_msg = picking_msg + pick.name + ', '
            if new_pickings:
                title_shipment = 'Incoming Shipment'
                message_shipment = \
                    'Vendor %s has following open shipments Please look ' \
                    'into that. \n %s' % (self.partner_id.name, picking_msg)
            if title_credit and title_shipment:
                warning['title'] = title_credit + '/' + title_shipment
                warning['message'] = \
                    message_credit + '\n \n' + message_shipment
            elif title_credit and title_credit:
                warning['title'] = title_credit
                warning['message'] = message_credit
            elif title_shipment and message_shipment:
                warning['title'] = title_shipment
                warning['message'] = message_shipment
            return {'warning': warning}
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            warning = {}
            self.name = self.product_id.name
            message_shipment = title_shipment = False
            partner_list = list()
            if self.partner_id and self.partner_id.id:
                partner_list.append(self.partner_id.id)
                if self.partner_id and self.partner_id.parent_id:
                    partner_list.append(self.partner_id.parent_id.id)
            user_company = self.env.user.company_id
            picking_type_id = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'),
                 ('warehouse_id.company_id', '=', user_company.id)])
            if picking_type_id:
                pickings = self.env['stock.picking'].search(
                    [('partner_id', 'in', partner_list),
                     ('picking_type_id', '=', picking_type_id[0].id),
                     ('state', 'in', ('assigned',))])

            picking_msg = str()
            new_pickings = pickings.filtered(
                lambda x: x.move_lines.filtered(lambda y: y.product_id == self.product_id))
            for pick in new_pickings:
                picking_msg = picking_msg + pick.name + ', '
            if new_pickings:
                title_shipment = 'Incoming Shipment'
                message_shipment = \
                    'Vendor %s has following open shipments Please look ' \
                    'into that. \n %s' % (self.partner_id.name, picking_msg)
            if title_shipment and message_shipment:
                warning['title'] = title_shipment
                warning['message'] = message_shipment
            return {'warning': warning}

        return res

    stock_available = fields.Float(
        compute="_compute_virtual_available",
        string='SOH',
        store=True,
    )

    @api.depends('product_id')
    def _compute_virtual_available(self):
        location_ids = self.env['stock.location'].search(
            [('is_consignee_location', '=', True)])
        for rec in self:
            rec.stock_available = rec.product_id.with_context(
                warehouse=rec.order_id.picking_type_id.warehouse_id.id
            ).qty_available - rec.product_id.with_context(
                location=location_ids.ids
            ).qty_available

