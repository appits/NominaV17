hr_employee_customization
=========================

Este módulo extiende el modelo de empleados añadiendo mejoras para facilitar la gestión de los empleados en Odoo.

Características:
~~~~~~~~~~~~~~~~

- Agrega varios campos adicionales al modelo hr.employee para almacenar información como descuentos adicionales, información bancaria, edad, altura, peso, tipo de empleado, entre otros.
- Permite registrar los adelantos de salario solicitados por los empleados. Proporcionando estados como "Borrador", "Por aprobar", "Aprobado", "Pagado" o "Rechazado" para darles seguimiento.
- Facilita a los usuarios el registro de descripciones, montos, fechas de inicio y finalización, y el tipo de ingreso o descuento (ingreso o descuento adicional) para cada empleado.
- Los ingresos y descuentos adicionales pueden estar asociados a contratos de empleados específicos, lo que permite un seguimiento preciso y asociación con los contratos existentes.
- El módulo tiene en cuenta las tasas de cambio y permite especificar la moneda en la que se registra el ingreso o descuento adicional.
- Calcula automáticamente el total de sábados y domingos en caso de ser necesario, mostrando un mensaje alusivo al usuario.
- Cuenta con la generacion de constancias de trabajo

Instrucciones
~~~~~~~~~~~~~

- Para generar las constancias de trabajo, es necesario escoger los empleados a los cuales se le generará para que aparesca el boton 'Constancia de Trabajo', el cual al darle click preguntara por el responsable de la constancia para acto seguido generar el PDF.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr
- hr_payroll
- res_currency_customization
- hr_rule_category_customization
- hr_payroll_settings_customization

-----------------------------------------------------------

[ Version 15.1.1.0 ] --- 2024/05/09
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- Nuevo campo "Dinero asignado", que indica cuándo el anticipo fue asignado al empleado. Se actualiza cuando el estado del recibo de nómina es "Pagado".

[ Version 15.1.0.1 ] --- 2024/04/24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- Se añadió una validación para los números de identificación:
    #. No deben contener espacios.
    #. No pueden contener símbolos especiales.
    #. Deben comenzar con una V o E mayúscula para las identificaciones venezolanas o extranjeras respectivamente.
    #. Deben contener al menos ocho dígitos. Se debe rellenar con ceros a la izquierda en caso de ser necesario. Por Ejemplo: V01874557.