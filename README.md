# Mesa — Comparador de etiquetas nutricionales y alimentos

**Autoría / titular del repositorio:** `emilialevi2008-pixel`.
Desarrollo asistido por Codex. La estudiante debe verificar su nombre académico,
las reglas de asistencia de la cátedra y poder explicar y defender el código.
No se atribuye aquí una defensa realizada ni aprobación docente.

Versión candidata evaluable: etiqueta Git **`tp2-entrega-v1`**. El commit exacto se
obtiene con `git rev-parse tp2-entrega-v1^{commit}`. No implica entrega en EVA.

## 1. Problema, usuario, solución y alcance

Comparar fichas con bases o unidades distintas puede producir conclusiones
incorrectas; confundir un nutriente faltante con cero agrava el problema.
Una persona que consulta etiquetas puede buscar productos, seleccionar categorías
o códigos y obtener una tabla homogénea por 100 gramos, con diferencias absolutas.
La salida distingue alimentos genéricos de etiquetas comerciales y conserva N/D.

El núcleo adapta el apéndice A.9 del PDF TP2 (comparador de etiquetas), con una
extensión de alimentos CIQUAL para disponer de una muestra de 65 observaciones.
El tema original de recetas **no tiene aprobación acreditada**. La extensión de
recetas personales no sustituye ese núcleo y requiere confirmar su aceptación si
se presenta como tema propio. No se presupone esa aprobación.

Primera versión: consola reproducible y web local; catálogo, búsquedas, selección
por categoría, filtros nutricionales, comparación, gráfico de barras, exportación
y recetas personales estimadas con CRUD persistente. Fuera de alcance: diagnóstico
clínico, ranking de salud, cuentas de usuario, despliegue público, densidades,
correcciones por cocción y actualización automática de etiquetas.

## 2. Datos, fuente y condiciones de uso

65 fichas incluidas en CSV y JSON equivalentes: **60 alimentos CIQUAL 2020** de
ANSES (Licence Ouverte/Etalab) y **5 etiquetas** de Open Food Facts y colaboradores
(ODbL/DbCL). Unidad de análisis: una ficha de alimento o de producto; no una persona
ni una observación de consumo. Consulta: 2026-10-17.

La procedencia, URLs, revisión Git de origen, selección, responsables, licencias,
diccionario de las 11 variables, unidades, reproducción del extracto, restricciones
y sesgos están en [data/README.md](data/README.md). No se simularon valores.
Los códigos CIQ son internos; no se fabricaron EAN para los alimentos genéricos.
El conjunto es una muestra de conveniencia, no 65 etiquetas ni 65 recetas.

## 3. Instalación y ejecución

Requiere Python **3.11 o superior** (probado en 3.12.14). Sin servicios externos,
secretos ni dependencias de terceros. Desde la raíz del repositorio:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main --entrada data/productos.csv --salida outputs
python -m src.main --entrada data/productos.json --salida outputs/json
python -m unittest discover -s tests -v
```

En Windows se puede activar con `.venv\Scripts\activate`.
El entorno virtual es opcional porque se usa la biblioteca estándar.
No hay compilación ni generación de código requeridas.

### Consola: búsqueda, selección y comparación

```sh
python -m src.main --codigos 3023290234839 3175681213081 --salida outputs/comparacion
python -m src.main --tipo etiqueta
python -m src.main --categoria 'mixed salads'
python -m src.main --texto salad --max-energia 200 --min-proteinas 2
python -m src.main --help
```

`--codigos` conserva texto y ceros iniciales. La búsqueda por códigos ausentes
falla con mensaje y código de salida 2. Una categoría sin coincidencias produce
tabla vacía y mensaje explícito en el resultado. Los filtros de categoría usan
pertenencia exacta entre las categorías separadas por `|`, sin inferir jerarquías.

Salidas: `resultado.json` (inspección, tabla, unidades y auditoría) e
`incidencias.json` (filas modificadas/rechazadas, originales, cambios y motivos).
La numeración de filas empieza en 1 para el primer registro, sin contar cabecera.
Se sobrescriben las salidas de la misma carpeta; usar otra carpeta para conservar
una corrida. Las salidas de ejecución no se versionan.

### Interfaz web y recetas personales

```sh
python -m src.web --puerto 8000
```

Usar un navegador local en el puerto 8000 del servidor; en un entorno remoto se
necesita un mecanismo de acceso al puerto de esa plataforma. Este onboarding no
ofrece una vista previa web. No se ha realizado un despliegue público.
`--host`, `--puerto`, `--entrada` y `--almacen` permiten configurar el servidor.
Detener con Ctrl+C; reiniciar con el mismo comando conserva las recetas.

1. Buscar por nombre o código; filtrar por tipo, categoría, energía o proteína.
2. Marcar dos o más fichas y pulsar **Comparar selección**. Las tablas y las barras
   usan 100 g; descargar el resultado con **Descargar comparación JSON**.
3. En **Mis recetas**, ingresar nombre y porciones. Seleccionar alimentos y gramos
   y añadir ingredientes. También se pueden editar líneas `codigo,gramos` con
   punto decimal. Guardar, editar y eliminar mediante los botones de cada ficha.
4. Las recetas se pueden seleccionar junto con los alimentos para comparar por
   100 g. Las fichas de recetas también muestran masa por porción, energía por
   porción y nutrientes totales. Volver a comparar después de una edición.

Las entradas personales se guardan en `local/recetas.sqlite`, ignorado por Git;
los CSV/JSON originales no se alteran. Copiar ese archivo preserva los datos
personales; el servidor es para uso local y no incorpora cuentas/autenticación.

## 4. Flujo, diseño y decisiones de limpieza

`leer → inspeccionar/validar → limpiar/transformar → analizar → comunicar`.

- `FuenteDatos.cargar(ruta)` define el contrato; `FuenteCSV` y `FuenteJSON` dan una
  lista de diccionarios. Fallos de lectura/esquema se informan, no se ocultan.
- `validar_esquema` exige las 11 columnas. `normalizar_ficha` limpia espacios,
  convierte coma decimal y categorías; `validar_producto` comprueba tipo, código,
  base, unidades y rangos; `limpiar_datos` registra cada fila afectada.
- `ProductoNutricional` reúne atributos y el comportamiento `nutriente_100g` y
  `ficha(porcion_g)`. No se usa una clase por formalidad: centraliza la conversión.
- `indexar_productos`, `buscar_producto`, `seleccionar`, `comparar_etiquetas` y
  `guardar_resultado` separan búsqueda, selección, cálculo y presentación.
- La regex `(?:[0-9]{8}|[0-9]{13})`, mediante `fullmatch`, valida el alcance EAN de
  etiquetas y excluye dígitos Unicode y longitudes distintas. **No valida el dígito
  de control ni la existencia comercial**. `CIQ-[0-9]+` identifica alimentos ANSES.
- Vacío/null significa desconocido; se conserva como `None`/JSON null y se muestra
  N/D. No se imputa cero. Categoría ausente se registra como `sin-categoria`.
- Se rechazan códigos mal formados, campos obligatorios faltantes, no finitos,
  bases no positivas, unidades incompatibles y valores fuera de rango por 100 g:
  energía 0–1000 kcal y cada macronutriente 0–100 g. Son límites de plausibilidad,
  no certificación de exactitud. No se impone 4P+4C+9G exacto por fibra y redondeos.
- Duplicados: se conserva la primera ficha **válida** por código; los siguientes
  registros se rechazan, aunque difieran. No se suman ni promedian fichas.
- Conversión: `valor × 100/base_g`; kJ/4.184 → kcal, mg/1000 → g. No se convierte
  volumen a masa. Se ordena por código y se redondea a seis decimales al presentar.
- Una receta suma `nutriente_100g × gramos/100`; divide por porciones o masa total.
  Si un ingrediente no conoce un nutriente, el total de ese nutriente es N/D.
  No se incluyen pérdidas, evaporación, rendimiento ni cocción: es una estimación.

## 5. Ejemplo e interpretación

Comparación generada con los códigos del primer ejemplo:

| Ficha | kcal/100 g | Proteínas g | Carbohidratos g | Grasas g |
|---|---:|---:|---:|---:|
| La Laitière Yaourt au lait entier nature | 67 | 3.9 | 4.8 | 3.3 |
| Tostadas crujientes de cereales y semillas | 365 | 7.1 | 76 | 2.1 |

Diferencia absoluta de energía: **298 kcal por 100 g**. La diferencia no significa
que un alimento sea mejor: las porciones, finalidad y categorías son distintas.
Una comparación por marca debería seleccionar etiquetas de la misma categoría.
El [ejemplo JSON](docs/ejemplo_resultado.json) fue generado por el pipeline.
N/D indica falta de información, no ausencia del nutriente.

## 6. Organización y tecnologías

```text
README.md, PLAN_TP2.md, VERIFICACION_TP2.md, requirements.txt, .gitignore
src/
  fuentes.py       interfaz abstracta y lectores CSV/JSON
  modelos.py       ProductoNutricional y conversiones
  pipeline.py      inspección, limpieza, selección, análisis, exportación
  recetas.py       cálculo por ingredientes y persistencia SQLite
  main.py          argumentos y ejecución reproducible
  web.py           servidor HTTP y API
  index.html       interfaz adaptable, tablas y barras
scripts/
  preparar_datos.py    adaptación de CIQUAL y campos anidados OFF
  verificar_web.py    comprobaciones en navegador real
 tests/               pruebas unittest de lógica y HTTP
 data/                CSV, JSON y documentación de procedencia
 docs/                resultado de ejemplo y guía de defensa
 outputs/             generados, ignorados
 local/               recetas personales, ignoradas
```

Python estándar (`csv`, `json`, `re`, `abc`, `dataclasses`, `sqlite3`, `http.server`,
`unittest`); HTML/CSS/JavaScript sin CDN. Requisitos de ejecución en requirements.

## 7. Pruebas y calidad

```sh
python -m unittest discover -s tests -v
```

Resultado verificado: **24 pruebas pasaron, 0 fallidas, 0 omitidas**.
Incluyen caso normal, inválidos/rangos, conversión conocida, ceros iniciales,
faltantes, duplicados, auditoría, conservación de filas, equivalencia CSV/JSON,
repetibilidad, exportación, filtros y CRUD persistente, más peticiones HTTP reales.
Los valores artificiales dentro de tests son fixtures de prueba, no fuentes del
catálogo. Se corrigieron discrepancias de tipos CSV/JSON y de serialización de la
auditoría detectadas durante el desarrollo.

Comprobación adicional opcional de navegador (no necesaria para ejecutar la app):
Playwright 1.62.0 y Chromium instalado en `/usr/bin/chromium`:

```sh
python -m pip install playwright==1.62.0
python scripts/verificar_web.py
```

Ejecutada satisfactoriamente: filtros, comparación, descarga, CRUD, persistencia
tras recarga, errores, ausencia de errores JS y ancho móvil 390 px. Si Chromium
no está instalado, este chequeo adicional requiere instalarlo con el administrador
de paquetes del sistema; las 24 pruebas estándar no lo requieren.

## 8. Límites, pendientes académicos y entrega

La muestra no es representativa; OFF proviene de fixtures históricos y CIQUAL
contiene valores medios de preparaciones. Los 60 alimentos no son etiquetas ni
recetas desglosadas. **No se implementó una colección de recetas reales con
ingredientes/cantidades de fuente verificable**: se priorizó la consigna sobre esa
ampliación del texto adjunto. Sí funciona el CRUD de recetas estimadas personales.
Si se exige ese catálogo adicional o 50 etiquetas comerciales, ampliar las fuentes
antes de declarar terminado ese alcance. No se reduce este punto a una simulación.

La matriz [VERIFICACION_TP2.md](VERIFICACION_TP2.md) revisa individualmente los siete
pasos. No se declara el TP aprobado ni entregado: faltan confirmación de acceso de
la cátedra, nombre académico definitivo, reglas de asistencia, tema propio si se
mantiene recetas como tema principal, fechas/medio EVA y defensa individual.
El PDF no publica fechas concretas; se consultan en EVA. Recuperación TP1 solo si
corresponde según la situación académica de la estudiante.

El historial incluye avances reales con revisión de `git status` y `git diff`
antes de confirmar, sin commits vacíos ni historia retroactiva. Ver:

```sh
git log --oneline --reverse
git show tp2-entrega-v1 --stat
git status --short
```

Repositorio: https://github.com/emilialevi2008-pixel/TP2-sistema-de-control-de-alimentacion
Entregar ese enlace y la etiqueta `tp2-entrega-v1` mediante EVA según indique la
cátedra. Asegurar visibilidad pública o conceder acceso docente si es privado.
La guía [docs/DEFENSA.md](docs/DEFENSA.md) prepara una demostración y preguntas;
leerla no sustituye comprender y defender personalmente el trabajo.
