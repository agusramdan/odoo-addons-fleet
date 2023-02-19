# -*- coding: utf-8 -*-
{
    'name': "Fleet Vehicle Reserve",

    'summary': """
        Reserve Vehicle by Time """,

    'description': """
        Reserve Vehicle by Time
    """,

    'author': "Agus Muhammad Ramdan",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Service',
    'version': '14.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/fleet_vehicle_reserve_rule.xml'
        'views/fleet_vehicle_reserved_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
