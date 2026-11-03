# Lab LP3-02 · Configure apps on AKS

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-kubernetes-service/02-aks-configure-container.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal. Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). Notas de clase: [`docs/modulos/03-aks.md`](../../docs/modulos/03-aks.md). Salidas reales saneadas: [`salidas.md`](salidas.md) (se crea al ejecutar).

**Estado:** preparado, no ejecutado (03/11/2026).

## Objetivo
Configurar la API con ConfigMap (no sensible), Secret (credenciales) y PVC (disco Azure `managed-csi` para logs, solo demo).

## Antes de empezar
- Editar solo `rg` y `location` en `azdeploy.py` (grupo propio: `rg-ai200-aks-cfg`). Región recomendada por la guía: `eastus2`, `swedencentral` o `australiaeast` (si falla, probar otra).
- `AKS_VM_SIZE = "Standard_D2s_v7"`: si da error de SKU o cuota, cambiar a una v5/v6 o de región.
- Las guías avisan de que las ACR tasks no funcionan con créditos gratuitos; la suscripción temporal de la plataforma debe permitirlo (comprobar al lanzar el build).
- Los números del menú de `azdeploy.py` cambian entre labs: leer siempre el menú.

## Pasos
1. `az provider register` (sin CognitiveServices).
2. `python3 azdeploy.py`: **1** ACR (copiar el endpoint), **2** build, **3** AKS, **4** credenciales kubectl, **5** estado.
3. Rellenar `configmap.yaml`, `secrets.yaml`, `pvc.yaml`; sustituir `<YOUR_ACR_ENDPOINT>` en `deployment.yaml`.
4. `kubectl apply -f k8s/{configmap,secrets,pvc,deployment,service}.yaml` (en ese orden).
5. `kubectl get svc aks-config-api-service -w` hasta tener IP; `azdeploy.py` → **5** (escribe `API_ENDPOINT` en `client/.env`).
6. Cliente (igual que lab 1), opciones 1-6. Tras cambiar ConfigMap/Secret: `kubectl rollout restart deployment aks-config-api`.

## Comprobación final y cleanup
```bash
az group delete --name rg-ai200-aks-cfg --no-wait --yes
az group exists --name rg-ai200-aks-cfg      # repetir hasta que devuelva false
az group list -o table         # no debe quedar nada rg-ai200-*
```
