# KAN-16 — Casos de prueba

Ejecución local: 29/10/2026, America/Santiago.

## Matriz de trazabilidad

| Criterio | Descripción | Casos |
|---|---|---|
| AC1 | Solo el creador autenticado publica | K16-01, K16-02, K16-19, K16-20, K16-25 |
| AC2 | El creador edita actualizaciones propias | K16-03, K16-19, K16-20, K16-24 |
| AC3 | El creador elimina actualizaciones propias | K16-04, K16-19, K16-20 |
| AC4 | Se permite publicar en ACTIVA y FINANCIADA | K16-01, K16-02 |
| AC5 | No publicar en BORRADOR, NO_FINANCIADA ni activa vencida | K16-06, K16-07, K16-08, K16-25 |
| AC6 | Lectura pública respetando privacidad de borradores | K16-01, K16-02, K16-05, K16-25 |
| AC7 | Título, contenido, autor y fecha; asociación persistente correcta | K16-01, K16-02, K16-05 |
| AC8 | Orden desde la publicación más reciente | K16-05 |
| AC9 | Título 1–150 y contenido 1–5000; rechazo de vacío y espacios | K16-09, K16-10, K16-11, K16-12, K16-13, K16-14, K16-15, K16-16, K16-17, K16-18, K16-24 |
| AC10 | Permisos e identificadores validados en servidor | K16-01, K16-02, K16-03, K16-04, K16-19, K16-20, K16-21 |
| AC11 | Seguridad XSS, CSRF y métodos HTTP | K16-22, K16-23, K16-24 |
| AC12 | Integración Bootstrap y compatibilidad con detalle/aportes | K16-25 |

## Casos y resultados

Todas las pruebas usan pytest-django, fixtures independientes y base de pruebas aislada. Los casos de límites/estados se parametrizan; flujos de seguridad relacionados comparten un único escenario con aserciones para cada operación.

### K16-01 — Publicación en ACTIVA

- Criterio de aceptación: AC1,AC4,AC6,AC7,AC10.
- Nombre automatizado: `test_k16_01_create_and_association[ACTIVA]`.
- Objetivo: comprobar publicación en activa para evitar regresiones de este comportamiento.
- Tipo de prueba: positivo.
- Precondiciones: Creador autenticado; dos campañas y otro usuario.
- Datos de entrada: Título y contenido Unicode con espacios; autor y campaña falsificados.
- Procedimiento: POST crear; seguir redirección; consultar registro y detalle.
- Resultado esperado: Persiste texto recortado con creador y campaña correctos; fecha visible; mensaje de éxito.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-02 — Publicación en FINANCIADA

- Criterio de aceptación: AC1,AC4,AC6,AC7,AC10.
- Nombre automatizado: `test_k16_01_create_and_association[FINANCIADA]`.
- Objetivo: comprobar publicación en financiada para evitar regresiones de este comportamiento.
- Tipo de prueba: positivo.
- Precondiciones: Creador autenticado; campaña financiada.
- Datos de entrada: Texto válido Unicode e IDs falsificados.
- Procedimiento: POST crear y consultar registro.
- Resultado esperado: Se permite publicar en financiada; asociación y presentación correctas.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-03 — Editar actualización propia

- Criterio de aceptación: AC2,AC10.
- Nombre automatizado: `test_k16_02_edit_own`.
- Objetivo: comprobar editar actualización propia para evitar regresiones de este comportamiento.
- Tipo de prueba: positivo.
- Precondiciones: Actualización existente; creador autenticado; campaña ahora NO_FINANCIADA.
- Datos de entrada: Título y contenido nuevos; IDs ajenos.
- Procedimiento: GET formulario y POST edición.
- Resultado esperado: Valores iniciales presentes; cambia texto; mantiene autor, campaña y fecha de publicación; un solo registro.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-04 — Eliminar actualización propia

- Criterio de aceptación: AC3,AC10.
- Nombre automatizado: `test_k16_03_delete_own`.
- Objetivo: comprobar eliminar actualización propia para evitar regresiones de este comportamiento.
- Tipo de prueba: positivo.
- Precondiciones: Actualización del creador; campaña FINANCIADA.
- Datos de entrada: POST eliminar.
- Procedimiento: Eliminar y consultar persistencia.
- Resultado esperado: Desaparece actualización, permanece campaña; mensaje de éxito.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-05 — Lectura pública, orden y aislamiento

- Criterio de aceptación: AC6,AC7,AC8.
- Nombre automatizado: `test_k16_04_public_order_and_isolation`.
- Objetivo: comprobar lectura pública, orden y aislamiento para evitar regresiones de este comportamiento.
- Tipo de prueba: positivo.
- Precondiciones: Múltiples actualizaciones, fechas diferentes y empatadas; otra campaña.
- Datos de entrada: GET detalle sin sesión.
- Procedimiento: Comparar posición de títulos y ausencia de gestión.
- Resultado esperado: Orden descendente, desempate por ID; excluye otra campaña; visitante no ve controles.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-06 — Rechazar BORRADOR

- Criterio de aceptación: AC5.
- Nombre automatizado: `test_k16_05_publication_status[borrador]`.
- Objetivo: comprobar rechazar borrador para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador autenticado; campaña borrador.
- Datos de entrada: Texto válido.
- Procedimiento: POST crear y GET detalle.
- Resultado esperado: 403, sin registro ni enlace de publicación.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-07 — Rechazar NO_FINANCIADA

- Criterio de aceptación: AC5.
- Nombre automatizado: `test_k16_05_publication_status[no-financiada]`.
- Objetivo: comprobar rechazar no_financiada para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador autenticado; campaña no financiada.
- Datos de entrada: Texto válido.
- Procedimiento: POST crear y GET detalle.
- Resultado esperado: 403, sin registro ni enlace de publicación.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-08 — Rechazar ACTIVA vencida

- Criterio de aceptación: AC5.
- Nombre automatizado: `test_k16_05_publication_status[activa-vencida]`.
- Objetivo: comprobar rechazar activa vencida para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Campaña activa con fecha de ayer.
- Datos de entrada: Texto válido.
- Procedimiento: POST crear y recargar campaña.
- Resultado esperado: 403, no persiste, cambia estado a NO_FINANCIADA.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-09 — Título vacío

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[titulo-vacio]`.
- Objetivo: comprobar título vacío para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: Cadena vacía; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en title; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-10 — Título espacios

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[titulo-espacios]`.
- Objetivo: comprobar título espacios para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: Espacios, tabulación, salto de línea y espacio Unicode; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en title; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-11 — Título 1 carácter

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[titulo-1]`.
- Objetivo: comprobar título 1 carácter para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Persiste valor completo y redirige.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-12 — Título 150 caracteres

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[titulo-150]`.
- Objetivo: comprobar título 150 caracteres para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a repetida 150 veces; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Persiste valor completo y redirige.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-13 — Título 151 caracteres

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[titulo-151]`.
- Objetivo: comprobar título 151 caracteres para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a repetida 151 veces; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en title; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-14 — Contenido vacío

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[contenido-vacio]`.
- Objetivo: comprobar contenido vacío para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: Cadena vacía; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en content; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-15 — Contenido espacios

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[contenido-espacios]`.
- Objetivo: comprobar contenido espacios para evitar regresiones de este comportamiento.
- Tipo de prueba: negativo.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: Espacios, tabulación, salto de línea y espacio Unicode; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en content; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-16 — Contenido 1 carácter

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[contenido-1]`.
- Objetivo: comprobar contenido 1 carácter para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Persiste valor completo y redirige.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-17 — Contenido 5000 caracteres

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[contenido-5000]`.
- Objetivo: comprobar contenido 5000 caracteres para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a repetida 5000 veces; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Persiste valor completo y redirige.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-18 — Contenido 5001 caracteres

- Criterio de aceptación: AC9.
- Nombre automatizado: `test_k16_06_validation[contenido-5001]`.
- Objetivo: comprobar contenido 5001 caracteres para evitar regresiones de este comportamiento.
- Tipo de prueba: borde.
- Precondiciones: Creador con sesión; campaña activa; una actualización previa.
- Datos de entrada: a repetida 5001 veces; el otro campo es válido.
- Procedimiento: POST crear y consultar errores y base.
- Resultado esperado: Error visible en content; no crea registro ni altera actualización previa.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-19 — Autenticación en todas las escrituras

- Criterio de aceptación: AC1,AC2,AC3,AC10.
- Nombre automatizado: `test_k16_07_authentication`.
- Objetivo: comprobar autenticación en todas las escrituras para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Visitante y actualización existente.
- Datos de entrada: POST crear, editar y eliminar.
- Procedimiento: Enviar las tres operaciones sin sesión.
- Resultado esperado: Todas redirigen al login; datos intactos.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-20 — Permisos del servidor

- Criterio de aceptación: AC1,AC2,AC3,AC10.
- Nombre automatizado: `test_k16_08_server_permissions`.
- Objetivo: comprobar permisos del servidor para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Usuario ajeno con privilegios staff y superuser.
- Datos de entrada: POST crear, editar y eliminar; author falsificado.
- Procedimiento: Intentar gestionar campaña ajena.
- Resultado esperado: 404 en las tres operaciones; no concede excepción al administrador; datos intactos.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-21 — IDs inexistentes y mezcla de campañas

- Criterio de aceptación: AC10.
- Nombre automatizado: `test_k16_09_invalid_identifiers`.
- Objetivo: comprobar ids inexistentes y mezcla de campañas para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Creador con dos campañas; actualización en primera campaña.
- Datos de entrada: URL con segunda campaña; IDs 999999.
- Procedimiento: Editar/eliminar con campaña incorrecta y usar IDs inexistentes.
- Resultado esperado: 404 en cada solicitud; actualización intacta.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-22 — CSRF en ciclo completo

- Criterio de aceptación: AC11.
- Nombre automatizado: `test_k16_11_csrf`.
- Objetivo: comprobar csrf en ciclo completo para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Cliente enforce_csrf_checks=True y sesión del creador.
- Datos de entrada: Tokens ausentes, inválido y válido.
- Procedimiento: Rechazar crear/editar/eliminar sin token válido; completar ciclo autorizado con token.
- Resultado esperado: 403 en ataques; creación, edición y eliminación válidas; original intacto.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-23 — Métodos HTTP

- Criterio de aceptación: AC11.
- Nombre automatizado: `test_k16_12_http_methods`.
- Objetivo: comprobar métodos http para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Creador con sesión; actualización existente.
- Datos de entrada: PUT crear, PATCH editar, GET eliminar.
- Procedimiento: Invocar métodos incorrectos.
- Resultado esperado: 405 y Allow GET, POST para formularios o POST para eliminar; sin cambios.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-24 — XSS y Unicode al editar

- Criterio de aceptación: AC2,AC9,AC11.
- Nombre automatizado: `test_k16_13_xss`.
- Objetivo: comprobar xss y unicode al editar para evitar regresiones de este comportamiento.
- Tipo de prueba: seguridad.
- Precondiciones: Creador cuyo nombre contiene HTML; actualización existente.
- Datos de entrada: Script en título; HTML y Unicode en contenido; cierre textarea y más de 5000 caracteres.
- Procedimiento: Editar, leer públicamente e intentar edición inválida.
- Resultado esperado: Escapa autor, título, contenido y formulario; Unicode visible; edición inválida conserva contenido anterior.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

### K16-25 — Detalle e integración con aportes

- Criterio de aceptación: AC1,AC5,AC6,AC12.
- Nombre automatizado: `test_k16_14_detail_integration`.
- Objetivo: comprobar detalle e integración con aportes para evitar regresiones de este comportamiento.
- Tipo de prueba: integración.
- Precondiciones: Campaña vacía; luego una actualización y distintos usuarios.
- Datos de entrada: GET detalle/formulario; aporte -1; campaña pasa a borrador.
- Procedimiento: Revisar vacío, controles propios, ausencia de controles ajenos, error de aporte y privacidad.
- Resultado esperado: Formulario solo para creador; actualizaciones sobreviven error de aporte; borrador devuelve 404 a visitante.
- Resultado obtenido: todas las aserciones del caso se cumplieron; pytest registró PASSED.
- Estado: **aprobado localmente**.

## Resumen verificable

- [Pruebas KAN-16](evidencias/KAN-16/07-pruebas-kan16.jpg): 25 ejecutadas, 25 aprobadas, 0 fallidas, 0 omitidas.
- [Suite completa](evidencias/KAN-16/08-suite-completa.jpg): 122 ejecutadas, 122 aprobadas, 0 fallidas, 0 omitidas.
- Los conteos anteriores son locales. GitHub también reportó SUCCESS para Jenkins de la rama y PR #25; no se atribuye a Jenkins un conteo de casos sin consultar su reporte.

No se mantienen como pruebas dedicadas todas las permutaciones de estado al editar/eliminar, todos los métodos HTTP inválidos ni la cascada al eliminar campañas: se priorizaron los 25 escenarios anteriores. La edición reutiliza el mismo formulario validado y tiene un caso específico de entrada inválida.


## Correspondencia con los criterios de Jira

| Criterio Jira | Requisitos detallados de esta matriz |
|---|---|
| CA1 Publicar actualizaciones | AC1, AC4, AC5, AC7 |
| CA2 Visualizar actualizaciones | AC6, AC7, AC8, AC12 |
| CA3 Editar actualizaciones | AC2, AC9, AC10 |
| CA4 Eliminar actualizaciones | AC3, AC10 |
| CA5 Validaciones | AC9, AC11 |
| CA6 Control de acceso | AC1, AC2, AC3, AC5, AC10, AC11 |

[Volver al índice](README.md)
