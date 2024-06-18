# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CurrencyRate(models.Model):
	_inherit = "res.currency.rate"

	is_payroll_rate = fields.Boolean(string="Payroll rate")


class Currency(models.Model):
	_inherit = "res.currency"

	def _convert_payroll(self, from_amount, to_currency, company, date, round=True):
		"""Returns the converted amount of ``from_amount``` from the currency
			``self`` to the currency ``to_currency`` for the given ``date`` and
			company.

			:param company: The company from which we retrieve the convertion rate
			:param date: The nearest date from which we retriev the conversion rate.
			:param round: Round the result or not
		"""
		self, to_currency = self or to_currency, to_currency or self
		assert self, "convert amount from unknown currency"
		assert to_currency, "convert amount to unknown currency"
		assert company, "convert amount from unknown company"
		assert date, "convert amount from unknown date"
		# apply conversion rate
		if self == to_currency:
			to_amount = from_amount
		else:
			to_amount = from_amount * self._get_conversion_rate_payroll(self, to_currency, company, date)
		# apply rounding
		return to_currency.round(to_amount) if round else to_amount

	@api.model
	def _get_conversion_rate_payroll(self, from_currency, to_currency, company, date):
		currency_rates = (from_currency + to_currency)._get_rates_payroll(company, date)
		res = currency_rates.get(to_currency.id) / currency_rates.get(from_currency.id)
		return res

	def _get_rates_payroll(self, company, date):
		if not self.ids:
			return {}
		self.env['res.currency.rate'].flush(['rate', 'currency_id', 'company_id', 'name'])
		query = """SELECT c.id,
						COALESCE((SELECT r.rate FROM res_currency_rate r
								WHERE r.currency_id = c.id AND r.name <= %s
									AND (r.company_id IS NULL OR r.company_id = %s)
									AND r.is_payroll_rate = True
							ORDER BY r.company_id, r.name DESC
								LIMIT 1), 1.0) AS rate
				FROM res_currency c
				WHERE c.id IN %s"""
		resul = self.env.cr.mogrify(query, (date, company.id, tuple(self.ids))).decode(self.env.cr.connection.encoding)
		self._cr.execute(resul)
		currency_rates = dict(self._cr.fetchall())
		return currency_rates


