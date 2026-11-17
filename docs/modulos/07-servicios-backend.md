# LP7 · Integrar servicios backend para soluciones de IA

Notas preparadas el 17/11/2026 a partir de la presentación del instructor (`docs/AI-200T00A-07_Integrate Backend Services for AI Solutions.pdf`) y del test (`docs/LP7 - Knowledge check.pdf`). La clase del 17/11 no se pudo seguir: se repite en solitario (ver el plan de recuperación en `sesiones/`). **Preparado, aún no practicado.**

Idea del bloque: una app de IA no es solo "llamar al modelo". La latencia de inferencia es impredecible, así que se **desacoplan** los componentes con mensajes (Service Bus), se **reacciona** a cambios con eventos (Event Grid) y se **ejecuta** el código sin servidores que gestionar (Functions).

## Agenda (3 módulos, 1 lab cada uno + 1 opcional)
| Módulo | Tema | Notas | Lab |
|---|---|---|---|
| 1 | Colas y procesamiento con Service Bus | [07-1-servicebus.md](07-1-servicebus.md) | [LP7-01 · Service Bus](../../labs/lp7-01-servicebus/README.md) |
| 2 | Flujos de eventos con Event Grid | [07-2-eventgrid.md](07-2-eventgrid.md) | [LP7-02 · Event Grid](../../labs/lp7-02-eventgrid/README.md) |
| 3 | Backends serverless con Azure Functions | [07-3-functions.md](07-3-functions.md) | [LP7-03 · Servidor MCP con Functions](../../labs/lp7-03-functions-mcp/README.md) |
| (opcional) | Durable Functions: flujo duradero de procesamiento de documentos | (sin notas) | [Guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/04-durable-functions-ai.html): ejercicio extra respecto a los 24 labs del curso; confirmar con el profesor si se hace |

## Mensajes frente a eventos (con analogía K8s)
| | Service Bus | Event Grid |
|---|---|---|
| Qué es | Broker de **mensajes** empresarial (colas y temas) | Servicio de **enrutado de eventos** |
| Un mensaje/evento es... | Una orden de trabajo que alguien **debe** procesar | Una notificación de que **algo ha pasado** |
| Entrega | Pull del consumidor con bloqueo (peek-lock) | Push (webhook, Functions...) o pull (el lab) |
| Protocolo | AMQP 1.0 | HTTP / CloudEvents v1.0 |
| Analogía K8s | Cola de trabajo que consumen los pods, tipo Kafka/RabbitMQ; KEDA escala por su longitud | Eventos de K8s / webhooks / `Event` + suscriptores que filtran |
| Preguntas del test | 1 y 2 de módulo 1 | 1 y 2 de módulo 2 |

Regla práctica de la presentación (preguntas de debate): una cola aporta valor cuando hay trabajo **largo o a ráfagas** o varios consumidores; si no, es complejidad añadida. Event Grid compensa cuando **crece el número de consumidores**; para uno o dos servicios conocidos, una llamada directa es más simple.

## Lo nuevo para un perfil SysOps/K8s
Hosting, escalado, red e identidad son terreno conocido. Lo nuevo es el **código**: liquidación de mensajes (`complete`/`abandon`/`dead_letter`), idempotencia ante entrega "al menos una vez", `CloudEvent` y filtros, y el modelo de **triggers y bindings** de Functions. Todo el lab autentica con `DefaultAzureCredential` (sin claves).

## Preguntas de repaso (test de la presentación)
> Respuestas razonadas por nosotros (la presentación no las trae): **a confirmar con el profesor**.

| # | Pregunta (resumen) | Respuesta propuesta |
|---|---|---|
| M1-1 | Tres servicios independientes reaccionan al mismo resultado: ¿qué entidad? | A. Tema con tres suscripciones |
| M1-2 | No perder la petición si el worker cae: ¿modo de recepción? | A. Peek-lock |
| M2-1 | Emitir eventos al terminar una clasificación: ¿tipo de topic? | A. Topic personalizado (custom) |
| M2-2 | Enrutar por `data.status`: ¿qué filtrado? | A. Filtro avanzado con `StringIn` sobre `data.status` |
| M3-1 | Reducir cold start manteniendo bajo el coste en reposo | A. Flex Consumption con instancias always-ready |
| M3-2 | Clave en Key Vault rotada sin redesplegar | A. Referencia a Key Vault con URI **sin versión** |

El razonamiento de cada una está en la nota de su módulo.

## Preguntas de debate (de la presentación)
1. ¿Cuándo mejora un backend de IA añadir una cola y cuándo solo añade complejidad?
2. ¿Qué eventos van por Event Grid y cuáles por llamada directa? ¿Cambia al crecer los consumidores?
3. En Flex Consumption con always-ready aún hay cold starts en picos: ¿cómo evaluar si compensa Premium y qué probar antes?
