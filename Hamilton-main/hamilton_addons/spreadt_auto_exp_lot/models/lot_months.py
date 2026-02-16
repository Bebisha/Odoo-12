# -*- coding: utf-8 -*-
from odoo import fields, models


class LotMonths(models.Model):
    _name = "lot.months"
    _rec_name = 'code'
    _description = 'Months for Auto lot creation'

    MONTHS = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
              (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
              (9, 'September'), (10, 'October'), (11, 'November'),
              (12, 'December')]

    month = fields.Selection(MONTHS, 'Months', required=1)
    code = fields.Char('Code', required=1)
