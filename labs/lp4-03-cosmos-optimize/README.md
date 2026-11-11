# Lab LP4-03 · Optimize query performance for Azure Cosmos DB (plataforma: Lab 11 · AI-200-LP04M03)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/03-optimize-query-performance.html (índice: [`docs/00-plan/labs-oficiales.md`](../../docs/00-plan/labs-oficiales.md)).
- **Estado (05/11/2026): completado.** Hechos todos los pasos (0-15): despliegue, 3 contenedores, 2 funciones, carga de 500 tickets, comparación de búsqueda y búsqueda filtrada. **Cleanup verificado** (`az group exists` = `false` en la misma suscripción y sin ningún `rg-ai200-*`).
- Lab anterior: [LP4-02](../lp4-02-cosmos-vector-search/README.md) · Lab siguiente: [LP5-01](../lp5-01-pg-agent-backend/README.md). Notas de clase y conclusiones: [`docs/modulos/04-cosmosdb.md`](../../docs/modulos/04-cosmosdb.md). Origen MIT de `azdeploy.py` y `client/`: ver [`../NOTICE.md`](../NOTICE.md).

Cada paso tiene: **por qué → comando → salida real (saneada) → qué mirar → comprobación**. Saneado: sin IDs de suscripción ni tenant (`<sub-id>`), sin usuario del lab (`<usuario-del-lab>`) y con el sufijo de la cuenta como `<hash>`.

## Qué se construye
Un banco de pruebas: **los mismos 500 tickets en tres contenedores** que solo se diferencian en el índice vectorial. Se lanza la misma búsqueda en los tres y se compara lo que cuesta (RU) y lo que tarda.

```
azdeploy.py 1 → RG rg-ai200-cosmos-optimize + cuenta serverless cosmos-index-<hash> con EnableNoSQLVectorSearch + BD indexoptimize
azdeploy.py 2 → 3 contenedores, todos con /documentId y /embedding (float32, cosine, 256):
                vectors-flat (flat) · vectors-quantized (quantizedFlat) · vectors-diskann (diskANN)
azdeploy.py 3 → roles Contributor (ARM) + Cosmos DB Built-in Data Contributor (datos)
azdeploy.py 4 → estado · 5 → .env (endpoint y BD; sin claves) · 6 → salir
client/index_functions.py → vector_similarity_search (mide RU y ms) + compare_index_performance (los 3 contenedores)
client/app.py (Flask)     → carga 500 tickets en cada contenedor y compara · http://127.0.0.1:5000
```

**Objetivo en cristiano:** comprobar con números qué índice vectorial conviene. La respuesta del lab: **depende de cuántos vectores tengas**. Con pocos, el índice «tonto» (`flat`) es el más barato. Los índices avanzados cuestan más al escribir y solo compensan a escala.

### Los tres índices (con analogía de sistemas)
| Índice | Cómo busca | Analogía |
|---|---|---|
| `flat` | **Exacto**: compara la pregunta con todos los vectores | `grep` sobre todos los ficheros: siempre exacto, más lento cuanto más hay |
| `quantizedFlat` | **Exacto sobre vectores comprimidos**: menos memoria, precisión casi igual | `grep` sobre ficheros comprimidos |
| `diskANN` | **Aproximado**: recorre un grafo de vecinos y no mira todos los vectores (≈ 95 % de recall) | Un índice de buscador: muy rápido a escala, pero caro de mantener al escribir |

Dato de las diapositivas del curso: `quantizedFlat` y `diskANN` **necesitan 1.000 o más vectores para activarse**. Por debajo hacen un recorrido completo, como `flat`. Con los 500 vectores de este lab esto se nota en los resultados (pasos 13 y 14).

---

## Paso 0 · Preparar la terminal
**Por qué:** `REQUESTS_CA_BUNDLE` para el proxy de empresa, en cada terminal. `deactivate` sale del `.venv` de LP4-02.
```bash
cd ~/claude/AI-200-Developing/labs/lp4-03-cosmos-optimize
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `[ -n "${REQUESTS_CA_BUNDLE:-}" ] && echo "definida: $REQUESTS_CA_BUNDLE"` debe mostrar `/etc/ssl/certs/ca-certificates.crt`. En LP4-02 se tecleó `.crtrt`: si la ruta no existe, `az` falla con `invalid file path`.

## Paso 1 · `az login` con el usuario del lab 11
**Por qué:** tercera sesión de la plataforma del día, tercera suscripción.
```bash
az login --use-device-code
az account show --query name -o tsv
az group list -o table
```
Salida real (la lista de grupos es de justo después del despliegue):
```text
[1] *  XLabs-232            <sub-id>                              Lab Directory
Tenant: Lab Directory
Subscription: XLabs-232 (<sub-id>)

XLabs-232
Name                      Location    Status
------------------------  ----------  ---------
az104-rg7                 eastus      Succeeded
rg-ai200-cosmos-optimize  eastus      Succeeded
```
**Qué mirar:** LP4-01 fue en `XLabs-278`, LP4-02 en `XLabs-274` y este en `XLabs-232`. `az104-rg7` es de otro curso de la plataforma: **no se toca**. Como este es el último lab del día, el cleanup se verifica aquí sin cambiar de sesión.

✅ **Comprobación:** `XLabs-232` y ningún `rg-ai200-*` antes de desplegar. Si el proveedor no está registrado: `az provider register --namespace Microsoft.DocumentDB`.

## Paso 2 · Descargar el starter y poner los valores de `azdeploy.py`
```bash
curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-optimize-query-python.zip
unzip -oq cosmosdb-optimize-query-python.zip && ls client
sed -i 's|<your-resource-group-name>|rg-ai200-cosmos-optimize|; s|<your-azure-region>|eastus|' azdeploy.py
sed -n '5,6p' azdeploy.py
grep -nE 'DATABASE_NAME *=|"vectors-' azdeploy.py | head -4
```
Salida real:
```text
app.py  generate_sample_data.py  index_functions.py  requirements.txt  sample_vectors.json  setup_containers.py  static  templates
rg = "rg-ai200-cosmos-optimize"  # Resource Group name
location = "eastus"   # Azure region for the resources
20:DATABASE_NAME = "indexoptimize"
38:    ("vectors-flat", "flat", "exact nearest neighbor"),
39:    ("vectors-quantized", "quantizedFlat", "compressed exact search"),
40:    ("vectors-diskann", "diskANN", "approximate nearest neighbor"),
```
**Qué mirar:** el script define los 3 contenedores, uno por índice. En `client/` hay que completar `index_functions.py`; `setup_containers.py` solo se revisa, y `generate_sample_data.py` es el generador de los 500 tickets de `sample_vectors.json`.

✅ **Comprobación:** si siguen apareciendo `<your-…>`, edita las líneas 5 y 6 a mano.

## Paso 3 · Crear la cuenta y la BD (`azdeploy.py` → opción 1)
**Por qué:** cuenta serverless con búsqueda vectorial y BD `indexoptimize`. En este lab la opción 1 **no** crea contenedores.
```bash
python3 azdeploy.py      # menú → 1
```
Menú (igual que el de LP4-02):
```text
1. Create Cosmos DB account (with vector search capability)
2. Create containers (with vector indexing policies)
3. Configure Entra ID access
4. Check deployment status
5. Retrieve connection info
6. Exit
```
Salida real de la opción 1:
```text
Checking/creating resource group 'rg-ai200-cosmos-optimize'...
Resource group created: rg-ai200-cosmos-optimize

Creating Azure Cosmos DB for NoSQL account 'cosmos-index-<hash>' in 'eastus'...
This may take several minutes...
Cosmos DB account created with vector search capability
Creating database 'indexoptimize'...
Database created: indexoptimize
Use option 2 to create the containers.
```
✅ **Comprobación:**
```bash
az cosmosdb list -g rg-ai200-cosmos-optimize --query "[].{n:name,e:provisioningState,cap:capabilities[].name}" -o json
```
Salida real:
```text
[{"cap": ["EnableServerless", "EnableNoSQLVectorSearch"], "e": "Succeeded", "n": "cosmos-index-<hash>"}]
```
Deben salir las dos capabilities y `Succeeded`. Si sale `Creating`, espera.

## Paso 4 · Crear los 3 contenedores (opción 2)
**Por qué:** es el corazón del experimento: **mismos datos, misma política de embeddings y solo cambia el índice**. Así cualquier diferencia de coste se debe al índice.

Enter → **`2`**. Salida real:
```text
Creating containers with vector indexing policies...
Creating container 'vectors-flat' with flat vector index...
Container created: vectors-flat (exact nearest neighbor)
Creating container 'vectors-quantized' with quantizedFlat vector index...
Container created: vectors-quantized (compressed exact search)
Creating container 'vectors-diskann' with diskANN vector index...
Container created: vectors-diskann (approximate nearest neighbor)

All containers share:
  - Partition key: /documentId
  - Vector embedding: /embedding (float32, cosine, 256 dimensions)
Use option 3 to configure Entra ID access.
```
✅ **Comprobación:**
```bash
A=$(az cosmosdb list -g rg-ai200-cosmos-optimize --query "[0].name" -o tsv)
az cosmosdb sql container list -g rg-ai200-cosmos-optimize -a "$A" -d indexoptimize \
  --query "[].{n:name, idx:resource.indexingPolicy.vectorIndexes[0].type}" -o table
```
Salida real:
```text
N                  Idx
-----------------  -------------
vectors-diskann    diskANN
vectors-quantized  quantizedFlat
vectors-flat       flat
```
Tres contenedores, cada uno con su índice. Si falta alguno, repite la opción 2: lo que ya existe se lo salta.

## Paso 5 · Dar acceso con Entra ID: dos roles (opción 3)
**Por qué:** igual que en LP4-01 y LP4-02: `Contributor` de ARM (plano de control) y `Cosmos DB Built-in Data Contributor` (plano de datos), sin claves.

Enter → **`3`**. Salida real:
```text
Configuring Microsoft Entra ID access...
Assigning Azure RBAC 'Contributor' role to '<usuario-del-lab>'...
Azure RBAC Contributor role assigned
Assigning 'Cosmos DB Built-in Data Contributor' role to '<usuario-del-lab>'...
Cosmos DB Data Contributor role assigned
Entra ID access configured for: <usuario-del-lab>
```
✅ **Comprobación:**
```bash
A=$(az cosmosdb list -g rg-ai200-cosmos-optimize --query "[0].name" -o tsv)
az cosmosdb sql role assignment list -g rg-ai200-cosmos-optimize -a "$A" --query "length(@)" -o tsv
```
Salida real: `1`. Si sale `0`, repite la opción 3.

## Paso 6 · Comprobar el despliegue (opción 4)
Enter → **`4`**. Salida real:
```text
Checking deployment status...
Cosmos DB Account (cosmos-index-<hash>):
  Status: Succeeded
  Cosmos DB account is ready
  Vector search capability enabled
  Database indexoptimize: Created
  Container vectors-flat: Created
  Container vectors-quantized: Created
  Container vectors-diskann: Created
  Entra ID access: <usuario-del-lab> (full control)
```
✅ **Comprobación:** los tres contenedores `Created` y `full control`. Si sale `WARNING`, falta un rol: repite la opción 3.

## Paso 7 · Crear el entorno Python
**Por qué:** las mismas librerías que en los labs anteriores (`flask`, `azure-cosmos`, `azure-identity`), en un `.venv` dentro de `client/`.
```bash
cd client
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python -c "import azure.cosmos, azure.identity, flask; print('ok', azure.cosmos.__version__)"
cd ..
```
Salida real:
```text
ok 4.17.1
```
✅ **Comprobación:** `ok 4.x.x`. Si sale `ModuleNotFoundError`, el venv no está activo.

## Paso 8 · Generar el `.env` (opción 5) y cargarlo
**Por qué:** la app necesita el endpoint y la BD. Aquí el `.env` solo trae **dos** variables: los nombres de los 3 contenedores están fijados en `index_functions.py`.

⚠️ **Lo que pasó:** se intentó cargar el `.env` antes de generarlo:
```text
bash: .env: No existe el archivo o el directorio
```
En la sesión se indicó la «opción 4», pero en este menú la 4 es el estado: el `.env` lo genera la **5**.

```bash
python3 azdeploy.py      # menú → 5 → Enter → 6
```
Salida real de la opción 5:
```text
Retrieving connection information...
Endpoint: https://cosmos-index-<hash>.documents.azure.com:443/
Database: indexoptimize
Authentication: Microsoft Entra ID (DefaultAzureCredential)
Containers: vectors-flat, vectors-quantized, vectors-diskann
Environment variables saved to .env and .env.ps1
```
Cargarlo:
```bash
source .env && source client/.venv/bin/activate
for v in COSMOS_ENDPOINT COSMOS_DATABASE; do [ -n "${!v:-}" ] && echo "$v definida" || echo "$v FALTA"; done
```
Salida real:
```text
COSMOS_ENDPOINT definida
COSMOS_DATABASE definida
```
✅ **Comprobación:** `grep -c '^export COSMOS_' .env` debe dar `2` y las dos variables `definida`. Si el fichero no existe, repite la opción 5. El `.env` se versiona en el repo: no tiene claves y la cuenta ya no existe.

## Paso 9 · Completar las 2 funciones de `client/index_functions.py`
**Por qué:** son las que miden. Una ejecuta la búsqueda en un contenedor y anota RU y tiempo. La otra la repite en los tres. El código es literal de la guía y va entre los marcadores `BEGIN`/`END` (el fichero del repo ya está completado).

```python
# vector_similarity_search(container_name, query_embedding, top_n): una búsqueda, con su coste
start_time = time.time()
items = list(container.query_items(
    query="SELECT TOP @topN c.id, c.documentId, c.content, c.metadata, "
          "VectorDistance(c.embedding, @queryVector) AS similarityScore "
          "FROM c ORDER BY VectorDistance(c.embedding, @queryVector)",
    parameters=[{"name": "@topN", "value": top_n}, {"name": "@queryVector", "value": query_embedding}],
    enable_cross_partition_query=True))
execution_time_ms = (time.time() - start_time) * 1000
ru_charge = float(container.client_connection.last_response_headers.get('x-ms-request-charge', 0))

# compare_index_performance(query_embedding, top_n): la misma búsqueda en los 3 contenedores
for index_type, container_name in [("flat", CONTAINER_FLAT),
                                   ("quantizedFlat", CONTAINER_QUANTIZED),
                                   ("diskANN", CONTAINER_DISKANN)]:
    result = vector_similarity_search(container_name, query_embedding, top_n)   # si falla: status "error" y sigue
```
**Qué hace cada detalle:**
- `list(...)` consume todas las páginas antes de parar el reloj: el tiempo incluye la consulta entera.
- Las RU se leen del header `x-ms-request-charge` de la **última** respuesta. Si la consulta tuviera varias páginas, sería aproximado: el propio código avisa de que en producción se mide con Azure Monitor.
- El tiempo incluye la **red** (y el proxy), no solo el motor de Cosmos.

✅ **Comprobación** (desde `client/`):
```bash
python -c "import index_functions as i; print(callable(i.vector_similarity_search), callable(i.compare_index_performance))"
```
Salida real: `True True`. Si sale `IndentationError`, revisa la alineación del código pegado.

## Paso 10 · Revisar `client/setup_containers.py`
**Por qué:** la guía pide repasar cómo se declara cada índice con el SDK de Python: `create_flat_container`, `create_quantized_container` y `create_diskann_container`. Solo cambia el `type` de `vectorIndexes`: `flat`, `quantizedFlat` o `diskANN`. Es lo mismo que hizo la opción 2 con `az`.

No se ejecutó: los contenedores ya existían (paso 4).

✅ **Comprobación:** `grep -n '"type"' client/setup_containers.py` debe mostrar los tres tipos de índice.

## Paso 11 · Arrancar la app Flask
```bash
source client/.venv/bin/activate && cd client && python app.py
```
Salida real:
```text
Dashboard running at http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
```
✅ **Comprobación:** en la web, **Container Status** muestra los tres contenedores. Al empezar tienen 0 documentos. Si la app da `ValueError`, falta el `.env` en esa terminal (paso 8).

## Paso 12 · Cargar 500 tickets en cada contenedor («Load Data to All Containers»)
**Por qué:** los mismos datos en los tres contenedores, para que la comparación sea justa. La carga va en paralelo (≈ 30 hilos) y tarda de 30 a 45 segundos. Aquí se mide el **coste de escribir** con cada índice.

Salida real:
```text
Loaded 500 documents to all containers. RU costs - flat: 5829.66, quantizedFlat: 6884.66, diskANN: 27535.68
```
| Índice | RU totales | RU por documento | Respecto a `flat` |
|---|---|---|---|
| `flat` | 5.829,66 | ≈ 11,7 | 1,0× |
| `quantizedFlat` | 6.884,66 | ≈ 13,8 | 1,2× |
| `diskANN` | 27.535,68 | ≈ 55,1 | **4,7×** |

**Qué mirar:**
- **`diskANN` es el más caro de escribir** (≈ 4,7× `flat`): cada vector se enlaza en un grafo de vecinos. `quantizedFlat` añade poco (+18 %): solo comprime el vector.
- **Coincide con LP4-02:** allí un ticket con DiskANN costó ≈ 53,4 RU, y aquí ≈ 55,1.
- La escritura se paga una vez. La idea es ganarlo luego en cada lectura, **a escala**.

✅ **Comprobación:** Container Status con `500 documents` en los tres. Si alguno se queda corto, vuelve a pulsar el botón: es `upsert` y no duplica.

## Paso 13 · Comparar la búsqueda («Compare Index Performance»)
**Por qué:** la misma pregunta en los tres contenedores: ahora se mide el **coste de leer**.

Consulta `I can't login to my account`, Top 5. Salida real:
```text
Index Type     Container          Results  RU Cost  Time (ms)  Status
flat           vectors-flat       5        10.13    604.02     ✓
quantizedFlat  vectors-quantized  5        21.60    500.89     ✓
diskANN        vectors-diskann    5        21.60    538.47     ✓
```
Primeros resultados (se pegaron 3 de los 5 por índice; los textos de los tickets son ficticios y no se copian):
```text
flat           doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-005  0.0207
quantizedFlat  doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-100  0.0207
diskANN        doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-100  0.0207
```
**Qué mirar:**
- **RU:** `flat` es el más barato (10,13). `quantizedFlat` y `diskANN` cuestan **exactamente lo mismo** (21,60), el doble. Es el umbral de las diapositivas: con menos de 1.000 vectores **no activan su índice** y hacen un recorrido completo. Con 500 vectores los dos hicieron lo mismo.
- **Tiempo (500-604 ms):** muy parecido entre los tres y dominado por la red y el proxy. Una sola ejecución no basta para ordenar los índices por velocidad.
- **Resultados iguales:** la única diferencia (`doc-account-005` frente a `doc-account-100`) es un **empate**: misma puntuación (0,0207) y mismo texto, porque el generador repite plantillas. No es una pérdida de precisión de `diskANN`.
- **Calidad semántica baja:** para «no puedo entrar en mi cuenta» el primero es un ticket de facturación con 0,0638, casi ortogonal. Estos 500 vectores no tienen significado real: sirven para medir **coste**, no relevancia.

✅ **Comprobación:** las tres filas con `5` resultados y estado correcto. Si alguna sale con `error`, el mensaje dice qué contenedor falla. Comprueba que existe (paso 4) y que tiene 500 documentos (paso 12).

## Paso 14 · Comparar la búsqueda filtrada («Compare Filtered Search»)
**Por qué:** combinar un filtro de metadatos con el ranking vectorial reduce los candidatos **antes** de ordenar. Se comprueba cuánto baja el coste.

Categoría `account`, Top 5. La guía propone la consulta `Protect my account from hackers`. En lo guardado de la sesión consta `I can't login to my account`. El pegado original no quedó en la transcripción exportada, así que no se puede confirmar cuál se eligió.

Salida real:
```text
Index Type     Container          Results  RU Cost  Time (ms)  Status
flat           vectors-flat       5        8.15     673.56     ✓
quantizedFlat  vectors-quantized  5        8.15     461.72     ✓
diskANN        vectors-diskann    5        8.15     510.40     ✓

flat           doc-account-001  0.0521 · doc-account-098  0.0207 · doc-account-097  0.0207
quantizedFlat  doc-account-001  0.0521 · doc-account-099  0.0207 · doc-account-097  0.0207
diskANN        doc-account-001  0.0521 · doc-account-098  0.0207 · doc-account-097  0.0207
```
**Qué mirar:**
- **Los tres cuestan 8,15 RU**, menos que sin filtro: `flat` baja de 10,13 a 8,15 y `quantizedFlat`/`diskANN` de 21,60 a 8,15 (**−62 %**). Filtrar antes del ranking vectorial abarata la consulta.
- **Solo salen tickets `account`:** el de facturación (`doc-billing-002`), primero sin filtro, desaparece.
- Las diferencias entre índices (`097/098/099`) son otra vez empates de puntuación y texto.
- Tiempos de 461-673 ms: siguen dominados por la red.

✅ **Comprobación:** todos los resultados con prefijo `doc-account-`. Si aparece otra categoría, el filtro no se aplicó.

## Paso 15 · Sacar conclusiones y parar la app
Tabla de la guía, contrastada con lo medido:

| Escenario | Índice recomendado | Lo que se vio aquí |
|---|---|---|
| Menos de ~10.000 vectores | `flat`: exacto y a un coste aceptable | Con 500, `flat` fue el más barato al escribir y al leer |
| Memoria limitada | `quantizedFlat` | Escribe casi como `flat` (+18 %). Con menos de 1.000 vectores no se activa |
| Producción a gran escala | `diskANN`: mejor coste por consulta, ≈ 95 % de recall | Escribir cuesta ≈ 4,7× `flat`. Con 500 vectores no aporta nada |

**Para el examen:** `diskANN` se paga al **escribir** y se gana al **leer**, pero solo **a escala**. Filtrar por metadatos antes del ranking reduce el coste en cualquier índice.

**`Ctrl+C`** en la terminal de Flask.

---

## Cleanup (obligatorio al acabar) — verificado
**Por qué:** borra la cuenta, los 3 contenedores con sus 1.500 documentos y los roles. Al ser el último lab del día, se puede verificar sin cambiar de sesión.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-optimize --no-wait --yes
az group list -o table
```
Salida real tras lanzar el borrado:
```text
Name                      Location    Status
------------------------  ----------  ---------
az104-rg7                 eastus      Succeeded
rg-ai200-cosmos-optimize  eastus      Deleting
```
Lo último en borrarse es la cuenta Cosmos. Salida real de `az resource list -g rg-ai200-cosmos-optimize` mientras tanto:
```text
N                      T
---------------------  -------------------------------------
cosmos-index-<hash>    Microsoft.DocumentDB/databaseAccounts
```
Comprobación cada 20 s hasta ver `false`:
```bash
for i in $(seq 1 60); do r=$(az group exists --name rg-ai200-cosmos-optimize); [ "$r" = "false" ] && { echo "false tras ~$((i*20))s"; break; }; sleep 20; done
az group list -o table
```
Salida real:
```text
false tras ~140s
Name       Location    Status
---------  ----------  ---------
az104-rg7  eastus      Succeeded
```
✅ **Verificado** el 05/11/2026 (suscripción `XLabs-232`, la misma del despliegue, comprobada con `az account show`). `false` y ningún `rg-ai200-*`, solo `az104-rg7` de otro curso. A diferencia de LP4-01 y LP4-02, la suscripción no cambió entre el borrado y la comprobación, así que el `false` es una prueba válida. Si pasados 15 minutos siguiera en `true`, mira `az group show -n rg-ai200-cosmos-optimize --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| `bash: .env: No existe el archivo` | No se había generado: en este menú es la opción **5** (la 4 es el estado) | Opción 5 y luego `source .env` (paso 8) |
| `ca-certificates.crtrt` (arrastrado de LP4-02) | Error al teclear el `export` | Repetirlo con la ruta correcta (paso 0) |
| `quantizedFlat` y `diskANN` cuestan lo mismo | Con menos de 1.000 vectores no activan su índice | Ninguno: es el comportamiento esperado a esta escala |
| Los resultados difieren entre índices | Empates de puntuación con texto repetido | Ninguno: no es pérdida de precisión |
| Cada lab trae otra suscripción | La plataforma crea una por sesión | Verificar el cleanup **antes** de abrir la sesión siguiente |
