# Lab LP1-02 · Deploy a container to Azure App Service

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html
Material de partida: `app-svc-container-python.zip` (https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/app-svc-container-python.zip). No se versiona aquí: descargar y descomprimir en esta carpeta (`azdeploy.py`, `document.txt`, `api/`).

Ejecutado en Linux (bash). La plataforma del curso da los mismos pasos en PowerShell. Diferencias de la guía de la plataforma respecto a la oficial: región `canadacentral` y SKU del plan `B1` (línea 224 de `azdeploy.py`, el script trae `P0v3`).

## Qué hay en el material de partida
- `api/Dockerfile`: `python:3.11-slim`, instala `requirements.txt` (flask 3.0.0, gunicorn 22.0.0), `mkdir -p /home/processed`, `EXPOSE 80`, `CMD gunicorn --bind 0.0.0.0:80 --workers 2 --access-logfile - main:app`.
- `api/main.py`: API Flask de procesado de documentos simulado. Configuración por variables de entorno (`ENVIRONMENT`, `LOG_LEVEL`, `MAX_DOCUMENT_SIZE_MB`, `PROCESSING_TIMEOUT_SECONDS`, `STORAGE_PATH`). Rutas: `GET /`, `GET /health`, `POST /process` (guarda el resultado en `/home/processed/<id>.json`), `GET /documents`, `GET /documents/<id>`. El análisis (entidades, sentimiento) es fijo; las estadísticas son reales.
- `azdeploy.py`: menú. Opción 1: resource group + ACR (`--admin-enabled false`) + `az acr build` de `docprocessor:v1`. Opción 2: App Service plan Linux y escritura de `.env`. Opción 3: comprobación de estado. La web app **no** la crea el script.

## Comandos ejecutados (en orden)

```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # solo si hay proxy que intercepta TLS

# Ediciones en azdeploy.py: rg="rg-ai200-appsvc", location="canadacentral", línea 224 "--sku","B1"
python3 azdeploy.py        # menú: 1 (ACR + imagen), 2 (plan + .env), 4 (salir)
source .env                # RESOURCE_GROUP, ACR_NAME, APP_PLAN, APP_NAME, LOCATION

# 6. Web app
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_PLAN --name $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1

# 7. Identidad gestionada (system-assigned)
az webapp identity assign --resource-group $RESOURCE_GROUP --name $APP_NAME

# 8. Rol AcrPull de la identidad sobre el ACR
PRINCIPAL_ID=$(az webapp identity show -g $RESOURCE_GROUP -n $APP_NAME --query principalId -o tsv)
ACR_ID=$(az acr show -g $RESOURCE_GROUP -n $ACR_NAME --query id -o tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull

# 9. La app usa la identidad para el pull
az webapp config set -g $RESOURCE_GROUP -n $APP_NAME --acr-use-identity true --acr-identity '[system]'
az webapp config container set -g $RESOURCE_GROUP -n $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1 \
  --container-registry-url https://$ACR_NAME.azurecr.io

# 10. Runtime, almacenamiento persistente, Always On, logs de contenedor
az webapp config appsettings set -g $RESOURCE_GROUP -n $APP_NAME --settings WEBSITES_PORT=80
az webapp config appsettings set -g $RESOURCE_GROUP -n $APP_NAME --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
az webapp config set -g $RESOURCE_GROUP -n $APP_NAME --always-on true
az webapp log config -g $RESOURCE_GROUP -n $APP_NAME --docker-container-logging filesystem

# 11. URL
APP_URL=$(az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query defaultHostName -o tsv)

# 12. Prueba funcional
curl -X POST "https://$APP_URL/process" -H "Content-Type: text/plain" --data-binary @document.txt
curl https://$APP_URL/documents

# 13. Logs en directo (ver notas)
az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME

# 14. Kudu / SCM
echo "Kudu URL: https://$APP_NAME.scm.azurewebsites.net"

# 15. Ajustes (lectura real de valores)
az webapp config appsettings list -g $RESOURCE_GROUP -n $APP_NAME -o table

# 16. Cleanup (lo ejecuta el alumno)
az group delete --name rg-ai200-appsvc --no-wait --yes
```

## Resultados
| Comprobación | Resultado |
|---|---|
| Build de `docprocessor:v1` (run `cx1`) | OK, 29 s |
| Plan real | `B1` Basic, Linux, `Ready` (el script imprime `P0v3` por una línea de texto fija) |
| `GET /` | 200 en ~0,7 s: `Document Processing API`, `status: running` |
| `POST /process` | 166 caracteres, 22 palabras, `"saved": true` en `/home/processed/<uuid>.json` |
| `GET /documents` | `count: 1`, mismo `document_id`, 1003 bytes |
| Always On | `true`; la plataforma lo hace visible con el user-agent `AlwaysOn` en el log |
| Logs de contenedor | Presentes en el paquete de logs: arranque de gunicorn, `main - INFO` de la app y access log |

## Cómo funciona (lo que se aprendió)

**Plan vs web app.** El plan es la capacidad reservada (equivale a un node pool); la web app se coloca en él. Se paga el plan, no cada app. `B1` = 1 vCPU, 1,75 GB; Always On exige Basic o superior; los deployment slots empiezan en Standard (con B1 no se pueden practicar los slot settings).

**Autenticación al ACR sin secretos.** El ACR se creó con `--admin-enabled false`. Cadena completa: identidad system-assigned en la app → rol `AcrPull` limitado al ACR → `acrUseManagedIdentityCreds=true`. El aviso "Retrieving credentials failed… enable admin" de `config container set` es esperable y **no** se arregla habilitando el admin. En los app settings no aparece ningún `DOCKER_REGISTRY_SERVER_USERNAME/PASSWORD`.

**Estado antes y después de la identidad.** El JSON de `webapp create` mostraba `identity: null`, `acrUseManagedIdentityCreds: false` y `linuxFxVersion: ""`; tras el paso 9, `linuxFxVersion` pasa a `DOCKER|<acr>.azurecr.io/docprocessor:v1`.

**Almacenamiento.** `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` monta `/home` como persistente (ruta fija). `RUN mkdir -p /home/processed` del Dockerfile queda oculto por el montaje; por eso `main.py` recrea la carpeta al arrancar. Para elegir otra ruta existe el montaje de Azure Storage propio (`az webapp config storage-account add --mount-path /data`): Azure Files lectura/escritura (SMB y NFS en Linux), Azure Blob solo lectura; no se puede montar en `/` ni en `/home`; el directorio debe estar vacío; las cuentas con clave deshabilitada no son compatibles. Verificado en Microsoft Learn ("Mount Azure Storage as a local share in App Service"). No practicado en el lab.

**Configuración y logs.** `appsettings set` oculta los valores en su respuesta (`value: null`); hay que comprobar con `appsettings list`. El logging de contenedor se activa explícitamente (`--docker-container-logging filesystem`) y `az webapp log show` no lo refleja bien.

**Kudu = SCM = Advanced Tools.** Cada web app tiene dos hostnames: `<app>.azurewebsites.net` (la app) y `<app>.scm.azurewebsites.net` (sitio de gestión). Se protege con Entra ID; el permiso que lo permite es el del usuario sobre la web app (plano de gestión), no el `AcrPull` (identidad de la carga de trabajo). Analogía: `kubectl exec` + `kubectl logs` + `kubectl describe` en el navegador.

## Respuestas del knowledge check del módulo 2
1. Contenedor en el 8000 con errores de conexión → **`WEBSITES_PORT=8000`**.
2. Que la URL de staging no pase a producción en el swap → **configurarla como slot setting**.

## Incidencias y soluciones
| Problema | Causa | Solución |
|---|---|---|
| Sesión de `az` caducada (`AADSTS130507`) | La instancia del lab dura ~120 min | Nueva instancia y nuevo login con device code + TAP |
| `azdeploy.py` opción 3 dice "App Service Plan: Not created" | `az appservice plan show --query provisioningState` devuelve `null` aunque el plan esté `Ready` | Falso negativo; comprobar con `az appservice plan list` |
| `appsettings set` imprime `value: null` | La CLI oculta los valores en la respuesta | `az webapp config appsettings list` |
| `az webapp log tail` sin salida | Sin confirmar: probable corte del streaming por el proxy corporativo, o ausencia de tráfico durante el tail | Logs verificados con `az webapp log download` |
| `echo $APP_NAM` vacío | Errata en el nombre de la variable | `echo $APP_NAME` |

## Estado al cierre
- Pasos 1-12 verificados con salidas reales.
- Paso 13 (`log tail`): no se confirmó el stream en vivo.
- Paso 14 (Kudu): URL generada; el alumno no llegó a informar de lo que vio en Environment, la consola ni `/home/LogFiles/`.
- Experimento opcional (reiniciar la app y comprobar que `/documents` conserva el documento): no realizado.
- Cleanup: la plataforma de labs desprovisiona los recursos al finalizar el laboratorio (según el docente); además se puede borrar a mano con el comando del paso 16. Pendiente de ejecutar por el alumno.
