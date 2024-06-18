from odoo import models, fields, api, _

class HrContractHistoryCustomization(models.Model):
    _inherit = 'hr.contract.history'

    def massive_update_security_salary(self):
        for contract in self:
            open_contract = contract.contract_ids.filtered(lambda x: x.state == "open")
            for c in open_contract:
                c.check_compute_security_salary = True
                c.onchange_check_compute_security_salary()
