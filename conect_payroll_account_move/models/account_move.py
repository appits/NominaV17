# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountMove(models.Model):
	_inherit = "account.move"

	payroll_id = fields.Many2one('hr.payslip', string="Payroll")
	payroll_run_id = fields.Many2one('hr.payslip.run', string="Payroll lot")
