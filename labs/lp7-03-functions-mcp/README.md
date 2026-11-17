# Lab LP7-03 · Create an MCP server with Azure Functions (plataforma: lab de LP7M03)

- **Guía oficial:** https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/03-azure-functions-mcp-server.html (fuente Markdown: `instructions/integrate-services/03-azure-functions-mcp-server.md`; el código y los prompts de este README están copiados literales de ahí).
- **Estado: PREPARADO, sin ejecutar** (17/11/2026). Las salidas marcadas «(pendiente de ejecutar; salida esperada según la guía)» se sustituirán por las reales al hacer el lab.
- **Notas teóricas:** [07-3-functions.md](../../docs/modulos/07-3-functions.md). Índice: [07-servicios-backend.md](../../docs/modulos/07-servicios-backend.md).
- **Duración:** ~25 min (la guía). **No hay starter zip** (el proyecto se crea desde cero) y **no se crea ningún recurso en Azure**: todo corre en local. El proyecto vivirá en esta carpeta (`labs/lp7-03-functions-mcp/`).
- Anterior: [LP7-02](../lp7-02-eventgrid/README.md). Opcional del bloque (no preparado): [Durable Functions](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/04-durable-functions-ai.html).

Cada paso tiene: **por qué → comando → salida → qué mirar → comprobación (y qué hacer si no coincide)**.

## Qué se construye
Un **servidor MCP** (Model Context Protocol) con la extensión MCP de Azure Functions: cada función con trigger `mcpToolTrigger` es una *tool* que un cliente MCP (aquí GitHub Copilot en modo agente) puede descubrir y llamar.

```
function_app.py → summarize_text, classify_document (stubs, @app.generic_trigger type=mcpToolTrigger)
host.json       → extension bundle Preview + serverName document-tools
.vscode/mcp.json→ registra http://localhost:7071/runtime/webhooks/mcp/sse (type sse)
func start / F5 → Core Tools en el puerto 7071
```
- Analogía K8s: un servicio que publica un catálogo de operaciones (como un API/CRD con su descripción) para que un agente decida cuándo llamarlas; el campo `description` es lo que lee el modelo.
- Guía: la extensión MCP **evoluciona** (preview); consultar la [doc de la extensión](https://learn.microsoft.com/azure/azure-functions/functions-bindings-mcp) si algo difiere.
- Para producción (no es parte del lab): Flex Consumption, clave de sistema `mcp_extension`, llamadas a servicios de IA con `DefaultAzureCredential`.

## Requisitos (la guía) y estado de este equipo
| Requisito | Estado verificado el 17/11/2026 |
|---|---|
| VS Code + extensión Azure Functions | `code` presente; extensión **no comprobada** |
| Azure Functions Core Tools v4+ | **`func` no está instalado** en este equipo (se comprobó con `command -v func`) |
| Python 3.9+ | 3.12.3 |
| Cuenta GitHub con **Copilot** + extensión GitHub Copilot, con sesión iniciada en VS Code | **Sin confirmar**: sin Copilot no se puede hacer la prueba de la guía (ver alternativa en el paso 6) |

Pregunta previa para el alumno: ¿tienes licencia de GitHub Copilot (la de empresa sirve si la tienes)?

---

## Paso 0 · Terminal y carpeta
```bash
cd ~/claude/AI-200-Developing/labs/lp7-03-functions-mcp
deactivate 2>/dev/null
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```
✅ **Comprobación:** `pwd` termina en `labs/lp7-03-functions-mcp`.

## Paso 1 · Instalar Core Tools (si falta)
**Por qué:** `func` es el runtime local de Functions; la guía lo da por instalado (v4 o posterior). Se anticipa porque aquí **no** está.
```bash
command -v func && func --version
```
Si no hay `func`, instalación por npm (`node` y `npx` están presentes), sin `sudo`:
```bash
npm install --prefix ./tmp/func-tools azure-functions-core-tools@4
./tmp/func-tools/node_modules/.bin/func --version
```
Salida: *(pendiente de ejecutar; salida esperada: una versión 4.x)*

**Qué mirar:** la instalación **descarga binarios** de internet; con el proxy de empresa puede fallar por certificado o bloqueo *(no verificado)*. Alternativas: paquete `apt` de Microsoft (necesita `sudo` y repo de Microsoft; decidirlo juntos) o la extensión de VS Code, que puede instalar Core Tools. Si usas el `func` de `tmp/`, llámalo con su ruta o añádelo al `PATH` de esa terminal (`export PATH="$PWD/tmp/func-tools/node_modules/.bin:$PATH"`, desde la raíz del repo).

✅ **Comprobación:** `func --version` (o con ruta) imprime `4.x`. Si falla la descarga, no sigas: avísame con el error.

## Paso 2 · Crear el proyecto (comando de VS Code de la guía)
**Por qué:** genera `function_app.py`, `host.json`, `local.settings.json`, `requirements.txt` y `.vscode/`.

En VS Code: **File > Open Folder…** → `labs/lp7-03-functions-mcp`; **View > Command Palette…** → **Azure Functions: Create Function…** con estas opciones (literal de la guía):

| Opción | Acción |
|---|---|
| Select the folder... | La carpeta abierta |
| Select a project type | **Python** |
| Select a Python interpreter... | **Skip virtual environment** |
| Select a template... | **HTTP trigger** |
| Function name | Aceptar **http_trigger** |
| Authorization level | **ANONYMOUS** |

*Alternativa por terminal (no es de la guía; `func init` es de Core Tools, **no verificado** que genere exactamente lo mismo):* `func init . --python -m v2`, que crea el proyecto Python v2 sin la plantilla HTTP ni `.vscode/`; en ese caso el paso 3 sobrescribe igualmente `function_app.py`, y `.vscode/mcp.json` se crea a mano.

✅ **Comprobación (solo lectura):**
```bash
ls -A
```
Esperado: `function_app.py`, `host.json`, `local.settings.json`, `requirements.txt` y `.vscode`. Si falta alguno, repite el comando de la paleta.

## Paso 3 · Configuración: `host.json`, `local.settings.json`, `.vscode/mcp.json`
**Por qué:** `mcpToolTrigger` es un binding en **preview**, que solo está en el *extension bundle* Preview; `serverName/serverVersion/serverInstructions` es lo que ve el cliente al conectar. `AzureWebJobsStorage` vacío evita necesitar Azurite/Storage para este lab; `AzureWebJobsSecretStorageType: Files` guarda claves en ficheros locales.

Sustituye el contenido de `host.json` por (literal):
```json
{
    "version": "2.0",
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle.Preview",
        "version": "[4.*, 5.0.0)"
    },
    "extensions": {
        "mcpToolTrigger": {
            "serverName": "document-tools",
            "serverVersion": "1.0.0",
            "serverInstructions": "Tools for document processing and classification"
        }
    }
}
```

Sustituye `local.settings.json` por:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsSecretStorageType": "Files"
  }
}
```

Crea `.vscode/mcp.json`:
```json
    "servers": {
        "document-tools-local": {
            "type": "sse",
            "url": "http://localhost:7071/runtime/webhooks/mcp/sse"
        }
    }
}
```

✅ **Comprobación (solo lectura):**
```bash
python3 -I -c "import json;[json.load(open(f)) for f in ('host.json','local.settings.json','.vscode/mcp.json')];print('JSON OK')"
```
Esperado: `JSON OK`. Si falla, hay una coma o llave mal pegada en el fichero que cita el traceback.

## Paso 4 · Definir las dos tools (`function_app.py`)
**Por qué:** `@app.generic_trigger(type="mcpToolTrigger")` convierte cada función en tool; `toolName` es el nombre que ve el cliente, `description` ayuda al modelo a elegir y `toolProperties` define el esquema de entrada. Las dos son **stubs**: en real llamarían a un servicio de IA.

Sustituye todo `function_app.py` por (literal):
```python
import azure.functions as func
import json
import logging

# Initialize the FunctionApp instance that registers all trigger functions
app = func.FunctionApp()

# Define an MCP tool trigger that exposes "summarize_text" to MCP clients.
# toolProperties defines the input schema: a single "text" string parameter.
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="summarize_text",
    description="Summarize a block of text into key points",
    toolProperties='[{"propertyName": "text", "propertyType": "string", "description": "The text to summarize"}]'
)
def summarize_text(context: str) -> str:
    # Log the raw payload for debugging
    logging.info(f"summarize_text raw context: {context}")
    # Parse the outer request envelope sent by the MCP client
    request = json.loads(context)
    logging.info(f"summarize_text parsed request: {request}")
    # Extract the tool arguments from the request
    arguments = request.get("arguments", {})
    # Retrieve the "text" property defined in toolProperties
    text = arguments.get("text", "")

    # In a real implementation, call an Azure AI service here
    summary = f"Summary of {len(text.split())} words: {text[:100]}..."

    # Return a JSON response; the "content" field is displayed to the MCP client
    return json.dumps({"content": summary})

# Define a second MCP tool trigger that exposes "classify_document" to MCP clients.
# toolProperties defines two input parameters: "text" and "categories".
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="classify_document",
    description="Classify a document into a category",
    toolProperties='[{"propertyName": "text", "propertyType": "string", "description": "The document text to classify"}, {"propertyName": "categories", "propertyType": "string", "description": "Comma-separated list of possible categories"}]'
)
def classify_document(context: str) -> str:
    # Log the raw payload for debugging
    logging.info(f"classify_document raw context: {context}")
    # Parse the outer request envelope sent by the MCP client
    request = json.loads(context)
    logging.info(f"classify_document parsed request: {request}")
    # Extract the tool arguments from the request
    arguments = request.get("arguments", {})
    # Retrieve the "text" and "categories" properties defined in toolProperties
    text = arguments.get("text", "")
    categories = arguments.get("categories", "general")

    # In a real implementation, call an Azure AI service here
    # Split the comma-separated categories string into a list
    category_list = [c.strip() for c in categories.split(",")]
    # Select the first category as the classification result
    selected_category = category_list[0] if category_list else "unknown"

    # Return a JSON response with the classification result
    return json.dumps({
        "content": f"Classification: {selected_category}",
        "category": selected_category
    })
```

✅ **Comprobación (solo lectura):**
```bash
python3 -I -m py_compile function_app.py && echo "sintaxis OK"
grep -c "mcpToolTrigger" function_app.py
```
Esperado: `sintaxis OK` y `2`. Si falla `IndentationError`, revisa la sangría pegada.

## Paso 5 · Entorno Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list | grep -i azure-functions
```
Salida: *(pendiente de ejecutar; salida esperada: `azure-functions` instalado)*

Después, en VS Code, **Python: Select Interpreter** → el de `.venv` (para el depurador con F5).

**Qué mirar:** error de certificado en `pip` → `PIP_CERT=/etc/ssl/certs/ca-certificates.crt pip install -r requirements.txt`.

✅ **Comprobación:** `azure-functions` en la lista. Si no, repite `pip install`.

## Paso 6 · Arrancar el runtime y comprobar las tools
```bash
func start
```
(o **F5** en VS Code; si pide cuenta de almacenamiento: **Skip for now**).

Salida: *(pendiente de ejecutar; salida esperada según la guía)*
```text
Functions:
    classify_document: mcpToolTrigger
    summarize_text: mcpToolTrigger
```
**Qué mirar:** deben aparecer **ambas** funciones. Los avisos sobre *health checks* se pueden ignorar (guía). La primera ejecución descarga el extension bundle Preview desde internet: con el proxy puede fallar *(no verificado)*; si pasa, pega el error.

✅ **Comprobación (solo lectura, en otra terminal):**
```bash
curl -s -m 5 -o /dev/null -w "%{http_code}\n" http://localhost:7071/admin/host/status
```
Esperado: `200`. Si no responde: ¿`func start` sigue corriendo?, ¿puerto 7071 ocupado?, ¿existe `local.settings.json`? Para ver el endpoint MCP: `curl -s -N -m 5 http://localhost:7071/runtime/webhooks/mcp/sse | head -3` *(no verificado: debería abrir un flujo SSE; no es parte de la guía)*.

## Paso 7 · Probar desde GitHub Copilot en modo agente
1. En VS Code, icono **Accounts**: sesión de GitHub con Copilot.
2. Abre el chat de Copilot (modo agente), icono de herramientas: grupo **document-tools-local** con **summarize_text** y **classify_document** y sus descripciones.
3. Al invocar por primera vez una tool aparece un permiso: **Allow in this Session**.

Prompts **explícitos** (literales de la guía):
```
Use the classify_document tool to classify this text: 'This agreement is entered into by Party A and Party B'  with categories: contract, invoice, memo
```
Esperado: clasificación **contract** (el stub devuelve la primera categoría) y una línea de log en la terminal de `func`.
```
Use the summarize_text tool to summarize this text: 'Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure.'
```
Esperado: texto que empieza por **Summary of** + nº de palabras + vista previa truncada.

Prompts en **lenguaje natural** (el modelo decide si usa la tool; confirma en la terminal que se invocó):
```
Is the following text an invoice, contract, or memo?
'Invoice B1234 for services rendered in January 2026. Total amount due: $5,000.'
```
```
Give me a brief summary of this text: 'Machine learning models require large datasets for training. The quality of the training data directly impacts model accuracy. Data preprocessing steps include cleaning, normalization, and feature extraction.'
```
Salida: *(pendiente de ejecutar; salida esperada según la guía)*

✅ **Comprobación:** el log de `func start` muestra `classify_document raw context: …` / `summarize_text raw context: …` por cada llamada (el código hace `logging.info`). Si Copilot responde sin llamar a la tool, no hay log: reformula nombrando la tool.

**Si no hay Copilot (alternativa no oficial, no verificada):** cliente MCP genérico, p. ej. `npx @modelcontextprotocol/inspector`, apuntando al endpoint SSE `http://localhost:7071/runtime/webhooks/mcp/sse` (descarga un paquete npm: puede toparse con el proxy). Esto no está en la guía: pregunta al profesor cómo se evalúa si no hay licencia.

**Si falla:** *Core Tools no arranca* → `func --version` ≥ 4, puerto 7071 libre, `local.settings.json` presente. *Copilot no ve las tools* → `.vscode/mcp.json` guardado y URL exacta, runtime mostrando las dos funciones, reiniciar VS Code. *Errores de invocación* → mira el traceback en la terminal, sangría de `function_app.py`, venv activo.

## Cleanup (obligatorio al acabar)
No hay recursos en Azure que borrar. Para el runtime con **Shift+F5** (o `Ctrl+C` si usaste `func start`), `deactivate`, y comprueba que no se ha creado nada en la suscripción:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group list -o table
```
Salida: *(pendiente de ejecutar; salida esperada: sin ningún grupo creado por este lab; si sigues con los otros labs de LP7, ya deberían estar borrados)*

✅ **Comprobación:** `curl -s -m 3 -o /dev/null -w "%{http_code}\n" http://localhost:7071/admin/host/status` ya no devuelve `200` (runtime parado: `000`). Si sigue `200`, queda un `func` en marcha: ciérralo. Si ya no se necesita, `rm -rf tmp/func-tools` elimina las Core Tools instaladas en el repo.

> **Antes de subir al repo:** `.venv/` ya está en `.gitignore`; `.vscode/` y `local.settings.json` no contienen claves en este lab. Revisar `git status` antes de commitear.

## Resumen de incidencias
| Síntoma | Causa | Arreglo |
|---|---|---|
| *(vacío: se rellena al ejecutar el lab)* | | |
