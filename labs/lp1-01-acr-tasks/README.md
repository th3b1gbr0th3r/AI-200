# Lab LP1-01 · Build and run a container image with ACR Tasks

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html
Documentación oficial del módulo (MS Learn): https://learn.microsoft.com/es-es/training/modules/store-manage-containers-azure-container-registry/
Notas de clase del learning path: [`docs/modulos/01-alojamiento-contenedores.md`](../../docs/modulos/01-alojamiento-contenedores.md)
Material de partida: `acr-tasks-python.zip` (https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/acr-tasks-python.zip). No se versiona aquí: descargar y descomprimir en esta carpeta (`azdeploy.py` + `api/`).

Ejecutado en Linux (bash) contra la suscripción temporal del lab. La plataforma del curso da los mismos pasos en PowerShell.

## Objetivo
Usar **ACR Tasks** para construir y gestionar una imagen de contenedor **íntegramente en la nube**, sin Docker local: crear un registry, construir y publicar una imagen, probarla, versionarla con tags y protegerla contra cambios.

Al terminar debes ser capaz de explicar: qué es un registry/repositorio/tag/digest, por qué el digest es inmutable y el tag no, qué ejecuta realmente `az acr build` y `az acr run`, y cómo se bloquea una imagen de producción.

## Qué se construye
```
 tu terminal (az CLI)
      │  az acr build ./api            (sube Dockerfile + app.py, 1,2 KiB)
      ▼
 ┌────────────────────────────┐        ┌──────────────────────────────────────┐
 │ Agente efímero de ACR Tasks│ push ─►│ ACR  acr<hash>.azurecr.io  (Basic)   │
 │ (build, run; sin caché)    │        │  └ inference-api                      │
 └────────────────────────────┘        │      ├ v1.0.0  sha256:7525…  (bloqueada)│
      ▲  az acr run (pull + ejecuta)   │      └ v1.1.0  sha256:ae0b…           │
      └────────────────────────────────┴──────────────────────────────────────┘
        todo dentro de un resource group (rg-ai200-acr), en eastus
```
- **Registry** = almacén (no ejecuta nada). **ACR Tasks** = cómputo efímero que construye y ejecuta.
- La app (`api/app.py`) es una API Flask de inferencia simulada; el Dockerfile la empaqueta con Python 3.11.

## Fases del lab
| Fase | Qué haces | Qué demuestra |
|---|---|---|
| 1. Despliegue | `azdeploy.py` crea el resource group y el ACR | El registry es un servicio PaaS: sin infraestructura que gestionar |
| 2. Build | `az acr build` v1.0.0 | Build en entorno controlado (respuesta del knowledge check 1) |
| 3. Verificación | listar repos, tags y manifests | Tag = puntero mutable; digest = huella inmutable (knowledge check 2) |
| 4. Prueba | `az acr run` con `python -c 'from app import app'` | La imagen arranca; la ejecuta un agente de Tasks, no el registry |
| 5. Versionado | segundo build v1.1.0 | Mismo código ≠ mismo digest; se comparten las capas de la base |
| 6. Protección | `--write-enabled false` sobre v1.0.0 | Guardarraíl contra sobrescritura (falta `--delete-enabled false` para impedir el borrado) |
| 7. Cleanup | `az group delete` | Se borra todo de una vez |

## Cómo se relaciona con lo que ya sabes (K8s) y con el examen
- Un tag en `image:` de un Deployment equivale a un tag mutable; `image: repo@sha256:…` fija el artefacto exacto.
- ACR Tasks es un mini CI gestionado (runner efímero, run con ID, triggers por commit, cron o cambio de imagen base).
- Examen (contenedores, 20-25 %): ACR Tasks quick build, digest frente a tag, `acr purge`, tiers Basic/Standard/Premium (geo-replicación solo en Premium).

## Qué hay en el material de partida
- `api/Dockerfile`: `python:3.11-slim` + Flask, copia `app.py`, `ENV APP_VERSION/MODEL_VERSION`, `EXPOSE 5000`, `CMD ["python","app.py"]`.
- `api/app.py`: API Flask simulada de inferencia (`/`, `/health`, `/predict`) que lee su versión de variables de entorno y escucha en `0.0.0.0:5000`.
- `azdeploy.py`: crea el resource group y un ACR Basic (nombre `acr` + 8 hex de un SHA-1 del ID de usuario) y escribe `.env` / `.env.ps1`. Solo se editan `rg` y `location`.

## Comandos ejecutados (en orden)

```bash
# Entorno (proxy corporativo: ver notas/2026-10-27-guia-az-login-lab.md)
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Despliegue (rg=rg-ai200-acr, región=eastus, la que exige el lab)
az provider register --namespace Microsoft.ContainerRegistry
python3 azdeploy.py
source .env

# 1. Build en la nube (sin Docker local)
az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api

# 2. Verificar
az acr repository list --name $ACR_NAME --output table
az acr repository show-tags --name $ACR_NAME --repository inference-api --output table
az acr manifest list-metadata --registry $ACR_NAME --name inference-api --output table

# 3. Probar la imagen en un agente de ACR Tasks
az acr run --registry $ACR_NAME \
  --cmd "$ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" /dev/null

# 4. Segunda versión
az acr build --registry $ACR_NAME --image inference-api:v1.1.0 ./api
az acr repository show-tags --name $ACR_NAME --repository inference-api --output table
az acr task list-runs --registry $ACR_NAME --output table

# 5. Bloquear v1.0.0 y comprobarlo
az acr repository update --name $ACR_NAME --image inference-api:v1.0.0 --write-enabled false
az acr repository show --name $ACR_NAME --image inference-api:v1.0.0

# Cleanup (ejecutado: el grupo solo contenía el ACR; comprobado con az group exists = false)
az group delete --name rg-ai200-acr --no-wait --yes
```

## Comandos al detalle

Convenciones: `az` = Azure CLI; `$VAR` = variable cargada con `source .env`; `-o table` = salida en tabla en lugar de JSON.

### 1. `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`
```
export  REQUESTS_CA_BUNDLE  =  /etc/ssl/certs/ca-certificates.crt
  │            │                          │
  │            │                          └ fichero con las CAs de confianza del sistema
  │            └ variable que lee la librería Python "requests" (la que usa az)
  └ la hereda cualquier proceso que lances desde este shell
```
- **Qué hace:** hace que `az` confíe en las CAs del sistema operativo en lugar de las de su propio bundle de Python.
- **Por qué:** un proxy corporativo que intercepta TLS re-firma los certificados con su propia CA. El sistema ya confía en ella (la instaló la empresa); `az` no, y falla con `SSLCertVerificationError … self-signed certificate in certificate chain`.
- **Detalles:** solo dura lo que dure el shell (para hacerlo permanente, añadirlo a `~/.bashrc`); no desactiva la verificación TLS; `curl` no lo necesita porque ya usa el almacén del sistema; sin proxy no hace falta.

### 2. `az provider register --namespace Microsoft.ContainerRegistry`
```
az   provider   register   --namespace Microsoft.ContainerRegistry
│       │          │                    └ proveedor de recursos (el "paquete" de API de ACR)
│       │          └ acción: activarlo en la suscripción
│       └ grupo de comandos sobre proveedores de recursos
└ CLI
```
- **Qué hace:** registra el proveedor de recursos de ACR en la suscripción. Es asíncrono: devuelve enseguida y termina en segundo plano.
- **Por qué:** una suscripción no puede crear recursos de un servicio hasta que su proveedor está registrado.
- **Comprobación:** `az provider show -n Microsoft.ContainerRegistry --query registrationState -o tsv` → `Registered` (en el lab ya lo estaba, así que fue un trámite).

### 3. `python3 azdeploy.py`
- **Antes:** se editan solo `rg = "rg-ai200-acr"` y `location = "eastus"` (la región exigida por el lab).
- **Qué hace por dentro:** pregunta a Azure quién eres (`az ad signed-in-user show`), calcula el nombre del ACR (`acr` + 8 hex de un SHA-1 del ID de usuario, p. ej. `acrdfbe0335`) y ejecuta, en silencio, el equivalente a:
  ```bash
  az group create --name rg-ai200-acr --location eastus
  az acr create --resource-group rg-ai200-acr --name acrdfbe0335 --sku Basic
  ```
  Después escribe `.env` y `.env.ps1` con `RESOURCE_GROUP`, `ACR_NAME` y `LOCATION`.
- **Por qué un hash:** los nombres de ACR son únicos globalmente y así sale uno estable por usuario.
- **Salida esperada:** `Resource group created`, `ACR created: acr…`, `Login server: acr….azurecr.io` y `Deployment Complete!`.
- **Error típico:** `can't open file 'azdeploy.py'` = ejecutado desde otra carpeta; hay que estar en `labs/lp1-01-acr-tasks`.

### 4. `source .env`
- **Qué hace:** ejecuta el fichero en el shell actual. Contiene líneas `export RESOURCE_GROUP="…"`, `export ACR_NAME="…"`, `export LOCATION="…"`.
- **Por qué `source` y no `./.env`:** ejecutarlo como programa crearía un subshell y las variables morirían con él; `source` las deja en tu sesión.
- **Comprobación:** `echo $ACR_NAME`. Hay que repetirlo en cada terminal nueva. Una errata (`$ACR_NAM`) devuelve vacío sin error.

### 5. `az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api`
```
az acr build  --registry $ACR_NAME   --image inference-api:v1.0.0   ./api
                    │                         │            │          └ contexto de origen: carpeta con el Dockerfile
                    │                         │            └ tag (mutable)
                    │                         └ nombre del repositorio dentro del registry
                    └ registry destino
```
- **Qué hace:** empaqueta `./api` (1,2 KiB), lo sube, y un **agente efímero de ACR Tasks** construye la imagen y la publica en tu registry. No hay Docker local.
- **Fases de la salida:** `Packing source code…` → `Queued a build with ID: ca1` (Run ID) → `Waiting for an agent…` → login al registry → `Step 1/8 … Step 8/8` (una capa por instrucción del Dockerfile) → `Pushed` por capa → `digest: sha256:7525…` → bloque de dependencias (imagen base con su digest) → `Run ID: ca1 was successful after 29s`.
- **Ruido que se ignora:** avisos de pip (`running as root`, `new release of pip`).
- **Por qué:** build en un entorno controlado, sin el "en mi máquina funciona" (respuesta del knowledge check 1).

### 6. `az acr repository list --name $ACR_NAME -o table`
- **Qué hace:** lista los repositorios del registry. Aquí: `inference-api`.
- **Ojo con el flag:** en los comandos `repository`, `--name` es el **registry**; el repositorio va en `--repository` o en `--image`.

### 7. `az acr repository show-tags --name $ACR_NAME --repository inference-api -o table`
- **Qué hace:** lista los tags del repositorio (`v1.0.0`, luego también `v1.1.0`).
- **Concepto:** un tag es un puntero mutable; varios tags pueden apuntar al mismo contenido.

### 8. `az acr manifest list-metadata --registry $ACR_NAME --name inference-api -o table`
- **Qué hace:** una fila por manifest con Digest, Architecture (`amd64`), Os (`linux`), ImageSize (≈50 MB comprimidos), CreatedTime y LastUpdateTime.
- **Ojo con el flag:** aquí `--registry` es el registry y `--name` es el **repositorio** (al revés que en `repository`).
- **Concepto:** el digest `sha256:…` identifica el contenido y es inmutable; debe coincidir con el que imprimió el `push`. Aviso `acr manifest is in preview`: se ignora.

### 9. `az acr run --registry $ACR_NAME --cmd "$ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" /dev/null`
```
--cmd "  <imagen>                                       <comando dentro del contenedor>  "   /dev/null
          └ de qué imagen arrancar el contenedor          └ importa app.py y sale             └ contexto de origen vacío
```
- **Qué hace:** un agente de Tasks hace `pull` de la imagen, arranca un contenedor temporal y ejecuta el comando. Es un `docker run` hecho en la nube (`kubectl run --image=… -- python -c …` en K8s).
- **Salida:** `Unable to find image … locally` (el agente es nuevo), siete capas descargadas, mismo digest `7525…`, `Run ID: ca2 was successful`. No imprime nada de la app: código de salida 0 = éxito; si faltara Flask o hubiera un error, verías el traceback y la run acabaría en `Failed`.
- **Idea clave:** el registry solo almacena; quien ejecuta es ACR Tasks. `/dev/null` es obligatorio porque `az acr run` exige un contexto.

### 10. `az acr build … --image inference-api:v1.1.0 ./api`
- **Qué hace:** repite el build con otro tag (run `ca3`).
- **Lo que se observó:** **digest distinto** (`ae0b67f4…`) con el mismo código: los builds de Docker no son reproducibles (la capa de `pip install` y la fecha de creación de la configuración cambian). Tiempo de build similar (el agente no tiene caché); el `push` es más rápido porque las tres capas de la base salen como `Layer already exists`.

### 11. `az acr task list-runs --registry $ACR_NAME -o table`
- **Qué hace:** historial de runs: RUN ID (`ca3`, `ca2`, `ca1`), TASK (vacío = quick task), PLATFORM, STATUS, TRIGGER (`Manual`), STARTED y DURATION.
- **Para qué:** diagnosticar builds fallidos; con el ID se ven los logs (`az acr task logs --registry $ACR_NAME --run-id <id>`).

### 12. `az acr repository update --name $ACR_NAME --image inference-api:v1.0.0 --write-enabled false`
- **Qué hace:** cambia los atributos del tag. `--image` lleva `repositorio:tag`.
- **Atributos:** `writeEnabled` (sobrescribir), `deleteEnabled` (borrar), `listEnabled`, `readEnabled`.
- **Salida:** devuelve el JSON actualizado con `writeEnabled: false`.
- **Matiz de examen:** esto impide sobrescribir, **no** borrar; una protección completa añade `--delete-enabled false`.

### 13. `az acr repository show --name $ACR_NAME --image inference-api:v1.0.0`
- **Qué hace:** muestra el JSON del tag: `changeableAttributes`, `digest`, `createdTime`, `lastUpdateTime`, `signed: false`.
- **Detalle:** `lastUpdateTime` no cambia al modificar atributos (refleja el contenido); `signed: false` = sin firma de contenido (otra función).

### 14. `az group delete --name rg-ai200-acr --no-wait --yes` y `az group exists --name rg-ai200-acr`
- `--name`: grupo a borrar. `--yes`: sin pedir confirmación. `--no-wait`: devuelve el control y borra en segundo plano.
- Borra **todo** lo que contiene el grupo (aquí solo el ACR). Antes de lanzarlo conviene listar el contenido con `az resource list -g rg-ai200-acr -o table`.
- `az group exists` devuelve `true` mientras borra (el grupo figura como `Deleting`) y `false` al terminar.

## Resultados

| Run | Comando | Resultado | Duración |
|---|---|---|---|
| ca1 | `az acr build` v1.0.0 | OK | 29 s |
| ca2 | `az acr run` | OK (import sin error = código de salida 0) | 17-19 s |
| ca3 | `az acr build` v1.1.0 | OK | 22-23 s |

| Tag | Digest | ImageSize |
|---|---|---|
| v1.0.0 | `sha256:752592a49358be33934fdcb1cd467250608ac3df32ffa9f97958819bc2bf4ba7` | 52 609 261 |
| v1.1.0 | `sha256:ae0b67f44eda3958c9b002f3e98b03398783b28d1364761d1b268e774f275499` | 52 609 243 |

Tras el bloqueo: `writeEnabled: false`, `deleteEnabled: true`.

## Cómo funciona (lo que se aprendió)

**Registry ≠ cómputo.** El registry solo almacena y sirve imágenes. `az acr build` y `az acr run` los ejecutan agentes efímeros de **ACR Tasks** (misma familia de servicio, otra función). Analogía: ACR Tasks es un mini CI gestionado (runner efímero, run con ID, triggers por commit, cron o cambio de imagen base). Un pipeline de Azure DevOps o GitHub Actions orquesta y puede delegar el build con `az acr build`.

**Salida del build.** Empaqueta `./api` y lo sube → encola la run (`Run ID`) → el agente hace login al registry → ejecuta cada paso del Dockerfile (una capa por instrucción) → `push` de capas → imprime el digest y las dependencias (imagen base con su digest, base de los triggers de imagen base).

**`az acr run`.** El argumento de `--cmd` es `<imagen> <comando>`: el agente hace `pull` de la imagen y ejecuta el comando dentro de un contenedor temporal. El `/dev/null` final es el contexto de origen, obligatorio pero vacío.

**Tag vs digest.** Mismo código, dos builds → **digests distintos** (la capa de `pip install` y la fecha de creación de la config no son reproducibles). Por eso `v1.1.0` no es "v1.0.0 renombrada", y por eso se despliega por digest para fijar el artefacto exacto.

**Caché.** El agente es efímero y no conserva caché: el segundo build vuelve a bajar la base y a ejecutar `pip install` (tiempos de build similares). Lo que se ahorra es el `push`: las capas de la base salen como `Layer already exists` (12,3 s → 5,9 s).

**Bloqueo.** `--write-enabled false` impide sobrescribir el tag; no impide borrarlo (`deleteEnabled` sigue en `true`). Una protección real de producción añade `--delete-enabled false`. `signed: false`: la firma de contenido es otra función, no se practica aquí.

## Respuestas del knowledge check del módulo 1
1. Builds inconsistentes en workstations → **ACR Tasks quick build**.
2. Misma versión en todos los nodos aunque se reutilice el tag → referenciar **por digest del manifest**.

## Incidencias y soluciones
| Problema | Causa | Solución |
|---|---|---|
| `az login` → `SSLCertVerificationError` | Proxy corporativo que re-firma TLS; `az` usa su bundle de Python | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` (no desactivar la verificación) |
| `az login -u -p` → `AADSTS50126` | Lo entregado era un Temporary Access Pass, no una contraseña | `az login --use-device-code` en ventana de incógnito y TAP en el navegador |
| `az account show` sin sesión | Login hecho con cuenta personal | Repetir con la cuenta del lab |
| `python3: can't open file azdeploy.py` | Se ejecutó desde la carpeta equivocada | `cd labs/lp1-01-acr-tasks` |
| Región | El lab exige `eastus` (la plataforma lo indica) | `location = "eastus"` |
