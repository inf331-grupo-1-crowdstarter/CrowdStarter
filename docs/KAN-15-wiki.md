# KAN-15 — Comentarios en campañas

## Descripción y funcionalidad

Se incorporó una sección de comentarios al detalle de campañas, con el estilo Bootstrap existente. Los visitantes pueden leer; los usuarios autenticados, incluido el creador, pueden publicar en campañas activas no vencidas. Cada comentario muestra autor, contenido y fecha. Se ordenan de más reciente a más antiguo, con ID descendente como desempate.

El formulario elimina espacios exteriores y exige entre 1 y 1000 caracteres. Los valores de autor y campaña se asignan en el servidor. Solo el autor puede eliminar, incluso cuando la campaña ya cerró. Las rutas de escritura exigen sesión, POST y CSRF. Los borradores conservan su privacidad. El autoescape de Django protege contenido, autor y formularios con errores.

La migración `campaigns/migrations/0002_comment.py` crea `Comment` y sus relaciones. Los comentarios se eliminan en cascada al eliminar su campaña o autor. El acceso al detalle obtiene autores con `select_related`. El control de campaña activa usa la misma política de fechas del sistema y el bloqueo de escritura ya empleado por los aportes. No se modificaron las pruebas anteriores.

## Criterios, matriz y resultados

Los once criterios de aceptación, su trazabilidad y los **20 casos priorizados** están documentados en [KAN-15-casos-de-prueba.md](KAN-15-casos-de-prueba.md), con objetivo, precondiciones, entrada, procedimiento, resultado esperado, obtenido y estado por prueba.

La selección final contiene 20 pruebas nuevas que cubren los criterios de aceptación y escenarios prioritarios.

| Verificación local, 29/10/2026 | Ejecutadas | Aprobadas | Fallidas | Omitidas |
|---|---:|---:|---:|---:|
| KAN-15 | 20 | 20 | 0 | 0 |
| Suite completa (97 anteriores + 20 nuevas) | 117 | 117 | 0 | 0 |

`python manage.py check`: sin problemas. `makemigrations --check --dry-run`: sin cambios pendientes. La migración se aplicó en la base ficticia y en las bases de pytest. No se modificó la base de desarrollo del usuario.

## Capturas y registros

Capturas reales del navegador con datos ficticios; las capturas de resultados muestran extractos de los registros reales de pytest, presentados en HTML para su lectura, no una terminal simulada. Los registros TXT y HTML conservan los resultados de ejecución; las rutas absolutas del equipo se sustituyeron por `CrowdStarter`.

1. [Sección pública](evidencias/KAN-15/01-seccion-publica.jpg).
2. [Formulario preparado para publicar](evidencias/KAN-15/02-publicacion.jpg).
3. [Publicación exitosa y comentarios de diferentes usuarios](evidencias/KAN-15/03-diferentes-usuarios.jpg).
4. [Validación de solo espacios](evidencias/KAN-15/04-validacion.jpg).
5. [Eliminación propia exitosa](evidencias/KAN-15/05-eliminacion.jpg).
6. [Resultado de las 20 pruebas KAN-15](evidencias/KAN-15/06-pruebas-kan15.jpg).
7. [Resultado de las 117 pruebas completas](evidencias/KAN-15/07-suite-completa.jpg).

Registros: [KAN-15](evidencias/KAN-15/pytest-kan15.txt), [suite completa](evidencias/KAN-15/pytest-suite.txt), [Django check](evidencias/KAN-15/check.txt). Las cuentas `example.test` son ficticias; no se incluyen contraseñas ni tokens en las evidencias.

## Problemas encontrados y soluciones

- El acceso inicial a GitHub y la apertura de puertos locales estaban restringidos por el entorno: se ejecutaron mediante el mecanismo de autorización disponible.
- El detalle se renderizaba también al fallar un aporte: se centralizó el contexto para conservar comentarios y formulario en ese flujo.
- La fecha vencida puede coexistir con estado activo antes de visitar la campaña: se reutiliza la expiración y se comprueban estado y fecha antes de publicar.
- Se encontró una imagen local sin seguimiento: se conservó y se excluyó de los cambios KAN-15.
- El disco del proyecto se llenó al guardar documentación: se preservaron documentos y capturas finales en una ubicación temporal externa, y se guardaron fuera del repositorio cuando volvió a haber espacio disponible.

## Reproducción

Desde la carpeta existente `CrowdStarter`, con las dependencias de `requirements.txt` instaladas:

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py check
pytest campaigns/tests/test_kan15.py -v
pytest -v
python manage.py makemigrations --check --dry-run
```

Pytest usa una base de pruebas independiente. La interfaz requiere aplicar la migración antes de iniciar el servidor. Para revisión manual, crear una campaña activa y dos usuarios ficticios; consultar sin sesión, comentar con ambas cuentas, enviar espacios y eliminar un comentario propio. Comprobar que no aparezca el botón de eliminar sobre el comentario ajeno.

## Jenkins y estado de entrega

Durante la validación inicial de KAN-15 (commit `543da47`), la rama no incluía un `Jenkinsfile`. Los resultados de este documento corresponden a pruebas locales; no se verificó una ejecución de Jenkins para ese commit. Esta observación es histórica y no describe la configuración posterior de `develop`.

La suite mantiene `pytest.ini` y el patrón `test_*.py`: un pipeline que ejecute `pytest -v` descubrirá los 20 casos. Al cierre de esa validación quedó pendiente comprobar su ejecución en el Jenkins del equipo.

Estado registrado al cierre de la validación inicial. Rama: `feature/KAN-15-comentarios-campanas`. Implementación y criterios verificados localmente; commit `543da479d79876f8edf118254c937f83716c53ed` publicado y [PR #21](https://github.com/inf331-grupo-1-crowdstarter/CrowdStarter/pull/21) abierto hacia `develop`, sin fusionar. En ese momento, la verificación de Jenkins quedó pendiente. No fusionar automáticamente.

## Archivos

Modificados: `campaigns/models.py`, `campaigns/forms.py`, `campaigns/views.py`, `campaigns/urls.py`, `templates/campaigns/detail.html`.

Nuevos en el repositorio: `campaigns/migrations/0002_comment.py`, `campaigns/tests/test_kan15.py`, `templates/campaigns/comments.html`.

[Volver al índice](README.md)
