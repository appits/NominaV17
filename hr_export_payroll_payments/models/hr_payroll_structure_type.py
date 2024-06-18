
from odoo import models, fields, api

class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    is_worker_payroll = fields.Boolean(string="Nómina de obrero", default=False, help="Indica si el tipo de estructura es para una nómina de obrero.")