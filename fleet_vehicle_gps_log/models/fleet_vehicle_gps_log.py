# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class FleetVehicleGPSLog(models.Model):
    _name = "fleet.vehicle.gps.log"
    _description = "Fleet Vehicle Gps Log"
    _order = 'gps_date_time desc'

    name = fields.Char(compute='_compute_vehicle_log_name', store=True)
    gps_date_time = fields.Datetime(default=fields.Datetime.now)
    gps_date = fields.Date(compute='gps_to_date', store=True)
    latitude = fields.Float('Latitude', digits=(12, 9))
    longitude = fields.Float('Longitude', digits=(12, 9))
    spead = fields.Integer('Spead')
    heading = fields.Integer('Heading')
    engine_on = fields.Boolean('Engine ON')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    source = fields.Char(default='Manual')

    def gps_to_date(self):
        for record in self:
            record.gps_date = fields.Date.context_today(record, record.gps_date_time)

    @api.depends('vehicle_id', 'gps_date_time')
    def _compute_vehicle_log_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = str(record.gps_date_time)
            elif record.gps_date_time:
                name += ' / ' + str(record.gps_date_time)
            record.name = name

    @api.model_create_multi
    def create(self, vals_list):
        results = super(FleetVehicleGPSLog, self).create(vals_list)
        results.vehicle_id.get_gps_log_lat_lng()
        return results

    def write(self, vals):
        result = super(FleetVehicleGPSLog, self).write(vals)
        if result and self:
            self.vehicle_id.get_gps_log_lat_lng()
        return result


class Fleet(models.Model):
    _inherit = 'fleet.vehicle'

    gps_log_ids = fields.One2many('fleet.vehicle.gps.log', 'vehicle_id', string='Gps', readonly=1,
                                  ondelete='cascade')
    gps_log_count = fields.Integer(compute='_compute_gps_log_count')
    gps_log_last = fields.Many2one('fleet.vehicle.gps.log', compute='get_gps_log_lat_lng', store=True )
    gps_date_time = fields.Datetime('GPS Time', related='gps_log_last.gps_date_time', store=True)
    latitude = fields.Float('Latitude', digits=(12, 9), related='gps_log_last.latitude', store=True)
    longitude = fields.Float('Longitude', digits=(12, 9), related='gps_log_last.longitude', store=True)
    spead = fields.Integer('Spead', related='gps_log_last.spead', store=True, )
    heading = fields.Integer('Heading', related='gps_log_last.heading', store=True, )
    engine_on = fields.Boolean('Engine ON', related='gps_log_last.engine_on', store=True, )

    def get_gps_log_lat_lng(self):
        gps_log = self.env['fleet.vehicle.gps.log']
        for record in self:
            record.gps_log_last = gps_log.search([('vehicle_id', '=', record.id)], limit=1, order='gps_date_time desc')

    def _compute_gps_log_count(self):
        gps_log = self.env['fleet.vehicle.gps.log']
        for record in self:
            filter_domain = [('vehicle_id', '=', record.id)]
            record.gps_log_count = gps_log.search_count(filter_domain)

    def return_action_gps_log(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'GPS Log',
            'view_mode': 'tree',
            'res_model': 'fleet.vehicle.gps.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
