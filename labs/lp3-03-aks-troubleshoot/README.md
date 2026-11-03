# Lab LP3-03 · Troubleshoot apps on AKS

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/03-aks-troubleshoot-container.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Salidas reales saneadas: [`salidas.md`](salidas.md) (se crea al ejecutar).

**Estado:** preparado, no ejecutado (03/11/2026).

## Objetivo
Diagnosticar y corregir tres fallos en el namespace `aks-troubleshoot`: selector del Service que no casa con las etiquetas, CrashLoopBackOff por falta de variable de entorno y readiness probe con ruta inválida.

## Antes de empezar
- Editar solo `rg` y `location` en `azdeploy.py` (grupo propio: `rg-ai200-aks-ts`). Región recomendada por la guía: `eastus2`, `swedencentral` o `australiaeast` (si falla, probar otra).
- `AKS_VM_SIZE = "Standard_D2s_v7"`: si da error de SKU o cuota, cambiar a una v5/v6 o de región.
- Las guías avisan de que las ACR tasks no funcionan con créditos gratuitos; la suscripción temporal de la plataforma debe permitirlo (comprobar al lanzar el build).
- Los números del menú de `azdeploy.py` cambian entre labs: leer siempre el menú.

## Pasos
1. `az provider register` (sin CognitiveServices).
2. `python3 azdeploy.py`: **1** ACR, **2** build, **3** AKS, **4** credenciales, **5** deploy, **6** estado.
3. Base: `kubectl get pods -n aks-troubleshoot`, `get endpointslices`, `port-forward service/api-service 8080:80` y `curl localhost:8080/healthz`.
4. Escenario 1 (`label-mismatch-service.yaml`): `get pods --show-labels`, `get endpointslices` vacío → `kubectl edit service`: `app: api-v2` → `app: api`.
5. Escenario 2 (`crashloop-deployment.yaml`): `logs -l app=api` → `kubectl edit deployment`: añadir env `API_KEY`.
6. Escenario 3 (`probe-failure-deployment.yaml`): `get events --field-selector reason=Unhealthy` → `kubectl edit deployment`: `/invalid-path` → `/healthz`.
7. End-to-end: port-forward + `curl /healthz /readyz /api/info`. Reiniciar escenarios con la opción **5**.

## Comprobación final y cleanup
```bash
az group delete --name rg-ai200-aks-ts --no-wait --yes
az group exists --name rg-ai200-aks-ts      # repetir hasta que devuelva false
az group list -o table         # no debe quedar nada rg-ai200-*
```
