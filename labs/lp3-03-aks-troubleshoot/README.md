# Lab LP3-03 · Troubleshoot apps on AKS (plataforma: Lab 8 · AI-200-LP03M03)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html (índice en [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (03/11/2026): completado.** Despliegue base y las tres averías provocadas, diagnosticadas y corregidas, más la verificación final. Todo el `kubectl` por `az aks command invoke` (sin kubeconfig, sin `port-forward`, sin `kubectl edit`). **Cleanup no verificado:** el `az group delete` falló con `AuthorizationFailed` porque la plataforma ya había revocado las credenciales.
- Registro de la sesión: [`sesiones/2026-11-03-sesion-04-aks.md`](../../sesiones/2026-11-03-sesion-04-aks.md). Notas del módulo: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Cómo crea el script el ACR: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md).
- Lab anterior: [LP3-02](../lp3-02-aks-configure/README.md) · Lab siguiente: [LP4-01](../lp4-01-cosmos-queries/README.md). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: IDs, usuario y pase del lab fuera; hash de ACR/AKS como `<hash>`.

## Qué se construye
Una API mínima (`api/`, FastAPI) en el namespace `aks-troubleshoot`, con un Service `ClusterIP`, y tres manifiestos «rotos» a propósito que se aplican encima para romperla y arreglarla.

```
azdeploy.py 1 → grupo rg-ai200-aks-ts + ACR (y reescribe image: en los tres *-deployment.yaml)
azdeploy.py 2 → az acr build → aks-troubleshoot-api:latest
azdeploy.py 3 → AKS aks-<hash> (1 nodo Standard_D2s_v3, AcrPull)
az aks command invoke → namespace + api-deployment + api-service (ClusterIP)
avería 1  label-mismatch-service.yaml   → selector app=api-v2   → Service sin endpoints
avería 2  crashloop-deployment.yaml     → sin API_KEY           → CrashLoopBackOff
avería 3  probe-failure-deployment.yaml → readiness /invalid-path → pod 0/1, sin tráfico
```

**El objetivo, en cristiano:** practicar el **método** de diagnóstico, no memorizar arreglos. Orden: `get pods` (¿qué estado?) → `logs` (¿por qué muere el proceso?) → `describe` / `events` (¿qué hace Kubernetes?) → `endpointslices` (¿llega tráfico?). Para un SysOps de K8s esto es el día a día; lo propio del lab es hacerlo **sin acceso directo al API server**: todo por `az aks command invoke`.

### Diferencias respecto a la guía (por la plataforma y por el proxy)
| Guía | Aquí | Por qué |
|---|---|---|
| `Standard_D2s_v7`, región libre | `Standard_D2s_v3`, `eastus`, grupo `rg-ai200-aks-ts` | Lo pide la plataforma; el grupo es nuestro → se borra entero |
| Opciones 4 (credenciales), 5 (deploy) y 6 (estado) | **solo 1, 2 y 3** | Las 4-6 usan `kubectl` local, que el proxy bloquea |
| `kubectl port-forward` + `curl localhost` | `kubectl exec` en el pod contra `http://api-service/…` | El túnel va por el API server (bloqueado); además así se prueba el Service |
| `kubectl edit` | `kubectl patch` / `kubectl set env` | `edit` es interactivo y no funciona por `az aks command invoke` |
| `kubectl get pods -w` | repetir la consulta | Sin sesión interactiva |

---

## Paso 0 · Preparar la terminal
**Por qué:** CA del proxy para `az` en cada terminal nueva.
```bash
deactivate 2>/dev/null
cd ~/claude/AI-200-Developing/labs/lp3-03-aks-troubleshoot
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `echo $REQUESTS_CA_BUNDLE` → la ruta.

## Paso 1 · `az login` e inventario inicial
**Por qué:** suscripción nueva del lab 8; ver qué había antes (base del cleanup) y si hacen falta los `az provider register`.
```bash
az logout
az login --use-device-code
```
Salida real:
```text
[Tenant and subscription selection]

No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-<n>            <sub-id>                              Lab Directory

Tenant: Lab Directory
Subscription: XLabs-<n> (<sub-id>)
```
```bash
az group list --query "[].{n:name, r:location}" -o table
az provider list --query "[?namespace=='Microsoft.ContainerService'||namespace=='Microsoft.ContainerRegistry'||namespace=='Microsoft.Compute'||namespace=='Microsoft.Network'||namespace=='Microsoft.Storage'].{ns:namespace, estado:registrationState}" -o table
```
Salida real:
```text
N               R
--------------  ------
AZ801-L0501-RG  eastus
Microsoft.ContainerService   Registered
Microsoft.Compute            Registered
Microsoft.Network            Registered
Microsoft.Storage            Registered
Microsoft.ContainerRegistry  Registered
```
**Qué mirar:** solo `AZ801-L0501-RG` (de otro curso de la plataforma: **no se toca**) y los cinco proveedores ya registrados.

✅ **Comprobación:** `az account show --query name -o tsv` debe dar una suscripción distinta de la de LP3-02. Proveedor `NotRegistered` → `az provider register --namespace <ns>`.

## Paso 2 · Valores de `azdeploy.py`
**Por qué:** grupo propio, región y VM de la plataforma.
```bash
sed -i 's|<your-resource-group-name>|rg-ai200-aks-ts|; s|<your-azure-region>|eastus|; s|"Standard_D2s_v7"|"Standard_D2s_v3"|' azdeploy.py
grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py
```
Salida real:
```text
5:rg = "rg-ai200-aks-ts"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
9:AKS_VM_SIZE = "Standard_D2s_v3"
```
✅ **Comprobación:** las tres líneas así; si no, edita las líneas 5, 6 y 9 a mano.

## Paso 3 · Menú: opciones 1, 2 y 3 (no la 4, 5 ni 6)
**Por qué:** 1 crea grupo + ACR y **reescribe `image:` en los tres `*-deployment.yaml`** (base y averías); 2 construye la imagen en la nube; 3 crea el AKS con `AcrPull`. Lánzalas seguidas sin salir del menú.
```bash
python3 azdeploy.py      # 1 → Enter → 2 → Enter → 3
```
Salida real:
```text
Checking/creating resource group 'rg-ai200-aks-ts'...
Resource group created: rg-ai200-aks-ts

Creating Azure Container Registry 'acr<hash>'...
ACR created: acr<hash>
ACR endpoint: acr<hash>.azurecr.io
Updating deployment YAML files with the ACR image reference...
Deployment YAML files updated

Building and pushing API image to ACR...
Image built and pushed: acr<hash>.azurecr.io/aks-troubleshoot-api:latest

Creating AKS cluster 'aks-<hash>' with one Standard_D2s_v3 node...
This may take 5-10 minutes to complete. Please wait...
```
✅ **Comprobación** (salida real):
```bash
RG=rg-ai200-aks-ts; AKS=aks-<hash>; ACR=acr<hash>
az acr repository show-tags -n $ACR --repository aks-troubleshoot-api -o tsv
az aks show -g $RG -n $AKS --query provisioningState -o tsv
grep -n "image:" k8s/*.yaml
```
```text
latest
Succeeded
k8s/crashloop-deployment.yaml:19:        image: acr<hash>.azurecr.io/aks-troubleshoot-api:latest
k8s/probe-failure-deployment.yaml:19:        image: acr<hash>.azurecr.io/aks-troubleshoot-api:latest
k8s/api-deployment.yaml:19:        image: acr<hash>.azurecr.io/aks-troubleshoot-api:latest
```
**Qué mirar:** imagen con tag `latest`, AKS `Succeeded` y los tres YAML apuntando a tu ACR (en el repo están con `<YOUR_ACR_ENDPOINT>`: si no lanzas la opción 1, sustitúyelo con `sed -i "s|<YOUR_ACR_ENDPOINT>|$ACR.azurecr.io|" k8s/*-deployment.yaml`). AKS `Failed` → opción 7 (borrar AKS fallido) y repetir la 3 con `D2s_v5`.

## Paso 4 · Comprobar el permiso de pull (AcrPull del kubelet)
**Por qué:** sin `--admin-enabled` ni `imagePullSecrets`, el nodo baja la imagen con **su identidad**. Desplegar (tu rol sobre el cluster) y descargar (el rol del kubelet sobre el registro) son permisos distintos.
```bash
K=$(az aks show -g $RG -n $AKS --query identityProfile.kubeletidentity.objectId -o tsv)
az role assignment list --assignee $K --all --query "[].{rol:roleDefinitionName, ambito:scope}" -o tsv | sed -E 's|/subscriptions/[0-9a-f-]+|/subscriptions/<sub-id>|'
```
Salida real:
```text
AcrPull  /subscriptions/<sub-id>/resourceGroups/rg-ai200-aks-ts/providers/Microsoft.ContainerRegistry/registries/acr<hash>
```
**Qué mirar:** un solo rol, `AcrPull`, acotado a **ese** ACR (lo dio `--attach-acr`).

✅ **Comprobación:** si falta, `az aks update -g $RG -n $AKS --attach-acr $ACR`. Si faltara, el síntoma sería `ImagePullBackOff` con `401 unauthorized` en el `describe pod`.

## Paso 5 · Task 2: desplegar la app base
**Por qué:** sustituye a la opción 5 del menú (que haría lo mismo con `kubectl` local).
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl create namespace aks-troubleshoot; kubectl apply -f api-deployment.yaml -f api-service.yaml -n aks-troubleshoot; kubectl rollout status deployment/api-deployment -n aks-troubleshoot --timeout=120s" \
  --file k8s/api-deployment.yaml --file k8s/api-service.yaml
```
Salida real:
```text
command started at 2026-11-03 20:15:43+00:00, finished at 2026-11-03 20:16:03+00:00 with exitcode=0
namespace/aks-troubleshoot created
deployment.apps/api-deployment created
service/api-service created
Waiting for deployment "api-deployment" rollout to finish: 0 of 1 updated replicas are available...
deployment "api-deployment" successfully rolled out
```
> **Alternativa local, solo sin proxy:** opciones 4 y 5 del menú (`get-credentials` + `kubectl apply`). No es la primera opción porque en el PC de empresa `kubectl` contra AKS falla (`x509` / `502 IncompleteCertChain`, LP3-01 paso 12).

✅ **Comprobación:** paso 6. Si el namespace ya existe, `create namespace` da `AlreadyExists` y el resto sigue: no pasa nada.

## Paso 6 · Verificar la app base sin `port-forward` (la referencia «sana»)
**Por qué:** el Service es `ClusterIP` (sin IP pública) y `port-forward` va por el API server, bloqueado. Se llama desde **dentro** del pod al **nombre del Service**: así se prueba DNS + selector + endpoints, justo lo que rompe la avería 1. El contenedor trae Python, no `curl`.
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl get pods -n aks-troubleshoot --show-labels; kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot; kubectl exec deploy/api-deployment -n aks-troubleshoot -- python -c \"import urllib.request;print(urllib.request.urlopen('http://api-service/healthz').read().decode())\""
```
Salida real (ejecutada por Claude, solo lectura):
```text
command started at 2026-11-03 20:18:40+00:00, finished at 2026-11-03 20:18:42+00:00 with exitcode=0
NAME                             READY   STATUS    RESTARTS   AGE     LABELS
api-deployment-89bf79f9c-xrkpb   1/1     Running   0          2m55s   app=api,pod-template-hash=89bf79f9c,…
NAME                ADDRESSTYPE   PORTS   ENDPOINTS     AGE
api-service-gw997   IPv4          8000    10.224.0.10   2m56s
{"status":"healthy","timestamp":"2026-11-03T20:18:42.255800"}
```
**Qué mirar:** pod `1/1`, etiqueta `app=api`, la EndpointSlice con la IP del pod (`10.224.0.10:8000`) y `healthy` **a través del Service**. Apunta el `pod-template-hash` (`89bf79f9c`): reaparece en la avería 2.

✅ **Comprobación:** si el `exec` falla con conexión rechazada, el Service no enruta: mira el selector (`kubectl describe service api-service -n aks-troubleshoot`).

---

## Paso 7 · Avería 1: selector del Service que no casa con las etiquetas
**Por qué:** fallo **silencioso**: el pod está sano y el Service existe, pero no hay tráfico. `label-mismatch-service.yaml` cambia el selector a `app: api-v2`; los pods llevan `app: api`.

**7.1 Provocar**
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl apply -f label-mismatch-service.yaml -n aks-troubleshoot" \
  --file k8s/label-mismatch-service.yaml
```
Salida real:
```text
bash: error de sintaxis cerca del elemento inesperado `('
command started at 2026-11-03 20:19:34+00:00, finished at 2026-11-03 20:19:36+00:00 with exitcode=0
service/api-service configured
```
⚠️ **Lo que pasó:** el error de `bash` viene de haber pegado también el título del bloque («1. Provoca la avería (…)»); bash lo leyó como comando. No afectó: el `apply` se ejecutó. Copia solo el contenido de los bloques de código.

**7.2 Diagnosticar** (solo lectura)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl get pods --show-labels -n aks-troubleshoot; kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot; kubectl describe service api-service -n aks-troubleshoot"
```
Salida real (recortada):
```text
NAME                             READY   STATUS    RESTARTS   AGE     LABELS
api-deployment-89bf79f9c-xrkpb   1/1     Running   0          4m17s   app=api,pod-template-hash=89bf79f9c,…
NAME                ADDRESSTYPE   PORTS     ENDPOINTS   AGE
api-service-gw997   IPv4          <unset>   <unset>     4m18s
Name:                     api-service
Namespace:                aks-troubleshoot
Labels:                   app=api
Selector:                 app=api-v2
Type:                     ClusterIP
IP:                       10.0.13.112
Port:                     http  80/TCP
TargetPort:               8000/TCP
Endpoints:
```
**Qué mirar:** pod `1/1 Running` con `app=api` + EndpointSlice `<unset>` + `Selector: app=api-v2` + `Endpoints:` vacío = **el selector no casa con las etiquetas**. No es problema del pod. Regla: comparar siempre `--show-labels` del pod con el `Selector` del Service.

**7.3 Corregir** (la guía usa `kubectl edit service`; por `az` se hace con `patch`)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl patch service api-service -n aks-troubleshoot -p '{\"spec\":{\"selector\":{\"app\":\"api\"}}}'"
```
Salida real:
```text
command started at 2026-11-03 20:21:17+00:00, finished at 2026-11-03 20:21:17+00:00 with exitcode=0
service/api-service patched (no change)
```
⚠️ **Lo que pasó:** `(no change)` porque ya se había lanzado un primer `patch` a las 20:20:20 que corrigió el selector; este segundo no tenía nada que cambiar (un `patch` con el mismo valor es idempotente). Se vio así:
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl get svc api-service -n aks-troubleshoot -o jsonpath='{.spec.selector}{\"\n\"}'; kubectl get svc api-service -n aks-troubleshoot --show-managed-fields -o jsonpath='{range .metadata.managedFields[*]}{.manager}{\" | \"}{.operation}{\" | \"}{.time}{\"\n\"}{end}'"
```
```text
{"app":"api"}
kubectl-client-side-apply | Update | 2026-11-03T20:19:36Z
kubectl-patch | Update | 2026-11-03T20:20:20Z
```
`managedFields` registra **quién** cambió el objeto y **cuándo**: útil cuando algo cambia «solo».

**7.4 Comprobar** (solo lectura)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot; kubectl exec deploy/api-deployment -n aks-troubleshoot -- python -c \"import urllib.request;print(urllib.request.urlopen('http://api-service/healthz').read().decode())\""
```
Salida real:
```text
command started at 2026-11-03 20:21:30+00:00, finished at 2026-11-03 20:21:31+00:00 with exitcode=0
NAME                ADDRESSTYPE   PORTS   ENDPOINTS     AGE
api-service-gw997   IPv4          8000    10.224.0.10   5m45s
{"status":"healthy","timestamp":"2026-11-03T20:21:31.934113"}
```
✅ **Comprobación:** vuelve la IP del pod y `healthy`. Si la EndpointSlice sigue vacía, repite el `describe service` y mira el `Selector`.

## Paso 8 · Avería 2: `CrashLoopBackOff` por falta de `API_KEY`
**Por qué:** `crashloop-deployment.yaml` solo comenta el bloque `env` con `API_KEY`. La app hace `logger.error("FATAL: API_KEY environment variable is not set. Exiting.")` y `sys.exit(1)`; Kubernetes la reinicia con esperas crecientes (`BackOff`). Aquí se aprenden **dos trampas** reales, por eso hubo tres intentos.

**8.1 Primer intento: diagnóstico demasiado pronto y del pod equivocado**
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl apply -f crashloop-deployment.yaml -n aks-troubleshoot" --file k8s/crashloop-deployment.yaml
az aks command invoke -g $RG -n $AKS --command "kubectl get pods -n aks-troubleshoot; kubectl logs -l app=api -n aks-troubleshoot --tail=20; kubectl describe pod -l app=api -n aks-troubleshoot | tail -25"
```
Salida real (recortada):
```text
deployment.apps/api-deployment configured
NAME                              READY   STATUS    RESTARTS   AGE
api-deployment-764b8b88b9-q6lx2   0/1     Running   0          8s
api-deployment-89bf79f9c-xrkpb    1/1     Running   0          8m54s
INFO:     10.224.0.4:53468 - "GET /healthz HTTP/1.1" 200 OK
…
  Normal  Started    8m49s  kubelet  spec.containers{api}: Container started
```
⚠️ **Lo que pasó:** a los **8 s** el pod nuevo aún no había fallado, y `-l app=api` selecciona **los dos pods** del rolling update: los `logs` y el `describe` eran del pod **antiguo** y sano. Después se arregló con `set env API_KEY=…` (`env updated`, `successfully rolled out`) y quedó solo el pod antiguo (`89bf79f9c`, 9 min): la plantilla volvió a ser idéntica a la original, así que Kubernetes **reutilizó el ReplicaSet antiguo** (mismo `pod-template-hash`), como en un rollback.

**8.2 Segundo intento: `apply` no deshace lo que hizo un comando imperativo**
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl apply -f crashloop-deployment.yaml -n aks-troubleshoot" --file k8s/crashloop-deployment.yaml
```
Salida real:
```text
deployment.apps/api-deployment unchanged
```
(y el `set env API_KEY=…` posterior devolvió `None`: no había nada que cambiar; `kubectl get rs` mostró `764b8b88b9` a 0 y `89bf79f9c` a 1).

⚠️ **Lo que pasó:** `apply` solo quita campos que **él mismo** aplicó (anotación `last-applied-configuration`). `API_KEY` la había puesto `set env`, así que el `apply` del YAML sin `env` no la borra → `unchanged`. **Moraleja:** no mezclar `apply` con comandos imperativos sobre el mismo objeto.

**8.3 Provocar de verdad: quitar la variable explícitamente**
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl set env deployment/api-deployment API_KEY- -n aks-troubleshoot"
```
Salida real:
```text
command started at 2026-11-03 20:30:37+00:00, finished at 2026-11-03 20:30:38+00:00 with exitcode=0
deployment.apps/api-deployment env updated
```
El `-` final **elimina** la variable.

**8.4 Diagnosticar el pod más reciente** (solo lectura; espera 60 s)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl get pods -n aks-troubleshoot --sort-by=.metadata.creationTimestamp; P=\$(kubectl get pods -n aks-troubleshoot --sort-by=.metadata.creationTimestamp -o name | tail -1); echo POD=\$P; kubectl logs \$P -n aks-troubleshoot --tail=10; kubectl describe \$P -n aks-troubleshoot | grep -E 'State|Reason|Exit Code|Restart Count|Back-off'"
```
Salida real:
```text
command started at 2026-11-03 20:30:49+00:00, finished at 2026-11-03 20:30:51+00:00 with exitcode=0
NAME                              READY   STATUS    RESTARTS     AGE
api-deployment-89bf79f9c-xrkpb    1/1     Running   0            15m
api-deployment-764b8b88b9-zm2g6   0/1     Running   1 (6s ago)   12s
POD=pod/api-deployment-764b8b88b9-zm2g6
2026-11-03 20:30:48,645 - ERROR - FATAL: API_KEY environment variable is not set. Exiting.
    State:          Terminated
      Reason:       Error
      Exit Code:    1
    Last State:     Terminated
      Reason:       Error
      Exit Code:    1
    Restart Count:  1
  Warning  BackOff    1s    kubelet    spec.containers{api}: Back-off restarting failed container api in pod api-deployment-764b8b88b9-zm2g6_aks-troubleshoot(<uid>)
```
**Qué mirar:** `logs` dice **por qué** muere (`FATAL: API_KEY …`); `describe` dice **qué hace Kubernetes** (`Exit Code: 1`, `Restart Count` subiendo, `Back-off`). Con unos minutos más el `STATUS` pasa a `CrashLoopBackOff`. El pod antiguo siguió `1/1` todo el rato: el rolling update no retira el viejo hasta que el nuevo está `Ready`, **el servicio no cae**.

**8.5 Corregir y comprobar** (la guía usa `kubectl edit deployment`)
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl set env deployment/api-deployment API_KEY=demo-api-key-12345 -n aks-troubleshoot"
az aks command invoke -g $RG -n $AKS --command "kubectl rollout status deployment/api-deployment -n aks-troubleshoot --timeout=120s; kubectl get pods -n aks-troubleshoot"
```
Salida real:
```text
deployment.apps/api-deployment env updated
deployment "api-deployment" successfully rolled out
NAME                             READY   STATUS    RESTARTS   AGE
api-deployment-89bf79f9c-xrkpb   1/1     Running   0          15m
```
✅ **Comprobación:** `successfully rolled out` y un pod `1/1`. Que sea el de 15 min es normal (ReplicaSet reutilizado; `kubectl get rs` lo muestra). En una app real la clave iría en un **Secret** (`secretKeyRef`, como en LP3-02), no en claro con `set env`.

## Paso 9 · Avería 3: readiness probe con ruta inválida
**Por qué:** `probe-failure-deployment.yaml` solo cambia la ruta de la readiness a `/invalid-path`. El proceso está vivo pero la sonda recibe 404: el pod queda **no listo** y fuera del Service. A diferencia de la avería 2, **no se reinicia** (eso lo haría la liveness).

**9.1 Provocar**
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl apply -f probe-failure-deployment.yaml -n aks-troubleshoot" --file k8s/probe-failure-deployment.yaml
```
Salida real:
```text
command started at 2026-11-03 20:32:50+00:00, finished at 2026-11-03 20:32:52+00:00 with exitcode=0
deployment.apps/api-deployment configured
```
`configured` (no `unchanged`): aquí `apply` sí cambia algo, porque la ruta está en los dos manifiestos.

**9.2 Diagnosticar** (solo lectura; mejor tras 60 s)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl get pods -n aks-troubleshoot --sort-by=.metadata.creationTimestamp; kubectl get events -n aks-troubleshoot --field-selector reason=Unhealthy; kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot"
```
Salida real (a los 9 s):
```text
NAME                              READY   STATUS    RESTARTS   AGE
api-deployment-89bf79f9c-xrkpb    1/1     Running   0          17m
api-deployment-5b564445f8-76rqs   0/1     Running   0          9s
No resources found in aks-troubleshoot namespace.
NAME                ADDRESSTYPE   PORTS   ENDPOINTS                 AGE
api-service-gw997   IPv4          8000    10.224.0.10,10.224.0.19   17m
```
⚠️ **Lo que pasó:** a los 9 s aún no había evento `Unhealthy` (la sonda empieza tras `initialDelaySeconds`). Y la tabla de EndpointSlices lista **también la IP del pod no listo** (`10.224.0.19`): no indica si está listo. La señal real es `conditions.ready` (ver 9.5).

**9.3 Confirmar la ruta**
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl get deploy api-deployment -n aks-troubleshoot -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet}{\"\n\"}'"
```
Salida real:
```text
{"path":"/invalid-path","port":8000,"scheme":"HTTP"}
```

**9.4 Corregir** (la guía usa `kubectl edit`; aquí `patch` JSON sobre ese campo)
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl patch deployment api-deployment -n aks-troubleshoot --type=json -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/readinessProbe/httpGet/path\",\"value\":\"/healthz\"}]'"
```
Salida real:
```text
command started at 2026-11-03 20:33:23+00:00, finished at 2026-11-03 20:33:24+00:00 with exitcode=0
deployment.apps/api-deployment patched
```

**9.5 Comprobar** (solo lectura)
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl rollout status deployment/api-deployment -n aks-troubleshoot --timeout=120s; kubectl get pods -n aks-troubleshoot; kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot -o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]}{\" ready=\"}{.conditions.ready}{\"\n\"}{end}'; kubectl get deploy api-deployment -n aks-troubleshoot -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}{\"\n\"}'; kubectl get events -n aks-troubleshoot --field-selector reason=Unhealthy --no-headers | tail -3"
```
Salida real (ejecutada por Claude: el comando del alumno se cortó con `^C` por una comilla sin cerrar):
```text
deployment "api-deployment" successfully rolled out
NAME                             READY   STATUS    RESTARTS   AGE
api-deployment-89bf79f9c-xrkpb   1/1     Running   0          19m
10.224.0.10 ready=true
/healthz
104s   Warning   Unhealthy   pod/api-deployment-5b564445f8-76rqs   Readiness probe failed: HTTP probe failed with statuscode: 404
```
**Qué mirar:** el evento que no salía a los 9 s (`Readiness probe failed … 404`), la ruta ya en `/healthz` y el endpoint `ready=true`. `RESTARTS 0` durante toda la avería: readiness fallida no mata, solo saca del Service.

✅ **Comprobación:** `successfully rolled out`, un pod `1/1` y `ready=true`. Si un comando largo se queda con el prompt `>`, falta cerrar una comilla: `Ctrl+C` y vuelve a pegarlo entero.

## Paso 10 · Verificación final de extremo a extremo
**Por qué:** la guía repite `port-forward` + `curl` de `/healthz`, `/readyz` y `/api/info`; aquí, desde el pod contra el Service, y con los logs para ver que llegan las peticiones.
```bash
az aks command invoke -g $RG -n $AKS \
  --command "for p in healthz readyz api/info; do echo == /\$p; kubectl exec deploy/api-deployment -n aks-troubleshoot -- python -c \"import urllib.request;print(urllib.request.urlopen('http://api-service/\$p').read().decode())\"; done; kubectl logs -l app=api -n aks-troubleshoot --tail=5"
```
Salida real:
```text
command started at 2026-11-03 20:36:07+00:00, finished at 2026-11-03 20:36:11+00:00 with exitcode=0
== /healthz
{"status":"healthy","timestamp":"2026-11-03T20:36:08.655651"}
== /readyz
{"status":"ready","timestamp":"2026-11-03T20:36:09.847442"}
== /api/info
{"app":"Troubleshoot API","version":"1.0.0","startup_time":"2026-11-03T20:15:54.752382","api_key_configured":true,"message":"Application is running correctly!"}
INFO:     10.224.0.4:55302 - "GET /healthz HTTP/1.1" 200 OK
2026-11-03 20:36:09,847 - INFO - GET /readyz - Readiness check requested
INFO:     10.224.0.4:3332 - "GET /readyz HTTP/1.1" 200 OK
2026-11-03 20:36:10,956 - INFO - GET /api/info - Info requested
INFO:     10.224.0.4:12121 - "GET /api/info HTTP/1.1" 200 OK
```
**Qué mirar:** las tres rutas responden y `api_key_configured: true`; el `startup_time` (20:15:54) confirma que es el pod del despliegue base, reutilizado tras las averías.

✅ **Comprobación:** tres JSON y líneas `200 OK`. Un 404 o error de conexión = alguna avería sigue: vuelve a los pasos 7.4, 8.5 o 9.5.

---

## Cleanup (obligatorio al acabar)
**Por qué `az group delete` aquí sí:** `rg-ai200-aks-ts` lo creó el script; contiene solo el ACR y el AKS (el `MC_…` se va con el AKS). `AZ801-L0501-RG` y `NetworkWatcherRG` no son nuestros.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az account show --query name -o tsv
az group list --query "[].name" -o tsv
az resource list -g rg-ai200-aks-ts --query "[].{n:name,t:type}" -o tsv
```
Salida real (20:38):
```text
XLabs-<n>
AZ801-L0501-RG
rg-ai200-aks-ts
MC_rg-ai200-aks-ts_aks-<hash>_eastus
NetworkWatcherRG
acr<hash>    Microsoft.ContainerRegistry/registries
aks-<hash>   Microsoft.ContainerService/managedClusters
```
```bash
az group delete --name rg-ai200-aks-ts --no-wait --yes
az group exists --name rg-ai200-aks-ts
```
Salida real:
```text
Code: AuthorizationFailed
Message: The client '<usuario>' with object id '<id>' does not have authorization to perform action 'Microsoft.Resources/subscriptions/resourcegroups/delete' over scope '/subscriptions/<sub-id>/resourcegroups/rg-ai200-aks-ts' or the scope is invalid. If access was recently granted, please refresh your credentials.
ERROR: Operation returned an invalid status 'Forbidden'
```
**Resultado: no verificado.** Las lecturas (`az group show`) también daban 403: la plataforma había revocado las credenciales entre las 20:38 (inventario OK) y el borrado. La plataforma desprovisiona el entorno, pero no se pudo comprobar. (El borrado lo lanzó Claude con el OK del alumno.)

✅ **Esperado si se repite a tiempo:** `exists` = `true` mientras borra y `false` al terminar; `az group list` sin `rg-ai200-*` ni `MC_rg-ai200-*`. Si sale `AuthorizationFailed` y la sesión del lab sigue activa, pide un pase nuevo, `az login --use-device-code` y repite. **Lección:** lanzar el cleanup **en cuanto termina el lab**, antes de documentar.

Local: con `az aks command invoke` no se crea kubeconfig, no hay contexto que limpiar. Al cierre del día: `az logout` y `az account clear` (0 cuentas).

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `bash: error de sintaxis cerca de '('` | Se pegó el título del bloque como comando | Copiar solo el bloque de código (7.1) |
| `patch … (no change)` | Un `patch` anterior ya había corregido el selector | `--show-managed-fields` muestra quién y cuándo (7.3) |
| Avería 2 sin `CrashLoopBackOff` (1.er intento) | Diagnóstico a los 8 s; `-l app=api` mezcla pod viejo y nuevo | Esperar 60 s y mirar el pod más reciente (`--sort-by`) (8.4) |
| `apply … unchanged` y `set env … None` | `apply` solo quita lo que él aplicó (`last-applied`); `API_KEY` la puso `set env` | No mezclar `apply` e imperativos; `set env API_KEY-` (8.3) |
| El pod «arreglado» tiene 15-19 min | Plantilla idéntica a la original → ReplicaSet reutilizado | Normal; `kubectl get rs` (8.1) |
| `get endpointslices` lista la IP de un pod `0/1` | La tabla no enseña si está listo | `conditions.ready` con `jsonpath` (9.5) |
| Sin evento `Unhealthy` a los 9 s | `initialDelaySeconds` de la sonda | Esperar y repetir (9.2) |
| Prompt `>` tras pegar un comando | Comilla sin cerrar | `Ctrl+C` y pegar entero (9.5) |
| `AuthorizationFailed` en el cleanup | Credenciales del lab revocadas | Cleanup inmediato; consta como no verificado |

## Las tres averías de un vistazo (para el examen)
| Avería | Síntoma | Dónde se ve | Causa | Corrección |
|---|---|---|---|---|
| 1. Etiquetas | Pod `Running`, Service sin endpoints | `describe service` (`Selector`), `endpointslices` | `app=api-v2` ≠ `app=api` | `patch` del selector |
| 2. Crash | `CrashLoopBackOff`, `RESTARTS` sube | `logs` (`FATAL`), `describe` (`Exit Code 1`, `Back-off`) | Falta `API_KEY` | `set env API_KEY=…` |
| 3. Readiness | `0/1 Running`, `RESTARTS 0` | `events` (`Unhealthy` 404), `conditions.ready` | Ruta `/invalid-path` | `patch` JSON de la ruta |

Otras parecidas: puerto mal (`targetPort` ≠ `containerPort`: endpoints con IP pero sin respuesta) e `ImagePullBackOff` (imagen/tag o `AcrPull`, paso 4).
