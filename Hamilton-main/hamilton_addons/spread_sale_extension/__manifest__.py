# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Sale Extension',
    'description': """ Sale  Extension
    - Local Export feature added
    - Content Table For Export Invoice and Sales Order
    - Product details on Account Invoice Line and Sales Order Lines
    - Customization on Quotation Report
    """,
    'version': '1.0',
    'category': 'Sale',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['spreadt_product_extension', 'delivery',
                'customer_credit_limit','spreadt_base_data', 'sale_margin'],
    'data': [
        'data/sale_data.xml',
        'security/ir.model.access.csv',
        'views/sale_order.xml',
        'views/account_invoice.xml',
        'views/res_partner.xml',
        'views/sale_quotation_report.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': False,
    'installable': True
}
