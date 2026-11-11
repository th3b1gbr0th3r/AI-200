# LP5 · Desarrollar soluciones de IA con Azure Database for PostgreSQL

Notas propias del día 6 (10/11/2026). Presentación del instructor: `docs/AI-200T00A-05_…pdf`; test: `docs/LP5 - Knowledge check.pdf`. Mismo problema que LP4 (memoria del agente + búsqueda vectorial para RAG), pero sobre una base de datos **relacional**.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Notas | Lab |
|---|---|---|---|
| 1 | Crear y consultar PostgreSQL (esquema, SQL, Python) | [05-1-postgresql-build-query.md](05-1-postgresql-build-query.md) | [LP5-01 · Agent tool backend](../../labs/lp5-01-pg-agent-backend/README.md) |
| 2 | Búsqueda vectorial con `pgvector` | [05-2-postgresql-vector-search.md](05-2-postgresql-vector-search.md) | [LP5-02 · Vector search](../../labs/lp5-02-pg-vector-search/README.md) (parcial) |
| 3 | Optimizar la búsqueda vectorial | [05-3-postgresql-optimize.md](05-3-postgresql-optimize.md) | [Guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html) |

## Cosmos DB (LP4) frente a PostgreSQL (LP5)
| | Cosmos DB | PostgreSQL |
|---|---|---|
| Modelo | Documentos JSON sin esquema fijo | Tablas con esquema + `JSONB` para lo flexible |
| Coste | Por operación (RU) | Por tamaño del servidor (vCores) y horas encendido |
| Escalado | Horizontal por partition key | Vertical primero; después réplicas de lectura (hasta 5) |
| Vectores | Integrado (`VectorDistance`, `flat`/`quantizedFlat`/`diskANN`) | Extensión `pgvector` (IVFFlat, HNSW) |
| Integridad | En la aplicación | En la BD: FK, `CHECK`, `UNIQUE` |
| Acceso sin claves | RBAC de datos de Cosmos | Admin/usuario de Entra + token como contraseña |

Idea de la presentación: con `pgvector` **no hace falta una base de datos vectorial aparte**; el embedding va en la misma fila que los datos.

## Lo nuevo para un perfil SysOps/K8s
Servidor, red, firewall, TLS y escalado son terreno conocido. Lo nuevo: **diseño del esquema y SQL propio de PostgreSQL** (`JSONB`, `ON CONFLICT`, `RETURNING`) y **elección del índice vectorial**.
