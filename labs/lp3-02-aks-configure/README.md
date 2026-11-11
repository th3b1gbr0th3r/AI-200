# Lab LP3-02 · Configure apps on AKS (plataforma: Lab 7 · AI-200-LP03M02)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/02-aks-configure-container.html (índice en [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (03/11/2026): completado.** Hechos los pasos 1-13: ACR, imagen y AKS con el menú (sin opciones 4 y 5), ConfigMap/Secret/PVC completados, simulacro y apply con `az aks command invoke`, API verificada con `curl` y cliente OK (opciones 1-6). **No hecho:** el experimento de cambiar el ConfigMap y `rollout restart` (paso 14). **Cleanup no verificado:** se dio el comando, pero no consta que se lanzara y a las 19:57 la suscripción ya respondía `Forbidden`.
- Desde este lab se aplica **primero `az`**: el proxy de empresa bloquea `kubectl` contra AKS (visto en LP3-01, paso 12), así que todo el `kubectl` va por `az aks command invoke` y no se crea kubeconfig.
- Registro de la sesión: [`sesiones/2026-11-03-sesion-04-aks.md`](../../sesiones/2026-11-03-sesion-04-aks.md). Notas del módulo: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Cómo crea el script el ACR: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md).
- Lab anterior: [LP3-01](../lp3-01-aks-deploy/README.md) · Lab siguiente: [LP3-03](../lp3-03-aks-troubleshoot/README.md). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: IDs, usuario y pase del lab fuera; hash de ACR/AKS como `<hash>`, IP pública como `<ip>`.

## Qué se construye
La misma idea que LP3-01 (API en AKS detrás de un LoadBalancer), pero sin modelo de IA: lo que se practica es **cómo llega la configuración al pod**.

```
azdeploy.py 1 → grupo rg-ai200-aks-cfg (nuestro) + ACR acr<hash>
azdeploy.py 2 → az acr build → aks-config-api:latest
azdeploy.py 3 → AKS aks-<hash> (1 nodo Standard_D2s_v3, AcrPull, rol de almacenamiento en MC_…)
k8s/ (tú)     → ConfigMap api-config · Secret api-secrets · PVC api-logs-pvc (+ ACR en deployment.yaml)
az aks command invoke → apply --dry-run=server → apply → rollout
                         ┌ envFrom: api-config        → STUDENT_NAME, API_VERSION, LOG_PATH
pod aks-config-api ──────┼ secretKeyRef: api-secrets  → SECRET_ENDPOINT, SECRET_ACCESS_KEY
                         └ volumeMount /var/log/api   → PVC → Azure Disk (managed-csi)
curl /healthz /readyz + client/ (opciones 1-6)
```

**El objetivo, en cristiano:** separar el código de su configuración. Lo no sensible va en un **ConfigMap**, lo sensible en un **Secret** y lo que debe sobrevivir al pod en un **PVC**. Para un SysOps de K8s los tres objetos son los de siempre; lo nuevo es la parte Azure: `managed-csi` = Azure Disk creado bajo demanda, LoadBalancer de Azure y `AcrPull` por identidad.

### Cómo se conectan los manifiestos (lo que se evalúa)
| El Deployment busca | Debe existir | Uso | Si el nombre no coincide |
|---|---|---|---|
| `configMapRef: api-config` | ConfigMap `api-config` | `envFrom`: todas sus claves → variables | `CreateContainerConfigError` |
| `secretKeyRef: api-secrets` (`secret-endpoint`, `secret-access-key`) | Secret `api-secrets` | dos variables sueltas | `CreateContainerConfigError` |
| `claimName: api-logs-pvc` | PVC `api-logs-pvc` | montado en `/var/log/api` | pod `Pending` |

### Diferencias de la plataforma respecto a la guía
| Aspecto | Guía / starter público | Plataforma | Qué se hizo |
|---|---|---|---|
| `AKS_VM_SIZE` | `Standard_D2s_v7` | `Standard_D2s_v3` | v3 |
| Región | libre | `eastus` | `eastus` |
| Grupo | lo crea el script | igual: **grupo propio** (no hay grupo de la plataforma) | `rg-ai200-aks-cfg` → se puede borrar entero |
| `az provider register` ×5 | sí | sí | no hizo falta (ya `Registered`) |
| Opción 4 (`get-credentials`) y 5 (estado con `kubectl`) | sí | sí | **no se lanzan**: `az aks command invoke` |
| `kubectl apply` | local | local | `az aks command invoke … --file` |

---

## Paso 0 · Preparar la terminal
**Por qué:** `az` necesita la CA del proxy en cada terminal nueva; y si venías del cliente de LP3-01, sal de su `.venv`.
```bash
deactivate 2>/dev/null
cd ~/claude/AI-200-Developing/labs/lp3-02-aks-configure
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `echo $REQUESTS_CA_BUNDLE` → la ruta. Si está vacía, repite el `export`.

## Paso 1 · `az login` con el usuario del lab 7
**Por qué:** cada lab es otra suscripción con otro usuario temporal.
```bash
az logout
az login --use-device-code
```
Salida real del login: _no guardada_ (el alumno confirmó «az login realizado»). Esperado: una suscripción `XLabs-<n>` en `Lab Directory`.

✅ **Comprobación:**
```bash
az account show --query "{estado:state, sub:name, tenant:tenantDisplayName}" -o table
```
Salida real:
```text
--------  ---------  -------------
Enabled   XLabs-<n>  Lab Directory
```
Debe ser una suscripción **distinta** de la de LP3-01. Si sale la anterior, `az logout` y repite.

## Paso 2 · Inventario inicial, proveedores, VM y cuota
**Por qué:** saber qué había antes (base del cleanup), si hacen falta los `az provider register` de la guía y si la VM que pide la plataforma existe y cabe.
```bash
az group list -o table
az provider list --query "[?namespace=='Microsoft.ContainerService'||namespace=='Microsoft.ContainerRegistry'||namespace=='Microsoft.Compute'||namespace=='Microsoft.Network'||namespace=='Microsoft.Storage'].{ns:namespace, estado:registrationState}" -o table
az vm list-skus -l eastus --size Standard_D2s_v3 --resource-type virtualMachines --query "[0].{sku:name, restr:restrictions[0].reasonCode}" -o tsv
az vm list-usage -l eastus --query "[?name.value=='cores'||name.value=='standardDSv3Family'].[name.value, currentValue, limit]" -o tsv
```
Salida real:
```text
(group list: sin filas)
Ns                           Estado
---------------------------  ----------
Microsoft.ContainerRegistry  Registered
Microsoft.ContainerService   Registered
Microsoft.Compute            Registered
Microsoft.Storage            Registered
Microsoft.Network            Registered
Standard_D2s_v3	None
cores	0	350
standardDSv3Family	0	350
```
**Qué mirar:** suscripción vacía; los cinco proveedores ya registrados (los `az provider register` no hacen falta); la VM sin restricciones (`None`) y 350 vCPU libres. Permisos del usuario del lab: `Contributor` + `XLabsAdmin`.

✅ **Comprobación:** si algún proveedor sale `NotRegistered`, `az provider register --namespace <ns>`. Si la VM sale con restricción, usa `Standard_D2s_v5`.

## Paso 3 · Poner los valores en `azdeploy.py`
**Por qué:** grupo propio (para poder borrarlo entero), región y VM que exige la plataforma. Es lo único que se cambia del script.
```bash
sed -i 's|<your-resource-group-name>|rg-ai200-aks-cfg|; s|<your-azure-region>|eastus|; s|"Standard_D2s_v7"|"Standard_D2s_v3"|' azdeploy.py
grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py
```
Salida real:
```text
5:rg = "rg-ai200-aks-cfg"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
9:AKS_VM_SIZE = "Standard_D2s_v3"
```
✅ **Comprobación:** las tres líneas así. Si alguna sigue con `<your-…>` o `v7`, edítala a mano (líneas 5, 6 y 9). En el repo `azdeploy.py` ya está con estos valores.

## Paso 4 · Opción 1: grupo + ACR
**Por qué:** en este starter la opción 1 crea **también** el grupo. Su `loginServer` es el prefijo de la imagen en `deployment.yaml`.
```bash
python3 azdeploy.py      # menú → 1  (no salgas del menú: siguen la 2 y la 3)
```
Salida del script: _no guardada_ (esperado: `ACR created: acr<hash>` y el endpoint).

✅ **Comprobación** (salida real):
```bash
az group show -n rg-ai200-aks-cfg --query "{n:name, r:location, e:properties.provisioningState}" -o table
az acr list -g rg-ai200-aks-cfg --query "[].{nombre:name, sku:sku.name, estado:provisioningState, login:loginServer}" -o table
```
```text
rg-ai200-aks-cfg  eastus  Succeeded
Nombre       Sku    Estado     Login
-----------  -----  ---------  ----------------------
acr<hash>    Basic  Succeeded  acr<hash>.azurecr.io
```
Apunta el `Login`: lo usas en el paso 8. Sin filas → la opción no terminó; relánzala (es idempotente).

## Paso 5 · Opción 2: build de la imagen
**Por qué:** ACR Tasks construye `aks-config-api:latest` en la nube con tu `az login`; sin Docker local.
```bash
# menú → 2   (3-5 min)
```
Salida real:
```text
Building and pushing API image to ACR...
Image built and pushed: acr<hash>.azurecr.io/aks-config-api:latest
```
✅ **Comprobación** (salida real):
```bash
az acr repository show-tags -n acr<hash> --repository aks-config-api -o tsv
az acr task list-runs -r acr<hash> --query "[].status" -o tsv
```
```text
latest
Succeeded
```
Si el run sale `Failed`: `az acr task logs -r acr<hash> --run-id <id>`.

## Paso 6 · Opción 3: AKS
**Por qué:** el cluster con identidad gestionada; `--attach-acr` da **AcrPull** al kubelet, y el script añade un rol para escribir en almacenamiento (el PVC).
```bash
# menú → 3   (5-10 min)  · NO lances la 4 ni la 5 (usan kubectl local / escriben kubeconfig)
```
Salida real:
```text
Creating AKS cluster 'aks-<hash>' with one Standard_D2s_v3 node...
This may take 5-10 minutes to complete. Please wait...

AKS cluster creation completed: aks-<hash>
  Deployment time: 4m 15s
Configuring storage permissions for Azure Files...
Storage permissions configured
```
✅ **Comprobación** (salida real):
```bash
RG=rg-ai200-aks-cfg; AKS=aks-<hash>; ACR=acr<hash>
az aks show -g $RG -n $AKS --query "{estado:provisioningState, energia:powerState.code, k8s:kubernetesVersion}" -o table
az role assignment list --scope $(az acr show -g $RG -n $ACR --query id -o tsv) --query "[?roleDefinitionName=='AcrPull'].roleDefinitionName" -o tsv
az resource list -g $RG --query "[].{n:name,t:type}" -o tsv
```
```text
Succeeded  Running  1.36
AcrPull
acr<hash>    Microsoft.ContainerRegistry/registries
aks-<hash>   Microsoft.ContainerService/managedClusters
```
**Qué mirar:** `Succeeded`/`Running` y `AcrPull` (pull sin credenciales). El rol de almacenamiento **no** aparece a nivel de grupo: va sobre el grupo de nodos `MC_…`. Si el AKS sale `Failed`: opción 6 y repetir la 3 (probar `D2s_v5`).

## Paso 7 · Ver qué falta en `k8s/`
**Por qué:** el starter entrega tres YAML **vacíos**; aplicarlos así crearía objetos sin contenido y el pod no arrancaría.
```bash
wc -l k8s/*.yaml
```
Salida real:
```text
   0 k8s/configmap.yaml
  84 k8s/deployment.yaml
   0 k8s/pvc.yaml
   0 k8s/secrets.yaml
  19 k8s/service.yaml
 103 total
```
✅ **Comprobación:** tras el paso 8, ninguno debe quedar a 0.

## Paso 8 · Completar ConfigMap, Secret y PVC, y poner el ACR en el Deployment
**Por qué:** es el ejercicio del lab. Los nombres (`api-config`, `api-secrets` + claves, `api-logs-pvc`) tienen que coincidir con lo que pide `deployment.yaml` (tabla de arriba). Los tres ficheros ya están completos en [`k8s/`](k8s/) (los escribió Claude a petición del alumno, con el contenido de la guía):
- [`configmap.yaml`](k8s/configmap.yaml): `STUDENT_NAME: "YourNameHere"`, `API_VERSION: "1.0.0"`, `LOG_PATH: "/var/log/api"`.
- [`secrets.yaml`](k8s/secrets.yaml): `type: Opaque`, `stringData` con `secret-endpoint` y `secret-access-key` **ficticios** (Kubernetes los guarda en base64; en un caso real no se versionan).
- [`pvc.yaml`](k8s/pvc.yaml): `ReadWriteOnce`, `1Gi`, `storageClassName: managed-csi` (Azure Disk).

El Deployment del repo lleva el placeholder `<YOUR_ACR_ENDPOINT>`: hay que sustituirlo por el ACR de **tu** lab.
```bash
sed -i "s|<YOUR_ACR_ENDPOINT>|$ACR.azurecr.io|" k8s/deployment.yaml
wc -l k8s/*.yaml; grep -n "image:" k8s/deployment.yaml; grep -c YOUR_ACR k8s/deployment.yaml
python3 -I -c "
import yaml
for f in ('configmap','secrets','pvc','deployment','service'):
    d=yaml.safe_load(open('k8s/'+f+'.yaml')); print(f, d['kind'], d['metadata']['name'])"
```
Salida real:
```text
  11 configmap.yaml
  84 deployment.yaml
  14 pvc.yaml
  11 secrets.yaml
  19 service.yaml
 139 total
22:        image: acr<hash>.azurecr.io/aks-config-api:latest
0
configmap ConfigMap api-config
secrets Secret api-secrets
pvc PersistentVolumeClaim api-logs-pvc
deployment Deployment aks-config-api
service Service aks-config-api-service
```
✅ **Comprobación:** ningún fichero a 0, `0` placeholders y los cinco `kind`/nombre. Un error de YAML casi siempre es indentación. **Antes de subir al repo**, vuelve a dejar `<YOUR_ACR_ENDPOINT>` en `deployment.yaml`.

## Paso 9 · Comprobar que el cluster responde por la vía `az`
**Por qué:** antes de aplicar, confirmar que `az aks command invoke` llega al cluster (sin kubeconfig ni `kubectl` local).
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl get nodes"
```
Salida real:
```text
command started at 2026-11-03 19:43:12+00:00, finished at 2026-11-03 19:43:12+00:00 with exitcode=0
NAME                                STATUS   ROLES    AGE   VERSION
aks-nodepool1-<…>-vmss000000        Ready    <none>   10m   v1.36.5
```
> **Alternativa local, solo sin proxy:** `python3 azdeploy.py` → opción 4 (`get-credentials`) y `kubectl get nodes`. No es la primera opción porque en el PC de empresa `kubectl` contra AKS falla (`x509` y `502 IncompleteCertChain`, LP3-01 paso 12).

✅ **Comprobación:** `exitcode=0` y un nodo `Ready`. Si da error de permisos, revisa que estás en la suscripción del lab (paso 1).

## Paso 10 · Simulacro: `apply --dry-run=server`
**Por qué:** el API server valida esquema, nombres y admisión **sin guardar nada**. Si falla, no se ha creado ningún objeto: es la comprobación previa más barata.
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl apply --dry-run=server -f configmap.yaml -f secrets.yaml -f pvc.yaml -f deployment.yaml -f service.yaml" \
  --file k8s/configmap.yaml --file k8s/secrets.yaml --file k8s/pvc.yaml --file k8s/deployment.yaml --file k8s/service.yaml
```
Salida real:
```text
command started at 2026-11-03 19:43:49+00:00, finished at 2026-11-03 19:43:51+00:00 with exitcode=0
configmap/api-config created (server dry run)
secret/api-secrets created (server dry run)
persistentvolumeclaim/api-logs-pvc created (server dry run)
deployment.apps/aks-config-api created (server dry run)
service/aks-config-api-service created (server dry run)
```
✅ **Comprobación:** cinco líneas `(server dry run)`. Un error aquí = corrige el YAML y repite; no hay nada que limpiar.

## Paso 11 · Apply real
**Por qué:** un solo comando con los cinco ficheros en orden: ConfigMap, Secret y PVC antes del Deployment que los usa.
```bash
az aks command invoke -g $RG -n $AKS \
  --command "kubectl apply -f configmap.yaml -f secrets.yaml -f pvc.yaml -f deployment.yaml -f service.yaml" \
  --file k8s/configmap.yaml --file k8s/secrets.yaml --file k8s/pvc.yaml --file k8s/deployment.yaml --file k8s/service.yaml
```
Salida real:
```text
command started at 2026-11-03 19:44:18+00:00, finished at 2026-11-03 19:44:20+00:00 with exitcode=0
configmap/api-config created
secret/api-secrets created
persistentvolumeclaim/api-logs-pvc created
deployment.apps/aks-config-api created
service/aks-config-api-service created
```
✅ **Comprobación:** `exitcode=0` y cinco `created` (si repites, `unchanged`/`configured`). Sigue con el paso 12.

## Paso 12 · Verificar despliegue, PVC e IP
**Por qué:** ver que el pod arranca con su configuración y que el PVC se enlaza: con `managed-csi` el disco se crea **cuando un pod lo pide** (`WaitForFirstConsumer`), así que puede verse `Pending` unos segundos.
```bash
az aks command invoke -g $RG -n $AKS --command "kubectl rollout status deploy/aks-config-api --timeout=150s; kubectl get cm,secret,pvc,deploy,svc,pods -o wide"
```
Salida real (ejecutada por Claude, solo lectura; recortada):
```text
Waiting for deployment "aks-config-api" rollout to finish: 0 of 1 updated replicas are available...
deployment "aks-config-api" successfully rolled out
NAME                         DATA   AGE
configmap/api-config         3      39s
NAME                 TYPE     DATA   AGE
secret/api-secrets   Opaque   2      39s
NAME                                 STATUS   VOLUME      CAPACITY   ACCESS MODES   STORAGECLASS
persistentvolumeclaim/api-logs-pvc   Bound    pvc-<…>     1Gi        RWO            managed-csi
NAME                             READY   UP-TO-DATE   AVAILABLE   IMAGES
deployment.apps/aks-config-api   1/1     1            1           acr<hash>.azurecr.io/aks-config-api:latest
NAME                             TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)
service/aks-config-api-service   LoadBalancer   10.0.251.115   <ip>          80:32483/TCP
pod/aks-config-api-…             1/1   Running   0
```
**Qué mirar:** ConfigMap con 3 datos, Secret con 2, PVC `Bound` (el disco ya existe), `1/1` y `EXTERNAL-IP` pública.

✅ **Comprobación:** `CreateContainerConfigError` → nombre de ConfigMap/Secret o clave mal escritos (`kubectl describe pod`); pod `Pending` → PVC o cuota; `ImagePullBackOff` → el `image:` del paso 8 o falta `AcrPull`. IP sola: `az aks command invoke -g $RG -n $AKS --command "kubectl get svc aks-config-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"`.

## Paso 13 · La API confirma ConfigMap, Secret y PVC; cliente
**Por qué:** la prueba de que la configuración **llega al proceso**, no solo que los objetos existen. `curl` local vale: es HTTP a una IP pública.
```bash
IP=<ip>
curl -sS -m 20 -w '  HTTP %{http_code}\n' http://$IP/healthz
curl -sS -m 20 -w '  HTTP %{http_code}\n' http://$IP/readyz
```
Salida real:
```text
{"status":"alive","service":"aks-config-api","version":"1.0.0","student":"YourNameHere"}  HTTP 200
{"status":"ready","configuration":{"student_name":"YourNameHere","api_version":"1.0.0"},"secrets_loaded":true,"persistent_storage_ready":true,"log_path":"/var/log/api"}  HTTP 200
```
**Qué mirar:** `student` y `api_version` salen del **ConfigMap**; `secrets_loaded: true` del **Secret**; `persistent_storage_ready: true` del **PVC** montado en `/var/log/api`.

Cliente (la opción 5 del menú lo habría escrito con `kubectl`; se hace a mano):
```bash
cd client
printf 'API_ENDPOINT=http://%s\n' "$IP" > .env
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Salida real: _no conservada_. El alumno confirmó «todas opciones ok»: 1 liveness (con `Student: …`), 2 readiness, 3 secretos **enmascarados**, 4 y 5 productos de ejemplo, 6 resumen de peticiones leído del log en el PVC.

✅ **Comprobación:** dos HTTP 200 con esos campos. `secrets_loaded: false` → el Secret no llegó (nombres de clave); `persistent_storage_ready: false` → el volumen no está montado o no se puede escribir.

## Paso 14 · Cambiar la configuración en caliente — no hecho
**Por qué:** las variables de `envFrom` se leen **al arrancar el contenedor**; cambiar el ConfigMap no afecta a los pods que ya corren hasta reiniciarlos.
```bash
sed -i 's|"YourNameHere"|"<tu-nombre>"|' k8s/configmap.yaml
az aks command invoke -g $RG -n $AKS --command "kubectl apply -f configmap.yaml && kubectl rollout restart deployment aks-config-api && kubectl rollout status deployment aks-config-api --timeout=120s" --file k8s/configmap.yaml
curl -sS -m 20 http://$IP/healthz
```
✅ **Esperado:** `configmap/api-config configured`, `restarted`, `successfully rolled out` y `/healthz` con el nuevo `student`. Si sigue el valor viejo, falta el `rollout restart`.

---

## Cleanup (obligatorio al acabar)
**Por qué aquí sí `az group delete`:** `rg-ai200-aks-cfg` lo creó el script; es **nuestro**. Se lleva el ACR, el AKS, el disco del PVC y, con el AKS, el grupo `MC_…`. Antes, confirmar el contenido para no borrar un grupo ajeno.
```bash
deactivate 2>/dev/null; export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group list --query "[].{n:name, r:location}" -o table
az resource list -g rg-ai200-aks-cfg --query "[].{n:name,t:type}" -o tsv
```
Salida real (19:49):
```text
N                                        R
---------------------------------------  ------
rg-ai200-aks-cfg                         eastus
MC_rg-ai200-aks-cfg_aks-<hash>_eastus    eastus
NetworkWatcherRG                         eastus
acr<hash>    Microsoft.ContainerRegistry/registries
aks-<hash>   Microsoft.ContainerService/managedClusters
```
`NetworkWatcherRG` lo crea Azure al usar redes: no se toca.
```bash
az group delete --name rg-ai200-aks-cfg --no-wait --yes
az group exists --name rg-ai200-aks-cfg
az group list -o table
```
✅ **Esperado:** `exists` = `true` mientras borra y `false` al terminar (varios minutos); `az group list` sin `rg-ai200-*` ni `MC_rg-ai200-*`. Si tras 15 min sigue `true`: `az group show -n rg-ai200-aks-cfg --query properties.provisioningState -o tsv` (si `Failed`, relanza el `delete`).

**Resultado real: no verificado.** El comando se dio a las 19:51; no consta que se lanzara. A las 19:57, ya con el usuario del lab 8, la lectura de esta suscripción devolvió:
```text
ERROR: (AuthorizationFailed) The client '<usuario>' with object id '<id>' does not have authorization to perform action 'Microsoft.Resources/subscriptions/resourcegroups/read' over scope '/subscriptions/<sub-id>' …
```
La plataforma revoca las credenciales al terminar el lab y desprovisiona el entorno, pero no se pudo comprobar. **Lección:** lanzar y verificar el cleanup **en cuanto termina el lab**, antes de documentar o pasar al siguiente.

## Resumen de incidencias y decisiones
| Síntoma / decisión | Causa | Arreglo |
|---|---|---|
| `kubectl` local no llega a AKS | Proxy de empresa (`x509`, `502`), visto en LP3-01 | Anticipado: `az aks command invoke` desde el paso 9; opciones 4 y 5 no se lanzan |
| `wc -l` → `0` en `configmap`, `secrets` y `pvc` | El starter los entrega vacíos | Paso 8 |
| `<YOUR_ACR_ENDPOINT>` en `deployment.yaml` | El starter no lo sustituye | `sed` del paso 8 |
| PVC `Pending` al principio | `managed-csi` crea el disco al primer consumidor | Esperar al pod; luego `Bound` |
| Cleanup no verificable | Credenciales del lab revocadas al pasar al siguiente | Cleanup inmediato al acabar cada lab |

## Para el examen
- ConfigMap → `envFrom` (todas las claves) o `configMapKeyRef`; Secret → `secretKeyRef` por clave; los dos se leen al arrancar → `rollout restart` tras cambiarlos.
- Secret ≠ cifrado: base64 en etcd; en Azure lo serio es Key Vault + CSI driver.
- PVC `managed-csi` = Azure Disk `RWO` (un nodo); para `RWX` → Azure Files (`azurefile-csi`).
- `--dry-run=server` valida contra el API server sin persistir.
