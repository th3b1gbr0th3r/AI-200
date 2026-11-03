# Lab LP3-03 · Troubleshoot apps on AKS (plataforma: Lab 8 · AI-200-LP03M03)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** completado el 03/11/2026 (las tres averías diagnosticadas y corregidas). **Cleanup: no verificado**, ver abajo.

## Objetivo
Desplegar una API en el namespace `aks-troubleshoot` y diagnosticar y corregir tres fallos clásicos: (1) selector del Service que no casa con las etiquetas, (2) `CrashLoopBackOff` por falta de una variable de entorno, (3) readiness probe con una ruta inválida.

## Qué se construye
```
azdeploy.py (1) → resource group rg-ai200-aks-ts + ACR (y reescribe image: de los 3 *-deployment.yaml)
azdeploy.py (2) → imagen aks-troubleshoot-api:latest (ACR Tasks)
azdeploy.py (3) → AKS (1 nodo Standard_D2s_v3, identidad gestionada, AcrPull)
az aks command invoke → namespace + api-deployment + api-service (ClusterIP)
3 escenarios: aplicar la avería → diagnosticar → corregir → comprobar
```

## Diferencias de la plataforma respecto a la guía oficial
| Aspecto | Starter público | Plataforma (Task 1) |
|---|---|---|
| `AKS_VM_SIZE` | `Standard_D2s_v7` | `Standard_D2s_v3` |
| Región | libre | `eastus` |
| Resource group | el que elijas | grupo propio `rg-ai200-aks-ts` (lo crea el script; **se puede borrar entero**) |
| Menú | 4 credenciales · 5 deploy · 6 estado (todas con `kubectl` local) | **solo 1, 2 y 3**; el resto se hace con `az aks command invoke` (proxy de empresa) |
| `port-forward` | túnel local al Service `ClusterIP` | no vale por el proxy: `kubectl exec` en el pod contra el nombre del Service |
| `kubectl edit` | interactivo | no vale con `az`: `patch` o `set env` |
| `kubectl get pods -w` | watch | no vale: se repite la consulta |

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `bash: error de sintaxis cerca de '('` | Se pegó el título de la guía (con paréntesis) como si fuera un comando | Copiar solo el contenido del bloque de código |
| `patch … (no change)` | Un primer `patch` ya había corregido el selector | `kubectl get svc … --show-managed-fields` muestra quién escribió y cuándo |
| Escenario 2 sin `CrashLoopBackOff` (1.er intento) | Diagnóstico a los 8 s; `-l app=api` mezcla el pod viejo y el nuevo durante el rolling update | Esperar 60 s y mirar el pod **más reciente** (`--sort-by=.metadata.creationTimestamp`) |
| `apply … unchanged` y `set env … None` (2.º intento) | `apply` solo quita campos que él mismo aplicó (`last-applied`); `API_KEY` la había puesto `set env` | No mezclar `apply` con comandos imperativos; quitar la variable con `set env API_KEY-` |
| El pod final tras arreglar tiene 15 min | Al volver a la plantilla original, Kubernetes **reutiliza el ReplicaSet antiguo** | Es normal (mismo `pod-template-hash`); `kubectl get rs` lo muestra |
| `get endpointslices` lista la IP de un pod `0/1` | Muestra todas las direcciones; no indica si están listas | Mirar `conditions.ready` con `-o jsonpath` |

## Las tres averías (cómo se reconocen)
| Escenario | Síntoma | Dónde se ve | Causa | Corrección |
|---|---|---|---|---|
| 1. Etiquetas | Pod `Running`, Service sin endpoints | `describe service` (`Selector`), `endpointslices` | Selector `app=api-v2` ≠ etiqueta `app=api` | `patch` del selector |
| 2. Crash | `CrashLoopBackOff`, `RESTARTS` sube | `logs` (`FATAL`), `describe` (`Exit Code 1`, `Back-off`) | Falta `API_KEY` | `set env API_KEY=…` |
| 3. Readiness | `0/1 Running`, `RESTARTS 0`, Service sin tráfico a ese pod | `events` (`Unhealthy` 404), `conditions.ready` | Ruta de la sonda `/invalid-path` | `patch` JSON de `readinessProbe…path` |

**Regla de diagnóstico:** `get pods` → `logs` (por qué muere el proceso) → `describe` / `events` (qué hace Kubernetes) → `endpointslices` (¿llega tráfico?). Durante un rolling update fallido el pod viejo sigue sirviendo: el servicio no cae.

## Comandos al detalle

### 1. Edición de `azdeploy.py`
`sed -i 's|<your-resource-group-name>|rg-ai200-aks-ts|; s|<your-azure-region>|eastus|; s|"Standard_D2s_v7"|"Standard_D2s_v3"|' azdeploy.py`
- **Comprobar:** `grep -n '^rg\|^location\|^AKS_VM_SIZE' azdeploy.py` → las tres líneas con esos valores.

### 2. Menú: opciones 1, 2 y 3 (no lanzar la 4, 5 ni 6)
- **Comprobar:** `az acr list -g rg-ai200-aks-ts -o table` (`Succeeded`), `az acr repository show-tags -n <acr> --repository aks-troubleshoot-api -o tsv` (`latest`) y `az aks show -g rg-ai200-aks-ts -n <aks> --query provisioningState -o tsv` (`Succeeded`). Los `*-deployment.yaml` ya apuntan al ACR (`grep -n "image:" k8s/*.yaml`).
- **Si no coincide:** AKS `Failed` → opción 7 del menú y repetir la 3 (SKU/cuota: probar `D2s_v5`).

### 3. Aplicar y verificar sin `kubectl` local
```
az aks command invoke -g <rg> -n <aks> --command "kubectl … -n aks-troubleshoot" --file k8s/<fichero>.yaml
  --command → corre dentro del cluster vía ARM (el proxy lo deja pasar)
  --file    → sube el fichero local al pod efímero que ejecuta el comando
```
- **Despliegue base:** `kubectl create namespace aks-troubleshoot; kubectl apply -f api-deployment.yaml -f api-service.yaml -n aks-troubleshoot; kubectl rollout status deployment/api-deployment -n aks-troubleshoot`.
- **Probar el Service sin `port-forward`:** `kubectl exec deploy/api-deployment -n aks-troubleshoot -- python -c "import urllib.request;print(urllib.request.urlopen('http://api-service/healthz').read().decode())"`.
- **Esperado:** pod `1/1 Running`, `endpointslice` con IP y `{"status":"healthy"}`.

### 4. Correcciones
`kubectl patch service api-service -n aks-troubleshoot -p '{"spec":{"selector":{"app":"api"}}}'` · `kubectl set env deployment/api-deployment API_KEY=demo-api-key-12345 -n aks-troubleshoot` · `kubectl patch deployment api-deployment -n aks-troubleshoot --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/healthz"}]'`. Todas con `az aks command invoke … --command "…"`.
- **Comprobar después de cada una:** `endpointslices` con IP y `ready=true`; `rollout status` correcto y pod `1/1`.

## Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general (piezas del script, push frente a pull, comprobaciones): [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab, según el código de su `azdeploy.py`:
| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (L164) | `--sku Basic`, `--admin-enabled true` (no se usa) |
| Subir la imagen | `az acr build` | `az acr build` (L196) con `aks-troubleshoot-api:latest`; la opción 1 reescribe además `image:` de los `*-deployment.yaml` con el ACR |
| Vincular (pull) | ver fila siguiente | `az aks create … --attach-acr` (L260): AcrPull al kubelet |
- **Push y pull son permisos distintos:** el build lo hace ACR en la nube con tu `az login`; la descarga la hace el servicio con una identidad y el rol **AcrPull**.
- **Comprobar el vínculo (solo lectura):** `az role assignment list --scope <id-ACR> --query "[?roleDefinitionName=='AcrPull']" -o table` (una fila).
- **Si el servicio no descarga la imagen** (`ImagePullBackOff`): falta AcrPull o la imagen/tag no existe → `az acr repository show-tags -n <acr> --repository <imagen> -o tsv` y la lista de roles de arriba.

## Cleanup
El grupo `rg-ai200-aks-ts` es **nuestro** (lo creó el script): aquí sí se borra entero. Antes, comprobar que es ese y no un grupo de la plataforma.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group list --query "[].name" -o tsv               # confirmar que rg-ai200-aks-ts existe
az group delete --name rg-ai200-aks-ts --no-wait --yes
az group exists --name rg-ai200-aks-ts               # repetir hasta que devuelva false
az group list -o table                               # no debe quedar rg-ai200-* ni MC_rg-ai200-*
```
`AZ801-L0501-RG` y `NetworkWatcherRG` son de la plataforma: no se tocan. Con la vía `az aks command invoke` no se creó kubeconfig.

### Resultado real del cleanup (03/11/2026)
Se intentó `az group delete --name rg-ai200-aks-ts --no-wait --yes` tras confirmar la suscripción activa y el contenido del grupo (solo el ACR y el AKS). **Falló con `AuthorizationFailed` (403)**, y también las lecturas (`az group show`): la plataforma había revocado las credenciales del lab. No se pudo borrar ni verificar.
- **Qué significa:** el entorno del lab es temporal y la plataforma lo desprovisiona al caducar la sesión, pero **no se ha comprobado** que el grupo se haya eliminado.
- **Si la sesión del lab sigue activa en la plataforma:** pedir un Temporary Access Pass nuevo, `az login --use-device-code` y repetir el borrado y la comprobación de arriba.
- **Para la próxima vez:** lanzar el cleanup **en cuanto termine el lab**, antes de documentar. La sesión del lab caduca por tiempo.
