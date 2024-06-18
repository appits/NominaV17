hr_payroll_settings_customization
=================================

El propósito de este módulo es ampliar la funcionalidad del módulo de configuración de la empresa en Odoo para incluir campos relacionados con la nómina y permitir la configuración de parámetros globales específicos de la nómina.

Características:
~~~~~~~~~~~~~~~~

- Agrega campos adicionales que permiten modificar parámetros como el salario mínimo, los días de vacaciones, los días de bonificación, los días de beneficio y el valor del ticket de alimentación.
- Los campos relacionados con valores monetarios en el módulo (como "minimum_salary" y "salary_basket_ticket") están vinculados a modelos de moneda para permitir la selección de la moneda adecuada.

Instrucciones de uso:
~~~~~~~~~~~~~~~~~~~~~

- Asegúrate de que el módulo esté instalado y activado en tu instancia de Odoo.
- Recuerta establecer los valores deseados para los campos Salario mínimo y Vacaciones antes de utilizar el módulo. 
- Dichos valores serán utilizados en otros módulos o informes relacionados con la nómina.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr
- hr_payroll

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
