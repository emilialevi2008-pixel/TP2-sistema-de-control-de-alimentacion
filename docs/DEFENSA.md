# Guía de demostración y defensa individual

1. Explicar el problema de comparar bases y faltantes; distinguir etiqueta y
   alimento genérico. Identificar las dos fuentes y sus limitaciones/licencias.
2. Ejecutar `python -m src.main --codigos 3023290234839 3175681213081`.
   Abrir outputs/resultado.json e incidencias.json. Mostrar base y unidades.
3. Ejecutar la misma operación con `--entrada data/productos.json`. Explicar por
   qué la equivalencia y la prueba de repetibilidad protegen el flujo.
4. Mostrar FuenteDatos y las dos implementaciones; justificar la interfaz común.
5. Explicar ProductoNutricional, kJ/4.184, mg/1000 y transformación a 100 g.
   No confundir normalización de unidades con estimar nutrientes faltantes.
6. Mostrar test_conversion_conocida_y_base, test_faltante_no_es_cero y la prueba
   de duplicados. Ejecutar `python -m unittest discover -s tests -v`.
7. Iniciar `python -m src.web`. Filtrar etiquetas y comparar dos. Añadir una receta
   con 200 g de CIQ-25001 y dos porciones; mostrar que cada porción son 100 g.
   Explicar que la estimación supone suma de masas sin cocción. Editar y borrar.
8. Mostrar el historial (`git log --oneline --reverse`) y la etiqueta evaluable.

Preguntas para estudiar:
- ¿Por qué no convertir un dato desconocido a cero ni una base en ml a gramos?
- ¿Por qué una regex EAN no comprueba el dígito de control?
- ¿Por qué conservar la primera ficha válida y registrar la segunda como rechazo?
- ¿Qué hace cada función y qué ocurriría ante JSON roto o un archivo inexistente?
- ¿Qué sesgo introduce elegir solo filas CIQUAL con nutrientes completos?
- ¿Qué diferencias existen entre las tablas por 100 g, por porción y totales?
- ¿Qué autoriza la licencia de cada fuente y cómo se conserva atribución?

La estudiante debe poder modificar y explicar el código. No hay evidencia de
aprobación del tema propio de recetas ni de aceptación del uso de asistencia;
confirmar las reglas de la cátedra. Si corresponde recuperación de TP1, preparar
sus contenidos: este proyecto no sustituye esa instancia.
