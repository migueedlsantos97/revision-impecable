# Evals de la skill

Comprueban que un agente que sigue la skill encuentra los defectos sembrados, no
inventa defectos en la pantalla limpia y dice con honestidad qué miró. Se corren
después de un cambio importante a la skill, no en cada revisión.

## Una vuelta

1. Copiar `casos/pantalla-{a,b,c}` a carpetas con nombre neutro (`trabajo-1..3`
   en un directorio temporal). El ejecutor no ve `clave.md` ni `resultados/`.
2. Un subagente por pantalla, de un modelo **más chico** que el juez, con el
   brief de `brief-ejecutor.md` (sin las palabras eval, test ni caso).
3. Un **juez de otro modelo** recibe `clave.md`, los tres informes, las carpetas
   de capturas y la rúbrica. No ve el brief del ejecutor.
4. Promedio de los seis criterios en las tres pantallas >= 9 y ninguna falsa
   alarma grave: pasa. Si no, se edita **solo la skill** (nunca los casos ni la
   clave) y se repite. Tope: 3 vueltas. Si no llega, se escribe en
   `resultados/` qué se decidió y por qué.

Antes de la vuelta, el control barato: `medir.py` sobre las tres páginas tiene
que marcar los defectos medibles de la clave y nada propio en la pantalla c.

## Rúbrica del juez (0-10 por criterio y pantalla)

1. **Recall**: defectos sembrados encontrados / total.
2. **Precisión**: sin falsas alarmas (en pantalla-c, 10 = sin defectos graves inventados).
3. **Evidencia**: cada hallazgo cita medida, selector o captura concreta.
4. **Cobertura honesta**: lista anchos y temas mirados y no mirados.
5. **Miró capturas**: el informe describe lo que se ve, no solo números.
6. **Cierre**: dice qué quedó sin verificar.

Salida del juez: tabla por pantalla y criterio, promedio, y para cada punto < 9
qué frase de la skill faltó o confundió.

## Casos nuevos

Cada escape real que sea de un tipo nuevo se convierte en un caso sembrado:
una página mínima que lo reproduce, su línea en `clave.md` y, si es medible, la
comprobación de que `medir.py` lo marca.

---

# Evals v2: cobertura general, no solo lo ya conocido

Las tres pantallas `a/b/c` miden regresión de lo visual y medible que la skill ya conoce (el script marca 9 de sus 10
defectos). No dicen si la skill cubre el conjunto amplio de defectos. Los casos de `casos-v2/` sí apuntan a eso:
funciones, datos y permisos, teclado y lectores, textos y datos regionales, consistencia entre sistemas, web pública y
estado vivo, más un caso limpio. Cada uno es una mini app que arranca sola (Python stdlib o HTML suelto).

| Caso | Familia que ejercita | Defectos | Dorados |
|---|---|---|---|
| D tareas | Funciones, datos | 5 | D4 |
| E roles | Datos, permisos, seguridad | 5 | E4, E5 |
| F formulario | Teclado y lectores | 7 | F7 |
| G textos y regional | Textos, estados límite | 7 | G6, G7 |
| H multisistema | Consistencia entre sistemas | 6 | H6 |
| I web pública | Web pública, estado vivo | 6 | I6 |
| J limpio | Precisión | 0 | |

Las claves están en `claves-v2/<caso>.md` (solo para el juez). `verificar_casos_v2.py` arranca los servidores, abre las
páginas y confirma que **cada defecto sembrado existe de verdad** (32 comprobaciones, 31 de las 36 filas de claves); correrlo antes de usar los casos
y cada vez que se edite uno. No se prueban por script (se confirman leyendo el código del caso): E3 (CSV con fórmula), G5 (moneda sin locale), G7 (fechas ambiguas), H2 (nombres distintos de la misma acción) y H4 (dos azules).

**Dorado**: defecto que, al escribir el caso, no tenía una línea explícita en la skill. Mide generalización: si un
revisor lo encuentra sin tener el check, la skill sirve de método y no solo de lista. **Un dorado se re-verifica cada vez**:
si desde entonces la skill ganó una línea sobre eso, deja de ser dorado (anotarlo en `resultados/historial.md`) y hay que
sembrar otro. Los casos se escriben **sin mirar el SKILL.md** ni los encargos, o por alguien que no los escribió.

## Una vuelta v2

1. `python evals/verificar_casos_v2.py` (debe dar 0 fallas). Control barato: `medir.py` sobre D/F/G/H/I/J no debe marcar
   nada propio en J.
2. Copiar cada carpeta de `casos-v2/` a un directorio de trabajo con nombre neutro (`trabajo-N`). El ejecutor no ve
   `claves-v2/`, `resultados/` ni este archivo. Los casos con `server.py` se arrancan con `python server.py <puerto>`
   (solo se mata por PID propio, nunca por nombre de imagen).
3. **Cada caso se corre dos veces**, en carpetas distintas: **sin pista** (brief de `brief-ejecutor.md`) y **con pista**
   (mismo brief más una línea: "Prestá especial atención a ..." con la frase de `Pista (eje 2)` de la clave).
4. Un juez de otro modelo, más grande que el ejecutor, recibe la clave, los informes y la rúbrica de abajo. No ve el brief.
5. Se corre `python evals/filtrar_privacidad.py` sobre los informes antes de archivarlos en `resultados/`.

## Puntuación v2 (dos ejes más precisión)

Pesos de la clave: grave 3, medio 2, menor 1. `R(x)` = suma de pesos encontrados / suma de pesos sembrados.

- **Eje 1, cobertura general (65 %)**: `R` del ejecutor **sin pista**, promediado por familia (cada familia pesa igual, así
  la visual no se come el puntaje). Se reporta aparte `R_dorados` (solo dorados): es la métrica de generalización.
- **Eje 2, atención a la corrección puntual (20 %)**: con la pista, el ejecutor debe (a) hallar y resolver el defecto
  señalado (si no, 0) y (b) **no perder cobertura**. Puntaje = `10 * (1 - caída)` donde
  `caída = max(0, R_sin_pista - R_con_pista) / R_sin_pista`, y un 0 si no atendió lo señalado. Visión de túnel (el caso
  histórico: señalaron los encabezados y el agente solo revisó encabezados) da caída alta. Mejorar con la pista no suma
  más de 10.
- **Eje 3, precisión (15 %)**: en J, 10 menos 3 por cada falsa alarma grave y 1 por cada media; en los demás casos, 10
  menos 2 por cada hallazgo afirmado que el juez no pueda reproducir (como el "activar el botón marca la casilla").
- Además, por hallazgo: evidencia (medida, selector, comando o captura) y cobertura honesta (qué no miró), 0-10 cada una,
  informativos; no entran en el total pero bajan el pase si el promedio es < 7.

Pasa si: total ponderado >= 8, `R_dorados` >= 0,5, ningún eje < 6 y J sin falsas alarmas graves. Si no pasa, se edita
**solo la skill** (nunca casos ni claves), tope de 3 vueltas, y se anota en `resultados/historial.md` qué frase de la skill
faltó. Para cada punto < 9 el juez dice qué línea de la skill faltó o confundió.
