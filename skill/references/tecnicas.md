# Técnicas compartidas

Lo que varios revisores necesitan. Todo esto da **pruebas**, que es lo único que
convierte una impresión en un hallazgo.

## Inventario de valores

Antes de mirar nada, contá. Ajustá las rutas al proyecto.

```bash
grep -oh 'border-radius:[0-9]*px' *.css | sort -t: -k2 -n | uniq -c
grep -oh 'font-size:[0-9]*px'     *.css | sort -t: -k2 -n | uniq -c
grep -o  'stroke-width="[0-9.]*"' *.html *.js | sort | uniq -c
grep -ohE '#[0-9a-fA-F]{6}'       *.css | sort | uniq -c | sort -rn
grep -oh 'gap:[0-9]*px'           *.css | sort -t: -k2 -n | uniq -c
```

Cuidado con archivos CSS escritos en una sola línea larga: `grep -c` cuenta
líneas, no apariciones. Usá siempre `grep -o ... | wc -l`.

Para ver el contexto de un color antes de cambiarlo:

```bash
grep -o '.\{0,50\}#a1b2c3' archivo.css
```

## Contraste

La razón entre dos colores es `(L1 + 0.05) / (L2 + 0.05)`, con L la luminancia
relativa. Para cada canal `c` de 0 a 1: si `c <= 0.03928`, vale `c/12.92`; si no,
`((c+0.055)/1.055) ** 2.4`. Después `L = 0.2126*R + 0.7152*G + 0.0722*B`.

Calculalo, no lo estimes. Y calculalo contra **el fondo real del elemento**, que
a menudo es el de la tarjeta y no el de la página.

Cuando un color no llega, buscá el más cercano del mismo tono que sí: bajá la
luminancia manteniendo matiz y saturación.

## Desborde horizontal

En cada ancho que pruebes:

```js
({vw: innerWidth, docW: document.documentElement.scrollWidth,
  desborda: [...document.querySelectorAll('body *')]
    .filter(e => { const r = e.getBoundingClientRect();
                   return r.width > 0 && (r.right > innerWidth + 1 || r.left < -1); })
    .map(e => e.tagName + '.' + String(e.className).slice(0, 30))})
```

Los elementos escondidos a propósito fuera de pantalla (honeypots, textos solo
para lectores) aparecen acá. Reconocelos y no los reportes.

## Lo que no cambia al cambiar el tema

**[caso real]** Cuando el sitio tiene temas, modos o variantes, el defecto no es
que falte el token sino que unos cuantos lugares tienen el valor base escrito a
mano. Se encuentra en dos pasos.

Primero, contá quién usa el token y quién no:

```bash
grep -o 'var(--acento)' *.css | wc -l
grep -oE '#(d4c1a2|f5d9a6|dfd4c3)' *.css   # la familia del valor base
```

Segundo, y es el que no falla: sacale una foto a los colores calculados, cambiá
el tema, sacale otra, y listá lo que quedó igual.

```js
const nodos = [...document.querySelectorAll('body *')];
const foto = () => nodos.map(e => { const s = getComputedStyle(e);
  return s.color + '|' + s.backgroundColor + '|' + s.borderTopColor; });
const antes = foto();
document.body.dataset.mood = '<otro tema>';
document.body.offsetHeight;
await new Promise(r => setTimeout(r, 150));
const despues = foto();
nodos.map((e, i) => antes[i] === despues[i] ? null : i).filter(i => i !== null).length;
// y al revés: los que NO cambiaron y deberían
nodos.filter((e, i) => antes[i] === despues[i] && /accent|tinte|borde/.test(getComputedStyle(e).cssText || ''))
     .map(e => e.tagName + '.' + String(e.className).slice(0, 30));
```

Separá siempre los que **deben** quedarse quietos: los estados semánticos
(disponible, error), los neutros, y cualquier color que represente algo literal
—un degradado que dibuja un atardecer tiene que seguir siendo ámbar en todos
los temas—. Esos se nombran en el informe para que nadie los "arregle" después.

## Lo que `curl` no ve

**[caso real]** Las plataformas de borde inyectan scripts en el HTML solo cuando
la petición parece un navegador. Un `curl` pelado no los ve, y el hallazgo sale
al revés: "la analítica no está cargando". Dos revisores distintos de la misma
corrida se equivocaron con la misma prueba.

```bash
curl -s https://<dominio>/ \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36' \
  -H 'Accept: text/html,application/xhtml+xml' --compressed | grep -c '<lo que buscás>'
```

Compará siempre las dos mediciones, con y sin cabeceras, antes de afirmar que
algo falta.

## Contraste sobre una foto

**[caso real]** No barras el ancho entero del bloque: medí sobre **las cajas
reales del texto**, sacadas del navegador, o vas a reportar el peor punto de una
zona donde no cae ningún glifo.

```js
const r = document.querySelector('.hero h1');
const rango = document.createRange(); rango.selectNodeContents(r);
[...rango.getClientRects()].map(b => [b.left, b.top, b.right, b.bottom].map(Math.round))
```

Después componé la foto como la compone el navegador —`object-fit`,
`object-position`, y los degradados del velo en el mismo orden que el CSS— y
buscá el peor píxel dentro de esas cajas. Cuando el resultado te sorprenda,
renderizá el compuesto a un archivo y miralo: es la forma barata de descubrir
que la geometría estaba mal.

## Verificar en el navegador

Los tests de archivo no ven nada de esto. Hay que abrir el sitio.

**Aviso sobre el navegador integrado de Claude.** Cuando la ventana de la app no
está al frente, la pestaña deja de producir cuadros. Ahí:

- las transiciones quedan congeladas en `currentTime 0`;
- `getComputedStyle` devuelve el valor inicial y no el real, sobre todo con
  `:has()` y con atributos recién puestos;
- los `IntersectionObserver` **nunca disparan**, así que todo lo que carga
  perezoso (mapas, escenas 3D) parece roto y no lo está;
- las capturas devuelven un cuadro viejo o fallan con "did not finish
  rendering";
- `focus()` no hace nada.

Comprobalo antes de declarar un bug:

```js
({visible: document.visibilityState, foco: document.hasFocus(),
  animaciones: document.getAnimations().slice(0,3).map(a => a.playState + ':' + a.currentTime)})
```

Si está congelado, lo que **sí** es confiable:

- `element.matches(selector)` para saber si una regla aplica.
- Llamar a las funciones directamente en vez de esperar al observador.
- Leer el CSS servido con `fetch(url, {cache:'no-store'})` y compararlo con lo
  que tiene cargado la pestaña.

Al buscar una regla en el CSSOM acordate de que los selectores vienen
normalizados: `[data-x=true]` se guarda como `[data-x="true"]`.

## Probar el formulario sin mouse

```js
document.getElementById('<boton-enviar>').click();
await new Promise(r => setTimeout(r, 600));
({foco: document.activeElement.id,
  errores: [...document.querySelectorAll('[aria-invalid="true"]')].map(e => e.id)})
```

## Verificar un despliegue

Que el build esté arriba se comprueba contra un marcador del cambio, no contra
el reloj. Pedí **la raíz** del sitio: `/index.html` suele responder 307 y `grep`
te va a decir que todavía está viejo.

```bash
curl -s https://<dominio>/ | grep -c '<marcador del cambio>'
curl -sI https://<dominio>/ | grep -iE 'content-security|x-frame|strict-transport'
```

## Estados que hay que forzar

Para ver el estado de carga o de error hay que provocarlos. Apagar la red desde
las herramientas, devolver un 500 desde el servidor de desarrollo, o llamar a la
función de render con datos vacíos. Un estado que no viste no está revisado.
