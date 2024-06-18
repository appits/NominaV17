# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrWorkEntryType(models.Model):
    _name = 'hr.work.entry.type'
    _inherit = ['hr.work.entry.type', 'mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char(tracking=True)
    code = fields.Char(tracking=True)
    color = fields.Integer(tracking=True)
    sequence = fields.Integer(tracking=True)

    is_unforeseen = fields.Boolean(tracking=True)
    round_days = fields.Selection(tracking=True)
    round_days_type = fields.Selection(tracking=True)
    leave_type_ids = fields.One2many(tracking=True)
    is_leave = fields.Boolean(tracking=True)
    unpaid_structure_ids = fields.Many2many(tracking=True)

    @api.model_create_multi
    def create(self, list_value):
        res = super(HrWorkEntryType, self).create(list_value)
        message = " "

        if list_value[0]:
            message += _("""<div><strong>Nuevo tipo de entradas de trabajo </strong><br/>""")
            message += _("""<ul>""")

            round_days = {'NO': 'Sin redondeo',
                        'HALF': 'Medio día', 'FULL': 'Día'}
            round_days_type = {'HALF-UP': 'Lo más cercano',
                            'UP': 'Hasta', 'DOWN': 'Abajo'}
            color = {0: 'No color', 1: 'Rojo', 2: 'Naranja', 3: 'Amarillo', 4: 'Azul claro', 5: 'Morado oscuro',
                    6: 'Rosa salmón', 7: 'Azul medio', 8: 'Azul oscuro', 9: 'Fushia', 10: 'Verde', 11: 'Morado'}

            message += "<li>" \
                + ' Nombre : ' + list_value[0].get('name', False) \
                + "<br/>" \
                + ' Código : ' + list_value[0].get('code', False) \
                + "<br/>" \
                + ' Secuencia : ' + str(list_value[0].get('sequence', False)) \
                + "<br/>" \
                + ' Color : ' + color.get(list_value[0].get('color', False), False) \
                + "<br/>" \
                + ' Ausencias : ' + str(list_value[0].get('is_leave', False)) \
                + "<br/>" \
                + ' Ausencia imprevista : ' + str(list_value[0].get('is_unforeseen', False)) \
                + "<br/>" \
                + ' Redondeo : ' + round_days.get(list_value[0].get('round_days', False), False) \
                + "<br/>" \
                + ' Tipo de redondeo : ' + round_days_type.get(list_value[0].get('round_days_type', False), False) \
                + "<br/>" \
                + "</li>"
            message += "<ul/></div>"

            if res.leave_type_ids:
                message += _("""<div> Tipo de tiempo libre <ul>""")
                for leave_type in res.leave_type_ids:
                    message += """<li>""" + leave_type.name
                message += "<ul/></div>"

            if res.unpaid_structure_ids:
                message += _("""<div> Sin pagar en tipos de estructura <ul>""")
                for structure in res.unpaid_structure_ids:
                    message += """<li>""" + structure.name
                message += "<ul/></div>"

            res.message_post(body=message)

        return res

    def write(self, vals):
        message = " "

        old_leave_type_ids = self.leave_type_ids
        old_unpaid_structure_ids = self.unpaid_structure_ids
        old_color = self.color

        res = super(HrWorkEntryType, self).write(vals)

        if vals.get('leave_type_ids'):
            new_leave_type_ids = self.leave_type_ids
            remove_leave_type_ids = [
                entry for entry in old_leave_type_ids if entry not in new_leave_type_ids]
            add_new_leave_type_ids = [
                entry for entry in new_leave_type_ids if entry not in old_leave_type_ids]

            if add_new_leave_type_ids:
                message += """<div><strong>Nuevos Tipo de tiempo libre</strong><br/>"""
                for add in add_new_leave_type_ids:
                    message += """<li>""" + ' Nombre : ' + str(add.name)
                message += "<ul/></div>"
            if remove_leave_type_ids:
                message += """<div><strong>Tipo de tiempo libre eliminadas</strong><br/>"""
                for add in remove_leave_type_ids:
                    message += """<li>""" + ' Nombre : ' + str(add.name)
                message += """<ul/></div>"""

        if vals.get('unpaid_structure_ids'):
            new_unpaid_structure_ids = self.unpaid_structure_ids
            remove_unpaid_structure_ids = [
                entry for entry in old_unpaid_structure_ids if entry not in new_unpaid_structure_ids]
            add_new_unpaid_structure_ids = [
                entry for entry in new_unpaid_structure_ids if entry not in old_unpaid_structure_ids]

            if add_new_unpaid_structure_ids:
                message += """<div><strong>Nuevos Sin pagar en tipos de estructura</strong><br/>"""
                for add in add_new_unpaid_structure_ids:
                    message += """<li>""" + ' Nombre : ' + str(add.name)
                message += "<ul/></div>"
            if remove_unpaid_structure_ids:
                message += """<div><strong>Sin pagar en tipos de estructura eliminadas</strong><br/>"""
                for add in remove_unpaid_structure_ids:
                    message += """<li>""" + ' Nombre : ' + str(add.name)
                message += """<ul/></div>"""

        if vals.get('color'):
            color = {0: 'No color', 1: 'Rojo', 2: 'Naranja', 3: 'Amarillo', 4: 'Azul claro', 5: 'Morado oscuro',
                    6: 'Rosa salmón', 7: 'Azul medio', 8: 'Azul oscuro', 9: 'Fushia', 10: 'Verde', 11: 'Morado'}
            message += """<li>""" + ' Color : ' + \
                str(color.get(old_color, False)) + ' <span>&#8594;<span/> ' + \
                str(color.get(vals.get('color', False), False))
        if message != " ":
            self.message_post(body=message)

        return res
