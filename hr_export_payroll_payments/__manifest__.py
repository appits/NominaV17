# -*- coding: utf-8 -*-
{
    'name': "hr_export_payroll_payments",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr', 'hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/export_bank_payments_views.xml',
        'views/export_payroll_banavih_view.xml',
        'views/export_payroll_food_view.xml',
        'views/export_payroll_trust_view.xml',
        'views/views.xml',
        'data/sequence_data.xml',
    ],
    'license': 'Other proprietary',
}
