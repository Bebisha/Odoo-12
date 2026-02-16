# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Manage Sale/Margin Price',
    'description': """
    - Add Inventory for Consignee Location Report 
    - Manage Sale Price on Stock Movement 
    """,
    'version': '1.0',
    'category': 'Stock',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['stock', 'spread_sale_extension', 'spreadt_consignment_order'],
    'data': [
        'views/stock_location_view.xml',
        'views/stock_account_views.xml',
        'views/stock_quant_view.xml',
        'views/stock_picking_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True
}
