# Cambios de la skill (changelog razonado)

Este archivo registra **cómo evolucionó la skill y por qué**. No describe
proyectos ni clientes. La bitácora de cada corrida (qué alcance tuvo, cuántos
hallazgos, qué escapó) vive **en el proyecto revisado**:
`.claude/revision/bitacora.md`. Los casos que justifican reglas están
anonimizados en `ejemplos/casos-reales.md`.

La medida de si la skill funciona no es cuántos hallazgos trajo, sino cuántos
**escapes** hubo: defectos que alguien encontró después de que la revisión dijo
"listo". Si bajan corrida tras corrida, la skill aprende.

## Formato de la bitácora de un proyecto (`.claude/revision/bitacora.md`)

```markdown
## <fecha>
- **Alcance**: revisores que corrieron y filas de cobertura N/A con motivo.
- **Hallazgos**: N confirmados, N plausibles, N descartados. Por cajón: N / N / N.
- **Escapes de la corrida anterior**: uno por línea, con qué chequeo debió cazarlo.
- **Cambios**: qué se agregó, afinó o borró (en reglas.md, tests o candidatos).
- **Hipótesis**: corazonadas sin evidencia suficiente todavía.
- **Chequeos dormidos**: los que no dispararon. Al tercero seguido, se borran.
```

Reglas: con nombre y apellido ("el encargo 3 no decía que un botón dentro de un
label…", no "faltó revisar el foco"); una corazonada es hipótesis hasta que se
repite; los chequeos dormidos se borran con constancia; un escape vale más que
diez hallazgos.

## Cómo sube un aprendizaje a la skill

1. Candidato en `.claude/revision/candidatos/<tema>.md` del proyecto, sin
   nombres de cliente o producto, rutas, URLs, textos de interfaz ni cifras.
2. Sube solo si se repitió en otro proyecto, o fue un escape real con causa
   técnica demostrable (especificación, comportamiento del navegador).
3. Nunca se escribe en la copia instalada de la skill. Se propone por PR al
   repo: la regla en 1-2 líneas en `references/`, la anécdota anonimizada en
   `ejemplos/casos-reales.md` con el siguiente número `[caso real #n]`, y una
   entrada acá.
4. Antes de subir: releer la regla y preguntarse "¿se entiende y aplica en un
   proyecto del que no sé nada?". Si no, es del proyecto.

## Historial

### v2.1 — cobertura general y regla de corrección del usuario
- **Por qué**: la v1 reaccionó a una indicación puntual del usuario revisando
  solo ese tema y dejó de lado el resto; y varias reglas llevaban anécdotas,
  nombres y supuestos de stack del proyecto donde nacieron.
- **Agregado**: paso "Corrección del usuario" (arreglar el caso, barrer su
  clase, volverlo chequeo, **volver a la cobertura completa**); paso 3
  "Cobertura sistemática" con `cobertura.md` de 20 categorías que bloquea la
  salida; encargos nuevos o ampliados (formularios con tabla de casos,
  teclado, red y fallos, seguridad de front, impresión y exportes, movimiento
  reducido, contraste forzado y zoom 200 %, tablas grandes, gráficos, subida de
  archivos, estados de carga, enlaces/404/deep links, superficies no web);
  `umbrales.md` como tabla única de números, anchos y criterios de parada;
  "Descubrimiento en 10 minutos" y campos nuevos del adaptador; flujo para que
  un aprendizaje suba a la skill sin contaminarla; refutador independiente y
  muestreo con más de 30 hallazgos; glosario ES/EN y descripción bilingüe.
- **Afinado**: un solo conteo de revisores (siete); numeración de pasos 0-9;
  cajones con nombre; `doctor` definido; modo noche aborta con informe si no
  puede construir el adaptador; lecturas GET de sitios públicos permitidas;
  un contexto de navegador por revisor; encargos independientes del idioma y
  del stack.
- **Movido**: todas las anécdotas a `ejemplos/casos-reales.md`; las bitácoras
  por corrida, al proyecto.
- **Borrado**: la historia por proyecto que estaba en este archivo.
- **Hipótesis abiertas**: que la tabla de cobertura reduzca los escapes en
  categorías que ningún revisor tenía (impresión, movimiento reducido, tablas
  de volumen); se confirma o cae en las primeras corridas reales.

### v2 — medición determinística
- Script de medición con chequeos de foco, tema, recortes y consistencia entre
  pantallas; siete revisores en lugar de once; adaptador por proyecto; modo
  noche; estándar de base en `hig.md`; "fijar como estructura antes que texto".

### v1 — procedimiento completo manual
- Once revisores sobre una revisión hecha a mano, con rondas paralelas, refutación
  de hallazgos y aprendizaje por escapes.
