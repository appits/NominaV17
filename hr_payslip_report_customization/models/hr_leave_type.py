# -*- coding: utf-8 -*-
from odoo import models, fields


class hrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    is_remunerado_nomina = fields.Boolean(string='Es remunerado',
                                          default=False)


class hrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    is_remunerado_nomina = fields.Boolean(string='Es remunerado',
                                          default=False)
