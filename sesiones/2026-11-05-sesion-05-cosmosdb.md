# Sesión 5 — 05/11/2026 · LP4 Azure Cosmos DB for NoSQL

## Planning del día (enviado por el docente)
| Hora | Actividad |
|---|---|
| 18:00-18:20 | Test LP3 (6 preguntas) |
| 18:20-19:20 | LP4 (Cosmos DB), módulos 1, 2 y 3: Queries / Vector Search / Optimize (teoría) |
| 19:20-19:50 | Lab 9 · AI-200-LP04M01 · Build queries for Azure Cosmos DB |
| 19:50-20:10 | Descanso |
| 20:10-21:50 | Lab 10 · AI-200-LP04M02 · Implement vector search y Lab 11 · AI-200-LP04M03 · Optimize query performance |
| 21:50-22:00 | Test LP4 (6 preguntas) |

Numeración de la plataforma: LP4 = labs 9-11 (carpetas: `lp4-01-cosmos-queries` = lab 9, `lp4-02-cosmos-vector-search` = lab 10, `lp4-03-cosmos-optimize` = lab 11). Material: presentación `AI-200T00A-04` y knowledge check de LP4 (PDF en `docs/`).

## Qué se hizo
- **Lab 9 (LP4-01) completado:** almacén de documentos RAG en Cosmos DB (cuenta serverless, BD `ragstore`, contenedor `chunks`, partition key `/documentId`). Cuatro funciones de `rag_functions.py` (guardar chunk, leer por documento, buscar por metadatos, lectura puntual), 5/5 tests en `passed` (29,70 RU por 3 chunks ≈ 9,9 RU/chunk) y consultas desde la app Flask. La Task 6 (Query Explorer) se saltó por tiempo. Detalle en `labs/lp4-01-cosmos-queries/`.
- **Lab 10 (LP4-02) completado:** cuenta con `EnableNoSQLVectorSearch`, contenedor `vectors` con política de embeddings (256, `float32`, `cosine`) e índice DiskANN. Tres funciones de `vector_functions.py`; carga de 12 tickets (640,68 RU ≈ 53 RU/ticket) y búsqueda por similitud (primer resultado 0,9997 y el resto casi igual). La búsqueda filtrada no se pegó. Detalle en `labs/lp4-02-cosmos-vector-search/`.
- **Lab 11 (LP4-03) completado:** tres contenedores con índice `flat`, `quantizedFlat` y `diskANN`; dos funciones de `index_functions.py`; 500 tickets en cada contenedor. Escritura: 5.829,66 / 6.884,66 / 27.535,68 RU (`diskANN` ≈ 4,7× `flat`). Lectura Top 5: 10,13 / 21,60 / 21,60 RU. Con filtro `account`: 8,15 RU en los tres. Detalle en `labs/lp4-03-cosmos-optimize/` y conclusiones en `docs/modulos/04-cosmosdb.md`.
- **Cleanup:**
  - Lab 9 (`XLabs-278`) y lab 10 (`XLabs-274`): borrado lanzado y visto en `Deleting`, **no verificado** a `false` porque la sesión siguiente trajo otra suscripción.
  - Lab 11 (`XLabs-232`): borrado lanzado y **verificado** (`az group exists` = `false`; `az group list` sin ningún `rg-ai200-*`, solo `az104-rg7` de otro curso).
- Preparación: `.claude/settings.json` con permisos de `mkdir` dentro del repo, y regla nueva en `oscar.md` (todo dentro del repo, temporales en `./tmp/`).

- **Notas de la clase del docente** incorporadas a `docs/modulos/04-cosmosdb.md` (extraídas, sin publicar la transcripción): jerarquía de Cosmos DB, consistencia, partition key, vectores y RRF, índices, avisos del test y corrección del test LP3. Dato clave: `quantizedFlat` y `diskANN` necesitan 1.000+ vectores para activarse, lo que confirma la explicación del coste idéntico en el lab 11.
- **Quiz LP4 (`/quiz-lab`):** 2 de 7 respondidas correctas antes de salir; puntos débiles: coste de escritura frente a lectura y query cross-partition.

## Decisiones
- Starters descargados con `curl` y extraídos en `labs/lp4-0N-*` (Linux, `python3`, `source .env`), en lugar de Edge/VS Code/PowerShell de la guía. El parche de PowerShell del lab 10 no aplica a `azdeploy.py`.
- Entornos virtuales en `client/.venv` dentro del repo (ignorados por git).
- El acceso a Cosmos es sin claves: `DefaultAzureCredential` con `az login` y los roles de ARM y de datos.

## Aprendizajes
Entrada completa en [`docs/aprendizajes.md`](../docs/aprendizajes.md) (2026-11-05).
- **Principal:** en Cosmos DB el coste se mide en RU y depende de la forma de la consulta (lectura puntual < una partición < cross-partition) y del índice (`diskANN` ≈ 4,7× más caro de escribir; a 500 vectores `flat` gana leyendo).
- **Apoyo:** dos planos de permisos (ARM y datos); la política vectorial es inmutable y el índice no; cada lab trae otra suscripción y hay que verificar el cleanup antes de cambiar de sesión.

## Pendientes
- Hacer el **test LP4** (6 preguntas, `docs/LP4 - Knowledge check.pdf`) y la corrección del test de LP3.
- Task 6 del lab 9 (Query Explorer) y la búsqueda filtrada del lab 10: no ejecutadas; opcionales.
- Hipótesis aún sin verificar: la calidad semántica baja de los embeddings de ejemplo (el coste idéntico de `quantizedFlat` y `diskANN` ya está explicado por el umbral de 1.000 vectores).
- Mergear la PR del día (el merge lo hace el alumno) y, si hay un lab 12 (memoria persistente), planificarlo con el docente.
- `az logout` al terminar.
