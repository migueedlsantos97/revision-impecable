# Encargos de los once revisores

Cada sección se le pasa **entera** a un revisor, junto con la raíz del proyecto,
la URL del sitio andando si es de la ronda B, y el contrato de salida de
`SKILL.md`. Las técnicas que varios comparten están en `tecnicas.md`.

Regla común a todos: **traer la prueba**. El número calculado, la salida del
comando, el selector que no matchea. Un hallazgo sin prueba es una opinión.

**Procedencia.** Los checks que entraron por un escape llevan la marca
`[de <proyecto>]`. No es decoración: dice que esa línea existe porque una vez se
pagó por no tenerla, y que borrarla tiene un costo conocido. Los checks sin
marca son los de origen y se juzgan solo por si disparan.

---

## Ronda A — sobre el código

### 1. Consistencia visual

Lo que más delata un sitio hecho sin cuidado son quince valores donde debería
haber cinco. Contalos antes de mirar nada (ver `tecnicas.md`, "Inventario").

Buscá:

- **Radios, grosores de trazo, tamaños de fuente, espaciados y colores** con más
  de cinco o seis valores distintos. Dos valores a uno o dos píxeles de
  distancia no son dos decisiones, son una decisión olvidada.
- **Excepciones sin motivo escrito.** Un ícono rotado se difumina y pide más
  trazo; una estrella de seis puntas se empasta y pide menos. Si no podés
  escribir el motivo, no es excepción: es descuido.
- **[caso real] Si el sitio tiene temas, variantes o modos, cambialos y mirá
  qué NO cambia.** El defecto típico no es que falte el token: es que el token
  existe, lo usan treinta reglas, y otras trece tienen el valor base escrito a
  mano. El tema se aplica a medias y el resultado se ve peor que si no hubiera
  tema, porque la mitad de la pantalla contradice a la otra. La técnica está en
  `tecnicas.md`, "Lo que no cambia al cambiar el tema".
- **[caso real] Un token derivado se declara donde vive el valor del que
  depende.** Si el tema redefine `--accent` en `body` y vos declarás
  `--tinte: color-mix(..., var(--accent), ...)` en `:root`, esa mezcla resuelve
  con el `--accent` de `:root`, que es siempre el base. El token existe, no da
  error, y el tema no llega nunca.
- **Pares que conviven.** Dos botones flotantes que ocupan el mismo lugar de la
  pantalla y se turnan tienen que ser el mismo botón, no uno tinta y otro
  violeta. Lo mismo con dos tarjetas hermanas, dos estados de un control, dos
  encabezados del mismo nivel.
- **Radios que no son lo que dicen ser.** Un radio de 40px en un control de 50px
  de alto no es una pastilla; es un rectángulo con las esquinas muy comidas.
- **Nesting de radios.** El radio interior tiene que ser menor que el exterior
  menos el padding, o la curva se ve torcida.

Proponé la escala corta que reemplaza a lo que encontraste, y a qué valor va
cada caso.

### 2. Controles del sistema operativo

Es la revisión que más rinde y la que casi nadie hace. Cada uno de estos lo
pinta el navegador o el sistema, cambia entre máquinas y rompe la paleta.

| Qué | Cómo se resuelve |
|---|---|
| Barra de desplazamiento | `scrollbar-width` + `scrollbar-color`, y `::-webkit-scrollbar*` de respaldo |
| Globo de validación ("Completa este campo") **[caso real]** | `novalidate` en el form, `checkValidity()`, escuchar `invalid` con `preventDefault()` y pintar el mensaje propio. Lo escribe el navegador en su idioma y sin voseo, cambia de forma en cada uno, y en el celular queda fuera de pantalla |
| Casillas y radios | input escondido (`position:absolute;opacity:0;width:1px`) y la caja en un `::before` del label; el foco delegado con `:has(input:focus-visible)` |
| Flecha del `<select>` | `appearance:none` + chevron SVG por `background-image` |
| Rectángulo azul al tocar en Android | `-webkit-tap-highlight-color:transparent` |
| Amarillo del autorrelleno de Chrome | `input:-webkit-autofill{box-shadow:0 0 0 40px <fondo> inset}` |
| Anillo de foco | `:focus-visible` propio, con `outline-offset` para que caiga sobre el fondo y no sobre el relleno |
| Triángulo de `<summary>` | `list-style:none` + `::-webkit-details-marker{display:none}` |
| Selección de texto y cursor | `::selection` y `caret-color` |
| Viñetas de listas de layout | `list-style:none` |
| Glifos Unicode como íconos (✦ ★ ☰ ✓) | pasarlos a SVG: caen fuera del subset de la fuente y los resuelve el sistema, así que se ven distinto en Windows, Mac y Android |
| Resaltado de `::-webkit-search-cancel-button`, spinners de `number`, ícono de `date` | estilarlos o elegir otro tipo de control |

Mirá también **la fuente de respaldo**: si la familia declarada no carga, ¿con
qué se ve? Una pila que termina en `serif` a secas deja el sitio en Times.

### 3. Contraste y color

Nunca digas "se ve bien". Calculá la razón con la fórmula de luminancia relativa
de WCAG (ver `tecnicas.md`) para **cada** color de texto contra **su fondo
real**, que muchas veces es el de la tarjeta y no el de la página.

- Texto normal 4,5:1. Texto grande (24px, o 19px en negrita) 3:1.
- Bordes y límites de controles 3:1, pero solo cuando el borde es lo único que
  dice dónde empieza el control. Si el relleno ya lo distingue, no aplica.
- **Un cambio de estado se juzga contra su estado anterior**, no contra el
  fondo. Un borde que pasa de gris claro a gris medio puede dar 2,8:1 entre sí y
  ser invisible aunque cada uno pase contra el fondo.
- Los créditos obligatorios por licencia (OpenStreetMap y similares) suelen
  quedar en gris casi invisible y tienen que leerse.
- Cuando no llegue, **bajá la luminancia del mismo tono**, no cambies el color.

Revisá también el texto sobre foto: ahí el fondo varía por píxel y hay que
mirar el peor punto, no el promedio.

### 4. Teclado, foco y lectores

- Recorré con Tab. **Toda acción que se hace con el mouse tiene que poder
  hacerse con teclado.** Un `<span onclick>` dentro de un `<button>` no es
  focusable y no responde a Enter.
- **El foco nunca se puede perder** — pero medí antes de afirmarlo.
  **[caso real]** Este encargo decía que deshabilitar un control enfocado tira
  el foco a `<body>` y que el Tab siguiente reinicia desde el tope. Un revisor
  lo midió en Chrome 152 y es falso: `disabled` y `hidden` conservan el foco, y
  al caer a `<body>` el navegador guarda el punto de partida secuencial. Los dos
  casos que **sí** lo pierden son **quitar del DOM el nodo enfocado** y
  **deshabilitar un `<fieldset>` que lo contiene**. Buscá esos dos: listas que
  se redibujan enteras con el foco adentro, diálogos que recalculan sus botones
  después de una acción, y el fieldset del botón de enviar. Movelo antes.
- **[caso real] Anunciá también el éxito, no solo el error.** Una acción que
  cambia el estado y solo avisa cuando falla deja a quien no ve la pantalla sin
  saber si pasó algo. Es el agujero más caro en un panel que se usa a diario.
- Ningún anillo de foco puede quedar tapado por un degradado, una viñeta o un
  elemento por encima.
- Los errores van con `aria-invalid` en el campo y `aria-describedby` al
  mensaje. Un texto suelto al final del formulario no dice cuál campo falló.
- Una región viva (`role="status"` / `role="alert"`) tiene que estar **en el DOM
  antes** de escribirle el texto. Escribir con `hidden` puesto y recién después
  mostrarla no anuncia nada. Y usá `setTimeout`, no `requestAnimationFrame`: en
  una pestaña de fondo el frame nunca llega y el aviso queda vacío.
- `role="grid"` exige `grid > row > gridcell`. Si no hay filas, sacá los roles:
  una lista de días es una lista.
- El nombre accesible de una casilla envuelta en `<label>` es **todo** el texto
  del label. Un botón anidado le pega su texto al control: "Acepto que reciban
  estos datos para responder mi consulta. Cómo usamos tus datos" se anuncia como
  una sola frase, y quien no ve la pantalla no sabe que ahí hay un botón.
- **[caso real] Cuidado con la versión exagerada de ese hallazgo.** Un revisor
  afirmó que además el botón *marcaba o desmarcaba la casilla*, por estar dentro
  del label. Es falso: el navegador no dispara la activación del label cuando el
  clic cae en un descendiente interactivo, y un `<button>` lo es. Se aceptó sin
  reproducirlo y se reportó como el hallazgo más grave de la revisión. Una
  afirmación sobre comportamiento del navegador se prueba en el navegador, en
  dos líneas, antes de escribirla.
- **[caso real]** Si escondiste el input nativo para dibujar tu propia
  casilla, el globo de validación del navegador se queda sin dónde anclarse: no
  puede apuntar a un elemento de 1px. Esconder un control obliga a hacerse cargo
  de todo lo que el navegador dibujaba sobre él.
- Nombres accesibles: el texto de un botón anidado se concatena al del control
  que lo contiene.
- `<th>` con `scope`. Listas de características como `<ul>`, no como `<div>` de
  `<span>` con un separador en `::before`.

### 5. Textos y nomenclatura

- **Un nombre por cosa**, en toda la superficie. Revisá interfaz, mensajes
  salientes (WhatsApp, mail) y panel de administración **juntos**. Si en la
  tarjeta dice "Sólo el espacio" y en el WhatsApp dice "Sólo salón y patio", son
  dos nombres para lo mismo.
- **Concordancia de número.** "1 invitados", "1 servicios elegidos". Buscá toda
  concatenación de un número con un sustantivo.
- Nada de jerga de sistema en la cara del usuario: "registro web", "formato
  inválido", "realiza cobros", "operación exitosa".
- Los `alt` describen la escena, no el tipo de archivo. "Referencia visual de
  ambientación cálida" no es un alt.
- **Los valores de los `<option>` tienen que ser exactamente los que acepta el
  servidor.** Un desplegable que manda `todo` contra una API que espera `todos`
  deja una operación rota y un mensaje de error que nombra valores que no
  existen en la pantalla. Comparalos uno por uno contra el validador.
- `text-transform:capitalize` pone mayúscula en cada palabra, también en las
  preposiciones: "Setiembre De 2026". Capitalizá la primera letra en el código.
- Ortografía vigente: "solo" sin tilde, comillas y guiones correctos, sin comas
  empalmadas.
- **Datos de contacto**: la dirección, el teléfono y el nombre tienen que ser
  carácter por carácter los mismos en la página visible, en los datos
  estructurados y en el perfil de Google. La consistencia es lo que pesa en el
  paquete local.
- Promesas que el cliente no confirmó (horarios, qué incluye, plazos) no van.
- **[caso real] Corré los tests al terminar y decí qué archivos no cubren.** Una
  pasada de textos anterior cambió `x.guest_count` por la versión con
  concordancia y se equivocó de variable: dejó una pantalla entera del panel
  rota, con un `ReferenceError`, y vivió tres commits porque ninguna prueba toca
  el render de esa pantalla.

### 6. Compatibilidad y Safari

Casi todo se prueba en Chromium y ahí está el agujero. Revisá en el código qué
depende de lo que Safari resuelve distinto o tarde:

- `:has()`, `@container`, `:is()` anidado, `text-wrap:balance`.
- `<dialog>` y `showModal()`, `::backdrop`, `backdrop-filter`.
- `env(safe-area-inset-*)` y `100dvh` en iPhone con la barra de direcciones.
- `scrollbar-color` (no lo soporta) frente a `::-webkit-scrollbar` (sí).
- `inert`, `popover`, `toggleAttribute` con segundo argumento.
- Formatos de imagen y de fuente, y `font-display`.
- `Intl.DateTimeFormat` con zonas horarias y `timeZone:'UTC'`.
- Prefijos que faltan: `-webkit-` en lo que todavía lo pide.

Para cada dependencia decí si hay respaldo y qué se ve si falla. Marcá lo que
solo se puede confirmar en un iPhone real.

---

## Ronda B — sobre el sitio andando

### 7. Anchos y reflujo

Probá 360, 390, 768, 860, 1024, 1280 y 1440. En cada uno, el script de desborde
de `tecnicas.md`.

- El hueco típico **no está en el móvil**, que siempre se prueba, sino **entre
  breakpoints**: una grilla de cuatro columnas que a 1280 respira y a 860 deja
  una columna de 98px con la dirección partida en seis líneas.
- Probá también **poca altura**: 1366×720 y 1536×735. Un hero de alto fijo se
  pisa con el contenido.
- `overflow-x:clip` en el `body` además de recortar impide el desplazamiento
  programático: cualquier desborde futuro se vuelve contenido inalcanzable. Usá
  `hidden` o arreglá la causa.
- Alturas fijas (`min-height` en px) revientan con texto ampliado. Probá zoom de
  texto al 200% y espaciado de texto.
- Palabras largas sin espacios y nombres de cuarenta caracteres.

### 8. Estados límite

Cada pantalla tiene más de un estado y normalmente solo se diseñó el feliz.
Forzá y mirá:

- **Vacío**: sin resultados, sin datos, primera vez.
- **Cargando**: ¿hay señal? ¿salta el layout cuando llega el contenido?
- **Error de red**: cortá la conexión o la API y mirá qué dice y si se puede
  seguir.
- **Lento**: 3G simulado. Lo que carga perezoso, ¿avisa o parece roto?
- **Desbordado**: textos larguísimos, muchos elementos, el máximo permitido.
- **Doble envío**, envío con el formulario a medias, vuelta atrás del navegador
  después de enviar.
- **Sin JavaScript**: ¿hay `<noscript>` y dice algo útil?
- Si hay panel privado: qué pasa al vencer la sesión con el formulario abierto.

### 9. Rendimiento

- Peso total de la primera carga, y qué pesa más. Fuentes, imágenes y bundles
  de 3D son los sospechosos.
- Imágenes: formato, tamaño servido contra tamaño mostrado, `width`/`height`
  puestos para no saltar el layout, `loading="lazy"` donde corresponde.
- Fuentes: subset, `font-display`, cuántos archivos.
- **Lo pesado en gama baja.** Una escena 3D o un mapa pueden ser insufribles en
  un celular viejo, que es justo el del público. Si no se puede medir en uno
  real, decilo y proponé el límite (por ejemplo, no cargar la escena por debajo
  de cierto ancho o con `prefers-reduced-motion`).
- **[caso real] Las cabeceras de caché.** Un sitio puede pesar poco y aun así
  hacer trece viajes de ida y vuelta en cada visita. Pedí `Cache-Control` de
  cada recurso: el default de varias plataformas es `max-age=0,
  must-revalidate`, que obliga a revalidar hasta las fuentes y las fotos que
  nunca cambian.
- Peticiones a terceros: cuántas, a quién, y si el sitio funciona sin ellas.
- `preload` que no se usa dentro de los primeros segundos es peso al pedo y
  además avisa por consola.

### 10. Conversión, SEO y cómo se comparte

Mirá la página como quien llega por primera vez y tiene que decidir.

- ¿La primera pantalla dice **qué es, dónde queda y qué hacer**? ¿El llamado a
  la acción está donde cae el ojo?
- ¿Cuántas veces se repite el mismo llamado? Siete veces el mismo botón lo
  vacía de sentido.
- **Cómo se ve el link al compartirlo**, sobre todo por el canal que usa el
  negocio. Comprobá la imagen y el texto de Open Graph con el tamaño real, y que
  las URLs sean absolutas y del dominio definitivo.
- `canonical`, `og:url`, `robots.txt` y `sitemap.xml` apuntando al dominio real.
- `noindex` puesto o sacado según corresponda al momento, y dicho explícitamente
  en el informe.
- Datos estructurados que validen, **sin marcar reseñas de terceros como
  propias**: está prohibido por la política de Google y es motivo de acción
  manual.
- Título y descripción que nombren categoría y lugar, que es lo que se tipea.
- ¿Lo que se quiere medir se está midiendo? Si hay analítica, comprobá que
  carga y que no la bloquea la política de seguridad. **Ojo con la prueba**: ver
  `tecnicas.md`, "Lo que `curl` no ve".
- **[caso real] ¿Alguien se entera cuando entra un lead?** El encargo miraba el
  embudo hasta que la persona envía, y el punto más caro estaba después: una
  consulta que se guarda y no le avisa a nadie muere si el dueño no abre el
  panel. Justo la que el diseño quería rescatar.

### 11. Dirección de arte

Las imágenes suelen ser la parte más débil y nadie las revisa **como conjunto**.

- ¿Se ven de la misma familia? Temperatura, luz, encuadre, grano.
- ¿Alguna desentona tanto que parece de otro sitio?
- ¿Se nota que son de stock o de demo? Si son provisorias, decilo en el informe
  con qué foto real haría falta en cada lugar.
- Recortes: ¿qué se pierde en el recorte móvil? ¿queda una cara cortada?
- ¿El texto encima se lee en el peor punto de la foto?
- Orden y ritmo: ¿la galería cuenta algo o es una pila?
- Peso y resolución, contra el tamaño real en pantalla.

Este revisor termina con una lista concreta: qué foto falta y para qué lugar.
