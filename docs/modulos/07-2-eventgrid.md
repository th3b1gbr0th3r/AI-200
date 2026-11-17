# LP7 · Módulo 2 · Flujos de IA dirigidos por eventos con Azure Event Grid

Volver al [índice de LP7](07-servicios-backend.md). Lab: [LP7-02 · Event Grid](../../labs/lp7-02-eventgrid/README.md). Fuente: presentación del módulo 2.

## Objetivos del módulo (presentación)
- Explicar cómo Event Grid habilita patrones dirigidos por eventos e identificar los componentes del enrutado.
- Diseñar eventos con el esquema CloudEvents, tipos propios y suscripciones con filtros.
- Configurar entrega y reintentos, y destinos de dead-letter.
- Publicar eventos personalizados con el SDK y la API REST.

## El servicio
Enrutado de eventos totalmente gestionado, con precio por evento, latencia inferior al segundo y millones de eventos por segundo. Entrega **push** (webhooks, Functions) y **pull** (el lab). Topics del sistema (eventos de servicios Azure) y personalizados (de tu aplicación). CloudEvents v1.0 nativo.

## Componentes (con analogía K8s)
| Componente | Qué es | Analogía |
|---|---|---|
| Evento | Notificación de un cambio de estado | Un `Event` de Kubernetes |
| Fuente | Quien emite | kubelet / controlador |
| Topic | Punto donde llegan los eventos | El bus (API server + watch) |
| Suscripción | Filtra y enruta a un handler | Un watcher con selector de campos |
| Handler | Functions, webhook, Service Bus, colas | El controlador que reacciona |

Beneficio para IA: reemplaza el *polling* por disparadores reactivos y aísla fallos y escalado entre etapas.

**Test 1 (propuesta A):** la inferencia es **tu aplicación** quien emite: **topic personalizado**. Un topic de sistema es para eventos de servicios Azure; Event Hubs es para flujos de telemetría, no para esto.

## Esquema CloudEvents v1.0
Estándar CNCF, recomendado en implementaciones nuevas. Obligatorios: `specversion`, `type`, `source`, `id`. `subject` permite filtrar por ruta jerárquica.

```json
{ "specversion": "1.0", "type": "com.contoso.ai.InferenceCompleted",
  "source": "/services/content-moderation", "id": "a1b2c3d4-e5f6-7890",
  "subject": "/pipelines/moderation/batch-42",
  "data": { "modelName": "content-classifier-v3", "resultLocation": "https://.../results.json", "status": "success" } }
```

## Tres niveles de filtrado
| Nivel | Flag/idea | Cuándo |
|---|---|---|
| Tipo | Coincidencia exacta del tipo (`--included-event-types`) | Separar `ContentFlagged` de `ContentApproved` (lo que hace el lab) |
| Asunto | Prefijo/sufijo de ruta (`--subject-begins-with`) | Por jerarquía (`/content/images/...`) |
| Avanzado | Operadores sobre campos de `data` (p. ej. `StringIn`) | Valores dentro del payload |

**Test 2 (propuesta A):** el estado vive en `data.status`, un campo del payload: **filtro avanzado `StringIn` sobre `data.status`**. El tipo y el asunto no miran dentro de `data`.

## Entrega y reintentos
- HTTP POST; éxito = 200-204 en menos de 30 s.
- **Al menos una vez**: los handlers deben ser **idempotentes**.
- Backoff exponencial: 10 s, 30 s, 1 min... hasta 24 h.
- Configurable: intentos máximos (1-30) y TTL del evento (1-1440 min).
- Dead-letter a **Blob Storage** para lo no entregable; batching de salida para alto rendimiento.
- En el lab (pull): bloqueo de recepción 60 s, max delivery 10, TTL 1 día; el consumidor llama `acknowledge` o `reject`.

## Publicar eventos
- Topic con esquema `cloudeventschemav1_0`; autenticar con Entra ID e identidad gestionada.
- SDK Python: `EventGridPublisherClient` + `CloudEvent`.
- Buen diseño: incluir correlation IDs, referenciar resultados por URL de storage (payload pequeño), publicar en hitos naturales del pipeline.

## Lab en una línea
Event Grid **namespace** con topic `moderation-events` y tres suscripciones pull (`sub-flagged`, `sub-approved`, `sub-all-events`); la app publica 5 eventos de moderación, los recibe por suscripción y rechaza uno.

## Event Grid frente a Service Bus (resumen)
Ver la tabla del [índice](07-servicios-backend.md#mensajes-frente-a-eventos-con-analogía-k8s).

## Errores comunes
| Síntoma | Causa |
|---|---|
| No llegan eventos | Suscripciones creadas antes que el topic (la guía: relanzar la opción 2) o rol de Receiver sin propagar |
| Un evento aparece solo en `sub-all-events` | Su tipo no coincide con ningún filtro (es lo esperado con `ReviewEscalated`) |
| Reentrega sin fin | No se hizo `acknowledge`/`reject`; el bloqueo caduca |

## Preguntas de repaso
Las 2 del test están en el [índice](07-servicios-backend.md#preguntas-de-repaso-test-de-la-presentación). Propias (orientativas, a confirmar):
1. ¿Por qué el handler debe ser idempotente? Porque la entrega es al menos una vez.
2. ¿Qué campos obligatorios tiene un CloudEvent? `specversion`, `type`, `source`, `id`.
3. ¿Dónde acaban los eventos no entregables? En un destino dead-letter de Blob Storage.
