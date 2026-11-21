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
  salida/           mediciones (no se versiona: agregalo al .gitignore)
```

## 1. Interrogá al repo, no a la persona

Respondé desde el código y preguntá solo lo que no se puede observar:

- **Superficie**: ¿qué toca el usuario? Web, app de escritorio, celular, API.
  Si hay varios sistemas montados juntos, listalos: la consistencia entre ellos
  es la mitad del trabajo.
- **Arranque**: el comando documentado del repo (scripts, Makefile, README).
  Puertos, variables de entorno, **datos de prueba** y usuarios de prueba. Tiene
  que arrancar desde una carpeta de datos vacía o de prueba, nunca la real.
- **Listo**: cómo se sabe que está usable, no solo que el proceso contesta.
- **Doctor**: un chequeo de solo lectura que dice si vale la pena manejar esa
  instancia: responde, es la versión del checkout, el puerto es nuestro, el
  login anda.
- **Entrar**: cómo inicia sesión cada rol. Preferí la API de login; si no hay,
  los pasos en la pantalla con selectores estables.
- **Tema**: si el modo oscuro sigue la preferencia del sistema, no hace falta
  nada. Si se cambia con un botón o un atributo, `tema.aplicar_js`.
- **Aislar**: ¿se pueden levantar dos instancias a la vez (otro puerto, otra
  carpeta de datos)? Los revisores que cambian datos necesitan una cada uno.
  Si no se puede, decilo: es preferible serializarlos a que se pisen.
- **Referencias de diseño**: guía de estilo, maquetas aprobadas, Figma,
  componentes compartidos, tokens. Es contra lo que se mide el criterio.

Si el checkout no arranca tal como está, arreglalo o reportalo con precisión
antes de seguir: un adaptador escrito contra una base rota enseña pasos falsos.
Si falta un archivo que el arranque necesita y no se versiona (datos de
ejemplo, configuración local), creá uno **de prueba**, marcado como tal.

## 2. `proyecto.json`

```json
{
  "nombre": "mi-app",
  "url": "http://127.0.0.1:8090",
  "arranque": {"comando": "python run.py --datos datos_prueba --puerto 8090", "cwd": ".", "listo": "/", "espera": 60, "env": {}},
  "otra_instancia": "python run.py --datos /tmp/rev-{n} --puerto {puerto}",
  "doctor": "curl -fsS http://127.0.0.1:8090/salud",
  "login": {"tipo": "api", "ruta": "/api/login", "roles": {"admin": {"usuario": "admin", "clave": "..."}, "operario": {"usuario": "op", "clave": "..."}}},
  "tema": {"aplicar_js": "document.documentElement.dataset.theme='{tema}'"},
  "anchos": [390, 768, 1366, 1920],
  "umbrales": {"tactil": 44, "texto": 13, "contraste": "AA", "scroll_propio": true, "foco_propio": true, "max_variantes": 2},
  "autonomia": "acompanado",
  "vueltas": 5,
  "pantallas": [
    {"id": "stock", "sistema": "almacen", "ruta": "/almacen/stock", "rol": "admin", "esperar": "table"},
    {"id": "stock-menu", "sistema": "almacen", "ruta": "/almacen/stock", "rol": "admin",
     "pasos": [{"accion": "click", "selector": "[data-accion=filtros]"}], "ancho_min": 768}
  ]
}
```

- `login.tipo` es `api` (POST con el cuerpo del rol) o `pasos` (lista de
  pasos; `{usuario}` y `{clave}` se reemplazan).
- Pasos: `click`, `fill`, `esperar`, `presionar`, `pausa`, `js`, e `ir` (clic en
  el menú de escritorio si se ve; si no, los clics de `alt` del celular).
- **Una pantalla es un estado, no una URL**: un menú abierto, un diálogo, la
  lista vacía, el formulario con error. Lo que arranca escondido (`hidden`,
  diálogos, la pantalla de sesión vencida) también va al mapa; si no, nunca se
  mide.
- `sistema` agrupa pantallas para medir la consistencia entre sistemas.
- Usuarios y claves de prueba nada más. Si el proyecto los genera con un script,
  el adaptador dice cuál y no copia las claves.

## 3. `funciones/`: el feature map

Un archivo por función que ve el usuario (empezá por las 5-10 principales, de
las rutas, menús y documentación). Cada uno, desde el punto de vista del
usuario, con estos títulos:

- **Qué es**: en las palabras de quien la usa.
- **Cómo se llega**: los clics, desde el inicio, para cada rol que la usa.
- **Cómo se maneja con Playwright**: selectores reales del repo (preferí
  etiquetas ARIA, `data-*`, textos estables), no coordenadas.
- **Qué prueba que anda**: el estado final observable **y el efecto real**: la
  fila en la base, el archivo escrito, el mensaje enviado, el stock que bajó.
- **Trampas**: lo que hay que saber para no equivocarse. Si los datos de prueba
  no alcanzan para el recorrido, se anota acá; nunca se afloja el recorrido
  para que pase.

Una prueba que maneja una sola entrada cómoda está incompleta si el mapa lista
otras.

## 4. `reglas.md`

Las reglas propias del proyecto, en una tabla:

| regla | por qué | qué la hace cumplir |
|---|---|---|
| sin `select` nativo | la lista la dibuja el sistema | `medir.py` (control_nativo) |
| botón primario 44 px, radio 12 | una sola forma en todos los sistemas | `medir.py` (variantes, distinto_por_sistema) |
| el contador se calcula de los datos | "3 alertas" con 1 en la lista | revisor 4 (criterio) |

Cuando la persona corrige algo, se arregla y se agrega la fila. Si la regla ya
estaba y nada la hacía cumplir, es una repetición: se sube de nivel (de texto a
chequeo) en el mismo cambio. Una regla cuyo error ya no puede pasar se borra.

Abajo de la tabla, la lista de revisiones con fecha y rutas cubiertas: es lo
que usa el paso 1 para buscar escapes.

## 5. Probalo antes de usarlo

Corré el adaptador una vez de punta a punta: levantar, doctor, entrar con cada
rol, `medir.py --pantalla <una> --rapido`, una función del mapa, apagar. Después
de apagar, confirmá que la evidencia sigue en `salida/`. Un adaptador que nunca
se ejecutó es un borrador.

## 6. Mantenerlo

En cada corrida, antes de medir: índice del mapa al día (sin entradas muertas ni
duplicadas), pantallas nuevas agregadas, doctor en verde. Un comportamiento que
el mapa describe y la app ya no hace es documentación vieja (se corrige el mapa)
o una regresión (se reporta, no se tapa en el mapa).
