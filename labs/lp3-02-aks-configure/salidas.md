# Salidas reales · LP3-02 Configure apps on AKS

Saneadas: sin ID de suscripción, tenant, usuario ni Temporary Access Pass; el hash de ACR/AKS como `<hash>`; IP pública como `<ip>`. Ejecutado el 03/11/2026 en Linux. En este lab el grupo `rg-ai200-aks-cfg` es **nuestro** (lo crea el script), a diferencia del lab 6.

## 1. Estado inicial de la suscripción nueva
```console
$ az group list -o table
(sin filas)
$ az provider list --query "[?namespace=='Microsoft.ContainerService'||…].{ns:namespace, estado:registrationState}" -o table
Microsoft.ContainerRegistry  Registered
Microsoft.ContainerService   Registered
Microsoft.Compute            Registered
Microsoft.Storage            Registered
Microsoft.Network            Registered
$ az vm list-skus -l eastus --size Standard_D2s_v3 …   →  Standard_D2s_v3  None   (sin restricciones)
$ az vm list-usage -l eastus …                         →  cores 0/350 · standardDSv3Family 0/350
```
**Qué mirar:** suscripción vacía (otro lab: `XLabs-<n>`), proveedores ya registrados (los `az provider register` de la guía no hacen falta), la VM que pide la plataforma existe en `eastus` y hay cuota.

## 2. Valores de `azdeploy.py` (Task 1)
```console
$ grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py
5:rg = "rg-ai200-aks-cfg"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
9:AKS_VM_SIZE = "Standard_D2s_v3"
```
**Qué mirar:** tres cambios: grupo propio, región `eastus` y `Standard_D2s_v3` (el starter público trae `D2s_v7`; la plataforma pide v3).

## 3. Opción 1 · ACR
```console
$ az group show -n rg-ai200-aks-cfg --query "{n:name, r:location, e:properties.provisioningState}" -o table
N                 R       E
rg-ai200-aks-cfg  eastus  Succeeded
$ az acr list -g rg-ai200-aks-cfg --query "[].{nombre:name, sku:sku.name, estado:provisioningState, login:loginServer}" -o table
Nombre       Sku    Estado     Login
acr<hash>    Basic  Succeeded  acr<hash>.azurecr.io
```
**Qué mirar:** la opción 1 crea el grupo **y** el ACR; el endpoint (`loginServer`) se usa luego en `deployment.yaml`.

## 4. Opción 2 · Build de la imagen
```console
Building and pushing API image to ACR...
Image built and pushed: acr<hash>.azurecr.io/aks-config-api:latest

$ az acr repository show-tags -n acr<hash> --repository aks-config-api -o tsv
latest
$ az acr task list-runs -r acr<hash> --query "[].{estado:status, tarea:taskName}" -o table
Succeeded
```

## 5. Opción 3 · AKS
```console
Creating AKS cluster 'aks-<hash>' with one Standard_D2s_v3 node...
AKS cluster creation completed: aks-<hash>
  Deployment time: 4m 15s
Configuring storage permissions for Azure Files...
Storage permissions configured

$ az aks show -g rg-ai200-aks-cfg -n aks-<hash> --query "{estado:provisioningState, energia:powerState.code, k8s:kubernetesVersion}" -o table
Succeeded  Running  1.36
$ az role assignment list --scope <id del ACR> --query "[?roleDefinitionName=='AcrPull'].roleDefinitionName" -o tsv
AcrPull
```
**Qué mirar:** `Succeeded` + `Running`; `AcrPull` sobre el ACR (pull sin credenciales). El script también da un rol para el almacenamiento: no está a nivel de grupo, sino sobre el grupo de nodos `MC_…`. **No se lanza la opción 4** (`get-credentials`): se usa `az aks command invoke` (ver README).

## 6. Cluster alcanzable sin kubectl local
```console
$ az aks command invoke -g rg-ai200-aks-cfg -n aks-<hash> --command "kubectl get nodes"
command started at …, finished at … with exitcode=0
NAME                                STATUS   ROLES    AGE   VERSION
aks-nodepool1-<…>-vmss000000        Ready    <none>   10m   v1.36.5
```

## 7. Simulacro y apply de los cinco manifiestos
```console
$ az aks command invoke … --command "kubectl apply --dry-run=server -f configmap.yaml -f secrets.yaml -f pvc.yaml -f deployment.yaml -f service.yaml" --file k8s/configmap.yaml … --file k8s/service.yaml
exitcode=0
configmap/api-config created (server dry run)
secret/api-secrets created (server dry run)
persistentvolumeclaim/api-logs-pvc created (server dry run)
deployment.apps/aks-config-api created (server dry run)
service/aks-config-api-service created (server dry run)

$ az aks command invoke … --command "kubectl apply -f … (los mismos cinco)" --file …
exitcode=0
configmap/api-config created
secret/api-secrets created
persistentvolumeclaim/api-logs-pvc created
deployment.apps/aks-config-api created
service/aks-config-api-service created
```
**Qué mirar:** `--dry-run=server` valida contra el API server sin guardar nada: si falla, no se ha creado nada. El apply va en un solo comando; `kubectl` aplica los ficheros en el orden dado (ConfigMap, Secret y PVC antes del Deployment que los usa).

## 8. Verificación del despliegue
```console
$ az aks command invoke … --command "kubectl rollout status deploy/aks-config-api --timeout=150s; kubectl get cm,secret,pvc,deploy,svc,pods -o wide"
deployment "aks-config-api" successfully rolled out
configmap/api-config         3 datos
secret/api-secrets           Opaque   2 datos
persistentvolumeclaim/api-logs-pvc   Bound   pvc-<…>   1Gi   RWO   managed-csi
deployment.apps/aks-config-api   1/1   1   1   acr<hash>.azurecr.io/aks-config-api:latest
service/aks-config-api-service   LoadBalancer   10.0.251.115   <ip>   80:32483/TCP
pod/aks-config-api-…   1/1   Running   0
```
**Qué mirar:** el PVC pasa a `Bound` (con `managed-csi` el disco se crea al usarlo), rollout correcto y `EXTERNAL-IP` pública.

## 9. La API confirma ConfigMap, Secret y PVC
```console
$ curl -m 20 http://<ip>/healthz
{"status":"alive","service":"aks-config-api","version":"1.0.0","student":"YourNameHere"}   HTTP 200
$ curl -m 20 http://<ip>/readyz
{"status":"ready","configuration":{"student_name":"YourNameHere","api_version":"1.0.0"},"secrets_loaded":true,"persistent_storage_ready":true,"log_path":"/var/log/api"}   HTTP 200
```
**Qué mirar:** `student` y `api_version` vienen del **ConfigMap**; `secrets_loaded: true` del **Secret**; `persistent_storage_ready: true` del **PVC** montado en `/var/log/api`.

## 10. Cliente Python
`client/.env` con `API_ENDPOINT=http://<ip>`, entorno virtual e `httpx` + `python-dotenv`. El alumno confirma que las opciones 1-6 del menú funcionan (liveness con `Student: …`, readiness, secretos enmascarados, productos y resumen de logs). _Salida literal no conservada._
