payslip_details_custom_itsales
==============================

Este módulo tiene como propósito proporcionar funcionalidad adicional y personalizada para la generación de informes relacionados con las nóminas de empleados en Odoo, un sistema de gestión empresarial.

Características
~~~~~~~~~~~~~~~

- Permite generar informes específicos relacionados con las nóminas de empleados. Estos informes incluyen informes de Banavih, INCES e ISLR.
- Los informes generados pueden ser personalizados según los requisitos del usuario. 
- Proporciona opciones para seleccionar el período de tiempo, el tipo de período (mensual o trimestral), el estado de las nóminas y otros parámetros relevantes.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll 
- hr_payroll 
- hr_payroll_customization 
- hr_contract_customization

-----------------------------------------------------------

[ Version 15.1.1.0 ] --- 2024/05/24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [ISLR] Se añadieron nuevas categorías al cálculo del devengado.

[ Version 15.1.0.9 ] --- 2024/05/22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- Se añadió la columna "Referencia" para los reportes de nómina por concepto y detallado.

[ Version 15.1.0.8 ] --- 2024/05/21
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [ISLR] Se añadieron campos para la ficha, número de cedula de identidad y devengado mensual 
- [ISLR] Se agregó un sistema de filtrado por el tipo de nómina, junto con su correspondiente campo en la vista.
- [ISLR] Se modificó la consulta sql para:
    #. Filtrar por tipo de nómina.
    #. Calcular correctamente aquellos empleados con vacaciones en el periodo seleccionado.
    #. Facilitar la validación de las nóminas de vacaciones, considerando el periodo de vacaciones del empleado.
- [ISLR] Se realizaron ajustes al reporte (mejoras en el espaciado, tamaño de letra y ubicación de las columnas).
- [ISLR] Se realizaron ajustes a la vista del wizard.
- [ISLR] Se agregó un campo "RPE" en la vista para filtrar por los empleados con el LPVH activo.
- [ISLR] Se añadieron validaciones para las fechas de ingreso y egreso de los trabajadores.
- [ISLR] Se amplió la funcionalidad para generar los reportes.
- [ISLR] Se añadieron las traducciones correspondientes para los campos agregados.
- [ISLR] Se agregó una funcionalidad para imprimir los reportes en formato excel.
- [ISLR] Se añadieron validaciones para los empleados en periodo de vacaciones dentro y fuera del periodo seleccionado.
- [ISLR] Se modificó el footer para eliminar los datos innecesarios.
- [ISLR] Se realizaron correcciones menores a las consultas sql y a las validaciones.
- [ISLR] Se agregaron validaciones en caso de que la consulta en el periodo y estructura salarial determinada no encuentre empleados. 
- [ISLR] Limpieza y documentacion del código.

[ Version 15.1.0.7 ] --- 2024/05/21
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX]

- [Banavih] Agregada validación para los empleados en vacaciones en el dentro y fuera del periódo seleccionado


[ Version 15.1.0.6 ] --- 2024/05/17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [Banavih] Se agregaron nuevas validaciones para el caso de los empleados en periodo de vacaciones en el periodo seleccionado. 
- [Banavih] Se agregaron validaciones en caso de que la consulta en el periodo y estructura salarial determinada no encuentre empleados. 
- [Banavih] Limpieza y documentacion del código.

[ Version 15.1.0.5 ] --- 2024/05/15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [Banavih] Se agregaron tres nuevas reglas al cálculo. 

[ Version 15.1.0.4 ] --- 2024/05/15
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX]

- [Banavih] Se agregó una validación adicional para que el acumulado se coloque como sueldo mínimo solo si el periodo seleccionado es de un mes y si el acumulado es menor al sueldo minimo. 

[ Version 15.1.0.3 ] --- 2024/05/14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[FIX]

- [Banavih] Se modificó el footer para eliminar los datos innecesarios.
- [Banavih] Se realizaron correcciones menores a las consultas sql y a las validaciones.

[ Version 15.1.0.2 ] --- 2024/05/13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [Banavih] Se añadieron dos nuevas columnas en los reportes, para la fecha de ingreso y egreso.
- [Banavih] Se añadió un sistema de filtrado por el tipo de nómina, junto con su correspondiente campo en la vista.
- [Banavih] Se modificó la consulta sql para:
    #. Permitir el filtrado por tipo de nómina.
    #. Llevar a cabo el cálculo de los empleados con nómina de vacaciones correctamente.
    #. Facilitar la validación de las nóminas de vacaciones, considerando el periodo de vacaciones del empleado.
- [Banavih] Se añadió un nuevo campo "RPE" en la vista para filtrar por los empleados con el LPVH activo.
- [Banavih] Se realizaron ajustes al reporte (mejoras en el espaciado, tamaño de letra y ubicación de las columnas).
- [Banavih] Se realizaron ajustes a la vista del wizard.
- [Banavih] Se añadieron validaciones para las fechas de ingreso y egreso de los trabajadores.
- [Banavih] Se amplió la funcionalidad para generar los reportes.
- [Banavih] Se añadieron las traducciones para los campos agregados correspondientes.

[ Version 15.1.0.1 ] --- 2024/05/06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[IMP]

- [Banavih] Se añadieron tres nuevos campos en el recibo: ficha, la edad del empleado y salario básico.
- [Banavih] Se añadieron cuatro métodos de ordenamiento para los recibos: Por ficha, nombre, cédula o fecha de nacimiento.
- [Banavih] Se ajustó el wizard del reporte de Banavih para visualizar los campos y facilitar el uso.
- [Banavih] Se modificó la lógica en las consultas para incluir una fecha de inicio y fin, con sus respectivas validaciones.
- [Banavih] Los reportes ahora se visualizan en distintos períodos, ya sean semanales, quincenales o mensuales.
- [Banavih] Ajustes menores a los recibos.