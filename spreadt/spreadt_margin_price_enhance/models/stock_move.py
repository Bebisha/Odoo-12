# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    price_category_id = fields.Many2one('price.category', string="Price Category")


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_price = fields.Float('Margin/Sale Price')

    @api.multi
    def _get_display_price(self, product):
        if self.picking_id.partner_id.property_product_pricelist \
                .discount_policy == 'with_discount':
            if self.picking_id.price_category_id.percentage > 0.0 and self.picking_id.price_category_id.percentage < 100.0:
                minus_price = self.product_id.msrp * ((self.picking_id.price_category_id.percentage or 0.0) / 100.0)
                return_price = self.product_id.msrp - minus_price
                return return_price
            elif self.picking_id.price_category_id.percentage >= 100.0:
                return_price = self.product_id.msrp
                return return_price
            else:
                return product.with_context(
                pricelist=self.picking_id.partner_id
                    .property_product_pricelist.id).price
        return_price = 0.0
        if self.picking_id.price_category_id.percentage > 0.0:
            minus_price = self.product_id.msrp * ((self.picking_id.price_category_id.percentage or 0.0) / 100.0)
            return_price = self.product_id.msrp - minus_price
        if self.picking_id.price_category_id.percentage >= 100.0:
            return_price = self.product_id.msrp
        return return_price

    @api.onchange('product_id')
    def product_id_change(self):
        price_unit = 0.00
        if not self.picking_id.price_category_id and self.picking_id.partner_id.is_reseller:
            raise UserError(_('Please select the price category !'))
        if self.product_id:
            product = self.product_id.with_context(
                lang=self.picking_id.partner_id.lang,
                partner=self.picking_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.picking_id.scheduled_date,
                pricelist=
                self.picking_id.partner_id.property_product_pricelist and
                self.picking_id.partner_id.property_product_pricelist.id or
                False,
                uom=self.product_uom.id
            )
            if self.picking_id.partner_id and \
                    self.picking_id.partner_id.property_product_pricelist:
                price_unit = \
                    self.env['account.tax']._fix_tax_included_price_company(
                        self._get_display_price(product), product.taxes_id,
                        self.env['account.tax'], self.env.user.company_id)
        if not price_unit and self.sale_line_id:
            price_unit = self.sale_line_id.price_unit

        self.sale_price = price_unit


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sale_price = fields.Float(string='Margin/Sale Price',
                              related='move_id.sale_price')
