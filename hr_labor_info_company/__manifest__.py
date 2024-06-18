# -*- coding: utf-8 -*-
{
    'name': "informacion laboral company",
    'author': "IT Sales",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ve_payroll'],

    'license': 'Other proprietary',

    # always loaded
    'data': [
        'views/labor_company_view.xml'
    ]

}
