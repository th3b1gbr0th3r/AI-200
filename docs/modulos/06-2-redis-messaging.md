# LP6 · Módulo 2 · Mensajería de eventos con Azure Managed Redis

Volver al [índice de LP6](06-redis.md). Lab: [LP6-02 · Pub/sub](../../labs/lp6-02-redis-pubsub/README.md).

Redis ofrece dos patrones, disponibles en Azure Cache for Redis y en Azure Managed Redis: **pub/sub** (difusión) y **Streams** (cola duradera).

| | Pub/sub (broadcast) | Streams (coordinado) |
|---|---|---|
| Entrega | A **todos** los suscriptores activos | A **un** consumidor del grupo |
| Garantías | *At-most-once*, fire-and-forget, sin persistencia ni confirmación | Mensajes persistentes, ack, reintento, historial |
| Si nadie escucha | El mensaje se pierde | Queda en el stream |
| Uso | Invalidar caché en varias instancias de la API, notificaciones, cambios de configuración | Colas de tareas, pipelines de procesamiento |
| Analogía K8s | un *watch* / evento: quien no está conectado, no lo ve | una cola de trabajo (Job con workers) con *visibility timeout* |

## Pub/sub
```python
redis_client.publish('ai:models:updated', f'{model_name}:{version}')   # devuelve nº de suscriptores
pubsub = redis_client.pubsub(); pubsub.subscribe('ai:models:updated')
for msg in pubsub.listen():
    if msg['type'] == 'message': clear_model_cache(msg['data'])
pubsub.psubscribe('ai:*')            # por patrón
```
- Canales con nombre; los suscriptores eligen canales o patrones (`psubscribe`, mensajes de tipo `pmessage`).
- Una conexión que se suscribe queda dedicada a escuchar (por eso el lab usa un hilo en segundo plano).

## Streams
```python
task_id = redis.xadd('ai:inference:queue', {'prompt': '...', 'model': 'gpt-4'})
msgs = redis.xreadgroup('workers', 'worker-1', {'ai:inference:queue': '>'}, count=5, block=5000)
redis.xack('ai:inference:queue', 'workers', task_id)
```
| Comando | Función |
|---|---|
| `XADD` | añade una tarea |
| `XREADGROUP` | un consumidor del grupo pide tareas |
| `XACK` | marca la tarea como completada |
| `XPENDING` / `XCLAIM` | detectan tareas atascadas y las reasignan a otro worker |

Las tareas sin `XACK` quedan *pendientes* y se pueden reintentar. Arquitectura híbrida: Streams para el procesamiento y pub/sub para avisar del estado.

## Qué hace el lab
Solo cubre **pub/sub** (app Flask con canales `orders:created`, `orders:shipped`, `inventory:alerts`, `notifications`): suscripción por canal y por patrón, difusión y desuscripción. **Streams se ve en la teoría, no en el lab.**

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros: confirmarlas con el profesor.
1. Diferencia clave pub/sub frente a Streams → **A.** pub/sub solo llega a suscriptores activos; Streams persiste para grupos de consumidores.
2. Pipeline con varios servicios y reintento automático → **A. Streams con consumer groups**.
