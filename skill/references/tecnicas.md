# Técnicas compartidas

Lo que varios revisores necesitan. Todo esto da **pruebas**, que es lo único que
convierte una impresión en un hallazgo. Casi todo lo mecánico ya lo hace
`scripts/medir.py`; lo de abajo es para lo que el script no cubre, para
confirmar una sospecha a mano y como receta cuando una técnica merece volverse
chequeo (si la usaste dos veces, pasala al script). Los casos están en
`ejemplos/casos-reales.md`.

Las recetas de shell usan `grep`/`curl`; en Windows funcionan en Git Bash o WSL.
Ajustá extensiones y rutas al proyecto (`*.css` puede ser `*.scss`, `*.module.css`
o estilos dentro de componentes `.tsx/.vue/.svelte`).

**Marcas para el script.** Un solape, recorte o ícono a propósito se marca en el
HTML con `data-revision-ok="solape"` (o `recorte`, `tactil`, `nativo`, `icono`,
`glifo`, `texto`, `contraste`, `tema`, `todo`) y el script deja de reportarlo.
Cada marca es una decisión: lleva su motivo en `reglas.md`.

## Inventario de valores

Antes de mirar nada, contá.

```bash
grep -rohE 'border-radius:[0-9.]+(px|rem)' --include=*.css . | sort | uniq -c | sort -rn
grep -rohE 'font-size:[0-9.]+(px|rem)'     --include=*.css . | sort | uniq -c | sort -rn
grep -rohE 'stroke-width="[0-9.]+"'        --include=*.{html,js,jsx,tsx,svg} . | sort | uniq -c
grep -rohE '#[0-9a-fA-F]{6}'               --include=*.css . | sort | uniq -c | sort -rn
grep -rohE 'gap:[0-9.]+(px|rem)'           --include=*.css . | sort | uniq -c | sort -rn
```

Con CSS escrito en una línea larga, `grep -c` cuenta líneas, no apariciones: usá
siempre `grep -o ... | wc -l`. Para el contexto de un color antes de cambiarlo:
`grep -o '.\{0,50\}#a1b2c3' archivo.css`.

## Contraste

Razón = `(L1 + 0.05) / (L2 + 0.05)`, con L la luminancia relativa. Por canal `c`
de 0 a 1: si `c <= 0.03928` vale `c/12.92`; si no, `((c+0.055)/1.055) ** 2.4`.
`L = 0.2126*R + 0.7152*G + 0.0722*B`. Calculalo, no lo estimes, contra **el
fondo real del elemento** (a menudo el de la tarjeta). Si un color no llega,
bajá la luminancia del mismo tono manteniendo matiz y saturación.

## Desborde horizontal

```js
({vw: innerWidth, docW: document.documentElement.scrollWidth,
  desborda: [...document.querySelectorAll('body *')]
    .filter(e => { const r = e.getBoundingClientRect();
                   return r.width > 0 && (r.right > innerWidth + 1 || r.left < -1); })
    .map(e => e.tagName + '.' + String(e.className).slice(0, 30))})
```

Los elementos escondidos a propósito fuera de pantalla (honeypots, textos solo
para lectores) aparecen acá: reconocelos y no los reportes. El alto se mide
igual contra `innerHeight` para bloques grandes. [caso real #14]

## Lo que no cambia al cambiar el tema

Cuando hay temas, modos o variantes, el defecto típico no es que falte el token
sino que algunos lugares tienen el valor base escrito a mano. [caso real #2]
Dos pasos. Primero, contá quién usa el token y quién no:

```bash
grep -rho 'var(--acento)' --include=*.css . | wc -l   # el nombre del token del proyecto
grep -rhoE '#(<hex1>|<hex2>)' --include=*.css .        # la familia del valor base
```

Segundo, sacale una foto a los colores calculados, cambiá el tema, sacale otra,
y listá lo que quedó igual:

```js
const nodos = [...document.querySelectorAll('body *')];
const foto = () => nodos.map(e => { const s = getComputedStyle(e);
  return s.color + '|' + s.backgroundColor + '|' + s.borderTopColor; });
const antes = foto();
document.documentElement.dataset.theme = '<otro tema>';   // o el atributo/clase del proyecto
document.body.offsetHeight;
await new Promise(r => setTimeout(r, 150));
const despues = foto();
nodos.filter((e, i) => antes[i] === despues[i])
     .map(e => e.tagName + '.' + String(e.className).slice(0, 30));
```

Separá los que **deben** quedarse quietos (estados semánticos, neutros, colores
literales como un degradado que dibuja un atardecer) y nombralos en el informe
para que nadie los "arregle" después.

## Lo que `curl` no ve

Las plataformas de borde inyectan scripts solo cuando la petición parece un
navegador; un `curl` pelado no los ve y el hallazgo sale al revés. [caso real #23]

```bash
curl -s https://<dominio>/ \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml' --compressed | grep -c '<lo que buscás>'
```

Compará las dos mediciones, con y sin cabeceras, antes de afirmar que algo falta.

## Contraste sobre una foto

Medí sobre **las cajas reales del texto**, sacadas del navegador, no sobre el
ancho del bloque:

```js
const r = document.querySelector('<selector del titular>');
const rango = document.createRange(); rango.selectNodeContents(r);
[...rango.getClientRects()].map(b => [b.left, b.top, b.right, b.bottom].map(Math.round))
```

Componé la foto como lo hace el navegador (`object-fit`, `object-position`,
degradados del velo en el mismo orden que el CSS) y buscá el peor píxel dentro
de esas cajas. Si el resultado sorprende, renderizá el compuesto a un archivo y
miralo.

## El estado vacío esconde la mitad de los errores

Una marca de notificaciones que parte la pestaña no se ve cuando el contador
está en cero y la marca oculta. [caso real #24] Lista vacía, contador en cero,
día sin eventos y formulario sin tocar son los estados más fáciles de mirar y
los que menos prueban. **Sembrá el estado**: contador con uno y dos dígitos,
lista con filas, campo con un error pintado. Casi siempre alcanza con escribirlo
desde la consola.

## Los anchos de prueba no se eligen, se preguntan

Los cortes por reflejo (320/360/375/390/430) dejan un hueco entre 430 y 560 donde
entran muchos Android comunes. Hay que **preguntar en qué aparato mira la
persona** (`viewport_real` del adaptador) y medir ahí. [caso real #25] El
umbral de un breakpoint tampoco se elige a ojo: se mide cuánto necesita el
contenido (hijos + separaciones + relleno) y se suma un margen.

## Lo que el navegador trae del sistema cambia según el aparato

`Intl.NumberFormat` con `style:'currency'`, el formato de fechas, el orden
alfabético y los nombres de los meses dependen de los datos regionales del
aparato, que pueden faltar (p. ej. Chrome en Android). [caso real #13] Cuando el
texto exacto importa, no se delega: se formatea el número y se pone el símbolo a mano.

## La caché guardada no la cambia una cabecera nueva

Cambiar `Cache-Control` solo afecta a lo que se pida **desde ahora**; un
navegador que ya bajó el archivo no lo vuelve a pedir hasta que venza. Para que
un arreglo llegue hoy hay que **cambiar la dirección** (`app.js?v=2`), también
en los módulos que se piden desde adentro. Mientras se itera, lo que se toca no
lleva caché larga; la caché larga se reserva para fuentes, bibliotecas e
imágenes. Dos patrones que matchean el mismo archivo salen concatenados en una
cabecera contradictoria: comprobá con `curl -sI <url> | grep -i cache-control`.
[caso real #26]

## Un test puede estar muerto en vez de en rojo

Un regex válido que no puede matchear nunca pasa por una razón equivocada.
[caso real #27] Dos revisiones baratas al escribir tests desde un script:

```bash
# Caracteres de control que no deberían estar en código
grep -rPanc '[\x07\x08\x0b\x0c\x1b]' tests/ src/
```

Y **romper a propósito lo que el test dice comprobar**: si sigue en verde, no
comprueba eso (sobre todo `doesNotMatch` y `assert.ok`, que pasan por ausencia).

## Los comentarios no son código

Un comentario que explica por qué *no* se usa algo nombra ese algo, y una
comprobación sobre el archivo entero lo encuentra. [caso real #28] Antes de
comprobar la ausencia de un patrón, sacá los comentarios:

```js
const codigo = js.replace(/^\s*\/\/.*$/gm, '');          // JS
const reglas = css.replace(/\/\*[\s\S]*?\*\//g, '');     // CSS
```

## `:focus` no existe si la ventana no tiene foco

`:focus` solo aplica con la ventana enfocada; en una pestaña que no está al
frente, `document.activeElement` es correcto pero `matches(':focus')` da `false`
y el anillo no se pinta. [caso real #11] Cualquier defecto de anillo es invisible
ahí: se revisa por CSS, no por observación (ver encargo 3, "Auditá el foco por selector").

## No ver algo no es prueba de nada

Un `IntersectionObserver` que no disparó en una pestaña que no pinta hace
parecer que un módulo "no se pidió". [caso real #29] **Una observación negativa
en un entorno que miente no prueba nada**: antes de aceptar un "no pasó",
demostrá que tuvo la oportunidad de pasar (que el observador disparó, que el
evento llegó, que la función se llamó). Si no se puede, el veredicto es
PLAUSIBLE.

## Verificar en el navegador

Los tests de archivo no ven nada de esto: hay que abrir el sitio.

**Entornos con la pestaña en segundo plano** (algunos navegadores integrados en
herramientas de agente, o ventanas sin foco). Ahí:

- las transiciones quedan congeladas en `currentTime 0`;
- `getComputedStyle` devuelve el valor inicial, sobre todo con `:has()` y
  atributos recién puestos;
- los `IntersectionObserver` no disparan, y lo perezoso parece roto;
- las capturas devuelven un cuadro viejo o fallan;
- `focus()` no hace nada.

Comprobalo antes de declarar un bug:

```js
({visible: document.visibilityState, foco: document.hasFocus(),
  animaciones: document.getAnimations().slice(0,3).map(a => a.playState + ':' + a.currentTime)})
```

Si está congelado, es confiable: `element.matches(selector)`; llamar a las
funciones directamente en vez de esperar al observador; leer el CSS servido con
`fetch(url, {cache:'no-store'})` y compararlo con el cargado. Al buscar una
regla en el CSSOM, los selectores vienen normalizados (`[data-x=true]` se guarda
como `[data-x="true"]`). Un contexto de Playwright propio por revisor evita que
varios revisores se pisen en el mismo navegador.

## Probar el formulario sin mouse

```js
document.getElementById('<boton-enviar>').click();
await new Promise(r => setTimeout(r, 600));
({foco: document.activeElement.id,
  errores: [...document.querySelectorAll('[aria-invalid="true"]')].map(e => e.id)})
```

## Forzar red y fallos

Con Playwright: `context.setOffline(true)`; `page.route('**/api/**', r => r.abort())`;
`r.fulfill({status: 500})` o con una demora de 5 s antes de continuar. Probá
cada pantalla con 401, 403, 404, 429, 500 y respuesta no JSON. Un estado que no
viste no está revisado.

## Emular preferencias del sistema

`page.emulate_media(reduced_motion='reduce', color_scheme='dark',
forced_colors='active', media='print')`. Para zoom de texto, subí el tamaño de
fuente raíz al 200 % y recorré las pantallas con el script de desborde.

## Verificar un despliegue

Se comprueba contra un marcador del cambio, no contra el reloj. Pedí **la raíz**
del sitio (la ruta `/index.html` puede redirigir):

```bash
curl -s https://<dominio>/ | grep -c '<marcador del cambio>'
curl -sI https://<dominio>/ | grep -iE 'content-security|x-frame|strict-transport'
```

Solo lectura: nunca se despliega desde esta skill.

## Un glifo que la fuente no trae

Antes de aceptar un carácter como ícono o flecha de texto (✳ → ✓ ★), comprobá
que esté en el `cmap` de la fuente servida. Un `.woff2` se abre con Node sin
dependencias (`zlib.brotliDecompressSync` sobre las tablas y leer el `cmap`) o
con `fontTools`. Si no está, lo dibuja una fuente del sistema distinta en cada
aparato, y en Android puede salir como emoji a color. [caso real #31]
