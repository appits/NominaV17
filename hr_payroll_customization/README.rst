hr_payroll_customization
========================

El propósito de este módulo es personalizar y extender la funcionalidad del módulo de Recursos Humanos (HR) y Nómina de Odoo. 
Introduce varios cambios de comportamiento y mejoras a los modelos existentes relacionados con la estructura salarial, las reglas salariales y las líneas de nómina.

Características:
~~~~~~~~~~~~~~~~

- Agrega un campo para establecer los distintos tipos de estructuras de nómina.
- Permite personalizar la estructura de nómina existente agregando el campo currency_id al modelo hr.payroll.structure.type. Esto permite especificar la moneda asociada a cada tipo de estructura de nómina.
- Introduce campos que permiten especificar las reglas salariales y las líneas de nómina, realizando los cálculos basándose en los contratos de los empleados.
- Permite configurar los valores de nómina, los cuales incluyen la tasa, el monto de la tasa, los números de lunes y los números de sábados y domingos, y el anticipo quincenal.
- Agrega el campo department_ids, relacionado con los departamentos asociados a la estructura de nómina. Esto permite filtrar los empleados según los departamentos seleccionados.
- Crea una lista de valores de nómina (payslips_vals) para cada contrato filtrado, que incluye información como el nombre, el empleado, la fecha de inicio y finalización, y la estructura de nómina. 
- Genera las nóminas a partir de todos los datos previamente calculados.
- Utiliza la mezcla de actividades de correo de Odoo para permitir la comunicación y colaboración relacionada con los registros de hr.payroll.structure a través de hilos de correo.
- Permite la gestión de préstamos de empleados, agregando pagos de utilidades, avances de vacaciones y descuentos de vacaciones.
- Incluye una acción para enviar los recibos de pago por correo electrónico a los empleados. 
- Genera archivos PDF de los recibos de pago y los adjunta a los correos electrónicos correspondientes.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_employee_customization
- hr_contract_customization
- hr_payroll

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instrucciones de uso: Para utilizar este módulo, se recomienda tener conocimientos previos sobre el funcionamiento básico de Odoo y su módulo de Recursos Humanos y Nómina. Después de instalar el módulo, puede acceder a las funciones y características personalizadas a través de la interfaz de usuario de Odoo. Por ejemplo, para generar las nóminas, puede seguir los pasos habituales para acceder al menú correspondiente, seleccionar los empleados y ejecutar la función "Generar Nómina".
