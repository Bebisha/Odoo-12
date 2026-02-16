# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Stock Category',
    'version': '1.0',
    'category': 'Stock',
    'summary': 'Stock reports',
    'description': """
            This Module is used for printing Packing list report.
            """,
    'author': 'Bista Solutions Pvt.Ltd.',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['stock', 'sale', 'account'],
    'data': [
        'views/stock_picking.xml',
        'views/report_pickinglist_view.xml',
        'views/stock_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
