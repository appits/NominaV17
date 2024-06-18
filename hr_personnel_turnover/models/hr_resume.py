from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    is_training = fields.Boolean(related="line_type_id.is_training")

    duration = fields.Float(string="Duration", digits=(6, 2))
    type_training = fields.Selection(selection=[('in', "Internal"), ('out', 'External')],
                                    help="""
                                        Internal: training provied by empress
                                        External: training provied by others
                                    """)
    supplier_name = fields.Char(string="Supplier name", 
                                help="This is the name of the institute, academy or whoever provided the training.")
    

    @api.onchange("type_training")
    def _onchange_type_training(self):
        if self.type_training == "in":
            self.supplier_name = self.env.company.name
        else:
            self.supplier_name = ''


class ResumeLineType(models.Model):
    _inherit = 'hr.resume.line.type'

    is_training = fields.Boolean(default=False, invisible=True, readonly=True)


    def unlink(self):
        if self.is_training:
            raise ValidationError(_("This record can't be delete because is used to identify trainings"))

        super(ResumeLineType, self).unlink()
