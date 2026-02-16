# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = "stock.quant"


    @api.multi
    def compute_sale_price(self):
        for quant in self:
            move_line = self.env['stock.move.line'].search([('product_id', '=', quant.product_id.id),'|', ('location_id', '=', quant.location_id.id),('location_dest_id', '=', quant.location_id.id),('lot_id', '=', quant.lot_id.id),'|',('package_id', '=', quant.package_id.id),('result_package_id', '=', quant.package_id.id)], order="id desc")
            if move_line:
                quant.sale_price = move_line[0].sale_price

    is_consignee_location = fields.Boolean(
        related='location_id.is_consignee_location',
        string='Consignee Location')

    sale_price = fields.Float(compute='compute_sale_price')
    product_category_id = fields.Many2one('product.category', string="Product Category")

    @api.model
    def create(self, vals):
        """
        To set product category
        :param vals:
        :return: res
        """
        res = super(StockQuant, self).create(vals)
        if res and res.product_id.categ_id:
            res.product_category_id = res.product_id.categ_id.id
        return res
