# Subagente agent-aa72f44644c43a720 · 2026-11-10

> Exportación saneada de la conversación con Claude Code (correo, GUID y ruta home sustituidos; resultados de herramientas recortados).


## 🧑 Alumno · 18:49 UTC

Lee https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html y devuélveme en español, de forma fiel y sin inventar: objetivo; URL exacta del zip starter; qué hace el script de despliegue (opciones del menú); variables del .env; cada Task con sus comandos exactos (literal en bloques de código para comandos y SQL); nombres de ficheros y funciones a completar y qué hace cada una, con las sentencias SQL clave literales (CREATE EXTENSION, CREATE TABLE con vector(n), CREATE INDEX, operadores <=> etc.); salidas esperadas que muestre la guía; si se habilita pgvector vía azure.extensions; si usa un modelo de embeddings real (Azure OpenAI) o embeddings precalculados; y los pasos de cleanup.


**🔧 WebFetch**

```text
Extract everything needed: objective; exact starter zip URL; deployment script and its menu options; .env variables; each Task with exact commands and SQL in code blocks; file and function names to complete with what each does and key SQL verbatim (CREATE EXTENSION, CREATE TABLE with vector(n), CREATE INDEX, <=> operators); expected outputs shown; whether pgvector is enabled via azure.extensions; whether it uses Azure OpenAI embeddings or precomputed embeddings; cleanup steps. Quote verbatim where it matters.
```


<details><summary>Resultado</summary>

```text
Fetched https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html from a non-preapproved source (HTTP 200 OK, text/html, 23676 characters).
<fetched-web-content>
Implement vector search on Azure Database for PostgreSQL | Develop AI Cloud Solutions on Microsoft Azure       

Develop AI Cloud Solutions on Microsoft Azure  [Home](https://microsoftlearning.github.io/mslearn-azure-ai)

* * *

* * *

Implement vector search on Azure Database for PostgreSQL
========================================================

In this exercise, you build a product similarity search application using Azure Database for PostgreSQL and the pgvector extension. You enable vector storage capabilities, create a database schema for products with embeddings, load sample data through a Flask web application, and perform similarity searches to find related products. This pattern provides a foundation for building recommendation systems, semantic search features, and other AI-powered applications.

Tasks performed in this exercise:

*   Download project starter files and configure the deployment script
*   Deploy an Azure Database for PostgreSQL Flexible Server with Microsoft Entra authentication
*   Complete the Flask application code while the server deploys
*   Enable the pgvector extension and create the products table schema
*   Run the Flask application to load products and perform similarity searches
*   Add new products and observe ho
… [recortado, 23927 caracteres]
```
</details>


**🔧 SubagentHandback**

```text
{"message": "Informe sobre la guía \"Implement vector search on Azure Database for PostgreSQL\" (ejercicio 02 del laboratorio de Microsoft Learning).\n\nURL leída: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html (HTTP 200, lectura completa). Fuente no preaprobada: las citas literales son breves, el resto está parafraseado.\n\n**1. Objetivo**\nConstruir una aplicación de búsqueda de similitud de productos con Azure Database for PostgreSQL y la extensión pgvector: habilitar el almacenamiento vectorial, crear el esquema de productos con embeddings, cargar datos de ejemplo mediante una aplicación web Flask y hacer búsquedas por similitud. Duración aproximada: 30 minutos. Requisitos: suscripción de Azure, VS Code, Azure CLI, Python 3.12 o superior, psql y, opcionalmente, la extensión Ruff.\n\n**2. URL exacta del zip starter**\nhttps://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-vector-search-python.zip\n\n**3. Script de despliegue (azdeploy.py)**\n- Antes de ejecutarlo hay que editar dos valores al inicio del script: \"<your-resource-group-name>\" (nombre del grupo de recursos) y \"<your-azure-region>\" (región). La guía indica no cambiar nada más.\n- Ejecución: `python azdeploy.py`\n- Opciones del menú:\n  1. Crear el servidor PostgreSQL con autenticación de Entra (solo Entra). Tarda de 5 a 10 minutos.\n  2. Configurar la lista de permitidos de `azure.extensions` (allow-list) para añadir `vector`. El servidor se reinicia (1-2 minutos).\n  3. Comprobar el estado del despliegue.\n  4. Obtener la información de conexión y un token de acceso. Crea los ficheros de variables de entorno `.env` y `.env.ps1`.\n  5. Salir del script.\n\n**4. Variables del .env**\nLa guía no enumera todas las variables. Nombra explícitamente `DB_HOST`, `DB_NAME` y `DB_USER` (DB_USER es el correo de la cuenta de Azure). En la sección de solución de problemas menciona `PGPASSWORD`, que debe estar definida. El token caduca aproximadamente en una hora; hay que volver a ejecutar la opción 4 para generar uno nuevo.\n\n**5. Tasks y comandos**\n\nParte 1: descarga y despliegue\n- Descargar y descomprimir el zip, abrir la carpeta en VS Code y editar azdeploy.py como se indica arriba.\n- Comandos en la terminal:\nʼʼʼ\naz login\naz provider register --namespace Microsoft.DBforPostgreSQL\npython azdeploy.py\nʼʼʼ\n- En el menú del script: opción `1`. Se deja la terminal abierta durante t
… [recortado, 7351 caracteres]
```


<details><summary>Resultado</summary>

```text
{"success":true,"message":"Report delivered to your caller."}
```
</details>
