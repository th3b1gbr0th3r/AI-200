# Lab LP5-01 · Build an agent tool backend (plataforma: Lab 12 · AI-200-LP05M01)

Guía oficial: https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/01-build-agent-tool-backend.html
Ejecutar con `export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt` en cada terminal y `python3` (no existe `python`). Origen MIT: ver [`../NOTICE.md`](../NOTICE.md). **Salidas reales saneadas: [`salidas.md`](salidas.md)** (se crea al pegar las primeras).

**Estado:** completado el 10/11/2026 (servidor `Ready`, esquema creado, `test_workflow.py` correcto con el upsert verificado y las 4 consultas de la Task 7). **Cleanup: borrado lanzado (`Deleting`), no verificado** (la suscripción del lab dejó de estar accesible), ver abajo.

## Objetivo
Usar PostgreSQL como memoria de un agente de IA: tablas de conversaciones, mensajes y *checkpoints* de tareas, y tres funciones de `agent-backend/agent_tools.py` que el agente usaría como herramientas (`create_conversation`, `get_conversation_history`, `save_task_state`).

## Qué se construye (leído de `azdeploy.py`)
```
azdeploy.py (1) → resource group + PostgreSQL Flexible Server psql-agent-<sha1 8>
                  Standard_B1ms (Burstable), 32 GB, PostgreSQL 16, acceso público
                  → admin de Entra = tu usuario → desactiva la contraseña (solo Entra)
                  → regla de firewall "AllowAll" 0.0.0.0-255.255.255.255
azdeploy.py (2) → estado: Ready, acceso público, admin de Entra, regla de firewall
azdeploy.py (3) → .env / .env.ps1 con DB_HOST, DB_NAME=postgres, DB_USER (tu UPN), PGPASSWORD (token Entra, ~1 h)
psql            → CREATE DATABASE agent_memory + 3 tablas + 4 índices + UNIQUE(conversation_id, task_name)
agent-backend/  → completar 3 funciones y ejecutar test_workflow.py (psycopg + DefaultAzureCredential)
```

## Diferencias respecto a la guía
| Aspecto | Guía (VM Windows) | Aquí (Linux, `mol-bastion`) |
|---|---|---|
| Descarga | Edge + Explorador | `curl -fLO` + `unzip` en esta carpeta (hecho) |
| Script | `python azdeploy.py` | `python3 azdeploy.py` |
| Login | `az login` | `az login --use-device-code` |
| psql | instalar | ya instalado (`psql 16.15`) |

## Puntos de atención
- **`.env` no se sube:** `PGPASSWORD` es un token de acceso de Entra (excepción en `.gitignore`).
- **Puerto 5432 desde el PC de empresa:** psql y psycopg se conectan directos al servidor (no hay vía `az` para el plano de datos). Si el proxy/firewall lo bloquea, plan B: Azure Cloud Shell (trae `psql` y `az`).
- **Firewall `AllowAll`:** abre el servidor a todo Internet. Aceptable en un lab desechable con solo Entra; en el trabajo, regla con tu IP o red privada (VNet).
- **Orden de la guía:** `save_task_state` usa `ON CONFLICT (conversation_id, task_name)`, que necesita la restricción UNIQUE creada en la Task 6.

## Decisiones y valores
- **Valores obligatorios de la plataforma** (política de la suscripción del lab, no vienen en la guía pública): resource group `ai200rg`, región `centralus` y SKU `Standard_D2ds_v4` con tier `GeneralPurpose` (en vez de `Standard_B1ms` / `Burstable`). Más caro que Burstable, pero trae PgBouncer integrado.
- Primer intento con `rg-ai200-pg-agent` / `eastus` / `B1ms` (los valores habituales del repo): cancelado al ver la instrucción de la plataforma.

## Incidencias y aprendizajes
| Síntoma | Causa | Arreglo |
|---|---|---|
| `unrecognized arguments: -n psql-agent-…` en `firewall-rule list` | En los subcomandos de reglas el servidor es `--server-name`/`-s`; `-n` es la regla | `--server-name psql-agent-dc48980e` |
| `ERROR: The location is restricted from performing this operation.` con `eastus` (el RG sí se crea) | Política de la suscripción del lab: PostgreSQL solo en `centralus` | Borrar el RG vacío y relanzar con los valores de la plataforma |
| La guía de la plataforma exige otro RG, región y SKU | Política de la suscripción del lab (la guía pública no lo dice) | Leer siempre la guía de la plataforma antes de editar `azdeploy.py`; `sed` de `rg`, `location`, `--sku-name` y `--tier` |

## Cleanup
```bash
az group delete --name ai200rg --yes --no-wait
az group show -n ai200rg --query properties.provisioningState -o tsv   # Deleting
az group exists --name ai200rg                                         # esperado: false (tarda unos minutos)
```
- `rg-ai200-pg-agent` (primer intento fallido en `eastus`, vacío): borrado y **verificado** (`az group exists` = `false`).
- `ai200rg` (servidor `psql-agent-dc48980e`): borrado lanzado; última comprobación en la suscripción `XLabs-079`: `Deleting`. **No verificado a `false`:** al cerrar el lab, `az` devolvió `No subscription found` (la suscripción temporal ya no está accesible).
- `az104-rg-region1` aparece en la suscripción: es de otro curso, no se toca.
