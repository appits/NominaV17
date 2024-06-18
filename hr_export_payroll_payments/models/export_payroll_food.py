from odoo import models, fields, _


class ExportBankPaymentsFood(models.Model):
    _inherit = "export.bank.payments"
    _description = "Exportar pagos de bono alimenticio"

    type_trans = fields.Selection(selection_add=[("food", "Food voucher")])


    def _get_payslips(self) -> list:
        if self.type_trans == "food":
            domain = [
                ('date_from', '<=', self.date_end),
                ('date_to', '>=', self.date_start),
                ('struct_id', '=', self.payroll_type.id),
                ('state', '=', 'done'),
            ]
            payslips = self.env['hr.payslip'].search(domain)
        
        else:
            payslips = super(ExportBankPaymentsFood, self)._get_payslips()

        return payslips


    def action_done(self):
        if self.type_trans != "food":
            super(ExportBankPaymentsFood, self).action_done()
            return
        
        # {ci empleado : neto}
        emp = self._search_employee_food()
        date = self.valid_date.strftime("%d%m%Y")
        total_fill = 21

        txt_data = ""
        for e in emp.items():
            ci = e[0]
            ci = ci[:1] + "0" + ci[1:]
            net = e[1]

            # Se completa el campo con ceros a la izquierda para que quede con una longitud fija
            string_net = "{:.2f}".format(net).replace(".", "")
            fill = total_fill - len(string_net)
            string_net = "0" * max(0, fill) + string_net

            txt_data += f"{ci}  {string_net}{date}\n"
            
        self._write_attachment(txt_data, f"BONO_DE_ALIMENTACION-")
        self.write({'state': 'done'})


    def _search_employee_food(self):
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
                    COALESCE(SUM(line.total), 0) AS net

                FROM hr_payslip_line AS line
                    JOIN hr_payslip AS slip ON line.slip_id = slip.id
                    JOIN hr_employee AS emp ON slip.employee_id = emp.id
                    JOIN hr_salary_rule AS rules ON line.salary_rule_id = rules.id
                    JOIN hr_payroll_structure AS struct ON slip.struct_id = struct.id
                    JOIN hr_payroll_structure_type AS stype ON struct.type_id = stype.id
                    JOIN hr_salary_rule_category AS categ ON rules.category_id = categ.id

                WHERE
                    rules.code = 'NET'
                    AND categ.code = 'NET'
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

            SELECT * FROM employee_data WHERE net != 0
        """.format(date_to=self.date_end, date_from=self.date_start, c=company.id, condition=condition)

        self._cr.execute(query)
        raw_data = self.env.cr.dictfetchall()

        data = {}
        for val in raw_data:
            if val['currency_id'] != company.currency_id.id:
                date = fields.Date.today()
                currency = self.env['res.currency'].browse(val['currency'])
                net = currency._convert_payroll(val['net'], company.currency_id, company, date)
                val['net'] = net

            if not data.get(val['ci'], False):
                data[val['ci']] = 0

            data[val['ci']] += round(val['net'], 2)

        return data

