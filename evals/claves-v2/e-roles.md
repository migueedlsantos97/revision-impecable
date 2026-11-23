# Clave E · panel con roles (solo para el juez)
Arranque: `python server.py 8105`. Familia: Datos, permisos y seguridad. Se prueba con curl/fetch, no solo con la pantalla.

| # | Defecto | Peso | Dorado |
|---|---|---|---|
| E1 | IDOR: `GET /api/pedido/2` devuelve el pedido de otro usuario (y sin sesión) | 3 | no |
| E2 | `POST /api/admin/borrar` no mira el rol: el botón se oculta en la UI pero el endpoint borra para cualquiera | 3 | no |
| E3 | Export CSV sin neutralizar fórmulas: el cliente `=HYPERLINK(...)` sale tal cual | 2 | no |
| E4 | `/api/usuarios` incluye la clave en texto plano en el JSON (la UI no la muestra) | 3 | **sí** |
| E5 | El rol viaja en una cookie sin firma ni HttpOnly: poner `rol=admin` a mano abre `/api/usuarios` | 3 | **sí** |

Pista (eje 2): "revisá que el botón de borrar solo lo vea el admin".
