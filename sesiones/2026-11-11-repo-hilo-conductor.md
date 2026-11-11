# Sesión 6b — 11/11/2026 · Repo seguible: labs con hilo conductor (sin clase)

## Cómo seguir esta sesión (hilo conductor)
**Idea del día:** no hubo clase. Se rehízo el repo para que cada clase se pueda repetir: la sesión marca el orden y el porqué, y cada lab es un único README paso a paso.

1. **Punto de entrada del curso:** tabla «Cómo seguir el curso» del [README raíz](../README.md#cómo-seguir-el-curso): día → sesión → teoría → labs.
2. **Formato de un lab:** el modelo es el [lab 13](../labs/lp5-02-pg-vector-search/README.md). En cada paso: por qué, comando, salida real, qué mirar y comprobación.
3. **Por qué se cambió:** [aprendizaje del día](../docs/aprendizajes.md) (2026-11-11).

---

## Qué se hizo
- **Conversación de la sesión 6:** exportada de Claude Code, saneada (correo, GUID, usuario y TAP del lab, cuenta de empresa y nombres) y dividida por lab en [`conversaciones/2026-11-10-sesion-06/`](conversaciones/2026-11-10-sesion-06/README.md). Enlazada desde los README de los labs 12 y 13. PR #15 y #16.
- **Queja del alumno:** «es imposible seguir la sesión, separas salidas de comandos»; «sin un hilo conductor y un porqué no sirve para nada ningún lab».
- **13 labs reescritos** (LP1-LP5) como un único README seguible. Los 11 `salidas.md` se integraron y se borraron. Donde no se guardó salida se indica «salida no guardada» con lo esperado.
- **Las 6 sesiones** empiezan con «Cómo seguir esta clase». [`labs/README.md`](../labs/README.md) lista ya los 13 labs.
- **Errores corregidos:**
  - En LP4-02 y LP4-03 el menú de `azdeploy.py` tiene 6 opciones y el `.env` es la 5. Explica el «`.env` no existe» del lab 11.
  - Los README de LP1 decían que el zip no se versionaba.
- **Regla nueva** en `CLAUDE.md`, `oscar.md`, `/aprender` y `/quiz-lab`, y en memoria.

## Decisiones
- **El repo es responsabilidad de Claude** (acuerdo del alumno): push, PR, merge y verificación en `origin/main`. Los recursos de Azure siguen siendo del alumno. Está guardado en memoria. Falta reflejarlo en la línea 26 de `CLAUDE.md`: el control de permisos de Claude Code bloquea que Claude edite sus propias instrucciones, así que lo cambia el alumno o lo autoriza expresamente.
- Con el token del repo, `gh pr edit` falla porque pide `read:org`: para editar o fusionar PRs se usa `gh api` (REST).

## Limpieza
No se crearon recursos de Azure hoy: no hay nada que borrar.

## Pendientes
- Línea 26 de `CLAUDE.md` («El merge lo hace el usuario»): actualizarla con el acuerdo nuevo.
- Opcional: exportar y sanear las conversaciones del 03/11 (AKS) y del 05/11 (Cosmos DB) y enlazarlas desde sus labs, como la del día 6.
- Pendientes de la sesión 6: lab 14 (LP5-03), tests de LP4 y LP5.
