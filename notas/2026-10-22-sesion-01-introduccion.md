# Sesión 1 — Introducción (22/10/2026)

## Organización del curso
- 15 sesiones de 4 h (60 h). Descontando la primera, la última y el examen: unas **10-11 sesiones operativas**.
- Ritmo: los primeros días ~1 learning path por día (con calma en los labs), luego 1,5 y al final hasta 2.
- Teoría ≈ 1-1,5 h por learning path; el resto, laboratorios. Alrededor de 30 diapositivas por learning path.
- Cada lección tiene su laboratorio: **9 learning paths, 24 lecciones, 24 labs**.
- Requisitos para aprobar el curso (SEPE): **asistencia ≥ 75 %** y **aprobar un test** que pone el docente. La plataforma de labs no controla si los terminas.
- Si un día no puedes hacer un lab, se puede recuperar en otra sesión.

## Examen interno
- 2 preguntas por lección (≈48 en total); el examen usará 15-20 de ellas.
- Se corrigen al día siguiente, antes del examen.
- Siempre habrá 4 opciones y **la D nunca es la correcta**.

## Estructura de cada learning path
Objetivos e introducción → teoría de cada lección → laboratorio guiado → preguntas al final (documento aparte).

## Lecciones por learning path
| LP | Tema | Lecciones |
|---|---|---|
| 1 | Alojamiento de contenedores | Azure Container Registry (ACR) · Contenedores en App Service (Web Apps) |
| 2 | Azure Container Apps | Desplegar · gestionar · escalar (autoescalado con peticiones HTTP concurrentes) |
| 3 | AKS | Desplegar · configurar/gestionar · monitorizar y troubleshooting (las dos primeras son cortas; se pueden unir) |
| 4 | Cosmos DB (NoSQL / no relacional) | Almacén de documentos · búsqueda semántica/vectorial · optimización de consultas |
| 5 | Azure Database for PostgreSQL | Construir y consultar · búsqueda vectorial (pgvector) · rendimiento |
| 6 | Azure Managed Redis | Operaciones de datos · eventos y streaming (pub/sub) · almacenamiento vectorial / búsqueda semántica |
| 7 | Servicios backend | Service Bus · Event Grid · Azure Functions (serverless, incl. MCP) |
| 8 | Secretos y configuración | Key Vault · App Configuration |
| 9 | Observabilidad | OpenTelemetry / instrumentación · logs y métricas con KQL |

Notas del docente:
- Azure SQL no se cubre aquí (está en las rutas de datos).
- Mucho contenido menciona IA, pero el foco es **desarrollar y operar los servicios en Azure**, no aprender a programar.
- Web Apps ya no tiene módulo propio: aparece en LP1, LP8 y LP9.
- Apps web de los labs: **Python + Flask**, probadas en local con VS Code.
- KQL también sirve en Microsoft Sentinel (hunting).

## Documentación
- Contenido completo en Microsoft Learn, accesible **sin registro** en modo anónimo. Cambiando el idioma de la URL se ve en inglés; para este curso la traducción al español aún no estaba disponible en algunas partes (el docente lo revisa).
- Carpeta compartida del curso (solo lectura): PDF de introducción, `links.txt`, y por learning path las preguntas de repaso y material extra. Los enlaces útiles del chat se añaden a `links.txt`.
- Enlace de **achievement code** para la insignia: se entrega al final del curso.
- Recomendación: añadir una segunda cuenta (personal) al perfil de Microsoft Learn por si cambia la cuenta corporativa.

## Plataforma de laboratorios
- Labs guiados con la guía a la izquierda y un PC virtual. Hay botones para copiar/pegar usuario y contraseña.
- Credenciales de Azure **temporales**, solo durante el lab (2 h de tiempo máximo). **No hace falta suscripción propia** mientras dure el acceso (6-12 meses; confirmar).
- Pasado ese plazo habrá que usar una suscripción propia.
- Se puede repetir un lab tantas veces como se quiera. Finalizar desde el menú **Acciones → Finalizar** (o Descartar si falló).

## Flujo típico de un lab
1. Descargar el zip del lab, extraerlo (p. ej. `C:\App`) y abrirlo en VS Code.
2. Editar el script de despliegue con el **nombre del resource group** y la **región**. Si no hay resource group, crearlo en el portal.
3. `az login` en el terminal integrado. Elegir **cuenta de trabajo o escuela**, no cuenta personal Microsoft. La ventana de login a veces queda oculta detrás: minimizar.
4. Registrar los resource providers necesarios (`az provider register`); a veces falla a la primera y vuelve a funcionar.
5. Ejecutar el script Python que genera las variables de entorno y cargarlas.
6. Aprovisionar con comandos `az` o scripts, y comprobar en el portal cómo se crean los recursos.
7. Al final, borrar los recursos.

## Consejos
- Si hay errores de despliegue, probar otra región. El docente observó mejor resultado en **West US** que en East US. También se han usado Spain Central y regiones de Europa.
- Labs que han dado problemas en ediciones anteriores: Event Grid, Functions con MCP. Suelen arreglarse con el tiempo.
- El docente completará algunas teorías con diapositivas de versiones anteriores del curso (AZ-204) como material extra.

## Pendiente
- Confirmar por qué proveedor se contrata la plataforma de labs y cuánto dura el acceso.
- Confirmar fecha de la próxima sesión y el primer módulo (LP1: ACR + App Service).
