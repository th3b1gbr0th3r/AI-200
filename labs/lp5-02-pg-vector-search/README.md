# Lab LP5-02 · Implement vector search (plataforma: Lab 13 · AI-200-LP05M02)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/02-implement-vector-search.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3`. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Salidas reales saneadas: [`salidas.md`](salidas.md) (se crea al pegar las primeras). Lab anterior: [LP5-01](../lp5-01-pg-agent-backend/README.md).

**Estado:** parcial (10/11/2026). Hecho: servidor, allow-list de `vector`, esquema (pgvector 0.8.7, `vector(330)`, HNSW), `app.py` completado y Flask arrancado. **No hecho:** cargar productos y la búsqueda por similitud en la web (el alumno decidió cerrar el lab). **Cleanup verificado** (`ai200rg` = `false` a las 21:19).

## Objetivo
Búsqueda de productos similares con `pgvector`: habilitar la extensión, tabla `products` con `embedding vector(330)` e índice HNSW, y una app Flask (`client/app.py`) que carga productos, busca similares con `<=>` (coseno) y añade productos nuevos.

## Qué se construye (leído de `azdeploy.py` y del starter)
```
azdeploy.py (1) → RG + Flexible Server psql-vector-<sha1 8>, solo Entra, firewall AllowAll (como LP5-01)
azdeploy.py (2) → azure.extensions = vector (allow-list) → reinicio del servidor (1-2 min)
azdeploy.py (3) → estado · (4) → .env/.env.ps1 con token (~1 h) · (5) → salir
psql            → CREATE EXTENSION vector + tabla products + índice HNSW (m=16, ef_construction=64)
client/app.py   → completar /load-data, /search y /add-product; Flask en http://127.0.0.1:5000
```
- Embeddings **precalculados** en `client/sample_products.json` (10 productos) y `client/new_products.json` (3): no se llama a ningún modelo.
- **Dimensiones reales: 330** (comprobado en los dos JSON). La guía dice "384" en el texto, pero el SQL `vector(330)` es el correcto.
- Menú distinto al de LP5-01: aquí la opción 4 es la de conexión y la 5 la de salir.

## Valores de la plataforma
Confirmados por la guía de la plataforma: `ai200rg`, `centralus`, `Standard_D2ds_v4`/`GeneralPurpose` (igual que LP5-01). Servidor: `psql-vector-acc85432`, suscripción `XLabs-245`.

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `relation "products" does not exist` al cargar datos | Se arrancó la app antes de crear el esquema | `\i sql/schema.sql` en `psql` y volver a cargar |

## Cleanup
```bash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv   # Deleting
az group exists --name ai200rg                                         # esperado: false
```

**Verificado** el 10/11/2026 a las 21:19: `az group exists --name ai200rg` = `false` (suscripción `XLabs-245`).
