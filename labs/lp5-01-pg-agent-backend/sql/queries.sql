-- Task 7 (plataforma) · Consultar el contexto del agente. Copia literal de la guía.
-- Ejecutar CONECTADO a agent_memory:  \i sql/queries.sql
\pset pager off

\echo '--- 1. Conversaciones de user_123'
SELECT id, session_id, started_at, metadata
FROM conversations
WHERE user_id = 'user_123'
ORDER BY started_at DESC;

\echo '--- 2. Últimos 10 mensajes de todas las conversaciones'
SELECT c.session_id, m.role, m.content, m.created_at
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
ORDER BY m.created_at DESC
LIMIT 10;

\echo '--- 3. Tareas completadas'
SELECT
    c.session_id,
    t.task_name,
    t.status,
    t.checkpoint_data,
    t.updated_at
FROM task_checkpoints t
JOIN conversations c ON t.conversation_id = c.id
WHERE t.status = 'completed';

\echo '--- 4. Mensajes por rol en cada conversación'
SELECT
    c.id AS conversation_id,
    m.role,
    COUNT(*) AS message_count
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, m.role
ORDER BY c.id, m.role;
