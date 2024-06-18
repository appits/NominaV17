from odoo import models, fields, api, _

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def action_payslip_paid(self):
        super(HrPayslip, self).action_payslip_paid()

        for slip in self:
            #additional days of social benefits
            rule = slip.line_ids.filtered(lambda x: x.code == "DIAPPSS")
            if rule:
                slip.contract_id.additional_salary -= rule.total

            #first pay of profits
            rule = slip.line_ids.filtered(lambda x: x.code == "UTILIDADES")
            if rule:
                slip.contract_id.profit_paid = rule.total

            #paid of trust contribution
            rule = slip.line_ids.filtered(lambda x: x.code == "AFID")
            if rule and self.env.company.trust_config == "tri":
                slip.contract_id.trust_contribution -= rule.total
