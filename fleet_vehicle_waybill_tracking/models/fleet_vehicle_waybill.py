# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicleWaybill(models.Model):
    _name = 'fleet.vehicle.waybill'
    _description = 'Fleet Vehicle Waybill'
    _inherit = ['fleet.vehicle.waybill']

    latitude = fields.Float('Latitude', digits=(12, 9), compute='_compute_lat_lng')
    longitude = fields.Float('Longitude', digits=(12, 9), compute='_compute_lat_lng')

    def _compute_lat_lng(self):
        for record in self:
            if record.state in ['draft', 'cancel']:
                record.latitude = False
                record.longitude = False
            elif record.state == 'shipment':
                # on shipment
                record.latitude = record.vehicle_id.latitude
                record.longitude = record.vehicle_id.longitude
            elif record.state in ['arrival', 'delivered', 'invoiced', 'done']:
                # done
                record.latitude = record.drop_point_id.partner_latitude
                record.longitude = record.drop_point_id.partner_longitude
            else:
                # not started
                record.latitude = record.pickup_point_id.partner_latitude
                record.longitude = record.pickup_point_id.partner_longitude
