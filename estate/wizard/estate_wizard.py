from odoo import models, fields, api

class EstateWizard(models.TransientModel):
   _name = 'estate.wizard'
   _description = 'Session Wizard'

   old_salesman = fields.Many2one("res.users", string="Old SalesMan")
   new_salesman = fields.Many2one("res.users", string="New SalesMan")


   def add_info(self):
      properties = self.env['estate.property'].search([('salesman_id', '=', self.old_salesman.id)])
      properties.salesman_id = self.new_salesman
