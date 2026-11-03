# Salidas reales · LP3-03 Troubleshoot apps on AKS

Saneadas: sin ID de suscripción, tenant, usuario ni Temporary Access Pass; hash de ACR/AKS como `<hash>`. Ejecutado el 03/11/2026 en Linux. Todo el `kubectl` va por `az aks command invoke` (el proxy de empresa bloquea el API server). El grupo `rg-ai200-aks-ts` es **nuestro**.

## 1. Estado inicial y valores de `azdeploy.py`
Suscripción nueva (`XLabs-<n>`), proveedores ya `Registered`; solo existía `AZ801-L0501-RG` (de otro curso, no se toca).
```console
$ grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py
5:rg = "rg-ai200-aks-ts"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
9:AKS_VM_SIZE = "Standard_D2s_v3"
```
**Qué mirar:** el starter trae `Standard_D2s_v7`; la plataforma pide `v3` y `eastus`.

## 2. Opciones 1, 2 y 3 del menú (la 4, 5 y 6 usan `kubectl` local: no se lanzan)
```console
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
```
```console
$ az acr repository show-tags -n acr<hash> --repository aks-troubleshoot-api -o tsv
latest
$ az aks show -g rg-ai200-aks-ts -n aks-<hash> --query provisioningState -o tsv
Succeeded
$ az role assignment list --assignee <kubelet> --all --query "[].{rol:roleDefinitionName, ambito:scope}" -o tsv
AcrPull  /subscriptions/<id>/resourceGroups/rg-ai200-aks-ts/providers/Microsoft.ContainerRegistry/registries/acr<hash>
```
**Qué mirar:** la opción 1 reescribe `image:` de los **tres** `*-deployment.yaml`; el kubelet tiene `AcrPull` solo sobre ese ACR (así descarga sin credenciales).

## 3. Task 2 · despliegue base y verificación (sin `port-forward`)
```console
$ az aks command invoke … --command "kubectl create namespace aks-troubleshoot; kubectl apply -f api-deployment.yaml -f api-service.yaml -n aks-troubleshoot; kubectl rollout status deployment/api-deployment -n aks-troubleshoot --timeout=120s" --file k8s/api-deployment.yaml --file k8s/api-service.yaml
exitcode=0
namespace/aks-troubleshoot created
deployment.apps/api-deployment created
service/api-service created
deployment "api-deployment" successfully rolled out

$ … --command "kubectl get pods -n aks-troubleshoot --show-labels; kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot; kubectl exec deploy/api-deployment -n aks-troubleshoot -- python -c \"import urllib.request;print(urllib.request.urlopen('http://api-service/healthz').read().decode())\""
api-deployment-89bf79f9c-…   1/1   Running   0   2m55s   app=api,…
api-service-…   IPv4   8000   10.224.0.10
{"status":"healthy","timestamp":"…"}
```
**Qué mirar:** el Service es `ClusterIP`, por eso no hay IP pública: se prueba con `kubectl exec` desde el pod contra el **nombre del Service** (`http://api-service/healthz`), que también valida el selector.

## 4. Escenario 1 · selector del Service que no casa con las etiquetas
```console
$ … --command "kubectl apply -f label-mismatch-service.yaml -n aks-troubleshoot" --file k8s/label-mismatch-service.yaml
service/api-service configured

$ … --command "kubectl get pods --show-labels -n aks-troubleshoot; kubectl get endpointslices …; kubectl describe service api-service -n aks-troubleshoot"
api-deployment-89bf79f9c-…   1/1   Running   0   4m17s   app=api,…
api-service-…   IPv4   <unset>   <unset>
Selector:                 app=api-v2
Endpoints:                

$ … --command "kubectl patch service api-service -n aks-troubleshoot -p '{\"spec\":{\"selector\":{\"app\":\"api\"}}}'"
service/api-service patched (no change)

$ … endpointslice + exec /healthz
api-service-…   IPv4   8000   10.224.0.10
{"status":"healthy",…}
```
**Qué mirar:** pod `Running` + Service sin endpoints + `Selector` ≠ etiqueta del pod = selector erróneo (no es problema del pod). El `patch` dijo `(no change)` porque un primer `patch` (20:20:20) ya había corregido el selector: `kubectl get svc … --show-managed-fields` muestra los dos escritores (`kubectl-client-side-apply` y `kubectl-patch`) con su hora.

## 5. Escenario 2 · CrashLoopBackOff
### Primer intento (no reprodujo el fallo)
```console
$ … apply crashloop-deployment.yaml   →  deployment.apps/api-deployment configured
$ … get pods; logs -l app=api; describe pod -l app=api | tail -25
api-deployment-764b8b88b9-q6lx2   0/1   Running   0   8s
api-deployment-89bf79f9c-xrkpb    1/1   Running   0   8m54s
(logs: GET /healthz 200 OK … → eran los del pod ANTIGUO)
$ … kubectl set env deployment/api-deployment API_KEY=demo-api-key-12345   →  deployment.apps/api-deployment env updated
```
**Qué mirar:** a los 8 s el pod nuevo aún no había fallado y `-l app=api` selecciona **dos pods** durante un rolling update: se estaba leyendo el pod sano. Además, `set env` dejó la plantilla idéntica a la original y Kubernetes **reutilizó el ReplicaSet antiguo** (por eso el pod final tenía 9 minutos).

### Segundo intento (trampa de `apply` + comandos imperativos)
```console
$ … apply crashloop-deployment.yaml   →  deployment.apps/api-deployment unchanged
$ … set env … API_KEY=…               →  None   (ya existía: no hay nada que cambiar)
```
**Qué mirar:** `unchanged` porque el `apply` solo elimina campos que él mismo aplicó (anotación `last-applied`); `API_KEY` lo puso `set env` y el `apply` no lo toca. Moraleja: no mezclar `apply` con comandos imperativos.

### Tercer intento (correcto): quitar la variable explícitamente
```console
$ … --command "kubectl set env deployment/api-deployment API_KEY- -n aks-troubleshoot"
deployment.apps/api-deployment env updated

$ … get pods --sort-by=.metadata.creationTimestamp; logs del pod más reciente; describe | grep …
api-deployment-89bf79f9c-xrkpb    1/1   Running   0            15m
api-deployment-764b8b88b9-zm2g6   0/1   Running   1 (6s ago)   12s
2026-11-03 20:30:48,645 - ERROR - FATAL: API_KEY environment variable is not set. Exiting.
    State:          Terminated
      Reason:       Error
      Exit Code:    1
    Restart Count:  1
  Warning  BackOff    1s    kubelet    Back-off restarting failed container api in pod api-deployment-764b8b88b9-zm2g6_aks-troubleshoot(…)

$ … kubectl set env deployment/api-deployment API_KEY=demo-api-key-12345  →  env updated
$ … rollout status; get pods
deployment "api-deployment" successfully rolled out
api-deployment-89bf79f9c-xrkpb   1/1   Running   0   15m
```
**Qué mirar:** `logs` del pod nuevo (`FATAL: API_KEY … Exiting.`) y `describe` (`Exit Code 1`, `Back-off`). El pod antiguo siguió `1/1 Running` todo el tiempo: el rolling update no retira el viejo hasta que el nuevo esté `Ready`.

## 6. Escenario 3 · readiness probe con ruta inválida
```console
$ … apply probe-failure-deployment.yaml   →  deployment.apps/api-deployment configured
$ … get pods; get events --field-selector reason=Unhealthy; get endpointslices …
api-deployment-89bf79f9c-xrkpb    1/1   Running   0   17m
api-deployment-5b564445f8-76rqs   0/1   Running   0   9s
No resources found in aks-troubleshoot namespace.
api-service-…   IPv4   8000   10.224.0.10,10.224.0.19

$ … get deploy api-deployment -o jsonpath='{…readinessProbe.httpGet}'
{"path":"/invalid-path","port":8000,"scheme":"HTTP"}

$ … kubectl patch deployment api-deployment -n aks-troubleshoot --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/healthz"}]'
deployment.apps/api-deployment patched

$ … rollout status; get pods; endpointslice ready; path; events (comprobación posterior)
deployment "api-deployment" successfully rolled out
api-deployment-89bf79f9c-xrkpb   1/1   Running   0   19m
10.224.0.10 ready=true
/healthz
104s   Warning   Unhealthy   pod/api-deployment-5b564445f8-76rqs   Readiness probe failed: HTTP probe failed with statuscode: 404
```
**Qué mirar:** `RESTARTS 0` (no es un crash); el pod queda `0/1`; el evento `Unhealthy` con `404` aparece tras el `initialDelaySeconds` (a los 9 s «No resources found»). **Ojo:** `kubectl get endpointslices` lista **también las IP de pods no listos** (`10.224.0.19`); la señal real es `conditions.ready` (`-o jsonpath='{range .items[0].endpoints[*]}{.addresses[0]} ready={.conditions.ready}{"\n"}{end}'`).

## 7. Verificación end-to-end
```console
$ … for p in healthz readyz api/info; do … kubectl exec deploy/api-deployment … urlopen('http://api-service/$p') …; done; kubectl logs -l app=api --tail=5
== /healthz   {"status":"healthy","timestamp":"…"}
== /readyz    {"status":"ready","timestamp":"…"}
== /api/info  {"app":"Troubleshoot API","version":"1.0.0","startup_time":"…","api_key_configured":true,"message":"Application is running correctly!"}
INFO:  10.224.0.4:… - "GET /healthz HTTP/1.1" 200 OK  (y /readyz, /api/info)
```
**Qué mirar:** las tres rutas responden y `api_key_configured` es `true`: las tres averías están corregidas.
