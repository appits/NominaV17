# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeSalaryAdvance(models.Model):
    _name = "hr_employee_salary_advance"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Employee salary advance"
    _order = "date desc"

    name = fields.Selection(
        # [("1", "Employee"), ("2", "Department"), ("3", "Company")],
        [("1", "Employee")],
        string="Advance type",
    )

    employee_ids = fields.Many2many(
        string="Employees", comodel_name="hr.employee", ondelete="restrict"
    )

    employee_id = fields.Many2one(
        string="Employee", comodel_name="hr.employee", ondelete="restrict"
    )

    employee_contract_ids = fields.Many2many(
        comodel_name="hr.contract", string="Employee contracts", ondelete="restrict"
    )

    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the salary advance tag without removing it.",
    )

    employee_payslip_id = fields.Many2one(
        comodel_name="hr.payslip", ondelete="restrict"
    )

    department_id = fields.Many2one(
        comodel_name="hr.department", ondelete="restrict", string="Department"
    )

    department_ids = fields.Many2many(
        comodel_name="hr.department", ondelete="restrict", string="Departments"
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", ondelete="restrict", string="Currency"
    )
    company_id = fields.Many2one(
        comodel_name="res.company", ondelete="restrict", string="Company"
    )

    date = fields.Date(string="Date")
    reason = fields.Selection(
        [
            ("1", "Advance payment of social benefits"),
            ("2", "Profit advance"),
            ("4", "Advance vacation"),
            ("3", "Advance Health"),
            ("5", "Advance Personal"),
        ],
        string="Reason",
        default="5" 
    )

    advancement = fields.Monetary(string="Amount")

    advance_vacation = fields.Boolean(string="It is a vacation bonus?")

    type_advance_vacation = fields.Selection(
        string="Type advance vacation", selection=[("1", "Bonus"), ("2", "Vacations")]
    )

    state = fields.Selection(
        selection=[
            ("draft", "To be sent"),
            ("confirm", "To be approved"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("refuse", "Rejected"),
        ],
        string="Status",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default="draft",
    )

    rate_id = fields.Many2one("res.currency.rate", string="Rate")
    rate_amount = fields.Float(string="Rate amount")

    quotes = fields.Integer(string="Nro de Cuotas", required=True, tracking=True, default=4)

    quot_actual = fields.Char(
        string="Cuota Actual",
        compute="_compute_quot_actual"
    )

    quote_amount = fields.Float(
        string="Cuota a Pagar", compute="_compute_quote_amount", store=True
    )

    debt_total = fields.Float(
        string="Deuda Total", compute="_compute_deuda_total", store=True
    )

    debt_inicial = fields.Float(
        string="Deuda Inicial", compute="_compute_deuda_total", store=True
    )
    payments_links_ids = fields.One2many(
        string="Payments Employee",
        comodel_name="hr_employee.debt_payment",
        inverse_name="salary_advance_id",
    )

    asig_struct_nomina = fields.Many2one(
        comodel_name="hr.payroll.structure", string="Asignar en Estructura"
    )

    desc_struct_nomina = fields.Many2many(
        "hr.payroll.structure", string="Descontar en Estructura"
    )

    active_advance = fields.Boolean(string="Active advance", default=True)
    money_assigned = fields.Boolean(string="Dinero asignado", default=False, copy=False)

    @api.onchange("reason")
    def _set_social_benefit_reason(self):
        if self.reason in ['1', '2']:
            self.quotes = 1

    @api.constrains('asig_struct_nomina', 'desc_struct_nomina', 'currency_id')
    def _check_struct_nomina_currencies(self):
        for record in self:
            if record.reason not in ['1']:
                desc_struct_currency = record._get_desc_struct_nomina_currencies( self.desc_struct_nomina )

                if not desc_struct_currency:
                    raise ValidationError(_("Todas las monedas en Descontar en Estructura tienen que ser la misma"))

                if record.asig_struct_nomina.currency_id != desc_struct_currency:
                    raise ValidationError(_("Todas las monedas en las estructuras escogidas tienen que ser la misma"))
                
                if desc_struct_currency != record.currency_id:
                    raise ValidationError(_("La moneda del préstamo y la moneda de las estructuras escogidas tienen que ser la misma"))

            else:
                if record.asig_struct_nomina.currency_id != record.currency_id:
                    raise ValidationError(_("Todas las monedas en las estructuras escogidas tienen que ser la misma"))

    @api.onchange('quotes')
    def _quotes_validation(self):
        if self.quotes <= 0:
            raise ValidationError(_("El número de cuotas no puede ser igual o menor a 0"))

    def _get_desc_struct_nomina_currencies(self, structures):

        first_currency = structures[0].currency_id
        for struct in structures:
            if first_currency != struct.currency_id:
                first_currency = None
                break
        return first_currency

    # Calcular Cuota Actual
    #TODO: REFACTOR
    @api.depends("payments_links_ids")
    def _compute_quot_actual(self):
        for record in self:
            quots = len(record.payments_links_ids) + 1
            record.quot_actual = quots if record.quotes >= quots else _("Paid")


    # Calcular Cuota Actual
    @api.depends("payments_links_ids")
    @api.onchange("payments_links_ids")
    def _onchange_payments_links_ids(self):
        count = 0 
        for line in self.payments_links_ids:
            count += 1
            line.cuota_nro = count
            
    # Calcular Deuda Total
    @api.depends("advancement", "quotes", "rate_amount", "payments_links_ids")
    def _compute_deuda_total(self):
        # La moneda del contrato
        company_currency = self.env.user.company_id.currency_id
        
        for rec in self:
            pagado = 0
            for pay in rec.payments_links_ids:

                if not pay.currency_id == company_currency:
                    pagado += pay.quote_amount * rec.rate_amount
                else:
                    pagado += pay.quote_amount

            advansacement = (
                rec.advancement * rec.rate_amount
                if not rec.currency_id == company_currency
                else rec.advancement
            )
            rec.debt_inicial = advansacement
            rec.debt_total = advansacement - pagado

    # Calcular Total en Cuotas
    @api.depends("advancement", "quotes", "rate_amount")
    def _compute_quote_amount(self):
        # La moneda del contrato
        company_currency = self.env.user.company_id.currency_id

        for rec in self:
            quote_amount = (
                rec.advancement / rec.quotes
                if rec.quotes and rec.quotes > 0
                else 0
            )

            if not rec.currency_id == company_currency:
                quote_amount = quote_amount * rec.rate_amount
            rec.quote_amount = quote_amount

    @api.onchange("rate_id", "currency_id")
    def _rate_onchange(self):
        company_currency = self.env.company.currency_id
        if self.rate_id:
            self.rate_amount = (
                self.rate_id.inverse_company_rate
                if not self.currency_id != company_currency
                else self.rate_id.company_rate
            )
        else:
            self.rate_amount = 1

    def name_get(self):
        result = []
        msg = " "

        for record in self:
            if self.name == "1":
                if len(self.employee_ids) == 1:
                    msg = str(self.employee_ids.name)
                else:
                    msg = _("Miscellaneous employees")
            elif self.name == "2":
                if len(self.department_ids) == 1:
                    msg = str(self.department_ids.name)
                else:
                    msg = _("Miscellaneous Departments")
            else:
                msg = str(self.employee_ids.company_id.name)
            result.append((record.id, msg))
            msg = " "
        return result

    @api.onchange("employee_ids")
    def _onchange_employee_ids(self):
        if self.name == "1":
            self.write({"employee_contract_ids": [(5, 0, 0)]})
            self.write({"department_ids": [(5, 0, 0)]})
            self.company_id = False
            if self.employee_ids:
                self.write(
                    {
                        "employee_contract_ids": [
                            (6, 0, self.employee_ids.contract_ids.ids)
                        ]
                    }
                )
                self.write(
                    {"department_ids": [(6, 0, self.employee_ids.department_id.ids)]}
                )
                self.company_id = self.employee_ids.company_id

    @api.onchange("department_ids")
    def _onchange_department_ids(self):
        if self.name == "2":
            self.write({"employee_ids": [(5, 0, 0)]})
            self.write({"employee_contract_ids": [(5, 0, 0)]})
            self.company_id = False
            if self.department_ids:
                self.write(
                    {"employee_ids": [(6, 0, self.department_ids.member_ids.ids)]}
                )
                self.write(
                    {
                        "employee_contract_ids": [
                            (6, 0, self.employee_ids.contract_ids.ids)
                        ]
                    }
                )
                self.company_id = self.employee_ids.company_id

    @api.onchange("company_id")
    def _onchange_company_id(self):
        if self.name == "3":
            employee_obj = self.env["hr.employee"].search(
                [("company_id", "=", self.company_id.id), ("active", "=", True)]
            )
            self.write({"employee_ids": [(5, 0, 0)]})
            self.write({"employee_contract_ids": [(5, 0, 0)]})
            self.write({"department_ids": [(5, 0, 0)]})
            if self.company_id:
                self.write({"employee_ids": [(6, 0, employee_obj.ids)]})
                self.write(
                    {
                        "employee_contract_ids": [
                            (6, 0, self.employee_ids.contract_ids.ids)
                        ]
                    }
                )
                self.write(
                    {"department_ids": [(6, 0, self.employee_ids.department_id.ids)]}
                )

    @api.constrains("employee_ids")
    def _check_employee_ids(self):
        if self.name == "1" and len(self.employee_ids) > 5:
            raise ValidationError(
                _("Advances per employee only accept a maximum of 5 employees")
            )

    #TODO revisar con Enith este comportamiento para las prestaciones MANTENER
    @api.constrains("advancement")
    def constrains_advancement(self):
        # Finding the amount of profits for the worker
        if self.name == "1":
            contract_obj = self.env["hr.contract"]
            advancement = self.currency_id._convert_payroll(
                self.advancement,
                contract_obj._get_fiscal_currency(),
                self.company_id,
                self.rate_id.name or fields.Date.today(),
            )
            print('advancement',advancement)
            for employee in self.employee_ids:
                first_contract = employee._get_first_contracts()
                result = False
                msj = " "
                # Validation of profit advances
                if self.name == "1" and self.reason == "2":
                    if first_contract:                        
                        aux_amount = first_contract.profit_accumulated - first_contract.profit_advance
                        
                        # Is the amount entered greater than the utilities available?
                        result = True if advancement > round(aux_amount, 2) else False
                        msj += _("to your profits")
                # Validation of social benefits
                elif self.name == "1" and self.reason == "1":
                    if first_contract:

                        # Is the amount deposited greater than 75% of the total available benefits?
                        # TODO:
                        # GRANTIA + DIAS ADICIONALES
                        # veremos
                        aux_amount = (
                            first_contract.available_social_benefits
                        )
                        result = (
                            True
                            if advancement > round(aux_amount * (75 / 100), 2)
                            else False
                        )
                        msj += _(
                            "to 75{} of the total amount of benefits available".format(
                                "%"
                            )
                        )
                else:
                    pass
                if result:
                    raise ValidationError(
                        _(
                            "The advance amount must not be greater than {}: {:,.2f}".format(
                                msj, aux_amount
                            )
                        )
                    )

    @api.constrains("name")
    def constrains_state(self):
        for record in self:
            record.write({"state": "confirm"})

    def action_confirm(self):
        for record in self:
            record.write({"state": "confirm"})

    def action_approve(self):
        active_ids = self.search( [('id', 'in', self.env.context.get('active_ids', False))] )
        records = active_ids or self

        for record in records:
            contract_obj = self.env["hr.contract"]
            for employee in record.employee_ids:
                current_contract = contract_obj._get_current_contract(employee)
                if record.reason == "3":
                    current_contract._compute_employee_loans(False, current_contract)
                elif record.reason == "4":
                    current_contract._compute_employee_holiday_advance(
                        False, current_contract
                    )
                else:
                    pass
            record.write({"state": "approved"})

    def action_refuse(self):
        active_ids = self.search( [('id', 'in', self.env.context.get('active_ids', False))] )
        records = active_ids or self

        for record in records:
            contract_obj = self.env["hr.contract"]
            advancement = record.currency_id._convert_payroll(
                record.advancement,
                contract_obj._get_fiscal_currency(),
                record.company_id,
                record.rate_id.name or fields.Date.today(),
            )
            for employee in record.employee_ids:
                current_contract = contract_obj._get_current_contract(employee)
                if record.reason == "3":
                    current_contract.employee_loans -= advancement
                    current_contract.employee_result_loans -= advancement
                elif record.reason == "4":
                    current_contract.employee_holiday_advance -= advancement
                    current_contract.employee_total_holiday_advance -= advancement
                else:
                    pass
            record.write({"state": "refuse"})

    def action_draft(self):
        for record in self:
            record.write({"state": "draft"})
