# LP7 · Módulo 1 · Colas y procesamiento de operaciones de IA con Azure Service Bus

Volver al [índice de LP7](07-servicios-backend.md). Lab: [LP7-01 · Service Bus](../../labs/lp7-01-servicebus/README.md). Fuente: presentación del módulo 1 (los datos sin enlace salen de ahí; si un límite importa, verificar en Microsoft Learn).

## Objetivos del módulo (presentación)
- Explicar cómo Service Bus desacopla componentes y cuándo aplicar *load leveling*, *competing consumers* y publish-subscribe.
- Elegir entre colas y temas con suscripciones.
- Estructurar mensajes para IA: serialización, payloads grandes, correlación.
- Procesar de forma fiable con peek-lock, gestionar mensajes venenosos y vigilar la dead-letter queue.

## El servicio
Broker de mensajes gestionado. Colas (punto a punto) y temas (publish-subscribe), AMQP 1.0, ordenación, detección de duplicados y transacciones.

| Nivel | Capacidad | Tamaño de mensaje |
|---|---|---|
| Standard | Compartida (el lab usa este) | 256 KB |
| Premium | Recursos dedicados | Hasta 100 MB por AMQP |

## Por qué mensajería en IA, y patrones (con analogía K8s)
La latencia de inferencia es impredecible: una llamada síncrona se bloquea bajo carga. La cola desacopla productores (APIs) de consumidores (procesadores del modelo).

| Patrón | Qué hace | Analogía |
|---|---|---|
| Load leveling | La cola absorbe picos; los procesadores consumen a ritmo estable | Cola delante de un Deployment con HPA/KEDA: los pods no se saturan |
| Competing consumers | Varios workers sobre una cola; cada mensaje se entrega a **uno** | Réplicas de un consumer group de Kafka/RabbitMQ |
| Desacoplo temporal | Productor y consumidor no tienen que estar a la vez | Un Job que arranca cuando hay trabajo pendiente |

## Colas frente a temas
| | Cola | Tema + suscripciones |
|---|---|---|
| Modelo | Punto a punto: un mensaje, un consumidor | Fan-out: copia a **cada** suscripción |
| Escalado | Competing consumers | Cada suscripción es una cola virtual independiente |
| Añadir consumidores | Compiten por lo mismo | Se añade una suscripción **sin tocar al productor** |
| Orden | Sesiones: FIFO por grupo de sesión (solo se cita para colas en la presentación) | - |

SDK Python: `client.get_queue_sender("requests")`, `get_queue_receiver(...)`, `get_topic_sender(...)`, `get_subscription_receiver(topic_name=..., subscription_name=...)`.

**Test 1 (propuesta A):** tres servicios independientes necesitan el mismo resultado: un **tema con tres suscripciones**. B (cola con consumidores) reparte, no copia; C obliga al productor a conocer a cada consumidor.

## Estructura del mensaje
- **Cuerpo:** payload serializado (JSON con prompt y parámetros).
- **Application properties:** metadatos propios para enrutar y filtrar (`priority`, `model_name`).
- **Propiedades del sistema:** `message_id` (detección de duplicados en la ventana), `correlation_id` (seguir la petición de extremo a extremo), `content_type`, `time_to_live` (caducar peticiones obsoletas).
- **Claim-check:** payloads grandes a Blob Storage; en el mensaje solo el URI. Vale con cualquier nivel.
- **Lotes:** `ServiceBusMessageBatch` agrupa envíos en una operación.

## Procesar de forma fiable
| Modo de recepción | Garantía |
|---|---|
| Receive-and-delete | Se borra al recibir: máximo rendimiento, **sin garantía** |
| **Peek-lock** (por defecto) | Se bloquea; el consumidor debe liquidarlo: **al menos una vez** |

Liquidación (*settlement*), lo equivalente a un `ack`/`nack`:
| Operación | Cuándo |
|---|---|
| `complete_message` | Éxito: sale de la cola |
| `abandon_message` | Error **transitorio**: suelta el bloqueo y se reentrega |
| `dead_letter_message(reason=…)` | Fallo **permanente** (p. ej. JSON mal formado) |
| `defer` | Se queda en la cola; se recupera luego por número de secuencia |

**Test 2 (propuesta A):** si el worker cae, el bloqueo caduca y el mensaje vuelve a estar disponible: **peek-lock**. Receive-and-delete lo habría perdido.

## Dead-letter queue (DLQ)
- Subcola automática en cada cola y suscripción.
- Recibe: mensajes caducados (si está activado), los que superan el *max delivery count* y los enviados explícitamente.
- Cada mensaje trae `dead_letter_reason` y `dead_letter_error_description`.
- Se lee con `sub_queue=ServiceBusSubQueue.DEAD_LETTER`.
- Vigilar su contador detecta despliegues rotos o entradas mal formadas.

## Gestión del bloqueo
Bloqueo por defecto: 1 minuto; máximo 5. `AutoLockRenewer` lo prolonga para inferencias largas. Alternativa: procesamiento en dos fases para operaciones muy largas.

## El lab en una línea
Cola `inference-requests` (max delivery 5), tema `inference-results` con suscripciones `notifications` (todo) y `high-priority` (filtro SQL `priority = 'high'`); app Flask que envía 3 mensajes (uno mal formado), los procesa, inspecciona la DLQ y prueba el tema.

## Errores comunes
| Síntoma | Causa |
|---|---|
| Mensaje que reaparece una y otra vez | No se liquidó (falta `complete`) o `abandon` ante un error permanente: acaba en la DLQ por *max delivery count* |
| `Unauthorized` al enviar con `DefaultAzureCredential` | Falta el rol de datos (Azure Service Bus Data Owner/Sender/Receiver) o aún no se ha propagado |
| La suscripción recibe todo | Queda la regla `$Default` junto al filtro SQL |
| Timeout de conexión en red corporativa | AMQP usa el puerto 5671; si el proxy lo bloquea, probar AMQP sobre WebSockets (443). Dato no incluido en la presentación: verificar en Microsoft Learn |

## Preguntas de repaso
Las 2 del test están en el [índice](07-servicios-backend.md#preguntas-de-repaso-test-de-la-presentación). Propias (con respuesta orientativa, a confirmar):
1. ¿Qué pasa con un mensaje cuyo `JSONDecodeError` se trata con `abandon`? Se reentrega hasta superar el max delivery count y acaba en la DLQ; lo correcto es `dead_letter` directo.
2. ¿Para qué sirve `correlation_id` frente a `message_id`? El primero enlaza todas las etapas de una petición; el segundo identifica el mensaje (duplicados).
3. Mensaje de 5 MB en nivel Standard: ¿cómo? Claim-check (blob + URI).
