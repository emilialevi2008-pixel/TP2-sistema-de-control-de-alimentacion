# Reemplazo de tema: conciliador de cheques electrónicos

Se reemplaza el comparador nutricional por un conciliador ECHEQ de consola,
por instrucción explícita de la usuaria. La versión anterior queda preservada
por `tp2-entrega-v1` y la rama remota `tp2-comparador-nutricional`.
Se revisaron las nueve páginas de consigna_TP2.pdf: los siete pasos siguen siendo
la referencia académica. El nuevo texto pegado termina truncado en la sección
14 (`docs: definir problema y`); sus requisitos legibles se aplican completos.

## Problema, usuario y solución

Personal contable de una pyme necesita cotejar registros bancarios y contables.
Se cargarán dos archivos CSV/JSON, se validarán/normalizarán filas, se conciliarán
IDs exactos o prefijos únicos y se exportarán cuatro reportes y un resumen de
terminal. Los datos serán sintéticos, deterministas y sin información sensible.

## Decisiones a verificar

- Importes Decimal, dos decimales; no float ni tolerancias monetarias implícitas.
- Totales brutos: incluir importes válidos incluso con otros campos inválidos o
  IDs duplicados. Excluir negativos, faltantes, no finitos o no numéricos y
  documentar cada exclusión. No confundir suma bruta con conciliada.
- Cada fila física tendrá exactamente una referencia principal en el detalle,
  sola o emparejada con una fila de la otra fuente. Candidatos no son matches.
- Coincidencias exactas tienen prioridad; duplicados y contrapartes inválidas se
  bloquean. Los prefijos se evalúan sobre todos los IDs bancarios reconocibles,
  incluidos los no utilizables; no filtrar para fabricar una coincidencia única.
- Prefijos que compiten por la misma fila bancaria no se asignan por orden.
- Comparar fecha_pago e importe; no producir error por emisor/estado distintos.
- CLI exclusivamente: sin web, GUI, base de datos, cuentas ni conexiones bancarias.

## Etapas de desarrollo

1. Reemplazo y alcance; 2. fuentes y datos; 3. validación y totales;
4. motor de conciliación; 5. CLI y reportes; 6. pruebas; 7. documentación/entrega.
Revisar git status y git diff antes de cada commit real. Ejecutar casos normales,
inválidos, propiedades, formatos combinados e integración; auditar los siete pasos.

## Dependencias externas

ECHEQ es un tema propio: la aprobación de la cátedra no está confirmada.
Acceso docente, nombre académico de autoría, reglas sobre asistencia, fecha y
entrega EVA y defensa individual requieren confirmación fuera del programa.
No inventar aprobación, publicación ni pruebas realizadas.
