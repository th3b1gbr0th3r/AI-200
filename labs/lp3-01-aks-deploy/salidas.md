# Salidas reales · LP3-01 Deploy an AI inference API to AKS

Saneadas: sin ID de suscripción, tenant, usuario ni Temporary Access Pass del lab, sin código de dispositivo. Ejecutado el 03/11/2026 en Linux.

## 1. `az login --use-device-code`
```console
To sign in, use a web browser to open the page https://login.microsoft.com/device and enter the code <código> to authenticate.

[Tenant and subscription selection]

No     Subscription name    Subscription ID   Tenant
-----  -------------------  ----------------  -------------
[1] *  XLabs-<n>            <subscription-id> Lab Directory

Tenant: Lab Directory
Subscription: XLabs-<n> (<subscription-id>)
```
**Qué mirar:** una sola suscripción del lab, marcada con `*` (predeterminada); Enter acepta. El Temporary Access Pass se escribe en el navegador (ventana de incógnito), nunca en la terminal.

## 2. Estado inicial de la suscripción
```console
$ az account show --query "{estado:state, sub:name}" -o table
Estado    Sub
--------  ---------
Enabled   XLabs-<n>

$ az group list -o table
Name                                      Location       Status
----------------------------------------  -------------  ---------
ResourceMoverRG-eastus-southeastasia-sea  southeastasia  Succeeded
```
**Qué mirar:** `Enabled`. El único grupo, `ResourceMoverRG-…`, lo crea la plataforma: **no es del curso y no se toca**. Ningún `rg-ai200-*` = limpio, sin restos del lab 5.

## 3. Proveedores de recursos
```console
$ az provider list --query "[?namespace=='Microsoft.ContainerService'||…].{ns:namespace, estado:registrationState}" -o table
Ns                           Estado
---------------------------  ----------
Microsoft.CognitiveServices  Registered
Microsoft.Storage            Registered
Microsoft.ContainerService   Registered
Microsoft.Network            Registered
Microsoft.Compute            Registered
Microsoft.ContainerRegistry  Registered
```
**Qué mirar:** los seis ya en `Registered`; los `az provider register` de la guía no hacen falta en esta suscripción.

## 4. Proyecto de Foundry creado desde el portal (Task 1 de la plataforma)
Datos del diálogo *Create a project*, aceptados por defecto: proyecto `xlab-<id>-<n>`, recurso Foundry `xlab-<id>-<n>-resource`, región Sweden Central, grupo `ResourceMoverRG-…` (el de la plataforma), sin marcar «Set up recommended resources» (evita un App Insights extra).

```console
$ az cognitiveservices account list --query "[].{nombre:name, rg:resourceGroup, tipo:kind, region:location}" -o table
Nombre                      Rg                                        Tipo        Region
--------------------------  ----------------------------------------  ----------  -------------
xlab-<id>-<n>-resource      ResourceMoverRG-eastus-southeastasia-sea  AIServices  swedencentral

$ az cognitiveservices account show -g ResourceMoverRG-… -n xlab-<id>-<n>-resource --query "{estado:properties.provisioningState, sku:sku.name, endpoint:properties.endpoint}" -o table
Estado     Sku    Endpoint
---------  -----  ---------------------------------------------------
Succeeded  S0     https://xlab-<id>-<n>-resource.cognitiveservices.azure.com/

$ az cognitiveservices account deployment list -g ResourceMoverRG-… -n xlab-<id>-<n>-resource -o table
(sin filas)
```
**Qué mirar:** `AIServices` en `swedencentral` y `Succeeded`: el proyecto está listo. Sin despliegues de modelo todavía. **No se creó ningún grupo nuevo**: el proyecto vive en el `ResourceMoverRG-…` de la plataforma, que no se borra. En el cleanup solo se borra el recurso Foundry (y se purga el soft-delete), nunca el grupo.

## 5. Despliegue del modelo gpt-5.1 (Task 2 de la plataforma)
Hecho en el portal: *Discover → Models → gpt-5.1 → Deploy → Custom settings*, **Tokens per Minute Rate Limit = 5000**. Nombre del despliegue: `gpt-5.1` (se pega en el script en el Task 4).

```console
$ az cognitiveservices account deployment list -g ResourceMoverRG-… -n xlab-<id>-<n>-resource --query "[].{nombre:name, modelo:properties.model.name, version:properties.model.version, estado:properties.provisioningState, tpm:sku.capacity, sku:sku.name}" -o table
Nombre    Modelo    Version     Estado     Tpm    Sku
--------  --------  ----------  ---------  -----  --------------
gpt-5.1   gpt-5.1   2025-11-13  Succeeded  5      GlobalStandard
```
**Qué mirar:** `Succeeded`; `Tpm` = 5 porque la capacidad se mide en **miles** de tokens por minuto (5 = 5000 TPM); `GlobalStandard` = despliegue global con facturación por uso. El nombre exacto (`gpt-5.1`) es el que usa el código como `model`/`deployment`.

## 6. `azdeploy.py` · opción 1 · Create Azure Container Registry
```console
$ az acr list -g ResourceMoverRG-… --query "[].{nombre:name, sku:sku.name, estado:provisioningState, region:location}" -o table
Nombre       Sku    Estado     Region
-----------  -----  ---------  -------------
acr<hash>    Basic  Succeeded  southeastasia
```
**Qué mirar:** nombre `acr<hash>` (el script lo deriva de un hash de tu identidad: es estable entre ejecuciones), SKU `Basic`, `Succeeded` y misma región que el grupo. Se creó **dentro del grupo de la plataforma** (el grupo ya existía, el script no lo crea).

## 7. `azdeploy.py` · opción 2 · Build and push API image to ACR
```console
$ az acr repository list -n acr<hash> -o tsv
aks-api

$ az acr repository show-tags -n acr<hash> --repository aks-api -o tsv
latest

$ az acr task list-runs -r acr<hash> --query "[].{id:runId, estado:status, tarea:taskName}" -o table
Estado
---------
Succeeded
```
**Qué mirar:** el repositorio `aks-api` con el tag `latest` y el run del build en `Succeeded`: la imagen ya está en el registro y AKS podrá descargarla. La opción 2 usa `--no-logs`, así que esta consulta es la forma de ver el resultado (y, si fallara, `az acr task logs -r acr<hash> --run-id <id>`).

## 8. `azdeploy.py` · opción 3 · Create AKS cluster
```console
$ az aks list -g ResourceMoverRG-… --query "[].{nombre:name, estado:provisioningState, energia:powerState.code, k8s:kubernetesVersion, nodos:agentPoolProfiles[0].count, vm:agentPoolProfiles[0].vmSize}" -o table
Nombre        Estado    Energia    K8s    Nodos    Vm
------------  --------  ---------  -----  -------  ---------------
aks-<hash>    Creating  Running    1.36   1        Standard_D2s_v3

$ az aks show -g ResourceMoverRG-… -n aks-<hash> --query "{estado:provisioningState, energia:powerState.code, k8s:kubernetesVersion}" -o table
Estado     Energia    K8s
---------  ---------  -----
Succeeded  Running    1.36

$ az role assignment list --scope <id del ACR> --query "[?roleDefinitionName=='AcrPull'].{rol:roleDefinitionName, tipo:principalType}" -o table
Rol      Tipo
-------  ----------------
AcrPull  ServicePrincipal
```
**Qué mirar:** la primera consulta, mientras corría, mostraba `Creating`; después `Succeeded` + `Running` (un nodo `Standard_D2s_v3`). El rol `AcrPull` sobre el ACR lo dejó el script al crear el cluster: es la identidad del **kubelet**, por eso los pods descargan la imagen sin `imagePullSecrets`.

## 9. `azdeploy.py` · opción 4 · Check deployment status
```console
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
**Qué mirar:** las tres piezas (modelo, registro, cluster) en `Succeeded`. Es la condición para lanzar la opción 5. Solo consulta; no cambia nada.

## 10. `azdeploy.py` · opción 5 · Deploy to AKS: INCIDENCIA del proxy
```console
Deploying application to AKS...

Getting AKS credentials...
AKS credentials configured

Assigning Cognitive Services OpenAI User role to AKS identity...
Role assigned to AKS kubelet identity (may take 1-2 minutes to propagate)

Deploying Kubernetes manifests...
Error: Apply deployment manifest failed (exit code 1).
error: error validating "STDIN": error validating data: failed to download openapi: Get "https://aks-<hash>-<...>.hcp.southeastasia.azmk8s.io:443/openapi/v2?timeout=32s": tls: failed to verify certificate: x509: certificate signed by unknown authority; if you choose to ignore these errors, turn validation off with --validate=false
```
**Qué mirar:** los dos primeros pasos (credenciales y rol) salieron bien; falló el `kubectl apply`. **Causa:** el proxy de empresa re-firma el TLS; `kubectl` solo confía en la CA del kubeconfig (la del cluster), no en la del proxy (`az` sí, vía `REQUESTS_CA_BUNDLE`). Al quitar la CA del kubeconfig el TLS pasó, pero el proxy transparente bloqueó el API server con `502 Bad Gateway · IncompleteCertChain` (no valida la CA privada de AKS). `NO_PROXY` no cambia nada. **Conclusión:** desde este PC no se llega al puerto 443 del API server; se usa `az aks command invoke` (ARM), que el proxy sí deja pasar.

## 11. Aplicar y verificar con `az aks command invoke` (sustituye a `kubectl` local)
```console
$ az aks command invoke -g ResourceMoverRG-… -n aks-<hash> --command "kubectl apply -f deployment.yaml -f service.yaml" --file deployment.yaml --file service.yaml
command started at …, finished at … with exitcode=0
deployment.apps/aks-api created
service/aks-api-service created

$ az aks command invoke … --command "kubectl rollout status deploy/aks-api --timeout=120s; kubectl get deploy,svc,pods -o wide"
Waiting for deployment "aks-api" rollout to finish: 0 of 1 updated replicas are available...
deployment "aks-api" successfully rolled out
NAME                      READY   UP-TO-DATE   AVAILABLE   IMAGES
deployment.apps/aks-api   1/1     1            1           acr<hash>.azurecr.io/aks-api:latest
NAME                      TYPE           CLUSTER-IP    EXTERNAL-IP      PORT(S)
service/aks-api-service   LoadBalancer   10.0.77.162   <ip-publica>     80:32297/TCP
pod/aks-api-…             1/1     Running   0
```
**Qué mirar:** `exitcode=0`, `successfully rolled out`, `READY 1/1` y una `EXTERNAL-IP` pública (no `<pending>` ni `10.x`). Los YAML se renderizaron antes con `sed` (`ACR_ENDPOINT`, `FOUNDRY_ENDPOINT`, `gpt-5-mini` → `gpt-5.1`), igual que haría el script.

## 12. Probes desde fuera (curl) y cliente Python
```console
$ az aks command invoke … --command "kubectl get svc aks-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
<ip-publica>

$ curl -m 20 http://<ip>/healthz
{"status":"alive","service":"aks-foundry-gateway"}   HTTP 200
$ curl -m 20 http://<ip>/readyz
{"status":"ready","foundry_endpoint":"https://<recurso>.openai.azure.com/"}   HTTP 200

(client) $ pip install -r requirements.txt   →  httpx 0.25.1, python-dotenv 1.0.0 (el cliente NO lleva openai)
(client) $ python main.py
Initializing client...
API Endpoint: http://<ip>
  ============================================================
  AKS Foundry Gateway API - Client Menu
  ============================================================
  1. Check API Health (Liveness)
  2. Check API Readiness (Foundry Connectivity)
  3. Send Inference Request
  4. Start Chat Session (Streaming)
  5. Exit
```
**Qué mirar:** `/healthz` = proceso vivo; `/readyz` = el pod llega a Foundry. El cliente solo habla con la API (HTTP); quien llama a `gpt-5.1` es el pod, con la identidad del kubelet y el rol *Cognitive Services OpenAI User*. **Nota:** el alumno confirma que las opciones 1-4 funcionan; solo se conserva la salida literal de la 4 (apartado 13). Verificado por nosotros: `curl /healthz` y `/readyz` (HTTP 200) y la opción 4 (ver apartado 13).

## 13. Cliente · opción 4 · Chat con streaming (llamada real a gpt-5.1)
```console
Select option (1-5): 4

[*] Starting chat session...
============================================================

You (type 'exit' to end): hoas del curso IA-200
Assistant: Te puedo ayudar, pero necesito un poco más de contexto.

¿A qué te refieres con “hoas del curso IA-200”? Puede ser, por ejemplo:
- ¿Apuntes/hojas de trabajo del curso IA-200?
- ¿Hojas de ejercicios o prácticas?
- ¿Hoja de datos / formulario de examen?
- ¿El temario (syllabus) del curso IA-200?
(…el modelo pide más contexto y ofrece ayuda…)
```
**Qué mirar:** el texto llega ya en `Assistant:` (streaming SSE desde `/v1/inference/stream`). Es la prueba end-to-end: cliente → LoadBalancer → pod → `gpt-5.1` en Foundry **sin ninguna clave** (identidad del kubelet + rol *Cognitive Services OpenAI User*). El prompt tenía una errata («hoas») y el modelo pidió aclaración: sin prompt de sistema, responde como asistente genérico.
