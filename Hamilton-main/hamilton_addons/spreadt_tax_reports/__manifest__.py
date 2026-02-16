# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2016 (http://www.bistasolutions.com)
#
##############################################################################

{
    'name': 'Account Tax Category',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Account Tax Category',
    'description': """
            This Module is used for printing VAT RETURN report.
            """,
    'author': 'Bista Solutions Pvt.Ltd.',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['account_accountant'],
    'data': [
        'views/account_report.xml',
        'wizard/vat_fta_report_view.xml',
        'views/report_vat_fta.xml',
        'views/partner.xml',
        'views/company.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
