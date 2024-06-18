from odoo import models, fields, _, api
from datetime import datetime
from odoo.exceptions import ValidationError


class ExportBankPaymentsTrust(models.Model):
    _inherit = "export.bank.payments"
    _description = "Exportar pagos de aporte de fideicomiso"

    type_trans = fields.Selection(selection_add=[("trust", "Trust contribution")])
    trust_contract_nro = fields.Integer(string="Nro. contract")


    @api.constrains('trust_contract_nro')
    def _save_trust_contract_nro(self):
        val = str(self.trust_contract_nro)
        if len(val) != 7 and self.type_trans == "trust":
            raise  ValidationError(_("The Trust Contract Number must be exactly 7 digits."))


    @api.onchange('bank_id')
    def _onchange_bank_account_id(self):
        if self.type_trans != "trust":
            return super(ExportBankPaymentsTrust, self)._onchange_bank_account_id()

        self.bank_account_id = False
        return {
            'domain': {
                'bank_account_id': [('bank_id', '=', self.bank_id.id), ('is_trust_account', '=', True)]
            }
        }


    def _get_payslips(self) -> list:
        if self.type_trans == "trust":
            domain = [
                ('date_from', '<=', self.date_end),
                ('date_to', '>=', self.date_start),
                ('struct_id', '=', self.payroll_type.id),
                ('state', '=', 'verify'),
            ]
            payslips = self.env['hr.payslip'].search(domain)
        
        else:
            payslips = super(ExportBankPaymentsTrust, self)._get_payslips()

        return payslips


    def action_done(self):
        if self.type_trans != "trust":
            super(ExportBankPaymentsTrust, self).action_done()
            return
        
        # {id empleado : cantidad}
        emp = self._search_employee_trust()
        txt_data = self._generate_txt_trust(emp)

        self._write_attachment(txt_data, f"APORTE DE FIDEICOMISO-")
        self.write({'state': 'done'})


    def _search_employee_trust(self):
        company = self.env.company

        condition = ""
        if self.get_data_from == "lote":
            ids = ", ".join([str(i) for i in self.lote_payroll_domain.ids])
            condition = f"AND slip.payslip_run_id IN ({ids}) "
        else:
            ids = ", ".join([str(i) for i in self.employee_ids.ids])
            condition = f"AND slip.id IN ({ids}) "

        query = """
            WITH employee_data AS (
                SELECT
                    slip.employee_id,
                    emp.identification_id AS ci,
                    stype.currency_id,
                    COALESCE(SUM(line.total), 0) AS amount

                FROM hr_payslip_line AS line
                    JOIN hr_payslip AS slip ON line.slip_id = slip.id
                    JOIN hr_employee AS emp ON slip.employee_id = emp.id
                    JOIN hr_salary_rule AS rules ON line.salary_rule_id = rules.id
                    JOIN hr_payroll_structure AS struct ON slip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS stype ON struct.type_id = stype.id
                    JOIN hr_salary_rule_category AS categ ON rules.category_id = categ.id

                WHERE
                    rules.code IN ('AFID', 'DIAPPSS')
                    AND slip.state = 'verify'
                    {condition}
                    AND '{date_to}' >= slip.date_from
                    AND '{date_from}' <= slip.date_to
                    AND (slip.company_id = {c} OR slip.company_id = NULL)

                GROUP BY
                    slip.employee_id,
                    emp.identification_id,
                    stype.currency_id
            )

            SELECT * FROM employee_data WHERE amount != 0
        """.format(date_to=self.date_end, date_from=self.date_start, c=company.id, condition=condition)

        self._cr.execute(query)
        raw_data = self.env.cr.dictfetchall()

        data = {}
        for val in raw_data:
            if val['currency_id'] != company.currency_id.id:
                date = fields.Date.today()
                currency = self.env['res.currency'].browse(val['currency'])
                net = currency._convert_payroll(val['amount'], company.currency_id, company, date)
                val['amount'] = net

            if not data.get(val['employee_id'], False):
                data[val['employee_id']] = 0

            data[val['employee_id']] += round(val['amount'], 2)

        return data


    def _generate_txt_trust(self, data):
        txt = ""

        if data:
            emp = self.env['hr.employee'].browse( list(data.keys()) )
            total_fill = 14
            strint_init = "01"
            string_date = datetime.now().strftime("%d%m%Y")
            string_contract = str(self.trust_contract_nro)

            for e in emp:
                ci = e.identification_id.replace("-", "").replace(" ", "")
                string_ci = ci[:1] + "0" + ci[1:]

                amount = data[e.id]
                string_amount = "{:.2f}".format(amount).replace(".", "")
                if string_amount[-2] == '.':
                    string_amount = string_amount + '0'
                fill = total_fill - len(string_amount)
                string_amount = "0" * max(0, fill) + string_amount

                txt += f"{strint_init}{string_date}{string_contract}{string_ci}{string_amount}\n"

        return txt
