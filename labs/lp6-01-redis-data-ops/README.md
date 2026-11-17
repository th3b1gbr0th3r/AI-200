# Lab LP6-01 · Perform data operations in Azure Managed Redis

- **Estado: PREPARADO, sin ejecutar.** Redactado el 17/11/2026 a partir de la guía oficial y del `azdeploy.py` del starter. Todas las salidas están marcadas «(pendiente de ejecutar; salida esperada según la guía)» y se sustituirán por las reales al hacer el lab.
- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/01-amr-data-operations.html (fuente Markdown: `instructions/azure-managed-redis/01-amr-data-operations.md` del repo MIT de Microsoft).
- **Teoría:** [06-1-redis-data-operations.md](../../docs/modulos/06-1-redis-data-operations.md). Índice: [06-redis.md](../../docs/modulos/06-redis.md).
- **Starter ya descargado y descomprimido aquí:** `amr-data-operations-python.zip` → `azdeploy.py`, `main.py`, `requirements.txt`. Origen MIT: [`../NOTICE.md`](../NOTICE.md). **Nada se ha ejecutado.**
- Duración según la guía: ~30 min (más 5-10 min de despliegue). Requisitos: Python 3.12+, Azure CLI reciente, extensión `redisenterprise`.

Cada paso tiene: **por qué → comando → salida esperada → qué mirar → comprobación (y qué hacer si no coincide)**.

## Qué se construye
Una app de consola (`main.py`) que se conecta a Azure Managed Redis con **Entra ID** (sin claves) y hace operaciones con un **hash**: guardar, leer, poner TTL, consultar TTL y borrar.

```
azdeploy.py 1 → RG + clúster Azure Managed Redis amr-exercise-<hash> (Balanced_B0, acceso público, sin base de datos)
azdeploy.py 2 → comprobar estado
azdeploy.py 3 → base de datos (puerto 10000, TLS, NoCluster, AllKeysLRU) + asignación de acceso Entra + .env con REDIS_HOST
main.py       → menú 1-6: hset/hgetall, expire/ttl, delete
```
Qué crea `azdeploy.py` (leído del script, no ejecutado): `az redisenterprise create --sku Balanced_B0 --public-network-access Enabled --no-database`; después `az redisenterprise database create --client-protocol Encrypted --clustering-policy NoCluster --eviction-policy AllKeysLRU --port 10000` y `az redisenterprise database access-policy-assignment create --access-policy-name default --object-id <tu object id>`. Es idempotente y, si encuentra un recurso en estado `Failed`, lo borra y reintenta.

Analogía K8s: el clúster es el *node pool* (cómputo y memoria), la base de datos es el Service/puerto que expones, y la asignación de acceso es un RoleBinding para tu identidad de Entra.

---

## Paso 0 · Preparar la terminal
```bash
cd ~/claude/AI-200-Developing/labs/lp6-01-redis-data-ops
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
RG=rg-ai200-lp6-01
sed -i "s/<your-resource-group-name>/$RG/; s/<your-azure-region>/eastus2/" azdeploy.py
grep -nE '^(rg|location) =' azdeploy.py
```
**Por qué:** solo se editan esas dos variables. Si la plataforma del lab impone un grupo o una región, usa los suyos. `eastus2` es una de las regiones que el propio script sugiere si falta capacidad (`eastus2`, `australiaeast`, `canadacentral`); no está verificado que sea la más barata ni la más cercana.

**Comprobación:** el `grep` debe mostrar `rg = "rg-ai200-lp6-01"` y `location = "eastus2"`. Si siguen apareciendo `<your-…>`, el `sed` no encontró el texto: edita el fichero a mano.

## Paso 4 · Crear el clúster (`azdeploy.py` → opción 1)
**Por qué:** crea el grupo y el recurso; son 5-10 minutos, así que se lanza primero y el código se completa mientras tanto. Antes avisa: **genera coste** y hay que confirmar suscripción, región y limpieza.
```bash
python3 azdeploy.py      # menú → 1
```
Menú de este lab (opciones **2 = estado** y **3 = base de datos**, al revés que en los labs 2 y 3):
```text
1. Create Azure Managed Redis resource
2. Check deployment status
3. Create database and configure access
4. Exit
```
Salida (pendiente de ejecutar; salida esperada según la guía):
```text
Creating Azure Managed Redis resource 'amr-exercise-<hash>' in 'eastus2'...
This takes 5-10 minutes to complete. Please wait...
Azure Managed Redis resource created successfully: amr-exercise-<hash>
```
**Qué mirar:** el script pide `main.py` junto a él (`_preflight`); si lo has movido, sale con error. Si falla por **falta de capacidad** en la región, el propio script lo explica: sal (opción 4), cambia `location` (`eastus2`, `australiaeast`, `canadacentral`) y repite la opción 1 (borra el recurso fallido antes de reintentar).

**Comprobación** (en **otra terminal**, con el paso 0 hecho, mientras el script espera):
```bash
az redisenterprise list -g rg-ai200-lp6-01 --query "[].{name:name, state:provisioningState, sku:sku.name}" -o table
```
Esperado: una fila `amr-exercise-<hash>`, `Balanced_B0` y estado `Creating` y luego `Succeeded`. Si la lista sale vacía y el script ya terminó con error, relee el error del script antes de repetir.

## Paso 5 · Completar `main.py`
**Por qué:** las cuatro secciones `BEGIN/END` están vacías; sin ellas no hay conexión ni funciones. Código **literal de la guía oficial**. Usa espacios, no tabuladores. En VS Code: pega pegado al margen, selecciona y pulsa Tab.

### 5.1 Conexión (`# BEGIN CONNECTION CODE SECTION`, dentro de `connect_to_redis`, **sangrado 4 espacios**)
```python
try:
    # Azure Managed Redis using Microsoft Entra ID authentication
    redis_host = os.getenv("REDIS_HOST")

    # create_from_default_azure_credential uses DefaultAzureCredential to
    # acquire and refresh a Microsoft Entra token for Redis.
    credential_provider = create_from_default_azure_credential(
        ("https://redis.azure.com/.default",),
    )

    r = redis.Redis(
        host=redis_host,
        port=10000,  # Azure Managed Redis uses port 10000
        ssl=True,
        decode_responses=True, # Decode responses to strings
        credential_provider=credential_provider,
        socket_timeout=30,  # Add timeout for better reliability
        socket_connect_timeout=30,
    )

    print(f"Connected to Redis at {redis_host}")
    input("\nPress Enter to continue...")
    return r
```
**Qué mirar:** el `try:` abre un bloque cuyo `except` ya viene escrito justo debajo del `END`. `create_from_default_azure_credential` (paquete `redis-entraid`) usa `DefaultAzureCredential` y renueva el token solo. Puerto 10000, `ssl=True`, `decode_responses=True`.

### 5.2 Guardar y leer (`# BEGIN STORE AND RETRIEVE CODE SECTION`, a nivel de módulo, sin sangrar)
```python
def store_hash_data(r, key, value) -> None:
    """Store a hash data in Redis"""
    clear_screen()
    print(f"Storing hash data for key: {key}")
    result = r.hset(key, mapping=value) # Store hash data
    if result > 0: # New fields were added
        print(f"Data stored successfully under key '{key}' ({result} new fields added)")
    else:
        print(f"Data updated successfully under key '{key}' (all fields already existed)")
    input("\nPress Enter to continue...")

def retrieve_hash_data(r, key) -> None:
    """Retrieve hash data from Redis"""
    clear_screen()
    print(f"Retrieving hash data for key: {key}")
    retrieved_value = r.hgetall(key) # Retrieve hash data
    if retrieved_value:
        print("\nRetrieved hash data:")
        for field, value in retrieved_value.items():
            print(f"  {field}: {value}")
    else:
        print(f"Key '{key}' does not exist.")

    input("\nPress Enter to continue...")
```
**Qué mirar:** `hset(mapping=…)` devuelve el número de campos **nuevos** (0 si solo actualizó).

### 5.3 Expiración (`# BEGIN EXPIRATION CODE SECTION`)
```python
def set_expiration(r, key) -> None:
    """Set an expiration time for a key"""
    clear_screen()
    print("Set expiration time for a key")
    # Set expiration time, 1 hour equals 3600 seconds
    expiration = int(input("Enter expiration time in seconds (default 3600): ") or 3600)
    result = r.expire(key, expiration) # Set expiration time
    if result:
        print(f"Expiration time of {expiration} seconds set for key '{key}'")
    else:
        print(f"Key '{key}' does not exist. Expiration not set.")

    input("\nPress Enter to continue...")

def retrieve_expiration(r, key) -> None:
    """Retrieve TTL of a key"""
    clear_screen()
    print(f"Retrieving the current TTL of {key}...")
    ttl = r.ttl(key) # Get current TTL
    if ttl == -2: # Key does not exist
        print(f"\nKey '{key}' does not exist.")
    elif ttl == -1: # No expiration set
        print(f"\nKey '{key}' has no expiration set (persists indefinitely).")
    else:
        print(f"\nCurrent TTL for '{key}': {ttl} seconds")
    input("\nPress Enter to continue...")
```
**Qué mirar:** `ttl` devuelve **-2** si la clave no existe y **-1** si no tiene expiración (es lo que dice la presentación). `expire` devuelve verdadero solo si la clave existe.

### 5.4 Borrado (`# BEGIN DELETE CODE SECTION`)
```python
def delete_key(r, key) -> None:
    """Delete a key"""
    clear_screen()
    print(f"Deleting key: {key}...")
    result = r.delete(key) # Delete the key
    if result == 1:
        print(f"Key '{key}' deleted successfully.")
    else:
        print(f"Key '{key}' does not exist.")
    input("\nPress Enter to continue...")
```

Guarda el fichero.

**Comprobación** (solo lectura: sintaxis y que no queden secciones vacías):
```bash
python3 -m py_compile main.py && echo "sintaxis OK"
grep -c "^def " main.py
```
Esperado: `sintaxis OK` y, con las 5 funciones nuevas más las 4 del starter (`clear_screen`, `connect_to_redis`, `show_menu`, `main`), un recuento de 9. Si `py_compile` da `IndentationError`, revisa el sangrado de la sección indicada. Ojo: `py_compile` crea un `__pycache__`; bórralo si no lo quieres en el repo.

## Paso 6 · Estado del clúster y base de datos (opciones 2 y 3)
**Por qué:** la opción 3 necesita que el clúster esté `Succeeded`; crea la base de datos, asigna tu acceso de datos y escribe `.env` / `.env.ps1`.
```bash
python3 azdeploy.py      # menú → 2 (repetir hasta Succeeded) → 3 → 4 para salir
```
Salida (pendiente de ejecutar; salida esperada según la guía):
```text
Cluster (amr-exercise-<hash>):
  Provisioning state: Succeeded
Database:
  Status: Not created
...
Creating database...
Assigning Microsoft Entra access for the current user...
Retrieving endpoint...
Redis Connection Information
Endpoint: <hash>.<región>.redis.azure.net   (formato no verificado)
Authentication: Microsoft Entra ID (current user)
```
**Qué mirar:** el estado de la base de datos pasa de «Not created» a `Succeeded` tras la opción 3. Si la opción 3 dice que el clúster no está listo, espera y repite la 2.

**Comprobación** (con `az`, lo que la guía mira en el portal):
```bash
az redisenterprise show -g rg-ai200-lp6-01 -n amr-exercise-<hash> --query "{state:provisioningState, host:hostName}" -o table
az redisenterprise database show -g rg-ai200-lp6-01 --cluster-name amr-exercise-<hash> --query "{state:provisioningState, port:port, protocol:clientProtocol, eviction:evictionPolicy}" -o table
az redisenterprise database access-policy-assignment show -g rg-ai200-lp6-01 --cluster-name amr-exercise-<hash> --database-name default --access-policy-assignment-name useraccess --query provisioningState -o tsv
```
Esperado: `Succeeded`, host con valor, puerto `10000`, `Encrypted`, `AllKeysLRU`, y `Succeeded` en la asignación. Si el último comando falla, la política aún se está aplicando: espera un minuto. El nombre del clúster sale de la lista del paso 4 (sustituye `<hash>`). Los nombres de propiedades de las consultas no están verificados: si una columna sale vacía, ejecuta el `show` sin `--query` y mira el nombre real.

**Comprobación del `.env`** (sin mostrar valores sensibles; solo contiene el host):
```bash
grep -c REDIS_HOST .env .env.ps1
```
Esperado: `1` en cada fichero. El `.env` de `labs/` se puede subir al repo (no contiene claves).

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

## Paso 8 · Entorno Python
**Por qué:** instala `redis`, `redis-entraid` y `azure-identity` (versiones fijadas en `requirements.txt`). Requiere Python 3.12+.
```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Salida (pendiente de ejecutar; salida esperada según la guía): `Successfully installed … redis-7.0.1 redis-entraid-1.2.1 azure-identity-1.24.0 …` (versiones leídas de `requirements.txt`).

**Comprobación:** `pip list | grep -iE "redis|azure-identity"` debe mostrar los tres paquetes. Si `python3 --version` es inferior a 3.12, la guía no lo soportaría: usa otra versión instalada. Si `pip` falla por certificado del proxy, pásale `--cert /etc/ssl/certs/ca-certificates.crt`.

## Paso 9 · Ejecutar la app
**Por qué:** `source .env` carga `REDIS_HOST` en esta terminal (si abres otra, repetirlo).
```bash
source .env
python3 main.py
```
Salida (pendiente de ejecutar; salida esperada según la guía): `Connected to Redis at <host>` y el menú:
```text
1. Store hash data
2. Retrieve hash data
3. Set expiration
4. Retrieve expiration (TTL)
5. Delete key
6. Exit
```
Secuencia sugerida con la clave `user:1001` y el hash `{name: Jane, age: 28, email: jane@example.com}` (definidos al inicio de `main()`):

| Orden | Opción | Esperado (según el código de la guía) | Qué demuestra |
|---|---|---|---|
| 1 | 4 TTL antes de existir | `Key 'user:1001' does not exist.` (TTL -2) | -2 = no existe |
| 2 | 1 Guardar | `Data stored successfully … (3 new fields added)` | `HSET` |
| 3 | 1 Guardar otra vez | `Data updated successfully … (all fields already existed)` | idempotencia: 0 campos nuevos |
| 4 | 2 Leer | los tres campos | `HGETALL` |
| 5 | 4 TTL | `has no expiration set (persists indefinitely)` (TTL -1) | -1 = sin expiración |
| 6 | 3 Expiración (Enter = 3600) | `Expiration time of 3600 seconds set…` | `EXPIRE` |
| 7 | 4 TTL | `Current TTL … : 3599 seconds` (aprox.) | cuenta atrás |
| 8 | 5 Borrar | `Key 'user:1001' deleted successfully.` | `DEL` |
| 9 | 2 Leer | `Key 'user:1001' does not exist.` | borrado verificado |

**Qué mirar:** los TTL -2 y -1 son preguntas típicas de examen. Si sale `Connection error`/`Timeout error`: red o proxy (paso 7). `Authentication error`: tu usuario no tiene la política de acceso (paso 6) o aún no se ha propagado; espera y repite. `Unexpected error` con `999`: red/firewall.

**Comprobación:** cada fila de la tabla coincide. Si la fila 7 da otra cosa distinta de 3600, mira si escribiste otro valor.

## Paso 10 · Cleanup (obligatorio)
**Por qué:** Azure Managed Redis cobra mientras exista (el precio por hora de `Balanced_B0` no está verificado: consúltalo en la página de precios). Hazlo **antes de documentar**: si caducan las credenciales del lab ya no se puede borrar ni comprobar.
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-lp6-01 --no-wait --yes
az group exists --name rg-ai200-lp6-01
```
**Comprobación:** repite `az group exists --name rg-ai200-lp6-01` hasta que devuelva `false` (puede tardar varios minutos; Redis Enterprise tarda en borrarse). Mientras tanto `az resource list -g rg-ai200-lp6-01 -o table` muestra lo que queda. Si pasados ~15 minutos sigue `true`, mira `az redisenterprise list -g rg-ai200-lp6-01 -o table` y repite el `delete`.

Inventario final: `az group list -o table` no debe mostrar `rg-ai200-lp6-01`. 

Salida (pendiente de ejecutar; salida esperada según la guía): `false`.

## Resumen de incidencias
(Se rellena al ejecutar el lab. Riesgos previstos:)

| Posible síntoma | Causa probable | Arreglo |
|---|---|---|
| `Timeout`/`SSL`/`Error 999` al conectar | Proxy corporativo bloquea el puerto 10000 | Paso 7 (alternativas) |
| `Authentication error` | Política de acceso no creada o no propagada | Opción 3 de `azdeploy.py`, esperar un minuto |
| Fallo de despliegue en la opción 1 | Falta de capacidad del SKU en la región | Cambiar `location` y repetir |
| `IndentationError` | Código pegado sin sangrar | Paso 5 |
| `Error: 'main.py' is missing` | `azdeploy.py` movido de carpeta | Mantener la carpeta intacta |
