from odoo import models, fields, api, _

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    exceptions_employee_ids = fields.Many2many('hr.employee', string="Exceptions", ondelete='restrict')

    @api.depends('structure_id','department_id')
    def _compute_employee_ids(self):
        super(HrPayslipEmployees, self)._compute_employee_ids()

        for wizard in self:
            struct = wizard.structure_id
            exceptions = wizard.employee_ids.filtered(lambda x: struct.id in x.contract_id.exception_struct_ids.ids and x.contract_id.state == 'open')

            wizard.employee_ids -= exceptions
            wizard.exceptions_employee_ids = exceptions

