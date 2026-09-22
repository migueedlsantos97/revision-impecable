# Revisión impecable — Salón de eventos

**Fecha**: 2026-09-22 · **Revisó**: Claude Code · **Estado del sitio**: preview con `noindex`

> Informe real, anonimizado. Es el primer proyecto donde se usó el procedimiento,
> todavía a mano y con solo tres revisores. Sirve para ver la forma del entregable
> y el tipo de hallazgo que sale.

## Resumen

Se revisó el sitio completo antes de mostrárselo a la dueña del salón. El
hallazgo más caro fue funcional y silencioso: el botón que abre la política de
privacidad vivía dentro del `<label>` de la casilla de consentimiento, así que
abrirlo la marcaba o la desmarcaba sin que se viera, en el único campo con peso
legal del formulario. Quedan tres decisiones de gusto a criterio del cliente y
una medición pendiente que necesita un teléfono de gama baja.

| | |
|---|---|
| Revisores que corrieron | 3 de 11 |
| Hallazgos confirmados | 41 |
| Descartados al refutar | 2 |
| Arreglados | 41 |
| Quedaron a criterio del cliente | 3 |
| Tests | 9 → 44 |
| Escapes de la revisión anterior | no aplica, primera corrida |

## Lo que le costaba la venta

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|
| Abrir "Cómo usamos tus datos" marcaba o desmarcaba el consentimiento, sin señal visible | `index.html:157` | CONFIRMADO | arreglado, el botón salió del label |
| Con teclado no había forma de abrir el detalle de una reserva: la celda abría "Bloquear fecha" | `admin/admin.js:222` | CONFIRMADO | los chips pasaron a ser botones |
| El formulario de bloqueo mandaba `todo` y `dia`; la API acepta `todos` y `dia`. La operación fallaba y el error nombraba valores que no existen en pantalla | `admin/admin.js` | CONFIRMADO | valores alineados contra el validador |
| El resumen contaba reservas canceladas como ingreso | `admin.js` | CONFIRMADO | filtrado por estado confirmado |
| Ningún error del panel se anunciaba: el texto se escribía con la región `hidden` y recién después se mostraba | `admin/admin.js:59` | CONFIRMADO | la región vive siempre en el DOM |

## Lo que parecía de principiante

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|
| Nueve colores de texto entre 2,79:1 y 4,20:1, incluido el placeholder que lleva el formato del teléfono | `configurator.css` | CONFIRMADO | mismo tono, luminancia bajada hasta 4,5:1 |
| El anillo de foco desaparecía en nombre, WhatsApp y notas: `.field input:focus` (0,2,1) le ganaba a `input:focus-visible` (0,1,1) con `outline:0` | `configurator.css:41` | CONFIRMADO | arreglado |
| Quince radios distintos, catorce a uno o dos píxeles entre sí | tres hojas de estilo | CONFIRMADO | escala de seis valores |
| Cinco grosores de trazo para el mismo ícono al mismo tamaño | `index.html` | CONFIRMADO | uno solo, con dos excepciones motivadas |
| Dos pastillas flotantes en el mismo lugar de la pantalla, una tinta y otra violeta | `configurator.css` | CONFIRMADO | unificadas |
| Entre 761 y 920px la dirección caía en 98px de ancho, partida en seis líneas junto a un mapa vertical | footer | CONFIRMADO | dos columnas en ese rango |
| El mes salía "Setiembre De 2026" por `text-transform:capitalize` | `admin.css` | CONFIRMADO | capitalización en el código |
| El pulgar del slider medía 25px en Chrome y 16px en Firefox | `configurator.css` | CONFIRMADO | parejo |
| Seis controles los dibujaba el sistema operativo: barra de desplazamiento, resaltado táctil de Android, autorrelleno de Chrome, flecha del select, dos casillas | varias | CONFIRMADO | todos reemplazados |
| El foco se perdía al deshabilitar el control que lo tenía, en tres lugares | `calendar.js`, `app.js` | CONFIRMADO | el foco se mueve antes |

## Lo que no nota nadie

- `role="grid"` sin `role="row"`: árbol ARIA inválido. Se sacaron los roles, es una lista.
- `<th>` sin `scope`, listas de características como `<div>` de `<span>`. Arreglado.
- Un `role="alert"` que nunca recibía texto. Eliminado.
- `overflow-x:clip` en el `body`, que además de recortar impide el desplazamiento programático. Pasó a `hidden`.

## Lo que quedó a criterio del cliente

- **El titular del hero.** Funciona, pero el círculo rotado compite con el nombre de marca. No lo toqué: es la voz del sitio.
- **El verde del botón de enviar.** Es el único color fuera de paleta de toda la página. Se justifica como señal de WhatsApp; también se puede llevar a la paleta.
- **Los verbos de los botones del panel.** Son correctos pero secos. Cambiarlos es preferencia, no error.

## Lo que se descartó

| Sospecha | Por qué se cae |
|---|---|
| El panel se podía alcanzar codificando el path en porcentajes | Se probó contra producción: responde 307 y después la guarda de 503. No hay bypass |
| Un `<details>` heredaba un gris sin contraste dentro del bloque oscuro | El bloque ya lo sobrescribe: 10,41:1. El revisor lo retiró él mismo |

## Lo que no se revisó

- **Rendimiento en gama baja.** La escena 3D nunca se midió en un teléfono viejo, que es justo el del público. Requiere un dispositivo real.
- **Safari en iPhone.** Todo se probó en Chromium. El sitio usa `:has()`, `<dialog>`, `backdrop-filter` y área segura, que es donde Safari rompe.
- **Estados límite, conversión y dirección de arte.** Esos encargos todavía no existían en esta corrida.

---

## Autoevaluación

**Escapes de la revisión anterior**

No aplica: primera corrida.

**Escapes de esta corrida: 1**

| Qué se escapó | Qué encargo debió cazarlo | Por qué no lo hizo | Qué línea lo caza ahora |
|---|---|---|---|
| El globo de validación del navegador, "Completa este campo". Lo encontró el cliente mirando una captura, después de darse la revisión por cerrada | Controles del sistema operativo | El encargo listaba los controles de formulario obvios y no incluía la validación | Fila propia en la tabla, marcada `[caso real]`, con `novalidate` + `checkValidity()` como solución |

Tenía una segunda cara que ningún encargo cubría: desde que la casilla se dibuja
con un input de 1px escondido, el globo del navegador ya no tenía dónde
anclarse. Esconder un control obliga a hacerse cargo de todo lo que el navegador
dibujaba encima. Eso entró como línea en el encargo de teclado.

**Qué cambió en la skill después de esta corrida**

- Agregado: la validación nativa como control del sistema; la consecuencia de
  esconder un control nativo; el desajuste entre valores de `<option>` y lo que
  acepta el servidor.
- Afinado: el encargo de contraste ahora pide juzgar un cambio de estado contra
  su estado anterior y no contra el fondo.
- Borrado: nada todavía, es la primera corrida.

**Hipótesis abiertas**

El entorno de verificación miente más de lo que parece. La pestaña del navegador
integrado congela animaciones, `getComputedStyle` y los `IntersectionObserver`
cuando la ventana no está al frente, y eso hizo sospechar de tres bugs que no
existían. Ya está documentado; falta confirmar si en otros entornos aparecen
trampas equivalentes.

**Dónde sigue siendo ciega**

Tres huecos, en orden de gravedad:

1. **No puede tocar un teléfono.** Todo lo que depende de un dispositivo real
   (Safari en iPhone, rendimiento en gama baja, gestos táctiles) queda en
   "plausible" y nunca llega a "confirmado".
2. **No ve lo que solo se nota en movimiento.** Una transición con la curva mal
   elegida, un salto de layout de 80 ms, un hover que llega tarde: nada de eso
   sale de leer el DOM.
3. **No juzga si la web vende.** El revisor de conversión mira estructura y
   claridad, pero si el mensaje convence o no lo dicen las consultas que
   entran, no una revisión.
