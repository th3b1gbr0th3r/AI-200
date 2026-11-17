# LP7 · Módulo 3 · Backends de IA serverless con Azure Functions

Volver al [índice de LP7](07-servicios-backend.md). Lab: [LP7-03 · Servidor MCP con Functions](../../labs/lp7-03-functions-mcp/README.md). Fuente: presentación del módulo 3.

## Objetivos del módulo (presentación)
- Evaluar cold start, escalado y memoria entre Flex Consumption y Premium.
- Entorno local: Core Tools, emuladores, IDE.
- Triggers y bindings para patrones de IA (endpoint HTTP, procesador por cola).
- Secretos con referencias a Key Vault y App Configuration.
- Identidad gestionada y autorización por funciones.

## El servicio
Cómputo serverless dirigido por eventos: de cero a miles de instancias, triggers y bindings declarativos, pago por ejecución. Python, JavaScript, C#, Java...

## Hosting y escalado (con analogía K8s)
| Concepto | Detalle de la presentación | Analogía |
|---|---|---|
| Cold start | Retraso al asignar instancia y cargar dependencias; en IA se agrava (librerías, modelos) | Pod nuevo tardando en pasar `readinessProbe` |
| Flex Consumption | Escalado por función, instancias **always-ready**, escala a cero | HPA/KEDA con `minReplicas` > 0 |
| Premium | Workers pre-calentados, sin cold start, contenedores propios | Deployment con réplicas siempre encendidas |
| Concurrencia | Cada tipo de trigger escala en sus instancias; menos concurrencia aísla recursos | `maxConcurrentCalls` ≈ hilos por pod |
| Memoria = CPU | 2.048 MB = 1 vCPU; 4.096 MB = 2 vCPU | `resources.limits` |

**Test 1 (propuesta A):** Flex Consumption con always-ready reduce el primer arranque sin pagar un plan siempre caliente. B (más timeout) no quita el cold start; C (Premium con pre-calentamiento **desactivado**) anula justo lo que ayuda.

Tareas largas: el trigger HTTP tiene un límite de **230 s** (balanceador). Patrón *async request-reply*: aceptar, encolar y devolver **202**; un procesador por cola no tiene ese límite.

## Entorno local
- **Core Tools** (`func`): runtime local. Python v2: un único `function_app.py` con decoradores; `host.json` (runtime) y `local.settings.json` (ajustes locales, no se sube).
- **Azurite** emula Storage (necesario incluso con triggers que no son de storage). F5 en VS Code arranca Core Tools con depurador. `func azure functionapp fetch-app-settings` sincroniza ajustes.

## Triggers y bindings
```python
@app.route(route="classify", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def classify_document(req): ...          # HTTP: respuesta directa, límite 230 s

@app.service_bus_queue_trigger(arg_name="msg", queue_name="document-jobs", connection="ServiceBusConnection")
@app.blob_output(arg_name="output_blob", path="results/{rand-guid}.json", connection="AzureWebJobsStorage")
def process_and_store(msg, output_blob): ...   # cola -> blob sin SDK
```
- **Service Bus trigger:** trabajo por lotes; `maxConcurrentCalls` en `host.json` marca el paralelismo por instancia; fallos repetidos van a la DLQ (enlaza con el módulo 1).
- **Bindings de salida:** el runtime gestiona conexión, auth y serialización (Blob, Cosmos DB, Service Bus).
- **SDK** para lo que no tiene binding (Document Intelligence, OpenAI, AI Search): clientes a nivel de módulo (reutilizados) y `DefaultAzureCredential`.

## Secretos y configuración
- Los app settings son variables de entorno (`os.environ`).
- **Referencia a Key Vault:** el setting apunta al secreto y se resuelve en ejecución. URI **sin versión** = siempre la última (rotación sin redesplegar). Analogía: Secret CSI Driver con sincronización.
- **App Configuration:** configuración no secreta compartida, con etiquetas por entorno.

**Test 2 (propuesta A):** para rotar sin redesplegar, la referencia lleva **URI sin versión**. Con versión queda fijada; guardar la clave en el setting rompe el requisito de Key Vault.

## Identidad y acceso
- **Conexiones por identidad:** sin cadena de conexión; sufijo `ServiceBusConnection__fullyQualifiedNamespace`; mínimo privilegio por servicio.
- **Claves de autorización:** de función (una), de host (todas), de sistema (extensiones), maestra (admin). Nivel por trigger: `anonymous`, `function`, `admin`.

## El lab en una línea
Servidor **MCP** con la extensión de Functions: dos tools (`summarize_text`, `classify_document`, ambas stub) con trigger `mcpToolTrigger`, probado en local desde GitHub Copilot en modo agente. **No crea recursos en Azure.** Un servidor MCP expone *tools* a un agente de IA: aquí cada función es una tool.

## Errores comunes
| Síntoma | Causa |
|---|---|
| Copilot no ve las tools | `.vscode/mcp.json` mal, runtime no arrancado o sin sesión de GitHub con Copilot |
| `func` no arranca | Core Tools < v4 o puerto 7071 ocupado |
| Cold start a pesar de always-ready | Pico por encima de las instancias reservadas (pregunta de debate 3) |

## Preguntas de repaso
Las 2 del test están en el [índice](07-servicios-backend.md#preguntas-de-repaso-test-de-la-presentación). Propias (orientativas, a confirmar):
1. ¿Cómo se procesa algo que tarda más de 230 s? Request-reply: 202 + cola + procesador.
2. ¿Qué sufijo tiene una conexión por identidad a Service Bus? `__fullyQualifiedNamespace`.
3. ¿Qué dos archivos de configuración tiene un proyecto Python v2? `host.json` y `local.settings.json`.
