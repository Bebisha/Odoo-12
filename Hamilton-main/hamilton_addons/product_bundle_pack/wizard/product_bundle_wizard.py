# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class bi_wizard_product_bundle(models.TransientModel):
    _name = 'wizard.product.bundle.bi'

    product_id = fields.Many2one('product.product', string='Bundle', required=True)
    product_qty = fields.Integer('Quantity', required=True, default=1)
    product_price = fields.Float(string="Price")
    pack_ids = fields.One2many('product.pack', related='product_id.pack_ids', string="Select Products")
    qty_available = fields.Float(string='Product Quantity')

    @api.multi
    def button_add_product_bundle_bi(self):
        order_id = self.env['sale.order'].browse(self._context.get('active_id'))
        ehf_module_id = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'linhaw_ehf'),
            ('state', '=', 'installed')], limit=1)
        for pack in self:
            if pack.product_id.is_pack:
                if order_id:
                    vals = {'order_id': order_id.id,
                            'product_id': pack.product_id.id,
                            'name': pack.product_id.name,
                            'price_unit': self.product_price,
                            'product_uom': pack.product_id.uom_id.id,
                            'product_uom_qty': self.product_qty,
                            'pricelist_id': order_id.pricelist_id.id or False,}
                    if ehf_module_id and not order_id.partner_shipping_id.ehf_ca:
                        ehf_charge = self.env['ehf.config'].calculate_ehf_charge(order_id.partner_shipping_id.state_id and \
                                                                                 order_id.partner_shipping_id.state_id.id or False,
                                                                                 pack.product_id.categ_id.id)
                        vals.update({'ehf_charge': ehf_charge or 0.00})
                    line_id = self.env['sale.order.line'].create(vals)
                    line_id.compute_available_qty()
        return True

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.product_price = self.product_id.lst_price
            self.qty_available = self.product_id.product_tmpl_id.pack_qty
        else:
            pass
