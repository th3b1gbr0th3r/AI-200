# Sesión 3 — 29/10/2026 · LP2 Azure Container Apps

## Cómo seguir esta clase (hilo conductor)
**Idea del día:** Container Apps es «Kubernetes sin gestionar el cluster»: cada cambio crea una **revisión** (como un rollout), los secretos se referencian con `secretref:` y el escalado lo hace KEDA con reglas HTTP.

1. **Teoría LP2:** environment, app, revisión, ingress, secretos y escalado. → [nota del módulo LP2](../docs/modulos/02-container-apps.md).
2. **Lab 3 · Deploy:** ACR + environment con `azdeploy.py` (pasos 4-7), app con identidad gestionada (8), secreto y variable `secretref:` que crea la revisión 0000002 (9-11), y prueba de la API (12-14). → [README del lab 3](../labs/lp2-01-aca-deploy/README.md).
3. **Lab 4 · Manage:** romper la app a propósito y arreglarla como en producción: fallo A, una variable que falta (pasos 6-10), y fallo B, un puerto de ingress equivocado (11); después reconstruir la historia con KQL en Log Analytics (12-14). Por qué: es el ciclo síntoma → diagnóstico → corrección → verificación. → [README del lab 4](../labs/lp2-02-aca-manage/README.md).
4. **Lab 5 · Scale:** pasar de 1 réplica fija a una regla HTTP (pasos 6-7) y ver con carga real cómo sube 1 → 3 → 5 (8-9). Por qué: la regla es concurrencia **por réplica**. → [README del lab 5](../labs/lp2-03-aca-scale/README.md).
5. **Limpieza** de los tres grupos y **repaso:** [aprendizaje del día](../docs/aprendizajes.md).

---

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
Entrada completa en [`docs/aprendizajes.md`](../docs/aprendizajes.md) (2026-10-29).
- **Principal:** el escalado HTTP de ACA depende de la concurrencia por réplica (regla de 10): 1 → 3 → 5 réplicas con 25 workers y `delayMs 500`.
- **Apoyo:** una revisión nueva por cada cambio de plantilla; diagnóstico con `logs show` y Log Analytics.
- **Apoyo:** `--no-wait` no espera; el borrado se verifica con `az group list`.

## Pendientes
- ~~Cleanup de los labs 2, 3 y 4~~: hecho; al reautenticarse solo quedaba `rg-ai200-aca-scale` (la plataforma había desprovisionado el resto).
- ~~Cleanup del lab 5 (`rg-ai200-aca-scale`)~~: realizado (`az group delete` lanzado el 29/10; el alumno lo da por completado el 30/10).
- Tarea 4 del lab 5 (escalado desde YAML): no ejecutada, el grupo se borró antes.
- ~~Labs 4 y 5~~: hechos y documentados.
- Corrección en clase de las 4 preguntas de LP1 y 6 de LP2.
- Siguiente: LP3 AKS.
