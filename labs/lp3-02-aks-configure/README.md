# Lab LP3-02 · Configure apps on AKS (plataforma: Lab 7 · AI-200-LP03M02)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/02-aks-configure-container.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** completado el 03/11/2026 (despliegue y API verificados; cleanup pendiente de lanzar al cierre de este documento).

## Objetivo
Configurar la API en AKS con un **ConfigMap** (valores no sensibles), un **Secret** (credenciales) y un **PVC** (disco de Azure `managed-csi` para los logs), y comprobar que llegan al pod. El almacenamiento persistente es solo de demostración.

## Qué se construye
```
azdeploy.py (1) → resource group rg-ai200-aks-cfg + ACR
azdeploy.py (2) → imagen aks-config-api:latest (ACR Tasks)
azdeploy.py (3) → AKS (1 nodo Standard_D2s_v3, identidad gestionada, AcrPull)
az aks command invoke → kubectl apply de ConfigMap, Secret, PVC, Deployment y Service
curl /healthz /readyz + client/ (opciones 1-6)
```

## Diferencias de la plataforma respecto a la guía oficial
| Aspecto | Guía pública / starter | Plataforma (Task 1) |
|---|---|---|
| `AKS_VM_SIZE` | `Standard_D2s_v7` | `Standard_D2s_v3` |
| Región | libre | `eastus` |
| Resource group | el que elijas (lo crea el script) | igual: **grupo propio** `rg-ai200-aks-cfg` (a diferencia del lab 6, no hay grupo de la plataforma) |
| Proveedores | `az provider register` ×5 | ya registrados en esta suscripción: no hizo falta |
| Opciones 4 y 5 del menú | `get-credentials` y estado con `kubectl` | **no se lanzan**: se usa `az aks command invoke` (proxy de empresa, ver incidencias) |
| `kubectl apply` | local | `az aks command invoke … --file` |

## Incidencias y decisiones
| Síntoma / decisión | Causa | Arreglo |
|---|---|---|
| `kubectl` local no llega al API server de AKS | Proxy de empresa: `x509` y luego `502 IncompleteCertChain` (visto en el lab 6) | Anticipado: `az aks command invoke` desde el principio, sin kubeconfig |
| `wc -l k8s/*.yaml` → `0` en `configmap`, `secrets` y `pvc` | El starter los entrega vacíos | Completarlos antes del `apply` (son parte del ejercicio) |
| Placeholder `<YOUR_ACR_ENDPOINT>` en `deployment.yaml` | El starter no lo sustituye | `sed -i 's\|<YOUR_ACR_ENDPOINT>\|acr<hash>.azurecr.io\|' k8s/deployment.yaml` |

## Cómo se conectan los manifiestos (lo que se evalúa)
| El Deployment busca | Debe existir | Uso |
|---|---|---|
| `configMapRef: api-config` | ConfigMap `api-config` | `envFrom`: todas sus claves → variables de entorno |
| `secretKeyRef: api-secrets` (`secret-endpoint`, `secret-access-key`) | Secret `api-secrets` | dos variables sueltas |
| `claimName: api-logs-pvc` | PVC `api-logs-pvc` | montado en `/var/log/api` |

Si un nombre no coincide: `CreateContainerConfigError` (ConfigMap/Secret) o pod `Pending` (PVC). K8s: es lo mismo que en cualquier cluster; lo nuevo es la parte Azure (`managed-csi` = Azure Disk, `LoadBalancer` = Azure Load Balancer, `AcrPull` por identidad).

## Comandos al detalle

### 1. Edición de `azdeploy.py`
```
sed -i 's|<your-resource-group-name>|rg-ai200-aks-cfg|; s|<your-azure-region>|eastus|; s|"Standard_D2s_v7"|"Standard_D2s_v3"|' azdeploy.py
```
- **Qué hace / por qué:** fija el grupo propio, la región y la VM que exige la plataforma; es lo único que se cambia del script.
- **Comprobar:** `grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py` → las tres líneas con esos valores.
- **Si no coincide:** editar las líneas 5, 6 y 9 a mano.

### 2. `python3 azdeploy.py` → opciones 1, 2 y 3
```
1 → az group create + az acr create (Basic)           2 → az acr build … aks-config-api:latest
3 → az aks create (1 nodo, identidad gestionada, --attach-acr) + rol de almacenamiento sobre el grupo de nodos
```
- **Comprobar:** `az acr list -g rg-ai200-aks-cfg -o table` (`Succeeded`); `az acr repository show-tags -n <acr> --repository aks-config-api -o tsv` (`latest`); `az aks show -g rg-ai200-aks-cfg -n <aks> --query provisioningState -o tsv` (`Succeeded`).
- **Si no coincide:** `Creating` → esperar; AKS `Failed` → opción 6 y repetir la 3 (SKU/cuota: probar `D2s_v5`).

### 3. Los tres YAML vacíos y el placeholder
`configmap.yaml` (`api-config`: `STUDENT_NAME`, `API_VERSION`, `LOG_PATH`), `secrets.yaml` (`api-secrets`, `type: Opaque`, `stringData` con **valores ficticios**) y `pvc.yaml` (`api-logs-pvc`, `ReadWriteOnce`, `1Gi`, `managed-csi`).
- **Comprobar:** `wc -l k8s/*.yaml` (ninguno a 0), `grep -c YOUR_ACR k8s/deployment.yaml` → `0`, y los cinco cargan con `yaml.safe_load`.

### 4. Simulacro, apply y verificación con `az aks command invoke`
```
az aks command invoke -g <rg> -n <aks> --command "kubectl apply --dry-run=server -f a.yaml -f b.yaml …" --file k8s/a.yaml --file k8s/b.yaml …
  --command → corre dentro del cluster (pod efímero) vía ARM, que el proxy deja pasar
  --file    → sube el fichero local a ese pod
  --dry-run=server → el API server valida sin guardar
```
- **Qué hace / por qué:** primero el simulacro (si falla, no se creó nada), luego el apply real en un solo comando y el orden ConfigMap → Secret → PVC → Deployment → Service.
- **Esperado:** `exitcode=0` y cinco líneas `created`; después `successfully rolled out`, PVC `Bound`, pod `1/1 Running`, `EXTERNAL-IP` pública.
- **Si no coincide:** `CreateContainerConfigError` → nombre de ConfigMap/Secret; `Pending` → PVC o cuota; error de validación → indentación del YAML.

### 5. Probar desde fuera y cliente
- `curl -m 20 http://<ip>/healthz` (`student` del ConfigMap) y `/readyz` (`secrets_loaded: true`, `persistent_storage_ready: true`). La IP: `az aks command invoke … --command "kubectl get svc aks-config-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"`.
- Cliente: `client/.env` con `API_ENDPOINT=http://<ip>`, `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py` (opciones 1-6).
- Tras cambiar ConfigMap o Secret: reaplicar y `kubectl rollout restart deployment aks-config-api` (también con `az aks command invoke`).

## Cleanup
El grupo `rg-ai200-aks-cfg` es **nuestro** (lo creó el script), así que aquí sí se borra entero. Antes de lanzarlo, comprobar que es ese y no un grupo de la plataforma:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group list --query "[].name" -o tsv                 # confirmar que rg-ai200-aks-cfg existe y qué más hay
az group delete --name rg-ai200-aks-cfg --no-wait --yes
az group exists --name rg-ai200-aks-cfg                # repetir hasta que devuelva false
az group list -o table                                 # no debe quedar rg-ai200-* ni MC_rg-ai200-*
```
El borrado arrastra el AKS, el ACR, el disco del PVC y el grupo `MC_…`. Si hubiera un kubeconfig de la sesión, limpiar el contexto (`kubectl --kubeconfig ~/.kube/config config get-contexts`); con la vía `az aks command invoke` no se creó ninguno.

## Resultado y aprendizajes
- ConfigMap → variables no sensibles con `envFrom`; Secret → `secretKeyRef` por clave; PVC `managed-csi` → disco de Azure `RWO` que se enlaza (`Bound`) al arrancar el pod.
- `--dry-run=server` es la comprobación previa más barata.
- Anticipar el proxy: en estos labs se trabaja con `az aks command invoke` y sin kubeconfig.
