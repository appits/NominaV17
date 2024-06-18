# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = ['hr.salary.rule', 'mail.thread.cc', 'mail.activity.mixin']
    

    # Tracking fields
    name = fields.Char(tracking=True)
    category_id = fields.Many2one(tracking=True)
    code = fields.Char(tracking=True)
    struct_id = fields.Many2one(tracking=True)
    appears_on_payslip = fields.Boolean(tracking=True)
    sequence = fields.Integer(tracking=True)
    active = fields.Boolean(tracking=True)
    condition_select = fields.Selection(tracking=True)
    condition_range = fields.Char(tracking=True)
    condition_range_min = fields.Float(tracking=True)
    condition_range_max = fields.Float(tracking=True)
    condition_python = fields.Text(tracking=True)
    amount_select = fields.Selection(tracking=True)
    amount_python_compute = fields.Text(tracking=True)
    amount_percentage_base = fields.Char(tracking=True)
    quantity = fields.Char(tracking=True)
    amount_percentage = fields.Float(tracking=True)
    amount_fix = fields.Float(tracking=True)
    note = fields.Text(tracking=True)
    account_debit = fields.Many2one(tracking=True)
    account_credit = fields.Many2one(tracking=True)
    analytic_account_id = fields.Many2one(tracking=True)
    not_computed_in_net = fields.Boolean(tracking=True)
