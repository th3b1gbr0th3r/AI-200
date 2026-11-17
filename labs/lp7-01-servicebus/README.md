# Lab LP7-01 · Process messages with Azure Service Bus (plataforma: lab de LP7M01)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/01-svcbus-process-messages.html (fuente Markdown: `instructions/integrate-services/01-svcbus-process-messages.md`; el código de este README está copiado literal de ahí).
- **Estado: PREPARADO, sin ejecutar** (17/11/2026). Todas las salidas marcadas «(pendiente de ejecutar; salida esperada según la guía)» se sustituirán por las reales al hacer el lab (previsto mié 18 o jue 19/11 por la mañana; reserva sáb 21/11).
- **Notas teóricas:** [07-1-servicebus.md](../../docs/modulos/07-1-servicebus.md). Índice del bloque: [07-servicios-backend.md](../../docs/modulos/07-servicios-backend.md).
- **Duración:** ~30 min. **Origen MIT** de `azdeploy.py` y `client/`: ver [`../NOTICE.md`](../NOTICE.md). Zip original: `service-bus-python.zip` (descargado de `https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/service-bus-python.zip`; ya descomprimido en esta carpeta).

Cada paso tiene: **por qué → comando → salida → qué mirar → comprobación (y qué hacer si no coincide)**. Los IDs de suscripción se sustituirán por `<sub-id>` al sanear.

## Qué se construye
Una app Flask (`client/app.py`) que muestra patrones de Service Bus con un caso de inferencia de IA:

```
azdeploy.py 1 → RG + namespace sbns-exercise-<hash> (Standard)
azdeploy.py 2 → cola inference-requests (max delivery 5, dead-letter al caducar)
                tema inference-results + suscripciones notifications (todo)
                y high-priority (regla SQL priority = 'high', se borra $Default)
azdeploy.py 3 → rol "Azure Service Bus Data Owner" para tu usuario sobre el namespace
azdeploy.py 5 → .env / .env.ps1 con SERVICE_BUS_FQDN
client/service_bus_functions.py → 4 funciones que pegas tú (send, process, DLQ, tema)
client/app.py → Flask en http://localhost:5000
```
- Autenticación **sin claves**: `DefaultAzureCredential` (en local usa la sesión de `az login`) + rol RBAC de datos. Analogía K8s: un `ServiceAccount` con un `RoleBinding` en lugar de un `Secret` con la cadena de conexión.
- Coste: namespace **Standard** (cuota base por horas + operaciones; el importe exacto no está verificado: mira la página de precios de Service Bus). El lab dura ~30 min; **se borra al final**.
- Dependencias del cliente (`client/requirements.txt`): `azure-identity==1.21.0`, `azure-servicebus==7.14.1`, `flask==3.1.1`.

## Antes de empezar (confirmar con el alumno)
| Qué | Valor | Nota |
|---|---|---|
| Suscripción | La del lab (usuario temporal) | Comprobar con `az account show` (paso 1) |
| Resource group | `rg-ai200-lp7-sb` (o el que imponga la plataforma) | Se borra entero al final |
| Región | La que indique la plataforma (en LP5 fue `centralus`); si no, `westeurope` | Si falla por política/cuota, cambiar y repetir |
| Python | 3.12+ (el equipo tiene 3.12.3) | La guía pide 3.12 o superior |

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp7-01-servicebus
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
**Por qué:** `deactivate` sale de cualquier `.venv` anterior; `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa (hay que exportarlo en **cada** terminal nueva).

✅ **Comprobación:** `pwd` termina en `labs/lp7-01-servicebus` y `ls` muestra `azdeploy.py` y `client`. Si no, estás en otra carpeta.

## Paso 1 · `az login` con el usuario del lab
```bash
az logout
az login
az account show --query "{sub:name, user:user.name}" -o table
```
Salida: *(pendiente de ejecutar; salida esperada según la guía: selección de suscripción y tabla con la suscripción del lab)*

**Qué mirar:** la suscripción debe ser la del lab, no la de empresa.

✅ **Comprobación:** si sale la cuenta de empresa, repite `az logout` y `az login`.

## Paso 2 · Registrar el proveedor de Service Bus
**Por qué:** si el proveedor no está registrado en la suscripción, `az servicebus namespace create` falla.
```bash
az provider register --namespace Microsoft.ServiceBus
az provider show -n Microsoft.ServiceBus --query registrationState -o tsv
```
Salida: *(pendiente de ejecutar; salida esperada según la guía: sin salida en el `register`; `Registered` en el `show`)*

✅ **Comprobación:** `Registered`. Si sale `Registering`, repite el `show` en un minuto.

## Paso 3 · Poner región y grupo en `azdeploy.py`
**Por qué:** el script tiene dos marcadores y la guía dice que no se cambie nada más.
```bash
sed -i 's/<your-resource-group-name>/rg-ai200-lp7-sb/; s/<your-azure-region>/westeurope/' azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
Salida: *(pendiente de ejecutar; salida esperada: `5:rg = "rg-ai200-lp7-sb"  # Resource Group name` y `6:location = "westeurope"   # Azure region for the resources`)*

**Qué mirar:** sustituye los valores por los que dé la plataforma.

✅ **Comprobación:** si algún valor sigue con `<your-…>`, el `sed` no lo encontró: edítalo a mano.

## Paso 4 · Crear namespace, entidades y rol (`azdeploy.py` 1, 2, 3)
**Por qué:** el plano de control (namespace, cola, tema, suscripciones, filtro) y el rol de datos los crea el script con `az servicebus …` y `az role assignment create`.
```bash
python3 azdeploy.py      # menú → 1 → 2 → 3
```
Salida: *(pendiente de ejecutar; salida esperada según el script)*
```text
Service Bus namespace created: sbns-exercise-<hash>
Queue created: inference-requests
Topic created: inference-results
Subscription created: notifications
Subscription created: high-priority
SQL filter created: high-priority-filter (priority = 'high')
Azure Service Bus Data Owner role assigned
```
**Qué mirar:** el script borra la regla `$Default` de `high-priority` antes de crear el filtro SQL (si no, recibiría todos los mensajes). El sufijo del namespace es un hash de tu object id.

✅ **Comprobación (solo lectura, con `az`):**
```bash
RG=rg-ai200-lp7-sb
NS=$(az servicebus namespace list -g $RG --query "[0].name" -o tsv); echo $NS
az servicebus namespace show -g $RG -n $NS --query "{estado:provisioningState, sku:sku.name}" -o tsv
az servicebus queue show -g $RG --namespace-name $NS -n inference-requests --query "{maxDelivery:maxDeliveryCount, dlqOnExpiry:deadLetteringOnMessageExpiration}" -o tsv
az servicebus topic subscription list -g $RG --namespace-name $NS --topic-name inference-results --query "[].name" -o tsv
az servicebus topic subscription rule list -g $RG --namespace-name $NS --topic-name inference-results --subscription-name high-priority --query "[].{regla:name, sql:filter.sqlExpression}" -o tsv
```
Esperado: `Succeeded Standard`; `5 True`; `notifications` y `high-priority`; una sola regla `high-priority-filter priority = 'high'`. Si el namespace sigue `Activating`, espera y repite; si falta algo, relanza la opción 2 (es idempotente: dice «already exists»).

## Paso 5 · Verificar el rol y obtener la conexión (opciones 4 y 5)
**Por qué:** sin el rol, el SDK falla con `Unauthorized` aunque todo esté creado; la opción 5 escribe `.env` con el FQDN.
```bash
python3 azdeploy.py      # menú → 4 → Enter → 5 → Enter → 6
source .env
[ -n "${SERVICE_BUS_FQDN:-}" ] && echo "FQDN definido"; echo "$SERVICE_BUS_FQDN"
```
Salida: *(pendiente de ejecutar; salida esperada: estado `Succeeded`, SKU `Standard`, entidades `Created`, rol asignado; `FQDN definido` y `sbns-exercise-<hash>.servicebus.windows.net`)*

**Qué mirar:** `.env` solo contiene `SERVICE_BUS_FQDN` (no hay clave), por eso se puede versionar.

✅ **Comprobación del rol con `az`:**
```bash
az role assignment list --scope $(az servicebus namespace show -g rg-ai200-lp7-sb -n $NS --query id -o tsv) --query "[].roleDefinitionName" -o tsv
```
Esperado: `Azure Service Bus Data Owner`. Si sale vacío, relanza la opción 3. El rol puede tardar unos minutos en propagarse.

**Anticipar el proxy (puerto AMQP):** el SDK habla AMQP sobre TCP **5671**, no HTTPS. Comprobación de red antes de seguir:
```bash
timeout 8 bash -c "</dev/tcp/${SERVICE_BUS_FQDN}/5671" && echo "5671 abierto" || echo "5671 bloqueado"
```
Si sale «bloqueado», usa AMQP sobre WebSockets (puerto 443): en `client/service_bus_functions.py`, `get_client()`, añade `transport_type=TransportType.AmqpOverWebsocket` al `ServiceBusClient(...)` e importa `TransportType` de `azure.servicebus`. *(Parámetro del SDK `azure-servicebus`; **no verificado** en este equipo ni en este lab. Si el proxy intercepta TLS, puede hacer falta pasar el bundle de CA; consultar la documentación del SDK.)* Si ni así conecta, ejecutar la app desde la máquina de la plataforma del lab.

## Paso 6 · Pegar el código en `client/service_bus_functions.py`
**Por qué:** el starter trae `get_client()` y los marcadores `BEGIN/END`; las cuatro funciones las escribes tú. Pega cada bloque **entre sus marcadores** con sangría de espacios (no tabs). Código literal de la guía.

El fichero se abre con `code client/service_bus_functions.py` (o desde VS Code).

### 6.1 Enviar mensajes (`# BEGIN SEND MESSAGES FUNCTION`)
**Por qué:** muestra `message_id` (duplicados), `correlation_id` (trazabilidad) y `application_properties` (enrutado); el tercer mensaje es JSON roto a propósito.
```python
def send_messages():
    """Send messages to the queue including one malformed message."""
    # Create a ServiceBusClient using DefaultAzureCredential
    client = get_client()
    results = []

    with client:
        # Open a sender bound to the queue
        with client.get_queue_sender(QUEUE_NAME) as sender:
            # Valid message 1 — message_id enables deduplication,
            # correlation_id links related messages for tracking,
            # and application_properties carry custom metadata for routing
            msg1 = ServiceBusMessage(
                body=json.dumps({
                    "prompt": "Extract parties and effective date.",
                    "model": "gpt-4o",
                    "document_id": "doc-001"
                }),
                content_type="application/json",
                message_id=str(uuid.uuid4()),
                correlation_id="req-doc-001",
                application_properties={"priority": "standard", "document_type": "contract"}
            )
            sender.send_messages(msg1)
            results.append({
                "correlation_id": msg1.correlation_id,
                "type": "valid",
                "status": "sent"
            })

            # Valid message 2 — priority is set to "high" so it matches
            # the SQL filter on the high-priority topic subscription
            msg2 = ServiceBusMessage(
                body=json.dumps({
                    "prompt": "Summarize the key terms.",
                    "model": "gpt-4o",
                    "document_id": "doc-002"
                }),
                content_type="application/json",
                message_id=str(uuid.uuid4()),
                correlation_id="req-doc-002",
                application_properties={"priority": "high", "document_type": "contract"}
            )
            sender.send_messages(msg2)
            results.append({
                "correlation_id": msg2.correlation_id,
                "type": "valid",
                "status": "sent"
            })

            # Invalid message — intentionally malformed JSON body to
            # demonstrate dead-lettering during processing
            msg3 = ServiceBusMessage(
                body="not valid json: [broken",
                content_type="application/json",
                message_id=str(uuid.uuid4()),
                correlation_id="req-doc-003",
                application_properties={"priority": "standard"}
            )
            sender.send_messages(msg3)
            results.append({
                "correlation_id": msg3.correlation_id,
                "type": "malformed",
                "status": "sent"
            })

    return results
```

### 6.2 Procesar con peek-lock (`# BEGIN PROCESS MESSAGES FUNCTION`)
**Por qué:** `complete_message` si el JSON es válido; `dead_letter_message(reason, error_description)` si no. Es la liquidación de la presentación.
```python
def process_messages():
    """Receive and process messages from the queue using peek-lock."""
    client = get_client()
    results = []

    with client:
        # Peek-lock is the default receive mode — the message is locked
        # but stays in the queue until explicitly completed or dead-lettered.
        # max_wait_time sets how long the receiver waits for new messages.
        with client.get_queue_receiver(
            queue_name=QUEUE_NAME,
            max_wait_time=5
        ) as receiver:
            for msg in receiver:
                try:
                    payload = json.loads(str(msg))
                    # Complete removes the message from the queue
                    receiver.complete_message(msg)
                    results.append({
                        "correlation_id": msg.correlation_id,
                        "document_id": payload.get("document_id"),
                        "model": payload.get("model"),
                        "prompt": payload.get("prompt", "")[:50],
                        "status": "completed"
                    })
                except json.JSONDecodeError:
                    # Dead-letter moves the message to the dead-letter
                    # sub-queue with a reason and description for diagnostics
                    receiver.dead_letter_message(
                        msg,
                        reason="MalformedPayload",
                        error_description="Message body is not valid JSON"
                    )
                    results.append({
                        "correlation_id": msg.correlation_id,
                        "document_id": None,
                        "model": None,
                        "prompt": str(msg)[:50],
                        "status": "dead-lettered"
                    })

    return results
```

### 6.3 Inspeccionar la DLQ (`# BEGIN INSPECT DLQ FUNCTION`)
**Por qué:** la DLQ es una subcola (`ServiceBusSubQueue.DEAD_LETTER`) con `dead_letter_reason`, `dead_letter_error_description` y `delivery_count`.
```python
def inspect_dead_letter_queue():
    """Inspect and remove messages from the dead-letter queue."""
    client = get_client()
    results = []

    with client:
        # ServiceBusSubQueue.DEAD_LETTER targets the dead-letter sub-queue,
        # which holds messages that failed processing
        with client.get_queue_receiver(
            queue_name=QUEUE_NAME,
            sub_queue=ServiceBusSubQueue.DEAD_LETTER,
            max_wait_time=5
        ) as dlq_receiver:
            for msg in dlq_receiver:
                # Dead-lettered messages include diagnostic properties:
                # dead_letter_reason, dead_letter_error_description,
                # and delivery_count (number of delivery attempts)
                results.append({
                    "message_id": msg.message_id,
                    "correlation_id": msg.correlation_id,
                    "dead_letter_reason": msg.dead_letter_reason,
                    "error_description": msg.dead_letter_error_description,
                    "delivery_count": msg.delivery_count,
                    "body": str(msg)[:100]
                })
                # Complete removes the message from the dead-letter queue
                dlq_receiver.complete_message(msg)

    return results
```

### 6.4 Tema con suscripciones filtradas (`# BEGIN TOPIC MESSAGING FUNCTION`)
**Por qué:** demuestra el fan-out y el filtro SQL: `notifications` recibe los 5, `high-priority` solo los `high`. Las propiedades pueden llegar como `bytes` por la codificación AMQP.
```python
def topic_messaging():
    """Send messages to a topic and receive from filtered subscriptions."""
    client = get_client()
    sent = []
    notifications = []
    high_priority = []

    with client:
        # get_topic_sender opens a sender bound to a topic instead of a queue.
        # Each message is broadcast to all matching subscriptions.
        with client.get_topic_sender(TOPIC_NAME) as sender:
            for i, priority in enumerate(["standard", "high", "standard", "high", "low"]):
                result = {
                    "document_id": f"doc-{i+1:03d}",
                    "status": "completed",
                    "confidence": 0.95
                }
                # The "priority" application property is what the SQL
                # filter on the high-priority subscription evaluates
                msg = ServiceBusMessage(
                    body=json.dumps(result),
                    content_type="application/json",
                    message_id=str(uuid.uuid4()),
                    application_properties={"priority": priority}
                )
                sender.send_messages(msg)
                sent.append({
                    "document_id": f"doc-{i+1:03d}",
                    "priority": priority
                })

        # Receive from the notifications subscription, which has no filter
        # and therefore receives all messages sent to the topic
        with client.get_subscription_receiver(
            topic_name=TOPIC_NAME,
            subscription_name="notifications",
            max_wait_time=5
        ) as receiver:
            for msg in receiver:
                body = json.loads(str(msg))
                # Application properties may arrive as bytes depending
                # on the AMQP encoding, so handle both str and bytes keys
                props = msg.application_properties or {}
                priority_val = props.get("priority") or props.get(b"priority", b"unknown")
                if isinstance(priority_val, bytes):
                    priority_val = priority_val.decode("utf-8")
                notifications.append({
                    "document_id": body["document_id"],
                    "priority": priority_val
                })
                receiver.complete_message(msg)

        # Receive from the high-priority subscription, which only delivers
        # messages where the SQL filter "priority = 'high'" matches
        with client.get_subscription_receiver(
            topic_name=TOPIC_NAME,
            subscription_name="high-priority",
            max_wait_time=5
        ) as receiver:
            for msg in receiver:
                body = json.loads(str(msg))
                props = msg.application_properties or {}
                priority_val = props.get("priority") or props.get(b"priority", b"unknown")
                if isinstance(priority_val, bytes):
                    priority_val = priority_val.decode("utf-8")
                high_priority.append({
                    "document_id": body["document_id"],
                    "priority": priority_val
                })
                receiver.complete_message(msg)

    return {
        "sent": sent,
        "notifications": notifications,
        "high_priority": high_priority
    }
```

✅ **Comprobación (solo lectura):**
```bash
grep -c "^def " client/service_bus_functions.py
python3 -I -m py_compile client/service_bus_functions.py && echo "sintaxis OK"
```
Esperado: `5` (`get_client` + las 4) y `sintaxis OK`. Si falla con `IndentationError`, el bloque está mal alineado: vuelve a pegarlo y selecciona + Tab.

## Paso 7 · Entorno Python
```bash
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list | grep -iE "azure-servicebus|azure-identity|flask"
```
Salida: *(pendiente de ejecutar; salida esperada: `azure-identity 1.21.0`, `azure-servicebus 7.14.1`, `Flask 3.1.1`)*

**Qué mirar:** si `pip` falla con error de certificado, el `REQUESTS_CA_BUNDLE` no cubre pip: usa `PIP_CERT=/etc/ssl/certs/ca-certificates.crt pip install -r requirements.txt` (variable acordada para este comando).

✅ **Comprobación:** las tres versiones anteriores. Si falta una, repite `pip install`.

## Paso 8 · Ejecutar la app y probar los cuatro patrones
```bash
python app.py
```
Abre `http://localhost:5000`.

| Botón | Resultado esperado (guía) | Qué demuestra |
|---|---|---|
| Send Messages | 3 enviados (2 `valid`, 1 `malformed`) con su correlation ID | Propiedades del mensaje |
| Process Messages | 2 `completed` y 1 `dead-lettered` (`MalformedPayload`) | Peek-lock y liquidación |
| Inspect Dead-Letter Queue | El mensaje con reason, error description y delivery count | DLQ |
| Send & Receive Topic Messages | 5 enviados; `notifications` = 5; `high-priority` = 2 (doc-002 y doc-004) | Fan-out y filtro SQL |

Salida: *(pendiente de ejecutar; salida esperada según la guía)*

✅ **Comprobación independiente con `az` (conteos de la cola), tras «Send Messages» y antes de «Process Messages»:**
```bash
az servicebus queue show -g rg-ai200-lp7-sb --namespace-name $NS -n inference-requests --query "countDetails" -o json
```
Esperado: `activeMessageCount: 3`; tras procesar `0` y `deadLetterMessageCount: 1`; tras inspeccionar la DLQ, `0`. *(Los contadores pueden tardar unos segundos en actualizarse; no verificado.)*

**Si falla:** `Unauthorized`/`401` → rol sin propagar (espera 2-5 min) o sesión de `az` distinta; `ServiceBusConnectionError`/timeout → red (paso 5); `SERVICE_BUS_FQDN environment variable must be set` → falta `source .env` en esta terminal.

## Paso 9 · Preguntas para el profesor y repaso
- ¿Qué pasaría si `process_messages` usara `abandon_message` en vez de `dead_letter_message` ante JSON roto? (acaba igualmente en la DLQ tras 5 entregas).
- Test del módulo 1: ver [07-servicios-backend.md](../../docs/modulos/07-servicios-backend.md#preguntas-de-repaso-test-de-la-presentación).

## Cleanup (obligatorio al acabar)
Para Flask con `Ctrl+C`, `deactivate` y:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-lp7-sb --no-wait --yes
az group exists --name rg-ai200-lp7-sb
```
Salida: *(pendiente de ejecutar; salida esperada: `true` mientras se borra y `false` al terminar)*

✅ **Comprobación:** repite `az group exists --name rg-ai200-lp7-sb` hasta `false`. Si pasados 15 minutos sigue `true`: `az group show -n rg-ai200-lp7-sb --query properties.provisioningState -o tsv`; si sale `Failed`, relanza el `delete`. Las asignaciones de rol van dentro del namespace, así que desaparecen con él. Si las credenciales caducan antes de verificar, documentarlo como «no verificado».

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| *(vacío: se rellena al ejecutar el lab)* | | |
