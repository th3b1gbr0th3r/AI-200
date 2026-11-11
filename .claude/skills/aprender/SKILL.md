---
name: aprender
description: Cierre de día del curso AI-200. Recoge el aprendizaje del día (concepto, comando, error resuelto), actualiza el registro de sesión y el diario de aprendizajes, y hace commit y push. Úsalo cuando el usuario diga "aprender", "cierra sesión" o "fin del día".
---

# Aprender — cierre de día

Objetivo: que cada día quede **al menos un aprendizaje** escrito con palabras del alumno, útil para repasar y para el examen.

## Pasos
1. **Recoger el día.** Revisa la conversación y los ficheros cambiados hoy (`git status`, `git log --since=midnight`). Resume en 3-5 líneas qué se vio (learning path, labs hechos, errores).
2. **Proponer aprendizajes.** Sugiere 2-3 candidatos concretos (un concepto, un comando `az`/código, un error y su causa) y pregunta al usuario cuál quiere guardar o si prefiere otro. No lo des por cerrado sin su elección.
3. **Redactar la entrada** en `docs/aprendizajes.md` (más reciente arriba) con este formato:
   ```
   ## AAAA-MM-DD · <tema corto>
   - **Aprendizaje:** una o dos frases.
   - **Analogía K8s:** si aplica.
   - **Comando / código:** bloque mínimo reproducible.
   - **Error típico:** síntoma → causa → arreglo.
   - **Repaso:** una pregunta tipo test (4 opciones, la D nunca correcta es opcional; solo si es útil).
   ```
4. **Actualizar la sesión** `sesiones/AAAA-MM-DD-<tema>.md` (crearla si no existe) como **hilo conductor de la clase**: en orden, qué se vio y por qué, con enlace a la nota del módulo y al paso de cada lab; luego decisiones, estado y pendientes. Enlaza el aprendizaje.
4b. **Comprobar la limpieza.** Antes de cerrar, verificar que se destruyó todo lo creado en los labs del día (`az group list -o table` sin `rg-ai200-*`); si queda algo, dar los comandos de borrado al alumno. Es obligatorio. Ojo (05/11/2026): cada lab de la plataforma puede traer **otra suscripción** (`az account show --query name -o tsv`); si cambió desde que se lanzó el borrado, `az group exists` devuelve `false` aunque el grupo siga vivo en la anterior, así que ese cleanup se documenta como «borrado lanzado, no verificado». El cierre del día solo se da por verificado para los grupos de la suscripción actual.
5a. **Salidas reales dentro del README.** Comprobar que cada lab del día es un `labs/<lab>/README.md` seguible de principio a fin: en cada paso, por qué, comando, salida real saneada, «Qué mirar» y comprobación (modelo: `labs/lp5-02-pg-vector-search/README.md`). No se crean `salidas.md` separados.
5. **Documentar los labs del día** en `labs/lpN-NN-*/README.md` (ver "Estándar de documentación de comandos"): objetivo, diagrama de qué se construye, fases, comandos al detalle, resultados e incidencias. Las notas de clase van a `docs/modulos/NN-*.md`.
6. **Comprobar seguridad** antes de subir: sin credenciales, IDs de suscripción/tenant, endpoints con claves, datos personales de terceros (nombres de docente y compañeros) ni metadatos con nombres de personas en los ficheros del curso (PDF/docx: comprobar autor/último editor y limpiarlo antes de subir). Acuerdo del 29/10/2026: las presentaciones PDF y los knowledge check del curso son públicos y **sí se suben**, igual que los scripts de aprovisionamiento de los labs de Microsoft (`azdeploy.py`, `api/`, `document.txt`) **sí se suben**, incluido el zip original del lab (repo de origen MIT, ver `labs/NOTICE.md`); los `.env` de `labs/` también se suben (sin claves: comprobar antes con un grep de `KEY|SECRET|TOKEN|PASSWORD`; los que las tengan siguen ignorados), y los `.env` fuera de `labs/` siguen fuera. El repo es público. Una transcripción de clase se usa para extraer contenido, nunca se publica.
7. **Una rama y una PR por día de curso.** Rama `dia-NN-AAAA-MM-DD` desde `main` actualizado; commit; push con el patrón del repo (token en cabecera temporal, nunca en `.git/config`); abrir la PR contra `main` con `gh pr create` usando `.github/pull_request_template.md` (`GH_TOKEN` solo inline en el comando). No hacer merge salvo que el usuario lo pida expresamente. Volver a `main` al terminar.
8. Si el aprendizaje es una preferencia o acuerdo de trabajo, guárdalo también en la memoria.

## Estándar de documentación de comandos
Pedido por el usuario el 27/10/2026: no basta una tabla de una línea por comando. Cada comando documentado lleva, en este orden:
1. **El comando completo** y, debajo, un **desglose por piezas** en bloque de código con flechas (`az` → grupo → acción → cada flag/variable → qué significa su valor). Para variables de entorno: `export`, nombre y valor por separado.
2. **Qué hace**: efecto real, incluyendo lo que ocurre por debajo (comandos `az` que envuelve un script, llamadas asíncronas, agentes efímeros…).
3. **Por qué hace falta**: el problema que resuelve (p. ej. proxy que re-firma TLS, proveedor sin registrar, identidad sin rol).
4. **Qué esperar**: salida típica y cómo leerla (campos que importan, ruido que se ignora).
5. **Detalles / trampas**: flags con significado distinto entre comandos parecidos, diferencias entre `show` y `list`, valores que la CLI oculta, errores típicos con síntoma → causa → arreglo.
6. **Analogía con Kubernetes** cuando ayude, y la relación con el examen.
Los comandos que crean o borran recursos los ejecuta el alumno; en la documentación se marcan igual, pero la ejecución es suya.

## Reglas
- Un aprendizaje bien hecho vale más que cinco apuntes sueltos (si el alumno elige varios, una sola entrada con uno principal y los demás como apoyo).
- Respuestas en español, sin relleno.
- Los labs se guardan con el mismo formato cada día; el curso completo (martes y jueves) vive en el repo.
