from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime
from lxml import etree
import json

class WizardPersonnelTurnover(models.TransientModel):
    _name = "wizard.personnel.turnover"
    _description = "Wizard personal turnover"



    def _get_employee(self):
        model = self._context.get("model", False)
        value = self._context.get("value", False)

        if model:
            res = self.env[model].browse([value])

        return res.employee_id if model == "hr.contract" else res

    
    def _create_personnel_turnover(self):
        changes = self._context.get("changes", {})
        vals = []
        res = self.env["wizard.personnel.turnover.line"]

        for field, value in changes.items():
            val = self._get_turnover_vals(field, value)
            res += self.env["wizard.personnel.turnover.line"].with_context(changed_field = {field: value}).create(val)

        return res.ids


    def _set_url(self):
        action_id = self.env.ref('hr_personnel_turnover.personnel_turnover_action').id
        return "/web#action={}&amp;view_type=list&amp;model=hr.personnel.turnover".format(action_id)


    employee_id = fields.Many2one("hr.employee", string="Employee", default=_get_employee)
    turnover_ids = fields.One2many("wizard.personnel.turnover.line", "personnel_id", default=_create_personnel_turnover)
    turnover_url = fields.Char(default=_set_url, readonly=True, invisible=True)



    def _get_turnover_vals(self, field, value):
        employee = self._get_employee()
        change = json.dumps({field: value})
        origin = {self._context.get("model", False): self._context.get("value", False)}
        origin = json.dumps(origin)

        val = {
            "origin": origin,
            "employee_id": employee.id,
            "changed_field": change,
        }

        return val


    def _get_approver_emails(self):
        approver = self.env.ref('hr_payroll.group_hr_payroll_manager').users
        return ",".join([e for e in approver.mapped("email") if e])
    

    def validate_personnel_turnover(self):
        vals = []
        for history in self.turnover_ids:
            vals.append( history._preparer_vals() )

        self.env["hr.personnel.turnover"].create(vals)

        self._send_emails()

        return self.close_personnel_turnover()


    def _send_emails(self):
        template_id = self.env.ref("hr_personnel_turnover.mail_personnel_turnover").id
        self.env["mail.template"].browse(template_id).send_mail(self.id, force_send=True)


    def close_personnel_turnover(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class WizardPersonnelTurnoverLine(models.TransientModel):
    _name = "wizard.personnel.turnover.line"
    _description = "HR Personal turnover line"


    selection = [
        ("collective", _("Collective Contract")),
        ("decree", _("Presidential Decree")),
        ("evaluation", _("Evaluation")),
        ("level", _("Leveling")),
        ("promo", _("Promotion")),
        ("other", _("Other")),
    ]

    personnel_id = fields.Many2one("wizard.personnel.turnover", readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    contract_id = fields.Many2one("hr.contract", string="Contract", compute="_set_contract")

    move_type = fields.Selection(string="Movement type", selection=[("in", "Internal"), ("out", "External")])
    reason = fields.Selection(string="Reason", selection=selection)
    description = fields.Char(string="Description", size=70)
    
    origin = fields.Char(required=True)
    changed_field = fields.Char(required=True)
    field_name = fields.Char(string="Field name", readonly=True, compute="_set_name_value_changed")
    field_value = fields.Char(string="New value", readonly=True)


    @api.depends("employee_id")
    def _set_contract(self):
        for record in self:
            record.contract_id = record.employee_id.contract_id


    def _set_name_value_changed(self):
        for record in self:
            change_dict = json.loads(record.changed_field)
            origin = json.loads(record.origin)
            o = str(list(origin.keys())[0])

            if o == "hr.contract":
                model = record.employee_id.contract_id
            else:
                model = record.employee_id
            
            field_str = str(list(change_dict.keys())[0])
            field = model._fields[field_str]

            value = list(change_dict.values())[0]
            if field.type in ["many2one", "one2many", "many2many"]:
                comodel = field.base_field.comodel_name
                value = self.env[comodel].search([('id', '=', value)]).name

            record.field_name = self.env['ir.translation'].get_field_string(model._name)[field_str]
            record.field_value = value


    def write_success(self):
        pass


    def _preparer_vals(self):
        val = {
            'user_changer': self.env.user.id,
            'company_id': self.env.company.id,
            'state': 'confirm',
            'employee_id': self.employee_id.id,
            'contract_id': self.contract_id.id,
            'reason': self.reason,
            'move_type': self.move_type,
            'description': self.description,
            'origin': self.origin,
            'changed_field': self.changed_field,
            'field_name': self.field_name,
            'field_value': self.field_value,
        }

        return val

