# LP5 · Módulo 2 · Búsqueda vectorial con pgvector

Volver al [índice de LP5](05-postgresql.md). Lab: [LP5-02 · Vector search](../../labs/lp5-02-pg-vector-search/README.md) (parcial: esquema con pgvector 0.8.7 y app; sin la búsqueda en la web).

## pgvector
Extensión que añade el tipo `vector(n)` y operadores de similitud. El embedding se guarda en la misma fila que los metadatos: una sola consulta trae ambos. `n` debe coincidir con las dimensiones del modelo (p. ej. 1536).

| Operador | Distancia | Clase de operador del índice |
|---|---|---|
| `<=>` | Coseno (la habitual para texto) | `vector_cosine_ops` |
| `<->` | Euclídea (L2) | `vector_l2_ops` |
| `<#>` | Producto interno negativo | `vector_ip_ops` |

**Trampa de examen:** si la clase de operador del índice no coincide con el operador de la consulta, **el índice no se usa**.

## Índices ANN: IVFFlat frente a HNSW
| | IVFFlat | HNSW |
|---|---|---|
| Estructura | Clusters (listas por k-means) | Grafo navegable por capas |
| Creación | Necesita datos ya cargados | Puede crearse vacío; inserciones incrementales |
| Construcción / memoria | Rápida / baja | Más lenta / más alta |
| Recall | Menor | Mayor (99 %+) |
| Sintaxis | `USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)` | `USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)` |

Comparación con Cosmos (LP4): `flat` ≈ sin índice (búsqueda exacta); `diskANN` ≈ HNSW (grafo); IVFFlat no tiene equivalente directo.

## Ciclo de vida del índice y de los embeddings
- Vigilar con `pg_stat_user_indexes`; reconstruir si cambia mucho la distribución de los datos.
- `CREATE INDEX CONCURRENTLY` para reconstruir sin cortar el servicio.
- Actualizar en lotes de 1.000-5.000 filas por transacción; columna `stale` para refrescar en segundo plano.
- Cambio de modelo: **columna paralela** (nueva columna → índice → rellenar → validar → borrar la vieja), con vuelta atrás posible. Como un despliegue blue/green.

## Búsqueda semántica y RAG
- Combinar similitud con `WHERE` sobre metadatos; umbral de distancia para descartar resultados poco relevantes; índices B-tree en las columnas filtradas.
- **Búsqueda híbrida:** vectorial + texto completo, fusionadas con Reciprocal Rank Fusion (RRF), igual que en Cosmos.
- Diseño RAG: tablas `source_documents` y `document_chunks` (con `chunk_index` y `token_count`) para citar la fuente, traer fragmentos vecinos y no pasarse de tokens.
- Medir la calidad con precision, recall y MRR.

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros (la presentación no las trae): confirmarlas con el profesor.
1. Embeddings normalizados, similitud semántica → **A. `<=>` (coseno)**.
2. 5 millones de embeddings, solo actualizaciones por lotes ocasionales → **A. IVFFlat** con un número adecuado de `lists`.
