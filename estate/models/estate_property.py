from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

# now = datetime.now()

class EstateProperty(models.Model):
	_name = "estate.property"
	_description = "estate property details"
	_order = "id desc"

	current_date = datetime.today()
	future_date = current_date + relativedelta(months=3)

	name = fields.Char(string="Title", required=True, default="Unknown")
	available_from = fields.Date(copy=False, default=future_date)
	description = fields.Text()
	postcode = fields.Char()
	date_availability = fields.Date()
	expected_price = fields.Float(copy=False)
	selling_price = fields.Float(readonly=True)
	bedrooms = fields.Integer()
	living_area = fields.Integer(string="Living Area (sqm)")
	facades = fields.Integer()
	garage = fields.Boolean()
	garden = fields.Boolean()
	active = fields.Boolean(default=True)
	garden_area = fields.Integer()
	garden_orientation = fields.Selection(selection = [('n','North'), ('s','South'), ('e','East'), ('w','West')])
	status = fields.Selection(selection = [('new', 'New'), ('receive', 'Offer Received'), ('accepted', 'Offer Accepted'), ('rejected', 'Refused'), ('sold', 'SOLD'), ('cancel', 'Canceled')], default='new', copy=False)
	property_type_id = fields.Many2one("estate.property.type", string="Property type")
	salesman_id = fields.Many2one("res.users", string="SalesMan")
	buyer_id = fields.Many2one("res.partner", string="Buyer")
	tag_ids = fields.Many2many("estate.property.tags", 'rel_property_tag','property_id', 'tag_id' ,string="Tags")
	offer_ids = fields.One2many("estate.property.offer", "property_id")

	total_area = fields.Integer(compute='_compute_total_area')

	best_price = fields.Float(compute='_compute_highest_price')

	@api.depends('living_area','garden_area')
	def _compute_total_area(self):
		for area in self:
			area.total_area = area.living_area + area.garden_area


	@api.depends("offer_ids")
	def _compute_highest_price(self):
		self.best_price = max(self.offer_ids.mapped('price'),default=0)


	@api.onchange("garden")
	def _onchange_garden(self):
		for rec in self:
			if rec.garden == True:
				rec.garden_area = 10
				rec.garden_orientation = 'n'
			else:
				rec.garden_area = ""
				rec.garden_orientation = ""

	@api.depends('status')
	def sold_property(self):
		for rec in self:
			if rec.status != 'cancel':
				if rec.status == 'accepted':
					rec.status = 'sold'
				else:
					raise UserError('Need to Accept one offer')	
			else:
				raise UserError('A canceled property cannot be set as sold')

	@api.depends('status')
	def cancel_property(self):
		for rec in self:
			if rec.status != 'sold':
				rec.status = 'cancel'
			else:
				raise UserError('sold property cannot be canceled.')

	_sql_constraints = [
    					('check_expected_price','CHECK(expected_price >= 0)','Enter Positive value of expected_price'),
    					('check_selling_price','CHECK(selling_price >= 0)','Enter Positive value of selling_price')
	]


	@api.constrains('selling_price')
	def _check_profit(self):
		for rec in self:
			# if float_compare(rec.selling_price) < (rec.expected_price * 90) / 100:
			for x in rec.offer_ids:
				if x.status != "accepted" and rec.selling_price != 0:
					if rec.selling_price < (rec.expected_price * 90) / 100:
						raise ValidationError("offer lower than 90% of the expected price.")


	@api.onchange("offer_ids")
	def _onchange_offer(self):
		for rec in self:
			# print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", len(rec.offer_ids))
			if len(rec.offer_ids) > 0:
				rec.status = "receive"
			else:
				rec.status = "new"

	# @api.ondelete(at_uninstall=False)
	def unlink(self):
		for rec in self:
			if rec.status == 'new' or rec.status == 'cancel':
				return super().unlink()
			else:
				raise UserError('Cannot delete property if it status is not new or canceled')


	# def add_info_wizard(self):
	# 	return {
	# 		'type': 'ir.actions.act_window',
	# 		'res_model': 'estate.wizard',
	# 		'name': 'Info Tab',
	# 		'view_mode': 'form',
	# 		'target': 'new'
	# 	}


		