# CrowdStarter — Documentación de funcionalidades de la Entrega 2

Este paquete reúne las descripciones, criterios de aceptación, pruebas y evidencias disponibles de KAN-13, KAN-14, KAN-15 y KAN-16. Los resultados corresponden a las ejecuciones registradas por historia; no acreditan una versión con las cuatro historias integradas.

## Documentación

| Historia | Funcionalidad y criterios | Pruebas | Resultado específico local |
|---|---|---|---|
| KAN-13 — Panel del creador | [Resumen](Resumen_KAN-13_KAN-14.md) | [Casos y resultados](Pruebas_KAN-13_KAN-14.md) | 5 aprobadas |
| KAN-14 — Historial de aportes | [Resumen](Resumen_KAN-13_KAN-14.md) | [Casos y resultados](Pruebas_KAN-13_KAN-14.md) | 6 aprobadas |
| KAN-15 — Comentarios | [Implementación](KAN-15-wiki.md) | [20 casos](KAN-15-casos-de-prueba.md) | 20 aprobadas |
| KAN-16 — Actualizaciones del creador | [Implementación](KAN-16-wiki.md) | [25 casos](KAN-16-casos-de-prueba.md) | 25 aprobadas |

## Alcance de los resultados

- KAN-13 y KAN-14: capturas de PyTest local y de interfaz. No se conserva aquí un registro de suite completa ni el identificador del commit probado.
- KAN-15: 117 pruebas locales aprobadas (97 anteriores y 20 nuevas), con capturas y registros TXT/HTML. Validación documentada sobre `543da47`.
- KAN-16: 122 pruebas locales aprobadas (97 anteriores y 25 nuevas), con capturas. Validación documentada sobre `5e1b702`.
- Las suites de 117 y 122 corresponden a versiones diferentes: no deben sumarse ni presentarse como una ejecución integrada.
- Los estados de PR, Jira y Jenkins descritos en los documentos son históricos. KAN-16 registra estados SUCCESS de Jenkins; este paquete no incluye sus logs de servidor ni un conteo de pruebas obtenido desde Jenkins.
