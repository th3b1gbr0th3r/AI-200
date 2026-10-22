# AI-200: Developing

Documentación, notas y laboratorios del curso **AI-200: Developing** (Microsoft Azure).

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

## Usar el repo con Claude Code
El repo está preparado para trabajar con [Claude Code](https://claude.com/claude-code). Al abrirlo (`claude` en la raíz) carga automáticamente `CLAUDE.md` y el agente y la skill de abajo.

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

### Flujo de trabajo
Una rama y una PR por día de curso, con la plantilla de `.github/pull_request_template.md`. Sin push directo a `main`.

### Si clonas el repo
- Los ficheros `.claude/` funcionan solos; no necesitas configurar nada.
- Las credenciales (`github.mb`, `.env`, etc.) están en `.gitignore`: **nunca** las subas.
- El material con copyright de Microsoft (PDF/PPTX del instructor) tampoco se sube; consúltalo en el campus o en Microsoft Learn.
- Para usar tu propia sesión, haz un fork o clona y crea tus ramas; puedes adaptar `CLAUDE.md` a tu perfil.
