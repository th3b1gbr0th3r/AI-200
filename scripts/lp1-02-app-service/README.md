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

## Qué hace el script, comando a comando
Funciones comunes explicadas en [`../README.md`](../README.md#funciones-comunes-de-todos-los-scripts-qué-hacen-y-por-qué). Aquí, lo propio de cada opción del menú:

### Opción 1 · `create_acr_and_build_image()`
1. `create_resource_group()` → `az group exists` / `az group create` (grupo `rg-ai200-appsvc`, región `canadacentral`).
2. `az acr show … --query name -o tsv` → ¿existe ya el ACR?
3. Si no: `az acr create --resource-group … --name acr<hash> --sku Basic --admin-enabled false` → registro Basic **sin usuario administrador**: solo se podrá acceder con identidad y rol.
4. `az acr build --resource-group … --registry acr<hash> --image docprocessor:v1 --file api/Dockerfile --no-logs api/` → construye en la nube la imagen de la API (Flask con gunicorn en el puerto 80) y la publica como `docprocessor:v1`.

### Opción 2 · `create_app_service_plan()`
1. `create_resource_group()` (idempotente).
2. `az appservice plan show … --name plan-docprocessor-<hash> --query name -o tsv` → ¿existe el plan?
3. Si no: `az appservice plan create --resource-group … --name plan-docprocessor-<hash> --location canadacentral --sku B1 --is-linux`
   ```
   az appservice plan create → crea el App Service Plan (la capacidad de cómputo; se paga el plan, no la app)
   --sku B1                  → nivel Basic (en el original, P0v3). B1 no admite slots ni autoescalado por reglas
   --is-linux                → plan Linux, necesario para contenedores Linux
   ```
   El texto «SKU: P0v3» que imprime después es fijo y no refleja el SKU real.
4. `write_env_files()` con `RESOURCE_GROUP`, `ACR_NAME`, `APP_PLAN`, `APP_NAME` (`app-docprocessor-<hash>`, que **todavía no existe**: la crea el alumno) y `LOCATION`.

### Opción 3 · `check_deployment_status()` (solo lectura)
| Comprobación | Comando |
|---|---|
| Estado del ACR | `az acr show … --query provisioningState -o tsv` |
| ¿Está la imagen? | `az acr repository show --name … --image docprocessor:v1 --query name -o tsv` |
| Estado y SKU del plan | `az appservice plan show … --query provisioningState` y `--query sku.name` |
| Estado de la web app | `az webapp show … --query state -o tsv` |
| ¿Tiene identidad gestionada? | `az webapp identity show … --query principalId -o tsv` |
Si la web app aún no existe sale `Not created (student task)`: es normal, la crea el alumno en el paso 5 del lab.

### Opción 4 · salir
Limpia la pantalla y sale con código 0.

Los pasos manuales posteriores (`az webapp create`, identidad gestionada, `AcrPull`, `appsettings`…) están desglosados en [`labs/lp1-02-app-service/README.md`](../../labs/lp1-02-app-service/README.md).
