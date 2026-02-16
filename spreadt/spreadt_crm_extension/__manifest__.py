# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'CRM Extension',
    'description': """ CRM Extension
    - Added Product Lines in Opprotunity
    - All Product Lines added in Opporunity transfered to Quotation
    """,
    'version': '1.0',
    'category': 'crm',
    'website': 'www.bistasolutions.com',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'depends': ['base', 'crm', 'product', 'sale_management', 'spread_sale_extension'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
    ],
    'demo': [],
    'auto_install': False,
    'application': True,
    'installable': True
}
