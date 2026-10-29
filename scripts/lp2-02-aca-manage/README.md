# azdeploy.py · lab LP2-02 (Manage containers in Azure Container Apps)

Aprovisiona todo lo necesario para practicar el día 2 de ACA: ACR con la imagen, environment y **la container app ya desplegada con su secreto**. Después el alumno introduce fallos a propósito (variable que falta, puerto de ingress erróneo) y los diagnostica con revisiones, `logs show` y Log Analytics.

## Menú
| Opción | Acción |
|---|---|
| 1 | Resource group + ACR + `az acr build` de `api/` (`ai-api:v1`) |
| 2 | Container Apps environment (`az containerapp env create`, con su Log Analytics) |
| 3 | **Despliega la container app y configura el secreto**; genera `.env` y `.env.ps1` |
| 4 | Estado: ACR, imagen, environment y container app |
| 5 | Salir |

Orden obligatorio: 1 → 2 → 3 (la 3 comprueba que existen ACR, imagen y environment y, si no, dice qué opción falta).

## Antes de ejecutar
```python
rg = "rg-ai200-aca-manage"
location = "eastus"
```
Cambios que pide la plataforma: `MODEL_NAME = "gpt-5.1"` (el original trae `gpt-5.4-mini`), `TPM_LIMIT = "5000"` tras `MODEL_NAME` y `"TPM_LIMIT": TPM_LIMIT,` en `write_env_files()`. Original sin editar: `labs/lp2-02-aca-manage/aca-manage-python.zip`.

## Uso
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # solo si hay proxy que re-firma TLS
az login --use-device-code
cd labs/lp2-02-aca-manage      # o copia api/ junto al script
python3 azdeploy.py            # 1, 2, 3 y 5
source .env
az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv   # Succeeded antes de la opción 3
```

## Qué hace el script, comando a comando
Funciones comunes explicadas en [`../README.md`](../README.md#funciones-comunes-de-todos-los-scripts-qué-hacen-y-por-qué). Las opciones 1 y 2 son idénticas a las del [lab LP2-01](../lp2-01-aca-deploy/README.md#qué-hace-el-script-comando-a-comando). Lo nuevo es la opción 3.

### Opción 3 · `deploy_container_app_and_configure_secrets()`
Primero **comprueba requisitos** con sondas de solo lectura:
| Comprobación | Comando | Si falta |
|---|---|---|
| ACR | `az acr show … --query name -o tsv` | «Run option 1 first» |
| Environment | `az containerapp env show … --query name -o tsv` | «Run option 2 first» |
| Imagen | `az acr repository show --name … --image ai-api:v1 --query name -o tsv` | «Run option 1 first» |
| App ya creada | `az containerapp show --name ai-api … --query name -o tsv` | la crea (paso siguiente) |

Después, tres comandos que crean cosas:

**1. `az containerapp create`** (solo si la app no existe)
```
az containerapp create
  --name ai-api --resource-group <rg> --environment <env>   → la app y dónde vive
  --image <acr>.azurecr.io/ai-api:v1                        → la imagen publicada en la opción 1
  --ingress external --target-port 8000                     → endpoint público con TLS; el contenedor escucha en el 8000
  --env-vars MODEL_NAME=gpt-5.1                             → variable no sensible
  --registry-server <acr>.azurecr.io --registry-identity system
```
`--registry-identity system` es **el momento en que la app obtiene permiso para descargar la imagen**: crea una identidad gestionada system-assigned para la app y la CLI le concede el rol `AcrPull` sobre ese ACR. Sin credenciales. Puede tardar 1-2 minutos en propagarse el rol.

**2. `az containerapp secret set --name ai-api … --secrets embeddings-api-key=<valor>`** → guarda el secreto en la app (el valor es una clave de demostración del lab). Por sí solo no reinicia nada.

**3. `az containerapp update --name ai-api … --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key`** → la variable apunta al secreto (`secretref:`) en vez de llevar el valor en claro. Es un cambio de plantilla: crea la **revisión 2** y la reinicia.

Por último `write_env_files()` con `RESOURCE_GROUP`, `ACR_NAME`, `ACR_SERVER`, `ACA_ENVIRONMENT`, `CONTAINER_APP_NAME`, `CONTAINER_IMAGE`, `TARGET_PORT`, `MODEL_NAME`, `TPM_LIMIT`, `EMBEDDINGS_API_KEY` y `LOCATION`.

### Opción 4 · `check_deployment_status()` (solo lectura)
`az acr show … --query provisioningState` (+ `az acr repository show` de la imagen), `az containerapp env show … --query properties.provisioningState` y `az containerapp show … --query properties.provisioningState`. Esperado: `Succeeded` en los tres y `Container App is deployed`.

## Problemas típicos
| Síntoma | Causa | Arreglo |
|---|---|---|
| La opción 2 da error de conexión | Error transitorio; el environment sigue creándose | Esperar a `provisioningState = Succeeded` |
| `ManagedEnvironmentNotProvisioned` | Environment aún en `Waiting` | Esperar y repetir la opción 3 |
| La opción 3 da error de conexión/timeout | La app puede haber quedado a medias (imagen placeholder, sin registry) | `az containerapp show -n ai-api -g <rg> --query "{image:properties.template.containers[0].image, registries:properties.configuration.registries}"`; si `image` no es tu ACR o `registries` es `null`: `az containerapp registry set` + `az containerapp update --image …`, o borrar la app y repetir la 3 |
| `ImagePullBackOff` / 403 | `AcrPull` aún sin propagar | Esperar 1-2 min; `az containerapp identity show` |

## Limpieza (obligatoria)
```bash
az group delete --name rg-ai200-aca-manage --no-wait --yes
az group exists --name rg-ai200-aca-manage        # hasta false
```
Solo se borra el grupo que creó el lab. Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/02-aca-manage-containers.html
