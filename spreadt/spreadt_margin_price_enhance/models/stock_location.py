# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_consignee_location = fields.Boolean('Consignee Location')
