# Sistema de conciliación automática de cheques electrónicos (ECHEQ)

**Autoría/titular:** cuenta GitHub `emilialevi2008-pixel`.
Desarrollo asistido por Codex. Completar el nombre académico de la estudiante en
la entrega formal. Versión candidata identificada por la etiqueta **`tp2-echeq-v1`**:

```sh
git rev-parse 'tp2-echeq-v1^{commit}'
```

Se reemplazó el comparador nutricional por pedido explícito de la usuaria. La
versión anterior permanece en `tp2-entrega-v1` y `tp2-comparador-nutricional`.
El nombre histórico del repositorio se conserva; el código de esta rama es ECHEQ.

## Problema, usuario, solución y alcance

Una pyme recibe un archivo bancario y mantiene otro contable. Ausencias,
abreviaturas, duplicados e inconsistencias de importe o fecha hacen que cotejarlos
manualmente sea lento y propenso a errores. La aplicación ayuda a personal
administrativo, contable y financiero a conciliar ambos archivos, identificar
exactamente qué ocurre en cada registro y comparar sus totales monetarios.

Primera versión: **consola**, dos entradas CSV/JSON, inspección/validación,
normalización, coincidencias exactas o por prefijo único, detección de errores,
totales brutos/conciliados/con diferencias, resumen de terminal y cuatro reportes.
No incluye web, GUI, base de datos, carga/edición manual, autenticación, IA ni
conexiones bancarias. Opera con datos ficticios, sin validar validez legal de ECHEQ.

Es un **tema propio** respecto de los ejemplos del PDF. La aprobación de la
cátedra **no está confirmada**. La implementación no equivale a esa aprobación,
a entrega en EVA ni a defensa realizada. Ver [propuesta](docs/propuesta.md).

## Datos y procedencia

Se incluyen **120 registros por fuente** (240 filas físicas), con cinco variables:
`id_cheque`, `importe` (ARS), `fecha_pago`, `emisor`, `estado`. Las cuatro entradas
son equivalentes por pares CSV/JSON y se generan de manera reproducible.

Fuente: simulación propia con semilla **20261018**, no archivos bancarios reales.
Responsable: cuenta titular del proyecto; fecha de generación **2026-10-18**;
condiciones del dataset: CC0 1.0. Unidad de análisis: una fila de una fuente, no
necesariamente un cheque único por la existencia de duplicados.
La [documentación de datos](data/README.md) incluye URL/procedimiento, responsable,
licencia/condiciones, fecha, diccionario, escenarios, reglas y limitaciones.

## Instalación

Python **3.11 o posterior**; probado en **3.12.14**. Solo biblioteca estándar;
`requirements.txt` documenta que no hay paquetes de terceros obligatorios.
Desde la raíz del repositorio:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

En Windows: `.venv\Scripts\activate`. El entorno virtual es opcional porque no
hay dependencias externas. No hay compilación, servicios ni claves que configurar.

## Uso: un comando de principio a fin

```sh
python -m src.main --banco data/banco.csv --sistema data/sistema.csv --salida outputs/
python -m src.main --banco data/banco.json --sistema data/sistema.json --salida outputs/json
python -m src.main --banco data/banco.csv --sistema data/sistema.json --salida outputs/mixto
python -m src.main --banco data/banco.json --sistema data/sistema.csv --salida outputs/mixto_inverso
python -m src.main --help
```

Sin argumentos se usan `data/banco.csv`, `data/sistema.csv` y `outputs`.
La aplicación lee, inspecciona, valida, limpia/normaliza, concilia, calcula importes
y exporta. Todos estos pasos se coordinan desde main; no hay notebooks ni orden
oculto. Las cuatro combinaciones de formatos fueron ejecutadas y verificadas.

- **Salida 0:** procesamiento y reportes completados, incluso si hay discrepancias.
- **Salida 2:** fallo de lectura, estructura, parámetros o escritura, con mensaje
  en stderr. No se reemplazan los reportes anteriores si falla la lectura.
- Archivos vacíos o solo cabecera no constituyen una conciliación exitosa.
- Filas con campos inválidos quedan para revisión, no se eliminan silenciosamente.

La carpeta se crea automáticamente. Repetir el comando reemplaza únicamente los
cuatro reportes de esa carpeta; no acumula resultados ni borra otros archivos.
Usar carpetas diferentes para conservar corridas. Se impide sobrescribir una
entrada cuyo nombre coincida con un reporte de salida. Los cuatro archivos se
preparan antes de reemplazarlos individualmente; no se promete una transacción
atómica de todo el directorio frente a un fallo del sistema de archivos.

## Reglas de validación, limpieza y conciliación

### Campos y normalización

El esquema exige los cinco campos; claves adicionales o ausentes se registran
como inválidas. Emisor y estado deben ser texto no vacío. No hay inferencias de
identidad desde esos campos. Se limpian espacios y se normalizan ID/estado a
mayúsculas sin modificar las entradas originales. La auditoría queda en
`resumen.json`: fuente, ordinal de fila, original, normalizado, cambios y motivos.

La expresión regular **`ECH-[0-9]{6,12}`**, aplicada con `fullmatch`, valida el ID
sintético de 6–12 dígitos ASCII. No describe un formato bancario oficial ni
comprueba autenticidad; conserva ceros iniciales. Una regla de prefijo separada
resuelve abreviaturas. Las fechas exigen `AAAA-MM-DD` con regex y, además, una
fecha real validada por `datetime.date.fromisoformat` (incluidos años bisiestos).

Importes: Decimal exacto, sin float; se acepta punto o coma decimal, sin separador
de miles ni exponentes, con hasta dos decimales. Se rechazan faltantes, negativos,
no numéricos, no finitos, bool/float y exceso de precisión. No se redondean
silenciosamente valores con tres decimales. Máximo individual documentado:
999999999999999.99 ARS. Cero es válido. No se imputa cero a datos desconocidos.
JSON numérico se lee directamente como Decimal, sin paso intermedio por float.

### Correspondencia y estados

1. **Exactos primero:** si ID, importe y fecha_pago coinciden, `CONCILIADO`.
2. **Prefijo estricto:** solo cuando no hay exacto, se buscan IDs bancarios más
   largos que comiencen exactamente por el ID contable. Si hay un único candidato
   válido, disponible y sin competencia, comparar importe/fecha; si coinciden,
   `CONCILIADO_ID_ABREVIADO`. Nunca usar distancia de texto ni aproximaciones.
3. Más de un ID candidato, o varios prefijos contables compitiendo por una fila:
   `COINCIDENCIA_AMBIGUA`. Se reportan los candidatos con sus filas bancarias.
4. Diferencia de importe: `ERROR_IMPORTE`, montos y diferencia banco−sistema.
   Diferencia de fecha_pago: `ERROR_FECHA`, ambas fechas. Si ocurren las dos:
   `CON_DIFERENCIAS` con **ambos** tipos de error, no dos filas duplicadas.
5. Sin candidato: `NO_ESTA_EN_BANCO` / `NO_ESTA_EN_SISTEMA`.
6. IDs repetidos en una fuente: **todas** sus ocurrencias son `ID_DUPLICADO`;
   ninguna se selecciona automáticamente. Otras invalidaciones se conservan también.
7. Campos inválidos: `DATOS_INVALIDOS`. Si la contraparte existe pero está bloqueada,
   `PENDIENTE_REVISION` con motivo específico, en vez de afirmar que está ausente.
8. Un banco ya reservado por exacto no se reutiliza para otro abreviado. Todas las
   propuestas por prefijo se evalúan antes de asignar: no decide el orden de filas.

Los candidatos incluyen IDs reconocibles de filas inválidas/duplicadas; excluirlos
podría fabricar una unicidad falsa. Un ID corrupto que no cumple el patrón no es
utilizable como candidato y se conserva para revisión, sin adivinar su contraparte.
Cambios de emisor/endosante o estado **no** generan error automático de conciliación
si ID, importe y fecha son compatibles. Fecha comparada: exclusivamente fecha_pago.

## Importes y conteos: bruto no significa conciliado

- **Bruto por archivo:** suma de todos los importes válidos, estén conciliados o no.
  Incluye cada ocurrencia duplicada válida y también filas con ID/fecha/emisor
  inválidos cuyo importe sí sea válido. Se señalan las filas duplicadas incluidas.
- Se excluyen de la suma los importes inválidos; se informa fuente, fila, valor
  original y motivo. Incluidos + excluidos conserva el total de filas por fuente.
- Diferencia total = bruto banco − bruto sistema; absoluta = valor absoluto.
- **Conciliado:** suma de pares correctos exactos o abreviados. Cada par una vez;
  se verifica igualdad de sus sumas de banco y sistema. No sumar ambos lados juntos.
- **Con diferencias:** suma por fuente solo de los pares con error de importe y/o
  fecha. Un par con dos errores se cuenta y suma una sola vez.
- Se publican además sumas por grupo (conciliados, con diferencias, sin
  correspondencia, revisión): su suma por fuente debe conservar el bruto.
- Una diferencia global cero **no** demuestra que cada cheque esté conciliado.

Los conteos se distinguen: registros válidos son filas con campos válidos, incluso
si el ID está duplicado; habilitados son válidos **y no duplicados**. Una fila
inválida puede estar duplicada también: estos indicadores no son categorías
excluyentes. Los cuatro grupos de resultados sí lo son. Un par representa dos
filas físicas y un resultado; una fila sola representa un resultado. Los ambiguos
son un subconjunto de pendientes, por lo que no se suman otra vez. Las incidencias
se cuentan por tipo y resultado; pueden coexistir tipos en el mismo resultado.

## Cuatro reportes e interpretación

| Archivo | Contenido |
|---|---|
| reporte_conciliacion.csv | Todos los resultados; IDs, importes, diferencia, fechas, estado, tipos, descripción y filas de origen |
| cheques_con_errores.csv | Subconjunto de todo resultado no conciliado: diferencias, ausencias y revisión |
| resumen.json | Conteos, estados/incidencias, totales, incluidos/excluidos, sumas por grupo, inspección y auditoría |
| resumen_importes.csv | Una fila con los totales monetarios y cantidades incluidas/excluidas de cada suma |

CSV de **salida**: UTF-8 con BOM, separador **punto y coma**, punto decimal sin miles;
puede abrirse/importarse en Excel seleccionando esos parámetros. No se afirma una
prueba en Microsoft Excel; se comprobó relectura con csv de Python. Los CSV de
**entrada** usan coma. JSON: UTF-8; montos monetarios como cadenas decimales exactas,
no números binarios. Al importar IDs en una planilla, indicar columna de texto.

Las columnas obligatorias de detalle se complementan con grupo, candidatos y
valores monetarios originales. Una diferencia vacía en una fila sin par o con
importe inválido significa **no calculable**, nunca cero implícito.
`fila_origen_*` es el ordinal del registro desde 1 sin cabecera, no línea física.

### Ejemplo real del conjunto sintético incluido

```text
Importe total banco:        $50.505.628,82
Importe total sistema:      $50.070.182,54
Diferencia banco-sistema:      $435.446,28
Diferencia absoluta:           $435.446,28
Importe conciliado:         $40.522.469,11

Conciliados: 86 (81 exactos y 5 abreviados)
Con diferencias: 15
Sin correspondencia: 11
Pendientes de revisión: 27 (incluyen 3 ambiguos)
Banco: 119 importes incluidos, 1 excluido
Sistema: 117 importes incluidos, 3 excluidos
```

Los 139 resultados trazan exactamente las 240 filas de origen:
`2 × (86 + 15) + 11 + 27 = 240`. Los 15 pares con diferencias suman
5.765.714,38 ARS en banco y 5.765.965,63 ARS en sistema. El detalle identifica cada
problema; el saldo global no permite deducir cuántos cheques fallaron. Ver el
[extracto JSON generado](docs/ejemplo_resumen.json).

## Diseño del código y paradigmas

```text
src/
  fuentes.py       FuenteDatos (ABC), FuenteCSV, FuenteJSON y cargar
  modelos.py       ChequeElectronico y Registro trazable
  validaciones.py  normalizar_campos, validar_importe, validar_registro, limpiar_registros
  conciliacion.py   indexar, emparejar, conciliar y verificar_trazabilidad
  importes.py       calcular_total_bruto y formato_ars
  pipeline.py       inspeccionar, resumir y ejecutar
  reportes.py       detalle, escribir_csv, guardar_reportes
  main.py           argumentos, resumen terminal y coordinación
scripts/generar_datos.py
tests/              fuentes, validaciones, conciliación, importes e integración
data/               cuatro entradas y README de procedencia
docs/               propuesta, defensa, cumplimiento y ejemplo de resultado
outputs/            generados, ignorados por Git
```

**Estructurada:** main coordina etapas, con condicionales y bucles explícitos.
**Funcional:** cálculos, normalización y comparación reciben datos y devuelven
resultados; no dependen de notebook ni servicios globales. La normalización copia
las filas originales; el generador usa su propia instancia de Random.
**Orientada a objetos:** FuenteDatos aporta el contrato útil `cargar(ruta)` que
ambos lectores implementan. ChequeElectronico reúne ID, importe, fecha, emisor y
estado con métodos `diferencias` y `diferencia_importe`, utilizados por el motor.
Registro conserva procedencia y errores; ResultadoConciliacion modela un par o una
fila pendiente. No se depende del formato de origen para conciliar o sumar.

## Pruebas y reproducción de datos

```sh
python -m unittest discover -s tests -v
python scripts/generar_datos.py --salida /tmp/echeq-datos --semilla 20261018
```

**Resultado ejecutado: 51 pruebas, todas aprobadas, ninguna omitida**.
Se cubren los 35 casos solicitados en el texto adjunto: normales, prefijos,
ambigüedad, errores múltiples, ausencias, duplicados, invalidaciones, archivos
rotos/vacíos, precisión Decimal, sumas/exclusiones, correspondencia uno a uno,
conservación, equivalencia/repetibilidad, cuatro reportes y coherencia detalle/resumen.
Además se verifica que reportes no sobrescriban entradas y que una lectura fallida
no altere salidas anteriores. Las cuatro combinaciones CSV/JSON producen los
cuatro archivos idénticos byte a byte. No se requieren bibliotecas para tests.

## Git, versión y entrega

Desarrollo en la rama **tp2-echeq**, con al menos siete avances reales desde el
reemplazo: alcance, datos/fuentes, validaciones/importes, motor, CLI/reportes,
pruebas y documentación. Antes de cada commit se revisaron estado y diferencias.
No se reescribió la historia nutricional ni se crearon commits vacíos.

```sh
git log --oneline --reverse tp2-entrega-v1..tp2-echeq
git show tp2-echeq-v1 --stat
git status --short
```

Repositorio: https://github.com/emilialevi2008-pixel/TP2-sistema-de-control-de-alimentacion
Entregar el enlace de la etiqueta ECHEQ y el identificador evaluado: la etiqueta
fija la versión aunque main avance posteriormente. La publicación final se
verifica con git ls-remote; no se fuerza ni reescribe la historia del remoto.

La [matriz de cumplimiento](docs/cumplimiento_consigna.md) revisa los siete pasos
individualmente. [VERIFICACION_TP2.md](VERIFICACION_TP2.md) presenta su balance.
Quedan fuera de la ejecución técnica: aprobación del tema propio, identificación
nominal definitiva, acceso docente si el repositorio es privado, fechas/medio EVA
y defensa individual. El PDF remite las fechas a EVA; no se inventan plazos.
Si corresponde recuperación del TP1, preparar esa instancia según la cátedra.

## Límites y defensa

Datos deliberadamente sintéticos, no representativos de bancos reales. Sin
normativa, autenticidad, integración financiera ni inferencias sobre el emisor.
Resolución conservadora: las ambigüedades se presentan para revisión; no se
«corrigen» inventando importes, fechas o contrapartes. El motor usa índices exactos
y búsqueda de prefijos en memoria; está destinado al tamaño acotado del TP.

La [guía de defensa](docs/defensa.md) propone una demostración y preguntas sobre
los datos, Decimal, regex/calendario, clases, trazabilidad, pruebas e historial.
La estudiante deberá comprender y defender individualmente el trabajo. No se
presenta la preparación técnica como aprobación o entrega académica final.
