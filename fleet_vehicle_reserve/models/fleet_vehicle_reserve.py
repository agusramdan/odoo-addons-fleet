# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class FleetReserveTime(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "fleet.vehicle.reserve"
    _description = "Fleet Vehicle Reserve Time"
    _order = 'date_from, date_to'
    _check_company_auto = True

    READONLY_STATES = {
        "reserved": [("readonly", True)],
        "done": [("readonly", True)],
        "running": [("readonly", True)],
        "cancel": [("readonly", True)],
    }
    name = fields.Char(
        "No", required=True, index=True, copy=False, default="New"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("reserved", "Reserved"), ("running", "Running"), ("cancel", "Canceled"),
         ("done", "Done")],
        string="Status",
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
        help=" * Draft: not reserved yet.\n"
             " * Reserved: Reserved has been confirmed.\n"
             " * Running: Running/ On Duty\n"
             " * Cancel:  cancel \n"
             " * Done:  Reserve done \n"
        ,
    )
    active = fields.Boolean('Active', default=True, tracking=True)
    reserve_date = fields.Datetime(string='Date', states=READONLY_STATES, tracking=True, default=fields.Date.today())
    company_id = fields.Many2one('res.company', 'Company', states=READONLY_STATES,
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'PIC', tracking=True, default=lambda self: self.env.user)
    reference = fields.Char("Ref", states=READONLY_STATES)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, check_company=True,
                                 states=READONLY_STATES)
    date_from = fields.Datetime(string='Start', tracking=True, required=True, states=READONLY_STATES)
    date_to = fields.Datetime(string='End', tracking=True, required=True, states=READONLY_STATES)
    vehicle_id = fields.Many2one('fleet.vehicle', tracking=True, string='Vehicle', check_company=True, required=True,
                                 states=READONLY_STATES)
    driver_id = fields.Many2one('res.partner', tracking=True, string='Driver', check_company=True, required=True,
                                states=READONLY_STATES)
    co_driver_id = fields.Many2one('res.partner', tracking=True, string='Co Driver', check_company=True,
                                   states=READONLY_STATES)

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        self.driver_id = self.vehicle_id.driver_id.id

    # hack change from calendar drag and drop
    @api.constrains('date_from', 'date_to')
    def _change_calendar_date_from(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError('Can not update Reserve Date.')

    @api.constrains('vehicle_id', 'date_from', 'date_to')
    def _check_availability(self):
        for record in self:
            if not record.vehicle_id.check_availability(record.date_from, record.date_to, record.id):
                raise ValidationError('Sorry This Vehicle is already reserved.')

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "fleet.vehicle.reserve", vals.get('reserve_date', fields.Date.today()))
                    or "/"
            )
        results = super(FleetReserveTime, self).create(vals)
        return results

    def button_confirm(self):
        self.state = 'reserved'

    def button_draft(self):
        self.state = 'draft'

    def button_running(self):
        self.state = 'running'

    def button_cancel(self):
        self.state = 'cancel'


class Fleet(models.Model):
    _inherit = 'fleet.vehicle'

    reserved_time = fields.One2many('fleet.vehicle.reserve', 'vehicle_id', string='Reserved Time', readonly=1,
                                    ondelete='cascade')
    reserved_count = fields.Integer(compute='_compute_reserved_count')

    reserved_id = fields.One2many('fleet.vehicle.reserve', compute='_compute_reserved_count')

    def _compute_reserved_id(self):
        Reserved = self.env['fleet.vehicle.reserve']
        for record in self:
            filter_domain = [('vehicle_id', '=', record.id), ('state', '=', 'reserved'),
                             ('date_to', '>', fields.Datetime.now())]
            record.reserved_id = Reserved.search(filter_domain, limit=1, order='date_from')

    def _compute_reserved_count(self):
        Reserved = self.env['fleet.vehicle.reserve']
        for record in self:
            filter_domain = [('vehicle_id', '=', record.id), ('date_from', '>', fields.Datetime.now())]
            record.reserved_count = Reserved.search_count(filter_domain)

    def open_reservation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reservation',
            'view_mode': 'tree,calendar,form',
            'res_model': 'fleet.vehicle.reserve',
            'domain': [('vehicle_id', '=', self.id), ('date_from', '>', fields.Datetime.now())],
            'context': {'default_vehicle_id': self.id}
        }

    def cancel_reserve(self, reserve_id):
        reserve = self.reserved_time.browse(reserve_id)
        reserve.unlink()

    def reserve_time(self, partner_id, date_from, date_to):
        if self.check_availability(date_from, date_to):
            reserved_id = self.reserved_time.create({'partner_id': partner_id,
                                                     'date_from': date_from,
                                                     'date_to': date_to,
                                                     'vehicle_id': self.id
                                                     })

            return reserved_id
        else:
            raise Warning('Sorry This vehicle is already booked by another customer')

    def check_availability(self, book_start_date, book_end_date, skip_id=False):
        availability = True
        for each in self.reserved_time:
            if skip_id == each.id or each.state in ['done', 'cancel']:
                continue

            if each.date_from < book_start_date < each.date_to:
                availability = False
            elif book_start_date < each.date_from:
                if each.date_from < book_end_date < each.date_to:
                    availability = False
                elif book_end_date > each.date_to:
                    availability = False

            if not availability:
                break

        return availability
