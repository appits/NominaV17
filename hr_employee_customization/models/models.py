# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
from odoo.exceptions import UserError, ValidationError
import re

from datetime import date,datetime
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_employee_additional_discounts(self):
        discounts_obj = self.env['hr_employee_additional_discount_income'].search(
            [('employee_id', '=', self.id)])

        if discounts_obj:
            self.write({'employee_additional_discounts_ids': [(6, 0, discounts_obj.ids)]})
        else:
            self.employee_additional_discounts_ids = False


    @api.depends("birthday")
    def _compute_employe_age(self):
        for rec in self:
            if rec.birthday:
                birthday = fields.Date.from_string(rec.birthday)
                employee_age = relativedelta(datetime.now(), birthday)
                rec.employee_age =  employee_age.years
            else:
                rec.employee_age =  0
                
                
    employee_additional_discounts_ids = fields.One2many(comodel_name='hr_employee_additional_discount_income',
                                                        inverse_name='employee_id', compute='_compute_employee_additional_discounts', help='Additional employee discount')

    coach_custom_id = fields.Many2one(
        'hr.employee', 'Coach', readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
            'The "Coach" has no specific rights or responsibilities by default.')

    salary_advance_ids = fields.Many2many(
        string='salary_advance',
        comodel_name='hr_employee_salary_advance',
        help="Salary advances requested by the employee",
        ondelete='restrict'
    )

    account_holder = fields.Char(
        string='Account holder', groups="hr.group_hr_user", help="Bank account holder")

    holder_account_id = fields.Char(
        string='C.I. of the account holder', groups="hr.group_hr_user", help="ID of the account holder")

    bank_account_number = fields.Char(
        string='Bank account number',
        groups="hr.group_hr_user",
        tracking=True,
        help='Employee Salary Bank Account')

    rif = fields.Char(string='R.I.F', groups="hr.group_hr_user")


    account_type = fields.Selection([
        ('1', 'Current account'),
        ('2', 'Savings account')], string="Type of account", groups="hr.group_hr_user", help='Type of employees bank account.') 

    bank_id = fields.Many2one('res.bank', 'Bank', help="Bank to which the beneficiary's bank account belongs.")

    
    employee_has_vehicle = fields.Boolean(
        string='Has vehicle?',
    )

    employee_age = fields.Integer(
        string='Employee age',
        compute="_compute_employe_age")

    employee_height = fields.Float(
        string='Employee height',
        default=0,
    )

    is_left_handed = fields.Boolean(
        string='Is left handed')
    
    employee_weight = fields.Float(
        string='Employee weight')
    
    hr_employee_type_id = fields.Many2one('hr.employee.type', string='Worker type')

    @api.constrains('identification_id')
    def _check_identification_id(self):

        def validate_expression(expression):
            pattern = r'^[EV]\d{8,}$'
            match = re.match(pattern, expression)
            return match is not None

        if not validate_expression(self.identification_id):
            raise ValidationError(_('¡Cuidado! Asegúrese de que su Nº identificación no contiene símbolos especiales. \n Sólo la letra E o V seguida de ocho cifras. Si el número tiene menos de 8 cifras, rellénelo con ceros al inicio. \n Por ejemplo: V08154872 o E00154234".'))

    @api.onchange('bank_id')
    def onchange_bank_id(self):
        if self.bank_id and self.bank_id.bic == False:
            raise exceptions.ValidationError("Por favor establezca el Código de identificación bancaria (BIC/SWIFT) para el banco seleccionado")

    @api.constrains('bank_account_number')
    def _check_bank_account_number(self):
        if self.bank_account_number and (not self.bank_account_number.isnumeric() or len(self.bank_account_number) != 20):
            raise ValidationError(
                _('Only numeric characters [0-9] are allowed and the total length of the bank account number must be equal to 20 characters.'))

    @api.constrains('account_holder')
    def _check_account_holder(self):
        account_holder_len = len(self.account_holder)
        account_holder_name = self.account_holder.replace(' ', '')
        if self.account_holder and (not account_holder_name.isalpha() or account_holder_len > 30):
            raise ValidationError(
                _('The account holders name must contain only alphabetic characters [a-z,A-Z] and its length must not exceed 30 characters.'))

    
    @api.constrains('holder_account_id')
    def _check_holder_account_id(self):
        if self.holder_account_id and (not self.holder_account_id.isnumeric() or len(self.holder_account_id) != 8):
            raise ValidationError(
                _('Only numeric characters [0-9] are allowed and the total length of the account holders I.D. number must be equal to 8 characters.'))

    def write(self, vals):
        res = {}
        if vals.get('rif'):
            res = self.validate_rif(vals.get('rif', False))
            if not res:
                raise ValidationError(_(
                    'Warning! The rif has the wrong format. Ej: V-012345678, E-012345678, J-012345678 o G-012345678. Please try again'))
            if not self.validate_rif_duplicate(vals.get('rif', False)):
                raise ValidationError(
                    _('Warning! The client or supplier is already registered with the rif: %s and is active') % (
                        vals.get('rif', False)))
        res = super(HrEmployee, self).write(vals)
        return res

    @api.model
    def create(self, vals):
        res = {}
        if vals.get('rif'):
            res = self.validate_rif(vals.get('rif'))
            if not res:
                raise ValidationError(_(
                    'Warning! The rif has the wrong format. Ej: V-012345678, E-012345678, J-012345678 o G-012345678. Please try again'))
            if not self.validate_rif_duplicate(vals.get('rif', False), True):
                raise ValidationError(
                    _('Warning! The client or supplier is already registered with the rif: %s and is active') % (
                        vals.get('rif', False)))
        res = super(HrEmployee, self).create(vals)
        return res

    @api.model
    def validate_rif(self, field_value):
        rif_obj = re.compile(r"^[V|E|J|G]+[-][\d]{9}", re.X)
        if rif_obj.search(field_value.upper()):
            if len(field_value) == 11:
                return True
            else:
                return False
        return False

    def validate_rif_duplicate(self, valor, create=False):
        found = True
        company = self.search([('rif', '=', valor)])
        if create:
            if company:
                found = False
        elif company:
            found = False
        return found


    def _get_write_amount(self):
        wage = self.contract_id.wage
        currency = self.contract_id.wage_currency
        if currency:
            currency = currency.with_context(lang="es_VE")

        salary_text = currency.amount_to_text(wage)
        salary_text = salary_text.replace( " Bolivar ", " Bolivares ")
        salary_text = salary_text.replace(" Uno C", " Un C")
        salary_text = salary_text.replace(" y ", " con ")
        salary_text = salary_text.replace(" Y ", " y ")
        salary_text = salary_text.replace(",", "")        

        if "Cts" not in salary_text:
            salary_text += " con Cero Cts"

        return salary_text
