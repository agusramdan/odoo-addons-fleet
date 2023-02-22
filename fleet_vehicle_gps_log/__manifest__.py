# -*- coding: utf-8 -*-
{
    'name': "Fleet Vehicle GPS Log",
    'summary': """
        This module extends the Fleet module allowing the registration
        of GPS log """,
    'author': "Agus Muhammad Ramdan",
    'website': "https://github.com/agusramdan/odoo-addons-fleet",
    "category": "Human Resources",
    'version': '14.0.1.0.0',
    "license": "AGPL-3",
    'depends': ['base', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_vehicle_log_gps_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
