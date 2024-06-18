# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    currency_id = fields.Many2one(related='contract_id.fiscal_currency_id')

    @api.depends('is_paid', 'number_of_hours', 'payslip_id', 'payslip_id.normal_wage', 'payslip_id.sum_worked_hours', 'payslip_id.rate_id')
    def _compute_amount(self):
        for worked_days in self.filtered(lambda wd: not wd.payslip_id.edited):
            if not worked_days.contract_id or worked_days.code == 'OUT':
                worked_days.amount = 0
                continue
            if worked_days.payslip_id.wage_type == "hourly":
                worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
            else:
                contract_salary = worked_days.contract_id.wage_currency._convert_payroll(worked_days.contract_id.wage, worked_days.contract_id.fiscal_currency_id, worked_days.contract_id.company_id, worked_days.payslip_id.rate_id.name or worked_days.payslip_id.date_to)
                worked_days.amount = (contract_salary / 30) * (worked_days.number_of_days or 1) if worked_days.is_paid else 0

