# Sesión 3 — 29/10/2026 · LP2 Azure Container Apps

## Planning del día (enviado por el docente)
| Hora | Actividad |
|---|---|
| 18:00-18:15 | Test LP1 (4 preguntas) |
| 18:15-19:00 | LP2 (ACA), módulos 1, 2 y 3: Deploy / Manage / Scale (teoría) |
| 19:00-19:50 | Lab 3 · AI-200-LP02M01 · Deploy containers to Azure Container Apps |
| 19:50-20:10 | Descanso |
| 20:10-21:50 | Lab 4 · AI-200-LP02M02 · Manage containers in ACA y Lab 5 · AI-200-LP02M03 · Scale containers in ACA |
| 21:50-22:00 | Test LP2 (6 preguntas) |

Numeración de la plataforma del curso: LP1 = labs 1-2, LP2 = labs 3-5. El módulo 4 de LP2 (dynamic sessions) y el sidecar de LP1 **no aparecen en el planning**.

## Qué se hizo
- Añadido el material del día: presentación del LP2 y knowledge checks de LP1 y LP2 (los PDF/zip/docx no se suben).
- Nota del módulo con resumen, respuestas del knowledge check y preguntas de discusión: `docs/modulos/02-container-apps.md`.
- Tema del día según la guía de estudio de MS Learn: learning path «Implementación y administración de aplicaciones en Azure Container Apps» (4 módulos: desplegar, gestionar, escalar y sesiones dinámicas). Las diapositivas solo cubren los 3 primeros; el 4.º se resumió desde los objetivos publicados.
- Documentado el test de LP1 (prueba corta sobre los labs del último día) con opciones, por qué falla cada distractor y el lab donde se practicó: `docs/tests/lp1-knowledge-check.md`.
- **Lab 3 (LP02M01) completo** en Linux: ACR + environment con `azdeploy.py` (región `eastus`, `gpt-5.1`, `TPM_LIMIT`), container app con identidad gestionada para el pull, secreto con `secretref:`, revisión `0000002` y verificación de `/health`, `/` y `/process`. Detalle en `labs/lp2-01-aca-deploy/README.md`; script en `scripts/lp2-01-aca-deploy/`.
- Incorporada la transcripción de la clase (Zoom): notas organizativas y técnicas en `docs/modulos/02-container-apps.md` y correcciones del test de LP1 en `docs/tests/lp1-knowledge-check.md` (sin nombres de personas; la transcripción no se publica: se borró del repo tras extraer el contenido).
- Enlaces del curso consolidados en `docs/links.md` (sin datos de terceros).
- `.gitignore` ampliado: zips, `.docx`, `azdeploy.py` y `api/` de los labs.

## Decisiones
- Los labs se reproducen igual que en LP1: el usuario ejecuta los comandos que crean/borran recursos, Claude guía a partir de la guía oficial.
- Dynamic sessions (LP2) y el sidecar (LP1) no figuran en el planning del docente: se dan por no previstos salvo aviso.

## Aprendizajes
_(pendiente: se rellena al cerrar el día con `/aprender`)_

## Pendientes
- Cleanup del lab 3 (`rg-ai200-aca`) tras decidir si los labs 4 y 5 reutilizan recursos; la plataforma desprovisiona al finalizar.
- Labs 4 (Manage) y 5 (Scale), con la guía de la plataforma.
- Cleanup del lab 2 de LP1 (`rg-ai200-appsvc`) si la plataforma no lo desprovisiona.
- Corrección en clase de las 4 preguntas de LP1 y 6 de LP2.
- Siguiente: LP3 AKS.
