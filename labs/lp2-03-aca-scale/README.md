# Lab LP2-03 · Configure autoscaling for an API using KEDA (Scale containers in Azure Container Apps)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-container-apps/03-aca-scale-containers.html
Documentación del módulo (MS Learn): https://learn.microsoft.com/es-es/training/modules/scale-containers-azure-container-apps/
Material de partida: `aca-scale-python.zip` (original, sin editar) y sus ficheros extraídos: `azdeploy.py` (editado), `api/` (la API simulada) y `client/` (dashboard Flask de carga). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Qué hace cada comando del script: [`scripts/lp2-03-aca-scale/README.md`](../../scripts/lp2-03-aca-scale/README.md). **Salidas reales de los comandos, saneadas: [`salidas.md`](salidas.md).** Notas de clase: [`docs/modulos/02-container-apps.md`](../../docs/modulos/02-container-apps.md).

Ejecutado en Linux (bash) contra la suscripción temporal del lab (29/10/2026). La plataforma del curso da los mismos pasos en PowerShell.

## Objetivo
Configurar el **autoescalado horizontal** de una container app con una regla HTTP (KEDA por debajo), generar carga y **ver cómo suben las réplicas**, y después ajustar el escalado desde un fichero YAML.

## Qué se construye
```
azdeploy.py (1) → resource group + ACR + imagen agent-api:v1
azdeploy.py (2) → Container Apps environment (+ Log Analytics workspace)
azdeploy.py (3) → container app "agent-api" (identidad gestionada + AcrPull), min 1 / max 1 réplica, AGENT_DEFAULT_DELAY_MS=500
Task 2          → regla HTTP: min 0, max 10, 10 peticiones concurrentes por réplica   → revisión 0000002
Task 3          → dashboard local (client/) genera carga → las réplicas suben (1 → 5)
Task 4          → exportar config a YAML y ajustar scale (cooldown 200, max 5, min 1)   [no ejecutada]
```

## Qué contiene la aplicación
- **`api/`** (la app desplegada, Flask + gunicorn, puerto **8080**): `GET /` (estado y estadísticas), `POST /agent/process`, que **espera `delayMs` milisegundos** (`time.sleep`) antes de responder, 500 por defecto. Es una simulación: no llama a ningún modelo. El retraso es deliberado: hace que las peticiones se solapen y se acumulen peticiones concurrentes, que es lo que mide la regla.
- **`client/`** (el generador de carga, corre en **tu máquina**, no en Azure): dashboard Flask en `http://127.0.0.1:5000`. Con **Start** lanza N workers asíncronos (`aiohttp`, `concurrency`, 25 por defecto, hasta 500) que durante `durationSeconds` (30 por defecto, hasta 600) hacen `POST …/agent/process` en bucle. Consulta las réplicas llamando a `az containerapp replica list`, por eso lee `RESOURCE_GROUP` y `CONTAINER_APP_NAME` de las variables de la terminal (`source .env` antes de arrancarlo) y usa tu sesión de `az`.
- **Importante:** el generador **no crea pods**. Solo manda tráfico simultáneo; quien crea las réplicas es Container Apps (KEDA) al ver más peticiones concurrentes.

## Diferencias de la plataforma respecto a la guía oficial
La plataforma indicó `rg` y `location` (usamos `rg-ai200-aca-scale` y `eastus`). En este lab **no** hay cambios de modelo (`gpt-5.1`) ni `TPM_LIMIT`: el zip no menciona ningún modelo.

## Cómo se relaciona con lo que ya sabes (K8s) y con el examen
- Réplica ≈ **pod**. La regla HTTP ≈ un **`ScaledObject` de KEDA** con el escalador HTTP; en Container Apps no se instala nada: viene incluido y se configura con `--scale-rule-*`.
- El generador de carga ≈ `hey`/`k6`/`ab` contra un Service.
- Examen: réplicas = peticiones concurrentes ÷ umbral (10), acotado por min/max; CPU y memoria **no** escalan a 0, HTTP y KEDA sí; `cooldownPeriod` retrasa el escalado hacia abajo; cron + HTTP para pre-escalar (M3-2 del test).

## Comandos ejecutados (en orden)
Los que crean o modifican recursos los lanza el alumno.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt   # antes de CUALQUIER az, en cada terminal
az login --use-device-code
az extension add --name containerapp && az extension add --name log-analytics
python3 azdeploy.py            # 1, 2, 3 y 5
source .env

# Task 2 · regla de escalado HTTP
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
    --min-replicas 0 --max-replicas 10 \
    --scale-rule-name http-scaling --scale-rule-type http --scale-rule-http-concurrency 10
az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.scale" -o json

# Task 3 · generador de carga (terminal aparte, con source .env hecho)
cd client && python3 -m venv .venv && source .venv/bin/activate
pip install -q -r requirements.txt && python3 app.py       # http://127.0.0.1:5000
az containerapp replica list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "length(@)" -o tsv
```

## Comandos al detalle

### 1. `python3 azdeploy.py` (opciones 1, 2, 3, 5)
Desglose en [`scripts/lp2-03-aca-scale/README.md`](../../scripts/lp2-03-aca-scale/README.md). La opción 3 crea la app con `--min-replicas 1 --max-replicas 1`: arranca con **una sola réplica y sin escalado**, para que después se vea el efecto de la regla.

### 2. Regla de escalado HTTP
```bash
az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
    --min-replicas 0 --max-replicas 10 \
    --scale-rule-name http-scaling --scale-rule-type http --scale-rule-http-concurrency 10
```
```
az containerapp update            → modifica la plantilla; crea una revisión nueva
--min-replicas 0                  → permite escalar a cero cuando no hay tráfico
--max-replicas 10                 → tope de réplicas
--scale-rule-name http-scaling    → nombre de la regla
--scale-rule-type http            → regla por peticiones HTTP
--scale-rule-http-concurrency 10  → una réplica más por cada 10 peticiones concurrentes
```
- **Qué hace:** KEDA (gestionado por la plataforma) consulta cada 30 s (`pollingInterval`) las peticiones concurrentes y pide `concurrentes ÷ 10` réplicas, entre 0 y 10.
- **Comprobación:** `az containerapp show … --query "properties.template.scale"` debe listar la regla `http-scaling` con `concurrentRequests: "10"`, `minReplicas 0`, `maxReplicas 10`; y `revision list` una revisión nueva (`0000002`) con el 100 % del tráfico. Los cambios de escalado van en la plantilla, así que crean revisión.
- **Resultado real:** ver [`salidas.md`](salidas.md), sección 3.
- **Trampa:** con `minReplicas 0` y sin tráfico durante el `cooldownPeriod` (300 s) la app llega a **cero réplicas**; el primer acceso tras eso sufre un *cold start* de unos segundos.

### 3. Generador de carga y observación de las réplicas
- Arranque del dashboard: `cd client && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python3 app.py`. El entorno virtual `client/.venv` **no se versiona** (está en `.gitignore`).
- En `http://127.0.0.1:5000`: **Refresh Revisions & Replicas** → **Start** → refrescar cada 5-10 s.
- **Comprobación independiente:** `az containerapp replica list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "length(@)" -o tsv` (o `--query "[].properties.runningState"` para ver `Running`/`NotRunning`).
- **Resultado real:** carga de **25 workers**, `delayMs 500`, 30 s → ~950-1.200 peticiones, todas correctas, **0 fallidas**; las réplicas subieron de **1 a 3** y después a **5** (todas `Running`). Con más concurrencia (p. ej. 100) debería llegar al máximo de 10.
- **Por qué no son exactamente `25 ÷ 10`:** la carga se lanzó varias veces y el escalador mide con margen; lo que cuenta es la relación (más concurrencia, más réplicas).
- **Si no escala:** subir `delayMs` (500-1500 ms) y la concurrencia; revisar la regla con `az containerapp show --query "properties.template.scale"`; eventos de plataforma con `az containerapp logs show --type system --tail 50`.

### 4. Escalado desde YAML — no ejecutada
Según la guía: `az containerapp show … --output yaml > app-config.yaml`, ajustar en `properties > template > scale` (`cooldownPeriod: 200`, `maxReplicas: 5`, `minReplicas: 1`, `pollingInterval: 30`) y aplicar con `az containerapp update … --yaml app-config.yaml`. Si falla, quitar propiedades de solo lectura (`id`, `systemData`, `type`) y revisar la indentación.

## Resultados
- Despliegue base correcto: 1 réplica, revisión `0000001` sana, pull por identidad `system`.
- Regla `http-scaling` aplicada (revisión `0000002`) y **escalado verificado**: 1 → 3 → 5 réplicas con carga, 0 peticiones fallidas.
- YAML: no ejecutada (el grupo se borró antes de hacerla).
- Cleanup: `az group delete --name rg-ai200-aca-scale --no-wait --yes` lanzado por el alumno; estado `Deleting` ([`salidas.md`](salidas.md), sección 6). La comprobación del día siguiente no fue posible (sesión de `az` caducada); última lectura: `Deleting`.

## Incidencias y soluciones
| Síntoma | Causa | Arreglo |
|---|---|---|
| El script «se cortó» al lanzar el ACR | Conexión larga a Azure interrumpida (el proxy Netskope re-firma el TLS) | El build ya estaba hecho en Azure: comprobar con `az acr task list-runs` y `az acr repository show-tags`, y seguir con la opción 2 |
| Opción 2 esperando más de 5-10 min con el environment ya `Succeeded` | La llamada a Azure quedó colgada | `Ctrl+C`, comprobar `provisioningState`, relanzar y elegir la opción 3 |
| `argument --name/-n: expected one argument` | `$CONTAINER_APP_NAME` vacía: el `.env` no estaba cargado en esa terminal | `source .env` y comprobar con `echo "RG=[$RESOURCE_GROUP] APP=[$CONTAINER_APP_NAME]"` |
| `The behavior of this command has been altered by the following extension: containerapp` | Aviso de la extensión preview | Se ignora |

## Cleanup (obligatorio, lo ejecuta el alumno)
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-aca-scale --no-wait --yes
az group exists --name rg-ai200-aca-scale        # repetir hasta false
```
Solo se borra el grupo del lab. Antes: parar el dashboard (`Ctrl+C`) y cerrar el navegador.
