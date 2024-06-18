# -*- coding: utf-8 -*-
{
    'name': "Salary Rules Customization",
    'installable' : True,
    'author': "IT Sales",
    'website': "http://www.itsalescorp.com",
    'version': '1.0.3',
    'category': 'l10n_ve_payroll',
    'depends':  [
                    'base',
                    'hr_leave_repose',
                    'hr_payslip_report_customization',
                ],
    'license': 'Other proprietary',
    'data': [
                'views/hr_salary_rules_views.xml',
                'views/hr_payslip_views.xml',
                'report/hr_payslip_report.xml',
            ],
}