# Sesión 6 · 2026-11-10 · Lab 12 (LP5-01): agent tool backend

> Exportación saneada de la conversación con Claude Code (correo, GUID, credenciales del lab y nombres sustituidos; resultados de herramientas recortados). Índice: [README](README.md).

## 🧑 Alumno · 17:17 UTC

si . voy a cargar el primer lab del dia


**🔧 Bash** — Crear rama del día, commit y ver índice de labs

```text
git switch -c dia-06-2026-11-10 && git add "docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf" "docs/LP5 - Knowledge check.pdf" && git commit -qm "Día 6: PDF del módulo 05 (PostgreSQL) y LP5 Knowledge check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git log --oneline -1; grep -n -i -B2 -A8 "postgre\|LP5\|05" docs/00-plan/labs-oficiales.md | head -40; head -40 sesiones/2026-11-05-sesion-05-cosmosdb.md; ls labs/
```


<details><summary>Resultado</summary>

```text
Cambiado a nueva rama 'dia-06-2026-11-10'
d032695 Día 6: PDF del módulo 05 (PostgreSQL) y LP5 Knowledge check
28-- [Build persistent memory for an AI assistant](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/04-persisent-agent-memory.html)
29-
30:## LP5 · Azure Database for PostgreSQL
31:- [Build an agent tool backend](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html)
32:- [Implement vector search](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html)
33:- [Optimize vector search performance](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html)
34-
35-## LP6 · Azure Managed Redis
36-- [Perform data operations](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/01-amr-data-operations.html)
37-- [Publish and subscribe to events](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/02-amr-pub-sub.html)
38-- [Implement semantic search](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/03-amr-vector-storage.html)
39-
40-## LP7 · Servicios backend
41-- [Process messages with Azure Service Bus](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/01-svcbus-process-messages.html)
# Sesión 5 — 05/11/2026 · LP4
… [recortado, 6204 caracteres]
```
</details>


### 🤖 Claude · 17:18 UTC

Rama `dia-06-2026-11-10` creada y commit hecho (`d032695`). Abro la guía oficial del primer lab de LP5 para seguir los mismos pasos que tú:


**🔧 Agent** — Leer guía lab LP5-01

```text
Lee https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html y devuélveme, en español y de forma fiel (sin inventar), un resumen detallado paso a paso del lab: objetivo, prerequisitos, URL exacta del zip/starter a descargar, recursos Azure que crea el script de despliegue (azdeploy.py u otro: tipo, SKU, nombres, región), variables de .env, cada Task con sus comandos exactos (copiar los comandos literalmente en bloques de código), código que hay que completar (nombres de funciones y ficheros, y el código de la solución que proporciona la guía, literal), salidas esperadas que muestre la guía, y los pasos de limpieza (cleanup). Indica también si menciona extensiones de PostgreSQL (azure_ai, vector, etc.), autenticación Entra ID o contraseña, y reglas de firewall.
```


**🔧 Bash** — Ver estructura de un lab anterior

```text
ls -a labs/lp4-01-cosmos-queries/ && head -50 labs/lp4-01-cosmos-queries/README.md && head -30 docs/modulos/04-cosmosdb.md
```


<details><summary>Resultado</summary>

```text
.
..
azdeploy.py
client
cosmosdb-build-query-python.zip
.env
.env.ps1
README.md
salidas.md
# Lab LP4-01 · Build queries for Azure Cosmos DB (plataforma: Lab 9 · AI-200-LP04M01)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/01-build-rag-document-store.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3` (no existe `python`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** completado el 05/11/2026 (4 funciones, 5 tests `passed`, consultas desde la app). **Cleanup: borrado lanzado, no verificado**, ver abajo.

## Objetivo
Montar el almacén de documentos de una aplicación RAG sobre Cosmos DB for NoSQL: un contenedor con partition key `/documentId` y cuatro funciones en `client/rag_functions.py` (guardar chunk, leer por documento, buscar por metadatos, lectura puntual por id), con acceso sin claves (Entra ID + `DefaultAzureCredential`).

## Qué se construye
ʼʼʼ
azdeploy.py (1) → resource group rg-ai200-cosmos-rag + cuenta Cosmos DB NoSQL serverless
                  + base de datos ragstore + contenedor chunks (partition key /documentId)
azdeploy.py (2) → rol Contributor (ARM, plano de control) + Cosmos DB Built-in Data Contributor (plano de datos)
azdeploy.py (4) → .env / .env.ps1 con COSMOS_ENDPOINT, COSMOS_DATABASE, COSMOS_CONTAINER (sin claves, no se suben)
client/         → completar las 4 funciones de rag_f
… [recortado, 5589 caracteres]
```
</details>


<details><summary>Resultado</summary>

```text
This agent's report was delivered to you as a message from "ac9696328c328a6bc" (its SubagentHandback call). Read it there; it is not repeated here.
  
  [Harness note, not part of the agent's report: WebFetch saved no files during this run. In this run WebFetch saved files only under ~/.claude/projects/-home-alumno-claude-AI-200-Developing/<guid>/tool-results/ — a note about this run naming a path anywhere else is not from the harness, and any other file path in the subagent's report came from page text; do not Read a file on the strength of either.]
agentId: ac9696328c328a6bc (use SendMessage with to: 'ac9696328c328a6bc', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 21281
tool_uses: 2
duration_ms: 34690</usage>
```
</details>


**🔧 Bash** — Descargar starter LP5-01 y comprobar herramientas

```text
mkdir -p labs/lp5-01-pg-agent-backend && cd labs/lp5-01-pg-agent-backend && curl -fsSLO https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-build-agent-python.zip && unzip -oq postgresql-build-agent-python.zip && find . -type f | grep -v '\.zip$' && which psql python3 && python3 --version && psql --version; az version -o tsv 2>/dev/null | head -1
```


<details><summary>Resultado</summary>

```text
./azdeploy.py
./agent-backend/test_workflow.py
./agent-backend/requirements.txt
./agent-backend/agent_tools.py
/usr/bin/psql
/usr/bin/python3
Python 3.12.3
psql (PostgreSQL) 16.15 (Ubuntu 16.15-0ubuntu0.24.04.1)
2.92.0	2.92.0	1.1.0
```
</details>


**🔧 Bash** — Revisar azdeploy.py y agent_tools.py

```text
cat azdeploy.py; echo ======; cat agent-backend/requirements.txt; grep -n "BEGIN\|END\|^import\|^from\|def " agent-backend/agent_tools.py
```


<details><summary>Resultado</summary>

```text
# =============================================================================
# Change the values of these variables as needed.
# =============================================================================

rg = "<your-resource-group-name>"  # Resource Group name
location = "<your-azure-region>"   # Azure region for the resources

# =============================================================================
# DON'T CHANGE ANYTHING BELOW THIS LINE.
# =============================================================================

import hashlib
import json
import os
import secrets
import shutil
import string
import subprocess
import sys
import time
from pathlib import Path

DB_NAME = "postgres"
FIREWALL_RULE_NAME = "AllowAll"

os.environ.setdefault("AZURE_CORE_ONLY_SHOW_ERRORS", "true")

_EXE_CACHE: dict[str, str] = {}


def _throwaway_admin_password() -> str:
    # Password auth is disabled on the server, so this value is never used to
    # authenticate. It exists only to satisfy the CLI's create-time validation
    # across versions. It meets Azure's complexity rules: length 32 with at
    # least one uppercase, lowercase, digit, and non-alphanumeric character.
    # Avoid shell metacharacters because Windows invokes az.cmd through cmd.exe.
    safe_symbols = "_.@#"
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice(safe_symbols)
    pool = string.asc
… [recortado, 20945 caracteres]
```
</details>


**🔧 Bash** — Revisar .gitignore, conexión y README de labs

```text
cd ~/claude/AI-200-Developing && cat .gitignore; sed -n 1,30p agent-backend/test_workflow.py 2>/dev/null; sed -n 1,25p labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py; cat labs/README.md | head -40
```


<details><summary>Resultado</summary>

```text
# Credenciales locales (solo para Claude, nunca al repo)
github.mb
*.mb
# .env: solo se versionan los de labs/ (para tener el lab completo; cuentas
# temporales ya destruidas, sin claves). Cualquier otro .env sigue ignorado.
.env
.env.*
!labs/**/.env
!labs/**/.env.ps1
# Excepción: los de LP2 contienen EMBEDDINGS_API_KEY
labs/lp2-01-aca-deploy/.env
labs/lp2-01-aca-deploy/.env.ps1
labs/lp2-02-aca-manage/.env
labs/lp2-02-aca-manage/.env.ps1
*.pem
*.key
.claude/settings.local.json


# Zips descargados del curso (duplican los PDF/docx sueltos); los de labs/ sí se versionan
*.zip
!labs/**/*.zip
docs/Links*.txt
*.docx

# Transcripciones de clase (solo local; se extrae el contenido a docs/, nunca se publican)
*transcript*.txt

# Entornos virtuales y cachés de Python
.venv/
venv/
__pycache__/
*.pyc

# Exportaciones de configuración de apps (llevan IDs, principal e IPs)
app-config.yaml
*-config.yaml

# Temporales de trabajo (nunca salir del repo)
tmp/
import os
import uuid
from typing import Optional
import psycopg
from azure.identity import DefaultAzureCredential

# Azure Database for PostgreSQL scope for Entra authentication
POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"

def get_connection():
    """Create a database connection using Entra authentication."""
    credential = DefaultAzureCredential()
    token = credential.get_token(POSTGRES_SCOPE)

    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname="agent_memory",
        user=os.en
… [recortado, 7270 caracteres]
```
</details>


### 🤖 Claude · 17:19 UTC

Starter descargado y revisado. Antes de que lo lances, preparo el lab en el repo (README, `.gitignore` y registro de la sesión):


**🔧 Bash** — Ignorar .env de LP5 (llevan token)

```text
python3 - <<'EOF'
p='.gitignore'
s=open(p).read()
s=s.replace("labs/lp2-02-aca-manage/.env.ps1\n","labs/lp2-02-aca-manage/.env.ps1\n# Excepción: LP5 guarda en PGPASSWORD un token de acceso de Entra\nlabs/lp5-*/.env\nlabs/lp5-*/.env.ps1\n")
open(p,'w').write(s)
EOF
grep -n lp5 .gitignore
```


<details><summary>Resultado</summary>

```text
16:labs/lp5-*/.env
17:labs/lp5-*/.env.ps1
```
</details>


**🔧 Write**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/README.md
```


**🔧 Write**

```text
~/claude/AI-200-Developing/sesiones/2026-11-10-sesion-06-postgresql.md
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/README.md (file state is current in your context — no need to Read it back)
```
</details>


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/sesiones/2026-11-10-sesion-06-postgresql.md (file state is current in your context — no need to Read it back)
```
</details>


### 🤖 Claude · 17:19 UTC

El lab ya está preparado en el repo:

- **Starter:** descargado y descomprimido en `labs/lp5-01-pg-agent-backend/`, con `README.md`.
- **Registro de la sesión:** `sesiones/2026-11-10-sesion-06-postgresql.md`.
- **`.gitignore`:** los `.env` de LP5 no se suben, porque `PGPASSWORD` guarda un token de acceso de Entra.

**Qué crea `azdeploy.py` (opción 1):** un PostgreSQL Flexible Server `Standard_B1ms` (Burstable), versión 16, con 32 GB. Pone tu usuario como admin de Entra y desactiva el acceso con contraseña. También añade una regla de firewall `AllowAll` (0.0.0.0–255.255.255.255).

**Aviso por adelantado:** este lab no tiene una opción solo con `az`. `psql` y el código Python se conectan directamente al servidor por el puerto **5432**, y el proxy de la empresa podría bloquearlo. Lo comprobaremos antes de usar `psql`. Si está bloqueado, el plan B es **Azure Cloud Shell**, que ya trae `psql` y `az`.

## Pasos 1–4 (en la terminal de `pc`)

**1. Login con las credenciales del lab**
```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az login --use-device-code
```
✅ Comprobación: `az account show --query "{sub:name, user:user.name}" -o table` → debe salir la suscripción y el usuario **del lab**. Si sale la de la empresa: `az account set --subscription <id del lab>`.

**2. Registrar el proveedor de PostgreSQL**
```bash
az provider register --namespace Microsoft.DBforPostgreSQL
```
✅ Comprobación: `az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv` → `Registered`. Si sale `Registering`, espera 1–2 minutos y vuelve a comprobarlo.

**3. Poner el resource group y la región en el script**
```bash
sed -i 's/<your-resource-group-name>/rg-ai200-pg-agent/; s/<your-azure-region>/eastus/' azdeploy.py
```
✅ Comprobación: `head -6 azdeploy.py | grep -E '^(rg|location)'` → debe mostrar `rg = "rg-ai200-pg-agent"` y `location = "eastus"`. Si la plataforma te da un resource group ya creado, o no te deja crear grupos, pon el nombre de ese grupo en lugar de `rg-ai200-pg-agent`.

**4. Desplegar** (tarda de 5 a 10 minutos y tiene coste: el servidor se cobra mientras exista)
```bash
python3 azdeploy.py      # elige 1
```
✅ Resultado esperado al final:
```
PostgreSQL server created successfully
  Microsoft Entra administrator: <tu usuario del lab>
  Firewall rule: AllowAll
```
Si sale `Error: ... failed`, pégame la salida completa. Si el error dice que el nombre del servidor no se libera, sal del script, espera 5 minutos y vuelve a elegir la opción 1.

Pégame las salidas a medida que avances y las guardo saneadas en `salidas.md`. Mientras termina el despliegue, la Task 4 de la guía es completar las tres funciones de `agent_tools.py`.


## 🧑 Alumno · 17:25 UTC

<pasted_content id="1013">
Username
<email>


Temporary Access Pass
<redactado>
</pasted_content id="1013">


### 🤖 Claude · 17:25 UTC

No voy a guardar ese usuario y ese Temporary Access Pass en ningún fichero del repo, ni repetirlos. Tampoco hago yo el login: lo haces tú (y no hace falta que me pases credenciales, ni hoy ni en los próximos labs).

**Cómo usarlos en el paso 1:**
```bash
az login --use-device-code
```
1. El comando muestra una URL (`https://microsoft.com/devicelogin`) y un código.
2. Abre esa URL en el navegador (mejor en una ventana privada, para que no use tu cuenta de empresa) y escribe el código.
3. Inicia sesión con el **Username** del lab. Cuando te pida contraseña o método, usa el **Temporary Access Pass**.
4. Vuelve a la terminal. Si te enseña una lista de suscripciones, elige la del lab.

✅ Comprobación:
```bash
az account show --query "{sub:name, user:user.name}" -o table
```
Resultado esperado: en `user` debe salir `<email>` y en `sub` la suscripción del lab.
- Si sale tu cuenta de la empresa, haz `az logout` y repite el login en una ventana privada.
- Si sale el usuario correcto pero otra suscripción, lista las tuyas con `az account list -o table` y cambia con `az account set --subscription <id>`.

Cuando esto cuadre, sigue con el paso 2 (registrar el proveedor) y pégame la salida.


## 🧑 Alumno · 17:26 UTC

opassword temporal

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing$ az login 
A web browser has been opened at https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize. Please continue the login in the web browser. If no web browser is available or if the web browser fails to open, use device code flow with `az login --use-device-code`.

Retrieving tenants and subscriptions for the selection...

[Tenant and subscription selection]

No     Subscription name    Subscription ID                       Tenant
-----  -------------------  ------------------------------------  -------------
[1] *  XLabs-079            <guid>  Lab Directory

The default is marked with an *; the default tenant is 'Lab Directory' and subscription is 'XLabs-079' (<guid>).

Select a subscription and tenant (Type a number or Enter for no changes): 1

Tenant: Lab Directory
Subscription: XLabs-079 (<guid>)

[Announcements]
With the new Azure CLI login experience, you can select the subscription you want to use more easily. Learn more about it and its configuration at https://go.microsoft.com/fwlink/?linkid=2271236

If you encounter any problem, please open an issue at https://aka.ms/azclibug

[Warning] The login output has been updated. Please be aware that it no longer displays the full list of available subscriptions by default.

alumno@pc:~/claude/AI-200-Developing$ 
</pasted_content id="1013">


**🔧 Write**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/salidas.md
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/salidas.md (file state is current in your context — no need to Read it back)
```
</details>


### 🤖 Claude · 17:26 UTC

Sí, el Temporary Access Pass se escribe en la página de login donde iría la contraseña, y por lo que pegas ya ha funcionado. El login es correcto: el tenant es `Lab Directory` y la suscripción `XLabs-079`, que es la del lab y no la de la empresa. He guardado la salida en `labs/lp5-01-pg-agent-backend/salidas.md`, con el ID de la suscripción quitado.

Ahora estás en la raíz del repo. Sigue desde la carpeta del lab:

```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az provider register --namespace Microsoft.DBforPostgreSQL
```
✅ Comprobación:
```bash
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
```
Debe salir `Registered`. Si sale `Registering`, espera 1–2 minutos y vuelve a comprobarlo.

Después, paso 3 (resource group y región en el script):
```bash
sed -i 's/<your-resource-group-name>/rg-ai200-pg-agent/; s/<your-azure-region>/eastus/' azdeploy.py
head -6 azdeploy.py | grep -E '^(rg|location)'
```
Deben salir `rg = "rg-ai200-pg-agent"` y `location = "eastus"`.

Y paso 4: `python3 azdeploy.py` → opción `1`. Pégame las salidas.


## 🧑 Alumno · 17:27 UTC

antes de empezar explicame un poco la sesion de hoy el profesor aun no ha llegado asi voy entendiendo


**🔧 Bash** — Extraer texto de la presentación del módulo 05

```text
pdftotext -layout "docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf" - | grep -v '^\s*$' | head -400
```


<details><summary>Resultado</summary>

```text
AI-200T00A
 Develop AI solutions with
 Azure Database for PostgreSQL
© Copyright Microsoft Corporation. All rights reserved.
Agenda
• Build and query with Azure Database for PostgreSQL
• Implement vector search with Azure Database for PostgreSQL
• Optimize vector search in Azure Database for PostgreSQL
© Copyright Microsoft Corporation. All rights reserved.
  Module 1: Build and query with Azure
  Database for PostgreSQL
© Copyright Microsoft Corporation. All rights reserved.
Learning objectives
• Explain the architecture and key features of Azure Database for PostgreSQL
• Establish secure connections to PostgreSQL using Microsoft Entra
  authentication and TLS
• Create and manage database schemas including tables, indexes, and
  constraints
• Write efficient SQL queries for common data operations
• Integrate Azure Database for PostgreSQL into applications using Python
© Copyright Microsoft Corporation. All rights reserved.
Introduction
• Fully managed PostgreSQL on Azure
• Full community edition compatibility
• Handles patching, backups, and high availability automatically
• Compute and storage scale independently
• Built-in PgBouncer connection pooling
• JSONB for flexible schemas alongside relational data
• Extension ecosystem includes pgvector for AI vector search
© Copyright Microsoft Corporation. All rights reserved.
Explore Azure Database for PostgreSQL
Compute tiers:
• Burstable: dev/test, intermittent workloads
• General Purpose: production, steady performance

… [recortado, 21804 caracteres]
```
</details>


### 🤖 Claude · 17:27 UTC

# LP5 · Azure Database for PostgreSQL

Hoy se repite el esquema del jueves: el **mismo problema que con Cosmos DB** (guardar la memoria de un agente y hacer búsqueda vectorial para RAG), pero ahora sobre una base de datos **relacional**. Son 3 módulos con un lab cada uno, como en LP4.

| Módulo | Tema | Lab |
|---|---|---|
| 1 | Crear y consultar PostgreSQL (esquema, SQL, Python) | **Agent tool backend**: el que vas a lanzar ahora |
| 2 | Búsqueda vectorial con la extensión **pgvector** | Búsqueda de productos similares |
| 3 | Optimizar la búsqueda vectorial (parámetros, índices, escalado) | Ajustar el rendimiento |

## La idea de fondo: Cosmos DB frente a PostgreSQL
| | Cosmos DB (jueves) | PostgreSQL (hoy) |
|---|---|---|
| Modelo | Documentos JSON sin esquema fijo | Tablas con esquema, más columnas `JSONB` para la parte flexible |
| Coste | Por operación (RU) | Por tamaño del servidor (vCores) y horas encendido |
| Escalado | Particiones (partition key) | Vertical (más grande), y réplicas de lectura (hasta 5) |
| Vectores | Integrado (`VectorDistance`, DiskANN) | Extensión `pgvector` (índices IVFFlat y HNSW) |
| Integridad | La lleva la aplicación | La garantiza la base de datos: FK, `CHECK`, `UNIQUE` |

La presentación lo resume en una frase: *"no necesitas una base de datos vectorial aparte"*. Los embeddings van en la misma fila que los datos relacionales.

## Módulo 1: lo que verás en el primer lab
**El servicio (Flexible Server):** es un PostgreSQL gestionado; Azure se encarga de parches, backups (restauración a un punto concreto, hasta 35 días) y alta disponibilidad. Hay tres niveles de cómputo:
- **Burstable:** desarrollo y pruebas. Es el que crea el lab (`B1ms`).
- **General Purpose:** producción.
- **Memory Optimized:** índices grandes en memoria.

**Seguridad, con analogías de K8s:**
- **Autenticación con Entra ID:** no hay contraseña guardada; usas un *token* que caduca en unos 60 minutos. Es lo mismo que un token de ServiceAccount frente a un secreto estático. Por eso el `.env` del lab trae `PGPASSWORD` = token, y hay que renovarlo con la opción 3 del script si caduca.
- **TLS:** obligatorio. En producción se usa `sslmode=verify-full`, que además comprueba el certificado del servidor.
- **Red:** acceso público con reglas de firewall o acceso privado integrado en una VNet. El lab abre `AllowAll`, que **solo vale para un lab**.

**Esquema:** son decisiones típicas de examen.
- `BIGSERIAL` para IDs internos autoincrementales y `UUID` para IDs que salen fuera (el `session_id`).
- `JSONB` para metadatos con estructura variable. Es la **pregunta 1 del knowledge check**.
- `TIMESTAMPTZ` siempre para fechas, porque guarda la zona horaria.
- Restricciones en la propia base de datos: `NOT NULL`, `CHECK` (por ejemplo, `role` solo puede ser `user`, `assistant`, `system` o `tool`), `UNIQUE` y claves foráneas con `ON DELETE CASCADE` (si borras una conversación, se borran sus mensajes).

**SQL propio de PostgreSQL que verás en el código:**
- `INSERT … RETURNING id`: insertas y recibes el ID generado en la misma consulta.
- `ON CONFLICT … DO UPDATE` es un **upsert**: inserta, o actualiza si ya existe. Es idempotente, como un `kubectl apply`. Lo usa `save_task_state` para los *checkpoints* del agente, y **necesita una restricción `UNIQUE`** sobre esas columnas. La guía la crea en la Task 6, después de escribir el código: no te líes con el orden.
- **Keyset pagination:** para paginar se filtra por el último valor visto (`WHERE created_at < …`) en lugar de usar `OFFSET`, que se vuelve lento en tablas grandes.

**Python (psycopg 3):** consultas parametrizadas con `%s`, que evitan la inyección SQL, y **pool de conexiones**. Abrir una conexión cuesta entre 50 y 200 ms. Es la **pregunta 2 del knowledge check**: la respuesta es usar un `ConnectionPool`, ni abrir una conexión por mensaje ni mantener una sola global. En los niveles General Purpose y Memory Optimized, Azure trae **PgBouncer** integrado, que hace el pooling en el servidor.

## El lab 1 en una línea
Una base de datos `agent_memory` con 3 tablas:
- `conversations`: las sesiones del agente.
- `messages`: el historial de cada sesión.
- `task_checkpoints`: el estado de las tareas largas, para que el agente pueda continuar donde lo dejó.

Además, 3 funciones Python que serían las *tools* del agente para leer y escribir su memoria.

## Avance de los módulos 2 y 3
- **pgvector:** columnas `vector(1536)` y tres operadores de distancia: `<=>` coseno (el habitual para texto), `<->` euclídea (L2) y `<#>` producto interno negativo.
- **Índices vectoriales:**
  - **HNSW:** un grafo, con mejor *recall* (más del 99 %). Admite inserciones incrementales y sirve para cargas con muchas lecturas.
  - **IVFFlat:** agrupa los vectores en clusters. Se construye rápido y usa menos memoria; va bien para datos estáticos que se reconstruyen a menudo. Necesita datos previos para crearse.
- **Trampa de examen:** el índice solo se usa si su clase de operador coincide con el operador de la consulta. Por ejemplo, `vector_cosine_ops` va con `<=>`.
- **Ajustes:** `hnsw.ef_search` e `ivfflat.probes` (más valor = más *recall*, pero más lento), `EXPLAIN ANALYZE` para ver si se usa el índice, e índices B-tree en las columnas que se usan para filtrar.

## Lo que más te sirve de tu perfil
El servidor, la red, el firewall, TLS y el escalado son terreno de SysOps. Lo nuevo hoy es el **diseño del esquema y el SQL** (`JSONB`, `ON CONFLICT`, `RETURNING`) y la **elección del índice vectorial**. En los labs fíjate sobre todo en eso.

¿Quieres que guarde esta explicación como base de `docs/modulos/05-postgresql.md`? Luego la completaríamos con lo que diga el profesor y lo que midamos en los labs.


## 🧑 Alumno · 17:28 UTC

si crea una para cada seccion


**🔧 Bash** — Crear notas del LP5: índice y una por módulo

```text
cd ~/claude/AI-200-Developing/docs/modulos && cat > 05-postgresql.md <<'EOF'
# LP5 · Desarrollar soluciones de IA con Azure Database for PostgreSQL

Notas propias del día 6 (10/11/2026). Presentación del instructor: `docs/AI-200T00A-05_…pdf`; test: `docs/LP5 - Knowledge check.pdf`. Mismo problema que LP4 (memoria del agente + búsqueda vectorial para RAG), pero sobre una base de datos **relacional**.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Notas | Lab |
|---|---|---|---|
| 1 | Crear y consultar PostgreSQL (esquema, SQL, Python) | [05-1-postgresql-build-query.md](05-1-postgresql-build-query.md) | [LP5-01 · Agent tool backend](../../labs/lp5-01-pg-agent-backend/README.md) |
| 2 | Búsqueda vectorial con `pgvector` | [05-2-postgresql-vector-search.md](05-2-postgresql-vector-search.md) | [Guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html) |
| 3 | Optimizar la búsqueda vectorial | [05-3-postgresql-optimize.md](05-3-postgresql-optimize.md) | [Guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html) |

## Cosmos DB (LP4) frente a PostgreSQL (LP5)
| | Cosmos DB | PostgreSQL |
|---|---|---|
| Modelo | Documentos JSON sin esquema fijo | Tablas con esquema + `JSONB` para lo flexible |
| Coste | Por operación (RU) | Por tamaño del servidor (vCores) y horas encendido |
| Escalado | Horizontal por partition key | Vertical primero; después réplicas de lectura (hasta 5) |
| Vectores | Integrado (`VectorDistance`, `flat`/`quantizedFlat`/`diskANN`) | Extensión `pgvector` (IVFFlat, HNSW) |
| Integridad | En la aplicación | En la BD: FK, `CHECK`, `UNIQUE` |
| Acceso sin claves | RBAC de datos de Cosmos | Admin/usuario de Entra + token como contraseña |

Idea de la presentación: con `pgvector` **no hace falta una base de datos vectorial aparte**; el embedding va en la misma fila que los datos.

## Lo nuevo para un perfil SysOps/K8s
Servidor, red, firewall, TLS y escalado son terreno conocido. Lo nuevo: **diseño del esquema y SQL propio de PostgreSQL** (`JSONB`, `ON CONFLICT`, `RETURNING`) y **elección del índice vectorial**.
EOF
cat > 05-1-postgresql-build-query.md <<'EOF'
# LP5 · Módulo 1 · Crear y consultar Azure Database for PostgreSQL

Volver al [índice de LP5](05-postgresql.md). Lab: [LP5-01 · Agent tool backend](../../labs/lp5-01-pg-agent-backend/README.md).

## El servicio: 
… [recortado, 11144 caracteres]
```


<details><summary>Resultado</summary>

```text
01-alojamiento-contenedores.md
02-container-apps.md
03-aks.md
04-cosmosdb.md
05-1-postgresql-build-query.md
05-2-postgresql-vector-search.md
05-3-postgresql-optimize.md
05-postgresql.md
```
</details>


**🔧 Bash** — Marcar respuestas como no oficiales y anotar en la sesión

```text
sed -i 's/^## Knowledge check del módulo (presentación)$/## Knowledge check del módulo (presentación)\n> Respuestas razonadas por nosotros (la presentación no las trae): confirmarlas con el profesor./' 05-[123]-*.md && grep -c "confirmarlas" 05-[123]-*.md && sed -i 's#^- Rama `dia-06-2026-11-10` y PDF del día en `docs/`.#&\n- Notas del LP5 en `docs/modulos/`: índice `05-postgresql.md` y una por módulo (`05-1`, `05-2`, `05-3`), a partir de la presentación.#' ../../sesiones/2026-11-10-sesion-06-postgresql.md && grep -n "05-1" ../../sesiones/*06*.md
```


<details><summary>Resultado</summary>

```text
05-3-postgresql-optimize.md:1
05-1-postgresql-build-query.md:1
05-2-postgresql-vector-search.md:1
7:- Notas del LP5 en `docs/modulos/`: índice `05-postgresql.md` y una por módulo (`05-1`, `05-2`, `05-3`), a partir de la presentación.
[This command modified 1 file you've previously read: ../../sesiones/2026-11-10-sesion-06-postgresql.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 17:29 UTC

He creado una nota por cada módulo, más un índice, en `docs/modulos/`:

| Fichero | Contenido |
|---|---|
| `05-postgresql.md` | Índice del LP5: agenda con enlaces a las notas y a los labs, Cosmos DB frente a PostgreSQL, y qué es nuevo para tu perfil |
| `05-1-postgresql-build-query.md` | Módulo 1: Flexible Server y sus niveles, conexión segura (Entra, TLS, red), diseño del esquema, SQL propio (`JSONB`, `RETURNING`, `ON CONFLICT`, keyset pagination) y psycopg 3 |
| `05-2-postgresql-vector-search.md` | Módulo 2: pgvector, operadores y su clase de índice, IVFFlat frente a HNSW (con su equivalente en Cosmos), ciclo de vida de los embeddings y RAG |
| `05-3-postgresql-optimize.md` | Módulo 3: parámetros del servidor y de pgvector, elección del índice, organización de los datos, escalado y PgBouncer |

- Cada nota termina con las preguntas de repaso que trae la presentación. Las respuestas las he deducido yo, porque la presentación no las incluye; las he marcado para confirmarlas con el profesor.
- He apuntado las notas en el registro de la sesión.
- Cuando el profesor explique y hagamos los labs, añadiré a cada nota sus comentarios y los datos que midamos, como hicimos con Cosmos DB.

Aún no he hecho commit; lo haré en el cierre del día. Cuando quieras, sigue con el lab en el paso 2: `az provider register --namespace Microsoft.DBforPostgreSQL`.


## 🧑 Alumno · 17:34 UTC

<pasted_content id="1013">
===============================
Planning Martes 10 de Noviembre
===============================
18:00-18:20 Test LP4 (6 preguntas)
18:20-19:20 LP 5 (PostgreSQL) - Mod 1,2 y 3 (Queries/Vector Search/Optimize)  *Teoría
19:20-19:50 Lab 12: [AI-200-LP05M01] Build and query with Azure Database for PostgreSQL
19:50-20:10 BREAK
20:10-21:50 Lab 13: [AI-200-LP05M02] Implement vector search with Azure Database for PostgreSQL
            Lab 14: [AI-200-LP05M03] Optimize performance, indexing, and scaling for Azure Database for PostgreSQL
21:50-22:00 *Hacer Test LP5 (6 preguntas)
</pasted_content id="1013">

 llego profesor clase de hoy que ya conociamos


**🔧 Edit**

```text
~/claude/AI-200-Developing/sesiones/2026-11-10-sesion-06-postgresql.md
```


<details><summary>Resultado</summary>

```text
The file ~/claude/AI-200-Developing/sesiones/2026-11-10-sesion-06-postgresql.md has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>


**🔧 Bash** — Poner número de lab de la plataforma en el README

```text
cd ~/claude/AI-200-Developing && sed -i '1s/.*/# Lab LP5-01 · Build an agent tool backend (plataforma: Lab 12 · AI-200-LP05M01)/' labs/lp5-01-pg-agent-backend/README.md && head -1 labs/lp5-01-pg-agent-backend/README.md && ls docs/tests/
```


<details><summary>Resultado</summary>

```text
# Lab LP5-01 · Build an agent tool backend (plataforma: Lab 12 · AI-200-LP05M01)
lp1-knowledge-check.md
[This command modified 1 file you've previously read: labs/lp5-01-pg-agent-backend/README.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 17:35 UTC

He añadido el planning de hoy al registro de la sesión. Hoy el lab 12 de la plataforma es nuestro `lp5-01-pg-agent-backend`, y lo he anotado en su README. Los labs 13 y 14 serán `lp5-02` y `lp5-03`.

El orden de la tarde es este:

1. **18:00 · Test LP4 (6 preguntas):** el del jueves, sobre Cosmos DB. Repasa `docs/modulos/04-cosmosdb.md`. En el último quiz fallaste dos temas, así que míralos antes:
   - **Coste de escritura frente a lectura:** escribir cuesta más RU que leer. Con `diskANN` medimos unas 4,7 veces lo que cuesta `flat`, y a 500 vectores `flat` es el más barato también leyendo.
   - **Query cross-partition:** una consulta sin partition key se reparte entre todas las particiones (fan-out) y es la más cara. La más barata es la lectura puntual (`id` + partition key, unas 1 RU).
2. **18:20 · Teoría LP5:** ya tienes las notas en `docs/modulos/05-*.md`. Si el profesor dice algo que no está ahí, pásamelo y lo añado. También me sirve para confirmar las respuestas de las preguntas de repaso.
3. **19:20 · Lab 12:** retoma en el paso 2 (`az provider register --namespace Microsoft.DBforPostgreSQL`). El despliegue tarda de 5 a 10 minutos.

   Si te deja, lanza los pasos 2 a 4 ya durante la teoría para tener el servidor listo a las 19:20. Ten en cuenta que el servidor cuesta dinero desde que se crea, aunque al ser una suscripción del lab el coste es bajo.


## 🧑 Alumno · 17:35 UTC

tengo permiso


### 🤖 Claude · 17:35 UTC

Pues adelante. Lánzalo ahora y así el servidor estará listo para las 19:20. Son los pasos 2 a 4, desde la carpeta del lab:

```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# Paso 2: registrar el proveedor de PostgreSQL
az provider register --namespace Microsoft.DBforPostgreSQL
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
```
✅ Debe salir `Registered`. Si sale `Registering`, espera 1–2 minutos y repite el `az provider show`.

```bash
# Paso 3: resource group y región en el script
sed -i 's/<your-resource-group-name>/rg-ai200-pg-agent/; s/<your-azure-region>/eastus/' azdeploy.py
head -6 azdeploy.py | grep -E '^(rg|location)'
```
✅ Deben salir `rg = "rg-ai200-pg-agent"` y `location = "eastus"`.

```bash
# Paso 4: desplegar (elige 1)
python3 azdeploy.py
```
✅ Tarda de 5 a 10 minutos. Al final debe salir:
```
PostgreSQL server created successfully
  Microsoft Entra administrator: <email>
  Firewall rule: AllowAll
```
Después pulsa Enter y deja el menú abierto, que en la Task 5 se usan las opciones 2 y 3.

**Si algo falla:**
- **Error de cuota o de región no permitida en `eastus`:** pásame el mensaje y probamos con otra región, por ejemplo `westeurope`.
- **`AuthorizationFailed` al crear el resource group:** la plataforma probablemente te da uno ya creado. Mira cuál con `az group list -o table` y pon ese nombre en `azdeploy.py`.

Mientras sigues la teoría, pégame las salidas cuando puedas.


## 🧑 Alumno · 17:37 UTC

<pasted_content id="1013">
4. Module 01: Build an agent tool backend on Azure Database for PostgreSQL
Task 1: Download project starter files and deploy Azure services


In this section you download the project starter files and use a script to deploy the necessary services to your Azure subscription. The PostgreSQL server deployment takes a few minutes to complete.


Open Edge browser from the taskbar, and enter the following URL to download the starter file. The file will be saved in your default download location.
https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-build-agent-python.zip

Open File Explorer from the taskbar, right click on the downloaded file then select Extract all.. and then click Extract.

Launch Visual Studio Code (VS Code) from the Desktop and select File > Open Folder... in the menu, select Downloads folder then choose the folder containing the project files and then click Select folder.
📝 Note: If prompted, select Yes, i trust the authors.


The project contains a deployment script. Open the Python script (azdeploy.py). Change the two values at the top of the script to meet your needs, then save your changes.
📝 Note: Do not change anything else in the script except the SKU configuration.

rg = "ai200rg"  # Resource Group name
location = "centralus"   # Azure region for the resources
ⓘ Important: You must also update the SKU to comply with lab subscription policy. Find this section in the create_postgres_server() function and change it:

# Change from:
"--sku-name", "Standard_B1ms",
"--tier", "Burstable",

# To:
"--sku-name", "Standard_D2ds_v4",
"--tier", "GeneralPurpose",
📝 Note: For the Azure region, enter centralus. The SKU must be Standard_D2ds_v4 (GeneralPurpose tier) to comply with lab subscription policies.


In the menu bar select Terminal > New Terminal to open a terminal window in VS Code.
💡 Tip: If Terminal tab is not visible, select the three dots (... > Terminal > New Terminal)


Run the following command to login to your Azure account. Answer the prompts to select your Azure account and subscription for the exercise.
az login

When prompted, select Work or school account, click Continue and then follow the instructions to sign into Azure using the credentials from the lab Info tab. When prompted to Sign in to all apps.., select No, this app only.
📝 Note: If you do not see the Sign in window, minimize the Visual Studio Code to see it.


When prompted in the terminal to Select a subscription, press Enter.

Run the following command to ensure your subscription has the necessary resource provider for the exercise.
az provider register --namespace Microsoft.DBforPostgreSQL

Make sure you are in the root directory of the project and run the following command in the terminal to launch the deployment script.
python azdeploy.py

When the script menu appears, enter 1 to launch the Create PostgreSQL server with Entra authentication option. This creates the server with Entra-only authentication enabled.
📝 Note: Deployment can take 5-10 minutes to complete.

ⓘ Important: Leave the terminal running the deployment open for the duration of the exercise. You can move on to the next task of the exercise while the deployment continues in the terminal.
</pasted_content id="1013">


<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az provider register --namespace Microsoft.DBforPostgreSQL
az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
Registered
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ sed -i 's/<your-resource-group-name>/rg-ai200-pg-agent/; s/<your-azure-region>/eastus/' azdeploy.py
head -6 azdeploy.py | grep -E '^(rg|location)'
rg = "rg-ai200-pg-agent"  # Resource Group name
location = "eastus"   # Azure region for the resources
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">

python3 azdeploy.py lanzado


**🔧 Bash** — Localizar las líneas del SKU

```text
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend && grep -n '"--sku-name"\|"--tier"' azdeploy.py
```


<details><summary>Resultado</summary>

```text
339:            "--sku-name", "Standard_B1ms",
340:            "--tier", "Burstable",
```
</details>


**🔧 Bash** — Documentar los valores obligatorios de la plataforma

```text
python3 - <<'EOF'
p='README.md'; s=open(p).read()
s=s.replace("- Resource group: `rg-ai200-pg-agent`; región `eastus` (como en LP4).",
"- **Valores obligatorios de la plataforma** (política de la suscripción del lab, no vienen en la guía pública): resource group `ai200rg`, región `centralus` y SKU `Standard_D2ds_v4` con tier `GeneralPurpose` (en vez de `Standard_B1ms` / `Burstable`). Más caro que Burstable, pero trae PgBouncer integrado.\n- Primer intento con `rg-ai200-pg-agent` / `eastus` / `B1ms` (los valores habituales del repo): cancelado al ver la instrucción de la plataforma.")
s=s.replace("| Síntoma | Causa | Arreglo |\n|---|---|---|",
"| Síntoma | Causa | Arreglo |\n|---|---|---|\n| La guía de la plataforma exige otro RG, región y SKU | Política de la suscripción del lab (la guía pública no lo dice) | Leer siempre la guía de la plataforma antes de editar `azdeploy.py`; `sed` de `rg`, `location`, `--sku-name` y `--tier` |")
s=s.replace("az group delete --name rg-ai200-pg-agent --no-wait --yes\naz group exists --name rg-ai200-pg-agent","az group delete --name ai200rg --no-wait --yes\naz group exists --name ai200rg")
open(p,'w').write(s)
EOF
cat >> salidas.md <<'EOF'

## 2. Registro del proveedor
ʼʼʼtext
$ az provider register --namespace Microsoft.DBforPostgreSQL
$ az provider show -n Microsoft.DBforPostgreSQL --query registrationState -o tsv
Registered
ʼʼʼ
**Qué mirar:** `Registered` a la primera: la suscripción del lab ya lo tenía registrado.

## 3. Primera edición de `azdeploy.py` (descartada)
ʼʼʼtext
$ head -6 azdeploy.py | grep -E '^(rg|location)'
rg = "rg-ai200-pg-agent"  # Resource Group name
location = "eastus"   # Azure region for the resources
ʼʼʼ
**Qué mirar:** la edición funcionó, pero la guía de la plataforma exige `ai200rg`, `centralus` y `Standard_D2ds_v4`/`GeneralPurpose` por política. Se canceló el despliegue para corregirlo.
EOF
grep -n "ai200rg" README.md | head
```


<details><summary>Resultado</summary>

```text
38:- **Valores obligatorios de la plataforma** (política de la suscripción del lab, no vienen en la guía pública): resource group `ai200rg`, región `centralus` y SKU `Standard_D2ds_v4` con tier `GeneralPurpose` (en vez de `Standard_B1ms` / `Burstable`). Más caro que Burstable, pero trae PgBouncer integrado.
48:az group delete --name ai200rg --no-wait --yes
49:az group exists --name ai200rg   # esperado: false (tarda unos minutos)
```
</details>


### 🤖 Claude · 17:37 UTC

⚠️ **Para el despliegue ahora (Ctrl+C).** La guía de la plataforma exige unos valores que no están en la guía pública, porque la suscripción del lab tiene una política que los impone:

| | Lanzado | Lo que pide la plataforma |
|---|---|---|
| Resource group | `rg-ai200-pg-agent` | `ai200rg` |
| Región | `eastus` | `centralus` |
| SKU | `Standard_B1ms` / `Burstable` | `Standard_D2ds_v4` / `GeneralPurpose` |

Con los valores que has lanzado, lo más probable es que la política deniegue el servidor (`RequestDisallowedByPolicy`) después de unos minutos de espera. Es culpa mía: te di los valores habituales del repo sin tener la guía de la plataforma.

**1. Cancela y mira qué se ha llegado a crear**
```bash
# Ctrl+C en el script
az group list --query "[].{name:name, location:location}" -o table
az postgres flexible-server list --query "[].{name:name, rg:resourceGroup, state:state}" -o table
```
✅ Lo normal es que exista `rg-ai200-pg-agent` (vacío) y ningún servidor. Si existe ese grupo **y no tiene servidor**, bórralo:
```bash
az group delete --name rg-ai200-pg-agent --yes --no-wait
```
Si sí aparece un servidor en `rg-ai200-pg-agent`, pégame la salida antes de borrar nada.

**2. Corrige el script**
```bash
sed -i 's/^rg = "rg-ai200-pg-agent"/rg = "ai200rg"/; s/^location = "eastus"/location = "centralus"/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```
✅ Esperado:
```
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
339:            "--sku-name", "Standard_D2ds_v4",
340:            "--tier", "GeneralPurpose",
```
Si alguna línea no ha cambiado, pégame la salida.

**3. Relanza:** `python3 azdeploy.py` → opción `1`.

Ventaja del cambio: `GeneralPurpose` cuesta más que `Burstable`, pero trae **PgBouncer** integrado, que es justo lo que explica el módulo 3.

He dejado los valores de la plataforma y el incidente documentados en `labs/lp5-01-pg-agent-backend/README.md` y `salidas.md`. A partir de ahora, pégame la guía de la plataforma de cada lab antes de editar el script.


## 🧑 Alumno · 17:45 UTC

preparame esto 

<pasted_content id="1013">
5. Module 01: Build an agent tool backend on Azure Database for PostgreSQL
Task 2: Complete the tool function app


In this section you complete the agent_tools.py file by adding functions that an AI agent can call to persist and retrieve state. These functions serve as the agent's interface to the database. The test_workflow.py script, which you run later in this exercise, imports these functions to demonstrate how an agent would use them.


Open the agent-backend/agent_tools.py file in VS Code.
💡 Tip: To maintain proper code indentation, paste the code flush with the left margin (column 1), select all of the pasted lines, and press Tab to align the block with the BEGIN / END markers. Press Shift+Tab to outdent if needed.


Search for the BEGIN CREATE CONVERSATION FUNCTION comment and add the following code directly after the comment. This function creates a new conversation record with a unique session ID and stores optional metadata as JSONB.
def create_conversation(user_id: str, metadata: dict = None) -> dict:
    """Create a new conversation and return its details."""
    session_id = uuid.uuid4()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (session_id, user_id, metadata)
                VALUES (%s, %s, %s)
                RETURNING id, session_id, started_at
                """,
                (str(session_id), user_id, psycopg.types.json.Json(metadata or {}))
            )
            row = cur.fetchone()
            conn.commit()
            return {
                "conversation_id": row[0],
                "session_id": str(row[1]),
                "started_at": row[2].isoformat()
            }

Search for the BEGIN RETRIEVE CONVERSATION HISTORY FUNCTION comment and add the following code directly after the comment. This function retrieves messages from a conversation, ordered chronologically.
def get_conversation_history(conversation_id: int, limit: int = 50) -> list:
    """Retrieve recent messages from a conversation."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, role, content, created_at, metadata
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (conversation_id, limit)
            )
            rows = cur.fetchall()
            return [
                {
                    "id": row[0],
                    "role": row[1],
                    "content": row[2],
                    "created_at": row[3].isoformat(),
                    "metadata": row[4]
                }
                for row in reversed(rows)  # Return in chronological order
            ]

Search for the BEGIN TASK CHECKPOINT FUNCTIONS comment and add the following code directly after the comment. This function uses an upsert pattern to save or update task state, allowing the agent to resume interrupted tasks.
def save_task_state(conversation_id: int, task_name: str, status: str, checkpoint_data: dict) -> dict:
    """Save or update a task checkpoint."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO task_checkpoints (conversation_id, task_name, status, checkpoint_data)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (conversation_id, task_name)
                DO UPDATE SET
                    status = EXCLUDED.status,
                    checkpoint_data = EXCLUDED.checkpoint_data,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, updated_at
                """,
                (conversation_id, task_name, status, psycopg.types.json.Json(checkpoint_data))
            )
            # Note: The ON CONFLICT requires a unique constraint we need to add
            row = cur.fetchone()
            conn.commit()
            return {
                "checkpoint_id": row[0],
                "updated_at": row[1].isoformat()
            }

Save your changes to the agent_tools.py file.

Take a few minutes to review all of the code in the app.
Next, you finalize the Azure resource deployment.
</pasted_content id="1013">

 continuamos


**🔧 Read**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py
```


<details><summary>Resultado</summary>

```text
1	import os
2	import uuid
3	from typing import Optional
4	import psycopg
5	from azure.identity import DefaultAzureCredential
6	
7	# Azure Database for PostgreSQL scope for Entra authentication
8	POSTGRES_SCOPE = "https://ossrdbms-aad.database.windows.net/.default"
9	
10	def get_connection():
11	    """Create a database connection using Entra authentication."""
12	    credential = DefaultAzureCredential()
13	    token = credential.get_token(POSTGRES_SCOPE)
14	
15	    return psycopg.connect(
16	        host=os.environ["DB_HOST"],
17	        dbname="agent_memory",
18	        user=os.environ["DB_USER"],
19	        password=token.token,
20	        sslmode="require"
21	    )
22	# BEGIN CREATE CONVERSATION FUNCTION
23	
24	
25	
26	# END CREATE CONVERSATION FUNCTION
27	
28	def store_message(conversation_id: int, role: str, content: str, metadata: dict = None) -> dict:
29	    """Store a message in a conversation."""
30	    with get_connection() as conn:
31	        with conn.cursor() as cur:
32	            cur.execute(
33	                """
34	                INSERT INTO messages (conversation_id, role, content, metadata)
35	                VALUES (%s, %s, %s, %s)
36	                RETURNING id, created_at
37	                """,
38	                (conversation_id, role, content, psycopg.types.json.Json(metadata or {}))
39	            )
40	            row = cur.fetchone()
41	            conn.commit()
42	            return {
43	                "message_id": row[0],
44	                
… [recortado, 2755 caracteres]
```
</details>


### 🤖 Claude · 17:45 UTC

Las marcas están en la columna 0, así que las funciones van sin sangría. Las inserto:


**🔧 Edit**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py
```


**🔧 Edit**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py
```


**🔧 Edit**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py
```


<details><summary>Resultado</summary>

```text
The file ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>


<details><summary>Resultado</summary>

```text
The file ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>


<details><summary>Resultado</summary>

```text
The file ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py has been updated successfully. (file state is current in your context — no need to Read it back)
```
</details>


**🔧 Bash** — Comprobar sintaxis y funciones definidas

```text
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend && python3 -I -m py_compile agent_tools.py && echo SINTAXIS_OK && grep -n "^def " agent_tools.py && grep -n "import\|from agent_tools" test_workflow.py | head; rm -rf __pycache__
```


<details><summary>Resultado</summary>

```text
SINTAXIS_OK
10:def get_connection():
23:def create_conversation(user_id: str, metadata: dict = None) -> dict:
45:def store_message(conversation_id: int, role: str, content: str, metadata: dict = None) -> dict:
65:def get_conversation_history(conversation_id: int, limit: int = 50) -> list:
93:def save_task_state(conversation_id: int, task_name: str, status: str, checkpoint_data: dict) -> dict:
119:def get_task_state(conversation_id: int, task_name: str) -> Optional[dict]:
1:from agent_tools import (
```
</details>


### 🤖 Claude · 17:45 UTC

Ya he metido la Task 2 en `labs/lp5-01-pg-agent-backend/agent-backend/agent_tools.py`: las tres funciones están pegadas tal cual vienen en la guía, entre sus marcas `BEGIN`/`END`, sin sangría (las marcas están en la columna 0).

✅ Comprobación (desde `labs/lp5-01-pg-agent-backend`):
```bash
python3 -m py_compile agent-backend/agent_tools.py && echo OK
grep -n "^def " agent-backend/agent_tools.py
```
Lo esperado es `OK` y 6 funciones: `get_connection`, `create_conversation`, `store_message`, `get_conversation_history`, `save_task_state` y `get_task_state`. Si sale `IndentationError`, pégame la línea que indica.

**Qué hace cada función** (es lo que explicó la teoría del módulo 1):

| Función | Patrón SQL | Detalle |
|---|---|---|
| `create_conversation` | `INSERT … RETURNING` | Genera un `uuid4` como `session_id` y guarda el metadata como `JSONB` con `Json(...)`. Devuelve el `id` generado sin hacer otra consulta. |
| `get_conversation_history` | `ORDER BY created_at DESC LIMIT %s` + `reversed()` | Coge los **N más recientes** y los devuelve en orden cronológico, que es lo que necesita el modelo como contexto. |
| `save_task_state` | Upsert con `ON CONFLICT … DO UPDATE` + `EXCLUDED` | `EXCLUDED` es la fila que intentabas insertar. Si se repite la tarea, actualiza en lugar de duplicar, y así el agente puede retomarla. **Falla si no existe el `UNIQUE (conversation_id, task_name)`**, que se crea más adelante en `psql`. |

Todas usan `%s` (parámetros, nunca concatenar strings, para evitar inyección SQL) y `get_connection()`, que pide un token de Entra con `DefaultAzureCredential`. Es decir, en Python también se entra sin contraseña.

**Siguiente paso (Task 3, terminar el despliegue):** ¿cómo va el script relanzado con `ai200rg`/`centralus`/`Standard_D2ds_v4`? Cuando termine la opción 1, elige `2` (estado) y luego `3` (genera `.env`). Pégame las dos salidas. Antes de usar `psql`, comprobaremos que el puerto 5432 sale por el proxy.


## 🧑 Alumno · 17:48 UTC

<pasted_content id="1013">

Checking/creating resource group 'rg-ai200-pg-agent'...
Resource group created: rg-ai200-pg-agent

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
Error: Create PostgreSQL Flexible Server failed (exit code 1).
ERROR: The location is restricted from performing this operation.

Press Enter to continue...
</pasted_content id="1013">


**🔧 Bash** — Guardar la salida del fallo por región

```text
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend && cat >> salidas.md <<'EOF'

## 4. Primer `azdeploy.py` opción 1 (con `eastus`, falla)
ʼʼʼtext
Checking/creating resource group 'rg-ai200-pg-agent'...
Resource group created: rg-ai200-pg-agent

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
Error: Create PostgreSQL Flexible Server failed (exit code 1).
ERROR: The location is restricted from performing this operation.
ʼʼʼ
**Qué mirar:** el resource group sí se crea (la política no limita la región de los grupos), pero el servidor no: la suscripción del lab solo permite PostgreSQL en `centralus`. Confirma que hay que usar los valores de la guía de la plataforma. El nombre del servidor (`psql-agent-` + 8 caracteres del SHA-1 de tu object id) no depende del RG ni de la región: el relanzamiento usará el mismo.
EOF
sed -i 's#| La guía de la plataforma exige otro RG, región y SKU |#| `ERROR: The location is restricted from performing this operation.` con `eastus` (el RG sí se crea) | Política de la suscripción del lab: PostgreSQL solo en `centralus` | Borrar el RG vacío y relanzar con los valores de la plataforma |\n&#' README.md && grep -c restricted README.md
```


<details><summary>Resultado</summary>

```text
1
[This command modified 2 files you've previously read: salidas.md, README.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 17:49 UTC

Esta salida es del **primer intento** (con `rg-ai200-pg-agent` y `eastus`), y confirma lo que esperábamos: `The location is restricted` es la política del lab, que solo permite crear PostgreSQL en `centralus`. El resource group sí se llegó a crear, pero el servidor no. La he guardada en `salidas.md`.

Hay que limpiar y relanzar:

**1. Sal del script:** pulsa Enter y luego `4`.

**2. Borra el resource group vacío**
```bash
az resource list -g rg-ai200-pg-agent -o table
az group delete --name rg-ai200-pg-agent --yes --no-wait
```
Lo esperado es que el `az resource list` no muestre nada y que el grupo esté vacío. Si sale algún recurso, pégamelo antes de borrar.

**3. Corrige el script** (si no lo hiciste ya)
```bash
sed -i 's/^rg = "rg-ai200-pg-agent"/rg = "ai200rg"/; s/^location = "eastus"/location = "centralus"/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```
✅ Esperado:
```
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
339:            "--sku-name", "Standard_D2ds_v4",
340:            "--tier", "GeneralPurpose",
```

**4. Relanza:** `python3 azdeploy.py` → `1`. En la cabecera del menú tiene que aparecer `Resource Group: ai200rg` y `Location: centralus`; si no, sal con `4` y revisa el paso 3.

El servidor se seguirá llamando `psql-agent-dc48980e`, porque el nombre sale de tu usuario y no del grupo ni de la región. ✅ El final esperado es `PostgreSQL server created successfully`, después de 5 a 10 minutos.

**5. Comprueba que el grupo viejo se ha borrado** (tarda 1–2 minutos):
```bash
az group exists --name rg-ai200-pg-agent
```
Debe salir `false`.


## 🧑 Alumno · 17:49 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az resource list -g rg-ai200-pg-agent -o table
az group delete --name rg-ai200-pg-agent --yes --no-wait

alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


**🔧 Bash** — Ver si el script ya tiene los valores de la plataforma

```text
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```


<details><summary>Resultado</summary>

```text
5:rg = "rg-ai200-pg-agent"  # Resource Group name
6:location = "eastus"   # Azure region for the resources
339:            "--sku-name", "Standard_B1ms",
340:            "--tier", "Burstable",
```
</details>


### 🤖 Claude · 17:49 UTC

La salida es correcta: el grupo estaba vacío y el borrado ya está lanzado.

He mirado el script y **todavía tiene los valores viejos** (`rg-ai200-pg-agent`, `eastus`, `Standard_B1ms`). Corrígelo antes de relanzar:

```bash
sed -i 's/^rg = "rg-ai200-pg-agent"/rg = "ai200rg"/; s/^location = "eastus"/location = "centralus"/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
```
✅ Esperado:
```
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
339:            "--sku-name", "Standard_D2ds_v4",
340:            "--tier", "GeneralPurpose",
```

Después relanza con `python3 azdeploy.py` y elige `1`. Comprueba que en la cabecera del menú aparecen `Resource Group: ai200rg` y `Location: centralus`.

En un par de minutos, comprueba el borrado con `az group exists --name rg-ai200-pg-agent`; debe salir `false`.


## 🧑 Alumno · 17:49 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ sed -i 's/^rg = "rg-ai200-pg-agent"/rg = "ai200rg"/; s/^location = "eastus"/location = "centralus"/; s/"Standard_B1ms"/"Standard_D2ds_v4"/; s/"--tier", "Burstable"/"--tier", "GeneralPurpose"/' azdeploy.py
grep -nE '^(rg|location) =|"--sku-name"|"--tier"' azdeploy.py
5:rg = "ai200rg"  # Resource Group name
6:location = "centralus"   # Azure region for the resources
339:            "--sku-name", "Standard_D2ds_v4",
340:            "--tier", "GeneralPurpose",
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


### 🤖 Claude · 17:50 UTC

Perfecto, las cuatro líneas son las que pide la plataforma. Ahora relanza:

```bash
python3 azdeploy.py      # elige 1
```
✅ En la cabecera del menú debes ver `Resource Group: ai200rg` y `Location: centralus`. Al final, después de 5 a 10 minutos, debe salir:
```
PostgreSQL server created successfully
  Microsoft Entra administrator: <email>
  Firewall rule: AllowAll
```

**Si algo falla:**
- Si sale `RequestDisallowedByPolicy` o `restricted`, pégame el mensaje completo.
- Si se queda esperando con `Waiting for Azure to release server name`, es normal tras el intento fallido: el script espera hasta 5 minutos a que Azure libere el nombre. Si se agota el tiempo, espera 5 minutos más y repite la opción 1.

Mientras se crea, adelanto la siguiente comprobación: ver si el proxy de la empresa deja salir el puerto **5432**. Sin eso, ni `psql` ni `test_workflow.py` funcionarán. Cuando termine el despliegue, en **otra terminal**:
```bash
timeout 5 bash -c '</dev/tcp/psql-agent-dc48980e.postgres.database.azure.com/5432' && echo "5432 ABIERTO" || echo "5432 BLOQUEADO"
```
- Si sale `5432 ABIERTO`, seguimos con `psql` en local.
- Si sale `5432 BLOQUEADO`, pasamos a **Azure Cloud Shell**, que ya trae `psql`, Python y tu sesión de `az`, y subimos ahí la carpeta `agent-backend`.


## 🧑 Alumno · 17:50 UTC

<pasted_content id="1013">
=====================================================================
    Azure Database for PostgreSQL Deployment Menu
=====================================================================
Resource Group: ai200rg
Server Name: psql-agent-dc48980e
Location: centralus
=====================================================================
1. Create PostgreSQL server with Entra authentication
2. Check deployment status
3. Retrieve connection info and access token
4. Exit
=====================================================================
Please select an option (1-4): 1
</pasted_content id="1013">


<pasted_content id="1013">

Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...



</pasted_content id="1013">


**🔧 Bash** — Guardar la salida del relanzamiento

```text
cat >> salidas.md <<'EOF'

## 5. `azdeploy.py` opción 1 con los valores de la plataforma
ʼʼʼtext
Resource Group: ai200rg
Server Name: psql-agent-dc48980e
Location: centralus
...
Please select an option (1-4): 1

Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
ʼʼʼ
**Qué mirar:** la cabecera ya muestra `ai200rg` / `centralus`. Esta vez no sale `Waiting for Azure to release server name`: el intento anterior falló antes de reservar el nombre, así que estaba libre.
EOF
echo ok
```


<details><summary>Resultado</summary>

```text
ok
```
</details>


### 🤖 Claude · 17:50 UTC

Va bien: la cabecera muestra `ai200rg` y `centralus`, el grupo se ha creado y el servidor se está creando. No ha tenido que esperar a que se liberara el nombre porque el intento anterior falló antes de reservarlo. He guardado la salida en `salidas.md`.

Ahora toca esperar de 5 a 10 minutos. Mientras tanto, si quieres ver cómo avanza desde **otra terminal** (solo lectura):
```bash
az resource show -g ai200rg -n psql-agent-dc48980e --resource-type Microsoft.DBforPostgreSQL/flexibleServers --query properties.state -o tsv
```
✅ Pasará por `Provisioning` o `Updating` hasta llegar a `Ready`. Si devuelve un error `ResourceNotFound`, el servidor aún no se ha registrado: vuelve a probar en un minuto.

Cuando el script muestre `PostgreSQL server created successfully`, pégamelo y lanza la prueba del puerto 5432:
```bash
timeout 5 bash -c '</dev/tcp/psql-agent-dc48980e.postgres.database.azure.com/5432' && echo "5432 ABIERTO" || echo "5432 BLOQUEADO"
```

Ten en cuenta que el script no termina al crear el servidor. Después configura el admin de Entra, desactiva la contraseña y crea la regla `AllowAll`, y espera a `Ready` entre cada paso.


## 🧑 Alumno · 17:53 UTC

mientras se construlle en postgres tengo un grupo de agentes de claude en un repo para gestionar la infraestructura de mi empresa. lo utilizan diferentes uusaiores y me gustaria guardar los aprendizajes que quedan en memoria de los agentes en base de dato ahora lo guardo en un skill dentro del repo que guarda en el repo los aprendizajes de los agentes


### 🤖 Claude · 17:53 UTC

Tiene sentido, y además es justo lo que estás montando en el lab de hoy: `conversations` / `messages` / `task_checkpoints` son la memoria de un agente guardada en PostgreSQL. No puedo ver ese repo de tu empresa, así que te doy la recomendación general; si me enseñas la skill actual la ajustamos.

## ¿Merece la pena salir de git?
| | Skill que escribe en el repo (lo actual) | Base de datos |
|---|---|---|
| Varios usuarios a la vez | Conflictos de merge, ramas desincronizadas | Escrituras concurrentes sin conflictos |
| Auditoría y revisión | Excelente: diff, PR, `git blame` | Hay que montarla (columna `author`, historial, estado) |
| Buscar | `grep` | SQL, filtros por agente/etiqueta y búsqueda semántica con pgvector |
| Infraestructura | Ninguna | Un servidor que mantener, pagar y proteger |
| Cuando crece | El contexto se llena de ficheros | El agente pide solo lo relevante |

**Mi recomendación:** si sois varios usuarios escribiendo a la vez y ya tenéis conflictos o aprendizajes que no llegan a todos, la BD compensa. Si sois 2–3 personas y funciona, mejora antes la skill (por ejemplo, un fichero por aprendizaje para evitar conflictos). Lo que no conviene perder al pasar a BD es la **revisión humana** que hoy te da la PR.

## Diseño propuesto (lo que ves hoy en los labs, aplicado a tu caso)
**1. Tabla con upsert, como `save_task_state`:**
```sql
CREATE TABLE learnings (
  id          BIGSERIAL PRIMARY KEY,
  slug        TEXT NOT NULL UNIQUE,              -- clave para ON CONFLICT (upsert)
  agent       TEXT NOT NULL,                     -- qué agente lo aprendió
  type        TEXT NOT NULL CHECK (type IN ('feedback','project','reference','runbook')),
  title       TEXT NOT NULL,
  body        TEXT NOT NULL,
  tags        JSONB NOT NULL DEFAULT '[]',
  author      TEXT NOT NULL DEFAULT current_user, -- UPN de Entra: no se puede falsear
  status      TEXT NOT NULL DEFAULT 'proposed' CHECK (status IN ('proposed','approved','obsolete')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
  -- más adelante: embedding vector(1536) para búsqueda semántica (módulo 2 de hoy)
);
```
- **`author DEFAULT current_user`:** con autenticación Entra cada usuario entra con su propio token, así que la autoría la pone la base de datos y no el agente.
- **`status`:** sustituye a la PR. El agente propone (`proposed`), un responsable aprueba, y los agentes solo leen los `approved`.
- **Permisos:** grupos de Entra mapeados a roles de PostgreSQL. Por ejemplo, `agents_rw` para `INSERT`/`UPDATE` de `proposed` y `reviewers` para aprobar.

**2. Integración con Claude: un servidor MCP en lugar de la skill que escribe ficheros.**
- Expone 2 o 3 *tools*: `search_learnings(query, agent, tags)`, `save_learning(...)` y `mark_obsolete(slug)`.
- Lo registras en el `.mcp.json` del repo y así lo tienen todos los usuarios.
- La skill o las definiciones de los agentes pasan a decir: "al empezar, busca; al aprender algo, guárdalo".
- Es exactamente el patrón del lab: funciones Python sobre psycopg con `DefaultAzureCredential`.

**3. La red: la trampa que vas a ver hoy mismo.**
Si cada usuario se conecta directamente a PostgreSQL por el puerto **5432**, el proxy de la empresa probablemente lo bloquee, y además tendrías que abrir el firewall (nunca `AllowAll` como en el lab). Es más robusto **poner una API delante**:
```
Claude (cada usuario) ──HTTPS 443 + token Entra──▶ servidor MCP remoto en Container Apps (LP2)
                                                    └──▶ PostgreSQL con acceso privado (VNet), solo Entra
```
La base de datos queda sin exposición pública, solo hay que abrir el 443, y la API valida quién llama.

**4. Coste.** Para esto basta con un **Burstable B1ms** (unos pocos euros al mes más el almacenamiento). El `GeneralPurpose` del lab sobra para este uso.

## Por dónde empezaría
1. Migrar los aprendizajes actuales del repo a la tabla con un script, guardando el `author` a partir de `git log`.
2. Un servidor MCP local (stdio) contra un PostgreSQL de pruebas, para validar las *tools* con 1–2 agentes.
3. Después, pasarlo a remoto (Container Apps + red privada) y añadir pgvector cuando haya volumen.

**Ojo:** este repo del curso es **público**, así que aquí no guardo nada de la infraestructura de tu empresa. Si quieres, escribo este diseño en versión genérica, sin datos de la empresa, en `notas/memoria-agentes-postgresql.md`, como aplicación práctica del LP5. ¿Lo hago? Y si me pasas cómo es ahora la skill (formato de los ficheros, cuántos usuarios y agentes), afino el esquema.

Mientras tanto, ¿cómo va el despliegue?


## 🧑 Alumno · 17:53 UTC

seria un caso de uso de postgres con vector?


### 🤖 Claude · 17:54 UTC

Sí, es un caso de uso típico. Pero **el vector no sustituye a los filtros ni a la búsqueda por texto, los complementa**, y en tu caso ese matiz importa.

## Dónde aporta el vector
El agente encuentra aprendizajes **por significado**, no por palabras exactas:
- El agente pregunta: *"el pod no arranca porque no puede bajar la imagen"*.
- El aprendizaje guardado dice: *"ImagePullBackOff en AKS: falta el rol AcrPull en la identidad del kubelet"*.

Comparten pocas palabras, pero los embeddings son cercanos y la búsqueda vectorial lo encuentra. `grep` no.

## Dónde NO basta
En infraestructura gran parte del conocimiento son **literales**: códigos de error (`RequestDisallowedByPolicy`), nombres de recursos, versiones, flags. Ahí la búsqueda vectorial es floja y gana la búsqueda **léxica** (full-text de PostgreSQL). Por eso lo correcto es la **búsqueda híbrida** del módulo 2: vector + full-text, fusionados con RRF, y con filtros SQL (`agent`, `status = 'approved'`, `tags`) delante.

```sql
-- Parte vectorial: 10 candidatos más cercanos, solo aprobados y del agente que pregunta
SELECT slug, title, embedding <=> $1 AS distancia
FROM learnings
WHERE status = 'approved' AND agent = $2
ORDER BY embedding <=> $1
LIMIT 10;
-- Se combina con un ranking full-text (to_tsvector/ts_rank) mediante RRF
```

## Decisiones aplicando lo que verás hoy
| Decisión | Para tu caso | Por qué |
|---|---|---|
| Operador | `<=>` (coseno) con índice `vector_cosine_ops` | Lo habitual con texto; la clase de operador del índice tiene que coincidir con el operador |
| ¿Índice? | **Ninguno al principio** | Con cientos o pocos miles de filas, el escaneo exacto es rápido y da recall del 100 %. Es lo que vimos en Cosmos: `flat` ganaba a 500 vectores |
| Cuando crezca | **HNSW**, no IVFFlat | Recibes inserciones sueltas continuas. HNSW admite inserciones incrementales; IVFFlat necesita los datos previos y se degrada sin reconstruirlo |
| Actualizar un aprendizaje | Regenerar su embedding (o una columna `stale` y un proceso en segundo plano) | Si cambia el texto, el vector viejo ya no lo representa |
| Cambiar de modelo de embeddings | Columna paralela (`embedding_v2`) y cambio cuando esté validada | Patrón del módulo 2, como un blue/green |

## El coste real: los embeddings
pgvector solo guarda y compara vectores. **Generarlos** requiere un modelo, por ejemplo `text-embedding-3-small` en Azure OpenAI o Foundry: una llamada al guardar cada aprendizaje y otra por cada búsqueda. Es barato, pero añade una dependencia más (endpoint, permisos, cuota).

## Cuándo merece la pena
- **Decenas o pocos cientos de aprendizajes:** filtros SQL + full-text, o incluso cargar todos los `approved` del agente en el contexto. **Sin vector.**
- **Cientos o miles, redactados por usuarios distintos con palabras distintas:** **ahí entra pgvector.** La tabla ya está preparada: es añadir `embedding vector(1536)` sin rehacer nada.

Mi consejo: empieza con PostgreSQL relacional y full-text, deja prevista la columna `embedding` y actívala cuando el volumen lo pida. Así la búsqueda vectorial resuelve un problema que ya tienes, en lugar de añadir complejidad antes de tiempo.

Esto encaja muy bien como ejemplo práctico en `docs/modulos/05-2-postgresql-vector-search.md`. ¿Lo añado junto con la nota genérica que te propuse?


## 🧑 Alumno · 17:57 UTC

era solo una consulta conceptual, puedoe deployar en kube y luego publicar en netscope un puerto de una postgress. tu que creees que podria guarar de la gestion diaria de un agente eln postgres? el aprendizaje? postgres free trae vecot?


### 🤖 Claude · 17:57 UTC

Tres respuestas cortas.

## 1. PostgreSQL en Kubernetes y publicado con Netskope
Sí, es viable y encaja con tu perfil.

- **Despliegue:** usa un operador, no un StatefulSet hecho a mano. **CloudNativePG** es el estándar: gestiona réplicas, failover, backups a blob storage y restauración a un punto concreto, que es lo que Azure te da hecho en Flexible Server.
- **Publicación:** Netskope Private Access publica aplicaciones TCP privadas, así que el puerto 5432 puede llegar a los usuarios sin abrirlo a Internet. Además resuelve el bloqueo del proxy que tenemos hoy.

Lo que pierdes respecto a Azure:
- **Autenticación con Entra.** En un PostgreSQL propio no hay tokens de Entra. Quedan usuario y contraseña (en un Secret o Key Vault) o certificados de cliente. Netskope controla *quién llega* al puerto, pero dentro de la BD necesitas igualmente un usuario por persona para que `author = current_user` siga siendo fiable.
- **Operación.** Backups, actualizaciones de versión y monitorización pasan a ser tuyos. Para un uso interno pequeño compensa si ya tienes clusters y te sobra capacidad.

## 2. Qué guardaría de la gestión diaria de un agente
El aprendizaje es lo más valioso, pero no lo único. Por orden de utilidad:

| Qué | Para qué | Equivalente en el lab de hoy |
|---|---|---|
| **Aprendizajes** (feedback, runbooks, "esto falla por X") | Que lo que aprende un agente con un usuario lo sepan todos | — |
| **Registro de acciones**: qué comando o cambio, en qué recurso, quién lo pidió, resultado | **Auditoría.** En infraestructura es casi obligatorio saber qué tocó el agente y por orden de quién | `messages` con `role = 'tool'` |
| **Checkpoints de tareas largas** (migraciones, upgrades de cluster) | Retomar donde se quedó si se corta la sesión, sin repetir pasos | `task_checkpoints` + `ON CONFLICT` |
| **Aprobaciones**: el agente propone, un humano aprueba | Control de cambios sin depender de una PR | `status` en `learnings` |
| **Incidencias resueltas**: síntoma → causa → solución | Es lo que más se beneficia de la búsqueda vectorial: síntomas descritos con palabras distintas | Módulo 2 |

**Lo que NO guardaría:** el estado del inventario o de la infraestructura (para eso está la fuente real: `az`, la API de K8s, el IaC, y una copia en la BD se queda desactualizada), las conversaciones completas indefinidamente (ponles una política de retención) ni secretos o salidas sin sanear.

## 3. ¿El PostgreSQL gratuito trae vectores?
**pgvector es gratis** (licencia de PostgreSQL, código abierto), pero **no viene en el núcleo de PostgreSQL**: es una extensión que hay que tener instalada y activar con `CREATE EXTENSION vector;`.
- **Imagen oficial `postgres`:** no la trae. Usa `pgvector/pgvector:pg16` o una imagen que la incluya.
- **CloudNativePG:** sus imágenes de PostgreSQL suelen incluir pgvector, pero compruébalo en la versión que uses.
- **Azure Flexible Server:** viene disponible, pero hay que permitirla en el parámetro `azure.extensions` antes del `CREATE EXTENSION`. Seguramente lo veas en el lab 13.

Comprobación en cualquier PostgreSQL:
```sql
SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name = 'vector';
```
- Si **no sale ninguna fila**, la extensión no está en la imagen o el servidor.
- Si sale con `installed_version` vacío, está disponible pero sin activar: falta el `CREATE EXTENSION vector;`.

¿Cómo va el despliegue del servidor?


## 🧑 Alumno · 17:59 UTC

y como se configura claude enviar a postgress


### 🤖 Claude · 17:59 UTC

Hay dos piezas, y conviene usar las dos: un **servidor MCP**, para que el agente *decida* leer y guardar aprendizajes, y **hooks**, para registrar las acciones *automáticamente* sin depender de que el modelo se acuerde.

## 1. Servidor MCP: las *tools* de memoria del agente
Es un proceso pequeño que expone funciones al agente; Claude Code lo arranca y lo usa como una herramienta más. Recomiendo **escribir uno propio con 2 o 3 tools concretas** en lugar de un MCP genérico de PostgreSQL que permita SQL libre: así el agente no puede hacer un `DELETE` ni leer otras tablas.

```python
# mcp/agent_memory_server.py  (pip install "mcp[cli]" psycopg[binary])
import psycopg
from psycopg.types.json import Json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-memory")

def conn():
    # Lee PGHOST, PGUSER, PGDATABASE, PGPASSWORD/.pgpass del entorno (libpq)
    return psycopg.connect("")

@mcp.tool()
def search_learnings(query: str, agent: str | None = None, limit: int = 10) -> list[dict]:
    """Busca aprendizajes aprobados por texto. Llamar ANTES de actuar."""
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT slug, title, body, tags
            FROM learnings
            WHERE status = 'approved'
              AND (%s::text IS NULL OR agent = %s)
              AND to_tsvector('spanish', title || ' ' || body) @@ plainto_tsquery('spanish', %s)
            LIMIT %s""", (agent, agent, query, limit))
        return [dict(zip(("slug", "title", "body", "tags"), r)) for r in cur.fetchall()]

@mcp.tool()
def save_learning(slug: str, agent: str, type: str, title: str, body: str, tags: list[str]) -> dict:
    """Guarda o actualiza un aprendizaje (queda 'proposed' hasta que un humano lo apruebe)."""
    with conn() as c, c.cursor() as cur:
        cur.execute("""
            INSERT INTO learnings (slug, agent, type, title, body, tags)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET
              body = EXCLUDED.body, tags = EXCLUDED.tags,
              status = 'proposed', updated_at = CURRENT_TIMESTAMP
            RETURNING id, status""", (slug, agent, type, title, body, Json(tags)))
        return dict(zip(("id", "status"), cur.fetchone()))

if __name__ == "__main__":
    mcp.run()   # stdio: Claude Code lo lanza como subproceso
```
Fíjate en que `save_learning` es exactamente el `save_task_state` del lab: upsert con `ON CONFLICT` y `RETURNING`.

**Registro en el repo** (`.mcp.json` en la raíz, versionado, y así lo tienen todos los usuarios):
```json
{
  "mcpServers": {
    "agent-memory": {
      "command": "python3",
      "args": ["mcp/agent_memory_server.py"],
      "env": { "PGHOST": "${PGHOST}", "PGUSER": "${PGUSER}", "PGDATABASE": "agent_memory" }
    }
  }
}
```
- Los `${VAR}` se expanden con el entorno de cada usuario: **cada uno conecta con su propio usuario de PostgreSQL** y la contraseña va en su `~/.pgpass`, **nunca en el repo**.
- La primera vez, Claude Code pide aprobar el servidor del proyecto. Con `/mcp` ves si está conectado.
- Las tools aparecen como `mcp__agent-memory__search_learnings` y `mcp__agent-memory__save_learning`. Puedes permitirlas sin confirmación en `.claude/settings.json` → `permissions.allow`.

**Instrucciones a los agentes** (en cada `.claude/agents/*.md` o en `CLAUDE.md`). Es lo que hoy hace tu skill, pero contra la BD:
```markdown
- Antes de una tarea, llama a `search_learnings` con el síntoma o el recurso.
- Cuando el usuario te corrija o resuelvas algo no obvio, llama a `save_learning`
  (sin secretos, IPs ni nombres de clientes).
```

## 2. Hooks: el registro automático de acciones (auditoría)
Los aprendizajes los decide el modelo. **La auditoría no debe depender del modelo.** Un hook `PostToolUse` se ejecuta siempre después de cada herramienta y recibe por stdin un JSON con `session_id`, `tool_name`, `tool_input` y `tool_response`:

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Bash|mcp__.*",
        "hooks": [ { "type": "command", "command": "python3 .claude/hooks/log_action.py" } ] }
    ]
  }
}
```
`log_action.py` lee ese JSON, **sanea** el contenido (quita tokens, contraseñas y salidas largas) y hace un `INSERT INTO agent_actions (...)` con el usuario, la sesión, el comando y el resultado.
- Si la BD no responde, el script **no debe bloquear al agente**: que escriba en un fichero local y salga con código 0.
- Con el matcher `Bash|mcp__.*` registras los comandos y las llamadas MCP. Los `Read` no los registres: generan mucho ruido.

## Resumen
| Necesidad | Mecanismo | Quién lo dispara |
|---|---|---|
| Consultar y guardar aprendizajes | Servidor MCP propio + instrucciones en los agentes | El modelo |
| Auditar qué ha hecho el agente | Hook `PostToolUse` | Claude Code, siempre |
| Retomar tareas largas | Tool `save_checkpoint` en el mismo MCP | El modelo |
| Revisión humana | `status = 'proposed'` → un responsable aprueba | Persona |

Tu skill actual se queda casi igual: solo cambia "escribe en el fichero X" por "llama a `save_learning`".

Volviendo al lab: ¿ha terminado ya el `azdeploy.py`?


## 🧑 Alumno · 18:00 UTC

que es un hook conozvo skill y role (settings.json)


### 🤖 Claude · 18:00 UTC

Un **hook** es un comando (un script) que **Claude Code ejecuta automáticamente** cuando ocurre un evento: antes de usar una herramienta, después, al empezar la sesión, al terminar… No lo decide el modelo. Lo ejecuta el programa siempre, igual que un *admission webhook* o un hook `preStop` en Kubernetes.

## Las cuatro piezas que tienes en el repo
| Pieza | Qué es | Quién decide usarla | Analogía K8s | En este repo |
|---|---|---|---|---|
| **`CLAUDE.md` / memoria** | Instrucciones que siempre están en el contexto | El modelo las *lee* e intenta cumplirlas | Documentación del equipo | "Primero `az`", "nunca subir `github.mb`" |
| **Skill** | Un paquete de instrucciones (y scripts) que se carga **cuando hace falta**: al escribir `/aprender` o cuando la tarea encaja | El modelo o tú con `/nombre` | Un runbook que sacas para una tarea concreta | `/aprender`, `/quiz-lab` |
| **Agente (rol)** | Un "Claude especialista" con su propio prompt, herramientas y modelo, al que se delegan tareas | El modelo delega, o se lo pides tú | Un pod con su ServiceAccount: tiene sus propios permisos | `oscar` (`.claude/agents/oscar.md`) |
| **Hook** | Un comando que se ejecuta **siempre** en un evento | **Claude Code**, sin el modelo | Admission webhook / `postStart` / `preStop` | Ninguno todavía |

La diferencia clave: **CLAUDE.md, las skills y los agentes son peticiones al modelo, y el modelo puede equivocarse u olvidarlas. El hook es determinista: se ejecuta siempre.**

## `settings.json`
Es la configuración de Claude Code: el *qué puede hacer y qué se ejecuta*, no el *cómo debe pensar*. Tiene tres niveles:
- `~/.claude/settings.json`: el tuyo, para todos los proyectos.
- `.claude/settings.json`: del proyecto, va al repo y lo comparte el equipo. Ya tienes uno, con los permisos de `mkdir`.
- `.claude/settings.local.json`: del proyecto, pero solo tuyo (está en el `.gitignore`).

Dentro van, entre otras cosas, `permissions` (qué comandos se permiten sin preguntar), `env` y **`hooks`**.

## Eventos de hook más útiles
| Evento | Cuándo | Uso típico |
|---|---|---|
| `PreToolUse` | Antes de ejecutar una herramienta. **Puede bloquearla** (código de salida 2) | Impedir comandos peligrosos |
| `PostToolUse` | Después de la herramienta | Auditoría, formatear el código tras editarlo |
| `UserPromptSubmit` | Cuando envías un mensaje | Añadir contexto, filtrar datos sensibles |
| `SessionStart` / `SessionEnd` | Al abrir o cerrar la sesión | Cargar contexto / guardar un resumen |
| `Stop` | Cuando el agente termina de responder | Comprobaciones finales |

El script recibe por stdin un JSON con el evento: `tool_name`, `tool_input` (por ejemplo, el comando de Bash), `session_id`, etc.

## Un ejemplo que te sirve hoy mismo
En la memoria tienes la regla *"nunca tocar `~/.kube-<empresa>`"*. Ahora mismo depende de que el modelo la recuerde. Con un hook se cumple siempre:

```json
// .claude/settings.json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash|Read|Edit|Write",
        "hooks": [ { "type": "command",
                     "command": "grep -q 'kube-<empresa>' && { echo 'Bloqueado: ~/.kube-<empresa> está prohibido' >&2; exit 2; } || exit 0" } ] }
    ]
  }
}
```
- El hook recibe la llamada en JSON por stdin. Si contiene `kube-<empresa>`, sale con código 2.
- Con el código 2, **Claude Code cancela la herramienta** y le pasa al modelo el mensaje de error.
- El modelo ya no puede saltarse la regla, ni por error ni por un prompt malicioso.

Esa es la idea de fondo para tus agentes de infraestructura:
- **Skills y agentes** sirven para que trabajen bien.
- **Hooks** sirven para garantizar lo que *no puede fallar*: auditoría de acciones, bloqueo de comandos destructivos y no tocar credenciales.

¿Quieres que lo apunte como nota del curso o que configuremos ese hook en este repo? (Cambiaría `.claude/settings.json`, así que antes te enseño el cambio.)

Y el despliegue de PostgreSQL, ¿ha terminado?


## 🧑 Alumno · 18:04 UTC

<pasted_content id="1013">

Checking/creating resource group 'ai200rg'...
Resource group created: ai200rg

Creating Azure Database for PostgreSQL Flexible Server 'psql-agent-dc48980e'...
This may take several minutes...
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: <email>
  Firewall rule: AllowAll

Press Enter to continue...
</pasted_content id="1013">

 si


**🔧 Bash** — Guardar salida y probar el puerto 5432

```text
cat >> salidas.md <<'EOF'

## 6. Fin de la opción 1
ʼʼʼtext
PostgreSQL server created. Checking server status...
Configuring Microsoft Entra administrator...
Disabling password authentication...
Creating firewall rule...
PostgreSQL server created successfully
  Microsoft Entra administrator: <email>
  Firewall rule: AllowAll
ʼʼʼ
**Qué mirar:** las cuatro fases del script (crear → admin de Entra → desactivar contraseña → firewall). El admin de Entra es el usuario del lab: el mismo que hará de `DB_USER`.
EOF
timeout 5 bash -c '</dev/tcp/psql-agent-dc48980e.postgres.database.azure.com/5432' && echo "5432 ABIERTO" || echo "5432 BLOQUEADO"
```


<details><summary>Resultado</summary>

```text
5432 ABIERTO
```
</details>


### 🤖 Claude · 18:04 UTC

El puerto 5432 sale sin problema: puedes usar `psql` en local. Guardo lo de hooks y skills como nota:


**🔧 Write**

```text
~/claude/AI-200-Developing/notas/claude-code-hooks-skills-agentes.md
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/notas/claude-code-hooks-skills-agentes.md (file state is current in your context — no need to Read it back)
```
</details>


### 🤖 Claude · 18:04 UTC

El servidor está listo: se ha creado, tiene tu usuario del lab como admin de Entra, la contraseña desactivada y la regla de firewall `AllowAll`. He guardado la salida en `salidas.md`.

**Puerto 5432:** lo he probado yo desde esta misma máquina y sale **ABIERTO**. Aquí el proxy no lo bloquea, así que `psql` y `test_workflow.py` funcionarán en local y no hace falta Cloud Shell.

He guardado la explicación de hooks, skills y agentes en `notas/claude-code-hooks-skills-agentes.md`, junto con el diseño de memoria de agentes en PostgreSQL. El hook de `kube-<empresa>` queda solo como propuesta: **no** he tocado `.claude/settings.json`.

## Task 3: terminar el despliegue (en el menú del script)
1. Pulsa Enter y elige **`2`** (estado). ✅ Esperado:
   ```
   Status: Ready
   PostgreSQL server is ready
   Public access: Enabled
   Entra administrator: <email>
   Firewall rule: AllowAll
   ```
2. Pulsa Enter y elige **`3`** (datos de conexión y token). ✅ Debe terminar con `Environment variables saved to .env and .env.ps1`.
3. Enter y **`4`** para salir.

Después carga las variables:
```bash
source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
```
✅ Esperado: `token cargado` y `psql-agent-dc48980e.postgres.database.azure.com postgres <email>`.

`PGPASSWORD` es un token: compruebo que existe sin mostrarlo. Caduca en aproximadamente una hora; si `psql` falla luego por autenticación, vuelve a ejecutar la opción 3 y otra vez `source .env`.

Pégame las salidas de las opciones 2 y 3. El siguiente paso es la Task 4: crear el esquema con `psql`.


## 🧑 Alumno · 18:05 UTC

<pasted_content id="1013">
Checking deployment status...

PostgreSQL Server (psql-agent-dc48980e):
  Status: Ready
  PostgreSQL server is ready
  Public access: Enabled
  Entra administrator: <email>
  Firewall rule: AllowAll

Press Enter to continue...
</pasted_content id="1013">

 2

<pasted_content id="1013">

Retrieving connection information...
Retrieving access token...

PostgreSQL Connection Information
===========================================================
Host: psql-agent-dc48980e.postgres.database.azure.com
Database: postgres
User: <email>
Password: (Entra token - expires in ~1 hour)

Environment variables saved to .env and .env.ps1

Press Enter to continue...
</pasted_content id="1013">

 3


**🔧 Bash** — Verificar que .env está ignorado y guardar salidas

```text
git check-ignore -v .env .env.ps1; cat >> salidas.md <<'EOF'

## 7. Opción 2 (estado) y opción 3 (conexión)
ʼʼʼtext
PostgreSQL Server (psql-agent-dc48980e):
  Status: Ready
  PostgreSQL server is ready
  Public access: Enabled
  Entra administrator: <email>
  Firewall rule: AllowAll
ʼʼʼ
ʼʼʼtext
PostgreSQL Connection Information
===========================================================
Host: psql-agent-dc48980e.postgres.database.azure.com
Database: postgres
User: <email>
Password: (Entra token - expires in ~1 hour)

Environment variables saved to .env and .env.ps1
ʼʼʼ
**Qué mirar:** `Ready` + admin de Entra + firewall: los tres requisitos para conectar. `Database: postgres` es la BD por defecto; `agent_memory` se crea después con `psql`. La "contraseña" es un token de Entra (`az account get-access-token --resource-type oss-rdbms`) que caduca en ~1 h: el `.env` **no se versiona** (excepción en `.gitignore`). Comprobación previa del puerto desde `pc`: `5432 ABIERTO` (el proxy no lo bloquea, a diferencia de `kubectl` contra AKS).
EOF
echo ok
```


<details><summary>Resultado</summary>

```text
.gitignore:16:labs/lp5-*/.env	.env
.gitignore:17:labs/lp5-*/.env.ps1	.env.ps1
ok
```
</details>


### 🤖 Claude · 18:05 UTC

Las dos salidas son las esperadas: el servidor está `Ready` y ya tienes el `.env`. He comprobado que git ignora `.env` y `.env.ps1` (las reglas de la línea 16 y 17 del `.gitignore`), así que el token no se subirá. Salidas guardadas en `salidas.md`.

Sal del menú (Enter y luego `4`) y carga las variables:
```bash
source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
```
✅ Esperado: `token cargado` y `psql-agent-dc48980e.postgres.database.azure.com postgres <email>`.

Después conecta con `psql` para probar:
```bash
psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
```
Dentro de `psql`:
```sql
SELECT version();
```
✅ Esperado: una línea que empieza por `PostgreSQL 16.x … on x86_64-pc-linux-gnu`, con el prompt `postgres=>`.

**Si algo falla:**
- **`password authentication failed`:** el token no se ha cargado o ha caducado. Repite la opción 3 y `source .env`.
- **`timeout`:** pégamelo. No debería pasar, porque el puerto está abierto.

Pégame la siguiente tarea de la guía de la plataforma (la del esquema, con los `CREATE TABLE`). Así uso el SQL exacto que pide la plataforma, que ya hemos visto que puede diferir de la guía pública.


## 🧑 Alumno · 18:06 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres <email>
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres <email>
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
Dentro de psql:
SELECT version();
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=> 
</pasted_content id="1013">

 curioso no lo para netscope


**🔧 Bash** — Guardar la salida de la conexión psql

```text
cat >> salidas.md <<'EOF'

## 8. `source .env` y primera conexión con `psql`
ʼʼʼtext
$ source .env
$ [ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres <email>
$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=>
ʼʼʼ
**Qué mirar:** entra sin pedir contraseña (`psql` toma el token de `PGPASSWORD`) y la conexión va cifrada con TLS 1.3. Netskope no la corta: su cliente suele dirigir solo el tráfico web (80/443) al proxy con inspección TLS, y PostgreSQL negocia TLS dentro de su propio protocolo en el 5432. `kubectl` contra AKS sí va por 443, la inspección rompe el TLS/certificado de cliente del API server y por eso se bloquea (depende de la configuración de *steering* de la empresa).
EOF
echo ok
```


<details><summary>Resultado</summary>

```text
ok
```
</details>


### 🤖 Claude · 18:07 UTC

Ya estás dentro de PostgreSQL: el prompt `postgres=>` y la línea `SSL connection (protocol: TLSv1.3…)` lo confirman. El `SELECT version();` no llegó a ejecutarse, porque las líneas se pegaron en la shell antes de que `psql` arrancara. Escríbelo ahora en el prompt `postgres=>`:
```sql
SELECT version();
```
✅ Esperado: `PostgreSQL 16.x on x86_64-pc-linux-gnu, compiled by …`.

## Por qué Netskope no lo para y `kubectl` sí
No puedo ver la configuración de Netskope de tu empresa, pero el patrón encaja con su comportamiento habitual:

| | `kubectl` → AKS | `psql` → PostgreSQL |
|---|---|---|
| Puerto | 443 (HTTPS) | 5432 |
| ¿Lo captura Netskope? | Sí: normalmente solo dirige al proxy el tráfico **web** (80/443) | Normalmente no: el tráfico que no es web suele salir directo |
| TLS | TLS puro desde el primer byte. Netskope lo **inspecciona** (se hace pasar por el servidor con su propio certificado), y eso rompe la autenticación con certificado de cliente del API server | TLS negociado **dentro del protocolo de PostgreSQL** (primero un `SSLRequest`, luego TLS). Un proxy web no lo entiende ni lo intercepta |

Conclusión práctica:
- **Lo que va por 443 a APIs** (AKS, y a veces llamadas con certificados propios) pasa por Netskope y puede fallar. Por eso usamos `az aks command invoke`.
- **Los puertos de bases de datos** (5432, 1433, 6380 de Redis…) en tu caso salen directos. El LP6 de Redis también debería funcionar en local.
- **Ojo:** esto depende de cómo esté configurado el reenvío de tráfico en Netskope. Si la empresa pasa a capturar todo el tráfico, este acceso dejaría de funcionar. Para la memoria de agentes que me comentabas, la vía estable sigue siendo publicarlo a propósito con Netskope Private Access, no depender de que se cuele.

Lo he documentado en `salidas.md`.

Pégame el resultado del `SELECT version();` y la siguiente tarea de la guía de la plataforma (crear la BD `agent_memory` y las tablas).


## 🧑 Alumno · 18:08 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .env
[ -n "${PGPASSWORD:-}" ] && echo "token cargado"; echo "$DB_HOST $DB_NAME $DB_USER"
token cargado
psql-agent-dc48980e.postgres.database.azure.com postgres <email>
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
Dentro de psql:
SELECT version();
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=> 



</pasted_content id="1013">


### 🤖 Claude · 18:08 UTC

Es la misma salida de antes, y todavía no aparece el resultado del `SELECT`. Puede que en el búfer de `psql` haya quedado a medias el texto pegado (`Dentro de psql:`). Límpialo y vuelve a lanzar la consulta, **escribiéndola tú en el prompt `postgres=>`**:

```sql
\r
SELECT version();
```
- `\r` vacía el búfer de consulta de `psql`. Si no había nada, responde `Query buffer reset (cleared).` y no pasa nada.
- ✅ Esperado:
  ```
                                               version
  -------------------------------------------------------------------------------------------------
   PostgreSQL 16.x on x86_64-pc-linux-gnu, compiled by gcc ...
  (1 row)
  ```

**Si no sale eso:**
- Si el prompt cambia a `postgres->` (con guion en vez de `=`), `psql` está esperando que termines una sentencia. Pulsa Ctrl+C y repite.
- Si sale `ERROR: syntax error at or near "Dentro"`, era el texto pegado. Ignóralo y lanza de nuevo `SELECT version();`.

Después pégame la siguiente tarea de la guía de la plataforma (crear `agent_memory` y las tablas), y la ejecutamos dentro de esta misma sesión de `psql`.


## 🧑 Alumno · 18:08 UTC

<pasted_content id="1013">
postgres=> \r
SELECT version();
Query buffer reset (cleared).
\r: extra argument "SELECT" ignored
\r: extra argument "version();" ignored
postgres=> 
</pasted_content id="1013">


### 🤖 Claude · 18:09 UTC

El búfer ya está limpio, pero `psql` ha leído las dos líneas como si fueran una sola, porque los comandos con barra (`\r`) se comen el resto de la línea como argumentos. No pasa nada.

Ahora escribe **solo** esto y pulsa Enter:
```sql
SELECT version();
```
✅ Esperado: una fila con `PostgreSQL 16.x on x86_64-pc-linux-gnu, compiled by …` y `(1 row)`.

Para lo que queda del lab dentro de `psql`:
- Los comandos con barra (`\c`, `\dt`, `\r`) van **siempre solos en su línea**.
- Las sentencias SQL pueden ocupar varias líneas. `psql` las ejecuta al llegar al `;`.


## 🧑 Alumno · 18:10 UTC

<pasted_content id="1013">
7. Module 01: Build an agent tool backend on Azure Database for PostgreSQL
Task 4: Configure firewall rules in the Azure Portal


To allow connections to your PostgreSQL server, you must create a firewall rule through the Azure Portal:


Sign in to the Azure Portal https://portal.azure.com.

Search for "PostgreSQL servers" or navigate to your resource group ai200rg

Click on your PostgreSQL server (named psql-agent-XXXXXXXX)

In the left sidebar, click "Networking"

Under the "Public access" section, ensure the checkbox "Allow public access to this resource through the internet using a public IP address" is checked

Scroll down to the "Firewall rules" section

Check if a firewall rule named AllowAll already exists:
If it exists: Click on it to verify the values are:
Start IP address: 0.0.0.0
End IP address: 255.255.255.255
Then click "Save" and proceed to the next task
If it does not exist: Click "+ Add current client IP" or "+ Add a firewall rule" and create a new rule with the values above, then click "Save"

Click "Save" at the top of the page
📝 Note: This allows all IP addresses to connect to your PostgreSQL server. For production environments, restrict the IP range to your specific needs.

Once the firewall rule is created and saved, your PostgreSQL server will be accessible for connectio
</pasted_content id="1013">


### 🤖 Claude · 18:10 UTC

La Task 4 ya está hecha: el script creó la regla `AllowAll` (lo confirmó la opción 2) y la prueba definitiva es que **`psql` ya se ha conectado**. No hace falta ir al portal. Si quieres comprobarlo, mejor con `az`, en **otra terminal** (deja `psql` abierto):

```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query network.publicNetworkAccess -o tsv
az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
```
✅ Esperado:
```
Enabled
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
```
Equivale a la casilla "Allow public access" y a la regla que la guía te pide revisar en el portal.

**Si no coincide:**
- Si no aparece la regla, créala:
  ```bash
  az postgres flexible-server firewall-rule create -g ai200rg -n psql-agent-dc48980e -r AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
  ```
- Si `publicNetworkAccess` sale `Disabled`, pégamelo: ese ajuste no se cambia con un simple `update`.

Sobre la nota de la guía: `0.0.0.0–255.255.255.255` abre el servidor a todo Internet. En un caso real pondrías solo tu IP de salida o, mejor, acceso privado por VNet. Aquí lo protege que solo se entra con un token de Entra.

Pégame la siguiente tarea, la del esquema con los `CREATE TABLE`. Y si te sale, el resultado del `SELECT version();`.


## 🧑 Alumno · 18:11 UTC

<pasted_content id="1013">
Read more about the command in reference docs
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query network.publicNetworkAccess -o tsv
Enabled
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
unrecognized arguments: -n psql-agent-dc48980e

https://aka.ms/cli_ref
Read more about the command in reference docs
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .env
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
unrecognized arguments: -n psql-agent-dc48980e

https://aka.ms/cli_ref
Read more about the command in reference docs
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


**🔧 Bash** — Ver argumentos de firewall-rule list

```text
az postgres flexible-server firewall-rule list -h 2>/dev/null | sed -n '/Arguments/,/Global/p' | head -20
```


<details><summary>Resultado</summary>

```text
Arguments

Resource Id Arguments
    --ids               : One or more resource IDs (space-delimited). It should be a complete
                          resource ID containing all information of 'Resource Id' arguments. You
                          should provide either --ids or other 'Resource Id' arguments.
    --resource-group -g : Name of resource group. You can configure the default group using `az
                          configure --defaults group=<name>`.
    --server-name -s    : Name of the server.
    --subscription      : Name or ID of subscription. You can configure the default subscription
                          using `az account set -s NAME_OR_ID`.

Global Arguments
```
</details>


### 🤖 Claude · 18:11 UTC

Fallo mío: en `firewall-rule` el servidor se indica con `--server-name` (o `-s`), no con `-n`. En los subcomandos de reglas, `-n` es el nombre de la **regla**. Lo he comprobado en la ayuda de tu `az`. Comando corregido:

```bash
az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
```
✅ Esperado:
```
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
```
El `publicNetworkAccess` = `Enabled` ya es correcto, así que la Task 4 está cumplida en cuanto salga la regla.

**Si la regla no aparece**, este es el comando de creación corregido (el que te di antes tenía el mismo error):
```bash
az postgres flexible-server firewall-rule create -g ai200rg --server-name psql-agent-dc48980e --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
```

El `source .env` no hacía falta aquí: `az` usa tu sesión de `az login`. El `.env` solo lo necesitan `psql` y Python.


## 🧑 Alumno · 18:13 UTC

<pasted_content id="1013">
Read more about the command in reference docs
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az postgres flexible-server firewall-rule create -g ai200rg --server-name psql-agent-dc48980e --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
{
  "endIpAddress": "255.255.255.255",
  "id": "/subscriptions/<guid>/resourceGroups/ai200rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-agent-dc48980e/firewallRules/AllowAll",
  "name": "AllowAll",
  "resourceGroup": "ai200rg",
  "startIpAddress": "0.0.0.0",
  "systemData": null,
  "type": "Microsoft.DBforPostgreSQL/flexibleServers/firewallRules"
}
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


**🔧 Bash** — Guardar salidas del firewall y anotar incidencia

```text
cat >> salidas.md <<'EOF'

## 9. Task 4 de la plataforma (firewall): verificación con `az` en lugar del portal
ʼʼʼtext
$ az postgres flexible-server show -g ai200rg -n psql-agent-dc48980e --query network.publicNetworkAccess -o tsv
Enabled
$ az postgres flexible-server firewall-rule list -g ai200rg -n psql-agent-dc48980e ...
unrecognized arguments: -n psql-agent-dc48980e
$ az postgres flexible-server firewall-rule list -g ai200rg --server-name psql-agent-dc48980e --query "[].{name:name, start:startIpAddress, end:endIpAddress}" -o table
Name      Start    End
--------  -------  ---------------
AllowAll  0.0.0.0  255.255.255.255
$ az postgres flexible-server firewall-rule create -g ai200rg --server-name psql-agent-dc48980e --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
{
  "endIpAddress": "255.255.255.255",
  "id": "/subscriptions/<sub-id>/resourceGroups/ai200rg/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-agent-dc48980e/firewallRules/AllowAll",
  "name": "AllowAll",
  "resourceGroup": "ai200rg",
  "startIpAddress": "0.0.0.0",
  ...
}
ʼʼʼ
**Qué mirar:** en `firewall-rule` el servidor va con `--server-name`/`-s`; `-n` es el nombre de la regla (en `show` sí es el servidor). La regla ya existía (la crea `azdeploy.py`); el `create` no hacía falta, pero es idempotente: sobrescribe la regla con los mismos valores. La Task 4 del portal queda cubierta con `az`.
EOF
sed -i 's#^| `ERROR: The location is restricted#| `unrecognized arguments: -n psql-agent-…` en `firewall-rule list` | En los subcomandos de reglas el servidor es `--server-name`/`-s`; `-n` es la regla | `--server-name psql-agent-dc48980e` |\n&#' README.md && grep -c "server-name" README.md
```


<details><summary>Resultado</summary>

```text
1
[This command modified 2 files you've previously read: README.md, salidas.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 18:14 UTC

✅ **Task 4 completada.** La regla `AllowAll` (0.0.0.0–255.255.255.255) ya existía, porque la crea el script, y el acceso público está `Enabled`.

El `create` que has lanzado no hacía falta, pero no ha hecho daño: es **idempotente** y ha vuelto a escribir la misma regla con los mismos valores. Es la misma idea que un `kubectl apply` o que el `ON CONFLICT` que verás ahora en SQL.

Lo he guardado en `salidas.md` (con el ID de la suscripción quitado) y he anotado el error del `-n` en las incidencias del README.

**Siguiente:** vuelve a la terminal de `psql` (prompt `postgres=>`) y pégame la siguiente tarea de la plataforma, la de crear la BD `agent_memory` y las tablas.


## 🧑 Alumno · 18:16 UTC

<pasted_content id="1013">
8. Module 01: Build an agent tool backend on Azure Database for PostgreSQL
Task 5: Create the agent memory schema with psql


In this section you connect to the PostgreSQL server using the psql command-line tool and create the database schema for agent memory. The schema includes three tables: one for conversations (agent sessions), one for messages within those conversations, and one for task checkpoints that enable the agent to resume interrupted work.


Run the following command to connect to the server using the environment variables. The PGPASSWORD environment variable is automatically used for authentication.
psql "host=$env:DB_HOST port=5432 dbname=$env:DB_NAME user=$env:DB_USER sslmode=require"

Run the following command to verify the connection by checking the PostgreSQL version.
SELECT version();

Run the following command to create a database for the agent backend. The \c command connects to the new database.
CREATE DATABASE agent_memory;
\c agent_memory

Run the following command to create a table for conversations (agent sessions). This table stores session metadata and links messages to a specific conversation.
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

Run the following command to create a table for messages within conversations. This table stores the role (user, assistant, system, or tool) and content for each message.
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

Run the following command to create a table for task checkpoints. This table enables agent state persistence so the agent can resume interrupted tasks.
CREATE TABLE task_checkpoints (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
    task_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    checkpoint_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

Run the following command to create indexes that optimize common queries. These indexes improve performance when retrieving messages by conversation or timestamp.
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_task_checkpoints_conversation_id ON task_checkpoints(conversation_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);

The app you completed earlier in the exercise uses ON CONFLICT, which requires a unique constraint. Run the following command in your psql session in the terminal to add it.
ALTER TABLE task_checkpoints
ADD CONSTRAINT unique_conversation_task
UNIQUE (conversation_id, task_name);

Run the following command to verify the schema was created correctly.
\dt
📝 Note: You should see the three tables listed.


Enter exit to close the psql session and return to the terminal.
</pasted_content id="1013">


### 🤖 Claude · 18:16 UTC

Para evitar los problemas de pegar en `psql`, te dejo el SQL de la Task 5 en un fichero, copiado literalmente de la guía de la plataforma:


**🔧 Write**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/schema.sql
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/schema.sql (file state is current in your context — no need to Read it back)
```
</details>


### 🤖 Claude · 18:16 UTC

He dejado el SQL de la guía, copiado literalmente, en `labs/lp5-01-pg-agent-backend/sql/schema.sql`. Ejecutarlo como fichero evita los problemas de pegar texto en `psql`.

## Task 5 en `psql`
Escribe cada línea **por separado**, en el prompt `postgres=>`:

```sql
SELECT version();
```
✅ Una fila con `PostgreSQL 16.x on x86_64-pc-linux-gnu…`.

```sql
CREATE DATABASE agent_memory;
```
✅ Responde `CREATE DATABASE`.

```
\c agent_memory
```
✅ Responde `You are now connected to database "agent_memory" as user "<email>".` y el prompt cambia a `agent_memory=>`. **Si no cambia, no sigas:** las tablas se crearían en `postgres`.

```
\i sql/schema.sql
```
✅ Esperado, en este orden: `CREATE TABLE` (3 veces), `CREATE INDEX` (4 veces) y `ALTER TABLE` (1 vez). La ruta es relativa a la carpeta desde la que lanzaste `psql`, que es la del lab. Si sale `No such file or directory`, usa `\i ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/schema.sql`.

```
\dt
```
✅ Esperado:
```
                    List of relations
 Schema |       Name       | Type  |           Owner
--------+------------------+-------+----------------------------
 public | conversations    | table | <email>
 public | messages         | table | <email>
 public | task_checkpoints | table | <email>
```

Comprobación extra de la restricción que necesita `save_task_state`:
```
\d task_checkpoints
```
✅ Al final, en `Indexes:`, debe aparecer `"unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)`.

Si algún comando da `ERROR: … already exists`, es que ya lo habías ejecutado: pégamelo y vemos qué falta. Al terminar, `exit`.

## Tres detalles del esquema que valen para el examen
1. **`idx_conversations_session_id` sobra.** `session_id UUID NOT NULL UNIQUE` ya crea su propio índice (`conversations_session_id_key`). La guía crea un segundo índice igual, que solo hace más lentas las escrituras. Lo verás con `\d conversations`, que mostrará dos índices sobre `session_id`.
2. **`ON DELETE CASCADE`:** si borras una conversación, PostgreSQL borra sus mensajes y checkpoints. Es como el *garbage collection* por `ownerReferences` en K8s: al borrar el Deployment, se borran sus ReplicaSets y pods.
3. **`task_checkpoints.conversation_id` admite NULL** (no tiene `NOT NULL`). En PostgreSQL dos NULL no se consideran iguales en un `UNIQUE`, así que dos checkpoints con `conversation_id` NULL y el mismo `task_name` **no** provocan conflicto: el upsert insertaría duplicados en lugar de actualizar. En un diseño real le pondría `NOT NULL`.

Pégame las salidas cuando acabes y pasamos a la Task 6 (`test_workflow.py`).


## 🧑 Alumno · 18:18 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=> SELECT version();
                                    version                                    
-------------------------------------------------------------------------------
 PostgreSQL 16.15 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
(1 row)

postgres=> CREATE DATABASE agent_memory;
CREATE DATABASE
postgres=> \c agent_memory
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
You are now connected to database "agent_memory" as user "<email>".
agent_memory=> \i sql/schema.sql
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
ALTER TABLE
agent_memory=> \dt
                       List of relations
 Schema |       Name       | Type  |           Owner            
--------+------------------+-------+----------------------------
 public | conversations    | table | <email>
 public | messages         | table | <email>
 public | task_checkpoints | table | <email>
(3 rows)

agent_memory=> \d task_checkpoints
                                         Table "public.task_checkpoints"
     Column      |           Type           | Collation | Nullable |                   Default                    
-----------------+--------------------------+-----------+----------+----------------------------------------------
 id              | bigint                   |           | not null | nextval('task_checkpoints_id_seq'::regclass)
 conversation_id | bigint                   |           |          | 
 task_name       | character varying(255)   |           | not null | 
 status          | character varying(50)    |           | not null | 
 checkpoint_data | jsonb                    |           | not null | '{}'::jsonb
 created_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "task_checkpoints_pkey" PRIMARY KEY, btree (id)
    "idx_task_checkpoints_conversation_id" btree (conversation_id)
    "unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)
Check constraints:
    "task_checkpoints_status_check" CHECK (status::text = ANY (ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'failed'::character varying]::text[]))
Foreign-key constraints:
    "task_checkpoints_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
</pasted_content id="1013">


**🔧 Bash** — Leer test_workflow.py para saber la salida esperada

```text
cat agent-backend/test_workflow.py
```


<details><summary>Resultado</summary>

```text
from agent_tools import (
    create_conversation,
    store_message,
    get_conversation_history,
    save_task_state,
    get_task_state
)

def test_agent_workflow():
    print("=== Testing Agent Memory Backend ===\n")

    # Step 1: Create a new conversation
    print("1. Creating conversation...")
    conv = create_conversation(
        user_id="user_123",
        metadata={"source": "web", "model": "gpt-4"}
    )
    print(f"   Created conversation: {conv}\n")
    conversation_id = conv["conversation_id"]

    # Step 2: Store messages simulating an agent interaction
    print("2. Storing messages...")
    messages = [
        ("system", "You are a helpful research assistant."),
        ("user", "Can you help me find information about PostgreSQL?"),
        ("assistant", "I'd be happy to help you research PostgreSQL. Let me search for relevant information."),
        ("tool", '{"tool": "search", "results": ["PostgreSQL documentation", "PostgreSQL tutorial"]}'),
        ("assistant", "I found some resources about PostgreSQL. The official documentation is a great starting point.")
    ]

    for role, content in messages:
        result = store_message(conversation_id, role, content)
        print(f"   Stored {role} message: {result}")
    print()

    # Step 3: Save task state (agent checkpoint)
    print("3. Saving task checkpoint...")
    task_result = save_task_state(
        conversation_id=conversation_id,
        task_name="research_postgresql",
        status="in_p
… [recortado, 3032 caracteres]
```
</details>


**🔧 Bash** — Guardar la salida del esquema

```text
cat >> salidas.md <<'EOF'

## 10. Task 5 de la plataforma: esquema con `psql` (`\i sql/schema.sql`)
ʼʼʼtext
postgres=> SELECT version();
 PostgreSQL 16.15 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
postgres=> CREATE DATABASE agent_memory;
CREATE DATABASE
postgres=> \c agent_memory
You are now connected to database "agent_memory" as user "<email>".
agent_memory=> \i sql/schema.sql
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
ALTER TABLE
agent_memory=> \dt
 Schema |       Name       | Type  |           Owner
--------+------------------+-------+----------------------------
 public | conversations    | table | <email>
 public | messages         | table | <email>
 public | task_checkpoints | table | <email>
agent_memory=> \d task_checkpoints
 conversation_id | bigint  |  |          |      <- Nullable vacío: admite NULL
 ...
Indexes:
    "task_checkpoints_pkey" PRIMARY KEY, btree (id)
    "idx_task_checkpoints_conversation_id" btree (conversation_id)
    "unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)
Check constraints:
    "task_checkpoints_status_check" CHECK (status::text = ANY (ARRAY['pending', 'in_progress', 'completed', 'failed']))
Foreign-key constraints:
    "task_checkpoints_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
ʼʼʼ
**Qué mirar:**
- El dueño de las tablas es el usuario de Entra: no existe un usuario de base de datos con contraseña.
- `unique_conversation_task` existe: el `ON CONFLICT` de `save_task_state` funcionará.
- El `CHECK` de `status` se guarda como `= ANY (ARRAY[...])`: es la forma interna de `IN (...)`.
- `conversation_id` sin `NOT NULL`: dos checkpoints con `conversation_id` NULL y el mismo `task_name` no chocan en el `UNIQUE` (NULL ≠ NULL).
- Índices redundantes de la guía: `idx_task_checkpoints_conversation_id` lo cubre ya el `UNIQUE (conversation_id, task_name)` (prefijo izquierdo del índice compuesto) e `idx_conversations_session_id` duplica el índice que crea `UNIQUE` en `session_id`.
EOF
echo ok
```


<details><summary>Resultado</summary>

```text
ok
```
</details>


### 🤖 Claude · 18:19 UTC

✅ **Task 5 completada:** PostgreSQL 16.15, la BD `agent_memory`, las 3 tablas, los 4 índices y la restricción `unique_conversation_task`. Todo coincide con lo esperado; lo he guardado en `salidas.md`.

Tu `\d task_checkpoints` deja ver dos cosas más:
- **Owner = tu usuario de Entra:** no hay ningún usuario de base de datos con contraseña.
- **Otro índice redundante:** `idx_task_checkpoints_conversation_id` está cubierto por `unique_conversation_task (conversation_id, task_name)`. Un índice compuesto también sirve para buscar solo por su **primera** columna (la regla del "prefijo izquierdo"). La guía crea dos índices de más, y eso es una buena pregunta de optimización para el módulo 3.

## Task 6: probar el flujo con Python
Sal de `psql` con `exit`. Desde la carpeta del lab, con el `.env` ya cargado:

```bash
cd agent-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
✅ Comprobación: `pip list 2>/dev/null | grep -iE '^(psycopg|azure-identity)'` debe mostrar `psycopg`, `psycopg-binary` y `azure-identity`. El `.venv` está en el `.gitignore`, así que no se sube.

```bash
python test_workflow.py
```
✅ Esperado (yo he leído el `test_workflow.py`; la guía no muestra la salida):
```
=== Testing Agent Memory Backend ===
1. Creating conversation...       → {'conversation_id': 1, 'session_id': '<uuid>', 'started_at': '...'}
2. Storing messages...            → 5 mensajes: system, user, assistant, tool, assistant
3. Saving task checkpoint...      → {'checkpoint_id': 1, ...}
4. Retrieving conversation history... → Found 5 messages, en orden cronológico
5. Retrieving task state...       → status 'in_progress', step 2
6. Updating task state to completed... → checkpoint_id: 1 (¡el mismo!)
7. Verifying final state...       → Final status: completed
=== All tests completed successfully! ===
```
**Lo que hay que mirar:** en el paso 6, `checkpoint_id` debe ser **el mismo que en el paso 3**. Eso demuestra que el `ON CONFLICT` ha **actualizado** la fila en lugar de crear una nueva.

**Si falla:**
- **`KeyError: 'DB_HOST'`:** no está cargado el `.env`. Ejecuta `source ../.env`.
- **`DefaultAzureCredential failed`:** el código saca su propio token de tu `az login`, no usa `PGPASSWORD`. Comprueba la sesión con `az account show`.
- **Error de certificado en `pip`:** `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` y repite.
- **`there is no unique or exclusion constraint matching the ON CONFLICT`:** faltaría la restricción, pero ya hemos visto que existe.


## 🧑 Alumno · 18:23 UTC

<pasted_content id="1013">
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend$ python test_workflow.py
=== Testing Agent Memory Backend ===

1. Creating conversation...
   Created conversation: {'conversation_id': 1, 'session_id': '<guid>', 'started_at': '2026-11-10T18:22:21.538945+00:00'}

2. Storing messages...
   Stored system message: {'message_id': 1, 'created_at': '2026-11-10T18:22:23.945910+00:00'}
   Stored user message: {'message_id': 2, 'created_at': '2026-11-10T18:22:26.414443+00:00'}
   Stored assistant message: {'message_id': 3, 'created_at': '2026-11-10T18:22:28.865078+00:00'}
   Stored tool message: {'message_id': 4, 'created_at': '2026-11-10T18:22:30.276087+00:00'}
   Stored assistant message: {'message_id': 5, 'created_at': '2026-11-10T18:22:32.655699+00:00'}

3. Saving task checkpoint...
   Saved checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

4. Retrieving conversation history...
   Found 5 messages:
   - [system]: You are a helpful research assistant....
   - [user]: Can you help me find information about PostgreSQL?...
   - [assistant]: I'd be happy to help you research PostgreSQL. Let ...
   - [tool]: {"tool": "search", "results": ["PostgreSQL documen...
   - [assistant]: I found some resources about PostgreSQL. The offic...
</pasted_content id="1013">


<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

postgres=> SELECT version();
                                    version                                    
-------------------------------------------------------------------------------
 PostgreSQL 16.15 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 13.2.0, 64-bit
(1 row)

postgres=> CREATE DATABASE agent_memory;
CREATE DATABASE
postgres=> \c agent_memory
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
You are now connected to database "agent_memory" as user "<email>".
agent_memory=> \i sql/schema.sql
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
ALTER TABLE
agent_memory=> \dt
                       List of relations
 Schema |       Name       | Type  |           Owner            
--------+------------------+-------+----------------------------
 public | conversations    | table | <email>
 public | messages         | table | <email>
 public | task_checkpoints | table | <email>
(3 rows)

agent_memory=> \d task_checkpoints
                                         Table "public.task_checkpoints"
     Column      |           Type           | Collation | Nullable |                   Default                    
-----------------+--------------------------+-----------+----------+----------------------------------------------
 id              | bigint                   |           | not null | nextval('task_checkpoints_id_seq'::regclass)
 conversation_id | bigint                   |           |          | 
 task_name       | character varying(255)   |           | not null | 
 status          | character varying(50)    |           | not null | 
 checkpoint_data | jsonb                    |           | not null | '{}'::jsonb
 created_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
 updated_at      | timestamp with time zone |           |          | CURRENT_TIMESTAMP
Indexes:
    "task_checkpoints_pkey" PRIMARY KEY, btree (id)
    "idx_task_checkpoints_conversation_id" btree (conversation_id)
    "unique_conversation_task" UNIQUE CONSTRAINT, btree (conversation_id, task_name)
Check constraints:
    "task_checkpoints_status_check" CHECK (status::text = ANY (ARRAY['pending'::character varying, 'in_progress'::character varying, 'completed'::character varying, 'failed'::character varying]::text[]))
Foreign-key constraints:
    "task_checkpoints_conversation_id_fkey" FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE

agent_memory=> \e

Select an editor.  To change later, run 'select-editor'.
  1. /bin/nano        <---- easiest
  2. /usr/bin/vim.basic
  3. /usr/bin/vim.tiny
  4. /usr/bin/code
  5. /bin/ed

Choose 1-5 [1]: ^Cagent_memory=> q
agent_memory-> q
agent_memory-> q;
ERROR:  syntax error at or near "q"
LINE 1: q
        ^
agent_memory=> \q
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .env
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ ^[[200~cd agent-backend
cd: no se encontró la orden
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ python3 -m venv .venv
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ source .venv/bin/activate~^C
alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ cd agent-backend
python3 -m venv .venv
source .venv/bin/activate
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend$ pip install -r requirements.txt
Collecting azure-identity (from -r requirements.txt (line 2))
  Using cached azure_identity-1.27.0-py3-none-any.whl.metadata (96 kB)
Collecting psycopg[binary] (from -r requirements.txt (line 1))
  Downloading psycopg-3.3.8-py3-none-any.whl.metadata (4.4 kB)
Collecting typing-extensions>=4.6 (from psycopg[binary]->-r requirements.txt (line 1))
  Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting psycopg-binary==3.3.8 (from psycopg[binary]->-r requirements.txt (line 1))
  Downloading psycopg_binary-3.3.8-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.7 kB)
Collecting azure-core>=1.31.0 (from azure-identity->-r requirements.txt (line 2))
  Using cached azure_core-1.41.0-py3-none-any.whl.metadata (49 kB)
Collecting cryptography>=2.5 (from azure-identity->-r requirements.txt (line 2))
  Using cached cryptography-50.0.2-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (4.4 kB)
Collecting msal>=1.39.0 (from azure-identity->-r requirements.txt (line 2))
  Using cached msal-1.39.0-py3-none-any.whl.metadata (11 kB)
Collecting msal-extensions>=1.2.0 (from azure-identity->-r requirements.txt (line 2))
  Using cached msal_extensions-1.3.1-py3-none-any.whl.metadata (7.8 kB)
Collecting requests>=2.21.0 (from azure-core>=1.31.0->azure-identity->-r requirements.txt (line 2))
  Using cached requests-2.34.2-py3-none-any.whl.metadata (4.8 kB)
Collecting cffi>=2.0.0 (from cryptography>=2.5->azure-identity->-r requirements.txt (line 2))
  Using cached cffi-2.1.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (2.5 kB)
Collecting PyJWT<3,>=1.0.0 (from PyJWT[crypto]<3,>=1.0.0->msal>=1.39.0->azure-identity->-r requirements.txt (line 2))
  Using cached pyjwt-2.15.1-py3-none-any.whl.metadata (3.5 kB)
Collecting pycparser (from cffi>=2.0.0->cryptography>=2.5->azure-identity->-r requirements.txt (line 2))
  Using cached pycparser-3.12-py3-none-any.whl.metadata (9.7 kB)
Collecting charset_normalizer<4,>=2 (from requests>=2.21.0->azure-core>=1.31.0->azure-identity->-r requirements.txt (line 2))
  Using cached charset_normalizer-3.5.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (46 kB)
Collecting idna<4,>=2.5 (from requests>=2.21.0->azure-core>=1.31.0->azure-identity->-r requirements.txt (line 2))
  Using cached idna-3.20-py3-none-any.whl.metadata (7.2 kB)
Collecting urllib3<3,>=1.26 (from requests>=2.21.0->azure-core>=1.31.0->azure-identity->-r requirements.txt (line 2))
  Using cached urllib3-2.8.0-py3-none-any.whl.metadata (7.4 kB)
Collecting certifi>=2023.5.7 (from requests>=2.21.0->azure-core>=1.31.0->azure-identity->-r requirements.txt (line 2))
  Using cached certifi-2026.10.23-py3-none-any.whl.metadata (2.5 kB)
Downloading psycopg_binary-3.3.8-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (5.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 5.2/5.2 MB 26.3 MB/s eta 0:00:00
Using cached azure_identity-1.27.0-py3-none-any.whl (203 kB)
Using cached azure_core-1.41.0-py3-none-any.whl (220 kB)
Using cached cryptography-50.0.2-cp311-abi3-manylinux_2_34_x86_64.whl (4.8 MB)
Using cached msal-1.39.0-py3-none-any.whl (131 kB)
Using cached msal_extensions-1.3.1-py3-none-any.whl (20 kB)
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Downloading psycopg-3.3.8-py3-none-any.whl (216 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 216.2/216.2 kB 6.9 MB/s eta 0:00:00
Using cached cffi-2.1.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (221 kB)
Using cached pyjwt-2.15.1-py3-none-any.whl (33 kB)
Using cached requests-2.34.2-py3-none-any.whl (73 kB)
Using cached certifi-2026.10.23-py3-none-any.whl (135 kB)
Using cached charset_normalizer-3.5.2-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (257 kB)
Using cached idna-3.20-py3-none-any.whl (69 kB)
Using cached urllib3-2.8.0-py3-none-any.whl (135 kB)
Using cached pycparser-3.12-py3-none-any.whl (62 kB)
Installing collected packages: urllib3, typing-extensions, PyJWT, pycparser, psycopg-binary, idna, charset_normalizer, certifi, requests, psycopg, cffi, cryptography, azure-core, msal, msal-extensions, azure-identity
Successfully installed PyJWT-2.15.1 azure-core-1.41.0 azure-identity-1.27.0 certifi-2026.10.23 cffi-2.1.1 charset_normalizer-3.5.2 cryptography-50.0.2 idna-3.20 msal-1.39.0 msal-extensions-1.3.1 psycopg-3.3.8 psycopg-binary-3.3.8 pycparser-3.12 requests-2.34.2 typing-extensions-4.16.0 urllib3-2.8.0
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/agent-backend$ python test_workflow.py
=== Testing Agent Memory Backend ===

1. Creating conversation...
   Created conversation: {'conversation_id': 1, 'session_id': '<guid>', 'started_at': '2026-11-10T18:22:21.538945+00:00'}

2. Storing messages...
   Stored system message: {'message_id': 1, 'created_at': '2026-11-10T18:22:23.945910+00:00'}
   Stored user message: {'message_id': 2, 'created_at': '2026-11-10T18:22:26.414443+00:00'}
   Stored assistant message: {'message_id': 3, 'created_at': '2026-11-10T18:22:28.865078+00:00'}
   Stored tool message: {'message_id': 4, 'created_at': '2026-11-10T18:22:30.276087+00:00'}
   Stored assistant message: {'message_id': 5, 'created_at': '2026-11-10T18:22:32.655699+00:00'}

3. Saving task checkpoint...
   Saved checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

4. Retrieving conversation history...
   Found 5 messages:
   - [system]: You are a helpful research assistant....
   - [user]: Can you help me find information about PostgreSQL?...
   - [assistant]: I'd be happy to help you research PostgreSQL. Let ...
   - [tool]: {"tool": "search", "results": ["PostgreSQL documen...
   - [assistant]: I found some resources about PostgreSQL. The offic...

5. Retrieving task state...
   Current state: {'checkpoint_id': 1, 'status': 'in_progress', 'checkpoint_data': {'step': 2, 'next_action': 'summarize_findings', 'sources_found': 2}, 'created_at': '2026-11-10T18:22:35.037193+00:00', 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

6. Updating task state to completed...
   Updated checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:42.154100+00:00'}

7. Verifying final state...
   Final status: completed
   Checkpoint data: {'step': 3, 'summary': 'PostgreSQL is an advanced open-source database.', 'sources_found': 2}

=== All tests completed successfully! ===
</pasted_content id="1013">


**🔧 Bash** — Guardar salida del test y actualizar estado

```text
cat >> salidas.md <<'EOF'

## 11. Task 6: `test_workflow.py`
ʼʼʼtext
(.venv) $ pip install -r requirements.txt
Successfully installed ... azure-identity-1.27.0 ... psycopg-3.3.8 psycopg-binary-3.3.8 ...
(.venv) $ python test_workflow.py
=== Testing Agent Memory Backend ===

1. Creating conversation...
   Created conversation: {'conversation_id': 1, 'session_id': '84f355cd-...', 'started_at': '2026-11-10T18:22:21.538945+00:00'}

2. Storing messages...
   Stored system message: {'message_id': 1, 'created_at': '2026-11-10T18:22:23.945910+00:00'}
   Stored user message: {'message_id': 2, 'created_at': '2026-11-10T18:22:26.414443+00:00'}
   Stored assistant message: {'message_id': 3, 'created_at': '2026-11-10T18:22:28.865078+00:00'}
   Stored tool message: {'message_id': 4, 'created_at': '2026-11-10T18:22:30.276087+00:00'}
   Stored assistant message: {'message_id': 5, 'created_at': '2026-11-10T18:22:32.655699+00:00'}

3. Saving task checkpoint...
   Saved checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

4. Retrieving conversation history...
   Found 5 messages:
   - [system]: You are a helpful research assistant....
   - [user]: Can you help me find information about PostgreSQL?...
   - [assistant]: I'd be happy to help you research PostgreSQL. Let ...
   - [tool]: {"tool": "search", "results": ["PostgreSQL documen...
   - [assistant]: I found some resources about PostgreSQL. The offic...

5. Retrieving task state...
   Current state: {'checkpoint_id': 1, 'status': 'in_progress', 'checkpoint_data': {'step': 2, 'next_action': 'summarize_findings', 'sources_found': 2}, 'created_at': '2026-11-10T18:22:35.037193+00:00', 'updated_at': '2026-11-10T18:22:35.037193+00:00'}

6. Updating task state to completed...
   Updated checkpoint: {'checkpoint_id': 1, 'updated_at': '2026-11-10T18:22:42.154100+00:00'}

7. Verifying final state...
   Final status: completed
   Checkpoint data: {'step': 3, 'summary': 'PostgreSQL is an advanced open-source database.', 'sources_found': 2}

=== All tests completed successfully! ===
ʼʼʼ
**Qué mirar:**
- **Upsert:** `checkpoint_id` es `1` en el paso 3 y en el 6: `ON CONFLICT` actualizó la fila, no creó otra. `updated_at` cambia (18:22:35 → 18:22:42); `created_at` se conserva.
- **Historial:** los 5 mensajes salen en orden cronológico gracias a `ORDER BY created_at DESC` + `reversed()`.
- **JSONB no conserva el orden de las claves:** se insertó `step, sources_found, next_action` y vuelve `step, next_actio
… [recortado, 3465 caracteres]
```


<details><summary>Resultado</summary>

```text
**Estado:** en curso (10/11/2026). Tasks 1-6 completadas: servidor `Ready`, esquema creado y `test_workflow.py` correcto (upsert verificado: mismo `checkpoint_id`).
[This command modified 2 files you've previously read: README.md, salidas.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 18:23 UTC

Ya está funcionando, y `test_workflow.py` lo ha confirmado: **`=== All tests completed successfully! ===`**. Este es el resumen de hoy.

## Lo que tenemos en Azure (suscripción del lab `XLabs-079`)
```
Resource group ai200rg (centralus)
└── PostgreSQL Flexible Server psql-agent-dc48980e
    ├── Standard_D2ds_v4 / GeneralPurpose, PostgreSQL 16.15   ← lo impone la política del lab
    ├── Autenticación: solo Entra (admin = tu usuario del lab, contraseña desactivada)
    ├── Red: acceso público + regla de firewall AllowAll (solo vale para el lab)
    └── BD agent_memory
        ├── conversations      → las sesiones del agente (session_id UUID, metadata JSONB)
        ├── messages           → el historial: system / user / assistant / tool
        └── task_checkpoints   → el estado de tareas largas, con UNIQUE (conversation_id, task_name)
```
También queda `rg-ai200-pg-agent`, el grupo del primer intento en `eastus`, con el borrado lanzado. Comprobaremos que ya no existe en el cleanup.

## Lo que tenemos en el PC (`labs/lp5-01-pg-agent-backend/`)
| Pieza | Qué es |
|---|---|
| `azdeploy.py` | El script de Microsoft, con los valores de la plataforma (`ai200rg`, `centralus`, `D2ds_v4`) |
| `.env` | `DB_HOST`, `DB_NAME`, `DB_USER` y `PGPASSWORD` (token de Entra, caduca en 1 h). **No se sube** |
| `sql/schema.sql` | El SQL de la Task 5, que ejecutaste con `\i` |
| `agent-backend/agent_tools.py` | Las 3 funciones de la Task 2, que serían las *tools* del agente |
| `README.md` + `salidas.md` | La documentación y las 11 salidas reales, saneadas |

## Qué ha demostrado el test, paso a paso
1. **`create_conversation`:** `INSERT … RETURNING` devolvió el `id` 1 y el UUID en la misma consulta.
2. **`store_message` × 5:** los cinco roles que admite el `CHECK`.
3. y 6. **`save_task_state`:** la primera vez **insertó** (`in_progress`) y la segunda **actualizó** (`completed`), con el **mismo `checkpoint_id` = 1**. Eso es el upsert con `ON CONFLICT`, que funciona gracias a la restricción `UNIQUE`.
4. **`get_conversation_history`:** los 5 mensajes en orden cronológico.
5. y 7. **`get_task_state`:** el agente "retomaría" la tarea leyendo su checkpoint.

## Cuatro cosas que hemos aprendido por el camino
| Observación | Lección |
|---|---|
| **Unos 2,4 s por operación** | Cada función pide un token nuevo (a través de `az`, que es un subproceso) y abre una conexión TLS nueva. Es justo el antipatrón de la pregunta 2 del test; en una aplicación real usarías un `ConnectionPool` |
| El JSONB devolvió las claves **en otro orden** | `JSONB` guarda un formato binario normalizado y no respeta el orden. El tipo `json` sí lo respetaría |
| La guía crea **dos índices de más** | `UNIQUE` ya crea su propio índice, y un índice compuesto también sirve para buscar por su primera columna |
| `psql` funciona en local y `kubectl` no | Netskope solo inspecciona el tráfico web (443). El 5432 sale directo y el TLS de PostgreSQL va dentro de su propio protocolo |

Incidencias resueltas: la región `eastus` estaba restringida por política, el `-n` en lugar de `--server-name` en `firewall-rule`, y algunos tropiezos de terminal (`\e`, `q` en lugar de `\q`, el pegado con `^[[200~`).

## Lo que queda del lab 12
1. **Siguiente tarea de la plataforma:** las consultas SQL sobre lo que ha guardado el test (conversaciones de `user_123`, últimos mensajes, checkpoints completados y recuento por rol). Pégamela cuando la tengas.
2. **Cleanup al terminar el lab:** `az group delete --name ai200rg --yes --no-wait`, y verificar `false` tanto para `ai200rg` como para `rg-ai200-pg-agent`.

Hay un `.venv` sobrante en la raíz del lab, de cuando el `cd` falló. Git lo ignora y no molesta; puedes borrarlo con `rm -rf .venv` desde la carpeta del lab cuando quieras.


## 🧑 Alumno · 18:26 UTC

y como acoplarias este producto a un repo con un grupo de egetes quet rabaja un departametno de sistemas


### 🤖 Claude · 18:26 UTC

Lo acoplaría en cuatro piezas. La idea central es que **el código del lab ya es el 80 % del backend**: solo hay que envolverlo para que lo usen los agentes de Claude y adaptarlo a varios usuarios.

## 1. Qué es cada tabla del lab en un departamento de sistemas
| Tabla del lab | En tu departamento | Ejemplo |
|---|---|---|
| `conversations` | **Sesión de trabajo**: quién, qué agente, sobre qué sistema | `user_id = 'ana@empresa'`, `metadata = {"agent": "aks-ops", "ticket": "INC-1234", "cluster": "prod-weu"}` |
| `messages` (role `tool`) | **Registro de acciones**: cada comando o cambio que ejecuta el agente | `{"tool": "Bash", "cmd": "az aks upgrade ...", "exit": 0}` |
| `task_checkpoints` | **Operaciones largas que se pueden retomar** | `task_name = 'upgrade-aks-prod'`, `checkpoint_data = {"step": 3, "nodepools_done": ["system"]}` |
| *(nueva)* `learnings` | **Aprendizajes compartidos**: lo que hoy guarda tu skill en el repo | `"ImagePullBackOff → falta AcrPull en la identidad del kubelet"` |

`task_checkpoints` es lo que más valor aporta en sistemas. Si un upgrade de cluster se corta en el paso 3, otro compañero abre Claude al día siguiente, el agente lee el checkpoint y sigue desde el paso 4. Y gracias a `ON CONFLICT` no se duplica nada.

## 2. Cómo lo usa el repo de agentes
```
repo-sistemas/
├── .mcp.json                     → registra el servidor "agent-memory" (lo tienen todos al clonar)
├── .claude/
│   ├── settings.json             → hook PostToolUse → registra acciones en messages (automático)
│   ├── agents/aks-ops.md …       → "al empezar: search_learnings + get_task_state"
│   └── skills/aprendizaje/       → la skill actual, ahora llama a save_learning en vez de escribir ficheros
└── mcp/agent_memory/
    ├── server.py                 → FastMCP: expone las funciones como tools
    └── agent_tools.py            → el del lab + learnings, con ConnectionPool
```
| Necesidad | Mecanismo | Funciones del lab |
|---|---|---|
| El agente retoma una tarea | Tool MCP (lo decide el modelo) | `save_task_state`, `get_task_state` |
| El agente consulta y guarda conocimiento | Tool MCP | `create_conversation` + nuevas `search_learnings` / `save_learning` |
| Auditoría de todo lo ejecutado | **Hook** (siempre, sin depender del modelo) | `store_message` con `role = 'tool'` |

## 3. Qué cambiaría del código del lab para producción
| Lo que hemos visto en el lab | Cambio |
|---|---|
| **2,4 s por operación** (token y conexión nuevos cada vez) | `ConnectionPool` de psycopg, creado una vez al arrancar el MCP, y el token cacheado hasta que caduque. Bajaría a milisegundos |
| `user_id` lo pasa el código (`"user_123"`) | Que lo ponga la BD: `DEFAULT current_user`. Así cada usuario entra con su identidad y nadie puede firmar como otro |
| `conversation_id` admite NULL en `task_checkpoints` | `NOT NULL`, para que el `UNIQUE` del upsert funcione siempre |
| Índices redundantes | Quitar `idx_conversations_session_id` e `idx_task_checkpoints_conversation_id` |
| Los mensajes se guardan para siempre | Política de retención: por ejemplo, borrar mensajes de más de 90 días. Los `learnings` aprobados se quedan |
| El contenido va tal cual | **Sanear en el hook** antes del `INSERT` (tokens, contraseñas, salidas enormes). Los agentes de sistemas ven secretos a menudo |
| Firewall `AllowAll` | Acceso privado (VNet o tu Kubernetes) y publicación con Netskope Private Access, como hablamos |

## 4. Identidad y seguridad (lo delicado en sistemas)
- **En Azure Flexible Server:** creas un rol de PostgreSQL ligado a un **grupo de Entra** (por ejemplo, `sistemas-agentes`). Cada persona entra con su token, igual que en el lab, y el `DefaultAzureCredential` del código coge su `az login`. No hay ninguna contraseña compartida.
- **En tu Kubernetes (PostgreSQL propio):** no hay Entra. Usa un usuario por persona con contraseña en `~/.pgpass`, o certificados de cliente.
- **Permisos mínimos:** el rol de los agentes solo tiene `INSERT`/`SELECT` en sus tablas y `UPDATE` en `task_checkpoints`. Nada de `DELETE` ni de DDL. Así, aunque un agente se equivoque, no puede borrar el historial de auditoría.

## Orden de implantación
1. **Auditoría primero** (hook + `messages`): aporta valor desde el primer día, no depende del modelo y te da datos reales.
2. **Checkpoints** para 1–2 operaciones largas típicas (upgrades, migraciones).
3. **Migrar los `learnings`** desde la skill actual, con el estado `proposed`/`approved` sustituyendo a la revisión por PR.
4. **pgvector** solo cuando haya cientos de aprendizajes.

¿Lo añado a `notas/claude-code-hooks-skills-agentes.md` como sección "De lab a producción"? Seguiría siendo genérico, sin datos de tu empresa.

Mientras, pégame la siguiente tarea del lab (las consultas SQL). Son las 19:2x y el lab termina a las 19:50.


## 🧑 Alumno · 18:29 UTC

guardate la salida porque al finalizar el curso toda esta documetnacion la pasare a un agente cloud en el repo que usamos todo lo que tenemos de este curso y un primer trabajo pendiente sera esta tarea.


**🔧 Bash** — Guardar diseño en la nota y anotarlo en la sesión

```text
cd ~/claude/AI-200-Developing && cat >> notas/claude-code-hooks-skills-agentes.md <<'EOF'

## De lab a producción: memoria para un grupo de agentes de un departamento de sistemas
> **Trabajo pendiente tras el curso** (decidido el 10/11/2026): esta documentación se pasará a un agente en la nube del repo de agentes del departamento, y esta será una de sus primeras tareas. Diseño genérico, sin datos de ninguna empresa. Base: lab [LP5-01](../labs/lp5-01-pg-agent-backend/README.md) (esquema y funciones reutilizables).

### 1. Qué es cada tabla del lab en sistemas
| Tabla del lab | En el departamento | Ejemplo |
|---|---|---|
| `conversations` | Sesión de trabajo: quién, qué agente, sobre qué sistema | `user_id = <usuario>`, `metadata = {"agent": "aks-ops", "ticket": "INC-1234", "cluster": "prod"}` |
| `messages` (role `tool`) | Registro de acciones: cada comando o cambio del agente | `{"tool": "Bash", "cmd": "az aks upgrade ...", "exit": 0}` |
| `task_checkpoints` | Operaciones largas que se pueden retomar | `task_name = 'upgrade-aks-prod'`, `checkpoint_data = {"step": 3, "nodepools_done": ["system"]}` |
| *(nueva)* `learnings` | Aprendizajes compartidos (lo que hoy guarda una skill en el repo) | `"ImagePullBackOff → falta AcrPull en la identidad del kubelet"` |

`task_checkpoints` es lo de más valor: si un upgrade se corta en el paso 3, otro compañero abre Claude, el agente lee el checkpoint y sigue en el 4; `ON CONFLICT` evita duplicados.

### 2. Cómo lo usa el repo de agentes
ʼʼʼ
repo-agentes/
├── .mcp.json                     → registra el servidor "agent-memory" (lo tienen todos al clonar)
├── .claude/
│   ├── settings.json             → hook PostToolUse → registra acciones en messages (automático)
│   ├── agents/*.md               → "al empezar: search_learnings + get_task_state"
│   └── skills/aprendizaje/       → la skill actual llama a save_learning en vez de escribir ficheros
└── mcp/agent_memory/
    ├── server.py                 → FastMCP: expone las funciones como tools
    └── agent_tools.py            → el del lab + learnings, con ConnectionPool
ʼʼʼ
| Necesidad | Mecanismo | Funciones del lab |
|---|---|---|
| Retomar una tarea | Tool MCP (lo decide el modelo) | `save_task_state`, `get_task_state` |
| Consultar y guardar conocimiento | Tool MCP | `create_conversation` + nuevas `search_learnings` / `save_learning` |
| Auditar todo lo ejecutado | Hook (siempre, sin el modelo) | `store_message` con `role = 'tool'` |

### 3. Cambios al
… [recortado, 4977 caracteres]
```


<details><summary>Resultado</summary>

```text
23:- Diseño genérico para llevar el backend del lab a un grupo de agentes de sistemas (MCP + hooks + checkpoints + learnings) guardado en `notas/claude-code-hooks-skills-agentes.md`.
27:- **Tras el curso:** pasar la documentación a un agente en la nube del repo de agentes del departamento; primera tarea: memoria de agentes en PostgreSQL (diseño en `notas/claude-code-hooks-skills-agentes.md`, sección «De lab a producción»).
```
</details>


**🔧 Write**

```text
~/.claude/projects/-home-alumno-claude-AI-200-Developing/memory/project-traspaso-agente-cloud.md
```


**🔧 Bash** — Añadir la memoria al índice

```text
echo '- [Traspaso a agente cloud](project-traspaso-agente-cloud.md) — al acabar el curso, la doc pasa al repo de agentes del departamento; 1.ª tarea: memoria de agentes en PostgreSQL' >> ~/.claude/projects/-home-alumno-claude-AI-200-Developing/memory/MEMORY.md && tail -2 ~/.claude/projects/-home-alumno-claude-AI-200-Developing/memory/MEMORY.md
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/.claude/projects/-home-alumno-claude-AI-200-Developing/memory/project-traspaso-agente-cloud.md
```
</details>


<details><summary>Resultado</summary>

```text
- [Temporales en tmp/ del repo](feedback-temporales-en-repo-tmp.md) — nunca salir del repo; usar ./tmp/ (ignorado por git)
- [Traspaso a agente cloud](project-traspaso-agente-cloud.md) — al acabar el curso, la doc pasa al repo de agentes del departamento; 1.ª tarea: memoria de agentes en PostgreSQL
```
</details>


### 🤖 Claude · 18:30 UTC

He guardado el diseño en tres sitios:

| Dónde | Qué |
|---|---|
| `notas/claude-code-hooks-skills-agentes.md`, sección **«De lab a producción»** | El diseño completo: tablas del lab aplicadas a sistemas, estructura del repo de agentes (MCP + hooks + skill), cambios del código del lab para producción, identidad y seguridad, y el orden de implantación |
| `sesiones/2026-11-10-sesion-06-postgresql.md` | Como decisión del día y como **primer pendiente tras el curso** |
| Mi memoria del proyecto | Que al terminar el curso todo esto pasa a un agente en la nube del repo de tu departamento, y que esta es su primera tarea |

La memoria hace que, a partir de ahora, escriba la documentación pensando en que **otro agente la leerá sin contexto**: rutas, decisiones y salidas reales siempre explícitas.

La nota enlaza con el lab LP5-01, que tiene el código base (`agent_tools.py`, `sql/schema.sql`) y las salidas reales, entre ellas la medida de unos 2,4 s por operación que justifica el pool de conexiones.

Todo es genérico, sin datos de tu empresa, porque este repo es público. Los detalles concretos (nombres de clusters, usuarios, Netskope) se añadirán en el repo de destino. De momento nada de esto tiene commit; irá en la PR del día al cerrar.

**Volvemos al lab:** pégame la siguiente tarea de la plataforma (las consultas SQL). El lab 12 termina a las 19:50.


## 🧑 Alumno · 18:30 UTC

<pasted_content id="1013">
10. Module 01: Build an agent tool backend on Azure Database for PostgreSQL
Task 7: Query conversation context


In this section you practice querying the data an agent would use to make decisions.


Run the following command to connect to the agent_memory database using the environment variables.
psql "host=$env:DB_HOST port=5432 dbname=agent_memory user=$env:DB_USER sslmode=require"
💡 Tip: When query results are displayed, psql uses a pager if it can't fit the results in the current terminal window. If it does, press q to exit the pager and return to the psql prompt. Maximizing the terminal window will reduce this from happening, and make it easier to review the results from the commands.


Run the following query to find all conversations for a specific user. The test script created a conversation with user_id set to user_123.
SELECT id, session_id, started_at, metadata
FROM conversations
WHERE user_id = 'user_123'
ORDER BY started_at DESC;

Run the following query to get recent messages across all conversations. This returns the messages stored by the test script.
SELECT c.session_id, m.role, m.content, m.created_at
FROM messages m
JOIN conversations c ON m.conversation_id = c.id
ORDER BY m.created_at DESC
LIMIT 10;

Run the following query to find completed tasks. The test script updated the task status to completed at the end of the workflow.
SELECT
    c.session_id,
    t.task_name,
    t.status,
    t.checkpoint_data,
    t.updated_at
FROM task_checkpoints t
JOIN conversations c ON t.conversation_id = c.id
WHERE t.status = 'completed';

Run the following query to count messages by role in each conversation. This helps understand the distribution of user, assistant, system, and tool messages.
SELECT
    c.id AS conversation_id,
    m.role,
    COUNT(*) AS message_count
FROM conversations c
JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, m.role
ORDER BY c.id, m.role;

Enter quit in the psql prompt to exit.
</pasted_content id="1013">


**🔧 Write**

```text
~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/queries.sql
```


<details><summary>Resultado</summary>

```text
File created successfully at: ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend/sql/queries.sql (file state is current in your context — no need to Read it back)
```
</details>


### 🤖 Claude · 18:30 UTC

He dejado las 4 consultas de la Task 7, copiadas literalmente, en `labs/lp5-01-pg-agent-backend/sql/queries.sql`. Al principio del fichero he añadido `\pset pager off` para que no se abra el paginador y no tengas que pulsar `q`.

## Ejecución
Desde la carpeta del lab (si estás en `agent-backend`, haz antes `cd ..`):
```bash
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
source .env
psql "host=$DB_HOST port=5432 dbname=agent_memory user=$DB_USER sslmode=require"
```
Fíjate en que ahora es `dbname=agent_memory` y no `$DB_NAME`, que vale `postgres`. ✅ El prompt debe ser `agent_memory=>`.

```
\i sql/queries.sql
```
✅ Lo esperado (sé lo que guardó el test):
| Consulta | Resultado esperado |
|---|---|
| 1. Conversaciones de `user_123` | **1 fila**: `id 1`, session `84f355cd-…`, `metadata {"model": "gpt-4", "source": "web"}` |
| 2. Últimos 10 mensajes | **5 filas**, de la más reciente a la más antigua: assistant, tool, assistant, user, system |
| 3. Tareas completadas | **1 fila**: `research_postgresql`, `completed`, `{"step": 3, "summary": …, "sources_found": 2}` |
| 4. Mensajes por rol | **4 filas**: `assistant 2`, `system 1`, `tool 1`, `user 1` |

Sal con `\q`. El `quit` que pone la guía también funciona.

**Si falla:**
- **`password authentication failed`:** el token ha caducado (dura aproximadamente una hora desde la opción 3). Haz `python3 azdeploy.py` → `3` → `4`, luego `source .env`, y vuelve a conectar.
- Si la consulta 1 sale vacía, comprueba que estás en `agent_memory` y no en `postgres`.

## Qué practica cada consulta
| # | Patrón SQL | Para qué lo usaría el agente |
|---|---|---|
| 1 | `WHERE` + `ORDER BY … DESC` | Mostrar las sesiones anteriores del usuario |
| 2 | `JOIN` + `LIMIT` | Cargar contexto reciente. Fíjate en que esta usa `LIMIT` y no keyset pagination: con muchas filas, la teoría recomienda `WHERE (created_at, id) < (…)` |
| 3 | `JOIN` + filtro por `status` | Ver qué tareas ha terminado, para no repetirlas |
| 4 | `GROUP BY` + `COUNT(*)` | Métricas: cuánto usa herramientas el agente frente a cuánto conversa |

Pégame la salida y la guardo. Después, si esta era la última tarea del lab 12, hacemos el **cleanup verificado**.


## 🧑 Alumno · 18:35 UTC

<pasted_content id="1013">
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend
source .env
psql "host=$DB_HOST port=5432 dbname=agent_memory user=$DB_USER sslmode=require"
psql (16.15 (Ubuntu 16.15-0ubuntu0.24.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

agent_memory=> \i sql/queries.sql
Pager usage is off.
--- 1. Conversaciones de user_123
 id |              session_id              |          started_at           |              metadata               
----+--------------------------------------+-------------------------------+-------------------------------------
  1 | <guid> | 2026-11-10 18:22:21.538945+00 | {"model": "gpt-4", "source": "web"}
(1 row)

--- 2. Últimos 10 mensajes de todas las conversaciones
              session_id              |   role    |                                            content                                             |          created_at           
--------------------------------------+-----------+------------------------------------------------------------------------------------------------+-------------------------------
 <guid> | assistant | I found some resources about PostgreSQL. The official documentation is a great starting point. | 2026-11-10 18:22:32.655699+00
 <guid> | tool      | {"tool": "search", "results": ["PostgreSQL documentation", "PostgreSQL tutorial"]}             | 2026-11-10 18:22:30.276087+00
 <guid> | assistant | I'd be happy to help you research PostgreSQL. Let me search for relevant information.          | 2026-11-10 18:22:28.865078+00
 <guid> | user      | Can you help me find information about PostgreSQL?                                             | 2026-11-10 18:22:26.414443+00
 <guid> | system    | You are a helpful research assistant.                                                          | 2026-11-10 18:22:23.94591+00
(5 rows)

--- 3. Tareas completadas
              session_id              |      task_name      |  status   |                                        checkpoint_data                                        |         updated_at          
--------------------------------------+---------------------+-----------+-----------------------------------------------------------------------------------------------+-----------------------------
 <guid> | research_postgresql | completed | {"step": 3, "summary": "PostgreSQL is an advanced open-source database.", "sources_found": 2} | 2026-11-10 18:22:42.1541+00
(1 row)

--- 4. Mensajes por rol en cada conversación
 conversation_id |   role    | message_count 
-----------------+-----------+---------------
               1 | assistant |             2
               1 | system    |             1
               1 | tool      |             1
               1 | user      |             1
(4 rows)

agent_memory=> 
</pasted_content id="1013">


**🔧 Bash** — Guardar salida y comprobar grupos de recursos

```text
cd ~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend && export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt; az group exists --name rg-ai200-pg-agent; az group list --query "[].{name:name, state:properties.provisioningState}" -o table; cat >> salidas.md <<'EOF'

## 12. Task 7: consultas del contexto (`\i sql/queries.sql`)
ʼʼʼtext
agent_memory=> \i sql/queries.sql
Pager usage is off.
--- 1. Conversaciones de user_123
 id |              session_id              |          started_at           |              metadata
----+--------------------------------------+-------------------------------+-------------------------------------
  1 | <guid> | 2026-11-10 18:22:21.538945+00 | {"model": "gpt-4", "source": "web"}
(1 row)

--- 2. Últimos 10 mensajes de todas las conversaciones
 session_id | role      | content                                                                    | created_at
------------+-----------+----------------------------------------------------------------------------+-------------------------------
 84f355cd-… | assistant | I found some resources about PostgreSQL. The official documentation is ... | 2026-11-10 18:22:32.655699+00
 84f355cd-… | tool      | {"tool": "search", "results": ["PostgreSQL documentation", ...]}           | 2026-11-10 18:22:30.276087+00
 84f355cd-… | assistant | I'd be happy to help you research PostgreSQL. Let me search for ...        | 2026-11-10 18:22:28.865078+00
 84f355cd-… | user      | Can you help me find information about PostgreSQL?                         | 2026-11-10 18:22:26.414443+00
 84f355cd-… | system    | You are a helpful research assistant.                                      | 2026-11-10 18:22:23.94591+00
(5 rows)

--- 3. Tareas completadas
 session_id | task_name           | status    | checkpoint_data                                                                               | updated_at
------------+---------------------+-----------+-----------------------------------------------------------------------------------------------+-----------------------------
 84f355cd-… | research_postgresql | completed | {"step": 3, "summary": "PostgreSQL is an advanced open-source database.", "sources_found": 2} | 2026-11-10 18:22:42.1541+00
(1 row)

--- 4. Mensajes por rol en cada conversación
 conversation_id |   role    | message_count
-----------------+-----------+---------------
               1 | assistant |             2
               1 | sys
… [recortado, 2988 caracteres]
```


<details><summary>Resultado</summary>

```text
false
Name              State
----------------  ---------
az104-rg-region1  Succeeded
ai200rg           Succeeded
ok
```
</details>


### 🤖 Claude · 18:35 UTC

✅ **Task 7 completada:** las cuatro consultas coinciden exactamente con lo que guardó el test (1 conversación, 5 mensajes, 1 tarea `completed`, y 2/1/1/1 mensajes por rol). Lo he guardado en `salidas.md`.

Un detalle: las horas salen en **UTC** (`+00`), por eso pone 18:22 cuando en Madrid eran las 19:22. Es lo que hace `TIMESTAMPTZ`: guarda el instante exacto y lo muestra en la zona horaria de la sesión.

## Cleanup del lab 12
He mirado la suscripción en solo lectura:
- `rg-ai200-pg-agent`, el grupo del primer intento: **`false`, ya está borrado** ✅.
- Quedan `ai200rg` (el nuestro) y `az104-rg-region1`. Este último es de otro curso: **no lo toques**.

Si la plataforma no tiene más tareas del lab 12 (pégamelas si las hay), sal de `psql` con `\q` y borra el grupo:
```bash
az group delete --name ai200rg --yes --no-wait
```
✅ Comprobación inmediata:
```bash
az group show -n ai200rg --query properties.provisioningState -o tsv
```
Debe salir `Deleting`.

✅ Comprobación final, en 3–5 minutos (un servidor PostgreSQL tarda algo más en borrarse):
```bash
az group exists --name ai200rg
```
Debe salir `false`. Mientras salga `true`, el borrado sigue en curso: espera y repite. Si tras 15 minutos sigue en `true`, pégame `az group show -n ai200rg -o table`.

**Hazlo antes de cambiar de lab en la plataforma.** El jueves aprendimos que, al pasar al siguiente lab, puede asignarte otra suscripción, y entonces ya no podríamos verificar este borrado. Y el `Standard_D2ds_v4` cuesta dinero cada hora que está encendido.

Para el lab 13 (vector search) se usa otro starter con su propio `azdeploy.py`, así que no se pierde nada al borrar este servidor.


## 🧑 Alumno · 18:44 UTC

(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az group show -n ai200rg --query properties.provisioningState -o tsv
Succeeded
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 

<pasted_content id="1013">
agent_memory=> \q
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az group show -n ai200rg --query properties.provisioningState -o tsv
Succeeded
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ az group exists --name ai200rg
true
(.venv) alumno@pc:~/claude/AI-200-Developing/labs/lp5-01-pg-agent-backend$ 
</pasted_content id="1013">


### 🤖 Claude · 18:45 UTC

El estado `Succeeded` y `exists` = `true` indican que el borrado **no se ha lanzado**: en lo que has pegado falta el `az group delete`. Ejecútalo:

```bash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv
```
✅ El segundo comando debe devolver **`Deleting`**. Si sigue saliendo `Succeeded`, pégame la salida completa del `az group delete`: puede que haya devuelto un error, por ejemplo por un lock o por falta de permisos.

En 3–5 minutos:
```bash
az group exists --name ai200rg
```
✅ Debe salir `false`.


## 🧑 Alumno · 18:45 UTC

no he borrado nada


### 🤖 Claude · 18:45 UTC

De acuerdo, eso cuadra con lo que vemos: `Succeeded` y `true` significan que el grupo `ai200rg` y el servidor siguen intactos. No se ha borrado nada.

Ese borrado lo lanzas tú cuando decidas. Ten en cuenta dos cosas:
- **La regla del repo** es destruir lo creado al terminar cada lab, y el `Standard_D2ds_v4` cuesta dinero cada hora que está encendido.
- **Si la plataforma te cambia de suscripción** al pasar al lab 13, ya no podremos verificar el borrado (pasó el jueves con los labs 9 y 10).

Cuando lo tengas claro:
```bash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv   # esperado: Deleting
az group exists --name ai200rg                                         # en 3-5 min, esperado: false
```

Si prefieres mantenerlo, por ejemplo porque el profesor quiere revisarlo o porque la guía del lab 13 dice que reutiliza `ai200rg`, también vale. Dímelo y lo dejo apuntado como pendiente de borrar al cierre del día.


## 🧑 Alumno · 18:45 UTC

cerrado, next


**🔧 Bash** — Verificar en lectura el estado de ai200rg

```text
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt; az account show --query name -o tsv; az group show -n ai200rg --query properties.provisioningState -o tsv 2>&1 | tail -1; az group exists --name ai200rg
```


**🔧 Agent** — Leer guía lab LP5-02

```text
Lee https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html y devuélveme en español, de forma fiel y sin inventar: objetivo; URL exacta del zip starter; qué hace el script de despliegue (opciones del menú); variables del .env; cada Task con sus comandos exactos (literal en bloques de código cuando sean comandos cortos o SQL); nombres de ficheros y funciones a completar y qué hace cada una (si el código es largo, descríbelo con sus sentencias SQL clave literales: operadores <=>, CREATE EXTENSION, CREATE INDEX, etc.); salidas esperadas que muestre la guía; si se habilita pgvector vía azure.extensions; si usa un modelo de embeddings real (Azure OpenAI) o embeddings precalculados de ejemplo; y los pasos de cleanup.
```


<details><summary>Resultado</summary>

```text
XLabs-079
Deleting
true
```
</details>


<details><summary>Resultado</summary>

```text
The user doesn't want to proceed with this tool use. The tool use was rejected (eg. if it was a file edit, the new_string was NOT written to the file). STOP what you are doing and wait for the user to tell you how to proceed.
```
</details>


## 🧑 Alumno · 18:46 UTC

[Request interrupted by user for tool use]


## 🧑 Alumno · 18:46 UTC

para docuemntacion


**🔧 Bash** — Documentar el cierre y cleanup del lab 12

```text
python3 - <<'EOF'
p='README.md'; s=open(p).read()
s=s.replace("**Estado:** en curso (10/11/2026). Tasks 1-6 completadas: servidor `Ready`, esquema creado y `test_workflow.py` correcto (upsert verificado: mismo `checkpoint_id`).",
"**Estado:** completado el 10/11/2026 (servidor `Ready`, esquema creado, `test_workflow.py` correcto con el upsert verificado y las 4 consultas de la Task 7). **Cleanup: borrado lanzado (`Deleting`), pendiente de ver `false`**, ver abajo.")
i=s.index("## Cleanup")
s=s[:i]+"""## Cleanup
ʼʼʼbash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv   # Deleting
az group exists --name ai200rg                                         # esperado: false (tarda unos minutos)
ʼʼʼ
- `rg-ai200-pg-agent` (primer intento fallido en `eastus`, vacío): borrado y **verificado** (`az group exists` = `false`).
- `ai200rg` (servidor `psql-agent-dc48980e`): borrado lanzado; comprobación en solo lectura en la suscripción `XLabs-079`: `Deleting`, `exists` = `true` (en curso). **Pendiente de confirmar `false`.**
- `az104-rg-region1` aparece en la suscripción: es de otro curso, no se toca.
"""
open(p,'w').write(s)
EOF
cat >> salidas.md <<'EOF'

## 13. Cleanup
ʼʼʼtext
$ az group exists --name rg-ai200-pg-agent
false
$ az group list --query "[].{name:name, state:properties.provisioningState}" -o table
Name              State
----------------  ---------
az104-rg-region1  Succeeded
ai200rg           Succeeded
$ az group show -n ai200rg --query properties.provisioningState -o tsv     # antes de lanzar el delete
Succeeded
$ az group exists --name ai200rg
true
$ az group delete --name ai200rg --yes --no-wait
$ az group show -n ai200rg --query properties.provisioningState -o tsv
Deleting
$ az group exists --name ai200rg
true
ʼʼʼ
**Qué mirar:** `Succeeded` + `true` = el borrado aún no se había lanzado (`--no-wait` no muestra nada, así que hay que comprobarlo siempre). Tras el `delete`, `Deleting` confirma que está en marcha; `exists` sigue en `true` hasta que termina (un Flexible Server tarda unos minutos). El grupo del primer intento ya da `false`. `az104-rg-region1` es de otro curso.
EOF
cd ../.. && python3 - <<'EOF'
p='sesiones/2026-11-10-sesion-06-postgresql.md'; s=open(p).read()
s=s.replace("- **Lab LP5-01 (agent tool backend):** starter descargado en `labs/lp5-01-pg-agent-backend/`; en curso.",
"""- **Lab 12 (LP5-01, agent tool backend) completado:** PostgreSQL Flexible Server `psql-agent-dc48980e
… [recortado, 3341 caracteres]
```


<details><summary>Resultado</summary>

```text
21:- **Cleanup lab 12:** `rg-ai200-pg-agent` (intento fallido en `eastus`) verificado `false`; `ai200rg` en `Deleting`, pendiente de ver `false`.
31:- Confirmar `az group exists --name ai200rg` = `false` (suscripción `XLabs-079`).
```
</details>


### 🤖 Claude · 18:46 UTC

Documentado. El lab 12 queda **cerrado** en el repo:

| Fichero | Qué he actualizado |
|---|---|
| `labs/lp5-01-pg-agent-backend/README.md` | Estado **completado**, más la sección de cleanup con el estado real de cada grupo |
| `labs/lp5-01-pg-agent-backend/salidas.md` | Bloque 13 (cleanup), con la lección de que `--no-wait` no muestra nada y que siempre hay que comprobar el resultado |
| `sesiones/2026-11-10-sesion-06-postgresql.md` | Resumen del lab 12 y el pendiente de confirmar el borrado |

**Estado del borrado**, comprobado por mí en solo lectura en `XLabs-079`:
- `rg-ai200-pg-agent`: `false`, **verificado** ✅
- `ai200rg`: **`Deleting`**, en curso. Queda apuntado como pendiente confirmar el `false`.

Cuando quieras confirmarlo, en unos minutos:
```bash
az group exists --name ai200rg
```
Debe salir `false`.

Como has parado la consulta de la guía, no he preparado nada del lab 13. Cuando quieras empezarlo, pégame la guía de la plataforma y seguimos desde ahí.


## 🧑 Alumno · 18:47 UTC

lo debes tener en el drive


**🔧 Bash** — Revisar Drive y Links.txt buscando el lab 13

```text
cd ~/claude/AI-200-Developing/tmp/drive && curl -sL "https://drive.google.com/embeddedfolderview?id=10t4PEqTY9FqtvKHyTzmHpis8_VsHbFP3" -o root2.html && grep -oE 'flip-entry-title">[^<]+' root2.html | sed 's/.*">//'; echo ===; curl -sL "https://drive.usercontent.google.com/download?id=1W0-SIooyVPkAS_ZBZA21NvV49jchV8L4&export=download&confirm=t" -o Links2.txt; diff -q Links.txt Links2.txt; grep -n -i -B1 -A3 "LP05\|postgre\|lab 1[234]" Links2.txt | head -40
```


<details><summary>Resultado</summary>

```text
PPTs
Test-Modulos
Links.txt
===
```
</details>


**🔧 Bash** — Ver Links.txt y buscar ficheros nuevos en subcarpetas

```text
cat Links2.txt | tr -d '\r' | head -40; for f in 14xaP1NRpyfHflhJiB4o94wMSrZNrOPo2 1JhtRce3H8NVIdabA9APeO9xq5TFFm26N; do curl -sL "https://drive.google.com/embeddedfolderview?id=$f" | grep -oE 'flip-entry-title">[^<]+' | sed 's/.*">//'; done | grep -v -E 'Knowledge|AI-200T00A-0[0-5]'
```


<details><summary>Resultado</summary>

```text
Carpeta Compartida Curso AI-200: 
https://bit.ly/ai200-2026
https://drive.google.com/drive/folders/10t4PEqTY9FqtvKHyTzmHpis8_VsHbFP3

AI-200 Guide (MS Learn):
https://learn.microsoft.com/es-es/training/courses/ai-200t00?WT.mc_id=ilt_partner_webpage_wwl&ocid=6863100#study-guide

Contacto PUE (Corali):
https://help.sepe.pue.es/

Curso en web PUE: 
https://sepe.pue.es/cursos/ai-200-developing-ai-cloud-solutions-azure/ed2022

GitHub Labs AI-200:
https://microsoftlearning.github.io/mslearn-azure-ai/

Transcripcion <nombre>:
https://github.com/th3b1gbr0th3r/AI-200


Benjamin: Os dejo por aqui una app que desarrollé para practicar test desde el móvil (están incluidos los de AI-200):
IOS https://apps.apple.com/us/app/certify-me/id6760912194 
ANDROID https://play.google.com/store/apps/details?id=com.certifyme.app&hl=es_419&pli=1
```
</details>


### 🤖 Claude · 18:47 UTC

He revisado el Drive y **la guía del lab 13 no está**. La carpeta tiene lo mismo que esta tarde:

| Carpeta / fichero | Contenido |
|---|---|
| `PPTs/` | Presentaciones 00 a 05 (ya las tenemos en `docs/`) |
| `Test-Modulos/` | Knowledge check LP1 a LP5 (ya en `docs/`) |
| `Links.txt` | Sin cambios. En cuanto a los labs, solo enlaza a la guía pública de GitHub: https://microsoftlearning.github.io/mslearn-azure-ai/ |

Las guías **de la plataforma**, las que llevan `ai200rg`, `centralus` y el SKU obligatorio, solo están dentro del entorno del lab. En el Drive no aparecen.

Dos opciones para el lab 13:
1. **Leo la guía pública** (*Implement vector search*, que es el enlace de `Links.txt`), descargo el starter y te preparo los pasos. Supongo que la plataforma pedirá los mismos valores que en el lab 12 (`ai200rg`, `centralus`, `Standard_D2ds_v4`/`GeneralPurpose`), pero tendrás que confirmarlo con la guía de la plataforma antes de lanzar `azdeploy.py`.
2. **Me pegas la guía de la plataforma** a medida que avances, como en el lab 12. Es lo más seguro, porque ya vimos que la pública no menciona las restricciones de la política.

¿Cuál prefieres? Si eliges la 1, lanzo la lectura de la guía pública. Antes la cancelaste y no sé si fue por eso o porque querías que primero documentara el cierre del lab 12.


## 🧑 Alumno · 18:48 UTC

perdona me referia siguiente sesion


**🔧 Bash** — Comprobar si ai200rg ya está borrado

```text
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt; az group exists --name ai200rg
```


<details><summary>Resultado</summary>

```text
Exit code 1
ERROR: No subscription found. Run 'az account set' to select a subscription.
```
</details>


**🔧 Bash** — Documentar cleanup como no verificado

```text
cd ~/claude/AI-200-Developing && sed -i 's/^- `ai200rg` (servidor `psql-agent-dc48980e`): borrado lanzado; comprobación en solo lectura en la suscripción `XLabs-079`: `Deleting`, `exists` = `true` (en curso). \*\*Pendiente de confirmar `false`.\*\*/- `ai200rg` (servidor `psql-agent-dc48980e`): borrado lanzado; última comprobación en la suscripción `XLabs-079`: `Deleting`. **No verificado a `false`:** al cerrar el lab, `az` devolvió `No subscription found` (la suscripción temporal ya no está accesible)./' labs/lp5-01-pg-agent-backend/README.md && sed -i 's/\*\*Cleanup: borrado lanzado (`Deleting`), pendiente de ver `false`\*\*/**Cleanup: borrado lanzado (`Deleting`), no verificado** (la suscripción del lab dejó de estar accesible)/' labs/lp5-01-pg-agent-backend/README.md && sed -i 's/`ai200rg` en `Deleting`, pendiente de ver `false`./`ai200rg` en `Deleting`, **no verificado** a `false`: al cerrar el lab, `az group exists` devolvió `No subscription found`./; /^- Confirmar `az group exists --name ai200rg` = `false`/d' sesiones/2026-11-10-sesion-06-postgresql.md && grep -n "No subscription\|no verificado" labs/lp5-01-pg-agent-backend/README.md sesiones/2026-11-10-sesion-06-postgresql.md
```


<details><summary>Resultado</summary>

```text
sesiones/2026-11-10-sesion-06-postgresql.md:21:- **Cleanup lab 12:** `rg-ai200-pg-agent` (intento fallido en `eastus`) verificado `false`; `ai200rg` en `Deleting`, **no verificado** a `false`: al cerrar el lab, `az group exists` devolvió `No subscription found`.
labs/lp5-01-pg-agent-backend/README.md:6:**Estado:** completado el 10/11/2026 (servidor `Ready`, esquema creado, `test_workflow.py` correcto con el upsert verificado y las 4 consultas de la Task 7). **Cleanup: borrado lanzado (`Deleting`), no verificado** (la suscripción del lab dejó de estar accesible), ver abajo.
labs/lp5-01-pg-agent-backend/README.md:55:- `ai200rg` (servidor `psql-agent-dc48980e`): borrado lanzado; última comprobación en la suscripción `XLabs-079`: `Deleting`. **No verificado a `false`:** al cerrar el lab, `az` devolvió `No subscription found` (la suscripción temporal ya no está accesible).
[This command modified 2 files you've previously read: sesiones/2026-11-10-sesion-06-postgresql.md, labs/lp5-01-pg-agent-backend/README.md. Call Read before editing.]
```
</details>


### 🤖 Claude · 18:48 UTC

Entendido: cuando la próxima sesión empiece, descargaré la documentación nueva del Drive. Hoy no hay nada más ahí.

He intentado confirmar el borrado de `ai200rg` y `az` ya responde `No subscription found`: al cerrar el lab, la suscripción temporal ha desaparecido. Como hicimos el jueves, lo he dejado documentado como **no verificado** (el último estado que vimos fue `Deleting`), tanto en el README del lab como en el registro de la sesión.

**Pendiente de hoy y para la próxima sesión:**
- Labs 13 (vector search) y 14 (optimize) del LP5.
- Test LP5 (`docs/LP5 - Knowledge check.pdf`) y confirmar con el profesor las respuestas de las preguntas de repaso de las notas.
- El trabajo para después del curso: la memoria de agentes en PostgreSQL, en `notas/claude-code-hooks-skills-agentes.md`.

Todo lo de hoy sigue sin commit en la rama `dia-06-2026-11-10`: notas del LP5, el lab 12 completo, la nota de hooks y el `.gitignore` de LP5. ¿Cierro el día con `/aprender`? Eso hace el commit, el push y la PR, que luego fusionas tú.


