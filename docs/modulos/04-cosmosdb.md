# LP4 · Desarrollar soluciones de IA con Azure Cosmos DB for NoSQL

Notas propias del día 5 (05/11/2026), con los datos medidos en los labs. Para un perfil K8s: lo nuevo es el modelo de coste (RU), la partition key y los índices vectoriales. Presentación del instructor: `docs/AI-200T00A-04_…pdf`.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Lab |
|---|---|---|
| 1 | Consultas y almacén de documentos para RAG | [LP4-01](../../labs/lp4-01-cosmos-queries/README.md) |
| 2 | Búsqueda vectorial (`VectorDistance`, DiskANN) | [LP4-02](../../labs/lp4-02-cosmos-vector-search/README.md) |
| 3 | Optimizar consultas: `flat` / `quantizedFlat` / `diskANN` | [LP4-03](../../labs/lp4-03-cosmos-optimize/README.md) |

## Conceptos base (con analogía K8s)
| Concepto | Qué es | Analogía |
|---|---|---|
| Partition key | Campo que reparte los datos en particiones lógicas (`/documentId`) | shard key; como indicar namespace y nombre exactos en `kubectl get` |
| `id` + partition key | Identifican un documento; el `id` es único **dentro** de la partición | clave de objeto en un namespace |
| RU (Request Units) | Moneda de cada operación (lectura puntual de 1 KB ≈ 1 RU) | requests/limits, pero cobrado por operación |
| Serverless | Sin RU aprovisionadas; pagas las consumidas | escalado a cero, coste por uso |
| Plano de control / de datos | Dos RBAC distintos: ARM (`Contributor`) y Cosmos (`Built-in Data Contributor`) | crear un `Deployment` frente a hacer `exec` en el pod |
| `DefaultAzureCredential` | Prueba entorno, workload identity, managed identity y `az login` | el mismo código sirve en el PC y en AKS con Workload Identity |

## Las cuatro operaciones del lab 9 (de más barata a más cara)
| Operación | Función | Partición | Coste |
|---|---|---|---|
| Lectura puntual (`read_item`, `id` + partition key) | `get_chunk_by_id` | directa | ≈ 1 RU: la mejor opción si conoces ambas claves |
| Query con partition key | `get_chunks_by_document` | una sola | baja |
| Query cross-partition (`enable_cross_partition_query`) | `search_chunks_by_metadata` | todas (fan-out) | la más alta |
| Escritura (`upsert_item`) | `store_document_chunk` | la del `documentId` | varias RU (medido: ≈ 9,9 RU/chunk) |

Puntos de examen:
- **Parametrizar siempre** (`@param`): evita inyección SQL y reutiliza el plan.
- **Filtrar por un campo que no es la partition key obliga al fan-out**, aunque todos los resultados estén en un solo documento.
- **`upsert_item` reemplaza el documento entero** (no hace merge); para cambiar un campo, `patch_item`. Es idempotente.
- `OFFSET 0 LIMIT n` va junto; `ARRAY_CONTAINS` busca dentro de arrays.
- **Cosmos indexa todo por defecto**, y por eso escribir es caro.

## Búsqueda vectorial (lab 10)
- **Vector embedding policy** (ruta, tipo, dimensiones, función de distancia): **inmutable** tras crear el contenedor. Aquí: `/embedding`, `float32`, 256, `cosine`.
- **Vector index** (`diskANN`, `flat`, `quantizedFlat`): en la indexing policy; se puede cambiar.
- **Excluir `/embedding/*` del índice normal**: los vectores usan su índice propio y no se indexan como 256 propiedades sueltas.
- La cuenta necesita la capability `EnableNoSQLVectorSearch`.
- **`TOP n` es obligatorio** en consultas vectoriales; con `ORDER BY VectorDistance(...)`.
- Con `cosine`, **la puntuación más alta es la más parecida**, y el `ORDER BY` la pone primero.
- **Búsqueda híbrida:** filtro por metadato (`WHERE c.metadata.category = …`) + ranking por similitud.
- **La calidad la da el modelo de embeddings, no Cosmos**: Cosmos solo ordena por distancia entre los vectores que le das. En el lab 10, solo el primer resultado fue razonable (≈ 0,9997); del 2.º al 4.º las puntuaciones eran casi iguales (≈ 0,992) y sin sentido semántico.

## Comparación de índices (lab 11, 500 vectores de 256 dimensiones)
**Escritura** (carga de 500 documentos en cada contenedor):
| Índice | RU totales | RU/documento | Respecto a `flat` |
|---|---|---|---|
| `flat` | 5.829,66 | ≈ 11,7 | 1,0× |
| `quantizedFlat` | 6.884,66 | ≈ 13,8 | 1,2× |
| `diskANN` | 27.535,68 | ≈ 55,1 | **4,7×** |

**Lectura** (misma consulta Top 5):
| Índice | RU | Tiempo | Resultados |
|---|---|---|---|
| `flat` | **10,13** | 604 ms | 5 |
| `quantizedFlat` | 21,60 | 501 ms | 5 |
| `diskANN` | 21,60 | 538 ms | 5 |

Conclusiones:
1. **`diskANN` es el más caro de escribir** (≈ 4,7×): cada vector se enlaza en un grafo de vecinos. Coincide con el lab 10 (≈ 53 RU por ticket con DiskANN frente a ≈ 55 aquí).
2. **A esta escala `flat` gana en lectura** (la mitad de RU): recorrer 500 vectores es barato y no hay nada que acelerar. `diskANN` compensa con muchos vectores.
3. **`quantizedFlat` y `diskANN` costaron exactamente lo mismo** (21,60). Hipótesis **no verificada** en esta sesión: con pocos vectores no tienen aún un grafo útil y ambos recorren vectores comprimidos.
4. **Los tiempos no distinguen nada:** dependen de la latencia de red desde `mol-bastion` y del proxy, y es una sola ejecución.
5. **Los resultados salieron idénticos.** La única diferencia (`doc-account-005` frente a `doc-account-100`) fue un **empate** de puntuación y texto (el generador repite plantillas), no pérdida de precisión.
6. **Los datos de ese lab no tienen significado semántico** (un ticket de facturación salió el primero para una consulta de login): sirven para medir coste, no relevancia.

**Con filtro** (`WHERE category = 'account'` + Top 5): los tres índices costaron **8,15 RU**, menos que sin filtro (`flat` 10,13 → 8,15; `quantizedFlat`/`diskANN` 21,60 → 8,15, un −62 %). Filtrar reduce los candidatos antes del ranking vectorial, y el resultado solo contiene la categoría pedida. Que los tres coincidan sugiere (hipótesis, no verificada) que con pocos documentos ninguno aprovecha su índice vectorial.

Guía de elección (de la guía oficial):
| Escenario | Índice | Motivo |
|---|---|---|
| Menos de ~10.000 vectores | `flat` | exacto, coste aceptable |
| Memoria limitada | `quantizedFlat` | menos memoria con buena precisión |
| Producción a gran escala | `diskANN` | mejor eficiencia de RU, ≈ 95 % de recall |

## Limitaciones y buenas prácticas anotadas
- `get_container()` de los starters crea cliente y credencial en cada llamada: en producción, **una sola vez** y reutilizar (el lab 11 ya cachea cliente y contenedores).
- `search_chunks_by_metadata` solo usa el **primer tag** (`filters["tags"][0]`).
- Las RU del SDK en consultas son aproximadas (solo la última página); en producción, Azure Monitor.
- Los tests del lab 9 solo exigen `>=`: comprueban que responden, no el contenido exacto.

## Aprendizajes de la plataforma de labs (importante)
- **Cada lab trajo una suscripción distinta** (`XLabs-278`, `-274`, `-232`). Desde otra suscripción `az group exists` devuelve `false` **aunque el grupo siga vivo** en la anterior. Por eso hay que **verificar el cleanup antes de abrir la sesión siguiente**; los de los labs 9 y 10 quedaron como «borrado lanzado, no verificado».
- Los `azdeploy.py` de la plataforma solo llaman a `az` (sin `kubectl`): el proxy no molesta. Lo que sí puede fallar por TLS interceptado es `pip`/SDK: `REQUESTS_CA_BUNDLE`.
- Los menús difieren entre labs (la opción de roles es la 2 en el lab 9 y la 3 en los labs 10 y 11).
- La guía asume Windows/PowerShell; en Linux: `python3`, `source .env` y `source .venv/bin/activate`.

## Preguntas de repaso
_(se completan con el knowledge check del día: `docs/LP4 - Knowledge check.pdf`)_
1. ¿Qué operación de lectura es la más barata y qué necesita? 2. ¿Por qué una query por `category` es cross-partition aunque los datos estén en un solo documento? 3. ¿Qué parte de la política vectorial no se puede cambiar tras crear el contenedor? 4. ¿Por qué `diskANN` cuesta más al escribir? 5. ¿Cuándo conviene `flat` frente a `diskANN`? 6. ¿Por qué hacen falta dos roles distintos para trabajar con Cosmos desde código?
