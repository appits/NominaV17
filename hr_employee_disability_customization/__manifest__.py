# -*- coding: utf-8 -*-
{
    'name': "hr_employee_disability",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr_employee_customization'],

    # always loaded
    'data': [
        'data/employee_disability_data.xml',
        'security/ir.model.access.csv',
        'views/employee_disability_view.xml',
        'views/views.xml',
    ],
    
    'license': 'Other proprietary',
}
