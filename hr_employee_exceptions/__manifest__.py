# -*- coding: utf-8 -*-
{
    'name': "Employee Exceptions",
    'installable' : True,
    'author': "IT Sales",
    'category': 'l10n_ve_payroll',
    'website': "http://www.itsalescorp.com",
    'version': '1.0.3',
    'depends':  [
                    'l10n_ve_payroll',
                    'hr_payroll_customization',
                    'hr_employee_customization',
                    'hr_contract_customization',
                ],
    'license': 'Other proprietary',
    'data': [
                'views/hr_contract_views.xml',
                'views/hr_payslip_employees_views.xml',                
            ],
}
