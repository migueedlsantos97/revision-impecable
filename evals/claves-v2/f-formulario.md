# Clave F · formulario accesible-roto (solo para el juez)
Abrir `index.html` directo. Familia: Controles, teclado y lectores.

| # | Defecto | Peso | Dorado |
|---|---|---|---|
| F1 | `<label>Nombre</label>` sin `for`: el campo no tiene nombre accesible | 3 | no |
| F2 | El error del correo es solo un borde rojo: sin texto, sin `aria-invalid`, sin `role=alert` | 3 | no |
| F3 | `tabindex` positivos (1, 2, 3): el orden del Tab salta (correo, teléfono, nombre) | 2 | no |
| F4 | El modal no mueve el foco adentro, no se cierra con Escape y el Tab sale hacia la página | 3 | no |
| F5 | Un enlace dentro del `<label>` de un radio: su texto se pega al nombre de la opción | 2 | no |
| F6 | "Enviado" aparece sin región viva (`#msg` sin `role=status`/`aria-live`) | 2 | no |
| F7 | El teléfono es `type=number`: flechitas, rueda que cambia el valor, pierde ceros y el `+` | 2 | **sí** |

Pista (eje 2): "fijate en el botón que está dentro de la opción de plan".
