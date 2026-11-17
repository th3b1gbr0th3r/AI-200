# LP6 · Mejorar soluciones de IA con Azure Managed Redis

Material de la clase del jueves 12/11/2026 (recuperada). Presentación del instructor: `docs/AI-200T00A-06_Enhance AI solutions with Azure Managed Redis.pdf`; test: `docs/LP6 - Knowledge check.pdf`. Redis es la **capa en memoria** delante de las bases de datos de LP4/LP5: caché, mensajería y también búsqueda vectorial.

> Estado: notas preparadas a partir de la presentación y la guía oficial **antes** de hacer los labs. Las respuestas del knowledge check están por confirmar con el profesor.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Notas | Lab |
|---|---|---|---|
| 1 | Operaciones de datos (tipos, TTL, invalidación de caché) | [06-1-redis-data-operations.md](06-1-redis-data-operations.md) | [LP6-01 · Data operations](../../labs/lp6-01-redis-data-ops/README.md) |
| 2 | Mensajería de eventos (pub/sub y Streams) | [06-2-redis-messaging.md](06-2-redis-messaging.md) | [LP6-02 · Pub/sub](../../labs/lp6-02-redis-pubsub/README.md) |
| 3 | Almacenamiento vectorial (RediSearch) | [06-3-redis-vector-storage.md](06-3-redis-vector-storage.md) | [LP6-03 · Semantic search](../../labs/lp6-03-redis-vector/README.md) |

## Cuándo Redis y cuándo la base de datos (LP4/LP5)
| | Cosmos DB / PostgreSQL | Azure Managed Redis |
|---|---|---|
| Papel | Fuente de verdad, persistente | Datos calientes en memoria (la presentación habla de acceso sub-milisegundo) |
| Datos típicos | Documentos, historial, tablas | Sesión, caché de resultados del modelo, contadores, colas, embeddings consultados a menudo |
| Vectores | `VectorDistance` / `pgvector` | RediSearch (FLAT y HNSW) |
| Mensajería | No es su función | Pub/sub y Streams |

Idea de la presentación: el chatbot necesita perfiles, sesiones y resultados de modelo rápidos; la caché descarga la base de datos y mantiene la latencia bajo concurrencia alta.

## Lo nuevo para un perfil SysOps/K8s
El servicio (tiers, red, escalado, métricas al 75 %) es terreno conocido. Lo nuevo es **el código**: elegir el tipo de dato, el patrón de caché (cache-aside, TTL, invalidación), el patrón de mensajería (broadcast frente a cola) y el esquema del índice vectorial. Y la autenticación: los labs usan **Entra ID** (`DefaultAzureCredential` + `redis-entraid`), sin clave de acceso en el código.
