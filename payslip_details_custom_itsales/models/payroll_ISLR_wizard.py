from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, MissingError
from odoo.tools.misc import xlsxwriter
import calendar


class WizardReportISLR(models.TransientModel):
    _name = "wizard.report.islr"
    _description = "ISLR report wizard Model"

    start_date = fields.Date(string="From date")
    end_date = fields.Date(string="To date")
    LPVH = fields.Boolean(string="RPE")
    contract_ids = fields.Many2many("hr.contract")
    salary_structure_type = fields.Many2many("hr.payroll.structure", string="Salary structure type")
    
    order_table_by = fields.Selection(
        selection = [('registration_number','Receipt'),
                     ('identification_id','Identification Number'),
                     ('rif','RIF'),
                     ('name','Name'),],
        string='Order by',
        default='registration_number',
    )

    file_type = fields.Selection(
        selection = [('pdf_report','PDF'),
                    ('xlsx_report','EXCEL'),],
        string='File type',
        default='pdf_report',
    )

    # This modified query includes the end date, and also considers the selected salary structures
    def _get_islr_contracts(self, start_date, end_date, salary_struct_ids):
        """
            This function gets the employee contracts from the database.

            :param:
                start_date: start date to limit the employee contracts we are getting.
                end_date: end date to limit the employee contracts we are getting.
                salary_struct_ids: a list of integers that contains the ids of the salary structures

            :result:
                (int) returns a list of tuples containing two integers (int, int) that is, 
                the ids of the contracts and payslips. 
        """
        if salary_struct_ids:
            condition = ','.join([f'{repr(s)}' for s in salary_struct_ids])
            condition = f'AND slip.struct_id IN ({condition})'
        else:
            condition = f''

        query = """
            	SELECT DISTINCT ON (contract.id)
                    contract.id
                FROM hr_payslip AS slip 
                    JOIN hr_contract AS contract ON slip.contract_id = contract.id
                WHERE
                    slip.is_holiday_nomina IS TRUE
                    AND (contract.date_end IS NULL OR (contract.date_end <= '{d_to}' AND '{d_from}' <= contract.date_end))
                    AND slip.state IN ('done', 'paid')
                    {cond}
                UNION
                SELECT DISTINCT ON (contract.id)
                    contract.id
                FROM hr_payslip AS slip
                    JOIN hr_contract AS contract ON slip.contract_id = contract.id
                WHERE
                    slip.is_holiday_nomina IS NOT TRUE
                    AND '{d_from}' <= slip.date_from AND slip.date_to <= '{d_to}'
                    AND (contract.date_end IS NULL OR (contract.date_end <= '{d_to}' AND '{d_from}' <= contract.date_end))
                    AND slip.state IN ('done', 'paid')
                    {cond}
        """.format(d_from=start_date, d_to=end_date, cond=condition)

        self._cr.execute(query)
        data = self.env.cr.fetchall()
        return data
    

    # Define an auxiliary function to retrieve the contracts
    def retrieve_contracts(self):
        # Get the employee entries
        registry_entries = self.env["wizard.report.islr"]._get_islr_contracts(self.start_date, self.end_date, 
                                                                              self.salary_structure_type.ids)
         # If there are registers to print
        if registry_entries:
            contracts = [c[0] for c in registry_entries]
            self.contract_ids = self.contract_ids.browse(contracts)


    # Adds a method to calculate the employee's accrued based on some rules, their current salary and vacations
    @api.model
    def _calculate_accrued_employee(self, employee, start_date, end_date):
        employee_on_holiday = False
        end_contract_date = employee.employee_id.contract_id.date_end
        ded = employee._calculate_paid_interest_(start_date, end_date, ['DED', 'DED2'], True)
        accrued = employee._calculate_paid_interest_(start_date, end_date, ['BASIC', 'BASIC2', 'BASIC3', 'BASIC4',
                                                                            'PROM', 'PROMUTIL', 'UTIL'], True) - ded
        employee_on_holiday = employee._is_employee_on_holiday(start_date, end_date)

        # If the employee meets certain conditions, the accrued wage is rounded off 
        if not employee_on_holiday:
            if self._are_dates_in_month_limits(start_date, end_date):
                if not (end_contract_date and accrued == 0):
                    if accrued < employee.wage:
                        accrued = employee.wage
                    
        return accrued


    # Define a function to generate the pdf report
    def print_islr_report(self):
        self.retrieve_contracts()
        # If there are registers to print
        if self.contract_ids:
            return self.env.ref('payslip_details_custom_itsales.islr_report_action').report_action(self)
        else:
            raise MissingError(_('No se encontraron empleados para el tipo de nómina y estructura salarial en el periodo seleccionado.'))
    
    
    # Define a function to call the xlsx generator function
    def generate_xlsx_report_action(self):
        self.retrieve_contracts()
        # If there are registers to print
        if self.contract_ids:
            return self.env.ref('payslip_details_custom_itsales.report_banavih_report_action_xlsx').report_action(self)
        else:
              raise MissingError(_('No se encontraron empleados para el tipo de nómina y estructura salarial en el periodo seleccionado.'))          
        

    # Adds a validation check for the dates
    @api.constrains('start_date', 'end_date')
    def _check_valid_date_interval(self):
        if self.start_date > self.end_date :
            raise ValidationError(_('¡Error! La fecha de inicial debe ser anterior a la fecha final.'))


    # Verity if the selected date is exactly within a month
    def _are_dates_in_month_limits(self, start_date, end_date):
        start_month = start_date.month
        end_month = end_date.month
        start_day = start_date.day
        end_day = end_date.day
        return start_month == end_month and start_day == 1 and end_day == calendar.monthrange(start_date.year, start_month)[1]


class EmployeeReportXlsx(models.AbstractModel):
    _name = "report.payslip_details_custom_itsales.report_employee_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Print ISLR report in excel format"

    # Define a function to generate the xlsx report
    def generate_xlsx_report(self, workbook, data, obj):
        if obj.contract_ids:
            # Create a new worksheet
            sheet = workbook.add_worksheet('ISLR Report')

            # Set the column widths
            sheet.set_column('A:A', 5)      # Ficha
            sheet.set_column('B:B', 38)     # Nombre
            sheet.set_column('C:C', 12)     # Cédula
            sheet.set_column('D:D', 12)     # RIF
            sheet.set_column('E:E', 11)     # Ingreso
            sheet.set_column('F:F', 11)     # Egreso
            sheet.set_column('G:G', 15)     # Sueldo básico
            sheet.set_column('H:H', 15)     # Devengado
            sheet.set_column('I:I', 15)     # % Retención
            sheet.set_column('J:J', 13)     # Deducción

            # Set the row width (header)
            sheet.set_row(0, 40) 

            # Create the header row
            header = [
                _('Ficha'),
                _('Nombre'),
                _('Cédula'),
                _('RIF'),
                _('Fecha de Ingreso'),
                _('Fecha de Egreso'),
                _('Sueldo Básico'),
                _('Devengado'),
                _('Porcentaje de Retención (%)'),
                _('Deducción en el periodo'),
            ]

            # Give format to the header row
            header_format = workbook.add_format({'bold': True,
                                                 'text_wrap': True,
                                                 'align': 'center', 
                                                 'valign': 'vcenter'})

            # Write the header row
            row = 0
            col = 0
            for item in header:
                sheet.write(row, col, item, header_format)
                col += 1

            # Write the data rows
            row = 1
            total_month = 0
            holiday = False

            # Define format styles
            ids_format = workbook.add_format()
            ids_format.set_align('center')
            ids_format.set_align('vcenter')
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            date_format.set_align('center')
            date_format.set_align('vcenter')
            curr_format = workbook.add_format({'num_format': '#,##0.00'})
            curr_format.set_align('vcenter')
            percentage_format = workbook.add_format()
            percentage_format.set_align('vcenter')

            # Sort the contracts by structure type
            contracts = sorted(obj.contract_ids, key=lambda x: x.employee_id.mapped(obj.order_table_by))
            
            for contract in contracts:
                if not obj.LPVH or contract.employee_id.contract_id.husing_policy_law:
                    sheet.write(row, 0, contract.employee_id.registration_number, ids_format)
                    sheet.write(row, 1, contract.employee_id.name)
                    sheet.write(row, 2, contract.employee_id.identification_id, ids_format)
                    sheet.write(row, 3, contract.employee_id.rif or '', ids_format)
                    sheet.write(row, 4, contract.employee_id.contract_id.date_start, date_format)
                    sheet.write(row, 5, contract.employee_id.contract_id.date_end or '', date_format)
                    sheet.write(row, 6, contract.wage, curr_format)
                    accrued = obj._calculate_accrued_employee(contract, obj.start_date, obj.end_date)
                    sheet.write(row, 7, accrued, curr_format)
                    sheet.write(row, 8, contract.withholding_discount_rate, percentage_format)
                    deduction = contract._calculate_paid_interest_(obj.start_date, obj.end_date, ['ISLR'])
                    sheet.write(row, 9, deduction, curr_format)
                    row += 1
                    total_month += deduction

            # Write the total row
            sheet.write(row, 8, _('Total Deducido:'), workbook.add_format({'bold': True}))
            sheet.write(row, 9, total_month, curr_format)
        else:
            raise MissingError(_('No se encontraron empleados para el tipo de nómina y estructura salarial en el periodo seleccionado.'))
    