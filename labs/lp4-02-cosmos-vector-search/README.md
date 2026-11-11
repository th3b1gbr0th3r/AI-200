# Lab LP4-02 · Implement vector search with Azure Cosmos DB (plataforma: Lab 10 · AI-200-LP04M02)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/02-build-semantic-search.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (05/11/2026): parcial.** Hechos los pasos 0-13: despliegue, contenedor vectorial, 3 funciones, carga de 12 tickets y búsqueda por similitud. **No hecho:** la búsqueda filtrada por categoría (paso 14; no se pegó ningún resultado). **Cleanup lanzado, no verificado** (se vio `Deleting`; la sesión del lab 11 trajo otra suscripción).
- Lab anterior: [LP4-01](../lp4-01-cosmos-queries/README.md) · Lab siguiente: [LP4-03](../lp4-03-cosmos-optimize/README.md). Notas de clase: [`docs/modulos/04-cosmosdb.md`](../../docs/modulos/04-cosmosdb.md). Origen MIT de `azdeploy.py` y `client/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: sin IDs de suscripción ni tenant (`<sub-id>`), sin usuario del lab (`<usuario-del-lab>`) y con el sufijo de la cuenta como `<hash>`.

## Qué se construye
Una búsqueda **semántica** de tickets de soporte: en vez de buscar por palabras, se busca por **significado**. Cada ticket lleva un *embedding* (un vector de 256 números que resume su significado) y Cosmos DB devuelve los tickets cuyo vector está más cerca del vector de la pregunta.

```
azdeploy.py 1 → RG rg-ai200-cosmos-vector + cuenta serverless cosmos-vector-<hash> con EnableNoSQLVectorSearch + BD vectorstore
azdeploy.py 2 → contenedor vectors (/documentId) con vector embedding policy (/embedding, float32, cosine, 256)
                + índice vectorial diskANN (y /embedding/* fuera del índice normal)
azdeploy.py 3 → roles Contributor (ARM) + Cosmos DB Built-in Data Contributor (datos)
azdeploy.py 4 → estado · 5 → .env (endpoint, BD, contenedor; sin claves) · 6 → salir
client/vector_functions.py → guardar ticket con vector · búsqueda por similitud · búsqueda filtrada por categoría
client/app.py (Flask)      → carga 12 tickets, busca por similitud · http://127.0.0.1:5000
```
- Los embeddings vienen **precalculados** en `client/sample_vectors.json` (12 tickets de 4 categorías: billing, technical, account y shipping), y también los de las preguntas. No se llama a ningún modelo ni hace falta Azure OpenAI.

**Objetivo en cristiano:** guardar vectores en Cosmos DB y pedirle «los 5 más parecidos a este». Se aprende qué hay que declarar en el contenedor para que eso funcione, y cuánto cuesta escribir un documento con vector frente a uno sin vector (LP4-01).

### Los conceptos nuevos (con analogía de sistemas)
| Concepto | Qué es | Analogía |
|---|---|---|
| `EnableNoSQLVectorSearch` | *Capability* de la cuenta. Sin ella no se pueden crear índices vectoriales | Un *feature gate* que se activa en el cluster |
| **Vector embedding policy** | Describe los vectores: ruta (`/embedding`), tipo (`float32`), dimensiones (256) y función de distancia (`cosine`). **No se puede cambiar** una vez creado el contenedor | Un campo inmutable del spec: para cambiarlo hay que recrear el objeto |
| **Vector index** (`diskANN`) | Índice aproximado basado en un grafo de vecinos. Vive en la *indexing policy* y **sí** se puede cambiar | Un índice que se puede reconstruir sin tocar los datos |
| `/embedding/*` en `excludedPaths` | Los 256 números no se indexan como propiedades sueltas: solo con el índice vectorial | No indexar en el buscador de logs un campo que nunca filtras |
| `VectorDistance(a, b)` | Función SQL de Cosmos que compara dos vectores con la función de la política | El «score» de un buscador |

---

## Paso 0 · Preparar la terminal
**Por qué:** `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa. Hay que exportarlo en cada terminal nueva. `deactivate` sale del `.venv` de LP4-01 si seguía activo.
```bash
cd ~/claude/AI-200-Developing/labs/lp4-02-cosmos-vector-search
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `[ -n "${REQUESTS_CA_BUNDLE:-}" ] && echo "definida: $REQUESTS_CA_BUNDLE"` debe mostrar `/etc/ssl/certs/ca-certificates.crt`. Si no, repite el `export`.

## Paso 1 · `az login` con el usuario del lab 10
**Por qué:** cada lab de la plataforma trae su usuario temporal y **su propia suscripción**.
```bash
az login --use-device-code
az account show --query "{n:name,e:state}" -o tsv
az group list -o table
az provider show --namespace Microsoft.DocumentDB --query registrationState -o tsv
```
Salida real:
```text
[1] *  XLabs-274            <sub-id>                              Lab Directory
Tenant: Lab Directory
Subscription: XLabs-274 (<sub-id>)

XLabs-274	Enabled
Name              Location    Status
----------------  ----------  --------
az104-rg-region1  eastus      Deleting
Registered
```
**Qué mirar:**
- La suscripción es **nueva**: `XLabs-274` (LP4-01 fue en `XLabs-278`).
- `az104-rg-region1` es de otro curso de la plataforma: **no se toca**. No hay ningún `rg-ai200-*`.
- `Microsoft.DocumentDB` ya está `Registered`.

⚠️ **Lo que pasó:** desde aquí, `az group exists --name rg-ai200-cosmos-rag` (el grupo de LP4-01) devolvió `false`. **No prueba** que se borrara: ese grupo vivía en otra suscripción. Por eso el cleanup de LP4-01 quedó «no verificado».

✅ **Comprobación:** `XLabs-274` en `Enabled` y `Registered`. Si sale `NotRegistered`, lanza `az provider register --namespace Microsoft.DocumentDB`.

## Paso 2 · Descargar el starter y poner los valores de `azdeploy.py`
**Por qué:** igual que en LP4-01: el zip trae `azdeploy.py` (solo llama a `az`) y `client/`. Hay que cambiar solo el resource group y la región.
```bash
curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-implement-vector-python.zip
unzip -oq cosmosdb-implement-vector-python.zip && ls client
sed -i 's|<your-resource-group-name>|rg-ai200-cosmos-vector|; s|<your-azure-region>|eastus|' azdeploy.py
sed -n '5,6p' azdeploy.py
grep -nE 'DATABASE_NAME *=|CONTAINER_NAME *=|"--capabilities"' azdeploy.py
```
Salida real:
```text
app.py  requirements.txt  sample_vectors.json  setup_container.py  static  templates  vector_functions.py
rg = "rg-ai200-cosmos-vector"  # Resource Group name
location = "eastus"   # Azure region for the resources
20:DATABASE_NAME = "vectorstore"
21:CONTAINER_NAME = "vectors"
203:        "--capabilities", "EnableServerless", "EnableNoSQLVectorSearch",
```
**Qué mirar:** la cuenta se crea **serverless** y con `EnableNoSQLVectorSearch`. `vector_functions.py` trae marcadores `BEGIN`/`END` vacíos que se completan en el paso 8.

La guía de la plataforma incluye un **parche** del bloque `az cosmosdb sql container create` de `azdeploy.ps1`: PowerShell rompía las comillas del JSON de las políticas. **No aplica** a `azdeploy.py`, que pasa los argumentos como lista con `subprocess`. Se comprueba en el paso 4: las políticas quedaron bien.

✅ **Comprobación:** si `sed -n '5,6p'` sigue mostrando `<your-…>`, edita las líneas a mano.

## Paso 3 · Crear la cuenta y la BD (`azdeploy.py` → opción 1)
**Por qué:** es el plano de control: cuenta serverless con búsqueda vectorial y BD `vectorstore`. Tarda de 5 a 10 minutos.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este lab (**distinto** del de LP4-01: aquí el contenedor tiene su propia opción):
```text
1. Create Cosmos DB account (with vector search capability)
2. Create container (with vector indexing policies)
3. Configure Entra ID access
4. Check deployment status
5. Retrieve connection info
6. Exit
```
**Salida no guardada** de la opción 1. Esperado (mensajes del script):
```text
Resource group created: rg-ai200-cosmos-vector
Creating Azure Cosmos DB for NoSQL account 'cosmos-vector-<hash>' in 'eastus'...
Cosmos DB account created with vector search capability
Database created: vectorstore
Use option 2 to create the container.
```
✅ **Comprobación:**
```bash
az cosmosdb list -g rg-ai200-cosmos-vector --query "[].{n:name,e:provisioningState,cap:capabilities[].name}" -o json
```
Salida real:
```text
[{"cap": ["EnableServerless", "EnableNoSQLVectorSearch"], "e": "Succeeded", "n": "cosmos-vector-<hash>"}]
```
Deben salir las **dos** capabilities y `Succeeded`. Si sale `Creating`, espera. Si falta `EnableNoSQLVectorSearch`, el contenedor del paso 4 no podrá tener índice vectorial.

## Paso 4 · Crear el contenedor vectorial (opción 2)
**Por qué:** aquí se declara cómo son los vectores (*vector embedding policy*) y cómo se indexan (*vector index*). Esta política **no se puede cambiar después**: si te equivocas en las dimensiones, hay que recrear el contenedor. Las 256 dimensiones tienen que coincidir con las del modelo que genera los embeddings (aquí, con las de `sample_vectors.json`).

Sin salir del menú: Enter → **`2`**. Salida real:
```text
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
Use option 3 to configure Entra ID access.
```
**Qué mirar:**
- **Dos piezas distintas:** la *embedding policy* (inmutable) y el *vector index* `diskANN` (aproximado, por grafo; se puede cambiar).
- **`/embedding/*` fuera del índice normal:** si no, cada escritura indexaría 256 números como propiedades sueltas. En LP4-01, con el índice por defecto, cada chunk ya costaba ≈ 9,9 RU.
- Partition key `/documentId`, igual que en LP4-01.

✅ **Comprobación:**
```bash
A=$(az cosmosdb list -g rg-ai200-cosmos-vector --query "[0].name" -o tsv)
az cosmosdb sql container show -g rg-ai200-cosmos-vector -a "$A" -d vectorstore -n vectors \
  --query "{pk:resource.partitionKey.paths, vec:resource.vectorEmbeddingPolicy, idx:resource.indexingPolicy}" -o json
```
Salida real (resumida):
```text
pk:  ["/documentId"]
vec: {"vectorEmbeddings": [{"dataType": "float32", "dimensions": 256, "distanceFunction": "cosine", "path": "/embedding"}]}
idx: includedPaths ["/*"]; excludedPaths ["/embedding/*", "/\"_etag\"/?"]
     vectorIndexes [{"path": "/embedding", "type": "diskANN", "quantizationByteSize": 64, "indexingSearchListSize": 100}]
```
Si `vectorIndexes` sale vacío o faltan las dimensiones, el contenedor se creó mal. Como la política no se puede cambiar, borra el contenedor y repite la opción 2.

## Paso 5 · Dar acceso con Entra ID: dos roles (opción 3)
**Por qué:** igual que en LP4-01, sin claves y con **dos planos de permisos**: `Contributor` de ARM (gestionar la cuenta) y `Cosmos DB Built-in Data Contributor` (leer y escribir documentos). Aquí es la opción **3**, no la 2.

Enter → **`3`**. Salida real:
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
A=$(az cosmosdb list -g rg-ai200-cosmos-vector --query "[0].name" -o tsv)
az cosmosdb sql role assignment list -g rg-ai200-cosmos-vector -a "$A" --query "length(@)" -o tsv
```
Salida real: `1`. Si sale `0`, repite la opción 3.

## Paso 6 · Comprobar el despliegue (opción 4)
**Por qué:** es de solo lectura y confirma cuenta, capability, BD, contenedor y roles de una vez.

Enter → **`4`**. Salida real:
```text
Checking deployment status...
Cosmos DB Account (cosmos-vector-<hash>):
  Status: Succeeded
  Cosmos DB account is ready
  Vector search capability enabled
  Database vectorstore: Created
  Container vectors: Created
  Entra ID access: <usuario-del-lab> (full control)
```
✅ **Comprobación:** las siete líneas, con `Vector search capability enabled` y `full control`. Si sale `WARNING`, falta uno de los dos roles: repite la opción 3.

## Paso 7 · Generar el `.env` (opción 5) y salir (opción 6)
**Por qué:** la app necesita el endpoint, la BD y el contenedor. No lleva claves: autentica `DefaultAzureCredential` con tu `az login`.

Enter → **`5`**. Salida real:
```text
Retrieving connection information...
Endpoint: https://cosmos-vector-<hash>.documents.azure.com:443/
Database: vectorstore
Container: vectors
Authentication: Microsoft Entra ID (DefaultAzureCredential)
Environment variables saved to .env and .env.ps1
```
Después, **`6`** para salir.

✅ **Comprobación:**
```bash
ls -la .env && grep -c '^export COSMOS_' .env
```
Salida real: el fichero (152 bytes) y `3`. Si no existe, repite la opción 5. El `.env` se versiona en el repo: no tiene claves y la cuenta ya no existe.

## Paso 8 · Completar las 3 funciones de `client/vector_functions.py`
**Por qué:** son las que usa la app para guardar tickets con su vector y buscar los más parecidos. El código es literal de la guía y va entre los marcadores `BEGIN`/`END` (el fichero del repo ya está completado).

| Función | Qué hace |
|---|---|
| `store_vector_document` | `upsert_item` como en LP4-01, pero con `embedding` relleno (256 floats). Devuelve las RU |
| `vector_similarity_search` | Los N tickets más cercanos al vector de la pregunta, sin filtro |
| `filtered_vector_search` | Igual, pero con `WHERE c.metadata.category = @category` antes de ordenar: búsqueda **híbrida** |

El núcleo de la búsqueda:
```sql
SELECT TOP @topN c.id, c.documentId, c.content, c.metadata,
       VectorDistance(c.embedding, @queryVector) AS similarityScore
FROM c
[WHERE c.metadata.category = @category]          -- solo en filtered_vector_search
ORDER BY VectorDistance(c.embedding, @queryVector)
```
**Qué hace cada detalle:**
- `VectorDistance` compara el vector de cada ticket con el de la pregunta, usando la función de la política (`cosine`).
- **Con `cosine`, el número es una similitud: cuanto más alto, más parecido.** `ORDER BY VectorDistance(...)` ya pone primero el más parecido, sin `DESC`. El comentario de la guía («lowest distance = most similar») confunde: el paso 13 lo comprueba con datos reales.
- `TOP @topN` es obligatorio en una consulta vectorial: sin límite, Cosmos tendría que ordenar todos los vectores.
- `enable_cross_partition_query=True`: la similitud se busca en todo el contenedor, no en una partición.
- El vector de la pregunta va como parámetro (`@queryVector`), igual que cualquier otro valor.

✅ **Comprobación** (crea el venv y prueba que el módulo carga):
```bash
cd client
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -c "import vector_functions as v; print([n for n in ('store_vector_document','vector_similarity_search','filtered_vector_search') if callable(getattr(v,n,None))])"
cd ..
```
Salida real:
```text
['store_vector_document', 'vector_similarity_search', 'filtered_vector_search']
```
Es solo una prueba de sintaxis. Si sale `IndentationError`, revisa la alineación del código pegado.

## Paso 9 · Revisar `client/setup_container.py`
**Por qué:** la guía pide repasar `create_vector_container()`. Es el mismo contenedor del paso 4 escrito con el SDK de Python en vez de con `az`: `PartitionKey(path="/documentId")`, la `vector_embedding_policy` y la `indexing_policy` con `diskANN` y `/embedding/*` excluido.

En este starter la función **ya venía implementada** y es igual a la de la guía (solo cambian comentarios y líneas en blanco). No hubo que tocar nada.

`python setup_container.py` (Task 6 de la guía): **no se ejecutó**. No hacía falta, porque la opción 2 ya había creado el contenedor. Usa `create_container_if_not_exists`, así que lanzarlo no cambia ni borra nada.

✅ **Comprobación:** `grep -n "diskANN\|/embedding" client/setup_container.py` debe mostrar la ruta `/embedding`, el índice `diskANN` y la exclusión `/embedding/*`.

## Paso 10 · Activar el entorno y cargar el `.env`
**Por qué:** la app lee las tres variables `COSMOS_*` del entorno de la terminal donde corre.
```bash
source .env && source client/.venv/bin/activate
for v in COSMOS_ENDPOINT COSMOS_DATABASE COSMOS_CONTAINER; do [ -n "${!v:-}" ] && echo "$v definida" || echo "$v FALTA"; done
```
Salida real:
```text
COSMOS_ENDPOINT definida
COSMOS_DATABASE definida
COSMOS_CONTAINER definida
```
✅ **Comprobación:** tres `definida` y el prompt con `(.venv)`. Si alguna dice `FALTA`, mira con `pwd` que estás en la carpeta del lab.

## Paso 11 · Arrancar la app Flask
```bash
cd client && python app.py
```
**Salida no guardada.** Esperado, como en LP4-01:
```text
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
```
✅ **Comprobación:** `curl -s -m 20 -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000/` en otra terminal debe dar `200`. Si la app da `ValueError`, falta el `.env` en esa terminal (paso 10).

## Paso 12 · Cargar los tickets con sus vectores («Load Vector Data»)
**Por qué:** `POST /load-data` lee `sample_vectors.json` y llama 12 veces a `store_vector_document`. Cada escritura guarda el ticket y lo inserta en el índice DiskANN.

Salida real:
```text
Successfully loaded 12 tickets with embeddings! Total RU: 640.68
```
**Qué mirar:** 640,68 / 12 ≈ **53,4 RU por ticket**, unas **5 veces** lo que costó un chunk sin vector en LP4-01 (≈ 9,9 RU). El documento pesa más (256 `float32`) y cada vector se enlaza en el grafo de DiskANN. Excluir `/embedding/*` evita algo peor, pero el índice vectorial tiene su propio coste. Es el trato de la búsqueda vectorial: **escribir caro para buscar rápido**. LP4-03 lo mide índice por índice.

✅ **Comprobación:** `12 tickets`. Si sale `Error loading data: … 403`, el rol de datos aún no se ha propagado: espera 2-3 minutos y repite.

## Paso 13 · Búsqueda por similitud («Vector Similarity Search»)
**Por qué:** es la búsqueda semántica: «I can't login to my account» debería encontrar tickets de acceso aunque no usen las mismas palabras.

Consulta `I can't login to my account`, Top 5. Salida real (se pegaron los 4 primeros):
```text
Query: "I can't login to my account" | Top 5 results
0.9997  ticket-technical-001-chunk-0  · technical, login, password, authentication
0.9920  ticket-shipping-002-chunk-0   · shipping, address-change, order-modification
0.9918  ticket-account-001-chunk-0    · account, email, profile, update
0.9917  ticket-account-002-chunk-0    · account (borrar la cuenta y los datos)
```
(Los textos de los tickets son ficticios, del starter público. Aquí se resumen con sus tags.)

**Qué mirar:**
- **Con `cosine`, la puntuación más alta es la más parecida** y sale primero. El primero es el ticket de login (0,9997): correcto.
- **Del 2.º al 4.º la diferencia es mínima** (0,9920 → 0,9917) y el orden no tiene sentido: un ticket de envíos va por delante de dos de cuenta. Hipótesis, **no comprobada**: los embeddings de ejemplo están precalculados de forma sencilla y solo distinguen bien el mejor resultado. La calidad la da el **modelo de embeddings**. Cosmos solo ordena los vectores que le das.

✅ **Comprobación:** 5 resultados con la puntuación del primero ≈ 1. Si no sale nada, no se hizo el paso 12. La guía propone probar también `My payment was charged twice` y `Package hasn't arrived yet` (no se hizo).

## Paso 14 · Búsqueda filtrada por categoría («Filtered Vector Search») — no hecho
No se pegó ningún resultado. Se ejecuta en la misma app: consulta `I can't login to my account`, **Filter by Category** = `technical` → **Search with Filter**. Después, la misma consulta con `account`.

Esperado según la guía:
- Con `technical`: solo tickets `technical`, con el de login primero (≈ 0,9997).
- Con `account`: solo tickets de cuenta, ordenados por similitud.

**Qué mirar:** el `WHERE` reduce los candidatos **antes** del ranking vectorial. Es la búsqueda híbrida (metadatos + vector) que se usa en RAG para dar contexto más preciso.

✅ **Comprobación:** ningún resultado de otra categoría. Si aparece alguno, revisa el `where_clause` de `filtered_vector_search`.

Al terminar, **`Ctrl+C`** en la terminal de Flask.

---

## Cleanup (obligatorio al acabar)
**Por qué:** borra la cuenta, la BD, el contenedor, los 12 tickets y los roles.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-vector --no-wait --yes
az group exists --name rg-ai200-cosmos-vector
az group show -n rg-ai200-cosmos-vector --query properties.provisioningState -o tsv
```
Salida real (antes de lanzarlo y después):
```text
true
Succeeded        ← todavía no se había lanzado
true
Deleting         ← lanzado
```
⚠️ **Lo que pasó:** en la terminal del borrado se tecleó `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crtrt` (con `rt` de más). El borrado se lanzó igualmente, pero esa terminal se quedó con la variable mal: los siguientes `az` fallarían con `invalid file path`. Hay que repetir el `export` bien escrito.

⚠️ **No verificado.** El lab 11 se abrió con otra sesión de la plataforma y otra suscripción (`XLabs-232`). Desde ella, `az group exists --name rg-ai200-cosmos-vector` devuelve `false` siempre, y ese `false` no prueba nada. Se documenta como «borrado lanzado, no verificado».

✅ **Comprobación correcta** (misma suscripción, **antes** de abrir la sesión siguiente):
```bash
az account show --query name -o tsv               # debe ser XLabs-274
az group exists --name rg-ai200-cosmos-vector     # false cuando termine (unos minutos)
```
Si pasados 10-15 minutos sigue en `true` y el `provisioningState` es `Failed`, relanza el `delete`.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `az group exists` da `false` para el grupo de LP4-01 | La sesión nueva es **otra suscripción** | Verificar el cleanup antes de cambiar de sesión |
| La guía pide parchear `azdeploy.ps1` | Fallo de comillas de PowerShell con el JSON de las políticas | No aplica a `azdeploy.py`. Se comprueba con `az cosmosdb sql container show` (paso 4) |
| Las opciones del menú no son las de LP4-01 | Este script tiene una opción más (crear el contenedor) | 2 = contenedor, 3 = roles, 4 = estado, 5 = `.env`, 6 = salir |
| `ca-certificates.crtrt` en el `export` | Error al teclear | Repetir el `export` con la ruta correcta |
| El 2.º-4.º resultado de la búsqueda casi empatan | Embeddings de ejemplo sencillos (hipótesis no comprobada) | Ninguno: es cosa de los datos, no de Cosmos |
