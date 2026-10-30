# KAN-16 — Actualizaciones del creador

## Implementación

Se agregó `CampaignUpdate` con campaña, autor, título, contenido, fecha de publicación y fecha de modificación. El detalle muestra las actualizaciones a visitantes, ordenadas por fecha descendente e ID como desempate. Solo el creador autenticado puede publicar; editar y eliminar exigen además ser autor de la actualización. No hay excepción para administradores.

Se permite publicar en ACTIVA no vencida y FINANCIADA. BORRADOR y NO_FINANCIADA rechazan publicaciones. La edición y eliminación propias siguen disponibles tras el cierre: la restricción de estado del requisito aplica a nuevas publicaciones. Los borradores mantienen la privacidad del detalle existente.

El título admite 1–150 caracteres y el contenido 1–5000, después de quitar espacios exteriores. La interfaz usa Bootstrap existente y autoescape; el servidor valida sesión, propietario, pertenencia a campaña, campos, CSRF y métodos HTTP. Se permite GET/POST en formularios y exclusivamente POST para eliminar. Editar no cambia la fecha de publicación ni el orden. El autor se obtiene de la sesión, nunca del POST.

La consulta de actualizaciones usa `select_related('author')`. La publicación sigue el patrón existente de transacción/bloqueo de SQLite para verificar estado. Las actualizaciones se eliminan en cascada con su campaña; el autor está protegido. Los formularios y vistas se separan en módulos específicos para reducir cambios sobre funcionalidades ajenas.

## Criterios y pruebas

La historia Jira contiene CA1 publicación, CA2 visualización, CA3 edición, CA4 eliminación, CA5 validaciones y CA6 control de acceso. La [matriz de 25 casos](KAN-16-casos-de-prueba.md) detalla esos comportamientos y sus requisitos derivados.

Resultados finales locales, 29/10/2026:

| Comando | Resultado |
|---|---|
| `python manage.py check` | Sin problemas |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes |
| `pytest campaigns/tests/test_kan16.py -v` | 25 aprobadas, 0 fallidas, 0 omitidas |
| `pytest -v` | 122 aprobadas: 97 anteriores + 25 nuevas; 0 fallidas, 0 omitidas |
| `python -m pip check` | Sin dependencias rotas |

La selección final contiene 25 pruebas nuevas. No se modificaron pruebas anteriores. Durante la validación se registró en GitHub SUCCESS para los builds #1 de la rama y del PR #25. Las cantidades de pruebas de esta tabla corresponden a ejecuciones locales.

## Reproducción

Desde CrowdStarter y en la rama de la historia:

```bash
source .venv/bin/activate
python manage.py migrate
python manage.py check
python manage.py makemigrations --check --dry-run
pytest campaigns/tests/test_kan16.py -v
pytest -v
python manage.py runserver
```

La migración `0002_campaign_update` se aplicó en una base ficticia independiente y durante pytest. No se aplicó sobre la base del usuario. Para uso local persistente, debe ejecutarse `migrate` antes de visitar el detalle.

## Evidencias

Capturas reales en navegador con cuentas `example.test`. No contienen contraseñas ni tokens. Las capturas de pruebas muestran extractos del registro real en HTML, no una terminal simulada; esta entrega conserva las capturas de los resultados.

- [Lectura pública](evidencias/KAN-16/01-lectura-publica.jpg)
- [Formulario de creación](evidencias/KAN-16/02-formulario-creacion.jpg)
- [Creación correcta](evidencias/KAN-16/03-creacion-correcta.jpg)
- [Formulario de edición](evidencias/KAN-16/04-edicion-formulario.jpg)
- [Edición correcta](evidencias/KAN-16/04b-edicion-correcta.jpg)
- [Eliminación](evidencias/KAN-16/05-eliminacion.jpg)
- [Validación](evidencias/KAN-16/06-validacion.jpg)
- [25 pruebas KAN-16](evidencias/KAN-16/07-pruebas-kan16.jpg)
- [122 pruebas completas](evidencias/KAN-16/08-suite-completa.jpg)

## Archivos del repositorio

Modificados: `campaigns/models.py`, `campaigns/urls.py`, `templates/campaigns/detail.html`.

Creados: `campaigns/migrations/0002_campaign_update.py`, `campaigns/update_forms.py`, `campaigns/update_views.py`, `campaigns/tests/test_kan16.py`, `templates/campaigns/update_form.html`, `templates/campaigns/updates.html`.

No se modificaron dependencias, Jenkinsfile, configuración Django, vistas anteriores ni los PR pendientes. La imagen sin seguimiento se conserva y se respalda fuera del repositorio.

## Compatibilidad pendiente de integración

KAN-16 parte exclusivamente de `origin/develop` en `5159e01`. No se incorporaron KAN-13, KAN-14, KAN-15 ni PR #22.

- **KAN-15:** sus migraciones `0002_comment` y `0002_campaign_update` parten de `0001_initial`, por lo que al integrar ambas habrá dos hojas. En la futura rama de integración se debe generar y revisar una migración de unión con `python manage.py makemigrations campaigns --merge`; después migrar y ejecutar la suite. No borrar ni renombrar migraciones ya aplicadas. Conservar ambos modelos y propiedades en `models.py`, todas las rutas en `urls.py`, y ambos includes (`comments.html` y `updates.html`) en el detalle. La línea compacta del detalle es un punto probable de conflicto textual.
- **KAN-13 y KAN-14:** también agregan rutas en `campaigns/urls.py`; conservar todas al resolver conflictos. KAN-16 no cambia `campaigns/views.py` ni `templates/base.html`, que esas historias sí modifican.
- **PR #22:** cambia estilos/base/listado y settings; KAN-16 hereda Bootstrap y no incorpora su CSS ni su configuración. Tras integrarlo, volver a revisar la presentación de actualizaciones con el estilo resultante.

Estos puntos se identificaron por inspección de diferencias, no por integrar las ramas ni afirmar que la combinación esté probada.

## Git y Jira

Estado histórico registrado durante la validación del 29/10/2026; no constituye una consulta actual de GitHub o Jira.

Rama: `feature/KAN-16-actualizaciones-creador`; destino del PR: `develop`. Commit `5e1b702` publicado; [PR #25](https://github.com/inf331-grupo-1-crowdstarter/CrowdStarter/pull/25) abierto hacia `develop`. La descripción termina con `Closes KAN-16`, según lo solicitado. No se cerrará la historia ni se fusionará el PR.

Se verificó en Jira que GitHub for Atlassian está instalado y que el panel Development de KAN-16 reconoce la rama, el commit y el PR #25 abierto hacia develop. La historia permanece En curso. La vinculación funciona. En la configuración accesible se pudo ver la plantilla de cierre por PR fusionado, pero no se pudo verificar una regla activa que realice esa transición. Por tanto, el cierre automático no está confirmado; Closes KAN-16 por sí solo no acredita su funcionamiento. No se modificaron reglas ni el estado de Jira.


Jenkins reportó finalmente SUCCESS para `continuous-integration/jenkins/branch` y `continuous-integration/jenkins/pr-head`, ambos sobre el commit `5e1b702`.

[Volver al índice](README.md)
