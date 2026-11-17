# Sesión 7 — 17/11/2026 · Plan de recuperación (LP5 pendiente + LP6 + LP7)

## Cómo seguir esta clase (hilo conductor)
**Idea del día:** no es una clase nueva, es un plan para ponerse al día. El alumno se perdió las clases posteriores a la sesión 6 (10/11) y hay que recuperar **LP6 Azure Managed Redis** y **LP7 Servicios backend**, más lo que quedó abierto de LP5. **Fecha objetivo: todo cerrado antes del jueves 19/11/2026 por la tarde.**

**Estado: PENDIENTE (todo).** Clases **preparadas** el 17/11: notas de teoría de LP6/LP7 y README de cada lab (pasos de la guía oficial, sin ejecutar; código copiado literal de la guía). Cosas a resolver antes de LP7: instalar Azure Functions Core Tools (`func`) y comprobar si hay GitHub Copilot en VS Code (lab 20). Marcar cada casilla cuando esté hecho y verificado.

Orden propuesto: A (LP5) → B (LP6) → C (LP7), de menor a mayor novedad. En cada lab: el cleanup va **antes** de documentar (las credenciales caducan) y se verifica con `az group exists` hasta `false`.

---

## Supuestos sobre las clases perdidas
- El calendario real es **martes y jueves** (así consta en [`docs/00-plan/README.md`](../docs/00-plan/README.md); las sesiones 1-6 fueron 22/10 jue, 27/10 mar, 29/10 jue, 3/11 mar, 5/11 jue y 10/11 mar). No lunes y miércoles.
- **Confirmado por el alumno (17/11):** la clase perdida es la del **jueves 12/11 (LP6 Redis)**. LP7 se imparte hoy (**martes 17/11**), clase que el alumno tampoco sigue en directo y repite el mié 18/11 o el jue 19/11 por la mañana (reserva: sáb 21/11).
- Numeración de labs de la plataforma (supuesta por continuidad, LP5 = 12-14): LP6 = labs 15-17 y LP7 = labs 18-20. Confirmarlo en la plataforma.
- Las presentaciones tienen un ejercicio por módulo: LP6 tres y LP7 tres (Service Bus, Event Grid, Functions MCP). El cuarto ejercicio del índice oficial (Durable Functions) no aparece en el PDF: se trata como **opcional**.

## Plan en casillas (tiempos estimados)

### A. Arrastrado de LP5 — ≈ 2 h 15 min
- [ ] **A1. Lab 13 · `[AI-200-LP05M02]` Implement vector search** — **aquí nos quedamos (punto de partida).** El entorno del 10/11 ya se destruyó, así que se repite entero siguiendo [su README](../labs/lp5-02-pg-vector-search/README.md) (pasos 1-9 ya documentados con salida real) y se completan la carga y la búsqueda (pasos 10-11, nunca ejecutados). ≈ 1 h. Cleanup + verificación.
- [ ] **A2. Lab 14 (LP5-03), optimize vector search** → [guía oficial](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-database-postgresql/03-optimize-vector-search.html). Preparado: [README](../labs/lp5-03-pg-optimize/README.md). ≈ 45 min. Cleanup + verificación.
- [ ] **A3. Tests LP4 y LP5** ([LP5 Knowledge check](../docs/LP5%20-%20Knowledge%20check.pdf)) y repaso de respuestas con `/quiz-lab`. ≈ 30 min.

### B. LP6 Azure Managed Redis — ≈ 3 h 30 min
Presentación: [`AI-200T00A-06`](../docs/AI-200T00A-06_Enhance%20AI%20solutions%20with%20Azure%20Managed%20Redis.pdf) (33 págs.; 3 módulos: operaciones de datos, mensajería de eventos, almacenamiento vectorial). Cada ejercicio indica 30 min en la presentación; se estima ~45 min reales con el cleanup.
- [ ] **B1. Teoría LP6** → [índice](../docs/modulos/06-redis.md) y notas [M1](../docs/modulos/06-1-redis-data-operations.md), [M2](../docs/modulos/06-2-redis-messaging.md), [M3](../docs/modulos/06-3-redis-vector-storage.md). ≈ 1 h. Apoyo del PDF: puerto TLS 10000 (no 6380 de Azure Cache for Redis), `SCAN` en vez de `KEYS`, `SETEX`, cache-aside, pipelining, niveles Memory/Balanced/Compute/Flash Optimized.
- [ ] **B2. Lab 15 · Perform data operations** · [README](../labs/lp6-01-redis-data-ops/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/01-amr-data-operations.html). ≈ 45 min. Cleanup + verificación.
- [ ] **B3. Lab 16 · Publish and subscribe to events** · [README](../labs/lp6-02-redis-pubsub/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/02-amr-pub-sub.html). ≈ 45 min. Cleanup + verificación.
- [ ] **B4. Lab 17 · Implement semantic search** · [README](../labs/lp6-03-redis-vector/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/azure-managed-redis/03-amr-vector-storage.html). ≈ 45 min. Cleanup + verificación.
- [ ] **B5. Knowledge check LP6** ([PDF](../docs/LP6%20-%20Knowledge%20check.pdf), 3 módulos) y repaso. ≈ 15 min.

### C. LP7 Servicios backend — ≈ 3 h 45 min (+ 45 min opcional)
Presentación: [`AI-200T00A-07`](../docs/AI-200T00A-07_Integrate%20Backend%20Services%20for%20AI%20Solutions.pdf) (39 págs.; 3 módulos: Service Bus, Event Grid, Azure Functions).
- [ ] **C1. Teoría LP7** → [índice](../docs/modulos/07-servicios-backend.md) y notas [M1](../docs/modulos/07-1-servicebus.md), [M2](../docs/modulos/07-2-eventgrid.md), [M3](../docs/modulos/07-3-functions.md). ≈ 1 h 15 min. Apoyo del PDF: colas frente a topics, peek-lock y liquidación (complete/abandon/dead-letter/defer), DLQ, patrón claim-check, `correlation_id` y `message_id`.
- [ ] **C2. Lab 18 · Process messages with Azure Service Bus** · [README](../labs/lp7-01-servicebus/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/01-svcbus-process-messages.html). ≈ 45 min. Cleanup + verificación.
- [ ] **C3. Lab 19 · Publish and receive events with Event Grid** · [README](../labs/lp7-02-eventgrid/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/02-eventgrid-publish-receive-events.html). ≈ 45 min. Cleanup + verificación.
- [ ] **C4. Lab 20 · Create an MCP server with Azure Functions** · [README](../labs/lp7-03-functions-mcp/README.md) → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/03-azure-functions-mcp-server.html). ≈ 45 min. Cleanup + verificación.
- [ ] **C5. Knowledge check LP7** ([PDF](../docs/LP7%20-%20Knowledge%20check.pdf), 3 módulos) y repaso. ≈ 15 min.
- [ ] **C6 (opcional). Durable document-processing workflow** → [guía](https://microsoftlearning.github.io/mslearn-azure-ai/instructions/integrate-services/04-durable-functions-ai.html). Solo si el docente lo incluye. ≈ 45 min.

### D. Cierre
- [ ] **D1. Inventario final:** `az group list -o table` sin grupos del curso (`ai200rg`, `rg-ai200-*`) y revisar fuera de RG (roles, soft-delete). Si caducan las credenciales, anotar «no verificado».
- [ ] **D2. Registro:** actualizar esta sesión con lo hecho, `docs/aprendizajes.md` y el estado de `docs/00-plan/README.md`.
- [ ] **D3. Preguntar al docente** qué se dio en las clases perdidas y confirmar la numeración de labs.

## Calendario propuesto
**Decisión del alumno (17/11):** la clase de hoy (mar 17/11, LP7) tampoco se sigue en directo; se repite **mañana mié 18/11 o el jue 19/11 por la mañana**. Si no fuera posible, **reserva: sáb 21/11 por la mañana** (ya después de la clase del jueves).

| Cuándo | Bloque | Horas |
|---|---|---|
| **Mié 18/11** | A (LP5) + B (LP6 completo). Si da tiempo, empezar C (LP7) | ≈ 5 h 15 min |
| **Jue 19/11** (mañana) | C (LP7, la sesión de hoy) y D (cierre) | ≈ 4 h (+ 45 min opcional) |
| **Jue 19/11** (tarde) | Clase normal | — |
| **Sáb 21/11** (mañana, reserva) | Lo que no haya cabido (prioridad: C → B4 → A2) | — |

**Total estimado: ≈ 9 h** (≈ 10 h con el Durable Functions opcional). Si hay que recortar: C6 es opcional; la teoría se puede leer en diagonal apoyándose en los knowledge check.

## Recordatorio de limpieza (regla del repo)
Al terminar **cada** lab, antes de documentar:
```bash
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
az group delete --name <rg> --no-wait --yes
az group exists --name <rg>    # repetir hasta que devuelva false
```
Esperado: `false`. Si devuelve `true`, esperar y repetir (el borrado puede tardar minutos; Redis y Service Bus no tienen soft-delete que purgar, pero Key Vault sí si aparece). Si `No subscription found` o `AuthorizationFailed`, las credenciales han caducado: anotarlo como «no verificado». El borrado lo lanza el alumno.

## Pendientes
Todo lo anterior. Prioridad: A → B → C antes del jueves 19/11 por la tarde; reserva sábado 21/11 por la mañana.
