# Umbrales, anchos y criterios de parada (tabla única)

Todo número que usa la skill vive acá. Si otro archivo cita uno, remite a esta
tabla. El adaptador (`proyecto.json`, `umbrales`) puede sobrescribirlos; lo que
no sobrescribe, vale lo de la columna "Base".

## Umbrales de medición

| Umbral | Base | Por qué ese número | Se puede cambiar si |
|---|---|---|---|
| Área táctil (`tactil`) | 44 × 44 px | Apple HIG: 44 pt; WCAG 2.5.5 pide 44, 2.5.8 pide 24 como mínimo absoluto | app solo de escritorio con mouse: `tactil_puntero`, nunca menos de 28 |
| Texto mínimo (`texto`) | 13 px | HIG fija 11 pt como piso absoluto; 12 px es el piso web; 13 deja margen en pantallas densas | el proyecto fija otro, nunca bajo 12 |
| Contraste texto normal | 4,5:1 | WCAG 1.4.3 AA | el proyecto exige AAA (7:1) |
| Contraste texto grande (≥24 px, o ≥19 px en negrita) | 3:1 | WCAG 1.4.3 | — |
| Contraste de bordes/íconos que son la única señal | 3:1 | WCAG 1.4.11 | — |
| Variantes por componente (`max_variantes`) | 2 | una forma base + una variante deliberada; más es decisión olvidada | sistema de diseño con más variantes declaradas |
| Zoom de texto | 200 % | WCAG 1.4.4 | — |
| Desplazamiento de layout (CLS) | ≤ 0,1 | umbral "bueno" de Core Web Vitals | — |
| Escala de espaciado | múltiplos de 4 u 8 px | grilla común; dos valores a 1-2 px son un descuido | — |
| Valores distintos de radio, tamaño de fuente, trazo | ≤ 5-6 por propiedad | más delata falta de decisión | — |

## Anchos de prueba

| Conjunto | Anchos (px) | Cuándo |
|---|---|---|
| Medición base (`anchos`) | 390, 768, 1366, 1920 | siempre; un móvil, una tablet, un portátil, una pantalla grande |
| `--rapido` | 390, 1366 | vueltas intermedias |
| Barrido de reflujo (revisor 5) | 360, 390, 768, 860, 1024, 1280, 1440 | el hueco típico está entre breakpoints |
| Alturas bajas | 1366×720, 1536×735 | héroes y bloques de alto fijo |
| Ancho real del usuario | el que dé `viewport_real` del adaptador | los cortes por reflejo (320/360/375/390/430) dejan huecos; **se pregunta en qué aparato mira** |

Un breakpoint no se elige redondo: se mide cuánto necesita el contenido y se
suma un margen.

## Criterios de parada (uno solo)

| Situación | Regla |
|---|---|
| Bucle normal 4-7 | repetir hasta que los cajones 1 y 2 estén vacíos o con motivo escrito |
| Tope de vueltas | `vueltas` del adaptador, 5 por defecto (suficiente para arreglar, volver a medir y absorber un efecto cascada) |
| Estancamiento (meseta) | si en **dos vueltas seguidas** no baja la métrica, **pivotar una vez** (otro revisor, otra técnica, releer el origen, ampliar la escala); si la vuelta siguiente tampoco baja, **parar** y informar. Una meseta no es permiso para relajar el criterio |
| Métrica de parada | no es solo "cantidad de hallazgos": cuenta junto con **silenciamientos** (`desactivar`, `data-revision-ok`, chequeos borrados), tests y cobertura. Bajar hallazgos subiendo silenciamientos no es progreso [caso real #40] |
| Regresión | un arreglo que rompe otra cosa se arregla antes de seguir o **se revierte** (un cambio, una medición, keep o revert) |
| Tiempo/costo | `limites.max_capturas`, `limites.max_minutos` y `presupuesto` (tokens) del adaptador, aplicados por `scripts/presupuesto.py`; si se acercan, `degradar` (`--rapido`, sin revisor 7, prioridad a lo cambiado) |

## Presupuesto y escala

| Decisión de `presupuesto.py decidir` | Cuándo |
|---|---|
| `seguir` | gastado < 70 % del presupuesto y la métrica baja |
| `degradar` | gastado ≥ 70 %, o más de la mitad del tiempo gastado con el cajón 1 abierto |
| `pivotar` | meseta de dos vueltas, una sola vez por corrida |
| `parar` | predicado cumplido, presupuesto ≥ 95 %, segunda meseta o tope de vueltas; siempre en un punto seguro (`relevo.md`) |

Escala por defecto: **ligera** (script + 2 revisores); ver `coordinacion.md`.

## Refutación

| Volumen | Regla |
|---|---|
| ≤ 30 hallazgos | se refutan todos |
| > 30 | todos los del cajón 1 + muestra ≥ 1/3 (mínimo 10) del resto, priorizando los sin prueba |
| La muestra falla > 1 de cada 5 | se refuta todo |

## Chequeos dormidos
Un chequeo que no disparó en tres corridas seguidas (la actual y las dos
anteriores de la bitácora del proyecto) se borra con constancia.
