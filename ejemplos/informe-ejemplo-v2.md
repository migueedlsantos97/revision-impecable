# Informe de ejemplo (v2): lo que produce `medir.py`

> Ejemplo reproducible, con datos ficticios: salió de correr la skill sobre
> [`proyecto-minimo/`](proyecto-minimo/) (una página con una tabla, un `<select>` y un botón, sembrada con
> defectos). Para ver una revisión completa con revisores y refutación, mirá
> [`informe-ejemplo.md`](informe-ejemplo.md) (v1, anonimizado). Lo que sigue es la forma de la salida de la v2.

## Medición: `.claude/revision/salida/<fecha>/informe.md`

Total: **36** (36 medidas, 0 sospechas: mirarlas con criterio). Cuatro defectos distintos, agrupados por selector:

| tipo | cantidad (celdas medidas: pantalla x ancho x tema) |
|---|---|
| texto_chico | 20 |
| tactil | 8 |
| control_nativo | 4 |
| contraste | 4 |

Una línea por defecto, con dónde aparece (pantalla@ancho/tema):

- **contraste** `html > body > p > small`: #aaaaaa sobre #ffffff da 2.32:1, pide 4.5:1 · pedidos@390/claro, pedidos@1366/claro (y los dos oscuros)
- **control_nativo** `html > body > select`: su lista la dibuja el sistema; hace falta un listbox propio
- **tactil** `button#act`: 79x28 px, el mínimo es 44
- **tactil** `html > body > select`: 89x19 px, el mínimo es 44
- **texto_chico** `table > tbody > tr > th, td`: 12 px, el mínimo es 13

Inventario de componentes (la medida de consistencia: cuántas formas distintas tiene cada uno en toda la app):

```
boton_primario (1 forma)    1x alto 28, radio 6px, peso 400   ej.: pedidos, button#act, "Actualizar"
campo (1 forma)             1x alto 19, radio 0px, borde 1px  ej.: pedidos, select
encabezado_tabla (1 forma)  3x fuente 12px, peso 700
```

Con un segundo sistema, una línea como `boton_primario (3 formas)` es la alerta: el mismo botón se ve distinto según
dónde estés. Los umbrales (`max_variantes`, `tactil`, `texto`) salen del adaptador del proyecto.

## Lo que sigue en una corrida completa

1. Los revisores toman las sospechas y lo que el script no puede medir; cada hallazgo se refuta antes de aceptarse.
2. Se arregla en el lugar compartido (aquí: una regla de botón y una de tabla en la hoja, no cinco parches).
3. Se vuelve a medir hasta que el total es 0 o lo que queda tiene motivo escrito.
4. Cada defecto se vuelve estructura (un chequeo o un test que falla si vuelve), y el informe final
   (`docs/revision-<fecha>.md`) separa: lo arreglado, lo descartado y por qué, lo que queda a criterio del dueño y
   dónde la revisión sigue ciega.
