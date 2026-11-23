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
| Revisores que corrieron | <N de 7> (el 7 solo si es web pública) |
| Categorías de cobertura sin marca | 0 |
| Fallas medidas | <primera vuelta> → <última vuelta> |
| Vueltas | <N> |
| Hallazgos confirmados | <N> |
| Descartados al refutar | <N> |
| Arreglados | <N> |
| Para tu ojo | <N> |
| Tests | <antes> → <después> |
| Escapes de la revisión anterior | <N> |

## Cobertura

Una fila por categoría de `SKILL.md` paso 3. Ninguna puede quedar vacía.

| # | Categoría | Marca (MEDIDO / REVISADO / N/A) | Quién y prueba, o motivo del N/A |
|---|---|---|---|
| 1 | funciones y datos | REVISADO | revisor 1, tabla de funciones |
| 2 | permisos | | |
| 3 | formularios y validación | | |
| 4 | teclado y foco | | |
| 5 | lector de pantalla y estructura | | |
| 6 | contraste, color y zoom 200 % | | |
| 7 | tamaños y reflujo | | |
| 8 | estados (vacío, carga, error, lento, offline, volumen) | | |
| 9 | tablas, listas y gráficos | | |
| 10 | subida y descarga de archivos | | |
| 11 | tema oscuro, contraste forzado, movimiento reducido | | |
| 12 | textos, idioma, formatos, zonas horarias | | |
| 13 | red y seguridad de front | | |
| 14 | rendimiento y estabilidad de carga | | |
| 15 | metadatos y cómo se comparte (si es pública) | | |
| 16 | impresión y exportes | | |
| 17 | compatibilidad de navegadores | | |
| 18 | consistencia entre pantallas y sistemas | | |
| 19 | enlaces, 404, deep links y Atrás | | |
| 20 | superficies no web (API/CLI) | | |

## Correcciones del usuario

Si la persona señaló defectos concretos durante la corrida. Cada uno es una
señal más: **no sustituye a la cobertura**. Si no hubo, escribir "ninguna".

| Caso señalado | Clase (genérica) | Instancias halladas / arregladas | Chequeo creado (falla con el defecto) | Clases vecinas miradas (mín. 2) |
|---|---|---|---|---|

<Si el pedido era solo esto, decirlo: "se corrigió X y su clase; el resto no se revisó".>

## Para tu ojo

<Lo que necesita a la persona, ordenado por importancia. Primero los rediseños y
las decisiones de gusto que se tomaron solos. Cada uno con captura de antes y
después y el commit para revertirlo si no convence.>

| Qué | Antes / después | Por qué así | Commit |
|---|---|---|---|

## Cajón 1 — Lo que le costaba al usuario

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|
| <qué le pasa a una persona, no qué regla se incumple> | `archivo:línea` | CONFIRMADO | arreglado en `<commit>` |

## Cajón 2 — Lo que delataba falta de oficio

| Qué se rompía | Dónde | Veredicto | Estado |
|---|---|---|---|

## Cajón 3 — Lo que no nota nadie

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

**Qué cambió en el proyecto y qué candidatos a la skill se redactaron**

- Agregado en `.claude/revision/` (reglas, tests, adaptador): <qué y aprendido de qué>
- Afinado: <qué chequeo estaba mal redactado y cómo quedó>
- Borrado: <qué chequeo llevaba tres corridas dormido>
- Candidatos a la skill (`.claude/revision/candidatos/`, sin nombres, rutas ni cifras): <lista; no se escribe en la copia instalada>

**Hipótesis abiertas**

<Corazonadas sin evidencia suficiente. Esperan repetirse en otro proyecto antes
de convertirse en check.>

**Dónde sigue siendo ciega**

<Lo más honesto del informe. Qué clase de defecto este procedimiento todavía no
puede encontrar, y qué haría falta para poder.>
