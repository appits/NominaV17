import re
from unicodedata import normalize
import time
import base64
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ExportBankPayments(models.Model):
    _name = 'export.bank.payments'
    _description = 'Exportar pagos de nomina'

    _READONLY_STATES = {'done': [('readonly', True)]}

    name = fields.Char(string='Nombre', default='Nuevo', readonly=True)

    state = fields.Selection([('draft', 'Borrador'), ('done', 'Confirmado')],
                             string='Estado de transacción',
                             default='draft',
                             copy=False)

    type_trans = fields.Selection([('payroll', 'Empleados')],
                                  string='Pago a',
                                  default='payroll',
                                  help='Indica el tipo de txt a generar',
                                  states=_READONLY_STATES)

    bank_id = fields.Many2one(
        'res.bank', string='Banco', states=_READONLY_STATES)

    bank_account_id = fields.Many2one('res.partner.bank',
                                      string='Número de Cuenta Bancaria',
                                      help='Cuenta bancaria de la compañía de donde será debitado el dinero',
                                      states=_READONLY_STATES)

    operation_type = fields.Selection([('same', 'Mismo banco'),
                                       ('other', 'Otros bancos')],
                                      string='Tipo de operación',
                                      default='same',
                                      help='Indica si el pago de nominas es entre cuentas del mismo banco o no',
                                      states=_READONLY_STATES)

    valid_date = fields.Date(string='Fecha efectiva de pago',
                             help="Fecha en que se ejecutará el pago.",
                             states=_READONLY_STATES)

    description = fields.Char(string='Descripción',
                              help='Texto descriptivo asociado al archivo txt generado', states=_READONLY_STATES)

    date_start = fields.Date(string='Fecha inicio', states=_READONLY_STATES)

    date_end = fields.Date(string='Fecha fin', states=_READONLY_STATES)

    get_data_from = fields.Selection([('individual', 'Individual'), ('lote', 'Lote')],
                                     default='individual',
                                     string="Pago")

    payroll_type = fields.Many2one('hr.payroll.structure',
                                   string='Estructura',
                                   help='Tipo de estructura de nómina para la generación del archivo txt',
                                   states=_READONLY_STATES,)

    employee_domain = fields.Many2many('hr.payslip',
                                       compute='_get_employee',
                                       string='Dominio para Empleados',
                                       help='Dominio para filtrar empleados')

    employee_ids = fields.Many2many('hr.payslip',
                                    string='Empleados',
                                    help='Empleados para los que se genera el archivo txt',
                                    states=_READONLY_STATES)

    lote_payroll_domain = fields.Many2many('hr.payslip.run',
                                           string='Lotes',
                                           domain="[('date_start', '>=', date_start), ('date_end', '<=', date_end), ('state', '=', 'verify')]",
                                           readonly=False)

    txt_file = fields.Binary(string='Archivo TXT', copy=False)

    txt_name = fields.Char(string='Filename txt', copy=False)

    @api.onchange('bank_id')
    def _onchange_bank_account_id(self):
        if self.type_trans == 'payroll':
            self.bank_account_id = False
            self.employee_ids = False
        banks = self.env['res.partner.bank'].search([])
        banks_ids = []
        for bank in banks:
            if bank.is_payroll_account:
                banks_ids.append(bank.id)
        return {'domain': {'bank_account_id': [('id', 'in', banks_ids),
                                               ('bank_id', '=', self.bank_id.id)]}}

    @api.onchange('type_trans')
    def _onchange_type_trans(self):
        if self.type_trans == 'fiscal':
            self.get_data_from = 'lote'

    @api.depends('payroll_type', 'bank_account_id', 'operation_type', 'date_start', 'date_end', 'get_data_from')
    def _get_employee(self):
        for record in self:
            record.employee_domain = record._get_payslips()

    def _get_payslips(self) -> list:
        """
        Consulta de recibos de pagos. De acuerdo a las siguientes condiciones:
            1. ...
        """
        domain = [
            ('date_from', '=', self.date_start),
            ('date_to', '=', self.date_end),
            ('struct_id', '=', self.payroll_type.id),
            ('state', '=', 'verify'),
        ]
        payslips = self.env['hr.payslip'].search(domain)
        return self.employee_for_operation_type(payslips)

    def employee_for_operation_type(self, payslips) -> list:
        if self.operation_type == 'same':
            payslips = payslips.filtered(
                lambda emp: emp.employee_id.bank_account_number[:4] == self.bank_account_id.acc_number[:4])
        else:
            payslips = payslips.filtered(
                lambda emp: emp.employee_id.bank_account_number[:4] != self.bank_account_id.acc_number[:4])

        payslips = payslips.filtered(lambda emp: emp.net_wage > 0)

        return payslips

    def employee_for_lote(self, payslips):
        empleados = payslips.employee_id

        if self.operation_type == 'same':
            empleados = empleados.filtered(
                lambda emp: emp.bank_account_number[:4] == self.bank_account_id.acc_number[:4])
        else:
            empleados = empleados.filtered(
                lambda emp: emp.bank_account_number[:4] != self.bank_account_id.acc_number[:4])

        empleados = payslips.filtered(lambda emp: emp.net_wage > 0)

        return empleados

    @api.onchange("get_data_from", "payroll_type")
    def _onchange_get_data_from(self):
        self._get_employee()
        if self.get_data_from == 'individual':
            self.lote_payroll_domain = False
        elif self.get_data_from == 'lote':
            self.employee_ids = False

    @api.model
    def create(self, vals):
        new_id = super().create(vals)
        new_id.name = self.env['ir.sequence'].next_by_code(
            'export.bank.payments')
        return new_id

    def action_draft(self):
        self.write({
            'state': 'draft',
            'txt_file': False,
            'txt_name': False,
        })
        return True

    def action_done(self):
        """ Exportar el documento en texto plano. """
        try:
            if self.type_trans in ["payroll"]:
                txt_data = self.generate_txt()
                name_bank = self.bank_account_id.bank_id.name
                fiscal_code = f"{self.date_end.month:0>2}{self.date_end.year}"
                # if self.get_data_from in ["lote"]:
                #     for lote in self.lote_payroll_ids:
                #         domain = [('id', '=', lote.id)]
                #         search_lote = self.env['hr.payslip.run'].search(domain)
                #         search_lote.action_paid()
                if self.get_data_from in ["individual"]:
                    for empleado in self.employee_ids:
                        domain = [('id', '=', empleado.id)]
                        search_empleado = self.env['hr.payslip'].search(domain)
                        search_empleado.action_payslip_paid()
                self._write_attachment(
                    txt_data, f"NOMINA {name_bank.upper()}{fiscal_code}", False)
            return self.write({'state': 'done'})
        except Exception as e:
            extra = "Este error pude ser causado por la falta de datos importantes en el registro de los empleados.\n\tRevise: número de cuenta bancaria, correo, cédula, etc."
            raise ValidationError(
                f'Error al escribir el archivo:\n\t {str(e)}\n\n{extra}')

    def _write_attachment(self, root, prefix, use_date=True):
        """ Encrypt txt, save it to the db and view it on the client as an
        attachment
        @param root: location to save document
        """
        try:
            date = time.strftime('%d%m%y') if use_date else ''
            txt_name = f'{prefix}{date}.txt'
            txt_file = root.encode('utf-8')
            txt_file = base64.encodebytes(txt_file)
            if not txt_file:
                raise ValidationError('No se pudo leer el archivo de origen.')
            self.write({'txt_name': txt_name, 'txt_file': txt_file})
            return txt_file, txt_name
        except Exception as e:
            raise ValidationError(
                f'Error al escribir el archivo:\n\t {str(e)}')

    # Obtener recibos de salario
    def _normalize_str(self, s: str) -> str:
        s = s.replace('ñ', 'n')
        s = re.sub(r'[.,"\'-?:!;]', '', s)  # Elimina signos de puntuacion
        s = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+",
                   r"\1", normalize("NFD", s), 0, re.I)  # Elimina signos diacriticos
        return s

    def generate_txt(self):
        if self.get_data_from in ["lote"]:
            payslips_in_lote = self.lote_payroll_domain.slip_ids
            payslips = self.employee_for_lote(payslips_in_lote)
            if len(payslips) <= 0:
                raise ValidationError(
                    'No existen recibos de pago válidos en el lote seleccionado.\n\tVálida el banco, el tipo de operación a realizar  o si el saldo a pagar del empleado es positivo o mayor que cero.')
        else:
            payslips = self.employee_ids

        bank_acron = self.bank_account_id.acc_number[:4]
        # Generador de txt nomina Venezuela
        if "0102" in bank_acron:
            return self._generate_txt_BDV(payslips)
        # Generador de txt nomina Mercantil
        elif "0105" in bank_acron:
            return self._generate_txt_mercantil(payslips)
        # Generador de txt nomina Provincial
        elif "0108" in bank_acron:
            return self._generate_txt_provincial(payslips)
        # Generador de txt nomina Banesco
        elif "0134" in bank_acron:
            return self._generate_txt_banesco(payslips)
        # Generador de txt nomina Bancamiga
        elif "0172" in bank_acron:
            return self._generate_txt_bancamiga(payslips)
        # Generador de txt nomina BNC
        elif "0191" in bank_acron:
            return self._generate_txt_BNC(payslips)
        # Generador de txt nomina Banplus
        elif "0174" in bank_acron:
            return self._generate_txt_banplus(payslips)

    def _generate_txt_banesco(self, payslips):
        company = self.env.company
        fecha_format = datetime.now().strftime("%d%m%Y%H%M%S")
        name_bank = self.bank_account_id.bank_id.name.upper()
        bank_acc = self.bank_account_id.sanitized_acc_number
        total_neto = sum(payslips.mapped("net_wage"))
        total = f"{total_neto:.2f}".replace(".", ",")

        if len(total) < 15:
            total = f"{(15 - len(total)) * '0'}{total}"

        date_with_id = f"{fecha_format[:8]}{str(self.id)}"

        if len(str(self.id)) < 9:
            add_zeros = (9 - len(str(self.id))) * ("0")
            id_consecutivo = f"02{add_zeros}{str(self.id)}"

        if len(date_with_id) > 9:
            tab = (29 - len(date_with_id)) * (" ")
        else:
            tab = 20 * (" ")

        if len(company.vat) == 10:
            tab2 = 7 * (" ")
        else:
            tab2 = (17 - len(company.vat)) * (" ")

        tab3 = (35 - len(company.name[:34])) * (" ")
        tab4 = (11 - len(name_bank[:11])) * (" ")

        file_txt = f"HDRBANESCO{8*' '}ED  95BPAYMULP\n"
        file_txt += f"01SCV{32*' '}9  {date_with_id}{tab}{fecha_format}\n"
        file_txt += f"{id_consecutivo}{20*' '}{company.vat}{tab2}{company.name}"
        file_txt += f"{tab3}{total} VES {bank_acc}{14*' '}"
        file_txt += f"{name_bank}{tab4}{fecha_format[:8][::-1]}\n"

        for employee in payslips:
            consecutivo_nomina = str(employee.id)
            employee_name = employee.employee_id.name
            bank_code = employee.employee_id.bank_id.bic
            bank_acc = employee.employee_id.bank_account_number
            identification = employee.employee_id.identification_id.replace(
                "-", "")
            neto_pagar = f"{employee.net_wage:.2f}".translate(
                str.maketrans("", "", ",."))

            if len(consecutivo_nomina) < 3:
                add_zeros = (3 - len(consecutivo_nomina)) * ("0")
                init_line = f"03{fecha_format[:8]}{add_zeros}{consecutivo_nomina}"
            elif len(consecutivo_nomina) >= 3:
                init_line = f"03{fecha_format[:8]}{consecutivo_nomina[:3]}"

            add_zero = (15 - len(neto_pagar)) * ("0")
            neto_pagar = f"{add_zero}{neto_pagar}"

            ajuste_espacio = (17 - len(identification[1:])) * (" ")

            file_txt += f"{init_line}{20*' '}{neto_pagar}VES{bank_acc}{10*' '}{bank_code}"
            file_txt += f"{10*' '}{identification[1:]}{ajuste_espacio}{employee_name}\n"

        return file_txt

    def _generate_txt_BDV(self, payslips):
        company = self.env.company
        afiliation_bank = self.bank_account_id.nro_afiliation_bank
        date_now = datetime.now()
        date_format_one = date_now.strftime("%d%m%Y")
        date_format_two = date_now.strftime("%d/%m/%Y")

        total_neto = sum(payslips.mapped("net_wage"))
        total = f"{total_neto:.2f}".replace(".", ",")

        if len(total) < 18:
            total = f"{(18 - len(total)) * '0'}{total}"

        file_txt = f"HEADER  {date_format_one}{afiliation_bank}"
        file_txt += f"{company.vat}{date_format_two}{date_format_two}\n"

        cant_credit, cant_deb = [0, 0]
        for employee in payslips:
            # *** Preparacion de campos ***
            consecutivo_nomina = str(employee.id)
            nro_bank = self.bank_account_id.acc_number.translate(
                str.maketrans("", "", "-."))
            employee_name = employee.employee_id.name
            identification = employee.employee_id.identification_id.replace(
                "-", "")
            neto_pagar = f"{employee.net_wage:.2f}".replace(".", ",")

            if len(consecutivo_nomina) < 8:
                add_zeros = (8 - len(consecutivo_nomina)) * ("0")
                consecutivo_nomina = add_zeros + consecutivo_nomina
            elif len(consecutivo_nomina) > 8:
                consecutivo_nomina = consecutivo_nomina[:7]

            if len(company.name) > 35:
                company.name = company.name[:34]

            tab1 = (35 - len(company.name)) * (" ")

            add_zero = (18 - len(neto_pagar)) * ("0")

            neto_pagar = f"{add_zero}{neto_pagar}"

            company_name = company.name[:30] \
                if len(employee_name) > 31 else company.name

            tab2 = (31 - len(employee_name)) * (" ")

            file_txt += f"DEBITO  {consecutivo_nomina}{company.vat}{company_name}"
            file_txt += f"{tab1}{date_format_two}00{nro_bank}{neto_pagar}VEB40\n"
            file_txt += f"CREDITO {consecutivo_nomina}{identification[1:]}{employee_name}"
            file_txt += f"{tab2}00{nro_bank}{neto_pagar}10BSCHVECA\n"

            cant_deb += 1
            cant_credit += 1

        # Pie de pagina
        if len(str(cant_credit)) > 5:
            cant_credit = int(str(cant_credit)[:4])
        add_zero = (5 - len(str(cant_credit))) * ("0")

        if len(str(cant_deb)) > 5:
            cant_deb = int(str(cant_deb)[:4])
        add_zero_deb = (5 - len(str(cant_deb))) * ("0")

        file_txt += f"TOTAL   {add_zero}{cant_credit}{add_zero_deb}{cant_deb}{total}"

        return file_txt

    def _generate_txt_BNC(self, payslips):
        company = self.env.company
        bank_acc = self.bank_account_id.sanitized_acc_number
        total_neto = sum(payslips.mapped("net_wage"))

        file_txt = f'NC0{bank_acc:<20}{total_neto:0>13}{company.vat[0]:<1}{company.vat[2:]:0>9}'

        for employee in payslips:
            # *** Preparacion de campos ***
            bank_acc = employee.employee_id.bank_account_number
            neto_pagar = f"{employee.net_wage:.2f}".translate(
                str.maketrans("", "", ",."))
            identification = employee.employee_id.identification_id.replace(
                "-", "")

            file_txt += f'ND0{bank_acc:<20}{neto_pagar:0>13}{identification:0>9}\n'

        return file_txt

    def _generate_txt_mercantil(self, payslips):
        company = self.env.company
        neto = str(round(sum(payslips.mapped("net_wage")), 2))
        if neto[-2] == '.':
            neto = neto + '0'
        neto = neto.translate(str.maketrans("", "", ",."))
        valid_date = self.valid_date.strftime('%Y%m%d')

        tipo_registro = 1
        identificacion_banco = f"BAMRVECA{4*' '}"  # Valor fijo = BANRVECA
        # Valor fijo = codigo especial que entrega el banco
        numero_lote = (15*'0')[:-(len(valid_date))] + valid_date
        tipo_producto = "NOMIN"  # Valor fijo = NOMIN
        tipo_pago = "0000000222"  # Valor fijo = 0000000222
        # Valor fijo => J = Jurid, G = Gobie, V = Vene, E = Extr, P = passpo
        tipo_identificacion = company.doc_type.upper()
        # Valor fijo = cedula o rif
        numero_identifi = (15*'0')[:-(len(company.vat))] + company.vat
        num_registros = str(len(payslips))
        registros = (8*'0')[:-(len(num_registros))] + num_registros
        total_monto = (17*'0')[:-(len(neto))] + neto
        fecha_realizar_pago = str(self.valid_date).replace(
            "-", "")  # <= discutir con enith
        cuenta_cliente = self.bank_account_id.sanitized_acc_number
        area_Reservada = f"{7*'0'}"
        numero_serial = f"{8*'0'}"
        codigo_respuesta = f"{4*'0'}"
        fecha_proceso = f"{8*'0'}"
        ceros = f"{261*'0'}"

        file_head = f"{tipo_registro}{identificacion_banco}{numero_lote}{tipo_producto}"
        file_head += f"{tipo_pago}{tipo_identificacion}{numero_identifi}{registros}"
        file_head += f"{total_monto}{fecha_realizar_pago}{cuenta_cliente}{area_Reservada}"
        file_head += f"{numero_serial}{codigo_respuesta}{fecha_proceso}{ceros}\n"
        file_body = ""

        for employee in payslips:
            emple_name = employee.employee_id.name
            emple_name = self._normalize_str(emple_name.lower())
            emple_id = employee.employee_id.identification_id.replace("-", "")

            emple_email_split = employee.employee_id.work_email.split('@')
            emple_email_split_normalize = self._normalize_str(
                emple_email_split[0])
            emple_email_normalize_list = [
                emple_email_split_normalize] + emple_email_split[1:]
            emple_email = '@'.join(emple_email_normalize_list)
            neto_pagar = str(round(employee.net_wage, 2))
            if neto_pagar[-2] == '.':
                neto_pagar = neto_pagar + '0'
            neto_pagar = neto_pagar.translate(
                str.maketrans("", "", ",."))

            tipo_proceso = self._normalize_str(employee.struct_id.display_name)

            tipo_registro = "2"  # Valor fijo = 2
            tipo_id = emple_id[0]  # Valor fijo => V, E  P
            numero_identifi = (
                15*'0')[:-(len(emple_id[1:]))] + emple_id[1:]  # Cedula
            # forma pago: 1 = abono en cuenta, 3 = A otros bancos
            forma_pago = "1" if self.operation_type == 'same' else "3"
            area_reservada_num_uno = f"{12*'0'}"
            area_reservada_alfa = f"{30*' '}"
            cuenta_cliente = employee.employee_id.bank_account_number
            monto = (17*'0')[:-(len(neto_pagar))] + neto_pagar
            indentificacion_cliente = f"{16*' '}"
            # Valor fijo de tipo de pago = 0000000222
            tipo_pago = "0000000222"
            area_reservada_num_dos = f"{3*'0'}"
            nombre_nom = emple_name + (60*' ')[len(emple_name):]
            area_reservada_num_tres = f"{15*'0'}"
            email_beneficiario = emple_email + (50*' ')[len(emple_email):]
            codigo_respuesta = f"{4*'0'}"
            mensaje_respuesta = f"{30*' '}"
            concepto_pago = tipo_proceso.upper() + (80*' ')[len(tipo_proceso):]
            ceros = f"{35*'0'}"

            file_body += f"{tipo_registro}{tipo_id}{numero_identifi}{forma_pago}"
            file_body += f"{area_reservada_num_uno}{area_reservada_alfa}{cuenta_cliente}"
            file_body += f"{monto}{indentificacion_cliente}{tipo_pago}{area_reservada_num_dos}"
            file_body += f"{nombre_nom}{area_reservada_num_tres}{email_beneficiario}"
            file_body += f"{codigo_respuesta}{mensaje_respuesta}{concepto_pago}{ceros}\n"
        return file_head + file_body

    def _generate_txt_provincial(self, payslips):
        file_txt = ""
        for employee in payslips:
            cuenta = employee.employee_id.bank_account_number
            emple_id = employee.employee_id.identification_id.replace(
                "-", "")
            tipo_id = emple_id[0]  # Valor fijo => V, E  P
            numero_identifi = (
                10*'0')[:-(len(emple_id[1:]))] + emple_id[1:]  # Cedula
            neto_pagar = str(round(employee.net_wage, 2))
            if neto_pagar[-2] == '.':
                neto_pagar = neto_pagar + '0'
            neto_pagar = neto_pagar.translate( str.maketrans("", "", ",."))
            monto = (15*'0')[:-(len(neto_pagar))] + neto_pagar
            emple_name = self._normalize_str(employee.employee_id.name)

            file_txt += f"{cuenta} {tipo_id}{numero_identifi} {monto} {emple_name}\n"
        return file_txt

    def _generate_txt_bancamiga(self, payslips):
        file_txt = "Tipo Documento;Nro Documento;Cuenta;Nombre Beneficiario;Monto\n"
        for employee in payslips:
            emple_id = employee.employee_id.identification_id.replace(
                "-", "")
            tipo_id = emple_id[0]  # Valor fijo => V, E  P
            numero_identifi = emple_id[1:]  # Cedula
            cuenta = employee.employee_id.bank_account_number
            emple_name = employee.employee_id.name
            monto = '{:,.2f}'.format(employee.net_wage).replace(
                ',', '@').replace('.', ',').replace('@', '.')
            file_txt += f"{tipo_id};{numero_identifi};{cuenta};{emple_name};{monto}\n"
        return file_txt


    def _generate_txt_banplus(self, payslips):
        company = self.env.company

        #header
        txt_rif = f"{company.doc_type.upper()}{company.vat}"
        txt_acc = self.bank_account_id.acc_number
        txt_qty = str( len(payslips.ids) )

        neto = str(round(sum(payslips.mapped("net_wage")), 2))
        if neto[-2] == '.':
            neto = neto + '0'
        txt_amount = neto.replace(".", ",")

        txt_date = self.valid_date.strftime("%d/%m/%Y")

        file_txt = f"{txt_rif};{txt_acc};{txt_qty};{txt_amount};{txt_date}\n"

        #body
        for slip in payslips:
            emple_id = slip.employee_id.identification_id.replace("-", "")
            txt_ven = ""
            if emple_id[0].lower() == "v": txt_ven = "01"
            elif emple_id[0].lower() == "p": txt_ven = "02"
            elif emple_id[0].lower() == "e": txt_ven = "08"
            txt_id =  emple_id.translate(str.maketrans("", "", "vepVEP"))

            txt_name = self._normalize_str(slip.employee_id.name).upper()
            txt_acc = slip.employee_id.bank_account_number

            neto = str(round(slip.net_wage, 2))
            if neto[-2] == '.':
                neto = neto + '0'
            txt_amount = neto.replace(".", ",")

            file_txt += f"{txt_ven};{txt_id};{txt_name};{txt_acc};{txt_amount}\n"

        return file_txt
