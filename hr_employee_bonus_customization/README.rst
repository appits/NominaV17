hr_employee_bonus_customization
===============================

La función de este módulo es gestionar los bonos para los empleados de una organización. 
Hace posible asignar distintos tipos de bonos a los empleados, como vales de juguetes, vales escolares y bonos varios.

Características:
~~~~~~~~~~~~~~~~

- Permite definir diferentes tipos de bonos, como vales de juguetes, vales escolares y bonos varios. Cada tipo de bono con su propia configuración y propiedades.
- Calcula automáticamente de cuánto será el bono en base a ciertos criterios, como la edad de los hijos del empleado y el nivel de estudios de los hijos en el caso de los vales escolares.
- Asigna automáticamente los bonos a los empleados que cumplen con los criterios establecidos. Los empleados elegibles se agregan a una lista y se les asigna la cantidad correspondiente de bono.
- Provee diferentes estados para los bonos, como "Nuevo", "Borrador", "Asignado" y "Cancelado". Estos permiten realizar un seguimiento del proceso de asignación de bonos.

Instrucciones:
~~~~~~~~~~~~~~

- Antes de utilizar el módulo, se deben configurar los diferentes tipos de bonos y sus propiedades, como la cantidad, las edades mínimas y máximas, y el nivel de estudios en el caso de los vales escolares.
- Una vez configurados los bonos, se puede iniciar el proceso de asignación. Esto se puede hacer mediante la activación del botón "Confirmar" en el formulario del bono correspondiente. El sistema buscará automáticamente los empleados elegibles y asignará los bonos a aquellos que cumplan con los criterios establecidos.
- Se puede realizar un seguimiento de los bonos asignados y su estado a través de la interfaz del módulo. Se pueden cancelar bonos asignados o marcarlos como "Borrador" si se requiere algún ajuste.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
