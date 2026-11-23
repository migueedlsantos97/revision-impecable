# Clave H · tres sistemas bajo un shell (solo para el juez)
Arranque: `python server.py 8108`; pantallas `/a`, `/b`, `/c`. Familia: Diseño y consistencia (inventario entre sistemas).

| # | Defecto | Peso | Dorado |
|---|---|---|---|
| H1 | El botón primario tiene 3 formas: radio 8 / 20 / 2 px, alto 44 / 40 / 44, peso 600 / 400 / 600 | 3 | no |
| H2 | La misma acción se llama Guardar / Guardar cambios / Grabar, y Aceptar / OK en el diálogo | 2 | no |
| H3 | `/c` es oscuro y `/a`, `/b` claros dentro del mismo shell (tema a medias entre sistemas) | 3 | no |
| H4 | El azul de marca es `#0b5cad` en a y b y `#0f6bd1` en c (token duplicado con otro valor) | 2 | no |
| H5 | `outline:none` en el botón de `/c`: sin anillo de foco | 3 | no |
| H6 | Un aviso fijo (`position:fixed`, 20 px + texto) tapa la parte baja de `/c` en 390 px, sobre el contenido tocable | 2 | **sí** |

Pista (eje 2): "ojo con el botón Guardar de Stock".
