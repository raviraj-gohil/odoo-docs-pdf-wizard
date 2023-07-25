from odoo import models, fields, api
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
	_name = "estate.property.offer"
	_description = "estate property offer details"
	_order = "price desc"


	price = fields.Float()
	status = fields.Selection(selection = [('accept', 'Accepted'),('refused', 'Refused')], copy=False, default="")
	partner_id = fields.Many2one("res.partner", string="Partner", required=True)
	property_id = fields.Many2one("estate.property", string="Property Type", required=True)
	current_date = fields.Date(default=fields.date.today())
	validity = fields.Integer(default=7)
	date_deadline = fields.Date(compute='_compute_date_deadline',inverse='_inverse_date_deadline')
	property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

	@api.depends("validity")
	def _compute_date_deadline(self):
		for record in self:
				record.date_deadline = False
				if record.validity:
					record.date_deadline = record.current_date + timedelta(days=record.validity)

	@api.depends('date_deadline')
	def _inverse_date_deadline(self):
		for record in self:
			if record.date_deadline:
				record.validity = (record.date_deadline - record.current_date).days


	def btn_accept(self):
		for rec in self:
			if rec.status != "accept" and rec.property_id.status != "accepted": 
				rec.status = "accept"
				rec.property_id.selling_price = rec.price
				rec.property_id.buyer_id = rec.partner_id
				rec.property_id.status = "accepted"


	def btn_refused(self):
		for rec in self:
			if rec.status != "refused":
				rec.status = "refused"
				if rec.property_id.status != "accepted":
					rec.property_id.selling_price = ''
					rec.property_id.buyer_id = ''
					rec.property_id.status = "rejected"

	_sql_constraints = [('check_offer_price','CHECK(price >= 0)','Enter Positive value of offer price')]


	@api.model
	def create(self, vals):
		property = self.env['estate.property'].browse(vals['property_id'])
		# print("--------------->>", property)
		if vals['price'] < property.best_price:
			raise UserError(f"Cannot create offer with a lower amount than {property.best_price:.2f}")
		property.status = 'receive'
		return super().create(vals)