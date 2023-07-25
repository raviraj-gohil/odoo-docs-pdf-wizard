from odoo import models, fields, api


class EstatePropertyType(models.Model):
	_name = "estate.property.type"
	_description = "estate property type details"
	_order = "sequence"


	name = fields.Char(required=True)
	property_ids = fields.One2many("estate.property", "property_type_id")
	sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
	offer_ids = fields.One2many('estate.property.offer', 'property_type_id')
	offer_count = fields.Integer(compute='_compute_count_number')

	_sql_constraints = [('check_type_name','unique(name)','property type must be unique')]


	def find_offer(self):
		offers = self.offer_ids
		# print("--------------------------------------------------------------------------------->", offers)
		return {
		'type':'ir.actions.act_window',
		'name':'Offers',
		'view_mode':'tree',
		'res_model':'estate.property.offer',
		'domain': [('id','in',offers.ids)],
		}
	

	@api.depends("offer_ids")
	def _compute_count_number(self):
		for rec in self:
			count_offer = 0
			for count in rec.offer_ids:
				count_offer += 1
			rec.offer_count = count_offer
