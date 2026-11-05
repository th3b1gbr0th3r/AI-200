# Lab LP4-01 · Build queries for Azure Cosmos DB (plataforma: Lab 9 · AI-200-LP04M01)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/01-build-rag-document-store.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3` (no existe `python`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** completado el 05/11/2026 (4 funciones, 5 tests `passed`, consultas desde la app). **Cleanup: borrado lanzado, no verificado**, ver abajo.

## Objetivo
Montar el almacén de documentos de una aplicación RAG sobre Cosmos DB for NoSQL: un contenedor con partition key `/documentId` y cuatro funciones en `client/rag_functions.py` (guardar chunk, leer por documento, buscar por metadatos, lectura puntual por id), con acceso sin claves (Entra ID + `DefaultAzureCredential`).

## Qué se construye
```
azdeploy.py (1) → resource group rg-ai200-cosmos-rag + cuenta Cosmos DB NoSQL serverless
                  + base de datos ragstore + contenedor chunks (partition key /documentId)
azdeploy.py (2) → rol Contributor (ARM, plano de control) + Cosmos DB Built-in Data Contributor (plano de datos)
azdeploy.py (4) → .env / .env.ps1 con COSMOS_ENDPOINT, COSMOS_DATABASE, COSMOS_CONTAINER (sin claves, no se suben)
client/         → completar las 4 funciones de rag_functions.py y probar con test_workflow.py / app.py (Flask)
```

## Diferencias de la plataforma respecto a la guía oficial
| Aspecto | Guía (VM Windows del lab) | Aquí (Linux, `mol-bastion`) |
|---|---|---|
| Descarga | Edge + Explorador | `curl -fLO` + `unzip` dentro de `labs/lp4-01-cosmos-queries/` |
| Script | `azdeploy.ps1` (la guía), pero el zip trae `azdeploy.py` | `python3 azdeploy.py` |
| Login | `az login` con navegador | `az login --use-device-code` |
| Editor | VS Code + terminal integrada | Terminal; edición con `sed`/Edit |

## Decisiones y valores
- Resource group: `rg-ai200-cosmos-rag`; región `eastus`; BD `ragstore`; contenedor `chunks`.
- Cuenta **serverless**: sin RU aprovisionadas; se paga por RU consumida (coste mínimo en un lab).
- Los `.env` generados no se suben (`.gitignore`).

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `Orden «python» no encontrada` | Solo existe `python3` | `python3 azdeploy.py` |
| `REQUESTS_CA_BUNDLE … invalid file path` | La variable apuntaba a una ruta inexistente | `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` |
| Contributor de ARM no basta para leer datos | Cosmos tiene un RBAC propio en el plano de datos | Asignar también `Cosmos DB Built-in Data Contributor` (opción 2) |

## Cleanup
Borrado lanzado el 05/11/2026 con:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-rag --no-wait --yes
```
Última comprobación en la suscripción del lab: el grupo estaba en `Deleting` (`az group show --query properties.provisioningState`). **No se pudo confirmar `false`**: al cambiar de sesión en la plataforma la suscripción pasó a ser otra y `az group exists` devuelve `false` allí siempre. Se documenta como **no verificado**. Las asignaciones de rol sobre la cuenta desaparecen con ella.
