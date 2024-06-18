hr_export_payroll_payments
==========================

La función de este módulo es permitir la exportación de pagos de nómina en formato de archivo de texto plano desde Odoo. 

Características:
~~~~~~~~~~~~~~~~

- Permite exportar pagos de nomina de banavih, de bono alimenticio y de aporte de fideicomiso en formato txt.
- Proporciona dos modalidades de pago, ya sea para empleados individuales o por lotes.
- Permite configurar diversos parámetros, como el banco, la cuenta bancaria, el tipo de operación y las fechas de inicio y fin.
- Proporciona opciones para filtrar los empleados según diferentes criterios, como la estructura de nómina y el tipo de operación.
- Gestiona el estado de las transacciones, permitiendo marcarlas como borrador o confirmadas.

Instrucciones de uso:
~~~~~~~~~~~~~~~~~~~~~

- Lleva a cabo la instalación del módulo.
- Una vez instalado, asegúrate de configurar correctamente el banco, la cuenta bancaria y otros parámetros necesarios antes de realizar la exportación.
- Elige entre la opción de pago individual o en lotes, según tus necesidades.
- Configura los filtros necesarios, como la estructura de nómina y el tipo de operación, para refinar la selección de empleados.
- Una vez que hayas configurado todos los parámetros, puedes generar el archivo de texto plano haciendo clic en el botón correspondiente.
- Antes de marcar la transacción como confirmada, revisa cuidadosamente la información y asegúrate de que sea correcta.

Dependencias:
~~~~~~~~~~~~~
Asegúrate de que los siguientes módulos están pre-instalados antes de instalar este módulo:

- l10n_ve_payroll
- hr
- hr_payroll

-----------------------------------------------------------

[ Version 15.0.1.0.1 ] --- 2024/04/26
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[FIX]

- Correccion de decimales al generar TXT del banco Provincial

[ Version 15.1.0.0 ] --- 2024/04/03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~