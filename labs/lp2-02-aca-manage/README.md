# Lab LP2-02 · Diagnose and fix a failing deployment (plataforma: Lab 4 · AI-200-LP02M02, «Manage containers in ACA»)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/02-aca-manage-containers.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)). Módulo en MS Learn: https://learn.microsoft.com/es-es/training/modules/manage-containers-azure-container-apps/
- **Estado (29/10/2026): hecho completo** (despliegue, fallo A, fallo B y Log Analytics). Las salidas del **fallo B** (puerto del ingress) no se guardaron: el alumno lo corrigió y dio el lab por terminado. **Cleanup no verificado con `az group exists`:** el `delete` no se llegó a lanzar; esa misma tarde, al limpiar el [LP2-03](../lp2-03-aca-scale/README.md#cleanup-obligatorio-al-acabar), `az group list` ya no mostraba `rg-ai200-aca-manage` (desprovisionado por la plataforma).
- **Conversación con Claude Code:** no se conserva (anterior a la exportación). Sesión del día: [`sesiones/2026-10-29-sesion-03-container-apps.md`](../../sesiones/2026-10-29-sesion-03-container-apps.md).
- Lab anterior: [LP2-01](../lp2-01-aca-deploy/README.md) · Lab siguiente: [LP2-03](../lp2-03-aca-scale/README.md).
- Material: `aca-manage-python.zip` (original sin editar), `azdeploy.py` (editado) y `api/`. Origen MIT: [`../NOTICE.md`](../NOTICE.md). Qué hace el script por dentro: [`scripts/lp2-02-aca-manage/README.md`](../../scripts/lp2-02-aca-manage/README.md). Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

Ejecutado en Linux (bash); la plataforma da los mismos pasos en PowerShell. Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Sin IDs de suscripción/tenant/workspace/principal ni usuario del lab; ~300 IPs omitidas; sufijos hash como `<hash>`. Prompt abreviado a `$`.

## Qué se construye y para qué
**Objetivo en cristiano:** es el «día 2» de operación. Se parte de la app del LP2-01 ya desplegada (esta vez la crea el script) y se **rompe a propósito** de dos formas típicas: una variable de entorno que desaparece (fallo silencioso: la app responde 200 pero mal configurada) y un puerto de ingress equivocado (la app deja de responder). Para cada uno: síntoma → diagnóstico con `az` → arreglo → verificación. Al final se lee la historia completa en **Log Analytics** con KQL.

```
azdeploy.py 1 → rg-ai200-aca-manage + ACR acr<hash> + imagen ai-api:v1
azdeploy.py 2 → environment aca-env-<hash> (+ Log Analytics)
azdeploy.py 3 → app ai-api (identidad + AcrPull) + secreto + secretref → revisión 0000002 (estado sano)
Fallo A → --remove-env-vars MODEL_NAME → revisión 0000003 (model = not-configured) → arreglo → 0000004
Fallo B → ingress --target-port 3000   → la app no responde → arreglo a 8000 (sin revisión nueva)
Log Analytics → ContainerAppConsoleLogs_CL con KQL
```

**Traducción a Kubernetes:** cada cambio de plantilla = revisión nueva ≈ rollout con ReplicaSet nuevo; el modo *single* hace el reemplazo. Quitar una variable ≈ editar el `env` del Deployment. `ingress --target-port` ≈ `targetPort` del Service apuntando a un puerto donde no escucha nadie. Log Analytics ≈ tu stack de logs centralizado (Loki/ELK).

**Para el examen:** logs primero; comparar la revisión sana con la fallida; desactivar antes de borrar; `--replace-env-vars` reemplaza **todas** las variables (cuidado).

### Diferencias de la plataforma respecto a la guía oficial
| Cambio | Dónde | Valor |
|---|---|---|
| Región | `location` | `eastus` |
| Resource group | `rg` | `rg-ai200-aca-manage` (elegido por nosotros) |
| Modelo | `MODEL_NAME` | `gpt-5.1` (el original y la guía dicen `gpt-5.4-mini`) |
| Límite de tokens | `TPM_LIMIT = "5000"` y entrada en `write_env_files()` | se exporta al `.env`; el código no lo usa |

La API es una **simulación** (Flask, entidades y sentimiento fijos): no llama a ningún modelo. El código usa `os.getenv("MODEL_NAME", "not-configured")`, y por eso el fallo A no tumba la app.

---

## Paso 0 · Preparar la terminal e iniciar sesión
**Por qué:** igual que en LP2-01: el proxy de empresa re-firma el TLS (`REQUESTS_CA_BUNDLE`, en cada terminal) y el usuario temporal del lab solo entra con login interactivo.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az login --use-device-code
```
Salida: no guardada. Esperado: una suscripción `XLabs-…` del tenant «Lab Directory».

✅ **Comprobación:**
```bash
az account show --query "{sub:name, tenant:tenantDisplayName}" -o table
az extension list --query '[].name' -o tsv
```
Suscripción `XLabs-…` y extensiones `containerapp` y `log-analytics` (la segunda hace falta en el paso 12). Si falta alguna: `az extension add --name containerapp` / `--name log-analytics`. Los proveedores `Microsoft.App`, `Microsoft.OperationalInsights` y `Microsoft.ContainerRegistry` se registran como en el [paso 3 del LP2-01](../lp2-01-aca-deploy/README.md#paso-3--registrar-los-proveedores-de-recursos).

## Paso 1 · Editar `azdeploy.py`
**Por qué:** grupo y región propios, y los cambios de la plataforma (tabla de arriba).
```bash
cd ~/claude/AI-200-Developing/labs/lp2-02-aca-manage
grep -nE '^(rg|location|MODEL_NAME|TPM_LIMIT) =|"TPM_LIMIT": TPM_LIMIT' azdeploy.py
```
Resultado (fichero ya editado, tal como está versionado):
```text
5:rg = "rg-ai200-aca-manage"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
22:MODEL_NAME = "gpt-5.1"
23:TPM_LIMIT = "5000"
303:        "TPM_LIMIT": TPM_LIMIT,
```
✅ **Comprobación:** las cinco líneas. Si falta alguna, edítala a mano.

## Paso 2 · ACR e imagen (opción 1)
**Por qué:** igual que en LP2-01: ACR sin usuario admin y build en la nube (`az acr build`), sin Docker local.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este script:
```text
1 → resource group + ACR + az acr build de api/ (ai-api:v1)
2 → Container Apps environment (con su Log Analytics)
3 → despliega la container app y configura el secreto; genera .env y .env.ps1
4 → estado: ACR, imagen, environment y app
5 → salir
```
Salida: no guardada. ✅ **Comprobación:** `az acr repository show-tags -n <acr> --repository ai-api -o tsv` → `v1`. Si no, revisa las runs con `az acr task list-runs --registry <acr> -o table`.

## Paso 3 · Environment (opción 2)
**Por qué:** el environment es el «cluster gestionado» de las apps; la CLI crea también el workspace de Log Analytics que se consultará en el paso 12.
```bash
python3 azdeploy.py      # menú → 2
```
Salida: no guardada.

⚠️ **Lo que pasó:** la opción 2 se quedó **más de 10 minutos** en «Creating Container Apps environment…» aunque el environment ya estaba creado: la llamada a Azure quedó colgada. Arreglo: `Ctrl+C`, comprobar el estado con `az` y relanzar el script directamente en la opción 3.

✅ **Comprobación:**
```bash
az containerapp env list -g rg-ai200-aca-manage --query "[].{name:name, state:properties.provisioningState}" -o tsv
```
Esperado: `aca-env-<hash>	Succeeded`. Si sale `Waiting`, espera; si `Succeeded` y el script sigue colgado, `Ctrl+C` y opción 3.

## Paso 4 · Desplegar la app con secreto (opción 3)
**Por qué:** la opción 3 hace de golpe lo que en LP2-01 eran los pasos 8-10: `az containerapp create … --registry-identity system` (identidad + `AcrPull`), `secret set` y `update --set-env-vars EMBEDDINGS_API_KEY=secretref:…` (revisión 2). Así se parte de un **estado sano conocido** para poder romperlo.
```bash
python3 azdeploy.py      # menú → 3 → 5
```
Salida: no guardada. Esperado: la app `ai-api` creada y el `.env`/`.env.ps1` escritos.

✅ **Comprobación:** opción 4 del menú (esperado: `Succeeded` en ACR, environment y app, `Container App is deployed`) o, con `az`:
```bash
az containerapp revision list -n ai-api -g rg-ai200-aca-manage -o table
```
Revisión `ai-api--0000002` con 100 % y `Healthy` (creada a las 19:33:44 UTC, según la tabla del paso 6). Si la opción 3 dio error de conexión, la app puede estar a medias: `az containerapp show -n ai-api -g rg-ai200-aca-manage --query "{image:properties.template.containers[0].image, registries:properties.configuration.registries}"`; si la imagen no es tu ACR o `registries` es `null`, `az containerapp registry set` + `az containerapp update --image …`, o borrar la app y repetir la 3.

## Paso 5 · Línea base: el estado sano
**Por qué:** sin una referencia «buena» no se puede decir qué ha cambiado. Se guarda la respuesta de `/` con el modelo, el código HTTP y el tiempo. `curl` va contra el endpoint público de la app (no hay API server de por medio), así que el proxy no lo bloquea.
```bash
source .env
FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
curl -sS -m 20 -w "\nhttp=%{http_code} tiempo=%{time_total}s\n" "https://$FQDN/"
```
`-sS` silencioso pero con errores visibles · `-m 20` abandona a los 20 s en vez de colgarse · `-w` imprime código y tiempo al final.

Salida real:
```text
{"config":{"log_level":"INFO","max_document_size_mb":10,"processing_timeout_seconds":15,"storage_path":"/tmp/processed"},"environment":"development","model":{"name":"gpt-5.1"},"secrets":{"embeddings_api_key_configured":true},"service":"AI Document Processing API","status":"running","version":"1.0.0"}

http=200 tiempo=0.333451s
```
**Qué mirar:** `model.name = gpt-5.1`, secreto configurado, HTTP 200 en ~0,3 s. Esta es la referencia para los fallos.

⚠️ **Lo que pasó:** el primer intento, `curl -s "https://$FQDN/" | jq .`, se quedó esperando sin salida (cuelgue puntual de la conexión). Desde otra sesión la app respondía en 0,3 s, así que no era el despliegue. Con `-m 20` y sin `jq` respondió normal.

✅ **Comprobación:** `http=200` y `gpt-5.1`. Si el `curl` se cuelga, el `-m 20` lo corta: repite. Si `$FQDN` está vacía, falta el `source .env`.

## Paso 6 · Fallo A: quitar `MODEL_NAME` (provocar)
**Por qué:** simula el error más común en un despliegue: una variable que se pierde en un cambio. `--remove-env-vars` quita solo esa (las demás y el secreto se mantienen) y, como toca la plantilla, crea revisión nueva.
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --remove-env-vars MODEL_NAME
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
```
Salida real (extracto del JSON del `update`, y la tabla):
```text
    "latestReadyRevisionName": "ai-api--0000002",
    "latestRevisionName": "ai-api--0000003",
    "template": { "containers": [ { "env": [ { "name": "EMBEDDINGS_API_KEY", "secretRef": "embeddings-api-key", "value": "" } ], … } ] }

CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:33:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000002
2026-10-29T19:41:44+00:00  True      1           100              None           Provisioned          ai-api--0000003
```
**Qué mirar:** revisión nueva `0000003` con el 100 % del tráfico (`HealthState None` mientras aún no tiene estado calculado). El `env` del JSON ya solo lista `EMBEDDINGS_API_KEY`.

✅ **Comprobación:** existe la `0000003` con 100 %. Si no aparece, el `update` no se aplicó: mira el error que devolvió.

## Paso 7 · Fallo A: observar el síntoma
**Por qué:** ver qué nota un cliente. Aquí está la lección: la app **no cae**.
```bash
curl -sS -m 20 "https://$FQDN/" | jq .model
```
Salida real:
```text
{
  "name": "not-configured"
}
```
**Qué mirar:** HTTP 200 con `not-configured` (el valor por defecto del `os.getenv`). Es un fallo **silencioso**: un *health check* que solo mire «responde» no lo detecta; hay que revisar la configuración de la revisión.

✅ **Comprobación:** sale `not-configured`. Si aún sale `gpt-5.1`, la `0000003` todavía no servía: espera 30-60 s y repite.

## Paso 8 · Fallo A: diagnosticar
**Por qué:** confirmar la causa en la **definición** de la app, no adivinarla por el síntoma (≈ `kubectl get deploy -o yaml`, pero con `az`).
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.containers[0].env" -o table
```
Salida real:
```text
Name                Value    SecretRef
------------------  -------  ------------------
EMBEDDINGS_API_KEY           embeddings-api-key
```
**Qué mirar:** falta `MODEL_NAME`. La única variable es la del secreto (sin valor visible, solo `SecretRef`).

✅ **Comprobación:** no aparece `MODEL_NAME`. Si aparece, el fallo es otro: compara con la revisión sana (`az containerapp revision show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --revision ai-api--0000002`).

## Paso 9 · Fallo A: corregir
**Por qué:** volver a poner la variable crea otra revisión (`0000004`). Se usa `--set-env-vars` (añade/actualiza esa variable), **no** `--replace-env-vars`, que borraría también la del secreto.
```bash
echo "MODEL_NAME=[$MODEL_NAME]"          # antes: que no esté vacía
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars MODEL_NAME=$MODEL_NAME
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
curl -sS -m 20 "https://$FQDN/" | jq .model
```
Salida real:
```text
    "latestReadyRevisionName": "ai-api--0000003",
    "latestRevisionName": "ai-api--0000004",
    "env": [ { "name": "EMBEDDINGS_API_KEY", "secretRef": "embeddings-api-key", "value": "" }, { "name": "MODEL_NAME" } ]

CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:41:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000003
2026-10-29T19:45:14+00:00  True      1           100              None           Provisioned          ai-api--0000004

{
  "name": "not-configured"
}
```
**Qué mirar:** la `0000004` ya lleva `MODEL_NAME` en su plantilla (la CLI muestra el nombre, no el valor). Pero el `curl` inmediato **sigue diciendo `not-configured`**: `latestReadyRevisionName` aún era la `0000003`. En modo *single* la revisión vieja **sigue sirviendo hasta que la nueva está lista** (zero-downtime), igual que un rolling update que no mata los pods viejos hasta que los nuevos pasan la *readiness*.

⚠️ **Lo que pasó:** en algún momento de este fallo se lanzó `az containerapp update` **sin argumentos**:
```text
$ az containerapp update
(--name --resource-group | --ids) are required
```
Siempre hace falta `-n $CONTAINER_APP_NAME -g $RESOURCE_GROUP` más el cambio. También salía el aviso `The behavior of this command has been altered by the following extension: containerapp`: es de la extensión preview y se ignora.

✅ **Comprobación:** el paso siguiente. Si `echo` muestra `MODEL_NAME=[]`, haz `source .env` antes del `update`: una variable de shell vacía fijaría un valor vacío.

## Paso 10 · Fallo A: verificar tras esperar
**Por qué:** confirmar que la plataforma completó el relevo y que solo queda la revisión buena.
```bash
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
curl -sS -m 20 "https://$FQDN/" | jq .model
```
Salida real (pasados ~30-60 s):
```text
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:45:14+00:00  True      1           100              Healthy        Provisioned          ai-api--0000004
```
**Qué mirar:** la `0000003` se desactivó sola; la `0000004` es la única activa y `Healthy`. El `curl` de esta comprobación no se guardó (esperado: `{"name": "gpt-5.1"}`, como en la guía).

✅ **Comprobación:** una sola revisión `Healthy` y `model.name = gpt-5.1`. Si tras 2-3 min sigue `not-configured`, revisa el paso 8 sobre la `0000004`.

## Paso 11 · Fallo B: puerto del ingress equivocado (provocar, observar, diagnosticar, corregir)
**Por qué:** el segundo fallo típico: el ingress (≈ Service) envía el tráfico a un puerto donde el contenedor no escucha. Se diagnostica comparando **dos fuentes**: la configuración del ingress (`az containerapp show`) y el puerto real que anuncia gunicorn en los logs (`az containerapp logs show`). Todo con `az`; el único comando local es el `curl` al endpoint público.
```bash
az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --target-port 3000        # provocar
curl -sS -m 20 -w "\nhttp=%{http_code}\n" "https://$FQDN/health"                                   # observar
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.configuration.ingress" -o yaml   # diagnosticar
az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP                                 # puerto real
az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --target-port 8000        # corregir
curl -sS -m 20 "https://$FQDN/health"                                                                # verificar
```
Salida: **no guardada** (no se pegó en el chat; el alumno corrigió el fallo y dio el lab por terminado). Esperado:
- **Síntoma:** la petición falla o se agota (la guía de la plataforma habla de HTTP **503** «connection refused» en **todos** los endpoints, no solo `/health`).
- **Diagnóstico:** `targetPort: 3000` en el ingress frente a `Listening at: http://0.0.0.0:8000` en los logs de gunicorn: esa discrepancia es la causa.
- **Arreglo:** con `--target-port 8000`, `/health` vuelve a dar `{"status":"healthy"}`.

**Qué mirar:**
- El ingress es configuración **de la app**, no de la plantilla del contenedor: según la documentación este cambio **no crea revisión nueva** (al contrario que las variables). Compruébalo con `revision list`: debería seguir solo la `0000004`.
- Los logs de la app **no registran** el fallo: la app nunca recibe las peticiones; el `connection refused` lo ve la plataforma. Por eso hay que mirar la configuración, no solo los logs.

✅ **Comprobación:**
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.targetPort -o tsv
curl -sS -m 20 -w "\nhttp=%{http_code}\n" "https://$FQDN/health"
```
Esperado: `8000` y `{"status":"healthy"}` con `http=200`. Si sale `3000`, el arreglo no se aplicó: repítelo. Si sale `8000` pero aún falla, espera un minuto (propagación del ingress).

## Paso 12 · Log Analytics: obtener el workspace
**Por qué:** `logs show` solo da lo reciente de la réplica activa; Log Analytics guarda el **histórico** aunque haya reinicios o cambios de revisión. Primero hace falta el identificador del workspace del environment.
```bash
WORKSPACE_ID=$(az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP \
    --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv)
echo "Workspace ID: $WORKSPACE_ID"
```
Salida real:
```text
Workspace ID: <guid-del-workspace>
```
**Qué mirar:** `customerId` es un GUID; no es un secreto, pero no se copia al repo.

✅ **Comprobación:** sale un GUID. Si sale vacío, falta `source .env` (`$ACA_ENVIRONMENT` vacía) o el environment no tiene Log Analytics enlazado.

## Paso 13 · Log Analytics: la historia del lab con KQL
**Por qué:** reconstruir qué pasó y cuándo, revisión a revisión. `ContainerAppConsoleLogs_CL` guarda stdout/stderr de las apps del environment (los eventos de plataforma, como pulls o cambios de revisión, están en `ContainerAppSystemLogs_CL`). Los datos tardan 2-5 min en aparecer.
```bash
az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' | project TimeGenerated, Log_s | order by TimeGenerated desc | take 20" -o table
```
`where` filtra por la app · `project` deja solo hora y mensaje · `order by … desc | take 20` las 20 últimas.

Salida real:
```text
Log_s                                                                                     TableName      TimeGenerated
----------------------------------------------------------------------------------------  -------------  ----------------------------
[2026-10-29 19:46:16 +0000] [9] [INFO] Worker exiting (pid: 9)                            PrimaryResult  2026-10-29T19:46:17.5158811Z
[2026-10-29 19:46:16 +0000] [7] [INFO] Shutting down: Master                              PrimaryResult  2026-10-29T19:46:17.5158811Z
[2026-10-29 19:46:16 +0000] [7] [INFO] Handling signal: term                              PrimaryResult  2026-10-29T19:46:17.5158811Z
[2026-10-29 19:46:16 +0000] [7] [ERROR] Worker (pid:8) was sent SIGTERM!                  PrimaryResult  2026-10-29T19:46:17.5158811Z
[2026-10-29 19:46:16 +0000] [8] [INFO] Worker exiting (pid: 8)                            PrimaryResult  2026-10-29T19:46:17.5158811Z
[2026-10-29 19:45:39 +0000] [7] [INFO] Listening at: http://0.0.0.0:8000 (7)              PrimaryResult  2026-10-29T19:45:42.099476Z
[2026-10-29 19:45:39 +0000] [8] [INFO] Booting worker with pid: 8                         PrimaryResult  2026-10-29T19:45:42.099476Z
[2026-10-29 19:45:39 +0000] [9] [INFO] Booting worker with pid: 9                         PrimaryResult  2026-10-29T19:45:42.099476Z
[2026-10-29 19:45:39 +0000] [7] [INFO] Starting gunicorn 22.0.0                           PrimaryResult  2026-10-29T19:45:42.099476Z
[2026-10-29 19:45:39 +0000] [7] [INFO] Using worker: sync                                 PrimaryResult  2026-10-29T19:45:42.099476Z
2026-10-29 19:45:29,493 - main - INFO - Service info requested                            PrimaryResult  2026-10-29T19:45:30.2525543Z
100.100.0.166 - - [29/Oct/2026:19:45:29 +0000] "GET / HTTP/1.1" 200 309 "-" "curl/8.5.0"  PrimaryResult  2026-10-29T19:45:30.2525543Z
[2026-10-29 19:42:45 +0000] [7] [INFO] Shutting down: Master                              PrimaryResult  2026-10-29T19:42:46.2036864Z
[2026-10-29 19:42:45 +0000] [7] [INFO] Handling signal: term                              PrimaryResult  2026-10-29T19:42:46.2036864Z
[2026-10-29 19:42:45 +0000] [9] [INFO] Worker exiting (pid: 9)                            PrimaryResult  2026-10-29T19:42:46.2036864Z
[2026-10-29 19:42:45 +0000] [8] [INFO] Worker exiting (pid: 8)                            PrimaryResult  2026-10-29T19:42:46.2036864Z
100.100.0.166 - - [29/Oct/2026:19:42:25 +0000] "GET / HTTP/1.1" 200 309 "-" "curl/8.5.0"  PrimaryResult  2026-10-29T19:42:26.1682247Z
2026-10-29 19:42:25,641 - main - INFO - Service info requested                            PrimaryResult  2026-10-29T19:42:26.1682247Z
[2026-10-29 19:42:05 +0000] [8] [INFO] Booting worker with pid: 8                         PrimaryResult  2026-10-29T19:42:07.3844439Z
[2026-10-29 19:42:05 +0000] [9] [INFO] Booting worker with pid: 9                         PrimaryResult  2026-10-29T19:42:07.3844439Z
```
**Qué mirar** (leído de abajo arriba, en orden cronológico, hora UTC):
| Hora | Qué muestra |
|---|---|
| 19:42:05 | Arrancan los workers de la revisión `0000003` (fallo A, paso 6) |
| 19:42:25 | `GET / 200 309` bytes: la respuesta con `not-configured` (paso 7) |
| 19:42:45 | `Handling signal: term` / `Shutting down`: se apaga la réplica de la `0000002` al tomar el relevo la `0000003` |
| 19:45:29 | `GET / 200 309` todavía servido por la `0000003`: el `curl` inmediato del paso 9 |
| 19:45:39 | Arranca gunicorn de la `0000004` (`Listening at: http://0.0.0.0:8000`) |
| 19:46:16 | Se apaga la réplica de la `0000003` al activarse la `0000004` (paso 10) |

- El **tamaño de la respuesta delata el fallo:** 302 bytes con `gpt-5.1` (ver LP2-01, paso 14) frente a **309** con `not-configured` (7 caracteres más).
- Las 20 líneas terminan a las 19:46:16 y **no aparece** el `GET /health` del arreglo del fallo B. O esta consulta se lanzó antes del fallo B, o esos logs aún no se habían ingerido (2-5 min). El orden exacto entre el paso 11 y este no quedó registrado.

✅ **Comprobación:** salen líneas de gunicorn y tus `GET /`. Si sale vacío, espera 2-5 min y repite; si sigue vacío, revisa `$WORKSPACE_ID` y el nombre de la app (`echo "[$CONTAINER_APP_NAME]"`).

## Paso 14 · Log Analytics: buscar «error»
**Por qué:** es lo primero que uno hace ante un incidente… y aquí se ve por qué no basta: hay que leer el contexto de cada línea.
```bash
az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' and Log_s contains 'error' | order by TimeGenerated desc | take 20" -o table
```
Salida real (25 columnas; extracto de la única fila):
```text
  ContainerAppName_s = ai-api
  RevisionName_s     = ai-api--0000003
  Stream_s           = stderr
  Log_s              = [2026-10-29 19:46:16 +0000] [7] [ERROR] Worker (pid:8) was sent SIGTERM!
  TimeGenerated      = 2026-10-29T19:46:17.5158811Z
```
**Qué mirar:** el único `error` **no es un fallo de la app**: gunicorn registra a nivel ERROR el `SIGTERM` que envía la plataforma al apagar la revisión vieja (`0000003`) cuando se activa la `0000004`. Buscar «error» encuentra ruido; hay que mirar la hora y la revisión antes de concluir. Sin `| project …` la consulta devuelve **todas** las columnas de la tabla (de ahí las 25).

✅ **Comprobación:** una fila de la revisión `0000003` a las 19:46:16. Si sale vacío, puede que aún no se hayan ingerido los logs (2-5 min).

---

## Cleanup (obligatorio al acabar)
**Por qué:** coste y entorno temporal: se borra solo el grupo del lab. El grupo `AZ802-L0501-RG` que había en la suscripción es de la plataforma y **no se toca**.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-aca-manage --no-wait --yes
az group exists --name rg-ai200-aca-manage        # repetir hasta false
```
Salida: no guardada (este `delete` no se llegó a lanzar).

**Estado real:** **no verificado con `az group exists`.** El 29/10, durante el cleanup del [LP2-03](../lp2-03-aca-scale/README.md#cleanup-obligatorio-al-acabar), `az group list` filtrado por `rg-ai200` solo devolvía `rg-ai200-aca-scale`: este grupo ya lo había desprovisionado la plataforma.

✅ **Comprobación:** `az group exists --name rg-ai200-aca-manage` → `false`. Si sale `true` pasados 15 min, mira `az group show -n rg-ai200-aca-manage --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`. Si `az` da `AuthorizationFailed`/`AADSTS…`, las credenciales del lab caducaron: anótalo como no verificado.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| Opción 2 colgada >10 min con el environment ya creado | Llamada a Azure sin respuesta | Paso 3: `Ctrl+C`, comprobar `provisioningState`, relanzar en la opción 3 |
| `curl … \| jq .` sin salida | Cuelgue puntual de la conexión | Paso 5: `curl -sS -m 20` sin `jq`; reintentar |
| `curl` justo tras el arreglo sigue dando `not-configured` | La revisión vieja sirve hasta que la nueva está lista | Paso 9-10: esperar 30-60 s |
| `(--name --resource-group \| --ids) are required` | `az containerapp update` sin argumentos | Paso 9: añadir `-n … -g …` y el cambio |
| `The behavior of this command has been altered by the following extension: containerapp` | Aviso de la extensión preview | Se ignora |
| La búsqueda de `error` devuelve un `SIGTERM` | Apagado normal de la revisión vieja | Paso 14: leer hora y revisión, no es un fallo |

## Anexo · Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab:
| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (L152) | `--sku Basic`, `--admin-enabled false` |
| Subir la imagen | `az acr build` (L169) | build en la nube |
| Vincular (pull) | `az containerapp create … --registry-server … --registry-identity system` (L260-261) | identidad system-assigned y `AcrPull` automático |
- **Push y pull son permisos distintos:** el build lo hace ACR con tu `az login`; la descarga la hace la app con su identidad y el rol **AcrPull**.
- **Comprobar el vínculo:** `az containerapp show -g rg-ai200-aca-manage -n ai-api --query identity.type -o tsv` → `SystemAssigned`.
- **Si no descarga la imagen** (`ImagePullBackOff`): falta `AcrPull` o la imagen/tag no existe → `az acr repository show-tags -n <acr> --repository ai-api -o tsv`.
