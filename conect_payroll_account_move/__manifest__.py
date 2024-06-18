# -*- coding: utf-8 -*-
{
    'name': "Conect payroll account move",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',
    'depends': [
        'l10n_ve_payroll',
        'hr_payroll_account',
        'res_currency_customization',
        'hr_payroll_customization'
    ],
    'data': [
        'views/account_move_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_employee.xml',
    ],
    'license': 'Other proprietary',
}
