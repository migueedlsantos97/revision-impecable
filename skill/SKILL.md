---
name: revision-impecable
description: Reviews, tests and polishes any running web page or app, in any project, without needing prior knowledge of it. Use when asked to "review everything", "make it flawless", "test the app", "QA this", "before showing it / before deploying", "run overnight", or in Spanish "revisá todo", "que quede impecable", "probá la app", "testeá", "antes de mostrarlo", "antes de desplegar", "dejalo corriendo toda la noche", "no quiero novatadas". A script measures what needs no judgment, parallel reviewers cover what does, functions are exercised like a user, every finding is refuted before fixing, fixes go in the shared component, and the run learns from what escaped. Can work alone overnight.
---

# Revisión impecable / Flawless review

Como un equipo de testers, diseñadores y programadores revisando la app entera.
Llega a los detalles **antes** que la persona que la usa, los arregla, y cada
corrida aprende de lo que se le escapó a la anterior. Los encargos aplican a
cualquier idioma de interfaz; esta skill está escrita en español y trae un
glosario ES/EN al final.

La regla de fondo: **no se termina cuando funciona, se termina cuando nada
parece accidental** y cuando cada categoría de defecto posible tiene una marca
en la tabla de cobertura (paso 3).

## Ideas que mandan sobre todo lo demás

1. **Sin verificación no hay loop.** Se corre la app, se usa como una persona,
   se mira la captura, se lee el dato guardado. "Compila" no es prueba.
2. **Lo mecánico lo hace un script; el criterio, los agentes.** `scripts/medir.py`
   mide siempre igual; los revisores gastan su criterio en lo que no se mide.
3. **Se arregla el entorno, no el caso.** Un defecto en dos lugares se arregla
   en el componente, token o regla compartida.
4. **Cada error se vuelve estructura** (chequeo, lint, test) y recién después texto.
5. **Lo general vive en la skill; lo del proyecto, en su adaptador**
   (`.claude/revision/`).
6. **Cobertura propia, no solo lo que se pidió o se vio.** Lo que la persona
   señala es UNA señal más (ver "Corrección del usuario"); nunca reduce el alcance.
7. **Escalera de garantías: estructura > chequeo duro > test > texto blando.**
   Una regla que solo vive en texto se olvida; si una persona tuvo que hacer
   cumplir una invariante en una revisión, esa invariante se vuelve chequeo.
8. **La confianza se gana antes de escalar.** Se empieza ligero (script + 2
   revisores) y se amplía solo si la medición o el tamaño lo justifican; se gasta
   primero en restricciones que hacen acertar hasta al agente más simple
   (`references/coordinacion.md`).
9. **El estado vive en disco**, no en la cabeza del agente: checkpoint, relevo y
   estado por sistema (`references/relevo.md`, `references/incremental.md`).

Estándar de diseño de base: `references/hig.md`. Las reglas del proyecto mandan.
Valores numéricos, anchos y criterios de parada: **una sola tabla**,
`references/umbrales.md`.

## Dos modos

- **Acompañado** (por defecto): los cambios de diseño grandes se muestran antes.
- **Noche** ("dejalo corriendo", "work alone overnight", o `"autonomia":"noche"`):
  no se pregunta nada; se decide con las reglas, se trabaja en un worktree y una
  rama propios, con presupuesto, checkpoints y relevo si se llena el contexto, y
  al volver la persona lee `LEEME-AL-VOLVER.md`. Si no se puede construir un
  adaptador que arranque, **se aborta con un informe** (no se inventa). Ver
  `references/noche.md` y `references/relevo.md`.

**Límites que ningún modo cruza:** nunca producción con escritura, nunca datos
reales, nunca deploy, nunca push a la rama principal ni `--force`, nunca borrar
datos de la persona, nunca matar procesos por nombre (solo los que levantó la
corrida), nunca escribir secretos en el repo. **Permitido:** lecturas GET de
sitios públicos (enlaces salientes, cabeceras, `robots.txt`); nunca mutar. Lo
que haga falta cruzar se anota como pendiente.

## Procedimiento

### 0. El adaptador
Buscá `.claude/revision/proyecto.json`.
- **No existe:** generalo con `references/adaptador.md` (empieza por
  "Descubrimiento en 10 minutos") y probalo de punta a punta. En modo noche, si
  no arranca, abortá con informe.
- **Existe:** corré `medir.py --validar` (doctor, login por rol, una pantalla);
  agregá pantallas nuevas (rutas, menús, commits) y, si el mapa tiene días, el
  pase de mantenimiento (`references/coordinacion.md`, §5).

### 1. Preparar
- Rama `revision/<fecha>` (obligatoria de noche, y en worktree propio).
- Si existe `checkpoint.json` sin terminar: **reanudar** (`references/relevo.md`),
  no empezar de cero.
- Si hay `estado/` y `dependencias.json`: `scripts/alcance.py` decide qué revisar
  y qué queda "vigente @sha" (`references/incremental.md`). Sin estado: completa.
- **Escala**: ligera por defecto; ampliada o completa según
  `references/coordinacion.md`. Presupuesto y tope en el adaptador
  (`scripts/presupuesto.py`).
- Activá los guardrails del repo (`.githooks/` con `core.hooksPath`, linters de
  CI): un commit tuyo no se saltea lo que se le exige a una persona. [caso real #36]
- Instancia de **prueba**; corré los tests existentes y anotá el número.
- Leé reglas del proyecto (`reglas.md`, `CLAUDE.md`, guías). Lo decidido no se discute.
- **Escapes anteriores:** `git log --since=<revisión previa>` sobre lo cubierto;
  todo commit que arregla algo que debió cazarse es un escape.
- **Lo último cambiado va primero:** `git log --name-only` de los últimos días.
- Si la persona señaló algo concreto, aplicá ya "Corrección del usuario".

### 2. Medir (script)
```bash
python <skill>/scripts/medir.py --config .claude/revision/proyecto.json
```
Deja `informe.md/json`, capturas y hojas de contacto en
`.claude/revision/salida/<fecha>/`. `--rapido` mide solo dos anchos.
`--descubrir` explora el sitio y propone pantallas (ver adaptador.md). Lo
**medido** está confirmado; las **sospechas** se refutan mirando la captura.
El script hace además chequeos generales del documento, imágenes, campos,
estructura, red, estabilidad de layout y tipografía; el detalle de tipos de
falla está en `--help` y en `informe.md`.

### 3. Cobertura sistemática
Antes de despachar, creá `salida/<fecha>/cobertura.md`: una fila por categoría
con **MEDIDO** (script), **REVISADO** (revisor N, con prueba) o **N/A** (motivo
en una línea). Categorías mínimas:

1 funciones y datos · 2 permisos · 3 formularios y validación · 4 teclado y foco
· 5 lector de pantalla y estructura (landmarks, headings, labels, lang, title)
· 6 contraste, color y zoom 200 % · 7 tamaños y reflujo (anchos y alturas)
· 8 estados (vacío, carga, error, lento, offline, desbordado, volumen)
· 9 tablas, listas y gráficos · 10 subida y descarga de archivos · 11 tema
oscuro, contraste forzado, movimiento reducido · 12 textos, idioma, formatos y
zonas horarias · 13 red y seguridad de front · 14 rendimiento y estabilidad de
carga · 15 metadatos y cómo se comparte (si es pública) · 16 impresión y
exportes · 17 compatibilidad de navegadores · 18 consistencia entre pantallas y
sistemas · 19 enlaces, 404, deep links y Atrás · 20 superficies no web (API/CLI).

Una categoría sin marca **bloquea la salida**. Las N/A se auditan en la corrida
siguiente. Lo que la persona señaló cuenta como una fila más, no la sustituye.

### 4. Revisores en paralelo (criterio)
Encargos en `references/encargos.md`, técnicas en `references/tecnicas.md`.
Escala y modelo por rol: `references/coordinacion.md` (**ligera**: revisores 1 y
2; se suman los demás si la medición lo pide, o todos si el pedido es "revisá
todo", es la primera revisión o hubo escapes). Despachá los de la escala
elegida **juntos, en un mensaje**, cada uno con su sección entera, la
raíz, `informe.md`, capturas, feature map, `cobertura.md` y el contrato de
salida. **Cada revisor usa su propio contexto de navegador** (perfil/contexto
Playwright separado); los que cambian datos (1, 5, 6) además su propia
instancia y datos.

| # | Revisor | Mira |
|---|---|---|
| 1 | Funciones | cada función, de punta a punta, con el dato guardado como prueba; formularios, archivos, impresión/exportes |
| 2 | Diseño y consistencia | capturas contra hig.md y entre sí; tablas grandes y gráficos |
| 3 | Controles, teclado y lectores | lo que dibuja el sistema, teclado, foco, lector, contraste forzado |
| 4 | Textos | un nombre por cosa, concordancia, idioma y formatos |
| 5 | Estados límite y anchos | vacío, error, red, lento, volumen, zoom, movimiento reducido |
| 6 | Datos, permisos y seguridad | permisos, pérdida, duplicados, seguridad de front y de servidor |
| 7 | Web pública (solo si `"publica":true`) | navegadores, rendimiento, SEO, cómo se comparte, enlaces |

Si no es pública, el revisor 7 no corre y se anota N/A en las filas 15 y 17.
Lo que un revisor no corre por la escala se marca N/A "escala ligera" y se
audita en la corrida siguiente.

**Verificar la cadena**: antes de dar por cubierta una fila, se contrasta lo que
el revisor dice haber mirado con su transcripción o registro (qué archivos y
capturas abrió realmente); una afirmación sin apertura invalida la fila y el
revisor se re-despacha (`references/coordinacion.md`, §4).
Proyecto solo API/CLI: ver encargos.md, "Superficies no web".

**Encargo puntual:** se despachan igual **todos** los revisores aplicables, con
el foco puntual como prioridad adicional. Solo se omite uno si el tipo de
proyecto no lo admite, y el informe dice cuál y por qué.

**Contrato de salida.** Cada hallazgo: dónde (`archivo:línea`, o pantalla +
ancho + tema, o selector); **qué le pasa a una persona**, en una frase; **la
prueba**; severidad (cajón del paso 6) o "gusto"; **dónde se arregla una sola
vez**. Línea final: qué no pudo revisar.

### 5. Refutar antes de aceptar
Ningún hallazgo se arregla por venir de un revisor. Lo refuta **un agente
distinto del que arregla** (refutador independiente): reproduce, mide, prueba
contra la instancia. Veredicto **CONFIRMADO**, **PLAUSIBLE** (va al informe, no
se arregla a ciegas) o **DESCARTADO** (queda con el motivo). Con más de 30
hallazgos se refutan todos los del cajón 1 y una muestra de al menos un tercio
(mínimo 10) de los demás, priorizando los que llegan sin prueba; si la muestra
falla más de 1 de cada 5, se refuta todo. Una afirmación sobre el navegador se
prueba en el navegador. [caso real #1]

### 6. Ordenar por lo que cuesta (los "cajones")
1. **Cajón 1 — Le cuesta al usuario**: no funciona, no se entiende, pierde o
   duplica datos, deja hacer lo que no debe, se ve roto donde se usa.
2. **Cajón 2 — Delata falta de oficio**: funciona pero se nota (controles de
   fábrica, valores casi iguales, un botón distinto por sistema, dos nombres).
3. **Cajón 3 — No lo nota nadie**: se arregla si es barato.

El gusto va aparte: acompañado no se toca; de noche se decide con las reglas y
queda anotado con la captura de antes.

### 7. Arreglar, donde vale para todo
- Primero la causa compartida; si cada sistema tiene su versión de un
  componente, se unifican en una.
- Rediseño con `hig.md` cuando arreglar de a uno no alcanza; misma solución en todos lados.
- Un commit por tema, explicando qué le pasaba a la persona.
- **Un cambio, una medición, keep o revert**: se mide contra la vuelta anterior;
  si no baja lo que debía o rompe algo, se revierte y queda la fila en
  `decisiones.tsv` (antes / después / delta / tests / veredicto / evidencia).
- Arreglos en paralelo: zonas de archivos con un solo dueño y worktrees
  (`references/coordinacion.md`, §3).
- Tras cada tanda, **volver a medir** (todo, o lo que `alcance.json` marque más
  las sondas), correr tests y las funciones del mapa, y escribir el checkpoint.
- **Baseline visual**: con la medición limpia, las capturas aprobadas se guardan
  (`medir.py --aprobar-baseline --motivo "..."`); en las vueltas y corridas
  siguientes `--baseline` compara y marca `regresion_visual`. Nunca se regenera
  el baseline para hacer pasar un diff: solo con motivo escrito y captura.
- Repetí 4-7 hasta cumplir el criterio de parada de `umbrales.md` (la meseta se
  pivota una vez antes de parar; los silenciamientos cuentan en contra).

### 8. Fijar: que no pueda volver
Por cada clase confirmada, la primera que funcione: (1) **estructura** (un solo
componente/token); (2) **chequeo que falla** (genérico en `scripts/`, del
proyecto en sus tests/lint); (3) **test**; (4) **texto** en el encargo o
`reglas.md`, solo si necesita criterio. Probá que el chequeo nuevo **falla con
el defecto real**. Un chequeo propio vive en `.claude/revision/chequeos/` y se
**engancha al pre-commit o al CI del proyecto** (si no se puede, queda como deuda
en `reglas.md`); un chequeo que no corre donde se exige a una persona es texto.

### 9. Informe y aprender
- `docs/revision-<fecha>.md` con `assets/plantilla-informe.md`: tabla de
  cobertura, capturas antes/después, "para tu ojo", "correcciones del usuario".
- Cinco preguntas, con nombre y apellido: **escapes** (qué chequeo los caza
  ahora), **falsos positivos**, **chequeos dormidos** (tres corridas sin
  disparar y se borran con constancia), **técnicas nuevas**, **revisores flojos**.
- Aplicá los cambios, no los propongas, **en el proyecto**: reglas →
  `.claude/revision/reglas.md` (columna "lo hace cumplir" obligatoria);
  bitácora de la corrida → `.claude/revision/bitacora.md`; chequeos propios →
  `.claude/revision/chequeos/` y sus tests.
- **Mejora continua doble** (`references/mejora-continua.md`): cada aprendizaje se
  clasifica `general` o `proyecto` con una sola tabla. Lo del proyecto mejora su
  adaptador, chequeos y mapa en el acto; lo general se candidatea. La corrida
  escribe `metricas.json`: la app queda más cubierta y, si tres corridas no
  bajan el costo, se pasa a revisión incremental.
- Al estado verificado: `scripts/estado.py` registra por sistema qué quedó
  verificado y en qué commit (solo los sistemas revisados).
- En noche, `LEEME-AL-VOLVER.md` con la sección "Atención" escrita por **otro**
  revisor (`references/noche.md`, §7).
- **Cómo sube un aprendizaje a la skill:** nunca se escribe en la copia
  instalada. Un candidato a general se redacta en
  `.claude/revision/candidatos/<tema>.md` **sin** nombres de cliente o
  producto, rutas, URLs, textos de interfaz ni cifras de la corrida. Sube solo
  si (a) se repitió en otro proyecto, o (b) fue un escape real con causa
  técnica demostrable (especificación, navegador). Se propone por PR al repo de
  la skill: la regla en 1-2 líneas y la anécdota anonimizada aparte en
  `ejemplos/casos-reales.md`. Una corazonada es hipótesis y espera repetirse.

## Corrección del usuario (en cualquier momento)

Cuando la persona señala un defecto concreto ("los encabezados están mal", "ese
botón no se ve"), es **una señal más, no el nuevo alcance**. En orden:

0. **Mapear el reporte al feature map**: un reporte vago ("no anda esto", una
   captura sin texto) se ubica primero en `funciones/` (qué función, cómo se
   llega, qué prueba que anda); si no está en el mapa, es un hueco del mapa y se
   agrega.
1. Arreglar el caso señalado, con antes/después.
2. Nombrar su **clase** en una frase genérica ("jerarquía y alineación de
   encabezados") y barrerla en TODO el proyecto: cada instancia y variante
   (otros niveles, sistemas, anchos, claro/oscuro, estados vacío/error).
3. Si no hay chequeo, escribirlo y verificar que **falla con el defecto real**;
   si necesita criterio, una línea en el encargo que corresponda.
4. Registrar en `reglas.md`: regla / por qué / qué la hace cumplir.
5. **Volver a la cobertura completa:** la corrección no cancela, reordena ni
   recorta los pasos 3-4. Si el pedido era solo esa cosa, el informe lo dice
   ("se corrigió X y su clase; el resto no se revisó"). Prohibido dar el
   proyecto por revisado porque la clase señalada quedó limpia.
6. El informe incluye "Correcciones del usuario": caso, clase, instancias
   halladas y arregladas, chequeo creado y al menos **2 clases vecinas** que se
   miraron para no quedar anclado.

## Criterio de salida
- Medición completa; última vuelta en el informe.
- `cobertura.md` sin categorías vacías; N/A con motivo.
- Revisores entregaron, o está escrito cuáles no y por qué.
- Todo hallazgo tiene veredicto; cajones 1 y 2 vacíos o con motivo escrito.
- Tests pasan y hay más que al empezar; las funciones del mapa andan.
- **Silenciamientos** (tipos desactivados, `data-revision-ok`, chequeos
  borrados) no aumentaron sin motivo escrito; el informe los cuenta.
- La cadena de los revisores se verificó (sin filas invalidadas pendientes).
- Ningún componente tiene más formas que las permitidas ni cambia según el sistema.
- Paso 9 hecho: bitácora del proyecto con entrada y reglas/adaptador cambiados
  (aunque sea para borrar algo).

## Glosario ES/EN
| ES | EN |
|---|---|
| adaptador | project adapter |
| mapa de funciones | feature map |
| cajón | severity bucket |
| refutar | disprove / verify independently |
| medido / sospecha | measured / suspected |
| escape | escaped defect (found after "done") |
| captura | screenshot |
| hallazgo | finding |
| corrección del usuario | user-pointed defect |
