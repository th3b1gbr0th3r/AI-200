# Sesión 2 — 27/10/2026 · LP1 Alojamiento en contenedores (ACR + App Service)

## Qué se hizo
- Añadido el material del día: presentación del LP1, knowledge check y enlace de recursos (los PDF/zip no se suben; `*.pdf` está en `.gitignore`).
- Nota del módulo con respuestas del knowledge check: `docs/modulos/01-alojamiento-contenedores.md`.
- Instalado **Azure CLI 2.91.0** en Linux Mint 22.3 (el script oficial deja el repo y no instala el paquete; hubo que hacer `apt-get install azure-cli`).
- Login en la suscripción temporal del lab y **lab 1 completo** (ACR Tasks): `labs/lp1-01-acr-tasks/README.md` con comandos, salidas y explicación.
- Guía para compañeros (instalar `az`, login con TAP, error de certificado): `notas/2026-10-27-guia-az-login-lab.md`.
- **Lab 2 (App Service con contenedor)** en una instancia nueva del lab (la anterior caducó tras ~120 min; región `canadacentral`, plan `B1`, como indicaba la guía de la plataforma): `labs/lp1-02-app-service/README.md`. Web app con identidad gestionada + `AcrPull`, almacenamiento persistente, Always On y logs; pruebas `POST /process` y `GET /documents` correctas.
- Verificado en Microsoft Learn el montaje de Azure Storage propio en App Service (ruta elegible, salvo `/` y `/home`).
- Merge de la PR nº 2 (lab 1) a `main` a petición del usuario.
- Incorporada la transcripción de la clase (Zoom): notas organizativas y técnicas en `docs/modulos/01-alojamiento-contenedores.md` (sin nombres de personas; la transcripción no se publica).

## Decisiones
- Los labs se reproducen en local (Linux) en paralelo a la plataforma (servidor virtual Windows con PowerShell); mismo usuario → mismo nombre de ACR y misma suscripción, así que hay que evitar pisar recursos.
- El usuario ejecuta los comandos y se explican las salidas. Incluye el cleanup: Claude borró el resource group del lab 1 por su cuenta y el usuario lo corrigió; queda en memoria que los comandos que crean/borran recursos los lanza el usuario.
- Región `eastus` por exigencia del lab; rg `rg-ai200-acr`.
- Las credenciales temporales del lab se pasaron por el chat con autorización expresa del usuario (caducan en 120 min); no se escriben en el repo.

## Aprendizajes
- **Registry ≠ cómputo:** el registry almacena; ACR Tasks ejecuta builds/runs en agentes efímeros (mini CI gestionado).
- **El digest cambia entre builds del mismo código:** los builds no son reproducibles; fijar por digest.
- **Un TAP no es una contraseña:** solo funciona en login interactivo.
- **Proxy corporativo:** `REQUESTS_CA_BUNDLE` apuntando al almacén del sistema.
- **Bloqueo de imagen:** `writeEnabled=false` no impide borrar (`deleteEnabled`).
- Analogía CI/CD: Azure DevOps o GitHub Actions orquestan; ACR guarda; AKS ejecuta.
- **Plan vs web app:** el plan es la capacidad (node pool), la app se coloca en él; se paga el plan. B1 no admite slots.
- **Identidad gestionada + RBAC:** identidad (quién soy) y rol (qué puedo hacer) son pasos separados; `AcrPull` limitado al ACR. Las app registrations (on-prem) llevan secreto o certificado; las SPA no tienen secreto (PKCE).
- **`/home` persistente tiene ruta fija**; para elegirla se monta Azure Storage (Files lectura/escritura, Blob solo lectura; no en `/` ni `/home`).
- **La CLI no siempre dice la verdad:** `appsettings set` oculta valores, `plan show` devuelve `provisioningState` nulo; contrastar con `list`.
- **Kudu = SCM = Advanced Tools**; el login de Kudu es plano de gestión (usuario), no la identidad de la app.

## Correcciones durante la sesión
- Predije que el segundo build sería mucho más rápido: no, el agente es efímero y no hay caché; solo se acelera el push.
- Dije que `lastUpdateTime` podía cambiar al bloquear: no cambia (refleja el contenido, no los atributos).
- El conteo de caracteres del mensaje para el chat estaba mal estimado; se midió con `wc -m`.

## Estado
- Lab 1 hecho y **recursos eliminados** (`rg-ai200-acr` borrado).
- Lab 2 hecho hasta el paso 12 verificado; pasos 13-14 sin confirmar (ver README del lab). **Recursos vivos:** `rg-ai200-appsvc` (ACR Basic + plan B1 + web app); cleanup a cargo del alumno.
- Pendiente: lab 3 (sidecar, por confirmar con el docente), preguntas de discusión en grupo.

## Pendientes
- Cleanup del lab 2: según el docente, la plataforma desprovisiona los recursos al finalizar el laboratorio; además, `az group delete --name rg-ai200-appsvc --no-wait --yes` lo ejecuta el alumno. Finalizar el lab en la plataforma.
- Confirmar qué se ve en Kudu (Environment, consola, `/home/LogFiles/`) y repetir la prueba de `log tail` con dos terminales.
- Experimento opcional: reiniciar la app y comprobar que el documento sobrevive en `/home`.
- Lab 3 (sidecar con modelo local), por confirmar con el docente; preguntas de discusión en grupo del LP1.
- Siguiente clase: corrección de las 4 preguntas del knowledge check del LP1 y LP2 Azure Container Apps (diapositivas aún no disponibles); AKS es el LP3.
- Los labs usan una suscripción compartida con cuotas por región: si el plan falla, cambiar de región.
