# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    nro_inden_labor = fields.Char(string='Número identificacion laboral (NIL)')

    nro_banavih = fields.Char(string='Número Afiliación Banavih')

    nro_patronal = fields.Char(string='Número Patronal (IVSS)')

    nro_inces = fields.Char(string='Código de Aportante INCES')
