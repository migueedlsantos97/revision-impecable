# Modo noche (autonomía total)

La persona se va y vuelve después. Durante ese tiempo **no hay a quién
preguntarle**: toda pregunta es una parada. Se decide con las reglas, todo lo
decidido queda escrito para revisarlo en minutos, y la corrida **sobrevive** al
límite de contexto y de tokens (`relevo.md`).

## 1. Ganarse el loop (requisitos antes de irse)

Un loop autónomo sobre algo que no se entiende solo produce trabajo sin revisar
más rápido. Los cuatro requisitos, todos:
1. **Se hizo una vez a mano**: `doctor` en verde, `medir.py --rapido` limpio o
   con fallas conocidas, y una función del mapa recorrida de punta a punta con
   el efecto real comprobado.
2. **El agente tiene las señales** que usaría una persona: capturas, consola,
   red, datos guardados, tests (con su número inicial anotado).
3. **Cada etapa prueba su trabajo y puede frenar la línea**: ningún arreglo
   queda sin medición posterior; un chequeo rojo detiene la tanda.
4. **Se leyeron transcripciones de revisores** (`coordinacion.md`, §4) y las
   fallas repetidas ya son chequeos, no texto.

Si falla alguno: se corre **acompañado**, o se aborta con informe.

## 2. Abortar con informe (antes de empezar)

1. ¿Existe adaptador? Si no, construirlo con `adaptador.md`; `medir.py --validar`
   debe pasar (doctor, login por rol, una pantalla).
2. ¿La instancia arranca y se puede entrar con cada rol?
3. Si **no se puede** (checkout roto, dependencia que no se versiona, datos que
   no se pueden sembrar): no se inventa nada ni se revisa a ciegas. Se escribe
   `docs/revision-<fecha>.md` con qué se intentó, el error exacto, qué falta y el
   primer paso para destrabar, se commitea en la rama y se termina.
4. SSO/2FA no automatizable: `storage_state` si la persona lo dejó; si no, esas
   pantallas se anotan como no revisadas.

## 3. Contrato nocturno (seguridad)

- **Worktree y rama propios**: `git worktree add ../rev-<fecha> -b revision/<fecha>`.
  Nunca se trabaja en el árbol de la persona ni en la rama principal.
- **Pre-push**: un hook en el worktree (`core.hooksPath` propio) que **rechaza**
  push a `main`, `master` o la rama de producción y cualquier `--force`. La corrida
  no pushea; el hook protege aunque algo se confunda.
- **`no_tocar` verificado**: antes de cada commit se corre `git diff --name-only
  --cached` y se compara con `no_tocar` del adaptador (rutas, marca, textos
  legales); si coincide, el commit se cancela y se anota como pendiente.
- **Entorno de prueba obligatorio**: `REVISION_ENTORNO=prueba`, URL en localhost o
  lista blanca del adaptador; si no, `medir.py` y los revisores abortan. Nunca
  producción con escritura, nunca datos reales, nunca deploy.
- **Datos sembrados de cero en cada vuelta**: se levanta la instancia con la base
  de prueba recién sembrada, para que una vuelta no dependa de lo que ensució la
  anterior ni de lo que hizo otro revisor.
- **Procesos**: solo se apagan los que levantó la corrida, por PID propio.
- **Hooks que bloquean** (compuerta de commit, lint, pre-commit): no se saltean
  (nada de `--no-verify`). Se arregla la causa si está dentro del alcance; si no,
  el commit queda como `wip:` en la rama con la nota "bloqueado por <hook>" y se
  pasa a la siguiente zona. Un hook que pide credenciales o red externa se anota
  como pendiente para la persona.
- Secretos: nunca se escriben en el repo. Lecturas GET a sitios públicos: sí.

## 4. Cómo se trabaja

- **Sin preguntas.** Ante una duda de diseño se aplica, en orden: reglas del
  proyecto, `hig.md`, lo que ya hace la mayoría de la app. Se anota la decisión.
- **Pausar solo lo irreversible** (deploy, datos, borrado, marca): se anota como
  pendiente; todo lo demás es reversible y se hace.
- **Rediseñar está permitido** cuando arreglar de a uno no alcanza, con una
  solución única en todos los sistemas. No se toca sin la persona: la marca, los
  textos legales ni lo que `no_tocar` declare.
- **Escala**: se empieza ligero y se amplía según `coordinacion.md`. **Arreglos en
  paralelo** con propiedad exclusiva de archivos y worktrees (`coordinacion.md`, §3).
- **Un cambio, una medición, keep o revert**: cada arreglo se mide contra la
  vuelta anterior y las pruebas; si no baja lo que debía bajar o rompe algo, se
  revierte y se anota. Lo que "quizás ayude" no se queda.
- **Hallazgos colaterales**: si apoyan el objetivo (un chequeo roto, un falso
  positivo, un mapa viejo) son de la corrida; los arreglos fuera de alcance van
  en un commit aparte.
- **Presupuesto**: `scripts/presupuesto.py` lleva tokens, minutos y vueltas;
  decide `seguir`, `degradar` (modo `--rapido`, sin revisor 7), `pivotar` o
  `parar` (`umbrales.md`).
- **Checkpoint** antes de cada tanda y tras cada commit (`relevo.md`). Con el
  contexto lleno o el presupuesto bajo, se llega a un punto seguro y se releva.

## 5. El registro de decisiones

`.claude/revision/salida/<fecha>/decisiones.tsv`, una fila por decisión o
intento; nunca se edita para atrás (un error se corrige con otra fila):

```
hora	fase	decisión	por qué	antes	después	delta	tests	veredicto	evidencia
02:14	diseño	unifiqué el botón primario en la hoja común	5 formas en 3 sistemas	variantes=5	variantes=1	-4	212/212	kept	commit 3a9f1c2, capturas antes/después
02:40	funciones	cambié el alta de pedidos	la cantidad quedó mal	fallas=3	fallas=4	+1	210/212	reverted	tests/test_pedidos rojo
03:05	cadena	revisor 3 sin abrir el menú móvil	declaraba haberlo visto	—	—	—	—	fila invalidada	transcripción, sin captura del menú
```

`veredicto`: `kept`, `reverted`, `pendiente`, `fila invalidada`. Evidencia es un
puntero (commit, ruta de captura, `archivo:línea`), no un párrafo.

## 6. Cuándo se para

- **Predicado de salida** (el mismo de `SKILL.md`, "Criterio de salida"): cajones
  1 y 2 vacíos o con motivo, cobertura completa, medición limpia en la última
  vuelta, tests verdes y con más pruebas que al empezar, **sin aumento de
  silenciamientos**.
- **Meseta**: dos vueltas seguidas sin bajar la métrica → **pivotar una vez**
  (otro revisor, otra técnica, releer el origen) y recién si la siguiente vuelta
  tampoco baja, **parar** con informe. Nunca relajar el predicado para dar por
  hecho.
- **Salida de escape**: tope de horas (`limites.max_minutos`) o de tokens
  (`presupuesto`): se llega a un punto seguro, se escribe por qué se frenó y qué
  falta, y se termina. Es mejor que horas de reinterpretar el objetivo.

## 7. Lo que encuentra la persona al volver

1. **`LEEME-AL-VOLVER.md`** (plantilla en `assets/LEEME-AL-VOLVER.md`, ≤ 40
   líneas): estado (terminado / parcial / abortado y por qué), tres cifras
   (**arreglado**, **necesita tu ojo**, **no verificado**), decisiones de gusto con
   antes/después, comandos para revisar y mergear la rama, qué **no** se tocó y
   por qué, y la sección **Atención**.
2. **Atención la escribe otro revisor**, de un modelo fuerte y distinto del que
   arregló: lee `decisiones.tsv`, el diff y las transcripciones y lista lo que
   merece escrutinio (cambios grandes sin captura, reverts, filas invalidadas,
   silenciamientos nuevos). El que arregló no se evalúa a sí mismo.
3. `docs/revision-<fecha>.md` con cobertura, capturas y "Correcciones del usuario".
4. La rama con commits chicos, lista para revisar por muestreo y mergear a mano.
5. Lo que no se pudo sin cruzar un límite, como pendiente con el paso exacto.

## 8. Antes de irse

La sesión tiene que poder correr comandos, editar y commitear sin pedir
aprobación (modo automático o permisos del proyecto). Si no puede, decírselo a la
persona **antes** de que se vaya. También avisar si el entorno impide abrir una
sesión de relevo.
