# Lab LP3-01 · Deploy an AI inference API to AKS (plataforma: Lab 6 · AI-200-LP03M01)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/01-aks-deploy-container.html (índice en [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (03/11/2026): completado.** Hechos todos los pasos: Foundry y `gpt-5.1` en el portal, ACR, imagen, AKS, manifiestos aplicados con `az aks command invoke` y API probada con `curl` y con el cliente (opciones 1-4). **Cleanup verificado** a las 19:57 (grupo de la plataforma con 0 recursos, sin soft-delete) y kubeconfig local limpio a las 20:42.
- **Incidencia principal:** el proxy de empresa bloquea `kubectl` contra el API server de AKS (paso 12). Desde ese día la regla es **primero `az`, después lo local**.
- Registro de la sesión: [`sesiones/2026-11-03-sesion-04-aks.md`](../../sesiones/2026-11-03-sesion-04-aks.md). Notas del módulo: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Cómo crea el script el ACR: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md).
- Lab anterior: [LP2-03](../lp2-03-aca-scale/README.md) · Lab siguiente: [LP3-02](../lp3-02-aks-configure/README.md). Origen MIT de `azdeploy.py`, `api/`, `client/` y `k8s/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: IDs de suscripción/tenant, usuario, Temporary Access Pass y código de dispositivo fuera; hash de ACR/AKS como `<hash>`, IP pública como `<ip>`, recurso de Foundry como `xlab-<id>`.

## Qué se construye
Una API FastAPI (`api/`) que hace de pasarela hacia el modelo `gpt-5.1` de Foundry, empaquetada en ACR y desplegada en AKS detrás de un LoadBalancer público. El pod llama al modelo **sin claves**: con la identidad del kubelet y el rol *Cognitive Services OpenAI User*.

```
Portal (Task 1-2) → proyecto Foundry xlab-<id> + despliegue gpt-5.1 (5000 TPM)   [grupo ResourceMoverRG-… de la plataforma]
azdeploy.py 1     → ACR acr<hash> (Basic)
azdeploy.py 2     → az acr build → imagen aks-api:latest (se construye en la nube, sin Docker local)
azdeploy.py 3     → AKS aks-<hash> (1 nodo Standard_D2s_v3, --attach-acr = AcrPull al kubelet)
azdeploy.py 5     → rol OpenAI User al kubelet ✔ · kubectl apply ✘ (proxy)
az aks command invoke → kubectl apply deployment.yaml + service.yaml (dentro del cluster)
cliente (PC) ──HTTP──► LoadBalancer <ip>:80 ──► pod aks-api:8000 ──Entra ID──► gpt-5.1
```

**El objetivo, en cristiano:** pasar de «tengo un modelo en Foundry» a «tengo una API en Kubernetes que lo usa», con las tres piezas que importan en el examen: el **registro** (ACR, de dónde sale la imagen), el **cluster** (AKS, dónde corre) y la **identidad** (cómo baja la imagen y cómo llama al modelo sin secretos). Para un SysOps de K8s lo nuevo no son los manifiestos, sino la parte Azure: `AcrPull` en vez de `imagePullSecrets`, rol RBAC en vez de API key, LoadBalancer de Azure.

### El starter de la plataforma no es el público
La plataforma da su propio zip (`aks-deploy-python-plataforma.zip`, del enlace del Task 4); `aks-deploy-python.zip` es el público, solo para comparar.

| Aspecto | Starter público | Starter de la plataforma (el usado) |
|---|---|---|
| Valores a rellenar | `rg`, `location` | `rg`, `location`, `foundryEndpoint`, `foundryDeploymentName` |
| Grupo de recursos | lo crea el script | **ya existe** (`ResourceMoverRG-…`, de la plataforma) |
| Foundry y modelo | opción 1 crea recurso y `gpt-5-mini` | **a mano en el portal** (Tasks 1-2), modelo `gpt-5.1` |
| VM del AKS | `Standard_D2s_v7` | `Standard_D2s_v3` |
| Menú | 1 Foundry · 2 ACR · 3 build · 4 AKS · 5 estado · 6 deploy… | **1 ACR · 2 build · 3 AKS · 4 estado · 5 deploy · 6 borrar AKS fallido · 7 salir** |
| Cleanup de la guía | `az group delete` | **prohibido**: el grupo no es nuestro → borrar por recursos |

Revisado el código antes de ejecutarlo: solo llama a `az` y `kubectl` (único `os.system`: `clear`). La opción 5 hace `az aks get-credentials`, asigna el rol *OpenAI User* al kubelet sobre el recurso Foundry **buscándolo en `rg`**, sustituye `ACR_ENDPOINT`, `FOUNDRY_ENDPOINT` y `gpt-5-mini` en `deployment.yaml` y aplica con `kubectl` local (lo que falla aquí).

---

## Paso 0 · Preparar la terminal
**Por qué:** el proxy de empresa re-firma el TLS; `az` (Python) solo confía en él si se le indica el almacén del sistema. Hay que hacerlo **en cada terminal nueva**.
```bash
cd ~/claude/AI-200-Developing/labs/lp3-01-aks-deploy
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `echo $REQUESTS_CA_BUNDLE` → `/etc/ssl/certs/ca-certificates.crt` (variable acordada del curso, se puede mostrar). Si sale vacío, repite el `export`; sin ella `az login` falla con `SSLCertVerificationError`.

## Paso 1 · `az login` con el usuario del lab
**Por qué:** cada lab trae un usuario temporal y una suscripción propia. El *Temporary Access Pass* solo vale en login interactivo (navegador, mejor en incógnito), por eso `--use-device-code`.
```bash
az login --use-device-code
```
Salida real:
```text
To sign in, use a web browser to open the page https://login.microsoft.com/device and enter the code <código> to authenticate.

[Tenant and subscription selection]

No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-<n>            <sub-id>                              Lab Directory

Select a subscription and tenant (Type a number or Enter for no changes):

Tenant: Lab Directory
Subscription: XLabs-<n> (<sub-id>)
```
**Qué mirar:** una sola suscripción `XLabs-<n>` en el tenant `Lab Directory`, marcada con `*`; Enter la acepta. El pase se escribe en el navegador, nunca en la terminal.

✅ **Comprobación:**
```bash
az account show --query "{estado:state, sub:name}" -o table
```
Salida real:
```text
Estado    Sub
--------  ---------
Enabled   XLabs-<n>
```
Si sale la cuenta de empresa o un lab anterior: `az logout` y repite. Si el código caduca, relanza el comando; si caduca el pase, pide otro en la plataforma.

## Paso 2 · Inventario inicial de la suscripción
**Por qué:** saber qué había **antes** es la base del cleanup: al final solo se borra lo que no estaba.
```bash
az group list -o table
```
Salida real:
```text
Name                                      Location       Status
----------------------------------------  -------------  ---------
ResourceMoverRG-eastus-southeastasia-sea  southeastasia  Succeeded
```
**Qué mirar:** el único grupo, `ResourceMoverRG-…`, lo crea la plataforma. En este lab **todo se crea dentro de él**, así que no se podrá borrar el grupo al final.

✅ **Comprobación:** ningún `rg-ai200-*` = sin restos de labs anteriores. Si hubiera alguno, bórralo (`az group delete --name <rg> --no-wait --yes`) antes de seguir.

## Paso 3 · Proveedores de recursos
**Por qué:** una suscripción nueva no puede crear AKS, ACR o Foundry si el proveedor no está `Registered`. La guía manda `az provider register`; antes de lanzarlo se mira si hace falta.
```bash
az provider list --query "[?namespace=='Microsoft.ContainerService'||namespace=='Microsoft.ContainerRegistry'||namespace=='Microsoft.CognitiveServices'||namespace=='Microsoft.Compute'||namespace=='Microsoft.Network'||namespace=='Microsoft.Storage'].{ns:namespace, estado:registrationState}" -o table
```
Salida real:
```text
Ns                           Estado
---------------------------  ----------
Microsoft.CognitiveServices  Registered
Microsoft.Storage            Registered
Microsoft.ContainerService   Registered
Microsoft.Network            Registered
Microsoft.Compute            Registered
Microsoft.ContainerRegistry  Registered
```
**Qué mirar:** los seis ya `Registered`: los `az provider register` de la guía **no hicieron falta**.

✅ **Comprobación:** si alguno sale `NotRegistered`, lanza `az provider register --namespace <ns>` y repite el `list` hasta ver `Registered` (`Registering` = esperar).

## Paso 4 · Task 1 (portal): crear el proyecto de Foundry
**Por qué:** en el starter de la plataforma el script **no** crea Foundry; el proyecto y su recurso `AIServices` se crean desde `https://ai.azure.com` con el usuario del lab (pestaña *Info* → *Cloud Express Pass*).

Datos del diálogo *Create a project*, aceptados por defecto: proyecto `xlab-<id>`, recurso `xlab-<id>-resource`, región **Sweden Central**, grupo `ResourceMoverRG-…` (el de la plataforma). Sin marcar «Set up recommended resources» (evita un App Insights extra; aun así el portal creó App Insights y Log Analytics, que luego desaparecieron solos).

Comprobación con `az` (en vez de mirar el portal):
```bash
az cognitiveservices account list --query "[].{nombre:name, rg:resourceGroup, tipo:kind, region:location}" -o table
```
Salida real (primer intento, a las 18:14, todavía creándose):
```text
(sin filas)
```
Salida real (18:18):
```text
Nombre                      Rg                                        Tipo        Region
--------------------------  ----------------------------------------  ----------  -------------
xlab-<id>-resource          ResourceMoverRG-eastus-southeastasia-sea  AIServices  swedencentral
```
**Qué mirar:** un recurso `AIServices` en `swedencentral` **dentro del grupo de la plataforma**: no se crea grupo nuevo. Proyecto de Foundry = recurso de Cognitive Services tipo `AIServices` + proyecto hijo.

✅ **Comprobación:**
```bash
az cognitiveservices account show -g ResourceMoverRG-eastus-southeastasia-sea -n xlab-<id>-resource --query "{estado:properties.provisioningState, sku:sku.name}" -o table
```
Salida real: `Succeeded  S0`. Si la lista sale vacía, espera unos minutos y repite; si sigue vacía, comprueba que el portal usa el usuario del lab (incógnito).

## Paso 5 · Task 2 (portal): desplegar `gpt-5.1`
**Por qué:** la API necesita un *deployment* del modelo. Su **nombre** es lo que el código pasa como `model`, no el nombre del modelo (pueden diferir).

En el proyecto: *Discover → Models → gpt-5.1 → Deploy → Custom settings*, **Tokens per Minute Rate Limit = 5000**. Nombre del despliegue: `gpt-5.1`.
```bash
az cognitiveservices account deployment list -g ResourceMoverRG-eastus-southeastasia-sea -n xlab-<id>-resource \
  --query "[].{nombre:name, modelo:properties.model.name, version:properties.model.version, estado:properties.provisioningState, tpm:sku.capacity, sku:sku.name}" -o table
```
Salida real:
```text
Nombre    Modelo    Version     Estado     Tpm    Sku
--------  --------  ----------  ---------  -----  --------------
gpt-5.1   gpt-5.1   2025-11-13  Succeeded  5      GlobalStandard
```
**Qué mirar:** `Succeeded`; `Tpm` = 5 porque la capacidad va en **miles** de TPM (5 = 5000; el portal mostró también 50 RPM); `GlobalStandard` = despliegue global de pago por uso.

✅ **Comprobación:** fila `gpt-5.1` en `Succeeded`. Sin filas → aún no ha terminado (repite en 1-2 min); `Failed` → cuota o región, lee el mensaje del portal. El portal enseña también una *Key*: **no se usa ni se guarda**, la API entra con identidad.

## Paso 6 · Task 3-4: rellenar los cuatro valores de `azdeploy.py`
**Por qué:** el script crea ACR y AKS en `rg`/`location` y necesita el endpoint OpenAI y el nombre del despliegue para dárselos al pod. Ojo: `location` es la región **del grupo** (`southeastasia`), no la del recurso Foundry (`swedencentral`).

Primero `az` (consultas de solo lectura, en lugar de copiar del portal): [`configurar.sh`](configurar.sh) saca los cuatro valores y genera `azdeploy.py` desde el zip original.
```bash
./configurar.sh ResourceMoverRG-eastus-southeastasia-sea
diff <(unzip -p aks-deploy-python-plataforma.zip azdeploy.py) azdeploy.py
```
Salida real del `diff` (el 03/11 la edición se hizo con `sed` con estos mismos valores; `configurar.sh` se escribió después para repetirlo):
```text
5,8c5,8
< rg                    = "YOUR_RESOURCE_GROUP"    # Existing resource group name (Task 3)
< location              = "YOUR_REGION"            # Azure region in CLI format, e.g. eastus, eastus2 (Task 3)
< foundryEndpoint       = "YOUR_FOUNDRY_ENDPOINT"  # OpenAI endpoint URL (Task 3), e.g. https://<recurso>.openai.azure.com/
< foundryDeploymentName = "YOUR_DEPLOYMENT_NAME"   # Model deployment name (Task 2), e.g. gpt-5.1
---
> rg                    = "ResourceMoverRG-eastus-southeastasia-sea"    # Existing resource group name (Task 3)
> location              = "southeastasia"            # Azure region in CLI format, e.g. eastus, eastus2 (Task 3)
> foundryEndpoint       = "https://<recurso>.openai.azure.com/"  # OpenAI endpoint URL (Task 3), e.g. https://<recurso>.openai.azure.com/
> foundryDeploymentName = "gpt-5.1"   # Model deployment name (Task 2), e.g. gpt-5.1
```
**Qué mirar:** solo cambian las líneas 5-8 («Do not change anything else»). El endpoint es el de la pestaña **OpenAI** (`…openai.azure.com`), no el `services.ai.azure.com/openai/v1/responses` que muestra el despliegue.

✅ **Comprobación:** `configurar.sh` termina con `Placeholders YOUR_ restantes: 0`. Si dice «No hay recurso AIServices» falta el paso 4; si dice «Falta endpoint OpenAI o despliegue» falta el paso 5. En el repo `azdeploy.py` se guarda con `https://<recurso>.openai.azure.com/`: hay que regenerarlo con `configurar.sh`.

Comprobación extra de la VM y la cuota (el AKS es lo que más suele fallar):
```bash
az vm list-skus -l southeastasia --size Standard_D2s_v3 --resource-type virtualMachines --query "[0].restrictions[0].reasonCode" -o tsv
az vm list-usage -l southeastasia --query "[?name.value=='cores'||name.value=='standardDSv3Family'].{familia:name.value, usado:currentValue, limite:limit}" -o table
```
Salida real:
```text
None
Familia             Usado    Limite
------------------  -------  --------
cores               0        350
standardDSv3Family  0        350
```
`None` = sin restricciones (v4 y v5 también disponibles). Si sale `NotAvailableForSubscription`, cambia `AKS_VM_SIZE` a `Standard_D2s_v4`/`v5`.

## Paso 7 · Completar `k8s/deployment.yaml` y `k8s/service.yaml`
**Por qué:** el starter trae `deployment.yaml` con tres huecos y `service.yaml` **vacío** (0 líneas); sin ellos no hay contenedor ni forma de llegar desde fuera.

Lo que se añadió (copia de la guía; ya está en [`k8s/`](k8s/)):
- `deployment.yaml` → contenedor `api` (`ACR_ENDPOINT/aks-api:latest`, `imagePullPolicy: Always`, puerto `http` 8000); **liveness** `GET /healthz` (10 s de retardo, cada 30 s, 3 fallos); **resources** requests 256Mi/250m y limits 512Mi/500m. La readiness (`/readyz`) ya venía.
- `service.yaml` → `aks-api-service`, `type: LoadBalancer` público (`azure-load-balancer-internal: "false"`), selector `app: aks-api` + `version: v1`, puerto 80 → `http`.

```bash
python3 -I -c "import yaml; [print(f, 'OK', yaml.safe_load(open(f))['kind']) for f in ('k8s/deployment.yaml','k8s/service.yaml')]"
```
Salida real:
```text
k8s/deployment.yaml OK Deployment
k8s/service.yaml OK Service
```
**Qué mirar:** los dos cargan como YAML. `ACR_ENDPOINT`, `FOUNDRY_ENDPOINT` y `gpt-5-mini` **siguen** como placeholders: los sustituye la opción 5 (o el paso 14).

✅ **Comprobación:** si da error de YAML, casi siempre es indentación. Liveness ≠ readiness: liveness reinicia el contenedor; readiness solo lo saca del Service (`/readyz` comprueba que el pod llega a Foundry).

## Paso 8 · `azdeploy.py` opción 1: crear el ACR
**Por qué:** el registro privado del que AKS bajará la imagen. El nombre `acr<hash>` sale de un hash de tu identidad: estable entre ejecuciones y único en Azure.
```bash
python3 azdeploy.py      # menú → 1
```
✅ **Comprobación** (salida real):
```bash
az acr list -g ResourceMoverRG-eastus-southeastasia-sea --query "[].{nombre:name, sku:sku.name, estado:provisioningState, region:location}" -o table
```
```text
Nombre       Sku    Estado     Region
-----------  -----  ---------  -------------
acr<hash>    Basic  Succeeded  southeastasia
```
**Qué mirar:** `Basic`, `Succeeded`, dentro del grupo de la plataforma. Si no hay filas: aún no has lanzado la opción (a las 18:32 salió vacío por eso) o falló; lee el mensaje del script. La opción es idempotente: si el ACR existe, lo dice.

## Paso 9 · Opción 2: construir la imagen en ACR
**Por qué:** `az acr build` sube `api/` (viene en el zip) y ACR Tasks construye y publica `aks-api:latest` en la nube: no hace falta Docker local ni `docker push` a través del proxy.
```bash
python3 azdeploy.py      # menú → 2   (3-5 min; usa --no-logs)
```
✅ **Comprobación** (salida real):
```bash
az acr repository show-tags -n acr<hash> --repository aks-api -o tsv
az acr task list-runs -r acr<hash> --query "[].status" -o tsv
```
```text
latest
Succeeded
```
Si el run sale `Failed`: `az acr task logs -r acr<hash> --run-id <id>` (con `--no-logs` el script no enseña el log). Lánzalo siempre desde la carpeta del lab (necesita `api/`).

## Paso 10 · Opción 3: crear el AKS
**Por qué:** es donde corren los pods. `--attach-acr` da **AcrPull** a la identidad del kubelet sobre el ACR: los nodos bajan la imagen sin `imagePullSecrets` (push y pull son permisos distintos: el push lo hizo ACR con tu `az login`).
```bash
python3 azdeploy.py      # menú → 3   (5-10 min)
```
Salida real mientras corría:
```text
Nombre        Estado    Energia    K8s    Nodos    Vm
------------  --------  ---------  -----  -------  ---------------
aks-<hash>    Creating  Running    1.36   1        Standard_D2s_v3
```
✅ **Comprobación** (salida real al terminar):
```bash
RG=ResourceMoverRG-eastus-southeastasia-sea; AKS=aks-<hash>; ACR=acr<hash>
az aks show -g $RG -n $AKS --query "{estado:provisioningState, energia:powerState.code, k8s:kubernetesVersion}" -o table
az role assignment list --scope $(az acr show -g $RG -n $ACR --query id -o tsv) --query "[?roleDefinitionName=='AcrPull'].{rol:roleDefinitionName, tipo:principalType}" -o table
```
```text
Estado     Energia    K8s
---------  ---------  -----
Succeeded  Running    1.36
Rol      Tipo
-------  ----------------
AcrPull  ServicePrincipal
```
**Qué mirar:** `Succeeded`/`Running` y la fila `AcrPull` (la identidad del kubelet). Si el AKS queda `Failed`/`Canceled`: opción 6 (borra solo un AKS fallido), corrige SKU/cuota y repite la 3. Si falta `AcrPull`: `az aks update -g $RG -n $AKS --attach-acr $ACR`.

## Paso 11 · Opción 4: estado del despliegue
**Por qué:** consulta (solo lectura) que las tres piezas están listas antes de desplegar.
```bash
python3 azdeploy.py      # menú → 4
```
Salida real:
```text
Checking deployment status...

Foundry Model Deployment (gpt-5.1):
  Status: Succeeded
  Model deployed and ready

Azure Container Registry (acr<hash>):
  Status: Succeeded

AKS Cluster (aks-<hash>):
  Status: Succeeded
  AKS cluster is ready for deployment
```
✅ **Comprobación:** las tres en `Succeeded`. Si alguna no, no lances la 5: espera (`Creating`) o repite su opción.

## Paso 12 · Opción 5: lanzarla para el rol (y saber que el `apply` fallará)
**Por qué:** la opción 5 hace cuatro cosas; las dos primeras son útiles y van por `az` (`get-credentials` y el rol *Cognitive Services OpenAI User* al kubelet sobre Foundry), pero la tercera es `kubectl apply` **local**, que el proxy de empresa bloquea. Se lanza igualmente por el rol; el despliegue se hace en los pasos 14-15 con `az`.
```bash
python3 azdeploy.py      # menú → 5
```
Salida real:
```text
Deploying application to AKS...

Getting AKS credentials...
AKS credentials configured

Assigning Cognitive Services OpenAI User role to AKS identity...
Role assigned to AKS kubelet identity (may take 1-2 minutes to propagate)

Deploying Kubernetes manifests...
Error: Apply deployment manifest failed (exit code 1).
error: error validating "STDIN": error validating data: failed to download openapi: Get "https://aks-<hash>-<…>.hcp.southeastasia.azmk8s.io:443/openapi/v2?timeout=32s": tls: failed to verify certificate: x509: certificate signed by unknown authority; if you choose to ignore these errors, turn validation off with --validate=false
```
**Qué mirar:** credenciales ✔ y rol ✔; falla el `apply`. El Service y el `client/.env` no llegan a crearse.

✅ **Comprobación del rol** (solo lectura; salida real `1`):
```bash
K=$(az aks show -g $RG -n $AKS --query identityProfile.kubeletidentity.objectId -o tsv)
F=$(az cognitiveservices account list -g $RG --query "[?kind=='AIServices']|[0].id" -o tsv)
az role assignment list --assignee $K --scope $F --query "[?roleDefinitionName=='Cognitive Services OpenAI User']|length(@)" -o tsv
```
Si sale `0`, asígnalo con `az` sin pasar por la opción 5: `az role assignment create --assignee-object-id $K --assignee-principal-type ServicePrincipal --role "Cognitive Services OpenAI User" --scope $F`.

⚠️ **Lo que pasó (diagnóstico del proxy):**
1. `x509`: `kubectl` (Go) solo confía en la CA del kubeconfig, la CA privada del cluster; el proxy re-firma con la suya. `az` sí funciona porque usa `REQUESTS_CA_BUNDLE`, que `kubectl` ignora.
2. Se probó quitar la CA del kubeconfig (`kubectl config unset clusters.<aks>.certificate-authority-data`): el TLS pasó, pero el proxy respondió `502 Bad Gateway · IncompleteCertChain` (no puede validar la CA privada del API server y **bloquea**). `NO_PROXY='.azmk8s.io'` no cambió nada: el proxy es transparente.
3. Conclusión: desde este PC **no se llega al puerto 443 del API server**. `az aks command invoke` sí funciona: va por ARM (`management.azure.com`), que el proxy deja pasar, y ejecuta el `kubectl` en un pod efímero dentro del cluster.

Esos cambios del paso 2 (kubeconfig) los hizo Claude sin pedirlo; desde entonces el alumno lanza todo lo que escribe y Claude solo verifica en lectura.

## Paso 13 · Renderizar los manifiestos (lo que la opción 5 no llegó a hacer)
**Por qué:** `deployment.yaml` sigue con `ACR_ENDPOINT`, `FOUNDRY_ENDPOINT` y `gpt-5-mini`. Se sustituyen igual que el script, en una carpeta temporal del repo (`tmp/`, ignorada por git), para no ensuciar `k8s/`.
```bash
mkdir -p ../../tmp/aks1
EP=$(grep -oE 'https://[a-z0-9-]+\.openai\.azure\.com/' azdeploy.py | head -1)
sed "s|ACR_ENDPOINT|$ACR.azurecr.io|; s|FOUNDRY_ENDPOINT|$EP|; s|gpt-5-mini|gpt-5.1|" k8s/deployment.yaml > ../../tmp/aks1/deployment.yaml
cp k8s/service.yaml ../../tmp/aks1/service.yaml
echo "pendientes de sustituir: $(grep -c 'ACR_ENDPOINT\|FOUNDRY_ENDPOINT\|gpt-5-mini' ../../tmp/aks1/deployment.yaml)"
grep -n "image:\|OPENAI_DEPLOYMENT_NAME" -A1 ../../tmp/aks1/deployment.yaml
```
Salida real:
```text
pendientes de sustituir: 0
24:        image: acr<hash>.azurecr.io/aks-api:latest  # Container image from
25-        imagePullPolicy: Always  # Always pull the latest image from registry
--
35:        - name: OPENAI_DEPLOYMENT_NAME
36-          value: "gpt-5.1"
```
✅ **Comprobación:** `pendientes de sustituir: 0`. Si no, revisa que `EP` no esté vacío (`azdeploy.py` todavía con `<recurso>` → regenera con `configurar.sh`).

## Paso 14 · Aplicar con `az aks command invoke` (sustituye al `kubectl apply` local)
**Por qué:** es el mismo `kubectl apply`, pero ejecutado **dentro** del cluster; `--file` sube cada YAML al pod efímero que corre el comando.
```bash
cd ../../tmp/aks1
az aks command invoke -g $RG -n $AKS \
  --command "kubectl apply -f deployment.yaml -f service.yaml" \
  --file deployment.yaml --file service.yaml
cd -
```
Salida real:
```text
command started at 2026-11-03 18:50:38+00:00, finished at 2026-11-03 18:50:40+00:00 with exitcode=0
deployment.apps/aks-api created
service/aks-api-service created
```
**Qué mirar:** `exitcode=0` y dos `created`. (El 03/11 este paso lo ejecutó Claude; el alumno decidió no repetirlo y seguir desde ese estado.)

> **Alternativa local, solo si el PC no tiene proxy:** `az aks get-credentials -g $RG -n $AKS` y `kubectl apply -f ../../tmp/aks1/`. No es la primera opción porque en el PC de empresa falla siempre (paso 12); `az aks command invoke` no necesita kubeconfig.

✅ **Comprobación:** paso 15. Si `exitcode` ≠ 0, lee el error de `kubectl` que devuelve (validación de YAML, nombre…).

## Paso 15 · Verificar el rollout y la IP pública
**Por qué:** `created` solo dice que el API server aceptó el objeto; hay que ver que el pod arranca (imagen bajada con AcrPull, probes en verde) y que Azure asigna IP al LoadBalancer.
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl rollout status deploy/aks-api --timeout=120s; kubectl get deploy,svc,pods -o wide"
```
Salida real:
```text
command started at 2026-11-03 18:50:54+00:00, finished at 2026-11-03 18:51:13+00:00 with exitcode=0
Waiting for deployment "aks-api" rollout to finish: 0 of 1 updated replicas are available...
deployment "aks-api" successfully rolled out
NAME                      READY   UP-TO-DATE   AVAILABLE   AGE   CONTAINERS   IMAGES                                SELECTOR
deployment.apps/aks-api   1/1     1            1           33s   api          acr<hash>.azurecr.io/aks-api:latest   app=aks-api,version=v1

NAME                      TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)        AGE    SELECTOR
service/aks-api-service   LoadBalancer   10.0.77.162   <ip>          80:32297/TCP   33s    app=aks-api,version=v1
service/kubernetes        ClusterIP      10.0.0.1      <none>        443/TCP        9m8s   <none>

NAME                           READY   STATUS    RESTARTS   AGE   IP           NODE
pod/aks-api-68c499c9c6-7lw2l   1/1     Running   0          33s   10.224.0.6   aks-nodepool1-<…>-vmss000000
```
**Qué mirar:** `successfully rolled out`, `1/1`, `RESTARTS 0` y `EXTERNAL-IP` pública (no `<pending>` ni `10.x`).

✅ **Comprobación:** `ImagePullBackOff` → falta AcrPull o el tag (paso 10/9); `CrashLoopBackOff` → `az aks command invoke … --command "kubectl logs deploy/aks-api"`; `0/1 Running` → readiness: el pod no llega a Foundry (endpoint mal renderizado); IP `<pending>` → espera un minuto.

## Paso 16 · Sacar la IP del LoadBalancer
**Por qué:** el cliente y `curl` necesitan la IP; la opción 5 la habría escrito en `client/.env`, pero no llegó.
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl get svc aks-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
```
Salida real:
```text
command started at 2026-11-03 19:02:33+00:00, finished at 2026-11-03 19:02:34+00:00 with exitcode=0
<ip>
```
✅ **Comprobación:** una IP pública. Vacía → el LoadBalancer aún no la tiene; repite en un minuto.

## Paso 17 · Probar los probes desde fuera
**Por qué:** antes del cliente, confirmar que el LoadBalancer enruta al pod. `/healthz` = proceso vivo; `/readyz` = el pod alcanza Foundry (un `HEAD` al endpoint; **no** prueba aún el rol, eso lo hace la inferencia). Aquí `curl` local sí vale: es HTTP a una IP pública, que el proxy dejó pasar.
```bash
IP=<ip>
curl -sS -m 20 -w '\nHTTP %{http_code}\n' http://$IP/healthz
curl -sS -m 20 -w '\nHTTP %{http_code}\n' http://$IP/readyz
```
Salida real:
```text
{"status":"alive","service":"aks-foundry-gateway"}
HTTP 200
{"status":"ready","foundry_endpoint":"https://<recurso>.openai.azure.com/"}
HTTP 200
```
✅ **Comprobación:** dos HTTP 200. `/readyz` 503 → el pod no llega a Foundry (endpoint del YAML o red); `curl` colgado → el proxy bloquea esa IP: prueba desde dentro con `az aks command invoke … --command "kubectl exec deploy/aks-api -- python -c \"import urllib.request;print(urllib.request.urlopen('http://aks-api-service/healthz').read().decode())\""`.

## Paso 18 · Preparar el cliente Python
**Por qué:** el cliente (`client/main.py`) solo habla HTTP con la API; lee `API_ENDPOINT` de `client/.env` con `python-dotenv`. Sus dependencias van en un `.venv` propio (ignorado por git).
```bash
cd client
printf 'API_ENDPOINT=http://%s\n' "$IP" > .env
cat .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list | grep -i -E "httpx|dotenv"
```
Salida real (recortada):
```text
API_ENDPOINT=http://<ip>
Successfully installed anyio-4.16.0 certifi-2026.10.23 h11-0.16.0 httpcore-1.0.9 httpx-0.25.1 idna-3.20 python-dotenv-1.0.0 sniffio-1.3.1 typing_extensions-4.16.0
python-dotenv     1.0.0
```
**Qué mirar:** el cliente **no lleva `openai`** (solo `httpx` y `python-dotenv`): quien llama al modelo es el pod. El primer `grep` se hizo buscando `openai` y no salió: es lo esperado.

✅ **Comprobación:** `.env` con la IP y `httpx`/`python-dotenv` instalados. Si `pip` falla por certificado: `PIP_CERT=/etc/ssl/certs/ca-certificates.crt pip install -r requirements.txt`.

## Paso 19 · Ejecutar el cliente (opciones 1-4)
**Por qué:** la opción 3/4 es la prueba de extremo a extremo: cliente → LoadBalancer → pod → `gpt-5.1` **sin clave** (identidad del kubelet + rol OpenAI User). La API arma los mensajes con roles (`user`, sin prompt de sistema).
```bash
python main.py
```
Salida real (opción 4, chat con streaming):
```text
  AKS Foundry Gateway API - Client Menu
============================================================
API Endpoint: http://<ip>
============================================================
1. Check API Health (Liveness)
2. Check API Readiness (Foundry Connectivity)
3. Send Inference Request
4. Start Chat Session (Streaming)
5. Exit
============================================================
Select option (1-5): 4

[*] Starting chat session...
============================================================

You (type 'exit' to end): hoas del curso IA-200
Assistant: Te puedo ayudar, pero necesito un poco más de contexto.

¿A qué te refieres con "hoas del curso IA-200"? Puede ser, por ejemplo:
- ¿Apuntes/hojas de trabajo del curso IA-200?
- ¿Hojas de ejercicios o prácticas?
(…el modelo pide más contexto y ofrece ayuda…)
```
**Qué mirar:** el texto llega en streaming (SSE desde `/v1/inference/stream`). El prompt tenía una errata y el modelo pidió aclaración: sin prompt de sistema responde como asistente genérico. El alumno confirmó que **las opciones 1-4 funcionan**; solo se guardó la salida literal de la 4.

✅ **Comprobación:** si la 3 o la 4 dan `401`/`403`, el rol aún se propaga (espera 2 min); `404 DeploymentNotFound` → el nombre del despliegue del YAML no coincide con el del paso 5; `500` → `kubectl logs` del pod vía `az aks command invoke`. Si sale `API Endpoint: http://localhost:8000`, no estás en `client/` o falta el `.env`.

---

## Cleanup (por recursos: el grupo es de la plataforma)
**Por qué no `az group delete`:** la guía dice `az group delete --name <rg-name>`, pero aquí `<rg-name>` sería `ResourceMoverRG-…`, que **no es nuestro** (contiene el Foundry, el `MoveCollection` de la plataforma…). Se borra solo lo que creamos. El AKS va primero porque es lo caro; arrastra solo su grupo de nodos `MC_…`.
```bash
deactivate 2>/dev/null; export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
RG=ResourceMoverRG-eastus-southeastasia-sea
az aks delete -g $RG -n aks-<hash> --no-wait --yes
az acr delete -g $RG -n acr<hash> --yes
az cognitiveservices account deployment delete -g $RG -n xlab-<id>-resource --deployment-name gpt-5.1
```
Salida real: ninguna (los tres comandos devuelven el control sin imprimir).

Comprobación inmediata (19:17):
```bash
az aks list -g $RG --query "[].{n:name, estado:provisioningState}" -o table
az acr list -g $RG -o table
az cognitiveservices account deployment list -g $RG -n xlab-<id>-resource --query "[].name" -o tsv
az group list --query "[].name" -o tsv
```
```text
N             Estado
------------  --------
aks-<hash>    Deleting

ResourceMoverRG-eastus-southeastasia-sea
MC_ResourceMoverRG-eastus-southeastasia-sea_aks-<hash>_southeastasia
NetworkWatcherRG
```
**Qué mirar:** las listas de ACR y de despliegues salieron vacías (borrados al momento); el AKS en `Deleting` (5-10 min) y el `MC_…` desaparece con él. No se relanza el borrado: solo se espera. En ese momento el grupo solo tenía el Foundry y su proyecto; `MoveCollection`, App Insights, Log Analytics y alertas ya no estaban (los retiró la plataforma).

✅ **Verificado** a las 19:57 (desde la sesión del lab 8, leyendo la suscripción del lab 6): `az group list` → solo `ResourceMoverRG-…`; `az aks list` vacío; `az resource list` → **0 recursos**; `az cognitiveservices account list-deleted` vacío (nada que purgar: el Foundry también lo retiró la plataforma). Si en otra repetición el Foundry siguiera, se borra al cierre del día con `az cognitiveservices account delete` + `az cognitiveservices account purge`.

**Kubeconfig local** (lo creó la opción 5 con `get-credentials`): limpiado a las 20:42.
```bash
kubectl --kubeconfig ~/.kube/config config delete-context aks-<hash>
kubectl --kubeconfig ~/.kube/config config delete-cluster aks-<hash>
kubectl --kubeconfig ~/.kube/config config unset users.clusterUser_ResourceMoverRG-eastus-southeastasia-sea_aks-<hash>
kubectl --kubeconfig ~/.kube/config config get-contexts
```
Salida real (la última línea es el recuento que se hizo en lugar del `get-contexts`):
```text
deleted context aks-<hash> from ~/.kube/config
deleted cluster aks-<hash> from ~/.kube/config
Property "users.clusterUser_ResourceMoverRG-eastus-southeastasia-sea_aks-<hash>" unset.
contextos: 0 · clusters: 0 · usuarios: 0
```
Esto es solo local (no toca Azure). Al final del día también se hizo `az logout` y `az account clear` (0 cuentas).

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `az cognitiveservices account list` vacío tras entrar en el portal | El proyecto aún se estaba creando | Esperar y repetir (paso 4) |
| `x509: certificate signed by unknown authority` en la opción 5 | El proxy re-firma el TLS y `kubectl` solo confía en la CA del cluster | `az aks command invoke` (pasos 13-15) |
| `502 Bad Gateway · IncompleteCertChain` al quitar la CA del kubeconfig | El proxy transparente no valida la CA privada de AKS y bloquea | Ídem: no hay vía local; `NO_PROXY` no sirve |
| `client/.env` no existe | La opción 5 se cortó antes de escribirlo | Paso 16 + `printf` del paso 18 |
| `pip list \| grep openai` vacío en el cliente | El cliente no usa `openai`; lo usa el pod | Lo esperado: comprobar `httpx` y `python-dotenv` |
| La guía manda `az group delete` | El grupo es de la plataforma | Cleanup por recursos |
| Claude aplicó YAML y editó el kubeconfig sin pedirlo | Error de proceso | Regla: el alumno ejecuta los cambios; Claude solo lee |

## Artefactos del lab
| Fichero | Para qué |
|---|---|
| `aks-deploy-python-plataforma.zip` | Starter original de la plataforma (fuente de verdad) |
| `aks-deploy-python.zip` | Starter público, para comparar |
| `azdeploy.py`, `api/`, `client/`, `k8s/` | Starter extraído; `k8s/*.yaml` ya completados (con placeholders), `azdeploy.py` con el endpoint saneado |
| `configurar.sh` | Regenera `azdeploy.py` con los 4 valores mediante consultas `az` de lectura |

## Para el examen
- ACR: el build en la nube (`az acr build`) frente a `docker build/push`; el pull por identidad (**AcrPull** al kubelet, `--attach-acr`) frente a admin user o `imagePullSecrets`.
- Foundry: el *deployment name* es lo que va como `model`; la API entra con `DefaultAzureCredential` y el rol *Cognitive Services OpenAI User*, sin clave.
- Probes: liveness (`/healthz`) reinicia; readiness (`/readyz`) saca del Service.
- `az aks command invoke` ejecuta `kubectl` dentro del cluster vía ARM: útil con API server privado o red que lo bloquea.
