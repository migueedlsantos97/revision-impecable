# Revisión incremental por sistema

Cuando un proyecto tiene varios sistemas montados juntos y ya están verificados,
no hace falta volver a medir todo cada vez. Se registra **qué quedó verificado,
en qué commit y con qué medidas**, y en la siguiente corrida se revisa solo lo
que cambió **más lo que lo comparte**. Si cambia un componente compartido, se
vuelve a medir todo lo que lo consume.

## Qué se guarda (en el proyecto, se versiona)

### `.claude/revision/estado/<sistema>.json`

```json
{
  "sistema": "inventario",
  "verificado_en": "<sha>", "fecha": "2026-01-10",
  "estado": "verificado",
  "archivos": {"apps/inventario/**": "<sha256 del árbol>", "compartido/hoja.css": "<sha256>"},
  "pantallas": {
    "lista@390@claro": {"fallas": 0, "variantes": {"boton": 1},
                        "baseline": "baseline/inventario/lista-390-claro.png", "hash_png": "<sha256>"}
  },
  "funciones": {"crear-pedido": {"ok": true, "commit": "<sha>"}},
  "tests": {"cantidad": 212, "ok": true},
  "contexto_hash": "<sha256 de umbrales + proyecto.json + versión de medir.py + datos de prueba>",
  "cobertura": "salida/2026-01-10/cobertura.md"
}
```

`estado`: `verificado` (cajones 1 y 2 vacíos o con motivo, cobertura completa),
`parcial` (algo no se pudo: queda anotado cuál), `vencido`. Lo escribe
`scripts/estado.py` al cerrar una corrida; **solo se actualizan los sistemas
efectivamente revisados**.

### `.claude/revision/dependencias.json`

```json
{
  "sistemas": {"inventario": {"propios": ["apps/inventario/**"], "consume": ["compartido/**"]}},
  "compartido": {"compartido/hoja.css": {"afecta": "*"},
                 "compartido/boton.js": {"afecta": ["inventario", "pedidos"]}},
  "pantallas": {"inventario": ["lista", "remito"]}
}
```

Se genera leyendo imports, `<link>` y `<script>` y se **valida**: se cambia un
token en una copia, se miden dos pantallas que dependen y una que no; [caso real #41] si la que
no dependía cambia, el mapa está incompleto y se amplía. Un archivo sin dueño
se trata como compartido.

## Cómo se decide el alcance (`scripts/alcance.py`, solo lee git)

1. `git diff --name-only <verificado_en>` (commits y árbol de trabajo, más archivos nuevos sin versionar), por sistema.
2. Archivo propio de un sistema → ese sistema, completo.
3. Archivo `compartido` → los sistemas de `afecta` (todos si `"*"`), completos.
4. Sistema **nuevo** (sin estado) → completo, más lo compartido que consume,
   comparado contra las pantallas de sus vecinos (categoría 18: consistencia).
5. Cambió `contexto_hash` (umbrales, `proyecto.json`, la herramienta de medición,
   los datos de prueba) → todos vencen.
6. Pasaron más de 90 días, o el estado es `parcial` → vence.
7. Lo no tocado queda **"vigente @sha"** en el informe, con su estado.

Salida: `alcance.json` con `revisar`, `vigentes` y el motivo (archivos) de cada
uno. `medir.py --alcance alcance.json` mide solo eso.

## Sondas y control

- **Sondas**: una pantalla por sistema se mide siempre (aunque esté vigente) para
  detectar divergencia de consistencia sin medir todo.
- **Muestreo**: en cada corrida incremental se re-mide al azar una pantalla
  "vigente"; si falla, el mapa de dependencias está mal y se amplía antes de seguir.
- **Completa obligatoria**: antes de mostrar o entregar a una persona de afuera,
  y cada vez que la revisión incremental falló el muestreo.
- **Baseline**: la comparación visual (ver `SKILL.md`, paso 7) usa el baseline del
  sistema; un sistema nuevo crea el suyo al quedar limpio.

## Cuándo pasar a incremental

Si tres corridas seguidas no bajaron el costo (minutos y tokens en
`metricas.json`) y la app no cambió en la mayoría de los sistemas, se pasa a
incremental. Sistemas nuevos se agregan sin estado: la primera corrida
los revisa completos.
