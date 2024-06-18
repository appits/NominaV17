hr_payslip_report_customization
===============================

Este módulo proporciona una serie de mejoras y funcionalidades adicionales relacionadas con la gestión de contratos, permisos y ausencias laborales, así como la generación de informes de nómina.

Características:
~~~~~~~~~~~~~~~~

- Ofrece un método para el cálculo de las horas de trabajo en función de las fechas de inicio y fin del contrato. 
- Proporciona un método que realiza ajustes a las fechas según reglas específicas.
- Se agregan campos booleanos llamados para indican si el tipo de permiso o entrada de trabajo está remunerado o no.
- Se agregan varios métodos y campos computados para calcular y almacenar información relacionada con las ausencias laborales. 
- métodos que calculan los días de fin de semana, días de vacaciones legales, días de vacaciones adicionales y días feriados laborables. 
- Determina si una ausencia es considerada vacaciones y se maneja la lista de feriados.
- Se agregan varios campos computados relacionados con las ausencias laborales en los informes de nómina. 
- Entre dichos campos se encuentran los días de ausencia, días de ausencia fuera del período de nómina, días de descanso, días de vacaciones legales, días de vacaciones adicionales y días feriados laborables. 
- También se incluye el cálculo del salario neto en formato de texto.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_payroll
- uom
- hr_holidays
- hr_work_entry_holidays
- hr_work_entry_contract

-----------------------------------------------------------

Changelog
~~~~~~~~~

[ Version 15.1.0.3 ] --- 2024/05/09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- Extensión del funcionamiento de asignaciones de anticipos y/o préstamos.

[ Version 15.1.0.2 ] --- 2024/04/25
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- Se añadió un botón adicional para indicar cuando se realiza el Pago de Cestatickets.
- Los recibos ahora muestran un mensaje especial cuando la acción "Pago de Cestatickets".
- Ahora se puede mostrar dicho mensaje en los recibos, tanto de forma individual como por lotes.
- Se ajustó nuevamente la posición de las firmas para tomar en cuenta el nuevo mensaje.


[ Version 15.1.0.1 ] --- 2024/04/22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX]

- Se ajustó el tamaño del texto de las tablas para evitar el desborde del contenido.
- Se colocó lineas para las firmas (Elaborado Por, Revisado Por y Firma del Trabajador) para los recibos de vacaciones, liquidaciones y préstamos.
- Se colocó una línea para las firmas del trabajador en los recibos de nomina y utilidades.
- Se eliminó el texto de los pie de página y el número de páginas.
