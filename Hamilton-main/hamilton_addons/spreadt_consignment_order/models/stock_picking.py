# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Picking(models.Model):
    _inherit = "stock.picking"

    is_consignment = fields.Boolean(string='Consignment Order')
    state = fields.Selection(selection_add=[('to_approve', 'To Approve')])

    @api.onchange('picking_type_id', 'partner_id')
    def onchange_picking_type(self):
        super(Picking, self).onchange_picking_type()
        if self.partner_id and self.partner_id.operation_type_id:
            self.picking_type_id = self.partner_id.operation_type_id.id
        if 'default_is_consignment' in self._context:
            return {'domain':{'partner_id':[('is_reseller','=',True)]}}

    @api.multi
    def action_confirm(self):
        res = super(Picking, self).action_confirm()
        for picking in self:
            if picking.move_ids_without_package:
                product_mv_with_zero_qty = \
                    picking.move_ids_without_package.filtered(
                    lambda x: x.product_uom_qty <= 0.0)
                if product_mv_with_zero_qty:
                    raise ValidationError(_('Please enter quantity in '
                                            'initial demand!'))
            if picking.is_consignment:
                picking.mapped('package_level_ids').filtered(
                    lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
                # call `_action_confirm` on every draft move
                picking.mapped('move_lines') \
                    .filtered(lambda move: move.state == 'draft') \
                    ._action_confirm()
                # call `_action_assign` on every confirmed move which location_id bypasses the reservation
                picking.filtered(lambda picking: picking.location_dest_id.is_consignee_location) \
                    .mapped('move_lines')._action_assign()
        return res

    @api.multi
    def validate_picking(self):
        """
        Approval workflow for picking
        :return:
        """
        for picking in self:
            if picking.picking_type_id and picking.picking_type_id.code == \
                    'internal' and picking.state == 'draft' and \
                    not picking.partner_id:
                picking.state = 'to_approve'
                return True
            else:
                picking.action_confirm()


class StockMove(models.Model):
    _inherit = "stock.move"

    stock_available = fields.Float(
        compute="_compute_virtual_available",
        string='SOH',
        store=True,
    )

    @api.depends('product_id')
    def _compute_virtual_available(self):
        location_ids = self.env['stock.location'].search(
            [('is_consignee_location', '=', True)])
        for rec in self:
            rec.stock_available = rec.product_id.with_context(
                warehouse=rec.warehouse_id.id
            ).qty_available - rec.product_id.with_context(
                location=location_ids.ids
            ).qty_available


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    display_consignee_location = fields.Boolean(compute='_compute_display_consignee_location', default=False)
    consignee_location = fields.Boolean(string="From Consignee Location ?", default=True)

    @api.multi
    def _compute_display_consignee_location(self):
        for order in self:
            if order.partner_id.is_reseller:
                order.display_consignee_location = True

    @api.multi
    def action_confirm(self):
        """
        This method is used to set 'picking_type_id' fields value from
        SO field 'partner_id.operation_type_id'.
        """
        res = super(SaleOrder, self).action_confirm()
        if res and self.partner_id and self.partner_id.is_reseller and \
                self.partner_id.operation_type_id and self.consignee_location:

            picking_obj = self.env['stock.picking']
            for rec in self:
                pick_recs = picking_obj.search([('sale_id', '=', rec.id)])
                for pick_rec in pick_recs:
                    pick_rec.write({
                        'location_id':rec.partner_id.operation_type_id
                            .default_location_dest_id.id,
                        'location_dest_id':
                            rec.partner_id.property_stock_customer.id
                    })
                    # set location based on operation type on partner
                    for move in pick_rec.move_lines:
                        move.write({
                            'location_id':rec.partner_id.operation_type_id
                            .default_location_dest_id.id,
                        'location_dest_id':
                            rec.partner_id.property_stock_customer.id
                        })
                        # set location based on operation type on partner
                        move.move_line_ids.write({
                            'location_id':
                                rec.partner_id.operation_type_id.
                                    default_location_dest_id.id
                        })

        return res
