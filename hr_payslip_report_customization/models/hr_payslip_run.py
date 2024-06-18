# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    # Field to add the checkbox of the cestaticket receipts in the batch view of payroll receipts
    cestaticket_payment = fields.Boolean(
        string="Pago de Cestaticket", default=False
    )

    # Update the cestaticket_payment field for all the registers 
    @api.onchange('cestaticket_payment')
    def cestaticket_payment_enable(self):
        self.slip_ids.cestaticket_payment = self.cestaticket_payment


# To update the registers for the wizzard.
class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    # This function adds the updated cestaticket entries to the run lot
    def _set_payslip_vals(self, run, contract):
        res = super(HrPayslipEmployees, self)._set_payslip_vals(run, contract)

        # Updates the cestaticket field for all of the registers, adding it to the  
        res.update({
            'cestaticket_payment': run.cestaticket_payment,
        })

        return res
