# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import models,fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    local_export = fields.Selection(
        [('local', 'Local'), ('export', 'Export')],
        default='local', required=True, string='Local/Export')
    price_category_id = fields.Many2one('price.category', string="Price Category")

    @api.onchange('local_export')
    def onchange_local_export(self):
        """
        set default advance payment term for export customer.
        :return:
        """
        if self.local_export == 'export':
            payment_term_id = self.env.ref(
                'spreadt_base_data.account_payment_term_full_advance')
            if payment_term_id:
                self.property_payment_term_id = payment_term_id
