# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Product Extension',
    'description': """
    - Product Extension
    """,
    'version': '1.0',
    'category': 'product',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['base', 'product'],
    'data': [
        'views/product_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True
}
