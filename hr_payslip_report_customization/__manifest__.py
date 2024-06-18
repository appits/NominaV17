# -*- coding: utf-8 -*-
{
    'name': "hr_payslip_report_customization",
    'author': "IT Sales",
    'website': "https://www.itsalescorp.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'l10n_ve_payroll',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': [
                'l10n_ve_payroll',
                'hr_payroll', 
                'uom','hr_holidays',
                'hr_work_entry_holidays',
                'hr_work_entry_contract',
                'hr_payroll_customization' 
                ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/report_names.xml',
        'report/payslip_report_customization.xml',
        'views/hr_payroll_structure_customization.xml',
        'views/report_name.xml',
        'views/uom_category_custom.xml',
        'views/hr_payslip_other_input_custom.xml',
        'views/hr_leave_views.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_payslip_customization_view.xml',
        'views/hr_payslip_run_customization_view.xml'
    ],

    'license': 'Other proprietary',
}
