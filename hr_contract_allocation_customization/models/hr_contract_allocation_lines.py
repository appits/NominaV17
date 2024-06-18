# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class HrContractAllocationLine(models.Model):
    _name = 'hr_contract_allocation_lines'
    _description = "Endowment lines"

    # Allocation

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )

    allocation_id = fields.Many2one(
        string='Allocation',
        comodel_name='hr_contract_allocation',
        ondelete='restrict',
    )

    size_id = fields.Many2one(
        string='Size',
        comodel_name='hr_contract_allocation_size',
        ondelete='restrict',
    )

    allocated_quantity = fields.Float(
        string='Allocated quantity',
        default=0
    )

    frequency = fields.Integer(
        string='Frequency',
        default=0
    )

    delivery_frequency = fields.Selection(
        string='Delivery frequency',
        selection=[('weekly', 'Weekly'), ('monthly','Monthly'), ('annual', 'Annual')],
        default='monthly'
    )

    # Delivery

    quantity_delivered = fields.Float(
        string='Quantity delivered',
        default=0
    )

    date_delivered = fields.Date(string='Date delivered')

    
    @api.onchange('quantity_delivered')
    def _onchange_quantity_delivered(self):
        for record in self:
            if record.quantity_delivered > record.allocated_quantity:
                raise UserError (_('You cannot deliver more than the allotted quantity.'))

