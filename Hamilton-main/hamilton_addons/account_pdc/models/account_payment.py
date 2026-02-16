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
from odoo.exceptions import UserError

from datetime import datetime, date, timedelta


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)
    effective_date = fields.Date('Effective Date', help='Effective date of PDC', copy=False, default=False)
    deposited_date = fields.Date('Deposite Date', help='Deposite Date', copy=False, default=False)

    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()
        if self.payment_method_id == self.env.ref('account_check_printing.account_payment_method_check'):
            res.update({
                'check_amount_in_words': self.check_amount_in_words,
                'check_manual_sequencing': self.check_manual_sequencing,
                'effective_date': self.effective_date,
                'deposited_date': self.deposited_date,
            })
        return res

    def _prepare_payment_vals(self, invoices):
        res = super(AccountRegisterPayments, self)._prepare_payment_vals(invoices)
        res.update({'bank_reference': self.bank_reference,
                    'cheque_reference': self.cheque_reference})
        return res


class AccountPayment(models.Model):
    _inherit = "account.payment"

    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)
    effective_date = fields.Date('Effective Date', help='Effective date of PDC', copy=False, default=False)
    deposited_date = fields.Date('Deposite Date', help='Deposite Date', copy=False, default=False)

    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code in ['check_printing', 'pdc'] and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' or 'PDC' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            next_check_number = last_printed_check and last_printed_check.check_number + 1 or 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').post()
            self.write({'state': 'sent'})
            return self.do_print_checks()


    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        if self.payment_method_code =='pdc':
            date = self.effective_date
        else:
            date = self.payment_date
        return {
            'name': name,
            'date': date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
        }



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
