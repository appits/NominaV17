from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    trust_config = fields.Selection(related="company_id.trust_config", string="Trust calculation", readonly=False,
    help="Quaterly: calculates the trust contribution each quarter of the year.\nStarting date: calculates each time the worker's seniority completes a quarter.\nNothing: don't calculate trust contribution.")

    @api.constrains('trust_config')
    def _check_fields(self):
        action = self.env.ref("hr_contract_customization.ir_cron_trust_contribution")
        action.active = True if self.trust_config == "tri" else False


class Company(models.Model):
    _inherit = 'res.company'

    trust_config = fields.Selection([('no', 'Nothing'), ('ing', 'Starting date'), ('tri', 'Quaterly')], default="no", required=True)
