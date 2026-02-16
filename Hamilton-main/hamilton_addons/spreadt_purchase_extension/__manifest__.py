# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Pop-up on Supplier Credit Note and Incoming Shipment',
    'version': '10.0.1.0.0',
    'category': 'Sale',
    'depends': ['stock_account', 'purchase', 'purchase_stock'],
    'license': 'AGPL-3',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Pop-us Message on PO while selecting Vendor',
    'description': '''
    ''',
    'website': 'http://www.bistasolutions.com',
    'data': [
        'views/purchase_lock_unlock.xml',
        'views/purchase_order_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
