# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class CancelPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_payslip_run_cancel(self):
        self.slip_ids.payslip_cancel()
        self.action_draft()

class CancelPayslip(models.Model):
    _inherit = 'hr.payslip'

    def payslip_cancel(self):
        self.action_payslip_draft()
        moves = self.mapped('move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        if self.filtered(lambda slip: slip.state == 'done'):
            raise UserError(_("Cannot cancel a payslip that is done."))

        # update employee's earnings
        # cancel_paid = False
        # sum_rejected_payrolls = 0
        # for payslip in self:
        #     for line in payslip.line_ids.filtered(lambda x: x.code in ['TA', 'TAVAC', 'TAQ']):
        #         if not line.slip_id.cancel_profit_paid:
        #             cancel_paid = True
        #             sum_rejected_payrolls += (
        #                 line.total * (self.company_id.profit_days / 360))

        #     if cancel_paid and sum_rejected_payrolls and payslip.contract_id.employee_profit > 0:
        #         payslip.cancel_profit_paid = True
        #         payslip.contract_id.employee_profit -= sum_rejected_payrolls
        #         if payslip.contract_id.employee_adu > 0:
        #             payslip.contract_id.employee_result_profit = payslip.contract_id.employee_profit - \
        #                 payslip.contract_id.employee_adu
        #         else:
        #             payslip.contract_id.employee_result_profit = payslip.contract_id.employee_profit
        self.write({'state': 'cancel'})