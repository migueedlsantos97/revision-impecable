---
name: revision-impecable
description: Revisa, prueba y deja impecable cualquier web o app andando, en cualquier proyecto. Úsala cuando pidan "revisá todo", "que quede impecable", "probá la app", "testeá", "antes de mostrarlo", "antes de desplegar", "dejalo corriendo toda la noche" o "no quiero novatadas". Mide con un script lo que no necesita criterio, despacha revisores en paralelo para lo que sí, prueba las funciones como un usuario, refuta cada hallazgo, arregla en el componente compartido para todas las pantallas y sistemas, y aprende de lo que se le escapó. Puede trabajar sola de noche.
---

# Revisión impecable

Como tener un equipo de testers, diseñadores y programadores revisando la app
entera. Llega a los detalles **antes** que la persona que la usa, los arregla, y
cada corrida aprende de lo que se le escapó a la anterior.

La regla de fondo: **no se termina cuando funciona, se termina cuando nada
parece accidental.** Un valor que no se eligió, un control que dibujó el
sistema, dos cosas parecidas que no son iguales.

## Cinco ideas que mandan sobre todo lo demás

1. **Sin verificación no hay loop.** Nada se da por bueno sin verlo andar: se
   corre la app, se usa como una persona, se mira la captura, se lee el dato
   guardado. "Compila" o "el agente dijo que anda" no es prueba.
2. **Lo mecánico lo hace un script; el criterio, los agentes.** Contraste,
   tamaños, desbordes, solapes, controles de fábrica, foco, tema a medias y
   consistencia los mide `scripts/medir.py` en minutos y siempre igual. Los
   revisores gastan su criterio en lo que un script no ve.
3. **Se arregla el entorno, no el caso.** Un defecto que aparece en dos lugares
   se arregla en el componente, el token o la regla compartida, y vale para
   todas las pantallas y todos los sistemas. Nunca un parche por pantalla.
4. **Cada error se vuelve estructura.** Lo que se escapó una vez se convierte en
   un chequeo del script, un lint o un test que falla si vuelve. Recién si
   necesita criterio, en una línea de encargo.
5. **Lo general vive en la skill; lo del proyecto, en su adaptador.** Esta
   skill sirve para cualquier app. Lo propio de cada una (cómo se levanta, sus
   pantallas, sus funciones, sus reglas de diseño) vive en
   `.claude/revision/` dentro de ese proyecto, y la skill lo genera y lo
   mantiene.

El estándar de diseño de base son las reglas de Apple (Human Interface
Guidelines) resumidas en `references/hig.md`. Las reglas del proyecto, si las
tiene, mandan sobre ellas.

## Dos modos

- **Acompañado** (por defecto): se corre con la persona presente; los cambios
  de diseño grandes se muestran antes de aplicarlos.
- **Noche** (cuando la persona dice "dejalo corriendo", "trabajá sola", "toda la
  noche", o el adaptador dice `"autonomia": "noche"`): **no se pregunta nada.**
  Se decide con las reglas de diseño, se rediseña si hace falta, se arregla, se
  verifica y se commitea en una rama. La persona revisa a la mañana. Ver
  `references/noche.md`.

**Límites que ningún modo cruza:** nunca producción, nunca datos reales, nunca
deploy, nunca push a la rama principal ni `--force`, nunca borrar datos de la
persona, nunca matar procesos por nombre (solo los que levantó la corrida),
nunca escribir secretos en el repo. Si algo de eso hace falta, se deja anotado
en el informe como pendiente.

## Procedimiento

### 0. El adaptador del proyecto

Buscá `.claude/revision/proyecto.json` en la raíz.

- **No existe:** generalo siguiendo `references/adaptador.md`. Se lee el repo,
  no se le pregunta a la persona lo que se puede averiguar. Antes de seguir,
  probalo de punta a punta: levantar, chequear, entrar con cada rol, medir una
  pantalla, apagar.
- **Existe:** corré su chequeo (`doctor`). Si una pantalla nueva no está en el
  mapa (rutas, menús o commits recientes que agregan vistas), agregala. Un mapa
  desactualizado es un escape esperando.

### 1. Preparar

- Trabajá en una rama `revision/<fecha>` (en modo noche, obligatorio).
- **Activá los guardrails del repo** si existen y no están activos: un
  `.githooks/` necesita `git config core.hooksPath .githooks` en cada clone, y
  los linters que el proyecto corre en CI se corren antes de cada commit. Un
  commit tuyo no puede saltearse lo que se le exige a una persona. **[caso
  real]** En la primera corrida v2 un commit pasó con el lint en rojo porque el
  pre-commit estaba versionado pero no activado en ese clone.
- Levantá la instancia de **prueba** del adaptador. Corré los tests que ya
  existan y anotá el número: es la línea de base.
- Leé las reglas del proyecto (`.claude/revision/reglas.md`, `CLAUDE.md`, guías
  de diseño). Lo decidido no se discute; lo pendiente ya es un hallazgo conocido.
- **Escapes de la vez anterior.** Si `reglas.md` tiene una revisión previa:

  ```bash
  git log --oneline --since="<fecha de la revisión anterior>" -- <rutas que cubrió>
  ```

  Todo commit posterior que arregle algo que la revisión debió cazar es un
  escape. Son la nota de la vez pasada y la materia prima del paso 8.
- **Lo que cambió último va primero.** `git log --name-only` de los últimos días
  va a cada revisor como prioridad: en los dos primeros proyectos, la mitad de
  lo grave estaba en código del mismo día.

### 2. Medir (script, minutos)

```bash
python <skill>/scripts/medir.py --config .claude/revision/proyecto.json
```

Recorre cada pantalla en 390, 768, 1366 y 1920 px, en claro y oscuro, y deja en
`.claude/revision/salida/<fecha>/`: `informe.md` (fallas agrupadas y las formas
de cada componente), `informe.json`, capturas y una hoja de contacto por
pantalla. `--rapido` mide solo 390 y 1366 para las vueltas intermedias.

Lo que el script marca como **medida** (contraste, táctil, texto chico,
desborde, recortado, control nativo, glifo, imagen rota, consola, no carga,
foco invisible) está confirmado: se reproduce corriéndolo de nuevo. Lo que marca
como **sospecha** (solape, tema a medias, variantes, casi iguales, distinto por
sistema, mismo rótulo con distinta forma) se refuta mirando la captura antes de
arreglar. Los umbrales salen del adaptador; los de base son los de Apple.

### 3. Revisores en paralelo (criterio)

Los encargos están en `references/encargos.md`; las técnicas, en
`references/tecnicas.md`. Despachá **todos juntos, en un solo mensaje**, cada
uno con: su sección entera, la raíz, el `informe.md` de la medición, la carpeta
de capturas, el feature map y el contrato de salida de abajo.

| # | Revisor | Mira |
|---|---|---|
| 1 | Funciones | cada función del feature map, de punta a punta, como un usuario, con el dato guardado como prueba |
| 2 | Diseño y consistencia | las capturas contra Apple, las referencias del proyecto y entre sí: una sola forma por componente en toda la app |
| 3 | Controles, teclado y lectores | lo que dibuja el sistema y lo que no se puede hacer sin mouse |
| 4 | Textos | un nombre por cosa, concordancia, palabras del usuario y no del sistema |
| 5 | Estados límite y anchos | vacío, error, lento, desbordado, sesión vencida, entre breakpoints |
| 6 | Datos, permisos y seguridad | quién puede hacer qué, qué se pierde, qué se duplica, qué queda abierto |
| 7 | Web pública (solo si lo es) | Safari, rendimiento, cómo se comparte, conversión, imágenes |

Los que **cambian datos** (1, 5 y 6) trabajan cada uno con **su propia
instancia** y sus datos de prueba (el adaptador dice cómo levantar otra en otro
puerto). Dos agentes sobre la misma instancia se pisan.

Si el encargo es puntual, elegí los revisores que correspondan y decilo.

**Contrato de salida.** Cada hallazgo lleva:

- dónde: `archivo:línea`, o pantalla + ancho + tema, o selector;
- **qué le pasa a una persona**, en una frase, no qué regla se incumple;
- **la prueba**: número, salida de comando, captura con la ruta, dato leído;
- severidad propuesta con el criterio del paso 5, y si es gusto, decirlo;
- **dónde se arregla una sola vez** (componente, token, regla compartida) si
  aparece en más de un lugar.

Y una línea final: qué no pudo revisar y qué le faltó al encargo.

### 4. Refutar antes de aceptar

Ningún hallazgo se arregla por venir de un revisor. Por cada uno, intentá
demostrar que está mal: reproducilo, medilo vos, probá el caso contra la
instancia. Veredicto:

- **CONFIRMADO**: lo reprodujiste.
- **PLAUSIBLE**: el razonamiento se sostiene pero no se pudo reproducir. Va al
  informe; no se arregla a ciegas.
- **DESCARTADO**: se cae. Queda en el informe con el motivo.

Una afirmación sobre cómo se comporta el navegador se prueba en el navegador
antes de escribirla. Esto existe porque una vez se reportó como lo más grave de
una revisión algo que era falso (ver el caso del label en `encargos.md`, 3).

### 5. Ordenar por lo que cuesta

1. **Le cuesta al usuario.** No funciona, no se entiende, pierde o duplica
   datos, deja hacer lo que no debería, se ve roto donde se va a usar.
2. **Delata falta de oficio.** Funciona pero se nota: controles de fábrica,
   valores casi iguales, un botón distinto en cada sistema, textos con dos
   nombres, lo que rompe las reglas de Apple o del proyecto.
3. **No lo nota nadie.** Se arregla si sale barato; si no, al informe.

Lo que es gusto va aparte. En modo acompañado no se toca; en modo noche se
decide con las reglas y queda anotado como decisión, con la captura de antes.

### 6. Arreglar, en el lugar que vale para todo

- **Primero la causa compartida.** Si el mismo defecto está en tres pantallas,
  se arregla el componente, el token o la hoja común. Si cada sistema tiene su
  propia versión del componente, se unifican en una sola compartida y los
  sistemas pasan a usarla. El objetivo es que no pueda volver a divergir.
- **Rediseño.** Cuando arreglar de a uno no alcanza (una pantalla confusa, una
  jerarquía que no se lee, cinco formas de botón), se rediseña con
  `references/hig.md` y las referencias del proyecto, aplicando la misma
  solución en todos los sistemas. Antes y después quedan en capturas.
- Un commit por tema, con el mensaje explicando **qué le pasaba a la persona**.
- **Después de cada tanda, volvé a medir todo**, no solo lo tocado: un arreglo
  en un componente compartido se nota en pantallas que nadie miró. Y corré los
  tests y las funciones del feature map que pasan por lo cambiado.
- Repetí 2-6 hasta que los cajones 1 y 2 estén vacíos o se llegue al tope del
  adaptador (`"vueltas"`, por defecto 5). Lo que quede va al informe con el
  motivo.

### 7. Fijar: que no pueda volver

Por cada clase de defecto confirmada, en este orden, la primera que funcione:

1. **Estructura**: un solo componente o token, borrar la versión vieja que un
   agente copiaría.
2. **Un chequeo que falla**: si sirve para cualquier app, en
   `scripts/medidas.js` de esta skill; si es del proyecto, en sus tests o su
   lint, con un mensaje que diga cómo se arregla.
3. **Un test** del comportamiento.
4. **Texto**: una línea en el encargo o en `reglas.md`, solo si necesita
   criterio.

Probá que el chequeo nuevo **falla con el defecto real** antes de darlo por
bueno.

### 8. Informe y aprender

- Escribí `docs/revision-<fecha>.md` con `assets/plantilla-informe.md`, con
  capturas de antes y después de cada cambio visible y la lista **"para tu
  ojo"**: lo que necesita a la persona, en orden de importancia.
- Respondé las cinco preguntas, con nombre y apellido:
  1. **Escapes**: por cada uno, qué revisor o chequeo debió cazarlo y qué línea
     o qué chequeo lo caza ahora.
  2. **Falsos positivos**: qué encargo o chequeo los indujo.
  3. **Chequeos dormidos**: los que no dispararon acá ni en las dos corridas
     anteriores de la bitácora. Al tercero, se borran con constancia.
  4. **Técnicas nuevas**: lo que hubo que averiguar a mano.
  5. **Revisores flojos**: quién entregó poco, y qué le faltaba al encargo.
- **Aplicá los cambios, no los propongas.** Cada aprendizaje va a uno de dos
  lugares:
  - **sirve para cualquier app** → esta skill (`medidas.js`, `encargos.md`,
    `tecnicas.md`, `hig.md`), con la marca `[caso real, <proyecto>]`;
  - **es de este proyecto** → `.claude/revision/reglas.md` del proyecto, en la
    tabla regla / qué la hace cumplir.
- Una corazonada no es un chequeo: va a la bitácora como hipótesis y espera a
  repetirse.
- Agregá la entrada a `references/bitacora.md`. Si se editó la skill de forma
  importante, corré sus evals (`evals/playbook.md` en el repo de la skill).

## Criterio de salida

- La medición corrió entera y la última vuelta está en el informe.
- Los revisores entregaron, o está escrito cuáles no y por qué.
- Todo hallazgo tiene veredicto. Ninguno quedó en "habría que ver".
- Los cajones 1 y 2 están vacíos, o lo que queda tiene motivo escrito.
- Los tests pasan y hay más que al empezar; las funciones del mapa andan.
- Ningún componente tiene más formas que las que el adaptador permite, y
  ninguno cambia según el sistema.
- El paso 8 está hecho: la bitácora tiene la entrada y la skill o el adaptador
  cambiaron, aunque sea para borrar algo. Una corrida que no cambió nada casi
  siempre es una corrida en la que no se miró.
