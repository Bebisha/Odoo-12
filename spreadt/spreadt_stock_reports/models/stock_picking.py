# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.one
    def get_so_date(self):
        # USE: show the total of qty brand wise into the report
        result = {}
        if self.origin:
            so_rec = self.env['sale.order'].search([('name', '=', self.origin)])
            if so_rec:
                invoice_list = []
                for inv in so_rec.invoice_ids:
                    if inv.number and inv.state not in ('draft', 'cancelled'):
                        invoice_list.append(inv.number)
                inv_number = ','.join(map(str, invoice_list))
                result = {'country_origin':so_rec.country_origin,
                               'hs_code':so_rec.hs_code,
                               'total_cbm':so_rec.total_cbm,
                               'gross_weight':so_rec.gross_weight,
                               'net_weight':so_rec.net_weight,
                               'no_of_box': so_rec.no_of_box,
                                'invoice_number': inv_number
                          }


        return dict(result)

    @api.one
    def get_product_categ(self):
        # USE: show the total of qty brand wise into the report
        categ_lst = []
        count_lst = []
        for move_line in self.move_lines:
            if move_line.product_id.categ_id.name not in categ_lst:
                categ_lst.append(move_line.product_id.categ_id.name)
            if move_line.product_id.country_origin_id.name not in count_lst:
                count_lst.append(move_line.product_id.country_origin_id.name)
        categ = ", ".join(map(str, categ_lst))
        country = ", ".join(map(str, count_lst))
        return {'category':categ,'country':country}


