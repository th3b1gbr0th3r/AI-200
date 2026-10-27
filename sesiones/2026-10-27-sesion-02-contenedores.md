# Sesión 2 — 27/10/2026 · LP1 Alojamiento en contenedores (ACR + App Service)

## Qué se hizo
- Añadido el material del día: presentación del LP1, knowledge check y enlace de recursos (los PDF/zip no se suben; `*.pdf` está en `.gitignore`).
- Nota del módulo con respuestas del knowledge check: `docs/modulos/01-alojamiento-contenedores.md`.
- Instalado **Azure CLI 2.91.0** en Linux Mint 22.3 (el script oficial deja el repo y no instala el paquete; hubo que hacer `apt-get install azure-cli`).
- Login en la suscripción temporal del lab y **lab 1 completo** (ACR Tasks): `labs/lp1-01-acr-tasks/README.md` con comandos, salidas y explicación.
- Guía para compañeros (instalar `az`, login con TAP, error de certificado): `notas/2026-10-27-guia-az-login-lab.md`.
- **Lab 2 (App Service con contenedor)** en una instancia nueva del lab (la anterior caducó tras ~120 min; región `canadacentral`, plan `B1`, como indicaba la guía de la plataforma): `labs/lp1-02-app-service/README.md`. Web app con identidad gestionada + `AcrPull`, almacenamiento persistente, Always On y logs; pruebas `POST /process` y `GET /documents` correctas.
- Verificado en Microsoft Learn el montaje de Azure Storage propio en App Service (ruta elegible, salvo `/` y `/home`).
- Merge de la PR nº 2 (lab 1) a `main` a petición del usuario.
- Incorporada la transcripción de la clase (Zoom): notas organizativas y técnicas en `docs/modulos/01-alojamiento-contenedores.md` (sin nombres de personas; la transcripción no se publica).

## Decisiones
- Los labs se reproducen en local (Linux) en paralelo a la plataforma (servidor virtual Windows con PowerShell); mismo usuario → mismo nombre de ACR y misma suscripción, así que hay que evitar pisar recursos.
- El usuario ejecuta los comandos y se explican las salidas. Incluye el cleanup: Claude borró el resource group del lab 1 por su cuenta y el usuario lo corrigió; queda en memoria que los comandos que crean/borran recursos los lanza el usuario.
- Región `eastus` por exigencia del lab; rg `rg-ai200-acr`.
- Las credenciales temporales del lab se pasaron por el chat con autorización expresa del usuario (caducan en 120 min); no se escriben en el repo.

## Aprendizajes
- **Registry ≠ cómputo:** el registry almacena; ACR Tasks ejecuta builds/runs en agentes efímeros (mini CI gestionado).
- **El digest cambia entre builds del mismo código:** los builds no son reproducibles; fijar por digest.
- **Un TAP no es una contraseña:** solo funciona en login interactivo.
- **Proxy corporativo:** `REQUESTS_CA_BUNDLE` apuntando al almacén del sistema.
- **Bloqueo de imagen:** `writeEnabled=false` no impide borrar (`deleteEnabled`).
- Analogía CI/CD: Azure DevOps o GitHub Actions orquestan; ACR guarda; AKS ejecuta.
- **Plan vs web app:** el plan es la capacidad (node pool), la app se coloca en él; se paga el plan. B1 no admite slots.
- **Identidad gestionada + RBAC:** identidad (quién soy) y rol (qué puedo hacer) son pasos separados; `AcrPull` limitado al ACR. Las app registrations (on-prem) llevan secreto o certificado; las SPA no tienen secreto (PKCE).
- **`/home` persistente tiene ruta fija**; para elegirla se monta Azure Storage (Files lectura/escritura, Blob solo lectura; no en `/` ni `/home`).
- **La CLI no siempre dice la verdad:** `appsettings set` oculta valores, `plan show` devuelve `provisioningState` nulo; contrastar con `list`.
- **Kudu = SCM = Advanced Tools**; el login de Kudu es plano de gestión (usuario), no la identidad de la app.

## Correcciones durante la sesión
- Predije que el segundo build sería mucho más rápido: no, el agente es efímero y no hay caché; solo se acelera el push.
- Dije que `lastUpdateTime` podía cambiar al bloquear: no cambia (refleja el contenido, no los atributos).
- El conteo de caracteres del mensaje para el chat estaba mal estimado; se midió con `wc -m`.

## Estado
- Lab 1 hecho y **recursos eliminados** (`rg-ai200-acr` borrado).
- Lab 2 hecho hasta el paso 12 verificado; pasos 13-14 sin confirmar (ver README del lab). **Recursos vivos:** `rg-ai200-appsvc` (ACR Basic + plan B1 + web app); cleanup a cargo del alumno.
- Pendiente: lab 3 (sidecar, por confirmar con el docente), preguntas de discusión en grupo.

## Resumen de comandos de la sesión (en orden, con explicación)

Valores de ejemplo: `acrdfbe0335` / `rg-ai200-acr` (lab 1) y `acr00a7662a` / `rg-ai200-appsvc` (lab 2). Los nombres cambian en cada instancia del lab. Detalle y salidas en `labs/lp1-01-acr-tasks/README.md` y `labs/lp1-02-app-service/README.md`.

### 1. Preparar la máquina
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash   # en Mint deja el repo pero no instala el paquete
sudo apt-get update && sudo apt-get install -y azure-cli # instalación efectiva
az version                                               # 2.91.0
```

### 2. Login en la cuenta temporal del lab
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # solo si un proxy re-firma TLS
az logout
az login --use-device-code     # navegador en incógnito, "Usar otra cuenta", usuario del lab y Temporary Access Pass
az account show -o table       # la suscripción debe ser la del lab
az group list -o table         # vacío en una instancia nueva
az provider show -n Microsoft.ContainerRegistry --query registrationState -o tsv   # Registered
```
- El TAP **no** es una contraseña: `az login -u -p` da `AADSTS50126`.
- La sesión caduca con la instancia (~2 h): `AADSTS130507` indica que hay que volver a entrar o que el lab expiró.

### 3. Lab 1 · ACR Tasks (`eastus`)
```bash
cd labs/lp1-01-acr-tasks
az provider register --namespace Microsoft.ContainerRegistry
python3 azdeploy.py            # crea rg-ai200-acr + ACR Basic y escribe .env  (rg y location editados antes)
source .env                    # RESOURCE_GROUP, ACR_NAME, LOCATION

az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api    # build + push en la nube (run ca1)
az acr repository list --name $ACR_NAME -o table                         # inference-api
az acr repository show-tags --name $ACR_NAME --repository inference-api -o table
az acr manifest list-metadata --registry $ACR_NAME --name inference-api -o table   # digest sha256:7525...
az acr run --registry $ACR_NAME \
  --cmd "$ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" /dev/null   # run ca2
az acr build --registry $ACR_NAME --image inference-api:v1.1.0 ./api    # segunda versión (ca3), digest distinto
az acr task list-runs --registry $ACR_NAME -o table                      # ca1, ca2, ca3
az acr repository update --name $ACR_NAME --image inference-api:v1.0.0 --write-enabled false   # bloqueo
az acr repository show --name $ACR_NAME --image inference-api:v1.0.0    # writeEnabled: false
az group delete --name rg-ai200-acr --no-wait --yes                      # cleanup
az group exists --name rg-ai200-acr                                      # false
```

### 4. Lab 2 · App Service con contenedor (`canadacentral`, plan `B1`)
```bash
cd labs/lp1-02-app-service
# azdeploy.py: rg="rg-ai200-appsvc", location="canadacentral", línea 224 "--sku","B1" (sustituye P0v3)
az provider register --namespace Microsoft.ContainerRegistry
az provider register --namespace Microsoft.Web
python3 azdeploy.py            # menú: 1 = ACR + imagen docprocessor:v1 ; 2 = App Service plan + .env ; 4 = salir
source .env                    # RESOURCE_GROUP, ACR_NAME, APP_PLAN, APP_NAME, LOCATION

# 6. Web app (aún sin identidad ni configuración de contenedor)
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_PLAN --name $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1

# 7. Identidad gestionada system-assigned
az webapp identity assign --resource-group $RESOURCE_GROUP --name $APP_NAME

# 8. Rol AcrPull de esa identidad, limitado al ACR
PRINCIPAL_ID=$(az webapp identity show --resource-group $RESOURCE_GROUP --name $APP_NAME --query principalId --output tsv)
ACR_ID=$(az acr show --resource-group $RESOURCE_GROUP --name $ACR_NAME --query id --output tsv)
az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull

# 9. La app usa la identidad para el pull (el aviso "Retrieving credentials failed" es esperable; no habilitar el admin)
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --acr-use-identity true --acr-identity '[system]'
az webapp config container set --resource-group $RESOURCE_GROUP --name $APP_NAME \
  --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1 --container-registry-url https://$ACR_NAME.azurecr.io

# 10. Runtime, persistencia, Always On y logs de contenedor
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings WEBSITES_PORT=80
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --always-on true
az webapp log config --resource-group $RESOURCE_GROUP --name $APP_NAME --docker-container-logging filesystem

# 11-12. URL y prueba funcional
APP_URL=$(az webapp show --resource-group $RESOURCE_GROUP --name $APP_NAME --query defaultHostName --output tsv)
echo "Application URL: https://$APP_URL"
curl -X POST "https://$APP_URL/process" -H "Content-Type: text/plain" --data-binary @document.txt   # "saved": true
curl https://$APP_URL/documents                                                                    # count: 1

# 13-15. Logs, Kudu y ajustes
az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME      # no se confirmó el stream en vivo
az webapp log download --resource-group $RESOURCE_GROUP --name $APP_NAME --log-file logs.zip   # alternativa que sí funcionó
echo "Kudu URL: https://$APP_NAME.scm.azurewebsites.net"
az webapp config appsettings list --resource-group $RESOURCE_GROUP --name $APP_NAME -o table   # valores reales (set los oculta)

# 16. Cleanup
az group delete --name rg-ai200-appsvc --no-wait --yes
az group exists --name rg-ai200-appsvc
```

### 5. Comprobaciones de lectura útiles
```bash
az appservice plan list -g $RESOURCE_GROUP -o table        # ProvisioningState/Status reales (plan show devuelve null)
az webapp show -g $RESOURCE_GROUP -n $APP_NAME --query '{state:state,alwaysOn:siteConfig.alwaysOn}'
az acr task list-runs --registry $ACR_NAME -o table
```

### 6. Git del día
```bash
git switch -c dia-02-2026-10-27
git add <ficheros concretos>                         # nunca zips, azdeploy.py/api ni .env
git commit -m "..."                                  # con Co-Authored-By
git -c http.extraHeader="Authorization: Basic ..." push -u origin dia-02-2026-10-27   # cabecera temporal, sin guardar el token
gh pr create --base main --head dia-02-2026-10-27    # con GH_TOKEN inline
```
PR nº 2 (lab 1) mergeada; PR nº 3 (lab 2 y cierre) pendiente de merge.

### Traducción PowerShell (plataforma) → bash (aquí)
| PowerShell | bash |
|---|---|
| `` ` `` fin de línea | `\` |
| `$env:ACR_NAME` | `$ACR_NAME` |
| `. .\.env.ps1` | `source .env` |
| `Write-Host "..."` | `echo "..."` |
| `Invoke-RestMethod -Method Post ...` | `curl -X POST ...` |

## Pendientes
- Cleanup del lab 2: según el docente, la plataforma desprovisiona los recursos al finalizar el laboratorio; además, `az group delete --name rg-ai200-appsvc --no-wait --yes` lo ejecuta el alumno. Finalizar el lab en la plataforma.
- Confirmar qué se ve en Kudu (Environment, consola, `/home/LogFiles/`) y repetir la prueba de `log tail` con dos terminales.
- Experimento opcional: reiniciar la app y comprobar que el documento sobrevive en `/home`.
- Lab 3 (sidecar con modelo local), por confirmar con el docente; preguntas de discusión en grupo del LP1.
- Siguiente clase: corrección de las 4 preguntas del knowledge check del LP1 y LP2 Azure Container Apps (diapositivas aún no disponibles); AKS es el LP3.
- Los labs usan una suscripción compartida con cuotas por región: si el plan falla, cambiar de región.
