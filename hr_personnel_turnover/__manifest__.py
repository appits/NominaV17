# -*- coding: utf-8 -*-
{
    'name': "Personnel Turnover",
    'installable' : True,
    'author': "IT Sales",
    'website': "http://www.itsalescorp.com",
    'version': '1.0.3',
    'category': 'l10n_ve_payroll',
    'depends':  [
                    'l10n_ve_payroll',
                    'hr_skills',
                    'hr_contract_customization',
                    'hr_employee_customization',
                ],
    'license': 'Other proprietary',
    'data': [
                "security/ir.model.access.csv",
                "data/mail_personnel_turnover.xml",
                "data/hr_resume.xml",
                "views/hr_personnel_turnover_views.xml",
                "views/hr_resume_views.xml",
                "wizard/hr_personnel_turnover_wizard_view.xml",
            ],

    'assets': {
        'web.assets_backend': [
            '/hr_personnel_turnover/static/src/js/personnel.js',
            '/hr_personnel_turnover/static/src/js/personnel_dialog.js',
        ],
    }
}
