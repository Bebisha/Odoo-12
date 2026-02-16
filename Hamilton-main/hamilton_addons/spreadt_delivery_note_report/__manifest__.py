# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
{
    'name': 'Delivery Note Report',
    'version': '11.0',
    'category': 'Report',
    'depends': ['stock'],
    'license': 'AGPL-3',
    'author': 'Bista Solutions Pvt. Ltd.',
    'maintainer': 'Bista Solutions Pvt. Ltd.',
    'summary': 'Manage Delivery Note report',
    'description': '''
    Manage Delivery Note report.
    ''',
    'website': 'http://www.bistasolutions.com',
    'data': [
        'views/delivery_note_report_tmpl.xml',
        'views/report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
