hr_employee_exceptions
======================

El propósito de este módulo es modificar los modelos "hr.payslip.employees" y "hr.contract" para tomar en cuenta las excepciones de nómina en los contratos de los empleados.

Características:
~~~~~~~~~~~~~~~~

- Permite seleccionar empleados específicos como excepciones para el procesamiento de la nómina.
- Se redefine el método para calcular la lista de empleados que serán procesados en la nómina. 
- Además del cálculo base, se filtran los empleados que tienen la estructura de nómina definida en su contrato como excepción y se encuentran en estado "abierto".
- Los empleados filtrados como excepciones se eliminan de la lista principal de empleados y se asignan al campo "exceptions_employee_ids".
- Agrega un campo exception_struct_ids que permite seleccionar las estructuras de nómina que se considerarán como excepciones en el contrato.

Instrucciones de uso:
~~~~~~~~~~~~~~~~~~~~~

- Llevar a cabo la instalación del módulo
- Antes de utilizar el módulo, se deben definir las estructuras de nómina que se considerarán como excepciones.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr_payroll_customization
- hr_employee_customization
- hr_contract_customization

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~