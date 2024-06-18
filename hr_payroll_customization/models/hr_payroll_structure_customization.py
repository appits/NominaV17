from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date

class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _inherit = ['hr.payroll.structure', 'mail.thread.cc', 'mail.activity.mixin']

    
    department_ids = fields.Many2many(
        string='departments',
        comodel_name='hr.department',
    )

        # Tracking fields
    name = fields.Char(tracking=True)
    active = fields.Boolean(tracking=True)
    type_id = fields.Many2one(tracking=True)
    country_id = fields.Many2one(tracking=True)
    note = fields.Text(tracking=True)
    report_id = fields.Many2one(tracking=True)
    payslip_name = fields.Char(tracking=True)
    regular_pay = fields.Boolean(tracking=True)
    unpaid_work_entry_type_ids = fields.Many2many(tracking=True)
    use_worked_day_lines = fields.Boolean(tracking=True)
    schedule_pay = fields.Selection(tracking=True)
    input_line_type_ids = fields.Many2many(tracking=True)
    unpaid_work_entry_type_ids = fields.Many2many(tracking=True)

    @api.model_create_multi
    def create(self, list_value):
        res = super(HrPayrollStructure, self).create(list_value)
        message = " "
        
        if res.unpaid_work_entry_type_ids:
            message += _("""<div><strong>Entradas de trabajo</strong><br/>""")
            message += _("""Nuevas entradas de trabajo <ul>""")
            for structure in res.unpaid_work_entry_type_ids:
                message += """<li>""" + structure.name + " " + structure.code 
            message += "<ul/></div>"
            res.message_post(body=message)

        if res.input_line_type_ids:
            message += _("""<div><strong>Otras Entradas</strong><br/>""")
            message += _("""Otras Entradas Nuevas <ul>""")
            for structure in res.input_line_type_ids:
                message += """<li>""" + structure.name + " " + structure.code 
            message += "<ul/></div>"
            res.message_post(body=message)

        return res

    def write(self, vals):
        message = " "

        # Salary rules
        if vals.get('rule_ids'):

            
            lines = [line for line in vals.get(
                'rule_ids') if line[0] in [0, 1, 2]]

            create_rules = [line for line in lines if line[0] == 0]
            edit_rules = [line for line in lines if line[0] == 1]
            delete_rules = [line for line in lines if line[0] == 2]

            # Creacion
            if create_rules:
                message += """<div><strong>Nuevo Reglas Salariales</strong><br/>"""
                for line in create_rules:
                    new_name = line[2].get('name') if line[2].get('name') else ' '
                    new_code = line[2].get('code') if line[2].get('code') else ' '
                    new_category = str(self.env['hr.salary.rule.category'].search(
                        [('id', '=', line[2].get('category_id'))]).name)
                    message += "<li>" \
                        + ' Nombre: ' + new_name \
                        + "<br/>" \
                        + ' Código: ' + new_code \
                        + "<br/>" \
                        + ' Categoría: ' + new_category \
                        + "<br/>" \
                        + "</li>"

            # Modificacion
            if edit_rules:
                message += """<div><strong>Reglas Salariales modificado</strong><br/>"""
                for line in edit_rules:
                    old_name = self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).name if self.env['hr.salary.rule'].search([('id', '=', line[1])]).name else ' '
                    new_name = line[2].get('name') if line[2].get('name') else ' '
                    old_code = str(self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).code)
                    new_code = line[2].get('code') if line[2].get('code') else ' '
                    new_category = str(self.env['hr.salary.rule.category'].search(
                        [('id', '=', line[2].get('category_id'))]).name)
                    old_category = self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).category_id.name if self.env['hr.salary.rule'].search([('id', '=', line[1])]).category_id.name else ' '
                    message += "<li>" \
                        + ' Nombre : ' + old_name + " <span>&#8594;<span/> " + new_name \
                        + "<br/>" \
                        + ' Código : ' + old_code + " <span>&#8594;<span/> " + new_code \
                        + "<br/>" \
                        + ' Categoría : ' + old_category + " <span>&#8594;<span/> " + new_category \
                        + "<br/>" \
                        + "</li>"

            # Eliminacion
            if delete_rules:
                message += """<div><strong>Reglas Salariales eliminado</strong><br/>"""
                for line in delete_rules:
                    old_name = self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).name if self.env['hr.salary.rule'].search([('id', '=', line[1])]).name else ' '
                    old_code = str(self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).code)
                    old_category = self.env['hr.salary.rule'].search(
                        [('id', '=', line[1])]).category_id.name if self.env['hr.salary.rule'].search([('id', '=', line[1])]).category_id.name else ' '
                    message += "<li>" \
                        + ' Nombre : ' + old_name \
                        + "<br/>" \
                        + ' Código : ' + old_code \
                        + "<br/>" \
                        + ' Categoría : ' + old_category \
                        + "<br/>" \
                        + "</li>"

            message += "<ul/></div>"

        old_other_entry = self.input_line_type_ids
        old_entry = self.unpaid_work_entry_type_ids

        res = super(HrPayrollStructure, self).write(vals)

        # Types of unpaid labor input
        if vals.get('unpaid_work_entry_type_ids'):
            new_entrys = self.unpaid_work_entry_type_ids
            remove_entrys = [entry for entry in old_entry if entry not in new_entrys]
            add_new_entrys = [entry for entry in new_entrys if entry not in old_entry]
            
            if add_new_entrys:
                message += """<div><strong>Nuevas entradas</strong><br/>"""
                for add in add_new_entrys:
                    message += """<li>""" + ' Nombre : ' + add.name \
                        + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' - ' + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' Código : ' + add.code
                message += "<ul/></div>"
            if remove_entrys:
                message += """<div><strong>Entradas eliminadas</strong><br/>"""
                for add in remove_entrys:
                    message += """<li>""" + ' Nombre : ' + add.name \
                        + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' - ' + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' Código : ' + add.code
                message += """<ul/></div>"""

        # Other entries
        if vals.get('input_line_type_ids'):            
            new_other_entrys = self.input_line_type_ids
            remove_other_entrys = [entry for entry in old_other_entry if entry not in new_other_entrys]
            add_new_other_entrys = [entry for entry in new_other_entrys if entry not in old_other_entry]
            
            if add_new_other_entrys:
                message += """<div><strong>Otras entradas</strong><br/>"""
                for add in add_new_other_entrys:
                    message += """<li>""" + ' Nombre : ' + add.name \
                        + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' - ' + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' Código : ' + add.code
                message += "<ul/></div>"
            if remove_other_entrys:
                message += """<div><strong>Otras entradas eliminadas</strong><br/>"""
                for add in remove_other_entrys:
                    message += """<li>""" + ' Nombre : ' + add.name \
                        + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' - ' + '&nbsp;&nbsp;&nbsp;&nbsp;' + ' Código : ' + add.code
                message += """<ul/></div>"""

        if message != " ":
            self.message_post(body=message)

        return res