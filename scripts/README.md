# scripts · scripts de Python de los labs

Catálogo de los scripts de Python (`azdeploy.py`) de los labs de Microsoft, cada uno con su `README.md` de uso. Origen y licencia (MIT): [`../labs/NOTICE.md`](../labs/NOTICE.md).

| Script | Qué hace | Uso |
|---|---|---|
| [`lp1-01-acr-tasks/azdeploy.py`](lp1-01-acr-tasks/README.md) | Resource group + Azure Container Registry (Basic) | [README](lp1-01-acr-tasks/README.md) |
| [`lp1-02-app-service/azdeploy.py`](lp1-02-app-service/README.md) | Resource group + ACR + build de imagen + App Service Plan Linux, con menú | [README](lp1-02-app-service/README.md) |
| [`lp2-01-aca-deploy/azdeploy.py`](lp2-01-aca-deploy/README.md) | Resource group + ACR + imagen + Container Apps environment, con menú | [README](lp2-01-aca-deploy/README.md) |
| [`lp2-02-aca-manage/azdeploy.py`](lp2-02-aca-manage/README.md) | Igual que el anterior **y además despliega la container app con su secreto** (opción 3) | [README](lp2-02-aca-manage/README.md) |
| [`lp2-03-aca-scale/azdeploy.py`](lp2-03-aca-scale/README.md) | Igual que lp2-01 y además crea `agent-api` con 1 réplica fija, para practicar el autoescalado (opción 3) | [README](lp2-03-aca-scale/README.md) |

## Reglas comunes
- Cada script espera encontrar **`api/Dockerfile` a su lado** (lo comprueba al arrancar). Las carpetas `api/` están en `../labs/<lab>/api/`: o ejecutas el script desde `labs/<lab>/`, o copias `api/` junto al script.
- Requisitos: Python 3.12+, Azure CLI y `az login` hecho.
- Solo se editan las variables del principio (`rg`, `location`); el resto del fichero no se toca.
- Generan `.env` (bash) y `.env.ps1` (PowerShell) en la carpeta del script; están en `.gitignore`. Cárgalos con `source .env`.
- Los scripts de aquí son copia de los de `labs/<lab>/`. Si se corrige uno, actualizar el otro. Los comandos que siguen al script, al detalle, están en el README de cada lab.
- Crean recursos con coste: limpiar al terminar (`az group delete --name <rg> --no-wait --yes`, lo lanza quien despliega).

## Funciones comunes de todos los scripts (qué hacen y por qué)
Los cuatro `azdeploy.py` comparten las mismas piezas de apoyo. Conviene entenderlas una vez.

| Pieza | Qué hace | Por qué |
|---|---|---|
| `os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")` | Variable de entorno que silencia los avisos de preview y deprecación de `az` | Para que la salida del script no se llene de `WARNING` |
| `_resolve_exe("az")` | Busca el ejecutable en el `PATH` con `shutil.which` (en Windows encuentra `az.cmd`); si no existe, sale con error | Fallar pronto y con un mensaje claro si falta Azure CLI |
| `run_quiet(descripción, [az …])` | Ejecuta un comando con `subprocess.run`, **captura su salida** y solo la imprime si falla (código de salida ≠ 0); devuelve `True`/`False` | Por eso, cuando todo va bien, el script **no muestra la salida de `az`**: solo `ACR created: …`. Si algo falla, enseña el error completo |
| `az_query([az … -o tsv])` | Igual, pero devuelve la salida limpia (o cadena vacía si el comando falla) | Se usa como **sonda de existencia**: «¿existe ya este recurso?». Ojo: vacío significa «no existe **o** hubo un error» (de ahí los falsos «Not created» que a veces se ven) |
| `require_az_login()` | Ejecuta `az ad signed-in-user show --query id -o tsv` y devuelve el *object id* del usuario; si no hay sesión, sale con `Please run: az login` | Comprueba que estás autenticado y obtiene la semilla de los nombres. Falla con un *service principal*, porque no hay «usuario con sesión» |
| `_derived_names(object_id)` | `sha1(object id)` → 8 primeros caracteres → `acr<hash>`, `aca-env-<hash>`, `plan-docprocessor-<hash>`… | El ACR necesita un nombre **único global**; derivarlo del usuario lo hace estable (mismo usuario ⇒ mismo nombre) y evita colisiones con otros alumnos |
| `write_env_files({…})` | Escribe `.env` (bash, `export VAR="…"`) y `.env.ps1` (PowerShell, `$env:VAR = "…"`) en UTF-8, sin BOM y con saltos LF, escapando `\`, `"`, `$` y `` ` `` | Así los comandos manuales de la guía usan `$ACR_NAME`, `$RESOURCE_GROUP`… sin teclear los nombres derivados. Hay que cargarlo con `source .env` |
| `_preflight()` | Comprueba que existe `api/Dockerfile` junto al script y hace `chdir` a la carpeta del script | El build (`az acr build … api/`) usa rutas relativas; por eso el script debe ejecutarse con `api/` a su lado |
| `show_menu` / `clear_screen` / `pause` / bucle `main` | Menú numerado: lee la opción con `input()`, limpia la pantalla, ejecuta la función y espera Enter | Interfaz sencilla; `Ctrl+C` sale con código 130 |

### Comandos `az` que comparten varios scripts
**`az group exists --name <rg>`** → devuelve `true`/`false` (sonda). Si no existe, el script llama a **`az group create --name <rg> --location <region>`**, que crea el resource group (el contenedor lógico de todo lo del lab).

**`az acr show --resource-group <rg> --name <acr> --query name -o tsv`** → sonda: ¿existe el ACR? (`--query name` extrae solo el nombre, `-o tsv` lo devuelve sin comillas).

**`az acr create --resource-group <rg> --name <acr> --sku Basic [--admin-enabled false]`** → crea el registro. `Basic` es el nivel barato para pruebas. `--admin-enabled false` desactiva el usuario administrador del ACR (que usa usuario y contraseña); así el único acceso es por identidad y rol (`AcrPull`). En el lab 1 no se pasa, pero el valor por defecto ya es `false`.

**`az acr build --resource-group <rg> --registry <acr> --image <nombre:tag> --file api/Dockerfile --no-logs api/`** →
```
az acr build        → build en la nube con ACR Tasks (un agente efímero de ACR; no hace falta Docker local)
--registry          → el ACR de destino
--image nombre:tag  → nombre y etiqueta con los que se publica la imagen en el ACR
--file api/Dockerfile → qué Dockerfile usar
--no-logs           → no volcar el log del build (por eso el script parece «mudo»)
api/                → contexto de build: la carpeta que se sube al agente
```
Sube el contexto, construye la imagen y la **publica** (push) en el ACR en una sola operación. Si falla, el script solo dice «failed»; para ver por qué: `az acr task list-runs` y `az acr task logs`.

**`az acr repository show --name <acr> --image <nombre:tag> --query name -o tsv`** → sonda: ¿está la imagen publicada?

**`az containerapp env show --name <env> --resource-group <rg> --query properties.provisioningState -o tsv`** → sonda del environment; `Succeeded` = listo. Otras respuestas: `Waiting`, `InProgress`.
