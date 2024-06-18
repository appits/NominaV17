res_currency_customization
==========================

El propósito de este módulo es extender y modificar el comportamiento relacionado con las tasas de cambio de moneda en el sistema Odoo, específicamente en el contexto de la nómina y los cálculos relacionados con la nómina.

Características:
~~~~~~~~~~~~~~~~

- Añade un nuevo modelo para gestionar las tasas de cambio, que incluye campos como la fecha de la tasa de cambio, el valor de la tasa de cambio y la compañía asociada. 
- También se aplican algunas restricciones para garantizar que solo haya una tasa de cambio por día y que el valor de la tasa de cambio sea estrictamente positivo.
- Se agrega un campo booleano que indica si una tasa de cambio es específicamente para la nómina.
- Añade un método para realizar la conversión de una cantidad de una moneda a otra. 
- Proporciona un método que obtiene la tasa de cambio específica para la nómina entre dos monedas.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll

-----------------------------------------------------------

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
