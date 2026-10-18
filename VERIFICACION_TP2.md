# Verificación TP2 — conciliador ECHEQ

La [matriz completa](docs/cumplimiento_consigna.md) identifica cada requisito,
archivo/función, prueba y observación. Incluye los siete pasos del PDF y los
35 casos del texto ECHEQ. No es la matriz del proyecto nutricional anterior.

| Paso evaluable | Balance | Evidencia principal |
|---|---|---|
| 1. Problema y alcance | Preparado; aprobación de tema propio pendiente | README y docs/propuesta.md |
| 2. Datos y procedencia | Documentado y verificado | 120 filas por fuente, cinco variables, generación reproducible, data/README.md |
| 3. Flujo reproducible | Verificado | CLI CSV, JSON y ambos formatos mixtos; cuatro reportes equivalentes |
| 4. Programación | Verificado | Funciones, ChequeElectronico, FuenteDatos/CSV/JSON, regex y calendario |
| 5. Calidad y pruebas | Verificado | 51 pruebas aprobadas, 0 fallidas/omitidas; trazabilidad y precisión Decimal |
| 6. Git/GitHub | Avances reales versionados; acceso docente por confirmar | Historial progresivo ECHEQ; .gitignore; verificación remota al publicar |
| 7. Documentación, entrega y defensa | Documentación y candidata preparadas; entrega/defensa pendientes | README, guía de defensa y etiqueta tp2-echeq-v1 |

Resultado de la muestra: banco **50505628.82 ARS**, sistema **50070182.54 ARS**,
diferencia **435446.28 ARS**, monto conciliado **40522469.11 ARS**.
86 pares conciliados, 15 con diferencias, 11 ausencias y 27 resultados para revisión.

Versión evaluable: **tp2-echeq-v1**. Identificar su SHA con
`git rev-parse 'tp2-echeq-v1^{commit}'`; no usar tp2-entrega-v1, que es nutricional.
No se afirma aprobación de la cátedra, entrega en EVA ni defensa realizadas.
