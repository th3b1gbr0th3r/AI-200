# Lab LP4-01 · Build queries for Azure Cosmos DB (plataforma: Lab 9 · AI-200-LP04M01)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/01-build-rag-document-store.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (05/11/2026): completado salvo la Task 6.** Hechos los pasos 0-16: despliegue, 4 funciones, 5/5 tests `passed` y consultas desde la app. **No hecho:** la Task 6 (Query Explorer, paso 17), que se saltó por tiempo. **Cleanup lanzado, no verificado** (se vio `Deleting`; la sesión siguiente trajo otra suscripción).
- Lab anterior: [LP3-03](../lp3-03-aks-troubleshoot/README.md) · Lab siguiente: [LP4-02](../lp4-02-cosmos-vector-search/README.md). Notas de clase: [`docs/modulos/04-cosmosdb.md`](../../docs/modulos/04-cosmosdb.md). Origen MIT de `azdeploy.py` y `client/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: sin IDs de suscripción ni tenant (`<sub-id>`), sin usuario del lab (`<usuario-del-lab>`) y con el sufijo de la cuenta como `<hash>`.

## Qué se construye
El «almacén de documentos» de una aplicación RAG: los textos se trocean en **chunks** y cada chunk se guarda en Cosmos DB con sus metadatos. Luego se recuperan de tres formas, cada una con un coste distinto. Ese coste es lo que hay que aprender en este lab.

```
azdeploy.py 1 → RG rg-ai200-cosmos-rag + cuenta Cosmos DB NoSQL serverless cosmos-rag-<hash>
                + BD ragstore + contenedor chunks (partition key /documentId)
azdeploy.py 2 → rol Contributor (ARM, plano de control) + Cosmos DB Built-in Data Contributor (plano de datos)
azdeploy.py 3 → comprobar estado · 4 → .env con COSMOS_ENDPOINT/DATABASE/CONTAINER (sin claves) · 5 → salir
client/rag_functions.py → 4 funciones: guardar chunk · leer un documento · buscar por metadatos · lectura puntual
client/app.py (Flask)   → cargar 12 chunks de ejemplo, 5 tests, consultas · http://127.0.0.1:5000
```

**Objetivo en cristiano:** guardar trozos de texto y aprender que en Cosmos DB **la forma de la consulta decide lo que pagas**. Si conoces el `id` y la partition key, la lectura es directa y cuesta ≈ 1 RU. Si conoces solo el documento, la consulta va a una partición. Si buscas por otro campo, como la categoría, la consulta recorre todas las particiones.

### Los conceptos que hacen falta (con analogía de sistemas)
| Cosmos DB | Qué es | Analogía |
|---|---|---|
| Cuenta → base de datos → contenedor → item | Jerarquía. El item es un documento JSON | Cluster → namespace → colección de objetos |
| **Partition key** (`/documentId`) | Campo que decide en qué partición vive cada item. Todos los chunks de un documento caen juntos | Shard key. Una consulta con la clave es un `kubectl get -n ns nombre`. Una sin ella recorre todos los namespaces |
| **RU** (Request Unit) | La moneda de cada operación. Leer 1 KB por `id` + partition key ≈ 1 RU | requests/limits, pero cobrados por operación |
| **Serverless** | No se reservan RU: se paga lo consumido | Pago por uso, sin capacidad reservada |
| **Dos planos de permisos** | `Contributor` (ARM) gestiona cuenta, BD y contenedores. `Cosmos DB Built-in Data Contributor` (RBAC propio de Cosmos) lee y escribe documentos | Crear un `Deployment` frente a hacer `exec` en el pod |
| `DefaultAzureCredential` | El código no lleva claves: usa tu `az login` en el PC y una identidad gestionada en Azure | El mismo código con kubeconfig local o con Workload Identity en AKS |

### Diferencias con la guía oficial
La guía está escrita para la VM Windows de la plataforma (Edge, VS Code y PowerShell, con `azdeploy.ps1`). Aquí se hizo en un equipo Linux: `curl` + `unzip`, `python3 azdeploy.py` (el zip solo trae el `.py`), `az login --use-device-code` y `source .env` en vez de `. .\.env.ps1`. Todo el despliegue va por `az` (vía `azdeploy.py`). No hay `kubectl` ni `docker`, así que el proxy de empresa no estorba.

---

## Paso 0 · Preparar la terminal
**Por qué:** `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa. Se pierde al abrir una terminal nueva.
```bash
cd ~/claude/AI-200-Developing/labs/lp4-01-cosmos-queries
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación** (muestra solo esta variable, acordada en el curso):
```bash
[ -n "${REQUESTS_CA_BUNDLE:-}" ] && echo "definida: $REQUESTS_CA_BUNDLE" || echo "no definida"
```
Esperado: `definida: /etc/ssl/certs/ca-certificates.crt`. Si sale otra ruta o `no definida`, repite el `export`.

⚠️ **Lo que pasó:** en una shell la variable apuntaba a una ruta inexistente y `az` falló así:
```text
ERROR: REQUESTS_CA_BUNDLE environment variable is specified with an invalid file path
```
Se arregla repitiendo el `export` con la ruta correcta.

## Paso 1 · `az login` con el usuario del lab 9
**Por qué:** cada lab de la plataforma trae un usuario temporal y **su propia suscripción**. Todo lo que se cree va a esa suscripción.
```bash
az login --use-device-code
```
`--use-device-code` da un código para iniciar sesión desde cualquier navegador, sin depender del navegador del equipo.

Salida real:
```text
No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-278            <sub-id>                              Lab Directory

Select a subscription and tenant (Type a number or Enter for no changes): 1

Tenant: Lab Directory
Subscription: XLabs-278 (<sub-id>)
```
**Qué mirar:** una sola suscripción, `XLabs-278`. Anótala: el cleanup solo se puede comprobar desde ella (ver Cleanup).

✅ **Comprobación:**
```bash
az account show --query "{nombre:name, estado:state}" -o table
```
Esperado: `XLabs-278` con estado `Enabled`. Si sale otra suscripción, repite `az login --use-device-code`.

## Paso 2 · Comprobar que no queda nada y que el proveedor está registrado
**Por qué:** antes de crear nada, se confirma que no hay restos de días anteriores (`rg-ai200-*`) y que la suscripción puede crear cuentas de Cosmos DB (`Microsoft.DocumentDB`).
```bash
az group list -o table
az provider show --namespace Microsoft.DocumentDB --query registrationState -o tsv
```
Salida real del proveedor:
```text
Registered
```
La lista de grupos no se guardó en este momento. Más tarde, ya con el grupo del lab borrándose, solo había además un grupo de otro curso de la plataforma, que no se toca.

✅ **Comprobación:** esperado, ningún `rg-ai200-*` y `Registered`. Si sale `NotRegistered`, lanza `az provider register --namespace Microsoft.DocumentDB` y repite el `show` al minuto.

## Paso 3 · Descargar el starter dentro del repo
**Por qué:** el zip trae `azdeploy.py` (despliega con `az`) y `client/` (el código a completar y la app Flask). Se guarda en `labs/<lab>/` para tener el lab completo.
```bash
curl -fLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-build-query-python.zip
unzip -o cosmosdb-build-query-python.zip && ls
```
Salida real (resumida):
```text
100 16424  100 16424    0     0  19046      0 --:--:-- --:--:-- --:--:-- 19046
Archive:  cosmosdb-build-query-python.zip
  inflating: client/app.py
  inflating: client/templates/index.html
  inflating: client/sample_chunks.json
  inflating: client/query_executor.py
  inflating: client/test_workflow.py
  inflating: client/requirements.txt
  inflating: client/rag_functions.py
  inflating: client/static/css/style.css
  inflating: azdeploy.py
azdeploy.py  client  cosmosdb-build-query-python.zip
```
**Qué mirar:** `curl` no tuvo problemas con el proxy. `client/rag_functions.py` trae las 4 funciones vacías entre marcadores `BEGIN`/`END`. `requirements.txt` pide `flask`, `azure-cosmos` y `azure-identity`.

✅ **Comprobación:** `ls client/rag_functions.py azdeploy.py` debe listar los dos. Si falta alguno, repite el `unzip`.

## Paso 4 · Poner el resource group y la región en `azdeploy.py`
**Por qué:** el script trae dos marcadores (`<your-…>`) y la guía pide cambiar solo esos.
```bash
sed -i 's|<your-resource-group-name>|rg-ai200-cosmos-rag|; s|<your-azure-region>|eastus|' azdeploy.py
sed -n '5,6p' azdeploy.py
grep -nE 'DATABASE_NAME *=|CONTAINER_NAME *=' azdeploy.py
```
Salida real:
```text
rg = "rg-ai200-cosmos-rag"  # Resource Group name
location = "eastus"   # Azure region for the resources
20:DATABASE_NAME = "ragstore"
21:CONTAINER_NAME = "chunks"
```
**Qué mirar:** la base de datos (`ragstore`) y el contenedor (`chunks`) vienen fijados en el script. Al arrancar, el script saca tu object ID con `az ad signed-in-user show` y llama a la cuenta `cosmos-rag-` + 8 caracteres de un hash de ese ID. Así el nombre es único en todo Azure y estable si relanzas el script.

✅ **Comprobación:** si siguen apareciendo `<your-…>`, el `sed` no los encontró: edita las líneas 5 y 6 a mano.

## Paso 5 · Crear la cuenta, la BD y el contenedor (`azdeploy.py` → opción 1)
**Por qué:** es el **plano de control**. Se crea la cuenta Cosmos DB **serverless** (sin RU reservadas: coste mínimo en un lab) con consistencia `Session`, la BD `ragstore` y el contenedor `chunks` con partition key `/documentId`. Tarda de 5 a 10 minutos.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este lab:
```text
1. Create Cosmos DB account
2. Configure Entra ID access
3. Check deployment status
4. Retrieve connection info
5. Exit
```
Salida real de la opción 1:
```text
Checking/creating resource group 'rg-ai200-cosmos-rag'...
Resource group created: rg-ai200-cosmos-rag

Creating Azure Cosmos DB for NoSQL account 'cosmos-rag-<hash>' in 'eastus'...
This may take several minutes...
Cosmos DB account created successfully
Creating database 'ragstore'...
Database created: ragstore
Creating container 'chunks'...
Container created: chunks (partition key: /documentId)
Use option 2 to configure Entra ID access.
Press Enter to continue...
```
**Qué mirar:** la partition key `/documentId` agrupa todos los chunks de un mismo documento en una **partición lógica**. Por eso leer «todos los chunks del documento X» será barato.

⚠️ **Lo que pasó:** la guía dice `python azdeploy.py`, y en este equipo solo existe `python3`:
```text
Orden «python» no encontrada. Quizá quiso decir:
  la orden «python3» del paquete deb «python3»
```
Se usa `python3 azdeploy.py`.

✅ **Comprobación** (en otra terminal, mientras corre):
```bash
az cosmosdb list -g rg-ai200-cosmos-rag --query "[].{n:name, e:provisioningState, loc:location}" -o table
A=$(az cosmosdb list -g rg-ai200-cosmos-rag --query "[0].name" -o tsv)
az cosmosdb sql container show -g rg-ai200-cosmos-rag -a "$A" -d ragstore -n chunks --query "resource.partitionKey.paths" -o tsv
```
Salida real:
```text
N                    E          Loc
-------------------  ---------  -------
cosmos-rag-<hash>    Succeeded  East US
/documentId
```
Si sale `Creating`, espera. Si el script da un error de capacidad en `eastus`, cambia `location` y repite la opción 1 (el script es idempotente: lo que ya existe se lo salta).

## Paso 6 · Dar acceso con Entra ID: dos roles (opción 2)
**Por qué:** el código no usa claves: entra con tu identidad (`DefaultAzureCredential`). Para eso hacen falta **dos roles**, porque Cosmos DB tiene **dos planos de permisos**:
- `Contributor` de ARM (`az role assignment`): gestionar la cuenta, BD y contenedores (plano de control).
- `Cosmos DB Built-in Data Contributor` (`az cosmosdb sql role assignment`, el RBAC propio de Cosmos): leer y escribir documentos (plano de datos).

Un rol de ARM, aunque sea Owner, **no** deja leer documentos. Es como tener permiso para crear un `Deployment` pero no para hacer `exec` en el pod.

Sin salir del menú: Enter → **`2`**.

Salida real:
```text
Configuring Microsoft Entra ID access...
Assigning Azure RBAC 'Contributor' role to '<usuario-del-lab>'...
Azure RBAC Contributor role assigned
Assigning 'Cosmos DB Built-in Data Contributor' role to '<usuario-del-lab>'...
Cosmos DB Data Contributor role assigned
Entra ID access configured for: <usuario-del-lab>
  - Azure RBAC Contributor: manage databases and containers
  - Cosmos DB Data Contributor: read/write data
```
✅ **Comprobación:**
```bash
A=$(az cosmosdb list -g rg-ai200-cosmos-rag --query "[0].name" -o tsv)
az cosmosdb sql role assignment list -g rg-ai200-cosmos-rag -a "$A" --query "length(@)" -o tsv
az role assignment list --scope "$(az cosmosdb show -g rg-ai200-cosmos-rag -n "$A" --query id -o tsv)" --query "[].roleDefinitionName" -o tsv
```
Salida real:
```text
1
Contributor
```
Esperado: `1` asignación de datos y `Contributor` en ARM. Si sale `0`, repite la opción 2. Si la app da luego `403 Forbidden`, espera 2-3 minutos: el rol de datos tarda en propagarse.

## Paso 7 · Comprobar el despliegue (opción 3)
**Por qué:** la opción 3 es de solo lectura y confirma de una vez que la cuenta, la BD, el contenedor y los dos roles están listos antes de generar la conexión.

Enter → **`3`**. Salida real:
```text
Checking deployment status...

Cosmos DB Account (cosmos-rag-<hash>):
  Status: Succeeded
  Cosmos DB account is ready
  Database ragstore: Created
  Container chunks: Created
  Entra ID access: <usuario-del-lab> (full control)
```
**Qué mirar:** `full control` significa que el script ve los **dos** roles. Si faltara uno, avisaría con `WARNING` (solo datos o solo plano de control).

✅ **Comprobación:** las cinco líneas como arriba. Si falta `full control`, repite la opción 2.

## Paso 8 · Generar el `.env` (opción 4) y salir (opción 5)
**Por qué:** la app necesita saber a qué cuenta, BD y contenedor conectarse. La opción 4 lo escribe en `.env` (bash) y `.env.ps1` (PowerShell). No lleva **ninguna clave**.

Enter → **`4`**. Salida real:
```text
Retrieving connection information...

Cosmos DB Connection Information
===========================================================
Endpoint: https://cosmos-rag-<hash>.documents.azure.com:443/
Database: ragstore
Container: chunks
Authentication: Microsoft Entra ID (DefaultAzureCredential)

Environment variables saved to .env and .env.ps1
```
Después, Enter → **`5`** para salir. Salir del menú **no** borra nada.

✅ **Comprobación:**
```bash
ls -la .env .env.ps1 && grep -c '^export COSMOS_' .env
```
Salida real: los dos ficheros (145 bytes cada uno) y `3`. Si falta el fichero, repite la opción 4. El `.env` de este lab se versiona en el repo: no tiene claves y la cuenta ya no existe.

## Paso 9 · Crear el entorno Python
**Por qué:** las librerías del lab (`azure-cosmos`, `azure-identity`, `flask`) se instalan en un `.venv` dentro de `client/`, sin tocar el Python del sistema. El lab pide Python 3.12 o superior.
```bash
python3 --version
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import azure.cosmos, azure.identity, flask; print('ok', azure.cosmos.__version__)"
cd ..
```
Salida real:
```text
Python 3.12.3
ok 4.17.1
```
**Qué mirar:** dentro del venv `python` sí existe (apunta a `python3`). `pip` instaló sin errores de TLS con el proxy. `client/.venv/` está en `.gitignore`.

⚠️ **Lo que pasó:** se dio la ruta `cd labs/lp4-01-cosmos-queries/client` estando ya dentro de `labs/lp4-01-cosmos-queries`:
```text
bash: cd: labs/lp4-01-cosmos-queries/client: No existe el archivo o el directorio
```
Mira dónde estás con `pwd`. Desde la carpeta del lab la ruta es solo `client`.

✅ **Comprobación:** `ok 4.x.x`. Si sale `ModuleNotFoundError`, el venv no está activo: `source client/.venv/bin/activate`.

## Paso 10 · Completar las 4 funciones de `client/rag_functions.py`
**Por qué:** son la interfaz entre la app y Cosmos DB. Cada función enseña un punto distinto de la escala de coste. El código es literal de la guía y va entre los marcadores `# BEGIN … FUNCTION` / `# END … FUNCTION` (el fichero del repo ya está completado).

| Función | Operación | Coste |
|---|---|---|
| `store_document_chunk` | `upsert_item`: inserta o reemplaza por `id` + partition key | Escritura: lo más caro por operación |
| `get_chunks_by_document` | Query con `partition_key=document_id`: **una sola partición** | Bajo-medio |
| `search_chunks_by_metadata` | Query por `category`/`source`/`tags` con `enable_cross_partition_query=True`: **todas las particiones** | La query más cara |
| `get_chunk_by_id` | `read_item(id, partition_key)`: **lectura puntual**, sin query | ≈ 1 RU, la más barata |

Los fragmentos clave:
```python
# 1. Escribir: upsert es idempotente (repetirlo no duplica). Las RU vienen en un header HTTP.
response = container.upsert_item(body=chunk)
ru_charge = response.get_response_headers()['x-ms-request-charge']

# 2. Un documento: la partition key limita la query a una partición.
items = container.query_items(
    query="SELECT c.id, c.content, c.metadata, c.chunkIndex, c.createdAt FROM c "
          "WHERE c.documentId = @documentId ORDER BY c.chunkIndex OFFSET 0 LIMIT @limit",
    parameters=[{"name": "@documentId", "value": document_id}, {"name": "@limit", "value": limit}],
    partition_key=document_id)

# 3. Por metadatos: no se conoce la partición, así que hay fan-out a todas.
where_clauses.append("ARRAY_CONTAINS(c.metadata.tags, @tag)")   # buscar dentro de un array
items = container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True)

# 4. Lectura puntual: con id + partition key Cosmos va directo al documento.
item = container.read_item(item=chunk_id, partition_key=document_id)   # 404 → devuelve None
```
**Qué hace cada detalle:**
- Los valores van como parámetros (`@documentId`, `@tag`), nunca pegados en el SQL: no hay inyección. El f-string de la función 3 solo inserta fragmentos fijos del propio código.
- `OFFSET 0 LIMIT @limit` es la sintaxis de Cosmos para limitar: no existe `LIMIT` a secas.
- `upsert_item` reemplaza el documento **entero** (no hace merge). Para cambiar un campo existe `patch_item`.
- La función 3 solo usa el **primer** tag (`filters["tags"][0]`): es una simplificación del ejercicio.
- `get_container()` crea un `CosmosClient` en cada llamada. En producción se crea una vez y se reutiliza.

✅ **Comprobación** (desde `client/`, con el venv activo):
```bash
python -c "import rag_functions as r; print([n for n in ('store_document_chunk','get_chunks_by_document','search_chunks_by_metadata','get_chunk_by_id') if callable(getattr(r,n,None))])"
```
Salida real:
```text
['store_document_chunk', 'get_chunks_by_document', 'search_chunks_by_metadata', 'get_chunk_by_id']
```
Es una prueba de sintaxis: todavía no toca Cosmos. Si sale `IndentationError`, revisa que el código pegado esté alineado con los marcadores.

## Paso 11 · Cargar el `.env` en la terminal
**Por qué:** el código lee `COSMOS_ENDPOINT`, `COSMOS_DATABASE` y `COSMOS_CONTAINER` del entorno. Solo viven en la terminal donde se hace el `source`.
```bash
source .env
for v in COSMOS_ENDPOINT COSMOS_DATABASE COSMOS_CONTAINER; do [ -n "${!v:-}" ] && echo "$v definida" || echo "$v FALTA"; done
```
Salida real:
```text
COSMOS_ENDPOINT definida
COSMOS_DATABASE definida
COSMOS_CONTAINER definida
```
✅ **Comprobación:** tres `definida` (se comprueba que existen sin mostrar los valores). Si alguna dice `FALTA`, mira con `pwd` que estás en la carpeta del lab y repite el `source`.

## Paso 12 · Arrancar la app Flask
**Por qué:** la app es la forma visual de ejecutar las 4 funciones contra Cosmos DB. Corre en el equipo y escucha solo en `127.0.0.1`.
```bash
source client/.venv/bin/activate && cd client && python app.py
```
Salida real:
```text
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
✅ **Comprobación** (en otra terminal):
```bash
curl -s -m 20 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/
```
Salida real: `200`. Si la app da `ValueError: COSMOS_ENDPOINT…`, la terminal no tenía el `.env`: `Ctrl+C`, `source ../.env` y relanza. Si entras al equipo por SSH, reenvía el puerto con `ssh -L 5000:127.0.0.1:5000 …` para abrirla en tu navegador.

## Paso 13 · Cargar los chunks de ejemplo («Load Sample Chunks»)
**Por qué:** mete datos para probar. El botón hace `POST /load-data`: lee `client/sample_chunks.json` (**12 chunks de 4 documentos** ficticios) y llama 12 veces a `store_document_chunk`, una escritura por chunk, cada una en la partición de su documento. Suma las RU de las 12.

**Salida no guardada** (el mensaje no se pegó). Se ejecutó: lo prueban los resultados de los pasos 14 y 16, que incluyen chunks de las muestras.

Esperado:
```text
Successfully loaded 12 chunks! Total RU: …     (≈ 120 RU: ≈ 10 RU por chunk, ver paso 14)
```
**Qué mirar:** recarga la página después: los desplegables de documentos y categorías se rellenan leyendo Cosmos. Pulsar dos veces no duplica (es `upsert`).

✅ **Comprobación** (sin navegador, en otra terminal):
```bash
curl -s -L -X POST http://127.0.0.1:5000/load-data | grep -iE "Successfully|Error"
```
Si sale `Error loading data: … 403`, el rol de datos no se ha propagado: espera 2-3 minutos y repite.

## Paso 14 · Ejecutar los tests («Run Tests»)
**Por qué:** `test_workflow.py` prueba las 4 funciones de extremo a extremo (credencial, rol de datos, red a través del proxy y Cosmos). Escribe 3 chunks propios: `test-doc-001` (2 chunks) y `test-doc-002` (1).

Salida real:
```text
Store Document Chunks            Stored 3 chunks, total RU: 29.70                 passed
Get Chunks by Document           Retrieved 2 chunks for test-doc-001              passed
Search by Category               Found 5 chunks with category 'databases'         passed
Search by Tag                    Found 2 chunks with tag 'serverless'             passed
Point Read (Get Chunk by ID)     Retrieved chunk with 58 characters               passed
```
**Qué mirar:**
- **29,70 RU / 3 chunks ≈ 9,9 RU por escritura.** Es más de lo que se estimó en clase (5-6 RU por KB): Cosmos **indexa todas las propiedades por defecto** (`metadata`, el array `tags`, el `embedding` vacío) y cada escritura actualiza el índice. En LP4-02 se excluye `/embedding/*` del índice normal por esto.
- **2 chunks de `test-doc-001`:** consulta de **una partición**. No ve `test-doc-002`.
- **5 con categoría `databases`:** 2 del test y 3 de las muestras. Es una consulta **cross-partition**.
- **2 con tag `serverless`:** 1 del test y 1 de las muestras (`ARRAY_CONTAINS`).
- **58 caracteres:** la longitud de `"Azure Cosmos DB is a fully managed NoSQL database service."`, leída con la **point read**.
- Los tests solo exigen `>=` (≥2, ≥2, ≥1): demuestran que las funciones responden, no el contenido exacto. Y **escriben datos**: `test-doc-001/002` se quedan en el contenedor hasta el cleanup.

✅ **Comprobación:**
```bash
curl -s -X POST http://127.0.0.1:5000/run-tests | grep -ioE "passed|failed" | sort | uniq -c
```
Esperado: `5 passed`. Si alguno sale `failed`, el texto del test dice qué función falla. Revisa ese bloque en `rag_functions.py`.

## Paso 15 · Leer un documento entero («Get Chunks»)
**Por qué:** es el patrón normal de RAG: «dame el documento completo para dar contexto al modelo». Usa `get_chunks_by_document`: una sola partición, ordenada por `chunkIndex`.

Se eligió `test-doc-001` (la guía propone `doc-azure-overview`). Salida real:
```text
Found 2 chunk(s)
test-doc-001-chunk-0 (index: 0)   Azure Cosmos DB is a fully managed NoSQL database service.          · databases, nosql, cosmosdb
test-doc-001-chunk-1 (index: 1)   Cosmos DB offers multiple APIs including NoSQL, MongoDB, and Cassandra. · databases, nosql, api
```
**Qué mirar:** salen en orden 0 y 1 por el `ORDER BY c.chunkIndex`. Con `doc-azure-overview` deberían salir 3 chunks (0, 1 y 2).

✅ **Comprobación:** el número de chunks coincide con los del documento elegido (2 para `test-doc-001`, 3 para `doc-azure-overview`). Si el desplegable solo muestra `test-doc-*`, no se hizo el paso 13.

## Paso 16 · Buscar por metadatos («Search by Metadata»)
**Por qué:** aquí no se conoce el documento: se busca por un atributo. Como `category` **no es la partition key**, Cosmos no sabe dónde están los datos y consulta **todas** las particiones (cross-partition). Es la consulta más cara de las cuatro.

Categoría `ai-applications`, tag vacío. Salida real:
```text
Filters: category="ai-applications" | Found 4 chunk(s)
doc-rag-patterns / doc-rag-patterns-chunk-0  · ai-applications, rag, llm, ai
doc-rag-patterns / doc-rag-patterns-chunk-1  · ai-applications, rag, chunking, documents
doc-rag-patterns / doc-rag-patterns-chunk-2  · ai-applications, rag, embeddings, vector-search
doc-rag-patterns / doc-rag-patterns-chunk-3  · ai-applications, rag, metadata, filtering
```
(Cada chunk trae además su texto. Aquí solo se muestran los tags.)

**Qué mirar:** los 4 resultados son de **un solo documento**, pero la consulta sigue siendo cross-partition. Lo que decide el coste es **la forma de la consulta**, no dónde estén los datos.

La segunda búsqueda de la guía (misma categoría + tag `embeddings`): **salida no guardada**. Esperado: **1** resultado, `doc-rag-patterns-chunk-2`, el único con ese tag.

✅ **Comprobación:**
```bash
curl -s -X POST -d "category=ai-applications" http://127.0.0.1:5000/search-metadata | grep -oE "doc-[a-z-]+-chunk-[0-9]+" | sort -u | wc -l
```
Esperado: `4`. Si sale `0`, no se cargaron las muestras (paso 13).

## Paso 17 · Consultas SQL en el Query Explorer (Task 6) — no hecho
Se saltó por tiempo: es práctica de SQL y no cambia nada en Azure. El Query Explorer (`query_executor.py`) solo acepta `SELECT` y siempre permite el fan-out. Resultados esperados, calculados de `sample_chunks.json` y `test_workflow.py`:

| Query | Qué enseña | Esperado |
|---|---|---|
| `SELECT c.id, c.chunkIndex, c.content, c.metadata FROM c WHERE c.documentId = 'doc-azure-overview' ORDER BY c.chunkIndex` | Igualdad sobre la partition key: una partición | 3 chunks (0, 1, 2) |
| `SELECT c.documentId, c.id, c.content, c.metadata.category FROM c WHERE c.metadata.category = 'cloud-services'` | Campo anidado que no es partition key: cross-partition | 3 chunks de `doc-azure-overview` |
| `SELECT DISTINCT c.documentId, c.metadata.category, c.metadata.source FROM c` | Inventario de lo que hay | 6 filas (4 de muestras + 2 de tests) |
| `SELECT c.documentId, c.id, c.content, c.metadata.tags FROM c WHERE ARRAY_CONTAINS(c.metadata.tags, 'compute')` | Buscar dentro de un array | 2: `doc-azure-overview-chunk-2` y `doc-azure-functions-chunk-0` |

✅ **Comprobación:** si la tercera devuelve 4 filas, faltan los `test-doc-*` (no se hizo el paso 14). Si devuelve 2, faltan las muestras (paso 13).

Al terminar, **`Ctrl+C`** en la terminal de Flask.

---

## Cleanup (obligatorio al acabar)
**Por qué:** la cuenta cuesta dinero mientras exista. Borrar el resource group borra la cuenta, la BD, el contenedor, los datos y las asignaciones de rol.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-rag --no-wait --yes
az group show -n rg-ai200-cosmos-rag --query properties.provisioningState -o tsv
```
Salida real (comprobación justo antes de lanzarlo, y justo después):
```text
Succeeded        ← todavía no se había lanzado el borrado
Deleting         ← ya lanzado
```
Minutos después, en la misma suscripción, `az group list -o table` seguía mostrando `rg-ai200-cosmos-rag  eastus  Deleting`.

⚠️ **No verificado.** El lab 10 se abrió con otra sesión de la plataforma, que trajo **otra suscripción** (`XLabs-274`). Desde ella, `az group exists --name rg-ai200-cosmos-rag` devuelve `false` siempre, porque ese grupo nunca existió allí. Ese `false` **no prueba nada**. Se documenta como «borrado lanzado, no verificado».

✅ **Comprobación correcta** (en la misma suscripción y **antes** de abrir la sesión del lab siguiente):
```bash
az account show --query name -o tsv           # debe ser XLabs-278
az group exists --name rg-ai200-cosmos-rag    # true mientras borra; false al acabar (unos minutos)
```
Si pasados 10-15 minutos sigue en `true`, mira el `provisioningState`. Si sale `Failed`, relanza el `delete`.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Orden «python» no encontrada` | En el equipo solo existe `python3` | `python3 azdeploy.py` (paso 5) |
| `REQUESTS_CA_BUNDLE … invalid file path` | La variable apuntaba a una ruta inexistente | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` (paso 0) |
| `cd: labs/lp4-01-cosmos-queries/client: No existe` | Ruta relativa dada desde la raíz del repo, estando ya en la carpeta del lab | `pwd` y `cd client` (paso 9) |
| El `Contributor` de ARM no basta para leer datos | Cosmos tiene un RBAC propio en el plano de datos | Opción 2: también `Cosmos DB Built-in Data Contributor` (paso 6) |
| `az group exists` da `false` para este grupo desde el lab 10 | La sesión nueva es **otra suscripción** | Verificar el cleanup antes de cambiar de sesión |
