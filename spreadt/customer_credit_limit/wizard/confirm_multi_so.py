# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import api, models, _
from odoo.exceptions import UserError


class SaleOrderConfirm(models.TransientModel):
    _name = 'sale.order.confirm'
    _description = 'Multiple Sale order confirmation those are in CREDIT ' \
                   'REVIEW state'

    @api.multi
    def so_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['sale.order'].browse(active_ids):
            if record.state not in ('credit_review'):
                raise UserError(_("Selected SO(s) cannot be override CL as "
                                  "they are not in 'CREDIT REVIEW' state."))
            record.with_context(review_log=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}
