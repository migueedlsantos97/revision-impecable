# Encargos de los revisores

Cada sección se le pasa **entera** a un revisor, junto con la raíz del proyecto,
el `informe.md` de la medición, la carpeta de capturas, el feature map
(`.claude/revision/funciones/`), `cobertura.md` y el contrato de salida de
`SKILL.md`. Técnicas compartidas: `tecnicas.md`. Estándar de diseño: `hig.md`.
Números y anchos: `umbrales.md`. Los casos que originaron una regla están
anonimizados en `ejemplos/casos-reales.md` y se citan como `[caso real #n]`.

Reglas comunes:

- **Traer la prueba**: número calculado, salida de comando, captura con ruta,
  dato leído. Un hallazgo sin prueba es una opinión.
- **No repitas lo que ya midió el script** (`informe.md`): contraste calculado
  contra fondos planos, tamaño táctil, texto chico, desbordes, recortes, solapes,
  controles nativos visibles, glifos, foco invisible, tema a medias, variantes,
  y los chequeos de documento, imágenes, campos, estructura y red. Tu trabajo
  empieza donde el script no llega (criterio, funciones, estados forzados,
  lectura de código). Si una falla del script te parece falsa, decilo con la captura.
- **Dónde se arregla**: para todo hallazgo repetido, el componente, token o
  regla compartida que lo arregla una sola vez.
- **Un contexto de navegador propio** (perfil/contexto separado). Los que
  cambian datos, también instancia propia.
- **Idioma**: los encargos valen para cualquier idioma de interfaz; donde un
  punto depende del idioma (ortografía, capitalización) se dice.
- **Procedencia**: `[caso real #n]` marca una línea que existe porque una vez se
  pagó por no tenerla; borrarla tiene un costo conocido.
- **Cobertura**: anotá en tu salida a qué filas de `cobertura.md` aportás.

---

## 1. Funciones (y formularios, archivos, impresión)

Sos el tester. Recorrés **cada función del feature map** como la usaría una
persona, de punta a punta, con tu instancia y tus datos.

- Llegá como dice "Cómo se llega" (para cada rol), hacela y comprobá **el efecto
  real**: la fila en la base, el archivo generado, el mensaje que salió. Una
  pantalla que dice "Listo" con la base igual que antes es el peor defecto.
- Hacela **dos veces** y con **doble clic**: ¿se duplica? Volvé atrás con el
  navegador: ¿queda a medias?
- Deshacé, anulá, cancelá: ¿vuelve todo, incluido lo que tocó en otro sistema?
- Con un rol que **no** debería poder: ¿se ve el botón? ¿Y llamando la API directo?
- Lo que cruza sistemas: seguilo hasta el otro lado.
- Si el mapa o los datos de prueba no alcanzan, es un hallazgo del adaptador:
  decilo, no aflojes el recorrido. [caso real #37]
- Al terminar, corré los tests y decí qué funciones del mapa **no tienen test**.

### Formularios (tabla de casos fijos)
Para cada formulario, probá estos casos y anotá el resultado:

| Caso | Qué se espera |
|---|---|
| Enviar vacío | error por campo, foco al primer error, mensaje propio asociado (`aria-describedby`), sin globo del navegador |
| 1 carácter / solo espacios | validación coherente con el servidor |
| Máximo permitido y máximo + 1 | tope visible o error claro; no se corta en silencio |
| Emoji, acentos, comillas, `<script>`, nombres con apóstrofo | se guarda y se muestra igual, escapado |
| Pegar (incluido desde una hoja de cálculo) | respeta formato y límites |
| Enter con el foco en un campo | envía (o no) como espera la persona; nunca envía algo a medias |
| Doble envío | una sola operación; botón deshabilitado durante el envío |
| Volver atrás y recargar | no pierde lo escrito sin avisar (`beforeunload` si hay cambios), no reenvía solo |
| Autocompletado y gestor de contraseñas | `autocomplete` correcto (`email`, `current-password`, `one-time-code`...), `type` e `inputmode` adecuados |
| Obligatorio | indicado antes de enviar, no solo con el error |
| Error del servidor tras enviar | el mensaje conserva lo escrito y dice qué hacer |

### Subida y descarga de archivos
Archivo vacío, sin cabecera, con otro separador y codificación, más largo que
los topes del servidor, nombre con espacios/unicode, mismo archivo dos veces,
tipo no permitido, cancelar a mitad, progreso visible, quitar el archivo
elegido. Si el cliente valida menos que el servidor, la vista previa dice
"listo" y el envío falla. [caso real #19] Descargas: abrir el archivo generado y
leerlo (CSV con tildes en una hoja de cálculo, PDF con todas las páginas).

### Impresión y exportes
Si el mapa lista imprimir/exportar o hay `@media print`: abrir la vista previa de
impresión (o `emulateMedia('print')`), comprobar que no se cortan tablas ni
títulos huérfanos, que se ocultan navegación y botones, que el contraste
sobrevive en blanco y negro y que los enlaces o códigos necesarios se ven. Un
exporte se abre y se compara contra lo que muestra la pantalla.

## 2. Diseño y consistencia

Sos el diseñador. Mirás **las capturas** (abrilas, no alcanza con números)
contra `hig.md`, las referencias del proyecto y **entre sí**: la misma cosa se
ve igual en todas las pantallas y sistemas.

Empezá por "Formas de cada componente" del `informe.md`: cada componente con más
de una forma es una decisión olvidada. Elegí la forma que queda (la de las
referencias o la más usada que cumpla con `hig.md`), decí a qué valor va cada
caso y **en qué archivo compartido se fija**. Después, la pasada de criterio de
`hig.md` pantalla por pantalla. Si no se arregla de a un detalle, proponé el
rediseño con la misma solución para todas las parecidas.

Inventario (ver `tecnicas.md`, "Inventario de valores"): radios, trazos,
tamaños de fuente, espaciados y colores con más de cinco o seis valores. Dos
valores a 1-2 px son una decisión olvidada.

- **Excepciones sin motivo escrito.** Si no podés escribir el motivo, es descuido.
- **Si hay temas o modos, cambialos y mirá qué NO cambia** (valores base escritos
  a mano). [caso real #2] Técnica en `tecnicas.md`.
- **Un token derivado se declara donde vive el valor del que depende.** [caso real #3]
- **Pares que conviven** (dos botones flotantes que se turnan, tarjetas
  hermanas, encabezados del mismo nivel) son el mismo componente.
- **Radios**: un radio que no es lo que dice ser (pastilla de verdad o no) y
  radio interior = exterior − relleno.
- **Una excepción de trazo que no hace nada**: buscá `stroke-width` en el CSS y
  en el sprite a la vez. [caso real #4]
- **Contraste que el script no calcula** (fondos con degradado, foto, estados):
  calculá la razón WCAG (`tecnicas.md`) contra el **fondo real**. Un cambio de
  estado se juzga contra su estado anterior. Texto sobre foto: el peor punto,
  no el promedio. Los créditos obligatorios por licencia tienen que leerse.
  Cuando no llegue, bajá la luminancia del mismo tono. Cada literal que
  comparte caja con un token variable se mide contra todos sus valores. [caso real #5]
- **Tablas grandes: sembrá volumen.** 0, 1, 50 y 10 000 filas (si el producto
  lo admite): cabecera fija, orden y filtro que no se pierden al paginar,
  scroll horizontal con la primera columna visible, columnas largas truncadas
  con acceso al texto completo, selección múltiple y acciones en lote, tiempo de
  render. Una tabla de 10 000 filas que congela la pestaña es un hallazgo del cajón 1.
- **Gráficos.** El color no es la única señal (patrón, etiqueta o forma);
  equivalente en tabla o texto; contraste de cada serie contra el fondo;
  leyenda; tooltip alcanzable con teclado; casos de datos vacíos, un solo
  punto, valores negativos, escala truncada que exagera, series con 20+ puntos
  y nombres largos.

## 3. Controles, teclado y lectores

El script marca los controles de fábrica visibles, campos sin nombre y foco que
no se ve; vos revisás el resto de lo que pinta el sistema y todo lo que no se
puede hacer sin mouse.

| Qué | Cómo se resuelve |
|---|---|
| Barra de desplazamiento | `scrollbar-width`/`scrollbar-color` y `::-webkit-scrollbar*` de respaldo |
| Globo de validación del navegador [caso real #38] | `novalidate`, `checkValidity()`, escuchar `invalid` con `preventDefault()` y pintar el mensaje propio (el navegador lo escribe en su idioma y puede quedar fuera de pantalla) |
| Casillas y radios | input escondido accesible + caja propia; foco con `:has(input:focus-visible)` |
| Flecha del `<select>` | `appearance:none` + chevron |
| Rectángulo al tocar en Android | `-webkit-tap-highlight-color` |
| Amarillo del autorrelleno | `input:-webkit-autofill` con `box-shadow` inset |
| Anillo de foco | `:focus-visible` propio con `outline-offset` |
| Triángulo de `<summary>` | `list-style:none` + `::-webkit-details-marker` |
| Selección y cursor | `::selection`, `caret-color` |
| Glifos Unicode como íconos | SVG: caen fuera de la fuente y los dibuja el sistema distinto en cada aparato |
| Cancelar de búsqueda, spinners de `number`, ícono de `date` | estilarlos o elegir otro control |

Mirá también **la fuente de respaldo**: si la declarada no carga, ¿con qué se
ve? Una pila que termina en `serif` a secas deja Times.

### Controles cuyo panel dibuja el navegador (hay que reemplazarlos)
| Qué | Única salida |
|---|---|
| Lista de un `<select>` | listbox propio: botón + `role="listbox"` + valor en input escondido |
| Calendario de `<input type="date">` | calendario propio |
| Sugerencias de autocompletado de otros formularios | `autocomplete="off"` en campos de búsqueda de datos propios [caso real #12] |

Se encuentran sin abrir el navegador (ajustá extensiones y framework):
```bash
grep -rEc '<select|type="(date|time|file)"' --include=*.{html,js,jsx,tsx,vue,svelte,jinja,erb} .
```
Trampas al construir el reemplazo: el panel se recorta dentro de `overflow` o
`<dialog>` (usar `popover` o `position:fixed` y reubicar al hacer scroll,
resize y viewport visual) [caso real #7]; un input escondido no lo valida el
navegador (validar en código); un valor combinado (día + hora) arma strings
inválidos si falta una mitad: probar cada mitad sola [caso real #6]; un control
propio hereda la obligación de **anunciar su valor**, no solo su etiqueta.

### Teclado y foco
- **Recorré con Tab** (el script puede hacer un barrido; lo juzgás vos). Toda
  acción de mouse se hace con teclado; un `<span onclick>` no es focusable.
- Orden de tabulación = orden visual; sin tabindex positivo; sin trampas
  (salvo diálogos, que atrapan y devuelven el foco al disparador); Esc cierra
  diálogos y menús; flechas en listbox/tabs/menús; el enlace "saltar al
  contenido" existe si hay navegación repetida.
- **El foco no se pierde — medí antes de afirmarlo.** Deshabilitar un control
  enfocado lo conserva; lo pierden **quitar del DOM el nodo enfocado** y
  **deshabilitar un `<fieldset>` que lo contiene**. [caso real #8] Buscá listas
  que se redibujan con el foco adentro y diálogos que recalculan botones.
- **Sondeo periódico**: `setInterval` + `innerHTML` pierde el foco cada N
  segundos aunque no cambie nada; una región `aria-live` que se redibuja se
  relee entera. [caso real #10]
- **Auditá el foco por selector, no mirando** (`:focus` no se pinta en un
  navegador sin foco de ventana): sacá `:focus` de las reglas, enumerá todo lo
  enfocable (`a[href], button, input, select, textarea, summary, [tabindex],
  dialog, [popover]`) y comprobá con `matches()` que alguna regla entera lo
  alcanza. [caso real #11] Un contenedor con `tabindex="-1"` no lleva anillo;
  la regla que lo apaga lista etiquetas para no apagar el de un botón.
- Ningún anillo queda tapado por un degradado o elemento superpuesto.

### Lectores de pantalla
- **Anunciá también el éxito**, no solo el error.
- Errores con `aria-invalid` y `aria-describedby` al mensaje.
- Una región viva está en el DOM **antes** de escribirle; usar `setTimeout`, no
  `requestAnimationFrame`. **Las regiones vivas fuera de un `<dialog>` modal
  están muertas** (`showModal()` vuelve inerte el exterior): medí el árbol de
  accesibilidad con el diálogo abierto. [caso real #9]
- `role="grid"` exige `grid > row > gridcell`; si no hay filas, sin roles.
- El nombre accesible de una casilla en `<label>` es todo el texto del label; un
  botón anidado se le pega. [caso real #1]
- `<th scope>`; listas de ítems como `<ul>`; un único `h1` y niveles sin saltos;
  landmarks (`main`, `nav`); `lang` correcto; imágenes con `alt` que describe la
  escena (decorativas con `alt=""`).
- Si es posible, recorré 3 flujos con un lector real (NVDA/VoiceOver) o su
  árbol de accesibilidad; si no, decí que no se hizo.

### Contraste forzado y preferencias del sistema
Emulá `forced-colors: active` y `prefers-contrast: more`: bordes de controles,
íconos y foco siguen visibles; nada depende de un fondo que el modo borra. Con
`prefers-color-scheme: dark`, imágenes y logotipos que no se adaptan, bordes
que desaparecen y `color-scheme` declarado.

## 4. Textos

- **Un nombre por cosa**, en interfaz, mensajes salientes (mail, chat) y panel
  de administración **juntos**.
- **Concordancia de número**: buscá toda concatenación de un número con un
  sustantivo ("1 elementos"). Usá la forma plural del idioma (algunos tienen más
  de dos).
- Nada de jerga de sistema ("formato inválido", "operación exitosa").
- Los `alt` describen la escena, no el tipo de archivo.
- **Los valores de `<option>` son exactamente los que acepta el servidor**:
  comparalos uno por uno contra el validador. [caso real #32]
- `text-transform:capitalize` pone mayúscula en cada palabra, también en
  preposiciones; capitalizá en el código. [caso real #33]
- Ortografía y tipografía **del idioma de la interfaz** (comillas, guiones,
  tildes, mayúsculas); en español, "solo" sin tilde y mayúscula solo al principio.
- **Datos de contacto** idénticos carácter por carácter en la página, los datos
  estructurados y los perfiles externos.
- Promesas que nadie confirmó (horarios, plazos, qué incluye) no van.
- **Idioma y formatos**: fechas dd/mm vs mm/dd, separador decimal y de miles al
  escribir y al leer, zonas horarias y cambio de horario de verano, orden
  alfabético con acentos, nombres con apóstrofo o `ñ`, textos un 40 % más largos
  (seudolocalización: probá `[Ñáéíóú xxxxxxxxx]`), RTL si el producto lo admite.
  Listá cada uso de `Intl`/`toLocale*` y decí si el texto exacto importa:
  no se delega en los datos regionales del aparato. [caso real #13]
- **Corré los tests al terminar y decí qué archivos no cubren**: una pasada de
  textos puede romper una pantalla sin que nada lo note. [caso real #30]

## 5. Estados límite y anchos

Trabajás con tu instancia: vas a forzar errores y vaciar datos. El script midió
desbordes y recortes en los anchos base; vos probás lo que está entre medio y
lo que no es el estado feliz.

### Anchos y reflujo
Probá los anchos y alturas del barrido de `umbrales.md` con el script de
desborde de `tecnicas.md`. El hueco típico está **entre breakpoints**. Además:
- `overflow-x:clip` en `body` impide el desplazamiento programático: usá
  `hidden` o arreglá la causa.
- **Zoom de texto al 200 %** y espaciado de texto de WCAG 1.4.12 (interlineado
  1,5, párrafos 2×, letra 0,12 em, palabra 0,16 em): nada se recorta ni se
  superpone; alturas fijas en px revientan.
- Palabras largas sin espacios y nombres de cuarenta caracteres.
- **Un bloque que mide más que la pantalla** (alto) se mide contra
  `innerHeight`. [caso real #14]
- Orientación horizontal en móvil y teclado virtual que tapa el campo activo.

### Estados límite
Cada pantalla tiene más de un estado y normalmente solo se diseñó el feliz.
- **Vacío** (sin resultados, sin datos, primera vez) dice por qué y qué hacer.
- **Cargando**: ¿hay señal (esqueleto, progreso, botón deshabilitado)? ¿Salta el
  layout al llegar el contenido? Forzá una demora de 5 s con una ruta
  interceptada; un spinner que no termina nunca es un hallazgo.
- **Error de red y de servidor**: offline, timeout, 401, 403, 404, 429, 500,
  respuesta malformada. Interceptá las rutas y mirá qué dice la pantalla, si se
  puede reintentar, si lo escrito se conserva y si hay una página 404 propia.
  **Sin red, lo guardado no puede parecer borrado.** [caso real #17]
- **Lento**: conexión lenta simulada; lo que carga perezoso, ¿avisa?
- **Desbordado**: textos larguísimos, muchos elementos, el máximo permitido.
- **Doble envío**, formulario a medias, vuelta atrás tras enviar.
- **Sin JavaScript**: `<noscript>` útil donde corresponde.
- **Sesión vencida con el formulario abierto.** [caso real #16]
- **Estados terminales**: leé qué instrucciones quedan en pantalla tras un
  pedido rechazado, cancelado o vencido. [caso real #18]
- **Movimiento reducido** (`prefers-reduced-motion: reduce`): no quedan
  animaciones infinitas, autoplay ni parallax; la información no depende de la
  animación; sin reducción, nada parpadea más de 3 veces por segundo.
- **Pantallas que arrancan `hidden`**: listá todo `[hidden]` y `display:none`,
  mostralo y revisalo. [caso real #15]
- **Sembrá el estado antes de mirar**: contador en cero y lista vacía son los
  casos que menos prueban. [caso real #24]

## 6. Datos, permisos y seguridad

Leés el código del servidor y del front, y probás contra tu instancia.

- **Permisos.** Por cada acción que cambia datos: ¿el servidor controla el rol o
  solo lo esconde la interfaz? Llamá la API con un rol que no debe y sin sesión.
  [caso real #20]
- **Plata y cantidades**: redondeos, negativos, decimales con coma, totales
  calculados en dos lugares que no coinciden.
- **Que nada se pierda**: borrados sin confirmar ni deshacer; ediciones
  concurrentes en dos pestañas.
- **Que nada se duplique**: doble envío, reintento tras un corte, importar dos veces.
- **Entradas**: lo escrito en un campo y mostrado en otro lado sin escapar;
  archivos sin límite de tamaño o tipo; rutas armadas con lo que manda el usuario.
- **Lo que queda abierto**: claves o tokens en el código o en mensajes de error,
  documentación de API publicada sin querer, CORS abierto, sesiones que no vencen.
- **Migraciones y datos viejos**: registros sin los campos nuevos.

### Seguridad de front
- XSS: grep de `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `document.write`,
  `eval` con datos del usuario o de la API sin sanear.
- Enlaces con `target="_blank"` sin `rel="noopener"`.
- Secretos, claves o URLs internas en el bundle o los sourcemaps publicados;
  tokens de sesión en `localStorage` (preferir cookies `HttpOnly`).
- Cookies sin `Secure`, `HttpOnly` o `SameSite`; falta de CSP, `X-Content-Type-Options`,
  `frame-ancestors`; contenido mixto http/https; scripts de terceros sin SRI.
- Dependencias con vulnerabilidades conocidas (`npm audit`, `pip-audit` o similar).
- Redirecciones abiertas (`?next=` aceptando cualquier host).

Cada sospecha se prueba contra la instancia antes de escribirla: más de una
"vulnerabilidad" resultó falsa. [caso real #35]

## 7. Web pública (solo si la ve gente de afuera: `"publica": true`)

En una herramienta interna este revisor no corre.

### Compatibilidad y navegadores
Corré las pantallas clave en Chromium, Firefox y WebKit (`--motores` si el
script lo ofrece, o Playwright a mano). Revisá en el código qué depende de lo
que otros motores resuelven distinto o tarde: `:has()`, `@container`,
`text-wrap:balance`, `<dialog>`/`::backdrop`/`backdrop-filter`,
`env(safe-area-inset-*)` y `100dvh`, `scrollbar-color` frente a
`::-webkit-scrollbar`, `inert`, `popover`, formatos de imagen y fuente,
`Intl.DateTimeFormat` con zonas, prefijos `-webkit-`. Para cada dependencia: si
hay respaldo y qué se ve si falla. Marcá lo que solo se confirma en un iPhone real.

### Rendimiento
- Peso de la primera carga y qué pesa más (fuentes, imágenes, bundles).
- Imágenes: formato, tamaño servido vs mostrado, `width`/`height`, `loading="lazy"`.
- Fuentes: subset, `font-display`, cantidad de archivos.
- **Gama baja**: escenas 3D, mapas y animaciones pesadas; si no se puede medir en
  un aparato real, decilo y proponé un límite (no cargar por debajo de cierto
  ancho o con `prefers-reduced-motion`).
- **Cabeceras de caché** de cada recurso: el default de varias plataformas
  obliga a revalidar hasta lo que nunca cambia. [caso real #26]
- Terceros: cuántos, a quién, y si el sitio funciona sin ellos.
- `preload` que no se usa en los primeros segundos es peso y ruido de consola.
- Estabilidad: CLS, tareas largas, LCP (ver los tipos del script).

### Conversión, SEO y cómo se comparte
- ¿La primera pantalla dice **qué es, dónde/para quién y qué hacer**? ¿Cuántas
  veces se repite el mismo llamado?
- **Cómo se ve el link al compartirlo** por el canal que se usa: Open Graph con
  tamaño real, URLs absolutas del dominio definitivo.
- `title` único y descriptivo, `meta description`, `canonical`, `og:url`,
  `robots.txt`, `sitemap.xml`, `lang`, favicon; `noindex` puesto o sacado según
  el momento y dicho en el informe.
- Datos estructurados válidos, **sin marcar reseñas de terceros como propias**.
- Analítica: que cargue y no la bloquee la política de seguridad. Ojo con la
  prueba: `tecnicas.md`, "Lo que `curl` no ve". [caso real #23]
- **¿Alguien se entera cuando entra una consulta?** [caso real #21]
- **Enlaces**: seguí cada enlace saliente hasta su URL final con `curl -sLI`
  (solo GET/HEAD) [caso real #22]; recorré los internos buscando 404; probá
  deep links, recarga en una subruta y el botón Atrás en cada pantalla.

### Dirección de arte
Las imágenes suelen ser la parte más débil y nadie las revisa **como conjunto**:
familia (temperatura, luz, encuadre, grano), las que desentonan, stock o demo
(decir qué foto real falta y dónde), recortes móviles (caras cortadas), texto
sobre imagen en el peor punto, orden y ritmo de galerías, peso contra tamaño
mostrado. Termina con una lista: qué foto falta y para qué lugar.

---

## Superficies no web (API, CLI, escritorio nativo)

Esta skill maneja un navegador (Playwright): lo que no es web **no** tiene
medición automática. Si el proyecto es solo API o CLI, el revisor 1 prueba cada
endpoint/comando contra su especificación (códigos de estado, errores con
mensaje útil, paginación, idempotencia, límites de tasa, validación de entradas,
autenticación) y el revisor 6 la seguridad; las categorías 5-7, 11, 14 y 17 de
`cobertura.md` se marcan N/A con ese motivo. Una app de escritorio nativa o
móvil nativa queda fuera del alcance: el informe lo declara en "Lo que no se revisó".
