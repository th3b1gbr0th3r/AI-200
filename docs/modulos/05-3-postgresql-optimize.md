# LP5 · Módulo 3 · Optimizar la búsqueda vectorial en PostgreSQL

Volver al [índice de LP5](05-postgresql.md). Lab: [Optimize vector search performance](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html) (carpeta del lab pendiente).

## Parámetros del servidor y de pgvector
| Parámetro | Qué hace | Valor de ejemplo |
|---|---|---|
| `shared_buffers` / `work_mem` | Memoria para tener los índices vectoriales en caché | `2GB` / `256MB` |
| `random_page_cost` | Coste estimado de lectura aleatoria; bajo para SSD | `1.1` |
| `effective_io_concurrency` | E/S en paralelo | `200` |
| `ivfflat.probes` (por sesión) | Listas que se exploran: más = más recall, más lento | `10` |
| `hnsw.ef_search` (por sesión) | Profundidad de exploración del grafo | `100` |

`EXPLAIN ANALYZE` confirma si la consulta usa el índice y cuánto tarda (como `kubectl describe` para el plan de la consulta). `SET LOCAL` aplica un parámetro solo a la transacción en curso.

## Elegir índice
- **HNSW:** lecturas intensivas y precisión crítica; latencia estable.
- **IVFFlat:** reconstrucciones frecuentes o poca memoria; `lists` ≈ raíz cuadrada del número de filas.

## Disposición de los datos
- Columnas estructuradas con B-tree para los filtros habituales; `JSONB` para atributos dinámicos o poco filtrados; índices compuestos para filtros de varias columnas.
- Filtrar por metadatos antes de la búsqueda vectorial; post-filtro cuando el predicado es poco selectivo.
- Particionar la tabla a partir de decenas de millones de filas.

## Escalado
- **Vertical primero:** Memory Optimized (8 GB/vCore) para tener los índices en caché; vigilar CPU, memoria e IOPS.
- **Después horizontal:** hasta 5 réplicas de lectura; Redis para datos muy pedidos; capacidad reservada (hasta 65 % de descuento).

## Conexiones
- **PgBouncer** integrado (General Purpose y Memory Optimized), en modo *transaction*: multiplexa conexiones y evita agotarlas con mucha concurrencia.
- Tamaño del pool repartido entre réplicas de la aplicación (como el `maxSurge` de pods × conexiones por pod).
- Reintentos con backoff exponencial ante fallos transitorios.

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros (la presentación no las trae): confirmarlas con el profesor.
1. 5 millones de embeddings, refresco completo diario, construcción en menos de 30 min → **A. IVFFlat** con `lists` = raíz cuadrada de las filas.
2. Búsqueda filtrada por `category_id` con *sequential scan* → **A. Comprobar que existe un índice B-tree en `category_id`**.
