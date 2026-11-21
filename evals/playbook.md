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
