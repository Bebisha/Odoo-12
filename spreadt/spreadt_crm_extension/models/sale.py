# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('opportunity_id')
    def onchange_opportunity_id(self):
        '''
        create SO lines based on opportunity
        :return:
        '''
        so_line = []
        if self.opportunity_id and self.opportunity_id.crm_lead_line_ids:
            for lead_line in self.opportunity_id.crm_lead_line_ids:
                name = lead_line.product_id.name_get()[0][1]
                if lead_line.product_id.description_sale:
                    name += '\n' + lead_line.product_id.description_sale
                # prepare vals for SOLines
                vals = {
                    'product_id': lead_line.product_id.id,
                    'product_uom_qty': lead_line.quantity,
                    'price_unit': lead_line.quoted_price,
                    'product_uom': lead_line.uom_id.id,
                    'name': name,
                }
                so_line.append(vals)
                self.price_category_id = lead_line.crm_lead_id.price_category_id.id
            self.order_line = so_line
