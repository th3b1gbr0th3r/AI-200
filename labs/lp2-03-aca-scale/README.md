# Lab LP2-03 · Configure autoscaling for an API using KEDA (plataforma: Lab 5 · AI-200-LP02M03, «Scale containers in ACA»)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/03-aca-scale-containers.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)). Módulo en MS Learn: https://learn.microsoft.com/es-es/training/modules/scale-containers-azure-container-apps/
- **Estado (29/10/2026): parcial.** Hechos Task 1 (despliegue), Task 2 (regla HTTP) y Task 3 (carga y escalado 1 → 3 → 5 réplicas). **No hecho:** Task 4 (escalado desde YAML): el grupo se borró antes. **Cleanup lanzado pero no verificado:** última lectura `Deleting` (~20 min después del `delete`); al día siguiente la sesión de `az` había caducado (`AADSTS130507`). El alumno lo da por realizado (30/10).
- **Conversación con Claude Code:** no se conserva (anterior a la exportación). Sesión del día: [`sesiones/2026-10-29-sesion-03-container-apps.md`](../../sesiones/2026-10-29-sesion-03-container-apps.md).
- Lab anterior: [LP2-02](../lp2-02-aca-manage/README.md) · Lab siguiente: [LP3-01](../lp3-01-aks-deploy/README.md).
- Material: `aca-scale-python.zip` (original sin editar), `azdeploy.py` (editado), `api/` (la API simulada), `client/` (dashboard de carga) y `.env`/`.env.ps1` (sin claves; cuenta temporal ya destruida). Origen MIT: [`../NOTICE.md`](../NOTICE.md). Qué hace el script por dentro: [`scripts/lp2-03-aca-scale/README.md`](../../scripts/lp2-03-aca-scale/README.md). Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

Ejecutado en Linux (bash); la plataforma da los mismos pasos en PowerShell. Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Sin IDs de suscripción/tenant ni usuario del lab; sufijos hash como `<hash>`. Prompt abreviado a `$`.

## Qué se construye y para qué
**Objetivo en cristiano:** ver con tus ojos el **autoescalado horizontal** de Container Apps. La app arranca con 1 réplica fija; se le pone una regla «una réplica más por cada 10 peticiones simultáneas» (KEDA por debajo, sin instalar nada), se le mete carga desde tu PC y se cuenta cómo suben las réplicas. Es el lab que más gustó al docente.

```
azdeploy.py 1 → rg-ai200-aca-scale + ACR acr<hash> + imagen agent-api:v1
azdeploy.py 2 → environment aca-env-<hash> (+ Log Analytics)
azdeploy.py 3 → app agent-api (identidad + AcrPull), min 1 / max 1, puerto 8080, AGENT_DEFAULT_DELAY_MS=500 → revisión 0000001
Task 2 → regla http-scaling: min 0, max 10, 10 peticiones concurrentes/réplica → revisión 0000002
Task 3 → client/ (en tu PC) lanza 25 workers contra POST /agent/process → réplicas 1 → 3 → 5
Task 4 → exportar a YAML y ajustar scale (cooldown 200, max 5, min 1)        [no hecho]
```

### Qué contiene la aplicación
- **`api/`** (la app desplegada, Flask + gunicorn, puerto **8080**): `GET /` (estado y estadísticas) y `POST /agent/process`, que **espera `delayMs` ms** (`time.sleep`, 500 por defecto) antes de responder. Es una simulación: no llama a ningún modelo. El retraso es deliberado: hace que las peticiones **se solapen**, que es justo lo que mide la regla.
- **`client/`** (el generador de carga, corre en **tu PC**, no en Azure): dashboard Flask en `http://127.0.0.1:5000`. Con **Start** lanza N workers asíncronos (`aiohttp`; `concurrency` 25 por defecto, hasta 500) que durante `durationSeconds` (30 por defecto, hasta 600) hacen `POST …/agent/process` en bucle. Para mostrar las réplicas llama a `az containerapp replica list` con tu sesión de `az`, y lee `RESOURCE_GROUP`, `CONTAINER_APP_NAME` y `CONTAINER_APP_URL` del entorno (`source .env` antes).
- **Importante:** el generador **no crea réplicas**. Solo manda tráfico simultáneo; quien crea réplicas es Container Apps (KEDA) al ver más peticiones concurrentes.

**Traducción a Kubernetes:** réplica ≈ pod; la regla HTTP ≈ un `ScaledObject` de KEDA con escalador HTTP (o un HPA con métrica personalizada), pero ya incluido y configurado con `--scale-rule-*`; el generador ≈ `hey`/`k6`/`ab` contra un Service.

**Para el examen:** réplicas ≈ peticiones concurrentes ÷ umbral (10), acotado por min/max; CPU y memoria **no** escalan a 0, HTTP y KEDA sí; `cooldownPeriod` retrasa el escalado hacia abajo; cron + HTTP para pre-escalar (M3-2 del knowledge check). Repaso: con umbral 10, 50 concurrentes sostenidas y `maxReplicas 10` → **5** réplicas.

### Diferencias de la plataforma respecto a la guía oficial
Solo `rg` y `location` (usamos `rg-ai200-aca-scale` y `eastus`). En este lab **no** hay cambio de modelo (`gpt-5.1`) ni `TPM_LIMIT`: el zip no menciona ningún modelo.

---

## Paso 0 · Preparar la terminal, iniciar sesión y extensiones
**Por qué:** igual que en LP2-01: `REQUESTS_CA_BUNDLE` por el proxy de empresa (en **cada** terminal, también en la del dashboard), login interactivo por el Temporary Access Pass y las extensiones de `az`.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az login --use-device-code
az extension add --name containerapp && az extension add --name log-analytics
```
Salida: no guardada. Esperado: suscripción `XLabs-…` del tenant «Lab Directory»; las extensiones no imprimen nada.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, tenant:tenantDisplayName}" -o table
az extension list --query '[].name' -o tsv
```
Suscripción `XLabs-…` y `containerapp`, `log-analytics`. Si falta algo, repite el comando correspondiente (sin `!` delante, ver LP2-01 paso 0). Proveedores: como en el [paso 3 del LP2-01](../lp2-01-aca-deploy/README.md#paso-3--registrar-los-proveedores-de-recursos).

## Paso 1 · Editar `azdeploy.py`
**Por qué:** grupo y región propios; es lo único que se toca en este zip.
```bash
cd ~/claude/AI-200-Developing/labs/lp2-03-aca-scale
grep -nE '^(rg|location) =' azdeploy.py
```
Resultado (fichero ya editado, tal como está versionado):
```text
5:rg = "rg-ai200-aca-scale"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
```
✅ **Comprobación:** esas dos líneas. Si sigue `<your-…>`, edítalo a mano.

## Paso 2 · ACR e imagen (opción 1)
**Por qué:** igual que en los labs anteriores: ACR sin admin y build en la nube con `az acr build` (sin Docker local).
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este script:
```text
1 → resource group + ACR + az acr build de api/ (agent-api:v1)
2 → Container Apps environment (con su Log Analytics)
3 → container app agent-api (identidad + AcrPull); genera .env y .env.ps1
4 → estado: ACR, imagen, environment, app, identidad y réplicas
5 → salir
```
Salida: no guardada.

⚠️ **Lo que pasó:** el script «se cortó» mientras lanzaba el build: una conexión larga a Azure interrumpida por el proxy de empresa (re-firma el TLS). El build ya se había lanzado **en Azure**, así que no hubo que repetirlo: se comprobó con `az` y se siguió con la opción 2.

✅ **Comprobación:**
```bash
az acr task list-runs --registry <acr> -o table
az acr repository show-tags -n <acr> --repository agent-api -o tsv
```
Última run `Succeeded` y tag `v1`. Si la run sigue `Running`, espera; si `Failed`, `az acr task logs --registry <acr> --run-id <id>` y relanza la opción 1.

## Paso 3 · Environment (opción 2)
**Por qué:** el «cluster gestionado» donde vivirá la app.
```bash
python3 azdeploy.py      # menú → 2
```
Salida: no guardada.

⚠️ **Lo que pasó:** igual que en LP2-02, la opción 2 se quedó esperando más de 5-10 min con el environment ya `Succeeded`. Arreglo: `Ctrl+C`, comprobar el estado y relanzar en la opción 3.

✅ **Comprobación:**
```bash
az containerapp env list -g rg-ai200-aca-scale --query "[].{name:name, state:properties.provisioningState}" -o tsv
```
Esperado: `aca-env-<hash>	Succeeded`. Si sale `Waiting`, espera antes de la opción 3 (si no, `ManagedEnvironmentNotProvisioned`).

## Paso 4 · Crear la app con 1 réplica fija (opción 3) y ver el estado (opción 4)
**Por qué:** la opción 3 crea `agent-api` con `--registry-identity system --system-assigned` (pull sin credenciales; además el script hace un `az role assignment create` de `AcrPull`), `--target-port 8080`, **`--min-replicas 1 --max-replicas 1`** (a propósito: sin escalado, para que luego se note la regla) y `AGENT_DEFAULT_DELAY_MS=500`. Después escribe el `.env`.
```bash
python3 azdeploy.py      # menú → 3, luego 4, luego 5
```
Salida real de la opción 4:
```text
Checking deployment status...

Container Apps Environment (aca-env-<hash>):
  Status: Succeeded
  Container Apps environment is ready

Azure Container Registry (acr<hash>):
  Status: Succeeded
  ACR is ready
  Container image: agent-api:v1

Container App (agent-api):
  Status: Succeeded
  System-assigned identity configured
  Ingress FQDN: agent-api.<dominio-del-environment>.eastus.azurecontainerapps.io
  Running replicas: 1
```
**Qué mirar:** todo `Succeeded`, identidad configurada y **1 réplica**: el punto de partida.

✅ **Comprobación (con `az`):**
```bash
az containerapp replica list -n agent-api -g rg-ai200-aca-scale --query "length(@)" -o tsv
```
Esperado: `1`. Si la app quedó con imagen `quickstart` y sin registry (create interrumpido): `az containerapp show -n agent-api -g rg-ai200-aca-scale --query "{image:properties.template.containers[0].image, registries:properties.configuration.registries}"` y arreglar con `az containerapp registry set` + `az containerapp update --image …`.

## Paso 5 · Cargar `.env` y probar la API
**Por qué:** los comandos siguientes y el dashboard leen las variables del `.env` (`RESOURCE_GROUP`, `ACA_ENVIRONMENT`, `CONTAINER_APP_NAME`, `CONTAINER_APP_FQDN`, `CONTAINER_APP_URL`, `CONTAINER_IMAGE`, `LOCATION`). La guía comprueba la API con un `curl` al endpoint público (no hay alternativa `az` para la petición HTTP, y el proxy no la bloquea).
```bash
source .env
echo "RG=[$RESOURCE_GROUP] APP=[$CONTAINER_APP_NAME]"
curl -sS -m 20 "$CONTAINER_APP_URL/" | head
```
Salida: no guardada. Esperado: `RG=[rg-ai200-aca-scale] APP=[agent-api]` y una respuesta JSON del agente simulado.

✅ **Comprobación:** corchetes con valor y JSON de la API. Si salen corchetes vacíos, el `source .env` no se hizo **en esta terminal** (ver incidencia del paso 6).

## Paso 6 · Añadir la regla de escalado HTTP (Task 2)
**Por qué:** es el corazón del lab. KEDA (gestionado) consulta cada `pollingInterval` (30 s) las peticiones concurrentes y pide `concurrentes ÷ 10` réplicas, entre 0 y 10. `--min-replicas 0` permite escalar a cero sin tráfico. Cambiar el escalado es cambiar la **plantilla**, así que crea revisión.
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
    --min-replicas 0 --max-replicas 10 \
    --scale-rule-name http-scaling --scale-rule-type http --scale-rule-http-concurrency 10
```
⚠️ **Lo que pasó:** el primer intento falló:
```text
argument --name/-n: expected one argument
```
`expected one argument` en `-n` = `$CONTAINER_APP_NAME` **vacía**: el comando se lanzó en una terminal nueva, donde las variables del `.env` no existen. Arreglo: `source .env`, comprobar con `echo "RG=[$RESOURCE_GROUP] APP=[$CONTAINER_APP_NAME]"` y relanzar. El reintento devolvió el JSON de la app (no guardado; el resultado se ve en el paso 7). Aviso que se ignora: `The behavior of this command has been altered by the following extension: containerapp`.

✅ **Comprobación:** el paso siguiente.

## Paso 7 · Comprobar la regla y la revisión nueva
**Por qué:** confirmar en la definición de la app que la regla quedó como se quería (no fiarse de que el comando «no dio error»).
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.scale" -o json
az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
```
Salida real:
```text
{
  "cooldownPeriod": 300,
  "maxReplicas": 10,
  "minReplicas": 0,
  "pollingInterval": 30,
  "rules": [
    {
      "http": {
        "auth": [],
        "metadata": {
          "concurrentRequests": "10"
        }
      },
      "name": "http-scaling"
    }
  ]
}

CreatedTime                Active    Replicas    TrafficWeight    HealthState    ProvisioningState    Name
-------------------------  --------  ----------  ---------------  -------------  -------------------  ------------------
2026-10-29T20:13:04+00:00  True      1           100              Healthy        Provisioned          agent-api--0000002
```
**Qué mirar:** `minReplicas 0`, `maxReplicas 10`, regla `http-scaling` con `concurrentRequests: "10"`, `cooldownPeriod 300` (5 min para bajar) y `pollingInterval 30`. La revisión `0000002` lleva el 100 %.

⚠️ **Trampa:** con `minReplicas 0` y sin tráfico durante el `cooldownPeriod` (300 s) la app llega a **cero réplicas**; el primer acceso después sufre un *cold start* de unos segundos.

✅ **Comprobación:** los cuatro valores y la `0000002`. Si `rules` sale `null`, el `update` no se aplicó: repite el paso 6 con las variables cargadas.

## Paso 8 · Arrancar el generador de carga (Task 3)
**Por qué:** hace falta tráfico **simultáneo** para que la regla actúe, y Azure no trae un generador: es un script local. No hay alternativa `az` para generar carga; el dashboard solo usa `az` para leer réplicas. Va en **otra terminal**, así que esa terminal necesita su propio `export REQUESTS_CA_BUNDLE` y `source .env`.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
cd ~/claude/AI-200-Developing/labs/lp2-03-aca-scale
source .env
cd client
python3 -m venv .venv && source .venv/bin/activate
pip install -q -r requirements.txt
python3 app.py
```
Salida real:
```text
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
**Qué mirar:** el dashboard escucha en `127.0.0.1:5000`. `client/.venv` **no se versiona** (`.gitignore`).

✅ **Comprobación:** abre http://127.0.0.1:5000 y pulsa **Refresh Revisions & Replicas**: debe mostrar 1 réplica (o 0 si ya escaló a cero). Si sale `Missing RESOURCE_GROUP or CONTAINER_APP_NAME`, falta el `source .env` en esa terminal; si no aparece `(.venv)` en el prompt, repite `source .venv/bin/activate`.

## Paso 9 · Generar carga y ver subir las réplicas
**Por qué:** es la prueba: más concurrencia → más réplicas. Se cuenta con `az` (lo fiable, independiente del dashboard).
En el dashboard: **Start** (25 workers, `delayMs 500`, 30 s) → **Refresh Revisions & Replicas** cada 5-10 s. En la primera terminal:
```bash
az containerapp replica list -n agent-api -g rg-ai200-aca-scale --query "length(@)" -o tsv
```
Salida real (durante la carga):
```text
5
```
**Qué mirar:**
- De **1** réplica a **3** y después **5** (todas `Running`), con ~950-1.200 peticiones por ronda, todas correctas, **0 fallidas** (datos del panel *Load Run*; captura no guardada).
- No es exactamente `25 ÷ 10 ≈ 3`: la carga se lanzó **varias veces** y el escalador mide con margen. Lo que cuenta es la relación: más concurrencia, más réplicas. Con más concurrencia (p. ej. 100) debería llegar al máximo de 10.
- El `delayMs` es clave: sin él las peticiones no se solapan y no escala.
- Bajar es lento: tras parar la carga, unos 5 min (`cooldownPeriod 300`) hasta volver a 0.

✅ **Comprobación:** el número sube por encima de 1 durante la carga. Para ver el estado de cada una: `--query "[].properties.runningState" -o tsv` (`Running`/`NotRunning`). Si no escala: sube `delayMs` (500-1500 ms) y la concurrencia, revisa la regla (paso 7) y mira eventos de plataforma con `az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --type system --tail 50`.

Al acabar: cierra el navegador y `Ctrl+C` en la terminal del dashboard.

## Paso 10 · Escalado desde YAML (Task 4) — no hecho
**Por qué:** en un equipo la configuración vive en ficheros versionados, no en comandos sueltos; `--yaml` aplica la definición completa (≈ `kubectl apply -f`).
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --output yaml > app-config.yaml
# editar properties > template > scale:
#   scale:
#     cooldownPeriod: 200
#     maxReplicas: 5
#     minReplicas: 1
#     pollingInterval: 30
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --yaml app-config.yaml
```
Esperado según la guía: el `update` termina sin error (revisión nueva) y el `scale` queda con cooldown 200 s, máximo 5 y siempre 1 réplica.

✅ **Comprobación:**
```bash
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.scale" -o json
```
`cooldownPeriod 200`, `maxReplicas 5`, `minReplicas 1`. Si el `update` falla: revisa la indentación y quita propiedades de solo lectura (`id`, `systemData`, `type`); el bloque debe estar en `properties > template > scale`.

---

## Cleanup (obligatorio al acabar)
**Por qué:** coste y entorno temporal. Antes, para el dashboard (`Ctrl+C`). La sesión de `az` se había cortado, así que hubo que reautenticarse (Temporary Access Pass, no se guarda) y hacer inventario antes de borrar.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt && az login
az account show --query "{usuario:user.name, sub:name}" -o table
az group list --query "[?starts_with(name,'rg-ai200')].name" -o tsv
az resource list -g rg-ai200-aca-scale -o table
az group delete --name rg-ai200-aca-scale --no-wait --yes
az group list --query "[?starts_with(name,'rg-ai200')].[name,properties.provisioningState]" -o table
```
Salida real:
```text
[1] *  XLabs-245   <sub-id>   Lab Directory

Usuario                     Sub
--------------------------  ---------
<usuario-del-lab>           XLabs-245

rg-ai200-aca-scale

Name                             ResourceGroup       Location    Type                                      Status
-------------------------------  ------------------  ----------  ----------------------------------------  ---------
acr<hash>                        rg-ai200-aca-scale  eastus      Microsoft.ContainerRegistry/registries    Succeeded
workspace-rgai200acascale<sufijo> rg-ai200-aca-scale  eastus      Microsoft.OperationalInsights/workspaces  Succeeded
aca-env-<hash>                   rg-ai200-aca-scale  eastus      Microsoft.App/managedEnvironments         Succeeded
agent-api                        rg-ai200-aca-scale  eastus      Microsoft.App/containerApps               Succeeded

(az group delete: sin salida)

Column1             Column2
------------------  ---------
rg-ai200-aca-scale  Deleting
```
Comprobación posterior (~20 min después del `delete`):
```text
$ az group list -o table
Name                Location    Status
------------------  ----------  --------
rg-ai200-aca-scale  eastus      Deleting
```
**Qué mirar:**
- Solo quedaba el grupo de este lab, con sus 4 recursos (ACR, workspace, environment y app). Los grupos de LP2-01 (`rg-ai200-aca`) y LP2-02 (`rg-ai200-aca-manage`) ya no existían: la plataforma los había desprovisionado.
- `--no-wait` devuelve el prompt sin esperar: el borrado se comprueba aparte (`Deleting` → desaparece).

**Estado real: no verificado.** La última lectura fue `Deleting`. Al día siguiente (30/10) la sesión de `az` había caducado (`AADSTS130507`) y no se pudo repetir. **El alumno da el cleanup por realizado.**

✅ **Comprobación:** `az group exists --name rg-ai200-aca-scale` → `false`. Si sale `true` pasados 15-20 min: `az group show -n rg-ai200-aca-scale --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`. Si `az` da `AADSTS…`/`AuthorizationFailed`, las credenciales del lab caducaron: anótalo como no verificado.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| El script «se cortó» al lanzar el build del ACR | Conexión larga interrumpida por el proxy de empresa | Paso 2: el build ya corría en Azure; comprobar con `az acr task list-runs` y `show-tags` y seguir con la opción 2 |
| Opción 2 esperando >5-10 min con el environment ya `Succeeded` | La llamada a Azure quedó colgada | Paso 3: `Ctrl+C`, comprobar `provisioningState`, relanzar en la opción 3 |
| `argument --name/-n: expected one argument` | `$CONTAINER_APP_NAME` vacía: `.env` sin cargar en esa terminal | Paso 6: `source .env` y `echo "RG=[…] APP=[…]"` |
| `The behavior of this command has been altered by the following extension: containerapp` | Aviso de la extensión preview | Se ignora |
| Sesión de `az` cortada antes del cleanup | Caducó el login del usuario temporal | Cleanup: reautenticar (TAP, login interactivo) y repetir el `export` del proxy |
| No se pudo verificar el borrado al día siguiente (`AADSTS130507`) | Credenciales del lab caducadas | Cleanup: documentado como no verificado |

## Anexo · Cómo `azdeploy.py` crea el ACR y lo vincula
Explicación general: [`../acr-en-azdeploy.md`](../acr-en-azdeploy.md). En este lab:
| Paso | Comando `az` | Detalle en este script |
|---|---|---|
| Crear el ACR | `az acr create` (L149) | `--sku Basic`, `--admin-enabled false` |
| Subir la imagen | `az acr build` (L166) | build en la nube |
| Vincular (pull) | `--registry-identity system` (L256) y `az role assignment create` (L292) | identidad system-assigned y `AcrPull` garantizado explícitamente |
- **Push y pull son permisos distintos:** el build lo hace ACR con tu `az login`; la descarga la hace la app con su identidad y el rol **AcrPull**.
- **Comprobar el vínculo:** `az role assignment list --scope <id-ACR> --query "[?roleDefinitionName=='AcrPull']" -o table` (una fila).
- **Si no descarga la imagen** (`ImagePullBackOff`): falta `AcrPull` o la imagen/tag no existe → `az acr repository show-tags -n <acr> --repository agent-api -o tsv`.
