# Subagente agent-a03514d4047d0487f · 2026-11-10

> Exportación saneada de la conversación con Claude Code (correo, GUID y ruta home sustituidos; resultados de herramientas recortados).


## 🧑 Alumno · 18:45 UTC

Lee https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html y devuélveme en español, de forma fiel y sin inventar: objetivo; URL exacta del zip starter; qué hace el script de despliegue (opciones del menú); variables del .env; cada Task con sus comandos exactos (literal en bloques de código cuando sean comandos cortos o SQL); nombres de ficheros y funciones a completar y qué hace cada una (si el código es largo, descríbelo con sus sentencias SQL clave literales: operadores <=>, CREATE EXTENSION, CREATE INDEX, etc.); salidas esperadas que muestre la guía; si se habilita pgvector vía azure.extensions; si usa un modelo de embeddings real (Azure OpenAI) o embeddings precalculados de ejemplo; y los pasos de cleanup.


**🔧 WebFetch**

```text
Extrae de forma fiel y completa: objetivo; URL exacta del zip starter; qué hace el script de despliegue y sus opciones de menú; variables del .env; cada Task con sus comandos exactos (literal en bloques de código para comandos cortos y SQL); nombres de ficheros y funciones a completar y qué hace cada una (con sentencias SQL clave literales: operadores <=>, CREATE EXTENSION, CREATE INDEX, etc.); salidas esperadas; si se habilita pgvector vía azure.extensions; si usa un modelo de embeddings real (Azure OpenAI) o embeddings precalculados; y pasos de cleanup. Indica explícitamente cualquier apartado que no aparezca en la página.
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


## 🧑 Alumno · 18:46 UTC

[Request interrupted by user]
