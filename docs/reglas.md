# Reglas y diseño del conciliador

## Recorrido de los datos

`main` recibe archivos y período. `FuenteDatos.cargar(ruta)` es la interfaz común;
`FuenteCSV` y `FuenteJSON` implementan el contrato y devuelven listas de diccionarios.
No ocultan archivos vacíos, estructuras rotas, claves repetidas ni errores de lectura.
`filtrar_periodo` interpreta fechas y guarda los ordinales originales de las filas.
`limpiar_registros` valida/normaliza solo los registros seleccionados. `conciliar`
resuelve coincidencias; `resumir` calcula montos/conteos y `guardar_reportes` exporta.

## Fechas, selección y auditoría

`interpretar_fecha` admite DD/MM/AAAA e ISO estricto, con calendario real. Las regex
comprueban el formato y `date` comprueba meses, días y años bisiestos. No se intenta
MM/DD/AAAA. Se aceptan exportaciones textuales a medianoche, sin zona horaria.
Los números de serie Excel enteros se interpretan con la base 1900 o 1904 indicada
para cada fuente. En 1900 se rechaza el serial 60, que representa un día inexistente.
Se rechazan fracciones con horas, horas no nulas, años cortos y fechas imposibles.
Un número no revela si el libro usaba 1900 o 1904: se aplica la configuración
explícita, 1900 por defecto, y se guarda esa elección en resumen.json.

`PeriodoConciliacion` valida inicio <= fin y contiene ambos límites. Sus fechas
siempre se eligen al ejecutar; no existen valores fijos de análisis. Las fechas
fijas del generador son parte de la simulación reproducible, no del período usado
por el programa. El usuario puede elegir cualquier año o intervalo válido.

Cada fila leída queda seleccionada, fuera de período o con fecha no interpretable.
La suma de esas cantidades conserva el total leído por fuente. Las exclusiones
se registran en `filtrado`, con fuente/fila y motivo; una fecha ilegible incluye
el ID y el valor original para revisión. No se imputa una fecha para incluirla.
No se suman montos cuya fecha no permita ubicarlos dentro del período.
Los detalles y montos contienen únicamente filas seleccionadas. Las exclusiones
son información de auditoría, no cheques conciliados fuera de la selección.

Las filas seleccionadas conservan el ordinal original, desde 1 sin cabecera.
El resultado normalizado usa DD/MM/AAAA; la auditoría conserva también el original,
incluso si era ISO o un serial. No se alteran los archivos de entrada.

## Validación y conciliación

El esquema exige id_cheque, importe, fecha_pago, emisor y estado; campos extras
se registran como error. Se limpian espacios y se normalizan ID/estado a mayúsculas.
`ECH-[0-9]{6,12}` con fullmatch valida IDs ASCII sintéticos: no es un patrón bancario
oficial. Los ceros iniciales se conservan como texto.

`ChequeElectronico` reúne atributos del dominio y compara importe y fecha_pago.
`Registro` conserva fuente, fila, original, normalizado y errores. El motor usa
funciones separadas para indexar, emparejar y comprobar correspondencia uno a uno.
La programación estructurada coordina el flujo; las funciones reciben/devuelven
datos sin depender del formato; la orientación a objetos concentra contratos y
comportamientos del dominio.

Los exactos tienen prioridad. Un ID contable abreviado solo puede coincidir por
prefijo estricto con un ID bancario más largo. Debe haber un único candidato,
válido y disponible; dos prefijos que compiten por el mismo banco quedan ambiguos.
No se usa fuzzy matching. Duplicados en el período: se señalan todas sus ocurrencias
y se bloquea su asignación. Los candidatos incluyen IDs reconocibles de registros
seleccionados inválidos/duplicados para no fabricar unicidad. Los IDs o registros
fuera del período no forman parte de la comparación solicitada.

Errores de importe y fecha pueden coexistir en una sola fila de resultado.
Los cambios de emisor/endosante y estado no son criterios automáticos de error.
Si una contraparte seleccionada existe pero es inválida/duplicada, se informa
pendiente; si no está incluida, se informa ausente dentro del período. No se infiere
una coincidencia para un ID corrupto. Los estados y errores conservan sus nombres
documentados en la matriz de cumplimiento.

## Totales y conteos

Importes: Decimal, sin float, hasta dos decimales, punto o coma decimal sin miles
ni exponentes. Cero es válido. No se redondean valores con más de dos decimales.
Se rechazan negativos, vacíos, no numéricos/no finitos y montos mayores a
999999999999999.99 ARS. JSON numérico se lee como Decimal directamente.

El bruto del período incluye todos sus importes válidos, aun con ID/emisor/estado
inválidos o duplicados. Los importes inválidos seleccionados se excluyen con su
motivo; las exclusiones por fecha/período se informan por separado. El monto
conciliado suma cada par correcto una vez; los pares con uno o dos errores se suman
una sola vez por fuente. Las sumas por los cuatro grupos conservan el bruto.

Un par tiene dos filas físicas y un resultado. Una fila sola es un resultado.
Ambiguos están incluidos en pendientes: no se suman otra vez. Válido significa
campos válidos; habilitado significa válido y no duplicado. Las incidencias pueden
coexistir; los cuatro grupos de resultados son excluyentes. El saldo global cero
no demuestra conciliación individual.

## Exportación y errores de ejecución

Cuatro archivos: detalle completo, detalle de errores, resumen JSON y resumen de
importes CSV. Los CSV de salida son UTF-8 con BOM, separador `;`, punto decimal.
Los monetarios JSON son cadenas exactas. Los reportes identifican el período;
cuando no hay filas, resumen.json y resumen_importes.csv explicitan la selección.

Una diferencia vacía en un registro sin par no se interpreta como cero. Los
candidatos contienen código y fila bancaria. Se preservan originales/cambios.
La escritura prepara los cuatro archivos antes de reemplazarlos individualmente;
no promete atomicidad del conjunto ante un fallo de disco. Se bloquea sobrescribir
una entrada. La salida 0 significa ejecución con reportes, no ausencia de errores
contables; la salida 2 significa fallo de parámetros/lectura/escritura. Una lectura
fallida no modifica reportes anteriores. Los archivos de estructura vacía fallan;
una selección vacía válida genera reportes y un mensaje claro.
