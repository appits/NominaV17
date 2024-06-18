# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Additional Payroll Reports",
    'author': "IT Sales",
    "website": "https://www.itsalescorp.com",
    'category': 'l10n_ve_payroll',
    "version": '1.0.3',
    "depends": [
        'l10n_ve_payroll', 'hr_payroll', 'hr_payroll_customization', 'hr_contract_customization'
    ],
    "application": True,
    "data": [
        "security/ir.model.access.csv",
        "view/payroll_report_wizard.xml",
        "report/report_actions.xml",
        "report/base_template.xml",
        "report/payroll_report_detail_template.xml",
        "report/payroll_report_by_concepts_template.xml",
        "view/payroll_banavih_wizard.xml",
        "report/banavih_report.xml",
        "view/payroll_ISLR_wizard.xml",
        "report/ISLR_report.xml",
        "view/payroll_inces_wizard.xml",
        "report/inces_report.xml",
        'report/social_benefits_report_report.xml',
        'view/social_benefits_report_views.xml',
    ],

    "license": "Other proprietary",
    "auto_install": False,
    "installable": True,
}
