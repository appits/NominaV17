hr_salary_rule_customization
============================

El módulo extender y modifica el comportamiento relacionado con las reglas salariales y los cálculos de duración en el sistema.

Características
~~~~~~~~~~~~~~~

- Proporciona un campo para indicar si la regla salarial tiene una duración activa y un campo numérico para almacenar la duración de la regla salarial.
- Añade un campo para especificar la unidad de tiempo de la duración de la regla (días, meses, años u horas).
- Agrega un campo de tipo texto para mostrar un texto al usuario, indicándole cómo debe ser la empresión en lenguaje python para calcular la duración de la regla salarial.
- Evalúa la expresión Python en un entorno de ejecución seguro y se asigna el resultado a la duración de la regla salarial.
- Calcula y muestra la duración de las reglas salariales en las líneas de nómina.

Instrucciones de uso:
~~~~~~~~~~~~~~~~~~~~~

- Asegúrate de instalar los módulos base correspondientes para que el módulo funcione correctamente.
- Una vez instalado, podrás configurar y utilizar las reglas salariales con duración activa a través de la interfaz de administración de Odoo. 
- Al editar una línea de nómina, podrás ver y modificar la duración de la regla salarial asociada.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- base
- hr_leave_repose
- hr_payslip_report_customization

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
