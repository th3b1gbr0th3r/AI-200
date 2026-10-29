# Labs · scripts de aprovisionamiento reutilizables

Cada lab trae los ficheros de partida de Microsoft (`azdeploy.py`, `api/`, `document.txt` y, si se conserva, el zip original) **versionados aquí** para poder reutilizarlos en el trabajo. Procedencia y licencia (MIT): [`NOTICE.md`](NOTICE.md). Cada carpeta tiene además su `README.md` con los comandos al detalle.

| Lab | Qué aprovisiona `azdeploy.py` | Qué hay en `api/` | Guía oficial |
|---|---|---|---|
| [`lp1-01-acr-tasks`](lp1-01-acr-tasks/README.md) | Resource group + ACR **Basic** | API Flask (`app.py`, puerto 5000, `Dockerfile` con `python:3.11-slim`) | [01-acr-tasks](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html) |
| [`lp1-02-app-service`](lp1-02-app-service/README.md) | Resource group + ACR (admin desactivado) + build de imagen + App Service Plan Linux | API Flask con gunicorn (`main.py`, puerto 80; `/`, `/health`, `/process`, `/documents`) | [02-app-svc-container](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/02-app-svc-container.html) |

## Cómo funcionan los scripts (patrón común)
1. **Edición previa:** solo se tocan las variables del principio: `rg` (resource group) y `location`. En el lab 2 además la línea del SKU (`--sku "B1"`; el script trae `P0v3`, y el mensaje impreso `SKU: P0v3` es un texto fijo que no se actualiza, no refleja el SKU real).
2. **Requisito:** `az login` hecho; el script consulta `az ad signed-in-user show` y sale si no hay sesión.
3. **Nombres derivados:** `acr` + los 8 primeros caracteres del SHA-1 del *object id* del usuario (`acrXXXXXXXX`), y en el lab 2 también `plan-docprocessor-XXXXXXXX` y `app-docprocessor-XXXXXXXX`. Mismo usuario ⇒ mismos nombres; en tu tenant del trabajo saldrán otros distintos.
4. **Idempotente:** comprueba con `az group exists` / `az … show` y no recrea lo que ya existe.
5. **Salida:** escribe `.env` (bash, `export VAR="…"`) y `.env.ps1` (PowerShell, `$env:VAR = "…"`) con `RESOURCE_GROUP`, `ACR_NAME`, `LOCATION` (y `APP_PLAN`, `APP_NAME` en el lab 2). Se cargan con `source .env`. Están en `.gitignore`: son locales.
6. **Por debajo solo envuelve `az`** (`subprocess`): `az group create`, `az acr create --sku Basic`, `az acr build --file api/Dockerfile api/`, `az appservice plan create --is-linux`. Lo demás (webapp, identidad, roles, ajustes) lo hace el alumno a mano en la guía.
7. **Menú del lab 2:** 1 = ACR + build · 2 = App Service Plan (y genera `.env`) · 3 = estado del despliegue · 4 = salir.

## Reutilizar en el trabajo
- Cambia `rg`/`location`, y valora el SKU: **ACR Basic** es para pruebas (Standard/Premium para producción, geo-replicación en Premium); **B1** no admite deployment slots ni autoescalado por reglas.
- El script no crea la web app ni asigna `AcrPull`: ese paso (identidad gestionada + rol + `--acr-use-identity`) está documentado en el [README del lab 2](lp1-02-app-service/README.md).
- Para entornos reales conviene pasar estos pasos a IaC (Bicep/Terraform) y a un pipeline; los scripts valen como referencia de los recursos y flags mínimos.
- Antes de ejecutar en una suscripción de empresa: revisar región, políticas de nombres y de red, y **limpiar** con `az group delete --name <rg> --no-wait --yes` (lo lanza quien despliega).
- La imagen de ejemplo se construye en la nube con ACR Tasks: no hace falta Docker local.

## Labs siguientes
Los de LP2 (ACA) usarán el mismo patrón (`azdeploy.py` con menú, `.env`) y se incorporarán a esta tabla al hacerlos.
