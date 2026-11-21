# Revisión impecable — <proyecto>

**Fecha**: <fecha> · **Revisó**: Claude Code · **Modo**: <acompañado / noche> · **Rama**: `<revision/fecha>`

> Este informe tiene que entenderse solo. Quien lo abra dentro de seis meses, sin
> haber estado en la sesión, tiene que saber qué se revisó, qué se encontró y qué
> se decidió dejar.

## Resumen

<Dos o tres frases. Qué se revisó, cuál fue el hallazgo más caro y qué queda
pendiente de decisión de la persona. Nada de adjetivos.>

| | |
|---|---|
| Revisores que corrieron | <N de 7> |
| Fallas medidas | <primera vuelta> → <última vuelta> |
| Vueltas | <N> |
| Hallazgos confirmados | <N> |
| Descartados al refutar | <N> |
| Arreglados | <N> |
| Para tu ojo | <N> |
| Tests | <antes> → <después> |
| Escapes de la revisión anterior | <N> |

## Para tu ojo

<Lo que necesita a la persona, ordenado por importancia. Primero los rediseños y
las decisiones de gusto que se tomaron solos. Cada uno con captura de antes y
después y el commit para revertirlo si no convence.>

| Qué | Antes / después | Por qué así | Commit |
|---|---|---|---|

## Lo que le costaba al usuario

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|
| <qué le pasa a una persona, no qué regla se incumple> | `archivo:línea` | CONFIRMADO | arreglado en `<commit>` |

## Lo que parecía de principiante

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|

## Lo que no nota nadie

<Lista corta. Lo que se arregló y lo que se dejó, con el motivo.>

## Decisiones de gusto

<En modo acompañado: lo que no se tocó, con qué se podría cambiar y qué opciones
hay. En modo noche: lo que se decidió solo, con la regla que se aplicó.>

## Lo que se descartó

| Sospecha | Por qué se cae |
|---|---|

<Queda escrito para que nadie lo vuelva a levantar.>

## Lo que no se revisó

<Revisores que no corrieron y por qué. Cosas que solo se pueden comprobar en un
dispositivo real o con el cliente delante. Sé explícito: lo no revisado tiene
que quedar visible, no escondido.>

---

## Autoevaluación

<Esta sección es sobre el procedimiento, no sobre el sitio. Es lo que hace que la
próxima revisión sea mejor que esta.>

**Escapes de la revisión anterior**

| Qué se escapó | Qué revisor o chequeo debió cazarlo | Por qué no lo hizo | Qué chequeo o línea lo caza ahora |
|---|---|---|---|

**Qué cambió en la skill (general) y en el adaptador (del proyecto)**

- Agregado: <qué check, en qué archivo, aprendido de qué>
- Afinado: <qué check estaba mal redactado y cómo quedó>
- Borrado: <qué check llevaba tres corridas dormido>

**Hipótesis abiertas**

<Corazonadas sin evidencia suficiente. Esperan repetirse en otro proyecto antes
de convertirse en check.>

**Dónde sigue siendo ciega**

<Lo más honesto del informe. Qué clase de defecto este procedimiento todavía no
puede encontrar, y qué haría falta para poder.>
