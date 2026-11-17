# LP6 · Módulo 1 · Operaciones de datos en Azure Managed Redis

Volver al [índice de LP6](06-redis.md). Lab: [LP6-01 · Data operations](../../labs/lp6-01-redis-data-ops/README.md).

## El servicio
Caché en memoria en Azure, **basada en Redis Enterprise**. Puerto TLS por defecto **10000** (en Azure Cache for Redis era 6380; **pregunta 1 del test**).

### Estrategias de caché
| Estrategia | Qué hace | Analogía K8s |
|---|---|---|
| Data cache (cache-aside) | Se carga bajo demanda y se invalida al cambiar el dato | caché de un informer: lees de memoria, si falta vas a la API |
| Content cache | Contenido estático (cabeceras, plantillas) servido desde memoria | contenido estático en un CDN/Ingress con caché |
| Session store | Estado de usuario por ID de sesión, en vez de cookies pesadas | estado fuera del Pod para que los Pods sean *stateless* |

### Tiers
| Tier | Relación memoria:vCPU | Para qué (según la presentación) |
|---|---|---|
| Memory Optimized | 8:1 | dev/test, más memoria y menos throughput |
| Balanced | 4:1 | cargas estándar (el lab usa `Balanced_B0`) |
| Compute Optimized | 2:1 | máximo throughput |
| Flash Optimized | datos fríos de RAM a NVMe | conjuntos de datos grandes |

Analogía: familias de VM de un node pool (memoria, general, cómputo).

## Clientes y buenas prácticas
- Librerías: `redis-py` (Python), StackExchange.Redis (.NET), Lettuce (Java), node_redis (Node.js).
- **Enterprise clustering** funciona con todos los clientes (`redis.Redis`); el **OSS clustering** exige clientes *cluster-aware* (`redis.cluster.RedisCluster`).
- Valores de clave pequeños: dividir los grandes en varias claves.
- **Pipelining** para operaciones por lotes: un solo viaje de ida y vuelta (como agrupar llamadas a la API en una).
- **Evitar `KEYS` en producción; usar `SCAN`** (**pregunta 2 del test**): `KEYS` bloquea el servidor recorriendo todo; `SCAN` itera por trozos (como paginar `kubectl get --chunk-size` en vez de listar todo de golpe).
- Redis y la app en la **misma región** de Azure.
- Escalar cuando memoria, CPU, clientes o ancho de banda superen el **75 %**.

## Tipos de datos del lab
| Tipo | Comandos | Uso |
|---|---|---|
| String | `SET`/`GET` | texto o datos serializados |
| Hash | `HSET`/`HGET`/`HGETALL` | campos de un objeto (perfil de usuario); es lo que usa el lab |
| List | | colas o feeds de actividad ordenados |
| Numérico | `INCR`/`DECR` atómicos | contadores y limitación de tasa |

```python
r = redis.Redis(host='...', port=10000, ssl=True, decode_responses=True)
r.hset('user:1001', mapping={'name': 'Alice', 'email': 'alice@example.com'})
pipe = r.pipeline(); pipe.hgetall('user:1001'); pipe.hgetall('user:1002'); res = pipe.execute()
```

## Expiración e invalidación
- `SETEX`: valor + TTL de forma atómica. `EXPIRE`: añade TTL a una clave existente (cualquier tipo). `TTL` devuelve **-1** (sin expiración) o **-2** (la clave no existe).
- Invalidación: por tiempo (TTL), manual (borrar al cambiar el origen), cache-aside (mirar caché, ir al origen en fallo y guardar con TTL) y por patrón (`SCAN` + borrar).
- Elegir el TTL según la volatilidad del dato (pregunta de debate de la presentación: TTL corto = más fallos de caché y más carga en la BD; largo = datos obsoletos).

## Autenticación en el lab
`redis-entraid` con `create_from_default_azure_credential` y el scope `https://redis.azure.com/.default`; la política de acceso de datos `default` se asigna al usuario con `az redisenterprise database access-policy-assignment`. Analogía: Workload Identity en vez de un Secret con la clave.

## Knowledge check del módulo (presentación)
> Respuestas razonadas por nosotros (la presentación no las trae): confirmarlas con el profesor.
1. Puerto TLS por defecto → **A. 10000** (la propia presentación lo dice en el resumen).
2. Comando a evitar para iterar claves → **A. `KEYS`** (usar `SCAN`).
