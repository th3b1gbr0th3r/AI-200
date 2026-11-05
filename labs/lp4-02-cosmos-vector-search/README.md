# Lab LP4-02 · Implement vector search with Azure Cosmos DB (plataforma: Lab 10 · AI-200-LP04M02)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/02-build-semantic-search.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3` (no existe `python`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** completado el 05/11/2026 (3 funciones vectoriales, carga de 12 tickets y búsqueda por similitud; la búsqueda filtrada no se pegó). **Cleanup: borrado lanzado, no verificado**, ver abajo.

## Objetivo
Búsqueda semántica sobre Cosmos DB for NoSQL: un contenedor con política de embeddings (256 dimensiones, `float32`, coseno) e índice vectorial DiskANN, y funciones que calculan similitud con `VectorDistance`, con y sin filtro por categoría. Los embeddings vienen precalculados (`sample_vectors.json`): no hace falta Azure OpenAI.

## Qué se construye
```
azdeploy.py (1) → resource group rg-ai200-cosmos-vector + cuenta serverless con EnableNoSQLVectorSearch
                  + base de datos vectorstore + contenedor vectors (partition key /documentId)
                  con vector embedding policy (/embedding, float32, cosine, 256) y vector index diskANN
azdeploy.py (3) → rol Contributor (ARM) + Cosmos DB Built-in Data Contributor (datos)
azdeploy.py (4) → .env / .env.ps1 (endpoint, base de datos, contenedor; sin claves, no se suben)
client/         → completar vector_functions.py (3 funciones) y setup_container.py; probar con app.py (Flask)
```

## Diferencias respecto al lab 9 y a la guía
| Aspecto | Lab 9 | Lab 10 |
|---|---|---|
| Suscripción | `XLabs-278` | **`XLabs-274`** (nueva por sesión de plataforma) |
| Cuenta | serverless | serverless **+ `EnableNoSQLVectorSearch`** |
| Contenedor | `chunks`, indexado por defecto | `vectors`, `/embedding/*` **excluido** del índice normal + índice DiskANN |
| Menú de `azdeploy.py` | 2 = roles, 4 = `.env` | 3 = roles, 4 = `.env`; la opción 1 ya crea el contenedor vectorial |
| Resource group | `rg-ai200-cosmos-rag` | `rg-ai200-cosmos-vector` |

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `az group exists` da `false` para el grupo del lab 9 | Sesión nueva = **otra suscripción**; ese grupo no existe aquí | El cleanup se verifica antes de cambiar de sesión; si no, se documenta como «no verificado» |
| Contributor de ARM no basta para leer datos | Cosmos tiene un RBAC propio en el plano de datos | Asignar también `Cosmos DB Built-in Data Contributor` (opción 3) |

## Cleanup
Borrado lanzado el 05/11/2026 con:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-vector --no-wait --yes
```
Última comprobación en la suscripción del lab: `rg-ai200-cosmos-vector` en `Deleting`. **No se pudo confirmar `false`**: al abrir la sesión del lab 11 la suscripción volvió a cambiar y `az group exists` devuelve `false` allí siempre. Se documenta como **no verificado**.
