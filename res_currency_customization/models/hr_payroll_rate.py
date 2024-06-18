from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PayrollRate(models.Model):
    _name = 'hr.payroll.rate'
    _description = "rate BCV used only to payroll"

    def _get_today(self):
        return fields.Date.from_string(fields.Date.today())

    name = fields.Date(string='Date', required=True, index=True, default=_get_today)
    rate = fields.Float(string="Average between active and passive", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_name_per_day', 'unique (name,company_id)', 'Only one rate per day allowed!'),
        ('currency_rate_check', 'CHECK (rate>0)', 'The rate must be strictly positive.'),
    ]

    def _get_lastest_rate(self):
        today = self._get_today()
        query = """
            SELECT
                rate.id
            FROM hr_payroll_rate AS rate
            WHERE
                rate.name <= '{}'
            ORDER BY
                rate.name DESC LIMIT 1;

        """.format(today)

        self._cr.execute(query)
        payroll_rate = self.env.cr.fetchone()
        
        res = self.env['hr.payroll.rate']
        if payroll_rate:
            res = res.search([('id', '=', payroll_rate[0])])
        
        return res


    def unlink(self):
        today = self._get_today()
        for record in self:
            if record.create_date.date() != today:
                raise UserError(_('You cannot delete a non-current date'))

        return super(PayrollRate, self).unlink()