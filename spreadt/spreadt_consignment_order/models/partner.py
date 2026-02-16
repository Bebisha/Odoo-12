# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    is_reseller = fields.Boolean(string="Create Consignment Order ?")
    operation_type_id = fields.Many2one('stock.picking.type',
                                        string="Operation Type")

    @api.onchange('customer')
    def onchange_is_customer(self):
        '''
        Reset Reseller/Retailer to False when customer is False
        :return:
        '''
        if not self.customer:
            self.is_reseller = False

    @api.onchange('is_reseller')
    def onchange_is_customer(self):
        '''
        Reset Reseller/Retailer to False when customer is False
        :return:
        '''
        if self.is_reseller and not self.operation_type_id:
            name = 'Internal Transfers: ' + self.name
            picking_type_rec = self.env['stock.picking.type'].search([('name', '=', name)])
            if not picking_type_rec:
                internal_picking = self.env.ref('stock.picking_type_internal')
                new_picking_type = internal_picking.copy()
                new_picking_type.write({'name': name})
                consignee_location = self.env['stock.location'].search([('name', '=', name)])
                if not consignee_location and new_picking_type:
                    stock_location = self.env.ref('stock.stock_location_stock')
                    stock_location = stock_location.copy()
                    stock_location.write({'name': self.name, 'return_location': False})
                    new_picking_type.write({'default_location_dest_id': stock_location.id})
                    self.operation_type_id = new_picking_type
                elif consignee_location and internal_picking:
                    self.operation_type_id = internal_picking
            else:
                self.operation_type_id = picking_type_rec
