from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    #save default data to print work constancy
    default_work_constancy = fields.Boolean(default=False)
    default_employee_work_constancy = fields.Char(default="")
    default_job_work_constancy = fields.Char(default="")

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_work_constancy(self):
        form_view = self.env.ref("hr_employee_customization.wizard_work_constancy_form")
        
        return{
            'name': _('Print Work Constancy'),
            'views': [ (form_view.id, 'form'), ],
            'res_model': 'wizard.work.constancy',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': { 'default_employee_id': self.ids, },
        }
    

class WizardWorkConstancy(models.Model):
    _name = 'wizard.work.constancy'
    _description='Work Constancy'

    def _get_default_employee(self):
        return self.env.user.default_employee_work_constancy
    
    def _get_default_job(self):
        return self.env.user.default_job_work_constancy

    def _get_default_check(self):
        return self.env.user.default_work_constancy

    def _get_employee_id(self):
        employees = self.env['hr.employee'].browse( self.env.context.get('default_employee_id', False) )
        return employees.filtered(lambda x: x.contract_id).ids
    

    employee = fields.Char(string="Name", default=lambda self: self._get_default_employee())
    job = fields.Char(string="Charge", default=lambda self: self._get_default_job())
    default = fields.Boolean(string="Set default", default=lambda self: self._get_default_check())
    employee_ids = fields.Many2many('hr.employee', default=lambda self: self._get_employee_id())


    def _save_values(self):
        if self.default:
            self.env.user.default_employee_work_constancy = self.employee
            self.env.user.default_job_work_constancy = self.job
            self.env.user.default_work_constancy = self.default

        else:
            self.env.user.default_employee_work_constancy = ""
            self.env.user.default_job_work_constancy = ""
            self.env.user.default_work_constancy = False


    def print_work_constancy(self):
        if not self.employee_ids:
            raise ValidationError(_("The employee don't have active contract"))
        self._save_values()
        
        return self.env.ref('hr_employee_customization.work_constancy_report_action').report_action(self)
