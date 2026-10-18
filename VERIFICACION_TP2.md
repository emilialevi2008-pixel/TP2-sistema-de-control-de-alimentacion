# Matriz de cumplimiento — revisión individual de los siete pasos

Base revisada: PDF adjunto `consigna_TP2.pdf`, 9 páginas; siete pasos (pp. 1–3),
organización común (p. 5) y comparador de etiquetas A.9 (p. 8). El mensaje menciona
`consigna_TP2(1).pdf`; el archivo efectivamente adjuntado se llama consigna_TP2.pdf.
El texto pegado es una ampliación de alcance, no reemplaza la consigna académica.

**Estado:** implementación técnica comprobada; entrega académica no cerrada.
`Verificado` significa evidencia ejecutada o inspección concreta, no aprobación.

| Paso / requisito | Archivo o función | Estado | Evidencia / prueba | Observaciones |
|---|---|---|---|---|
| 1. Problema concreto, usuario y finalidad | README §1 | Documentado | Lectura contra p. 1 del PDF | Comparación homogénea de fichas |
| 1. Solución, operaciones, salida e interpretación | README §§1,3,5; src/main.py; src/index.html | Verificado | test_arranque_y_comparacion; Chromium | Tabla, barras y JSON |
| 1. Alcance de primera versión y exclusiones | README §§1,8; PLAN_TP2.md | Documentado | Revisión contra PDF | Núcleo A.9; recetas son extensión |
| 1. Aprobación del tema propio de recetas | README §§1,8 | **Pendiente externo** | No hay evidencia de aprobación | No se presume; presentar núcleo de etiquetas o confirmar adaptación |
| 2. Fuente, URL/procedimiento, responsable, licencia y consulta | data/README.md | Documentado | Descarga por Git de revisión 4aa1cd1…; preparar_datos.py | API directa bloqueada; datos incluidos offline |
| 2. Unidad de análisis y variables/unidades | data/README.md | Documentado | Diccionario de 11 campos | Ficha por alimento/producto |
| 2. Al menos 50 observaciones y 3 variables | data/productos.csv y .json | Verificado | test_equivalencia_csv_json_y_repetibilidad | 65 fichas válidas, 4 nutrientes; 60 genéricos + 5 etiquetas |
| 2. Muestra conservada y obtención reproducible | data/; scripts/preparar_datos.py | Verificado | Extracción ejecutada dos veces; archivos equivalentes | Selección y revisión exactas documentadas |
| 2. Limitaciones, sesgos, restricciones y privacidad | data/README.md; .gitignore | Documentado | Inspección de datos y archivos versionados | Sin información personal; procedencia no clínica |
| 3. Lectura CSV/JSON definidos y equivalentes | src/fuentes.py | Verificado | test_equivalencia_csv_json_y_repetibilidad; test_errores_lectura_no_ocultos | JSON lista de objetos; CSV cabecera |
| 3. Inspección y validación del esquema | validar_esquema; ejecutar | Verificado | test_esquema_invalido; test_equivalencia_csv_json_y_repetibilidad | Resultado informa columnas y conteos |
| 3. Limpieza/transformación y registro de filas | normalizar_ficha; limpiar_datos | Verificado | test_auditoria_y_no_mutacion; test_todas_rechazadas_se_exportan | Originales, cambios, faltantes y motivos en JSON |
| 3. Análisis, resultado útil y comunicación | comparar_etiquetas; guardar_resultado; web | Verificado | test_diferencias_y_orden; test_exportacion; Chromium | 100 g, kcal y g; selección vacía explícita |
| 3. Comando único y reproducción coherente | src/main.py; README §3 | Verificado | Dos ejecuciones CLI; test_equivalencia_csv_json_y_repetibilidad | Sin orden oculto ni acceso online necesario |
| 4. Funciones con responsabilidades diferenciadas | src/fuentes.py, pipeline.py, recetas.py | Verificado | Pruebas unitarias separadas por operación | Lectura, validación, selección, cálculo y exportación |
| 4. Clase significativa del dominio | ProductoNutricional | Verificado | test_conversion_conocida_y_base; test_caso_normal | Atributos y métodos de conversión/ficha |
| 4. Clase base y dos implementaciones | FuenteDatos, FuenteCSV, FuenteJSON | Verificado | test_fuente_abstracta; test_equivalencia_csv_json_y_repetibilidad | Contrato cargar(ruta), usado por la aplicación |
| 4. Regex pertinente y justificación | EAN y CIQUAL; README §4 | Verificado | test_invalidos_y_rangos; test_caso_normal | EAN 8/13 ASCII; no comprueba dígito de control |
| 4. Supuestos y errores comprensibles | numero, validar_producto; main | Verificado | test_invalidos_y_rangos; test_limites_de_filtro_invalidos | Finitos, base, tipo, unidades y límites |
| 5. Caso normal ejecutable | tests/test_pipeline.py | Verificado | test_caso_normal | Conserva código y calcula energía |
| 5. Entrada inválida/límite | tests/test_pipeline.py | Verificado | test_invalidos_y_rangos; test_receta_invalida | 16 variantes en subtests de fichas |
| 5. Propiedad relevante del resultado | tests/test_pipeline.py | Verificado | test_duplicados_y_conservacion; test_equivalencia_csv_json_y_repetibilidad | Conservación de filas y equivalencia entre formatos |
| 5. No ocultar errores de lectura | fuentes.py, main.py | Verificado | test_errores_lectura_no_ocultos | Archivo ausente, JSON roto, formato no admitido |
| 5. Faltantes explícitos | modelos.py; limpiar_datos | Verificado | test_faltante_no_es_cero; test_receta_calculo_y_faltantes | Null/N/D, nunca cero imputado |
| 5. Duplicados explícitos | limpiar_datos | Verificado | test_duplicados_y_conservacion | Primera ficha válida por código |
| 5. Fuera de rango explícito | validar_producto | Verificado | test_invalidos_y_rangos | Energía/macro normalizados y finitos |
| 6. Git individual en GitHub desde inicio | Repositorio existente, commit inicial 0f7100f | Verificado localmente | git log; remoto existente | Desarrollo asistido declarado |
| 6. Al menos 5 commits significativos progresivos | Historial Git | Verificado | git log --oneline --reverse | Etapas reales: alcance, datos, pipeline, recetas, web, tests, docs |
| 6. Revisión antes de confirmar | Sesión de desarrollo | Verificado | git status, git diff y diff --cached previos | No commits vacíos ni historial retroactivo |
| 6. .gitignore apropiado | .gitignore | Verificado | git status --ignored | Ignora venv, cachés, secretos, outputs y SQLite personal |
| 6. Acceso de la cátedra | Ajustes GitHub | **Pendiente externo** | No se conocen cuentas docentes ni visibilidad requerida | Conceder acceso si privado y comprobar con la cátedra |
| 7. Estructura equivalente y requirements.txt | src/, tests/, data/, docs/ | Verificado | Inventario del repositorio | Solo biblioteca estándar obligatoria |
| 7. README con todos los apartados | README §§1–8 | Documentado | Revisión contra lista de p. 3 | Título, cuenta autora, problema, uso, fuentes, instalación, código, ejemplo, limpieza, límites |
| 7. Autor identificado por nombre académico | README encabezado | **Confirmación pendiente** | Cuenta GitHub identificada | No se inventa nombre completo; completar para entrega formal |
| 7. Versión evaluada identificada | etiqueta tp2-entrega-v1 | Candidata identificada | git rev-parse tp2-entrega-v1^{commit} | La etiqueta se crea sobre documentación revisada |
| 7. Entrega, hitos y fechas EVA | README §8 | **Pendiente externo** | PDF remite a EVA; sin fechas concretas | No se afirma entrega realizada |
| 7. Defensa individual y recuperación TP1 si aplica | docs/DEFENSA.md | **Pendiente externo** | Guía y comandos preparados | La exposición no puede automatizarse |
| A.9. Buscar código, categoría o grupo | buscar_producto; seleccionar; interfaz | Verificado | test_busqueda_y_filtros; Chromium | Categoría exacta, múltiples por producto |
| A.9. Normalizar campos anidados y unidades | preparar_datos.py; ProductoNutricional | Verificado | Extracción OFF ejecutada; test_conversion_conocida_y_base | Esquema interno plano documentado |
| A.9. Código con cero inicial | lectores/modelo | Verificado | test_caso_normal | Se rechazan códigos numéricos JSON |
| A.9. Nutriente desconocido no disponible | modelos.py; interfaz | Verificado | test_faltante_no_es_cero | Comparación/diferencia N/D |
| Ampliación: recetas personales, edición, borrado y persistencia | recetas.py; web.py; index.html | Verificado | test_crud_persistente; test_crud_http; Chromium | Estimaciones por masa, no etiquetas certificadas |
| Ampliación: tablas, gráficos, filtros y exportación | index.html | Verificado | scripts/verificar_web.py | Energía con barras, macronutrientes en tabla |
| Ampliación: colección de recetas reales con ingredientes/cantidades verificables | No implementada | **Pendiente de ampliación** | Catálogo contiene fichas CIQUAL, no recetas desglosadas | No exigida por PDF; no presentar como cumplida |

## Evidencia resumida de ejecución

Python 3.12.14. `python -m unittest discover -s tests -v`: **24 pruebas, OK**,
sin omisiones. Playwright 1.62.0 + Chromium: catálogo, filtros, selección,
comparación, descarga, CRUD, persistencia, entrada inválida, ancho móvil y cero
errores JS comprobados con `python scripts/verificar_web.py`.
CLI CSV/JSON: 65 entradas, 65 válidas, 0 rechazadas; las normalizaciones quedan
registradas. Los rechazos se verifican mediante fixtures explícitos en tests.
La primera corrida de tests detectó una discrepancia de serialización en la
auditoría, corregida y comprobada sin relajar las aserciones.

## Balance por paso

1. Problema y alcance documentados; tema propio de recetas sin aprobación confirmada.
2. Datos y procedencia documentados; mínimo de observaciones cumplido con catálogo mixto.
3. Flujo reproducible comprobado con ambos formatos y auditoría.
4. Conceptos de programación implementados y comprobados.
5. Calidad comprobada mediante 24 pruebas y navegador.
6. Historial y configuración local comprobados; acceso docente requiere confirmación.
7. Documentación y versión candidata preparadas; nombre formal, entrega y defensa pendientes.

No se declara el proyecto académicamente finalizado mientras estén pendientes
esas condiciones externas o se mantenga como obligatorio el catálogo adicional
de recetas del texto adjunto. Esta matriz distingue implementación, documentación,
publicación remota y aceptación académica.
