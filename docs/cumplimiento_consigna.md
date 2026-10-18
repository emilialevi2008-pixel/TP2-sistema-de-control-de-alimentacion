# Matriz de cumplimiento del TP2 — ECHEQ

Referencia: `consigna_TP2.pdf` adjunto, nueve páginas completas. Su SHA-256 es
`48936cb16630d9ae1e2f8ae863fbd4944d0738319dc4e623e530e9c6d91a7a5c`;
coincide con el PDF revisado antes. Los sufijos (1)/(3) mencionados en los textos
no corresponden al nombre efectivo del adjunto, pero la verificación directa del
PDF sí fue realizada. El texto de ECHEQ recibido termina en sección 14 con
`docs: definir problema y`; no se inventó contenido posterior.

Estados: **verificado** = comprobación ejecutada; **documentado** = evidencia
revisada en archivos; **externo pendiente** = no demostrable mediante ejecución.
La implementación completa no equivale a aprobación ni defensa académica.

## Los siete pasos evaluables, individualmente

| Paso / requisito | Archivo / implementación | Evidencia | Estado / observaciones |
|---|---|---|---|
| 1. Problema, necesidad y usuario | README; docs/propuesta.md | Descripción de conciliación contable de pymes | Documentado |
| 1. Solución, operaciones, salida e interpretación | README; main.py; reportes.py | test_cli_real_y_error_de_lectura; ejemplo_resumen.json | Verificado; cuatro reportes y terminal |
| 1. Primera versión pequeña y exclusiones | PLAN_TP2.md; README | Solo CLI, sin web/GUI/BD/IA/conexiones | Documentado |
| 1. Tema propio aprobado | docs/propuesta.md | No se recibió constancia de aprobación | **Externo pendiente**; no presumirla |
| 2. Fuente/procedimiento, URL, responsable, licencia/condiciones, fecha | data/README.md; generar_datos.py | Semilla 20261018, fecha 2026-10-18; CC0 1.0 | Documentado; simulación propia permitida por PDF |
| 2. Unidad de análisis y variables | data/README.md | Diccionario de cinco campos con unidades | Documentado; fila física por fuente |
| 2. 50 observaciones / 3 variables o justificación | Cuatro datasets en data | test_csv_json_equivalentes_y_ids_textuales | Verificado: 120 filas y 5 variables por archivo |
| 2. Muestra conservada y obtención reproducible | data; scripts/generar_datos.py | test_reproducibilidad_de_datos_y_analisis | Verificado byte a byte |
| 2. Sesgos, limitaciones y privacidad | data/README.md | Revisión de datos ficticios y exclusiones | Documentado; sin datos bancarios reales |
| 3. Leer CSV y JSON de esquema definido | fuentes.py | test_csv_json_equivalentes_y_ids_textuales | Verificado |
| 3. Inspeccionar y validar supuestos | validaciones.py; inspeccionar | test_campos_faltantes_y_obligatorios; test_errores_de_esquema_y_fuente | Verificado; inspección en resumen.json |
| 3. Limpiar/transformar y registrar filas | normalizar_campos; validar_registro; auditoria | test_normalizacion_sin_mutar_y_auditoria; test_todas_invalidas_conservan_auditoria_y_reportes | Verificado; no eliminación silenciosa |
| 3. Analizar y comunicar resultado útil | conciliar; resumir; reportes | test_integracion_csv_json_mixtos_y_cuatro_reportes_equivalentes | Verificado; detalle por cheque y montos |
| 3. Una instrucción, repetibilidad | main.py; README | Cuatro combinaciones CLI y test_reproducibilidad_de_datos_y_analisis | Verificado; sin notebooks |
| 4. Funciones diferenciadas | fuentes, validaciones, conciliacion, importes, reportes | Pruebas separadas por módulo | Verificado; no dependen del formato de origen |
| 4. Clase significativa de dominio | ChequeElectronico | test_error_importe; test_error_importe_y_fecha_simultaneos | Verificado; métodos usados por motor |
| 4. FuenteDatos abstracta y CSV/JSON concretas | fuentes.py | test_abstraccion y equivalencia | Verificado; cargar(ruta) común |
| 4. Regex pertinente y límites explicados | PATRON_ID; PATRON_FECHA; README | test_identificador_invalido_y_cero_inicial; test_fecha_imposible_y_formato | Verificado; patrón sintético, calendario adicional |
| 4. Supuestos y mensajes claros | validar_importe; validar_registro; CLI | test_importe_no_numerico_o_no_finito; test_cli_real_y_error_de_lectura | Verificado |
| 5. Caso normal | tests/test_conciliacion.py | test_coincidencia_exacta | Verificado |
| 5. Inválido o caso límite | tests/test_validaciones.py | Negativos, vacíos, formato, fecha imposible, campos ausentes | Verificado |
| 5. Propiedad relevante | tests/test_pipeline.py, test_importes.py | Conservación de 240 filas, equivalencia y sumas por grupo | Verificado |
| 5. No ocultar fallos de lectura | fuentes.py; main.py | Inexistente, CSV/JSON roto, vacío y salida CLI 2 | Verificado |
| 5. Faltantes, duplicados y fuera de rango | validaciones.py; importes.py | Tests de exclusiones, duplicados y precisión/rango | Verificado; bruto distingue habilitación |
| 6. Repositorio individual Git/GitHub | Repo existente y rama tp2-echeq | Historial real desde 0f7100f; nutrición preservada por etiqueta | Verificado localmente; push se comprueba aparte |
| 6. Al menos cinco commits significativos progresivos | Historial desde tp2-entrega-v1 | Alcance; fuentes/datos; validación/importes; motor; CLI/reportes; tests; docs | Verificado; no vacíos ni reescritura |
| 6. Revisar estado y cambios antes de confirmar | Sesión de desarrollo | git status, diff, diff --cached y --check antes de cada commit | Verificado |
| 6. .gitignore apropiado | .gitignore | git check-ignore de venv/cache/outputs/local/.env | Verificado; datos sintéticos pequeños sí versionados |
| 6. Acceso docente durante evaluación | Configuración GitHub | No se conocen cuentas/visibilidad requerida por la cátedra | **Externo pendiente**, conceder acceso si privado |
| 7. Estructura equivalente y requirements | src, tests, data, docs, requirements.txt | Inventario y ejecución desde raíz | Verificado; sin terceros |
| 7. README: título/autor, problema/usuario/solución, funcionalidades/uso | README | Revisión contra lista de p. 3 del PDF | Documentado; cuenta autora identificada, nombre académico a completar |
| 7. README: fuente/licencia/unidad, instalación, comandos app/tests | README; data/README.md | pip/CLI/tests ejecutados; procedimientos exactos | Documentado y verificado |
| 7. README: código, ejemplo, limpieza, interpretación/limitaciones | README; docs/ejemplo_resumen.json | Ejemplo generado por pipeline y reglas explícitas | Documentado y verificado |
| 7. Versión evaluable y enlace | Etiqueta tp2-echeq-v1 y repositorio | git rev-parse y comprobación remota al publicar | Candidata identificada; no es entrega EVA |
| 7. Entrega, hitos y fechas EVA | README | PDF remite a EVA, no publica fechas | **Externo pendiente** |
| 7. Defensa individual y TP1 si aplica | docs/defensa.md | Guía de demo y preguntas preparada | **Externo pendiente**; no acreditada |

## Reglas funcionales y monetarias del texto ECHEQ

| Requisito | Implementación | Prueba / evidencia |
|---|---|---|
| ID exacto, importe y fecha iguales → CONCILIADO | conciliar; ChequeElectronico | test_coincidencia_exacta |
| Prefijo estricto único válido → CONCILIADO_ID_ABREVIADO | propuestas de conciliar | test_prefijo_unico_valido |
| Prefijo con varios candidatos → COINCIDENCIA_AMBIGUA | conciliar | test_prefijo_ambiguo |
| IDs inválidos/duplicados no fabrican candidato único | indexar sobre todos los códigos reconocibles | test_candidato_invalido_no_fabrica_prefijo_unico |
| Error de importe con valores y delta exacto | emparejar; detalle | test_error_importe; test_coherencia_resumen_detalle_errores_y_dos_errores |
| Comparar solo fecha_pago, mostrar ambas | ChequeElectronico.diferencias | test_error_fecha |
| Ausencias en banco y sistema | conciliar | test_ausentes_en_ambas_fuentes |
| Duplicados bloqueados, todas las ocurrencias señaladas | limpiar_registros; conciliar | test_duplicado_no_se_concilia |
| Múltiples errores en una sola fila de resultado | emparejar; Registro.errores | test_error_importe_y_fecha_simultaneos; test_multiples_errores_invalidos |
| No marcar error por emisor/endosante distinto | diferencias compara solo importe/fecha | test_emisor_y_estado_no_son_reglas_de_error |
| Correspondencia uno a uno, exactos prioritarios | conciliar; verificar_trazabilidad | test_exactos_antes_de_prefijos_y_no_reutilizacion |
| Varios prefijos compitiendo no se asignan por orden | propuestas agrupadas por fila banco | test_dos_prefijos_compiten_sin_asignacion_por_orden |
| IDs textuales, fechas reales, importes válidos | validaciones.py | Tests de campos e importes/calendario |
| Decimal, dos decimales, no float | validar_importe; importes.py; lector JSON | test_precision_decimal; test_json_numerico_decimal_sin_float |
| Total de todos los importes válidos de cada archivo | calcular_total_bruto | test_total_banco_sistema_diferencia_y_absoluta |
| Duplicados incluidos y señalados en bruto | totales_brutos.duplicados_incluidos | test_duplicados_incluidos_en_bruto_no_en_conciliado |
| Incluir importe válido aunque otro campo falle | Registro.importe independiente de cheque | test_fecha_o_id_invalidos_no_excluyen_importe_valido |
| Excluir montos inválidos con motivos y conteos | registros_excluidos_sumas | test_importes_invalidos_excluidos_y_documentados |
| Conciliados y discrepantes sin sumar dos veces | importes_por_grupo | test_conciliados_y_diferencias_sin_doble_conteo |
| Diferencia cero no implica conciliación | Separación resumen/importes/resultados | test_errores_compensados_no_son_conciliacion |
| Cuatro reportes obligatorios y columnas solicitadas | reportes.py | Tests de integración y coherencia |
| Importes JSON como cadenas exactas | decimal_json | test_monetarios_json_cadenas_y_csv_utf8_bom |
| Salidas Excel-importables, codificación/separadores documentados | escribir_csv; README | Relectura CSV automatizada, no ejecución de Microsoft Excel |
| Sin web/GUI/BD/conexiones/IA/carga manual | Arquitectura actual | Inventario: se retiró la aplicación web nutricional |

## Cobertura de los 35 casos solicitados

Los nombres corresponden a métodos ejecutados mediante unittest, no a promesas.

| Nº del texto | Caso | Test ejecutado |
|---:|---|---|
| 1 | Coincidencia exacta | test_coincidencia_exacta |
| 2 | ID abreviado válido | test_prefijo_unico_valido |
| 3 | ID abreviado ambiguo | test_prefijo_ambiguo |
| 4 | Diferencia de importe | test_error_importe |
| 5 | Diferencia de fecha | test_error_fecha |
| 6 | Ambos errores | test_error_importe_y_fecha_simultaneos |
| 7–8 | Faltante en banco / sistema | test_ausentes_en_ambas_fuentes |
| 9 | ID duplicado | test_duplicado_no_se_concilia |
| 10 | Importe negativo | test_importe_negativo |
| 11 | Importe vacío | test_importe_vacio |
| 12 | Importe no numérico | test_importe_no_numerico_o_no_finito |
| 13 | Fecha imposible | test_fecha_imposible_y_formato |
| 14 | ID inválido | test_identificador_invalido_y_cero_inicial |
| 15 | Campos faltantes | test_campos_faltantes_y_obligatorios |
| 16 | Archivo inexistente | test_archivo_inexistente |
| 17 | CSV malformado | test_csv_malformados |
| 18 | JSON malformado | test_json_malformados |
| 19 | Archivos vacíos | test_archivos_vacios |
| 20 | Equivalencia CSV/JSON | test_csv_json_equivalentes_y_ids_textuales |
| 21 | Reproducibilidad | test_reproducibilidad_de_datos_y_analisis |
| 22 | Uno a uno | test_exactos_antes_de_prefijos_y_no_reutilizacion |
| 23 | Conservación/trazabilidad | test_conservacion_de_240_registros_y_conteos |
| 24–27 | Totales banco/sistema/diferencia/absoluta | test_total_banco_sistema_diferencia_y_absoluta |
| 28 | Precisión Decimal | test_precision_decimal |
| 29 | Duplicados en bruto | test_duplicados_incluidos_en_bruto_no_en_conciliado |
| 30 | Exclusiones documentadas | test_importes_invalidos_excluidos_y_documentados |
| 31–32 | Conciliados y con diferencias | test_conciliados_y_diferencias_sin_doble_conteo |
| 33 | Cuatro reportes | test_integracion_csv_json_mixtos_y_cuatro_reportes_equivalentes |
| 34 | Resumen/detalle coherentes | test_coherencia_resumen_detalle_errores_y_dos_errores |
| 35 | Sin doble conteo indebido | test_conciliados_y_diferencias_sin_doble_conteo; test_trazabilidad_detecta_doble_uso |

## Evidencia de ejecución y balance

Python 3.12.14: `python -m unittest discover -s tests -v` ejecutó **51 pruebas,
51 aprobadas, 0 fallidas, 0 omitidas**. Los cuatro tipos de combinación CSV/JSON
produjeron los cuatro reportes idénticos byte a byte. La regeneración en una
carpeta temporal reprodujo los cuatro archivos originales.

Muestra real de salida: 120 filas por fuente; 86 pares conciliados (81 exactos,
5 abreviados); 15 pares con diferencias; 11 ausencias y 27 resultados para revisión
(incluidos tres ambiguos). Los 139 resultados trazan las 240 filas exactamente
una vez. Brutos banco/sistema: 50505628.82 / 50070182.54 ARS; diferencia 435446.28;
importe conciliado: 40522469.11. Exclusiones monetarias: banco 1, sistema 3.

Los pasos técnicos 2–5 están comprobados y el alcance/documentación de 1 y 7
están preparados. Git muestra avances reales del paso 6. La aprobación del tema,
acceso docente, datos nominales de entrega, EVA y defensa siguen siendo externos:
no se declaran cumplidos ni se presentan como defectos solucionables con código.
