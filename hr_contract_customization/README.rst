hr_contract_customization
=========================

Este módulo extiende el modelo de contratos de Odoo para administrar los contratos de empleados en el sistema de recursos humanos. 
Agrega nuevas funcionalidades y campos al contrato, lo que permite realizar cálculos y configuraciones específicas relacionadas con los contratos y los beneficios sociales de los empleados.

Características:
~~~~~~~~~~~~~~~~

- Permite especificar el salario del empleado en diferentes monedas, así como realizar cálculos relacionados con las asignaciones salariales y las horas extras.
- Proporciona funcionalidades para calcular y gestionar los beneficios sociales de los empleados, como las vacaciones anticipadas, los bonos de vacaciones, prestaciones sociales acumuladas y utilidades.
- Permite registrar y realizar el seguimiento de los descuentos y adelantos salariales realizados a los empleados.
- El módulo incluye campos para registrar la antigüedad de los empleados, lo que facilita el cálculo de ciertos beneficios en función de su experiencia laboral.
- Permite establecer relaciones con otros modelos, como los motivos de salida de los empleados, las razones de retiro y las tasas de nómina.
- Se ofrece control de las retenciones SSO, SPF, LPVH e ISLR

Instrucciones:
~~~~~~~~~~~~~~

- Instala el módulo en tu instancia de Odoo.
- Completa la información requerida en los campos adicionales según tus necesidades y requisitos específicos.
- Asegúrate de configurar adecuadamente las monedas, tasas de nómina y otras opciones relacionadas en la configuración general de Odoo.
- Utiliza las funcionalidades adicionales, como el cálculo de beneficios sociales y los descuentos salariales, para llevar un seguimiento preciso de la información relacionada con los contratos de empleados y los beneficios correspondientes.
- Para actualizar la antiguedad se require hacer click en el boton 'Actualizar Anticipos/Préstamos'
- Para actualizar los campos 'Salario de cestaticked' y 'Salario minimo base SSO', se requiere modificar el check de 'Actualizar Salario'
- los campos 'Prestaciones sociales acumulados', 'Días adicionales acumulados', 'Anticipo de prestaciones sociales previos' y 'Acumulado de utilidades hasta hoy' sirven para realizar cargas iniciales, tambien se le puede asignar la fecha de cuando es esa carga

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_contract
- hr_holidays
- hr_employee_customization

-----------------------------------------------------------

[ Version 15.1.2.0 ] --- 2024/05/03
+++++++++++++++++++++++++++++++++++++

[IMP]

- Nuevo campo de "Intereses de prestaciones sociales previos", diseñado para cargas iniciales para el campo de "Intereses de prestaciones sociales".
- Nueva opción para configurar el cálculo de fideicomisos, opción "Nada" deshabilita y oculta el campo "Aporte de fideicomisos". 

[ Version 15.1.1.0 ] --- 2024/04/03
+++++++++++++++++++++++++++++++++++++

[IMP]

- Nueva configuración para el cálculo de fideicomisos en el apartado de Nómina:
    #. Trimestral: calcula el fideicomiso por cada trimestre del año.
    #. Fecha de inicio: calcula el fideicomiso cada vez que la antigüedad del trabajador completa un trimestre.

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
