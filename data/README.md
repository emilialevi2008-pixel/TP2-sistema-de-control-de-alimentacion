# Procedencia y diccionario

Consulta/descarga: 2026-10-17 (fecha del cliente). No se consultó la API en vivo:
la red rechazó la petición HTTPS. Se usó el proxy Git existente, sin credenciales
nuevas. Los valores NO se simularon.

Repositorio intermediario: https://github.com/openfoodfacts/openfoodfacts-server
Revisión exacta: `4aa1cd198d8e4cfea762f9b59e23860200bd60ab`.

1. **60 alimentos CIQUAL 2020**, responsable ANSES, Francia.
   Fuente original: https://ciqual.anses.fr/ . Condiciones: Licence Ouverte / Open
   Licence Etalab (https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
   Copia utilizada: `external-data/ciqual/ciqual/CIQUAL2020_ENG_2020_07_07.csv`
   en el repositorio intermediario y revisión anterior. Se conservan las primeras
   60 filas en orden de origen con energía y tres macronutrientes numéricos exactos.
   No se convierten límites `< x` a valores exactos ni se imputan desconocidos.
   Los identificadores `CIQ-...` son códigos internos de alimentos, **no EAN**.
2. **5 fichas de etiquetas** de Open Food Facts, responsable Open Food Facts y
   colaboradores, https://world.openfoodfacts.org/ . Base ODbL 1.0,
   contenido individual Database Contents License:
   https://opendatacommons.org/licenses/odbl/1-0/ y
   https://opendatacommons.org/licenses/dbcl/1-0/ . Se mantiene atribución y la
   porción derivada de la base bajo ODbL; no se incluyen imágenes.
   Copia: `tests/integration/inputs/madenearme/openfoodfacts-products.jsonl.gz`
   en la misma revisión. Se excluye la leche líquida (no se supone densidad 1).
   Son fixtures upstream: pueden estar desactualizados, no equivalen a una
   verificación actual de la etiqueta del fabricante. El código enlaza la ficha:
   `https://world.openfoodfacts.org/product/<codigo>`.

Unidad de análisis: una ficha por alimento genérico o producto etiquetado. No
mezclar ambos tipos al inferir diferencias entre marcas; usar `--tipo etiqueta`.
Las 65 observaciones permiten un catálogo mixto y cálculos sobre alimentos; solo
5 son etiquetas comerciales. La muestra no es representativa de un mercado.
No se afirma disponer de 50 etiquetas ni de 50 recetas con ingredientes.

CSV UTF-8 con encabezado; JSON lista de objetos con los mismos campos y valores.
`codigo`: texto; `nombre`: denominación original; `categorias`: etiquetas separadas
por `|` (selección por pertenencia exacta, sin inferir jerarquías); `tipo`:
`alimento` o `etiqueta`; `base_g`: masa a la que refieren los nutrientes;
`energia`, `unidad_energia` (kcal/kJ); `proteinas`, `carbohidratos`, `grasas`,
`unidad_masa` (g/mg). Los archivos preparados tienen base 100 g y kcal/g.
Vacío o null representa desconocido, nunca cero. La aplicación acepta otras
bases de masa positivas y transforma a 100 g; no acepta base volumétrica.

## Reproducción del extracto

Con Git y Python, desde la raíz del proyecto (los datos incluidos bastan offline):

```sh
git clone --filter=blob:none --no-checkout https://github.com/openfoodfacts/openfoodfacts-server.git /tmp/tp2-fuentes
git -C /tmp/tp2-fuentes show 4aa1cd198d8e4cfea762f9b59e23860200bd60ab:external-data/ciqual/ciqual/CIQUAL2020_ENG_2020_07_07.csv > /tmp/tp2-ciqual.csv
git -C /tmp/tp2-fuentes show 4aa1cd198d8e4cfea762f9b59e23860200bd60ab:tests/integration/inputs/madenearme/openfoodfacts-products.jsonl.gz > /tmp/tp2-off.gz
python scripts/preparar_datos.py /tmp/tp2-ciqual.csv /tmp/tp2-off.gz data
```

Limitaciones: exclusión de faltantes al seleccionar CIQUAL introduce sesgo de
completitud; valores medios y redondeos no describen una receta personal. No
hay trazabilidad de ingredientes o rendimiento de cocción: no se inventan.
Los datos no son consejo clínico ni una calificación integral de salud.
