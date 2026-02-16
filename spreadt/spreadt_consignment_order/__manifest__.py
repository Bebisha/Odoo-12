# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Consignment',
    'version': '10.0.2.0.0',
    'category': 'Sale',
    'depends': ['sale_stock', 'sale_management'],
    'license': 'AGPL-3',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Manage Consignment',
    'description': '''
    ''',
    'website': 'http://www.bistasolutions.com',
    'data': [
        'views/stock_picking.xml',
        'views/consignment_report_tmpl.xml',
        'views/report.xml',
        'views/partner.xml',
        'views/sale_quotation_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
