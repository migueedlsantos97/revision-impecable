# Clave I · sitio público (solo para el juez)
Arranque: `python server.py 8109`. Familia: Web pública + estado vivo.

| # | Defecto | Peso | Dorado |
|---|---|---|---|
| I1 | Imagen de 3 MB (BMP sin comprimir) sin `width`/`height`: salto de diseño y peso | 3 | no |
| I2 | `<title>Document</title>`, sin `lang`, sin `meta description`, sin `og:*` | 2 | no |
| I3 | "Ver la carta completa" lleva a un 404 | 3 | no |
| I4 | Un `setInterval` de 2 s reemplaza el campo de búsqueda: pierde el foco mientras se escribe | 3 | no |
| I5 | Ningún recurso trae `Cache-Control` | 1 | no |
| I6 | `robots.txt` con `Disallow: /`: el sitio público no se indexa | 3 | **sí** |

Pista (eje 2): "mirá la imagen de portada".
