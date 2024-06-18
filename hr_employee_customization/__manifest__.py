# -*- coding: utf-8 -*-
{
    'name': "hr_employee_customization",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr', 'hr_payroll', 'res_currency_customization', 'hr_rule_category_customization', 'hr_payroll_settings_customization'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_info.xml',
        'views/hr_employee_salary_advance.xml',
        'views/hr_employee_add_discounsts.xml',
        'views/hr_employee_type_views.xml',
        'report/work_constancy_report.xml',
        'report/wizard_work_constancy_view.xml'
    ],

    'license': 'Other proprietary',
}
