# Lab LP5-03 · Optimize vector search performance (plataforma: Lab 14 · AI-200-LP05M03)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html
- **Estado (17/11/2026): PREPARADO, sin ejecutar.** Previsto para el 18 o 19/11 por la mañana. Todas las salidas marcadas «(pendiente de ejecutar; salida esperada según la guía)» son estimaciones: se sustituyen por las reales al hacerlo.
- Labs anteriores: [LP5-01](../lp5-01-pg-agent-backend/README.md) y [LP5-02](../lp5-02-pg-vector-search/README.md). Notas del módulo: [`05-3-postgresql-optimize.md`](../../docs/modulos/05-3-postgresql-optimize.md). Origen MIT de `azdeploy.py`: ver [`../NOTICE.md`](../NOTICE.md).
- **SQL:** los ficheros de [`sql/`](sql/) son copia literal de la guía oficial (Markdown fuente de MicrosoftLearning/mslearn-azure-ai, MIT). La guía **no trae salidas de ejemplo ni tiempos**: lo que figura como «salida esperada» es solo lo que la guía describe (p. ej. `Seq Scan`, `Index Scan using idx_products_embedding_ivfflat`); los tiempos los rellena el alumno.

Cada paso: **por qué → comando → salida → qué mirar → comprobación**.

## Qué se construye
Un servidor PostgreSQL Flexible Server con 100.000 vectores aleatorios y una batería de `EXPLAIN ANALYZE` para comparar: sin índice, IVFFlat, HNSW y filtrado por metadatos. No hay app: todo es `psql`.

```
azdeploy.py 1 → RG + Flexible Server psql-optimize-<hash>, solo Entra, firewall AllowAll
azdeploy.py 2 → azure.extensions = vector (allow-list) → reinicio (1-2 min)
azdeploy.py 4 → .env con host, usuario y token de Entra (~1 h) · 5 → salir
psql          → tabla products (100.000 × vector(384)) → baseline → IVFFlat → HNSW → filtros
```
`azdeploy.py` (22.909 bytes, leído sin ejecutar) es el de LP5-02 con tres diferencias: servidor `psql-optimize-<hash>`, mismo menú de 5 opciones y **no hay `client/`** (el zip solo trae `azdeploy.py`). Mantiene `Standard_B1ms`/`Burstable`, `--storage-size 32`, PostgreSQL 16, `pgadmin` con contraseña aleatoria que luego desactiva y firewall `AllowAll`.

**Lo que se aprendió en LP5-01/02 y se anticipa aquí:**
| Tema | Qué hacer |
|---|---|
| Región/SKU | **La guía no los fija** (solo grupo y región a elegir). En LP5-01/02 la plataforma exigía `centralus` y `Standard_D2ds_v4`/`GeneralPurpose` (el script trae `B1ms`/`Burstable`). Mirar primero la guía de la plataforma del lab 14; el paso 3 deja el `sed` del SKU como **condicional** |
| Autenticación | Solo Entra: la «contraseña» (`PGPASSWORD`) es un token que caduca a la hora → repetir paso 6 |
| `vector` en dos planos | Opción 2 (`azure.extensions`, plano de control) y `CREATE EXTENSION` (base de datos) |
| Puerto 5432 | Sí pasa por el proxy de empresa (verificado en LP5-02) |
| Cortes de conexión | La sesión con `mol-bastion` se corta y mata el `psql`; la **tabla temporal `query_vectors` se pierde** → ver paso 7 |

---

## Paso 0 · Preparar la terminal
**Por qué:** certificado del proxy para `az`/Python; hay que repetirlo en cada terminal.
```bash
cd ~/claude/AI-200-Developing/labs/lp5-03-pg-optimize
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `pwd` termina en `lp5-03-pg-optimize` y `psql --version` responde. Si `psql` no existe: `sudo apt install postgresql-client`.

## Paso 1 · `az login` con el usuario del lab 14
**Por qué:** cada lab trae usuario y suscripción propios.
```bash
az logout
az login
az account show --query "{sub:name, user:user.name}" -o table
```
Salida: (pendiente de ejecutar; salida esperada según la guía) suscripción `XLabs-…` nueva y el usuario del lab.

✅ **Comprobación:** si sale la cuenta de empresa o la suscripción del lab 13, repite `az logout` y `az login`.

## Paso 2 · Registrar el proveedor de PostgreSQL
**Por qué:** la suscripción nueva puede no tenerlo registrado.
```bash
az provider register --namespace Microsoft.DBforPostgreSQL
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
```
Salida: `Registered` (pendiente de ejecutar; salida esperada según la guía).

✅ **Comprobación:** si sale `Registering`, repite el `show` al minuto.

## Paso 3 · Poner grupo y región en `azdeploy.py`
**Por qué:** la guía solo pide cambiar esos dos valores (`<your-resource-group-name>` y `<your-azure-region>`) y «no cambiar nada más». **Región y SKU no vienen en la guía**: usa los que indique la plataforma del lab 14 (en LP5-02: `centralus`).
```bash
sed -i 's/<your-resource-group-name>/ai200rg/; s/<your-azure-region>/centralus/' azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
Salida (pendiente de ejecutar; salida esperada según la guía):
```text
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
```
**Solo si la creación del servidor falla por política de SKU** (como en LP5-02; el script trae `Standard_B1ms`/`Burstable`), y la plataforma lo exige:
```bash
sed -i 's/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '"--sku-name"|"--tier"' azdeploy.py
```
Si ya había servidor a medias, la opción 1 pide confirmar el borrado y redespliegue (la guía: escribir `yes`).

✅ **Comprobación:** si sigue apareciendo `<your-…>`, edítalo a mano.

## Paso 4 · Crear el servidor y habilitar `vector` (opciones 1 y 2)
**Por qué:** crea RG y servidor solo Entra (5-10 min) y añade `vector` a `azure.extensions` (reinicio de 1-2 min).
```bash
python3 azdeploy.py      # menú → 1 → (esperar) → 2
```
Salida (pendiente de ejecutar; salida esperada según la guía):
```text
Creating Azure Database for PostgreSQL Flexible Server 'psql-optimize-<hash>'...
PostgreSQL server created successfully
  Microsoft Entra administrator: <usuario-del-lab>
  Firewall rule: AllowAll
...
Vector extension allow-listed and server is ready.
```
**Qué mirar:** las cuatro fases (servidor, admin Entra, contraseñas desactivadas, firewall) y el reinicio de la opción 2.

✅ **Comprobación** (el nombre real sale de `az postgres flexible-server list -g ai200rg --query "[].name" -o tsv`):
```bash
az postgres flexible-server show -g ai200rg -n psql-optimize-<hash> --query "{state:state, sku:sku.name, ver:version}" -o tsv
az postgres flexible-server parameter show -g ai200rg --server-name psql-optimize-<hash> --name azure.extensions --query value -o tsv
```
Esperado: `Ready  Standard_D2ds_v4  16` y `vector`. Si el estado no es `Ready` espera y repite; si `azure.extensions` sale vacío, repite la opción 2.

## Paso 5 · Estado del servidor (opción 3)
**Por qué:** confirma servidor, admin, firewall y allow-list de una vez.
```bash
python3 azdeploy.py      # menú → 3 → Enter → 5
```
Salida (pendiente de ejecutar; salida esperada según la guía):
```text
  Status: Ready
  Public access: Enabled
  Entra administrator: <usuario-del-lab>
  Firewall rule: AllowAll
  Vector extension: allow-listed
```
✅ **Comprobación:** cualquier línea `WARNING` o `not allow-listed` → repite la opción 1 o 2 correspondiente.

## Paso 6 · Token de Entra y conexión (opción 4)
**Por qué:** sin contraseñas, `PGPASSWORD` es un token de Entra que caduca en ~1 hora.
```bash
python3 azdeploy.py      # menú → 4 → Enter → 5
source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
```
Salida (pendiente de ejecutar; salida esperada según la guía): `token cargado` y host `psql-optimize-<hash>.postgres.database.azure.com`, `postgres`, usuario del lab.

**Qué mirar:** el `.env` lleva el token: está en `.gitignore` (`labs/lp5-*/.env`) y **no se versiona**.

✅ **Comprobación:**
```bash
psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require" -c "select version();"
```
Debe mostrar PostgreSQL 16. Si sale `password authentication failed`, token caducado: repite este paso. Si se cuelga, 5432 bloqueado: avisa (en LP5-02 sí pasó).

## Paso 7 · Esquema y 100.000 vectores
**Por qué:** hace falta volumen para que los índices importen; con 10 filas Postgres elegiría siempre Seq Scan.

⚠️ **Anticipa el corte de conexión:** `query_vectors` es **temporal** y desaparece si `psql` se cae (LP5-02: corte con `mol-bastion`). Si ocurre: paso 6 (token nuevo), reconectar y volver a crear solo `query_vectors` (último `CREATE TEMP TABLE` de `01-schema-data.sql`). Alternativa más segura: trabajar con `screen`/`tmux` en el equipo.
```bash
psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
```
Dentro de `psql`:
```text
\i sql/01-schema-data.sql
```
Salida (pendiente de ejecutar; salida esperada según la guía): `CREATE EXTENSION`, `CREATE TABLE`, `INSERT 0 100000`, `COUNT` = `100000` («You should see 100,000 rows», guía) y `SELECT 1` de la tabla temporal.

**Qué mirar:** el `INSERT` genera 384 `random()` por fila (100.000 filas): puede tardar un rato; la guía no da tiempo. La tabla lleva también `in_stock` (`BOOLEAN`) y `id BIGSERIAL`.

✅ **Comprobación:** `SELECT count(*) FROM products;` → `100000` y `SELECT vector_dims(embedding) FROM products LIMIT 1;` → `384`. Si `\i` no encuentra el fichero, usa la ruta completa. Si `count` es 0, el `INSERT` falló: lee el error.

## Paso 8 · Baseline sin índice
**Por qué:** referencia para medir la mejora.
```text
\i sql/02-baseline.sql
\i sql/02-baseline.sql
\i sql/02-baseline.sql
```
Salida (pendiente de ejecutar; salida esperada según la guía): plan con **Seq Scan** («PostgreSQL is scanning all 100,000 rows») y `Execution Time:` al final. La guía manda ejecutarlo **tres veces** (la primera puede ir lenta por caché fría) y anotar la última. Tiempo: no lo da la guía.

**Qué mirar:** `Seq Scan` + `Sort`/`top-N heapsort`. Anotar: **baseline = ___ ms**.

✅ **Comprobación:** debe aparecer `Seq Scan`. Si ya sale `Index Scan`, hay un índice previo (`\d products`).

## Paso 9 · IVFFlat y `probes`
**Por qué:** IVFFlat agrupa los vectores en `lists` y solo explora `probes` grupos: más rápido, menos exacto (recall).
```text
\i sql/03-ivfflat.sql
```
Salida (pendiente de ejecutar; salida esperada según la guía): `CREATE INDEX` (la guía pide anotar el tiempo de construcción: activa `\timing on` en `psql` antes, no está en la guía); plan con **Index Scan using idx_products_embedding_ivfflat**; `probes=1` es la opción indexada más rápida (puede perder vecinos reales) y `probes=50` más lenta y con mayor recall. El recall no se ve en el tiempo.

**Qué mirar:** tiempo de construcción (___ s), y latencias con `probes` 1 y 50. `ivfflat.probes` es por sesión (como una variable de entorno del pod, no del cluster).

✅ **Comprobación:** `Index Scan using idx_products_embedding_ivfflat` en los planes. Si sale `Seq Scan`, el índice no se creó o `\d products` no lo lista. Si el planificador lo ignora, comprobar `SELECT COUNT(*) FROM products;`.

## Paso 10 · HNSW y `ef_search`
**Por qué:** HNSW es un grafo: construcción más lenta y más memoria, mejor equilibrio velocidad/recall.
```text
\i sql/04-hnsw.sql
```
Salida (pendiente de ejecutar; salida esperada según la guía): `DROP INDEX`, `DROP INDEX`, `SET`, `CREATE INDEX` (la guía: 1-2 min con 100.000 vectores, más lento que IVFFlat) y planes con el índice `idx_products_embedding_hnsw`; `ef_search=20` más rápido y con menos recall que `100` (por defecto es 40).

**Qué mirar:** tiempo de construcción vs. IVFFlat; `maintenance_work_mem = 256MB` evita construir el grafo en disco. Resultado esperado según la guía: Seq Scan es lo más lento; IVFFlat `probes=1` es lo más rápido de los indexados (menos exacto); HNSW suele ir más rápido que IVFFlat con recall similar; subir `probes`/`ef_search` mejora la exactitud y sube la latencia.

✅ **Comprobación:** `\di+ *products*` muestra `idx_products_embedding_hnsw` y la PK (ya no el IVFFlat). Si se cae la conexión durante el `CREATE INDEX`, el índice no queda: repite token y script.

## Paso 11 · Filtrado por metadatos
**Por qué:** en una búsqueda real casi siempre hay filtro (`category_id`, precio). Sin B-tree, el filtro se aplica sobre el resultado del índice vectorial o con Seq Scan.
```text
\i sql/05-filtering.sql
```
Salida (pendiente de ejecutar; salida esperada según la guía): `CREATE INDEX idx_products_category`; 1.º plan (`category_id = 5`): la guía espera el índice HNSW para la similitud y luego el filtro de categoría; 2.º plan (`category_id = 5 AND price BETWEEN 100 AND 200`): puede aparecer un **Bitmap Index Scan** con post-filtro u otra estrategia; tras `CREATE INDEX idx_products_category_price` se repite la consulta y «potencialmente» baja el tiempo.

**Qué mirar:** la guía no garantiza el plan: el planificador decide según la selectividad. Conecta con el knowledge check (pregunta 2).

✅ **Comprobación:** `\di+ *products*` lista `idx_products_category` y `idx_products_category_price`. Salir con `\q`.

---

## Cleanup (obligatorio al acabar)
**Por qué:** el servidor `D2ds_v4` cuesta mientras exista y las credenciales del lab caducan: borrar antes de documentar.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv
az group exists --name ai200rg
```
Esperado: `Deleting`, `true` y, tras unos minutos, `false`.

✅ **Comprobación:** repetir `az group exists --name ai200rg` cada 15 s hasta `false`. Si sigue `true` pasados 15 min y el estado es `Failed`, relanzar el `delete`. Si caducan las credenciales, anotar «no verificado».

## Resumen de incidencias previstas
| Síntoma | Causa | Arreglo |
|---|---|---|
| Error de SKU/tier al crear servidor | Política de la plataforma (visto en LP5-02) | Paso 3, `sed` condicional del SKU |
| `password authentication failed` | Token Entra caducado (1 h) | Paso 6 |
| `extension "vector" is not allow-listed` | Falta la opción 2 | Paso 4 |
| `relation "query_vectors" does not exist` | Corte de sesión: tabla temporal perdida | Reconectar y recrear `query_vectors` |
| Server name no liberado al relanzar opción 1 | Azure tarda en liberar el nombre | Salir del script, esperar 5 min (guía) |
| `Access denied` en `psql` | Admin Entra ausente o `DB_USER` incorrecto | Opción 3; si falta, opción 1 y confirmar redespliegue (guía) |
| Plan con `Seq Scan` tras crear índice | Índice no creado o filtro poco selectivo | `\d products`, revisar plan |
