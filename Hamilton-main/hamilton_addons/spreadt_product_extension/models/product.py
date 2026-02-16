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
