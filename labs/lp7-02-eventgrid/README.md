# Lab LP7-02 · Publish and receive events with Azure Event Grid (plataforma: lab de LP7M02)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/02-eventgrid-publish-receive-events.html (fuente Markdown: `instructions/integrate-services/02-eventgrid-publish-receive-events.md`; el código de este README está copiado literal de ahí).
- **Estado: PREPARADO, sin ejecutar** (17/11/2026). Las salidas marcadas «(pendiente de ejecutar; salida esperada según la guía)» se sustituirán por las reales al hacer el lab.
- **Notas teóricas:** [07-2-eventgrid.md](../../docs/modulos/07-2-eventgrid.md). Índice: [07-servicios-backend.md](../../docs/modulos/07-servicios-backend.md).
- **Duración:** ~30 min. **Origen MIT** de `azdeploy.py`, `client/` y `moderation_events.json`: ver [`../NOTICE.md`](../NOTICE.md). Zip original: `event-grid-python.zip` (de `https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/event-grid-python.zip`; ya descomprimido aquí).
- Lab anterior: [LP7-01](../lp7-01-servicebus/README.md).

Cada paso tiene: **por qué → comando → salida → qué mirar → comprobación (y qué hacer si no coincide)**.

## Qué se construye
```
azdeploy.py 1 → RG + Event Grid namespace egns-exercise-<hash> (Standard, capacity 1)
                + topic moderation-events (CloudEventSchemaV1_0, retención 1 día)
azdeploy.py 2 → 3 suscripciones PULL (cola): sub-flagged (tipo ContentFlagged),
                sub-approved (tipo ContentApproved), sub-all-events (sin filtro)
                bloqueo 60 s, max delivery 10, TTL 1 día (P1D)
azdeploy.py 3 → roles EventGrid Data Sender + EventGrid Data Receiver sobre el namespace
azdeploy.py 4 → .env con RESOURCE_GROUP, NAMESPACE_NAME, EVENTGRID_TOPIC_NAME, EVENTGRID_ENDPOINT
azdeploy.py 5 → comprobación de estado · 6 → salir
client/event_grid_functions.py → 3 funciones que pegas tú (publish, receive/ack, inspect/reject)
client/app.py → Flask en http://localhost:5000
```
- Es el **namespace** de Event Grid (con *pull delivery*), no un topic clásico con webhook: tu app **pide** los eventos (`receive`) y los confirma (`acknowledge`) o rechaza (`reject`). Analogía K8s: parecido a un consumidor que hace *poll* con ack en una cola, pero con filtros de evento en la suscripción.
- Auth sin claves: `DefaultAzureCredential` + roles de datos.
- Coste: namespace **Standard** (unidades de throughput por hora + operaciones; importe exacto no verificado: ver precios de Event Grid). Se borra al final.
- `client/requirements.txt`: `azure-identity==1.21.0`, `azure-eventgrid==4.21.0`, `flask==3.1.1`.
- Los 5 eventos salen de `client/moderation_events.json` (2 `ContentFlagged`, 2 `ContentApproved`, 1 `ReviewEscalated`).

## Antes de empezar (confirmar con el alumno)
| Qué | Valor | Nota |
|---|---|---|
| Resource group | `rg-ai200-lp7-eg` (o el de la plataforma) | Se borra entero al final |
| Región | La de la plataforma; si no, `westeurope` | Si el namespace no está disponible en la región, probar otra *(no verificado)* |
| Extensión `az` | `eventgrid` | Obligatoria para `az eventgrid namespace …` |

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp7-02-eventgrid
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
**Por qué:** salir del `.venv` anterior y que `az`/Python confíen en el proxy (en cada terminal nueva).

✅ **Comprobación:** `ls` muestra `azdeploy.py` y `client`.

## Paso 1 · `az login`, proveedor y extensión
**Por qué:** el proveedor `Microsoft.EventGrid` debe estar registrado y el script usa `az eventgrid namespace …`, que vive en una extensión.
```bash
az logout
az login
az provider register --namespace Microsoft.EventGrid
az extension add --name eventgrid --yes
az provider show -n Microsoft.EventGrid --query registrationState -o tsv
az extension list --query "[?name=='eventgrid'].version" -o tsv
```
Salida: *(pendiente de ejecutar; salida esperada: `Registered` y la versión de la extensión)*

**Qué mirar:** la extensión se descarga de internet: si el proxy lo impide, `az extension add` falla con error de red/certificado (con `REQUESTS_CA_BUNDLE` exportado no debería).

✅ **Comprobación:** `Registered` y una versión. Si sale `Registering`, repite en un minuto; si la lista de extensiones está vacía, repite `az extension add`.

## Paso 2 · Valores en `azdeploy.py`
```bash
sed -i 's/<your-resource-group-name>/rg-ai200-lp7-eg/; s/<your-azure-region>/westeurope/' azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
Salida: *(pendiente de ejecutar; salida esperada: `rg = "rg-ai200-lp7-eg"` y `location = "westeurope"`)*

✅ **Comprobación:** ninguna línea con `<your-…>`. Si queda alguna, edítala a mano.

## Paso 3 · Namespace, topic, suscripciones y roles (`azdeploy.py` 1, 2, 3)
```bash
python3 azdeploy.py      # menú → 1 → 2 → 3
```
Salida: *(pendiente de ejecutar; salida esperada según el script: creación del namespace y del topic `moderation-events`, de las tres suscripciones y de los roles `EventGrid Data Sender` y `EventGrid Data Receiver`)*

**Qué mirar:** las suscripciones deben crearse **después** del topic (la guía: si no llegan eventos, relanzar la opción 2). El filtro de `sub-flagged` es `includedEventTypes:['com.contoso.ai.ContentFlagged']`.

✅ **Comprobación (solo lectura, con `az`):**
```bash
RG=rg-ai200-lp7-eg
NS=$(az eventgrid namespace list -g $RG --query "[0].name" -o tsv); echo $NS
az eventgrid namespace show -g $RG -n $NS --query "{estado:provisioningState, sku:sku.name}" -o tsv
az eventgrid namespace topic show -g $RG --namespace-name $NS -n moderation-events --query "{estado:provisioningState, esquema:inputSchema}" -o tsv
az eventgrid namespace topic event-subscription list -g $RG --namespace-name $NS --topic-name moderation-events --query "[].name" -o tsv
az role assignment list --scope $(az eventgrid namespace show -g $RG -n $NS --query id -o tsv) --query "[].roleDefinitionName" -o tsv
```
Esperado: `Succeeded Standard`; `Succeeded CloudEventSchemaV1_0`; `sub-flagged`, `sub-approved`, `sub-all-events`; y los dos roles. Si faltan suscripciones, relanza la opción 2; si faltan roles, la 3 (los roles tardan en propagarse).

## Paso 4 · Variables de entorno (opción 4) y estado (opción 5)
**Por qué:** la opción 4 escribe `.env` con las variables que lee `event_grid_functions.py`; la 5 verifica todo desde el propio script.
```bash
python3 azdeploy.py      # menú → 4 → Enter → 5 → Enter → 6
source .env
for v in EVENTGRID_ENDPOINT EVENTGRID_TOPIC_NAME RESOURCE_GROUP NAMESPACE_NAME; do [ -n "${!v:-}" ] && echo "$v definida"; done
```
Salida: *(pendiente de ejecutar; salida esperada: cuatro líneas `… definida`)*

**Qué mirar:** el `.env` no lleva claves (endpoint y nombres). El bucle solo imprime el **nombre** de las variables acordadas, no su valor.

✅ **Comprobación:** las cuatro definidas. Si falta alguna, repite la opción 4 y `source .env`.

## Paso 5 · Pegar el código en `client/event_grid_functions.py`
**Por qué:** el starter trae los clientes `get_publisher_client()` y `get_consumer_client()`; tú escribes las tres funciones entre sus marcadores (espacios, no tabs). Código literal de la guía.

### 5.1 Publicar eventos (`# BEGIN PUBLISH EVENTS FUNCTION`)
**Por qué:** carga `moderation_events.json`, añade `id` único y marca de tiempo UTC, construye `CloudEvent` y los publica con **un** `send()`.
```python
def publish_moderation_events():
    """Publish content moderation events to the Event Grid namespace topic."""
    client = get_publisher_client()
    results = []

    # Load event definitions from the JSON file. Each entry contains the
    # CloudEvent envelope fields (type, source, subject) and the data
    # payload that mirrors a realistic AI content moderation pipeline.
    json_path = os.path.join(os.path.dirname(__file__), "moderation_events.json")
    with open(json_path, "r") as f:
        event_definitions = json.load(f)

    # Build CloudEvent objects from the definitions, adding a unique id
    # and a current UTC timestamp to each event at publish time.
    events = []
    for defn in event_definitions:
        defn["data"]["timestamp"] = datetime.now(timezone.utc).isoformat()
        events.append(
            CloudEvent(
                type=defn["type"],
                source=defn["source"],
                subject=defn["subject"],
                data=defn["data"],
                id=str(uuid.uuid4())
            )
        )

    # send() publishes all events to the Event Grid namespace topic in a
    # single request. Event Grid then evaluates each subscription's
    # filters and routes matching events to the configured subscriptions.
    client.send(events)

    for event in events:
        results.append({
            "content_id": event.data["contentId"],
            "event_type": event.type.split(".")[-1],
            "category": event.data["category"],
            "confidence": event.data["confidence"],
            "status": "published"
        })

    return results
```

### 5.2 Recibir y confirmar (`# BEGIN CHECK DELIVERY FUNCTION`)
**Por qué:** `receive()` devuelve `ReceiveDetails` (evento + `lock_token`); `acknowledge()` lo elimina de la suscripción; si no, se reentrega al caducar el bloqueo (60 s).
```python
def check_filtered_delivery():
    """Receive and acknowledge events from each subscription to verify filtering."""
    flagged = []
    approved = []
    all_events = []

    # Receive from the sub-flagged subscription, which only delivers
    # events where the event type is com.contoso.ai.ContentFlagged.
    # receive() returns a list of ReceiveDetails, each containing
    # the CloudEvent and a lock token for acknowledgment.
    consumer = get_consumer_client(SUB_FLAGGED)
    details = consumer.receive(max_events=10, max_wait_time=10)
    tokens = []
    for detail in details:
        event = detail.event
        flagged.append({
            "content_id": event.data.get("contentId"),
            "category": event.data.get("category"),
            "severity": event.data.get("severity"),
            "confidence": event.data.get("confidence")
        })
        tokens.append(detail.broker_properties.lock_token)
    # acknowledge() removes the events from the subscription so they
    # are not delivered again on the next receive call.
    if tokens:
        consumer.acknowledge(lock_tokens=tokens)

    # Receive from the sub-approved subscription, which only delivers
    # events where the event type is com.contoso.ai.ContentApproved.
    consumer = get_consumer_client(SUB_APPROVED)
    details = consumer.receive(max_events=10, max_wait_time=10)
    tokens = []
    for detail in details:
        event = detail.event
        approved.append({
            "content_id": event.data.get("contentId"),
            "category": event.data.get("category"),
            "severity": event.data.get("severity"),
            "confidence": event.data.get("confidence")
        })
        tokens.append(detail.broker_properties.lock_token)
    if tokens:
        consumer.acknowledge(lock_tokens=tokens)

    # Receive from the sub-all-events subscription, which has no filter
    # and delivers every event published to the topic (audit log).
    consumer = get_consumer_client(SUB_ALL)
    details = consumer.receive(max_events=10, max_wait_time=10)
    tokens = []
    for detail in details:
        event = detail.event
        all_events.append({
            "content_id": event.data.get("contentId"),
            "event_type": event.data.get("modelName", "unknown"),
            "category": event.data.get("category"),
            "confidence": event.data.get("confidence")
        })
        tokens.append(detail.broker_properties.lock_token)
    if tokens:
        consumer.acknowledge(lock_tokens=tokens)

    return {
        "flagged": flagged,
        "approved": approved,
        "all_events": all_events
    }
```

### 5.3 Inspeccionar y rechazar (`# BEGIN INSPECT AND REJECT FUNCTION`)
**Por qué:** muestra el sobre completo del CloudEvent y `delivery_count`; `reject()` indica que no se puede procesar (≠ `acknowledge`).
```python
def inspect_and_reject():
    """Publish one event, receive it, inspect the CloudEvent envelope, then reject it."""
    publisher = get_publisher_client()

    # Publish a single test event so there is always something to inspect,
    # regardless of whether the student already acknowledged earlier events.
    test_event = CloudEvent(
        type="com.contoso.ai.ContentFlagged",
        source="/services/content-moderation",
        subject="/content/text/test-inspect",
        data={
            "contentId": "test-inspect",
            "contentType": "text",
            "modelName": "text-moderator-v2",
            "modelVersion": "2.4.0",
            "confidence": 0.76,
            "category": "misinformation",
            "severity": "medium",
            "reviewRequired": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        id=str(uuid.uuid4())
    )
    publisher.send([test_event])

    # Receive from the sub-flagged subscription to pick up the test event.
    consumer = get_consumer_client(SUB_FLAGGED)
    details = consumer.receive(max_events=1, max_wait_time=10)

    if not details:
        return None

    detail = details[0]
    event = detail.event
    lock_token = detail.broker_properties.lock_token
    delivery_count = detail.broker_properties.delivery_count

    # Capture the full CloudEvent envelope before rejecting.
    result = {
        "specversion": "1.0",
        "type": event.type,
        "source": event.source,
        "subject": event.subject,
        "id": event.id,
        "time": str(event.time) if event.time else "",
        "data": event.data,
        "delivery_count": delivery_count,
        "action": "rejected"
    }

    # reject() tells Event Grid this event cannot be processed. The event
    # is moved to the dead-letter location if configured, or discarded
    # if max delivery count has been reached.
    consumer.reject(lock_tokens=[lock_token])

    return result
```

✅ **Comprobación (solo lectura):**
```bash
grep -c "^def " client/event_grid_functions.py
python3 -I -m py_compile client/event_grid_functions.py && echo "sintaxis OK"
```
Esperado: `5` (2 `get_*_client` + 3) y `sintaxis OK`. Si hay `IndentationError`, vuelve a pegar y alinea con Tab.

## Paso 6 · Entorno Python
```bash
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list | grep -iE "azure-eventgrid|azure-identity|flask"
```
Salida: *(pendiente de ejecutar; salida esperada: `azure-eventgrid 4.21.0`, `azure-identity 1.21.0`, `Flask 3.1.1`)*

**Qué mirar:** error de certificado en `pip` → `PIP_CERT=/etc/ssl/certs/ca-certificates.crt pip install -r requirements.txt`.

✅ **Comprobación:** las tres versiones. Si falta una, repite `pip install`.

## Paso 7 · Ejecutar la app
```bash
python app.py
```
Abre `http://localhost:5000`. A diferencia de Service Bus, aquí el tráfico va por **HTTPS (443)** al endpoint del namespace, así que el proxy no debería ser un problema; si hay inspección TLS, `azure-core` usa `requests`, que respeta `REQUESTS_CA_BUNDLE` *(no verificado en este equipo)*.

| Botón | Resultado esperado (guía) |
|---|---|
| Publish Moderation Events | 5 eventos publicados (2 flagged, 2 approved, 1 escalated review) |
| Receive & Acknowledge Events | `sub-flagged`: 2 (violence, hate-speech); `sub-approved`: 2 (`safe`); `sub-all-events`: 5 (incluido `ReviewEscalated`, que solo aparece aquí) |
| Receive & Acknowledge otra vez | 0 eventos (ya confirmados) hasta publicar más |
| Inspect & Reject Event | Publica uno, lo recibe de `sub-flagged`, muestra el CloudEvent con `delivery_count` y lo rechaza |

Salida: *(pendiente de ejecutar; salida esperada según la guía)*

**Qué mirar:** `ReviewEscalated` no coincide con ningún filtro de tipo, por eso solo llega a la suscripción de auditoría. Es la respuesta al test 2 del módulo en versión práctica (filtro de tipo; el test pregunta por filtro avanzado sobre `data.status`).

✅ **Comprobación independiente:** nada que consultar con `az` para el contenido de los eventos (el plano de datos solo se lee con el SDK); la comprobación es el resultado de cada botón. Si «Receive» devuelve 0 en la primera pulsación: confirma que las suscripciones existen (paso 3) y que se crearon después del topic; relanza la opción 2 si no. Errores `403`/`Unauthorized` → roles sin propagar (2-5 min) o sesión de `az` distinta.

## Cleanup (obligatorio al acabar)
Para Flask con `Ctrl+C`, `deactivate` y:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-lp7-eg --no-wait --yes
az group exists --name rg-ai200-lp7-eg
```
Salida: *(pendiente de ejecutar; salida esperada: `true` mientras se borra y `false` al terminar)*

✅ **Comprobación:** repite `az group exists --name rg-ai200-lp7-eg` hasta `false`. Si a los 15 min sigue `true`: `az group show -n rg-ai200-lp7-eg --query properties.provisioningState -o tsv`; `Failed` → relanza el `delete`. Si caducan las credenciales antes de verificar, documentar «no verificado».

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| *(vacío: se rellena al ejecutar el lab)* | | |
