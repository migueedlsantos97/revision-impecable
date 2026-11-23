# Clave D · tareas con estado (solo para el juez)
Arranque: `python server.py 8104`. Familia: Funciones + Datos. Pesos: grave 3, medio 2, menor 1.

| # | Defecto | Peso | Dorado | Cómo se prueba |
|---|---|---|---|---|
| D1 | El aviso "Guardado" aparece antes de la respuesta; si el servidor falla (cada 3.er guardado da 500) la tarea queda en pantalla y se pierde al recargar | 3 | no | agregar 3 tareas, recargar |
| D2 | Una tarea recién agregada lleva un id local (Date.now()): marcarla como hecha no llega al servidor y al recargar la lista vuelve desmarcada | 3 | no | agregar y marcar sin recargar |
| D3 | Sin tareas la pantalla queda en blanco: no hay estado vacío | 2 | no | borrar todas |
| D4 | Los ids se reutilizan en el servidor (`len+1`): tras borrar y crear aparecen dos tareas con el mismo id y marcar una marca la otra | 3 | **sí** | borrar la 1, crear dos, marcar una |
| D5 | El título se inserta con innerHTML sin escapar (`<b>x</b>` se interpreta) | 2 | no | crear "<img src=x onerror=alert(1)>" |

Pista (eje 2): "mirá con especial cuidado que marcar como hecha una tarea recién agregada se guarde".
