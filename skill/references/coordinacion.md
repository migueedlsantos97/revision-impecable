# Coordinación: escala, modelos, paralelismo, cadena y mantenimiento

## 1. Escala gradual (el costo se gana, no se asume)

No se lanzan muchos agentes mientras no se confía en lo que devuelve uno. La
corrida empieza **ligera** y sube solo si hay motivo.

| Escala | Qué corre | Cuándo |
|---|---|---|
| **Ligera** (por defecto) | `medir.py` + 2 revisores: **Funciones** (1) y **Diseño y consistencia** (2) | siempre al empezar |
| **Ampliada** | se suman los revisores cuyo tema aparece en la medición (3 si hay fallas de foco/nombres/controles; 4 si hay textos o formatos dudosos; 5 si hay desbordes o estados; 6 si hay datos, permisos o formularios) | la medición o el tamaño lo justifican |
| **Completa** | los 7 (el 7 solo si `"publica":true`) | pedido explícito de la persona ("revisá todo", "antes de mostrarlo"), primera revisión de un proyecto, entrega a terceros, o `escapes` > 0 en la corrida anterior |

Criterios de tamaño que justifican subir: más de ~10 pantallas, más de 2 roles,
formularios que escriben datos, o un componente compartido tocado. Cada revisor
nuevo debe poder nombrar qué filas de `cobertura.md` aporta; la **cobertura
completa** (paso 3) no se negocia: lo que ningún revisor ligero cubre se marca
**N/A con motivo "escala ligera"** y se audita en la corrida siguiente.

**ROI**: gastar al principio en estructura (componentes compartidos, chequeos,
tests) que hace que hasta el agente más simple acierte, y no en más revisores.
Un revisor extra es una compra repetida; un chequeo es una compra única.

## 2. Modelo por rol

| Rol | Modelo mínimo suficiente |
|---|---|
| Mecánico: medir, resumir salidas, ordenar capturas, escribir el checkpoint | el más chico |
| Revisores, arreglos, mantenimiento del mapa | el intermedio |
| Refutar hallazgos del cajón 1 y la revisión final de la rama / la lectura independiente del rastro | el más fuerte |

Subagentes siempre con **punteros a archivos**, no texto pegado; informes
cortos (≤ 130 líneas); en segundo plano cuando se pueda; cada uno con su
contexto de navegador. Y en todo brief de subagente: nunca matar procesos por
nombre de imagen, solo por el PID propio.

## 3. Arreglos en paralelo: propiedad exclusiva y worktrees

- Antes de repartir, el agente principal parte los hallazgos aceptados en
  **zonas de archivos disjuntas**; cada zona tiene **un solo dueño**. Si dos
  hallazgos tocan el mismo archivo, van al mismo dueño y en serie.
- El componente compartido lo toca **un solo agente**, primero; las zonas que lo
  consumen esperan a que termine.
- Cada dueño trabaja en su propio `git worktree` (o rama) con su instancia y
  puerto; un commit por tema, solo con `git add <archivos de su zona>` (nunca
  `-A`). El principal integra en orden, corre la medición completa y revierte lo
  que rompa.
- Nadie edita fuera de su zona: un hallazgo ajeno se anota en el checkpoint.

## 4. Verificar la cadena de los revisores (que miraron lo que dicen)

Un hallazgo puede ser correcto y el revisor, igual, no haber mirado: es la forma
más cara de falsa cobertura. Antes de dar por cubierta una fila de
`cobertura.md`:
1. Leer la **transcripción** o el registro de herramientas del revisor (no su
   autoinforme): qué archivos abrió, qué capturas vio, qué comandos corrió.
2. Contrastar con lo que declara: cada pantalla o función citada debe tener una
   apertura real. [caso real #39] Una afirmación sobre código sin que haya leído ese archivo, o
   sobre una pantalla sin captura abierta, **invalida esa fila** (vuelve a
   `sin marca` y se re-despacha el revisor).
3. Si la transcripción no está disponible, se pide al revisor la lista de
   archivos/capturas abiertos y se verifica contra los timestamps de `salida/`.
4. Registrar en `decisiones.tsv` el resultado ("cadena ok" / "cadena rota: X").
5. Mismo principio para el agente principal: sospechar del método de
   observación antes que del sistema.

## 5. Pase de mantenimiento del mapa de funciones

Un mapa de funciones envejece al primer cambio. Pase periódico (se puede
programar, p. ej. diario) con resultado explícito:

1. **Higiene del índice**: entradas faltantes, sobrantes, duplicadas o muertas.
2. **Onda de lectura**: un subagente de solo lectura **por función**, en
   paralelo; cada uno explica desde el código cómo anda, marca desvíos con cita
   `archivo:línea` y devuelve una receta de verificación en vivo. No manejan la
   app ni editan.
3. **Reconciliar**: fusionar recetas en la menor cantidad de estados; revisar
   cambios recientes en busca de funciones que no estén en el mapa (se exige una
   ruta concreta para declararla faltante).
4. **Pase vivo**: el coordinador maneja la app y ejercita cada función una vez,
   aunque el código se vea limpio.
5. **Clasificar**: descripción equivocada → se corrige el mapa; algo que el
   recorrido no puede manejar → se arregla el recorrido; la app hace algo roto →
   se **reporta**, no se tapa en el mapa.
6. **Resultado** (uno solo, se dice cuál): **clean** (todo cubierto, nada que
   cambiar), **changed** (un commit con correcciones probadas, solo en
   `.claude/revision/`; nunca código de producto) o **blocked** (qué lo frenó).
   Las notas de la pasada no se versionan.
