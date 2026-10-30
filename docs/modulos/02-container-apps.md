# LP2 · Desplegar y gestionar apps en Azure Container Apps (ACA)

Resumen propio de la presentación del instructor (no se reproduce el material con copyright). Pensado para un perfil SysOps/K8s: se indica el equivalente en Kubernetes cuando existe.

## Documentación oficial

Learning path de MS Learn: [Implementación y administración de aplicaciones en Azure Container Apps](https://learn.microsoft.com/es-es/training/paths/deploy-manage-apps-azure-container-apps/) (4 módulos).
1. [Implementación de contenedores en Azure Container Apps](https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-container-apps/)
2. [Administración de contenedores en Azure Container Apps](https://learn.microsoft.com/es-es/training/modules/manage-containers-azure-container-apps/)
3. [Escalado de contenedores en Azure Container Apps](https://learn.microsoft.com/es-es/training/modules/scale-containers-azure-container-apps/)
4. [Ejecute código generado por IA de forma segura en sesiones dinámicas](https://learn.microsoft.com/es-es/training/modules/dynamic-sessions-azure-container-apps/)

## Módulo 1 · Desplegar contenedores en ACA

**Qué es:** plataforma de contenedores serverless. No hay plano de control de Kubernetes que gestionar (por debajo corre sobre K8s, pero no se expone). Modelo de despliegue por **revisiones**, ingress integrado (externo o interno), secretos y variables nativos, integración con ACR, Azure Monitor, VNet e identidades gestionadas.

**Environment:** frontera compartida de red, DNS interno y logging para un grupo de apps.
- Separar por ciclo de vida (dev/test/prod) y por red (las apps que se hablan en privado, juntas).
- Decidir el destino de logs (Log Analytics) **antes** de producción.

> K8s: el environment es aproximadamente un cluster/namespace gestionado; la *container app* es un Deployment + Service + Ingress en uno.

**Tres vías de despliegue:**
| Vía | Cuándo |
|---|---|
| `az containerapp up` | Prototipo rápido; crea el environment si no existe |
| `az containerapp create` | Control explícito sobre un environment ya creado |
| `az containerapp create --yaml app.yaml` | Producción: configuración en Git, revisable en code review |

Regla práctica: prototipar con `up/create`, pasar a YAML para repetibilidad. `az containerapp update` cambia imagen/config y **cada cambio crea una revisión nueva**.

**Variables y secretos:**
- Variables de entorno: lo no sensible (nivel de log, flags, URLs de dependencias). La misma imagen corre en dev/stage/prod con valores distintos.
- Secretos: claves API, credenciales. Se guardan aparte, se rotan sin reconstruir la imagen y pueden venir de Key Vault.
- *Secret reference*: la variable de entorno apunta al secreto (`secretref:`), así el código lee una variable normal. Los valores no van en el YAML ni en el historial del shell.

> K8s: `Secret` + `env.valueFrom.secretKeyRef`.

**Autenticación para descargar la imagen (ACR u otros):**
- Usuario/contraseña: vale con cualquier registry, rápido para probar, pero más secretos que rotar.
- **Identidad gestionada (recomendado para ACR):** sin credenciales, solo rol `AcrPull` (mínimo privilegio), `--identity system` / `--registry-identity`.
- La config del registry es independiente de la de la app: un fallo de pull suele parecer un error de autenticación.

**Verificar un despliegue (orden):** logs → revisiones → réplicas.
- *Console logs*: salida de la app (errores de arranque, variables que faltan, conexiones fallidas).
- *System logs*: eventos de plataforma (pull de imagen, escalado, probes).
- Revisiones: ¿existe la nueva y está sana/activa? Incluir las inactivas para investigar.
- Réplicas: scale-to-zero, crash loops, cold starts, nº de instancias bajo carga.

## Módulo 2 · Gestionar contenedores en ACA (operaciones de día 2)

**Identidad de imagen:** el tag es mutable, el **digest es inmutable**. En producción referenciar por digest para trazar qué artefacto corre en cada incidente (`imagen@sha256:…`).

**Flujo de revisiones:** actualizar → verificar salud → mover tráfico. Desactivar la revisión problemática (se conserva para investigar) en vez de borrarla; definir cuántas revisiones inactivas se retienen.

**Acciones de ciclo de vida y su alcance:**
| Acción | Efecto | Cuándo |
|---|---|---|
| Desactivar revisión | Aísla una sola release mala | **Primer paso más seguro** |
| Restart | Limpia estado transitorio | Deadlocks, procesos colgados |
| Stop | Garantiza cero tráfico a toda la app | Incidentes graves |

**Patrones de fallo a validar:** pull de imagen (credenciales), puertos (contenedor vs ingress), variables/secretos que faltan, probes (ruta equivocada, timeout corto), presión de recursos (throttling de CPU, OOM).

**Troubleshooting repetible:** identificar la revisión que falla → seguir logs mientras se reproduce → comparar la config de la revisión sana con la fallida → arreglo dirigido y verificar la siguiente revisión.
Logs estructurados: incluir request ID, revision ID, versión del modelo y latencias de dependencias; **no** registrar contenido sensible (prompts, documentos).

**Health probes:**
- *Readiness*: decide si la réplica recibe tráfico (protege la carga del modelo y el warmup).
- *Liveness*: detecta bloqueos y provoca reinicio.
- Para servicios de IA: `initialDelaySeconds` que cubra la carga del modelo, `failureThreshold` generoso; el endpoint de probe **no debe depender de servicios externos**.
- Si fallan nada más desplegar: comprobar que el servidor HTTP escucha en el puerto/ruta del probe y que el timeout da margen.

> K8s: idénticos a `readinessProbe`/`livenessProbe`.

**Dimensionar:** throttling de CPU → más CPU por réplica; reinicios por OOM → más memoria por réplica. Coste = tamaño por réplica × nº de réplicas.
- API síncrona: mínimo de réplicas > 0 para evitar cold starts (latencia).
- Worker en segundo plano dirigido por eventos: scale-to-zero (throughput/coste).
- Medir antes de cambiar, cambiar **una variable cada vez**, reevaluar tras cambios de versión del modelo.

## Módulo 3 · Escalar contenedores en ACA

Escalado horizontal automático basado en **KEDA** (por debajo), con scale-to-zero y reparto de tráfico entre revisiones.

**Definición de escalado:** límites (mín/máx réplicas, 0 a 1000), reglas (triggers) y comportamiento (polling, cool-down, estabilización). Con varias reglas, **gana la que pide más réplicas**.

**Reglas integradas:**
| Regla | Mide | ¿Escala a 0? |
|---|---|---|
| HTTP | Peticiones concurrentes por réplica (por defecto 10) | Sí |
| TCP | Conexiones concurrentes (protocolos persistentes) | Sí |
| CPU | % de utilización | **No** |
| Memoria | % de consumo | **No** |

**Escaladores KEDA:**
- Nativos de Azure: Service Bus (mensajes en cola/tema), Event Hubs (lag por partición), Storage Queue, Blob (nº de blobs).
- Otros: Kafka (lag del consumer group), Redis (longitud de lista/stream), **Cron** (pre-escalado por horario), Prometheus (PromQL propio).
- KEDA consulta la fuente cada 30 s y divide métrica actual / umbral para obtener las réplicas. Autenticación: identidad gestionada (recomendado) o cadena de conexión como secreto.
- Combinar: **cron** fija la capacidad base a una hora y **HTTP/eventos** atienden la demanda real.
- Migrar desde KEDA en K8s: mapear el tipo de `ScaledObject` a regla de ACA, copiar metadata y parámetros de auth, sustituir `TriggerAuthentication` por secretos o identidad.

**Recursos por contenedor:** CPU en cores, memoria en GiB; la memoria debe ser al menos 2× el valor de CPU (según la presentación). Pasarse de memoria **reinicia** la réplica; pasarse de CPU la **ralentiza** (throttling) sin reiniciar. Réplicas pequeñas escalan con más precisión pero más a menudo.

**Modos de revisión:**
| Modo | Comportamiento |
|---|---|
| Single (por defecto) | Una revisión activa; la nueva sustituye a la vieja tras pasar los health checks (zero-downtime automático); sin reparto de tráfico |
| Multiple | Varias activas a la vez; reparto por % (canary, blue-green, A/B); hay que desactivar las viejas a mano |

*Revision labels*: URLs con nombre para acceder a una revisión concreta sin afectar a producción; mover la etiqueta permite el cambio blue-green.

> K8s: single ≈ rolling update; multiple + pesos ≈ Argo Rollouts/service mesh; el escalado ≈ HPA/KEDA `ScaledObject` (con scale-to-zero que HPA nativo no da).

## Módulo 4 · Código generado por IA en sesiones dinámicas de ACA

Este módulo forma parte del learning path de MS Learn («Implementación y administración de aplicaciones en Azure Container Apps», 4 módulos) pero **no está en las diapositivas del instructor**; el planning del docente del 29/10 no lo incluye (labs 3-5 = módulos 1-3). Resumen a partir de los objetivos publicados (módulo de 8 unidades, ~84 min, nivel intermedio, requiere Python):
- Cómo las sesiones dinámicas **aíslan** el código generado por IA o enviado por usuarios (entornos aislados por sesión).
- Elegir entre el **intérprete de código integrado** y un **grupo de sesiones de contenedor personalizado**.
- Configurar capacidad del grupo, ciclo de vida de la sesión y acceso de red saliente.
- Usar **identificadores de sesión** para ejecutar código e intercambiar ficheros desde el código de la app.
- Gestionar expiración de sesión, límites de ejecución, timeouts y ejecuciones fallidas.

_(Detalle por completar al leer el módulo o hacer el lab 4.)_

## Knowledge check (respuestas)

| Pregunta | Respuesta | Por qué |
|---|---|---|
| M1-1 Despliegue consistente y versionado en Git | **A** · `create --yaml` con YAML en control de versiones | La config se revisa como código; `update --set-env-vars` es imperativo y las tags no versionan la config |
| M1-2 La app no arranca tras actualizar la imagen; feedback rápido | **A** · `az containerapp logs show` | Los logs son la señal más rápida; revisiones y réplicas vienen después |
| M2-1 Trazabilidad al desplegar a producción | **A** · referenciar por digest | Inmutable; `latest` es mutable y reconstruir en local no es reproducible |
| M2-2 Latencia alta y throttling de CPU | **A** · más CPU por réplica, luego reevaluar reglas | El throttling es por réplica; desactivar la revisión o cambiar digest→tag no lo resuelve |
| M3-1 Procesar cola de Service Bus y escalar a 0 | **C** · `--min-replicas 0` + regla `azure-servicebus` | CPU no escala a 0 y HTTP no mira la cola |
| M3-2 5 réplicas listas a las 8:00 y scale-to-zero de noche | **A** · cron + HTTP | Cron pre-escala por horario; HTTP cubre el tráfico; `min=5` impediría el scale-to-zero |

> Nota: el resumen del módulo 3 de las diapositivas habla de Cosmos DB (índices, vectores, consistencia); es un copy-paste erróneo del material, no corresponde a ACA.

## Labs de este bloque
1. [Deploy a containerized backend API to Container Apps](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/01-aca-deploy-containers.html) (~30 min) — identidad gestionada para pull de ACR + secretos como variables.
2. [Diagnose and fix a failing deployment](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/02-aca-manage-containers.html) (~30 min) — revisiones, logs y CLI para aislar fallos.
3. [Configure autoscaling for an API using KEDA](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/03-aca-scale-containers.html) (~30 min) — API simulada con escalado por peticiones HTTP concurrentes.
4. [Execute AI-generated code securely in ACA dynamic sessions](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/04-aca-dynamic-sessions.html) (extra; no está en el planning del 29/10)

## Preguntas de discusión en grupo (para preparar)
- ¿Qué se diseña de antemano (fronteras de environment, manejo de secretos, acceso al registry, config de runtime) y qué se puede refinar tras la primera release?
- Iterar rápido vs releases seguras: ¿cómo se equilibra cuando una imagen nueva puede traer fallos de runtime o de probes? (revisiones + readiness + modo multiple con tráfico gradual)
- Tráfico impredecible en cargas de IA: ¿escalado HTTP simple, event-driven con KEDA o gestión deliberada de tráfico entre revisiones? ¿Cómo no pagar de más?

## Notas de la clase del 29/10/2026 (a partir de la transcripción de Zoom)
Resumen propio del contenido técnico y organizativo, ordenado por temas; sin nombres de personas. La transcripción automática es ruidosa, cubre solo hasta el inicio de los labs y no se publica.

**Organización del curso y del día**
- Orden del día: corrección del test de LP1, teoría de las 3 lecciones de LP2 seguidas y después los 3 labs de la plataforma (`LP02M01..03`). Se junta toda la teoría para ir a la par; quien termine antes puede marcharse.
- Los labs son **independientes entre sí** (se pueden repetir, o hacer en otro orden), aunque se hacen en orden para ir acompasados; los ya hechos aparecen como *review lab*. Es poco habitual que cada módulo tenga su lab.
- Todos siguen un patrón parecido: script de Python con menú numerado que aprovisiona recursos. Se recomienda **leer el script** (qué funciones llama) y conectarse al **portal** con las mismas credenciales: cada servicio tiene su icono y quien administra sistemas lo mira ahí.
- El test del día (carpeta compartida) se hace al terminar los labs y se corrige al inicio de la siguiente clase (el docente dijo «mañana»; la próxima sesión es el martes, confirmar). Siguiente tema: AKS (LP3).

**Examen**
- Habrá muchas preguntas tipo test como las de los knowledge check, pero más difíciles: normalmente 4 o 5 opciones (algunas de selección múltiple), arrastrar y soltar, desplegables y casos de estudio. Las respuestas del test de LP1 son todas la A (ver [`docs/tests/lp1-knowledge-check.md`](../tests/lp1-knowledge-check.md)).
- No memorizar comandos; sí entender qué hace cada pieza.

**Contexto: ACI, ACA y AKS**
- **ACI** (Azure Container Instances): PaaS que oculta una VM; vale para un contenedor o un *container group*, pero sin escalado ni control de versiones. No se estudia.
- **AKS**: Kubernetes gestionado (martes). **ACA**: plataforma propia de Microsoft construida sobre Kubernetes, **sin acceso al plano de control ni al sistema operativo**; puede aparecer un resource group adicional gestionado por la plataforma: se mira, no se toca.
- Microsoft alude a la IA con intención de marketing; el contenido de contenedores es el mismo.

**Environments y despliegue**
- El **environment** se aprovisiona primero: aísla las apps entre sí y comparte red, DNS interno y logs (Azure Monitor). Separar por ciclo de vida (dev/test/prod) y por red; decidir el destino de logs antes de producción.
- Vías: `up` (rápida, decide ella), `create` (más control, environment existente) y `--yaml` (configuración revisable como código; en el lab se lanzará una revisión nueva cambiando el YAML). Azure documenta sobre todo en JSON; Bicep y Terraform van por el lado de IaC.
- El script del lab genera un fichero de variables que **hay que cargar** antes de seguir (`.env`/`.env.ps1`).

**Secretos, registro e identidad**
- Variables de entorno para lo no sensible y **secretos** aparte, rotables sin reconstruir la imagen. No dejar valores en YAML ni en el historial de comandos; sí se puede **referenciar la URI de Key Vault** (módulo posterior): si se expone solo se ve dónde está, no el valor.
- Pull de imágenes: usuario y contraseña vale con cualquier registro (ACR, Docker Hub, GitHub) pero hay que rotarlos; la **identidad gestionada** solo aplica a recursos de Azure autenticables con Entra, no deja credenciales y se concede con `AcrPull` (mínimo privilegio). `--identity system` para ACR.

**Operación (día 2) y monitorización**
- Verificar: **logs primero** (consola = salida de la app; sistema = eventos de plataforma como pull o escalado), luego revisiones (incluidas las inactivas) y réplicas.
- Tag mutable, **digest inmutable**: en producción, digest para trazar la revisión exacta.
- **Desactivar, no eliminar** las revisiones con problemas; definir retención de las inactivas. A veces es más rápido rehacer desde cero y analizar después.
- Stop = tráfico 0 (incidentes) · restart = limpia estado (procesos atascados) · desactivar revisión = aísla una versión mala (lo más seguro).
- Fallos habituales: credenciales del registro, puertos, secretos o variables ausentes, probes y presión de recursos (OOM, throttling).
- Logs estructurados con ID de petición, revisión y versión del modelo, y latencias de dependencias (para saber si el cuello de botella es externo); sin contenido sensible.
- **Monitorizar cuesta** (Azure Monitor, Application Insights, Container Insights son de pago por uso): ser preciso, no monitorizar todo.

**Health probes**
- Son los *health checks* de toda la vida. Dar margen de arranque (delay y umbral de fallos generosos) para evitar falsos positivos durante el calentamiento; que no dependan de servicios externos. Si fallan nada más desplegar: puerto, ruta (las URI son largas y fáciles de equivocar) y timeout.

**Dimensionado y coste**
- CPU throttling → más CPU por réplica · OOM → más memoria. Coste = tamaño × nº de réplicas.
- API síncrona: mínimo de réplicas para evitar *cold start*. Worker dirigido por eventos: escalar a 0 (más rendimiento por coste, más latencia al arrancar).
- Cambiar **una variable cada vez**, medir y reevaluar. A veces pocas máquinas grandes salen más baratas que muchas pequeñas (caso real de escritorios virtuales).
- Memoria al menos 2× la CPU (2 CPU → 4 GiB). Pasarse de memoria reinicia; pasarse de CPU ralentiza.

**Escalado y KEDA**
- Vertical (más CPU/RAM por instancia) frente a horizontal (*scale out/in*, más réplicas tras un balanceador transparente). También hay que **desescalar**, para no quedarse en el máximo.
- Límite de 0 a 1000 réplicas, impuesto por el balanceador básico de Azure; poner un máximo bajo al principio (en el lab se fija) para no arruinarse.
- Las reglas son disparadores sobre valores medios en un periodo (ejemplo: CPU media > 70 % durante 10 min), no sobre picos puntuales; no todo es CPU.
- Integradas: **HTTP** (10 peticiones concurrentes por réplica por defecto), TCP, CPU y memoria (**estas dos no escalan a 0**).
- **KEDA** = Kubernetes Event-Driven Autoscaling; consulta cada 30 s. Service Bus (hay lab), Event Hubs (no se estudia; sí Event Grid), Storage Queue y Blob; Kafka, Redis (módulo propio), **Cron** (pre-escalado planificado, p. ej. 8:00-17:00) y Prometheus. Autenticación con identidad gestionada o cadena de conexión en secreto.
- Los escaladores se **combinan** (cron para la base, HTTP/eventos para la demanda); gana el que pide más réplicas dentro del mínimo y máximo.

**Revisiones y reparto de tráfico**
- **Single**: una activa; se hace el *cutover*. **Multiple**: varias activas con reparto por porcentaje (probar una versión nueva con pocos usuarios; si las incidencias se concentran en ella, es la sospechosa). **Etiquetas de revisión**: URL propia para pruebas; se parece al swap entre *deployment slots* de App Service.
- El lab 5 es el que más gustó al docente: se escala por peticiones HTTP concurrentes y se satura la API.
