# -*- coding: utf-8 -*-
# © 2004-2009 Tiny SPRL (<http://tiny.be>).
# © 2014-2017 Tecnativa - Pedro M. Baeza
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Purchase order lines with discounts",
    "author": "Tiny, "
              "Acysos S.L., "
              "Tecnativa, "
              "ACSONE SA/NV,"   
              "Odoo Community Association (OCA)",
    "version": "11.0.1.0.1",
    "category": "Purchase Management",
    "depends": ["purchase", "base", 'sprogroup_purchase_request',],
    "data": [
        "views/purchase_discount_view.xml",
        "views/report_purchaseorder.xml",
        "security/purchase_discount_security.xml",
        "security/ir.model.access.csv",
    ],
    "license": 'AGPL-3',
    'installable': True,
    'images': ['images/purchase_discount.png'],
}
