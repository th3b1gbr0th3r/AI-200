# azdeploy.py · lab LP1-02 (App Service con contenedor)

Aprovisiona la infraestructura del lab con un menú interactivo. La web app, la identidad gestionada y el rol `AcrPull` los crea el alumno a mano después.

## Menú
| Opción | Acción |
|---|---|
| 1 | Resource group + ACR (admin desactivado) + `az acr build` de `api/` (imagen y tag fijados en el script) |
| 2 | Resource group + App Service Plan Linux; **genera `.env` y `.env.ps1`** |
| 3 | Estado: ACR, imagen, plan (SKU), web app e identidad |
| 4 | Salir |

Nombres derivados del *object id* del usuario (SHA-1, 8 caracteres): `acrXXXXXXXX`, `plan-docprocessor-XXXXXXXX`, `app-docprocessor-XXXXXXXX`. El script es idempotente: no recrea lo existente.

## Antes de ejecutar
Edita al principio del fichero:
```python
rg = "rg-ai200-appsvc"
location = "canadacentral"   # región; cambiar si hay cuota 0
```
Y en la creación del plan, la línea `"--sku", "B1"` (el original trae `P0v3`; B1 es lo que indicaba la plataforma). El mensaje `SKU: P0v3` que imprime después es texto fijo y no refleja el SKU real: comprobarlo con la opción 3.

## Uso
```bash
az login
cd labs/lp1-02-app-service    # o copia api/ junto al script
python3 azdeploy.py           # opción 1, luego 2, luego 4
source .env                   # carga RESOURCE_GROUP, ACR_NAME, APP_PLAN, APP_NAME, LOCATION
```
Sin `source .env` los comandos siguientes de la guía fallan por variables vacías.

## Problemas típicos
| Síntoma | Causa | Arreglo |
|---|---|---|
| La opción 2 falla | SKU mal editado o sin cuota en la región | Revisar la línea del SKU; cambiar de región |
| `Not authenticated with Azure` | Sin sesión | `az login` |
| `api/Dockerfile is missing` | `api/` no está junto al script | Ejecutar desde `labs/lp1-02-app-service/` |
| Proveedor sin registrar | Primera vez en la suscripción | `az provider register --namespace Microsoft.ContainerRegistry` y `Microsoft.Web` |

## Limpieza
```bash
az group delete --name rg-ai200-appsvc --no-wait --yes
```
Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html · Comandos al detalle: [`labs/lp1-02-app-service/README.md`](../../labs/lp1-02-app-service/README.md)
