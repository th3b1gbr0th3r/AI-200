# Test LP1 · Knowledge check (4 preguntas)

Prueba corta del último día de LP1 («Implementación del hospedaje de aplicaciones de contenedor en Azure»), de 18:00 a 18:15 al inicio de la sesión siguiente. Resumen propio: el documento original (`LP1 - Knowledge check.docx`) no se sube al repo.

Documentación oficial: [módulo 1 · ACR](https://learn.microsoft.com/es-es/training/modules/store-manage-containers-azure-container-registry/) · [módulo 2 · App Service](https://learn.microsoft.com/es-es/training/modules/deploy-containers-azure-app-service/). Notas del learning path: [`docs/modulos/01-alojamiento-contenedores.md`](../modulos/01-alojamiento-contenedores.md).

## Módulo 1 · ACR

### 1. Builds inconsistentes en estaciones de trabajo
> El equipo construye imágenes en los equipos de los desarrolladores y los resultados son inconsistentes. Hay que construirlas todas en un entorno controlado. ¿Qué característica de ACR lo resuelve?

| Opción | ¿Correcta? | Por qué |
|---|---|---|
| **A. ACR Tasks quick build** | ✅ | `az acr build` envía el contexto a ACR y el build corre en un agente efímero de la nube: mismo entorno para todos, sin Docker local |
| B. Geo-replicación | ❌ | Copia el registry a otras regiones (Premium); no construye nada |
| C. Namespaces de repositorio | ❌ | Organizan nombres y permisos; no controlan dónde se hace el build |

- **Lo practicamos en:** [lab 1](../../labs/lp1-01-acr-tasks/README.md), paso `az acr build --registry $ACR_NAME --image inference-api:v1.0.0 ./api`.
- **Clave:** el registry almacena; las Tasks son quienes ejecutan los builds.

### 2. Misma versión en todos los nodos aunque alguien reutilice el tag
> Desplegar a producción asegurando que cada nodo ejecuta exactamente la misma versión, aunque alguien suba otra imagen con el mismo tag. ¿Cómo se referencia?

| Opción | ¿Correcta? | Por qué |
|---|---|---|
| **A. Por digest del manifiesto** | ✅ | `imagen@sha256:…` es inmutable: identifica el contenido, no un nombre |
| B. Tag `latest` | ❌ | Mutable, es justo el problema |
| C. Tag semántico (`v1.2.0`) | ❌ | Sigue siendo un tag: alguien puede volver a publicar `v1.2.0` (por eso en el lab se bloqueó con `--write-enabled false`) |

- **Lo practicamos en:** lab 1, `az acr manifest list-metadata` (digests) y observación de que el digest cambia entre builds del mismo código.
- **Analogía K8s:** fijar `image: repo/api@sha256:…` en el `Deployment`.

## Módulo 2 · App Service

### 3. Contenedor en el puerto 8000 con errores de conexión
> Una imagen escucha en el 8000. Tras desplegarla en App Service las peticiones devuelven errores de conexión. ¿Qué lo resuelve?

| Opción | ¿Correcta? | Por qué |
|---|---|---|
| **A. App setting `WEBSITES_PORT=8000`** | ✅ | App Service solo asume 80/8080 si no se le dice otra cosa |
| B. `EXPOSE 80` en el Dockerfile | ❌ | `EXPOSE` es metadato; no configura el puerto de la plataforma, y el 80 no es donde escucha la app |
| C. Activar HTTP/2 | ❌ | Es protocolo, no puerto |

- **Lo practicamos en:** [lab 2](../../labs/lp1-02-app-service/README.md), `az webapp config appsettings set … --settings WEBSITES_PORT=80` (allí la app sí escucha en el 80).
- **Es el fallo más común** de contenedores personalizados en App Service.

### 4. URL de staging distinta de producción tras un swap
> Una app necesita URLs de API distintas en los slots de staging y producción. ¿Cómo se evita que la de staging pase a producción en el swap?

| Opción | ¿Correcta? | Por qué |
|---|---|---|
| **A. `API_ENDPOINT` como *slot setting*** | ✅ | Los slot settings se quedan en su slot al hacer swap |
| B. Meter la URL en la imagen de cada entorno | ❌ | Una imagen por entorno rompe «build once, deploy anywhere» y mezcla config con código |
| C. Usar connection strings en vez de app settings | ❌ | El tipo de ajuste no decide si viaja con el swap; lo decide marcarlo como *slot setting* |

- **No practicado:** el plan B1 del lab no admite slots; es concepto de teoría.
- **Analogía K8s:** ConfigMap/Secret por namespace en vez de hornear la config en la imagen.

## Resumen para repasar
| # | Respuesta | Idea |
|---|---|---|
| 1 | A | Builds en la nube con ACR Tasks |
| 2 | A | Digest > tag |
| 3 | A | `WEBSITES_PORT` |
| 4 | A | Slot setting |

## Corrección del profesor
_(pendiente: añadir cuando se incorporen las transcripciones de la clase)_
