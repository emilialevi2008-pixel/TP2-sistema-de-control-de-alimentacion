# Guía de defensa individual ECHEQ

## Demostración breve

1. Presentar problema/usuario y aclarar: son datos sintéticos, no cheques reales.
   Mostrar data/README.md y el generador con su semilla. Explicar aprobación pendiente.
2. Ejecutar desde la raíz:
   `python -m src.main --banco data/banco.csv --sistema data/sistema.csv --desde 01/11/2026 --hasta 31/12/2026 --salida outputs/demo`.
3. Leer el resumen: banco 50.477.968,91; sistema 50.070.182,54; diferencia 407.786,37.
   Explicar que bruto incluye duplicados válidos y montos de filas con otros errores.
4. Abrir reporte_conciliacion.csv con separador `;` y UTF-8. Mostrar:
   - un CONCILIADO_ID_ABREVIADO y su ID completo;
   - CON_DIFERENCIAS con ambos errores, importes/fechas y filas;
   - ID_DUPLICADO, un ambiguo con candidatos y una exclusión de suma en resumen.json.
5. Ejecutar con JSON y luego formatos combinados. Explicar por qué los mismos
   datos deben producir reportes idénticos; mostrar la prueba de equivalencia.
6. Ejecutar `python -m unittest discover -s tests -v` (65 pruebas).
   Mostrar precisión 0.10+0.20=0.30 y errores compensados con saldo global cero.
7. Mostrar FuenteDatos/FuenteCSV/FuenteJSON, ChequeElectronico y métodos del modelo.
   Explicar normalización, cálculo y exportación separados de los lectores.
8. Mostrar `git log --oneline --reverse tp2-entrega-v1..tp2-echeq` y
   `git rev-parse 'tp2-echeq-v2^{commit}'`. Aclarar que main no es necesariamente
   la versión evaluable y que la entrega debe identificar rama/etiqueta.

## Preguntas para estudiar y responder con el código

- ¿Por qué Decimal y no float? ¿Qué pasa con 0.10+0.20 en binario?
- ¿Por qué no redondear sin aviso 1.005 ni aceptar separadores de miles ambiguos?
- ¿Por qué un importe válido de una fila con fecha imposible se excluye antes del bruto del período?
- ¿Cómo se distingue un dato faltante de cero y dónde aparece la exclusión?
- ¿Por qué duplicados entran en bruto pero no se concilian automáticamente?
- ¿Qué prueba demuestra que una fila bancaria no se usa dos veces?
- ¿Cómo se resuelven dos prefijos que compiten? ¿Por qué no elegir el primero?
- ¿Por qué considerar IDs de filas inválidas al evaluar unicidad de prefijos?
- ¿Qué hace la regex y qué comprobación de calendario agrega datetime?
- ¿Por qué no comparar emisor/endosante? ¿Qué campo de fecha se compara?
- ¿Por qué dos errores del mismo cheque no duplican su importe ni su conteo?
- ¿Cómo se reconcilian 137 resultados más dos exclusiones con 240 filas físicas?
- ¿Qué significa cada clase y qué beneficio aporta la abstracción de fuentes?
- ¿Dónde se preserva el original y qué limitaciones tienen los datos sintéticos?

Comprender, ejecutar y poder modificar el código. Esta guía no sustituye la
exposición individual. Si corresponde recuperación del TP1, preparar sus temas
según las indicaciones de la cátedra; este repositorio no acredita esa instancia.

## Demostración de fechas y selección libre

Ejecutar sin --desde/--hasta y responder el inicio y el final en DD/MM/AAAA.
Repetir con otro período, incluso entre dos años. Mostrar que los límites son
inclusivos y que no se conserva la selección anterior. Explicar por qué una fecha
ilegible queda registrada fuera de los totales y por qué los valores originales
no se reescriben en la auditoría. Mostrar el test de seriales Excel y la opción
1904 para fuentes que usen ese sistema; no se adivina a partir del número.
