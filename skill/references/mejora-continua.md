# Mejora continua doble: la skill y la app

Cada corrida deja dos cosas mejores: **la skill pública** (lo que sirve a
cualquier proyecto) y **la app medida** (lo que solo vale en ella). La
pregunta de cada aprendizaje es *¿a quién le sirve?*, y se responde con una sola
tabla.

## Clasificación (una sola tabla, en el paso 9)

| Pregunta | Sí → | No → |
|---|---|---|
| ¿La causa es de la especificación, del navegador o de la plataforma (no de esta app)? | candidata a **general** | **proyecto** |
| ¿Se repitió en otro proyecto, o hay una prueba técnica reproducible? | sube a **general** | queda en **proyecto** (hipótesis) |
| ¿Menciona nombres, rutas, textos, cifras o reglas de marca de esta app? | **proyecto** (siempre) | — |
| ¿Es una corazonada sin repetirse? | hipótesis en `bitacora.md` | — |

Cada escape se anota con `ambito: general|proyecto` y su evidencia.

## Carril proyecto (inmediato, sin PR)

Mejora la app y el costo de la próxima pasada:
1. **Chequeo propio** en `.claude/revision/chequeos/<id>.js|py` (contrato en
   `adaptador.md`, sección 7). Se prueba que **falla con el defecto real** y que
   no dispara en lo limpio. Un chequeo escrito pero que no corre en pre-commit o en
   CI es un texto más: el paso 8 exige engancharlo (ver `SKILL.md`, paso 8).
2. **`reglas.md`** con la columna **"lo hace cumplir"** obligatoria: apunta a un
   chequeo, test o estructura. Si está vacía, la regla es deuda y se anota como tal.
3. **`funciones/`**: la función del escape (nueva o ampliada) con su recorrido y
   su prueba de efecto real.
4. **`proyecto.json`**: pantallas y estados nuevos que el escape reveló.
5. Si un humano tuvo que hacer cumplir una invariante en una revisión, **se vuelve
   chequeo** en la misma corrida (escalera: arquitectura > chequeo duro > test >
   texto blando).

## Carril skill (con PR, anonimizado)

1. Redactar `.claude/revision/candidatos/<tema>.md` con frontmatter
   `{id, regla (1-2 líneas), causa_tecnica, proyectos_que_lo_vieron, chequeo_generico}`,
   **sin** nombres, rutas, URLs, textos de interfaz ni cifras.
2. `python <skill>/scripts/promover.py .claude/revision/candidatos/<tema>.md`
   valida la anonimización y arma el borrador de PR: la regla en `references/`,
   la anécdota anonimizada en `ejemplos/casos-reales.md` y la entrada en
   `CHANGELOG.md`.
3. Se propone por PR al repo de la skill. Nunca se escribe en la copia instalada.
4. Antes de subir: «¿se entiende y aplica en un proyecto del que no sé nada?». Si
   no, es del proyecto.

## Métricas por corrida (`.claude/revision/metricas.json`, acumulativo)

`fecha`, `escala`, `pantallas_en_mapa`, `funciones_en_mapa`,
`funciones_con_test`, `chequeos_propios`, `escapes_previos`,
`hallazgos_cajon_1_2`, `silenciamientos`, `minutos`, `tokens`.

**Criterio**: la app queda *más cubierta* (mapa y chequeos suben, `escapes` no
sube, `funciones_con_test` no baja). Si **tres corridas seguidas no bajan el
costo** (minutos y tokens por pantalla), se pasa a revisión incremental
(`incremental.md`). Los `silenciamientos` (tipos desactivados, marcas
`data-revision-ok`) cuentan: una baja de hallazgos con alza de silenciamientos
no es una mejora.
