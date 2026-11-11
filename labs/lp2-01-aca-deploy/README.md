# Lab LP2-01 · Deploy a containerized backend API to Azure Container Apps (plataforma: Lab 3 · AI-200-LP02M01)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/01-aca-deploy-containers.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)). Módulo en MS Learn: https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-container-apps/
- **Estado (29/10/2026): hecho completo** (Task 1, 2 y 3 de la plataforma). **Cleanup no verificado con `az group exists`:** el alumno no llegó a lanzar el `delete` de este grupo; esa misma tarde, al limpiar el [LP2-03](../lp2-03-aca-scale/README.md#cleanup-obligatorio-al-acabar), `az group list` ya no mostraba `rg-ai200-aca` (la plataforma lo había desprovisionado).
- **Conversación con Claude Code:** no se conserva (es anterior a la exportación de conversaciones). Sesión del día: [`sesiones/2026-10-29-sesion-03-container-apps.md`](../../sesiones/2026-10-29-sesion-03-container-apps.md).
- Lab anterior: [LP1-02](../lp1-02-app-service/README.md) · Lab siguiente: [LP2-02](../lp2-02-aca-manage/README.md).
- Material: `aca-deploy-python.zip` (original sin editar), `azdeploy.py` (editado), `api/` y `document.txt`. Origen MIT: [`../NOTICE.md`](../NOTICE.md). Qué hace el script por dentro: [`scripts/lp2-01-aca-deploy/README.md`](../../scripts/lp2-01-aca-deploy/README.md). Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

Ejecutado en Linux (bash); la plataforma da los mismos pasos en PowerShell. Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Sin IDs de suscripción/tenant/principal ni usuario del lab; los sufijos hash del script salen como `<hash>`. Prompt abreviado a `$`.

## Qué se construye y para qué
**Objetivo en cristiano:** subir una API en contenedor a Container Apps (el «Kubernetes sin cluster» de Azure) de forma que la app **descargue su imagen del ACR sin contraseñas** (identidad gestionada) y lea una **clave como secreto**, no en claro. Después se comprueba que cada cambio de configuración genera una **revisión** nueva, igual que un rollout de un Deployment.

```
azdeploy.py 1 → resource group rg-ai200-aca + ACR acr<hash> + imagen ai-api:v1 (az acr build, sin Docker local)
azdeploy.py 2 → Container Apps environment aca-env-<hash> (+ Log Analytics) + .env
az containerapp create     → app "ai-api": ingress externo :8000, identidad system-assigned, AcrPull automático → revisión 0000001
az containerapp secret set → secreto embeddings-api-key (no crea revisión)
az containerapp update     → EMBEDDINGS_API_KEY=secretref:embeddings-api-key → revisión 0000002
curl /health, /, /process + az containerapp logs show → comprobar ingress, configuración y logs
```

**Traducción a Kubernetes:** container app ≈ Deployment + Service + Ingress; environment ≈ cluster/namespace gestionado; secreto + `secretref:` ≈ `Secret` + `secretKeyRef`; `--registry-identity system` ≈ `imagePullSecrets` pero sin secreto (identidad + rol `AcrPull`); revisión ≈ ReplicaSet de un rollout.

**Para el examen:** identidad gestionada para el pull, `secretref:` para secretos, logs primero para diagnosticar, `create --yaml` para configuración versionada (knowledge check del módulo 1).

### Diferencias de la plataforma respecto a la guía oficial
| Cambio | Dónde | Valor |
|---|---|---|
| Región | `location` en `azdeploy.py` | `eastus` |
| Resource group | `rg` en `azdeploy.py` | `rg-ai200-aca` (elegido por nosotros) |
| Modelo | `MODEL_NAME` (única aparición de `gpt-5.4-mini`) | `gpt-5.1` |
| Límite de tokens | línea nueva `TPM_LIMIT = "5000"` tras `MODEL_NAME` y `"TPM_LIMIT": TPM_LIMIT` en `write_env_files()` | se exporta en `.env`; este lab no lo usa |
| `document.txt` | no viene en el zip | la plataforma pide crearlo (paso 13) |
| Task 0 (instalar Azure CLI en Windows) | — | no aplica en Linux |

La API es una **simulación** (Flask + gunicorn): `MODEL_NAME` es solo una variable; no se llama a ningún modelo.

---

## Paso 0 · Preparar la terminal (proxy de empresa)
**Por qué:** el proxy de empresa re-firma el TLS; sin decirle a `az` (Python `requests`) que confíe en el almacén de CAs del sistema, `az login` falla con `SSLCertVerificationError` o `Could not find a suitable TLS CA certificate bundle`. Hay que repetirlo en **cada terminal nueva**.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
Salida: ninguna (es normal).

✅ **Comprobación:**
```bash
echo "$REQUESTS_CA_BUNDLE"
```
Debe salir `/etc/ssl/certs/ca-certificates.crt`. Si sale vacío, el `export` se hizo en otra terminal: repítelo aquí.

⚠️ **Lo que pasó:** algunos comandos se pegaron como `! export … && az …` en una terminal normal. En bash, `!` niega el código de salida del `export`, el `&&` se salta el `az` y **no se ejecuta nada** (por eso más tarde `az extension list` salía vacío, ver paso 2). El `!` solo tiene sentido en el prompt de Claude Code; en tu terminal, sin `!`.

## Paso 1 · `az login` con el usuario temporal del lab
**Por qué:** el lab da un usuario temporal con **Temporary Access Pass**, que solo vale en login interactivo (no con `-u -p`). El flujo de código de dispositivo evita depender de que se abra un navegador en la máquina.
```bash
az login --use-device-code
```
Salida: salida no guardada. Esperado: un código y la URL `login.microsoft.com/device`; tras validar (ventana de incógnito, «cuenta profesional o educativa») aparece una lista con una sola suscripción `XLabs-…` del tenant «Lab Directory» y Enter acepta la predeterminada.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, tenant:tenantDisplayName}" -o table
```
Debe salir una suscripción `XLabs-…`. Si sale la cuenta de empresa, `az logout` y repite el login con el usuario del lab.

## Paso 2 · Extensiones de la CLI
**Por qué:** `az containerapp` y las consultas a Log Analytics no vienen en la CLI base; sin ellas el comando «no existe».
```bash
az extension add --name containerapp
az extension add --name log-analytics
```
Salida: ninguna si va bien (salida no guardada).

✅ **Comprobación:**
```bash
az extension list --query '[].name' -o tsv
```
Deben salir `containerapp` y `log-analytics`. ⚠️ **Lo que pasó:** la primera vez salió **vacío**: los comandos se habían lanzado con `!` delante (paso 0) y nunca se ejecutaron. Arreglo: repetirlos sin `!`.

## Paso 3 · Registrar los proveedores de recursos
**Por qué:** una suscripción nueva no tiene habilitados todos los «tipos» de recurso. Es como instalar los CRD antes de crear objetos: `Microsoft.App` (Container Apps), `Microsoft.OperationalInsights` (Log Analytics) y `Microsoft.ContainerRegistry` (ACR).
```bash
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
```
Salida: ninguna (el registro es asíncrono; salida no guardada). Aquí ya estaban registrados.

✅ **Comprobación:**
```bash
for ns in Microsoft.App Microsoft.OperationalInsights Microsoft.ContainerRegistry; do
  echo "$ns $(az provider show -n $ns --query registrationState -o tsv)"; done
```
Los tres en `Registered`. Si alguno sale `Registering`, espera un minuto y repite.

## Paso 4 · Editar `azdeploy.py` con los valores de la plataforma
**Por qué:** el script crea los recursos con el nombre de grupo y la región que pongas arriba; la plataforma además exige `gpt-5.1` y `TPM_LIMIT` (tabla de diferencias). No se toca nada más.
```bash
cd ~/claude/AI-200-Developing/labs/lp2-01-aca-deploy
grep -nE '^(rg|location|MODEL_NAME|TPM_LIMIT) =|"TPM_LIMIT": TPM_LIMIT' azdeploy.py
```
Resultado (fichero ya editado, tal como está versionado):
```text
5:rg = "rg-ai200-aca"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
22:MODEL_NAME = "gpt-5.1"
23:TPM_LIMIT = "5000"
219:        "TPM_LIMIT": TPM_LIMIT,
```
✅ **Comprobación:** las cinco líneas. Si alguna falta o sigue `<your-…>` o `gpt-5.4-mini`, edítala a mano.

## Paso 5 · Crear ACR e imagen (`azdeploy.py` → opción 1)
**Por qué:** la app necesita una imagen en un registry privado. El script crea el ACR (`--sku Basic --admin-enabled false`: sin usuario admin, solo identidades) y construye la imagen **en la nube** con `az acr build` (ACR Tasks), así que no hace falta Docker en local: primero `az`, nada local.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este script:
```text
1 → resource group + ACR + az acr build de api/ (ai-api:v1)
2 → Log Analytics workspace + Container Apps environment; escribe .env y .env.ps1
3 → comprobar estado (ACR, imagen, environment)
4 → salir
```
Salida: no guardada. Esperado: el grupo `rg-ai200-aca`, el ACR `acr<hash>` y el build de `ai-api:v1` (el script lanza el build con `--no-logs`, así que va en silencio).

✅ **Comprobación:**
```bash
az acr repository show-tags -n <acr> --repository ai-api -o tsv
```
Debe salir `v1`. Si no aparece, mira las runs del build: `az acr task list-runs --registry <acr> -o table` y `az acr task logs --registry <acr> --run-id <id>` (ejecuta el script desde la carpeta que contiene `api/`). Si una run se queda en `Queued` más de un par de minutos: `az acr task cancel-run --registry <acr> --run-id <id>` y relanza la opción 1.

## Paso 6 · Crear el environment (opción 2) y comprobar el estado (opción 3)
**Por qué:** el environment es el «cluster gestionado» donde viven las apps: red, DNS interno y logs compartidos. Sin `--logs-workspace-id` la CLI crea también un workspace de Log Analytics. Es lo más lento (varios minutos). La opción 2 escribe además el `.env` con los nombres que usarán los comandos manuales.
```bash
python3 azdeploy.py      # menú → 2, luego 3, luego 4
```
Salida real de la opción 3:
```text
Checking deployment status...

Container Apps Environment (aca-env-<hash>):
  Status: Succeeded
  Container Apps environment is ready

Azure Container Registry (acr<hash>):
  Status: Succeeded
  ACR is ready
  Container image: ai-api:v1
```
**Qué mirar:** `Succeeded` en environment y ACR, y la imagen `ai-api:v1` ya publicada. Nombres derivados del *object id* del usuario: `acr<hash>` y `aca-env-<hash>`.

⚠️ **Trampa (guía de la plataforma):** la opción 2 puede dar un error de conexión aunque el environment siga creándose; al repetirla dice «already exists» sin comprobar que haya terminado. Aquí no pasó, pero comprueba siempre `provisioningState` (paso 7).

## Paso 7 · Cargar `.env` y confirmar que el environment está listo
**Por qué:** los comandos manuales usan variables (`$RESOURCE_GROUP`, `$ACR_SERVER`…) que el script dejó en `.env`. Y crear la app con el environment aún en `Waiting` falla con `ManagedEnvironmentNotProvisioned`.
```bash
source .env
az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv
```
Salida real:
```text
Succeeded
```
**Qué mirar:** `.env` carga `RESOURCE_GROUP`, `ACR_NAME`, `ACR_SERVER`, `ACA_ENVIRONMENT`, `CONTAINER_APP_NAME`, `CONTAINER_IMAGE`, `TARGET_PORT`, `MODEL_NAME`, `TPM_LIMIT`, `EMBEDDINGS_API_KEY` y `LOCATION`. Este `.env` **no se sube** al repo porque lleva `EMBEDDINGS_API_KEY`.

✅ **Comprobación:**
```bash
echo "RG=[$RESOURCE_GROUP] APP=[$CONTAINER_APP_NAME] ACR=[$ACR_SERVER] PORT=[$TARGET_PORT]"
[ -n "${EMBEDDINGS_API_KEY:-}" ] && echo "clave cargada"
```
Esperado: `RG=[rg-ai200-aca] APP=[ai-api] ACR=[acr<hash>.azurecr.io] PORT=[8000]` y `clave cargada` (sin mostrar la clave). Si salen corchetes vacíos, el `source .env` no se hizo en esta terminal. Si el estado es `Waiting`, espera y repite el `env show`.

## Paso 8 · Crear la container app con identidad gestionada (Task 2)
**Por qué:** es el despliegue en sí. `--registry-identity system` crea una identidad gestionada para la app y la CLI le da `AcrPull` sobre el ACR: la primera revisión ya puede descargar la imagen **sin credenciales** (sin ella, `ImagePullBackOff`/403). `--ingress external` da un FQDN público con TLS gestionado; `--target-port` es el puerto donde escucha gunicorn.
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
Salida real:
```text
Container app created. Access your app at https://ai-api.<dominio-del-environment>.eastus.azurecontainerapps.io/
```
**Qué mirar:** `Container app created` sin error de conexión. Es **en este comando** donde la app obtiene `AcrPull`. La imagen va por tag (`:v1`); en producción, por digest.

✅ **Comprobación:**
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
  --query "{identity:identity.type, image:properties.template.containers[0].image, registries:properties.configuration.registries[0].identity}" -o tsv
```
Esperado: `SystemAssigned`, `acr<hash>.azurecr.io/ai-api:v1` y `system`. ⚠️ **Trampa (guía de la plataforma):** si el `create` da un error de conexión (`NameResolutionError`, `Max retries exceeded`), la app puede quedar a medias con una imagen *placeholder* y `registries` en `null`. Antes de reintentar, mira esa misma consulta; si la imagen no es la del ACR o no hay registry: `az containerapp registry set` + `az containerapp update --image …`, o `az containerapp delete` y repetir. Si da `ImagePullBackOff`/403, espera 1-2 min (propagación del rol) y revisa `az containerapp identity show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP`.

## Paso 9 · Guardar el secreto
**Por qué:** la clave no debe ir en claro en la definición de la app. El secreto se guarda en la app (≈ `Secret` de K8s); por sí solo **no crea revisión** ni reinicia nada.
```bash
az containerapp secret set -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --secrets embeddings-api-key=$EMBEDDINGS_API_KEY
```
Salida: no guardada. Esperado: la lista de secretos con el **nombre** `embeddings-api-key` (los valores nunca se muestran).

✅ **Comprobación:**
```bash
az containerapp secret list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
```
Debe salir una fila `embeddings-api-key`. Si sale vacío, `$EMBEDDINGS_API_KEY` estaba vacía (paso 7) o el comando no se ejecutó: repítelo.

## Paso 10 · Variable que referencia el secreto → revisión 0000002
**Por qué:** la app lee la clave de una variable de entorno; con `secretref:` el valor de la variable es el secreto, no un texto (≈ `secretKeyRef`). Cambiar variables es cambiar la **plantilla**, así que crea una revisión nueva y reinicia.
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key
```
Salida real (extracto del JSON; se omiten las ~300 `outboundIpAddresses` y los IDs):
```text
{
  "identity": { "type": "SystemAssigned" },
  "location": "East US",
  "name": "ai-api",
  "properties": {
    "configuration": {
      "activeRevisionsMode": "Single",
      "ingress": { "external": true, "targetPort": 8000, "traffic": [ { "latestRevision": true, "weight": 100 } ] },
      "registries": [ { "identity": "system", "server": "acr<hash>.azurecr.io", "username": "" } ],
      "secrets": [ { "name": "embeddings-api-key" } ]
    },
    "latestReadyRevisionName": "ai-api--0000001",
    "latestRevisionName": "ai-api--0000002",
    "outboundIpAddresses": [ … ≈300 direcciones omitidas … ],
    "provisioningState": "Succeeded",
    "runningStatus": "Running",
    "template": {
      "containers": [ {
        "env": [ { "name": "MODEL_NAME" }, { "name": "EMBEDDINGS_API_KEY", "secretRef": "embeddings-api-key" } ],
        "image": "acr<hash>.azurecr.io/ai-api:v1",
        "resources": { "cpu": 0.5, "ephemeralStorage": "2Gi", "memory": "1Gi" }
      } ],
      "scale": { "cooldownPeriod": 300, "maxReplicas": 10, "minReplicas": null, "pollingInterval": 30, "rules": null }
    },
    "workloadProfileName": "Consumption"
  }
}
```
**Qué mirar:**
- `registries[0].identity = "system"`: pull por identidad, sin usuario ni contraseña.
- `secrets` solo lista el **nombre**, nunca el valor; la variable lleva `secretRef`, no un valor en claro.
- `MODEL_NAME` sale **sin `value`**: la CLI lo oculta en esta salida. No se asume que falte: se comprueba con `GET /` en el paso 13.
- `latestRevisionName = …0000002` pero `latestReadyRevisionName = …0000001`: la nueva aún arrancaba cuando volvió el comando.
- Valores por defecto: `cpu 0.5`, `memory 1Gi`, `maxReplicas 10`, `minReplicas null` (equivale a 0: scale-to-zero), perfil `Consumption`, modo de revisiones `Single`.

✅ **Comprobación:** el paso siguiente.

## Paso 11 · Ver las dos revisiones
**Por qué:** confirma que el cambio de plantilla generó una revisión y cómo se reparte el tráfico en modo *single* (≈ ReplicaSet nuevo de un rollout).
```bash
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
```
Salida real:
```text
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T18:48:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000001
2026-10-29T18:52:17+00:00  True      1           100              Healthy        Provisioned          ai-api--0000002
```
**Qué mirar:** la `0000002` tiene el 100 % del tráfico; la `0000001` sigue `Active` con 1 réplica y 0 % porque está en plena transición: la plataforma la desactiva cuando la nueva está sana.

✅ **Comprobación:** repite el `revision list` pasado un minuto. Esperado: solo `ai-api--0000002` activa con 100 % (salida no guardada). Si la `0000002` sale `Unhealthy` o `Failed`, mira los logs (paso 14).

**Para el examen:** cada cambio de plantilla (imagen, variables, recursos, escalado) crea revisión; `secret set` por sí solo, no.

## Paso 12 · Obtener el FQDN y probar `/health` (Task 3)
**Por qué:** demuestra que el ingress enruta tráfico a la réplica. `curl` va contra el **endpoint público de la app**, no contra un API server, así que el proxy de empresa no lo bloquea (no hay alternativa `az` para hacer la petición HTTP a la app).
```bash
FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
echo "$FQDN"
curl -s "https://$FQDN/health"
```
Salida real:
```text
{"status":"healthy"}
```
✅ **Comprobación:** `{"status":"healthy"}`. Si da 502/503 recién desplegado, la réplica aún arranca: espera un minuto y repite. Si `echo "$FQDN"` sale vacío, el `show` falló (revisa `source .env`).

## Paso 13 · Comprobar la configuración (`GET /`) y procesar un documento (`POST /process`)
**Por qué:** `/` dice qué ve la app por dentro (modelo y si el secreto está configurado): es la comprobación fiable de que variables y `secretref:` llegaron. `/process` prueba la lógica de la API con el `document.txt` que pide la plataforma.
```bash
curl -s "https://$FQDN/"
printf 'This is a test document for the Azure Container Apps exercise.\n' > document.txt
curl -s -X POST "https://$FQDN/process" -H "Content-Type: text/plain" --data-binary @document.txt
```
`--data-binary @document.txt` envía el fichero tal cual (equivale a `-Body (Get-Content -Raw …)` de PowerShell). `document.txt` está versionado con ese texto.

Salida real:
```text
{"config":{"log_level":"INFO","max_document_size_mb":10,"processing_timeout_seconds":15,"storage_path":"/tmp/processed"},"environment":"development","model":{"name":"gpt-5.1"},"secrets":{"embeddings_api_key_configured":true},"service":"AI Document Processing API","status":"running","version":"1.0.0"}

{"analysis":{"entities":[{"confidence":0.95,"text":"Azure","type":"Technology"},{"confidence":0.93,"text":"Container Apps","type":"Service"},{"confidence":0.87,"text":"document","type":"Concept"}],"key_phrases":["document processing","container deployment","secrets and configuration","revision management"],"sentiment":{"confidence":0.78,"overall":"neutral","scores":{"negative":0.1,"neutral":0.68,"positive":0.22}}},"document_id":"8080bbc5-298e-4d5f-bde9-77c4785878da","environment":"development","filename":"document.txt","model":{"name":"gpt-5.1"},"processed_at":"2026-10-29T18:55:13.923635Z","processing_config":{"max_size_mb":10,"timeout_seconds":15},"secrets":{"embeddings_api_key_configured":true},"statistics":{"character_count":63,"size_bytes":63,"word_count":11},"storage":{"path":"/tmp/processed/8080bbc5-298e-4d5f-bde9-77c4785878da.json","saved":true}}
```
**Qué mirar:**
- `/` confirma `"model":{"name":"gpt-5.1"}` y `"embeddings_api_key_configured":true`: **resuelve la duda del paso 10** (la CLI no enseñaba el valor de `MODEL_NAME`, pero la app sí lo tiene).
- `/process` devuelve entidades, frases clave y sentimiento **simulados**, `statistics` (63 caracteres, 11 palabras) y guarda el resultado en `/tmp/processed`: almacenamiento **efímero del contenedor**, se pierde al reiniciar o escalar. En App Service (LP1-02) se usaba `/home`, persistente; aquí haría falta montar un volumen (Azure Files).

✅ **Comprobación:** `model.name = gpt-5.1` y `embeddings_api_key_configured = true`. Si sale `not-configured` o `false`, revisa la plantilla: `az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.containers[0].env" -o table` y `az containerapp secret list …`.

## Paso 14 · Logs de la consola
**Por qué:** «logs primero» es la regla de diagnóstico (y pregunta de examen). `logs show` conecta a la réplica activa y trae las últimas líneas de stdout/stderr (≈ `kubectl logs`, pero vía `az`, sin pasar por ningún API server de cluster).
```bash
az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
```
Salida real:
```text
{"TimeStamp": "2026-10-29T18:55:19.51046", "Log": "Connecting to the container 'ai-api'..."}
{"TimeStamp": "2026-10-29T18:55:19.69895", "Log": "Successfully Connected to container: 'ai-api' [Revision: 'ai-api--0000002', Replica: 'ai-api--0000002-6f7b8899-z7wlj']"}
{"TimeStamp": "2026-10-29T18:52:34.0896641+00:00", "Log": "F [2026-10-29 18:52:34 +0000] [7] [INFO] Starting gunicorn 22.0.0"}
{"TimeStamp": "2026-10-29T18:52:34.0900312+00:00", "Log": "F [2026-10-29 18:52:34 +0000] [7] [INFO] Listening at: http://0.0.0.0:8000 (7)"}
{"TimeStamp": "2026-10-29T18:52:34.0900498+00:00", "Log": "F [2026-10-29 18:52:34 +0000] [7] [INFO] Using worker: sync"}
{"TimeStamp": "2026-10-29T18:52:34.0919838+00:00", "Log": "F [2026-10-29 18:52:34 +0000] [8] [INFO] Booting worker with pid: 8"}
{"TimeStamp": "2026-10-29T18:52:34.1640935+00:00", "Log": "F [2026-10-29 18:52:34 +0000] [9] [INFO] Booting worker with pid: 9"}
{"TimeStamp": "2026-10-29T18:55:13.2674224+00:00", "Log": "F … \"GET /health HTTP/1.1\" 200 21 \"-\" \"curl/8.5.0\""}
{"TimeStamp": "2026-10-29T18:55:13.5967065+00:00", "Log": "F … \"GET / HTTP/1.1\" 200 302 \"-\" \"curl/8.5.0\""}
{"TimeStamp": "2026-10-29T18:55:13.9238173+00:00", "Log": "F 2026-10-29 18:55:13,923 - main - INFO - Document processing request received"}
{"TimeStamp": "2026-10-29T18:55:13.9245209+00:00", "Log": "F 2026-10-29 18:55:13,924 - main - INFO - Result saved to /tmp/processed/8080bbc5-….json"}
{"TimeStamp": "2026-10-29T18:55:13.9249618+00:00", "Log": "F … \"POST /process HTTP/1.1\" 200 866 \"-\" \"curl/8.5.0\""}
{"TimeStamp": "2026-10-29T18:55:15.2071195+00:00", "Log": "F … \"GET / HTTP/1.1\" 200 302 \"-\" \"python-requests/2.33.0\""}
```
**Qué mirar:**
- Réplica de la revisión `0000002`; gunicorn escuchando en el **8000** con 2 workers (pid 8 y 9).
- Las tres peticiones con 200. `GET /` mide **302 bytes** con `gpt-5.1` (dato útil en LP2-02).
- La última `GET /` con `python-requests` **no la lanzó el alumno**: probable validación automática de la plataforma del lab.
- Las líneas `MODEL_NAME=…` y `EMBEDDINGS_API_KEY configured: …` del código **no salen**: están bajo `if __name__ == "__main__"` y gunicorn importa el módulo, no lo ejecuta como principal. Por eso la comprobación fiable es `GET /`.
- `logs show` solo trae lo reciente; el histórico está en Log Analytics (KQL, se practica en LP2-02). Para seguir en directo: `--follow`.

✅ **Comprobación:** aparecen `Listening at: http://0.0.0.0:8000` y tus `curl` con 200. Si no sale nada, espera unos segundos (la conexión a la réplica tarda) y repite; si la app escaló a 0 réplicas, haz antes un `curl` para despertarla.

---

## Cleanup (obligatorio al acabar)
**Por qué:** los recursos tienen coste y el entorno es temporal; se borra el grupo entero del lab.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-aca --no-wait --yes
az group exists --name rg-ai200-aca        # repetir hasta false
```
Salida: no guardada (este `delete` no se llegó a lanzar).

**Estado real:** **no verificado con `az group exists`.** El 29/10, durante el cleanup del [LP2-03](../lp2-03-aca-scale/README.md#cleanup-obligatorio-al-acabar), `az group list --query "[?starts_with(name,'rg-ai200')]…"` solo devolvía `rg-ai200-aca-scale`: `rg-ai200-aca` ya no existía porque la plataforma lo había desprovisionado.

✅ **Comprobación:** `az group exists --name rg-ai200-aca` → `false`. Si sale `true` pasados 15 min: `az group show -n rg-ai200-aca --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`. Si `az` da `AuthorizationFailed`/`AADSTS…`, las credenciales del lab han caducado: anótalo como no verificado.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Could not find a suitable TLS CA certificate bundle` en `az login` | Proxy de empresa que re-firma TLS | Paso 0: `export REQUESTS_CA_BUNDLE=…` |
| Comandos pegados con `!` no hacen nada | En bash `!` niega el estado y el `&&` se salta lo siguiente | Paso 0: no usar `!` fuera del prompt de Claude Code |
| `az extension list` vacío aunque se «instalaron» | Misma causa: nunca se ejecutaron | Paso 2: repetir sin `!` |
| `curl` o `az` con 502/503 recién desplegado | Réplica aún arrancando | Paso 12: esperar un minuto |
| `ManagedEnvironmentNotProvisioned` (no pasó) | Environment en `Waiting` | Paso 7: esperar a `Succeeded` |
| Error de conexión en `create` (no pasó) | App a medias con imagen placeholder | Paso 8: revisar imagen/registries antes de reintentar |

## Troubleshooting de la guía de la plataforma (solo lectura)
| Problema | Comprobación |
|---|---|
| Estado base | `python3 azdeploy.py` → opción 3 |
| Autenticación y variables | `az account show`; `echo "[$ACR_NAME]"`; si está vacía, `source .env` |
| ACR | `az acr list -o table` y `ProvisioningState = Succeeded` |
| Fallo del build | `az acr task list-runs --registry $ACR_NAME -o table`; `az acr task logs --registry $ACR_NAME --run-id <id>` |
| `ImagePullBackOff` / 403 | `az containerapp identity show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP` y rol `AcrPull` sobre el ACR (1-2 min de propagación) |
| Arranque o errores | `az containerapp logs show … --follow`; `az containerapp revision list … -o table` |
| Secreto | `az containerapp secret list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table`; `GET /` → `embeddings_api_key_configured` |

## Anexo · Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab:
| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (L152) | `--sku Basic`, `--admin-enabled false` |
| Subir la imagen | `az acr build` (L169) | build en la nube, sin Docker local |
| Vincular (pull) | `az containerapp create … --registry-identity system` (paso 8, lo lanza el alumno) | identidad system-assigned y `AcrPull` automático |
- **Push y pull son permisos distintos:** el build lo hace ACR con tu `az login`; la descarga la hace la app con su identidad y el rol **AcrPull**.
- **Comprobar el vínculo:** `az containerapp show -g rg-ai200-aca -n ai-api --query identity.type -o tsv` → `SystemAssigned`.
- **Si no descarga la imagen:** falta `AcrPull` o la imagen/tag no existe → `az acr repository show-tags -n <acr> --repository ai-api -o tsv`.
