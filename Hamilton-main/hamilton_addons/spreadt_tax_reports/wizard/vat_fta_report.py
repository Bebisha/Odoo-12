# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class VatFtaWizard(models.TransientModel):
    _name = 'vat.fta.wiz'
    _description = 'Report for VAT'

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    name = fields.Char('Name')
    ph_country_code = fields.Char('Phone/Mobile Country Code')
    ph_number = fields.Char('Phone/Mobile Number')

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        '''
            This will raise error if End date is less than start date.1
        '''
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_('Ending datetime cannot be set less \
                than starting datetime.'))

    @api.multi
    def print_report(self, data):
        '''
            This method will print report.
        '''
        data = {}
        data['form'] = self.read([])
        return self.env.ref('spreadt_tax_reports.action_report_vat_fta'
                            ).report_action(self, data=data, config=False)
