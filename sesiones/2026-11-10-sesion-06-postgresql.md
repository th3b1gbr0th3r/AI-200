# Sesión 6 — 10/11/2026 · LP5 Azure Database for PostgreSQL

## Cómo seguir esta clase (hilo conductor)
**Idea del día:** el mismo problema que en Cosmos DB (memoria y búsqueda vectorial para un agente), pero con PostgreSQL: tablas relacionales, upsert idempotente y la extensión `pgvector`. Acceso solo con Entra: la «contraseña» es un token que caduca a la hora.

1. **Teoría LP5:** Flexible Server, autenticación con Entra, pgvector, HNSW frente a IVFFlat y optimización. → [índice LP5](../docs/modulos/05-postgresql.md) y notas [M1](../docs/modulos/05-1-postgresql-build-query.md), [M2](../docs/modulos/05-2-postgresql-vector-search.md) y [M3](../docs/modulos/05-3-postgresql-optimize.md).
2. **Lab 12 · Agent backend:** servidor solo Entra (pasos 3-6, con el primer intento fallido por la política de región), conexión con `psql` y token (8-9), esquema con `UNIQUE` y upsert (11), flujo del agente (12) y consultas de contexto (13). Por qué: el upsert es el `kubectl apply` de SQL. → [README del lab 12](../labs/lp5-01-pg-agent-backend/README.md) · [conversación](conversaciones/2026-11-10-sesion-06/01-lab12-pg-agent-backend.md).
3. **Lab 13 · Vector search:** habilitar `vector` en el servidor (paso 5) y en la base de datos (paso 8), índice HNSW y app Flask (9). La carga y la búsqueda (pasos 10-11) quedaron sin hacer. → [README del lab 13](../labs/lp5-02-pg-vector-search/README.md) · [conversación](conversaciones/2026-11-10-sesion-06/02-lab13-pg-vector-search.md).
4. **Limpieza** y **repaso:** [aprendizaje del día](../docs/aprendizajes.md).

---

Material: presentación `AI-200T00A-05` y knowledge check de LP5 (PDF en `docs/`, descargados de la carpeta de Drive del curso; metadatos de autor saneados en el LP5).

## Planning del día (enviado por el docente)
| Hora | Actividad |
|---|---|
| 18:00-18:20 | Test LP4 (6 preguntas) |
| 18:20-19:20 | LP5 (PostgreSQL), módulos 1, 2 y 3: Queries / Vector Search / Optimize (teoría) |
| 19:20-19:50 | Lab 12 · AI-200-LP05M01 · Build and query with Azure Database for PostgreSQL |
| 19:50-20:10 | Descanso |
| 20:10-21:50 | Lab 13 · AI-200-LP05M02 · Implement vector search y Lab 14 · AI-200-LP05M03 · Optimize performance, indexing, and scaling |
| 21:50-22:00 | Test LP5 (6 preguntas) |

Numeración de la plataforma: LP5 = labs 12-14 (carpetas: `lp5-01-pg-agent-backend` = lab 12, `lp5-02-*` = lab 13, `lp5-03-*` = lab 14).

## Qué se hizo
- Rama `dia-06-2026-11-10` y PDF del día en `docs/`.
- Notas del LP5 en `docs/modulos/`: índice `05-postgresql.md` y una por módulo (`05-1`, `05-2`, `05-3`), a partir de la presentación.
- **Lab 12 (LP5-01, agent tool backend) completado:** PostgreSQL Flexible Server `psql-agent-dc48980e` (`Standard_D2ds_v4`/`GeneralPurpose`, PG 16.15, solo Entra, `centralus`, RG `ai200rg`: valores obligatorios de la plataforma). Esquema `agent_memory` (3 tablas, upsert con `UNIQUE`), `test_workflow.py` correcto (mismo `checkpoint_id` tras el upsert; ≈ 2,4 s por operación sin pool) y 4 consultas de contexto. `psql` funciona en local: el 5432 no pasa por Netskope. Detalle en `labs/lp5-01-pg-agent-backend/`.
- **Cleanup lab 12:** `rg-ai200-pg-agent` (intento fallido en `eastus`) verificado `false`; `ai200rg` en `Deleting`, **no verificado** a `false`: al cerrar el lab, `az group exists` devolvió `No subscription found`.

- **Lab 13 (LP5-02, vector search) parcial:** servidor `psql-vector-acc85432` (suscripción `XLabs-245`), opción 2 `azure.extensions = vector`, esquema con pgvector 0.8.7 (`vector(330)`, índice HNSW `vector_cosine_ops`), `app.py` completado y Flask arrancado. Un corte de conexión con `mol-bastion` obligó a renovar el token y relanzar. La carga de productos y la búsqueda en la web no se hicieron: el alumno decidió cerrar (la parte de base de datos le está costando). Detalle en `labs/lp5-02-pg-vector-search/`.
- **Cleanup lab 13 verificado:** `ai200rg` = `false` a las 21:19 (suscripción `XLabs-245`).

## Decisiones
- Diseño genérico para llevar el backend del lab a un grupo de agentes de sistemas (MCP + hooks + checkpoints + learnings) guardado en `notas/claude-code-hooks-skills-agentes.md`.
- Los `.env` de LP5 no se versionan: `PGPASSWORD` lleva un token de acceso de Entra.

## Aprendizajes
Entrada completa en [`docs/aprendizajes.md`](../docs/aprendizajes.md) (2026-11-10).
- **Principal:** el upsert `INSERT … ON CONFLICT … DO UPDATE` es idempotente (como `kubectl apply`) y necesita un `UNIQUE` exacto; verificado con el mismo `checkpoint_id` tras actualizar.
- **Apoyo:** pgvector en dos planos (`azure.extensions` + `CREATE EXTENSION`), HNSW con `vector_cosine_ops`; token de Entra como contraseña y ≈ 2,4 s por operación sin pool; política del lab (`centralus`, `D2ds_v4`); el 5432 no pasa por Netskope.

## Pendientes
- **Tras el curso:** pasar la documentación a un agente en la nube del repo de agentes del departamento; primera tarea: memoria de agentes en PostgreSQL (diseño en `notas/claude-code-hooks-skills-agentes.md`, sección «De lab a producción»).
- Lab 13: opcional, repetir la carga y la búsqueda («Find Similar») si se quiere ver `<=>` funcionando.
- Lab 14 (LP5-03, optimize).
- Test LP4 y test LP5 (`docs/LP5 - Knowledge check.pdf`); confirmar con el profesor las respuestas de repaso marcadas en `docs/modulos/05-*.md`.
- Cleanup verificado del lab 14.

## Conversación con Claude Code
Exportación saneada, dividida por tramos ([índice](conversaciones/2026-11-10-sesion-06/README.md)):
- [Inicio: documentación del día](conversaciones/2026-11-10-sesion-06/00-inicio.md)
- [Lab 12 (LP5-01): agent tool backend](conversaciones/2026-11-10-sesion-06/01-lab12-pg-agent-backend.md), con el desvío sobre hooks, skills y memoria de agentes en PostgreSQL
- [Lab 13 (LP5-02): vector search](conversaciones/2026-11-10-sesion-06/02-lab13-pg-vector-search.md)
- [Cierre: commit, push y PR](conversaciones/2026-11-10-sesion-06/03-cierre.md)

Además, tres subagentes que leyeron las guías oficiales de LP5-01 y LP5-02 (enlazados en el índice). Se han sustituido el correo, los GUID, el usuario y el TAP del lab, la cuenta de GitHub de empresa y los nombres de persona.
