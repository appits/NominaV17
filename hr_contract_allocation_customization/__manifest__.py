# -*- coding: utf-8 -*-
{
    'name': "hr_contract_allocation_customization",
    'version': '1.0.3',
    'license': 'Other proprietary',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr_contract_customization', 'product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_contract_allocation.xml',
        'views/hr_contract_allocation_lines.xml',
    ],

    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

}
