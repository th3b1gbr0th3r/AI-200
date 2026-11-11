# LP5 · Módulo 1 · Crear y consultar Azure Database for PostgreSQL

Volver al [índice de LP5](05-postgresql.md). Lab: [LP5-01 · Agent tool backend](../../labs/lp5-01-pg-agent-backend/README.md).

## El servicio: Flexible Server
PostgreSQL gestionado y compatible con la edición comunitaria: Azure hace parches, backups (restauración a un punto, hasta 35 días) y alta disponibilidad. Cómputo y almacenamiento escalan por separado. Extensiones: `pgvector`, `pg_trgm`, `hstore`.

| Nivel | Uso | PgBouncer integrado |
|---|---|---|
| Burstable | Desarrollo/pruebas, carga intermitente (el lab: `Standard_B1ms`) | No |
| General Purpose | Producción, rendimiento estable | Sí |
| Memory Optimized | Datos grandes en memoria, analítica, índices vectoriales | Sí |

## Conexión segura (con analogía K8s)
| Aspecto | Opciones | Analogía |
|---|---|---|
| Autenticación | **Entra ID** (token, sin contraseña guardada) o nativa usuario/contraseña (en Key Vault) | token de ServiceAccount frente a Secret estático |
| TLS | 1.2+ obligatorio; en producción `sslmode=verify-full` (valida el certificado) | `--insecure-skip-tls-verify` = `sslmode=require` |
| Red | Pública con reglas de firewall, o privada con VNet | Service `LoadBalancer` con `loadBalancerSourceRanges` frente a interno |

Con Entra, la "contraseña" es un token de acceso (`az account get-access-token --resource-type oss-rdbms`, scope `https://ossrdbms-aad.database.windows.net/.default`) que caduca en ~1 h.

## Diseño del esquema
- `BIGSERIAL` para IDs internos autoincrementales; `UUID` para IDs expuestos fuera (`session_id`).
- `JSONB` para metadatos de estructura variable (**pregunta 1 del test**).
- `TIMESTAMPTZ` para todas las fechas.
- Restricciones en la BD: `NOT NULL`, `CHECK` (p. ej. `role IN ('user','assistant','system','tool')`), `UNIQUE`, claves foráneas con `ON DELETE CASCADE` o `RESTRICT`; claves primarias compuestas en tablas de unión.

## SQL propio de PostgreSQL
| Elemento | Para qué | Ejemplo |
|---|---|---|
| Operadores `JSONB` | `->` (JSON), `->>` (texto), `@>` (contiene), `?` (existe clave) | `metadata->>'source'` |
| `RETURNING` | Devolver lo insertado/actualizado en la misma consulta | `INSERT … RETURNING id` |
| `ON CONFLICT … DO UPDATE` | Upsert idempotente (como `kubectl apply`); **requiere `UNIQUE`** en esas columnas | `ON CONFLICT (user_id, key) DO UPDATE SET value = EXCLUDED.value` |
| Keyset pagination | Paginar por el último valor visto, no por `OFFSET` (lento en tablas grandes) | `WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT 20` |
| CTE / CTE recursiva | Consultas en varios pasos legibles / datos jerárquicos | `WITH … AS (…)` |

## Integración en Python (psycopg 3)
- Consultas parametrizadas con `%s` (evitan inyección SQL); gestores de contexto (`with`) para cerrar solos.
- **`ConnectionPool`**: una conexión nueva cuesta 50-200 ms (**pregunta 2 del test**: ni una conexión por mensaje ni una global).
- Timeouts y reintentos con backoff exponencial.
- Carga masiva: `executemany` para cientos de filas, `COPY` para más de 10.000.

## El lab en una línea
BD `agent_memory` con `conversations`, `messages` y `task_checkpoints`, y tres funciones (`create_conversation`, `get_conversation_history`, `save_task_state`) que serían las *tools* con las que el agente lee y escribe su memoria.

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros (la presentación no las trae): confirmarlas con el profesor.
1. Metadatos de estructura variable → **B. `JSONB`**.
2. Muchas conexiones cortas → **B. `ConnectionPool`**.
