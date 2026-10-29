# azdeploy.py · lab LP2-01 (Deploy a containerized backend API to Azure Container Apps)

Aprovisiona la base del lab con un menú: resource group, ACR con la imagen `ai-api:v1` y el Container Apps environment. La container app, el secreto y las revisiones los crea el alumno a mano (ver el README del lab).

## Menú
| Opción | Acción |
|---|---|
| 1 | Resource group + ACR + `az acr build` de `api/` (imagen `ai-api:v1`, ACR Tasks) |
| 2 | Log Analytics workspace + Container Apps environment; **genera `.env` y `.env.ps1`** |
| 3 | Estado: ACR, imagen y environment |
| 4 | Salir |

Nombres derivados del *object id* del usuario (SHA-1, 8 caracteres): `acr<hash>` y `aca-env-<hash>`. Idempotente.

## Antes de ejecutar
Edita al principio del fichero:
```python
rg = "rg-ai200-aca"
location = "eastus"
```
Cambios que pide la plataforma del curso (no están en la guía pública): `MODEL_NAME = "gpt-5.1"` (en vez de `gpt-5.4-mini`), una línea `TPM_LIMIT = "5000"` tras `MODEL_NAME`, y `"TPM_LIMIT": TPM_LIMIT,` en el diccionario de `write_env_files()`. Versión original sin editar: `labs/lp2-01-aca-deploy/aca-deploy-python.zip`.

## Uso
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # solo si hay proxy que re-firma TLS
az login --use-device-code
az extension add --name containerapp && az extension add --name log-analytics
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.ContainerRegistry
cd labs/lp2-01-aca-deploy      # o copia api/ junto al script
python3 azdeploy.py            # opciones 1, 2 y 4
source .env
az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP --query properties.provisioningState -o tsv   # esperar Succeeded
```
Variables que carga `.env`: `RESOURCE_GROUP`, `ACR_NAME`, `ACR_SERVER`, `ACA_ENVIRONMENT`, `CONTAINER_APP_NAME`, `CONTAINER_IMAGE`, `TARGET_PORT`, `MODEL_NAME`, `TPM_LIMIT`, `EMBEDDINGS_API_KEY` (clave de demostración del lab), `LOCATION`.

## Problemas típicos
| Síntoma | Causa | Arreglo |
|---|---|---|
| Opción 2 da error de conexión | Error transitorio; el environment sigue creándose | Esperar y comprobar `provisioningState` = `Succeeded` antes de seguir |
| `ManagedEnvironmentNotProvisioned` en `az containerapp create` | Environment aún en `Waiting` | Esperar a `Succeeded` |
| `Could not find a suitable TLS CA certificate bundle` | Proxy corporativo | `export REQUESTS_CA_BUNDLE=…` (arriba) |
| `az containerapp` no existe | Falta la extensión | `az extension add --name containerapp` |

## Limpieza
```bash
az group delete --name rg-ai200-aca --no-wait --yes
```
Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/01-aca-deploy-containers.html · Comandos al detalle: [`labs/lp2-01-aca-deploy/README.md`](../../labs/lp2-01-aca-deploy/README.md)
