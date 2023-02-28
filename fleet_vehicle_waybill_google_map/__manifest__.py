# Copyright 2021 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Fleet Vehicle Waybill Google Map",
    "summary": """
        This module extends the fleet management functionality. Adds the pivot
        table and graph view and google map to the fleet vehicles Waybill.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "Agus Muhammad Ramdan,Odoo Community Association (OCA)",
    "maintainers": ["agusramdan"],
    "images": ["static/description/banner.png"],
    'website': "https://github.com/agusramdan/odoo-addons-fleet",
    "depends": ["fleet", "fleet_vehicle_waybill_tracking", "web_google_maps"],
    "data": ["views/fleet_vehicle_waybill_views.xml"],
}
