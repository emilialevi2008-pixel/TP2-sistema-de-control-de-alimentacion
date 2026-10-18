# Datos sintéticos de conciliación ECHEQ

## Procedencia, responsable y condiciones

Fuente: **simulación propia**, no extractos bancarios. Procedimiento completo en
[`scripts/generar_datos.py`](../scripts/generar_datos.py). URL del procedimiento:
https://github.com/emilialevi2008-pixel/TP2-sistema-de-control-de-alimentacion/blob/tp2-echeq/scripts/generar_datos.py

Responsable del conjunto: **Emilia Agustina Levi** (`emilialevi2008-pixel`). Fecha de generación: **18/10/2026**. No hubo consulta de datos
externos: la fecha de generación reemplaza una fecha de consulta de fuente remota.
Condiciones de uso del conjunto sintético: **CC0 1.0**
(https://creativecommons.org/publicdomain/zero/1.0/). No se atribuyen operaciones,
empresas, personas o números de ECHEQ reales. No hay información personal sensible.

## Tamaño y unidad de análisis

Cada fila representa **un registro físico de un cheque en una fuente**. Un mismo
cheque puede tener contraparte y también duplicados: una fila no equivale
necesariamente a un cheque único. Se parte de 120 cheques ficticios; se agregan
cuatro identidades especiales y se introducen ausencias/duplicados. Resultado:
**120 filas bancarias y 120 contables**, cinco variables por fila. Ambos archivos
superan el mínimo orientativo de 50 observaciones y tres variables de la consigna.

| Variable | Tipo y unidad | Significado / regla |
|---|---|---|
| id_cheque | texto | ECH- seguido de 6 a 12 dígitos ASCII; ceros iniciales preservados |
| importe | texto decimal, ARS | Valor monetario; hasta dos decimales, punto o coma decimal, sin miles |
| fecha_pago | texto de fecha | DD/MM/AAAA; también se admite ISO y serial Excel; se valida el calendario |
| emisor | texto | Emisor/endosante ficticio; obligatorio, no criterio de coincidencia |
| estado | texto | Estado de origen ficticio; obligatorio, no criterio de coincidencia |

El patrón es **sintético**, no describe la estructura oficial de ECHEQ de ningún
banco. En la simulación los IDs bancarios completos tienen 12 dígitos y algunos
contables tienen prefijos de 6, 8 o 9. El programa admite IDs de 6–12 dígitos en
ambos archivos: un ID contable solo se considera abreviado si no existe un exacto
y es prefijo estricto de uno o más IDs bancarios más largos. No hay fuzzy matching.

## Formatos equivalentes

- `banco.csv` / `sistema.csv`: UTF-8 con BOM, separador **coma**, cabecera de cinco
  columnas. Una coma decimal se entrecomilla automáticamente.
- `banco.json` / `sistema.json`: UTF-8, listas de objetos con las mismas claves y
  valores textuales que CSV. No hay objetos anidados ni wrappers.
- Los IDs deben ser texto, aun si parecen números. En entradas JSON externas se
  aceptan importes numéricos exactos usando Decimal al leer, nunca float.
- La fila de origen es el **ordinal del registro desde 1**, sin contar cabecera,
  no el número de línea física del editor (CSV permite campos multilínea).

## Generación reproducible y escenarios

```sh
python scripts/generar_datos.py --salida data --semilla 20261018
```

`random.Random` local, semilla fija y fecha base fija 01/11/2026 (solo para generar la muestra); no depende del
reloj ni del estado global del generador. Probado con Python 3.12.14. La prueba
`test_reproducibilidad_de_datos_y_analisis` regenera en una carpeta temporal y
compara los cuatro archivos **byte a byte** con los versionados. Una semilla
alternativa puede cambiar los valores; si produjera una colisión en los prefijos
esperados como únicos, el generador lo informa en lugar de alterar silenciosamente
el escenario. El comando sobrescribe solo los cuatro datasets en la carpeta dada;
para experimentar sin reemplazar la muestra, usar `--salida /tmp/echeq-datos`.

Escenarios sobre las 120 identidades iniciales (índices Python desde 0):

| Índices / adición | Situación introducida |
|---|---|
| 0–79 | Coincidencias normales; en 0 cambia emisor/estado sin error, en 1 espacios/minúsculas/coma decimal |
| 80–84 | Solo diferencia de importe (+100.25 en sistema) |
| 85–89 | Solo diferencia de fecha (+1 día) |
| 90–94 | Importe y fecha diferentes (−50.00 y +2 días en sistema) |
| 95–99 | Ausentes del banco |
| 100–104 | Ausentes del sistema |
| 105–109 | IDs contables abreviados únicos |
| 110 | ID bancario repetido en dos filas |
| 111 | ID contable repetido en dos filas, con importes diferentes |
| 112 | Importe bancario negativo |
| 113–114 | Importe contable vacío / no numérico |
| 115 | Fecha bancaria imposible |
| 116 | ID contable faltante |
| 117 | Importe negativo y fecha imposible simultáneos |
| 118–119 | Emisor / estado contable faltantes |
| ECH-777777… | Dos candidatos bancarios y un prefijo contable ambiguo |
| ECH-888888… | Dos prefijos contables compiten por una fila bancaria |
| ECH-000000000001 | Código con ceros iniciales y coincidencia correcta |

## Limpieza y exclusiones

Cada ejecución exige elegir inicio y fin, en DD/MM/AAAA. No hay período por
omisión. Solo se comparan/suman fechas válidas dentro de esos límites inclusivos.
Las filas con fecha ilegible o fuera de la selección quedan registradas por fuente
y ordinal en resumen.json. No se inventa una fecha para poder incluir un monto.
Dentro de la selección, los importes inválidos quedan fuera de las sumas; los
otros campos inválidos no impiden sumar un importe válido. Todas las ocurrencias
de IDs duplicados se bloquean para conciliación, pero sus importes válidos entran
en el bruto del período. Los datos originales no se sobrescriben.

Las fechas normalizadas y de presentación usan DD/MM/AAAA. Solo los valores
originales de la auditoría mantienen la entrada exacta. Se admite ISO sin ambigüedad
y seriales Excel enteros de 1900 (predeterminado) o 1904 (opción por fuente). No se
leen XLSX ni se adivina el sistema del libro. Las horas no nulas, seriales con
fracción y el día inexistente de Excel 1900 se rechazan con motivo. Ver docs/reglas.md.

## Limitaciones y sesgos

Es una muestra diseñada para probar reglas, no una distribución realista de
operaciones o errores. No sirve para inferir tasas bancarias ni tiempos de cobro.
No se consultó normativa bancaria, no se autentican cheques ni se valida su estado
legal. No hay datos para identificar una contraparte de un ID corrupto o vacío;
se conserva para revisión y no se inventa una coincidencia. Los cambios de estado
o emisor no alteran las reglas solicitadas de ID/importe/fecha. No hay conexiones
reales, acceso bancario, datos personales ni secretos.
