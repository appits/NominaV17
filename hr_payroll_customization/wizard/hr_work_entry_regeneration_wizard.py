from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrWorkEntryRegenerationWizard(models.TransientModel):
    _inherit = 'hr.work.entry.regeneration.wizard'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=False)

    employee_ids = fields.Many2many('hr.employee', string="Employees")
    massive_regeneration = fields.Boolean(  string="Massive regeneration", default=False,
                                            help="""
                                                Active this check to bring al employee with ongoing contract.\n
                                                Desactive to clean all selected employees
                                                """)


    @api.onchange('massive_regeneration')
    def _get_all_employee(self):
        self.employee_ids = None
        employee_ids = self._get_employee_ids()
        if self.massive_regeneration:
            self.employee_ids = self.employee_ids.browse(employee_ids)

        return {'domain':{'employee_ids':[('id', 'in', employee_ids)]}}


    def _get_employee_ids(self):
        query = """
            SELECT DISTINCT ON (employee.id)
                employee.id
            FROM hr_contract AS contract
                JOIN hr_employee AS employee ON contract.employee_id = employee.id
            WHERE
                contract.state = 'open'
        """

        self._cr.execute(query)
        data = self.env.cr.fetchall()
        data = [d[0] for d in data]

        return data


    def massive_regenerate_work_entries(self):
        try:
            def _set_employee_id(wizard, employee):
                wizard.employee_id = employee
            
            for employee in self.employee_ids:
                _set_employee_id(self, employee)
                self.regenerate_work_entries()
                
        except Exception as e:
            raise ValidationError(_("Error while regenerating work entries of {employee}:\n\n{e}".format(employee=self.employee_id.name, e=e)))
