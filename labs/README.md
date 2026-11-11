# Labs · scripts de aprovisionamiento reutilizables

> **Repositorio de formación:** estos labs se ejecutaron en cuentas y suscripciones temporales de la plataforma del curso, ya destruidas. Los `.env`, nombres de recursos y endpoints versionados aquí son de esos entornos desechables y no contienen claves.

Cada lab trae los ficheros de partida de Microsoft (`azdeploy.py`, `api/`, `document.txt` y, si se conserva, el zip original) **versionados aquí** para poder reutilizarlos en el trabajo. Procedencia y licencia (MIT): [`NOTICE.md`](NOTICE.md). Cada carpeta tiene su `README.md`, que se sigue de principio a fin: en cada paso, por qué se hace, el comando, la salida real y la comprobación.

| Lab | Qué aprovisiona `azdeploy.py` | Qué hay en `api/` | Guía oficial |
|---|---|---|---|
| [`lp1-01-acr-tasks`](lp1-01-acr-tasks/README.md) | Resource group + ACR **Basic** | API Flask (`app.py`, puerto 5000, `Dockerfile` con `python:3.11-slim`) | [01-acr-tasks](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html) |
| [`lp1-02-app-service`](lp1-02-app-service/README.md) | Resource group + ACR (admin desactivado) + build de imagen + App Service Plan Linux | API Flask con gunicorn (`main.py`, puerto 80; `/`, `/health`, `/process`, `/documents`) | [02-app-svc-container](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html) |
| [`lp2-01-aca-deploy`](lp2-01-aca-deploy/README.md) | Resource group + ACR + imagen + Container Apps environment (Log Analytics) | API Flask con gunicorn (puerto 8000; `/health`, `/`, `/process`, `/documents`) | [01-aca-deploy-containers](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/01-aca-deploy-containers.html) |
| [`lp2-02-aca-manage`](lp2-02-aca-manage/README.md) | Igual que lp2-01 y además la container app con su secreto (opción 3) | API Flask simulada (puerto 8000) | [02-aca-manage-containers](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/02-aca-manage-containers.html) |
| [`lp2-03-aca-scale`](lp2-03-aca-scale/README.md) | Igual que lp2-01 y además `agent-api` con 1 réplica fija | API simulada con `/agent/process` (puerto 8080) + `client/` dashboard de carga | [03-aca-scale-containers](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/03-aca-scale-containers.html) |
| [`lp3-01-aks-deploy`](lp3-01-aks-deploy/README.md) | ACR + AKS dentro del grupo de la plataforma (el proyecto y el modelo `gpt-5.1` de Foundry se crean a mano en el portal); `configurar.sh` rellena los valores | API FastAPI (`/healthz`, `/readyz`, `/v1/inference`) + `client/` + manifiestos `k8s/` | [01-aks-deploy-container](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/01-aks-deploy-container.html) |
| [`lp3-02-aks-configure`](lp3-02-aks-configure/README.md) | ACR + imagen + AKS en un grupo propio (menú sin la opción 4) | API FastAPI + `client/` + `k8s/` (ConfigMap, Secret, PVC, Deployment, Service) | [02-aks-configure-container](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/02-aks-configure-container.html) |
| [`lp3-03-aks-troubleshoot`](lp3-03-aks-troubleshoot/README.md) | ACR + imagen + AKS en un grupo propio (menú 1-3) | API + `k8s/` con tres averías a propósito (selector, `CrashLoopBackOff`, readiness) | [03-aks-troubleshoot-container](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html) |
| [`lp4-01-cosmos-queries`](lp4-01-cosmos-queries/README.md) | Cuenta Cosmos DB serverless + BD `ragstore` + contenedor `chunks` (`/documentId`) + roles de datos | `client/`: `rag_functions.py`, `test_workflow.py`, app Flask | [01-build-rag-document-store](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/01-build-rag-document-store.html) |
| [`lp4-02-cosmos-vector-search`](lp4-02-cosmos-vector-search/README.md) | Cuenta con `EnableNoSQLVectorSearch` | `client/`: `setup_container.py` (política vectorial + DiskANN), `vector_functions.py`, app Flask | [02-build-semantic-search](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/02-build-semantic-search.html) |
| [`lp4-03-cosmos-optimize`](lp4-03-cosmos-optimize/README.md) | Cuenta con búsqueda vectorial | `client/`: `setup_containers.py` (índices `flat`, `quantizedFlat`, `diskANN`), `index_functions.py`, `generate_sample_data.py`, app Flask | [03-optimize-query-performance](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/03-optimize-query-performance.html) |
| [`lp5-01-pg-agent-backend`](lp5-01-pg-agent-backend/README.md) | Resource group + PostgreSQL Flexible Server solo Entra (+ admin de Entra, contraseña desactivada, firewall `AllowAll`); en la plataforma: `centralus` + `Standard_D2ds_v4`/`GeneralPurpose` | `agent-backend/` (`agent_tools.py` con psycopg + `DefaultAzureCredential`, `test_workflow.py`) + `sql/` | [01-build-agent-tool-backend](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html) |
| [`lp5-02-pg-vector-search`](lp5-02-pg-vector-search/README.md) | Igual que lp5-01 y además `azure.extensions = vector` (opción 2, reinicia el servidor) | `client/` Flask (búsqueda por similitud con `<=>`, embeddings precalculados de 330 dim) + `sql/` | [02-implement-vector-search](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html) |

## Cómo funcionan los scripts (patrón común)
1. **Edición previa:** solo se tocan las variables del principio: `rg` (resource group) y `location`. En el lab 2 además la línea del SKU (`--sku "B1"`; el script trae `P0v3`, y el mensaje impreso `SKU: P0v3` es un texto fijo que no se actualiza, no refleja el SKU real).
2. **Requisito:** `az login` hecho; el script consulta `az ad signed-in-user show` y sale si no hay sesión.
3. **Nombres derivados:** `acr` + los 8 primeros caracteres del SHA-1 del *object id* del usuario (`acrXXXXXXXX`), y en el lab 2 también `plan-docprocessor-XXXXXXXX` y `app-docprocessor-XXXXXXXX`. Mismo usuario ⇒ mismos nombres; en tu tenant del trabajo saldrán otros distintos.
4. **Idempotente:** comprueba con `az group exists` / `az … show` y no recrea lo que ya existe.
5. **Salida:** escribe `.env` (bash, `export VAR="…"`) y `.env.ps1` (PowerShell, `$env:VAR = "…"`) con `RESOURCE_GROUP`, `ACR_NAME`, `LOCATION` (y `APP_PLAN`, `APP_NAME` en el lab 2). Se cargan con `source .env`. Se versionan para tener el lab completo (cuentas temporales ya destruidas, sin claves).
6. **Por debajo solo envuelve `az`** (`subprocess`): `az group create`, `az acr create --sku Basic`, `az acr build --file api/Dockerfile api/`, `az appservice plan create --is-linux`. Lo demás (webapp, identidad, roles, ajustes) lo hace el alumno a mano en la guía.
7. **Menú del lab 2:** 1 = ACR + build · 2 = App Service Plan (y genera `.env`) · 3 = estado del despliegue · 4 = salir.

## Reutilizar en el trabajo
- Cambia `rg`/`location`, y valora el SKU: **ACR Basic** es para pruebas (Standard/Premium para producción, geo-replicación en Premium); **B1** no admite deployment slots ni autoescalado por reglas.
- El script no crea la web app ni asigna `AcrPull`: ese paso (identidad gestionada + rol + `--acr-use-identity`) está documentado en el [README del lab 2](lp1-02-app-service/README.md).
- Para entornos reales conviene pasar estos pasos a IaC (Bicep/Terraform) y a un pipeline; los scripts valen como referencia de los recursos y flags mínimos.
- Antes de ejecutar en una suscripción de empresa: revisar región, políticas de nombres y de red, y **limpiar** con `az group delete --name <rg> --no-wait --yes` (lo lanza quien despliega).
- La imagen de ejemplo se construye en la nube con ACR Tasks: no hace falta Docker local.

## Cómo crean y vinculan el ACR los scripts
Explicación común (qué hace `az acr create`, `az acr build` y la vinculación por identidad, con las comprobaciones): [`acr-en-azdeploy.md`](acr-en-azdeploy.md). Cada README de lab añade los datos de su propio script.

## Labs siguientes
El lab 14 (LP5-03, optimize) y los de LP6 en adelante se añaden a esta tabla al hacerlos. Orden del curso y sesión de cada lab: [`../README.md`](../README.md#cómo-seguir-el-curso).

Los `.env` de LP5 **no** se versionan: `PGPASSWORD` guarda un token de acceso de Entra.

## Catálogo de scripts
Copia de los `azdeploy.py` con su guía de uso en [`../scripts/`](../scripts/README.md).
