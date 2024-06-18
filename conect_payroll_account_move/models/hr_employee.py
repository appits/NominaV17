from odoo import models, fields, api, _, exceptions
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    select = [
        ('exp', 'Expense'),
        ('d_cost', 'Direct costs'),
        ('i_cost', 'Indirect costs')
    ]
    account_location = fields.Selection(selection=select, string="Accounting location", default="exp", required=True,
        help="""
Configure the accounts in which payroll payments will be recorded.

Expenses: it will take the expense accounts from the rules (base behavior).
Direct cost: it will take the direct cost accounts from the rules.
Indirect cost: it will take the indirect cost accounts from the rules.
""" )