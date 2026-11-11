# Lab LP5-01 · Build an agent tool backend (plataforma: Lab 12 · AI-200-LP05M01)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html
- **Estado (10/11/2026): completado.** Servidor `Ready`, esquema creado, `test_workflow.py` correcto (upsert verificado) y las 4 consultas de la Task 7. **Cleanup: borrado lanzado (`Deleting`), no verificado a `false`**: al cerrar el lab, la sesión de `az` caducó (`No subscription found`).
- **Conversación completa con Claude Code:** [`01-lab12-pg-agent-backend.md`](../../sesiones/conversaciones/2026-11-10-sesion-06/01-lab12-pg-agent-backend.md).
- Lab siguiente: [LP5-02 · vector search](../lp5-02-pg-vector-search/README.md). Origen MIT de `azdeploy.py` y `agent-backend/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Los IDs de suscripción se sustituyen por `<sub-id>`, el usuario del lab por `<usuario-del-lab>` y los UUID de sesión por `<uuid>`. Las horas de las salidas están en UTC (18:22 UTC = 19:22 en Madrid).

## Qué se construye
**El objetivo, en cristiano:** un agente de IA no recuerda nada entre llamadas. Para que pueda seguir una conversación o retomar una tarea a medias, alguien tiene que guardarle la memoria. En este lab esa memoria es una base de datos PostgreSQL con tres tablas (conversaciones, mensajes y *checkpoints* de tareas) y unas funciones Python que el agente usaría como herramientas (*tools*) para leer y escribir en ella.

```
azdeploy.py 1 → RG ai200rg + Flexible Server psql-agent-<hash>  (Standard_D2ds_v4, PG 16, centralus)
                → admin de Entra = tu usuario → contraseñas desactivadas (solo Entra)
                → regla de firewall AllowAll 0.0.0.0-255.255.255.255
azdeploy.py 2 → comprueba: Ready, acceso público, admin de Entra, regla
azdeploy.py 3 → .env con DB_HOST, DB_NAME=postgres, DB_USER y PGPASSWORD (token de Entra, ~1 h)
psql          → CREATE DATABASE agent_memory + sql/schema.sql (3 tablas, 4 índices, 1 UNIQUE)

                ┌──────────────── BD agent_memory ─────────────────┐
agent_tools.py  │ conversations ──< messages                        │
(las "tools")   │       │  (1 conversación tiene N mensajes)        │
  ──psycopg──►  │       └──────< task_checkpoints                   │
  token Entra   │          (1 conversación tiene N tareas; una fila │
                │           por tarea gracias al UNIQUE + upsert)   │
                └───────────────────────────────────────────────────┘
test_workflow.py → simula una conversación del agente y comprueba el upsert
sql/queries.sql  → 4 consultas de "contexto" que el agente usaría para decidir
```

**Las tres ideas que hay que llevarse:**
1. **Upsert** (`INSERT … ON CONFLICT … DO UPDATE`) ≈ `kubectl apply`: crea si no existe, actualiza si existe, y se puede repetir sin duplicar. Necesita un `UNIQUE`, que hace el papel de nombre + namespace.
2. **Sin contraseñas:** se entra con un token de Entra que caduca en una hora, como el token proyectado de un ServiceAccount.
3. **`ON DELETE CASCADE`** ≈ recolección por `ownerReferences`: borras la conversación y PostgreSQL borra sus mensajes y checkpoints.

---

## Paso 0 · Descargar el starter y preparar la terminal
**Por qué:** el lab trae un script de despliegue (`azdeploy.py`) y el código Python a medio hacer. La guía lo descarga con Edge en una VM Windows; aquí se hace con `curl` en Linux. `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa, y hay que exportarlo **en cada terminal nueva**.

```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-build-agent-python.zip
unzip -oq postgresql-build-agent-python.zip
find . -type f | grep -v '\.zip$'; which psql python3; python3 --version; psql --version
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
Salida real:
```text
./azdeploy.py
./agent-backend/test_workflow.py
./agent-backend/requirements.txt
./agent-backend/agent_tools.py
/usr/bin/psql
/usr/bin/python3
Python 3.12.3
psql (PostgreSQL) 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
```
**Qué mirar:** `psql` ya está instalado (la guía pide instalarlo) y no existe `python`, solo `python3` (fuera del `.venv`).

✅ **Comprobación:** deben salir los cuatro ficheros y las rutas de `psql` y `python3`. Si falta `psql`: `sudo apt install postgresql-client`.

> En el repo, `azdeploy.py` ya está editado con los valores de la plataforma (paso 5) y `agent_tools.py` ya está completado (paso 4). Si repites el lab desde el zip, esos pasos sí cambian los ficheros.

## Paso 1 · `az login` con el usuario del lab 12
**Por qué:** cada lab de la plataforma trae un usuario temporal y su propia suscripción. Todo lo que se cree debe ir a esa suscripción, no a la de la empresa. El *Temporary Access Pass* (TAP) que da la plataforma se escribe en la página de login donde iría la contraseña.

```bash
az login
```
Salida real:
```text
No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-079            <sub-id>                              Lab Directory

Select a subscription and tenant (Type a number or Enter for no changes): 1

Tenant: Lab Directory
Subscription: XLabs-079 (<sub-id>)
```
**Qué mirar:** tenant `Lab Directory` y una sola suscripción (`XLabs-079`): es la del lab. Con navegador disponible, `az login` funciona; sin él, `az login --use-device-code`.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Debe salir `XLabs-079` (o la suscripción que te toque) y el usuario del lab. Si sale la cuenta de empresa, `az logout` y repite el login en una ventana privada del navegador.

## Paso 2 · Registrar el proveedor de PostgreSQL
**Por qué:** una suscripción de Azure solo puede crear recursos de un tipo si su *resource provider* está registrado. Es como tener que instalar el CRD antes de crear objetos de ese tipo en Kubernetes.

```bash
az provider register --namespace Microsoft.DBforPostgreSQL
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
```
Salida real:
```text
Registered
```
**Qué mirar:** `Registered` a la primera: la suscripción del lab ya lo traía registrado.

✅ **Comprobación:** si sale `Registering`, espera 1-2 minutos y repite el `show`.

## Paso 3 · Primer intento: `eastus` + opción 1 → falla ⚠️
**Por qué:** `azdeploy.py` trae dos huecos (`<your-resource-group-name>` y `<your-azure-region>`). Se rellenaron con los valores habituales del repo **antes de leer la guía de la plataforma**, y ese fue el error.

```bash
sed -i 's/<your-resource-group-name>/rg-ai200-pg-agent/; s/<your-azure-region>/eastus/' azdeploy.py
head -6 azdeploy.py | grep -E '^(rg|location)'
python3 azdeploy.py      # menú → 1
```
Salida real:
```text
rg = "rg-ai200-pg-agent"  # Resource Group name
location = "eastus"   # Azure region for the resources
```
```text
Checking/creating resource group 'rg-ai200-pg-agent'...
Resource group created: rg-ai200-pg-agent

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
Error: Create PostgreSQL Flexible Server failed (exit code 1).
ERROR: The location is restricted from performing this operation.
```
⚠️ **Lo que pasó:** la suscripción del lab tiene una **política de Azure** (algo así como un `ValidatingAdmissionPolicy` de toda la suscripción) que solo deja crear PostgreSQL en `centralus` y con SKU `Standard_D2ds_v4`/`GeneralPurpose`. La guía pública no lo dice; la guía **de la plataforma** sí (Task 1).

**Qué mirar:**
- El resource group **sí** se crea (la política no limita la región de los grupos); el servidor no.
- El nombre del servidor (`psql-agent-` + 8 caracteres del SHA-1 de tu *object id*) no depende del grupo ni de la región: el relanzamiento usará el mismo.

✅ **Comprobación:** si te sale este error, no reintentes: sigue con el paso 5. Lección: **leer siempre la guía de la plataforma antes de editar `azdeploy.py`**.

## Paso 4 · Task 2: completar las tres *tools* de `agent_tools.py` (mientras se desplegaba)
**Por qué:** estas funciones son la interfaz entre el agente y la base de datos: el modelo no escribe SQL, llama a `create_conversation(…)` y la función hace el SQL. Se completaron mientras el primer despliegue estaba en marcha, porque no necesitan el servidor para escribirse.

En [`agent-backend/agent_tools.py`](agent-backend/agent_tools.py) se pegó el código de la guía entre cada marca `# BEGIN …` / `# END …`, sin sangría (las marcas están en la columna 0):

| Función | SQL clave | Qué hace y por qué |
|---|---|---|
| `create_conversation` | `INSERT … RETURNING id, session_id, started_at` | Abre una sesión del agente con un `uuid4` como `session_id`. `RETURNING` devuelve el `id` generado sin hacer otra consulta. El `metadata` se guarda como JSONB con `Json(...)`. |
| `get_conversation_history` | `ORDER BY created_at DESC LIMIT %s` + `reversed()` | Coge los **N mensajes más recientes** y los devuelve en orden cronológico: es el contexto que se le pasa al modelo. |
| `save_task_state` | `INSERT … ON CONFLICT (conversation_id, task_name) DO UPDATE SET … = EXCLUDED.…` | **El upsert.** La primera vez inserta el checkpoint; las siguientes lo actualizan. `EXCLUDED` es la fila que intentabas insertar. Así el agente puede retomar una tarea interrumpida. **Falla si no existe el `UNIQUE (conversation_id, task_name)`** (se crea en el paso 11). |

Ya venían hechas `get_connection()` (pide un token de Entra con `DefaultAzureCredential` y conecta con `sslmode=require` a `agent_memory`), `store_message()` y `get_task_state()`. Todas usan `%s`: los valores viajan como parámetros aparte, nunca pegados en el texto del SQL (sin inyección).

```bash
python3 -m py_compile agent-backend/agent_tools.py && echo OK
grep -n "^def " agent-backend/agent_tools.py
```
Salida real (la ejecutó Claude, con `echo SINTAXIS_OK`):
```text
SINTAXIS_OK
10:def get_connection():
23:def create_conversation(user_id: str, metadata: dict = None) -> dict:
45:def store_message(conversation_id: int, role: str, content: str, metadata: dict = None) -> dict:
65:def get_conversation_history(conversation_id: int, limit: int = 50) -> list:
93:def save_task_state(conversation_id: int, task_name: str, status: str, checkpoint_data: dict) -> dict:
119:def get_task_state(conversation_id: int, task_name: str) -> Optional[dict]:
```
✅ **Comprobación:** `OK` y **6 funciones**. Si sale `IndentationError`, la función se pegó con sangría: quítala.

## Paso 5 · Borrar el grupo vacío y poner los valores de la plataforma
**Por qué:** el grupo `rg-ai200-pg-agent` quedó creado y vacío; hay que borrarlo (regla del repo: no dejar nada) y corregir el script con lo que exige la política: RG `ai200rg`, región `centralus` y SKU `Standard_D2ds_v4`/`GeneralPurpose` (más caro que `Burstable`, pero trae PgBouncer integrado, que se ve en el módulo 3).

```bash
az resource list -g rg-ai200-pg-agent -o table
az group delete --name rg-ai200-pg-agent --yes --no-wait
sed -i 's/^rg = "rg-ai200-pg-agent"/rg = "ai200rg"/; s/^location = "eastus"/location = "centralus"/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```
Salida real:
```text
                                    ← az resource list: vacío (el grupo no tenía nada)
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
339:            "--sku-name", "Standard_D2ds_v4",
340:            "--tier", "GeneralPurpose",
```
**Qué mirar:** las cuatro líneas cambiadas. `az resource list` vacío = se puede borrar el grupo sin perder nada.

> Si repites el lab **desde el zip**, haz los cuatro cambios de una vez sobre los huecos originales:
> `sed -i 's/<your-resource-group-name>/ai200rg/; s/<your-azure-region>/centralus/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py`

✅ **Comprobación:**
```bash
az group exists --name rg-ai200-pg-agent
```
Debe salir `false` (se verificó a las 18:35: `false`). Si alguna línea del `grep` sigue con `rg-ai200-pg-agent`, `eastus`, `Standard_B1ms` o `Burstable`, el `sed` no la encontró: edítala a mano.

## Paso 6 · Crear el servidor (`azdeploy.py` → opción 1), ahora sí
**Por qué:** la opción 1 hace el trabajo de plataforma: crea el Flexible Server, nombra administrador de Entra a tu usuario, **desactiva las contraseñas** (solo se entra con token) y abre el firewall. Tarda de 5 a 10 minutos y **cuesta dinero desde que existe**.

```bash
python3 azdeploy.py      # menú → 1
```
Salida real:
```text
=====================================================================
    Azure Database for PostgreSQL Deployment Menu
=====================================================================
Resource Group: ai200rg
Server Name: psql-agent-dc48980e
Location: centralus
=====================================================================
1. Create PostgreSQL server with Entra authentication
2. Check deployment status
3. Retrieve connection info and access token
4. Exit
=====================================================================
Please select an option (1-4): 1

Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: <usuario-del-lab>
  Firewall rule: AllowAll
```
**Qué mirar:**
- La cabecera ya dice `ai200rg` / `centralus`: si no, sal con `4` y revisa el paso 5.
- Las cuatro fases: crear → admin de Entra → desactivar contraseña → firewall. El admin de Entra es el mismo usuario que hará de `DB_USER`.
- No salió `Waiting for Azure to release server name`: el intento fallido no llegó a reservar el nombre.

✅ **Comprobación** (en otra terminal, solo lectura, mientras se crea):
```bash
az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query state -o tsv
```
Pasa por `Provisioning`/`Updating` hasta `Ready`. Si da `ResourceNotFound`, aún no se ha registrado: repite en un minuto. Si el script falla con `restricted` o `RequestDisallowedByPolicy`, revisa los valores del paso 5.

## Paso 7 · ¿Sale el puerto 5432 por el proxy de empresa?
**Por qué:** `psql` y Python hablan **directamente** con el servidor por el 5432 (plano de datos): aquí no hay un `az … command invoke` que haga de puente, como sí lo hay con `kubectl`. Antes de seguir hay que saber si el proxy lo deja pasar; si no, el plan B es Azure Cloud Shell (trae `psql` y `az`).

```bash
timeout 5 bash -c '</dev/tcp/psql-agent-dc48980e.postgres.database.azure.com/5432' && echo "5432 ABIERTO" || echo "5432 BLOQUEADO"
```
Salida real:
```text
5432 ABIERTO
```
**Qué mirar:** el proxy de empresa (Netskope) suele desviar solo el tráfico web (80/443) a su inspección TLS. PostgreSQL negocia el TLS dentro de su propio protocolo en el 5432 y sale directo. `kubectl` contra AKS va por 443, la inspección rompe su TLS y por eso se bloquea.

✅ **Comprobación:** `5432 ABIERTO` → sigue en local. `5432 BLOQUEADO` → abre Cloud Shell, sube la carpeta del lab y sigue allí.

## Paso 8 · Task 3: estado (opción 2) y datos de conexión (opción 3)
**Por qué:** la opción 2 confirma los tres requisitos para conectar (servidor `Ready`, admin de Entra, regla de firewall). La opción 3 escribe el `.env` con los datos de conexión y un **token de Entra** como contraseña (`az account get-access-token --resource-type oss-rdbms`), que caduca en ~1 h. El `.env` hace de `Secret`: **no se sube al repo** (`.gitignore`: `labs/lp5-*/.env`).

```bash
python3 azdeploy.py      # menú → 2 → Enter → 3 → Enter → 4
```
Salida real (opción 2):
```text
Checking deployment status...

PostgreSQL Server (psql-agent-dc48980e):
  Status: Ready
  PostgreSQL server is ready
  Public access: Enabled
  Entra administrator: <usuario-del-lab>
  Firewall rule: AllowAll
```
Salida real (opción 3):
```text
Retrieving connection information...
Retrieving access token...

PostgreSQL Connection Information
===========================================================
Host: psql-agent-dc48980e.postgres.database.azure.com
Database: postgres
User: <usuario-del-lab>
Password: (Entra token - expires in ~1 hour)

Environment variables saved to .env and .env.ps1
```
**Qué mirar:** `Database: postgres` es la BD que trae todo servidor; `agent_memory` se crea en el paso 11. La «contraseña» no es una contraseña: es un token que caduca.

✅ **Comprobación:**
```bash
git check-ignore -v .env .env.ps1
```
Salida real: `.gitignore:16:labs/lp5-*/.env  .env` y `.gitignore:17:labs/lp5-*/.env.ps1  .env.ps1`. Si no sale nada, **no hagas commit**: el token acabaría en el repo público.

## Paso 9 · Cargar el `.env` y conectar con `psql`
**Por qué:** `psql` lee la contraseña de la variable `PGPASSWORD` si existe, así que basta con cargar el `.env` en la shell. `sslmode=require` obliga a cifrar (Azure lo exige). Para comprobar el token se mira que **existe**, sin mostrar su valor.

```bash
source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
```
Salida real:
```text
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres <usuario-del-lab>
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=>
```
**Qué mirar:** entra **sin pedir contraseña** (usa el token) y la conexión va con TLS 1.3. El prompt `postgres=>` dice en qué base de datos estás.

⚠️ **Lo que pasó:** se pegaron en la shell, de golpe, el `psql` y la línea `SELECT version();`: la consulta se perdió porque `psql` aún no había arrancado. Al intentar limpiar con `\r` y la consulta en el mismo pegado:
```text
postgres=> \r
SELECT version();
Query buffer reset (cleared).
\r: extra argument "SELECT" ignored
\r: extra argument "version();" ignored
```
Los comandos con barra (`\r`, `\c`, `\dt`, `\i`, `\q`) **se comen el resto de la línea como argumentos**: van siempre solos. Las sentencias SQL pueden ocupar varias líneas y se ejecutan al llegar al `;`. Si el prompt cambia a `postgres->` (guion), `psql` espera el final de una sentencia: `Ctrl+C`.

✅ **Comprobación:** prompt `postgres=>` y línea `SSL connection`. Si sale `password authentication failed`, el token no está cargado o caducó: opción 3 de nuevo y `source .env`.

## Paso 10 · Task 4: firewall, comprobado con `az` en vez del portal
**Por qué:** la guía de la plataforma manda revisar en el portal el acceso público y la regla `AllowAll`. Con `az` se ve lo mismo sin salir de la terminal (primero `az`). `AllowAll` (0.0.0.0-255.255.255.255) equivale a un `Service` `LoadBalancer` sin `loadBalancerSourceRanges`: abierto a todo Internet. Vale en un lab desechable con solo Entra; en el trabajo, tu IP o una VNet privada.

```bash
az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query network.publicNetworkAccess -o tsv
az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
```
Salida real:
```text
Enabled
unrecognized arguments: -n psql-agent-dc48980e
```
⚠️ **Lo que pasó:** en los subcomandos de reglas (`firewall-rule`, `parameter`) el servidor va con `--server-name`/`-s`; `-n` es el nombre de **la regla**. En `flexible-server show`, en cambio, `-n` sí es el servidor. Comando corregido:
```bash
az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
```
Salida real:
```text
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
```
El alumno lanzó además el `create` (no hacía falta, la regla ya la crea `azdeploy.py`):
```bash
az postgres flexible-server firewall-rule create -g ai200rg --server-name psql-agent-dc48980e --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
```
Salida real:
```text
{
  "endIpAddress": "255.255.255.255",
  "id": "/subscriptions/<sub-id>/resourceGroups/ai200rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-agent-dc48980e/firewallRules/AllowAll",
  "name": "AllowAll",
  "resourceGroup": "ai200rg",
  "startIpAddress": "0.0.0.0",
  "systemData": null,
  "type": "Microsoft.DBforPostgreSQL/flexibleServers/firewallRules"
}
```
**Qué mirar:** el `create` es **idempotente**: reescribe la misma regla con los mismos valores, como un `kubectl apply` repetido. La prueba definitiva de la Task 4 es que `psql` ya conectó en el paso 9.

✅ **Comprobación:** `Enabled` y la fila `AllowAll 0.0.0.0 255.255.255.255`. Si `publicNetworkAccess` sale `Disabled`, no se arregla con un `update` simple: el servidor se creó con red privada.

## Paso 11 · Task 5: crear la base `agent_memory` y el esquema
**Por qué:** el esquema es el «contrato» de la memoria: qué se guarda, con qué tipos y qué reglas (como el schema OpenAPI de un CRD, pero aplicado por la base de datos). El SQL de la guía se copió literal en [`sql/schema.sql`](sql/schema.sql) y se ejecuta con `\i`, para no pegar 40 líneas en `psql`.

Dentro de `psql` (cada línea por separado):
```text
SELECT version();
CREATE DATABASE agent_memory;
\c agent_memory
\i sql/schema.sql
\dt
\d task_checkpoints
```
**Qué crea `sql/schema.sql`:**

| Objeto | Para qué | Detalles que importan |
|---|---|---|
| `conversations` | Una fila por sesión del agente | `id BIGSERIAL` (autonumérico) como clave; `session_id UUID NOT NULL UNIQUE` (el identificador que ve la aplicación); `user_id`; `metadata JSONB` libre (como las *annotations*: cada uno guarda lo que quiera sin cambiar el esquema). |
| `messages` | El historial: cada mensaje de la conversación | `conversation_id … REFERENCES conversations(id) ON DELETE CASCADE` (clave foránea: no puede haber mensajes huérfanos; si borras la conversación, se borran sus mensajes). `CHECK (role IN ('user','assistant','system','tool'))`: la BD rechaza cualquier otro rol. |
| `task_checkpoints` | El estado de tareas largas, para retomarlas | `status` con `CHECK` (`pending`, `in_progress`, `completed`, `failed`); `checkpoint_data JSONB` (en qué paso iba y qué le falta); `created_at` y `updated_at`. |
| 4 `CREATE INDEX` | Acelerar las búsquedas típicas | Mensajes por conversación y por fecha; checkpoints por conversación; conversaciones por `session_id`. |
| `ALTER TABLE … ADD CONSTRAINT unique_conversation_task UNIQUE (conversation_id, task_name)` | **Hace posible el upsert** del paso 4 | Una sola fila por (conversación, tarea). Sin ella, `ON CONFLICT` falla con *no unique or exclusion constraint matching*. |

Salida real:
```text
postgres=> SELECT version();
                                    version
-------------------------------------------------------------------------------
 PostgreSQL 16.15 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
(1 row)

postgres=> CREATE DATABASE agent_memory;
CREATE DATABASE
postgres=> \c agent_memory
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
You are now connected to database "agent_memory" as user "<usuario-del-lab>".
agent_memory=> \i sql/schema.sql
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
ALTER TABLE
agent_memory=> \dt
                       List of relations
 Schema |       Name       | Type  |           Owner
--------+------------------+-------+----------------------------
 public | conversations    | table | <usuario-del-lab>
 public | messages         | table | <usuario-del-lab>
 public | task_checkpoints | table | <usuario-del-lab>
(3 rows)

agent_memory=> \d task_checkpoints
                                         Table "public.task_checkpoints"
     Column      |           Type           | Collation | Nullable |                   Default
-----------------+--------------------------+-----------+----------+----------------------------------------------
 id              | bigint                   |           | not null | nextval('task_checkpoints_id_seq'::regclass)
 conversation_id | bigint                   |           |          |
 task_name       | character varying(255)   |           | not null |
 status          | character varying(50)    |           | not null |
 checkpoint_data | jsonb                    |           | not null | '{}'::jsonb
 created_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "task_checkpoints_pkey" PRIMARY KEY, btree (id)
    "idx_task_checkpoints_conversation_id" btree (conversation_id)
    "unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)
Check constraints:
    "task_checkpoints_status_check" CHECK (status::text = ANY (ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'failed'::character varying]::text[]))
Foreign-key constraints:
    "task_checkpoints_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
```
**Qué mirar:**
- El prompt cambia a `agent_memory=>` tras `\c`. **Si no cambia, no sigas:** las tablas se crearían en `postgres`.
- El **Owner** de las tablas es el usuario de Entra: no existe ningún usuario de BD con contraseña.
- `unique_conversation_task` existe → el `ON CONFLICT` funcionará.
- El `CHECK` se guarda como `= ANY (ARRAY[...])`: es la forma interna de `IN (...)`.
- `conversation_id` tiene `Nullable` vacío (admite NULL). En PostgreSQL NULL ≠ NULL, así que dos checkpoints con `conversation_id` NULL y el mismo `task_name` **no chocan** en el `UNIQUE` y el upsert duplicaría. En un diseño real: `NOT NULL`.
- **Dos índices de la guía sobran:** `idx_task_checkpoints_conversation_id` ya lo cubre el `UNIQUE (conversation_id, task_name)` (un índice compuesto sirve para buscar por su **primera** columna: «prefijo izquierdo»), e `idx_conversations_session_id` duplica el que crea el `UNIQUE` de `session_id`. Solo hacen más lentas las escrituras.

✅ **Comprobación:** 3 `CREATE TABLE`, 4 `CREATE INDEX`, 1 `ALTER TABLE`, 3 tablas en `\dt` y `unique_conversation_task` en `\d task_checkpoints`. Si sale `\i: No such file`, `psql` se abrió desde otra carpeta: `\i ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/schema.sql`. Si sale `already exists`, ya estaba creado: sigue.

Sal de `psql` con `\q` (no con `q`).

## Paso 12 · Task 6: probar el flujo del agente con `test_workflow.py`
**Por qué:** [`agent-backend/test_workflow.py`](agent-backend/test_workflow.py) hace de agente: abre una conversación, guarda 5 mensajes, guarda un checkpoint `in_progress`, lee el historial y luego **vuelve a guardar la misma tarea** como `completed`. Si el upsert funciona, el `checkpoint_id` no cambia. Ojo: Python **no usa** `PGPASSWORD`; `get_connection()` pide su propio token a tu `az login` con `DefaultAzureCredential` (como Workload Identity en AKS: el mismo código sirve con tu usuario o con una identidad gestionada). Del `.env` solo usa `DB_HOST` y `DB_USER`.

```bash
cd agent-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source ../.env
python test_workflow.py
```
Salida real (`pip`, resumida a la última línea):
```text
Successfully installed PyJWT-2.15.1 azure-core-1.41.0 azure-identity-1.27.0 certifi-2026.10.23 cffi-2.1.1 charset_normalizer-3.5.2 cryptography-50.0.2 idna-3.20 msal-1.39.0 msal-extensions-1.3.1 psycopg-3.3.8 psycopg-binary-3.3.8 pycparser-3.12 requests-2.34.2 typing-extensions-4.16.0 urllib3-2.8.0
```
Salida real (`test_workflow.py`):
```text
=== Testing Agent Memory Backend ===

1. Creating conversation...
   Created conversation: {'conversation_id': 1, 'session_id': '<uuid>', 'started_at': '2026-11-10T18:22:21.538945+00:00'}

2. Storing messages...
   Stored system message: {'message_id': 1, 'created_at': '2026-11-10T18:22:23.945910+00:00'}
   Stored user message: {'message_id': 2, 'created_at': '2026-11-10T18:22:26.414443+00:00'}
   Stored assistant message: {'message_id': 3, 'created_at': '2026-11-10T18:22:28.865078+00:00'}
   Stored tool message: {'message_id': 4, 'created_at': '2026-11-10T18:22:30.276087+00:00'}
   Stored assistant message: {'message_id': 5, 'created_at': '2026-11-10T18:22:32.655699+00:00'}

3. Saving task checkpoint...
   Saved checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

4. Retrieving conversation history...
   Found 5 messages:
   - [system]: You are a helpful research assistant....
   - [user]: Can you help me find information about PostgreSQL?...
   - [assistant]: I'd be happy to help you research PostgreSQL. Let ...
   - [tool]: {"tool": "search", "results": ["PostgreSQL documen...
   - [assistant]: I found some resources about PostgreSQL. The offic...

5. Retrieving task state...
   Current state: {'checkpoint_id': 1, 'status': 'in_progress', 'checkpoint_data': {'step': 2, 'next_action': 'summarize_findings', 'sources_found': 2}, 'created_at': '2026-11-10T18:22:35.037193+00:00', 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

6. Updating task state to completed...
   Updated checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:42.154100+00:00'}

7. Verifying final state...
   Final status: completed
   Checkpoint data: {'step': 3, 'summary': 'PostgreSQL is an advanced open-source database.', 'sources_found': 2}

=== All tests completed successfully! ===
```
**Qué mirar:**
- **El upsert, demostrado:** `checkpoint_id` es `1` en el punto 3 y en el 6 → `ON CONFLICT` **actualizó** la fila, no creó otra. `updated_at` cambia (18:22:35 → 18:22:42); `created_at` se conserva.
- **Historial en orden:** los 5 mensajes salen cronológicos gracias a `ORDER BY created_at DESC` + `reversed()`. Hay 2 `assistant` porque el agente habla antes y después de usar la herramienta (`tool`).
- **JSONB no guarda el orden de las claves:** se insertó `step, sources_found, next_action` y vuelve `step, next_action, sources_found`. JSONB guarda un binario normalizado; el tipo `json` sí lo conservaría.
- **≈ 2,4 s por operación** (mensajes a :23,9 / :26,4 / :28,9 / :30,3 / :32,7): cada función crea un `DefaultAzureCredential`, pide un token (llamando a `az`, un subproceso) y abre una conexión TLS nueva. Es como abrir una conexión nueva al API server en cada `kubectl get`. En producción: `ConnectionPool` y reutilizar credencial/token (pregunta 2 del test del módulo 1).

⚠️ **Lo que pasó (tropiezos de terminal, sin efecto en el lab):**
- `\e` en `psql` abre un editor (se salió con `Ctrl+C`); `q` no sale de `psql`, hay que usar `\q`.
- Un pegado llegó con `^[[200~` delante (*bracketed paste*) y rompió el `cd agent-backend` (`cd: no se encontró la orden`): se creó un `.venv` sobrante en la raíz del lab (git lo ignora; se puede borrar con `rm -rf .venv`).

✅ **Comprobación:** la última línea `=== All tests completed successfully! ===` y el mismo `checkpoint_id` en los puntos 3 y 6. Si falla:
- `KeyError: 'DB_HOST'` → falta `source ../.env`.
- `DefaultAzureCredential failed` → revisa la sesión con `az account show`.
- `there is no unique or exclusion constraint matching the ON CONFLICT specification` → falta el `ALTER TABLE … UNIQUE` del paso 11.
- Error de certificado en `pip` → `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`.

## Paso 13 · Task 7: consultar el contexto del agente
**Por qué:** guardar memoria solo sirve si luego se puede **leer para decidir**. Estas 4 consultas son lo que un agente (o tú, depurándolo) preguntaría a su memoria. Se copiaron literales en [`sql/queries.sql`](sql/queries.sql), con `\pset pager off` al principio para que no se abra el paginador (el `less` de `psql`) y no haya que pulsar `q`. Ojo: ahora se conecta **directamente a `agent_memory`** (`$DB_NAME` vale `postgres`).

```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
source .env
psql "host=$DB_HOST port=5432 dbname=agent_memory user=$DB_USER sslmode=require"
```
```text
\i sql/queries.sql
```
**Qué hace cada consulta:**

| # | SQL | Para qué la usaría el agente |
|---|---|---|
| 1 | `WHERE user_id = 'user_123' ORDER BY started_at DESC` | Listar las sesiones anteriores de un usuario, la más reciente primero. |
| 2 | `messages JOIN conversations … ORDER BY m.created_at DESC LIMIT 10` | Cargar el contexto reciente. `JOIN` une cada mensaje con su conversación para sacar el `session_id`. `LIMIT` vale con pocas filas; con millones, la teoría recomienda *keyset pagination* (`WHERE (created_at, id) < (…)`). |
| 3 | `task_checkpoints JOIN conversations … WHERE t.status = 'completed'` | Saber qué tareas ya terminó, para no repetirlas. |
| 4 | `JOIN … GROUP BY c.id, m.role` + `COUNT(*)` | Métricas: cuánto conversa el agente frente a cuánto usa herramientas. |

Salida real:
```text
agent_memory=> \i sql/queries.sql
Pager usage is off.
--- 1. Conversaciones de user_123
 id |              session_id              |          started_at           |              metadata
----+--------------------------------------+-------------------------------+-------------------------------------
  1 | <uuid>                               | 2026-11-10 18:22:21.538945+00 | {"model": "gpt-4", "source": "web"}
(1 row)

--- 2. Últimos 10 mensajes de todas las conversaciones
 session_id |   role    |                                            content                                             |          created_at
------------+-----------+------------------------------------------------------------------------------------------------+-------------------------------
 <uuid>     | assistant | I found some resources about PostgreSQL. The official documentation is a great starting point. | 2026-11-10 18:22:32.655699+00
 <uuid>     | tool      | {"tool": "search", "results": ["PostgreSQL documentation", "PostgreSQL tutorial"]}             | 2026-11-10 18:22:30.276087+00
 <uuid>     | assistant | I'd be happy to help you research PostgreSQL. Let me search for relevant information.          | 2026-11-10 18:22:28.865078+00
 <uuid>     | user      | Can you help me find information about PostgreSQL?                                             | 2026-11-10 18:22:26.414443+00
 <uuid>     | system    | You are a helpful research assistant.                                                          | 2026-11-10 18:22:23.94591+00
(5 rows)

--- 3. Tareas completadas
 session_id |      task_name      |  status   |                                        checkpoint_data                                        |         updated_at
------------+---------------------+-----------+-----------------------------------------------------------------------------------------------+-----------------------------
 <uuid>     | research_postgresql | completed | {"step": 3, "summary": "PostgreSQL is an advanced open-source database.", "sources_found": 2} | 2026-11-10 18:22:42.1541+00
(1 row)

--- 4. Mensajes por rol en cada conversación
 conversation_id |   role    | message_count
-----------------+-----------+---------------
               1 | assistant |             2
               1 | system    |             1
               1 | tool      |             1
               1 | user      |             1
(4 rows)
```
**Qué mirar:** coincide al 100 % con lo que guardó `test_workflow.py`: 1 conversación, 5 mensajes (del más nuevo al más viejo), 1 tarea `completed` con el `checkpoint_data` final del upsert, y 2/1/1/1 por rol. Las horas salen en UTC (`+00`): `TIMESTAMPTZ` guarda el instante exacto y lo muestra en la zona de la sesión.

✅ **Comprobación:** las cuatro tablas con 1, 5, 1 y 4 filas. Si la consulta 1 sale vacía, estás en `postgres` y no en `agent_memory` (mira el prompt). Si sale `password authentication failed`, el token caducó: `python3 azdeploy.py` → `3` → `4`, `source .env` y reconecta.

Sal con `\q`.

---

## Cleanup (obligatorio al acabar)
**Por qué:** el `Standard_D2ds_v4` se cobra cada hora que existe, y al pasar al siguiente lab la plataforma cambia de suscripción: después ya no se puede comprobar el borrado. Borrar el resource group borra todo lo que hay dentro (como `kubectl delete namespace`).

Antes de borrar, se miró qué había (solo lectura):
```bash
az group exists --name rg-ai200-pg-agent
az group list --query "[].{name:name, state:properties.provisioningState}" -o table
az group show -n ai200rg --query properties.provisioningState -o tsv
az group exists --name ai200rg
```
Salida real:
```text
false
Name              State
----------------  ---------
az104-rg-region1  Succeeded
ai200rg           Succeeded
Succeeded
true
```
**Qué mirar:** el grupo del primer intento ya da `false` (borrado verificado). `ai200rg` en `Succeeded` + `true` = **el borrado aún no se había lanzado** (`--no-wait` no imprime nada, así que siempre hay que comprobarlo). `az104-rg-region1` es de otro curso: no se toca.

Borrado:
```bash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv
az group exists --name ai200rg
```
Salida real:
```text
Deleting
true
```
**Qué mirar:** `Deleting` confirma que está en marcha; `exists` sigue en `true` hasta que termina (un Flexible Server tarda unos minutos).

Comprobación final, minutos después:
```bash
az group exists --name ai200rg
```
Salida real:
```text
ERROR: No subscription found. Run 'az account set' to select a subscription.
```
**Estado: no verificado.** Al cerrar el lab en la plataforma, la suscripción temporal `XLabs-079` dejó de estar accesible y la sesión de `az` caducó. Último estado visto: `Deleting`. `rg-ai200-pg-agent` sí está verificado (`false`).

✅ **Comprobación (para la próxima vez):** espera a ver `false` **antes** de cerrar el lab en la plataforma. Si sigue en `true` pasados 15 minutos, mira `az group show -n ai200rg --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`.

## Resumen de incidencias
| Paso | Síntoma | Causa | Arreglo |
|---|---|---|---|
| 3 | `ERROR: The location is restricted from performing this operation.` (el RG sí se crea) | Política de la suscripción del lab: PostgreSQL solo en `centralus` con `Standard_D2ds_v4`/`GeneralPurpose` | Borrar el RG vacío y relanzar con los valores de la guía de la plataforma (paso 5) |
| 9 | `\r: extra argument "SELECT" ignored` / el `SELECT` no se ejecuta | Pegado de varias líneas; los comandos con barra se comen el resto de la línea | Comandos `\…` solos en su línea; escribir el SQL en el prompt `postgres=>` |
| 10 | `unrecognized arguments: -n psql-agent-…` en `firewall-rule list` | En `firewall-rule` el servidor es `--server-name`/`-s`; `-n` es la regla | `--server-name psql-agent-dc48980e` |
| 12 | `cd: no se encontró la orden` con `^[[200~` | *Bracketed paste* de la terminal | Repetir el comando escrito; borrar el `.venv` sobrante de la raíz |
| 12 | `q` no sale de `psql`; `\e` abre un editor | Atajos de `psql` | `\q` para salir; `Ctrl+C` en el selector de editor |
| 12 | ≈ 2,4 s por operación | Token y conexión TLS nuevos en cada llamada | En producción, `ConnectionPool` (no se cambió el código del lab) |
| Cleanup | `No subscription found` al verificar | La suscripción temporal desaparece al cerrar el lab | Verificar `false` antes de cerrar el lab |
| — | `password authentication failed` (no pasó, pero es lo esperable pasada 1 h) | El token de Entra caduca | `azdeploy.py` → `3` y `source .env` |
| — | `there is no unique or exclusion constraint matching the ON CONFLICT specification` (no pasó) | Falta el `UNIQUE (conversation_id, task_name)` | `ALTER TABLE … ADD CONSTRAINT … UNIQUE` (paso 11) |
