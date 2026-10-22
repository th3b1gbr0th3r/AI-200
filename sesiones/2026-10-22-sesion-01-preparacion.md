# Sesión 1 — 22/10/2026 · Preparación y clase de introducción

## Qué se hizo
- Creado el repo `AI-200` y publicado en GitHub (se hará público para los compañeros). Credenciales locales fuera de git (`github.mb` en `.gitignore`); el push se hace con cabecera temporal, sin guardar el token.
- Creado el agente especializado en Azure + DevOps, orientado a un perfil SysOps/Kubernetes que aprende la parte de desarrollo. Renombrado a **`oscar`**.
- Estructura: `docs/00-plan`, `docs/modulos`, `labs`, `notas`, `sesiones`.
- Plan de estudio con datos del curso, calendario de 9 learning paths en 5 días y pesos del examen.
- Acta de la clase de introducción: `notas/2026-10-22-sesion-01-introduccion.md`.
- Índice de las 28 guías oficiales de labs: `docs/00-plan/labs-oficiales.md`.

## Decisiones
- El PDF de la presentación del instructor (copyright Microsoft) no se sube; `*.pdf` y `*.pptx` en `.gitignore`.
- No se publican datos personales de terceros (docente, compañeros) en el repo.
- Las credenciales del campus se compartieron por error en el chat; se restablecieron. Regla: no pegar credenciales en la conversación.
- Los labs son un SaaS con credenciales temporales. Si hay bloqueo, dos vías: guiar en la plataforma, o reproducir en local y probar juntos.
- Cada sesión se guarda en `sesiones/`.

## Estado
- Azure CLI **no instalado** todavía en la máquina (Linux Mint 22.3). Instalación: `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash`.
- Primera clase impartida solo como introducción; sin labs hechos.

## Dudas / pendientes
- La guía oficial tiene 28 ejercicios y el docente habló de 24 labs; preguntar cuáles se hacen (dynamic sessions, sidecar, memoria persistente en Cosmos DB y Durable Functions son los extra).
- Duración del acceso a la plataforma de labs y fecha de la próxima sesión.
- Estado de Python del alumno; posible repaso de SDKs de Azure antes de los módulos de datos.
- Instalar `az` y probar `az login` antes del primer lab.
