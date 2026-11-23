# Revisión nocturna — <proyecto> — <fecha>

> Máximo 40 líneas. Se entiende solo, sin haber estado en la sesión.

**Estado**: <terminado | parcial | abortado> — <una frase: por qué>
**Rama / worktree**: `revision/<fecha>` · `../rev-<fecha>` · **Escala**: <ligera/ampliada/completa>
**Gastado**: <minutos> min · <tokens> tokens de <presupuesto> · vueltas <n>/<tope>

| Arreglado | Necesita tu ojo | No verificado |
|---|---|---|
| <N> (cajón 1: <n>, cajón 2: <n>) | <N> | <N> (motivo en la lista de abajo) |

## Decisiones de gusto (antes / después)
- <qué se decidió solo> — antes: `<captura>` · después: `<captura>` · regla aplicada: <cuál>

## Para revisar y mergear
```bash
git log --oneline <base>..revision/<fecha>
git diff --stat <base>..revision/<fecha>
git merge --no-ff revision/<fecha>   # lo hacés vos; la corrida no mergea ni pushea
```
Retomar si quedó parcial: leer `.claude/revision/salida/<fecha>/relevo.md`.

## No se tocó (límite) y por qué
- <ruta o acción> — <motivo: marca, datos reales, deploy, hook que bloquea…> — paso exacto: <...>

## No verificado
- <pantalla/función/rol> — <qué faltó para poder verificarla>

## Atención
> Escrita por un revisor **distinto** del que arregló (modelo fuerte). Leé esto primero.
- <cambio grande sin captura / revert / fila invalidada / silenciamiento nuevo> — `decisiones.tsv` fila <n>
- <lo que merece mirarse a mano>

Cadena de revisores: <ok | filas invalidadas: …> · Silenciamientos: <antes> → <después>
