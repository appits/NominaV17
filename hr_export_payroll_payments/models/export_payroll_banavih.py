from odoo import models, fields


class ExportBankPaymentsBanavih(models.Model):
    _inherit = "export.bank.payments"
    _description = "Exportar pagos de nomina banavih"

    type_trans = fields.Selection(selection_add=[("fiscal", " Banavih")])

    nro_banavih = fields.Char(string="nro afiliation banavih",
                              default=lambda self: self.env.company.nro_banavih)

    def action_done(self):
        """ Exportar el documento en texto plano. """
        super().action_done()
        # Contruccion de lineas Banavih
        if self.type_trans in ["fiscal"]:
            txt_data = self.generate_fiscal_payroll()
            fiscal_code = f"{self.date_end.month:0>2}{str(self.date_end.year)}"
            self._write_attachment(
                txt_data, f"{self.nro_banavih}{fiscal_code}", False)

    def _generate_str_name(self, employee_name) -> str:
        name_with_no_notation = self._normalize_str(employee_name.lower())
        upper_name = name_with_no_notation.upper()
        split_name = upper_name.split()
        first_name = split_name[0]
        second_name = "" if len(split_name) < 4 else split_name[1]
        first_surname = split_name[2] if len(
            split_name) == 4 else split_name[1]
        second_surname = "" if len(split_name) < 3 else split_name[-1]
        return f"{first_name},{second_name},{first_surname},{second_surname}"

    # Los datos que contiene el TXT para banavih son:
    # Nacionalidad, (C.I), 1er Nombre , 2do Nombre, 1er Apelli , 2do Apelli,
    # Monto  Devengado( Salario + Categories.Basic2)
    # Fecha de Inicio de Contrato, Fecha de Finalizacion del Contrato, LA LINEA DEBE TERMINAR CON COMA (,)
    def generate_fiscal_payroll(self):
        payslips = self._get_import_total_by_employee()
        ids = [k for k in payslips]
        employees = self.env["hr.employee"].search([("id", "in", ids)])
        txt_data = ""
        for employee in employees:
            identifi = employee.identification_id
            name = self._generate_str_name(employee.name)
            deb_amount = f"{payslips[employee.id]:.2f}".replace(".", "")
            contract_id = employee.contract_id
            entry_date = contract_id.date_start.strftime("%d%m%Y")
            exit_date = contract_id.date_end.strftime(
                "%d%m%Y") + "," if contract_id.date_end else ""

            # Contruccion de lineas
            txt_data += f'{identifi[0]},{identifi[1:]},{name},{deb_amount},{entry_date},{exit_date}\n'

        return txt_data.upper()

    def _get_import_total_by_employee(self):
        cache = {}
        for id_lote in self.lote_payroll_domain:
            domain = [
                ("slip_id.payslip_run_id", "=", id_lote.id),
                ("slip_id.contract_id.husing_policy_law", "=", True),
                ("slip_id.state", "=", "verify"),
                ("category_id.code", "in", ["BASIC", "BASIC2"])
            ]
            fields = ["employee_id", "total :sum"]
            groupby = ["employee_id"]
            group_data = self.env["hr.payslip.line"].read_group(
                domain, fields, groupby)

            for data in group_data:
                employee_id = data["employee_id"][0]
                total = data["total"]
                if employee_id in cache:
                    cache[employee_id] += total
                else:
                    cache[employee_id] = total
        return cache
