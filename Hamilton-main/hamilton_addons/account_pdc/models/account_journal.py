# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Fasluca(<faslu@cybrosys.in>)
#    you can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    @api.one
    @api.depends('outbound_payment_method_ids')
    def _compute_check_printing_payment_method_selected(self):
        self.check_printing_payment_method_selected = any(
            pm.code in ['check_printing', 'pdc'] for pm in self.outbound_payment_method_ids)

    @api.model
    def _enable_pdc_on_bank_journals(self):
        """ Enables check printing payment method and add a check sequence on bank journals.
            Called upon module installation via data file.
        """
        pdcin = self.env.ref('account_pdc.account_payment_method_pdc_in')
        pdcout = self.env.ref('account_pdc.account_payment_method_pdc_out')
        bank_journals = self.search([('type', '=', 'bank')])
        for bank_journal in bank_journals:
            # bank_journal._create_check_sequence()
            bank_journal.write({
                'inbound_payment_method_ids': [(4, pdcin.id, None)],
                'outbound_payment_method_ids': [(4, pdcout.id, None)],
            })




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

