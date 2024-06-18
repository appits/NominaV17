conect_payroll_account_move
===========================

Este módulo personalizado amplía la funcionalidad de los módulos de nómina y asientos contables de Odoo. 
Su propósito principal es automatizar la creación de asientos contables a partir de las nóminas generadas en el sistema.

Características:
~~~~~~~~~~~~~~~

- Permite crear asientos contables automáticamente a partir de las nóminas generadas en el sistema.
- Asocia los asientos contables creados con las nóminas correspondientes.
- Gestiona la generación de asientos de nómina para múltiples estructuras salariales y periodos de pago.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_payroll_account
- res_currency_customization
- hr_payroll_customization

-----------------------------------------------------------

[ Version 15.1.1.0 ] --- 2024/04/12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Changlog
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**15.1.1.0**

- Nuevos campos en las reglas salariales referentes a las cuentas de débito y crédito para costos directos e indirectos.
- Cambio de nombre de los campos 'Cuenta de débito' y 'Cuenta de crédito' en las reglas salariales, ahora se llaman 'Cuenta de débito gasto' y 'Cuenta de crédito gasto'.
- Nuevo campo en el formulario del empleado, 'Ubicación contable', sirve para escoger cuál par de cuentas se usará de las reglas salariales al momento de generar el asiento contable.
- Nuevo comportamiento al generar asiento contable, ahora se crea automáticamente seleccionando las cuentas respectivas previamente configuradas en el empleado.
