# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Multiple Invoice Payment',
    'description': """
    - Multiple Invoice Payment
    """,
    'version': '1.0',
    'category': 'account',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['base', 'account'],
    'data': [
        'wizard/multiple_invoice_payment_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True
}
