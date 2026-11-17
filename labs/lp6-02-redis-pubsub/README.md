# Lab LP6-02 · Publish and subscribe to events in Azure Managed Redis

- **Estado: PREPARADO, sin ejecutar.** Redactado el 17/11/2026 a partir de la guía oficial y del `azdeploy.py` del starter. Todas las salidas están marcadas «(pendiente de ejecutar; salida esperada según la guía)».
- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/02-amr-pub-sub.html (fuente Markdown: `instructions/azure-managed-redis/02-amr-pub-sub.md`).
- **Teoría:** [06-2-redis-messaging.md](../../docs/modulos/06-2-redis-messaging.md). Índice: [06-redis.md](../../docs/modulos/06-redis.md).
- **Starter ya descargado y descomprimido aquí:** `amr-pub-sub-python.zip` → `azdeploy.py` y `client/` (`app.py`, `pubsub_functions.py`, `requirements.txt`, `templates/`, `static/`). Origen MIT: [`../NOTICE.md`](../NOTICE.md). **Nada se ha ejecutado.**
- Duración según la guía: ~30 min (más 5-10 min de despliegue). La guía pide la extensión `redisenterprise` 2.75.0 o superior.
- Lab anterior: [LP6-01](../lp6-01-redis-data-ops/README.md).

Cada paso tiene: **por qué → comando → salida esperada → qué mirar → comprobación (y qué hacer si no coincide)**.

## Qué se construye
Una app Flask (`client/app.py`, **no se edita**) que publica eventos y gestiona suscripciones con **pub/sub**. Solo hay que completar `client/pubsub_functions.py`. **Streams no forma parte de este lab** (solo está en la teoría).

```
azdeploy.py 1 → RG + clúster amr-exercise-<hash> (Balanced_B0, acceso público)
azdeploy.py 2 → base de datos (NoCluster, AllKeysLRU, puerto 10000) + acceso Entra + .env con REDIS_HOST
azdeploy.py 3 → estado
client/app.py → http://localhost:5000: publicar, suscribirse a canal/patrón, broadcast
```
Canales de la demo (`AVAILABLE_CHANNELS`): `orders:created`, `orders:shipped`, `inventory:alerts`, `notifications`. Qué crea el script (leído, no ejecutado): igual que en LP6-01, con el menú reordenado (2 = base de datos y acceso, 3 = estado). `_preflight` exige `client/app.py` junto al script.

Analogía K8s: pub/sub es como un *watch*: quien no está conectado cuando ocurre el evento no lo recibe (*at-most-once*, sin persistencia).

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp6-02-redis-pubsub
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
**Por qué:** `deactivate` sale del `.venv` de otro lab. `REQUESTS_CA_BUNDLE` hace que `az` y Python confíen en el certificado del proxy de empresa; hay que exportarlo **en cada terminal nueva**.

**Comprobación:** `[ -n "${REQUESTS_CA_BUNDLE:-}" ] && echo definida` debe imprimir `definida`. Si no, repite el `export`.

## Paso 1 · `az login` con el usuario del lab
```bash
az logout
az login
```
**Por qué:** cada lab de la plataforma trae su propio usuario temporal y suscripción. `azdeploy.py` consulta `az ad signed-in-user show` y **sale si no hay sesión**; además el nombre de la caché (`amr-exercise-<hash>`) sale de un hash de tu *object id*.

Salida (pendiente de ejecutar; salida esperada según la guía): selección de suscripción y tenant del lab.

**Qué mirar:** que la suscripción sea la del lab, no la de empresa.

**Comprobación:**
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Debe salir la suscripción y el usuario del lab. Si sale la cuenta de empresa, repite `az logout` y `az login`.

## Paso 2 · Registrar el proveedor e instalar la extensión `redisenterprise`
```bash
az provider register --namespace Microsoft.Cache
az extension add --upgrade --name redisenterprise
```
**Por qué:** Azure Managed Redis vive en `Microsoft.Cache` y se gestiona con `az redisenterprise …` (extensión de la CLI, no incluida de serie; la guía pide una versión reciente, 2.75.0 o superior en los labs 2 y 3). Es lo que `azdeploy.py` ejecuta por debajo.

**Qué mirar:** si `az extension add` falla con error de certificado, falta el `REQUESTS_CA_BUNDLE` del paso 0.

**Comprobación:**
```bash
az provider show -n Microsoft.Cache --query registrationState -o tsv
az extension list --query "[?name=='redisenterprise'].version" -o tsv
```
Esperado: `Registered` y un número de versión. Si el proveedor sale `Registering`, repite el `show` al cabo de un minuto.

## Paso 3 · Poner el resource group y la región en `azdeploy.py`
```bash
RG=rg-ai200-lp6-02
sed -i "s/<your-resource-group-name>/$RG/; s/<your-azure-region>/eastus2/" azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
**Por qué:** solo se editan esas dos variables. Si la plataforma del lab impone un grupo o una región, usa los suyos. `eastus2` es una de las regiones que el propio script sugiere si falta capacidad (`eastus2`, `australiaeast`, `canadacentral`); no está verificado que sea la más barata ni la más cercana.

**Comprobación:** el `grep` debe mostrar `rg = "rg-ai200-lp6-02"` y `location = "eastus2"`. Si siguen apareciendo `<your-…>`, el `sed` no encontró el texto: edita el fichero a mano.

## Paso 4 · Crear el clúster (`azdeploy.py` → opción 1)
**Por qué:** 5-10 minutos; se lanza primero. **Genera coste**: confirmar suscripción, región y limpieza antes.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este lab:
```text
1. Create Azure Managed Redis resource
2. Create database and configure access
3. Check deployment status
4. Exit
```
Salida (pendiente de ejecutar; salida esperada según la guía): `Azure Managed Redis resource created successfully: amr-exercise-<hash>`.

**Qué mirar:** si falla por capacidad, la guía indica cambiar `location` (`eastus2`, `australiaeast`, `canadacentral`) y repetir la opción 1.

**Comprobación** (otra terminal, con el paso 0 hecho):
```bash
az redisenterprise list -g rg-ai200-lp6-02 --query "[].{name:name, state:provisioningState, sku:sku.name}" -o table
```
Esperado: `amr-exercise-<hash>`, `Balanced_B0`, `Creating` y luego `Succeeded`. Si sigue `Creating` más de ~15 minutos o sale `Failed`, repite la opción 1 (el script borra el fallido y reintenta).

## Paso 5 · Completar `client/pubsub_functions.py`
**Por qué:** seis secciones vacías. Código **literal de la guía**. Espacios, no tabuladores. Cada sección va en su marcador `BEGIN/END`; no tocar `app.py`.

### 5.1 Conexión (`CONNECTION`, sin sangrar)
```python
def get_client() -> redis.Redis:
    """Create a Redis client for Azure Managed Redis using Microsoft Entra ID."""
    redis_host = os.environ.get("REDIS_HOST")

    if not redis_host:
        raise ValueError("REDIS_HOST environment variable must be set")

    # create_from_default_azure_credential uses DefaultAzureCredential to
    # acquire a Microsoft Entra token for Redis. The credential provider
    # refreshes the token automatically in the background so long-lived
    # connections (like the pub/sub listener) stay authenticated.
    credential_provider = create_from_default_azure_credential(
        ("https://redis.azure.com/.default",),
    )

    return redis.Redis(
        host=redis_host,
        port=10000,
        ssl=True,
        decode_responses=True,
        credential_provider=credential_provider,
        socket_timeout=30,
        socket_connect_timeout=30,
    )
```
**Qué mirar:** el cliente usa Entra ID (sin clave); el `credential_provider` renueva el token en segundo plano, importante porque el *listener* mantiene la conexión abierta mucho rato. `decode_responses=True` → los mensajes llegan como `str`.

### 5.2 Publicar (`PUBLISH MESSAGE`, sin sangrar)
```python
def publish_order_created(r: redis.Redis) -> dict:
    """Publish an order created event to the 'orders:created' channel."""
    order_data = {
        "event": "order_created",
        "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer": "Jane Doe",
        "total": 129.99,
        "timestamp": datetime.now().isoformat(),
    }
    channel = "orders:created"

    # publish() sends the message to every subscriber of the channel and
    # returns the number of subscribers that received it.
    subscribers = r.publish(channel, json.dumps(order_data))

    return {"channel": channel, "subscribers": subscribers, "message": order_data}
```
**Qué mirar:** `publish()` devuelve el **número de suscriptores** que recibieron el mensaje: es el dato que la app muestra para confirmar la entrega. Con 0, el mensaje se perdió (pub/sub no guarda nada).

### 5.3 Difusión a todos los canales (`BROADCAST`, sin sangrar)
```python
def broadcast_to_all(r: redis.Redis) -> dict:
    """Broadcast the same message to every channel using publish() in a loop."""
    announcement = {
        "event": "system_announcement",
        "message": "System maintenance scheduled for 2 AM",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
    }
    message = json.dumps(announcement)

    results = []
    total_subscribers = 0
    for channel in AVAILABLE_CHANNELS:
        # Send the same message to multiple channels for multi-channel delivery.
        count = r.publish(channel, message)
        total_subscribers += count
        results.append({"channel": channel, "subscribers": count})

    return {
        "channels": results,
        "total_subscribers": total_subscribers,
        "message": announcement,
    }
```

### 5.4 Formatear mensajes recibidos (`MESSAGE FORMATTING`, sin sangrar)
```python
def format_message(message: dict) -> dict:
    """Parse a pub/sub message and extract relevant fields for display."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    channel = message.get("channel", "unknown")
    pattern = message.get("pattern")

    try:
        data = json.loads(message["data"])
    except (json.JSONDecodeError, TypeError):
        # Non-JSON payloads are returned as-is under a "raw" key.
        return {
            "timestamp": timestamp,
            "channel": channel,
            "pattern": pattern,
            "event": None,
            "details": {"raw": message.get("data")},
        }

    # Pull out the fields that the demo events include so the UI can
    # display a clean summary of each message.
    field_names = [
        "order_id", "customer", "total", "tracking_number",
        "product_name", "current_stock", "message",
    ]
    details = {name: data[name] for name in field_names if name in data}

    return {
        "timestamp": timestamp,
        "channel": channel,
        "pattern": pattern,
        "event": data.get("event", "unknown"),
        "details": details,
    }
```

### 5.5 Escucha en segundo plano (`MESSAGE LISTENER`, **dentro de la clase `PubSubManager`, sangrado 4 espacios**)
```python
def listen_messages(self) -> None:
    """Background thread that reads messages from subscribed channels."""
    self.listener_active = True
    try:
        # listen() blocks and yields messages as they are published.
        for message in self.pubsub.listen():
            if not self.listening:
                break

            # Handle both direct channel messages and pattern messages.
            if message["type"] in ("message", "pmessage"):
                self._add_message(format_message(message))

    except Exception as e:
        if self.listening:
            self._add_message({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "channel": "system",
                "pattern": None,
                "event": "listener_error",
                "details": {"error": str(e)},
            })
    finally:
        self.listener_active = False
```
**Qué mirar:** `pubsub.listen()` bloquea, por eso corre en un hilo; trata `message` (canal) y `pmessage` (patrón).

### 5.6 Suscripciones (`SUBSCRIBE CHANNEL/PATTERN`, **dentro de la clase, sangrado 4 espacios**)
```python
def subscribe_to_channel(self, channel: str) -> str:
    """Subscribe to a specific channel using subscribe()."""
    self.pubsub.subscribe(channel)  # Register interest in the channel.
    self.restart_listener()
    return f"Subscribed to channel: {channel}"

def subscribe_to_pattern(self, pattern: str) -> str:
    """Subscribe using a pattern with psubscribe() (e.g. 'orders:*')."""
    self.pubsub.psubscribe(pattern)  # Register interest in matching channels.
    self.restart_listener()
    return f"Subscribed to pattern: {pattern}"
```
**Qué mirar:** `subscribe` = canal exacto, `psubscribe` = patrón con comodines (`orders:*`).

**Comprobación** (solo lectura):
```bash
python3 -m py_compile client/pubsub_functions.py && echo "sintaxis OK"
grep -c "def listen_messages\|def subscribe_to_pattern\|def get_client\|def broadcast_to_all\|def format_message\|def publish_order_created" client/pubsub_functions.py
```
Esperado: `sintaxis OK` y `6`. Si `py_compile` da `IndentationError`, revisa que `listen_messages`, `subscribe_to_channel` y `subscribe_to_pattern` estén **dentro** de la clase. Borra el `__pycache__` generado.

## Paso 6 · Base de datos y acceso (opciones 2 y 3)
**Por qué:** crea la base de datos con autenticación Entra, asigna tu política de acceso y genera `.env`.
```bash
python3 azdeploy.py      # menú → 2 → 3 → 4
```
Salida (pendiente de ejecutar; salida esperada según la guía): resumen con `Endpoint` y `Authentication: Microsoft Entra ID (current user)`; la opción 3 muestra clúster y base de datos en `Succeeded`.

**Comprobación** (con `az`):
```bash
az redisenterprise database show -g rg-ai200-lp6-02 --cluster-name amr-exercise-<hash> --query "{state:provisioningState, port:port}" -o table
grep -c REDIS_HOST .env
```
Esperado: `Succeeded`, puerto `10000` y `1`. Si la opción 2 dice que el clúster no está listo, espera y repite el `list` del paso 4. Los nombres de propiedades de `--query` no están verificados: si sale vacío, ejecuta el `show` sin `--query`.

## Paso 7 · Comprobar que el puerto 10000 sale del PC (aviso del proxy)
**Por qué:** Azure Managed Redis habla **TLS por el puerto 10000**, no por 443. El PC es de empresa y su proxy transparente ya ha bloqueado `kubectl` contra AKS, así que **este puerto puede fallar** (timeout, o error de certificado/TLS). Mejor saberlo antes de arrancar la app. Esta comprobación solo lee.
```bash
source .env
timeout 10 bash -c 'exec 3<>/dev/tcp/$REDIS_HOST/10000' && echo "puerto 10000 abierto" || echo "puerto 10000 BLOQUEADO"
```
(`REDIS_HOST` es la variable que genera el propio lab; no se muestra su valor.)

Salida (pendiente de ejecutar; salida esperada según la guía): `puerto 10000 abierto`.

**Qué mirar:** `/dev/tcp` solo prueba el TCP. Aunque salga abierto, el proxy podría romper el TLS: el error aparecería al conectar la app (paso siguiente). Si sale BLOQUEADO o la app da `Timeout`/`SSL`/`Error 999` (el propio código del lab sugiere que 999 es un problema de red o firewall), alternativas, en este orden:
1. Otra red sin ese proxy (por ejemplo, un punto de acceso móvil), si la política de empresa lo permite.
2. Ejecutar la app desde otra máquina o desde Azure Cloud Shell (subes los ficheros del lab y haces `az login`). No verificado que `DefaultAzureCredential` autentique en Cloud Shell: confírmalo antes de depender de ello.
3. Pedir a TI que permita `*.redis.azure.net:10000` (el dominio del endpoint no está verificado hasta ver el valor real de `REDIS_HOST`).

**Comprobación:** el `echo` final dice `abierto`. Si no, no sigas: el resto del lab necesita esa conexión.

## Paso 8 · Entorno Python (en `client/`)
```bash
source .env
cd client
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
**Por qué:** `source .env` va **antes** de entrar en `client/` porque el `.env` está en la carpeta del lab.

Salida (pendiente de ejecutar; salida esperada según la guía): `Successfully installed … flask-3.1.1 … redis-8.0.1 redis-entraid-1.2.1 azure-identity-1.24.0 …` (versiones leídas de `requirements.txt`).

**Comprobación:** `pip list | grep -iE "flask|redis|azure-identity"`. Si falla por certificado: `--cert /etc/ssl/certs/ca-certificates.crt`.

## Paso 9 · Ejecutar la app y probar pub/sub
```bash
python3 app.py
```
La app escucha en el puerto 5000 con `host="0.0.0.0"` (visible en la red local mientras corra; ciérrala al terminar). Abre http://localhost:5000.

Salida (pendiente de ejecutar; salida esperada según la guía): arranque de Flask; la página con **Subscriptions**, **Publish Events** y **Received Messages**.

Pruebas, en este orden (comportamiento descrito en la guía):

| # | Acción | Esperado | Qué demuestra |
|---|---|---|---|
| 1 | Suscribirse a `notifications` | aparece en *Active subscriptions* | sin suscripción no se recibe nada |
| 2 | Publicar **Notification** | resultado con canal y nº de suscriptores; llega a *Received Messages* en 1-2 s | entrega a suscriptores activos |
| 3 | Publicar **Inventory Alert** | se publica en `inventory:alerts` pero **no llega** | no estás suscrito a ese canal |
| 4 | Suscribirse al patrón `orders:*` | aparece junto a `notifications` | `psubscribe` |
| 5 | Publicar **Order Created** y **Order Shipped** | **ambos llegan** | el patrón cubre `orders:created` y `orders:shipped` |
| 6 | **Broadcast to All** | llegan los que casan con tus suscripciones | un mensaje a todos los canales |
| 7 | **Unsubscribe from All** y de nuevo **Broadcast to All** | **no llega nada** | sin suscripciones, el mensaje se pierde |

**Qué mirar:** el contador de suscriptores del resultado de publicación (con 0 el mensaje se perdió) y el campo `pattern` en los mensajes recibidos por patrón. Es la demostración práctica del *at-most-once* de la teoría.

**Comprobación:** cada fila coincide. Si no llega nada, comprueba que estás suscrito al canal o patrón correcto y que la app sigue corriendo. Un mensaje `listener_error` en la lista indica fallo de conexión (red/proxy, paso 7, o política de acceso). Para parar la app: Ctrl+C.

## Paso 10 · Cleanup (obligatorio)
**Por qué:** Azure Managed Redis cobra mientras exista (el precio por hora de `Balanced_B0` no está verificado: consúltalo en la página de precios). Hazlo **antes de documentar**: si caducan las credenciales del lab ya no se puede borrar ni comprobar.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-lp6-02 --no-wait --yes
az group exists --name rg-ai200-lp6-02
```
**Comprobación:** repite `az group exists --name rg-ai200-lp6-02` hasta que devuelva `false` (puede tardar varios minutos; Redis Enterprise tarda en borrarse). Mientras tanto `az resource list -g rg-ai200-lp6-02 -o table` muestra lo que queda. Si pasados ~15 minutos sigue `true`, mira `az redisenterprise list -g rg-ai200-lp6-02 -o table` y repite el `delete`.

Inventario final: `az group list -o table` no debe mostrar `rg-ai200-lp6-02`. 

Salida (pendiente de ejecutar; salida esperada según la guía): `false`.

## Resumen de incidencias
(Se rellena al ejecutar el lab. Riesgos previstos:)

| Posible síntoma | Causa probable | Arreglo |
|---|---|---|
| `listener_error` / timeout / SSL | Proxy bloquea el puerto 10000 | Paso 7 |
| Fallo de despliegue | Falta de capacidad en la región | Cambiar `location`, repetir opción 1 |
| `Authentication error` | Política de acceso no propagada | Esperar y repetir; revisar opción 2 |
| No llegan mensajes | No hay suscripción al canal/patrón, o la app se paró | Paso 9 |
| `IndentationError` o métodos fuera de la clase | Sangrado | Paso 5 |
| Sin variable `REDIS_HOST` | No se hizo `source .env` antes de `cd client` | Paso 8 |
