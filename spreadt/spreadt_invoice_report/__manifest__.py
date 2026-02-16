# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Spreadt Invoice Report',
    'version': '10.0.2.0.0',
    'category': 'Report',
    'depends': ['account', 'spread_sale_extension'],
    'license': 'AGPL-3',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Manage Accounting invoice report',
    'description': '''
    ''',
    'website': 'http://www.bistasolutions.com',
    'data': [
        'views/invoice_report_tmpl.xml',
        'views/report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
