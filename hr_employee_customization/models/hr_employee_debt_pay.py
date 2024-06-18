# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeDebtPayment(models.Model):
    _name = "hr_employee.debt_payment"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Employee Debt Payment"
    _order = "date desc"

    name = fields.Selection(
        [("1", "Employee"), ("2", "Department"), ("3", "Company")],
        string="Advance type",
    )

    employee_ids = fields.Many2many(
        string="Employees", comodel_name="hr.employee", ondelete="restrict"
    )

    employee_id = fields.Many2one(
        string="Employee", comodel_name="hr.employee", ondelete="restrict"
    )

    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the salary advance tag without removing it.",
    )

    employee_payslip_id = fields.Many2one(
        comodel_name="hr.payslip", ondelete="restrict"
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", ondelete="restrict", string="Currency"
    )

    company_id = fields.Many2one(
        comodel_name="res.company", ondelete="restrict", string="Company"
    )

    date = fields.Date(string="Date")

    date_from = fields.Date(string="Date from")
    date_to = fields.Date(string="Date to")

    state = fields.Selection(
        selection=[("draft", "Borrador"), ("confirm", "Pagado")],
        string="Status",
        required=True,
        tracking=True,
        default="draft",
    )

    rate_id = fields.Many2one("res.currency.rate", string="Rate")
    salary_advance_id = fields.Many2one(
        "hr_employee_salary_advance", string="Advance Salary id", ondelete="restrict",
    )
    rate_amount = fields.Float(string="Rate amount")

    quote_amount = fields.Float(string="Cuota a Pagar")
    deuda_total = fields.Float(string="Deuda Total")

    cuota_nro = fields.Char(string="Nro Cuota")

    