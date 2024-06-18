# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta

class HrContractAllocation(models.Model):
    _name = 'hr_contract_allocation'
    _description = 'Contract allocations'
    _order = 'allocation_date desc'

    name = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
    
    employee_contract_ids = fields.Many2many(
        comodel_name='hr.contract',
        string='Employee contract',
        compute='_compute_current_contract',
        ondelete='restrict',
        store=True
    )
    
    allocation_date = fields.Date(
        string='Allocation date',
        default=fields.Date.context_today,
    )

    allocation_line_ids = fields.One2many(
        string='Allocation line',
        comodel_name='hr_contract_allocation_lines',
        inverse_name='allocation_id',
    )

    delivered_count = fields.Integer(compute='compute_delivered_count')

    active = fields.Boolean(
        default=True, help="Set active to false to hide the allocation tag without removing it.")

    @api.depends('name')
    def _compute_current_contract(self):
        contract_obj = self.env['hr.contract']
        for record in self:
            if record.name:
                record.employee_contract_ids = contract_obj._get_current_contract(record.name)

    def get_endowments_delivered(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Dotaciones entregadas'),
            'view_mode': 'tree',
            'res_model': 'hr_contract_allocation_lines',
            'domain': [('allocation_id.name', '=', self.name.id), ('quantity_delivered', '>', 0)],
            'context': "{'create': False}"
        }

    def get_lines_to_delivered(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': ('Líneas de Dotaciones a entregar'),
            'view_mode': 'tree',
            'res_model': 'hr_contract_allocation_lines',
            'domain': [('allocation_id.name', '=', self.name.id), ('quantity_delivered', '=', 0)],
            'context': "{'create': False}",
            'target': "new",
        }


    def compute_delivered_count(self):
        for record in self:
            record.delivered_count = self.env['hr_contract_allocation_lines'].search_count(
                [('allocation_id.name', '=', self.name.id), ('quantity_delivered', '>', 0)])