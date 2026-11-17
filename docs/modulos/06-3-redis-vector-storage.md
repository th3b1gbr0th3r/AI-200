# LP6 · Módulo 3 · Almacenamiento vectorial en Azure Managed Redis

Volver al [índice de LP6](06-redis.md). Lab: [LP6-03 · Semantic search](../../labs/lp6-03-redis-vector/README.md).

**RediSearch** añade capacidades de base de datos vectorial: almacenar y consultar embeddings, con índices **FLAT** y **HNSW** y filtrado híbrido por metadatos. Casos: búsqueda semántica, recomendaciones y RAG. Mismo concepto que `VectorDistance` en Cosmos (LP4) y `pgvector` (LP5), pero en memoria.

## Crear el índice
```python
schema = (TextField("title"),
          VectorField("embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": 1536, "DISTANCE_METRIC": "COSINE"}))
redis_client.ft("idx:docs").create_index(fields=schema,
    definition=IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH))
```
- El índice se **autosincroniza** con las claves cuyo prefijo coincide (`doc:`): analogía con un selector de etiquetas que recoge los objetos nuevos.
- Los embeddings se convierten a bytes con `tobytes()`; carga masiva con pipelines (la presentación habla de 10-100x de throughput).
- Las **dimensiones** del índice y de la consulta deben coincidir.

## Consultas
| Tipo | Qué hace |
|---|---|
| KNN | número fijo de vecinos más cercanos: `*=>[KNN 5 @embedding $vec AS score]` |
| Híbrida | filtro por metadatos + similitud: `@category:{docs}=>[KNN 3 @embedding $vec AS score]` |
| Range | todos los vectores dentro de un umbral de distancia |

Menor distancia = mayor similitud. Las consultas vectoriales requieren `.dialect(2)`.

## Elecciones de diseño
| Decisión | Opción | Cuándo (según la presentación) |
|---|---|---|
| Algoritmo | FLAT | menos de ~10.000 vectores; exacto |
| | HNSW | datasets grandes, 95-99 % de precisión, ajustando `EF_RUNTIME` (**pregunta 1**) |
| Tipo | FLOAT32 | estándar en IA: la mitad de memoria que FLOAT64 sin pérdida significativa |
| Estructura | Hash | datos planos, vectores en bytes, menos memoria y más rápido (**pregunta 2**) |
| | JSON | objetos anidados o varios vectores por documento; vectores como arrays (`tolist()`) |

## Qué hace el lab
8 dimensiones (de juguete, para ver el funcionamiento), HNSW, FLOAT32, COSINE, claves `product:*`. La base de datos se crea con el **módulo RediSearch** (el script lo pasa en `az redisenterprise database create --modules name=RediSearch`).

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros: confirmarlas con el profesor.
1. HNSW frente a FLAT → **A.** datasets grandes (>10.000) y consultas rápidas con 95-99 % de precisión.
2. Hash frente a JSON → **A.** modelo plano y máxima eficiencia de memoria y consulta.
