# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Auto Expiry date on Lots',
    'version': '12.0',
    'category': 'purchase',
    'summary': 'Automatic Expiry date on Lots based on Lot Number',
    'description': """
            This Module is used to set Automatic Expiry date on Lots based on 
            Lot Number.
            """,
    'author': 'Bista Solutions Pvt.Ltd.',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['purchase', 'stock', 'product_expiry'],
    'data': [
        'security/ir.model.access.csv',
        'data/lot.year.csv',
        'data/lot.months.csv',
        'views/lot_months_view.xml',
        'views/lot_year_view.xml',
        'views/stock_move_line_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
