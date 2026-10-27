# LP1 · Alojamiento de aplicaciones en contenedores (ACR + App Service)

Resumen propio de la presentación del instructor (no se reproduce el material con copyright). Pensado para un perfil SysOps/K8s: se indica el equivalente en Kubernetes cuando existe.

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

| Pregunta | Respuesta | Por qué |
|---|---|---|
| M1-1 Builds inconsistentes en workstations | **A** · ACR Tasks quick build | Build en entorno controlado en la nube |
| M1-2 Misma versión en todos los nodos aunque se reutilice el tag | **A** · manifest digest | El tag es mutable; el digest no |
| M2-1 Contenedor en el 8000, errores de conexión | **A** · `WEBSITES_PORT=8000` | App Service solo asume 80/8080 |
| M2-2 Que la URL de staging no pase a producción | **A** · slot setting | Los slot settings no viajan en el swap |

## Labs de este bloque
1. [Build and run a container image with ACR Tasks](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html) (~30 min)
2. [Deploy a container to Azure App Service](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html) (~30 min)
3. [Sidecar con modelo local](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/03-app-svc-sidecar.html) (extra; confirmar si se hace)

## Preguntas de discusión en grupo (para preparar)
- ¿Qué va en la imagen y qué se externaliza como configuración? ¿Cambia para cargas de IA (rutas de modelo, API keys, flags)?
- ¿Qué guardarraíles evitan errores de tag, puerto o slot antes de llegar a producción?
- Mutable (tags estables, settings editables) vs inmutable (digests, imágenes bloqueadas): cuándo cada uno.
