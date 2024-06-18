from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval

class HrSalaryRule(models.Model):
	_inherit = 'hr.salary.rule'

	categ_code = fields.Char(related="category_id.code", string="Category code")

	account_debit_direct_cost_id = fields.Many2one('account.account', string="Debit account direct cost")
	account_credit_direct_cost_id = fields.Many2one('account.account', string="Credit account direct cost")
	account_debit_indirect_cost_id = fields.Many2one('account.account', string="Debit account indirect cost")
	account_credit_indirect_cost_id = fields.Many2one('account.account', string="Credit account indirect cost")


	@api.onchange('category_id')
	def onchange_category_code_id(self):
		invalid_categ = [
			'CONTRIB'
		]
		if self.categ_code in invalid_categ:
			self.account_debit_direct_cost_id = False
			self.account_credit_direct_cost_id = False
			self.account_debit_indirect_cost_id = False
			self.account_credit_indirect_cost_id = False
