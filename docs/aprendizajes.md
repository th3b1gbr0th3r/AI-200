# Diario de aprendizajes

Un aprendizaje por día, recogido con la skill `/aprender`. Más reciente arriba.

## 2026-10-29 · Container Apps: escalado por concurrencia, revisiones y limpieza
- **Aprendizaje:** el escalado de ACA (KEDA por debajo) con la regla `http-scaling` se decide por **peticiones concurrentes por réplica** (aquí 10), no por peticiones por segundo. Con 25 workers y `delayMs 500` las réplicas subieron 1 → 3 → 5 con 0 peticiones fallidas; sin `delayMs` las peticiones no se solapan y no escala.
- **Más aprendizajes del día:**
  - *Revisiones:* un cambio de plantilla (escala, imagen, variables) crea una revisión nueva (`0000002`); el diagnóstico de los fallos del lab 4 se hizo con `az containerapp logs show` y Log Analytics (KQL).
  - *Limpieza:* `az group delete --no-wait` devuelve el prompt sin esperar; el borrado se comprueba aparte con `az group list` (`Deleting` → vacío). Los grupos de los labs 2, 3 y 4 ya los había desprovisionado la plataforma.
- **Analogía K8s:** regla HTTP de ACA = KEDA `ScaledObject` con trigger HTTP (HPA con métrica personalizada); revisión = ReplicaSet de un rollout del Deployment.
- **Comando / código:**
  ```bash
  az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "properties.template.scale" -o json
  az containerapp replica list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --query "length(@)" -o tsv
  az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --type system --tail 50
  ```
- **Error típico:**
  - La app no escala bajo carga → las peticiones no se solapan → subir `delayMs` (500-1500 ms) y la concurrencia.
  - Se corta la sesión de `az` → caduca el login → reautenticar con el Temporary Access Pass (solo login interactivo) y repetir el `export REQUESTS_CA_BUNDLE=…` por el proxy.
- **Repaso:** una container app con regla HTTP de 10 peticiones concurrentes por réplica recibe 50 concurrentes sostenidas, con `maxReplicas 10`. ¿Cuántas réplicas esperas?
  A. 1 · B. 5 · C. 10 · D. 50 → **B**.

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
