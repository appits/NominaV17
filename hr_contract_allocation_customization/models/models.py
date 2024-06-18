# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class HrContractCustomization(models.Model):
    _inherit = 'hr.contract'

    allocation = fields.Boolean(
        string='Allocation')
    
    allocation_ids = fields.Many2many(
        string='Allocations',
        comodel_name='hr_contract_allocation',
        ondelete='restrict')