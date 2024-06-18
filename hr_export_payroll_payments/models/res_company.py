# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from datetime import datetime, date



class banavitBanavit(models.Model):
    _name = 'banavit.banavit'
    _description = 'Nro Afiliciacion banavit por company'

    name = fields.Char(string='Nro Afiliacion Banavit', tracking=True )
    company_id = fields.Many2one('res.company',
                string='Company',
                default=lambda self: self.env.user.company_id.id)
    
    
    _sql_constraints = [
        ('unique_company_id', 'unique(company_id)', "Ya existe un registro con la misma compañía"),
    ]
                
                
                
            
