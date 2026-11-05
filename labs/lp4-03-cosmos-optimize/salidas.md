# Salidas reales · LP4-03 Optimize query performance for Azure Cosmos DB (Lab 11 · AI-200-LP04M03)

Saneadas: sin ID de suscripción, tenant ni usuario del lab; hash de la cuenta como `<hash>`. Ejecutado el 05/11/2026 en Linux (`mol-bastion`). Todo el despliegue va por `az` (vía `azdeploy.py`). El grupo `rg-ai200-cosmos-optimize` es **nuestro**.

## 1. Login: tercera suscripción del día
```console
$ az login --use-device-code
Tenant: Lab Directory
Subscription: XLabs-<n> (<subscription-id>)      # lab 9: 278 · lab 10: 274 · lab 11: 232
$ az group list -o table
az104-rg7                 eastus  Succeeded     # de otro curso, no se toca
```
**Qué mirar:** cada lab de la plataforma trajo una suscripción distinta. Por eso el cleanup de los labs 9 y 10 quedó **sin verificar**: desde otra suscripción `az group exists` devuelve `false` aunque el grupo siga vivo en la anterior.

## 2. Starter (dentro del repo, `labs/lp4-03-cosmos-optimize/`)
```console
$ curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-optimize-query-python.zip
$ unzip -oq cosmosdb-optimize-query-python.zip && ls client
app.py  generate_sample_data.py  index_functions.py  requirements.txt  sample_vectors.json  setup_containers.py  static  templates
$ sed -n '5,6p' azdeploy.py
rg = "rg-ai200-cosmos-optimize"  # Resource Group name
location = "eastus"   # Azure region for the resources
```
**Qué mirar:** la guía menciona `index_functions.py` (a completar), `setup_containers.py` (revisión) y `generate_sample_data.py`. El script define 3 contenedores, uno por tipo de índice vectorial (`flat`, `quantizedFlat`, `diskANN`).

## 3. Opción 1: cuenta y base de datos
```console
Checking/creating resource group 'rg-ai200-cosmos-optimize'...
Resource group created: rg-ai200-cosmos-optimize

Creating Azure Cosmos DB for NoSQL account 'cosmos-index-<hash>' in 'eastus'...
Cosmos DB account created with vector search capability
Creating database 'indexoptimize'...
Database created: indexoptimize
```
```console
$ az cosmosdb list -g rg-ai200-cosmos-optimize --query "[].{n:name,e:provisioningState,cap:capabilities[].name}" -o json
[{"cap": ["EnableServerless", "EnableNoSQLVectorSearch"], "e": "Succeeded", "n": "cosmos-index-<hash>"}]
```
**Qué mirar:** cuenta **serverless** con `EnableNoSQLVectorSearch`. En este lab la opción 1 **no** crea contenedores: lo hace la opción 2.

## 4. Opción 2: tres contenedores con distinto índice vectorial
```console
Container created: vectors-flat (exact nearest neighbor)
Container created: vectors-quantized (compressed exact search)
Container created: vectors-diskann (approximate nearest neighbor)

All containers share:
  - Partition key: /documentId
  - Vector embedding: /embedding (float32, cosine, 256 dimensions)
```
```console
$ az cosmosdb sql container list -g rg-ai200-cosmos-optimize -a cosmos-index-<hash> -d indexoptimize --query "[].{n:name, idx:resource.indexingPolicy.vectorIndexes[0].type}" -o table
N                  Idx
-----------------  -------------
vectors-diskann    diskANN
vectors-quantized  quantizedFlat
vectors-flat       flat
```
**Qué mirar:** mismos datos y misma política de embeddings, **solo cambia el índice**. `flat` es búsqueda exacta (recorre todos los vectores); `quantizedFlat` es exacta sobre vectores comprimidos; `diskANN` es aproximada, basada en grafo. El objetivo del lab es medir RU y tiempo de la misma consulta en los tres.

## 5. Opción 3: acceso con Entra ID y estado
```console
Azure RBAC Contributor role assigned
Cosmos DB Data Contributor role assigned

Cosmos DB Account (cosmos-index-<hash>):
  Status: Succeeded
  Database indexoptimize: Created
  Container vectors-flat: Created
  Container vectors-quantized: Created
  Container vectors-diskann: Created
  Entra ID access: <usuario-del-lab> (full control)
```
```console
$ az cosmosdb sql role assignment list -g rg-ai200-cosmos-optimize -a cosmos-index-<hash> --query "length(@)" -o tsv
1
```
**Qué mirar:** los dos roles (ARM y datos), igual que en los labs 9 y 10.

## 6. Opción 4: `.env`, entorno Python y funciones
```console
Endpoint: https://cosmos-index-<hash>.documents.azure.com:443/
Database: indexoptimize
Containers: vectors-flat, vectors-quantized, vectors-diskann
Environment variables saved to .env and .env.ps1
$ grep -c '^export COSMOS_' .env
2
```
**Qué mirar:** el `.env` solo trae endpoint y base de datos (los nombres de los 3 contenedores están fijados en `index_functions.py`). Sin claves; está en `.gitignore`. En `client/index_functions.py` se completaron `vector_similarity_search` (mide tiempo y RU de una consulta) y `compare_index_performance` (la ejecuta en los 3 contenedores).

## 7. Carga de 500 tickets en cada contenedor (coste de escritura por índice)
```console
Loaded 500 documents to all containers. RU costs - flat: 5829.66, quantizedFlat: 6884.66, diskANN: 27535.68
```
| Índice | RU totales | RU por documento | Respecto a `flat` |
|---|---|---|---|
| `flat` | 5.829,66 | ≈ 11,7 | 1,0× |
| `quantizedFlat` | 6.884,66 | ≈ 13,8 | 1,2× |
| `diskANN` | 27.535,68 | ≈ 55,1 | 4,7× |

**Qué mirar:**
- **`diskANN` es el más caro de escribir** (≈ 4,7× `flat`): hay que insertar cada vector en un grafo de vecinos. `quantizedFlat` añade poco sobre `flat` (comprime el vector).
- **Coincide con el lab 10:** allí un ticket con DiskANN costó ≈ 53,4 RU; aquí ≈ 55,1.
- Es el precio de una búsqueda aproximada rápida: las escrituras se pagan una vez; las lecturas con DiskANN deberían ser más baratas **a escala** (en 500 vectores la diferencia puede ser pequeña o invertida).

## 8. Comparación de búsqueda: `I can't login to my account`, Top 5
```console
Index Type     Container          Results  RU Cost  Time (ms)  Status
flat           vectors-flat       5        10.13    604.02     ok
quantizedFlat  vectors-quantized  5        21.60    500.89     ok
diskANN        vectors-diskann    5        21.60    538.47     ok
```
Primeros resultados (se pegaron 3 de los 5 por índice; el contenido de los tickets es ficticio y no se guarda):
```console
flat           doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-005  0.0207
quantizedFlat  doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-100  0.0207
diskANN        doc-billing-002  0.0638 · doc-account-001  0.0521 · doc-account-100  0.0207
```
**Qué mirar:**
- **RU:** `flat` es el más barato (10,13); `quantizedFlat` y `diskANN` cuestan **exactamente lo mismo** (21,60), el doble. Con 500 vectores `diskANN` no aporta ventaja. Causa (diapositivas del curso): `quantizedFlat` y `diskANN` **necesitan 1.000 o más vectores para activarse**; por debajo hacen un escaneo por fuerza bruta. Con 500 vectores los dos hicieron lo mismo, lo que explica el coste idéntico.
- **Tiempo:** 500-604 ms, muy parecido entre los tres y dominado por la latencia de red desde `mol-bastion` y el proxy; no es una medida fiable del motor. Una sola ejecución no basta para ordenar los índices.
- **Resultados iguales** en los tres: mismos documentos y mismas puntuaciones. La única diferencia (`doc-account-005` frente a `doc-account-100`) es un **empate**: ambos tienen la misma puntuación (0,0207) y el mismo texto, porque el generador de datos repite plantillas. No es una pérdida de precisión de `diskANN`.
- **La calidad semántica es baja:** el primero para «no puedo entrar en mi cuenta» es un ticket de facturación (`billing`) con puntuación 0,0638, casi ortogonal. Los 500 vectores no tienen significado real, así que sirven para medir coste, no relevancia.

## 9. Búsqueda filtrada: `I can't login to my account` + categoría `account`, Top 5
```console
Index Type     Container          Results  RU Cost  Time (ms)  Status
flat           vectors-flat       5        8.15     673.56     ok
quantizedFlat  vectors-quantized  5        8.15     461.72     ok
diskANN        vectors-diskann    5        8.15     510.40     ok
```
Primeros resultados (se pegaron 3 de los 5 por índice):
```console
flat           doc-account-001  0.0521 · doc-account-098  0.0207 · doc-account-097  0.0207
quantizedFlat  doc-account-001  0.0521 · doc-account-099  0.0207 · doc-account-097  0.0207
diskANN        doc-account-001  0.0521 · doc-account-098  0.0207 · doc-account-097  0.0207
```
**Qué mirar:**
- **Los tres cuestan lo mismo (8,15 RU)**, y menos que sin filtro: `flat` baja de 10,13 a 8,15 y `quantizedFlat`/`diskANN` de 21,60 a 8,15 (**−62 %**). Filtrar reduce los candidatos antes del ranking vectorial. Que los tres coincidan es coherente con el umbral de 1.000 vectores (ninguno activa su índice) y con que el filtro deja aún menos candidatos.
- **Solo salen tickets `account`:** el ticket de facturación (`doc-billing-002`, 0,0638) que era el primero sin filtro ya no aparece, y el primero es `doc-account-001` (0,0521).
- **Las diferencias entre índices** (`doc-account-097/098/099`) son otra vez **empates** (misma puntuación 0,0207 y mismo texto por las plantillas repetidas), no pérdida de precisión.
- **Tiempo:** 461-673 ms, de nuevo dominado por la red/proxy; no sirve para comparar índices.

## 10. Cleanup (verificado)
```console
$ az group delete --name rg-ai200-cosmos-optimize --no-wait --yes
$ az group show -n rg-ai200-cosmos-optimize --query properties.provisioningState -o tsv
Deleting
$ az group exists --name rg-ai200-cosmos-optimize
false                      # tras unos minutos (la cuenta Cosmos tarda en borrarse)
$ az group list -o table
az104-rg7  eastus  Succeeded      # de otro curso, no se toca; ningún rg-ai200-*
```
**Qué mirar:** a diferencia de los labs 9 y 10, aquí la suscripción no cambió entre el borrado y la comprobación, así que `false` es una prueba válida.
