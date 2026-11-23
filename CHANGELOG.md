# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Hasta ahora las versiones eran ramas, no tags;
ver "Pendiente de versionado" abajo.

## [Sin publicar] - rama `mejoras-generales`

### v2.2 — fidelidad a la fuente, incremental y autonomía total
- **Por qué**: una auditoría contra la entrevista y pstack mostró que la skill
  cubría la verificación y el estructurar errores, pero no el relevo por límite de
  contexto, el presupuesto, el estado verificado por sistema, el baseline visual,
  la verificación de la cadena de los revisores, ni cómo mejorar a la vez la skill y
  la app medida.
- **Agregado** (`references/`): `relevo.md` (checkpoint, punto seguro, relevo,
  reanudar); `incremental.md` (estado por sistema, dependencias, alcance, sondas);
  `coordinacion.md` (escala ligera por defecto, modelo por rol, zonas de archivos
  y worktrees, cadena de revisores, pase de mantenimiento del mapa);
  `mejora-continua.md` (tabla general/proyecto, carriles, métricas); plantilla
  `assets/LEEME-AL-VOLVER.md`. `noche.md` reescrito con contrato de seguridad,
  requisitos para "ganarse el loop", `decisiones.tsv` con antes/después/veredicto,
  salida de escape y "Atención" por otro revisor.
- **Cambiado**: `umbrales.md` (meseta = pivotar una vez antes de parar; los
  silenciamientos cuentan; presupuesto); `adaptador.md` (chequeos propios,
  estado, dependencias, baseline); `SKILL.md` (escalera de garantías, baseline,
  un cambio una medición, paso 0 de "Corrección del usuario", criterio de salida).
- **README**: la entrevista queda en su canal primario; se distingue qué ideas
  vienen de la fuente y cuáles son propias; la otra charla se cita solo como
  complementaria, sin cifras de agentes.
- **Casos reales** #39-#41 (anonimizados).
- **Hipótesis abiertas**: que la escala ligera por defecto no baje la cobertura
  (se confirma con escapes en las primeras corridas); que el mapa de dependencias
  generado por lectura sea suficiente sin validación manual.

### Agregado
- `README.en.md`, `CHANGELOG.md`, `CONTRIBUTING.md` y `SECURITY.md`.
- README: requisitos, ejemplo de 5 minutos con `ejemplos/proyecto-minimo/`, instalación con junction (Windows, sin
  administrador), enlace simbólico o copia; cómo actualizar y desinstalar; sección "Qué ejecuta y qué toca".
- `ejemplos/proyecto-minimo/` (app mínima con defectos y su `proyecto.json`) y `ejemplos/informe-ejemplo-v2.md`.
- Evals v2: casos D a J en `evals/casos-v2/` (funciones, permisos, teclado y lectores, textos y datos regionales,
  consistencia entre sistemas, web pública, caso limpio), claves en `evals/claves-v2/`, `evals/brief-ejecutor-v2.md`,
  `evals/verificar_casos_v2.py` (comprueba que los defectos sembrados existen) y puntuación de dos ejes con pista en
  `evals/playbook.md`.
- `evals/filtrar_privacidad.py`: filtro de privacidad (emails, rutas de usuario, IP privadas, dominios internos, tokens,
  teléfonos y lista negra) para todo lo que vaya a un repo público.

### Cambiado
- Landing: una sola página (`landing/index.html`; se borró `landing/artifact.html`, que era la misma sin el esqueleto),
  "once" pasa a "siete" revisores y la instalación usa un enlace en vez de `cp -r`. Sin fuentes externas: ya no pide
  nada a Google al abrirla.
- `ejemplos/informe-ejemplo.md` queda marcado como ejemplo de la v1.

### Eliminado
- `skill/scripts/__pycache__/` del índice de git; `.gitignore` ignora `__pycache__/`, `*.pyc`, las mediciones (`salida/`)
  y `instancia.log`.

Los cambios a `skill/` (SKILL.md, references, scripts) de esta rama están en `git log -- skill/`.

## [2.0] - 2026-11-21 (rama `v2`)

Cambio de procedimiento: de once revisores que medían todo a mano a un script más siete revisores.
- Agregado: `scripts/medir.py` y `scripts/medidas.js` (medición determinística: contraste, táctil, texto chico, desbordes,
  controles nativos, foco invisible, tema a medias, contenido recortado, consistencia de componentes entre pantallas y
  sistemas), `references/adaptador.md` (lo del proyecto vive en `.claude/revision/`), `references/hig.md` (Apple como
  estándar de base), `references/noche.md` (modo autónomo), el paso de "fijar como estructura antes que como texto" y el
  reparto de cada aprendizaje entre la skill y el adaptador.
- Cambiado: once revisores pasan a siete (`encargos.md`: entran Funciones y Datos/permisos; Contraste pasa al script;
  Compatibilidad, Rendimiento, Conversión y Dirección de arte se juntan en Web pública).
- Cambiado: `medir` clasifica botones por función, mira el foco del contenedor y no confunde adornos con tema a medias;
  espera una marca en el log antes de medir; la skill activa los guardrails del repo.
- Agregado: `evals/` con tres páginas sembradas.

## [1.x] - 2026-09 a 2026-11

Procedimiento con once revisores en dos rondas, refutación de cada hallazgo y bitácora de escapes. Entre otros: landing
como banco de pruebas; seis encargos que aprenden de cuatro escapes; tema que se aplica a medias; lo que no se estila hay
que reemplazarlo; caché guardada; estado vacío, anchos de prueba y datos regionales; foco por selector y anillo de foco
invisible con la ventana sin foco; lo que cambió hoy va primero.

## [1.0] - 2026-09-22

Primera versión: la skill y su landing, nacida de una revisión a mano de un sitio de eventos.

## Pendiente de versionado

No hay tags ni releases. Se recomienda taggear `v2.0.0` cuando esta rama se mergee y numerar de ahí en más: mayor si
cambia el formato de `proyecto.json` o la forma de invocar la skill, menor si se agrega un revisor o un chequeo, parche si
solo se corrige un texto.
