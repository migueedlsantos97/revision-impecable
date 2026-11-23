# El adaptador del proyecto

La skill es general. Lo que cambia de un proyecto a otro vive en
`.claude/revision/` dentro del proyecto, se versiona con él y lo mantiene la
skill. Lo escribís para el próximo agente, que lo va a leer en frío, a mitad de
una tarea, sin conocer la app.

```
.claude/revision/
  proyecto.json     cómo se levanta, se entra y qué pantallas hay (lo lee medir.py)
  funciones/        el feature map: un archivo por función, desde el usuario
    README.md       índice
    <funcion>.md
  reglas.md         reglas propias de diseño y de la app, con qué las hace cumplir
  bitacora.md       una entrada por corrida (formato en bitacora de la skill)
  candidatos/       aprendizajes que podrían subir a la skill (genéricos, sin nombres)
  salida/           mediciones y cobertura.md (no se versiona: agregalo al .gitignore)
```

## 0. Descubrimiento en 10 minutos (sin análisis profundo)

Objetivo: un adaptador que arranca y un mapa razonable de pantallas, roles y
funciones con ~15 comandos. Se entrega como tabla **descubierto / falta /
supuesto** para que la persona confirme en una pregunta, no en veinte.

1. **Stack y arranque.** Mirá `package.json` (scripts `dev`/`start`/`build`, deps
   react/vue/svelte/next/vite), `pyproject.toml`/`requirements.txt`
   (flask/django/fastapi), `Gemfile`, `composer.json`, `go.mod`,
   `docker-compose.yml`, `Makefile`, README. Usá el comando documentado; si hay
   varios, `dev`. Puerto: `grep -rnE 'PORT|listen\(|--port'` y `.env.example`.
   Listo: la primera ruta que devuelve 200 con HTML no vacío (`curl -I`).
2. **Pantallas por tipo de proyecto.**

   | Tipo | Cómo encontrar rutas |
   |---|---|
   | Next/Nuxt/SvelteKit/Remix | listar `pages/`, `app/**/page.*`, `routes/` |
   | SPA con router (React Router, Vue Router) | `grep -rnE "path:|<Route"` |
   | Backend con plantillas (Flask, Django, Express, Rails) | `url_map`, `urls.py`, `app.get(`, `routes.rb` |
   | Sitio estático | `**/*.html` y `sitemap.xml` |
   | Cualquiera | `medir.py --descubrir`: explora desde `/` hasta profundidad 3 siguiendo enlaces del DOM y de los menús, y propone `pantallas`; complementar con `docs/`, tests e2e y `openapi.json` |
   | Solo API/CLI | no hay pantallas: ver "Superficies no web" en `encargos.md` |

3. **Roles y permisos.** `grep -rniE "role|isAdmin|permission|can\(|require|guard|middleware|@login_required"`;
   seeds y fixtures (`seed`, `fixtures`, `factories`); tests de autenticación.
   Entrá con cada rol y **compará el menú visible**: la diferencia es el mapa de
   permisos y la lista de acciones prohibidas para probar contra la API.
4. **Funciones.** Cada `form`, `button[type=submit]` y ruta POST/PUT/DELETE es
   una función candidata; los verbos de los tests e2e y del README las nombran.
   Orden: lo que toca plata o datos, lo más tocado
   (`git log --name-only --since=60.days | sort | uniq -c | sort -rn | head`) y
   lo reciente. Empezá por 5-10.
5. **Reglas de diseño.** `tailwind.config.*`, `:root{--...}`, `design-tokens.json`,
   Storybook, `docs/`, `CLAUDE.md`, enlaces a Figma. El inventario de valores
   (`tecnicas.md`) lo demuestra con números.
6. **Datos de prueba.** `seed`, `fixtures`, `.env.example`, `docker-compose` con
   base; si no hay, crear una carpeta o base **de prueba**, nunca la real.
7. **Estados escondidos.** `grep -rnE 'hidden|display:none|role="dialog"|<dialog|aria-modal'`;
   modales que abre un clic; página 404 y de error; lista vacía.
8. **Sitio público o interno** (`publica`): ¿tiene dominio, `robots.txt`,
   `sitemap.xml`, analítica? Si lo ve gente de afuera, `"publica": true`.

## 1. Interrogá al repo, no a la persona

Respondé desde el código y preguntá solo lo que no se puede observar:

- **Superficie y tipo**: web, SPA, estático, API, escritorio, celular. Si hay
  varios sistemas montados juntos, listalos: la consistencia entre ellos es la
  mitad del trabajo.
- **Arranque**: el comando documentado, puertos, variables, **datos y usuarios
  de prueba**. Tiene que arrancar desde una carpeta de datos vacía o de prueba.
- **Listo**: cómo se sabe que está usable, no solo que el proceso contesta.
- **`doctor`**: un comando de solo lectura que dice si vale la pena manejar esa
  instancia (responde, es la versión del checkout, el puerto es nuestro, el
  login anda). **Lo corre el agente en el paso 0** de la skill antes de medir; si
  falla, no se mide: se arregla el adaptador o se reporta (de noche, se aborta
  con informe).
- **Entrar**: `api` (POST de login), `pasos` (clics con selectores estables) o
  `storage_state` (un archivo de sesión ya autenticada que la persona deja,
  válido para SSO, OAuth o 2FA que no se automatizan). Nunca se escriben claves
  reales ni se eluden captchas.
- **Tema**: si el modo oscuro sigue el sistema, no hace falta nada; si se cambia
  con botón o atributo, `tema.aplicar_js`.
- **Aislar**: ¿se pueden levantar dos instancias (otro puerto, otra carpeta de
  datos)? Los revisores que cambian datos necesitan una cada uno; si no se
  puede, serializarlos.
- **Referencias de diseño**: guía de estilo, maquetas, Figma, componentes
  compartidos, tokens. Es contra lo que se mide el criterio.
- **Idioma y país**: idioma(s) de la interfaz, país (moneda, formato de fecha,
  zona horaria) y aparato real de la persona (`viewport_real`).

Si el checkout no arranca tal como está, arreglalo o reportalo con precisión:
un adaptador escrito contra una base rota enseña pasos falsos. Si falta un
archivo que el arranque necesita y no se versiona, creá uno **de prueba**,
marcado como tal.

## 2. `proyecto.json`

```json
{
  "nombre": "mi-app",
  "tipo": "spa",
  "publica": false,
  "idioma": "es",
  "pais": "AR",
  "url": "http://127.0.0.1:3000",
  "arranque": {"comando": "npm run dev -- --port 3000", "cwd": ".", "listo": "/", "espera": 60, "env": {}},
  "otra_instancia": "npm run dev -- --port {puerto}",
  "doctor": "curl -fsS http://127.0.0.1:3000/health",
  "login": {"tipo": "api", "ruta": "/api/login", "roles": {"admin": {"usuario": "admin-prueba", "clave": "<clave de prueba>"}, "lector": {"usuario": "lector-prueba", "clave": "<clave de prueba>"}}},
  "tema": {"aplicar_js": "document.documentElement.dataset.theme='{tema}'"},
  "anchos": [390, 768, 1366, 1920],
  "viewport_real": [450, 900],
  "umbrales": {"tactil": 44, "texto": 13, "contraste": "AA", "scroll_propio": true, "foco_propio": true, "max_variantes": 2},
  "no_tocar": ["/api/pagos/real", "/admin/borrar-todo", "marca: logo y colores"],
  "limites": {"max_capturas": 400, "max_minutos": 45},
  "autonomia": "acompanado",
  "vueltas": 5,
  "pantallas": [
    {"id": "lista", "sistema": "panel", "ruta": "/clientes", "rol": "admin", "esperar": "table"},
    {"id": "lista-menu", "sistema": "panel", "ruta": "/clientes", "rol": "admin",
     "pasos": [{"accion": "click", "selector": "[data-accion=filtros]"}], "ancho_min": 768}
  ]
}
```

- `tipo`: `estatico`, `spa`, `ssr`, `api`, `escritorio`. Activa o descarta
  revisores y categorías de cobertura (un `api` marca N/A las de pantalla).
- `publica`: `true` activa el revisor 7 (SEO, compartir, navegadores, rendimiento).
- `idioma`/`pais`: orientan ortografía, formatos y zona horaria del revisor 4.
- `viewport_real`: el aparato de la persona; se mide además de `anchos`.
- `no_tocar`: rutas, acciones o áreas (marca, textos legales) que nunca se
  modifican ni se ejecutan; en modo noche, el revisor las trata como solo lectura.
- `limites`: tope de capturas y de minutos (ver `umbrales.md`); superado, se mide
  con `--rapido` y se prioriza lo cambiado recientemente.
- `arranque.listo_log`: texto que la instancia escribe al terminar de prepararse;
  `medir.py` lo espera en `instancia.log` antes de medir.
- `login.tipo`: `api`, `pasos` (`{usuario}` y `{clave}` se reemplazan) o
  `storage_state` (`{"tipo":"storage_state","archivo":".claude/revision/sesion-admin.json"}`;
  el archivo no se versiona).
- Pasos: `click`, `fill`, `esperar`, `presionar`, `pausa`, `js`, e `ir` (clic en
  el menú de escritorio si se ve; si no, el recorrido alternativo del celular
  que declare el adaptador).
- **Una pantalla es un estado, no una URL**: un menú abierto, un diálogo, la
  lista vacía, el formulario con error. Lo que arranca escondido (`hidden`,
  diálogos, sesión vencida) también va al mapa; si no, nunca se mide.
- `ancho_min` / `ancho_max`: pantallas que solo existen en escritorio o celular.
- Un aviso que se va solo se captura con los pasos justos, sin pausas largas.
- En `esperar`, si la navegación de escritorio queda en el DOM oculta en celular,
  usá `:visible`: `a, b` espera al primero que encuentra aunque no se vea.
- `sistema` agrupa pantallas para medir la consistencia entre ellas.
- Usuarios y claves de **prueba** nada más. Si el proyecto los genera con un
  script, el adaptador dice cuál y no copia las claves.

### Descubrimiento automático (`--descubrir`)
`python <skill>/scripts/medir.py --config .claude/revision/proyecto.json --descubrir`
explora el sitio con el rol indicado (GET y navegación, sin enviar formularios
ni pulsar acciones destructivas), sigue enlaces y menús a poca profundidad y
**propone** un listado de `pantallas` y estados escondidos para pegar en
`proyecto.json`. Es un punto de partida: se revisa a mano y se completa con
estados que solo existen tras una acción (menús, diálogos, vacíos, errores). Los
flags exactos están en `--help`.

### Qué mide el script además de lo visual (en términos generales)
Además de contraste, tamaños, desbordes, solapes y foco, `medir.py` marca
problemas de **documento** (idioma, viewport, título), **imágenes** (texto
alternativo, dimensiones), **campos** sin nombre o etiqueta, **estructura**
(encabezados, ids duplicados, referencias ARIA rotas), **red** (respuestas
4xx/5xx, contenido mixto), **estabilidad de layout** (CLS), elementos **tapados**
por otros, textos **truncados** (puntos suspensivos) que esconden información,
**fuentes** que no cargan y `tabindex` problemáticos.

Cada falla lleva `certeza`: **medida** (se reproduce corriendo de nuevo) o
**sospecha** (se refuta mirando la captura).
- Medidas nuevas: `sin_lang`, `sin_viewport`, `sin_titulo`, `img_sin_alt`,
  `campo_sin_nombre`, `sin_nombre_accesible`, `id_duplicado`, `aria_roto`,
  `tabindex_positivo`, `fuente_no_cargo`, `http_error`, `request_fallida`,
  `contenido_mixto`, `cls_alto`, `sin_sesion`, `captura_fallida`.
- Sospechas: `img_sin_dimensiones`, `enlace_falso`, `heading_h1`,
  `heading_salto`, `texto_cortado_sin_title`, `tapado`, `titulo_duplicado`,
  `solape_truncado`, y los de consistencia (`variantes`, `casi_iguales`,
  `escala`, `distinto_por_sistema`, `mismo_rotulo_distinta_forma`,
  `tema_a_medias`, `recortado`).
- Flags: `--config --url --sistema --pantalla --anchos --rapido --salida --ver`
  y los nuevos `--descubrir --rol --max-paginas --profundidad --motores
  chromium,firefox,webkit`. Umbrales en `umbrales` del config (ver
  `umbrales.md`; `desactivar` apaga un tipo, `ignorar_url` filtra recursos).
- Marcas para silenciar un falso positivo concreto en el HTML:
  `data-revision-ok="alt|dimensiones|nombre|tabindex|cortado|tapado|tema|..."`.

Lo que el script no ve (formularios, teclado, lector,
red forzada, impresión, volumen) queda en los encargos.

## 3. `funciones/`: el feature map

Un archivo por función que ve el usuario (empezá por las 5-10 principales, de
las rutas, menús y documentación). Cada uno, desde el punto de vista del
usuario, con estos títulos:

- **Qué es**: en las palabras de quien la usa.
- **Cómo se llega**: los clics, desde el inicio, para cada rol que la usa.
- **Cómo se maneja con Playwright**: selectores reales del repo (ARIA, `data-*`,
  textos estables), no coordenadas.
- **Qué prueba que anda**: el estado final observable **y el efecto real**: la
  fila en la base, el archivo escrito, el mensaje enviado, el stock que bajó.
- **Trampas**: lo que hay que saber para no equivocarse. Si los datos de prueba
  no alcanzan para el recorrido, se anota acá; nunca se afloja el recorrido.

Una prueba que maneja una sola entrada cómoda está incompleta si el mapa lista
otras. [caso real #37]

## 4. `reglas.md`

Las reglas propias del proyecto, en una tabla:

| regla | por qué | qué la hace cumplir |
|---|---|---|
| sin `select` nativo | la lista la dibuja el sistema | `medir.py` (control_nativo) |
| botón primario 44 px, radio 12 | una sola forma en todos los sistemas | `medir.py` (variantes, distinto_por_sistema) |
| el contador se calcula de los datos | "3 alertas" con 1 en la lista | revisor 4 (criterio) |

Cuando la persona corrige algo, se aplica "Corrección del usuario" (`SKILL.md`):
se arregla, se barre la clase y se agrega la fila. Si la regla ya estaba y nada
la hacía cumplir, es una repetición: se sube de nivel (de texto a chequeo) en el
mismo cambio. Una regla cuyo error ya no puede pasar se borra. Abajo de la
tabla, la lista de revisiones con fecha y rutas cubiertas (la usa el paso 1
para buscar escapes).

## 5. Probalo antes de usarlo

Corré el adaptador una vez de punta a punta: levantar, `doctor`, entrar con cada
rol, `medir.py --pantalla <una> --rapido`, una función del mapa, apagar.
Después de apagar, confirmá que la evidencia sigue en `salida/`. Un adaptador
que nunca se ejecutó es un borrador.

## 6. Mantenerlo

En cada corrida, antes de medir: índice del mapa al día (sin entradas muertas ni
duplicadas), pantallas nuevas agregadas, `doctor` en verde. Un comportamiento
que el mapa describe y la app ya no hace es documentación vieja (se corrige el
mapa) o una regresión (se reporta, no se tapa en el mapa).
