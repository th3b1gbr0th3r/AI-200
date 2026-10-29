# scripts · scripts de Python de los labs

Catálogo de los scripts de Python (`azdeploy.py`) de los labs de Microsoft, cada uno con su `README.md` de uso. Origen y licencia (MIT): [`../labs/NOTICE.md`](../labs/NOTICE.md).

| Script | Qué hace | Uso |
|---|---|---|
| [`lp1-01-acr-tasks/azdeploy.py`](lp1-01-acr-tasks/README.md) | Resource group + Azure Container Registry (Basic) | [README](lp1-01-acr-tasks/README.md) |
| [`lp1-02-app-service/azdeploy.py`](lp1-02-app-service/README.md) | Resource group + ACR + build de imagen + App Service Plan Linux, con menú | [README](lp1-02-app-service/README.md) |
| [`lp2-01-aca-deploy/azdeploy.py`](lp2-01-aca-deploy/README.md) | Resource group + ACR + imagen + Container Apps environment, con menú | [README](lp2-01-aca-deploy/README.md) |

## Reglas comunes
- Cada script espera encontrar **`api/Dockerfile` a su lado** (lo comprueba al arrancar). Las carpetas `api/` están en `../labs/<lab>/api/`: o ejecutas el script desde `labs/<lab>/`, o copias `api/` junto al script.
- Requisitos: Python 3.12+, Azure CLI y `az login` hecho.
- Solo se editan las variables del principio (`rg`, `location`); el resto del fichero no se toca.
- Generan `.env` (bash) y `.env.ps1` (PowerShell) en la carpeta del script; están en `.gitignore`. Cárgalos con `source .env`.
- Los scripts de aquí son copia de los de `labs/<lab>/`. Si se corrige uno, actualizar el otro. Los comandos que siguen al script, al detalle, están en el README de cada lab.
- Crean recursos con coste: limpiar al terminar (`az group delete --name <rg> --no-wait --yes`, lo lanza quien despliega).
