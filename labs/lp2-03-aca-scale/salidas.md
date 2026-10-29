# Salidas reales · Lab LP2-03 (Scale containers in Azure Container Apps)

Capturas de terminal del 29/10/2026, saneadas (sin IDs de suscripción ni tenant, sin el usuario del lab, hash como `<hash>`). Se irá ampliando a medida que avance el lab. Prompt abreviado a `$`.

## 1 · Estado tras el despliegue base (opción 4 del script)
```console
Checking deployment status...

Container Apps Environment (aca-env-<hash>):
  Status: Succeeded
  Container Apps environment is ready

Azure Container Registry (acr<hash>):
  Status: Succeeded
  ACR is ready
  Container image: agent-api:v1

Container App (agent-api):
  Status: Succeeded
  System-assigned identity configured
  Ingress FQDN: agent-api.<dominio-del-environment>.eastus.azurecontainerapps.io
  Running replicas: 1
```
**Qué mirar:** todo en `Succeeded` y **1 réplica** en ejecución: es el punto de partida (la app se crea con `min 1` / `max 1`).

## 2 · Error: variables sin cargar (incidencia)
```console
$ az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
    --min-replicas 0 --max-replicas 10 \
    --scale-rule-name http-scaling --scale-rule-type http --scale-rule-http-concurrency 10
argument --name/-n: expected one argument
```
**Qué mirar:** `expected one argument` en `-n` = `$CONTAINER_APP_NAME` vacía. Las variables del `.env` se pierden al abrir otra terminal. Arreglo: `source .env` y comprobar con `echo "RG=[$RESOURCE_GROUP] APP=[$CONTAINER_APP_NAME]"`.

## 3 · Regla de escalado HTTP aplicada
```console
$ source .env
$ az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.scale" -o json
{
  "cooldownPeriod": 300,
  "maxReplicas": 10,
  "minReplicas": 0,
  "pollingInterval": 30,
  "rules": [
    {
      "http": {
        "auth": [],
        "metadata": {
          "concurrentRequests": "10"
        }
      },
      "name": "http-scaling"
    }
  ]
}

$ az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ------------------
2026-10-29T20:13:04+00:00  True      1           100              Healthy        Provisioned          agent-api--0000002
```
**Qué mirar:** `minReplicas 0`, `maxReplicas 10` y la regla `http-scaling` con `concurrentRequests: "10"`. El cambio de escalado está en la plantilla, así que crea la revisión `0000002`.

## 4 · Dashboard de carga en marcha (Flask, `client/`)
```console
$ cd client
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -q -r requirements.txt
$ python3 app.py
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
**Qué mirar:** el dashboard escucha en `127.0.0.1:5000`. Lee `RESOURCE_GROUP` y `CONTAINER_APP_NAME` de las variables de la terminal (hay que hacer `source .env` antes) y consulta las réplicas con `az containerapp replica list`.

## 5 · Las réplicas suben con la carga
```console
$ az containerapp replica list -n agent-api -g rg-ai200-aca-scale --query "length(@)" -o tsv
5
```
**Qué mirar:** de **1** réplica (despliegue base) a **5** durante la carga: la regla HTTP (10 peticiones concurrentes por réplica) está escalando. Con 25 workers saldrían ~3; con más concurrencia, más, hasta un máximo de 10.
