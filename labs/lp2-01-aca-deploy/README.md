# Lab LP2-01 · Deploy a containerized backend API to Azure Container Apps

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/01-aca-deploy-containers.html
Documentación del módulo (MS Learn): https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-container-apps/
Material de partida: `aca-deploy-python.zip` (original, sin editar) y sus ficheros extraídos (`azdeploy.py` editado, `api/`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

**Salidas reales de los comandos, saneadas: [`salidas.md`](salidas.md).**

Ejecutado en Linux (bash) contra la suscripción temporal del lab (29/10/2026). La plataforma del curso da los mismos pasos en PowerShell.

## Objetivo
Desplegar una API en contenedor en Azure Container Apps con **identidad gestionada** para descargar la imagen del ACR (sin credenciales), y configurar un **secreto** referenciado desde una variable de entorno. Comprobar después que cada cambio de configuración crea una **revisión** nueva.

## Qué se construye
```
azdeploy.py (1) → resource group + ACR + imagen ai-api:v1 (ACR Tasks)
azdeploy.py (2) → Log Analytics workspace + Container Apps environment + .env
az containerapp create    → app "ai-api" (ingress externo, puerto 8000, identidad system-assigned, AcrPull automático)
az containerapp secret set → secreto embeddings-api-key
az containerapp update     → variable EMBEDDINGS_API_KEY=secretref:… → revisión 0000002
curl /health, /, /process + az containerapp logs show
```

## Diferencias de la plataforma respecto a la guía oficial
La guía de la plataforma (Task 1) pide cambios que la guía pública no recoge:
| Cambio | Dónde | Valor |
|---|---|---|
| Región | `location` en `azdeploy.py` | `eastus` |
| Resource group | `rg` en `azdeploy.py` | `rg-ai200-aca` (elegido por nosotros) |
| Modelo | `MODEL_NAME` (única aparición del texto `gpt-5.4-mini`) | `gpt-5.1` |
| Límite de tokens | línea nueva `TPM_LIMIT = "5000"` tras `MODEL_NAME` y `"TPM_LIMIT": TPM_LIMIT` en el diccionario de `write_env_files()` | se exporta en `.env`; este módulo no lo usa en `create` |

El proyecto **no incluye `document.txt`**: la plataforma pide crearlo (`Set-Content … "This is a test document for the Azure Container Apps exercise."`; en bash, `printf '…\n' > document.txt`). Está versionado aquí con ese texto.

Task 0 de la plataforma (instalar Azure CLI x64 en Windows) no aplica en Linux.

## Cómo se relaciona con lo que ya sabes (K8s) y con el examen
- Container app ≈ Deployment + Service + Ingress; el environment ≈ cluster/namespace gestionado.
- Secreto + `secretref:` ≈ `Secret` + `secretKeyRef`.
- `--registry-identity system` ≈ `imagePullSecrets` sin secreto: identidad + rol `AcrPull`.
- Examen: `create --yaml` para config versionada, logs primero para diagnosticar, identidad gestionada para el pull (ver knowledge check del módulo 1).

## Comandos ejecutados (en orden)
Los que crean recursos los lanza el alumno.
```bash
# Entorno (proxy corporativo que re-firma TLS) — antes de CUALQUIER comando az, en cada terminal
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Task 1 · Preparación
az login --use-device-code
az extension add --name containerapp
az extension add --name log-analytics
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
cd labs/lp2-01-aca-deploy && python3 azdeploy.py      # menú: 1, 2, 4
source .env
az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv   # Succeeded

# Task 2 · Despliegue y secretos (ver "Comandos al detalle")
az containerapp create …
az containerapp secret set …
az containerapp update …
az containerapp revision list …
```

## Comandos al detalle

### 1. `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`
```
export                  → variable de entorno solo para esta terminal
REQUESTS_CA_BUNDLE      → la librería requests (que usa az) la lee como almacén de CAs
/etc/ssl/certs/ca-certificates.crt → almacén de certificados del sistema, que incluye la CA del proxy
```
- **Qué hace:** hace que `az` confíe en la CA corporativa del proxy.
- **Por qué hace falta:** el proxy re-firma el TLS; sin esto `az login` falla con `SSLCertVerificationError` o `Could not find a suitable TLS CA certificate bundle`.
- **Qué esperar:** no imprime nada. Hay que repetirlo en cada terminal nueva.
- **Trampa:** si se lanza como `! export … && az …` en una terminal normal, el `!` niega el estado del `export`, el `&&` se salta el `az` y no se ejecuta nada. El `!` solo vale en el prompt de Claude Code.

### 2. `az login --use-device-code`
```
az login            → autenticación
--use-device-code   → flujo de código de dispositivo: az da un código y una URL, el login se hace en el navegador
```
- **Qué hace:** abre sesión; el alumno pega el código en `login.microsoft.com/device`.
- **Por qué hace falta:** el **Temporary Access Pass** del lab solo vale en login interactivo (no con `-u -p`). Usar ventana de incógnito y cuenta de trabajo o escuela.
- **Qué esperar:** lista de suscripciones (una: `XLabs-…`, tenant «Lab Directory»); Enter acepta la predeterminada.

### 3. `az extension add --name containerapp` y `--name log-analytics`
```
az extension add    → instala una extensión de la CLI
--name containerapp → comandos az containerapp …
--name log-analytics→ comandos del workspace de Log Analytics
```
- **Por qué hace falta:** no vienen en la CLI base; sin ellas `az containerapp` no existe.
- **Qué esperar:** nada si va bien. Comprobar con `az extension list --query '[].name' -o tsv`.

### 4. `az provider register --namespace Microsoft.App | Microsoft.OperationalInsights | Microsoft.ContainerRegistry`
```
az provider register → habilita un proveedor de recursos en la suscripción
--namespace          → Microsoft.App (Container Apps) · OperationalInsights (Log Analytics) · ContainerRegistry (ACR)
```
- **Qué hace:** registro asíncrono; devuelve enseguida y termina en segundo plano.
- **Qué esperar:** comprobar `az provider show -n <ns> --query registrationState -o tsv` → `Registered`. Aquí ya estaban registrados.

### 5. `python3 azdeploy.py` (menú interactivo)
```
1 → resource group + ACR + az acr build de la imagen ai-api:v1 (ACR Tasks, sin Docker local)
2 → Log Analytics workspace + Container Apps environment; escribe .env y .env.ps1
3 → comprobar estado (ACR, imagen, environment)
4 → salir
```
- **Qué hace por debajo:** solo envuelve comandos `az` (group create, acr create, acr build, containerapp env create). Nombres derivados del object id del usuario: `acr<hash8>` y `aca-env-<hash8>`.
- **Edición previa:** `rg`, `location` y los cambios de la plataforma (tabla de arriba). No tocar nada más.
- **Qué esperar:** opción 3 → `Status: Succeeded` para ACR y environment, e imagen `ai-api:v1`.
- **Trampa (guía de la plataforma):** la opción 2 puede dar un error de conexión aunque el environment siga creándose; al repetirla dice «already exists» sin comprobar que haya terminado. Comprobar siempre `provisioningState`.

### 6. `source .env` y comprobación del environment
```
source .env → carga RESOURCE_GROUP, ACR_NAME, ACR_SERVER, ACA_ENVIRONMENT, CONTAINER_APP_NAME, CONTAINER_IMAGE,
              TARGET_PORT, MODEL_NAME, TPM_LIMIT, EMBEDDINGS_API_KEY, LOCATION (el .env está en .gitignore)
az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv
```
- **Qué esperar:** `Succeeded`. Si sale `Waiting`, esperar: un `create` antes de tiempo falla con `ManagedEnvironmentNotProvisioned`.
- **Resultado real:** `Succeeded`.

### 7. `az containerapp create` (Task 2) — ejecutado
```bash
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ACA_ENVIRONMENT \
    --image "$ACR_SERVER/$CONTAINER_IMAGE" \
    --ingress external \
    --target-port $TARGET_PORT \
    --env-vars MODEL_NAME=$MODEL_NAME \
    --registry-server "$ACR_SERVER" \
    --registry-identity system
```
```
az containerapp create   → crea la app y su primera revisión
--name / --resource-group→ ai-api / rg-ai200-aca
--environment            → el environment creado en la opción 2
--image                  → <acr>.azurecr.io/ai-api:v1 (ojo: tag; en producción, digest)
--ingress external       → endpoint público con FQDN y TLS gestionado
--target-port 8000       → puerto donde escucha el contenedor (el de la imagen)
--env-vars MODEL_NAME=…  → variable no sensible
--registry-server        → registry privado del que descargar
--registry-identity system → identidad gestionada system-assigned para el pull; la CLI asigna AcrPull sobre el ACR
```
- **Por qué hace falta la identidad en el create:** la primera revisión necesita poder descargar la imagen; sin credenciales falla con `ImagePullBackOff`/403.
- **Resultado real:** `Container app created. Access your app at https://ai-api.<dominio-del-environment>.eastus.azurecontainerapps.io/` (sin error de conexión, no hizo falta el arreglo de abajo).
- **Trampa (guía de la plataforma):** si da un error de conexión (`NameResolutionError`, `Max retries exceeded`), la app puede haberse creado a medias con una imagen placeholder y sin registry. Comprobar antes de reintentar: `az containerapp show … --query "{image:properties.template.containers[0].image, registries:properties.configuration.registries}"`; si la imagen no es la del ACR o `registries` es null, arreglar con `az containerapp registry set` y `az containerapp update --image …`, o borrar con `az containerapp delete` y repetir.

### 8. `az containerapp secret set` — ejecutado
```bash
az containerapp secret set -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --secrets embeddings-api-key=$EMBEDDINGS_API_KEY
```
```
secret set  → guarda un secreto en la app (no crea revisión por sí solo)
--secrets   → pares nombre=valor; nombre en minúsculas y guiones
```
- **Qué esperar:** lista de secretos con el nombre (los valores no se muestran).

### 9. `az containerapp update --set-env-vars … secretref:` — ejecutado
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key
```
```
update           → modifica la app; un cambio en la plantilla crea una revisión nueva
--set-env-vars   → añade/actualiza variables
secretref:<nombre> → el valor de la variable es el secreto, no un texto en claro
```
- **Qué hace:** crea la revisión `…--0000002` y la reinicia para aplicar el secreto.
- **Resultado real:** JSON largo (se ignora casi todo: lista de ~300 `outboundIpAddresses`, ids de suscripción/tenant/principal, que no se copian al repo). Lo que importa:
  - `identity.type = SystemAssigned` · `activeRevisionsMode = Single` · `ingress.external = true`, `targetPort = 8000`, tráfico 100 % a `latestRevision`.
  - `registries[0].identity = "system"` (pull por identidad, sin usuario ni contraseña) y `secrets = [{name: embeddings-api-key}]` (**solo el nombre, nunca el valor**).
  - `template.containers[0].env`: `EMBEDDINGS_API_KEY` con `secretRef` (no en claro) y `MODEL_NAME`, **sin `value` visible** en esta salida. No se asume que falte: se verifica con `GET /` (ver Task 3).
  - Recursos por defecto: `cpu 0.5`, `memory 1Gi`, `maxReplicas 10`, `minReplicas null` (equivale a 0, scale-to-zero), `workloadProfileName Consumption`.
  - `latestRevisionName = …--0000002` pero `latestReadyRevisionName = …--0000001` en el momento de la respuesta: la nueva todavía no estaba lista.

### 10. `az containerapp revision list -o table` — ejecutado
- **Qué esperar:** dos revisiones; la `…--0000002` con el 100 % del tráfico (modo single).
- **Resultado real:**
  ```
  Active  Replicas  TrafficWeight  HealthState  ProvisioningState  Name
  True    1         0              Healthy      Provisioned        ai-api--0000001
  True    1         100            Healthy      Provisioned        ai-api--0000002
  ```
  La revisión 1 sigue `Active` con 1 réplica y 0 % de tráfico: en modo single es la transición; la plataforma la desactiva cuando la nueva está sana (ver con otro `revision list` pasado un minuto).
- **Detalle de examen:** cada cambio en la plantilla (imagen, variables, recursos, escalado) crea revisión; `secret set` por sí solo no.

### 11. Verificación de la API (Task 3)
```bash
FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
curl -s "https://$FQDN/health"
curl -s "https://$FQDN/"
printf 'This is a test document for the Azure Container Apps exercise.\n' > document.txt
curl -s -X POST "https://$FQDN/process" -H "Content-Type: text/plain" --data-binary @document.txt
az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
```
```
FQDN=$(… -o tsv)                       → dominio público de la app (ingress.fqdn), sin comillas
curl -s                                → silencioso, sin barra de progreso
-X POST -H "Content-Type: text/plain"  → la API lee el cuerpo como texto
--data-binary @document.txt            → envía el fichero tal cual (equivale a -Body (Get-Content -Raw …) de PowerShell)
az containerapp logs show              → últimas líneas de la consola de la réplica (stdout/stderr); sin --follow no sigue en directo
```
- **Qué hace:** comprueba las tres cosas que importan tras un despliegue: ingress (llega tráfico), configuración (modelo y secreto) y logs (qué ve la app).
- **Resultados reales:**
  - `/health` → `{"status":"healthy"}`
  - `/` → `"model":{"name":"gpt-5.1"}` y `"secrets":{"embeddings_api_key_configured":true}`, `"environment":"development"`. **Aclara la duda de la salida de `update`:** la CLI no mostraba el valor de `MODEL_NAME`, pero la app sí lo tiene.
  - `/process` → JSON con entidades, frases clave y sentimiento **simulados** (mock), `statistics` (63 caracteres, 11 palabras) y `storage.path = /tmp/processed/<uuid>.json`.
  - `logs show` → conexión a la réplica de la revisión `…--0000002`; `Starting gunicorn 22.0.0`, `Listening at: http://0.0.0.0:8000`, `Using worker: sync`, dos `Booting worker` (pid 8 y 9) y las líneas de acceso `GET /health 200`, `GET / 200`, `POST /process 200`.
- **Detalles / trampas:**
  - Las líneas `MODEL_NAME=…` y `EMBEDDINGS_API_KEY configured: …` del código **no salen en los logs**: están bajo `if __name__ == "__main__"` y gunicorn importa el módulo, no lo ejecuta como principal. La comprobación fiable es `GET /`.
  - El resultado de `/process` se guarda en `/tmp/processed`, almacenamiento **efímero del contenedor**: se pierde al reiniciar o escalar. En App Service (lab 2) usábamos `/home` persistente; aquí haría falta montar un volumen (Azure Files).
  - Aparece una petición `GET /` con `User-Agent: python-requests` que no lanzamos nosotros (probable validación automática de la plataforma del lab).
  - `logs show` solo trae las líneas recientes; el histórico está en el workspace de Log Analytics del environment (KQL).
- **Examen:** logs primero para diagnosticar (M1-2 del knowledge check); `logs show --follow` para seguirlos en directo.

## Resultados
- Task 1 completada: ACR con `ai-api:v1` y environment en `Succeeded` (verificado con la opción 3 del script y con `az containerapp env show`).
- `az containerapp create`: app `ai-api` creada con ingress externo e identidad gestionada para el pull.
- Secreto + variable `secretref:` aplicados; revisión `0000002` sana con el 100 % del tráfico (la `0000001` en 0 % mientras se desactiva).
- Verificación de la API (Task 3) correcta: `/health` healthy, `/` con modelo `gpt-5.1` y secreto configurado, `/process` 200 con análisis simulado y logs de gunicorn con las tres peticiones.
- **Lab completado.** Cleanup: lo lanza el alumno (ver abajo).

## Incidencias y soluciones
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Could not find a suitable TLS CA certificate bundle` en `az login` | Proxy corporativo que re-firma TLS | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` |
| `curl` o `az` fallan con 502/503 recién desplegado | Réplica aún arrancando | Esperar un minuto y repetir |
| Comandos pegados con `!` no hacen nada | En bash normal `!` niega el estado y el `&&` se salta el siguiente comando | No usar `!` fuera del prompt de Claude Code |
| `az extension list` vacío aunque se «instalaron» | Misma causa: nunca se ejecutaron | Repetir sin `!` |

## Cleanup (lo ejecuta el alumno)
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-aca --no-wait --yes
az group exists --name rg-ai200-aca
```
La plataforma también desprovisiona los recursos al finalizar el laboratorio.

## Troubleshooting (de la guía de la plataforma)
| Problema | Comprobación |
|---|---|
| Estado base | `python3 azdeploy.py` → opción 3 (ACR, imagen y environment) |
| Autenticación y variables | `az account show`; `echo $ACR_NAME`; si está vacía, `source .env` |
| ACR | `az acr list -o table` y `ProvisioningState = Succeeded` |
| Fallo del build (`az acr build` va en silencio en el script) | ejecutar desde la raíz del proyecto (donde está `api/`); `az acr task list-runs --registry $ACR_NAME -o table`; `az acr task logs --registry $ACR_NAME --run-id <id>`; si una run se queda en `Queued` más de un par de minutos: `az acr task cancel-run … --run-id <id>` y repetir `az acr build` |
| `ImagePullBackOff` / 403 / unauthorized | `az containerapp identity show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP` (identidad system-assigned) y rol `AcrPull` sobre el ACR (puede tardar 1-2 min en propagarse) |
| Arranque o errores de la app | `az containerapp logs show … --follow`; 502/503 justo tras desplegar: esperar un minuto; `az containerapp revision list … -o table` |
| Secreto | `az containerapp secret list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table`; llamar a `/` y mirar `embeddings_api_key_configured` |

Recuerda `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` antes de cualquier `az`.
