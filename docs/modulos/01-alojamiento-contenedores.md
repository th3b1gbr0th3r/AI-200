# LP1 · Alojamiento de aplicaciones en contenedores (ACR + App Service)

Resumen propio de la presentación del instructor (no se reproduce el material con copyright). Pensado para un perfil SysOps/K8s: se indica el equivalente en Kubernetes cuando existe.

## Documentación oficial y nuestros pasos

Learning path de MS Learn: [Implementación del hospedaje de aplicaciones de contenedor en Azure](https://learn.microsoft.com/es-es/training/paths/implement-container-app-hosting-azure/) (3 módulos). Las diapositivas del instructor cubren los dos primeros.

| Módulo | Documentación oficial (MS Learn) | Lab oficial | Nuestros pasos detallados |
|---|---|---|---|
| 1 · ACR | [Almacenamiento y administración de contenedores en Azure Container Registry](https://learn.microsoft.com/es-es/training/modules/store-manage-containers-azure-container-registry/) | [Build and run a container image with ACR Tasks](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html) | [`labs/lp1-01-acr-tasks/README.md`](../../labs/lp1-01-acr-tasks/README.md) |
| 2 · App Service | [Implementación de contenedores en Azure App Service](https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-app-service/) | [Deploy a container to Azure App Service](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html) | [`labs/lp1-02-app-service/README.md`](../../labs/lp1-02-app-service/README.md) |
| 3 · Sidecar | [Ejecutar aplicaciones de IA con sidecar en Azure App Service](https://learn.microsoft.com/es-es/training/modules/deploy-sidecar-azure-app-service/) | [Deploy an AI API with a local model-serving sidecar](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/03-app-svc-sidecar.html) | pendiente (extra; confirmar con el docente) |

**Módulo 3 (no está en las diapositivas):** según su descripción oficial, usa *sidecars* de App Service para ejecutar componentes de IA estrechamente acoplados junto al contenedor principal de la app Linux, y cubre la descarga segura de imágenes, la comunicación local, los archivos compartidos y el diagnóstico de toda la aplicación. Detalle por completar al leerlo.

## Módulo 1 · Azure Container Registry (ACR)

**Qué es:** registro privado gestionado de imágenes Docker y artefactos OCI (Helm charts incluidos). Se integra con AKS, Container Apps y App Service. Tiers: Basic, Standard, Premium (geo-replicación solo en Premium).

**Jerarquía:** registry → repository → artifact. Un *tag* es una referencia **mutable** (`api:v1.2.0`); el *digest* (`api@sha256:…`) es **inmutable**. Las capas se deduplican entre imágenes.

> K8s: es lo mismo que cualquier registry; la regla de oro de fijar por digest en un `Deployment` se aplica igual.

**ACR Tasks** (build en la nube, sin Docker local):
- *Quick task*: `az acr build` → build + push en un comando.
- Tarea con trigger (commit en Git, actualización de imagen base, cron): `az acr task create … --context <repo>#main --image api:{{.Run.ID}}`.
- Multi-step: YAML con build → test → push.

**Versionado y ciclo de vida:**
- Tags únicos para producción (build ID, SHA de Git, timestamp); tags estables solo para imágenes base.
- Bloquear una imagen: `az acr repository update --image api:v1.2.0 --write-enabled false`.
- Limpieza de imágenes sin tag: tarea programada con `acr purge --untagged --ago 7d`.

## Módulo 2 · Azure App Service con contenedores

**Qué es:** PaaS para contenedores Linux. Trae autoescalado, *deployment slots*, TLS terminado en la plataforma (el contenedor recibe HTTP).

**Despliegue:**
- Imagen desde ACR (recomendado), Docker Hub, GHCR o registry propio.
- Autenticación a ACR: **managed identity con rol `AcrPull`** (producción); credenciales admin solo dev/test.
- Despliegue continuo vía webhook de ACR.

**Runtime:**
- *Startup command* sustituye el `CMD` del Dockerfile (no el `ENTRYPOINT`).
- `WEBSITES_PORT` si el contenedor no escucha en 80/8080 (**el fallo más común**).
- Almacenamiento persistente compartido entre instancias.
- *Always on* (Basic+) evita la descarga por inactividad (~20 min); *health check* cada minuto saca del balanceo las instancias que fallan.

**Configuración:**
- App settings → variables de entorno (cifradas en reposo).
- *Slot settings*: se quedan en su slot al hacer swap (URLs de entorno, feature flags).
- Referencias a Key Vault: `@Microsoft.KeyVault(SecretUri=…)`, requieren managed identity con acceso al vault.
- Connection strings con prefijo de tipo (`SQLAZURECONNSTR_`); en apps no .NET mejor app settings.

**Diagnóstico:** logs de contenedor (stdout/stderr + eventos de plataforma, hay que **activarlos explícitamente**), `az webapp log tail`, consola Kudu (SCM), envío a Log Analytics (`ConsoleLogs`, `HTTPLogs`, `PlatformLogs`) para KQL y alertas.

## Knowledge check (respuestas)
Detalle de cada opción y por qué fallan las demás: [`docs/tests/lp1-knowledge-check.md`](../tests/lp1-knowledge-check.md).

| Pregunta | Respuesta | Por qué |
|---|---|---|
| M1-1 Builds inconsistentes en workstations | **A** · ACR Tasks quick build | Build en entorno controlado en la nube |
| M1-2 Misma versión en todos los nodos aunque se reutilice el tag | **A** · manifest digest | El tag es mutable; el digest no |
| M2-1 Contenedor en el 8000, errores de conexión | **A** · `WEBSITES_PORT=8000` | App Service solo asume 80/8080 |
| M2-2 Que la URL de staging no pase a producción | **A** · slot setting | Los slot settings no viajan en el swap |

## Labs de este bloque
1. [Build and run a container image with ACR Tasks](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html) (~30 min) — hecho: `labs/lp1-01-acr-tasks/`
2. [Deploy a container to Azure App Service](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html) (~30 min) — hecho hasta el paso 12: `labs/lp1-02-app-service/`
3. [Sidecar con modelo local](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/03-app-svc-sidecar.html) (extra; confirmar si se hace)

## Preguntas de discusión en grupo (para preparar)
- ¿Qué va en la imagen y qué se externaliza como configuración? ¿Cambia para cargas de IA (rutas de modelo, API keys, flags)?
- ¿Qué guardarraíles evitan errores de tag, puerto o slot antes de llegar a producción?
- Mutable (tags estables, settings editables) vs inmutable (digests, imágenes bloqueadas): cuándo cada uno.

## Notas de la clase del 27/10/2026 (a partir de la transcripción de Zoom)
Resumen propio del contenido técnico y organizativo; sin nombres de personas. La transcripción automática es ruidosa y no se publica.

**Organización del curso**
- Ahora los *módulos* son *lecciones* y la presentación completa es el *learning path*. El LP1 tiene 2 lecciones; los 3 primeros learning paths de los 9 son de contenedores.
- Siguiente: LP2 Azure Container Apps (el día siguiente); después AKS (LP3). Las 4 preguntas del knowledge check se corrigen al empezar la siguiente clase.
- Sesiones de 18:00 a 22:00 con descanso de ~20 min. A partir del lab 4-5 se empieza a tocar código; hasta entonces son comandos.
- Los labs duran 2 h, **no se pueden guardar** y al finalizar el laboratorio en la plataforma se desprovisionan los recursos (el coste lo asume el proveedor). Aun así se recomienda borrar el resource group como práctica. "Finalizar" marca el lab como completado; "Descartar" se usa si falló o no hubo tiempo.
- El docente recomienda **no memorizar comandos** (caen en el examen, pero los tests de práctica los cubren) y usar el portal para localizar visualmente ACR, repositorios, tags/digests, plan y asignaciones de rol.
- El perfil del curso se registra en Microsoft Learn el último día.

**ACR**
- "Docker Hub de Azure": almacén central de imágenes y artefactos OCI (también charts de Helm), integrado con AKS, Container Apps y App Service. Servicio PaaS: no hay infraestructura que gestionar.
- Dominio `<nombre>.azurecr.io`; registry → repositorio → artefacto. Referencia por tag (mutable) o por digest (inmutable).
- Tiers: Basic (pruebas, hardware limitado), Standard (producción) y Premium (**geo-replicación**: la imagen cerca de los servicios que la consumen). Sin Premium, el ACR vive en una sola región y despliegues a otras regiones tiran de ahí con más latencia.
- ACR Tasks también sirve para **probar** una imagen, no para ejecutarla en producción.
- Se bloquean las imágenes en producción para evitar borrados y se usan políticas de retención.

**App Service**
- Plan de precios = esqueleto de cómputo: Basic escala solo de forma manual; en Premium hay autoescalado por reglas. El número de *deployment slots* depende del plan.
- Slots: p. ej. producción y desarrollo/testing sobre los mismos recursos, con URL propia; swap entre slots y reparto de tráfico por porcentaje (p. ej. 90/10) para despliegues graduales. No es obligatorio usarlos.
- Se puede desplegar en modo integrado en una VNet propia si se quiere acceso privado.
- Un contenedor personalizado no declara lenguaje: es una imagen que se despliega tal cual (hay que vigilar la versión del runtime que lleve dentro).
- Comando de arranque: sustituye al comando del Dockerfile. Puerto: 80/8080 por defecto, configurable con `WEBSITES_PORT`. TLS lo termina la plataforma.
- Almacenamiento: por defecto efímero; opciones persistentes (se ampliarán en AKS: disco y Azure Files).
- Always On evita la descarga a los ~20 min de inactividad; el health check se lanza cada minuto y saca de rotación las instancias que fallan.
- Observabilidad (se amplía en el último módulo): logs de contenedor, log stream, sitio SCM/Kudu, envío a Log Analytics con KQL, Application/Container Insights.
- Referencias a Key Vault desde los app settings: se verán en algún lab.

**Identidad gestionada**
- Cada recurso autenticado con Entra puede tener una identidad gestionada: la plataforma genera el token y el servicio destino (ACR, Storage, base de datos) lo valida; no hace falta Key Vault para ello. Se concede el permiso en el IAM del recurso destino (aquí, `AcrPull` sobre el ACR). Hay system-assigned y user-assigned.
- Se verifica en el portal: ACR → Control de acceso (IAM) → Asignaciones de roles, donde aparece la web app con `AcrPull`.

**Problemas de los labs observados en la clase**
- El lab usa una **suscripción compartida por todo el grupo**: aparecen cuotas por región. Si el plan falla con cuota 0, cambiar de región (la guía recomienda `canadacentral` en el lab 2 y `eastus` en el lab 1) y escribirla en minúsculas y sin espacios.
- `az login`: elegir cuenta de trabajo o escuela (no personal); la ventana puede quedar detrás de VS Code (minimizar). Si falla, repetir el comando; en último caso reiniciar la máquina virtual o relanzar el lab.
- Extraer el zip del lab en una carpeta propia (p. ej. `C:\lab`) y abrir esa carpeta en VS Code, para que las rutas relativas del script funcionen.
- Si se edita mal el SKU de la línea 224 de `azdeploy.py` (hay que sustituir el valor `P0v3` por `B1`, sin tocar la clave `--sku`), la opción 2 del menú falla.
- El fichero `.env.ps1` lo genera el script al ejecutar la opción 2; sin cargarlo, los comandos siguientes fallan.
- Los comandos de la guía están en PowerShell; en otras plataformas de labs cambia la sintaxis.
- Un `az ... --acr-use-identity` puede imprimir un aviso de "no credential" aunque haya funcionado: comprobar el resultado.
- El `az` de los pasos puede fallar a la primera; repetir una o dos veces.
