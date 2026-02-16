# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Base Data Configuration',
    'version': '1.0',
    'category': 'base',
    'summary': 'Product Categories configuration using data file',
    'description': """ Basic Data Configuration
        - Company Name and Logo Changes
        - Product Categories  
        """,
    'author': 'Bista Solutions Pvt.Ltd.',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['base', 'product', 'stock', 'account'],
    'data': [
        'data/base_data.xml',
    ],
    'installable': True,
    'auto_install': True,
}
