from odoo import models, fields, api, _

class HrContractCustomization(models.Model):
    _inherit = 'hr.contract'

    exception_struct_ids = fields.Many2many('hr.payroll.structure', string="Exceptions")
