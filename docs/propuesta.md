# Propuesta para aprobación: conciliador ECHEQ

**Autora/titular:** Emilia Agustina Levi (cuenta emilialevi2008-pixel).
**Materia:** Programación Orientada a Datos, TP2 individual, UCA.

## Problema y usuario

Personal contable de pymes compara archivos bancarios y contables con errores,
ausencias, duplicados e IDs abreviados. Necesita encontrar diferencias concretas
y explicar por qué no coincide el total de cada archivo.

## Solución y operaciones

Aplicación pequeña de consola en Python, sin conexión bancaria, que pide un
período libre (DD/MM/AAAA, ambos días incluidos) y lee dos
archivos CSV/JSON, valida y registra limpieza, concilia exactos/prefijos únicos,
calcula importes exactos y genera cuatro reportes más resumen terminal.
Los ambiguos/duplicados se conservan para revisión, sin adjudicación arbitraria.

## Datos y salida verificable

120 registros sintéticos por fuente, cinco variables: id_cheque, importe (ARS),
fecha_pago (DD/MM/AAAA, ISO o Excel), emisor y estado. Semilla 20261018; procedimiento versionado,
CC0 1.0; ninguna información sensible. Cada fila de origen conserva su ordinal.
La salida permite demostrar coincidencias, múltiples errores, ausencias,
precisión decimal y diferencia entre saldo bruto y monto conciliado.

## Alcance académico

Se cubren los siete pasos: problema, procedencia, flujo, funciones/clases/regex,
pruebas ejecutables, Git y documentación/entrega. No habrá web, GUI, BD, IA,
autenticación ni edición manual. Es tema propio: se solicita su evaluación por
la cátedra. **No hay evidencia de aprobación todavía.**
Las fechas, hitos y medio de entrega se consultan en EVA; no están en el PDF.
