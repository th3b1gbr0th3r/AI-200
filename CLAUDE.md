# AI-200: Developing — repositorio de estudio

Repo de documentación y labs del curso AI-200 (Microsoft). El usuario es SysOps/especialista en Kubernetes; necesita apoyo en la parte de desarrollo.

- Idioma: español.
- Agente especializado: `.claude/agents/azure-devops.md` (Azure + DevOps). Delega en él las dudas de Azure.
- `github.mb` contiene credenciales de GitHub: está en `.gitignore`, **nunca** subirlo, mostrarlo ni copiarlo a la URL del remote. Para push usar cabecera temporal (`git -c http.extraHeader=...`) sin guardar el token en `.git/config`.
- Estructura: `docs/00-plan` (plan y temario), `docs/modulos` (notas por módulo), `labs/` (prácticas con IaC), `notas/` (apuntes sueltos).
- Los labs crean recursos con coste: confirmar antes de desplegar y limpiar al terminar.
