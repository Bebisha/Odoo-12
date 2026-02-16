# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import math
from datetime import datetime, date, timedelta

from odoo.exceptions import UserError
from odoo import api, fields, models, _




class ProductPack(models.Model):
    _name = 'product.pack'

    @api.multi
    def set_qty_available(self):
        """ Compute product pack components quantity.
        """
        for each in self:
            if each.product_id and each.product_id.qty_available:
                each.qty_available = math.floor(each.product_id.qty_available / (each.qty_uom or 1))

    @api.onchange('product_id', 'qty_uom')
    def _onchange_product_id_qty_available(self):
        self.set_qty_available()

    @api.depends()
    def _compute_pack_qty(self):
        self.set_qty_available()

    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    qty_uom = fields.Float(string='Quantity', required=True, default=1.0)
    bi_product_template = fields.Many2one(comodel_name='product.template', string='Product pack')
    bi_image = fields.Binary(related='product_id.image_medium', string='Image', store=True)
    price = fields.Float(related='product_id.lst_price', string='Product Price')
    uom_id = fields.Many2one(related='product_id.uom_id', string="Unit of Measure", readonly="1")
    name = fields.Char(related='product_id.name', readonly="1")
    qty_available = fields.Float(compute='_compute_pack_qty', string='Product Quantity')


class ProductProduct(models.Model):
    _inherit = 'product.template'

    @api.depends('pack_ids')
    def _compute_pack_qty(self):
        for each in self:
            if each.pack_ids:
                each.pack_qty = min(pack.qty_available for pack in each.pack_ids)


    def _default_location(self):
        for rec in self:
            quant_obj = self.env['stock.quant'].search([('product_id', '=', rec.id)])
            location_lines = set()
            for line in quant_obj:
                location_lines.update(line.mapped('location_id.id'))
            self.stock_location_ids = self.env['stock.location'].browse(list(location_lines)).sorted()


    is_pack = fields.Boolean(string='Is Product Pack')
    cal_pack_price = fields.Boolean(string='Calculate Pack Price')
    pack_ids = fields.One2many(comodel_name='product.pack', inverse_name='bi_product_template',
                               string='Product pack')
    pack_qty = fields.Float(compute='_compute_pack_qty', string='Pack Quantity')
    stock_location_ids = fields.Many2many('stock.location', 'product_stock_loc_rel','prod_id','stock_id',string='Stock Location',compute=_default_location)

    @api.model
    def create(self, vals):
        total = 0
        res = super(ProductProduct, self).create(vals)
        if res.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in res.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            res.list_price = total
        return res

    @api.multi
    def write(self, vals):
        total = 0
        res = super(ProductProduct, self).write(vals)
        if self.cal_pack_price:
            if 'pack_ids' in vals or 'cal_pack_price' in vals:
                    for pack_product in self.pack_ids:
                            qty = pack_product.qty_uom
                            price = pack_product.product_id.list_price
                            total += qty * price
        if total > 0:
            self.list_price = total
        return res


class Location(models.Model):
    _inherit = 'stock.location'

    prod_ids = fields.Many2many('product.template', 'product_stock_loc_rel','stock_id','prod_id',string='Product')

class AccountJournal(models.Model):
    _inherit = 'account.journal'


    refund_sequence = fields.Boolean(string='Dedicated Credit Note Sequence', help="Check this box if you don't want to share the same sequence for invoices and credit notes made from this journal", compute='set_refund_seq')

    def set_refund_seq(self):
        for r in self:
            r.refund_sequence = True
            if (r.type=='sale' or r.type=='purchase') and len(r.refund_sequence_id) == 0:
                journal_vals = {
                    'name': r.name,
                    'company_id': r.company_id.id,
                    'code': r.code,
                    'refund_sequence_number_next': r.refund_sequence_number_next,
                }
                refund_sequence_id = self.sudo()._create_sequence(journal_vals, refund=True).id
                r.write({'refund_sequence_id': refund_sequence_id})


    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'CN'
        return prefix + '/%(range_year)s/'

    @api.model
    def _create_sequence(self, vals, refund=False):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_sequence_prefix(vals['code'], refund)
        seq_name = refund and vals['code'] + _(': Refund') or vals['code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        return seq


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def create(self, vals):
        rslt = super(AccountPayment, self).create(vals)
        # When a payment is created by the multi payments wizard in 'multi' mode,
        # its partner_bank_account_id will never be displayed, and hence stay empty,
        # even if the payment method requires it. This condition ensures we set
        # the first (and thus most prioritary) account of the partner in this field
        # in that situation.
        if not rslt.partner_bank_account_id and rslt.show_partner_bank_account and rslt.partner_id.bank_ids:
            rslt.partner_bank_account_id = rslt.partner_id.bank_ids[0]
        if (rslt.payment_method_id.name == 'PDC'):
            acc_user = self.env['res.users'].search([('groups_id.name', '=', 'Accountant')])
            for user in acc_user:
                user_id = self.env['mail.followers'].search(
                        [('res_id', '=', user.id), ('res_model', '=', 'account.payment'), ('partner_id', '=', user.partner_id.id)])
                rslt.message_subscribe(partner_ids=user_id.partner_id.ids)
                display_msg = """ Draft PDC created"""
            rslt.message_post(body=display_msg)
        return rslt



    def payment_reminder(self):
        now = datetime.now()
        date_now = now.date()
        match = self.search([])
        for i in match:
            if i.payment_method_id.name == 'PDC' and i.state == 'draft':
                exp_date = i.deposited_date - timedelta(days=1)
                if date_now >= exp_date:
                    i.message_post(body=('PDC cheque is to be deposited on %s.') % (str(i.deposited_date),))
                for followers in i.message_follower_ids:
                    if i.deposited_date:
                        exp_date = i.deposited_date - timedelta(days=1)
                        if date_now >= exp_date:
                            if i.cheque_reference:
                                mail_content = "Reminder for PDC cheque deposit" +",<p><p>Cheque No.:" + i.cheque_reference + "<p>Date: " + \
                                               str(i.deposited_date) + "<p>Customer:" + i.partner_id.name
                                main_content = {
                                    'subject': ('Reminder for PDC Cheque deposit'),
                                    'author_id': self.env.user.partner_id.id,
                                    'body_html': mail_content,
                                    'email_to': followers.partner_id.email,
                                }
                                self.env['mail.mail'].create(main_content).send()
                            else:
                                mail_content = "Reminder for PDC cheque deposit" +",<p><p>Cheque No.:" +   "<p>Date: " + \
                                               str(i.deposited_date) + "<p>Customer:" + i.partner_id.name
                                main_content = {
                                    'subject': ('Reminder for PDC Cheque deposit'),
                                    'author_id': self.env.user.partner_id.id,
                                    'body_html': mail_content,
                                    'email_to': followers.partner_id.email,
                                }
                                self.env['mail.mail'].create(main_content).send()
