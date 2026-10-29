# Lab LP2-02 · Diagnose and fix a failing deployment (Manage containers in Azure Container Apps)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/02-aca-manage-containers.html
Documentación del módulo (MS Learn): https://learn.microsoft.com/es-es/training/modules/manage-containers-azure-container-apps/
Material de partida: `aca-manage-python.zip` (original, sin editar) y sus ficheros extraídos (`azdeploy.py` editado, `api/`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Qué hace cada comando del script: [`scripts/lp2-02-aca-manage/README.md`](../../scripts/lp2-02-aca-manage/README.md). Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

Ejecutado en Linux (bash) contra la suscripción temporal del lab (29/10/2026). La plataforma del curso da los mismos pasos en PowerShell.

## Objetivo
Practicar la operación de día 2 de una container app: **introducir fallos a propósito**, detectarlos con revisiones, `logs show` y la configuración de la revisión, corregirlos y consultar el histórico en Log Analytics con KQL.

## Qué se construye
```
azdeploy.py (1) → resource group + ACR + imagen ai-api:v1
azdeploy.py (2) → Container Apps environment (+ Log Analytics workspace creado por az)
azdeploy.py (3) → container app "ai-api" (identidad gestionada + AcrPull) + secreto + variable secretref  → revisión 0000002
Fallo 1 → quitar MODEL_NAME            → revisión 0000003 (model.name = not-configured)
Fallo 2 → ingress con target-port 3000 → la app deja de responder
Log Analytics → histórico con KQL
```

## Diferencias de la plataforma respecto a la guía oficial
| Cambio | Dónde | Valor |
|---|---|---|
| Región | `location` | `eastus` |
| Resource group | `rg` | `rg-ai200-aca-manage` (elegido por nosotros) |
| Modelo | `MODEL_NAME` | `gpt-5.1` (el original trae `gpt-5.4-mini`) |
| Límite de tokens | `TPM_LIMIT = "5000"` y entrada en `write_env_files()` | se exporta al `.env`; el código no lo usa |

`MODEL_NAME` y `TPM_LIMIT` son solo variables de entorno: la API es una **simulación** (Flask, entidades y sentimiento fijos); no llama a ningún modelo.

## Cómo se relaciona con lo que ya sabes (K8s) y con el examen
- Cada cambio de plantilla crea una **revisión** ≈ un `Deployment` nuevo con su ReplicaSet; el modo *single* hace el reemplazo.
- Quitar una variable ≈ editar el `env` del Deployment; `ingress --target-port` ≈ `targetPort` del Service.
- Examen: logs primero, comparar revisión sana con la fallida, desactivar antes de borrar, `--replace-env-vars` reemplaza **todas** las variables (cuidado).

## Comandos ejecutados (en orden)
Los que crean o modifican recursos los lanza el alumno.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # antes de CUALQUIER az, en cada terminal
az login --use-device-code
python3 azdeploy.py            # 1, 2, 3 y 5
source .env
FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
curl -sS -m 20 "https://$FQDN/" | jq .

# Fallo 1
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --remove-env-vars MODEL_NAME
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
curl -sS -m 20 "https://$FQDN/" | jq .model
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.containers[0].env" -o table
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --set-env-vars MODEL_NAME=$MODEL_NAME
```

## Comandos al detalle

### 1. `python3 azdeploy.py` (opciones 1, 2, 3, 5)
Detalle completo, comando por comando, en [`scripts/lp2-02-aca-manage/README.md`](../../scripts/lp2-02-aca-manage/README.md). En resumen: ACR + imagen, environment, y **la opción 3 crea la app con `--registry-identity system`**, que es el momento en que la app obtiene el rol `AcrPull` para descargar la imagen; después fija el secreto y la variable `secretref:` (revisión 2).
- **Incidencia real:** la opción 2 se quedó más de 10 minutos en «Creating Container Apps environment…» aunque el environment ya estaba en `Succeeded` (la llamada a Azure quedó colgada). Arreglo: `Ctrl+C`, comprobar `az containerapp env show … --query properties.provisioningState -o tsv`, volver a lanzar el script y elegir directamente la opción 3.

### 2. Verificación inicial
```bash
FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)
curl -sS -m 20 -w "\nhttp=%{http_code} tiempo=%{time_total}s\n" "https://$FQDN/"
```
```
az containerapp show … --query properties.configuration.ingress.fqdn -o tsv → dominio público de la app
curl -sS         → silencioso pero con errores visibles
-m 20            → abandona a los 20 s en vez de colgarse
-w "…"           → al final imprime código HTTP y tiempo
```
- **Resultado real (estado sano):** `{"config":{…},"environment":"development","model":{"name":"gpt-5.1"},"secrets":{"embeddings_api_key_configured":true},…}` con `http=200 tiempo≈0,33s`.
- **Incidencia:** un primer `curl … | jq .` se quedó esperando sin salida (cuelgue puntual de la conexión); con `-m 20` y sin `jq` respondió normal. Desde otra sesión la app respondía en 0,3 s, así que no era el despliegue.

### 3. Fallo 1 · variable de entorno que falta
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --remove-env-vars MODEL_NAME
```
```
az containerapp update        → modifica la plantilla; crea una revisión nueva
--remove-env-vars MODEL_NAME  → elimina solo esa variable (las demás y el secreto se mantienen)
```
- **Qué hace:** crea la revisión `ai-api--0000003` con la plantilla sin `MODEL_NAME`.
- **Resultado real:** JSON de la app con `latestRevisionName = ai-api--0000003`, `latestReadyRevisionName = ai-api--0000002` en ese momento y `template.containers[0].env` con **solo** `EMBEDDINGS_API_KEY` (`secretRef`). Se ignoran las ~300 `outboundIpAddresses`, y los IDs de suscripción/tenant/principal no se copian al repo.
- **`az containerapp revision list -o table`:**
  ```
  Active  Replicas  TrafficWeight  HealthState  ProvisioningState  Name
  True    1         0              Healthy      Provisioned        ai-api--0000002
  True    1         100            None         Provisioned        ai-api--0000003
  ```
  La nueva lleva el 100 % del tráfico; `HealthState = None` mientras no tiene estado calculado.
- **`curl … | jq .model`:** `{"name": "not-configured"}`.
- **Por qué importa:** la app **no cae**: el código usa `os.getenv("MODEL_NAME", "not-configured")`, así que sigue devolviendo 200. Es un fallo **silencioso**: comprobar solo que responde no basta, hay que revisar la configuración de la revisión.
- **Diagnóstico:** `az containerapp show … --query "properties.template.containers[0].env" -o table` → no aparece `MODEL_NAME`.
- **Corrección:** `az containerapp update … --set-env-vars MODEL_NAME=$MODEL_NAME` → crea la revisión `…--0000004`, que ya lleva `MODEL_NAME` en su plantilla (el JSON de la CLI no muestra el valor, solo el nombre).
- **Trampa (modo single, zero-downtime):** justo después del `update`, `latestReadyRevisionName` seguía siendo la `…--0000003` y un `curl` inmediato devolvió todavía `not-configured`: la revisión **vieja sigue sirviendo hasta que la nueva está lista**. Al cabo de ~30-60 s:
  ```
  Active  Replicas  TrafficWeight  HealthState  Name
  True    1         100            Healthy      ai-api--0000004
  ```
  La 0000003 se desactiva sola y la 0000004 queda como única activa. Si tras 2-3 min siguiera `not-configured`, revisar `echo "MODEL_NAME=[$MODEL_NAME]"`: una variable de shell vacía fijaría un valor vacío.

### 4. Fallo 2 · puerto de destino incorrecto (ingress)
```bash
az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --target-port 3000        # provocar
curl -sS -m 20 -w "\nhttp=%{http_code}\n" "https://$FQDN/health"                                   # observar
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.configuration.ingress" -o yaml   # diagnosticar
az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --target-port 8000        # corregir
curl -sS -m 20 "https://$FQDN/health"                                                                # verificar
```
```
az containerapp ingress update → cambia solo la configuración del ingress de la app
--target-port 3000             → el ingress enruta al 3000; el contenedor escucha en el 8000
```
- **Síntoma (según la guía de la plataforma):** HTTP 503 «connection refused» en **todos** los endpoints, no solo `/health`.
- **Diagnóstico:** `ingress.targetPort: 3000` en la configuración frente a `Listening at: http://0.0.0.0:8000` en los logs de gunicorn: esa discrepancia es la causa.
- **Corrección:** `--target-port 8000` → `{"status":"healthy"}`.
- **Detalle de examen:** el ingress es configuración de la app, no de la plantilla del contenedor, así que (según la documentación) este cambio **no crea una revisión nueva**, al contrario que las variables de entorno. Los logs de la app **no registran** el fallo: la app nunca recibe las peticiones; el `connection refused` lo ve la plataforma.
- Salidas de este fallo no pegadas en el chat; el resultado final se comprobó (el alumno dio el lab por terminado).

### 5. Log Analytics con KQL (histórico)
```bash
WORKSPACE_ID=$(az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP \
    --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv)
az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' | project TimeGenerated, Log_s | order by TimeGenerated desc | take 20" -o table
az monitor log-analytics query -w $WORKSPACE_ID --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' and Log_s contains 'error' | order by TimeGenerated desc | take 20" -o table
```
```
customerId                          → identificador del workspace (no es un secreto, pero no se copia al repo)
az monitor log-analytics query -w   → ejecuta una consulta KQL (extensión log-analytics)
ContainerAppConsoleLogs_CL          → tabla con stdout/stderr de las apps del environment
| where ContainerAppName_s == '…'   → filtra por la app
| project TimeGenerated, Log_s      → solo hora y mensaje
| order by TimeGenerated desc | take 20
Log_s contains 'error'              → líneas con esa palabra (sin `project` devuelve todas las columnas de la tabla)
```
- **Por qué:** `logs show` solo trae lo reciente; Log Analytics conserva el histórico aunque haya reinicios o cambios de revisión. Los datos tardan 2-5 min en aparecer. Eventos de plataforma (pull, cambios de revisión): tabla `ContainerAppSystemLogs_CL`.
- **Resultado real (consulta 1):** la historia del lab leída desde los logs:
  | Hora (UTC) | Qué muestra |
  |---|---|
  | 19:42:05 | Arrancan los workers de la revisión `0000003` |
  | 19:42:25 | `GET / 200 309` bytes (la respuesta con `not-configured`) |
  | 19:42:45 | `Handling signal: term` / `Shutting down`: se apaga la réplica de la revisión anterior al tomar el relevo la 0003 |
  | 19:45:29 | `GET / 200 309` todavía a la 0003 (la 0004 aún arrancaba) |
  | 19:45:39 | Arranca gunicorn de la revisión `0000004` (`Listening at: http://0.0.0.0:8000`) |
  | 19:46:16 | Se apaga la réplica de la `0000003` al activarse la 0004 |
  El tamaño de la respuesta delata el fallo: **302 bytes** con `gpt-5.1` y **309** con `not-configured` (7 caracteres más).
- **Resultado real (consulta 2, `error`):** una sola línea, `[ERROR] Worker (pid:8) was sent SIGTERM!` de la revisión `ai-api--0000003` a las 19:46:16. **No es un fallo de la app**: gunicorn registra a nivel ERROR la señal de apagado que la plataforma envía al sustituir la revisión vieja. Lección: buscar `error` encuentra ruido; hay que leer el contexto (hora, revisión) antes de concluir.


## Resultados
- Despliegue base correcto (revisión `0000002` sana, pull por identidad `system`, secreto `secretref`).
- Fallo 1 reproducido, diagnosticado y corregido (`not-configured` en la revisión `0000003`; arreglo en la `0000004`, única activa y `Healthy`).
- Fallo 2 (puerto 3000 frente a 8000) diagnosticado y corregido.
- Log Analytics: histórico consultado con KQL; el único `error` era el SIGTERM de apagado de la revisión anterior.
- **Lab completado.** Falta ejecutar el cleanup.

## Incidencias y soluciones
| Síntoma | Causa | Arreglo |
|---|---|---|
| Opción 2 colgada >10 min con el environment ya `Succeeded` | Llamada a Azure sin respuesta | `Ctrl+C`, comprobar `provisioningState`, relanzar y usar la opción 3 |
| `curl … \| jq .` sin salida | Conexión puntual colgada | `curl -sS -m 20` sin `jq`; reintentar |
| `az containerapp update` → `(--name --resource-group \| --ids) are required` | Se lanzó el comando sin argumentos | Incluir `-n $CONTAINER_APP_NAME -g $RESOURCE_GROUP` y el cambio (`--set-env-vars …`) |
| `The behavior of this command has been altered by the following extension: containerapp` | Aviso de la extensión preview | Se ignora |

## Cleanup (obligatorio, lo ejecuta el alumno)
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-aca-manage --no-wait --yes
az group exists --name rg-ai200-aca-manage        # repetir hasta false
```
Solo se borra el grupo del lab; el grupo `AZ802-L0501-RG` que había en la suscripción es de la plataforma y no se toca.
