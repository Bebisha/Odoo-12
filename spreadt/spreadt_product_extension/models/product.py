# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models,fields,api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    country_origin_id = fields.Many2one("res.country",'Country of Origin')
    hs_code = fields.Char("HS Code")

class ProductCategory(models.Model):
    _inherit = 'product.category'

    # @api.model
    # def create(self, vals):
    #     print(vals,"valsssssssssssssss")
    #     if vals.get('property_stock_account_input_categ_id'):
    #         account_input = self.env.ref('stock_account.property_stock_account_input_categ_id')
    #         print(account_input,"account_input")
    #         vals['property_stock_account_input_categ_id'] = account_input.id
    #     return super(ProductCategory, self).create(vals)

    @api.multi
    def write(self, vals):
        print(vals, "valsssssssssssssss")
        res = super(ProductCategory, self).write(vals)
        print(res,"res")
        # if vals.get('property_stock_account_input_categ_id'):
        #     account_input = self.env.ref('stock_account.property_stock_account_input_categ_id')
        #     print(account_input, "account_input")

        return res
