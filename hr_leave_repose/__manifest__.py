# -*- coding: utf-8 -*-
{
    'name': "Repose Leaves",
    'installable' : True,
    'author': "IT Sales",
    'category': 'l10n_ve_payroll',
    'website': "http://www.itsalescorp.com",
    'version': '1.0.3',
    'depends':  [
                    'l10n_ve_payroll',
                    'hr_payslip_report_customization',
                    'hr_payroll_customization',
                ],
    'license': 'Other proprietary',
    'data': [
                'views/hr_leaves_views.xml',
                # 'views/hr_payslip_views.xml',
            ],
}
