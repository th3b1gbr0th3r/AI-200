# Salidas reales · Lab LP2-02 (Diagnose and fix a failing deployment)

Capturas de terminal del 29/10/2026, saneadas (sin IDs de suscripción, tenant, workspace ni principal, sin el usuario del lab, con las ~300 IPs omitidas y los hash como `<hash>`). Comandos explicados al detalle en el [README del lab](README.md). Prompt abreviado a `$`.

## 1 · Estado sano de partida
```console
$ curl -sS -m 20 -w "\nhttp=%{http_code} tiempo=%{time_total}s\n" "https://$FQDN/"
{"config":{"log_level":"INFO","max_document_size_mb":10,"processing_timeout_seconds":15,"storage_path":"/tmp/processed"},"environment":"development","model":{"name":"gpt-5.1"},"secrets":{"embeddings_api_key_configured":true},"service":"AI Document Processing API","status":"running","version":"1.0.0"}

http=200 tiempo=0.333451s
```
**Qué mirar:** `model.name = gpt-5.1` y HTTP 200. Esta es la referencia para comparar los fallos.

## 2 · Fallo 1: quitar la variable `MODEL_NAME`
```console
$ az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --remove-env-vars MODEL_NAME
  (JSON; extracto)
    "latestReadyRevisionName": "ai-api--0000002",
    "latestRevisionName": "ai-api--0000003",
    "template": { "containers": [ { "env": [ { "name": "EMBEDDINGS_API_KEY", "secretRef": "embeddings-api-key", "value": "" } ], … } ] }

$ az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:33:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000002
2026-10-29T19:41:44+00:00  True      1           100              None           Provisioned          ai-api--0000003

$ curl -sS -m 20 "https://$FQDN/" | jq .model
{
  "name": "not-configured"
}
```
**Qué mirar:** revisión nueva `0000003` con el 100 %; la app **no cae**, responde 200 con `not-configured` (fallo silencioso). El `env` del JSON ya solo lista `EMBEDDINGS_API_KEY`.

## 3 · Diagnóstico
```console
$ az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.containers[0].env" -o table
Name                Value    SecretRef
------------------  -------  ------------------
EMBEDDINGS_API_KEY           embeddings-api-key
```
**Qué mirar:** falta `MODEL_NAME`.

## 4 · Corrección
```console
$ az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars MODEL_NAME=$MODEL_NAME
  (JSON; extracto)
    "latestReadyRevisionName": "ai-api--0000003",
    "latestRevisionName": "ai-api--0000004",
    "env": [ { "name": "EMBEDDINGS_API_KEY", "secretRef": "embeddings-api-key", "value": "" }, { "name": "MODEL_NAME" } ]

$ az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:41:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000003
2026-10-29T19:45:14+00:00  True      1           100              None           Provisioned          ai-api--0000004

$ curl -sS -m 20 "https://$FQDN/" | jq .model
{
  "name": "not-configured"
}
```
**Qué mirar:** el `curl` inmediato aún devuelve `not-configured`: `latestReadyRevisionName` seguía siendo la `0000003`, y **la revisión vieja sirve hasta que la nueva está lista** (zero-downtime del modo *single*).

## 5 · Tras esperar, una sola revisión sana
```console
$ az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T19:45:14+00:00  True      1           100              Healthy        Provisioned          ai-api--0000004
```
**Qué mirar:** la `0000003` se desactivó sola; la `0000004` es la única activa y `Healthy`.

## 6 · Error de uso (incidencia)
```console
$ az containerapp update
(--name --resource-group | --ids) are required
```
**Qué mirar:** el comando se lanzó sin argumentos. Siempre `-n $CONTAINER_APP_NAME -g $RESOURCE_GROUP` más el cambio.

## 7 · Log Analytics con KQL
```console
$ WORKSPACE_ID=$(az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP \
    --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv)
$ echo "Workspace ID: $WORKSPACE_ID"
Workspace ID: <guid-del-workspace>

$ az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' | project TimeGenerated, Log_s | order by TimeGenerated desc | take 20" -o table
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
**Qué mirar:** la historia del lab en orden inverso: la `0000003` arranca a las 19:42:05, responde `GET / 200 309` bytes (**309** con `not-configured` frente a **302** con `gpt-5.1`), y a las 19:46:16 recibe `SIGTERM` al activarse la `0000004`.

```console
$ az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' and Log_s contains 'error' | order by TimeGenerated desc | take 20" -o table
  (25 columnas; extracto de la única fila)
  ContainerAppName_s = ai-api
  RevisionName_s     = ai-api--0000003
  Stream_s           = stderr
  Log_s              = [2026-10-29 19:46:16 +0000] [7] [ERROR] Worker (pid:8) was sent SIGTERM!
  TimeGenerated      = 2026-10-29T19:46:17.5158811Z
```
**Qué mirar:** el único `error` **no es un fallo**: gunicorn registra a nivel ERROR el `SIGTERM` de apagado cuando la plataforma sustituye la réplica antigua. Sin `| project …` la consulta devuelve todas las columnas de la tabla.
