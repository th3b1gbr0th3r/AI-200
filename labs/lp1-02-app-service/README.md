# Lab LP1-02 · Deploy a container to Azure App Service

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html
Documentación oficial del módulo (MS Learn): https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-app-service/
Notas de clase del learning path: [`docs/modulos/01-alojamiento-contenedores.md`](../../docs/modulos/01-alojamiento-contenedores.md)
Material de partida: `app-svc-container-python.zip` (https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/app-svc-container-python.zip). No se versiona aquí: descargar y descomprimir en esta carpeta (`azdeploy.py`, `document.txt`, `api/`).

Ejecutado en Linux (bash). La plataforma del curso da los mismos pasos en PowerShell. Diferencias de la guía de la plataforma respecto a la oficial: región `canadacentral` y SKU del plan `B1` (línea 224 de `azdeploy.py`, el script trae `P0v3`).

## Objetivo
Desplegar una imagen **Linux** guardada en ACR en **Azure App Service**, autenticándose contra el registry **sin credenciales** (identidad gestionada + rol `AcrPull`), configurar su comportamiento en ejecución (puerto, almacenamiento persistente, Always On) y observarla con logs y la consola Kudu.

Al terminar debes ser capaz de explicar: la diferencia entre App Service plan y web app, cómo obtiene la app permiso para hacer `pull`, para qué sirven `WEBSITES_PORT` y `WEBSITES_ENABLE_APP_SERVICE_STORAGE`, y dónde se miran los logs y la configuración.

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
- El **plan** es la capacidad (equivale a un node pool); la **web app** es lo que se coloca en él.
- La app (`api/main.py`) simula el procesado de documentos: `POST /process` guarda un JSON en `/home/processed` y `GET /documents` lo lista.

## Fases del lab
| Fase | Qué haces | Qué demuestra |
|---|---|---|
| 1. Despliegue base | `azdeploy.py` opciones 1 y 2: ACR + imagen y plan B1 | La infraestructura de soporte; la web app no la crea el script |
| 2. Web app | `az webapp create` | Existe y está `Running`, pero **no puede hacer pull** (`identity: null`) |
| 3. Identidad | `az webapp identity assign` | "Quién soy": service principal ligado a la app |
| 4. Permiso | `az role assignment create … AcrPull` | "Qué puedo hacer": solo descargar, solo de ese ACR |
| 5. Pull con identidad | `config set --acr-use-identity` + `config container set` | Sin usuario/contraseña de ACR (el aviso de credenciales es esperable) |
| 6. Runtime | `WEBSITES_PORT`, `WEBSITES_ENABLE_APP_SERVICE_STORAGE`, `--always-on`, `log config` | Puerto, persistencia en `/home`, no dormirse y logs de contenedor |
| 7. Verificación | `curl /`, `POST /process`, `GET /documents` | La app responde y escribe en almacenamiento persistente |
| 8. Observabilidad | logs, Kudu, `appsettings list` | Dónde mirar cuando algo falla |
| 9. Cleanup | `az group delete` | Se borra todo de una vez |

## Cómo se relaciona con lo que ya sabes (K8s) y con el examen
- Identidad + rol = ServiceAccount + RoleBinding (workload identity). Plan = node pool; web app = Deployment; Kudu = `kubectl exec` + `logs` + `describe` en el navegador.
- Examen (contenedores 20-25 %; seguridad/monitorización 20-25 %): managed identity + `AcrPull`, `WEBSITES_PORT` (fallo de despliegue más común), startup command que sustituye al `CMD`, slot settings que no viajan en el swap (con B1 no hay slots: es teoría), Key Vault references, log stream y Kudu.

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

## Comandos al detalle

Convenciones: `$VAR` = variable cargada con `source .env`; `\` = continuación de línea en bash; `-o tsv` = valor plano sin comillas; `-g` = `--resource-group`, `-n` = `--name`. Los comandos de los pasos 1-3 (proxy, proveedores, login) son los del lab 1; aquí se detallan los nuevos.

### 1. Edición de `azdeploy.py` (antes de ejecutarlo)
| Línea | Antes | Después | Por qué |
|---|---|---|---|
| 5 | `rg = "<your-resource-group-name>"` | `rg = "rg-ai200-appsvc"` | Nombre libre; el script crea el grupo si no existe |
| 6 | `location = "<your-azure-region>"` | `location = "canadacentral"` | Región indicada por la guía de la plataforma; escrita en minúsculas y sin espacios |
| 224 | `"--sku", "P0v3",` | `"--sku", "B1",` | La suscripción del lab no permite Premium; **se cambia el valor, no la clave `--sku`** |
- **Trampa:** la línea 230 sigue imprimiendo `SKU: P0v3 (Premium v3 tier)`; es texto fijo. El plan real es `B1`.
- **Error típico:** si se borra por error la clave `--sku`, la opción 2 del menú falla con un error de argumento no reconocido.

### 2. `az provider register --namespace Microsoft.ContainerRegistry` y `--namespace Microsoft.Web`
- Igual que en el lab 1 (ver allí el desglose). `Microsoft.Web` es el proveedor de App Service. Ambos ya estaban `Registered` en el lab.

### 3. `python3 azdeploy.py` (menú)
```
Opción 1  →  az group create  +  az acr create --sku Basic --admin-enabled false  +  az acr build --image docprocessor:v1 --file api/Dockerfile api/
Opción 2  →  az group create (ya existe: lo salta)  +  az appservice plan create --sku B1 --is-linux   y escribe .env
Opción 3  →  solo lectura: estado de ACR, imagen, plan y web app
Opción 4  →  salir
```
- **`--admin-enabled false`:** el registry no tiene usuario/contraseña de administrador. Obliga a usar identidad gestionada para el `pull`.
- **`az appservice plan create … --is-linux`:** el plan es la capacidad (node pool); `--is-linux` es obligatorio para contenedores Linux y no se puede mezclar con Windows en el mismo plan.
- **Nombres derivados** de un hash del usuario: `acr<hash>`, `plan-docprocessor-<hash>`, `app-docprocessor-<hash>`. El `.env` solo lo escribe la opción 2.
- **La opción 3 da un falso negativo** para el plan ("Not created"): `az appservice plan show --query provisioningState` devuelve `null`. Se comprueba con `az appservice plan list -g $RESOURCE_GROUP -o table` (`Succeeded` / `Ready`).
- **Error típico:** la pantalla se limpia al volver al menú y se pierde el resultado; se comprueba con las lecturas de la sección 18.

### 4. `source .env`
- Carga `RESOURCE_GROUP`, `ACR_NAME`, `APP_PLAN`, `APP_NAME`, `LOCATION`. Se repite en cada terminal nueva. Errata típica: `echo $APP_NAM` devuelve vacío sin error.

### 5. `az webapp create`
```
az webapp create  --resource-group $RESOURCE_GROUP  --plan $APP_PLAN  --name $APP_NAME  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1
                          │                            │                  │                          └ imagen con formato registry/repositorio:tag
                          │                            │                  └ nombre global → <name>.azurewebsites.net
                          │                            └ plan donde se coloca (B1)
                          └ grupo
```
- **Qué hace:** crea la web app en el plan. Equivale a crear el Deployment sobre un node pool.
- **Qué esperar:** un JSON largo. Los campos que importan: `state: Running`, `kind: app,linux,container`, `defaultHostName`, `enabledHostNames` (la app y el sitio `.scm.`), `identity: null`, `acrUseManagedIdentityCreds: false`, `linuxFxVersion: ""`.
- **Trampa:** `Running` es el estado del recurso, no de tu contenedor. La app **todavía no puede hacer pull** (sin identidad ni configuración).
- **Seguridad:** el JSON incluye el ID de suscripción y un `customDomainVerificationId`; no se copia al repo.

### 6. `az webapp identity assign --resource-group $RESOURCE_GROUP --name $APP_NAME`
- **Qué hace:** crea una identidad **system-assigned**: un service principal en Entra ID ligado al ciclo de vida de la app (nace y muere con ella).
- **Qué esperar:** `{"principalId": "…", "tenantId": "…", "type": "SystemAssigned", "userAssignedIdentities": null}`. El `principalId` es el "quién soy".
- **Por qué:** es el equivalente a dar a un pod un ServiceAccount con workload identity. La identidad sola no puede hacer nada: falta el rol.
- **Alternativa:** *user-assigned*, un recurso independiente reutilizable por varios recursos (habitual en AKS).

### 7. Variables con `$(…)` y `az role assignment create`
```bash
PRINCIPAL_ID=$(az webapp identity show --resource-group $RESOURCE_GROUP --name $APP_NAME --query principalId --output tsv)
ACR_ID=$(az acr show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query id --output tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull
```
```
$( … )                   sustitución de comandos: ejecuta lo de dentro y pone su salida en la variable
--query principalId      consulta JMESPath: extrae solo ese campo del JSON
--output tsv             valor plano, sin comillas ni JSON
--assignee               quién recibe el permiso (la identidad de la web app)
--scope                  dónde vale: el ID completo del ACR, no el grupo ni la suscripción
--role AcrPull           qué puede hacer: solo descargar imágenes (mínimo privilegio)
```
- **Qué esperar:** JSON con `principalType: ServicePrincipal`, `roleDefinitionId` terminado en `7f951dda-…` (el ID fijo de `AcrPull`) y `scope` terminado en `/registries/<acr>`.
- **Por qué:** sin este rol, el pull falla (`ImagePullBackOff` / `unauthorized` / 403). Puede tardar 1-2 minutos en propagarse.
- **Idea clave:** identidad (quién soy) y rol (qué puedo hacer) son dos pasos separados. ServiceAccount + RoleBinding en K8s.

### 8. `az webapp config set … --acr-use-identity true --acr-identity '[system]'`
- **Qué hace:** le dice a App Service que use la identidad system-assigned para autenticarse en el registry. Pone `acrUseManagedIdentityCreds: true`.
- **Trampa:** las comillas simples en `'[system]'` evitan que bash interprete los corchetes.
- **Qué esperar:** el JSON de configuración del sitio; `linuxFxVersion` sigue vacío hasta el siguiente comando.

### 9. `az webapp config container set … --container-image-name … --container-registry-url https://$ACR_NAME.azurecr.io`
- **Qué hace:** guarda la imagen y la URL del registry en la configuración; `linuxFxVersion` pasa a `DOCKER|<acr>.azurecr.io/docprocessor:v1`.
- **Qué esperar:** el aviso `Retrieving credentials failed … run 'az acr update --admin-enabled true'`. **Es esperable y no se arregla habilitando el admin**: el CLI intenta primero buscar usuario/contraseña, no los encuentra y sigue con la identidad. Después imprime los app settings: `DOCKER_REGISTRY_SERVER_URL`, `DOCKER_CUSTOM_IMAGE_NAME` y `WEBSITES_ENABLE_APP_SERVICE_STORAGE=false`.
- **Detalle:** no aparece ningún `DOCKER_REGISTRY_SERVER_USERNAME/PASSWORD`; confirma que no hay credenciales guardadas.

### 10. `az webapp config appsettings set … --settings WEBSITES_PORT=80`
```
--settings  WEBSITES_PORT=80
                │            └ valor
                └ app setting: se inyecta como variable de entorno al arrancar el contenedor
```
- **Por qué:** App Service solo asume 80 u 8080; si el contenedor escucha en otro puerto, hay errores de conexión (knowledge check 2.1). Aquí gunicorn ya escucha en 80, así que es declarativo.
- **Trampa:** la respuesta muestra `"value": null` en todos los settings: **la CLI oculta los valores**. Se comprueba con `appsettings list`.

### 11. `… --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true`
- **Qué hace:** monta `/home` como almacenamiento persistente compartido entre instancias.
- **Por qué:** sin él, `/home/processed` es efímero y los JSON se pierden al reiniciar.
- **Detalle:** la ruta es fija (`/home`); para elegirla existe el montaje de Azure Storage propio (`az webapp config storage-account add --mount-path …`, no se puede usar `/` ni `/home`, Blob es solo lectura). El montaje oculta lo que la imagen tuviera en `/home`: por eso `main.py` recrea la carpeta al arrancar.

### 12. `az webapp config set … --always-on true`
- **Qué hace:** evita que la app se descargue tras ~20 minutos de inactividad.
- **Requisito:** plan Basic o superior (`B1` vale). En el log aparece como peticiones `GET /` con user-agent `AlwaysOn`.

### 13. `az webapp log config … --docker-container-logging filesystem`
- **Qué hace:** activa la captura de stdout/stderr del contenedor en el sistema de ficheros (retención de 3 días, 100 MB).
- **Por qué:** el logging de contenedor hay que activarlo explícitamente.
- **Trampa:** la salida muestra `applicationLogs.fileSystem.level: Off` y `az webapp log show` devuelve `dockerContainerLogging: null`; no refleja el ajuste, pero los logs existen (se comprueba con `log download`).

### 14. `APP_URL=$(az webapp show … --query defaultHostName --output tsv)` y `echo "Application URL: https://$APP_URL"`
- Guarda el hostname público (`app-…azurewebsites.net`). La plataforma termina TLS: se accede por HTTPS y el contenedor recibe HTTP. Faltar el `echo` de la segunda línea es un fallo habitual: la variable queda guardada pero no se ve.

### 15. `curl -X POST "https://$APP_URL/process" -H "Content-Type: text/plain" --data-binary @document.txt`
```
-X POST                       método
-H "Content-Type: text/plain" cabecera: el cuerpo es texto
--data-binary @document.txt   cuerpo = contenido exacto del fichero (-d podría alterar saltos de línea)
```
- **Qué esperar:** JSON con `statistics` **reales** (166 caracteres, 22 palabras), `analysis` **simulado** (siempre las mismas entidades) y `"storage": {"saved": true, "path": "/home/processed/<uuid>.json"}`.
- **PowerShell:** `Invoke-RestMethod -Method Post -Uri … -ContentType "text/plain" -Body $body`.

### 16. `curl https://$APP_URL/documents`
- **Qué hace:** lista los JSON guardados. `count: 1` con el mismo `document_id`; `size_bytes: 1003` es el tamaño del fichero (resultado completo con `indent=2`), no el del texto.
- **Qué prueba:** que `/home/processed` es escribible y legible. Para probar la **persistencia** hay que reiniciar la app (`az webapp restart`) y repetir este `GET` (experimento no realizado).

### 17. `az webapp log tail …` y `az webapp log download … --log-file logs.zip`
- `log tail`: stream en vivo; solo muestra líneas **nuevas** mientras está abierto. En este entorno no se confirmó (probable corte por el proxy, o falta de tráfico durante el `tail`). Se prueba con dos terminales: `tail` en una y `curl` en otra. Salir con Ctrl+C.
- `log download`: zip con `LogFiles/*_default_docker.log`, que contiene el arranque de gunicorn (`Listening at: http://0.0.0.0:80`, dos workers), las líneas `main - INFO` de la app (`Document processing request received`, `Result saved to …`) y el access log (`"POST /process" 200`). La IP `169.254.130.1` es la del front-end interno de App Service, no la del cliente. Los `HealthCheck/1.0` y `AlwaysOn` son tráfico de la plataforma.

### 18. Lecturas para comprobar el estado
```bash
az appservice plan list -g $RESOURCE_GROUP -o table                                 # ProvisioningState/Status reales
az webapp config appsettings list -g $RESOURCE_GROUP -n $APP_NAME -o table          # valores reales (set los oculta)
az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query '{state:state,alwaysOn:siteConfig.alwaysOn}'
az acr task list-runs --registry $ACR_NAME -o table                                 # run cx1: build de docprocessor:v1
```
- **Idea clave:** `set` no confirma el valor y `plan show` devuelve `provisioningState: null`; contrastar siempre con `list` / `show` antes de dar algo por hecho.
- **Detalle:** el prefijo de las runs depende de la región del registry (`ca` en East US, `cx` en Canada Central).

### 19. Kudu: `echo "Kudu URL: https://$APP_NAME.scm.azurewebsites.net"`
- **Qué es:** cada web app tiene dos hostnames: `<app>.azurewebsites.net` (la aplicación) y `<app>.scm.azurewebsites.net` (sitio de gestión). SCM = Source Control Manager; Kudu = el motor; el portal lo llama *Advanced Tools*.
- **Qué se mira:** *Environment* (variables de entorno: `WEBSITES_PORT`, `WEBSITES_ENABLE_APP_SERVICE_STORAGE`), *SSH → Kudu* (consola; `ls /home/processed`) y *File Manager* (`/home/LogFiles/`).
- **Seguridad:** lo protege Entra ID. Entras con tu usuario (plano de gestión); el rol `AcrPull` es de la identidad de la app (carga de trabajo): no son lo mismo.
- **Analogía K8s:** `kubectl exec` + `logs` + `describe` en el navegador. En esta sesión no se llegó a confirmar lo visto en Kudu.

### 20. `az group delete --name rg-ai200-appsvc --no-wait --yes` y `az group exists --name rg-ai200-appsvc`
- Mismo desglose que en el lab 1. Borra ACR, plan, web app y la asignación de rol. Lo ejecuta el alumno. La plataforma de labs también desprovisiona los recursos al finalizar el laboratorio, y la sesión de `az` caduca con la instancia (`AADSTS130507`).

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

## Cleanup y troubleshooting (de la guía de la plataforma)

**Cleanup.** Borra el resource group y todo lo que contiene (ACR, plan, web app, asignación de rol). Se ejecuta en segundo plano:

```bash
az group delete --name rg-ai200-appsvc --no-wait --yes
az group exists --name rg-ai200-appsvc     # false cuando termina
```

Aviso de la guía: si se hubiera usado un resource group preexistente, también se borrarían sus recursos ajenos al lab. Al finalizar el laboratorio en la plataforma, ésta desprovisiona los recursos igualmente.

**Troubleshooting**
| Síntoma | Qué comprobar |
|---|---|
| Variables vacías o sesión equivocada | `az account show`; recargar `source .env` (bash) o `. .\.env.ps1` (PowerShell) |
| El ACR no responde | `az acr list -o table`; en el portal, *Provisioning State* = `Succeeded` |
| Falla el build (el script oculta la salida de `az acr build`) | `az acr task list-runs --registry $ACR_NAME -o table` y `az acr task logs --registry $ACR_NAME --run-id <id>`; ejecutar el script desde la raíz del proyecto (donde está `api/`) |
| `ImagePullBackOff` / `unauthorized` / `403` | `az webapp identity show` (identidad system-assigned activa); asignación `AcrPull` sobre el ACR (puede tardar 1-2 min en propagarse); repetir `az webapp config container set` por si la imagen o la URL del registry son incorrectas |
| 502/503 poco después de desplegar | Esperar un minuto: el primer arranque descarga la imagen. Activar el logging de contenedor y `az webapp log tail` |
| La persistencia no funciona | `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` en los app settings; llamar a `/documents` tras enviar un documento |

