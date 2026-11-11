# Sesión 6 · 2026-11-10 · Inicio: documentación del día

> Exportación saneada de la conversación con Claude Code (correo, GUID, credenciales del lab y nombres sustituidos; resultados de herramientas recortados). Índice: [README](README.md).



## 🧑 Alumno · 17:14 UTC

tenemos nueva clase del curso recoge la documetnacion nueva https://drive.google.com/drive/folders/10t4PEqTY9FqtvKHyTzmHpis8_VsHbFP3


**🔧 Bash** — Leer memoria de Drive y listar docs

```text
cat ~/.claude/projects/-home-alumno-claude-AI-200-Developing/memory/reference-drive-archivos-diarios.md; ls docs/ docs/*/ | head -50; ls sesiones/
```


<details><summary>Resultado</summary>

```text
---
name: reference-drive-archivos-diarios
description: "Carpeta de Google Drive con los archivos (PDF de módulo, knowledge check) de cada día del curso; descargarlos al iniciar sesión"
metadata:
  node_type: memory
  type: reference
  originSessionId: <guid>
  modified: 2026-11-05T16:58:38.712Z
---

Carpeta de Drive con los materiales del día: https://drive.google.com/drive/folders/10t4PEqTY9FqtvKHyTzmHpis8_VsHbFP3

**Why:** el alumno sube ahí los PDF de cada día (módulo `AI-200T00A-NN_…pdf`, `LPn - Knowledge check.pdf`) y pidió que se recuerde al empezar la sesión.

**How to apply:** al iniciar sesión, recordar/ofrecer descargar los archivos de hoy desde esa carpeta y dejarlos en `docs/` (solo PDF, sin metadatos de autor; ver CLAUDE.md). La carpeta es privada: puede requerir que el alumno los descargue o dé acceso; no inventar contenido si no se puede leer. Relacionado: [[feedback-alumno-ejecuta-cambios]].
docs/:
00-plan
AI-200T00A-00_Introduction.pdf
AI-200T00A-01_Implement container application hosting on Azure.pdf
AI-200T00A-02_Deploy and manage apps on Azure Container Apps.pdf
AI-200T00A-03_Deploy and monitor applications on Azure Kubernetes Service.pdf
AI-200T00A-04_Develop AI solutions with Azure Cosmos DB for NoSQL.pdf
aprendizajes.md
img
Links (1).txt
Links (2).txt
links.md
LP1 - Knowledge check.pdf
LP2 - Knowledge check.pdf
LP3 - Knowledge check.pdf
LP4 - Knowledge check.pdf
modulos
Test-Modulos-20261027T171555Z-1-001.zip
tests

docs/0
… [recortado, 1895 caracteres]
```
</details>


**🔧 Bash** — Buscar cómo se descargó la última vez

```text
which gdown; grep -ril "drive.google\|gdown" sesiones/ .claude/ 2>/dev/null | head; grep -i -A3 "drive" sesiones/2026-11-05-sesion-05-cosmosdb.md | head -20
```


<details><summary>Resultado</summary>

```text
(Bash completed with no output)
```
</details>


**🔧 Bash** — Listar contenido de la carpeta pública de Drive

```text
mkdir -p tmp/drive && cd tmp/drive && curl -sL "https://drive.google.com/embeddedfolderview?id=10t4PEqTY9FqtvKHyTzmHpis8_VsHbFP3#list" -o folder.html; wc -c folder.html; grep -oE 'file/d/[A-Za-z0-9_-]+|folders/[A-Za-z0-9_-]+' folder.html | sort -u; grep -oE 'flip-entry-title">[^<]+' folder.html
```


<details><summary>Resultado</summary>

```text
3630 folder.html
file/d/1W0-SIooyVPkAS_ZBZA21NvV49jchV8L4
folders/14xaP1NRpyfHflhJiB4o94wMSrZNrOPo2
folders/1JhtRce3H8NVIdabA9APeO9xq5TFFm26N
flip-entry-title">PPTs
flip-entry-title">Test-Modulos
flip-entry-title">Links.txt
```
</details>


**🔧 Bash** — Listar subcarpetas PPTs y Test-Modulos

```text
for f in 14xaP1NRpyfHflhJiB4o94wMSrZNrOPo2 1JhtRce3H8NVIdabA9APeO9xq5TFFm26N; do echo "== $f"; curl -sL "https://drive.google.com/embeddedfolderview?id=$f" -o $f.html; paste <(grep -oE 'file/d/[A-Za-z0-9_-]+' $f.html | sed 's#file/d/##' | awk '!s[$0]++') <(grep -oE 'flip-entry-title">[^<]+' $f.html | sed 's/.*">//'); done
```


<details><summary>Resultado</summary>

```text
== 14xaP1NRpyfHflhJiB4o94wMSrZNrOPo2
1uXExy48Kxy25t2K-OqL9oVGF-7TsSbo5	AI-200T00A-00_Introduction.pdf
1jsV-6tiydUr8TM7LzQ8wABX7OXPgn-WP	AI-200T00A-01_Implement container application hosting on Azure.pdf
1IDcCOAqvokocaALu1gs1nVq8cVSNuRYp	AI-200T00A-02_Deploy and manage apps on Azure Container Apps.pdf
1ggmzXxbfdBnBRa5ClWGhg0B3p5icedXP	AI-200T00A-03_Deploy and monitor applications on Azure Kubernetes Service.pdf
1S6uPOjuRdHfUm-yJvlrZChzCfq-DGfKp	AI-200T00A-04_Develop AI solutions with Azure Cosmos DB for NoSQL.pdf
12mFD5O193tz82KHT_zV14lKxYGtHLCnE	AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf
== 1JhtRce3H8NVIdabA9APeO9xq5TFFm26N
1aoCq3g4Aw5QJbTBDIeFiYL6nmQOHrE1O	LP1 - Knowledge check.docx
12k15IBmxNr-Thl02gLDkeMPlFIRmwyVz	LP1 - Knowledge check.pdf
1_t1Doc0YFMQmgeCxlFMZ8S5yXq3-LWKL	LP2 - Knowledge check.docx
1fD8iQ6UQf8yx4tVuBn5NeOChL0fn7azr	LP2 - Knowledge check.pdf
1vUKhLQdqQ0Atncs7KlgpUUih_HEzioar	LP3 - Knowledge check.docx
1c4QAoEfExNE55f-k_ydJ_G0l7mGk84Rn	LP3 - Knowledge check.pdf
1Rqsru8GFiT6Xy9vdyO38flienfqUbleQ	LP4 - Knowledge check.docx
1r-5wfzQaLtHxDcVPJjl0Kw-loLADAJLk	LP4 - Knowledge check.pdf
1pCDpQ60UwBvTU5xAhdRqOYCnpyY6BqbU	LP5 - Knowledge check.docx
1IAvxRUQTOZtVKkYN4b-BjQeZ847wb2gI	LP5 - Knowledge check.pdf
```
</details>


### 🤖 Claude · 17:15 UTC

Novedades: módulo 05 (PostgreSQL) y LP5 Knowledge check, más Links.txt (por si cambió). Descargo:


**🔧 Bash** — Descargar PDF nuevos y comparar Links.txt

```text
dl(){ curl -sL "https://drive.usercontent.google.com/download?id=$1&export=download&confirm=t" -o "$2"; file "$2"; }; dl 12mFD5O193tz82KHT_zV14lKxYGtHLCnE "AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf"; dl 1IAvxRUQTOZtVKkYN4b-BjQeZ847wb2gI "LP5 - Knowledge check.pdf"; dl 1W0-SIooyVPkAS_ZBZA21NvV49jchV8L4 Links.txt; diff Links.txt "../../docs/Links (2).txt" >/dev/null && echo "Links igual a (2)" || diff Links.txt "../../docs/Links (1).txt" | head
```


<details><summary>Resultado</summary>

```text
AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf: PDF document, version 1.7, 38 page(s)
LP5 - Knowledge check.pdf: PDF document, version 1.7, 2 page(s)
Links.txt: Unicode text, UTF-8 text, with CRLF line terminators
Links igual a (2)
```
</details>


### 🤖 Claude · 17:15 UTC

Links.txt no ha cambiado. Ahora quito metadatos de autor y los paso a `docs/`:


**🔧 Bash** — Ver metadatos de los PDF descargados

```text
cd ~/claude/AI-200-Developing && which exiftool qpdf pdfinfo; for f in tmp/drive/*.pdf; do echo "== $f"; pdfinfo "$f" | grep -iE "author|creator|producer|title"; done; echo "== referencia (anterior)"; pdfinfo "docs/LP4 - Knowledge check.pdf" | grep -iE "author|creator|producer|title"
```


<details><summary>Resultado</summary>

```text
/usr/bin/pdfinfo
== tmp/drive/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf
Title:           
Author:          
Creator:         Microsoft® PowerPoint® para Microsoft 365
Producer:        Microsoft® PowerPoint® para Microsoft 365
== tmp/drive/LP5 - Knowledge check.pdf
Author:          <autor del PDF>
Creator:         Microsoft® Word para Microsoft 365
Producer:        Microsoft® Word para Microsoft 365
== referencia (anterior)
Title:           LP4 - Knowledge check
Author:          Curso AI-200
Creator:         Microsoft® Word para Microsoft 365
Producer:        GPL Ghostscript 10.02.1
```
</details>


### 🤖 Claude · 17:15 UTC

Mismo tratamiento que el LP4 (Ghostscript, autor «Curso AI-200"):


**🔧 Bash** — Limpiar metadatos y copiar PDF a docs

```text
printf '[ /Title (LP5 - Knowledge check) /Author (Curso AI-200) /DOCINFO pdfmark\n' > tmp/drive/meta.ps && gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="docs/LP5 - Knowledge check.pdf" "tmp/drive/LP5 - Knowledge check.pdf" tmp/drive/meta.ps && cp "tmp/drive/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf" docs/ && for f in "docs/LP5 - Knowledge check.pdf" "docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf"; do echo "== $f"; pdfinfo "$f" | grep -iE "author|title|pages"; done; pdftotext "docs/LP5 - Knowledge check.pdf" - | grep -ci oscar; git status --short
```


<details><summary>Resultado</summary>

```text
== docs/LP5 - Knowledge check.pdf
Title:           LP5 - Knowledge check
Author:          Curso AI-200
Pages:           2
== docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf
Title:           
Author:          
Pages:           38
0
?? "docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf"
?? "docs/LP5 - Knowledge check.pdf"
```
</details>


**🔧 Bash** — Comprobar metadatos XMP

```text
for f in docs/AI-200T00A-05*.pdf "docs/LP5 - Knowledge check.pdf"; do pdfinfo -meta "$f" | grep -iE "creator>|author|dc:creator" -A2 | head -5; done; echo fin
```


<details><summary>Resultado</summary>

```text
<dc:title><rdf:Alt><rdf:li xml:lang="x-default"></rdf:li></rdf:Alt></dc:title><dc:creator><rdf:Seq><rdf:li></rdf:li></rdf:Seq></dc:creator></rdf:Description>
<rdf:Description rdf:about=""  xmlns:xmp="http://ns.adobe.com/xap/1.0/">
<xmp:CreatorTool>Microsoft® PowerPoint® para Microsoft 365</xmp:CreatorTool><xmp:CreateDate>2026-10-26T20:23:55+01:00</xmp:CreateDate><xmp:ModifyDate>2026-10-26T20:23:55+01:00</xmp:ModifyDate></rdf:Description>
<rdf:Description rdf:about="" xmlns:dc='http://purl.org/dc/elements/1.1/' dc:format='application/pdf'><dc:title><rdf:Alt><rdf:li xml:lang='x-default'>LP5 - Knowledge check</rdf:li></rdf:Alt></dc:title><dc:creator><rdf:Seq><rdf:li>Curso AI-200</rdf:li></rdf:Seq></dc:creator></rdf:Description>
</rdf:RDF>
</x:xmpmeta>
fin
```
</details>


### 🤖 Claude · 17:15 UTC

Ya tienes la documentación nueva en `docs/`:

| Fichero | Contenido |
|---|---|
| `docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf` | Presentación del módulo 05 (38 páginas) |
| `docs/LP5 - Knowledge check.pdf` | Knowledge check del LP5 (2 páginas) |

- **Metadatos:** la presentación ya venía sin autor. El knowledge check traía el nombre del profesor; lo he cambiado por «Curso AI-200», igual que el LP4. He comprobado los dos ficheros con `pdfinfo` (incluidos los metadatos XMP) y ya no aparece ningún nombre personal.
- **Lo que no he descargado:** los `.docx` de los knowledge check, porque en el repo solo se guardan los PDF. Tampoco `Links.txt`, que es igual que el `docs/Links (2).txt` que ya tenías.
- Las copias descargadas se han quedado en `tmp/drive/`, que git ignora.

**Comprobación:** ejecuta `git status --short`. Deberían aparecer solo esos dos PDF como nuevos (`??`). Si sale algo más, avísame antes de hacer commit.

Todavía estás en `main` y no he hecho commit. Siguiente paso: ¿creo la rama del día `dia-06-2026-11-10` y empiezo las notas `docs/modulos/05-postgresql.md` y el registro de la sesión?


## 🧑 Alumno · 17:16 UTC

<pasted_content id="1013">
alumno@pc:~/claude/AI-200-Developing$ git status --short
?? "docs/AI-200T00A-05_Develop AI solutions with Azure Database for PostgreSQL.pdf"
?? "docs/LP5 - Knowledge check.pdf"
alumno@pc:~/claude/AI-200-Developing$ 
</pasted_content id="1013">


### 🤖 Claude · 17:16 UTC

La salida es la esperada: aparecen solo los dos PDF nuevos y nada más. Puedes hacer commit sin problema.

Sigue pendiente lo de antes, porque aún estás en `main`: ¿creo la rama `dia-06-2026-11-10`, hago commit de los dos PDF y empiezo las notas del módulo 05 (PostgreSQL) y el registro de la sesión de hoy?


