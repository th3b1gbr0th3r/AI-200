# Diario de aprendizajes

Un aprendizaje por día, recogido con la skill `/aprender`. Más reciente arriba.

## 2026-10-27 · Contenedores en Azure: ACR Tasks y App Service sin secretos
- **Aprendizaje:** una web app se autentica contra el ACR **sin contraseña** en tres pasos separados: identidad system-assigned en la app (quién soy) → rol `AcrPull` limitado a ese ACR (qué puedo hacer) → `acrUseManagedIdentityCreds=true` (usa esa identidad para el pull). El ACR puede crearse con `--admin-enabled false`.
- **Más aprendizajes del día:**
  - *Registry ≠ cómputo:* el registry solo almacena; ACR Tasks ejecuta builds y runs en agentes efímeros (mini CI gestionado). El pipeline (Azure DevOps / GitHub Actions) orquesta; ACR guarda; AKS ejecuta.
  - *Mismo código, otro digest:* dos builds del mismo código dan digests distintos (no son reproducibles). Por eso se despliega por digest y se bloquea el tag (`--write-enabled false`, que no impide borrar: falta `--delete-enabled false`).
  - *La CLI no siempre dice la verdad:* `appsettings set` oculta los valores y `appservice plan show` devuelve `provisioningState` nulo aunque el plan esté `Ready`. Contrastar con `list`.
- **Analogía K8s:** identidad + rol = ServiceAccount + RoleBinding (workload identity); el App Service plan es el node pool y la web app el Deployment; Kudu es `kubectl exec` + `logs` + `describe` en el navegador.
- **Comando / código:**
  ```bash
  az webapp identity assign -g $RESOURCE_GROUP -n $APP_NAME
  az role assignment create --assignee $PRINCIPAL_ID --scope $ACR_ID --role AcrPull
  az webapp config set -g $RESOURCE_GROUP -n $APP_NAME --acr-use-identity true --acr-identity '[system]'
  ```
- **Error típico:**
  - `az login -u -p` → `AADSTS50126` → lo entregado era un Temporary Access Pass, solo vale en el login interactivo (`az login --use-device-code`, en incógnito).
  - `SSLCertVerificationError` → proxy corporativo que re-firma TLS → `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt`.
  - El script del lab marca "Not created" → falso negativo de la consulta, no un fallo del despliegue.
- **Repaso:** una web app tiene identidad system-assigned y `AcrPull` sobre el ACR, pero sigue sin poder hacer pull. ¿Qué falta?
  A. Habilitar el usuario admin del ACR · B. Activar `acrUseManagedIdentityCreds` (`--acr-use-identity true`) · C. Subir el SKU del plan a Premium · D. Abrir el puerto 443 en el ACR → **B**.

## 2026-10-22 · Preparar el entorno de estudio
- **Aprendizaje:** el examen AI-200 pesa más en datos para IA (25-30 %); contenedores, integración de servicios y seguridad/monitorización pesan 20-25 % cada uno.
- **Analogía K8s:** AKS, Container Apps y secretos te sonarán a Deployments, KEDA/HPA y Secrets; lo nuevo son Cosmos DB, PostgreSQL con pgvector y Redis vectorial.
- **Comando / código:** `az login --use-device-code` y `az account show` para comprobar tenant y suscripción.
- **Error típico:** la ventana de login de `az` queda oculta detrás de otras y parece que el comando se cuelga → minimizar ventanas.
