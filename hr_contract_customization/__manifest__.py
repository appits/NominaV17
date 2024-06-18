# -*- coding: utf-8 -*-
{
    'name': "hr_contract_customization",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll', 'hr_contract','hr_holidays',  'hr_employee_customization'],

    # always loaded
    'data': [
        'data/social_benefits.xml',
        'views/hr_contract_customization.xml',
        'views/hr_contract_history.xml',
        'views/res_config_view.xml',
    ],
    
    'license': 'Other proprietary',
}
