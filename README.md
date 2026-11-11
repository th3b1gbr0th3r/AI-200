# AI-200: Developing

Documentación, notas y laboratorios del curso **AI-200: Developing** (Microsoft Azure).

> **Repositorio de formación.** Es material de estudio de un curso, no un proyecto de producción. Los labs se ejecutan en una plataforma de laboratorios con **cuentas y suscripciones temporales que se destruyen al terminar**; por eso los `.env`, los nombres de recursos y los endpoints que aparecen en `labs/` pertenecen a entornos desechables que ya no existen (no contienen claves; los que las tenían no se publican). Nada de lo que hay aquí debe reutilizarse tal cual en producción.

## Cómo seguir el curso
Cada clase se sigue en este orden: **sesión** (hilo conductor del día: qué se ve, por qué y en qué orden) → **nota del módulo** (la teoría) → **README de cada lab** (los pasos, cada uno con su porqué, el comando, la salida real y la comprobación).

| Día | Fecha | Tema | Sesión (empieza aquí) | Teoría | Labs (n.º de la plataforma) |
|---|---|---|---|---|---|
| 1 | 22/10/2026 | Introducción y preparación | [sesión 1](sesiones/2026-10-22-sesion-01-preparacion.md) | [plan](docs/00-plan/README.md) | — |
| 2 | 27/10/2026 | LP1 · Contenedores: ACR y App Service | [sesión 2](sesiones/2026-10-27-sesion-02-contenedores.md) | [LP1](docs/modulos/01-alojamiento-contenedores.md) | [1 · ACR Tasks](labs/lp1-01-acr-tasks/README.md) · [2 · App Service](labs/lp1-02-app-service/README.md) |
| 3 | 29/10/2026 | LP2 · Azure Container Apps | [sesión 3](sesiones/2026-10-29-sesion-03-container-apps.md) | [LP2](docs/modulos/02-container-apps.md) | [3 · Deploy](labs/lp2-01-aca-deploy/README.md) · [4 · Manage](labs/lp2-02-aca-manage/README.md) · [5 · Scale](labs/lp2-03-aca-scale/README.md) |
| 4 | 03/11/2026 | LP3 · AKS | [sesión 4](sesiones/2026-11-03-sesion-04-aks.md) | [LP3](docs/modulos/03-aks.md) | [6 · Deploy](labs/lp3-01-aks-deploy/README.md) · [7 · Configure](labs/lp3-02-aks-configure/README.md) · [8 · Troubleshoot](labs/lp3-03-aks-troubleshoot/README.md) |
| 5 | 05/11/2026 | LP4 · Cosmos DB for NoSQL | [sesión 5](sesiones/2026-11-05-sesion-05-cosmosdb.md) | [LP4](docs/modulos/04-cosmosdb.md) | [9 · RAG store](labs/lp4-01-cosmos-queries/README.md) · [10 · Vector search](labs/lp4-02-cosmos-vector-search/README.md) · [11 · Optimize](labs/lp4-03-cosmos-optimize/README.md) |
| 6 | 10/11/2026 | LP5 · Azure Database for PostgreSQL | [sesión 6](sesiones/2026-11-10-sesion-06-postgresql.md) | [LP5](docs/modulos/05-postgresql.md) | [12 · Agent backend](labs/lp5-01-pg-agent-backend/README.md) · [13 · Vector search](labs/lp5-02-pg-vector-search/README.md) |

Aprendizaje de cada día: [`docs/aprendizajes.md`](docs/aprendizajes.md). Guías oficiales de todos los labs: [`docs/00-plan/labs-oficiales.md`](docs/00-plan/labs-oficiales.md).

## Estructura
| Ruta | Contenido |
|---|---|
| `docs/00-plan/` | Plan de estudio y temario |
| `docs/modulos/` | Notas por módulo |
| `labs/` | Prácticas con Bicep/CLI |
| `notas/` | Apuntes sueltos |
| `.claude/agents/` | Agente `oscar` de apoyo Azure + DevOps |
| `sesiones/` | Registro de cada sesión de trabajo |
| `docs/aprendizajes.md` | Un aprendizaje por día (skill `/aprender`) |
| `docs/tests/` | Knowledge checks y resultados de quizzes (skill `/quiz-lab`) |

## Usar el repo con Claude Code
El repo está preparado para trabajar con [Claude Code](https://claude.com/claude-code). Al abrirlo (`claude` en la raíz) carga automáticamente `CLAUDE.md` y el agente y las skills de abajo.

### Agente `oscar`
Especialista en Azure con enfoque DevOps, pensado para un perfil SysOps/Kubernetes que aprende la parte de desarrollo. Definido en `.claude/agents/oscar.md`.
- Explica los conceptos comparándolos con Kubernetes y verifica en Microsoft Learn antes de afirmar.
- Ayuda con los labs de dos formas: guiando en la plataforma con la [guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/) (índice en `docs/00-plan/labs-oficiales.md`) o reproduciéndolos en local.
- Pide confirmación antes de crear o borrar recursos en Azure.

### Skill `/aprender` — cierre de día
Definida en `.claude/skills/aprender/SKILL.md`. Se ejecuta escribiendo `/aprender` en Claude Code al terminar la jornada:
1. Resume lo visto ese día y propone 2-3 aprendizajes; tú eliges cuál guardar.
2. Lo añade a `docs/aprendizajes.md` (concepto, analogía K8s, comando, error típico y pregunta de repaso).
3. Actualiza la nota de la sesión en `sesiones/`.
4. Comprueba que no hay secretos ni datos personales (el repo es público).
5. Crea la rama `dia-NN-AAAA-MM-DD` y abre una PR contra `main`. El merge lo haces tú.

### Skill `/quiz-lab` — repaso de labs con menú
Definida en `.claude/skills/quiz-lab/SKILL.md`. Se ejecuta escribiendo `/quiz-lab` en Claude Code:
1. Muestra un menú con **todos los labs documentados** en `labs/` (se descubren solos al añadir uno nuevo): primero el learning path (LP1, LP2, LP3 o mezcla) y luego el lab.
2. Eliges el nivel: repaso (5 preguntas), examen (10) o solo errores y troubleshooting.
3. Hace las preguntas **una a una** en formato test, sacadas solo de lo documentado (README de cada lab, notas del módulo y knowledge checks).
4. Evalúa cada respuesta al momento: correcta o no, por qué, qué falla en el distractor elegido y en qué paso del lab se practicó.
5. Termina con la nota, los puntos débiles y qué repasar; ofrece guardar el resultado en `docs/tests/` o llevar un fallo a `/aprender`.
Es de solo lectura: no ejecuta `az` ni crea recursos.

### Flujo de trabajo
Una rama y una PR por día de curso, con la plantilla de `.github/pull_request_template.md`. Sin push directo a `main`.

### Si clonas el repo
- Los ficheros `.claude/` funcionan solos; no necesitas configurar nada.
- Las credenciales (`github.mb`, `.env`, etc.) están en `.gitignore`: **nunca** las subas.
- El material con copyright de Microsoft (PDF/PPTX del instructor) tampoco se sube; consúltalo en el campus o en Microsoft Learn.
- Para usar tu propia sesión, haz un fork o clona y crea tus ramas; puedes adaptar `CLAUDE.md` a tu perfil.
