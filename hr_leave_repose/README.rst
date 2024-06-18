hr_leave_repose
===============

El propósito de este módulo es extender y modificar el comportamiento del modelo hr.contract del sistema Odoo. 
El módulo se encarga de gestionar los contratos de empleados y realizar cálculos relacionados con las horas de trabajo y las ausencias.

Características:
~~~~~~~~~~~~~~~~

- Agregar el cálculo de las horas de trabajo. Este cálculo tiene en cuenta las ausencias registradas para el empleado en el período especificado.
- Implementa métodos para gestionar las ausencias de los empleados. Estos agregan las ausencias al cálculo de horas de trabajo y recalculan las asistencias y los tiempos libres teniendo en cuenta las ausencias registradas.
- Realiza el cálculo de los días de ausencia teniendo en cuenta diferentes factores, como la duración de la ausencia, los días pagados y los días de fin de semana.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_payslip_report_customization
- hr_payroll_customization

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
