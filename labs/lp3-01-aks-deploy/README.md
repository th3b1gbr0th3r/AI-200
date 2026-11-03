# Lab LP3-01 · Deploy an AI inference API to AKS

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/01-aks-deploy-container.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal. Starter de la plataforma: `aks-deploy-python-plataforma.zip` (descargado del enlace del Task 4; es el que se usa en el lab). Starter público original: `aks-deploy-python.zip`. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Salidas reales saneadas: [`salidas.md`](salidas.md) (se crea al ejecutar).

**Estado:** completado el 03/11/2026 (cleanup por recursos lanzado; AKS en `Deleting` al cierre de este documento, a verificar). Salidas reales saneadas: [`salidas.md`](salidas.md).

## Objetivo
Desplegar en AKS una API de inferencia (modelo `gpt-5.1` de Foundry, imagen en ACR), completar `deployment.yaml` (contenedor, liveness, requests/limits) y `service.yaml` (LoadBalancer) y probar con el cliente Python.

## Antes de empezar
Usamos el **starter de la plataforma** (distinto del público). Diferencias en `azdeploy.py`:
| Aspecto | Starter público | Starter de la plataforma |
|---|---|---|
| Valores iniciales | `rg`, `location` | `rg`, `location`, `foundryEndpoint`, `foundryDeploymentName` |
| Grupo de recursos | lo crea el script | **ya existe** (el de la plataforma): ACR y AKS se crean dentro |
| Foundry y modelo | opción 1 crea recurso y despliega `gpt-5-mini` | se crean **a mano en el portal** (Tasks 1-2); el script solo los referencia |
| Nombre del recurso Foundry | derivado de un hash | se deduce del `foundryEndpoint` (`https://<recurso>.openai.azure.com/`) |
| VM del AKS | `Standard_D2s_v7` | `Standard_D2s_v3` (si no hay en la región: v4 o v5) |
| Menú | 1 Foundry · 2 ACR · 3 build · 4 AKS · 5 estado · 6 deploy · 7/8/9 | **1 ACR · 2 build · 3 AKS · 4 estado · 5 deploy · 6 borrar AKS fallido · 7 salir** |

Valores aplicados (03/11/2026): `rg` = grupo de la plataforma (`ResourceMoverRG-…`), `location` = `southeastasia` (la región del **grupo**, no la del recurso Foundry, que está en `swedencentral`), `foundryEndpoint` = endpoint *OpenAI* del recurso (`…openai.azure.com`), `foundryDeploymentName` = `gpt-5.1`. «No cambiar nada más» en el script.
- Revisado el código del starter: solo llama a `az` y `kubectl` (único `os.system`: `clear`); sin red propia.
- La opción 5 hace `az aks get-credentials` (escribe `~/.kube/config`), da el rol *Cognitive Services OpenAI User* al kubelet **sobre el recurso Foundry buscándolo en `rg`** (por eso el recurso tiene que estar en ese mismo grupo), sustituye `ACR_ENDPOINT`, `FOUNDRY_ENDPOINT` y el nombre del despliegue en `deployment.yaml` y aplica los manifiestos con `kubectl`.
- `deployment.yaml` y `service.yaml` llegan **con huecos** (`service.yaml` vacío): se completan según la guía antes de la opción 5.
- Los valores del recurso del lab no se suben al repo tal cual: antes del commit se sustituyen por `<recurso>`.

## Diferencias de la plataforma respecto a la guía oficial
| Cambio | Detalle |
|---|---|
| Task 1 previa | Crear un **proyecto de Microsoft Foundry desde el portal** (`https://ai.azure.com`): entrar con el usuario y el Temporary Access Pass de la pestaña *Info* del lab (*Cloud Express Pass*) y esperar a que se cree solo. No crea grupo nuevo: usa el `ResourceMoverRG-…` de la plataforma |
| Task 2 | Desplegar **`gpt-5.1`** a mano en el proyecto (*Discover → Models → Deploy → Custom settings*, **5000 TPM**) y anotar el nombre del despliegue. Sustituye a la opción 1 del menú público |
| Task 3 | Obtener grupo, región del **grupo** (`southeastasia`) y endpoint *OpenAI* (`…openai.azure.com`). Con `az`: `configurar.sh` lo hace |
| Task 4 | Descargar el starter de la plataforma y rellenar 4 valores en `azdeploy.py`; menú propio (ver tabla de arriba) |
| Cleanup | El recurso Foundry y el despliegue del portal viven en el grupo de la plataforma: **no borrar el grupo**, solo los recursos del curso (ver cleanup) |

## Incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `az cognitiveservices account list` vacío tras entrar en el portal | El proyecto aún no se había creado (o login con otra cuenta) | Esperar unos minutos y repetir; comprobar usuario `XLab-…` y probar en incógnito |
| `x509: certificate signed by unknown authority` en la opción 5 al hacer `kubectl apply` | Proxy de empresa re-firma el TLS; `kubectl` solo confía en la CA del cluster. Quitar la CA no basta: el proxy transparente bloquea el API server (`502 IncompleteCertChain`) | Renderizar el YAML con `sed` y usar `az aks command invoke … --command "kubectl …" --file …` (comando 12; `salidas.md` 10-11) |
| `pip list \| grep openai` no muestra nada en el cliente | El cliente solo usa `httpx` y `python-dotenv`; `openai` es de la API (pod) | Es lo esperado: comprobar `httpx` y `python-dotenv` |

## Reproducir este lab (artefactos guardados)
| Artefacto | Para qué |
|---|---|
| `aks-deploy-python-plataforma.zip` | Starter **original de la plataforma** (Task 4), sin editar. Fuente de verdad |
| `aks-deploy-python.zip` | Starter público de Microsoft Learning, para comparar |
| `azdeploy.py`, `api/`, `client/`, `k8s/` | Starter extraído; `k8s/*.yaml` ya con los huecos completados |
| `configurar.sh` | Rellena los 4 valores de `azdeploy.py` con consultas `az` de lectura, partiendo del zip original |
| `salidas.md` | Salidas reales saneadas de cada comando |

Pasos para repetirlo en otro lab o suscripción:
1. `az login --use-device-code` (con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`) y `az group list -o table`.
2. Task 1-2 en el portal: proyecto de Foundry y despliegue `gpt-5.1` con 5000 TPM.
3. `./configurar.sh <grupo-de-la-plataforma>` → genera `azdeploy.py`. Comprobar: imprime `Placeholders YOUR_ restantes: 0`; si no hay recurso `AIServices` o despliegue, lo dice y sale.
4. `python3 azdeploy.py` → opciones 1, 2, 3, 4 y 5 (ver «Comandos al detalle»).
5. Cliente Python y cleanup (más abajo).

> **Antes de subir al repo:** `azdeploy.py` lleva el endpoint con el identificador del lab. En el commit se deja con `https://<recurso>.openai.azure.com/` y el nombre real del grupo se mantiene (es el de la plataforma); `configurar.sh` regenera el fichero real cuando se necesite.

## Pasos
1. Login y estado inicial (`az login`, `az group list`, proveedores).
2. Portal: Task 1 (proyecto de Foundry) y Task 2 (despliegue `gpt-5.1`, 5000 TPM).
3. Task 3-4: `./configurar.sh <grupo>` rellena los 4 valores de `azdeploy.py`.
4. Completar `k8s/deployment.yaml` (contenedor, liveness, resources) y `k8s/service.yaml` según la guía.
5. `python3 azdeploy.py`: **1** ACR · **2** build · **3** AKS · **4** estado · **5** deploy.
6. Si la 5 falla por el proxy (`x509`): renderizar el YAML con `sed` y aplicar con `az aks command invoke` (ver comando 12).
7. Probar: `curl /healthz` y `/readyz`; cliente Python (`client/.env`, venv, `python main.py`, opciones 1-4).

## Comandos al detalle
Los que crean o borran recursos los lanza el alumno. Salidas reales en [`salidas.md`](salidas.md).

### 1. `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`
```
export                  → variable de entorno solo para esta terminal
REQUESTS_CA_BUNDLE      → la librería requests (que usa az) la lee como almacén de CAs
/etc/ssl/certs/ca-certificates.crt → almacén del sistema, con la CA del proxy de empresa
```
- **Qué hace:** hace que `az` confíe en la CA que re-firma el TLS del proxy.
- **Por qué hace falta:** sin ella `az login` falla con `SSLCertVerificationError`.
- **Qué esperar:** no imprime nada. Comprobar: `echo $REQUESTS_CA_BUNDLE` → la ruta. Repetirlo en cada terminal nueva.
- **Trampa:** esta es una variable acordada del curso; cualquier otra variable de entorno no se muestra sin avisar (ver `CLAUDE.md`).

### 2. `az login --use-device-code`
```
az login            → autenticación en Entra ID
--use-device-code   → az da un código y una URL; el login se completa en el navegador
```
- **Qué hace:** abre sesión y guarda el token en `~/.azure`.
- **Por qué hace falta:** el *Temporary Access Pass* del lab solo vale en login interactivo (navegador, mejor en incógnito); no sirve con usuario y contraseña en terminal.
- **Qué esperar:** una única suscripción `XLabs-<n>` y tenant `Lab Directory`; Enter acepta la predeterminada. Comprobar: `az account show --query state -o tsv` → `Enabled`.
- **Si no coincide:** código caducado → repetir el comando; pase caducado → pedir uno nuevo en la plataforma.

### 3. `az group list -o table`
```
az group list   → lista los resource groups de la suscripción
-o table        → salida tabular legible
```
- **Qué hace / por qué:** inventario inicial; confirma que no quedan restos de labs anteriores y es la base del cleanup final.
- **Qué esperar:** solo `ResourceMoverRG-…`, que crea la plataforma y **no se toca**. Cualquier `rg-ai200-*` es un resto → borrarlo con `az group delete --name <rg> --no-wait --yes` y repetir hasta que desaparezca.

### 4. `az provider list … -o table` (y `az provider register --namespace …`)
```
az provider list           → proveedores de recursos y su estado de registro
--query "[?namespace=='…'].{ns:namespace, estado:registrationState}" → JMESPath: filtra los seis y muestra su estado
az provider register       → activa un proveedor en la suscripción (asíncrono)
```
- **Qué hace / por qué:** una suscripción nueva no puede crear AKS, ACR o Foundry si el proveedor no está `Registered`.
- **Qué esperar:** los seis (CognitiveServices, ContainerService, ContainerRegistry, Compute, Network, Storage) en `Registered`; aquí ya lo estaban, así que el `register` no hizo falta.
- **Si no coincide:** `Registering` → esperar y repetir el `list`; `NotRegistered` → lanzar el `register`.
- **K8s:** no hay equivalente; es parte del modelo de suscripción de Azure.

### 5. `sed -i 's|<your-resource-group-name>|rg-ai200-aks|; s|<your-azure-region>|eastus2|' azdeploy.py`
```
sed -i      → edita el fichero en el sitio
s|a|b|      → sustituye a por b (| de delimitador porque los valores no lo llevan)
```
- **Qué hace:** fija el grupo y la región que usará el script (solo edita un fichero local).
- **Comprobar:** `grep -n '^rg\|^location' azdeploy.py` → `rg = "rg-ai200-aks"` y `location = "eastus2"`.
- **Si no coincide:** editar las dos líneas a mano (líneas 5 y 6).

### 6. Proyecto de Foundry en el portal (Task 1 de la plataforma) y su comprobación
```
az cognitiveservices account list                 → recursos de Cognitive Services / Foundry de la suscripción
--query "[].{nombre:name, rg:resourceGroup, tipo:kind, region:location}" → columnas útiles
```
- **Qué hace / por qué:** el portal crea automáticamente el proyecto (un recurso `AIServices` en un grupo nuevo); la plataforma lo exige antes del resto.
- **Qué esperar:** una fila `AIServices` en `swedencentral` y `provisioningState` = `Succeeded` (`az cognitiveservices account show … --query properties.provisioningState -o tsv`). **No aparece grupo nuevo**: el proyecto se crea dentro de `ResourceMoverRG-…`, el de la plataforma. Hecho el 03/11/2026 (ver `salidas.md`, apartado 4).
- **Si no coincide:** esperar unos minutos y repetir; comprobar que el portal usa el usuario del lab (incógnito).
- **Examen:** Foundry project = recurso de Cognitive Services de tipo `AIServices` + proyecto hijo.

### 7. `az cognitiveservices account deployment list … -o table`
```
az cognitiveservices account deployment list → despliegues de modelo de un recurso Foundry/OpenAI
-g / -n   → grupo y nombre del recurso (el del portal)
--query   → nombre, modelo, versión, estado, capacidad y SKU
```
- **Qué hace / por qué:** confirma que el modelo existe antes de que el código lo llame; un `404 DeploymentNotFound` desde la API suele ser un nombre de despliegue mal escrito.
- **Qué esperar:** `gpt-5.1`, `Succeeded`, `Tpm` = 5 (miles de TPM, es decir 5000), `GlobalStandard`.
- **Si no coincide:** `Failed` → cuota o región (releer el mensaje del portal); sin filas → el despliegue no terminó, repetir tras 1-2 min.
- **K8s/examen:** el *deployment name* es lo que se pasa como `model` en el SDK, no el nombre del modelo; pueden diferir.

### 8. `python3 azdeploy.py` → opción 1 (Create Azure Container Registry)
```
python3 azdeploy.py   → menú interactivo del starter de la plataforma
opción 1              → az acr create en el grupo existente (rg) y la región (location) del script
```
- **Qué hace:** crea el registro `acr<hash>` (SKU Basic); el nombre sale de un hash de tu identidad, así que es reproducible y único.
- **Por qué hace falta:** AKS descargará de aquí la imagen `aks-api`; ACR Tasks (opción 2) construye la imagen en la nube.
- **Qué esperar:** mensaje de éxito y vuelta al menú. Comprobar: `az acr list -g <rg> -o table` → una fila `acr<hash>`, `Succeeded`.
- **Si no coincide:** nombre en uso o proveedor sin registrar → leer el error del script; sin filas → no terminó, repetir la opción 1 (es idempotente: si existe, lo dice).
- **K8s:** el registry es el equivalente a tu registry privado; en AKS el acceso se da por identidad (`AcrPull`), no con `imagePullSecrets`.

### 9. `python3 azdeploy.py` → opción 2 (Build and push API image to ACR)
```
az acr build --resource-group <rg> --registry <acr> --image aks-api:latest --file api/Dockerfile --no-logs api/
```
- **Qué hace:** sube la carpeta `api/` (viene en el zip; el script **no** la crea) a ACR Tasks, que construye la imagen con el Dockerfile en un agente efímero de la nube y la publica como `aks-api:latest`.
- **Por qué:** AKS descarga la imagen del registro; no hace falta Docker local.
- **Qué esperar:** éxito y vuelta al menú (3-5 min). Comprobar: `az acr repository show-tags -n <acr> --repository aks-api -o tsv` → `latest`; `az acr task list-runs -r <acr> -o table` → `Succeeded`.
- **Si no coincide:** `--no-logs` oculta el log → `az acr task logs -r <acr> --run-id <id>`; ejecutar siempre desde esta carpeta (necesita `api/`).

### 10. `python3 azdeploy.py` → opción 3 (Create AKS cluster)
```
az aks create → clúster de 1 nodo Standard_D2s_v3 con identidad gestionada
--attach-acr  → asigna AcrPull a la identidad del kubelet sobre el ACR
```
- **Qué hace:** crea `aks-<hash>` en el grupo y la región del script (5-10 min).
- **Por qué:** es donde correrán los pods. La identidad gestionada + `AcrPull` evita secretos de registro.
- **Qué esperar:** éxito y vuelta al menú. Comprobar: `az aks show -g <rg> -n <aks> --query "{estado:provisioningState, energia:powerState.code}" -o table` → `Succeeded` / `Running`; y `az role assignment list --scope <id-ACR> --query "[?roleDefinitionName=='AcrPull']" -o table` → una fila.
- **Si no coincide:** `Creating` → esperar; `Failed` → opción 6 y repetir (si es SKU/cuota, cambiar `AKS_VM_SIZE`). Cuota comprobada antes: 0 de 350 vCPU.
- **K8s:** control plane gestionado por Azure (no lo administras); el pool de nodos es un VM Scale Set.

### 11. `python3 azdeploy.py` → opción 4 (Check deployment status)
- **Qué hace:** consulta (solo lectura) el estado del despliegue del modelo en Foundry, del ACR y del AKS.
- **Qué esperar:** los tres en `Succeeded` y «AKS cluster is ready for deployment». Si alguno no lo está, no lanzar la opción 5.
- **Si no coincide:** `Creating` → esperar y repetir; AKS `Failed` o `Canceled` → opción 6 y repetir la 3.

### 12. Aplicar y verificar sin `kubectl` local: `az aks command invoke`
```
az aks command invoke -g <rg> -n <aks> --command "kubectl apply -f deployment.yaml -f service.yaml" --file deployment.yaml --file service.yaml
  --command   → comando que corre en un pod efímero dentro del cluster
  --file      → sube el fichero local a ese pod para que el comando lo vea
```
- **Qué hace / por qué:** ejecuta `kubectl` dentro de Azure vía ARM; necesario cuando el proxy bloquea el API server. Antes hay que renderizar el YAML con `sed` (`ACR_ENDPOINT`, `FOUNDRY_ENDPOINT`, `gpt-5-mini` → `gpt-5.1`), porque el script no llegó a hacerlo.
- **Qué esperar:** `exitcode=0`, `created` y luego `successfully rolled out`, `1/1`, `EXTERNAL-IP` pública.
- **Si no coincide:** `ImagePullBackOff` → falta AcrPull o imagen; `CrashLoopBackOff` → `kubectl logs`; IP `<pending>` → esperar.

### 13. Probar la API y el cliente
- `curl -m 20 http://<ip>/healthz` → `alive`; `/readyz` → `ready`. La IP: `az aks command invoke … --command "kubectl get svc aks-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"`.
- Cliente: `client/.env` con `API_ENDPOINT=http://<ip>` (la opción 5 no llegó a escribirlo), `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py`.
- **Estado:** curl verificado (HTTP 200 en ambos); opciones 1-4 del cliente confirmadas por el alumno; salida literal guardada de la 4.
- **Concepto:** la API arma la lista de mensajes (roles `system`/`user`/`assistant`) y llama a `gpt-5.1` con `DefaultAzureCredential`; el cliente solo habla HTTP con la API.

## Cleanup (por recursos: el grupo es de la plataforma)
> **No ejecutar `az group delete`** de la guía: el starter de la plataforma usa un grupo **ya existente** (`ResourceMoverRG-…`) que contiene también el Foundry y recursos de la plataforma. Se borra solo lo que creamos nosotros.

```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
RG=<grupo-de-la-plataforma>
az aks delete -g $RG -n aks-<hash> --no-wait --yes          # 5-10 min; arrastra el grupo MC_… de los nodos
az acr delete -g $RG -n acr<hash> --yes
az cognitiveservices account deployment delete -g $RG -n <recurso-foundry> --deployment-name gpt-5.1
```
Comprobación (solo lectura): `az aks list -g $RG -o table` (pasa por `Deleting` y queda vacío), `az acr list -g $RG -o table` (vacío), `az cognitiveservices account deployment list -g $RG -n <recurso-foundry> -o table` (vacío) y `az group list -o table` (desaparece `MC_…`).

Kubeconfig de la sesión (carpeta `~/.kube` nueva): `kubectl --kubeconfig ~/.kube/config config delete-context/delete-cluster aks-<hash>` y `config unset users.clusterUser_…`; comprobar con `config get-contexts` (vacío).

**Al cierre del día:** borrar el recurso Foundry y su proyecto (los creó el portal, Task 1) y **purgar** el soft-delete (`az cognitiveservices account delete` + `az cognitiveservices account purge`), junto con Application Insights / Log Analytics si aparecen. En el inventario final hubo recursos de la plataforma (`MoveCollection`, App Insights, alertas) que desaparecieron sin que los borráramos nosotros; no se tocan.

## Resultado y aprendizajes
- Flujo completo comprobado: ACR → imagen → AKS → manifiestos → LoadBalancer → API → modelo `gpt-5.1` sin claves (identidad del kubelet + rol *Cognitive Services OpenAI User*).
- **Proxy de empresa:** `kubectl` local no llega al API server de AKS (`x509`, luego `502 IncompleteCertChain`); la vía es `az aks command invoke`.
- **Grupos de la plataforma:** el cleanup de la guía (`az group delete`) sería destructivo; se hace por recursos.
- **Roles:** `system`/`user`/`assistant`; el prompt de sistema vive en la API/configuración, no en el cliente.
