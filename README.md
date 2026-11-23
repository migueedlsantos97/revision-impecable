# Revisión impecable

[English](README.en.md) · Español

Una skill para Claude Code que revisa, prueba y deja impecable cualquier web o
app andando. Como tener un equipo de testers, diseñadores y programadores
revisando todo, incluso de noche, mientras dormís.

No es un linter ni una lista de buenas prácticas. Es un procedimiento:

1. **Mide con un script** lo que no necesita criterio: contraste, tamaño
   táctil, texto chico, desbordes, recortes, solapes, controles de fábrica,
   glifos como íconos, foco invisible, tema a medias, errores de consola, y
   **cuántas formas distintas tiene cada componente en toda la app** (el botón
   que en cada sistema se ve distinto). En 4 anchos y 2 temas, en minutos.
2. **Despacha revisores en paralelo** para lo que sí necesita criterio: probar
   cada función como un usuario (con el dato guardado como prueba), diseño
   contra las reglas de Apple, teclado y lectores, textos, estados límite,
   datos y permisos.
3. **Refuta** cada hallazgo antes de aceptarlo.
4. **Arregla en el lugar compartido**, para que el cambio valga en todas las
   pantallas y todos los sistemas, y vuelve a medir todo.
5. **Convierte cada error en un chequeo** que falla si vuelve.
6. **Aprende de lo que se le escapó**, leyendo el historial de git.

## Requisitos

- [Claude Code](https://claude.com/claude-code) (la skill se carga desde `~/.claude/skills/`).
- Python 3 reciente (se probó con 3.14), `pip` y `git`.
- Playwright (`pip install -r skill/scripts/requirements.txt`) y un navegador: el Chromium de Playwright
  (`python -m playwright install chromium`) o, si no lo bajaste, el Chrome instalado en la máquina.
- Una app que se pueda levantar en local con datos de **prueba** (la skill nunca toca producción).
- Windows, macOS o Linux.

## Probala en 5 minutos

Hay un proyecto mínimo en [`ejemplos/proyecto-minimo/`](ejemplos/proyecto-minimo/): una página con un botón chico, un
`<select>` nativo, texto de 12 px y un gris sin contraste. Ya trae su adaptador (`.claude/revision/proyecto.json`).

1. Instalá la skill y las dependencias (sección Instalación, más abajo).
2. Corré solo la medición, sin Claude, desde la raíz de este repo:

```bash
python skill/scripts/medir.py --config ejemplos/proyecto-minimo/.claude/revision/proyecto.json --rapido
```

   Levanta `app.py` en el puerto 8090, abre el navegador sin ventana, mide en 390 y 1366 px, claro y oscuro, y escribe
   `informe.md`, `informe.json` y capturas en `ejemplos/proyecto-minimo/.claude/revision/salida/<fecha>/`. Esperá
   cerca de **36 medidas** agrupadas en cuatro defectos (contraste, control nativo, táctil, texto chico). El informe
   está explicado en [`ejemplos/informe-ejemplo-v2.md`](ejemplos/informe-ejemplo-v2.md).
3. La revisión completa, con revisores y arreglos: abrí Claude Code **dentro de `ejemplos/proyecto-minimo/`** y pedí
   `revisá todo` (o `/revision-impecable`). Usa el adaptador que ya está.

En un proyecto propio no hace falta escribir el adaptador a mano: la primera vez la skill lo genera leyendo tu repo
(`skill/references/adaptador.md`) y te pregunta solo lo que no puede observar.

## La versión 2

La primera versión despachaba once revisores que medían todo a mano: era
exhaustiva y lenta. La segunda toma tres ideas de cómo trabaja Lauren Tan
(poteto) con agentes ([la entrevista](https://www.youtube.com/watch?v=MN9dGgmLyso),
[sus skills](https://github.com/cursor/plugins/tree/main/pstack)):

- **La verificación es lo primero**: darle al agente manos y ojos para usar la
  app y ver el resultado. Sin eso no hay loop.
- **Lo determinístico va a un script**, el criterio queda para los agentes.
- **Se arregla el entorno, no el caso**: cada error se vuelve estructura
  (un componente compartido, un chequeo, un test) antes que texto.

Y separa lo general de lo particular: la skill sirve para cualquier proyecto, y
lo propio de cada uno (cómo se levanta, sus pantallas, sus funciones, sus
reglas) vive en un **adaptador** dentro de ese proyecto, en
`.claude/revision/`, que la skill genera la primera vez y mantiene.

El estándar de diseño de base son las Human Interface Guidelines de Apple,
resumidas en `skill/references/hig.md`.

Tiene un **modo noche**: trabaja sola en una rama, sin preguntar, decide con
las reglas, rediseña si hace falta, y a la mañana deja un informe con capturas
de antes y después y la lista de lo que necesita tu ojo. Nunca despliega ni
toca datos reales.

## El problema

Un revisor solo, por atento que sea, arrastra sus puntos ciegos: da por bueno lo
que él mismo decidió hace dos horas.

En el proyecto donde nació esta skill yo había recorrido el formulario entero,
con cuidado, dos veces. Un revisor de accesibilidad despachado aparte encontró
que el botón "Cómo usamos tus datos" vivía dentro del `<label>` del
consentimiento, así que su texto se pegaba al nombre de la casilla: quien no ve
la pantalla escucha "responder mi consulta cómo usamos tus datos" como una sola
frase, y no sabe que ahí hay un botón. Lo había mirado y no lo vi.

El mismo hallazgo enseñó la otra mitad. El revisor decía además que activar el
botón **marcaba o desmarcaba la casilla**. Lo di por bueno sin reproducirlo y lo
reporté como lo más grave de la revisión. Es falso: el navegador no dispara el
label cuando el clic cae en un descendiente interactivo. El paso que refuta cada
hallazgo existe por eso, y esta skill lo lleva escrito con su propio error como
ejemplo.

Y al revés: más revisores sin refutación son más ruido. En la misma sesión una
sospecha de vulnerabilidad resultó falsa al probarla contra producción. Sin el
paso que intenta desmentir cada hallazgo, once revisores son once veces más
ruido, no once veces más criterio.

## Qué revisa

| | Quién | Busca |
|---|---|---|
| 0 | `scripts/medir.py` | todo lo medible, en 390/768/1366/1920 y claro/oscuro, y las formas de cada componente entre pantallas y sistemas |
| 1 | Funciones | cada función del mapa, de punta a punta, con el efecto real como prueba |
| 2 | Diseño y consistencia | las capturas contra Apple, las referencias del proyecto y entre sí |
| 3 | Controles, teclado y lectores | lo que dibuja el sistema y lo que no se puede hacer sin mouse |
| 4 | Textos | dos nombres para la misma cosa |
| 5 | Estados límite y anchos | vacío, error, lento, desbordado, entre breakpoints |
| 6 | Datos, permisos y seguridad | quién puede hacer qué, qué se pierde, qué se duplica |
| 7 | Web pública (si lo es) | Safari, rendimiento, cómo se comparte, imágenes |

## Cómo aprende

La medida de si la skill sirve no es cuántos hallazgos trajo. Es cuántos
**escapes** hubo: defectos que alguien encontró *después* de que la revisión dijo
"listo". Esa es la nota.

Cada corrida empieza buscando los escapes de la anterior en el historial de git:

```bash
git log --oneline --since="<fecha de la revisión anterior>" -- <rutas que cubrió>
```

Todo commit posterior que arregle algo que la revisión debió cazar es un escape.
No hace falta que nadie lo reporte: el repositorio ya lo dice.

Después, el paso 7 responde cinco preguntas con nombre y apellido, y **aplica los
cambios**, no los propone:

1. Por cada escape, qué encargo debió cazarlo y qué línea exacta lo caza ahora.
2. Qué falso positivo indujo un encargo mal redactado.
3. Qué check lleva tres corridas sin disparar.
4. Qué técnica hubo que improvisar y debería estar escrita.
5. Qué revisor entregó poco porque su encargo era vago.

Lo del proyecto queda en el proyecto. Lo que sirve para cualquier app sube a esta skill **solo con un caso mínimo
inventado y pasando el filtro de privacidad**: ver [`CONTRIBUTING.md`](CONTRIBUTING.md).

### Por qué no se vuelve un monstruo inútil

Un documento que solo suma termina en tres mil líneas que nadie ejecuta. Por eso
hay poda: **un check que no dispara en tres corridas seguidas se borra**, con
constancia de por qué. Si vuelve a hacer falta, vuelve con evidencia.

Los checks que entraron por un escape llevan la marca `[caso real]`. No es
decoración: dice que esa línea existe porque una vez se pagó por no tenerla.

## Instalación

Clonar y **enlazar** la carpeta `skill/` en tus skills de Claude Code. Con un enlace (y no una copia), `git pull` trae
todo lo que la skill aprendió.

**macOS / Linux**

```bash
git clone https://github.com/migueedlsantos97/revision-impecable ~/revision-impecable
mkdir -p ~/.claude/skills
ln -s ~/revision-impecable/skill ~/.claude/skills/revision-impecable
pip install -r ~/revision-impecable/skill/scripts/requirements.txt
python -m playwright install chromium
```

**Windows, sin administrador (junction), en `cmd`**

```bat
git clone https://github.com/migueedlsantos97/revision-impecable "%USERPROFILE%\revision-impecable"
mkdir "%USERPROFILE%\.claude\skills"
mklink /J "%USERPROFILE%\.claude\skills\revision-impecable" "%USERPROFILE%\revision-impecable\skill"
pip install -r "%USERPROFILE%\revision-impecable\skill\scripts\requirements.txt"
python -m playwright install chromium
```

**Windows con enlace simbólico** (PowerShell como administrador, o con el modo de desarrollador):

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\revision-impecable" -Target "$env:USERPROFILE\revision-impecable\skill"
```

**Sin enlaces (cualquier sistema)**: copiá la carpeta `skill/` a `~/.claude/skills/revision-impecable`. Es lo más simple,
pero para actualizar hay que volver a copiarla.

Se carga en la sesión siguiente. Después alcanza con pedirlo:

> revisá todo antes de mostrárselo al cliente

O invocarla por nombre: `/revision-impecable`. Para la noche:

> revisá todo y dejalo corriendo toda la noche

### Actualizar y desinstalar

- **Actualizar**: `git -C ~/revision-impecable pull` (Windows: `git -C "%USERPROFILE%\revision-impecable" pull`). Con
  enlace, queda al día en todos tus proyectos. Mirá [`CHANGELOG.md`](CHANGELOG.md) por si cambió el formato del adaptador.
- **Desinstalar**: quitá el enlace, no el destino: `rm ~/.claude/skills/revision-impecable` (macOS/Linux) o
  `rmdir "%USERPROFILE%\.claude\skills\revision-impecable"` (Windows; con un junction solo quita el enlace). Después,
  si querés, borrá el clon. Los adaptadores de tus proyectos (`.claude/revision/`) son tuyos y quedan.

## Qué ejecuta y qué toca

Leelo antes de instalarla: es una skill que **corre código y abre un navegador** sobre tu app.

- **Ejecuta** `skill/scripts/medir.py` (Python + Playwright) y el comando de arranque del adaptador de tu proyecto,
  para levantar una instancia **de prueba**. Abre un navegador (sin ventana por defecto) y recorre las pantallas del
  adaptador. Los revisores que despacha Claude leen tu código y manejan esa instancia.
- **Escribe** solo en tu proyecto: `.claude/revision/` (adaptador y mediciones en `salida/`, que conviene ignorar en
  git), `docs/revision-<fecha>.md` (el informe) y los arreglos en tu código. En modo acompañado te muestra los cambios
  de diseño grandes antes de aplicarlos.
- **Modo noche**: trabaja en una **rama propia**, sin preguntar. Nunca hace push a la rama principal ni `--force`, nunca
  despliega, nunca escribe en producción, nunca usa datos reales, nunca borra datos de la persona, nunca mata procesos
  por nombre (solo los que levantó la corrida) y nunca escribe secretos en el repo.
- **Red**: solo lecturas GET de sitios públicos (enlaces salientes, cabeceras, `robots.txt`). La skill no manda tu código
  ni tus datos a ningún servicio propio; lo que ve Claude depende de las condiciones que ya tengas en Claude Code.
- Si tu app solo arranca contra datos reales, la skill **se detiene** y te dice qué falta en vez de inventar.

## ¿Funciona? Los evals

`evals/` tiene dos juegos de casos con defectos sembrados: las tres pantallas originales (`a/b/c`, lo medible) y los
casos `casos-v2/` D a J (funciones, permisos, teclado y lectores, textos y datos regionales, consistencia entre
sistemas, web pública y un caso limpio para medir falsas alarmas). Cada caso trae defectos "dorados" que la skill no
tenía escritos, para medir si **generaliza** y no solo recuerda. La puntuación separa cobertura general, atención a una
corrección puntual (con y sin pista) y precisión: [`evals/playbook.md`](evals/playbook.md). Todavía no hay una vuelta
completa registrada sobre los casos v2.

## Qué entrega

Un informe en markdown en `docs/revision-<fecha>.md`, pensado para que se
entienda solo: alguien que lo abre dentro de seis meses, sin haber estado en la
sesión, tiene que saber qué se revisó, qué se encontró y qué se decidió dejar.

Hay un ejemplo completo en [`ejemplos/informe-ejemplo.md`](ejemplos/informe-ejemplo.md).

El informe separa cuatro cosas que normalmente se mezclan: lo que se arregló, lo
que se descartó y por qué, lo que quedó a criterio del cliente, y **dónde el
procedimiento sigue siendo ciego**. Esa última sección es la más honesta y la que
hace que la próxima revisión sea mejor.

## La regla de fondo

No se termina cuando funciona. Se termina cuando **nada parece accidental**.

Un valor que no se eligió, un control que dibujó el sistema operativo, dos cosas
parecidas que no son iguales: cada uno es una novatada que un cliente nota sin
saber nombrarla.

---

La skill está escrita en español, que es el idioma en el que revisa y en el que se invoca
("revisá todo", "que quede impecable"). English readers: [README.en.md](README.en.md).

## Contribuir, seguridad y licencia

- [`CONTRIBUTING.md`](CONTRIBUTING.md): cómo proponer un check (evidencia reproducible, caso mínimo, sin datos de proyecto).
- [`SECURITY.md`](SECURITY.md): cómo reportar un problema de seguridad.
- [`CHANGELOG.md`](CHANGELOG.md): qué cambió entre versiones.
- MIT. Ver [LICENSE](LICENSE).
