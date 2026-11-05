# Salidas reales · LP4-02 Implement vector search with Azure Cosmos DB (Lab 10 · AI-200-LP04M02)

Saneadas: sin ID de suscripción, tenant ni usuario del lab; hash de la cuenta como `<hash>`. Ejecutado el 05/11/2026 en Linux (`mol-bastion`). Todo el despliegue va por `az` (vía `azdeploy.py`). El grupo `rg-ai200-cosmos-vector` es **nuestro**.

## 1. Login: suscripción distinta a la del lab 9
```console
$ az login --use-device-code
Tenant: Lab Directory
Subscription: XLabs-274 (<subscription-id>)
$ az group list -o table
az104-rg-region1  eastus  Deleting          # de otro curso, no se toca
$ az provider show --namespace Microsoft.DocumentDB --query registrationState -o tsv
Registered
```
**Qué mirar:** cada sesión de la plataforma entrega una **suscripción nueva** (aquí `XLabs-274`; el lab 9 fue en `XLabs-278`). Por eso el cleanup del lab anterior se lanza y se verifica **antes** de cambiar de sesión: desde otra suscripción `az group exists` devuelve `false` aunque el grupo siga vivo en la anterior.

## 2. Starter (dentro del repo, `labs/lp4-02-cosmos-vector-search/`)
```console
$ curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-implement-vector-python.zip
$ unzip -oq cosmosdb-implement-vector-python.zip && ls client
app.py  requirements.txt  sample_vectors.json  setup_container.py  static  templates  vector_functions.py
$ sed -n '5,6p' azdeploy.py
rg = "rg-ai200-cosmos-vector"  # Resource Group name
location = "eastus"   # Azure region for the resources
$ grep -nE 'DATABASE_NAME *=|CONTAINER_NAME *=|capabilities' azdeploy.py
20:DATABASE_NAME = "vectorstore"
21:CONTAINER_NAME = "vectors"
203:        "--capabilities", "EnableServerless", "EnableNoSQLVectorSearch",
```
**Qué mirar:** la cuenta se crea **serverless** y con la capability `EnableNoSQLVectorSearch`, imprescindible para los índices vectoriales. `vector_functions.py` y `setup_container.py` traen marcadores `BEGIN/END` vacíos que se completan en el lab.

## 3. Opción 1 del menú: cuenta, base de datos y contenedor con políticas vectoriales
```console
Creating container with vector search policies...
Container created: vectors

  Vector embedding policy:
    - Path: /embedding
    - Data type: float32
    - Distance function: cosine
    - Dimensions: 256

  Indexing policy:
    - Vector index type: diskANN
    - Embedding path excluded from standard indexing
```
Verificación en solo lectura:
```console
$ az cosmosdb list -g rg-ai200-cosmos-vector --query "[].{n:name,e:provisioningState,cap:capabilities[].name}" -o json
[{"cap": ["EnableServerless", "EnableNoSQLVectorSearch"], "e": "Succeeded", "n": "cosmos-vector-<hash>"}]
$ az cosmosdb sql container show -g rg-ai200-cosmos-vector -a cosmos-vector-<hash> -d vectorstore -n vectors \
    --query "{pk:resource.partitionKey.paths, vec:resource.vectorEmbeddingPolicy, idx:resource.indexingPolicy}"
pk:  ["/documentId"]
vec: {"vectorEmbeddings": [{"dataType": "float32", "dimensions": 256, "distanceFunction": "cosine", "path": "/embedding"}]}
idx: includedPaths ["/*"]; excludedPaths ["/embedding/*", "/\"_etag\"/?"];
     vectorIndexes [{"path": "/embedding", "type": "diskANN", "quantizationByteSize": 64, "indexingSearchListSize": 100}]
```
**Qué mirar:**
- **Dos piezas distintas.** La *vector embedding policy* (ruta, tipo de dato, dimensiones y función de distancia) describe los vectores y **no se puede cambiar** una vez creado el contenedor. El *vector index* (`diskANN`, aproximado y basado en grafo) vive en la indexing policy y sí se puede cambiar.
- **`/embedding/*` está excluido del índice normal**: se indexa solo con el índice vectorial. Así las escrituras no pagan el coste de indexar 256 floats como propiedades normales (en el lab 9, con el índice por defecto, cada chunk costaba ~9,9 RU).
- Partition key `/documentId`, igual que en el lab 9.
- El menú de este script no es el del lab 9: la opción 1 crea ya el contenedor vectorial; el acceso con Entra ID está en la opción 3 (en el lab 9 era la 2).

## 4. Acceso con Entra ID (dos roles)
```console
Configuring Microsoft Entra ID access...
Azure RBAC Contributor role assigned
Cosmos DB Data Contributor role assigned
Entra ID access configured for: <usuario-del-lab>
```
```console
$ az cosmosdb sql role assignment list -g rg-ai200-cosmos-vector -a cosmos-vector-<hash> --query "length(@)" -o tsv
1
```
**Qué mirar:** igual que en el lab 9: `Contributor` (ARM, plano de control) más `Cosmos DB Built-in Data Contributor` (RBAC propio de Cosmos, plano de datos).

## 5. Estado y conexión
```console
Checking deployment status...
Cosmos DB Account (cosmos-vector-<hash>):
  Status: Succeeded
  Cosmos DB account is ready
  Vector search capability enabled
  Database vectorstore: Created
  Container vectors: Created
  Entra ID access: <usuario-del-lab> (full control)

Retrieving connection information...
Endpoint: https://cosmos-vector-<hash>.documents.azure.com:443/
Database: vectorstore
Container: vectors
Authentication: Microsoft Entra ID (DefaultAzureCredential)
Environment variables saved to .env and .env.ps1
```
```console
$ ls -la .env && grep -c '^export COSMOS_' .env
-rw-r--r-- 1 jgonzalezr mol-bastion 152 nov  5 19:48 .env
3
```
**Qué mirar:** el `.env` solo trae endpoint, base de datos y contenedor, sin claves. Está en `.gitignore`.

## 6. App Flask: carga de tickets con embeddings
```console
Successfully loaded 12 tickets with embeddings! Total RU: 640.68
```
**Qué mirar:** 640,68 RU / 12 tickets ≈ **53,4 RU por escritura**, unas 5 veces lo que costó un chunk sin vector en el lab 9 (≈ 9,9 RU). Cada ticket lleva un vector de 256 `float32` y además hay que insertarlo en el índice DiskANN. Excluir `/embedding/*` del índice normal evita indexar los 256 valores como propiedades sueltas, pero el índice vectorial tiene su propio coste de escritura.

## 7. Búsqueda por similitud (`vector_similarity_search`)
Consulta: `"I can't login to my account"`, top 5 (se pegaron los 4 primeros):
```console
0.9997  ticket-technical-001-chunk-0  · technical, login, password, authentication
0.9920  ticket-shipping-002-chunk-0   · shipping, address-change, order-modification
0.9918  ticket-account-001-chunk-0    · account, email, profile, update
0.9917  ticket-account-002-chunk-0    · account (borrar la cuenta y los datos)
```
**Qué mirar:**
- **Con `cosine`, la puntuación más alta es la más parecida** y `ORDER BY VectorDistance(...)` la pone primero. Aquí el primero es el ticket de login (0,9997), que es el correcto.
- **Del segundo al cuarto la diferencia es mínima** (0,9920 → 0,9917) y el orden no es semánticamente razonable: un ticket de envíos (`shipping`) queda por delante de dos de cuenta (`account`), más cercanos a «no puedo entrar en mi cuenta». Lo más probable es que los embeddings de `sample_vectors.json` estén precalculados de forma sencilla y solo discriminen bien el mejor resultado. Es una hipótesis, no se ha comprobado.
- Los datos de los tickets son ficticios, del starter público.

## 8. Cleanup (no verificado)
```console
$ az group delete --name rg-ai200-cosmos-vector --no-wait --yes
$ az group show -n rg-ai200-cosmos-vector --query properties.provisioningState -o tsv
Deleting
```
**Qué mirar:** se vio `Deleting`, pero no se llegó a ver `false`: la sesión del lab 11 trajo otra suscripción. Se documenta como **borrado lanzado, no verificado**.

**No guardadas** (no se pegaron): la búsqueda filtrada por categoría y el 5.º resultado de la búsqueda por similitud.
