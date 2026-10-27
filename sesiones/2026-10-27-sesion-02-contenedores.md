# Sesión 2 — 27/10/2026 · LP1 Alojamiento en contenedores (ACR)

## Qué se hizo
- Añadido el material del día: presentación del LP1, knowledge check y enlace de recursos (los PDF/zip no se suben; `*.pdf` está en `.gitignore`).
- Nota del módulo con respuestas del knowledge check: `docs/modulos/01-alojamiento-contenedores.md`.
- Instalado **Azure CLI 2.91.0** en Linux Mint 22.3 (el script oficial deja el repo y no instala el paquete; hubo que hacer `apt-get install azure-cli`).
- Login en la suscripción temporal del lab y **lab 1 completo** (ACR Tasks): `labs/lp1-01-acr-tasks/README.md` con comandos, salidas y explicación.
- Guía para compañeros (instalar `az`, login con TAP, error de certificado): `notas/2026-10-27-guia-az-login-lab.md`.
- Consultada la guía del lab 2 (App Service) para planificar el siguiente paso.

## Decisiones
- Los labs se reproducen en local (Linux) en paralelo a la plataforma (servidor virtual Windows con PowerShell); mismo usuario → mismo nombre de ACR y misma suscripción, así que hay que evitar pisar recursos.
- El usuario ejecuta los comandos y se explican las salidas.
- Región `eastus` por exigencia del lab; rg `rg-ai200-acr`.
- Las credenciales temporales del lab se pasaron por el chat con autorización expresa del usuario (caducan en 120 min); no se escriben en el repo.

## Aprendizajes
- **Registry ≠ cómputo:** el registry almacena; ACR Tasks ejecuta builds/runs en agentes efímeros (mini CI gestionado).
- **El digest cambia entre builds del mismo código:** los builds no son reproducibles; fijar por digest.
- **Un TAP no es una contraseña:** solo funciona en login interactivo.
- **Proxy corporativo:** `REQUESTS_CA_BUNDLE` apuntando al almacén del sistema.
- **Bloqueo de imagen:** `writeEnabled=false` no impide borrar (`deleteEnabled`).
- Analogía CI/CD: Azure DevOps o GitHub Actions orquestan; ACR guarda; AKS ejecuta.

## Correcciones durante la sesión
- Predije que el segundo build sería mucho más rápido: no, el agente es efímero y no hay caché; solo se acelera el push.
- Dije que `lastUpdateTime` podía cambiar al bloquear: no cambia (refleja el contenido, no los atributos).
- El conteo de caracteres del mensaje para el chat estaba mal estimado; se midió con `wc -m`.

## Estado
- Lab 1 hecho y **recursos eliminados** (`rg-ai200-acr` borrado; la suscripción queda sin resource groups).
- Pendiente: lab 2 (App Service con contenedor), lab 3 (sidecar, por confirmar con el docente), preguntas de discusión en grupo.

## Pendientes
- Lab 2: su `azdeploy.py` crea su propio ACR; si el nombre se deriva del mismo ID de usuario saldrá `acrdfbe0335` otra vez (no verificado). El grupo del lab 1 ya está borrado, así que no habrá conflicto.
- Reproducir el lab 2 con App Service plan, identidad gestionada (`AcrPull`) y `WEBSITES_PORT`.
- Experimento opcional del bloqueo (reconstruir `v1.0.0` y ver el fallo del push): descartado al borrar el registry.
- Cierre del día: rama `dia-02-2026-10-27`, commit, PR y entrada en `docs/aprendizajes.md` con la skill `aprender`.
