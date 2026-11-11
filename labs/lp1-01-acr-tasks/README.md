# Lab LP1-01 · Build and run a container image with ACR Tasks

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html (índice de guías: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (27/10/2026): hecho completo.** Todos los pasos de la guía ejecutados con resultado correcto. **Cleanup verificado** (`az group exists --name rg-ai200-acr` = `false` el mismo día).
- **Sesión:** [`sesiones/2026-10-27-sesion-02-contenedores.md`](../../sesiones/2026-10-27-sesion-02-contenedores.md) (no hay transcripción de esa fecha). Notas del módulo: [`docs/modulos/01-alojamiento-contenedores.md`](../../docs/modulos/01-alojamiento-contenedores.md). Documentación MS Learn: [Store and manage containers in ACR](https://learn.microsoft.com/es-es/training/modules/store-manage-containers-azure-container-registry/).
- Lab anterior: — (es el primero). Lab siguiente: [LP1-02 · App Service](../lp1-02-app-service/README.md).
- Material de partida versionado en esta carpeta: `acr-tasks-python.zip`, `azdeploy.py` (ya editado) y `api/`. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md).

Ejecutado en Linux (bash) contra la suscripción temporal del lab; la plataforma da los mismos pasos en PowerShell. Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. De este lab solo se guardaron **fragmentos** de las salidas (los que se citan); donde no hay salida guardada se dice y se da el resultado esperado.

## Objetivo (en cristiano)
Construir una imagen de contenedor **sin Docker en tu máquina**: le mandas el código a Azure, un agente de **ACR Tasks** la construye y la deja en tu registry (ACR). Después la pruebas, sacas una segunda versión y bloqueas la primera para que nadie la sobrescriba.

El hilo conductor: **registry = almacén** (no ejecuta nada) y **ACR Tasks = cómputo efímero** que construye y ejecuta. Al acabar tienes que saber explicar qué es registry/repositorio/tag/digest, por qué el digest es inmutable y el tag no, y cómo se protege una imagen de producción.

## Qué se construye
```
 tu terminal (az CLI)
      │  az acr build ./api            (sube Dockerfile + app.py, 1,2 KiB)
      ▼
 ┌────────────────────────────┐        ┌───────────────────────────────────────┐
 │ Agente efímero de ACR Tasks│ push ─►│ ACR  acr<hash>.azurecr.io  (Basic)    │
 │ (build, run; sin caché)    │        │  └ inference-api                      │
 └────────────────────────────┘        │      ├ v1.0.0  sha256:7525… (bloqueada)│
      ▲  az acr run (pull + ejecuta)   │      └ v1.1.0  sha256:ae0b…           │
      └────────────────────────────────┴───────────────────────────────────────┘
        todo dentro de un resource group (rg-ai200-acr), en eastus
```
- `api/Dockerfile`: `python:3.11-slim` + Flask, copia `app.py`, `ENV APP_VERSION/MODEL_VERSION`, `EXPOSE 5000`, `CMD ["python","app.py"]`.
- `api/app.py`: API Flask de inferencia **simulada** (`/`, `/health`, `/predict`) que escucha en `0.0.0.0:5000`.
- `azdeploy.py`: crea el resource group y un ACR Basic (nombre `acr` + 8 hex de un SHA-1 del ID de usuario) y escribe `.env` / `.env.ps1`. Solo se editan `rg` y `location`.

**Analogía K8s:** un tag en `image:` de un Deployment es un puntero mutable; `image: repo@sha256:…` fija el artefacto exacto. ACR Tasks es un mini CI gestionado (runner efímero, run con ID, triggers por commit, cron o cambio de imagen base).

---

## Paso 0 · Preparar la máquina y la terminal
**Por qué:** sin `az` no hay lab, y el proxy de empresa re-firma el TLS con su propia CA: `az` (Python) no confía en ella y falla con `SSLCertVerificationError`. `REQUESTS_CA_BUNDLE` le dice que use las CAs del sistema, que sí la incluyen (no desactiva la verificación).
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash    # en Linux Mint deja el repo pero no instala el paquete
sudo apt-get update && sudo apt-get install -y azure-cli  # instalación efectiva
cd ~/claude/AI-200-Developing/labs/lp1-01-acr-tasks
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
Salida real (fragmento): `az version` → `2.91.0`.

**Qué mirar:** el `export` solo dura lo que la terminal; en cada terminal nueva hay que repetirlo (o ponerlo en `~/.bashrc`). Guía para compañeros: [`notas/2026-10-27-guia-az-login-lab.md`](../../notas/2026-10-27-guia-az-login-lab.md).

✅ **Comprobación:**
```bash
az version --query '"azure-cli"' -o tsv
echo "$REQUESTS_CA_BUNDLE"
```
Esperado: una versión (`2.91.0` o superior) y la ruta `/etc/ssl/certs/ca-certificates.crt`. Si `az` no existe, repite el `apt-get install`; si la variable sale vacía, repite el `export`.

## Paso 1 · `az login` con el usuario temporal del lab
**Por qué:** el lab corre en una suscripción temporal; todo lo que crees tiene que ir ahí, no a la de empresa. Lo que da la plataforma es un **Temporary Access Pass (TAP)**, no una contraseña, y solo vale en un login interactivo.
```bash
az logout
az login --use-device-code   # navegador en incógnito → "Usar otra cuenta" → usuario del lab + TAP
az account show -o table
az group list -o table
```
Salida: no guardada. Esperado: `az account show` muestra la suscripción del lab y `az group list` sale vacío en una instancia nueva.

⚠️ **Lo que pasó:**
- `az login` → `SSLCertVerificationError … self-signed certificate in certificate chain`: faltaba el `export` del paso 0.
- `az login -u <usuario> -p <TAP>` → `AADSTS50126`: el TAP no es una contraseña. Arreglo: `az login --use-device-code` en incógnito.
- `az account show` sin la suscripción del lab: el primer login se hizo con una cuenta personal. Arreglo: `az logout` y repetir con la cuenta del lab.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Esperado: la suscripción y el usuario del lab. Si sale la cuenta de empresa o personal, `az logout` y repite el login.

## Paso 2 · Registrar el proveedor de ACR
**Por qué:** una suscripción no puede crear recursos de un servicio hasta que su proveedor (el «paquete» de API) está registrado. Es asíncrono: el comando vuelve enseguida.
```bash
az provider register --namespace Microsoft.ContainerRegistry
```
Salida: no guardada (en el lab ya estaba registrado, fue un trámite).

✅ **Comprobación:**
```bash
az provider show -n Microsoft.ContainerRegistry --query registrationState -o tsv
```
Esperado: `Registered`. Si sale `Registering`, repite al cabo de un minuto.

## Paso 3 · Crear el resource group y el ACR (`azdeploy.py`)
**Por qué:** el registry es un servicio PaaS: no hay máquinas que gestionar, solo un endpoint `<nombre>.azurecr.io`. El nombre es único en todo Azure, por eso el script le pone un hash estable por usuario.

Antes, en `azdeploy.py` (ya hecho en la copia versionada): `rg = "rg-ai200-acr"` y `location = "eastus"` (región que exige la plataforma).
```bash
grep -nE '^(rg|location) =' azdeploy.py
python3 azdeploy.py
source .env
```
Por dentro el script hace `az ad signed-in-user show` (quién eres), calcula `acr<hash>` y lanza en silencio:
```bash
az group create --name rg-ai200-acr --location eastus
az acr create --resource-group rg-ai200-acr --name acr<hash> --sku Basic   # sin --admin-enabled: admin desactivado
```
Salida real: no guardada completa. Esperado (textos del script): `Resource group created: rg-ai200-acr`, `ACR created: acr<hash>`, `Login server: acr<hash>.azurecr.io`, `Deployment Complete!` y `Environment variables have been saved to: .env and .env.ps1`.

**Qué mirar:** `source .env` carga `RESOURCE_GROUP`, `ACR_NAME` y `LOCATION` en **esta** terminal (`./.env` los cargaría en un subshell que muere al acabar). Hay que repetirlo en cada terminal nueva.

⚠️ **Lo que pasó:** `python3: can't open file '…/azdeploy.py'` → se lanzó desde otra carpeta. Arreglo: `cd labs/lp1-01-acr-tasks`.

✅ **Comprobación:**
```bash
echo "$ACR_NAME"
az acr show -n "$ACR_NAME" --query "{sku:sku.name, state:provisioningState, admin:adminUserEnabled}" -o table
```
Esperado: `acr<hash>` y `Basic  Succeeded  False`. Si `$ACR_NAME` sale vacío, falta `source .env` (o hay una errata en el nombre de la variable: `$ACR_NAM` devuelve vacío sin error). Si el ACR no existe, relanza `python3 azdeploy.py` y mira el `Error: … failed`.

## Paso 4 · Construir y publicar v1.0.0 en la nube (`az acr build`)
**Por qué:** el build se hace en un entorno controlado de Azure, no en tu portátil: se acaba el «en mi máquina funciona» (respuesta 1 del knowledge check). No necesitas Docker local.
```bash
az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api
```
Salida real (fragmentos guardados; la salida completa no se guardó):
```text
Packing source code…   (1,2 KiB)
Queued a build with ID: ca1
Waiting for an agent...
Step 1/8 … Step 8/8
…  Pushed
… digest: sha256:752592a49358be33934fdcb1cd467250608ac3df32ffa9f97958819bc2bf4ba7 …
Run ID: ca1 was successful after 29s
```
**Qué mirar:** las fases: empaqueta y sube `./api` → encola la run (`ca1`) → un agente efímero hace login al registry → un `Step` por instrucción del Dockerfile → `push` capa a capa → **digest** → bloque de dependencias (imagen base con su digest, que es lo que usan los triggers de imagen base). Los avisos de pip (`running as root`, `new release of pip`) son ruido.

✅ **Comprobación:**
```bash
az acr task list-runs --registry $ACR_NAME --query "[0].{run:runId, status:status}" -o table
```
Esperado: `ca1  Succeeded`. Si sale `Failed`, mira el log: `az acr task logs --registry $ACR_NAME --run-id ca1`.

## Paso 5 · Ver repositorio, tag y digest
**Por qué:** separar los tres conceptos. Repositorio = nombre de la imagen; tag = puntero **mutable** (se puede mover a otro contenido); digest = huella `sha256` del contenido, **inmutable** (respuesta 2 del knowledge check: para que todos los nodos corran lo mismo, se despliega por digest).
```bash
az acr repository list --name $ACR_NAME -o table
az acr repository show-tags --name $ACR_NAME --repository inference-api -o table
az acr manifest list-metadata --registry $ACR_NAME --name inference-api -o table
```
Salida real (fragmentos): repositorio `inference-api`; tag `v1.0.0`; manifest con digest `sha256:752592a4…`, `amd64`, `linux`, ImageSize `52609261`.

**Qué mirar:**
- El digest del manifest **coincide** con el que imprimió el `push` del paso 4.
- **Trampa de flags:** en `acr repository`, `--name` es el **registry**; en `acr manifest`, `--registry` es el registry y `--name` el **repositorio**.
- El aviso `acr manifest is in preview` se ignora.

✅ **Comprobación:** el `show-tags` debe listar `v1.0.0`. Si sale vacío o `repository not found`, el build del paso 4 no terminó bien: revisa `list-runs`.

## Paso 6 · Probar la imagen en un agente (`az acr run`)
**Por qué:** el registry no ejecuta nada; para arrancar la imagen hace falta cómputo, y aquí lo pone ACR Tasks. Es un `docker run` en la nube (en K8s: `kubectl run --image=… -- python -c …`). Sirve para **probar** una imagen, no para producción.
```bash
az acr run --registry $ACR_NAME \
  --cmd "$ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" /dev/null
```
Salida real (fragmentos):
```text
Unable to find image '…/inference-api:v1.0.0' locally
… (7 capas descargadas)
… mismo digest sha256:752592a4…
Run ID: ca2 was successful   (17-19 s)
```
**Qué mirar:** `--cmd` es `<imagen> <comando dentro del contenedor>`; el `/dev/null` final es el contexto de origen (obligatorio, aquí vacío). La app **no imprime nada**: el import termina con código 0 y eso es el éxito. Si faltara Flask verías un traceback y la run acabaría en `Failed`. `Unable to find image … locally` es normal: el agente es nuevo y sin caché.

✅ **Comprobación:**
```bash
az acr task list-runs --registry $ACR_NAME --query "[0].{run:runId, status:status}" -o table
```
Esperado: `ca2  Succeeded`. Si sale `Failed`: `az acr task logs --registry $ACR_NAME --run-id ca2`.

## Paso 7 · Segunda versión v1.1.0
**Por qué:** ver qué cambia al versionar: mismo código, nuevo tag… y **otro digest**, porque los builds de Docker no son reproducibles (la capa de `pip install` y la fecha de creación de la configuración cambian). Por eso v1.1.0 no es «v1.0.0 renombrada».
```bash
az acr build --registry $ACR_NAME --image inference-api:v1.1.0 ./api
az acr repository show-tags --name $ACR_NAME --repository inference-api -o table
```
Salida real (fragmentos): run `ca3` correcta en 22-23 s; digest `sha256:ae0b67f44eda3958c9b002f3e98b03398783b28d1364761d1b268e774f275499`; las tres capas de la base salen como `Layer already exists`; tags `v1.0.0` y `v1.1.0`.

**Qué mirar:**
- El build tarda casi lo mismo: el agente es efímero y **no tiene caché** (vuelve a bajar la base y a ejecutar `pip install`).
- Lo que sí se acelera es el **push** (12,3 s → 5,9 s), porque las capas de la base ya estaban en el registry.

⚠️ **Lo que pasó:** se predijo que el segundo build sería mucho más rápido; no lo fue, por la falta de caché.

✅ **Comprobación:** `show-tags` debe listar `v1.0.0` y `v1.1.0`, y `az acr manifest list-metadata --registry $ACR_NAME --name inference-api -o table` dos digests **distintos**. Si solo sale un tag, revisa la run `ca3` con `list-runs`.

## Paso 8 · Historial de runs
**Por qué:** cada build o run tiene un ID y un log; es lo primero que se mira cuando un build falla (como el historial de un pipeline de CI).
```bash
az acr task list-runs --registry $ACR_NAME -o table
```
Salida real (resumen):

| RUN ID | TASK | STATUS | TRIGGER | DURATION |
|---|---|---|---|---|
| ca3 | (vacío) | Succeeded | Manual | 22-23 s |
| ca2 | (vacío) | Succeeded | Manual | 17-19 s |
| ca1 | (vacío) | Succeeded | Manual | 29 s |

**Qué mirar:** `TASK` vacío = *quick task* (lanzada a mano, sin tarea definida). El prefijo del ID depende de la región del registry (`ca` en East US).

✅ **Comprobación:** tres filas `Succeeded`. Si alguna sale `Failed`: `az acr task logs --registry $ACR_NAME --run-id <id>`.

## Paso 9 · Bloquear v1.0.0 (imagen de «producción»)
**Por qué:** un tag es mutable; si alguien hace build con `v1.0.0` otra vez, lo sobrescribe. Bloquear la escritura es el guardarraíl.
```bash
az acr repository update --name $ACR_NAME --image inference-api:v1.0.0 --write-enabled false
az acr repository show --name $ACR_NAME --image inference-api:v1.0.0
```
Salida real (fragmento):
```text
"changeableAttributes": {
  "deleteEnabled": true,
  …
  "writeEnabled": false
},
"digest": "sha256:752592a4…",
"signed": false
```
**Qué mirar:**
- `writeEnabled: false` impide **sobrescribir**, pero `deleteEnabled: true`: **se puede borrar**. Protección completa = añadir `--delete-enabled false` (matiz de examen).
- `lastUpdateTime` **no cambia** al tocar atributos (refleja el contenido).
- `signed: false` = sin firma de contenido (otra función, no se practica).

✅ **Comprobación:**
```bash
az acr repository show --name $ACR_NAME --image inference-api:v1.0.0 --query changeableAttributes.writeEnabled -o tsv
```
Esperado: `false`. Si sale `true`, repite el `update` y revisa que `--image` lleva `repositorio:tag`.

---

## Cleanup (obligatorio al acabar)
**Por qué:** el resource group es la unidad de borrado: se va todo lo que contiene (aquí solo el ACR). Antes conviene ver qué hay dentro.
```bash
az resource list -g rg-ai200-acr -o table
az group delete --name rg-ai200-acr --no-wait --yes
az group exists --name rg-ai200-acr
```
Salida real: `true` mientras borraba (el grupo aparece como `Deleting`) y después `false`.

✅ **Verificado** el 27/10/2026: `az group exists --name rg-ai200-acr` = `false`. Si sigue en `true` pasados 10-15 minutos, mira `az group show -n rg-ai200-acr --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`.

⚠️ **Lo que pasó:** el `delete` lo lanzó Claude por su cuenta y el alumno lo corrigió: desde entonces, los comandos que crean o borran recursos los ejecuta el alumno.

## Resumen de resultados
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

## Resumen de incidencias
| Paso | Síntoma | Causa | Arreglo |
|---|---|---|---|
| 1 | `SSLCertVerificationError` en `az login` | Proxy de empresa que re-firma TLS; `az` usa su propio bundle | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` (paso 0) |
| 1 | `AADSTS50126` con `az login -u -p` | Lo entregado era un TAP, no una contraseña | `az login --use-device-code` en incógnito |
| 1 | `az account show` sin la suscripción del lab | Login con cuenta personal | `az logout` y repetir con la cuenta del lab |
| 3 | `can't open file 'azdeploy.py'` | Lanzado desde otra carpeta | `cd labs/lp1-01-acr-tasks` |
| 3 | Región | La plataforma exige `eastus` | `location = "eastus"` |
| 7 | El 2.º build no fue más rápido | Agente efímero sin caché | Esperable: solo se acelera el push |

## Para el examen (contenedores, 20-25 %)
- Knowledge check del módulo 1: builds inconsistentes en workstations → **ACR Tasks quick build**; misma versión en todos los nodos aunque se reutilice el tag → **referenciar por digest**.
- También cae: `acr purge --untagged --ago 7d` para limpiar, tareas con trigger (`az acr task create … --context <repo>#main`), tiers Basic/Standard/Premium (geo-replicación solo en Premium).

## Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab:

| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (línea 144) | `--sku Basic` y **sin** `--admin-enabled` (admin desactivado por defecto) |
| Subir la imagen | `az acr build` | No lo hace el script: lo lanza el alumno (es el objetivo del lab) |
| Vincular (pull) | — | Ninguna: no hay servicio que descargue la imagen. Eso llega en [LP1-02](../lp1-02-app-service/README.md) |

- **Push y pull son permisos distintos:** el build lo hace ACR con tu `az login`; la descarga la hace el servicio con una identidad y el rol **AcrPull**.
