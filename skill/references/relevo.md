# Checkpoint y relevo (sobrevivir al límite de contexto y de tokens)

Una corrida larga muere cuando se llena el contexto o se acaba el presupuesto.
Para que no se pierda nada, el estado vive **en disco**, no en la cabeza del
agente. Vale en cualquier modo; en modo noche es obligatorio.

## `checkpoint.json`

`.claude/revision/salida/<fecha>/checkpoint.json` (lo escribe `scripts/presupuesto.py`;
si no está disponible, a mano con estos campos). Se reescribe **antes de cada
tanda (pasos 4-7) y tras cada commit de arreglo**:

```json
{
  "fase": "arreglos", "vuelta": 2, "rama": "revision/2026-01-10", "worktree": "../rev-2026-01-10",
  "estado": "running",
  "abiertos": [{"id": "H-014", "cajon": 1, "veredicto": "CONFIRMADO", "dueno": "agente-3"}],
  "commits": ["3a9f1c2"], "ultima_medicion_ok": "salida/2026-01-10/v2/informe.json",
  "proximo_paso": "refutar H-015..H-019, luego arreglar H-014 en la hoja común",
  "no_rehacer": ["unificar botón primario (hecho, 3a9f1c2)"],
  "gastado": {"tokens": 410000, "minutos": 95}, "presupuesto": {"tokens": 1500000, "minutos": 240},
  "escala": "ligero"
}
```

`estado`: `running`, `paused`, `done`, `aborted`. Evidencia por puntero (commit,
ruta), nunca párrafos.

## Punto seguro

Solo se corta o releva en un **punto seguro**, que exige todo a la vez:
1. el paso en curso está terminado **y verificado** (medición y tests corridos);
2. no hay subagentes ni procesos propios vivos (los que levantó la corrida se
   apagan por PID; nunca por nombre de imagen);
3. el trabajo está commiteado (un commit `wip:` si hace falta, con una línea en
   el cuerpo si el árbol quedó roto);
4. el `checkpoint.json` está al día.

Si no hay punto seguro: terminar el paso en curso, **no empezar el siguiente**,
y recién ahí cortar.

## Cuándo parar y relevar

`scripts/presupuesto.py decidir` devuelve `seguir`, `degradar`, `pivotar` o
`parar` (ver `umbrales.md`). Además, relevar cuando el contexto de la sesión
pasa de ~60 % o queda menos del 15 % del presupuesto, o al cerrar un bloque
(una tanda completa con la medición limpia = punto seguro natural).

## Cómo relevar

1. Llegar a un punto seguro; commit `wip:` si queda algo sin commitear. Nunca
   push, nunca merge.
2. Escribir `relevo.md` junto al checkpoint: objetivo, hecho, falta, **próximo
   paso exacto**, decisiones y por qué, qué NO rehacer, qué espera de la persona
   (si hay algo), cómo levantar la instancia y entrar. Si ya existe un
   `relevo.md`, **leerlo antes de escribir** (no se pisa a ciegas).
3. Poner `estado: "paused"`.
4. Si el entorno permite abrir una sesión nueva, abrirla con: «leé
   `relevo.md` y `checkpoint.json` de `<ruta>` y seguí». En modo acompañado, avisar
   a la persona en dos líneas **antes** y esperar su OK. En modo noche se hace sin
   preguntar. Si no se puede abrir otra sesión, el informe de la mañana dice
   exactamente cómo retomar.
5. La sesión vieja no se borra ni se archiva.

## Cómo reanudar

Al arrancar, si existe `checkpoint.json` con `estado` distinto de `done`:
1. leer `relevo.md` y el checkpoint; **no re-derivar** lo ya hecho;
2. comprobar el entorno: `git status` limpio o solo el `wip:`, rama y worktree
   correctos, `doctor` en verde (la instancia puede haber muerto);
3. leer `decisiones.tsv` hasta la última fila y verificar que el último commit
   coincide con el checkpoint;
4. ejecutar el `proximo_paso`; al terminar de consumir el relevo, borrarlo y
   poner `estado: "running"`.

Un relevo contradictorio con el repo (el commit no existe, la rama cambió) es un
hallazgo: se anota y se reconstruye el estado desde `git log` y `decisiones.tsv`,
no se sigue a ciegas.
