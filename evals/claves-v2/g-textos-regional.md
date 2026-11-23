# Clave G · textos y datos regionales (solo para el juez)
Abrir `index.html` directo; probar con zona horaria America/Montevideo y con un navegador en otro idioma.

| # | Defecto | Peso | Dorado |
|---|---|---|---|
| G1 | "4 resultados" sin singular/plural calculado (con un solo dato diría "1 resultados") | 2 | no |
| G2 | El mismo concepto se llama Clientes / Usuarios / Cuentas en el menú | 2 | no |
| G3 | `slice(0,14)` parte el emoji de "Álvaro Jardín🌿 Integral" y deja un carácter roto | 2 | no |
| G4 | La fecha `2026-04-03` se interpreta como UTC y se muestra "2/4" en Uruguay (un día antes) | 3 | no |
| G5 | Moneda con `Intl` sin locale explícito: el texto cambia según el aparato ("21.314,40 UYU" vs "UYU 21,314.40") | 2 | no |
| G6 | `sort` por comparación de código: "Ñandú" y "Álvaro" quedan después de "Zeta" (falta `localeCompare`) | 2 | **sí** |
| G7 | Fechas `3/3`, `2/4`, `30/11` sin año ni cero: ambiguas entre d/m y m/d | 1 | **sí** |

Pista (eje 2): "mirá cómo se ven las fechas".
