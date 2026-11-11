# Subagente agent-ac9696328c328a6bc · 2026-11-10

> Exportación saneada de la conversación con Claude Code (correo, GUID y ruta home sustituidos; resultados de herramientas recortados).


## 🧑 Alumno · 17:18 UTC

Lee https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html y devuélveme, en español y de forma fiel (sin inventar), un resumen detallado paso a paso del lab: objetivo, prerequisitos, URL exacta del zip/starter a descargar, recursos Azure que crea el script de despliegue (azdeploy.py u otro: tipo, SKU, nombres, región), variables de .env, cada Task con sus comandos exactos (copiar los comandos literalmente en bloques de código), código que hay que completar (nombres de funciones y ficheros, y el código de la solución que proporciona la guía, literal), salidas esperadas que muestre la guía, y los pasos de limpieza (cleanup). Indica también si menciona extensiones de PostgreSQL (azure_ai, vector, etc.), autenticación Entra ID o contraseña, y reglas de firewall.


**🔧 WebFetch**

```text
Extrae de forma completa y fiel toda la información del lab: objetivo, prerequisitos, URL exacta del zip/starter, recursos Azure del script de despliegue (tipo, SKU, nombres, región), variables de .env, cada Task con comandos literales, código a completar (funciones y ficheros), código de solución literal, salidas esperadas, pasos de limpieza, y menciones de extensiones de PostgreSQL (azure_ai, vector, etc.), autenticación Entra ID o contraseña, y reglas de firewall. Responde en español sin inventar; copia literalmente comandos y código.
```


<details><summary>Resultado</summary>

```text
Fetched https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html from a non-preapproved source (HTTP 200 OK, text/html, 23086 characters).
<fetched-web-content>
Build an agent tool backend on Azure Database for PostgreSQL | Develop AI Cloud Solutions on Microsoft Azure       

Develop AI Cloud Solutions on Microsoft Azure  [Home](https://microsoftlearning.github.io/mslearn-azure-ai)

* * *

* * *

Build an agent tool backend on Azure Database for PostgreSQL
============================================================

In this exercise, you create an Azure Database for PostgreSQL instance that serves as a tool backend for an AI agent. The database stores conversation context and task state that an agent can read and write during operation. You design a schema for agent memory, build Python functions that serve as agent tools, and test the complete workflow. This pattern provides a foundation for building AI agents that maintain persistent memory across sessions and can resume interrupted tasks.

Tasks performed in this exercise:

*   Download project starter files and configure the deployment script
*   Deploy an Azure Database for PostgreSQL Flexible Server with Microsoft Entra authentication
*   Build Python tool functions for conversation and task state management
*   Create a database schema for agent memory with tables for conversations, messages, and task checkpoints
*   Test the agent memory workflow us
… [recortado, 23338 caracteres]
```
</details>


**🔧 SubagentHandback**

```text
{"message": "Resumen del lab \"Build an agent tool backend on Azure Database for PostgreSQL\" (URL leída: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html, HTTP 200, contenido en vivo, no caché).\n\nNota sobre citas: la fuente no es preaprobada, así que las citas literales se limitan a 125 caracteres. Los comandos cortos los copio literales. Los bloques de código largos (funciones Python y CREATE TABLE completos) los describo en prosa con fragmentos literales cortos. Si necesitas el código exacto, la guía está en la URL de arriba.\n\n**1. Objetivo**\nCrear un backend en Azure Database for PostgreSQL que sirva de herramienta (tool backend) para un agente de IA. La base de datos guarda contexto de conversación y estado de tareas (checkpoints) que el agente lee y escribe. Se diseña un esquema de memoria, se escriben funciones Python como herramientas del agente y se prueba el flujo completo. Duración indicada: unos 30 minutos.\n\n**2. Prerrequisitos**\n- Suscripción de Azure con permisos y cuota suficientes.\n- Visual Studio Code.\n- Azure CLI (última versión).\n- Python 3.12 o superior.\n- Herramientas de línea de comandos de PostgreSQL (psql).\n- Opcional: extensión Ruff para VS Code.\n\n**3. Starter (zip) a descargar**\nURL exacta:\nʼʼʼ\nhttps://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-build-agent-python.zip\nʼʼʼ\nSe descomprime en una carpeta y se abre con File > Open Folder en VS Code.\n\n**4. Script de despliegue y recursos Azure**\n- Script: azdeploy.py.\n- Hay que editar solo dos valores al principio del script: el nombre del grupo de recursos (`\"<your-resource-group-name>\"`) y la región (`\"<your-azure-region>\"`). La guía dice que no se cambie nada más.\n- Recurso que crea: Azure Database for PostgreSQL Flexible Server con autenticación de Microsoft Entra (opción 1 del menú: \"Create PostgreSQL server with Entra authentication\"). Según la guía, esto deja la autenticación solo con Entra (Entra-only).\n- La guía NO indica: SKU, versión de PostgreSQL, nombre del servidor, ni región de ejemplo. Esos datos hay que leerlos en azdeploy.py, que no está en la guía.\n- Requisito de proveedor: `az provider register --namespace Microsoft.DBforPostgreSQL`.\n- Tiempo de despliegue: 5-10 minutos. Hay que dejar la terminal del despliegue abierta durante todo el ejercicio.\n- Si el script detecta un servidor existente, avisa de que redesplegar bor
… [recortado, 10885 caracteres]
```


<details><summary>Resultado</summary>

```text
{"success":true,"message":"Report delivered to your caller."}
```
</details>
