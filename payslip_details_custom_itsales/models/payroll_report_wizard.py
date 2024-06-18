# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardReportPayslipDetail(models.TransientModel):
    _name = "wizard.report.payslip.detail"
    _description = "Payslip Detail report wizard Model"

    date_start = fields.Date(string="Start Date",
                             required=True,
                             default=fields.Date.today)

    date_end = fields.Date(string="End Date",
                           required=True,
                           default=fields.Date.today)

    # Tener en cuenta que este state puede cambiar
    state = fields.Selection([("draft", "Borrador"),
                              ("verify", "En Espera"),
                              ("done", "Hecho"),
                              ("paid", "Pagado"),
                              ("cancel", "Rechazada")],
                             string="Estado",
                             default="done")

    state_lote = fields.Selection([("draft", "Nuevo"),
                                   ("verify", "Confirmado"),
                                   ("close", "Hecho"),
                                   ("paid", "Pagado")],
                                  string="Estado",
                                  default="verify")

    type_payslip_id = fields.Many2one("hr.payroll.structure",
                                      string="Tipo de Nomina")

    is_for_contract = fields.Boolean(string="Por Contrato", default=False)

    type_contract_ids = fields.Many2one("hr.contract.type",
                                        string="Tipo de contrato")

    is_for_reference = fields.Boolean(string="Por referencia", default=False)

    reference_ids = fields.Many2one('hr.payslip.run',
                                    domain="[('date_start', '>=', date_start), ('date_end', '<=', date_end), ('state', '=', state_lote)]",
                                    string="Tipo de referencia")

    type_report = fields.Selection([("detallado", "Detallado"),
                                    ("conceptos", "Por Conceptos")],
                                   string="Tipo de Reporte",
                                   default="Detallado")

    payslip_ids = fields.Many2many(comodel_name="hr.payslip",
                                   relation="rel_wizard_payslip_detail_report",
                                   string="Hojas de Pago")

    def get_lines_ids_formated(self, payslip_id):
        lines_ids_formated = []
        for line in payslip_id.line_ids:
            if (
                line.category_id.code in [
                    "ALW", "BESP", "GROSS", "UTIL",
                    "BASIC", "BASIC2", "BASIC3", "BASIC4", "BASIC5"]
                and line.salary_rule_id.appears_on_payslip
            ):
                lines_ids_formated.append(
                    [line.name, line.salary_rule_id.sequence, round(line.total, 2), 0, round(line.total, 2), 1, line.duration_display])
            if (
                line.category_id.code in [
                    "COMP", "CONTRIB", "BEMP", "DED", "DED2"]
                and line.salary_rule_id.appears_on_payslip
            ):
                lines_ids_formated.append(
                    [line.name, line.salary_rule_id.sequence, 0, round(line.total, 2), round(-line.total, 2), 1, line.duration_display])
        return lines_ids_formated

    def get_lines_ids_totales(self, payslip_id):
        asignaciones = round(payslip_id.accumulated_assignments(), 2)
        deducciones = round(payslip_id.accumulated_deductions(), 2)
        return [asignaciones, deducciones]

    def get_lines_ids_neto(self, payslip_id):
        asignaciones = round(payslip_id.accumulated_assignments(), 2)
        deducciones = round(payslip_id.accumulated_deductions(), 2)
        neto_pagar = round(asignaciones - deducciones, 2)
        if neto_pagar < 0:
            neto_pagar * -1
        return neto_pagar

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_("start date must be less than end date."))

    def generate_report(self):
        get_payslip = []
        if self.is_for_reference:
            get_payslip = self.reference_ids.slip_ids
        else:
            dominio_payslip = [
                ("date_from", ">=", self.date_start),
                ("date_to", "<=", self.date_end),
                ("state", "=", self.state),
                ("struct_id", "=", self.type_payslip_id.id)
            ]
            if self.type_contract_ids.id:
                dominio_payslip.append(
                    ("contract_id.contract_type_id", "=", self.type_contract_ids.display_name))

            get_payslip = self.env["hr.payslip"].search(dominio_payslip)

        if self.type_report == 'detallado':
            data = self.get_data_detail(get_payslip)
            set_ref_action = "payslip_details_custom_itsales.report_payroll_detail_action"

        elif self.type_report == 'conceptos':
            data = self.get_data_concepts(get_payslip)
            set_ref_action = "payslip_details_custom_itsales.report_payroll_by_concepts_action"

        return self.env.ref(set_ref_action).report_action([], data)

    def get_data_detail(self, payslips) -> dict:
        payroll_by_period = {}
        for employee in payslips:
            empleado = employee.employee_id.name
            identificacion = employee.employee_id.identification_id
            puesto = employee.employee_id.job_title
            salario = "{:,.2f}".format(employee.employee_id.contract_ids.wage)
            salario_f = salario.replace(
                ",", "@").replace(".", ",").replace("@", ".")
            fecha_ingreso = employee.employee_id.contract_id.date_start
            payslip_data = self.get_lines_ids_formated(employee)
            payslip_totales = self.get_lines_ids_totales(employee)
            payslip_neto_pagar = self.get_lines_ids_neto(employee)

            for amount in payslip_data:
                if amount[3] < 0:
                    amount[3] = amount[3] * -1

            lista_dict_data = [
                empleado,
                identificacion,
                puesto,
                salario_f,
                fecha_ingreso.strftime("%d/%m/%Y"),
                payslip_data,
                payslip_totales,
                payslip_neto_pagar,
            ]

            departamento = employee.contract_id.department_id.name

            if employee.struct_id.name not in payroll_by_period:
                depar_empl = {departamento: [lista_dict_data]}
                payroll_by_period[str(employee.struct_id.name)] = depar_empl
            else:
                depar_empl = payroll_by_period[employee.struct_id.name]
                if departamento in depar_empl:
                    depar_empl[departamento].append(lista_dict_data)
                else:
                    depar_empl[departamento] = [lista_dict_data]

        payroll_by_period[str(employee.struct_id.name)] = dict(
            sorted(payroll_by_period[employee.struct_id.name].items()))

        report_name = 'payslip_details_custom_itsales.payroll_detail_doc'
        report = self.env['ir.actions.report']._get_report_from_name(
            report_name)

        html = report.report_action(self.ids)

        return {"date_start": self.date_start.strftime("%d/%m/%Y"),
                "date_end": self.date_end.strftime("%d/%m/%Y"),
                "payroll_by_period": payroll_by_period,
                "html": html,
                "type_report": self.type_report}

    def get_data_concepts(self, payslips) -> dict:
        payroll_concept = []
        max_count = 0
        totales = []

        for employee in payslips:
            max_count += 1
            employee_data = self.get_lines_ids_formated(employee)
            payroll_concept.append(employee_data)

        payroll_concept_group = self.group_lista(payroll_concept)

        for amount in payroll_concept_group:
            if amount[3] < 0:
                amount[3] = amount[3] * -1

        asignaciones = sum([sublist[1]
                            for sublist in payroll_concept_group])
        deducciones = sum([sublist[2]
                           for sublist in payroll_concept_group])

        total_general = asignaciones - deducciones

        totales = [asignaciones, deducciones, total_general]

        report_name = 'payslip_details_custom_itsales.payroll_by_concepts_doc'
        report = self.env['ir.actions.report']._get_report_from_name(
            report_name)
        html = report.report_action(self.ids)

        return {"date_start": self.date_start.strftime("%d/%m/%y"),
                "date_end": self.date_end.strftime("%d/%m/%y"),
                "payroll_concept": payroll_concept_group,
                "nro_employees": max_count,
                "totales": totales,
                "html": html,
                "type_payslip_id": self.type_payslip_id.name.upper(),
                "type_report": self.type_report}

    def group_lista(self, lista_full) -> list:
        dictionary_inter = {}
        concepts_name = list(range(0, 100))
        concepts = []
        # Recorremos la lista y agrupamos las listas con la misma primera letra
        for lista in lista_full:
            for element in lista:
                # n = lista.index(element)
                if element[0] in dictionary_inter:
                    dictionary_inter[element[0]].append(element[2:6])
                else:
                    dictionary_inter[element[0]] = [element[2:6]]
                    concepts_name.insert(element[1], element[0])

        for concept in concepts_name:
            if type(concept) == str:
                concepts.append(concept)
        # concepts = [name  ]
        lista_comp = list(range(0, len(concepts)))
        # Creamos la lista comprimida sumando los elementos correspondientes
        for clave, values in dictionary_inter.items():
            sum_all = [sum(x) for x in zip(*values)]
            flag = sum_all[0] + sum_all[2]
            if flag != 0:
                lista_comp.insert(concepts.index(
                    clave), [clave] + sum_all)
        rect_comp = []
        for comp in lista_comp:
            if type(comp) == list:
                rect_comp.append(comp)
        return rect_comp
