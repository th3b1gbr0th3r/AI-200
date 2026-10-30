# Salidas reales · Lab LP2-01 (Deploy a containerized backend API to ACA)

Capturas de terminal del 29/10/2026, copiadas tal cual las pegó el alumno y saneadas: sin IDs de suscripción, tenant ni workspace, sin el usuario del lab y con los sufijos hash como `<hash>`. Los comandos, explicados al detalle, están en el [README del lab](README.md). Prompt abreviado a `$`.

## 1 · Estado de la infraestructura base (opción 3 del script)
```console
Checking deployment status...

Container Apps Environment (aca-env-<hash>):
  Status: Succeeded
  Container Apps environment is ready

Azure Container Registry (acr<hash>):
  Status: Succeeded
  ACR is ready
  Container image: ai-api:v1
```
**Qué mirar:** `Succeeded` en el environment y el ACR, y la imagen `ai-api:v1` ya publicada.

## 2 · El environment está listo antes de crear la app
```console
$ source .env
$ az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv
Succeeded
```
**Qué mirar:** debe ser `Succeeded`; con `Waiting`, `az containerapp create` falla con `ManagedEnvironmentNotProvisioned`.

## 3 · Crear la container app con identidad gestionada
```console
$ az containerapp create \
    --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --environment $ACA_ENVIRONMENT \
    --image "$ACR_SERVER/$CONTAINER_IMAGE" --ingress external --target-port $TARGET_PORT \
    --env-vars MODEL_NAME=$MODEL_NAME --registry-server "$ACR_SERVER" --registry-identity system

Container app created. Access your app at https://ai-api.<dominio-del-environment>.eastus.azurecontainerapps.io/
```
**Qué mirar:** `Container app created` sin error de conexión. Es en este comando donde la app obtiene `AcrPull` para descargar la imagen.

## 4 · Variable que referencia el secreto (extracto de la salida de `az containerapp update`)
```console
$ az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key
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
**Qué mirar:** `registries[0].identity = "system"` (pull sin credenciales), `secrets` solo con el **nombre**, la variable con `secretRef`, y `latestReadyRevisionName` aún en la `0000001` mientras la `0000002` arranca. `MODEL_NAME` sale sin valor: la CLI lo oculta.

## 5 · Dos revisiones
```console
$ az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ---------------
2026-10-29T18:48:44+00:00  True      1           0                Healthy        Provisioned          ai-api--0000001
2026-10-29T18:52:17+00:00  True      1           100              Healthy        Provisioned          ai-api--0000002
```
**Qué mirar:** la `0000002` lleva el 100 % del tráfico; la `0000001` sigue activa con 0 % durante la transición del modo *single*.

## 6 · Verificación de la API
```console
$ curl -s "https://$FQDN/health"
{"status":"healthy"}

$ curl -s "https://$FQDN/"
{"config":{"log_level":"INFO","max_document_size_mb":10,"processing_timeout_seconds":15,"storage_path":"/tmp/processed"},"environment":"development","model":{"name":"gpt-5.1"},"secrets":{"embeddings_api_key_configured":true},"service":"AI Document Processing API","status":"running","version":"1.0.0"}

$ curl -s -X POST "https://$FQDN/process" -H "Content-Type: text/plain" --data-binary @document.txt
{"analysis":{"entities":[{"confidence":0.95,"text":"Azure","type":"Technology"},{"confidence":0.93,"text":"Container Apps","type":"Service"},{"confidence":0.87,"text":"document","type":"Concept"}],"key_phrases":["document processing","container deployment","secrets and configuration","revision management"],"sentiment":{"confidence":0.78,"overall":"neutral","scores":{"negative":0.1,"neutral":0.68,"positive":0.22}}},"document_id":"8080bbc5-298e-4d5f-bde9-77c4785878da","environment":"development","filename":"document.txt","model":{"name":"gpt-5.1"},"processed_at":"2026-10-29T18:55:13.923635Z","processing_config":{"max_size_mb":10,"timeout_seconds":15},"secrets":{"embeddings_api_key_configured":true},"statistics":{"character_count":63,"size_bytes":63,"word_count":11},"storage":{"path":"/tmp/processed/8080bbc5-298e-4d5f-bde9-77c4785878da.json","saved":true}}
```
**Qué mirar:** `/` confirma `"model":{"name":"gpt-5.1"}` y el secreto configurado (resuelve la duda de la salida de `update`). `/process` devuelve datos **simulados** y guarda el resultado en `/tmp/processed`, almacenamiento efímero del contenedor.

## 7 · Logs de la consola
```console
$ az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
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
**Qué mirar:** gunicorn escuchando en el 8000 con 2 workers; las tres peticiones con 200; la última, con `python-requests`, no la lanzó el alumno (probable validación de la plataforma). `GET /` mide 302 bytes con `gpt-5.1`.
