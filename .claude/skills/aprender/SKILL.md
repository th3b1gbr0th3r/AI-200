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
4. **Actualizar la sesión** `sesiones/AAAA-MM-DD-<tema>.md` (crearla si no existe): qué se hizo, decisiones, estado, pendientes. Enlaza el aprendizaje.
5. **Comprobar seguridad** antes de subir: sin credenciales, IDs de suscripción/tenant, endpoints con claves, datos personales de terceros ni material con copyright. El repo es público.
6. **Una rama y una PR por día de curso.** Rama `dia-NN-AAAA-MM-DD` desde `main` actualizado; commit; push con el patrón del repo (token en cabecera temporal, nunca en `.git/config`); abrir la PR contra `main` con `gh pr create` usando `.github/pull_request_template.md` (`GH_TOKEN` solo inline en el comando). No hacer merge: lo decide el usuario. Volver a `main` al terminar.
7. Si el aprendizaje es una preferencia o acuerdo de trabajo, guárdalo también en la memoria.

## Reglas
- Un aprendizaje bien hecho vale más que cinco apuntes sueltos.
- Respuestas en español, sin relleno.
