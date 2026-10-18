# Conciliador de cheques ECHEQ

Autora: **Emilia Agustina Levi**. Versión: **tp2-echeq-v2**.

## Para qué sirve

El programa compara los cheques registrados por un banco con los de un sistema
de gestión. Ayuda al personal contable a encontrar diferencias de importes,
fechas, cheques faltantes, duplicados e identificadores ambiguos.

Lee los dos archivos, selecciona el período elegido, revisa los datos y guarda
cuatro reportes. Funciona desde la terminal. No se conecta con bancos reales.

## Archivos necesarios

Se necesita un archivo del banco y otro del sistema, en CSV o JSON. Se pueden
combinar los formatos. Cada registro debe tener estos cinco campos:

| Campo | Contenido |
|---|---|
| id_cheque | Código de texto. Por ejemplo, ECH-000000000001 |
| importe | Pesos argentinos, con hasta dos decimales y sin separador de miles |
| fecha_pago | Fecha de pago. Preferentemente DD/MM/AAAA |
| emisor | Nombre del emisor o endosante |
| estado | Estado indicado en el archivo de origen |

Los CSV de entrada usan coma como separador y UTF-8. Los JSON contienen una lista
de registros. La carpeta `data` incluye **120 registros ficticios por fuente**.
La [documentación de datos](data/README.md) explica su origen, variables,
condiciones de uso y limitaciones. No contiene información bancaria real.

## Cómo ejecutar el programa

Se necesita Python 3.11 o posterior. No requiere paquetes adicionales.
Desde la carpeta del proyecto:

```sh
python -m pip install -r requirements.txt
python -m src.main --banco data/banco.csv --sistema data/sistema.csv --salida outputs
```

El programa preguntará la fecha de inicio y la fecha final, en **DD/MM/AAAA**.
También pueden indicarse directamente:

```sh
python -m src.main --banco data/banco.csv --sistema data/sistema.json --desde 01/11/2026 --hasta 31/12/2026 --salida outputs
```

Las fechas del comando son un ejemplo. Se puede elegir cualquier período válido,
incluso entre años distintos. Se incluyen el primer día y el último. No se guarda
un período anterior ni se elige uno automáticamente. Para consultar las opciones:

```sh
python -m src.main --help
```

## Cómo se interpretan las fechas

El formato principal es **día/mes/año**. `01/02/2026` significa 1 de febrero.
También se aceptan fechas ISO, como `2026-02-01`, y fechas de Excel exportadas a
CSV o JSON: números de serie enteros y fechas textuales a medianoche.

Para números de Excel se usa el sistema 1900. Si el archivo usa el sistema 1904,
se debe indicar `--excel-banco 1904` o `--excel-sistema 1904`, según corresponda.
El programa no lee directamente archivos `.xlsx`. Tampoco adivina fechas con años
de dos dígitos, orden mes/día, horas distintas de medianoche o seriales con horas.

Una fecha ilegible queda fuera de la conciliación y de los totales del período.
El resumen identifica la fuente, la fila, el código y el motivo. Las fechas de
resultados se muestran en DD/MM/AAAA. Los originales de la auditoría conservan
el texto recibido para que puedan revisarse.

## Cómo leer los resultados

| Archivo de salida | Qué contiene |
|---|---|
| reporte_conciliacion.csv | Todos los cheques incluidos en el período y su resultado |
| cheques_con_errores.csv | Diferencias, faltantes y registros que requieren revisión |
| resumen.json | Período, cantidades, totales, cambios y filas excluidas |
| resumen_importes.csv | Totales monetarios y período analizado |

Los CSV de salida usan **punto y coma**, UTF-8 con BOM y punto decimal sin miles.
En Excel pueden importarse indicando esos datos. No hubo una prueba en Microsoft
Excel; se comprobó que los archivos se vuelven a leer correctamente con Python.
Repetir una ejecución reemplaza los cuatro reportes de la carpeta elegida.
Para conservar otra conciliación, se puede usar una carpeta de salida diferente.

Un cheque queda conciliado cuando coinciden ID, importe y fecha. Un código
abreviado se acepta si es un prefijo único del código bancario. Si hay varios
candidatos, se informa la ambigüedad. No se elige uno arbitrariamente.

Cada diferencia muestra el cheque, las fechas e importes de ambos archivos,
el tipo de error, una explicación y las filas de origen. Si tiene dos errores,
se informan ambos. Emisor y estado deben estar presentes, pero una diferencia
entre sus textos no impide por sí sola conciliar el cheque.

Los totales suman los importes válidos **dentro del período**, con `Decimal` para
evitar errores de precisión. Los duplicados se incluyen en ese total y se señalan,
pero no se concilian automáticamente. Los importes negativos, vacíos o inválidos
se excluyen con su motivo. Una diferencia total de cero no garantiza que todos
los cheques estén conciliados.

Ejemplo comprobado, del **01/11/2026 al 31/12/2026**:

- Total banco: **$50.477.968,91**.
- Total sistema: **$50.070.182,54**.
- Diferencia: **$407.786,37**.
- 86 conciliados, 15 con diferencias, 13 sin contraparte en el período y 23 para revisión.
- Dos filas adicionales no pudieron ubicarse en el período por tener fechas inválidas.

Ver [ejemplo de resumen](docs/ejemplo_resumen.json). Si una contraparte está fuera
del período, se informa como ausente **dentro de esa selección**, no del archivo
completo. Si no hay registros en las fechas elegidas, el resumen lo indica.

## Pruebas y organización

```sh
python -m unittest discover -s tests -v
```

Resultado comprobado: **65 pruebas aprobadas, ninguna fallida u omitida**.
Se verifican fechas, períodos, conciliación, importes, errores y los cuatro
reportes. CSV, JSON y sus combinaciones producen resultados equivalentes.

El código está en `src`; las pruebas, en `tests`; los datos, en `data`; el
generador, en `scripts`; y la documentación académica, en `docs`. Se usa Python
estándar: CSV, JSON, Decimal, fechas, expresiones regulares, clases y unittest.
Las [reglas y el diseño](docs/reglas.md) explican las funciones, clases y decisiones
de limpieza. Los registros modificados o excluidos quedan identificados.

La [matriz de cumplimiento](docs/cumplimiento_consigna.md) revisa los siete pasos
de la consigna. La [guía de defensa](docs/defensa.md) propone una demostración.
La versión se identifica con `git rev-parse 'tp2-echeq-v2^{commit}'`.
