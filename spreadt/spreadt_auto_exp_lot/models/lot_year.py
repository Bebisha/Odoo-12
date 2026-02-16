# -*- coding: utf-8 -*-
from odoo import fields, models


class LotYear(models.Model):
    _name = "lot.year"
    _rec_name = 'code'
    _description = 'Year for Auto lot creation'

    year = fields.Char('Year', required=1)
    code = fields.Char('Code', required=1)
