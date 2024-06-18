from odoo import models, api, fields, _
from datetime import datetime
from pytz import timezone
import json


class HrPersonnelTurnover(models.Model):
    _name = "hr.personnel.turnover"
    _description = "HR Personal turnover"


    selection = [
        ("collective", _("Collective Contract")),
        ("decree", _("Presidential Decree")),
        ("evaluation", _("Evaluation")),
        ("level", _("Leveling")),
        ("promo", _("Promotion")),
        ("vacation", _("Vacation")),
        ("other", _("Other")),
    ]

    name = fields.Char(compute='_set_name')
    company_id = fields.Many2one("res.company", string="Company", ondelete="restrict", default=lambda self: self.env.company)

    validate_date = fields.Datetime(string="Validate date")

    state = fields.Selection(selection=[("refuse", "Refuse"), ("confirm", "To Approve"), ("validate", "Approved")], default="confirm")
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    contract_id = fields.Many2one("hr.contract", string="Contract")

    move_type = fields.Selection(string="Movement type", selection=[("in", "Internal"), ("out", "External")], required=True)
    reason = fields.Selection(string="Reason", selection=selection, required=True)
    description = fields.Char(string="Description", size=70)
    
    origin = fields.Char(required=True)
    changed_field = fields.Char(required=True)
    field_name = fields.Char(string="Field name", readonly=True)
    field_value = fields.Char(string="New value", readonly=True)

    user_changer = fields.Many2one("res.users", string="Changed by", readonly=True)
    user_validate = fields.Many2one("res.users", string="Validated by", readonly=True)


    def _set_name(self):
        self.name = _("Movement of ") + self.employee_id.name


    def validate_move(self):
        to_validate = self.filtered(lambda x: x.state == "confirm")

        for record in to_validate:
            if record.reason == "vacation":
                record.user_validate = record.user_changer
                record.state = "validate"
                continue

            record.validate_date = datetime.now()
            changed_field = json.loads(record.changed_field)
            origin = json.loads(record.origin)

            model = str(list(origin.keys())[0])
            value = list(origin.values())[0]

            model = self.env[model].search([('id', '=', value)])
            model.write(changed_field)

            record.user_validate = self.env.user
            record.state = "validate"


    def refuse_move(self):
        to_refuse = self.filtered(lambda x: x.state == "confirm")

        for record in to_refuse:
            if record.reason == "vacation":
                continue
            record.state = "refuse"


