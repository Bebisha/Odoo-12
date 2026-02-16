# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models,fields, api


class Product(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, fields):
        res = super(Product, self).default_get(fields)
        if 'type' in res:
            res['type'] = 'product'
        return res