# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Excel Report',
    'version': '11.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Purchase',
    'license': 'LGPL-3',
    'support': 'business@pptservices.com',
    'website': 'https://www.pptssolutions.com',
    'summary': 'Excel sheet for Purchase Order',
    'description': """ Purchase order excel report
When user need to print the excel report in purchase order select the purchase order list and
user need to click the "Purchase order Excel Report" button and message will appear.select the "Print Excel report"button
for generating the purchase order excel file""",
    'depends': [
        'purchase','base', 'sprogroup_purchase_request',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_xls_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}