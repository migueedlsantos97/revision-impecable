# Las reglas de Apple como base

Resumen de las Human Interface Guidelines de Apple aplicado a web y apps
web. Es el estándar cuando el proyecto no dice otra cosa; las reglas del
proyecto (`.claude/revision/reglas.md`) mandan sobre estas.

Apple lo resume en tres principios: **jerarquía** (lo importante se ve primero
y el resto se ordena detrás), **armonía** (la interfaz acompaña al contenido y
no compite con él) y **consistencia** (lo que se parece se comporta igual en
todas partes). Antes los nombraba claridad, deferencia y profundidad: es la
misma idea. Todo lo de abajo baja esos principios a cosas que se pueden
comprobar.

## Lo que mide el script (`medir.py`)

| Regla | Valor de base | Tipo de falla |
|---|---|---|
| Todo lo que se toca mide al menos 44 × 44 pt | 44 px en web; en apps solo de escritorio con mouse se puede bajar con `tactil_puntero` (no menos de 28) | `tactil` |
| Texto legible | 11 pt es el mínimo absoluto de Apple; en web, 12 px de base, y el proyecto lo sube (13 es común) | `texto_chico` |
| Contraste | 4,5:1 texto normal, 3:1 texto grande (24 px o 19 px en negrita) | `contraste` |
| Nada se sale de la pantalla ni se esconde sin aviso | sin scroll horizontal; sin contenido recortado | `desborde`, `recortado` |
| Nada tapa a nada | controles y textos no se pisan | `solape` (sospecha) |
| Controles propios, no los del sistema | `select`, fecha, hora, archivo, color, casillas sin estilo | `control_nativo` |
| Íconos de una sola familia | nada de emoji ni glifos Unicode como íconos | `glifo` |
| Todo control tiene nombre | botón de ícono con `aria-label` | `icono_sin_nombre` |
| El foco se ve | al recibirlo cambia algo a la vista | `foco_invisible` |
| Modo oscuro completo | todo cambia con el tema, nada queda a medias | `tema_a_medias` (sospecha) |
| Movimiento reducido | se mide con `prefers-reduced-motion: reduce` puesto | (las capturas salen así) |
| Consistencia | una forma por componente, la misma en todos los sistemas | `variantes`, `casi_iguales`, `distinto_por_sistema`, `mismo_rotulo_distinta_forma` |

## Lo que se juzga mirando las capturas (revisor 2, con criterio)

Para cada pantalla, en 390 y en 1366, claro y oscuro, respondé con la captura
abierta:

**Jerarquía**
- ¿Qué es lo primero que se ve? ¿Es lo más importante para quien abre esa
  pantalla? Si hay que leer todo para encontrarlo, la jerarquía falla.
- **Una acción principal por pantalla**, con aspecto de principal (relleno,
  color de acento) y en el lugar donde cae el ojo. Si hay dos que compiten,
  una sobra o una tiene que bajar a secundaria.
- Títulos con una escala corta y clara. Referencia de Apple: 34 título grande,
  28 / 22 / 20 títulos, 17 cuerpo y titulares (semibold), 16 / 15 secundarios,
  13 notas, 12 / 11 leyendas. En web se traduce a 4-6 tamaños, no a quince.
- Pesos con intención: regular para leer, semibold para lo que se busca. Evitar
  los pesos finos para texto chico.

**Armonía**
- La interfaz no compite con el contenido: fondos calmos, color solo para
  significar (estado, acento, alerta), sombras y bordes mínimos.
- **Márgenes y espacios de una escala** (múltiplos de 4 u 8). Dos espacios a 2
  px de distancia son un descuido.
- Alineación: todo apoya en una grilla. Bordes que casi coinciden se ven peor
  que bordes que no coinciden.
- Radios anidados: el interior es el exterior menos el relleno.
- Ancho de lectura: párrafos de 50-75 caracteres; tablas que usan el ancho.

**Consistencia**
- El mismo componente se ve y se comporta igual en todas las pantallas y en
  todos los sistemas: botones, campos, encabezados, tablas, diálogos, avisos.
- La misma acción se llama igual en todas partes y está en el mismo lugar.
- Los íconos son de una sola familia, del mismo trazo y tamaño, y su sentido es
  el mismo en todas partes.

**Respuesta a cada acción**
- Todo toque tiene respuesta visible enseguida: estado presionado, carga,
  resultado. Lo que tarda más de un segundo muestra progreso.
- Lo destructivo se pide confirmar con un título que dice qué se va a perder,
  el botón destructivo en rojo y con el verbo ("Eliminar 3 movimientos"), y
  Cancelar como salida fácil. Mejor aún: deshacer.
- Los errores dicen qué pasó y qué hacer, junto al campo que falló.

**Navegación y modales**
- Siempre se sabe dónde se está y cómo volver. Volver hace lo que se espera.
- En celular, la navegación principal al alcance del pulgar; no más de cinco
  destinos en la barra.
- Los modales, pocos y con salida clara (botón y Esc). Un modal no abre otro.

**Formularios**
- La etiqueta siempre visible (el placeholder no es etiqueta).
- El teclado adecuado en celular (`inputmode`, `type=email/tel`).
- Validar al salir del campo, no al tipear la primera letra.

**Estados**
- Vacío: dice por qué está vacío y qué hacer. Cargando: estructura de
  marcador, no un salto. Error: qué pasó y cómo seguir.

**Accesibilidad**
- Todo se puede hacer con teclado y con lector de pantalla.
- El color nunca es la única señal (agregar ícono o texto).
- Con texto ampliado al 200 % nada se rompe ni se esconde.

**Escritura**
- Breve, en las palabras de quien usa la app, sin jerga de sistema. En
  español, mayúscula solo al principio ("Guardar cambios", no "Guardar
  Cambios").
- Botones con verbo que dice qué pasa.

## Cómo reportar algo de criterio

Igual que cualquier hallazgo: captura con la ruta, qué le pasa a la persona y
**dónde se arregla una sola vez**. "No me gusta" no es hallazgo; "la acción
principal (Registrar) queda abajo a la derecha en gris, igual que Cancelar, y en
390 hay que bajar para verla" sí.
