# Casos reales (anonimizados)

Anécdotas de corridas reales que justifican reglas de la skill. Las reglas viven
en `skill/references/` con la marca `[caso real #n]`; acá está el detalle.
Sin nombres de cliente, rutas ni cifras identificables. Un caso nuevo entra por
PR (ver paso 9 de `SKILL.md`) y se numera al final.

| # | Caso | Regla que dejó |
|---|---|---|
| 1 | Un revisor afirmó que un botón dentro del `<label>` de una casilla la marcaba y desmarcaba. Se aceptó sin probar y se reportó como lo más grave. Era falso: el navegador no activa el label si el clic cae en un descendiente interactivo. El problema real era menor: el texto del botón se pegaba al nombre accesible de la casilla. | Una afirmación sobre el navegador se prueba en el navegador antes de escribirla. |
| 2 | Un sitio con temas: treinta reglas usaban el token de acento y otras trece tenían el valor base escrito a mano. El tema se aplicaba a medias y se veía peor que sin tema. | Cambiar de tema y listar lo que no cambió. |
| 3 | Un token derivado (`color-mix` sobre el acento) declarado en `:root` mientras el tema redefinía el acento en `body`: resolvía siempre con el valor base. | Declarar el derivado donde vive el valor del que depende. |
| 4 | Un sprite SVG declaraba `stroke-width` en cada `<symbol>`; el atributo ganaba sobre el CSS y cinco reglas de grosor no hacían nada. | Buscar el atributo en el sprite y en el CSS; confirmar renderizando con dos valores. |
| 5 | Un color literal pasaba contra el fondo neutro pero daba 3,2:1 contra uno de los cinco valores del token que tenía al lado. | Medir cada literal que comparte caja con un token variable contra todos sus valores. |
| 6 | Un `datetime-local` reemplazado por día + hora propios armaba `"T10:00"` si faltaba el día; `toISOString()` lanzaba excepción y "Guardar" no hacía nada. | Probar cada mitad de un control compuesto por separado. |
| 7 | Un desplegable propio sin `popover` caía en `position:absolute` dentro de un padre relativo y aparecía corrido en un navegador antiguo. | El respaldo es `position:fixed` y se reubica con scroll, resize y viewport visual. |
| 8 | Un encargo decía que deshabilitar un control enfocado hacía perder el foco. Un revisor lo midió: es falso; solo lo pierden quitar el nodo del DOM y deshabilitar un `<fieldset>` que lo contiene. | Medir antes de afirmar; buscar esos dos casos. |
| 9 | Con un `<dialog>` modal abierto, la región viva del `<body>` quedaba inerte: los avisos no los oía nadie (el árbol de accesibilidad bajó de más de 1800 nodos a 227). | Probar que las regiones vivas existen dentro del diálogo. |
| 10 | Un panel consultaba cada pocos segundos y redibujaba con `innerHTML`: el foco se perdía aunque los datos fueran iguales. | No tocar el DOM si los datos no cambiaron; devolver el foco al equivalente. |
| 11 | Once elementos caían al anillo de foco de fábrica en dos vistas (una sección enmarcada de miles de px, cinco diálogos, dos calendarios). Nadie lo vio: `:focus` no se pinta en un navegador sin foco de ventana. | Auditar el foco por selector con `matches()`, no mirando. |
| 12 | Las sugerencias de autocompletado del navegador mostraban nombres y números de otros sitios sobre un panel privado. | `autocomplete="off"` en campos de búsqueda de datos ajenos al navegador. |
| 13 | `Intl.NumberFormat` con `style:'currency'` daba `$ 0` en un equipo y un código de moneda en Chrome de Android, que no traía los datos de esa región. | No delegar en datos regionales del aparato cuando el texto exacto importa. |
| 14 | El pie de página en móvil medía más que la pantalla y se leía como una segunda página; ningún chequeo miraba el alto. | Medir el alto de los bloques grandes contra `innerHeight`. |
| 15 | Un ícono sin dimensionar salió a 54×54 px en la pantalla de acceso, oculta hasta que vence la sesión; nadie la había renderizado. | Listar y mostrar todo lo `hidden` o `display:none`. |
| 16 | Al vencer la sesión con un modal de edición abierto, el modal quedaba sobre el login y la única salida era Cancelar, perdiendo lo escrito. | Probar sesión vencida con formulario abierto. |
| 17 | Sin red, un carrito guardado decía "producto que ya no está", total 0 y ofrecía "Quitar". | Distinguir "no cargó" de "no existe". |
| 18 | Un pedido rechazado seguía mostrando instrucciones de pago y retiro. | Recorrer cada estado terminal y leer qué instrucciones quedan. |
| 19 | Un importador CSV aceptaba en la vista previa archivos que el servidor rechazaba (separador `;`, codificación Windows-1252, más largo que el tope). | Probar archivos vacíos, sin cabecera, con otro separador y codificación, y sobre el tope. |
| 20 | Tres acciones de escritura no exigían sesión: parecían protegidas solo porque el botón no aparecía. | Llamar a la API directo con un rol sin permiso y sin sesión. |
| 21 | Una consulta de contacto se guardaba sin avisar a nadie; si el dueño no abría el panel, moría. | Verificar que alguien se entera de cada entrada. |
| 22 | Un enlace corto "Cómo llegar" terminaba en una búsqueda web y no en una ruta. | Seguir cada enlace saliente con `curl -sLI`. |
| 23 | Dos revisores reportaron "la analítica no carga" porque `curl` sin cabeceras de navegador no recibe el script que inyecta el borde. | Comparar la respuesta con y sin cabeceras de navegador. |
| 24 | Una marca de notificaciones partía la pestaña en dos renglones, pero con el contador en cero estaba oculta y nunca se vio. | Sembrar el estado (contador con 1 y 2 dígitos, lista con filas) antes de verificar. |
| 25 | Se verificó en 320, 360 y 393 px; el teléfono real de la persona medía 450 px CSS y el arreglo no le llegaba. | Preguntar en qué aparato mira. |
| 26 | Cambiar `Cache-Control` no alcanzó: el navegador ya tenía el script guardado una hora; además dos reglas matcheaban el mismo archivo y daban una cabecera contradictoria. | Cambiar la URL (`?v=`) y comprobar con `curl -sI`. |
| 27 | Un `\b` quedó como carácter de retroceso real al generar un test: el regex era válido y pasaba, pero no podía matchear nunca. | Romper a propósito lo que el test dice comprobar. |
| 28 | Un comentario que explicaba por qué no se usaba `Intl` hacía fallar la prueba que busca `Intl`. | Quitar comentarios antes de comprobar ausencia de un patrón. |
| 29 | Un revisor midió que un módulo pesado "no se había pedido"; el observador que lo carga nunca disparó en una pestaña sin pintar. | Una observación negativa solo vale si la cosa tuvo oportunidad de pasar. |
| 30 | Una pasada de textos cambió una variable por otra equivocada y dejó una pantalla rota tres commits; ninguna prueba tocaba ese render. | Correr los tests al terminar y decir qué archivos no cubren. |
| 31 | Dos glifos usados como ícono no estaban en la fuente servida y los dibujaba una fuente del sistema distinta por dispositivo. | Comprobar el `cmap` de la fuente. |
| 32 | Los `<option>` de un filtro mandaban `todo` y la API esperaba `todos`. | Comparar cada valor contra el validador del servidor. |
| 33 | `text-transform:capitalize` produjo "Setiembre De 2026". | Capitalizar la primera letra en el código. |
| 34 | La suite comprobaba nueve tipos de control nativo en el sitio público y dos en el panel: dos controles nativos escaparon en el panel. | Una asimetría entre superficies es un agujero. |
| 35 | Un revisor levantó como falla que "9.30" no se aceptaba como hora; al probarlo contra la instancia se normalizaba bien. | Cada sospecha se prueba contra la instancia antes de escribirla. |
| 36 | Un commit pasó con el lint en rojo porque el pre-commit estaba versionado pero no activado en ese clon. | Activar los guardrails del repo antes de commitear. |
| 37 | Se probó una función por una sola de sus entradas cómodas y el mapa listaba otras. | Una prueba que maneja una sola entrada está incompleta si el mapa lista otras. |
| 38 | El globo de validación nativo ("Completa este campo") lo encontró el cliente mirando una captura, después de dar la revisión por cerrada; además, al esconder el input para dibujar una casilla propia, el globo quedaba sin dónde anclarse (un elemento de 1 px). | Esconder un control obliga a hacerse cargo de todo lo que el navegador dibujaba sobre él. |

## Navegador integrado en segundo plano
Algunos entornos de agente muestran el navegador en una pestaña que no tiene
foco de ventana. Ahí se congelan transiciones, `getComputedStyle` devuelve
valores iniciales, los `IntersectionObserver` no disparan, las capturas fallan y
`focus()` no hace nada. Detalle y receta en `skill/references/tecnicas.md`
("Verificar en el navegador").

## Una corrida de ejemplo
El informe completo anonimizado vive en `ejemplos/informe-ejemplo.md`.
