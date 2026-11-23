# Modo noche

La persona se va y vuelve después. Durante ese tiempo **no hay a quién
preguntarle**: toda pregunta es una parada. Así que se decide con las reglas, y
todo lo que se decide queda escrito para revisarlo en minutos.

## Antes de arrancar (aborta con informe)

1. ¿Existe adaptador? Si no, constrúyelo con `adaptador.md` (descubrimiento).
2. ¿La instancia arranca y responde `doctor`? ¿Se puede entrar con cada rol?
3. Si **no se puede construir un adaptador que arranque** (checkout roto, falta
   una dependencia que no se versiona, datos que no se pueden sembrar), **no se
   inventa nada ni se revisa a ciegas**: se escribe `docs/revision-<fecha>.md`
   con qué se intentó, el error exacto, qué falta y el primer paso para
   destrabarlo, se commitea en la rama y se termina.
4. Pantallas con login por SSO/2FA que no se puede automatizar: se usa
   `storage_state` si la persona lo dejó; si no, se anotan como no revisadas.

## Cómo se trabaja

- **Rama propia** `revision/<fecha>`. Un commit por tema. Nunca la principal.
- **Sin preguntas.** Ante una duda de diseño se aplica, en orden: reglas del
  proyecto, `hig.md`, lo que ya hace la mayoría de la app. Se anota la decisión.
- **Rediseñar está permitido** cuando arreglar de a uno no alcanza, con una
  solución única en todos los sistemas. No se toca sin la persona: la marca
  (logo, nombre, colores de marca), textos legales ni lo que la regla del
  proyecto declare suyo (`no_tocar` del adaptador).
- **Coordinación.** El agente principal reparte: revisores en paralelo, cada uno
  en su contexto de navegador; los arreglos de un mismo componente los hace un
  solo agente. La refutación la hace un agente distinto del que arregla.
- **Vuelta completa** tras cada tanda: medir todo, tests, funciones del mapa. Lo
  que se rompió se arregla antes de seguir o se revierte.
- **Criterios de parada**: los de `umbrales.md` (tope de vueltas, estancamiento
  en dos vueltas seguidas, límites de tiempo y capturas).
- Solo lecturas GET a sitios públicos; nunca producción con escritura.

## El registro de decisiones

Un TSV en `.claude/revision/salida/<fecha>/decisiones.tsv`, una fila por
decisión, nunca se edita para atrás (un error se corrige con otra fila):

```
hora	fase	decisión	por qué	evidencia	resultado
02:14	diseño	unifiqué el botón primario en la hoja común (44 px, radio 12)	había 5 formas en 3 secciones	commit 3a9f1c2, capturas antes/después	medir: variantes 5→1
02:40	funciones	revertí el cambio del alta de pedidos	la cantidad dejó de descontarse	tests/test_pedidos rojo	revertido, anotado para la mañana
```

Evidencia es un puntero (commit, ruta de captura, `archivo:línea`), no un párrafo.

## Lo que encuentra la persona a la mañana

1. `docs/revision-<fecha>.md` con el resumen arriba: qué se arregló, qué se
   rediseñó, qué quedó y por qué, la tabla de cobertura y "Correcciones del usuario".
2. **"Para tu ojo"**: lo que necesita a la persona, ordenado, con captura de
   antes y después. Arriba, los rediseños y decisiones de gusto tomados solos.
3. La rama con los commits, lista para revisar por muestreo y mergear.
4. Lo que no se pudo sin cruzar un límite (deploy, datos reales, la marca),
   como pendiente con el paso exacto.

## Antes de irse

Para que la noche no se trabe en un permiso, la sesión tiene que poder correr
comandos, editar y commitear sin pedir aprobación (modo automático o permisos
del proyecto). Si no puede, decíselo a la persona antes de que se vaya.
