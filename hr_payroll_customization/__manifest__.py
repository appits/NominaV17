# -*- coding: utf-8 -*-
{
    'name': "hr_payroll_customization",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr_employee_customization', 'hr_contract_customization', 'hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/hr_payslip_customization_view.xml',
        'views/hr_payslip_run_customization_view.xml',
        'views/currency_payslip_line_views.xml',
        'views/hr_payroll_structure_customization.xml',
        'views/hr_salary_rule_customizacion.xml',
        'views/hr_work_entry_type.xml',
        'views/hr_payroll_structure_type_views.xml',
        'wizard/hr_work_entry_regeneration_wizard_views.xml',
    ],

    'license': 'Other proprietary',
}
