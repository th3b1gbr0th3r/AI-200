# AI-200: Developing — repositorio de estudio

Repo de documentación y labs del curso AI-200 (Microsoft). El usuario es SysOps/especialista en Kubernetes; necesita apoyo en la parte de desarrollo.

- Idioma: español.
- Agente especializado: `.claude/agents/oscar.md` (se llama **oscar**; Azure + DevOps). Delega en él las dudas de Azure.
- `github.mb` contiene credenciales de GitHub: está en `.gitignore`, **nunca** subirlo, mostrarlo ni copiarlo a la URL del remote. Para push usar cabecera temporal (`git -c http.extraHeader=...`) sin guardar el token en `.git/config`.
- Estructura: `docs/00-plan` (plan y temario), `docs/modulos` (notas por módulo), `labs/` (prácticas con IaC), `notas/` (apuntes sueltos).
- **Todo comando que se da al alumno lleva su comprobación** (comando de verificación + resultado esperado + qué hacer si no coincide); regla vinculante para el agente oscar (ver `.claude/agents/oscar.md`).
- **Las salidas reales que pega el alumno se guardan saneadas en `labs/<lab>/salidas.md`** (un bloque por comando + «Qué mirar»), enlazadas desde el README del lab.
- Los labs crean recursos con coste: confirmar antes de desplegar. **Obligatorio: destruir todo lo creado en el curso al final de cada lab y al cierre del día** (regla vinculante para el agente oscar; ver `.claude/agents/oscar.md`).
- Los scripts de aprovisionamiento de Microsoft de cada lab (`azdeploy.py`, `api/`, `document.txt`, y el zip original) se versionan en `labs/<lab>/`: el repo de origen es MIT (ver `labs/NOTICE.md`). Los `.env` generados no se suben. Las presentaciones y los knowledge check del curso son públicos y se versionan en `docs/` solo en PDF, sin duplicar formatos y sin metadatos de autor; los zips de `docs/` y `docs/Links*.txt` no.

## Guías oficiales de labs
Índice en `docs/00-plan/labs-oficiales.md` (fuente: https://microsoftlearning.github.io/mslearn-azure-ai/). Al ayudar con un lab, abrir la guía oficial correspondiente con WebFetch para seguir los mismos pasos que el alumno.

## Registro de sesiones
Cada sesión de clase/trabajo se guarda en `sesiones/AAAA-MM-DD-<tema>.md` (decisiones, qué se hizo, dudas, pendientes). Al final de cada sesión: crear/actualizar el fichero y abrir la PR del día. Sin datos personales de terceros ni credenciales (repo público).

## Labs: dos vías
Los labs son un SaaS con credenciales temporales; si el alumno se atasca se puede guiar en la plataforma o reproducir el lab en local (ver `.claude/agents/oscar.md`).

## Flujo de PRs
Una rama y una PR por día de curso (`dia-NN-AAAA-MM-DD` → `main`), con la plantilla de `.github/`. Nunca hacer push directo a `main` desde el día 2. El merge lo hace el usuario. Skill: `/aprender`.
