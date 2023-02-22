# -*- coding: utf-8 -*-
{
    'name': "Fleet Vehicle Reserve",
    'summary': """
        This module extends the Fleet module allowing the registration
        of Reservation Vehicle by Time """,
    'author': "Agus Muhammad Ramdan",
    'website': "https://github.com/agusramdan/odoo-addons-fleet",
    "category": "Human Resources",
    'version': '14.0.1.0.0',
    "license": "AGPL-3",
    'depends': ['base', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'security/fleet_vehicle_reserve_rule.xml',
        'views/fleet_vehicle_reserved_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
