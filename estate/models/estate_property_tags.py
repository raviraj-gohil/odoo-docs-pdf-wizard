from odoo import models, fields


class EstatePropertyTags(models.Model):
	_name = "estate.property.tags"
	_description = "estate property tags details"
	_order = "name"


	name = fields.Char(required=True)
	color = fields.Integer(default="1")

	_sql_constraints = [('check_tag_name','unique(name)','property tags must be unique')]
	