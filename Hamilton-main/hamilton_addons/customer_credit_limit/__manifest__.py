# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Customer Credit Limit',
    'version': '10.0.2.0.0',
    'category': 'Partner',
    'depends': ['account', 'delivery'],
    'license': 'AGPL-3',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Set credit limit for customer',
    'description': '''Customer Credit Limit
        1: Set the credit limit for customers.
        2: if CL < 0, SO move to Credit Review state.
        3: Only 'Can override credit limit' group of users confirm those SO.
    ''',
    'website': 'http://www.bistasolutions.com',
    'data': [
        'security/ir.model.access.csv',
        'security/partner_credit_limit_security.xml',
        'views/partner_view.xml',
        'views/account_invoice_view.xml',
        'views/sale_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/confirm_multi_so_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
