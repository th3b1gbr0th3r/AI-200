# Lab LP4-03 · Optimize query performance for Azure Cosmos DB (plataforma: Lab 11 · AI-200-LP04M03)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/cosmosdb/03-optimize-query-performance.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3`. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase y conclusiones: [`docs/modulos/04-cosmosdb.md`](../../docs/modulos/04-cosmosdb.md). **Salidas reales saneadas: [`salidas.md`](salidas.md).**

**Estado:** en curso (05/11/2026). Despliegue, funciones, carga, comparación de búsqueda y búsqueda filtrada hechos; pendiente el Cleanup.

## Objetivo
Medir cómo cambia el coste (RU) y el tiempo de la misma búsqueda vectorial según el índice: `flat` (exacto), `quantizedFlat` (exacto sobre vectores comprimidos) y `diskANN` (aproximado, grafo).

## Qué se construye
```
azdeploy.py (1) → resource group rg-ai200-cosmos-optimize + cuenta serverless con EnableNoSQLVectorSearch + base indexoptimize
azdeploy.py (2) → 3 contenedores: vectors-flat, vectors-quantized, vectors-diskann (/documentId; /embedding float32 cosine 256)
azdeploy.py (3) → rol Contributor (ARM) + Cosmos DB Built-in Data Contributor (datos)
azdeploy.py (4) → .env (endpoint y base de datos; sin claves, no se sube)
client/         → completar vector_similarity_search y compare_index_performance; app Flask: carga 500 tickets y compara
```

## Conclusiones medidas (500 vectores)
| Índice | Escritura (RU/doc) | Lectura Top 5 (RU) | Tiempo |
|---|---|---|---|
| `flat` | ≈ 11,7 | **10,13** | 604 ms |
| `quantizedFlat` | ≈ 13,8 | 21,60 | 501 ms |
| `diskANN` | ≈ 55,1 (≈ 4,7× `flat`) | 21,60 | 538 ms |

- `diskANN` es el más caro de escribir; a esta escala `flat` gana en lectura. `diskANN` compensa con muchos vectores.
- `quantizedFlat` y `diskANN` costaron lo mismo: hipótesis (no verificada) de que con pocos vectores no hay un grafo útil.
- Los tiempos dependen de la red/proxy y no distinguen los índices. Los resultados fueron los mismos (diferencia solo por un empate de puntuación).
- Los datos no tienen significado semántico: sirven para medir coste, no relevancia. Detalle y explicación en [`salidas.md`](salidas.md) y en `docs/modulos/04-cosmosdb.md`.

## Diferencias respecto a los labs 9 y 10
| Aspecto | Lab 10 | Lab 11 |
|---|---|---|
| Suscripción | `XLabs-274` | **`XLabs-232`** |
| Contenedores | 1 (`vectors`, DiskANN), creado por la opción 1 | **3** (uno por índice), creados por la opción 2 |
| Datos | 12 tickets | 500 tickets en cada contenedor |
| `.env` | endpoint, base y contenedor | endpoint y base (los contenedores están fijados en el código) |

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `bash: .env: No existe el archivo` | No se había lanzado la opción 4 | Opción 4 del menú y luego `source .env` |
| Typo `ca-certificates.crtrt` en el `export` | Error al teclear | Repetir el `export` con la ruta correcta (`az` falla con «invalid file path» si la ruta no existe) |
| Cada lab trae otra suscripción | La plataforma crea una nueva por sesión | Verificar el cleanup **antes** de abrir la siguiente sesión |

## Cleanup
**Pendiente** (obligatorio al terminar el lab):
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name rg-ai200-cosmos-optimize --no-wait --yes
az group exists --name rg-ai200-cosmos-optimize    # repetir hasta que devuelva false
```
Verificación final del día: `az group list -o table` sin ningún `rg-ai200-*`.
