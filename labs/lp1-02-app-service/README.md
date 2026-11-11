# Lab LP1-02 · Deploy a container to Azure App Service

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html (índice de guías: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (27/10/2026): parcial.** Hechos los pasos 0-16 y 19 con salidas reales. **No confirmado:** el stream en vivo de `az webapp log tail` (paso 17; los logs sí se vieron con `log download`). **No hecho:** inspeccionar Kudu (paso 18, solo se generó la URL) y el experimento de persistencia tras reiniciar (paso 20). **Cleanup: no verificado por el alumno con `az group exists`**; el 29/10 `rg-ai200-appsvc` ya no existía (lo desprovisionó la plataforma al cerrar el lab).
- **Sesión:** [`sesiones/2026-10-27-sesion-02-contenedores.md`](../../sesiones/2026-10-27-sesion-02-contenedores.md) (no hay transcripción de esa fecha). Notas del módulo: [`docs/modulos/01-alojamiento-contenedores.md`](../../docs/modulos/01-alojamiento-contenedores.md). Documentación MS Learn: [Deploy containers to Azure App Service](https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-app-service/).
- Lab anterior: [LP1-01 · ACR Tasks](../lp1-01-acr-tasks/README.md). Lab siguiente: [LP2-01 · Container Apps](../lp2-01-aca-deploy/README.md). (El lab 3 del LP1, sidecar, no se hizo: era opcional.)
- Material de partida versionado en esta carpeta: `app-svc-container-python.zip`, `azdeploy.py` (ya editado), `document.txt` y `api/`. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md).

Ejecutado en Linux (bash); la plataforma da los mismos pasos en PowerShell. Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. De este lab se guardaron **fragmentos** de las salidas (los que se citan); donde no hay salida guardada se dice. IDs de suscripción, tenant y principal: `<sub-id>`, `<tenant-id>`, `<principal-id>`.

## Objetivo (en cristiano)
Coger la imagen que está en un ACR y ponerla a servir por HTTPS en **App Service**, sin guardar **ninguna contraseña** del registry: la web app se identifica con una **identidad gestionada** que tiene el rol `AcrPull` sobre ese ACR. Luego se ajusta cómo corre (puerto, disco persistente, que no se duerma, logs) y se mira dónde diagnosticar.

El hilo conductor son **tres pasos separados** para que la app pueda hacer pull: identidad (quién soy) → rol `AcrPull` (qué puedo hacer) → `acrUseManagedIdentityCreds=true` (úsala para el pull). Si falta uno, la imagen no baja.

## Qué se construye
```
                    ┌──────────────── resource group rg-ai200-appsvc (canadacentral) ───────────────┐
 usuario (HTTPS) ──►│  App Service plan  plan-docprocessor-<hash>   (B1, Linux)                      │
   TLS lo termina   │   └ Web app  app-docprocessor-<hash>                                           │
   la plataforma    │        ├ identidad system-assigned ──(rol AcrPull)──┐                          │
                    │        ├ contenedor gunicorn :80  (WEBSITES_PORT=80)│ pull                      │
                    │        └ /home/processed  (persistente)             ▼                          │
                    │  ACR  acr<hash>  (Basic, admin deshabilitado)  docprocessor:v1                  │
                    └────────────────────────────────────────────────────────────────────────────────┘
   Diagnóstico: log de contenedor (stdout/stderr)  ·  Kudu / SCM  <app>.scm.azurewebsites.net
```
- `api/Dockerfile`: `python:3.11-slim`, instala `requirements.txt` (flask 3.0.0, gunicorn 22.0.0), `mkdir -p /home/processed`, `EXPOSE 80`, `CMD gunicorn --bind 0.0.0.0:80 --workers 2 --access-logfile - main:app`.
- `api/main.py`: procesado de documentos **simulado**. `GET /`, `GET /health`, `POST /process` (guarda el resultado en `/home/processed/<id>.json`), `GET /documents`, `GET /documents/<id>`. El análisis (entidades, sentimiento) es fijo; las estadísticas (caracteres, palabras) son reales.
- `azdeploy.py`: menú. **1** = resource group + ACR (`--admin-enabled false`) + `az acr build` de `docprocessor:v1`. **2** = App Service plan Linux + `.env`. **3** = estado. **4** = salir. **La web app no la crea el script**: la creas tú.

**Analogía K8s:** plan = node pool (se paga el plan, no cada app); web app = Deployment; identidad + rol = ServiceAccount + RoleBinding (workload identity); `AcrPull` = un `imagePullSecret` sin secreto; Kudu = `kubectl exec` + `logs` + `describe` en el navegador.

---

## Paso 0 · Terminal y login (instancia nueva del lab)
**Por qué:** cada instancia del lab dura ~120 min y trae su propia sesión; al caducar la del lab 1 hubo que abrir otra. El proxy de empresa obliga a exportar `REQUESTS_CA_BUNDLE` en cada terminal (ver [LP1-01, paso 0](../lp1-01-acr-tasks/README.md#paso-0--preparar-la-máquina-y-la-terminal)).
```bash
cd ~/claude/AI-200-Developing/labs/lp1-02-app-service
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az logout
az login --use-device-code   # incógnito → usuario del lab + Temporary Access Pass
```
Salida: no guardada.

⚠️ **Lo que pasó:** con la instancia anterior caducada, `az` respondía `AADSTS130507`. Arreglo: nueva instancia del lab y nuevo login con device code + TAP.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
az group list -o table
```
Esperado: suscripción y usuario del lab; lista de grupos vacía. Si sale `AADSTS130507`, la instancia caducó: abre otra y repite el login.

## Paso 1 · Registrar los proveedores
**Por qué:** hacen falta dos servicios: ACR (`Microsoft.ContainerRegistry`) y App Service (`Microsoft.Web`).
```bash
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Web
```
Salida: no guardada (ambos ya estaban registrados).

✅ **Comprobación:**
```bash
for ns in Microsoft.ContainerRegistry Microsoft.Web; do az provider show -n $ns --query registrationState -o tsv; done
```
Esperado: `Registered` dos veces. Si sale `Registering`, espera un minuto y repite.

## Paso 2 · Ajustar `azdeploy.py` a la plataforma
**Por qué:** la guía de la plataforma difiere de la oficial: región `canadacentral` y plan `B1`, porque la suscripción compartida del lab no permite Premium (`P0v3`) y tiene cuotas por región.

| Línea | Antes | Después |
|---|---|---|
| 5 | `rg = "<your-resource-group-name>"` | `rg = "rg-ai200-appsvc"` |
| 6 | `location = "<your-azure-region>"` | `location = "canadacentral"` (minúsculas, sin espacios) |
| 224 | `"--sku", "P0v3",` | `"--sku", "B1",` (se cambia el **valor**, no la clave `--sku`) |

La copia versionada ya está editada:
```bash
grep -nE '^(rg|location) =|"--sku", "B1"' azdeploy.py
```
Salida real (de la copia del repo):
```text
5:rg = "rg-ai200-appsvc"  # Resource Group name
6:location = "canadacentral"   # Azure region for the resources
224:                "--sku", "B1",
```
**Qué mirar:** la línea 230 seguirá imprimiendo `SKU: P0v3 (Premium v3 tier)`: es texto fijo, el plan real es `B1`.

✅ **Comprobación:** las tres líneas de arriba. Si se borró la clave `--sku`, la opción 2 del menú falla con un error de argumento no reconocido.

## Paso 3 · Opción 1: ACR + imagen `docprocessor:v1`
**Por qué:** la app necesita su imagen en un registry. El ACR se crea con `--admin-enabled false`: no hay usuario/contraseña de administrador, así que el pull **tendrá** que ser por identidad.
```bash
python3 azdeploy.py      # menú → 1
```
Por dentro: `az group create` + `az acr create --sku Basic --admin-enabled false` + `az acr build --image docprocessor:v1 --file api/Dockerfile api/`.

Salida: no guardada (el script oculta la salida del build y limpia la pantalla al volver al menú).

✅ **Comprobación:**
```bash
az acr list -g rg-ai200-appsvc --query "[].{name:name, admin:adminUserEnabled}" -o table
az acr task list-runs --registry <acr> -o table
```
Salida real (fragmento): run `cx1` (build de `docprocessor:v1`) `Succeeded` en 29 s; el prefijo `cx` es de Canada Central (en East US era `ca`). Si la run sale `Failed`: `az acr task logs --registry <acr> --run-id cx1`, y lanzar el script desde la carpeta donde está `api/`.

## Paso 4 · Opción 2: App Service plan y `.env`
**Por qué:** el plan es la capacidad reservada (1 vCPU / 1,75 GB en B1). `--is-linux` es obligatorio para contenedores Linux. Esta opción también escribe `.env`.
```bash
python3 azdeploy.py      # menú → 2, luego 3 (estado) y 4 (salir)
```
Por dentro: `az appservice plan create --sku B1 --is-linux` y escritura de `.env` / `.env.ps1`.

Salida: no guardada la de la opción 2.

⚠️ **Lo que pasó:** la opción 3 dijo `App Service Plan: Not created`. Es un **falso negativo**: el script usa `az appservice plan show --query provisioningState`, que devuelve `null` aunque el plan esté listo.

✅ **Comprobación:**
```bash
az appservice plan list -g rg-ai200-appsvc --query "[].{name:name, sku:sku.name, state:provisioningState, status:status}" -o table
```
Salida real (fragmento): `plan-docprocessor-<hash>  B1  Succeeded  Ready`. Si no sale ninguna fila, la opción 2 falló: relánzala y mira el `Error: … failed`; si es de cuota, cambia de región.

## Paso 5 · Cargar las variables
**Por qué:** los comandos siguientes usan `$RESOURCE_GROUP`, `$ACR_NAME`, `$APP_PLAN`, `$APP_NAME` y `$LOCATION`. Solo las escribe la opción 2.
```bash
source .env
```
✅ **Comprobación:**
```bash
echo "$RESOURCE_GROUP $ACR_NAME $APP_PLAN $APP_NAME $LOCATION"
```
Esperado: `rg-ai200-appsvc acr<hash> plan-docprocessor-<hash> app-docprocessor-<hash> canadacentral`. Si sale vacío, repite `source .env` en esta terminal.

⚠️ **Lo que pasó:** `echo $APP_NAM` salió vacío: errata en el nombre. Bash no avisa de variables inexistentes.

## Paso 6 · Crear la web app
**Por qué:** es lo que se coloca en el plan (el Deployment sobre el node pool). Se crea apuntando a la imagen, pero **aún no puede descargarla**: no tiene identidad ni configuración de registry.
```bash
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_PLAN --name $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1
```
Salida real (campos relevantes de un JSON largo):
```text
"state": "Running",
"kind": "app,linux,container",
"defaultHostName": "app-docprocessor-<hash>.azurewebsites.net",
"enabledHostNames": [ "app-docprocessor-<hash>.azurewebsites.net", "app-docprocessor-<hash>.scm.azurewebsites.net" ],
"identity": null,
"acrUseManagedIdentityCreds": false,
"linuxFxVersion": ""
```
**Qué mirar:** `Running` es el estado del **recurso**, no del contenedor. `identity: null` y `acrUseManagedIdentityCreds: false` dicen que todavía no hay forma de hacer pull. Los dos hostnames: la app y su sitio de gestión `.scm.` (Kudu). El JSON trae el ID de suscripción y un `customDomainVerificationId`: no se copian al repo.

✅ **Comprobación:**
```bash
az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query "{state:state, kind:kind, identity:identity}" -o json
```
Esperado: `Running`, `app,linux,container`, `identity: null`. Si dice que no existe, revisa `$APP_PLAN` y que el plan sea Linux.

## Paso 7 · Identidad gestionada (system-assigned)
**Por qué:** «quién soy». Crea un service principal en Entra ID ligado al ciclo de vida de la app (nace y muere con ella). Sola no puede hacer nada: falta el rol. La alternativa *user-assigned* es un recurso aparte, reutilizable (habitual en AKS).
```bash
az webapp identity assign --resource-group $RESOURCE_GROUP --name $APP_NAME
```
Salida real (saneada):
```text
{
  "principalId": "<principal-id>",
  "tenantId": "<tenant-id>",
  "type": "SystemAssigned",
  "userAssignedIdentities": null
}
```
✅ **Comprobación:**
```bash
az webapp identity show -g $RESOURCE_GROUP -n $APP_NAME --query type -o tsv
```
Esperado: `SystemAssigned`. Si sale vacío, repite el `assign`.

## Paso 8 · Rol `AcrPull` sobre el ACR
**Por qué:** «qué puedo hacer»: solo descargar imágenes, solo de ese ACR (mínimo privilegio). Sin él, el pull falla con `unauthorized`/403.
```bash
PRINCIPAL_ID=$(az webapp identity show --resource-group $RESOURCE_GROUP --name $APP_NAME --query principalId --output tsv)
ACR_ID=$(az acr show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query id --output tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull
```
Salida real (campos relevantes, saneada):
```text
"principalType": "ServicePrincipal",
"roleDefinitionId": "/subscriptions/<sub-id>/providers/Microsoft.Authorization/roleDefinitions/7f951dda-…",
"scope": "/subscriptions/<sub-id>/resourceGroups/rg-ai200-appsvc/providers/Microsoft.ContainerRegistry/registries/acr<hash>"
```
**Qué mirar:** `$( … )` guarda la salida de un comando en una variable; `--query … -o tsv` saca un valor plano. `7f951dda-…` es el ID fijo del rol `AcrPull`. El `scope` acaba en `/registries/<acr>`: vale solo para ese registry, no para el grupo ni la suscripción. La asignación tarda 1-2 min en propagarse.

✅ **Comprobación:**
```bash
az role assignment list --assignee $PRINCIPAL_ID --scope $ACR_ID --query "[].roleDefinitionName" -o tsv
```
Esperado: `AcrPull`. Si sale vacío, comprueba que `$PRINCIPAL_ID` y `$ACR_ID` no están vacíos (`[ -n "$PRINCIPAL_ID" ] && echo ok`) y repite el `create`. En el portal: ACR → Control de acceso (IAM) → Asignaciones de roles.

## Paso 9 · Decirle a la app que use la identidad para el pull
**Por qué:** tener identidad y rol no basta: App Service tiene que saber que debe usarlos (`acrUseManagedIdentityCreds`). Después se le dice qué imagen y de qué registry.
```bash
az webapp config set -g $RESOURCE_GROUP -n $APP_NAME --acr-use-identity true --acr-identity '[system]'
az webapp config container set -g $RESOURCE_GROUP -n $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1 \
  --container-registry-url https://$ACR_NAME.azurecr.io
```
Salida real (fragmentos): del primero, el JSON de configuración con `acrUseManagedIdentityCreds: true` y `linuxFxVersion` aún vacío. Del segundo:
```text
Retrieving credentials failed … run 'az acr update --admin-enabled true' …
(después, los app settings: DOCKER_REGISTRY_SERVER_URL, DOCKER_CUSTOM_IMAGE_NAME,
 WEBSITES_ENABLE_APP_SERVICE_STORAGE=false)
```
**Qué mirar:**
- El aviso `Retrieving credentials failed … --admin-enabled true` es **esperable y no se arregla habilitando el admin**: el CLI busca primero usuario/contraseña, no los encuentra y sigue con la identidad.
- No aparece ningún `DOCKER_REGISTRY_SERVER_USERNAME/PASSWORD`: no hay secretos guardados.
- Las comillas en `'[system]'` evitan que bash interprete los corchetes.
- `linuxFxVersion` pasa a `DOCKER|acr<hash>.azurecr.io/docprocessor:v1`.

✅ **Comprobación:**
```bash
az webapp config show -g $RESOURCE_GROUP -n $APP_NAME --query "{mi:acrUseManagedIdentityCreds, image:linuxFxVersion}" -o table
```
Esperado: `True` y `DOCKER|acr<hash>.azurecr.io/docprocessor:v1`. Si `mi` es `False`, repite el `config set`; si la imagen está vacía, repite el `config container set`.

## Paso 10 · Puerto del contenedor (`WEBSITES_PORT`)
**Por qué:** App Service solo asume 80 u 8080; si el contenedor escucha en otro, hay errores de conexión (knowledge check: contenedor en el 8000 → `WEBSITES_PORT=8000`). Aquí gunicorn ya escucha en 80: es declarativo. Un app setting llega al contenedor como variable de entorno.
```bash
az webapp config appsettings set -g $RESOURCE_GROUP -n $APP_NAME --settings WEBSITES_PORT=80
```
Salida real (fragmento): la lista de settings con `"value": null` en todos.

**Qué mirar:** `value: null` **no** significa que no se guardara: la CLI oculta los valores en la respuesta de `set`.

✅ **Comprobación:**
```bash
az webapp config appsettings list -g $RESOURCE_GROUP -n $APP_NAME --query "[?name=='WEBSITES_PORT'].value" -o tsv
```
Esperado: `80`. Si sale vacío, repite el `set`.

## Paso 11 · Almacenamiento persistente en `/home`
**Por qué:** sin esto, `/home/processed` es efímero y los JSON procesados se pierden al reiniciar. Con `true`, `/home` se monta como almacenamiento compartido y persistente (ruta **fija**).
```bash
az webapp config appsettings set -g $RESOURCE_GROUP -n $APP_NAME --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
```
Salida: igual que el paso 10 (`value: null`).

**Qué mirar:** el montaje tapa lo que la imagen tuviera en `/home` (el `RUN mkdir -p /home/processed` del Dockerfile queda oculto): por eso `main.py` recrea la carpeta al arrancar. Para elegir otra ruta existe el montaje de Azure Storage propio (`az webapp config storage-account add --mount-path /data`): Files lectura/escritura, Blob solo lectura, no en `/` ni `/home` (verificado en MS Learn; no practicado).

✅ **Comprobación:**
```bash
az webapp config appsettings list -g $RESOURCE_GROUP -n $APP_NAME --query "[?name=='WEBSITES_ENABLE_APP_SERVICE_STORAGE'].value" -o tsv
```
Esperado: `true`. Si sale `false` (lo dejó así el paso 9), repite el `set`.

## Paso 12 · Always On
**Por qué:** sin él la app se descarga tras ~20 min sin tráfico y la siguiente petición sufre un arranque en frío. Exige plan Basic o superior (B1 vale).
```bash
az webapp config set -g $RESOURCE_GROUP -n $APP_NAME --always-on true
```
✅ **Comprobación:**
```bash
az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query '{state:state,alwaysOn:siteConfig.alwaysOn}'
```
Salida real: `alwaysOn: true`. Si sale `false`, revisa que el plan no sea Free/Shared y repite. En el log se ve como peticiones `GET /` con user-agent `AlwaysOn`.

## Paso 13 · Activar los logs del contenedor
**Por qué:** el stdout/stderr del contenedor no se guarda si no se activa explícitamente; sin esto no hay `log tail` ni `log download` útiles.
```bash
az webapp log config -g $RESOURCE_GROUP -n $APP_NAME --docker-container-logging filesystem
```
Salida real (fragmento): `applicationLogs.fileSystem.level: Off`.

**Qué mirar:** la salida **no refleja** el ajuste (y `az webapp log show` devuelve `dockerContainerLogging: null`), pero los logs existen: se comprueba en el paso 17 con `log download`. Retención: 3 días, 100 MB.

✅ **Comprobación:** la real es el paso 17 (aparece `*_default_docker.log` en el zip). Si no aparece, repite este comando.

## Paso 14 · URL de la app y primera petición
**Por qué:** comprobar que el contenedor arranca y responde. La plataforma termina el TLS: tú entras por HTTPS y el contenedor recibe HTTP en el 80.
```bash
APP_URL=$(az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query defaultHostName -o tsv)
echo "Application URL: https://$APP_URL"
curl -s "https://$APP_URL/"
```
Salida real (fragmento): `GET /` → 200 en ~0,7 s con `Document Processing API` y `status: running`.

**Qué mirar:** si se olvida el `echo`, la variable queda guardada pero no se ve (fallo habitual). La primera petición puede tardar: el primer arranque descarga la imagen.

✅ **Comprobación:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' "https://$APP_URL/health"
```
Esperado: `200`. Si sale 502/503, espera un minuto (primer pull). Si persiste, `unauthorized`/`ImagePullBackOff` en los logs = repasa pasos 7-9; errores de conexión = paso 10.

## Paso 15 · Procesar un documento (`POST /process`)
**Por qué:** prueba funcional: la app recibe texto, lo analiza y **escribe** el resultado en `/home/processed`.
```bash
curl -X POST "https://$APP_URL/process" -H "Content-Type: text/plain" --data-binary @document.txt
```
Salida real (resumen): `statistics` con **166 caracteres y 22 palabras** (reales), `analysis` simulado (siempre las mismas entidades) y `"storage": {"saved": true, "path": "/home/processed/<uuid>.json"}`.

**Qué mirar:** `--data-binary` manda el fichero tal cual (`-d` podría alterar los saltos de línea). En PowerShell: `Invoke-RestMethod -Method Post -Uri … -ContentType "text/plain" -Body $body`.

✅ **Comprobación:** `"saved": true` en la respuesta. Si sale `false`, revisa el paso 11 y los logs.

## Paso 16 · Listar documentos (`GET /documents`)
**Por qué:** confirmar que lo escrito en `/home/processed` se puede leer.
```bash
curl https://$APP_URL/documents
```
Salida real (resumen): `count: 1`, mismo `document_id` que el paso 15, `size_bytes: 1003`.

**Qué mirar:** `1003` es el tamaño del JSON guardado (con `indent=2`), no del texto original. Esto prueba escritura y lectura, **no** persistencia (eso es el paso 20).

✅ **Comprobación:** `count` ≥ 1 y el `document_id` del paso 15. Si `count: 0`, el paso 15 no guardó: revisa `"saved"`.

## Paso 17 · Ver los logs del contenedor
**Por qué:** es lo primero que se mira cuando la app no arranca o falla una petición.
```bash
az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME                         # en vivo (Ctrl+C para salir)
az webapp log download -g $RESOURCE_GROUP -n $APP_NAME --log-file logs.zip  # alternativa que sí funcionó
```
⚠️ **Lo que pasó:** `log tail` no mostró nada. Sin confirmar la causa: probable corte del streaming por el proxy de empresa, o que no hubo tráfico mientras estaba abierto (solo muestra líneas **nuevas**). Se recurrió a `log download`.

Salida real de `logs.zip` (`LogFiles/*_default_docker.log`; líneas resumidas, no literales):
```text
Listening at: http://0.0.0.0:80   (gunicorn, dos workers)
main - INFO - Document processing request received
main - INFO - Result saved to /home/processed/<uuid>.json
169.254.130.1 … "POST /process" 200
… "GET /" … HealthCheck/1.0
… "GET /" … AlwaysOn
```
**Qué mirar:** `169.254.130.1` es el front-end interno de App Service, no tu IP. `HealthCheck/1.0` y `AlwaysOn` son tráfico de la plataforma.

✅ **Comprobación:** `unzip -l logs.zip | grep default_docker` debe listar al menos un fichero. Para probar el `tail` de verdad: abrirlo en una terminal y lanzar `curl https://$APP_URL/` en otra — **pendiente**.

## Paso 18 · Consola Kudu (SCM) — no hecho
**Por qué:** cada web app tiene un segundo hostname de gestión, `<app>.scm.azurewebsites.net` (SCM = Source Control Manager; Kudu = el motor; el portal lo llama *Advanced Tools*). Se entra con tu usuario de Entra (plano de gestión), no con la identidad de la app.
```bash
echo "Kudu URL: https://$APP_NAME.scm.azurewebsites.net"
```
Hecho: se generó la URL. **No hecho:** no se registró qué se vio dentro. Esperado según la guía:
- *Environment*: aparecen `WEBSITES_PORT` y `WEBSITES_ENABLE_APP_SERVICE_STORAGE`.
- *SSH → Kudu*: shell en el navegador (`ls /home/processed` debería mostrar el `<uuid>.json`).
- *File Manager*: `/home/LogFiles/` con los logs.
- El sitio SCM es aparte del contenedor de la app: no ve todo su sistema de ficheros ni sus procesos.

✅ **Comprobación:** la URL abre en el navegador tras autenticarte. Si da 401/403, entra con el usuario del lab (no el de empresa).

## Paso 19 · Ver los app settings con sus valores
**Por qué:** `set` oculta los valores; `list` es la forma de ver qué tiene realmente la app.
```bash
az webapp config appsettings list -g $RESOURCE_GROUP -n $APP_NAME -o table
```
Salida real (resumen): `WEBSITES_PORT=80`, `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true`, `DOCKER_REGISTRY_SERVER_URL=https://acr<hash>.azurecr.io`, `DOCKER_CUSTOM_IMAGE_NAME` y ningún `DOCKER_REGISTRY_SERVER_USERNAME/PASSWORD`.

✅ **Comprobación:** los cuatro settings de arriba y **ningún** `…PASSWORD`. Si aparece una contraseña, alguien habilitó el admin del ACR: no es lo que pide el lab.

## Paso 20 · Persistencia tras reiniciar — no hecho
**Por qué:** demostrar que `/home` sobrevive a un reinicio (lo que realmente aporta el paso 11). Experimento opcional, no está en la guía.
```bash
az webapp restart -g $RESOURCE_GROUP -n $APP_NAME
curl https://$APP_URL/documents
```
Esperado: el mismo `count: 1` y `document_id` que en el paso 16. Si sale `count: 0`, `WEBSITES_ENABLE_APP_SERVICE_STORAGE` no está a `true` (paso 11).

---

## Cleanup (obligatorio al acabar)
**Por qué:** borra todo lo del grupo de una vez (ACR, plan, web app y la asignación de rol). Si el grupo fuera preexistente, también borraría recursos ajenos al lab.
```bash
az group delete --name rg-ai200-appsvc --no-wait --yes
az group exists --name rg-ai200-appsvc     # true mientras borra, false al terminar
```
Salida: **no guardada**; no consta que el alumno lanzara el `delete` antes de cerrar la instancia.

**No verificado con `az group exists` al cerrar el lab.** El 29/10/2026 `rg-ai200-appsvc` ya no existía: la plataforma desprovisiona los recursos al finalizar el laboratorio (y la sesión de `az` caduca con la instancia, `AADSTS130507`). Si al comprobarlo sale `true` pasados 10-15 min, mira `az group show -n rg-ai200-appsvc --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`.

## Resumen de resultados
| Comprobación | Resultado |
|---|---|
| Build de `docprocessor:v1` (run `cx1`) | OK, 29 s |
| Plan real | `B1`, Linux, `Succeeded` / `Ready` (el script imprime `P0v3` por un texto fijo) |
| `GET /` | 200 en ~0,7 s: `Document Processing API`, `status: running` |
| `POST /process` | 166 caracteres, 22 palabras, `"saved": true` en `/home/processed/<uuid>.json` |
| `GET /documents` | `count: 1`, mismo `document_id`, 1003 bytes |
| Always On | `true`; visible con el user-agent `AlwaysOn` en el log |
| Logs de contenedor | En `log download`: arranque de gunicorn, `main - INFO` y access log |

## Resumen de incidencias
| Paso | Síntoma | Causa | Arreglo |
|---|---|---|---|
| 0 | `AADSTS130507` | La instancia del lab (~120 min) caducó | Nueva instancia y login con device code + TAP |
| 4 | Opción 3: `App Service Plan: Not created` | `plan show --query provisioningState` devuelve `null` | Falso negativo: `az appservice plan list` |
| 5 | `echo $APP_NAM` vacío | Errata en la variable | `echo $APP_NAME` |
| 9 | `Retrieving credentials failed … --admin-enabled true` | El CLI busca primero credenciales de admin | Esperable: **no** habilitar el admin |
| 10-11 | `appsettings set` imprime `value: null` | La CLI oculta los valores | `az webapp config appsettings list` |
| 13 | `log config`/`log show` no reflejan el logging | Salida engañosa de la CLI | Comprobar con `log download` |
| 17 | `log tail` sin salida | Sin confirmar: proxy o falta de tráfico | `az webapp log download` |

## Troubleshooting (de la guía)
| Síntoma | Qué comprobar |
|---|---|
| Variables vacías o sesión equivocada | `az account show`; `source .env` (bash) o `. .\.env.ps1` (PowerShell) |
| Falla el build (el script oculta la salida) | `az acr task list-runs --registry $ACR_NAME -o table` y `az acr task logs --registry $ACR_NAME --run-id <id>` |
| `ImagePullBackOff` / `unauthorized` / 403 | `az webapp identity show`; `AcrPull` sobre el ACR (1-2 min de propagación); `az webapp config show --query acrUseManagedIdentityCreds -o tsv` = `true`; repetir `config container set` |
| 502/503 recién desplegado | Esperar un minuto (primer pull); logs de contenedor |
| La persistencia no funciona | `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` en `appsettings list` |

## Para el examen (contenedores 20-25 %; seguridad/monitorización 20-25 %)
- Knowledge check del módulo 2: contenedor en el 8000 con errores de conexión → **`WEBSITES_PORT=8000`**; que la URL de staging no pase a producción en el swap → **slot setting** (con B1 no hay slots: es teoría; empiezan en Standard).
- También: managed identity + `AcrPull`, startup command que sustituye al `CMD`, Key Vault references en app settings, log stream y Kudu.

## Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab:

| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (línea 176) | `--sku Basic`, `--admin-enabled false` |
| Subir la imagen | `az acr build` (línea 196) | `docprocessor:v1` desde `api/` |
| Vincular (pull) | pasos 7-9 de este README | Lo haces tú: identidad system-assigned + `AcrPull` + `--acr-use-identity`. El script no crea la web app |

- **Push y pull son permisos distintos:** el build lo hace ACR con tu `az login`; la descarga la hace App Service con su identidad y el rol **AcrPull**.
