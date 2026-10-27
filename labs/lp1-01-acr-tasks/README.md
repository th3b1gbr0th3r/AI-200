# Lab LP1-01 · Build and run a container image with ACR Tasks

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/container-hosting/01-acr-tasks.html
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

## Comandos explicados

| # | Comando | Qué hace | Por qué / concepto |
|---|---|---|---|
| 1 | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` | Hace que `az` use el almacén de certificados del sistema | Solo si un proxy corporativo re-firma TLS; `az` trae su propio bundle de Python y no confía en esa CA |
| 2 | `az provider register --namespace Microsoft.ContainerRegistry` | Activa el proveedor de recursos de ACR en la suscripción | Una suscripción no puede crear recursos de un servicio hasta registrar su proveedor (aquí ya estaba `Registered`) |
| 3 | `python3 azdeploy.py` | Crea el resource group y un ACR Basic; escribe `.env` | Envuelve `az group create` y `az acr create --sku Basic`. El nombre del ACR sale de un hash del ID de usuario |
| 4 | `source .env` | Carga `RESOURCE_GROUP`, `ACR_NAME`, `LOCATION` en la sesión | Hay que repetirlo en cada terminal nueva |
| 5 | `az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api` | Sube `./api`, construye la imagen en un agente de ACR Tasks y la sube al registry | Sin Docker local; build en entorno controlado. Genera una run (`ca1`) |
| 6 | `az acr repository list --name $ACR_NAME -o table` | Lista los repositorios | Muestra `inference-api` |
| 7 | `az acr repository show-tags --name $ACR_NAME --repository inference-api -o table` | Lista los tags del repositorio | El tag es una referencia mutable |
| 8 | `az acr manifest list-metadata --registry $ACR_NAME --name inference-api -o table` | Muestra digest, arquitectura, tamaño y fechas de cada manifest | El digest `sha256:…` identifica el contenido y es inmutable; coincide con el del push |
| 9 | `az acr run --registry $ACR_NAME --cmd "<imagen> python -c 'from app import app'" /dev/null` | Arranca un contenedor de la imagen en un agente de Tasks y ejecuta el comando | Prueba que la app importa sin desplegarla. `/dev/null` = contexto de origen vacío. Run `ca2` |
| 10 | `az acr build … --image inference-api:v1.1.0 ./api` | Segunda versión del mismo código | Digest distinto aunque el código no cambie (builds no reproducibles); solo se ahorra tiempo de push por las capas compartidas. Run `ca3` |
| 11 | `az acr task list-runs --registry $ACR_NAME -o table` | Historial de runs | Tipo manual, estado y duración de `ca1`, `ca2`, `ca3` |
| 12 | `az acr repository update --name $ACR_NAME --image inference-api:v1.0.0 --write-enabled false` | Bloquea la escritura del tag | Impide sobrescribirlo; no impide borrarlo (`deleteEnabled` sigue `true`) |
| 13 | `az acr repository show --name $ACR_NAME --image inference-api:v1.0.0` | Muestra los atributos del tag | Comprobar `writeEnabled: false` |
| 14 | `az group delete --name rg-ai200-acr --no-wait --yes` | Borra el resource group y todo lo que contiene | `--no-wait` lo deja en segundo plano |
| 15 | `az group exists --name rg-ai200-acr` | Comprueba si existe | `false` cuando el borrado terminó |

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
