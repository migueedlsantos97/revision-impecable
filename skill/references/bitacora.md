# Bitácora

Una entrada por revisión, la más nueva arriba. Es la memoria de la skill entre
proyectos y la materia prima del paso 7.

La medida de si la skill funciona no es cuántos hallazgos trajo. Es **cuántos
escapes hubo**: defectos que alguien encontró después de que la revisión dijo
"listo". Esa es la nota. Si baja corrida tras corrida, la skill está aprendiendo.

## Formato

```markdown
## <fecha> — <proyecto>

- **Alcance**: revisores que corrieron (o "los once").
- **Hallazgos**: N confirmados, N plausibles, N descartados. Por cajón: N / N / N.
- **Escapes de la corrida anterior**: N. Uno por línea, con qué encargo debió cazarlo.
- **Cambios a la skill**: qué se agregó, qué se afinó, qué se borró. Con el archivo.
- **Hipótesis**: corazonadas sin evidencia suficiente todavía. Esperan repetirse.
- **Checks dormidos**: los que no dispararon. Al tercero seguido, se borran.
```

## Reglas para escribir acá

- **Con nombre y apellido.** "Faltó revisar el foco" no sirve. "El encargo 4 no
  decía que un botón dentro de un label dispara el label" sí.
- **Una corazonada no es un check.** Va a Hipótesis y espera a que se repita en
  otro proyecto. Si aparece dos veces, se convierte en línea de encargo.
- **Los checks dormidos se borran.** Tres corridas sin disparar y afuera, con
  constancia de por qué. La skill se vuelve inútil por larga mucho antes que por
  corta. Si el check vuelve a hacer falta, vuelve con evidencia.
- **Un escape vale más que diez hallazgos.** Es lo único que dice dónde está el
  agujero real del procedimiento.

---

## 2026-09-26 — Proyecto 1 (salón de eventos)

Segunda corrida completa. La primera con datos sembrados y midiendo en el ancho
real del telefono de quien revisa el trabajo.

- **Alcance**: los once.
- **Hallazgos**: 61 confirmados, 9 plausibles, 3 descartados. Por cajon: 14 / 29 / 18.
- **Escapes de la corrida anterior**: **4**, contra 1 de la vez pasada. La nota
  empeoro, y el motivo es claro: entre una corrida y la otra se agrego el panel
  entero y se toco el sitio en 30 commits. Los cuatro escapes:
  - Dos controles nativos en el panel (encargo 2). No faltaba el check: el test
    comprobaba 9 tipos en el sitio publico y 2 en el panel. **Una asimetria
    entre superficies es un agujero, aunque las dos esten cubiertas.**
  - El footer de 866px contra 812 de pantalla (encargo 7). El encargo pedia
    desborde horizontal y nadie penso en el vertical.
  - Un icono a 54x54 en la pantalla de acceso (encargo 8). Esta `hidden`: el
    revisor nunca la renderizo.
  - `UYU 0` en Android (ningun encargo). No existia el concepto de "dato que
    cambia segun los datos regionales del aparato".
- **Lo que encontro que nadie habia visto**: un arreglo propio de la moneda
  quedo a mitad -el separador de miles seguia en Intl-; las reglas de cache
  volvieron a chocar con /vendor por la misma causa que ya se habia arreglado en
  /assets; los puntos del calendario puestos ese mismo dia eran indistinguibles
  a 1,03:1; el panel guardaba la fecha de la senia en UTC; la casilla obligatoria
  solo se pintaba con :has(); y "Como llegar" abria una busqueda de Google.
- **Falsos positivos**: 3, los tres refutados con prueba. Dos los refuto **el
  propio revisor que los levanto**, uno con fontTools y otro midiendo los
  contenedores. El tercero se refuto con un control de sanidad previo, porque
  el navegador congelaba el foco y sin el control la medicion habria mentido en cualquier direccion.
- **Cambios a la skill**:
  - `encargos.md` 3: medir los literales que comparten caja con un token variable
    contra los cinco valores del token.
  - `encargos.md` 4: un control propio hereda la obligacion de anunciar su valor.
  - `encargos.md` 6: listar todo `Intl`/`toLocale*` y decir si el texto exacto importa.
  - `encargos.md` 7: medir el alto de cada bloque contra el viewport, no solo el ancho.
  - `encargos.md` 8: renderizar todo lo que arranca `hidden`; sembrar el estado.
  - `encargos.md` 10: seguir cada enlace saliente hasta su URL final con `curl -sLI`.
  - `tecnicas.md`: el estado vacio esconde la mitad de los errores; los anchos de
    prueba se preguntan, no se eligen; los datos regionales cambian segun el aparato.
- **Hipotesis**: que **el revisor mas util es el que revisa lo que toco quien
  revisa**. Cinco de los diez hallazgos del primer cajon eran codigo escrito ese
  mismo dia, incluidos dos arreglos propios incompletos. La corrida anterior
  no tenia este patron porque revisaba codigo viejo. Si se repite en un tercer
  proyecto, corresponde un encargo nuevo: "lo que cambio en los ultimos N commits".
- **Checks dormidos**: `type=color`, `type=file`, `<datalist>`, `type=week` y
  `<progress>`/`<meter>` no dispararon **ni esta corrida ni la anterior**. Van a
  la tercera. Si en la proxima siguen mudos, se borran de `NATIVOS`.

## 2026-09-23 — Proyecto 1 (salón de eventos)

Primera corrida del procedimiento completo. Once revisores, dos rondas.

- **Alcance**: los once.
- **Hallazgos**: 38 confirmados, 4 descartados. Por cajón: 7 / 9 / 22.
- **Escapes de la corrida anterior**: 1, el globo de validación nativo. Ya
  incorporado al encargo 2 en la corrida pasada, así que esta vez no hizo falta
  tocar nada por él.
- **Lo que encontró que nadie había visto**: una pestaña del panel rota por un
  `ReferenceError` introducido tres commits antes por la propia pasada de
  textos; el error crudo del parser de JSON mostrado al cliente al enviar; el
  titular del hero en celular a 1,64:1; la palabra de acento de cada titular de
  sección a 1,61:1; el chevron de los `<select>` declarado y nunca pintado.
- **Falsos positivos**: 4. El más instructivo lo reportaron **dos revisores
  distintos con la misma prueba equivocada**: `curl` sin cabeceras de navegador
  no ve el script que el borde inyecta. Otro revisor **refutó su propio
  encargo** midiendo en el navegador: deshabilitar un control enfocado no
  pierde el foco en Chrome, y al caer a `<body>` el Tab no reinicia desde el
  tope.
- **Cambios a la skill**:
  - `SKILL.md`: la ronda B se despacha en dos tandas, porque cinco revisores
    comparten un solo navegador y chocaron en vivo.
  - `encargos.md` 4: corregida la afirmación sobre el foco al deshabilitar, que
    era falsa; agregado anunciar el éxito de una acción y no solo el error.
  - `encargos.md` 5: correr los tests después de la pasada y decir qué archivos
    no cubren.
  - `encargos.md` 9: pedir las cabeceras de caché.
  - `encargos.md` 10: verificar que exista un aviso cuando entra un lead.
  - `tecnicas.md`: `curl` sin cabeceras de navegador no ve la inyección del
    borde; el contraste sobre foto se mide sobre las cajas reales del texto.
- **Hipótesis**: que el valor del procedimiento está sobre todo en los encargos
  que nunca se corrieron antes. Cinco de los siete hallazgos del primer cajón
  salieron de estados límite, rendimiento y arte, que no existían en la corrida
  anterior. Falta un tercer proyecto para saber si se sostiene.
- **Checks dormidos**: ninguno. Es la segunda corrida; la poda empieza a la
  tercera.

## <fecha> — Proyecto 1 (salón de eventos)

Entrada cero: la revisión que originó la skill. Se corrió a mano, sin el
procedimiento todavía escrito, así que sirve de línea de base.

- **Alcance**: tres revisores en paralelo (textos, consistencia visual,
  accesibilidad) más revisión propia. No existían todavía los encargos de
  rendimiento, Safari, estados límite, conversión ni dirección de arte.
- **Hallazgos**: el botón de privacidad dentro del label del consentimiento, los
  chips de la agenda inalcanzables con teclado, el anillo de foco borrado en los
  campos de texto, nueve grises por debajo de 4,5:1, el formulario de bloqueo
  del panel mandando valores que la API no acepta, "Setiembre De 2026", quince
  radios distintos, cinco grosores de trazo, y el footer estrangulado entre 761
  y 920px.
- **Escapes de la corrida anterior**: no aplica, es la primera.
- **Falso positivo aceptado sin refutar**: **1**, y es el peor error de la
  corrida. Un revisor afirmó que un botón dentro del `<label>` marcaba o
  desmarcaba la casilla. Se dio por bueno, se reportó como el hallazgo más grave
  y recién se probó días después: el navegador no dispara el label para
  descendientes interactivos, así que la casilla nunca se movía. El arreglo igual
  correspondía, pero por el nombre accesible, que es bastante menos dramático.
  Es exactamente lo que el paso 3 existe para evitar, y ocurrió antes de que el
  paso 3 estuviera escrito.
- **Escapes de esta corrida**: **1**. El globo de validación nativo del
  navegador. Lo encontró el cliente mirando una captura, después de que la revisión
  se dio por cerrada. Ningún encargo hablaba de controles de validación, y el
  encargo 2 solo listaba los controles de formulario más obvios.
- **Cambios a la skill**: se creó entera. El escape se incorporó como línea
  propia en el encargo 2 y se sumó el caso al encargo 4, porque tenía una
  segunda cara: desde que la casilla se dibuja con un input de 1px escondido, el
  globo del navegador ya no tenía dónde anclarse.
- **Hipótesis**: que el entorno de verificación miente más de lo que parece. La
  pestaña del navegador integrado congela animaciones, `getComputedStyle` y los
  `IntersectionObserver` cuando la ventana no está al frente, y eso hizo
  sospechar de tres bugs que no existían. Ya está en `tecnicas.md`; falta
  confirmar en otro proyecto si aparecen trampas parecidas.
- **Checks dormidos**: ninguno todavía.
