# Salidas reales · LP4-01 Build queries for Azure Cosmos DB (Lab 9 · AI-200-LP04M01)

Saneadas: sin ID de suscripción, tenant ni usuario del lab; hash de la cuenta como `<hash>`. Ejecutado el 05/11/2026 en Linux (`mol-bastion`). Todo el despliegue va por `az` (vía `azdeploy.py`). El grupo `rg-ai200-cosmos-rag` es **nuestro**.

## 1. Login y suscripción
```console
$ az login --use-device-code
Tenant: Lab Directory
Subscription: XLabs-<n> (<subscription-id>)
```
**Qué mirar:** una sola suscripción de la plataforma del lab. `--use-device-code` evita depender del navegador del PC.

## 2. Descarga del starter (dentro del repo, `labs/lp4-01-cosmos-queries/`)
```console
$ curl -fLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-build-query-python.zip
100 16424  100 16424    0     0  19046
$ unzip -o cosmosdb-build-query-python.zip && ls
azdeploy.py  client  cosmosdb-build-query-python.zip
```
**Qué mirar:** `client/` contiene `app.py`, `rag_functions.py` (las 4 funciones a completar), `query_executor.py`, `test_workflow.py`, `sample_chunks.json`, `requirements.txt` (`flask`, `azure-cosmos`, `azure-identity`), `templates/` y `static/`. `curl` no tuvo problemas con el proxy.

## 3. Valores de `azdeploy.py`
```console
$ sed -i 's|<your-resource-group-name>|rg-ai200-cosmos-rag|; s|<your-azure-region>|eastus|' azdeploy.py
$ sed -n '5,6p' azdeploy.py
rg = "rg-ai200-cosmos-rag"  # Resource Group name
location = "eastus"   # Azure region for the resources
$ grep -nE 'DATABASE_NAME *=|CONTAINER_NAME *=' azdeploy.py
20:DATABASE_NAME = "ragstore"
21:CONTAINER_NAME = "chunks"
```
**Qué mirar:** la guía menciona `azdeploy.ps1`, pero el zip trae `azdeploy.py` (Linux/Windows). El script solo llama a `az`, sin `kubectl` ni `docker`.

## 4. Proveedor registrado
```console
$ az provider show --namespace Microsoft.DocumentDB --query registrationState -o tsv
Registered
```
**Qué mirar:** ya estaba `Registered`; si no, `az provider register --namespace Microsoft.DocumentDB`.

## 5. Opción 1 del menú: cuenta, base de datos y contenedor
```console
Checking/creating resource group 'rg-ai200-cosmos-rag'...
Resource group created: rg-ai200-cosmos-rag

Creating Azure Cosmos DB for NoSQL account 'cosmos-rag-<hash>' in 'eastus'...
This may take several minutes...
Cosmos DB account created successfully
Creating database 'ragstore'...
Database created: ragstore
Creating container 'chunks'...
Container created: chunks (partition key: /documentId)
```
Verificación en solo lectura:
```console
$ az cosmosdb list -g rg-ai200-cosmos-rag --query "[].{n:name, e:provisioningState, loc:location}" -o table
N                    E          Loc
-------------------  ---------  -------
cosmos-rag-<hash>    Succeeded  East US
$ az cosmosdb sql container show -g rg-ai200-cosmos-rag -a cosmos-rag-<hash> -d ragstore -n chunks --query "resource.partitionKey.paths" -o tsv
/documentId
```
**Qué mirar:** la cuenta es **serverless** (`EnableServerless`, sin RU aprovisionadas) con consistencia `Session`. El nombre sale de `cosmos-rag-` + 8 caracteres del SHA1 del object ID del usuario: único globalmente y estable al relanzar. La partition key `/documentId` agrupa los chunks de un mismo documento en una partición lógica.

## 6. Opción 2 del menú: acceso con Entra ID (dos roles)
```console
Configuring Microsoft Entra ID access...
Assigning Azure RBAC 'Contributor' role to '<usuario-del-lab>'...
Azure RBAC Contributor role assigned
Assigning 'Cosmos DB Built-in Data Contributor' role to '<usuario-del-lab>'...
Cosmos DB Data Contributor role assigned
```
Verificación en solo lectura:
```console
$ az cosmosdb sql role assignment list -g rg-ai200-cosmos-rag -a cosmos-rag-<hash> --query "length(@)" -o tsv
1
$ az role assignment list --scope <id-de-la-cuenta> --query "[].roleDefinitionName" -o tsv
Contributor
```
**Qué mirar:** hay **dos planos de permisos distintos**. `Contributor` (RBAC de ARM) gestiona BD y contenedores (plano de control); `Cosmos DB Built-in Data Contributor` (RBAC propio de Cosmos, `az cosmosdb sql role assignment`) lee y escribe documentos (plano de datos). Analogía K8s: crear un `Deployment` frente a hacer `exec` en el pod. Un rol de ARM, aunque sea Owner, no permite leer documentos con `DefaultAzureCredential`.

## 7. Opción 3 del menú: estado del despliegue
```console
Checking deployment status...

Cosmos DB Account (cosmos-rag-<hash>):
  Status: Succeeded
  Cosmos DB account is ready
  Database ragstore: Created
  Container chunks: Created
  Entra ID access: <usuario-del-lab> (full control)
```
**Qué mirar:** «full control» significa que el script ve **los dos roles** (Contributor de ARM y Data Contributor de Cosmos). Si faltara uno, avisaría con `WARNING` (solo datos, o solo plano de control). Es la comprobación de que ya se puede pasar a la opción 4.

## 8. Opción 4 del menú: información de conexión (`.env`)
```console
Retrieving connection information...

Cosmos DB Connection Information
===========================================================
Endpoint: https://cosmos-rag-<hash>.documents.azure.com:443/
Database: ragstore
Container: chunks
Authentication: Microsoft Entra ID (DefaultAzureCredential)

Environment variables saved to .env and .env.ps1
```
**Qué mirar:** el `.env` solo trae `COSMOS_ENDPOINT`, `COSMOS_DATABASE` y `COSMOS_CONTAINER`: **ninguna clave**. La autenticación la hace `DefaultAzureCredential` con tu sesión de `az login` y el rol de datos del paso 6. Para cargarlo: `source .env`. Está en `.gitignore`, no se sube.

## 9. Task 5: app Flask y «Run Tests» (5/5 passed)
Servidor (terminal con `.env` cargado y el venv de `client/`):
```console
$ source client/.venv/bin/activate && cd client && python app.py
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
$ curl -s -m 20 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/
200
```
Resultado del botón **Run Tests**:
```console
Store Document Chunks            Stored 3 chunks, total RU: 29.70                       passed
Get Chunks by Document           Retrieved 2 chunks for test-doc-001                    passed
Search by Category               Found 5 chunks with category 'databases'               passed
Search by Tag                    Found 2 chunks with tag 'serverless'                   passed
Point Read (Get Chunk by ID)     Retrieved chunk with 58 characters                     passed
```
**Qué mirar:**
- **RU de escritura:** 29,70 RU / 3 chunks ≈ **9,9 RU por chunk**, más de lo que cabía esperar para ~1 KB. Cosmos indexa todas las propiedades por defecto (incluidos `metadata`, el array `tags` y el `embedding` vacío), y eso encarece cada escritura. En el lab 10 se excluye `/embedding/*` del índice.
- **3 chunks guardados, 2 leídos:** el test guarda 3 chunks de dos documentos (`test-doc-001` con 2 y `test-doc-002` con 1). La consulta por documento es de **una partición** y solo ve `test-doc-001`.
- **5 con categoría `databases`:** son los 2 del test más los de las muestras cargadas antes; la consulta es **cross-partition**. Con `serverless` salen 2 (1 del test y 1 de las muestras).
- **58 caracteres:** longitud de `"Azure Cosmos DB is a fully managed NoSQL database service."`, devuelta por la **point read** (la operación más barata).
- Los tests solo exigen `>=` (≥2, ≥2, ≥1), no cifras exactas: comprueban que las funciones responden, no el contenido exacto.
- Los tests **escriben datos** (`test-doc-001/002`) que se quedan en el contenedor hasta el Cleanup.

## 10. Consultas desde la app (Get Chunks y Search by Metadata)
**Get Chunks** con `test-doc-001` (una partición, ordenado por `chunkIndex`):
```console
Found 2 chunk(s)
test-doc-001-chunk-0 (index: 0)  · tags: databases, nosql, cosmosdb
test-doc-001-chunk-1 (index: 1)  · tags: databases, nosql, api
```
**Search by Metadata** con `category="ai-applications"` y sin tag (cross-partition):
```console
Filters: category="ai-applications" | Found 4 chunk(s)
doc-rag-patterns / doc-rag-patterns-chunk-0  · ai-applications, rag, llm, ai
doc-rag-patterns / doc-rag-patterns-chunk-1  · ai-applications, rag, chunking, documents
doc-rag-patterns / doc-rag-patterns-chunk-2  · ai-applications, rag, embeddings, vector-search
doc-rag-patterns / doc-rag-patterns-chunk-3  · ai-applications, rag, metadata, filtering
```
**Qué mirar:**
- Los 4 resultados son de **un solo documento** (`doc-rag-patterns`), pero la query sigue siendo **cross-partition**: filtra por `category`, no por la partition key, así que Cosmos no puede saber de antemano en qué partición están y consulta todas.
- Solo uno de los 4 chunks lleva el tag `embeddings` (el `chunk-2`), así que añadir ese tag deja **1 resultado**.
- Cada chunk guarda su texto (`content`) además de los tags; aquí se resumen los tags por brevedad.

## Incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Orden «python» no encontrada` | En este equipo solo existe `python3` | Usar `python3 azdeploy.py` |
| `ERROR: REQUESTS_CA_BUNDLE environment variable is specified with an invalid file path` | La variable apuntaba a una ruta inexistente en esa shell | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal |

## 11. Cleanup (no verificado)
```console
$ az group delete --name rg-ai200-cosmos-rag --no-wait --yes
$ az group show -n rg-ai200-cosmos-rag --query properties.provisioningState -o tsv
Deleting
```
**Qué mirar:** se vio `Deleting`, pero no se llegó a ver `false`: al abrir la sesión del lab 10 la suscripción cambió y `az group exists` devuelve `false` allí aunque el grupo siga vivo en la anterior. Se documenta como **borrado lanzado, no verificado**.

**No guardadas** (no se pegaron): el mensaje de «Load Sample Chunks» con sus RU, la búsqueda con el tag `embeddings` y las 4 consultas del Query Explorer (Task 6, que se saltó).
