# Claude Code: CLAUDE.md, skills, agentes y hooks

Nota de apoyo del día 6 (10/11/2026), surgida al hablar de guardar la memoria de los agentes en PostgreSQL (LP5). Genérica, sin datos de ninguna empresa.

## Las cuatro piezas
| Pieza | Qué es | Quién decide usarla | Analogía K8s | En este repo |
|---|---|---|---|---|
| `CLAUDE.md` / memoria | Instrucciones siempre en contexto | El modelo las lee e intenta cumplirlas | Documentación del equipo | "Primero `az`", "nunca subir `github.mb`" |
| Skill | Paquete de instrucciones (y scripts) que se carga cuando hace falta | El modelo, o el usuario con `/nombre` | Runbook para una tarea | `/aprender`, `/quiz-lab` |
| Agente (rol) | Claude especialista con su prompt, herramientas y modelo | El modelo delega o se le pide | Pod con su ServiceAccount | `oscar` |
| Hook | Comando que se ejecuta **siempre** en un evento | Claude Code, sin el modelo | Admission webhook, `postStart`/`preStop` | Ninguno todavía |

**Clave:** `CLAUDE.md`, skills y agentes son peticiones al modelo (pueden olvidarse); el hook es determinista.

## `settings.json`
Configuración de Claude Code (qué puede hacer y qué se ejecuta): `permissions`, `env`, `hooks`…
- `~/.claude/settings.json`: personal, todos los proyectos.
- `.claude/settings.json`: del proyecto, versionado y compartido.
- `.claude/settings.local.json`: del proyecto, solo local (en `.gitignore`).

## Eventos de hook más útiles
| Evento | Cuándo | Uso típico |
|---|---|---|
| `PreToolUse` | Antes de una herramienta; con código de salida 2 la **bloquea** | Impedir comandos peligrosos |
| `PostToolUse` | Después de la herramienta | Auditoría, formatear código |
| `UserPromptSubmit` | Al enviar un mensaje | Añadir contexto, filtrar datos |
| `SessionStart` / `SessionEnd` | Inicio / fin de sesión | Cargar contexto / guardar resumen |
| `Stop` | El agente termina de responder | Comprobaciones finales |

El script recibe por stdin un JSON con `session_id`, `tool_name`, `tool_input` (y `tool_response` en `PostToolUse`).

## Ejemplo: convertir una regla de memoria en garantía
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash|Read|Edit|Write",
        "hooks": [ { "type": "command",
                     "command": "grep -q 'kube-prod' && { echo 'Bloqueado: ~/.kube-prod está prohibido' >&2; exit 2; } || exit 0" } ] }
    ]
  }
}
```
Propuesta, **no aplicada** en `.claude/settings.json`.

## Aplicación: memoria de agentes en PostgreSQL
| Necesidad | Mecanismo | Quién lo dispara |
|---|---|---|
| Consultar y guardar aprendizajes | Servidor MCP propio (`search_learnings`, `save_learning` con `ON CONFLICT`) registrado en `.mcp.json` | El modelo |
| Auditar qué hizo el agente | Hook `PostToolUse` → `INSERT INTO agent_actions` (saneado; si la BD falla, no bloquear) | Claude Code, siempre |
| Retomar tareas largas | Tool `save_checkpoint` (patrón `task_checkpoints` del lab LP5-01) | El modelo |
| Revisión humana | `status = 'proposed'` → un responsable aprueba | Persona |

- MCP propio con tools concretas, no un MCP genérico con SQL libre.
- Cada usuario conecta con su propio usuario de PostgreSQL (`${PGUSER}` en `.mcp.json`, contraseña en `~/.pgpass`, nunca en el repo) → `author DEFAULT current_user` fiable.
- pgvector: útil cuando hay cientos o miles de aprendizajes redactados con palabras distintas; mejor búsqueda híbrida (vector + full-text con RRF), porque en infraestructura abundan los literales (códigos de error, nombres de recursos). Sin índice al principio; HNSW cuando crezca (inserciones sueltas).
- pgvector es libre pero no viene en el núcleo: `CREATE EXTENSION vector;` (imagen `pgvector/pgvector`, o `azure.extensions` en Azure Flexible Server).

## De lab a producción: memoria para un grupo de agentes de un departamento de sistemas
> **Trabajo pendiente tras el curso** (decidido el 10/11/2026): esta documentación se pasará a un agente en la nube del repo de agentes del departamento, y esta será una de sus primeras tareas. Diseño genérico, sin datos de ninguna empresa. Base: lab [LP5-01](../labs/lp5-01-pg-agent-backend/README.md) (esquema y funciones reutilizables).

### 1. Qué es cada tabla del lab en sistemas
| Tabla del lab | En el departamento | Ejemplo |
|---|---|---|
| `conversations` | Sesión de trabajo: quién, qué agente, sobre qué sistema | `user_id = <usuario>`, `metadata = {"agent": "aks-ops", "ticket": "INC-1234", "cluster": "prod"}` |
| `messages` (role `tool`) | Registro de acciones: cada comando o cambio del agente | `{"tool": "Bash", "cmd": "az aks upgrade ...", "exit": 0}` |
| `task_checkpoints` | Operaciones largas que se pueden retomar | `task_name = 'upgrade-aks-prod'`, `checkpoint_data = {"step": 3, "nodepools_done": ["system"]}` |
| *(nueva)* `learnings` | Aprendizajes compartidos (lo que hoy guarda una skill en el repo) | `"ImagePullBackOff → falta AcrPull en la identidad del kubelet"` |

`task_checkpoints` es lo de más valor: si un upgrade se corta en el paso 3, otro compañero abre Claude, el agente lee el checkpoint y sigue en el 4; `ON CONFLICT` evita duplicados.

### 2. Cómo lo usa el repo de agentes
```
repo-agentes/
├── .mcp.json                     → registra el servidor "agent-memory" (lo tienen todos al clonar)
├── .claude/
│   ├── settings.json             → hook PostToolUse → registra acciones en messages (automático)
│   ├── agents/*.md               → "al empezar: search_learnings + get_task_state"
│   └── skills/aprendizaje/       → la skill actual llama a save_learning en vez de escribir ficheros
└── mcp/agent_memory/
    ├── server.py                 → FastMCP: expone las funciones como tools
    └── agent_tools.py            → el del lab + learnings, con ConnectionPool
```
| Necesidad | Mecanismo | Funciones del lab |
|---|---|---|
| Retomar una tarea | Tool MCP (lo decide el modelo) | `save_task_state`, `get_task_state` |
| Consultar y guardar conocimiento | Tool MCP | `create_conversation` + nuevas `search_learnings` / `save_learning` |
| Auditar todo lo ejecutado | Hook (siempre, sin el modelo) | `store_message` con `role = 'tool'` |

### 3. Cambios al código del lab para producción
| Visto en el lab | Cambio |
|---|---|
| ≈ 2,4 s por operación (token y conexión nuevos cada vez) | `ConnectionPool` de psycopg creado al arrancar el MCP y token cacheado hasta que caduque |
| `user_id` lo pasa el código (`"user_123"`) | `DEFAULT current_user`: lo pone la BD con la identidad real |
| `conversation_id` admite NULL en `task_checkpoints` | `NOT NULL`, para que el `UNIQUE` del upsert funcione siempre |
| Índices redundantes (`idx_conversations_session_id`, `idx_task_checkpoints_conversation_id`) | Quitarlos |
| Mensajes para siempre | Retención (p. ej. 90 días); los `learnings` aprobados se quedan |
| Contenido tal cual | Sanear en el hook antes del `INSERT` (tokens, contraseñas, salidas enormes) |
| Firewall `AllowAll` | Acceso privado (VNet o Kubernetes) publicado con Netskope Private Access |

### 4. Identidad y seguridad
- **Azure Flexible Server:** rol de PostgreSQL ligado a un grupo de Entra; cada persona entra con su token (`DefaultAzureCredential` + su `az login`), sin contraseña compartida.
- **PostgreSQL propio en Kubernetes (CloudNativePG):** sin Entra; usuario por persona (`~/.pgpass`) o certificados de cliente.
- **Mínimo privilegio:** el rol de los agentes solo `INSERT`/`SELECT` (y `UPDATE` en `task_checkpoints`); sin `DELETE` ni DDL, para que nadie pueda borrar la auditoría.

### 5. Orden de implantación
1. Auditoría (hook + `messages`): valor desde el día 1, no depende del modelo.
2. Checkpoints para 1-2 operaciones largas típicas (upgrades, migraciones).
3. Migrar los aprendizajes de la skill a `learnings` (`proposed` → `approved` sustituye a la revisión por PR).
4. pgvector cuando haya cientos de aprendizajes (búsqueda híbrida; sin índice al principio, HNSW después).

### 6. Búsqueda semántica de aprendizajes con PostgreSQL propio (lab LP5-02 aplicado)
Decisión del alumno (10/11/2026): preferencia por **PostgreSQL local/autogestionado** (Kubernetes) en lugar de Azure Flexible Server. Base: [lab LP5-02](../labs/lp5-02-pg-vector-search/README.md).

| Lab 13 (Azure) | Equivalente en PostgreSQL propio |
|---|---|
| Opción 2: `azure.extensions = vector` | No existe: basta con que la imagen traiga pgvector (`pgvector/pgvector:pg16`, o imagen de CloudNativePG con pgvector; comprobar con `pg_available_extensions`) |
| `CREATE EXTENSION IF NOT EXISTS vector;` | Igual (en CloudNativePG, declarativo en `postInitApplicationSQL` o con el recurso `Database`) |
| Embeddings precalculados en JSON | Hay que generarlos: modelo **local** (p. ej. `all-MiniLM-L6-v2`, 384 dim, con `sentence-transformers` u Ollama) para que el texto de infraestructura no salga de la empresa; o un modelo en la nube si la política lo permite |
| `products.embedding vector(330)` | `learnings.embedding vector(384)` (las dimensiones las fija el modelo) |
| Índice HNSW `vector_cosine_ops` | Igual, pero solo cuando haya volumen (cientos/miles); antes, escaneo exacto |
| `ORDER BY embedding <=> %s LIMIT 5` | Igual, con `WHERE status = 'approved'` y umbral de distancia |
| Autenticación Entra + token | Usuario por persona (`~/.pgpass`) o certificado de cliente; acceso publicado con Netskope Private Access |

Esquema y consultas (sobre la tabla `learnings` del apartado 2):
```sql
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE learnings ADD COLUMN embedding vector(384);          -- NULL hasta calcularlo
ALTER TABLE learnings ADD COLUMN search_tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('spanish', title || ' ' || body)) STORED;
CREATE INDEX learnings_tsv_idx ON learnings USING gin (search_tsv);
-- Más adelante, con volumen:
-- CREATE INDEX learnings_embedding_idx ON learnings USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Búsqueda semántica (lab 13): los 5 más parecidos al síntoma, con umbral
SELECT slug, title, embedding <=> %(q_emb)s AS distance
FROM learnings
WHERE status = 'approved' AND embedding IS NOT NULL
  AND embedding <=> %(q_emb)s < 0.5
ORDER BY distance
LIMIT 5;

-- Búsqueda híbrida con RRF (vector + texto; los literales como códigos de error los encuentra el texto)
WITH v AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY embedding <=> %(q_emb)s) AS r
  FROM learnings WHERE status = 'approved' AND embedding IS NOT NULL
  ORDER BY embedding <=> %(q_emb)s LIMIT 20
), t AS (
  SELECT id, ROW_NUMBER() OVER (ORDER BY ts_rank(search_tsv, q) DESC) AS r
  FROM learnings, plainto_tsquery('spanish', %(q_text)s) q
  WHERE status = 'approved' AND search_tsv @@ q
  LIMIT 20
)
SELECT l.slug, l.title,
       COALESCE(1.0/(60 + v.r), 0) + COALESCE(1.0/(60 + t.r), 0) AS rrf
FROM learnings l
LEFT JOIN v ON v.id = l.id
LEFT JOIN t ON t.id = l.id
WHERE v.id IS NOT NULL OR t.id IS NOT NULL
ORDER BY rrf DESC
LIMIT 5;
```
Flujo en el servidor MCP: `save_learning` guarda el texto y calcula el embedding con el modelo local (si falla, deja `embedding` en NULL y un proceso lo rellena después: patrón «columna stale» del módulo 2); `search_learnings` calcula el embedding de la pregunta y lanza la consulta híbrida.
