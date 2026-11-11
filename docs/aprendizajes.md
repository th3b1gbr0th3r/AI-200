# Diario de aprendizajes

Un aprendizaje por día, recogido con la skill `/aprender`. Más reciente arriba.

## 2026-11-11 · Documentar un lab: si no se puede repetir leyendo un solo fichero, no sirve
- **Aprendizaje:** un lab documentado tiene que poder repetirse de principio a fin leyendo **un único fichero**. Cada paso lleva, en este orden: **por qué** se hace → **comando** → **salida real** → **qué mirar** en ella → **✅ comprobación** (comando, resultado esperado y qué hacer si no coincide). Las incidencias se cuentan en el paso donde ocurrieron. Guardar las salidas en un fichero aparte (`salidas.md`), sin su comando ni su porqué, deja un resumen que nadie puede seguir. Se rehicieron así los 13 labs; modelo: [`labs/lp5-02-pg-vector-search/README.md`](../labs/lp5-02-pg-vector-search/README.md). La sesión del día es el hilo conductor: orden de la clase y enlaces a cada paso.
- **Analogía K8s:** es la diferencia entre un *runbook* y un volcado de `kubectl get events`. Los eventos dicen qué pasó; el runbook dice qué hacer, por qué y cómo saber que ha funcionado. Un lab bien documentado es un runbook.
- **Comando / código:** plantilla de un paso.
  ````markdown
  ## Paso N · <qué se consigue>
  **Por qué:** <el problema que resuelve, en 1-3 frases>.
  ```bash
  <comando>
  ```
  Salida real:
  ```text
  <lo que salió, saneado>
  ```
  **Qué mirar:** <el campo o la línea que importa>.
  ✅ **Comprobación:** `<comando>` → debe salir `<valor>`. Si no, <qué hacer>.
  ````
- **Error típico:** documentar «lo que hice» en lugar de «cómo se repite» → al volver al lab no se sabe qué comando produjo cada salida ni por qué se ejecutó → un fichero por lab, pasos en orden real, y nunca una salida sin su comando. Si una salida no se guardó, decirlo («salida no guardada») y poner lo esperado; nunca inventarla.
- **Repaso:** ¿qué le falta a un paso que solo tiene el comando y la salida real?
  - A) Nada: con el comando y la salida ya se puede repetir.
  - B) El porqué y la comprobación: sin ellos no sabes para qué sirve el paso ni si te ha salido bien. ✅
  - C) Una captura de pantalla del portal.
  - D) El tiempo que tardó.

## 2026-11-10 · PostgreSQL: el upsert con `ON CONFLICT` hace idempotente la memoria del agente (y necesita un `UNIQUE`)
- **Aprendizaje:** `INSERT … ON CONFLICT (cols) DO UPDATE SET … = EXCLUDED.…` inserta la fila si no existe y la **actualiza** si ya existe; es una sola sentencia atómica, idempotente. `EXCLUDED` es la fila que se intentaba insertar. Solo funciona si hay una restricción `UNIQUE` (o PK) **exactamente** sobre esas columnas. En el lab 12, `save_task_state` guardó la tarea `research_postgresql` como `in_progress` y luego como `completed`: el `checkpoint_id` fue **1 las dos veces** (actualizó, no duplicó), `created_at` se mantuvo y `updated_at` cambió (18:22:35 → 18:22:42 UTC). Con `RETURNING id, updated_at` se recibe el resultado sin otra consulta.
- **Más aprendizajes del día:**
  - *pgvector en dos planos:* `azure.extensions = vector` con `az` (plano de control, reinicia el servidor) y después `CREATE EXTENSION vector` en `psql` (plano de datos). Índice HNSW con `vector_cosine_ops`, que debe casar con el operador `<=>` de la consulta (si no, no se usa el índice). HNSW se crea con la tabla vacía; IVFFlat necesita datos.
  - *Entra sin contraseña:* `PGPASSWORD` es un token de Entra (`--resource-type oss-rdbms`, ~1 h). Pedir token y conexión por cada operación costó ≈ 2,4 s por llamada → en producción, `ConnectionPool` (pregunta 2 del test del módulo 1).
  - *Plataforma:* `The location is restricted` → la política del lab solo admite `centralus` y `Standard_D2ds_v4`/`GeneralPurpose`; leer siempre la guía **de la plataforma** antes de editar `azdeploy.py`.
  - *Red:* `psql` sale por el 5432 desde el PC de empresa; Netskope solo inspecciona el tráfico web (443), que es lo que rompe `kubectl` contra AKS.
- **Analogía K8s:** `ON CONFLICT … DO UPDATE` = `kubectl apply` (crea o actualiza según exista, se puede repetir sin efectos raros); el `UNIQUE` hace el papel del nombre + namespace que identifica el objeto; `ON DELETE CASCADE` = recolección por `ownerReferences`.
- **Comando / código:**
  ```sql
  -- la restricción que hace posible el upsert
  ALTER TABLE task_checkpoints
  ADD CONSTRAINT unique_conversation_task UNIQUE (conversation_id, task_name);

  -- upsert idempotente con resultado en la misma sentencia
  INSERT INTO task_checkpoints (conversation_id, task_name, status, checkpoint_data)
  VALUES (%s, %s, %s, %s)
  ON CONFLICT (conversation_id, task_name)
  DO UPDATE SET status = EXCLUDED.status,
                checkpoint_data = EXCLUDED.checkpoint_data,
                updated_at = CURRENT_TIMESTAMP
  RETURNING id, updated_at;
  ```
- **Error típico:**
  - `there is no unique or exclusion constraint matching the ON CONFLICT specification` → falta el `UNIQUE` sobre esas columnas (la guía lo crea **después** de escribir el código) → `ALTER TABLE … ADD CONSTRAINT … UNIQUE (…)`.
  - El upsert inserta duplicados en vez de actualizar → la columna del `UNIQUE` admite NULL (`conversation_id` sin `NOT NULL`) y en PostgreSQL NULL ≠ NULL → poner `NOT NULL`.
  - `unrecognized arguments: -n psql-…` en `az postgres flexible-server firewall-rule list` → en los subcomandos de reglas/parámetros el servidor es `--server-name`; `-n` es la regla.
- **Repaso:** Tu agente guarda el estado de una tarea con `INSERT … ON CONFLICT (conversation_id, task_name) DO UPDATE`. La segunda llamada falla con *no unique or exclusion constraint matching*. ¿Qué haces?
  - A. Cambiar `DO UPDATE` por `DO NOTHING`.
  - B. Crear `UNIQUE (conversation_id, task_name)` en la tabla. ✅
  - C. Crear un índice B-tree solo en `conversation_id`.
  - D. Envolver el `INSERT` en una transacción explícita.

## 2026-11-05 · Cosmos DB for NoSQL: el coste se mide en RU y lo decide la forma de la consulta y del índice
- **Aprendizaje:** en Cosmos DB todo se paga en **RU** y depende de cómo preguntas y de cómo indexas. Una lectura puntual (`id` + partition key) cuesta ≈ 1 RU; una query con partition key va a una partición; una query por otro campo (p. ej. `category`) es **cross-partition** (fan-out) aunque los datos estén en un solo documento. En vectores, `diskANN` es el más caro de **escribir** (≈ 55 RU/doc, ≈ 4,7× `flat` con ≈ 11,7) y a 500 vectores `flat` gana leyendo (10,13 RU frente a 21,60); DiskANN compensa a escala (≈ 95 % de recall). Filtrar por categoría antes del ranking bajó la lectura a 8,15 RU en los tres índices.
- **Más aprendizajes del día:**
  - *Dos planos de permisos:* `Contributor` (ARM) gestiona la cuenta, BD y contenedores; `Cosmos DB Built-in Data Contributor` (RBAC propio de Cosmos) lee y escribe documentos. Un rol de ARM, ni siquiera Owner, basta para leer datos con `DefaultAzureCredential`.
  - *Política vectorial:* la *vector embedding policy* (ruta, tipo, dimensiones, distancia) es **inmutable** tras crear el contenedor; el *vector index* sí se puede cambiar. `/embedding/*` se excluye del índice normal. Con `cosine`, la puntuación más alta es la más parecida. La calidad semántica la da el modelo de embeddings, no Cosmos.
  - *Plataforma de labs:* cada lab trajo **otra suscripción** (`XLabs-278`, `-274`, `-232`); desde otra suscripción `az group exists` devuelve `false` aunque el grupo siga vivo en la anterior. Hay que verificar el cleanup **antes** de abrir la sesión siguiente; los de los labs 9 y 10 quedaron como «borrado lanzado, no verificado».
- **Analogía K8s:** partition key = shard key (como dar namespace y nombre exactos a `kubectl get`); RU = requests/limits cobrados por operación; los dos roles = crear un `Deployment` frente a hacer `exec` en el pod; `DefaultAzureCredential` = el mismo código con tu `az login` en el PC y con Workload Identity en AKS.
- **Comando / código:**
  ```python
  # lectura puntual: la operación más barata (≈ 1 RU)
  item = container.read_item(item=chunk_id, partition_key=document_id)
  # búsqueda vectorial: TOP obligatorio; con cosine, mayor puntuación = más parecido
  container.query_items(
      query="SELECT TOP @n c.id, VectorDistance(c.embedding, @v) AS s FROM c ORDER BY VectorDistance(c.embedding, @v)",
      parameters=[{"name": "@n", "value": 5}, {"name": "@v", "value": vector}],
      enable_cross_partition_query=True)
  ```
  ```bash
  # comprobar la política vectorial de un contenedor (solo lectura)
  az cosmosdb sql container show -g <rg> -a <cuenta> -d <bd> -n <contenedor> \
    --query "{vec:resource.vectorEmbeddingPolicy, idx:resource.indexingPolicy.vectorIndexes}"
  ```
- **Error típico:**
  - `az group exists` da `false` para el lab anterior → la sesión nueva es **otra suscripción**, no que se haya borrado → verificar el cleanup antes de cambiar de sesión.
  - `bash: .env: No existe el archivo` → no se lanzó la opción de «Retrieve connection info» del menú → lanzarla y luego `source .env`.
  - `REQUESTS_CA_BUNDLE environment variable is specified with an invalid file path` → la ruta no existe (aquí un typo `.crtrt`) → repetir el `export` con `/etc/ssl/certs/ca-certificates.crt`.
- **Repaso:** ¿Qué operación de lectura de Cosmos DB es la más barata y qué necesita?
  A) Una query con `ORDER BY` · B) Una lectura puntual con `id` y partition key · C) Una query cross-partition · D) Un `SELECT *`.
  *Respuesta: B.*

## 2026-11-03 · AKS en un PC con proxy: `az aks command invoke`, apply vs imperativo y AcrPull
- **Aprendizaje:** el proxy de empresa re-firma el TLS y **bloquea el API server de AKS** (`x509` y luego `502 IncompleteCertChain`), así que `kubectl` local no llega al cluster. `az aks command invoke` ejecuta el `kubectl` **dentro de Azure** vía ARM, que el proxy sí deja pasar; no necesita kubeconfig. Regla de trabajo: ofrecer siempre el comando `az` antes que el local.
- **Más aprendizajes del día:**
  - *`apply` frente a comandos imperativos:* `kubectl apply` solo quita los campos que él mismo aplicó (`last-applied`); lo que se puso con `set env` o `patch` no lo toca (`unchanged`). Al volver a la plantilla original, Kubernetes reutiliza el ReplicaSet antiguo (mismo `pod-template-hash`). Durante un rolling update fallido el pod viejo sigue sirviendo.
  - *Subir y bajar son permisos distintos:* `az acr build` lo autoriza tu login (el push lo hace ACR en la nube); la descarga la hace el kubelet con el rol **AcrPull** (`--attach-acr`). En producción `--admin-enabled false`, CI con identidad federada y `AcrPush` mínimo.
  - *Diagnóstico de las tres averías:* pod `Running` + Service sin endpoints = selector ≠ etiquetas; `CrashLoopBackOff` = `logs` (por qué muere) y luego `describe` (`Exit Code`, `Back-off`); readiness = `RESTARTS 0`, `0/1`, evento `Unhealthy` (404) y `conditions.ready`.
  - *Cleanup:* las credenciales del lab caducan por tiempo; hay que borrar **al terminar el lab**, antes de documentar. Los labs 7 y 8 quedaron «no verificado» (entorno temporal del curso).
- **Analogía K8s:** `az aks command invoke` = ejecutar `kubectl` desde un Job dentro del cluster; AcrPull al kubelet = `imagePullSecret` sin secreto; ConfigMap/Secret/PVC son los mismos objetos de siempre, lo nuevo es `managed-csi` (Azure Disk) y el LoadBalancer de Azure.
- **Comando / código:**
  ```bash
  # kubectl dentro de Azure, con ficheros locales (sin kubeconfig ni port-forward)
  az aks command invoke -g <rg> -n <aks> \
    --command "kubectl apply -f deployment.yaml -n <ns>; kubectl rollout status deploy/<d> -n <ns>" \
    --file k8s/deployment.yaml
  # probar un Service ClusterIP desde dentro del pod
  az aks command invoke -g <rg> -n <aks> --command "kubectl exec deploy/<d> -n <ns> -- python -c \"import urllib.request;print(urllib.request.urlopen('http://<svc>/healthz').read().decode())\""
  ```
- **Error típico:**
  - `x509: certificate signed by unknown authority` al hacer `kubectl apply` → el proxy re-firma el TLS y `kubectl` solo confía en la CA del cluster → usar `az aks command invoke`.
  - `apply … unchanged` y la avería no se produce → la variable la puso `set env` y el `apply` no la quita → `kubectl set env <d> VAR-`.
  - Diagnóstico a los 8 s sin `CrashLoopBackOff` → el pod nuevo aún no ha fallado y `-l app=api` mezcla el viejo → esperar 60 s y mirar el pod más reciente.
- **Repaso:** un Service existe, su pod está `1/1 Running` y `kubectl get endpointslices` no muestra endpoints. ¿Qué compruebas primero?
  A. Los `logs` del pod · B. El `Selector` del Service frente a las etiquetas del pod · C. Los límites de CPU · D. El rol AcrPull del kubelet → **B**.

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
