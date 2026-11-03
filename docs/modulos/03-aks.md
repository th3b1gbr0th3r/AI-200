# LP3 · Desplegar y monitorizar apps en Azure Kubernetes Service (AKS)

Resumen propio de la presentación del instructor (`docs/AI-200T00A-03_…pdf`). Para un perfil K8s: aquí lo nuevo es la parte Azure (ACR, identidades, LoadBalancer de Azure, Foundry), no los objetos de K8s.

## Agenda (3 módulos, 1 lab cada uno)
| Módulo | Tema | Lab |
|---|---|---|
| 1 | Deployments, Services, Pods; `kubectl apply` y verificación | [LP3-01](../../labs/lp3-01-aks-deploy/README.md) |
| 2 | ConfigMap, Secret, PVC | [LP3-02](../../labs/lp3-02-aks-configure/README.md) |
| 3 | Monitorizar y diagnosticar (selector, probes, CrashLoop, eventos) | [LP3-03](../../labs/lp3-03-aks-troubleshoot/README.md) |

## Qué es nuevo para ti (lo que va a examen)
- **Pull de ACR sin secretos:** el cluster se crea con identidad gestionada y rol `AcrPull` sobre el ACR (`--attach-acr`).
- **Acceso a Foundry desde pods:** rol *Cognitive Services OpenAI User* para la identidad kubelet (lab 1). Más fino: Workload Identity.
- **Service `LoadBalancer`:** crea un Azure Load Balancer con IP pública; la anotación `azure-load-balancer-internal: "false"` la hace pública.
- **PVC `managed-csi`:** disco de Azure (`ReadWriteOnce`), un solo pod a la vez.
- **Cadena de conectividad a revisar:** selector ↔ etiquetas del pod → puerto → EndpointSlices.

## Diagnóstico rápido (orden)
`kubectl get pods` → `describe pod` / `get events` → `logs` → `get endpointslices` → `port-forward` + `curl`.
| Síntoma | Causa típica |
|---|---|
| Service sin endpoints | selector ≠ etiquetas del pod |
| CrashLoopBackOff | falta env/secret; ver `logs` |
| Running pero 0/1 READY | readiness probe falla (ruta/puerto) |
| ImagePullBackOff | imagen no está en ACR o falta `AcrPull` |
| Pending | requests superiores a lo que cabe en el nodo |

## Preguntas de repaso
_(se completan con el knowledge check del día)_
