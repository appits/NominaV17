# -*- coding:utf-8 -*-


from odoo import api, fields, models, _


class HrPayrollStructureType(models.Model):
	_inherit = 'hr.payroll.structure.type'

	currency_id = fields.Many2one('res.currency', string="Currency")

class HrPayrollStructure(models.Model):
	_inherit = 'hr.payroll.structure'

	currency_id = fields.Many2one('res.currency', string="Currency", related='type_id.currency_id')

class HrSalaryRule(models.Model):
	_inherit = 'hr.salary.rule'

	currency_id = fields.Many2one('res.currency', string="Currency", related='struct_id.currency_id')

class HrPayslipLine(models.Model):
	_inherit = 'hr.payslip.line'

	currency_id = fields.Many2one(related='salary_rule_id.currency_id')
