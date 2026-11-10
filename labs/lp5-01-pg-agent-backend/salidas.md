# Salidas reales · Lab LP5-01 (saneadas)

Volver al [README](README.md). IDs de suscripción sustituidos por `<sub-id>`.

## 1. `az login` (10/11/2026)
```text
$ az login
A web browser has been opened at https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize. ...

[Tenant and subscription selection]

No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-079            <sub-id>                              Lab Directory

Select a subscription and tenant (Type a number or Enter for no changes): 1

Tenant: Lab Directory
Subscription: XLabs-079 (<sub-id>)
```
**Qué mirar:** el tenant es `Lab Directory` y hay una sola suscripción (`XLabs-079`): es la del lab, no la de la empresa. Con navegador disponible, `az login` sin `--use-device-code` también funciona; el Temporary Access Pass se escribe en la página de login como si fuera la contraseña.

## 2. Registro del proveedor
```text
$ az provider register --namespace Microsoft.DBforPostgreSQL
$ az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
Registered
```
**Qué mirar:** `Registered` a la primera: la suscripción del lab ya lo tenía registrado.

## 3. Primera edición de `azdeploy.py` (descartada)
```text
$ head -6 azdeploy.py | grep -E '^(rg|location)'
rg = "rg-ai200-pg-agent"  # Resource Group name
location = "eastus"   # Azure region for the resources
```
**Qué mirar:** la edición funcionó, pero la guía de la plataforma exige `ai200rg`, `centralus` y `Standard_D2ds_v4`/`GeneralPurpose` por política. Se canceló el despliegue para corregirlo.

## 4. Primer `azdeploy.py` opción 1 (con `eastus`, falla)
```text
Checking/creating resource group 'rg-ai200-pg-agent'...
Resource group created: rg-ai200-pg-agent

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
Error: Create PostgreSQL Flexible Server failed (exit code 1).
ERROR: The location is restricted from performing this operation.
```
**Qué mirar:** el resource group sí se crea (la política no limita la región de los grupos), pero el servidor no: la suscripción del lab solo permite PostgreSQL en `centralus`. Confirma que hay que usar los valores de la guía de la plataforma. El nombre del servidor (`psql-agent-` + 8 caracteres del SHA-1 de tu object id) no depende del RG ni de la región: el relanzamiento usará el mismo.

## 5. `azdeploy.py` opción 1 con los valores de la plataforma
```text
Resource Group: ai200rg
Server Name: psql-agent-dc48980e
Location: centralus
...
Please select an option (1-4): 1

Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
```
**Qué mirar:** la cabecera ya muestra `ai200rg` / `centralus`. Esta vez no sale `Waiting for Azure to release server name`: el intento anterior falló antes de reservar el nombre, así que estaba libre.

## 6. Fin de la opción 1
```text
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: XLab-JoR-079@xtremelabs.us
  Firewall rule: AllowAll
```
**Qué mirar:** las cuatro fases del script (crear → admin de Entra → desactivar contraseña → firewall). El admin de Entra es el usuario del lab: el mismo que hará de `DB_USER`.

## 7. Opción 2 (estado) y opción 3 (conexión)
```text
PostgreSQL Server (psql-agent-dc48980e):
  Status: Ready
  PostgreSQL server is ready
  Public access: Enabled
  Entra administrator: XLab-JoR-079@xtremelabs.us
  Firewall rule: AllowAll
```
```text
PostgreSQL Connection Information
===========================================================
Host: psql-agent-dc48980e.postgres.database.azure.com
Database: postgres
User: XLab-JoR-079@xtremelabs.us
Password: (Entra token - expires in ~1 hour)

Environment variables saved to .env and .env.ps1
```
**Qué mirar:** `Ready` + admin de Entra + firewall: los tres requisitos para conectar. `Database: postgres` es la BD por defecto; `agent_memory` se crea después con `psql`. La "contraseña" es un token de Entra (`az account get-access-token --resource-type oss-rdbms`) que caduca en ~1 h: el `.env` **no se versiona** (excepción en `.gitignore`). Comprobación previa del puerto desde `mol-bastion`: `5432 ABIERTO` (el proxy no lo bloquea, a diferencia de `kubectl` contra AKS).

## 8. `source .env` y primera conexión con `psql`
```text
$ source .env
$ [ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres XLab-JoR-079@xtremelabs.us
$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=>
```
**Qué mirar:** entra sin pedir contraseña (`psql` toma el token de `PGPASSWORD`) y la conexión va cifrada con TLS 1.3. Netskope no la corta: su cliente suele dirigir solo el tráfico web (80/443) al proxy con inspección TLS, y PostgreSQL negocia TLS dentro de su propio protocolo en el 5432. `kubectl` contra AKS sí va por 443, la inspección rompe el TLS/certificado de cliente del API server y por eso se bloquea (depende de la configuración de *steering* de la empresa).

## 9. Task 4 de la plataforma (firewall): verificación con `az` en lugar del portal
```text
$ az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query network.publicNetworkAccess -o tsv
Enabled
$ az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e ...
unrecognized arguments: -n psql-agent-dc48980e
$ az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
$ az postgres flexible-server firewall-rule create -g ai200rg --server-name psql-agent-dc48980e --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
{
  "endIpAddress": "255.255.255.255",
  "id": "/subscriptions/<sub-id>/resourceGroups/ai200rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-agent-dc48980e/firewallRules/AllowAll",
  "name": "AllowAll",
  "resourceGroup": "ai200rg",
  "startIpAddress": "0.0.0.0",
  ...
}
```
**Qué mirar:** en `firewall-rule` el servidor va con `--server-name`/`-s`; `-n` es el nombre de la regla (en `show` sí es el servidor). La regla ya existía (la crea `azdeploy.py`); el `create` no hacía falta, pero es idempotente: sobrescribe la regla con los mismos valores. La Task 4 del portal queda cubierta con `az`.

## 10. Task 5 de la plataforma: esquema con `psql` (`\i sql/schema.sql`)
```text
postgres=> SELECT version();
 PostgreSQL 16.15 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
postgres=> CREATE DATABASE agent_memory;
CREATE DATABASE
postgres=> \c agent_memory
You are now connected to database "agent_memory" as user "XLab-JoR-079@xtremelabs.us".
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
 Schema |       Name       | Type  |           Owner
--------+------------------+-------+----------------------------
 public | conversations    | table | XLab-JoR-079@xtremelabs.us
 public | messages         | table | XLab-JoR-079@xtremelabs.us
 public | task_checkpoints | table | XLab-JoR-079@xtremelabs.us
agent_memory=> \d task_checkpoints
 conversation_id | bigint  |  |          |      <- Nullable vacío: admite NULL
 ...
Indexes:
    "task_checkpoints_pkey" PRIMARY KEY, btree (id)
    "idx_task_checkpoints_conversation_id" btree (conversation_id)
    "unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)
Check constraints:
    "task_checkpoints_status_check" CHECK (status::text = ANY (ARRAY['pending', 'in_progress', 'completed', 'failed']))
Foreign-key constraints:
    "task_checkpoints_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
```
**Qué mirar:**
- El dueño de las tablas es el usuario de Entra: no existe un usuario de base de datos con contraseña.
- `unique_conversation_task` existe: el `ON CONFLICT` de `save_task_state` funcionará.
- El `CHECK` de `status` se guarda como `= ANY (ARRAY[...])`: es la forma interna de `IN (...)`.
- `conversation_id` sin `NOT NULL`: dos checkpoints con `conversation_id` NULL y el mismo `task_name` no chocan en el `UNIQUE` (NULL ≠ NULL).
- Índices redundantes de la guía: `idx_task_checkpoints_conversation_id` lo cubre ya el `UNIQUE (conversation_id, task_name)` (prefijo izquierdo del índice compuesto) e `idx_conversations_session_id` duplica el índice que crea `UNIQUE` en `session_id`.

## 11. Task 6: `test_workflow.py`
```text
(.venv) $ pip install -r requirements.txt
Successfully installed ... azure-identity-1.27.0 ... psycopg-3.3.8 psycopg-binary-3.3.8 ...
(.venv) $ python test_workflow.py
=== Testing Agent Memory Backend ===

1. Creating conversation...
   Created conversation: {'conversation_id': 1, 'session_id': '84f355cd-...', 'started_at': '2026-11-10T18:22:21.538945+00:00'}

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
- **Upsert:** `checkpoint_id` es `1` en el paso 3 y en el 6: `ON CONFLICT` actualizó la fila, no creó otra. `updated_at` cambia (18:22:35 → 18:22:42); `created_at` se conserva.
- **Historial:** los 5 mensajes salen en orden cronológico gracias a `ORDER BY created_at DESC` + `reversed()`.
- **JSONB no conserva el orden de las claves:** se insertó `step, sources_found, next_action` y vuelve `step, next_action, sources_found` (JSONB guarda un formato binario normalizado; el tipo `json` sí lo conservaría).
- **≈ 2,4 s por operación** (mensajes a las :23,9 / :26,4 / :28,9 / :30,3 / :32,7): cada función llama a `get_connection()`, que crea un `DefaultAzureCredential`, pide un token (vía `az` CLI, un subproceso) y abre una conexión TLS nueva. Es el antipatrón de la pregunta 2 del test: la solución es un `ConnectionPool` (y reutilizar la credencial/token).
- Incidencias de terminal sin efecto: `\e` abre un editor (se salió con Ctrl+C); `q` no sale de `psql`, hay que usar `\q`; un pegado con `^[[200~` (bracketed paste) rompió un `cd`; se creó un `.venv` sobrante en la raíz del lab (ignorado por git).

## 12. Task 7: consultas del contexto (`\i sql/queries.sql`)
```text
agent_memory=> \i sql/queries.sql
Pager usage is off.
--- 1. Conversaciones de user_123
 id |              session_id              |          started_at           |              metadata
----+--------------------------------------+-------------------------------+-------------------------------------
  1 | 84f355cd-5a36-471c-a886-dce35372c9ce | 2026-11-10 18:22:21.538945+00 | {"model": "gpt-4", "source": "web"}
(1 row)

--- 2. Últimos 10 mensajes de todas las conversaciones
 session_id | role      | content                                                                    | created_at
------------+-----------+----------------------------------------------------------------------------+-------------------------------
 84f355cd-… | assistant | I found some resources about PostgreSQL. The official documentation is ... | 2026-11-10 18:22:32.655699+00
 84f355cd-… | tool      | {"tool": "search", "results": ["PostgreSQL documentation", ...]}           | 2026-11-10 18:22:30.276087+00
 84f355cd-… | assistant | I'd be happy to help you research PostgreSQL. Let me search for ...        | 2026-11-10 18:22:28.865078+00
 84f355cd-… | user      | Can you help me find information about PostgreSQL?                         | 2026-11-10 18:22:26.414443+00
 84f355cd-… | system    | You are a helpful research assistant.                                      | 2026-11-10 18:22:23.94591+00
(5 rows)

--- 3. Tareas completadas
 session_id | task_name           | status    | checkpoint_data                                                                               | updated_at
------------+---------------------+-----------+-----------------------------------------------------------------------------------------------+-----------------------------
 84f355cd-… | research_postgresql | completed | {"step": 3, "summary": "PostgreSQL is an advanced open-source database.", "sources_found": 2} | 2026-11-10 18:22:42.1541+00
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
**Qué mirar:** coincide al 100 % con lo que guardó `test_workflow.py`. Las horas salen en UTC (`+00`): 18:22 UTC = 19:22 en Madrid. `\pset pager off` evita el paginador. La consulta 2 usa `LIMIT` (sin keyset pagination): suficiente con 5 filas, no con millones. En la 4 hay 2 `assistant` porque el agente habló antes y después de usar la herramienta.

## 13. Cleanup
```text
$ az group exists --name rg-ai200-pg-agent
false
$ az group list --query "[].{name:name, state:properties.provisioningState}" -o table
Name              State
----------------  ---------
az104-rg-region1  Succeeded
ai200rg           Succeeded
$ az group show -n ai200rg --query properties.provisioningState -o tsv     # antes de lanzar el delete
Succeeded
$ az group exists --name ai200rg
true
$ az group delete --name ai200rg --yes --no-wait
$ az group show -n ai200rg --query properties.provisioningState -o tsv
Deleting
$ az group exists --name ai200rg
true
```
**Qué mirar:** `Succeeded` + `true` = el borrado aún no se había lanzado (`--no-wait` no muestra nada, así que hay que comprobarlo siempre). Tras el `delete`, `Deleting` confirma que está en marcha; `exists` sigue en `true` hasta que termina (un Flexible Server tarda unos minutos). El grupo del primer intento ya da `false`. `az104-rg-region1` es de otro curso.
