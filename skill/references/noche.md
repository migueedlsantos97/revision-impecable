# Modo noche

La persona se va y vuelve a la mañana. Durante ese tiempo **no hay a quién
preguntarle**: toda pregunta es una parada. Así que se decide con las reglas, y
todo lo que se decide queda escrito para que a la mañana se pueda revisar en
minutos.

## Cómo se trabaja

- **Rama propia**: `revision/<fecha>`. Un commit por tema. Nunca la principal.
- **Sin preguntas.** Ante una duda de diseño se aplica, en orden: las reglas del
  proyecto, `hig.md`, lo que ya hace la mayoría de la app. Se anota la decisión.
- **Rediseñar está permitido** cuando arreglar de a uno no alcanza. La solución
  es una y se aplica en todos los sistemas; nunca una pantalla distinta de las
  demás. Lo que no se toca sin la persona: la marca (logo, nombre, colores de
  marca), textos legales y lo que la regla del proyecto diga que es suyo.
- **Coordinación.** El agente principal no hace el trabajo fino: reparte. Los
  revisores corren en paralelo; los arreglos de un mismo componente los hace
  un solo agente (dos que tocan el mismo archivo se pisan). Cada agente que
  cambia datos usa su propia instancia.
- **Vuelta completa** después de cada tanda: medir todo, tests, funciones del
  mapa. Lo que se rompió con un arreglo se arregla antes de seguir o se revierte.
- **Tope**: las `vueltas` del adaptador (5 por defecto). Si en dos vueltas
  seguidas no baja la cantidad de hallazgos, se para: el procedimiento está
  dando vueltas sobre lo mismo y la persona tiene que mirar.

## El registro de decisiones

Un TSV en `.claude/revision/salida/<fecha>/decisiones.tsv`, una fila por
decisión, nunca se edita para atrás (un error se corrige con una fila nueva):

```
hora	fase	decisión	por qué	evidencia	resultado
02:14	diseño	unifiqué el botón primario en suite.css (44 px, radio 12)	había 5 formas en 3 sistemas	commit 3a9f1c2, montaje-antes/despues	medir: variantes 5→1
02:40	funciones	revertí el cambio de alta de stock	la baja dejó de descontar	tests/test_moves.py rojo	revertido, anotado para la mañana
```

Evidencia es un puntero (commit, ruta de captura, `archivo:línea`), nunca un
párrafo.

## Lo que encuentra la persona a la mañana

1. `docs/revision-<fecha>.md` con el resumen arriba: qué se arregló, qué se
   rediseñó, qué quedó y por qué.
2. **"Para tu ojo"**: lo que necesita a la persona, ordenado, cada cosa con su
   captura de antes y después. Arriba van los rediseños y las decisiones de
   gusto que se tomaron solos.
3. La rama con los commits, lista para revisar por muestreo y mergear.
4. Lo que no se pudo hacer sin cruzar un límite (deploy, datos reales, la marca),
   escrito como pendiente con el paso exacto.

## Antes de irse

Para que la noche no se trabe en un permiso, la sesión tiene que poder correr
comandos, editar y commitear sin pedir aprobación (modo automático o permisos
del proyecto). Si no puede, decíselo a la persona antes de que se vaya, no a
las tres de la mañana.
