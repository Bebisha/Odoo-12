# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    msrp = fields.Float(string='MSRP')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.product_id')
    def get_product_export_data(self):
        """
        compute data for export order
        :return:
        """
        for rec in self:
            hs_code = []
            country_origin = []
            for line in rec.order_line:
                if line.product_id:
                    if line.country_origin_id and line.country_origin_id.name \
                            not in country_origin:
                        country_origin.append(line.country_origin_id.name)
                    if line.hs_code and line.hs_code not in hs_code:
                        hs_code.append(line.hs_code)
                    if line.product_id.weight and line.product_uom_qty:
                        total_weight = line.product_uom_qty * \
                                       line.product_id.weight
            rec.hs_code = ', '.join(hs_code)
            rec.country_origin = ', '.join(country_origin)

    local_export = fields.Selection(
        [('local', 'Local'),
         ('export', 'Export')],
        default='local', required=True, string='Local/Export'
    )
    country_origin = fields.Char(compute='get_product_export_data',
                                 string="Country Of Origin")
    no_of_box = fields.Float(string="Number Of Box")
    hs_code = fields.Char(compute='get_product_export_data', string='HS Code')
    net_weight = fields.Float(string='Net Weight(KG)')
    gross_weight = fields.Float('Gross Weight(KG)')
    total_cbm = fields.Float('Total Value (CBM)')
    price_category_id = fields.Many2one('price.category', string="Price Category", required=True)

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order.
        This method may be overridden to implement custom invoice
        generation (making sure to call super() to establish
        a clean extension chain).
        """

        res = super(SaleOrder, self)._prepare_invoice()
        res.update({
                'local_export': self.local_export,
                'country_origin': self.country_origin,
                'no_of_box': self.no_of_box,
                'hs_code': self.hs_code,
                'net_weight': self.net_weight,
                'gross_weight': self.gross_weight,
                'total_cbm': self.total_cbm,
        })
        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        Reset Reseller/Retailer to False when customer is False
        :return:
        '''
        res = super(SaleOrder, self).onchange_partner_id()
        if self.partner_id and self.partner_id.local_export:
            self.local_export = self.partner_id.local_export
        if self.partner_id and self.partner_id.price_category_id:
            self.price_category_id = self.partner_id.price_category_id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _get_display_price(self, product):
        res = super(SaleOrderLine, self)._get_display_price(product)
        if self.order_id.price_category_id.percentage > 0.0 and self.order_id.price_category_id.percentage < 100.0:
            minus_price = self.product_id.msrp * ((self.order_id.price_category_id.percentage or 0.0) / 100.0)
            res = self.product_id.msrp - minus_price
        if self.order_id.price_category_id.percentage >= 100.0:
            res = self.product_id.msrp
        return res

    hs_code = fields.Char(related="product_id.hs_code", string="HS Code")
    country_origin_id = fields.Many2one(
        related="product_id.country_origin_id", string='Country Origin')

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
                warehouse=rec.order_id.warehouse_id.id
            ).qty_available - rec.product_id.with_context(
                location=location_ids.ids
            ).qty_available

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.order_id.price_category_id:
            raise UserError(_('Please select price category !'))
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.name = self.product_id.name
        return res


class PriceCategory(models.Model):
    _name = 'price.category'

    name = fields.Char(string="Name")
    percentage = fields.Float(string="Margin (%)")
