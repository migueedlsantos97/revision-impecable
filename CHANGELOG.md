# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/). Hasta ahora las versiones eran ramas, no tags;
ver "Pendiente de versionado" abajo.

## [Sin publicar] - rama `mejoras-generales`

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
