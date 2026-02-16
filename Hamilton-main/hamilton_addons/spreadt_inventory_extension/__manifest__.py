# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Inventory Extension',
    'description': """
    - Inventory  Extension
    """,
    'version': '1.0',
    'category': 'Inventory',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['stock', 'spreadt_margin_price_enhance'],
    'data': [
        'views/stock_picking.xml',
        'report/report_stock_picking_operations.xml'
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True
}
