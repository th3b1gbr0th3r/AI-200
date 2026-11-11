# Lab LP5-02 · Implement vector search (plataforma: Lab 13 · AI-200-LP05M02)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html
- **Estado (10/11/2026): parcial.** Hechos los pasos 1-9 y la limpieza. **No hecho:** cargar productos y buscar similares en la web (pasos 10-11): el alumno decidió cerrar el lab. **Cleanup verificado** (`ai200rg` = `false` a las 21:19).
- **Conversación completa con Claude Code:** [`02-lab13-pg-vector-search.md`](../../sesiones/conversaciones/2026-11-10-sesion-06/02-lab13-pg-vector-search.md).
- Lab anterior: [LP5-01](../lp5-01-pg-agent-backend/README.md). Origen MIT de `azdeploy.py` y `client/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **comando → salida real (saneada) → qué mirar → comprobación**. Los IDs de suscripción se sustituyen por `<sub-id>`.

## Qué se construye
Búsqueda de productos similares con `pgvector`: se habilita la extensión, se crea una tabla `products` con `embedding vector(330)` e índice HNSW, y una app Flask (`client/app.py`) carga productos, busca similares con `<=>` (distancia coseno) y añade productos nuevos.

```
azdeploy.py 1 → RG + Flexible Server psql-vector-<hash>, solo Entra, firewall AllowAll
azdeploy.py 2 → azure.extensions = vector (allow-list) → reinicio del servidor (1-2 min)
azdeploy.py 4 → .env con host, usuario y token de Entra (~1 h) · 5 → salir
psql          → CREATE EXTENSION vector + tabla products + índice HNSW
client/app.py → /load-data, /search, /add-product · Flask en http://127.0.0.1:5000
```
- Los embeddings vienen **precalculados** en `client/sample_products.json` (10 productos) y `client/new_products.json` (3): no se llama a ningún modelo.
- **Dimensiones: 330** (comprobado en los dos JSON). La guía dice «384» en el texto, pero su SQL usa `vector(330)`, que es lo correcto.

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp5-02-pg-vector-search
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
**Por qué:** `deactivate` sale del `.venv` del lab anterior. `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa. Hay que exportarlo **en cada terminal nueva**.

## Paso 1 · `az login` con el usuario del lab 13
```bash
az logout
az login
```
Salida real:
```text
[1] *  XLabs-245            <sub-id>                              Lab Directory
Select a subscription and tenant (Type a number or Enter for no changes): 1
Tenant: Lab Directory
Subscription: XLabs-245 (<sub-id>)
```
**Qué mirar:** la suscripción es nueva (`XLabs-245`; en el lab 12 era `XLabs-079`). Cada lab trae su propio usuario temporal y su suscripción, por eso la limpieza del lab anterior ya no se puede comprobar desde aquí.

✅ **Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Debe salir `XLabs-245` y el usuario del lab (`<usuario-del-lab>`). Si sale la cuenta de empresa o la suscripción del lab anterior, repite `az logout` y `az login`.

## Paso 2 · Registrar el proveedor de PostgreSQL
```bash
az provider register --namespace Microsoft.DBforPostgreSQL
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
```
✅ **Esperado:** `Registered`. Si sale `Registering`, repite el `show` al cabo de un minuto.

## Paso 3 · Poner los valores de la plataforma en `azdeploy.py`
La guía de la plataforma exige `centralus` y `Standard_D2ds_v4`/`GeneralPurpose` (la política de la suscripción no deja crear `Standard_B1ms`/`Burstable`, que es lo que trae el script).
```bash
sed -i 's/<your-resource-group-name>/ai200rg/; s/<your-azure-region>/centralus/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```
Salida real:
```text
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
325:            "--sku-name", "Standard_D2ds_v4",
326:            "--tier", "GeneralPurpose",
```
**Qué mirar:** las cuatro líneas cambiadas. La guía habla de `azdeploy.ps1`, pero el zip solo trae `azdeploy.py`.

✅ **Comprobación:** si alguna línea sigue mostrando `<your-…>`, `Standard_B1ms` o `Burstable`, el `sed` no la encontró: edítala a mano.

## Paso 4 · Crear el servidor (`azdeploy.py` → opción 1)
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este lab (la opción 2 es nueva respecto a LP5-01; salir pasa a ser la 5):
```text
1. Create PostgreSQL server with Entra authentication
2. Configure vector extension allow-list
3. Check deployment status
4. Retrieve connection info and access token
5. Exit
```
Salida real (tarda de 5 a 10 minutos):
```text
Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-vector-acc85432'...
This may take several minutes...
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: <usuario-del-lab>
  Firewall rule: AllowAll
```
**Qué mirar:** las mismas cuatro fases que en LP5-01: servidor, administrador de Entra, contraseñas desactivadas (solo Entra) y regla de firewall `AllowAll`. El sufijo del nombre (`acc85432`) es un hash del usuario, por eso cambia en cada lab.

✅ **Comprobación:**
```bash
az postgres flexible-server show -g ai200rg -n psql-vector-acc85432 --query state -o tsv
```
Debe salir `Ready`. Si no existe el servidor, vuelve a lanzar la opción 1 y pégame el error.

## Paso 5 · Habilitar `vector` en el servidor (opción 2)
Sin salir del menú: Enter → **`2`**.

Salida real:
```text
Configuring the vector extension allow-list...
Adding the vector extension to the server's allow-list.
The server will restart to apply the change. This can take 1-2 minutes...
Vector extension allow-listed and server is ready.
```
**Qué mirar:** esto es el **plano de control**: la opción 2 hace `az postgres flexible-server parameter set --name azure.extensions --value vector` y reinicia el servidor. Es la mitad de pgvector. La otra mitad es `CREATE EXTENSION` dentro de la base de datos (paso 8). Sin este paso, `CREATE EXTENSION vector` falla con `extension "vector" is not allow-listed`.

✅ **Comprobación:**
```bash
az postgres flexible-server parameter show -g ai200rg --server-name psql-vector-acc85432 --name azure.extensions --query value -o tsv
```
Debe salir `vector`. Si sale vacío, repite la opción 2.

## Paso 6 · Comprobar con `az` lo que la guía mira en el portal
La Task 3 de la plataforma revisa en el portal el acceso público y la regla de firewall. Con `az` se ve lo mismo sin salir de la terminal:
```bash
az postgres flexible-server show -g ai200rg -n psql-vector-acc85432 --query "{state:state, public:network.publicNetworkAccess, sku:sku.name, version:version}" -o tsv
az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-vector-acc85432 --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o tsv
```
Salida real:
```text
Ready	Enabled	Standard_D2ds_v4	16
AllowAll	0.0.0.0	255.255.255.255
```
**Qué mirar:** servidor `Ready`, acceso público `Enabled`, SKU de la política y PostgreSQL 16. Erratas de la guía de la plataforma: el servidor se llama `psql-vector-…` (no `psql-agent-…`, copiado de LP5-01).

## Paso 7 · Obtener el token y conectarse con `psql` (opción 4)
```bash
python3 azdeploy.py      # menú → 4 → Enter → 5
source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
```
Salida real de la opción 4:
```text
Host: psql-vector-acc85432.postgres.database.azure.com
Database: postgres
User: <usuario-del-lab>
Password: (Entra token - expires in ~1 hour)
Environment variables saved to .env and .env.ps1
```
**Qué mirar:** la «contraseña» es un **token de Entra** que caduca en una hora. Si pasado ese tiempo sale `password authentication failed`, repite este paso. El `.env` de este lab no se sube al repo porque lleva el token.

✅ **Comprobación:** debe salir `token cargado` y una línea con host, `postgres` y el usuario. Si no sale `token cargado`, el `source .env` no se hizo en esta terminal.

## Paso 8 · Crear el esquema con pgvector
```bash
psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
```
Dentro de `psql`:
```text
\i sql/schema.sql
```
[`sql/schema.sql`](sql/schema.sql) es copia literal de la guía: `CREATE EXTENSION vector`, la tabla `products` y el índice HNSW.

Salida real:
```text
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
**Qué mirar:**
- `CREATE EXTENSION` funciona porque el paso 5 añadió `vector` a `azure.extensions`. Versión de pgvector: **0.8.7**.
- La columna es `vector(330)`, igual que los embeddings de los JSON.
- El índice **HNSW** se puede crear con la tabla vacía (IVFFlat no: necesita datos para calcular sus grupos). Usa `vector_cosine_ops`, que casa con el operador `<=>` de la búsqueda.

✅ **Comprobación:** las tres líneas `CREATE …` y `vector | 0.8.7`. Si sale `\i: No such file`, `psql` se abrió desde otra carpeta: usa la ruta completa `\i ~/claude/AI-200-Developing/labs/lp5-02-pg-vector-search/sql/schema.sql`. Si sale `relation "products" already exists`, el esquema ya estaba creado: sigue.

Sal de `psql` con `\q`.

## Paso 9 · Completar y arrancar la app Flask
Las tres rutas de [`client/app.py`](client/app.py) ya están completadas con el código de la guía:
- `/load-data`: inserta los productos de `sample_products.json` y convierte cada embedding al formato `[x,y,…]` que espera pgvector.
- `/search`: busca los 5 productos más parecidos al elegido:
  ```sql
  SELECT id, name, category, description, price, embedding <=> %s AS distance
  FROM products
  WHERE id != %s          -- excluye el propio producto
  ORDER BY distance       -- más parecido primero (0 = idéntico, 2 = opuesto)
  LIMIT 5;
  ```
- `/add-product`: inserta uno de los productos de `new_products.json`.

```bash
python3 -m py_compile client/app.py && echo OK
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
source ../.env
python app.py
```
Salida real:
```text
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
✅ **Comprobación:** abre http://127.0.0.1:5000 y debe cargar la página del lab.

⚠️ **Lo que pasó:** la primera vez se arrancó la app **antes** del paso 8 (la plataforma pone el código antes que el esquema). Al pulsar «Load Sample Products»:
```text
Error loading data: relation "products" does not exist LINE 1: SELECT id FROM products WHERE name = $1 ^
```
**Qué mirar:** la conexión con Entra funciona (el error viene de PostgreSQL, no de la autenticación). Solo faltaba la tabla: se arregla con el paso 8. El `$1` indica que psycopg 3 envía los `%s` como parámetros aparte, no los pega en el texto de la consulta (por eso no hay inyección SQL).

⚠️ **Corte de conexión:** a las 20:05 se cortó la sesión SSH con el equipo. Flask se paró y el `\i` no se había llegado a ejecutar. Se recuperó repitiendo el paso 7 (token nuevo), el paso 8 y este paso desde `cd client` (el `.venv` ya existía: basta con `source .venv/bin/activate`).

## Paso 10 · Cargar productos y buscar similares — no hecho
En la web: **Load Sample Products** → elegir un producto → **Find Similar**. Esperado según la guía: 10 productos cargados y una lista de 5 similares ordenada por distancia (menor = más parecido).

✅ **Comprobación (en `psql`):**
```sql
SELECT count(*) FROM products;   -- esperado: 10
```

## Paso 11 · Añadir un producto nuevo — no hecho
En la web: **Add Product** con uno de `new_products.json` y repetir **Find Similar** para ver que el nuevo aparece entre los similares de su categoría. Esperado en `psql`: `count(*)` = 11.

---

## Cleanup (obligatorio al acabar)
Para Flask con `Ctrl+C` y luego:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv
az group exists --name ai200rg
```
Salida real:
```text
Deleting
true
... (comprobación cada 15 s)
21:19:32 false
```
**Qué mirar:** `Deleting` mientras se borra el servidor, `true` hasta que acaba, y `false` cuando ya no existe (unos minutos).

✅ **Verificado** el 10/11/2026 a las 21:19: `az group exists --name ai200rg` = `false` (suscripción `XLabs-245`). Si sigue en `true` pasados 15 minutos, mira `az group show -n ai200rg --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `relation "products" does not exist` al cargar datos | La app se arrancó antes de crear el esquema | Paso 8 y volver a cargar |
| `password authentication failed` | El token de Entra caduca a la hora | Paso 7 (opción 4) y `source .env` |
| `extension "vector" is not allow-listed` | No se hizo la opción 2 | Paso 5 |
| Se corta la sesión SSH | Conexión con el equipo | Pasos 7, 8 y 9 de nuevo; el `.venv` se reutiliza |
