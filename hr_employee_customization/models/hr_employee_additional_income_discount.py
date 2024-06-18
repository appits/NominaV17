from odoo import models, fields, api, _


class AdditionalEmployeeIncomeDiscount(models.Model):
    _name = 'hr_employee_additional_discount_income'
    _description = 'Employee additional Income and Discount'
    _order = 'start_date desc, end_date desc'

    name = fields.Char(string='Description')
    active = fields.Boolean(
        default=True, help="Set active to false to hide the additional Income and Discount tag without removing it.")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(string='Amount')
    start_date = fields.Date(string='Date from')
    end_date = fields.Date(string='Date to')
    employee_id = fields.Many2one(
        comodel_name='hr.employee', ondelete='restrict',string='Employee')
    contract_id = fields.Many2one(
        comodel_name='hr.contract', ondelete='restrict', string='Contract')
    contract_ids = fields.Many2many(
        comodel_name='hr.contract', string='Contracts')
    type = fields.Selection(
        string='Type',
        selection=[('1', 'Income'), ('2', 'Discount')],
        help="Indicate if it is an income or an additional discount"
    )

    rate_id = fields.Many2one('res.currency.rate', string='Rate')
    rate_amount = fields.Float(string="Rate amount")


    @api.onchange('rate_id')
    def _rate_onchange(self):
        company_currency = self.env.company.currency_id
        if self.rate_id:
            # self.rate_amount = self.rate_id.company_rate if self.rate_id.currency_id == company_currency else self.rate_id.inverse_company_rate
            self.rate_amount = self.rate_id.inverse_company_rate if self.rate_id.currency_id == company_currency else self.rate_id.company_rate
        else:
            self.rate_amount = 0


    @api.onchange('employee_id')
    def onchange_employee_id(self):
        # Searching for the Department and company of the employee
        self.contract_id = False
        self.contract_ids = False
        if self.employee_id:
            if self.employee_id.contract_id:
                self.contract_id = self.employee_id.contract_id.id
            else:
                self.write({'contract_ids': [(6, 0, self.employee_id.contract_ids.ids)]})
        else:
            pass
