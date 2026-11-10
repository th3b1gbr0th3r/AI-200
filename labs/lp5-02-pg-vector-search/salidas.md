# Salidas reales · Lab LP5-02 (saneadas)

Volver al [README](README.md). IDs de suscripción sustituidos por `<sub-id>`.

## 1. `az login` con el usuario del lab 13
```text
$ az logout
$ az login
[1] *  XLabs-245            <sub-id>                              Lab Directory
Select a subscription and tenant (Type a number or Enter for no changes): 1
Tenant: Lab Directory
Subscription: XLabs-245 (<sub-id>)
```
**Qué mirar:** suscripción nueva (`XLabs-245`; el lab 12 era `XLabs-079`). Por eso el cleanup del lab anterior no se puede verificar desde aquí.

## 2. Valores de la plataforma en `azdeploy.py`
```text
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
325:            "--sku-name", "Standard_D2ds_v4",
326:            "--tier", "GeneralPurpose",
```
**Qué mirar:** la guía de la plataforma confirma `centralus` y `Standard_D2ds_v4`/`GeneralPurpose` (mismos que LP5-01). La guía cita `azdeploy.ps1`, pero el zip solo trae `azdeploy.py`.

## 3. `azdeploy.py` opción 1
```text
Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-vector-acc85432'...
This may take several minutes...
```
**Qué mirar:** a la primera, sin el error de región del lab 12. El hash del nombre cambia porque es otro usuario (otro object id).

## 4. Fin de la opción 1
```text
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: XLab-1bC-245@xtremelabs.us
  Firewall rule: AllowAll
```
**Qué mirar:** idéntico a LP5-01 (mismas cuatro fases). Falta la novedad de este lab: la opción 2 (`azure.extensions`).

## 5. Opción 2: allow-list de `vector`
```text
Configuring the vector extension allow-list...
Adding the vector extension to the server's allow-list.
The server will restart to apply the change. This can take 1-2 minutes...
Vector extension allow-listed and server is ready.
```
**Qué mirar:** es el paso de plano de control (`az postgres flexible-server parameter set --name azure.extensions --value vector`). Reinicia el servidor. Sin él, `CREATE EXTENSION vector` falla con «extension "vector" is not allow-listed».

## 6. Menú del lab 13
```text
1. Create PostgreSQL server with Entra authentication
2. Configure vector extension allow-list
3. Check deployment status
4. Retrieve connection info and access token
5. Exit
```
**Qué mirar:** respecto a LP5-01 se inserta la opción 2 y el resto se desplaza (salir = 5).

## 7. App arrancada antes de crear el esquema
```text
(.venv) $ python app.py
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
En la web, al pulsar «Load Sample Products»:
```text
Error loading data: relation "products" does not exist LINE 1: SELECT id FROM products WHERE name = $1 ^
```
**Qué mirar:** la app y la conexión con Entra funcionan (el error viene de PostgreSQL, no de la autenticación); falta la tabla. La plataforma pone la Task 2 (código) antes del esquema. Fíjate en `$1`: psycopg 3 envía los `%s` como parámetros del servidor (`$1`), no los incrusta en el texto.

## 8. Corte de conexión y recuperación
Se cortó la sesión con `mol-bastion` antes de crear el esquema: Flask se paró y el `\i` no llegó a ejecutarse (comprobado en solo lectura: `ext:NO`, `tabla:NO`, `indice:NO`; `az` seguía con sesión y el servidor existía). Token renovado con la opción 4:
```text
Host: psql-vector-acc85432.postgres.database.azure.com
Database: postgres
User: XLab-1bC-245@xtremelabs.us
Password: (Entra token - expires in ~1 hour)
Environment variables saved to .env and .env.ps1
```

## 9. Esquema con pgvector (`\i sql/schema.sql`)
```text
postgres=> \i sql/schema.sql
CREATE EXTENSION
CREATE TABLE
CREATE INDEX
                                  Table "public.products"
   Column    |     Type      | Collation | Nullable |               Default
-------------+---------------+-----------+----------+--------------------------------------
 id          | integer       |           | not null | nextval('products_id_seq'::regclass)
 name        | text          |           | not null |
 category    | text          |           |          |
 description | text          |           |          |
 price       | numeric(10,2) |           |          |
 embedding   | vector(330)   |           |          |
Indexes:
    "products_pkey" PRIMARY KEY, btree (id)
    "products_embedding_idx" hnsw (embedding vector_cosine_ops) WITH (m='16', ef_construction='64')

 extname | extversion
---------+------------
 vector  | 0.8.7
(1 row)
```
**Qué mirar:** `CREATE EXTENSION` funciona porque la opción 2 añadió `vector` a `azure.extensions`. pgvector **0.8.7**. El índice HNSW se crea con la tabla vacía (IVFFlat no podría: necesita datos para calcular los clusters) y usa `vector_cosine_ops`, que casa con el operador `<=>` de la búsqueda.

## 10. Task 3 de la plataforma: verificación con `az` (en lugar del portal)
```text
$ az postgres flexible-server show -g ai200rg -n psql-vector-acc85432 --query "{state:state, public:network.publicNetworkAccess, sku:sku.name, version:version}" -o tsv
Ready	Enabled	Standard_D2ds_v4	16
$ az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-vector-acc85432 --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o tsv
AllowAll	0.0.0.0	255.255.255.255
$ az postgres flexible-server parameter show -g ai200rg --server-name psql-vector-acc85432 --name azure.extensions --query value -o tsv
vector
```
**Qué mirar:** cubre los pasos del portal (acceso público + regla `AllowAll`) y confirma la opción 2 (`azure.extensions = vector`). Erratas de la guía de la plataforma: el servidor se llama `psql-vector-…` (no `psql-agent-…`, copiado de LP5-01) y la columna es `vector(330)` aunque el texto diga «384».

## 11. Cleanup
```text
$ az group delete --name ai200rg --yes --no-wait
$ az group show -n ai200rg --query properties.provisioningState -o tsv
Deleting
$ az group exists --name ai200rg
true
... (comprobación cada 15 s)
21:19:32 false
```
**Qué mirar:** `Deleting` → `true` mientras se borra el servidor → `false` a las 21:19 (unos minutos). Verificado antes de cerrar el lab en la plataforma.
