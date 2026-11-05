# LP4 · Desarrollar soluciones de IA con Azure Cosmos DB for NoSQL

Notas propias del día 5 (05/11/2026), con los datos medidos en los labs. Para un perfil K8s: lo nuevo es el modelo de coste (RU), la partition key y los índices vectoriales. Presentación del instructor: `docs/AI-200T00A-04_…pdf`.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Lab |
|---|---|---|
| 1 | Consultas y almacén de documentos para RAG | [LP4-01](../../labs/lp4-01-cosmos-queries/README.md) |
| 2 | Búsqueda vectorial (`VectorDistance`, DiskANN) | [LP4-02](../../labs/lp4-02-cosmos-vector-search/README.md) |
| 3 | Optimizar consultas: `flat` / `quantizedFlat` / `diskANN` | [LP4-03](../../labs/lp4-03-cosmos-optimize/README.md) |

## Conceptos base (con analogía K8s)
| Concepto | Qué es | Analogía |
|---|---|---|
| Partition key | Campo que reparte los datos en particiones lógicas (`/documentId`) | shard key; como indicar namespace y nombre exactos en `kubectl get` |
| `id` + partition key | Identifican un documento; el `id` es único **dentro** de la partición | clave de objeto en un namespace |
| RU (Request Units) | Moneda de cada operación (lectura puntual de 1 KB ≈ 1 RU) | requests/limits, pero cobrado por operación |
| Serverless | Sin RU aprovisionadas; pagas las consumidas | escalado a cero, coste por uso |
| Plano de control / de datos | Dos RBAC distintos: ARM (`Contributor`) y Cosmos (`Built-in Data Contributor`) | crear un `Deployment` frente a hacer `exec` en el pod |
| `DefaultAzureCredential` | Prueba entorno, workload identity, managed identity y `az login` | el mismo código sirve en el PC y en AKS con Workload Identity |

## Las cuatro operaciones del lab 9 (de más barata a más cara)
| Operación | Función | Partición | Coste |
|---|---|---|---|
| Lectura puntual (`read_item`, `id` + partition key) | `get_chunk_by_id` | directa | ≈ 1 RU: la mejor opción si conoces ambas claves |
| Query con partition key | `get_chunks_by_document` | una sola | baja |
| Query cross-partition (`enable_cross_partition_query`) | `search_chunks_by_metadata` | todas (fan-out) | la más alta |
| Escritura (`upsert_item`) | `store_document_chunk` | la del `documentId` | varias RU (medido: ≈ 9,9 RU/chunk) |

Puntos de examen:
- **Parametrizar siempre** (`@param`): evita inyección SQL y reutiliza el plan.
- **Filtrar por un campo que no es la partition key obliga al fan-out**, aunque todos los resultados estén en un solo documento.
- **`upsert_item` reemplaza el documento entero** (no hace merge); para cambiar un campo, `patch_item`. Es idempotente.
- `OFFSET 0 LIMIT n` va junto; `ARRAY_CONTAINS` busca dentro de arrays.
- **Cosmos indexa todo por defecto**, y por eso escribir es caro.

## Búsqueda vectorial (lab 10)
- **Vector embedding policy** (ruta, tipo, dimensiones, función de distancia): **inmutable** tras crear el contenedor. Aquí: `/embedding`, `float32`, 256, `cosine`.
- **Vector index** (`diskANN`, `flat`, `quantizedFlat`): en la indexing policy; se puede cambiar.
- **Excluir `/embedding/*` del índice normal**: los vectores usan su índice propio y no se indexan como 256 propiedades sueltas.
- La cuenta necesita la capability `EnableNoSQLVectorSearch`.
- **`TOP n` es obligatorio** en consultas vectoriales; con `ORDER BY VectorDistance(...)`.
- Con `cosine`, **la puntuación más alta es la más parecida**, y el `ORDER BY` la pone primero.
- **Búsqueda híbrida:** filtro por metadato (`WHERE c.metadata.category = …`) + ranking por similitud.
- **La calidad la da el modelo de embeddings, no Cosmos**: Cosmos solo ordena por distancia entre los vectores que le das. En el lab 10, solo el primer resultado fue razonable (≈ 0,9997); del 2.º al 4.º las puntuaciones eran casi iguales (≈ 0,992) y sin sentido semántico.

## Comparación de índices (lab 11, 500 vectores de 256 dimensiones)
**Escritura** (carga de 500 documentos en cada contenedor):
| Índice | RU totales | RU/documento | Respecto a `flat` |
|---|---|---|---|
| `flat` | 5.829,66 | ≈ 11,7 | 1,0× |
| `quantizedFlat` | 6.884,66 | ≈ 13,8 | 1,2× |
| `diskANN` | 27.535,68 | ≈ 55,1 | **4,7×** |

**Lectura** (misma consulta Top 5):
| Índice | RU | Tiempo | Resultados |
|---|---|---|---|
| `flat` | **10,13** | 604 ms | 5 |
| `quantizedFlat` | 21,60 | 501 ms | 5 |
| `diskANN` | 21,60 | 538 ms | 5 |

Conclusiones:
1. **`diskANN` es el más caro de escribir** (≈ 4,7×): cada vector se enlaza en un grafo de vecinos. Coincide con el lab 10 (≈ 53 RU por ticket con DiskANN frente a ≈ 55 aquí).
2. **A esta escala `flat` gana en lectura** (la mitad de RU): recorrer 500 vectores es barato y no hay nada que acelerar. `diskANN` compensa con muchos vectores.
3. **`quantizedFlat` y `diskANN` costaron exactamente lo mismo** (21,60). Explicación (diapositivas del curso): **necesitan 1.000 o más vectores para activarse; por debajo caen a un escaneo por fuerza bruta**. Con 500 vectores los dos hicieron lo mismo, y por eso `flat` (exacto, sin umbral) salió más barato.
4. **Los tiempos no distinguen nada:** dependen de la latencia de red desde `mol-bastion` y del proxy, y es una sola ejecución.
5. **Los resultados salieron idénticos.** La única diferencia (`doc-account-005` frente a `doc-account-100`) fue un **empate** de puntuación y texto (el generador repite plantillas), no pérdida de precisión.
6. **Los datos de ese lab no tienen significado semántico** (un ticket de facturación salió el primero para una consulta de login): sirven para medir coste, no relevancia.

**Con filtro** (`WHERE category = 'account'` + Top 5): los tres índices costaron **8,15 RU**, menos que sin filtro (`flat` 10,13 → 8,15; `quantizedFlat`/`diskANN` 21,60 → 8,15, un −62 %). Filtrar reduce los candidatos antes del ranking vectorial, y el resultado solo contiene la categoría pedida. Que los tres coincidan es coherente con el umbral: con menos de 1.000 vectores `quantizedFlat` y `diskANN` no se activan, y además el filtro deja aún menos candidatos.

Guía de elección. **Presentación del curso** (la que cae en el test):
| Índice | Mejor para | Dimensiones máx. |
|---|---|---|
| `flat` | menos de 1.000 vectores, búsqueda exacta | 505 |
| `quantizedFlat` | 1.000 a 50.000 vectores (comprimido) | 4.096 |
| `diskANN` | más de 50.000 vectores (producción) | 4.096 |

`quantizedFlat` y `diskANN` **necesitan 1.000+ vectores para activarse**; por debajo hacen un escaneo por fuerza bruta. La guía oficial del lab 11 da otra regla orientativa (menos de ~10.000 vectores: `flat`; memoria limitada: `quantizedFlat`; gran escala: `diskANN`, ≈ 95 % de recall). Para el examen, usa la tabla de la presentación.

## Lo que añadió el docente en clase (05/11/2026)
Contenido extraído de la sesión (sin transcripción literal):
- **Jerarquía de Cosmos DB y analogía relacional:** cuenta (servidor/cluster) → base de datos → contenedor (≈ tabla; **no** es un contenedor Docker) → ítem (≈ fila, normalmente JSON). No hay relaciones explícitas entre contenedores: las define quien diseña.
- **Cosmos DB es un «paraguas» de APIs** (NoSQL, MongoDB, Cassandra, Gremlin, Table); en el curso se usa **NoSQL**, el que se consulta con SQL. **No existe versión on-premises.** Es PaaS: no hay que gestionar VM, motor ni parches. Distribución global: eliges en cuántas regiones replicar (a más regiones, más coste).
- **Partition key:** la decisión de diseño más crítica; se elige un campo de **alta cardinalidad** (usuario, identificador, categoría…). Con ella la query va a una partición (menos RU y latencia); sin ella hace fan-out a todas.
- **Rendimiento (throughput):** manual (RU fijas) o **autoscale** (entre el 10 % y el 100 % del máximo). Lectura puntual ≈ 1 RU; una escritura puede costar de 5 a 10 RU o más según índices y consistencia.
- **Patrón singleton del cliente:** reutilizar un único `CosmosClient` (pool de conexiones y caché).
- **Consultas parametrizadas** frente a literales (más seguras y legibles).
- **Cinco niveles de consistencia** (de más a menos consistente): Strong, Bounded staleness, **Session**, Consistent prefix, Eventual. Más consistencia = menos rendimiento. Strong y Bounded cuestan **2×** en RU de lectura; Session, Consistent prefix y Eventual **1×**. Para IA: **Session** (garantiza leer lo que escribiste en la sesión; pasar el *session token* de las escrituras a las lecturas); **Eventual** para analítica y procesos en segundo plano; **Strong** solo en casos financieros o regulatorios. Se define a nivel de cuenta (no se mezclan varios a la vez); un cliente por nivel si se necesitan distintos.
- **Vectores y embeddings:** un embedding es un array numérico por documento (cada dimensión es una característica; `text-embedding-ada-002` usa 1.536). Se guarda **en el mismo documento** que los datos de negocio, sin base de datos aparte. Funciones de distancia: **cosine**, dot product y euclidean. Con cosine, 1 = idéntico y valores altos (≈ 0,7-0,9) = bastante similares. `TOP n` es obligatorio.
- **Búsqueda híbrida con RRF:** `ORDER BY RANK RRF(VectorDistance(...), FullTextScore(...))` mezcla ranking semántico y por palabras clave; requiere política e índice de **full-text**. Útil para códigos de error (búsqueda literal). Un **pre-filtro** (`WHERE`, partition key) reduce el espacio de búsqueda.
- **Refrescar embeddings:** al cambiar un documento hay que regenerar su vector (change feed); un hash del contenido evita regenerar si solo cambian metadatos; embeddings por lotes; procesos idempotentes; manejo de borrados; *dead-letter* para lo que no se pueda procesar (se verá con colas).
- **Optimizar índices:** por defecto indexa **todas** las propiedades (buen punto de partida, caro al escalar). Política personalizada: incluir/excluir rutas, **índices compuestos** para filtro + ordenación, excluir los arrays de embeddings del índice de rango, no indexar textos muy largos. Cada índice compuesto sube el coste de escritura: cargas con muchas escrituras = pocos índices; cargas de lectura (la mayoría de apps de IA) = invertir en índices. Métricas a vigilar: índice utilizado, documentos recuperados frente a devueltos, y RU por query (`x-ms-request-charge`).
- **Firewall integrado:** los servicios gestionados de base de datos filtran por defecto el tráfico de Internet. Si no conecta, permitir la IP pública de salida en *Networking*. En nuestros tres labs no hizo falta.
- **Costes:** no dejar recursos desplegados (un día o una semana duele); si no da tiempo a un lab, desprovisionar y hacerlo otro día.

## Test y examen (avisos del docente)
- Las preguntas del examen salen de los tests de cada learning path, **con las mismas respuestas pero en otro orden**: no memorizar la letra, sino la respuesta correcta. En los tests hechos hasta ahora la **A** era correcta en la inmensa mayoría; en el examen no será así.
- El test es de obligado cumplimiento para aprobar el curso. Se corrige en la clase siguiente.
- **Próximo martes:** learning path de bases de datos **relacionales** con **PostgreSQL** en Azure (Azure SQL no entra). Los labs serán parecidos a los de Cosmos DB.
- Nomenclatura Microsoft: los *learning paths* son lo que antes eran módulos, y los «módulos» actuales son las lecciones.

## Corrección del test LP3 (AKS) en clase
| Tema | Respuesta correcta | Por qué |
|---|---|---|
| Exponer una app a Internet | **Service LoadBalancer** (balanceador de carga de Azure) | El ClusterIP es una IP privada del cluster |
| Que el tráfico llegue a los pods | Las **etiquetas del pod** de la plantilla deben coincidir con el **selector del Service** | No es el nombre del Deployment ni el puerto |
| Guardar una cadena de conexión con contraseña | **Secret** | Mantiene lo sensible fuera del código y del control de versiones |
| Cambiar un `.json` sin reconstruir la imagen | Montar un **ConfigMap como volumen** | Reconstruir la imagen es justo lo que se quiere evitar |
| Errores 500 intermitentes en un pod | **`kubectl logs`** | Lo primero siempre son los logs |
| Service sin endpoints con pods sanos | **`kubectl describe service`** | Revela si selector y etiquetas no casan |

## Limitaciones y buenas prácticas anotadas
- `get_container()` de los starters crea cliente y credencial en cada llamada: en producción, **una sola vez** y reutilizar (el lab 11 ya cachea cliente y contenedores).
- `search_chunks_by_metadata` solo usa el **primer tag** (`filters["tags"][0]`).
- Las RU del SDK en consultas son aproximadas (solo la última página); en producción, Azure Monitor.
- Los tests del lab 9 solo exigen `>=`: comprueban que responden, no el contenido exacto.

## Aprendizajes de la plataforma de labs (importante)
- **Cada lab trajo una suscripción distinta** (`XLabs-278`, `-274`, `-232`). Desde otra suscripción `az group exists` devuelve `false` **aunque el grupo siga vivo** en la anterior. Por eso hay que **verificar el cleanup antes de abrir la sesión siguiente**; los de los labs 9 y 10 quedaron como «borrado lanzado, no verificado».
- Los `azdeploy.py` de la plataforma solo llaman a `az` (sin `kubectl`): el proxy no molesta. Lo que sí puede fallar por TLS interceptado es `pip`/SDK: `REQUESTS_CA_BUNDLE`.
- Los menús difieren entre labs (la opción de roles es la 2 en el lab 9 y la 3 en los labs 10 y 11).
- La guía asume Windows/PowerShell; en Linux: `python3`, `source .env` y `source .venv/bin/activate`.

## Preguntas de repaso
_(se completan con el knowledge check del día: `docs/LP4 - Knowledge check.pdf`)_
1. ¿Qué operación de lectura es la más barata y qué necesita? 2. ¿Por qué una query por `category` es cross-partition aunque los datos estén en un solo documento? 3. ¿Qué parte de la política vectorial no se puede cambiar tras crear el contenedor? 4. ¿Por qué `diskANN` cuesta más al escribir? 5. ¿Cuándo conviene `flat` frente a `diskANN`? 6. ¿Por qué hacen falta dos roles distintos para trabajar con Cosmos desde código?
