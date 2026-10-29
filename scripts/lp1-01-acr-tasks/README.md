# azdeploy.py · lab LP1-01 (ACR Tasks)

Crea la base del lab: un resource group y un Azure Container Registry. La imagen la construye después el alumno con `az acr build`.

## Qué hace
1. Comprueba `api/Dockerfile` y fija el directorio de trabajo en la carpeta del script.
2. Exige sesión de `az` (consulta `az ad signed-in-user show`).
3. Deriva el nombre del ACR: `acr` + 8 primeros caracteres del SHA-1 del *object id* del usuario.
4. `az group create` (si no existe) y `az acr create --sku Basic`.
5. Escribe `.env` y `.env.ps1` con `RESOURCE_GROUP`, `ACR_NAME` y `LOCATION`.

No tiene menú: se ejecuta de principio a fin.

## Antes de ejecutar
Edita al principio del fichero:
```python
rg = "rg-ai200-acr"   # nombre del resource group
location = "eastus"   # región (la exige el lab; si falla por cuota, cambiar)
```

## Uso
```bash
az login                      # o az login --use-device-code
cd labs/lp1-01-acr-tasks      # o copia api/ junto al script
python3 azdeploy.py
source .env
az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api
```
Salida esperada: `Resource group created`, `ACR created` y `Deployment Complete!` con las tres variables.

## Problemas típicos
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Not authenticated with Azure` | Sin sesión | `az login` |
| `api/Dockerfile is missing` | `api/` no está junto al script | Ejecutar desde `labs/lp1-01-acr-tasks/` |
| `SSLCertVerificationError` | Proxy que re-firma TLS | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` |
| Error al crear el ACR | Proveedor sin registrar | `az provider register --namespace Microsoft.ContainerRegistry` |

## Limpieza
```bash
az group delete --name rg-ai200-acr --no-wait --yes
```
Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html · Comandos al detalle: [`labs/lp1-01-acr-tasks/README.md`](../../labs/lp1-01-acr-tasks/README.md)
