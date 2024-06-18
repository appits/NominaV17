from odoo import models, fields, _

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_payslip_lines(self):
        res = super(HrPayslip, self)._get_payslip_lines()
        t_type = {
            'd': 'Días',
            'm': 'Meses',
            'y': 'Años',
            'h': 'Horas',
        }

        localdict = self.env.context.get('force_payslip_localdict', None)
        if localdict is None:
            localdict = self._get_localdict()
        rules_dict = localdict['rules'].dict

        blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

        for val in res:
            rule = self.struct_id.rule_ids.filtered(lambda x: x.id == val['salary_rule_id'])
            if rule:
                if rule.id in blacklisted_rule_ids:
                    continue
                localdict.update({
                    'result': None,
                    'result_qty': 1.0,
                    'result_rate': 100,
                    'result_name': False
                })

                time = rule._compute_duration(localdict)
                # time_type = _( dict(rule._fields['type_duration'].selection).get(rule.type_duration) )
                time_type = t_type[rule.type_duration]

                duration_display = str(time) + " " + time_type if time else "-"

                val.update({
                        'duration_display': duration_display,
                        'duration': time,
                    })
                
                rules_dict[rule.code] = rule
                
        return res


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    duration_display = fields.Char(string="Duration")
    duration = fields.Float()
