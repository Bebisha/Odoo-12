# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

from odoo import api, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('location_id', 'product_id', 'product_uom_qty')
    def compute_available_qty(self):
        for line in self:
            if not line.product_id:
                return
            if line.product_id.is_pack:
                line.qty_available = line.product_id.pack_qty or 0.0
            else:
                if not line.location_id:
                    line.qty_available = line.product_id.qty_available
                else:
                    line.qty_available = line._get_product_quantity()
                if self._context.get('quantity', False):
                    if line.product_uom_qty > line.qty_available:
                        line.qty_backoder = line.product_uom_qty - line.qty_available
                        line.qty_deliver = line.qty_available
                    else:
                        line.qty_backoder = 0.0
                        line.qty_deliver = line.product_uom_qty
                else:
                    line.qty_backoder = line.product_uom_qty - line.qty_deliver

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_check_availability(self):
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if self.product_id.is_pack:
            if self.product_id.type == 'product':
                warning_mess = {}
                for pack_product in self.product_id.pack_ids:
                    qty = self.product_uom_qty
                    if qty * pack_product.qty_uom > pack_product.product_id.virtual_available:
                        warning_mess = {'title': _('Not enough inventory!'),
                                        'message': ('You plan to sell %s but you only have %s %s available, \
                                                     and the total quantity to sell is %s !' %
                                                     (qty, pack_product.product_id.virtual_available,
                                                      pack_product.product_id.name,
                                                      qty * pack_product.qty_uom))
                                        }
                        return {'warning': warning_mess}
        else:
            return res

    @api.multi
    def _action_launch_stock_rule(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:
            if line.state != 'sale' or line.product_id.type not in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement()
            # qty = 0.0
            # for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
            #     qty += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom, rounding_method='HALF-UP')
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                vals = {'name': line.order_id.name,
                        'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id}
                group_id = self.env['procurement.group'].create(vals)
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            # Prodcut Bundle pack code start
            if line.product_id.pack_ids:
                values = line._prepare_procurement_values(group_id=line.order_id.procurement_group_id)
                product_qty = line.product_uom_qty - qty
                product_obj = self.env['product.product']
                product_uom_obj = self.env['uom.uom']
                get_param = self.env['ir.config_parameter'].sudo().get_param
                for val in values:
                    product_id = product_obj.browse(val.get('product_id'))
                    procurement_uom = product_uom_obj.browse(val.get('product_uom'))
                    quant_uom = line.product_id.uom_id
                    if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                        product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                        procurement_uom = quant_uom
                    try:
                        self.env['procurement.group'].run(product_id, val.get('product_qty'), procurement_uom,
                                                          line.order_id.partner_shipping_id.property_stock_customer,
                                                          val.get('name'),
                                                          val.get('origin'), val)
                    except UserError as error:
                        errors.append(error.name)
            else:
                values = line._prepare_procurement_values(group_id=group_id)
                product_qty = line.product_uom_qty - qty

                procurement_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                get_param = self.env['ir.config_parameter'].sudo().get_param
                if procurement_uom.id != quant_uom.id and get_param('stock.propagate_uom') != '1':
                    product_qty = line.product_uom._compute_quantity(product_qty, quant_uom, rounding_method='HALF-UP')
                    procurement_uom = quant_uom

                try:
                    self.env['procurement.group'].run(line.product_id, product_qty, procurement_uom, line.order_id.partner_shipping_id.property_stock_customer, line.name, line.order_id.name, values)
                except UserError as error:
                    errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True

    @api.multi
    def _prepare_procurement_values(self, group_id):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        values = []
        date_planned = \
            self.order_id.confirmation_date \
            + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
        if self.product_id.pack_ids:
            for item in self.product_id.pack_ids:
                values.append({
                    'name': item.product_id.name,
                    'origin': self.order_id.name,
                    'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_id': item.product_id.id,
                    'product_qty': item.qty_uom * self.product_uom_qty,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'company_id': self.order_id.company_id.id,
                    'group_id': group_id,
                    'sale_line_id': self.id,
                    'warehouse_id': self.order_id.warehouse_id and self.order_id.warehouse_id,
                    'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
                    'route_ids': self.route_id and [(4, self.route_id.id)] or [],
                    'partner_dest_id': self.order_id.partner_shipping_id and self.order_id.partner_shipping_id.id,
                })
            return values
        else:
            res.update({'company_id': self.order_id.company_id,
                        'group_id': group_id,
                        'sale_line_id': self.id,
                        'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'route_ids': self.route_id,
                        'warehouse_id': self.order_id.warehouse_id or False,
                        'partner_dest_id': self.order_id.partner_shipping_id})
            return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if product_id.pack_ids:
            for item in product_id.pack_ids:
                result.update({
                    'product_id': item.product_id.id,
                    'product_uom': item.uom_id and item.uom_id.id,
                    'product_uom_qty': item.qty_uom,
                    'origin': origin,
                    })
        return result

# In models/account_move.py

class AccountMove(models.Model):
    _inherit = 'account.move'

    def update_product_move_logic(self):
        # Update credit where account_id = 169
        self.env.cr.execute("""
            UPDATE account_move_line aml
            SET credit = pt.msrp
            FROM account_move_line aml2
            JOIN account_move am ON aml2.move_id = am.id
            JOIN product_product pp ON aml2.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE aml.move_id = aml2.move_id
              AND aml.account_id = 169
              AND aml2.product_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM account_move_line sub_aml
                  WHERE sub_aml.move_id = aml.move_id
                  GROUP BY sub_aml.move_id
                  HAVING SUM(sub_aml.debit) <> 0 OR SUM(sub_aml.credit) <> 0
              );
        """)

        # Update debit where account_id = 68
        self.env.cr.execute("""
            UPDATE account_move_line aml
            SET debit = pt.msrp
            FROM account_move_line aml2
            JOIN account_move am ON aml2.move_id = am.id
            JOIN product_product pp ON aml2.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE aml.move_id = aml2.move_id
              AND aml.account_id = 68
              AND aml2.product_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM account_move_line sub_aml
                  WHERE sub_aml.move_id = aml.move_id
                  GROUP BY sub_aml.move_id
                  HAVING SUM(sub_aml.debit) <> 0 OR SUM(sub_aml.credit) <> 0
              );
        """)
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def update_credit_debit_from_product_cost(self):
        self.env.cr.execute("""
            UPDATE account_move_line aml
            SET credit = pt.x_cosst_db::numeric
            FROM product_product pp
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE aml.product_id = pp.id
            AND aml.debit = 0 AND aml.credit = 0
            AND aml.account_id = 169
          
        """)

        self.env.cr.execute("""
            UPDATE account_move_line aml
            SET debit = pt.x_cosst_db::numeric
            FROM product_product pp
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE aml.product_id = pp.id
            AND aml.debit = 0 AND aml.credit = 0
            AND aml.account_id = 68
        
        """)

