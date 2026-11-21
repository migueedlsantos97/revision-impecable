# Clave de defectos sembrados (solo para el juez; el ejecutor nunca la ve)

## pantalla-a (5 defectos)
1. Botón Actualizar de 30x30 px (táctil < 44).
2. `<select>` nativo (control nativo prohibido).
3. Texto de tabla de 11 px (< 13).
4. A 390 px la tabla (min-width 560) fuerza scroll horizontal de la tabla/página (desborde).
5. Dos botones de tema visibles ("Tema" y "Oscuro") que hacen lo mismo (interruptor repetido).

## pantalla-b (5 defectos)
1. Emoji ⚠️ usado como ícono.
2. Contraste bajo: `small` en #aaa sobre tarjeta blanca (≈2,3:1) en claro.
3. El botón de tema (ancho 230 px, absolute) pisa el título de la cabecera a 390 px.
4. Aviso fijo "3 alertas" mientras la lista muestra 1 (contador no calculado de los datos).
5. En oscuro, la tarjeta "Nota del encargado" tiene texto #111 sobre fondo oscuro (ilegible); solo se ve mirando el tema oscuro. (El aviso amarillo tiene su propio fondo claro y es legible: no es defecto.)

## pantalla-c (0 defectos)
Pantalla limpia: cualquier "defecto grave" reportado es falsa alarma. Se acepta como mucho observaciones menores marcadas como tales.
