# azdeploy.py · lab LP2-03 (Scale containers in Azure Container Apps)

Aprovisiona la base para practicar el autoescalado: ACR con la imagen `agent-api:v1`, environment y la container app `agent-api`, que arranca con **una sola réplica y sin escalado**. La regla de escalado y el generador de carga son pasos posteriores del lab.

## Menú
| Opción | Acción |
|---|---|
| 1 | Resource group + ACR + `az acr build` de `api/` (`agent-api:v1`) |
| 2 | Container Apps environment (`az containerapp env create`, con su Log Analytics) |
| 3 | Crea la container app `agent-api` (identidad gestionada + `AcrPull`); genera `.env` y `.env.ps1` |
| 4 | Estado: ACR, imagen, environment, app, identidad y réplicas en ejecución |
| 5 | Salir |

Orden: 1 → 2 → 3. Nombres derivados del *object id* del usuario: `acr<hash>`, `aca-env-<hash>`. Funciones comunes explicadas en [`../README.md`](../README.md#funciones-comunes-de-todos-los-scripts-qué-hacen-y-por-qué).

## Antes de ejecutar
```python
rg = "rg-ai200-aca-scale"
location = "eastus"
```
Es lo único que se edita (no hay cambios de modelo en este zip). Original sin editar: `labs/lp2-03-aca-scale/aca-scale-python.zip`.

## Qué hace el script, comando a comando
- **Opciones 1 y 2:** idénticas a las del [lab LP2-01](../lp2-01-aca-deploy/README.md#qué-hace-el-script-comando-a-comando): `az group create`, `az acr create … --sku Basic --admin-enabled false`, `az acr build … --image agent-api:v1 --file api/Dockerfile --no-logs api/` y `az containerapp env create`.
- **Opción 3 · `az containerapp create`:**
  ```
  az containerapp create
    --name agent-api --resource-group <rg> --environment <env>
    --image <acr>.azurecr.io/agent-api:v1
    --registry-server <acr>.azurecr.io --registry-identity system --system-assigned
    --ingress external --target-port 8080
    --min-replicas 1 --max-replicas 1
    --env-vars AGENT_DEFAULT_DELAY_MS=500
  ```
  - `--registry-identity system` + `--system-assigned`: la app obtiene una identidad gestionada y la CLI le concede `AcrPull` sobre el ACR; así descarga la imagen sin credenciales.
  - `--target-port 8080`: puerto en que escucha esta API (las de los otros labs usan 8000).
  - `--min-replicas 1 --max-replicas 1`: **fija una sola réplica**, a propósito: el lab añade después la regla de escalado.
  - `AGENT_DEFAULT_DELAY_MS=500`: cada petición tarda 500 ms, para que se acumulen peticiones concurrentes bajo carga.
  Después comprueba con `az containerapp identity show` que la identidad existe y escribe el `.env`.
- **Opción 4 · estado (solo lectura):** `az containerapp env show`, `az acr show`, `az acr repository show`, `az containerapp show`, `az containerapp identity show` y `az containerapp replica list` (para «Running replicas»). Esperado: `Succeeded` en todo y `Running replicas: 1`.

## Problemas típicos
| Síntoma | Causa | Arreglo |
|---|---|---|
| El script se corta al lanzar el ACR | Conexión larga interrumpida (proxy) | El build suele haber terminado: `az acr task list-runs --registry <acr>`; seguir con la 2 |
| Opción 2 o 3 colgada con el recurso ya creado | La llamada a Azure no respondió | `Ctrl+C`, comprobar `provisioningState`, relanzar y elegir la opción siguiente |
| `ManagedEnvironmentNotProvisioned` | Environment aún en `Waiting` | Esperar a `Succeeded` |
| La app queda con imagen `quickstart` y sin registry | `create` interrumpido a medias | `az containerapp show … --query "{image:…, registries:…}"` y `az containerapp registry set` + `az containerapp update --image …` |

## Limpieza (obligatoria)
```bash
az group delete --name rg-ai200-aca-scale --no-wait --yes
az group exists --name rg-ai200-aca-scale        # hasta false
```
Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/03-aca-scale-containers.html · Comandos al detalle del lab: [`labs/lp2-03-aca-scale/README.md`](../../labs/lp2-03-aca-scale/README.md)
