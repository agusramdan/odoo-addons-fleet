# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicleWaybill(models.Model):
    _name = 'fleet.vehicle.waybill'
    _description = 'Fleet Vehicle Waybill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = 'date'

    name = fields.Char()

    READONLY_STATES = {
        "booking": [("readonly", True)],
        "waiting": [("readonly", True)],
        "pickup": [("readonly", True)],
        "shipment": [("readonly", True)],
        "arrival": [("readonly", True)],
        "delivered": [("readonly", True)],
        "invoiced": [("readonly", True)],
        "done": [("readonly", True)],
        "cancel": [("readonly", True)],
    }
    name = fields.Char(
        "No", required=True, index=True, copy=False, default="New"
    )
    state = fields.Selection(
        [("draft", "Draft"),
         ("booking", "Booking"),
         ("waiting", "Waiting Pickup"),
         ("pickup", "Pickup"),
         ("shipment", "Shipment"),
         ("arrival", "Arrival"),
         ("delivered", "Delivered"),
         ("invoiced", "Invoiced"),
         ("cancel", "Canceled"),
         ("done", "Done")],
        string="Status",
        copy=False,
        index=True,
        readonly=True,
        tracking=True,
        default="draft",
        help=" * Draft: not reserved yet.\n"
             " * Booking: On Process booking for route , vehicle, Driver etc..\n"
             " * Waiting: Waiting Pickup \n"
             " * Pickup: Pickup vehicle arrival to origin location until Departure \n"
             " * Shipment:  Package departure from Origin \n"
             " * Arrival:  Package arrival to destination \n"
             " * Delivered:  Package unloading and POD \n"
             " * Invoiced:  Process invoiced to customer \n"
             " * Cancel:  Cancel \n"
             " * Done:  Reserve done \n"
        ,
    )
    date = fields.Datetime(string='Date', states=READONLY_STATES, tracking=True, default=fields.Date.today())
    company_id = fields.Many2one('res.company', 'Company', states=READONLY_STATES,
                                 default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'PIC', tracking=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True, check_company=True,
                                 states=READONLY_STATES)

    shipper_id = fields.Many2one('res.partner', tracking=True, string='Shipper', check_company=True, required=True,
                                 states=READONLY_STATES)

    origin_id = fields.Many2one('res.partner', tracking=True, string='Origin', check_company=True,
                                states=READONLY_STATES, help="Fill when Shipper and Origin deferment address")
    origin_contact_id = fields.Many2one('res.partner', tracking=True, string='Origin Contact', check_company=True,
                                 states=READONLY_STATES)
    pickup_point_id = fields.Many2one('res.partner', compute='_compute_pickup_point_id')

    def _compute_pickup_point_id(self):
        for record in self:
            record.pickup_point_id = record.origin_id.id or record.shipper_id.id

    is_requirement_time_pickup = fields.Boolean()
    estimation_time_pickup = fields.Datetime()
    actual_time_pickup = fields.Datetime()

    is_requirement_etd = fields.Boolean()
    estimation_time_departure = fields.Datetime("ETD")
    actual_time_departure = fields.Datetime("ATD")

    consignee_id = fields.Many2one('res.partner', tracking=True, string='Consignee', check_company=True, required=True,
                                   states=READONLY_STATES)

    destination_id = fields.Many2one('res.partner', tracking=True, string='Destination', check_company=True,
                                     states=READONLY_STATES,
                                     help="Fill when Consignee and Destination different address")
    destination_contact_id = fields.Many2one('res.partner', tracking=True, string='Destination', check_company=True,
                                     states=READONLY_STATES,
                                     help="Fill when Consignee and Destination different address")
    drop_point_id = fields.Many2one('res.partner', compute='_compute_drop_point')

    def _compute_drop_point(self):
        for record in self:
            record.drop_point_id = record.destination_id.id or record.consignee_id.id

    is_requirement_eta = fields.Boolean()
    estimation_time_arrival = fields.Datetime()
    actual_time_arrival = fields.Datetime()

    is_requirement_delivery = fields.Boolean()
    estimation_time_deliver = fields.Datetime()
    actual_time_deliver = fields.Datetime()

    vehicle_id = fields.Many2one('fleet.vehicle', tracking=True, string='Vehicle', check_company=True,
                                 states=READONLY_STATES)
    driver_id = fields.Many2one('res.partner', tracking=True, string='Driver', check_company=True,
                                states=READONLY_STATES)

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "fleet.vehicle.waybill", vals.get('date', fields.Date.today()))
                    or "/"
            )
        results = super(FleetVehicleWaybill, self).create(vals)
        return results

    def button_draft(self):
        self.state = 'draft'

    def button_confirm(self):
        self.state = 'booking'

    def button_go_origin(self):
        self.state = 'waiting'

    def button_pickup(self):
        self.actual_time_pickup = fields.Datetime.now()
        self.state = 'pickup'

    def button_departure(self):
        self.actual_time_departure = fields.Datetime.now()
        self.state = 'shipment'

    def button_arrival(self):
        self.actual_time_arrival = fields.Datetime.now()
        self.state = 'arrival'

    def button_delivered(self):
        self.actual_time_deliver = fields.Datetime.now()
        self.state = 'delivered'

    def button_invoiced(self):
        self.state = 'invoiced'

    def button_done(self):
        self.state = 'done'

    def button_cancel(self):
        self.state = 'cancel'

    goods_line = fields.One2many('fleet.vehicle.waybill.goods', 'waybill_id', copy=True)


class FleetVehicleWaybillGoods(models.Model):
    _name = 'fleet.vehicle.waybill.goods'
    _description = 'Fleet Vehicle Waybill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "waybill_id, sequence"
    name = fields.Char()
    sequence = fields.Integer()
    waybill_id = fields.Many2one('fleet.vehicle.waybill')
    remark = fields.Char()
    est_weight = fields.Boolean()
    weight = fields.Float("Weight")
    uom_weight = fields.Many2one("uom.uom")
    est_volume = fields.Boolean()
    volume = fields.Float(" Volume")
    uom_volume = fields.Many2one("uom.uom")
