---
name: quiz-lab
description: Repaso interactivo de los labs del curso AI-200. Muestra un menú con todos los labs documentados en el repo, el alumno elige uno y recibe preguntas tipo test (una a una) sobre lo que se hizo, con evaluación inmediata de cada respuesta y resumen final. Úsalo cuando el usuario diga "quiz", "quiz-lab", "repasar un lab", "hacer lab con menú" o "examen de labs".
---

# Quiz de labs — repaso con menú y evaluación

Objetivo: que el alumno compruebe que **entiende** cada lab (no solo que lo ejecutó), con preguntas tipo examen y corrección inmediata. Idioma: español.

## 1. Menú de labs (dinámico)
1. Descubre los labs documentados: `ls labs/*/README.md`. Un lab cuenta si tiene README. Marca con «con salidas» los que tienen `salidas.md` y con «sin ejecutar» los que su README diga *preparado, no ejecutado* (el quiz de estos usa solo la guía y el README).
2. Muestra el menú con `AskUserQuestion` (máx. 4 opciones por pregunta, así que en dos pasos):
   - **Paso 1 · Learning path:** deduce los LP de los prefijos de `labs/` (`lpN-…`) y de los ficheros `docs/LPN - Knowledge check.pdf` / `docs/AI-200T00A-0N_*.pdf`. Hoy: LP1 (ACR + App Service), LP2 (Container Apps), LP3 (AKS), LP4 (Cosmos DB for NoSQL). Máx. 4 opciones: muestra los **3 LP más recientes** y una cuarta «Otros LP / Mezcla de todos», que abre una segunda pregunta con el resto de LP y «Mezcla de todos».
   - **Paso 2 · Lab:** los labs de ese LP (más «Todos los de este LP»). Etiqueta = código + título corto (p. ej. `LP2-03 · Scale en ACA`); descripción = estado y si tiene salidas. Si el LP **no tiene labs en `labs/`** (p. ej. un LP nuevo antes de hacer sus labs; LP4 ya tiene `lp4-01-cosmos-queries`, `lp4-02-cosmos-vector-search` y `lp4-03-cosmos-optimize`), ofrece «Teoría + knowledge check del LP» y avisa de que el quiz sale solo del PDF del módulo y del knowledge check.
   Si se añaden labs o LP nuevos, aparecen solos: no hay lista fija.
3. Pregunta también el **nivel** con `AskUserQuestion`: *Repaso (5 preguntas)* · *Examen (10 preguntas)* · *Solo errores y troubleshooting*.

## 2. Preparar las preguntas
Lee, del lab elegido: `README.md`, `salidas.md` (si existe), la nota del módulo (`docs/modulos/NN-*.md`) y, si la hay, el knowledge check (`docs/tests/`). Si el LP no tiene nota de módulo, usa el PDF del módulo (`docs/AI-200T00A-0N_*.pdf`) y `docs/LPN - Knowledge check.pdf`: léelos con `pdftotext "<pdf>" -` (solo lectura; si necesitas un temporal, usa `tmp/` en la raíz del repo, nunca fuera). Los PDF son material del curso: no copies preguntas literales del knowledge check; reformúlalas como escenario. **Las preguntas salen solo de lo documentado**: nada inventado. Mezcla estos tipos:
| Tipo | Ejemplo de enfoque |
|---|---|
| Concepto | por qué identidad gestionada y no credenciales de ACR |
| Comando | qué comando comprueba X / qué hace cada flag |
| Lectura de salida | dada una salida de `salidas.md`, qué indica |
| Troubleshooting | síntoma → causa → arreglo (incidencias reales del lab) |
| Analogía K8s | qué objeto de Kubernetes equivale |
| Cleanup | qué comando borra y cómo se verifica (y por qué `az group exists` = `false` no vale si la sesión es otra suscripción) |
| Diseño de datos (LP4) | clave de partición, RU/s, consistencia, índices vectoriales vs. coste de la consulta |

Reglas de las preguntas: formato examen MS (enunciado de escenario, 3-4 opciones, una correcta), distractores plausibles, sin pistas por longitud ni posición (varía la letra correcta), y sin IDs, claves ni datos personales. Si el lab no tiene material suficiente para N preguntas, hazlas menos y dilo.

## 3. Hacer el quiz (una pregunta por vez)
Por cada pregunta, usa `AskUserQuestion` (una sola pregunta por llamada; `header` = «P3/5»; opciones con etiqueta corta; **sin marcar cuál es la correcta**; sin `preview` salvo que ayude a comparar YAML/comandos). Tras cada respuesta, antes de la siguiente, evalúa:
- **✅ / ❌** y la opción correcta.
- **Por qué**: 1-3 líneas; para cada distractor elegido, qué lo hace incorrecto.
- **Dónde se practicó**: enlace al paso del README o bloque de `salidas.md`.
- Si falló: cómo recordarlo (analogía K8s o regla mnemotécnica) y, si es un comando, la comprobación que lo demuestra.
No reveles la siguiente pregunta antes de evaluar la actual. Si el alumno elige «Other» con texto libre, evalúa su razonamiento igualmente.

## 4. Resumen final
Tabla `pregunta · tema · resultado`, nota (aciertos/total y %), **puntos débiles** (temas fallados) y qué repasar (enlaces a README/nota del módulo). Después ofrece, sin hacerlo por defecto:
1. Guardar el resultado y los fallos en `docs/tests/quiz-<lab>-AAAA-MM-DD.md` (sin datos personales).
2. Añadir un fallo relevante como aprendizaje en `docs/aprendizajes.md` (vía `/aprender`).
3. Repetir solo las falladas, otro lab, o terminar.

## Reglas
- Solo lectura sobre Azure: este skill **no ejecuta** `az` ni crea recursos. Si una pregunta de cleanup lo menciona, solo explica.
- Si el alumno pide ayuda con Azure a mitad del quiz, delega en el agente `oscar`, y retoma la pregunta pendiente.
- Todo comando que se mencione en una explicación lleva su comprobación (comando de verificación + resultado esperado + qué hacer si no coincide).
