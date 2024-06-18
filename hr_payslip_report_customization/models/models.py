# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

# Nuevos calculos para Sabados y Domingos y dias totales en el periodo


def number_of_weekend_days(date1, date2):
    """ Returns the number of days between  the dates,
    considering weekends and totals days between  """
    weekend_days = 0
    total_days = 0
    current_date = date1
    while current_date <= date2:
        if current_date.weekday() in [5, 6]:
            weekend_days += 1
        else:
            total_days += 1
        current_date += timedelta(days=1)
    return weekend_days, total_days


class PayslipReport(models.Model):
    _inherit = "hr.payslip"

    leaves_all_days_ids = fields.Many2many(
        "hr.leave",
        "hr_payslip_custom_id",
        store=True,
        compute="compute_leaves_all_days_ids",
        string="Ausencias Contabilizadas",
    )

    format_struct_id_name = fields.Char(
        store=True,
        compute="_compute_format_struct_id_name",
        string="Estructura General",
    )

    leaves_all_days = fields.Integer(
        string="Ausencias Totales",
        store=True,
        compute='_compute_number_days_leaves_totales'
    )

    leaves_out_period = fields.Integer(
        string="Ausencias Fuera de Periodo",
    )

    net_salary_text = fields.Text(
        string="Neto en Texto", store=True, compute="_compute_net_amount_to_text"
    )

    is_holiday_nomina = fields.Boolean(string="Es Vacaciones", store=True)

    calcular_in_periodo = fields.Boolean(
        string="Ausencias en Periodo", store=True)

    period_holidays = fields.Char(string="Periodo de Vacaciones")

    weekend_days_hr = fields.Integer(
        string="Dias de Descanso", compute="_compute_number_of_weekend_days"
    )

    work_days_legales = fields.Integer(
        string="Vaciones Legales", compute="_compute_number_of_weekend_days"
    )

    work_days_hr = fields.Integer(
        string="Dias Vacaciones", compute="_compute_number_of_weekend_days"
    )

    work_days_aditionales = fields.Integer(
        string="Dias Adicionales", compute="_compute_number_of_weekend_days"
    )

    holidays_number_hr = fields.Integer(
        string="Dias Feriados Laborable", compute="_compute_number_holidays_in_date"
    )

    date_exit_holiday = fields.Char(
        string="Fecha de Salida Vacaciones", compute="_compute_date_holiday"
    )

    date_return_holiday = fields.Char(
        string="Fecha de Regreso Vacaciones", compute="_compute_date_holiday"
    )

    # Field to add the checkbox for the cestaticket receipts in the Payroll Receipts view.
    cestaticket_payment = fields.Boolean(
        string="Pago de Cestaticket", default=False)

    def get_current_employee_contract(self, employee):
        return self.env["hr.contract"]._get_current_contract(employee)

    def refund_sheet(self):
        """
        Heredar refund_sheet para devolver pagos a prestamos y
        actualizacion de ausencias

        Returns:
            _type_: res
        Heredar refund_sheet para devolver pagos a prestamos y
        actualizacion de ausencias
        """
        for leave in self.leaves_all_days_ids:
            if (
                self.name
                and "rembols" not in self.name.lower()
                and self.struct_id
                and "prestamo" not in self.name.lower()
            ):
                leave.payslip_state = "normal"

        if (
            self.name
            and "rembols" not in self.name.lower()
            and self.struct_id
            and "prestamo" not in self.name.lower()
        ):
            self.action_payslip_refund_prestamo()

        res = super(PayslipReport, self).refund_sheet()
        return res

    def action_payslip_refund_prestamo(self):
        """
        Crear Funcion para  Reembolso de prestamos

        Returns:
            _type_: Retorna True
        """

        # Agrega aquí tu propia lógica después de llamar a la función original
        # Agegar las lineas a el prestamo pagado
        total_pagado = sum(
            line.total
            for line in self.line_ids.filtered(
                lambda x: x.code in ["DPREST", "Descpresta"]
            )
        )
        contract = self.contract_id

        for advance in self.salary_advance_ids:

            if (
                contract.employee_result_loans > 0
                and advance.payments_links_ids[-1].quote_amount == total_pagado
            ):
                # una mejor forma de hacer esto seria agregar un campo
                # conectado a la nomina donde se paga el prestamo y al cancelar llamar a ese id
                advance.payments_links_ids[-1].unlink()

        # Actualizar los prestamos
        contract.update_advances()
        return True

    def action_payslip_paid_advance(self):
        """
        Crear Funcion para  pagos a prestamos
        """
        contract = self.contract_id
        # Actualizar los prestamos
        contract.update_advances()

        rule = self.line_ids.filtered(lambda x: x.code.startswith("PREST"))

        if contract.employee_result_loans > 0 and not rule:
            salary_advance_ids = contract.salary_advance_ids.filtered(lambda x: x.reason in ['3', '5'])
            for line in salary_advance_ids:
                struct = self.struct_id in line.desc_struct_nomina

                if line.debt_total > 0 and line.state == 'approved' and line.active_advance and struct:
                    pay_advance = line.quote_amount if line.debt_total > line.quote_amount else line.debt_total

                    pay_advance_dict = {
                        "employee_id": self.employee_id.id,
                        "currency_id": self.currency_id.id,
                        "date": datetime.now().date(),
                        "date_from": self.date_from,
                        "date_to": self.date_to,
                        "quote_amount": pay_advance,
                        "salary_advance_id": line.id,
                    }

                    pay_id = self.env["hr_employee.debt_payment"].create(pay_advance_dict)
                    pay_id.salary_advance_id._onchange_payments_links_ids()

                    if len(line.payments_links_ids) >= line.quotes:
                        line.write({"state": "paid"})


    def action_payslip_paid_advance_profit(self):
        """
        Crear Funcion para  pagos a prestamos utilidades
        """
        contract = self.contract_id
        
        rule = self.line_ids.filtered(lambda x: x.code == "UTILIDADES")
        if rule:
            salary_advance_ids = contract.salary_advance_ids.filtered(lambda x: x.reason == '2')
            for line in salary_advance_ids:
                struct = self.struct_id in line.desc_struct_nomina

                if line.debt_total > 0 and line.state == 'approved' and line.active_advance and struct:
                    pay_advance = line.quote_amount if line.debt_total > line.quote_amount else line.debt_total

                    pay_advance_dict = {
                        "employee_id": self.employee_id.id,
                        "currency_id": self.currency_id.id,
                        "date": datetime.now().date(),
                        "date_from": self.date_from,
                        "date_to": self.date_to,
                        "quote_amount": pay_advance,
                        "salary_advance_id": line.id,
                    }

                    pay_id = self.env["hr_employee.debt_payment"].create(pay_advance_dict)
                    pay_id.salary_advance_id._onchange_payments_links_ids()

                    if len(line.payments_links_ids) >= line.quotes:
                        line.write({"state": "paid"})


    def action_payslip_assign_advance(self):
        rules = self.line_ids.filtered(lambda x: x.code.startswith("PREST"))
        contract = self.contract_id

        for r in rules:
            try: rtype = r.code[5]
            except: rtype = ""
            salary_advance_ids = contract.salary_advance_ids.filtered(lambda x: x.reason == rtype and x.asig_struct_nomina.id == self.struct_id.id and not x.money_assigned)
            salary_advance_ids.money_assigned = True


    def action_payslip_paid(self):
        """
        Heredar action_payslip_paid para actualizar pagos a prestamos y
        actualizacion de ausencias
        """
        # Agrega aquí tu propia lógica después de llamar a la función original
        # Agegar las lineas a el prestamo pagado
        for rec in self:
            rec.action_payslip_paid_advance()
            rec.action_payslip_paid_advance_profit()
            rec.action_payslip_assign_advance()
            super(PayslipReport, rec).action_payslip_paid()


    @api.depends("employee_id", "contract_id", "struct_id", "date_from", "date_to")
    @api.onchange("employee_id", "contract_id", "struct_id", "date_from", "date_to")
    def _onchange_struct_id_false(self, domain=None):
        for rec in self:
            rec._compute_worked_days_line_ids()
            rec._compute_number_days_leaves_totales()


    # method for calculating the accumulated Allocations
    def accumulated_assignments(self):
        return sum(
            line.total
            for line in self.line_ids.filtered(
                lambda x: x.appears_on_payslip
                and x.category_id.code not in ['DED', 'DED2', 'DED3', 'DED4', 'COMP', 'SALDO']
            )
        )

    # method for calculating the accumulated Deductions
    def accumulated_deductions(self):
        return sum(
            line.total
            for line in self.line_ids.filtered(
                lambda x: x.appears_on_payslip 
                and x.category_id.code in ['DED', 'DED2', 'DED3', 'DED4', 'COMP']
            )
        )

    def compute_report_name(self):
        return (
            self.struct_id.report_name_id.name.upper()
            if self.struct_id.report_name_id
            else _("Salary Slip")
        )

    # Calcular en TEXTO el saldo a pagar neto para Bs en la nomina

    def _compute_net_amount_to_text(self):
        """Compute the net amount in text in the report nomina."""
        # La moneda del contrato
        for rec in self:
            total_a_pagar = 0
            asignaciones = rec.accumulated_assignments()
            deducciones = rec.accumulated_deductions()
            total_a_pagar = asignaciones - deducciones
            moneda = rec.currency_id
            if moneda:
                moneda = moneda.with_context(lang="es_VE")

            net_salary_text = moneda.amount_to_text(total_a_pagar)
            if moneda.name and "ve" in moneda.name.lower():

                net_salary_text = net_salary_text.replace(
                    " Bolivar ", " Bolivares ")
                net_salary_text = net_salary_text.replace(" Uno C", " Un C")
                net_salary_text = net_salary_text.replace(" y ", " con ")
                net_salary_text = net_salary_text.replace(" Y ", " y ")
            return net_salary_text

    def payslip_get_contract_wage(self):
        """_summary_: Esta funcion solo esta disponible para el report,
        Es necesaria para actualizar el campo sueldo o bono
        Asi como cambiar el monto en el reporte

        Returns:
            _type_: wage puede ser diferente para cada estructura o reporte
        """
        for record in self:
            if record.payslip_run_id:
                rate = record.payslip_run_id.rate_id
            else:
                rate = record.rate_id

            if (
                record.contract_id.wage_currency
                and record.struct_id.currency_id
                and rate
            ):
                wage = record.contract_id.wage_currency._convert_payroll(
                    record.contract_id._get_contract_wage(),
                    record.struct_id.currency_id,
                    record.company_id,
                    rate.name or fields.Date.today(),
                )
            else:
                wage = record.contract_id._get_contract_wage()
        return wage

    @api.depends('is_holiday_nomina')
    def _calculate_date_return_vacaciones(self, fecha_end_holiday):
        search_holidays_all = self.env["resource.calendar.leaves"].search([])
        if not fecha_end_holiday:
            return False

        while True:
            dia_es_feriado = search_holidays_all.filtered(
                lambda x: x.work_entry_type_id.name
                and "eriado" in x.work_entry_type_id.name.lower()
                and (
                    (x.date_to.date() > fecha_end_holiday and x.date_from.date(
                    ) < fecha_end_holiday)
                    or (x.date_to.date() == fecha_end_holiday)
                    or (x.date_from.date() == fecha_end_holiday)
                )
            )

            if fecha_end_holiday.weekday() not in [5, 6] and not dia_es_feriado:
                return fecha_end_holiday
            fecha_end_holiday += timedelta(days=1)

    # Calcular Dias Feriados segun el periodo y la estructura

    @api.depends("date_to", "date_from", "struct_id")
    def _compute_date_holiday(self):
        """
        _compute_date_holiday: Esta funcion Calcula los dias feriados para
        el periodo y la estructura, se vio necesario crearla para actualizar
        dias a trabajar en el reporte asi como los dias de descanso en el
        calendario definido como publico.
        """

        for rec in self:
            rec.date_exit_holiday = False
            rec.date_return_holiday = False
            if rec.struct_id.name and "acaci" in (rec.struct_id.name).lower():
                dominio_search = [
                    ("employee_ids", "in", [rec.employee_id.id]),
                    ("request_date_to", "<=", rec.date_to),
                    ("request_date_from", ">=", rec.date_from),
                    ("state", "=", "validate"),
                    ("is_holiday_nomina", "=", True),
                ]
                search_holidays = rec.env["hr.leave"].search(
                    dominio_search, limit=1)

                if not search_holidays.request_date_to:
                    rec.date_exit_holiday = False
                    rec.date_return_holiday = False
                    return True

                rec.date_exit_holiday = search_holidays.request_date_from.strftime(
                    "%d-%m-%Y")

                fecha_return_vacaciones = search_holidays.request_date_to + \
                    timedelta(+1)
                date_return_vacaciones = self._calculate_date_return_vacaciones(
                    fecha_return_vacaciones)
                rec.date_return_holiday = date_return_vacaciones.strftime(
                    "%d-%m-%Y")

    # Calcular numero de dias de descanso teniendo en cuenta feriados

    @api.depends("date_from", "date_to")
    def _compute_number_of_weekend_days(self):
        """
        Calcula numer de dias de descanso totales
        """
        for rec in self:
            rec.weekend_days_hr = 0
            rec.work_days_hr = 0
            rec.holidays_number_hr = 0
            rec.work_days_aditionales = 0
            rec.work_days_legales = 0
            if rec.is_holiday_nomina:

                if rec.date_from and rec.date_to:
                    date_from = rec.date_from
                    date_to = rec.date_to
                    rec.weekend_days_hr, total_dias = number_of_weekend_days(
                        date_from, date_to
                    )
                    rec.holidays_number_hr = self._compute_number_holidays_in_date(
                        date_from, date_to
                    )
                    rec.work_days_hr = total_dias - rec.holidays_number_hr
                    if rec.work_days_hr > 15:
                        rec.work_days_legales = 15
                        rec.work_days_aditionales = rec.work_days_hr - 15
                    else:
                        rec.work_days_legales = rec.work_days_hr

    # Verificar si es Vacaciones

    @api.depends("holiday_status_id")
    def _compute_is_holiday_nomina(self):
        for rec in self:
            rec.is_holiday_nomina = False
            if (
                rec.holiday_status_id.name
                and "vacaci" in (rec.holiday_status_id.name).lower()
            ):
                rec.is_holiday_nomina = True

    # Lista de Feriados

    @api.depends("date_from", "date_to")
    def compute_lista_feriados(self, date1, date2, search_holidays_all):
        """_summary_

        Args:
            date1 (Fecha): Periodo desde
            date2 (Fecha): Periodo hasta
            search_holidays_all (Lista Recordset): Todos los feriados

        Returns:
            dias_feriado Entero: Cantidad de Dias Feriados
        """
        date_list = []
        d = date1
        while d <= date2:
            date_list.append(d.strftime("%Y-%m-%d"))
            d += timedelta(days=1)
        dias_feriado = 0
        for fecha in date_list:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date()

            dia_es_feriado = search_holidays_all.filtered(
                lambda x: x.work_entry_type_id.name
                and "eriado" in x.work_entry_type_id.name.lower()
                and (
                    (x.date_to.date() > fecha and x.date_from.date() < fecha)
                    or (x.date_to.date() == fecha)
                    or (x.date_from.date() == fecha)
                )
            )
            if dia_es_feriado and fecha.weekday() not in [5, 6]:
                dias_feriado += 1
        return dias_feriado

    # Retornar lista de dias feriados y verifica si el periodo termina como feriado

    @api.depends("date_to", "date_from")
    def _compute_number_holidays_in_date(self, date_from, date_to):
        """_summary_

        Args:
            date_from (date): fecha desde
            date_to (date): fecha hasta

        Returns:
            integer: dias_feriado
        """
        search_holidays_all = self.env["resource.calendar.leaves"].search([])
        if date_to and date_from:
            try:
                date_from = date_from.date()
                date_to = date_to.date()
            except:
                date_from = date_from
                date_to = date_to

            dias_feriado = self.compute_lista_feriados(
                date_from, date_to, search_holidays_all
            )

        return dias_feriado

    def _get_number_days_leaves_in_period(self, search_leaves_all, date_from, date_to):
        """_summary_
        Metodo que filtra los dias de ausencia en el periodo

        Args:
            search_leaves_all (lista de recorset): Todas las ausencias
            date_from (date): fecha desde
            date_to (date): fecha hasta

        Returns:
            integer : dias_ausencia_total
        """
        rec = self
        data1 = search_leaves_all.filtered(
            lambda x: (rec.employee_id in x.employee_ids)
            and (rec.date_from <= x.request_date_from <= rec.date_to)
        )

        data2 = search_leaves_all.filtered(
            lambda x: (rec.employee_id in x.employee_ids)
            and (rec.date_from <= x.request_date_to <= rec.date_to)
        )
        # Es necesario comparar conjuntos por si tengo dias parciales en el periodo

        set_data1 = set(data1.ids)
        set_data2 = set(data2.ids)
        different_set = set_data1 ^ set_data2
        common_days = 0
        if different_set:
            different_list = [x for x in different_set]
            data_verificar = rec.env["hr.leave"].search(
                [("id", "in", different_list)])
            iterar_dias = 0
            for data in data_verificar:
                inicio_current = data.request_date_to
                current_date = inicio_current + timedelta(iterar_dias)
                # verificar si el dia esta dentro del segundo periodo
                if date_from <= current_date <= date_to:
                    common_days += 1
                iterar_dias += 1

        search_leaves_all = search_leaves_all.filtered(
            lambda x: (rec.employee_id in x.employee_ids)
            and (rec.date_from <= x.request_date_from <= rec.date_to)
            and rec.date_from <= x.request_date_to <= rec.date_to
        )
        dias_ausencia = sum(search_leaves_all.mapped("number_of_days"))
        dias_no_filtrados = common_days

        rec.leaves_all_days = dias_ausencia + dias_no_filtrados
        return rec.leaves_all_days

    # Retornar numero de ausencias
    @api.depends("employee_id", "date_to", "date_from")
    @api.onchange("employee_id", "date_to")
    def _compute_number_days_leaves_totales(self):
        """ Funcion que calcula numero de dias de ausencia Dentro
        y fuera del periodo
        Returns:
            leaves_all_days integer: Numero de Dias dentro del Periodo
            leaves_out_period integer: Numero de Dias fuera del Periodo
        """
        for rec in self:
            rec.leaves_all_days = 0
            if rec.date_to and rec.date_from:
                try:
                    date_from = rec.date_from.date()
                    date_to = rec.date_to.date()
                except:
                    date_from = rec.date_from
                    date_to = rec.date_to

                search_leaves_all = rec._get_search_leaves_all()

                dias_ausencia_total = sum(
                    search_leaves_all.mapped("number_of_days")
                )

                rec.leaves_all_days = rec._get_number_days_leaves_in_period(
                    search_leaves_all, date_from - timedelta(days=15), date_to
                )

                rec.leaves_all_days = dias_ausencia_total
                rec.update({'leaves_all_days': dias_ausencia_total})

    @api.depends("date_to", "date_from")
    def _get_search_leaves_all(self):
        """Extraer Lista de Ausencias Totales dentro
        y fuera del Periodo

        Returns:
            Recorset: Dias de ausencias dentro y fuera de Periodo
        """
        for rec in self:
            if rec.date_to and rec.date_from:
                try:
                    date_from = rec.date_from.date()
                    date_to = rec.date_to.date()
                except:
                    date_from = rec.date_from
                    date_to = rec.date_to

                search_leaves_all = rec.env["hr.leave"].search(
                    [
                        ("state", "in", ["validate"]),
                        ("payslip_state", "in", ["normal", "blocked", 'done']),
                    ]
                )

                limite_bajar = timedelta(days=15)
                search_out_leaves_all = search_leaves_all.filtered(
                    lambda x: (
                        rec.employee_id in x.employee_ids
                        and (x.date_to.date() <= date_to)
                        and (x.date_from.date() >= date_from - limite_bajar)
                    )
                )

                search_leaves_all = rec.env["hr.leave"].search(
                    [
                        ("state", "in", ["validate"]),
                        ("payslip_state", "in", ["normal", "blocked", "done"]),
                    ]
                )

                search_leaves_all = search_leaves_all.filtered(
                    lambda x: (
                        rec.employee_id in x.employee_ids
                        and (x.date_to.date() <= date_to)
                        and (x.date_from.date() >= date_from)
                        and x.id not in search_out_leaves_all.ids
                    )
                )

                if search_out_leaves_all:
                    search_leaves_all = search_leaves_all + search_out_leaves_all
                return search_leaves_all

    @api.depends("date_to", "date_from")
    def compute_leaves_all_days_ids(self):
        """Calcular todas las ausencias y guardar en worked_days_line_ids

        Returns:
            Lista lista_leaves: Lista de Ausencias
        """
        ### Returns the values of the worked_days_line_ids ###

        for rec in self:
            rec.leaves_all_days_ids = False
            search_leaves_all = rec._get_search_leaves_all()

            lista_leaves = []
            lista_leaves_ids = []

            for leave in search_leaves_all:
                if isinstance(rec.id, fields.NewId):
                    rec_origin = rec._origin
                    if rec.format_struct_id_name == rec_origin.format_struct_id_name:
                        rec_origin = rec._origin
                        rec = rec_origin
                # Es necesario buscar las hojas de pago para verificar si la ausencia esta en alguna de las estructuras
                search_payslips_employee = rec.env["hr.payslip"].search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("format_struct_id_name", "=", rec.format_struct_id_name),
                        ("state", "in", ["done", "paid"]),
                    ]
                )

                search_filtered = search_payslips_employee.filtered(
                    lambda x: (
                        x.id != rec.id and leave.id in x.leaves_all_days_ids.ids and leave.full_paid)
                )

                if (
                    not search_filtered and leave.id not in lista_leaves
                ):  # si existe no agregar para no procesar, ya que existe en otra nomina de la misma estructura
                    lista_leaves_ids.append([4, leave.id])
                    lista_leaves.append(leave)

            rec.update({'leaves_all_days_ids': lista_leaves_ids})

            return lista_leaves

    @api.depends("struct_id")
    def _compute_format_struct_id_name(self):
        """
        Genera un char como tipo de estructura para ser buscado
        y analizar ausencias fuera de periodo
        """

        for rec in self:
            if rec.struct_id and rec.struct_id.name:
                struct_name = rec.struct_id.name
                format_struct_id_name = struct_name.replace('1era ', '')
                format_struct_id_name = format_struct_id_name.replace(
                    '2da ', '')
                rec.format_struct_id_name = format_struct_id_name


    def action_print_payslip(self):
        for slip in self:
            if 'liquida' in (slip.struct_id.name).lower() and not slip.contract_id.average_salary:
                raise ValidationError(_("There's no average salary calculated in the contract"))
            slip.contract_id.update_advances()

        return super(PayslipReport, self).action_print_payslip()
    
    
class PayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    report_name_id = fields.Many2one(
        string="Report name", comodel_name="hr_report_names", ondelete="restrict"
    )


class UomCategory(models.Model):
    _inherit = "uom.category"

    is_payroll_category = fields.Boolean(string="Is payroll category")


class PayrollInput(models.Model):
    _inherit = "hr.payslip.input"

    uom_id = fields.Many2one(
        string="Uom", comodel_name="uom.uom", ondelete="restrict")
