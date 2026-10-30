# KAN-15 — Casos de prueba

La matriz inicial se elaboró antes del código de pruebas. Por solicitud posterior del usuario se priorizaron **exactamente 20 pruebas nuevas**, manteniendo intactas las 97 anteriores. Se agrupan en una misma prueba los pasos del mismo flujo (CSRF, privacidad o integración), sin repetir cada combinación de métodos y roles.

## Criterios de aceptación y trazabilidad

| Criterio | Descripción | Casos |
|---|---|---|
| AC1 | Lectura pública respetando privacidad de borradores | KAN15-03, KAN15-16, KAN15-19 |
| AC2 | Publicación autenticada en campañas activas | KAN15-01, KAN15-02, KAN15-14, KAN15-16, KAN15-17, KAN15-18, KAN15-19 |
| AC3 | Autor, contenido, fecha y asociación correcta | KAN15-01, KAN15-02, KAN15-03, KAN15-20 |
| AC4 | Orden descendente por fecha | KAN15-03 |
| AC5 | Eliminación propia | KAN15-04, KAN15-14, KAN15-16, KAN15-17, KAN15-18, KAN15-19 |
| AC6 | Prohibición de eliminar comentarios ajenos | KAN15-14, KAN15-15 |
| AC7 | Rechazo de vacío y espacios | KAN15-05, KAN15-06, KAN15-07 |
| AC8 | Máximo 1000 caracteres | KAN15-07, KAN15-08, KAN15-09, KAN15-20 |
| AC9 | Rechazo de campañas inactivas o vencidas | KAN15-10, KAN15-11, KAN15-12, KAN15-13, KAN15-16, KAN15-19 |
| AC10 | Presentación segura de HTML/JavaScript | KAN15-03, KAN15-20 |
| AC11 | Creador también puede comentar | KAN15-02 |

## Casos ejecutados localmente

Fecha: 29/10/2026 (America/Santiago). Archivo automatizado: `campaigns/tests/test_kan15.py`. La parametrización genera las variantes de publicación, contenido y estado. Todas usan base aislada de pytest-django.

### KAN15-01 — Publicación válida por participante

- Criterio: AC2,AC3.
- Nombre automatizado: `test_cp01_publish_association[False]`.
- Objetivo: verificar publicación válida por participante, evitando regresiones de este comportamiento.
- Tipo: positivo.
- Precondiciones: Campaña activa y sesión de otro usuario.
- Datos de entrada: Texto con espacios exteriores e IDs falsificados.
- Procedimiento: Publicar y consultar comentario persistido.
- Resultado esperado: Se guarda texto recortado con autor autenticado y campaña de URL; fecha y contenido visibles.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-02 — Publicación por creador

- Criterio: AC2,AC3,AC11.
- Nombre automatizado: `test_cp01_publish_association[True]`.
- Objetivo: verificar publicación por creador, evitando regresiones de este comportamiento.
- Tipo: positivo.
- Precondiciones: Campaña activa y sesión del creador.
- Datos de entrada: Comentario válido e IDs manipulados.
- Procedimiento: Publicar desde cuenta creadora.
- Resultado esperado: Mismas garantías de persistencia y asociación; creador autorizado.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-03 — Lectura pública, orden y aislamiento

- Criterio: AC1,AC3,AC4,AC10.
- Nombre automatizado: `test_cp02_public_order_isolation`.
- Objetivo: verificar lectura pública, orden y aislamiento, evitando regresiones de este comportamiento.
- Tipo: positivo.
- Precondiciones: Varias campañas y comentarios con fechas distintas y empatadas.
- Datos de entrada: GET sin sesión; comentario con script.
- Procedimiento: Consultar detalle público y su lista.
- Resultado esperado: Orden por fecha descendente e ID; otra campaña excluida; HTML escapado; no hay botón eliminar.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-04 — Eliminación propia en campaña cerrada

- Criterio: AC5.
- Nombre automatizado: `test_cp03_delete_own`.
- Objetivo: verificar eliminación propia en campaña cerrada, evitando regresiones de este comportamiento.
- Tipo: positivo.
- Precondiciones: Comentario propio; campaña financiada.
- Datos de entrada: POST eliminar.
- Procedimiento: Autenticar autor y eliminar siguiendo redirección.
- Resultado esperado: Comentario desaparece de base; mensaje de éxito; cierre no bloquea eliminación.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-05 — Contenido vacío

- Criterio: AC7.
- Nombre automatizado: `test_cp04_content_boundaries[-False]`.
- Objetivo: verificar contenido vacío, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Sesión y campaña activa.
- Datos de entrada: Cadena vacía.
- Procedimiento: Enviar formulario.
- Resultado esperado: No persiste; error visible.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-06 — Solo espacios

- Criterio: AC7.
- Nombre automatizado: `test_cp04_content_boundaries[ \t\n\u2003 -False]`.
- Objetivo: verificar solo espacios, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Sesión y campaña activa.
- Datos de entrada: Espacios, tabulación, salto de línea y espacio Unicode.
- Procedimiento: Enviar formulario.
- Resultado esperado: No persiste; error visible.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-07 — Un carácter

- Criterio: AC7,AC8.
- Nombre automatizado: `test_cp04_content_boundaries[a-True]`.
- Objetivo: verificar un carácter, evitando regresiones de este comportamiento.
- Tipo: borde.
- Precondiciones: Sesión y campaña activa.
- Datos de entrada: a.
- Procedimiento: Publicar y consultar base.
- Resultado esperado: Persiste exactamente un carácter.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-08 — Exactamente 1000 caracteres

- Criterio: AC8.
- Nombre automatizado: `test_cp04_content_boundaries[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-True]`.
- Objetivo: verificar exactamente 1000 caracteres, evitando regresiones de este comportamiento.
- Tipo: borde.
- Precondiciones: Sesión y campaña activa.
- Datos de entrada: a repetida 1000 veces.
- Procedimiento: Publicar y consultar base.
- Resultado esperado: Aceptado y persistido íntegramente.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-09 — 1001 caracteres

- Criterio: AC8.
- Nombre automatizado: `test_cp04_content_boundaries[aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-False]`.
- Objetivo: verificar 1001 caracteres, evitando regresiones de este comportamiento.
- Tipo: borde.
- Precondiciones: Sesión y campaña activa.
- Datos de entrada: a repetida 1001 veces.
- Procedimiento: Enviar formulario.
- Resultado esperado: Rechazado sin persistencia; muestra error.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-10 — Borrador del creador

- Criterio: AC9.
- Nombre automatizado: `test_cp05_campaign_status[BORRADOR-1-True-403]`.
- Objetivo: verificar borrador del creador, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Sesión del creador; borrador.
- Datos de entrada: Texto válido.
- Procedimiento: Intentar publicar.
- Resultado esperado: 403; no persiste.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-11 — Campaña financiada

- Criterio: AC9.
- Nombre automatizado: `test_cp05_campaign_status[FINANCIADA-1-False-403]`.
- Objetivo: verificar campaña financiada, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Sesión y campaña financiada.
- Datos de entrada: Texto válido.
- Procedimiento: Intentar publicar.
- Resultado esperado: 403; no persiste.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-12 — Campaña no financiada

- Criterio: AC9.
- Nombre automatizado: `test_cp05_campaign_status[NO_FINANCIADA-1-False-403]`.
- Objetivo: verificar campaña no financiada, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Sesión y campaña no financiada.
- Datos de entrada: Texto válido.
- Procedimiento: Intentar publicar.
- Resultado esperado: 403; no persiste.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-13 — Campaña vencida

- Criterio: AC9.
- Nombre automatizado: `test_cp05_campaign_status[ACTIVA--1-False-403]`.
- Objetivo: verificar campaña vencida, evitando regresiones de este comportamiento.
- Tipo: negativo.
- Precondiciones: Estado activo y fecha de ayer.
- Datos de entrada: Texto válido.
- Procedimiento: Intentar publicar y recargar campaña.
- Resultado esperado: 403; no persiste; estado pasa a NO_FINANCIADA.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-14 — Escrituras sin autenticación

- Criterio: AC2,AC5,AC6.
- Nombre automatizado: `test_cp06_anonymous_write`.
- Objetivo: verificar escrituras sin autenticación, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Visitante y comentario existente.
- Datos de entrada: POST crear y eliminar.
- Procedimiento: Intentar ambas mutaciones sin sesión.
- Resultado esperado: Redirección a login; comentario original intacto.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-15 — Propiedad e identificadores

- Criterio: AC6.
- Nombre automatizado: `test_cp07_identifier_permissions`.
- Objetivo: verificar propiedad e identificadores, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Comentario de participante y segunda campaña.
- Datos de entrada: POST del creador; después autor con campaña incorrecta.
- Procedimiento: Intentar eliminación ajena y manipular URL.
- Resultado esperado: Ambos 404; comentario intacto.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-16 — Recursos inexistentes y privacidad

- Criterio: AC1,AC2,AC5,AC9.
- Nombre automatizado: `test_cp08_missing_or_private`.
- Objetivo: verificar recursos inexistentes y privacidad, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Sesión de participante y campaña existente.
- Datos de entrada: IDs inexistentes; luego campaña convertida a borrador.
- Procedimiento: Consultar campaña inexistente, publicar y eliminar con IDs inválidos; leer/publicar borrador ajeno.
- Resultado esperado: 404 en cada operación; comentario intacto.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-17 — Métodos HTTP incorrectos

- Criterio: AC2,AC5.
- Nombre automatizado: `test_cp09_http_methods`.
- Objetivo: verificar métodos http incorrectos, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Sesión del autor.
- Datos de entrada: GET crear; DELETE eliminar.
- Procedimiento: Invocar rutas con métodos no permitidos.
- Resultado esperado: 405 con Allow POST; sin mutaciones.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-18 — Protección CSRF

- Criterio: AC2,AC5.
- Nombre automatizado: `test_cp10_csrf`.
- Objetivo: verificar protección csrf, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Cliente con enforce_csrf_checks=True y sesión.
- Datos de entrada: Token ausente, incorrecto y válido.
- Procedimiento: Crear sin token; eliminar con token inválido; repetir con token válido.
- Resultado esperado: 403 en solicitudes inválidas; crear y eliminar autorizados con token válido.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-19 — Integración visual y regresión de aportes

- Criterio: AC1,AC2,AC5,AC9.
- Nombre automatizado: `test_cp11_cp13_ui_and_contribution_error`.
- Objetivo: verificar integración visual y regresión de aportes, evitando regresiones de este comportamiento.
- Tipo: integración.
- Precondiciones: Campaña con comentario; visitante, autor y creador.
- Datos de entrada: GET detalle; aporte -1; cierre de campaña.
- Procedimiento: Revisar login, formulario y botones; enviar aporte inválido; cerrar; dejar sin comentarios.
- Resultado esperado: Solo autor ve eliminar; aporte inválido conserva sección; cerrada sin formulario; estado vacío visible.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

### KAN15-20 — Unicode y XSS en contenido, autor y errores

- Criterio: AC3,AC8,AC10.
- Nombre automatizado: `test_cp12_xss_unicode_and_errors`.
- Objetivo: verificar unicode y xss en contenido, autor y errores, evitando regresiones de este comportamiento.
- Tipo: seguridad.
- Precondiciones: Sesión con autor que contiene HTML.
- Datos de entrada: Unicode, emoji, script y contenido largo con cierre de textarea.
- Procedimiento: Publicar texto mixto; consultar detalle; enviar payload demasiado largo.
- Resultado esperado: Unicode persiste; etiquetas escapadas en contenido, autor y textarea; entrada inválida no persiste.
- Resultado obtenido: se cumplieron todas las aserciones descritas; pytest registró `PASSED` para este nodo.
- Estado: **aprobado** (local).

## Alcance y evidencia

- [Registro específico completo](evidencias/KAN-15/pytest-kan15.txt): 20 ejecutadas, 20 aprobadas, 0 fallidas, 0 omitidas.
- [Registro de regresión completo](evidencias/KAN-15/pytest-suite.txt): 117 ejecutadas, 117 aprobadas, 0 fallidas, 0 omitidas; incluye las 20 nuevas y las 97 anteriores.
- [Control de Django](evidencias/KAN-15/check.txt): sin problemas.

[Volver al índice](README.md)
