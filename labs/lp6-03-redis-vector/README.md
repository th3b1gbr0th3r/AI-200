# Lab LP6-03 · Implement semantic search in Azure Managed Redis

- **Estado: PREPARADO, sin ejecutar.** Redactado el 17/11/2026 a partir de la guía oficial y del `azdeploy.py` del starter. Todas las salidas están marcadas «(pendiente de ejecutar; salida esperada según la guía)».
- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/03-amr-vector-storage.html (fuente Markdown: `instructions/azure-managed-redis/03-amr-vector-storage.md`).
- **Teoría:** [06-3-redis-vector-storage.md](../../docs/modulos/06-3-redis-vector-storage.md). Índice: [06-redis.md](../../docs/modulos/06-redis.md).
- **Starter ya descargado y descomprimido aquí:** `amr-vector-query-python.zip` → `azdeploy.py` y `client/` (`app.py`, `vector_functions.py`, `sample_data.json`, `requirements.txt`, `templates/`, `static/`). Origen MIT: [`../NOTICE.md`](../NOTICE.md). **Nada se ha ejecutado.**
- Duración según la guía: ~30 min (más 5-10 min de despliegue). Extensión `redisenterprise` 2.75.0 o superior.
- Lab anterior: [LP6-02](../lp6-02-redis-pubsub/README.md).

Cada paso tiene: **por qué → comando → salida esperada → qué mirar → comprobación (y qué hacer si no coincide)**.

## Qué se construye
Búsqueda semántica de productos con **RediSearch**: índice vectorial HNSW (FLOAT32, **8 dimensiones**, distancia COSINE) sobre hashes `product:*`, consulta KNN y app Flask (`client/app.py`, no se edita). Los embeddings vienen precalculados en `client/sample_data.json`: no se llama a ningún modelo.

```
azdeploy.py 1 → RG + clúster amr-exercise-<hash> (Balanced_B0, acceso público)
azdeploy.py 2 → base de datos con módulo RediSearch (EnterpriseCluster, NoEviction) + acceso Entra + .env
azdeploy.py 3 → estado
client/app.py → http://localhost:5000: cargar, listar, buscar similares, guardar y borrar productos
```
Diferencia clave respecto a LP6-01/02 (leída del script, no ejecutada): la base de datos se crea con `--modules name=RediSearch`, `--clustering-policy EnterpriseCluster` y `--eviction-policy NoEviction` (aquí no se puede desalojar nada: es el almacén de vectores, no una caché). Si el módulo se puede añadir después de crear la base de datos, no está verificado.

Analogía K8s: el índice se autosincroniza con las claves del prefijo `product:`, como un selector de etiquetas que recoge los objetos nuevos.

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp6-03-redis-vector
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
**Por qué:** `deactivate` sale del `.venv` de otro lab. `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa; hay que exportarlo **en cada terminal nueva**.

**Comprobación:** `[ -n "${REQUESTS_CA_BUNDLE:-}" ] && echo definida` debe imprimir `definida`. Si no, repite el `export`.

## Paso 1 · `az login` con el usuario del lab
```bash
az logout
az login
```
**Por qué:** cada lab de la plataforma trae su propio usuario temporal y suscripción. `azdeploy.py` consulta `az ad signed-in-user show` y **sale si no hay sesión**; además el nombre de la caché (`amr-exercise-<hash>`) sale de un hash de tu *object id*.

Salida (pendiente de ejecutar; salida esperada según la guía): selección de suscripción y tenant del lab.

**Qué mirar:** que la suscripción sea la del lab, no la de empresa.

**Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Debe salir la suscripción y el usuario del lab. Si sale la cuenta de empresa, repite `az logout` y `az login`.

## Paso 2 · Registrar el proveedor e instalar la extensión `redisenterprise`
```bash
az provider register --namespace Microsoft.Cache
az extension add --upgrade --name redisenterprise
```
**Por qué:** Azure Managed Redis vive en `Microsoft.Cache` y se gestiona con `az redisenterprise …` (extensión de la CLI, no incluida de serie; la guía pide una versión reciente, 2.75.0 o superior en los labs 2 y 3). Es lo que `azdeploy.py` ejecuta por debajo.

**Qué mirar:** si `az extension add` falla con error de certificado, falta el `REQUESTS_CA_BUNDLE` del paso 0.

**Comprobación:**
```bash
az provider show -n Microsoft.Cache --query registrationState -o tsv
az extension list --query "[?name=='redisenterprise'].version" -o tsv
```
Esperado: `Registered` y un número de versión. Si el proveedor sale `Registering`, repite el `show` al cabo de un minuto.

## Paso 3 · Poner el resource group y la región en `azdeploy.py`
```bash
RG=rg-ai200-lp6-03
sed -i "s/<your-resource-group-name>/$RG/; s/<your-azure-region>/eastus2/" azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
**Por qué:** solo se editan esas dos variables. Si la plataforma del lab impone un grupo o una región, usa los suyos. `eastus2` es una de las regiones que el propio script sugiere si falta capacidad (`eastus2`, `australiaeast`, `canadacentral`); no está verificado que sea la más barata ni la más cercana.

**Comprobación:** el `grep` debe mostrar `rg = "rg-ai200-lp6-03"` y `location = "eastus2"`. Si siguen apareciendo `<your-…>`, el `sed` no encontró el texto: edita el fichero a mano.

## Paso 4 · Crear el clúster (`azdeploy.py` → opción 1)
**Por qué:** 5-10 minutos; se lanza primero. **Genera coste**: confirmar suscripción, región y limpieza.
```bash
python3 azdeploy.py      # menú → 1
```
Menú: `1` crear, `2` base de datos y acceso, `3` estado, `4` salir.

Salida (pendiente de ejecutar; salida esperada según la guía): `Azure Managed Redis resource created successfully: amr-exercise-<hash>`.

**Qué mirar:** si falla por capacidad, cambia `location` (por ejemplo `eastus2`) y repite la opción 1.

**Comprobación** (otra terminal, con el paso 0 hecho):
```bash
az redisenterprise list -g rg-ai200-lp6-03 --query "[].{name:name, state:provisioningState, sku:sku.name}" -o table
```
Esperado: `Balanced_B0` y `Creating` → `Succeeded`. Si sale `Failed`, repite la opción 1.

## Paso 5 · Completar `client/vector_functions.py`
**Por qué:** cuatro secciones vacías. Código **literal de la guía**. Espacios, no tabuladores. Ya están importados `numpy`, `TextField`, `VectorField`, `IndexDefinition`, `IndexType` y `Query`.

### 5.1 Conexión (`CONNECTION`, sin sangrar, a nivel de módulo)
```python
def get_client() -> redis.Redis:
    """Create a Redis client for Azure Managed Redis using Microsoft Entra ID."""
    redis_host = os.environ.get("REDIS_HOST")

    if not redis_host:
        raise ValueError("REDIS_HOST environment variable must be set")

    credential_provider = create_from_default_azure_credential(
        ("https://redis.azure.com/.default",),
    )

    return redis.Redis(
        host=redis_host,
        port=10000,
        ssl=True,
        decode_responses=False,
        credential_provider=credential_provider,
        socket_timeout=30,
        socket_connect_timeout=30,
    )
```
**Qué mirar:** aquí `decode_responses=False`: el cliente devuelve **bytes**, necesario porque el embedding se guarda en binario.

### 5.2 Crear el índice (`CREATE VECTOR INDEX`, **dentro de `VectorManager`, sangrado 4 espacios**)
```python
def _create_vector_index(self):
    """Create a RediSearch index for product semantic search."""
    try:
        schema = (
            TextField("name"),
            TextField("category"),
            TextField("product_id"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": VECTOR_DIM,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )

        definition = IndexDefinition(
            prefix=["product:"],
            index_type=IndexType.HASH,
        )

        self.r.ft(VECTOR_INDEX_NAME).create_index(
            fields=schema,
            definition=definition,
        )
    except redis.ResponseError as e:
        if "already exists" not in str(e):
            raise Exception(f"Error creating vector index: {e}")
    except Exception as e:
        raise Exception(f"Error creating vector index: {e}")
```
**Qué mirar:** los parámetros de la teoría: algoritmo `HNSW`, `TYPE FLOAT32`, `DIM` = `VECTOR_DIM` (8) y `DISTANCE_METRIC COSINE`; `prefix=["product:"]` e `index_type=HASH`. Si el índice ya existe, el error `already exists` se ignora (idempotente, como `kubectl apply`).

### 5.3 Guardar productos (`STORE PRODUCT`, sangrado 4 espacios)
```python
def store_product(
    self,
    vector_key: str,
    vector: list[float],
    metadata: dict[str, str] | None = None,
) -> tuple[bool, str]:
    """Store or update a product hash containing embedding and metadata."""
    try:
        embedding = np.array(vector, dtype=np.float32)
        data: dict[str, Any] = {"embedding": embedding.tobytes()}

        if metadata:
            for key, value in metadata.items():
                data[key] = str(value)

        result = self.r.hset(vector_key, mapping=data)
        if result > 0:
            return True, f"Product stored successfully under key '{vector_key}'"
        return True, f"Product updated successfully under key '{vector_key}'"
    except Exception as e:
        return False, f"Error storing product: {e}"
```
**Qué mirar:** el embedding se convierte a bytes float32 con `tobytes()` y va en el mismo hash que los metadatos.

### 5.4 Buscar similares (`SEARCH SIMILAR PRODUCTS`, sangrado 4 espacios)
```python
def search_similar_products(
    self,
    query_vector: list[float],
    top_k: int = 3,
) -> tuple[bool, list[dict[str, Any]] | str]:
    """Run a KNN vector query against product embeddings."""
    try:
        query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

        knn_query = (
            Query(f"*=>[KNN {top_k} @embedding $query_vec AS score]")
            .return_fields("name", "category", "product_id", "score")
            .sort_by("score")
            .dialect(2)
        )

        results = self.r.ft(VECTOR_INDEX_NAME).search(
            knn_query,
            query_params={"query_vec": query_bytes},
        )

        if results.total == 0:
            return False, "No products found in Redis. Load sample products first."

        similarities: list[dict[str, Any]] = []
        for doc in results.docs:
            similarities.append(
                {
                    "key": doc.id,
                    "similarity": float(doc.score),
                    "product_id": doc.product_id.decode() if isinstance(doc.product_id, bytes) else doc.product_id,
                    "name": doc.name.decode() if isinstance(doc.name, bytes) else doc.name,
                    "category": doc.category.decode() if isinstance(doc.category, bytes) else doc.category,
                }
            )

        return True, similarities
    except Exception as e:
        return False, f"Error searching products: {e}"
```
**Qué mirar:** `KNN {top_k} @embedding $query_vec AS score`, `sort_by("score")` y **`dialect(2)`** obligatorio para consultas vectoriales. Con COSINE, **menor `score` = más parecido**.

**Comprobación** (solo lectura):
```bash
python3 -m py_compile client/vector_functions.py && echo "sintaxis OK"
grep -c "def get_client\|def _create_vector_index\|def store_product\|def search_similar_products" client/vector_functions.py
```
Esperado: `sintaxis OK` y `4`. Si falla con `IndentationError`, revisa que las tres últimas funciones estén dentro de `VectorManager`. Borra el `__pycache__` generado.

## Paso 6 · Base de datos con RediSearch y acceso (opciones 2 y 3)
**Por qué:** crea la base de datos vectorial, asigna tu acceso Entra y escribe `.env`.
```bash
python3 azdeploy.py      # menú → 2 → 3 → 4
```
Salida (pendiente de ejecutar; salida esperada según la guía): `Creating vector-search database with RediSearch module...`, `Assigning Microsoft Entra access for the current user...` y el resumen con el endpoint.

**Comprobación** (con `az`):
```bash
az redisenterprise database show -g rg-ai200-lp6-03 --cluster-name amr-exercise-<hash> --query "{state:provisioningState, modules:modules[].name, clustering:clusteringPolicy, eviction:evictionPolicy}" -o json
grep -c REDIS_HOST .env
```
Esperado: `Succeeded`, módulo `RediSearch`, `EnterpriseCluster`, `NoEviction` y `1`. Si `modules` sale vacío, la base de datos no tiene RediSearch y la creación del índice fallará con un error de comando desconocido; no hay vuelta atrás sin recrear la base de datos (borrarla y repetir la opción 2). Los nombres de propiedades de `--query` no están verificados.

## Paso 7 · Comprobar que el puerto 10000 sale del PC (aviso del proxy)
**Por qué:** Azure Managed Redis habla **TLS por el puerto 10000**, no por 443. El PC es de empresa y su proxy transparente ya ha bloqueado `kubectl` contra AKS, así que **este puerto puede fallar** (timeout, o error de certificado/TLS). Mejor saberlo antes de arrancar la app. Esta comprobación solo lee.
```bash
source .env
timeout 10 bash -c 'exec 3<>/dev/tcp/$REDIS_HOST/10000' && echo "puerto 10000 abierto" || echo "puerto 10000 BLOQUEADO"
```
(`REDIS_HOST` es la variable que genera el propio lab; no se muestra su valor.)

Salida (pendiente de ejecutar; salida esperada según la guía): `puerto 10000 abierto`.

**Qué mirar:** `/dev/tcp` solo prueba el TCP. Aunque salga abierto, el proxy podría romper el TLS: el error aparecería al conectar la app (paso siguiente). Si sale BLOQUEADO o la app da `Timeout`/`SSL`/`Error 999` (el propio código del lab sugiere que 999 es un problema de red o firewall), alternativas, en este orden:
1. Otra red sin ese proxy (por ejemplo, un punto de acceso móvil), si la política de empresa lo permite.
2. Ejecutar la app desde otra máquina o desde Azure Cloud Shell (subes los ficheros del lab y haces `az login`). No verificado que `DefaultAzureCredential` autentique en Cloud Shell: confírmalo antes de depender de ello.
3. Pedir a TI que permita `*.redis.azure.net:10000` (el dominio del endpoint no está verificado hasta ver el valor real de `REDIS_HOST`).

**Comprobación:** el `echo` final dice `abierto`. Si no, no sigas: el resto del lab necesita esa conexión.

## Paso 8 · Entorno Python (en `client/`)
```bash
source .env
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Salida (pendiente de ejecutar; salida esperada según la guía): `Successfully installed … numpy-2.5.3 … redis-8.0.1 redis-entraid-1.2.1 …` (versiones leídas de `requirements.txt`).

**Comprobación:** `pip list | grep -iE "numpy|redis|flask"`. Si falla por certificado: `--cert /etc/ssl/certs/ca-certificates.crt`.

## Paso 9 · Ejecutar la app y probar la búsqueda
```bash
python3 app.py
```
Abre http://localhost:5000 (el script del starter fija el puerto 5000). Salida (pendiente de ejecutar; salida esperada según la guía): la página de la app; al arrancar `VectorManager` hace `ping` y crea el índice `idx:products`.

Pruebas de la guía:

| # | Acción | Esperado | Qué demuestra |
|---|---|---|---|
| 1 | **Load Sample Products**, luego **List All Products** | los productos de `sample_data.json` (`product:001`…) | ingesta con `HSET` |
| 2 | Buscar similares a `product:001`, top_k = 5 | 5 resultados ordenados por score (el propio `product:001` con score ≈ 0) | KNN con COSINE |
| 3 | Guardar `product:011` con embedding `[0.53, 0.63, 0.58, 0.37, 0.68, 0.47, 0.73, 0.57]` y `product_id=011`, `name=Gym Bag`, `category=Sports` | guardado correcto | el índice se autosincroniza |
| 4 | Buscar similares a `product:009` | `product:011` aparece según su cercanía | el producto nuevo ya es buscable sin reindexar |
| 5 | Borrar `product:011` y **List All Products** | ya no aparece | borrado |

**Qué mirar:** el embedding de 8 números debe tener **exactamente** 8 valores (si no, el índice rechaza el vector: las dimensiones deben coincidir). Busca antes de cargar los datos de ejemplo y dará «No products found». Nota para el debate de la teoría: `list_all_products` del starter usa `KEYS product:*`, justo el comando que el módulo 1 dice **evitar en producción** (aquí vale por ser 10 claves).

**Comprobación:** cada fila coincide. Errores de conexión/timeout: red o proxy (paso 7). `Authentication error`: espera a que se propague la política (paso 6). Para parar la app: Ctrl+C.

## Paso 10 · Cleanup (obligatorio)
**Por qué:** Azure Managed Redis cobra mientras exista (el precio por hora de `Balanced_B0` no está verificado: consúltalo en la página de precios). Hazlo **antes de documentar**: si caducan las credenciales del lab ya no se puede borrar ni comprobar.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-lp6-03 --no-wait --yes
az group exists --name rg-ai200-lp6-03
```
**Comprobación:** repite `az group exists --name rg-ai200-lp6-03` hasta que devuelva `false` (puede tardar varios minutos; Redis Enterprise tarda en borrarse). Mientras tanto `az resource list -g rg-ai200-lp6-03 -o table` muestra lo que queda. Si pasados ~15 minutos sigue `true`, mira `az redisenterprise list -g rg-ai200-lp6-03 -o table` y repite el `delete`.

Inventario final: `az group list -o table` no debe mostrar `rg-ai200-lp6-03`. 

Salida (pendiente de ejecutar; salida esperada según la guía): `false`.

## Resumen de incidencias
(Se rellena al ejecutar el lab. Riesgos previstos:)

| Posible síntoma | Causa probable | Arreglo |
|---|---|---|
| Timeout/SSL al conectar | Proxy bloquea el puerto 10000 | Paso 7 |
| Error al crear el índice (comando desconocido) | La base de datos no tiene RediSearch | Paso 6: recrear con la opción 2 |
| «No products found» | Búsqueda antes de cargar los datos | Load Sample Products |
| Error de dimensión del vector | Embedding con distinto nº de valores que `VECTOR_DIM` (8) | Usar 8 valores |
| Fallo de despliegue | Falta de capacidad en la región | Cambiar `location`, repetir opción 1 |
