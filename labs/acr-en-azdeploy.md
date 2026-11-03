# Cómo crean y vinculan el ACR los `azdeploy.py` de los labs

Referencia común. Cada README de lab tiene su sección «Cómo `azdeploy.py` crea el ACR y lo vincula» con los datos concretos de su script.

## El script es un envoltorio de `az`
`azdeploy.py` no habla con Azure por su cuenta: lanza comandos `az` con `subprocess`.
- `run_quiet(descripción, [comando])`: ejecuta un `az` y, si falla, imprime `Error: … failed` con la salida.
- `az_query([…])`: ejecuta un `az … -o tsv` de solo lectura y devuelve el texto; sirve para comprobar si algo ya existe (los scripts son idempotentes).

## 1. Crear el ACR: `az acr create`
```
az acr create
  --resource-group <rg>      → grupo donde vive
  --name acr<hash>           → nombre único en todo Azure; el hash sale de la identidad del alumno
  --sku Basic                → nivel más barato (sin geo-replicación ni redes privadas)
  --admin-enabled true|false → usuario/contraseña administrador del registro (según el lab)
```
El endpoint es `<nombre>.azurecr.io`, el prefijo de las imágenes. `--admin-enabled true` crea un secreto más que rotar; **ninguno de los labs lo usa** (el pull es por identidad), y en producción se deja a `false`.

## 2. Subir la imagen: `az acr build`
```
az acr build --registry acr<hash> --image <nombre>:latest --file api/Dockerfile api/
```
`az` empaqueta la carpeta y la sube; **el build y el push los hace ACR en la nube** (ACR Tasks, agente efímero). No hace falta Docker ni `docker login`. Quien construye es el propio registro, así que el permiso lo da el `az login` del alumno. Alternativa local (`az acr login`, `docker build`, `docker push`): necesita Docker y que el proxy deje pasar el registro; no se usa.

## 3. Vincular el servicio con el ACR (el pull)
Subir y bajar son dos permisos distintos:
| Acción | Quién | Cómo se autoriza |
|---|---|---|
| Subir (push) | `az acr build` / el alumno | Su login de `az` |
| Bajar (pull) | El servicio que ejecuta el contenedor | Rol **AcrPull** de una identidad |

| Servicio | Cómo se vincula | Equivalente en K8s |
|---|---|---|
| AKS | `az aks create … --enable-managed-identity --attach-acr acr<hash>` → AcrPull a la identidad del **kubelet** | `imagePullSecrets` sin secreto |
| Container Apps | `az containerapp create … --registry-server <acr>.azurecr.io --registry-identity system` → identidad system-assigned + AcrPull | idem |
| App Service | `az webapp identity assign` + rol AcrPull sobre el ACR + `acrUseManagedIdentityCreds` | idem |

Si el pod/app queda en `ImagePullBackOff`, casi siempre falla el pull: falta AcrPull o la imagen/tag no existen. Vincular después: `az aks update -g <rg> -n <aks> --attach-acr <acr>`.

## Comprobaciones (solo lectura)
```bash
az acr show -g <rg> -n <acr> --query "{sku:sku.name, login:loginServer, admin:adminUserEnabled}" -o table
az acr repository show-tags -n <acr> --repository <imagen> -o tsv
az role assignment list --scope $(az acr show -g <rg> -n <acr> --query id -o tsv) --query "[].{rol:roleDefinitionName, tipo:principalType}" -o table
```
Esperado: `Basic` con su `…azurecr.io`; el tag `latest`; y, una vez vinculado el servicio, una fila `AcrPull` / `ServicePrincipal`. Si falta `AcrPull`: el servicio aún se está creando o la vinculación falló (usar el `update` de arriba).

## Examen
Build en la nube (`az acr build`) frente a build local; pull por identidad (`AcrPull`) frente a admin user o `imagePullSecrets`; cuándo usar `--attach-acr`.
