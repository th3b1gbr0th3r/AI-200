# Plan de estudio

## Datos del curso
| | |
|---|---|
| Curso | AI-200T00-A: Desarrollo de soluciones en la nube de IA en Azure |
| Nivel / duración | Intermedio · 5 días |
| Rol | Desarrollador |
| Certificación relacionada | Microsoft Certified: Azure AI Cloud Developer Associate |
| Ficha oficial | https://learn.microsoft.com/es-es/training/courses/ai-200t00 |
| Campus del alumno | https://campus.pue.es/index.php?action=campus |
| Soporte / ayuda | https://help.sepe.pue.es/ |
| Sesiones | Zoom |

## Qué cubre
Alojar aplicaciones en contenedores, crear APIs sin servidor con Functions, integrar servicios por eventos y mensajes (Service Bus, Event Grid), trabajar con datos para IA (Cosmos DB NoSQL, PostgreSQL con pgvector, Azure Managed Redis para caché, streaming y búsqueda vectorial) y construir apps seguras, escalables y observables.

## Prerrequisitos oficiales
- Contenedorización de apps (nivel básico) y servicios de datos de Azure (nivel básico)
- Fundamentos de agentes y modelos de IA
- Al menos 2 años de Python
- Familiaridad con Azure CLI

Para un perfil SysOps/K8s: contenedores y CLI cubiertos; reforzar **Python** y los SDKs de Azure.

## Calendario previsto del temario (5 días, 9 learning paths)
Reparto teórico del temario oficial; el ritmo real está en la sección siguiente.
| Día | Learning paths | Afinidad con K8s |
|---|---|---|
| 1 | 01 Alojamiento de apps en contenedores · 02 Azure Container Apps | Alta |
| 2 | 03 Desplegar y monitorizar en AKS · 04 Cosmos DB for NoSQL para IA | Muy alta · Media |
| 3 | 05 Azure Database for PostgreSQL (pgvector) · 06 Azure Managed Redis | Media |
| 4 | 07 Integrar servicios backend (Functions, Service Bus, Event Grid) · 08 Secretos y configuración | Baja (desarrollo) · Alta |
| 5 | 09 Observar y diagnosticar apps | Alta |

## Calendario real de las clases
Las clases son **dos días por semana (martes y jueves)**, por Zoom, de 18:00 a 22:00 con un descanso de ~20 min. Cada clase se guarda en `sesiones/` y su contenido en `docs/modulos/` y `labs/`.

| Sesión | Fecha | Contenido | Estado |
|---|---|---|---|
| 1 | jue 22/10/2026 | Presentación del curso | Hecha — `sesiones/2026-10-22-*.md` |
| 2 | mar 27/10/2026 | LP1 Alojamiento en contenedores: ACR Tasks y App Service (labs 1 y 2) | Hecha — `sesiones/2026-10-27-*.md`, `labs/lp1-01-*`, `labs/lp1-02-*` |
| 3 | jue 29/10/2026 | Corrección del knowledge check del LP1; LP2 Azure Container Apps | Estimada |
| 4+ | mar 03/11 y siguientes | LP3 AKS y el resto de learning paths | Estimada |

- Las fechas de las sesiones 3 en adelante se deducen del patrón martes/jueves y de lo que adelantó el docente (Container Apps la siguiente clase, después AKS); **hay que confirmarlas**.
- El número total de clases y el reparto por learning path pueden diferir de la previsión de 5 días: en las dos primeras sesiones solo se ha cubierto la presentación y el LP1.
- Cada learning path se guardará con el mismo formato: nota de módulo en `docs/modulos/NN-*.md`, labs en `labs/lpN-NN-*/README.md` (objetivo, diagrama, comandos explicados, resultados, incidencias) y acta en `sesiones/`.

## Examen AI-200: Developing AI Cloud Solutions on Azure
| Área | Peso |
|---|---|
| Soluciones en contenedores | 20-25% |
| Soluciones de IA con servicios de datos | 25-30% |
| Conectar y consumir servicios de Azure | 20-25% |
| Seguridad, monitorización y troubleshooting | 20-25% |

Prioridad: las áreas de datos para IA y de conexión de servicios son donde más tiempo dedicar (las más de desarrollo).

## Material
El contenido está en Microsoft Learn y en el entorno de labs del curso. Las diapositivas del instructor (PDF) son material con copyright y no se publican en el repo; se guardan solo en local.

## Docente
Pendiente de decidir qué datos se publican.
