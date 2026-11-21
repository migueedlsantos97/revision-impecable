# Revisión impecable

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

Todo queda en una bitácora que cruza proyectos.

### Por qué no se vuelve un monstruo inútil

Un documento que solo suma termina en tres mil líneas que nadie ejecuta. Por eso
hay poda: **un check que no dispara en tres corridas seguidas se borra**, con
constancia de por qué. Si vuelve a hacer falta, vuelve con evidencia.

Los checks que entraron por un escape llevan la marca `[caso real]`. No es
decoración: dice que esa línea existe porque una vez se pagó por no tenerla.

## Instalación

Cloná el repo y enlazá la carpeta `skill/` en tus skills de Claude Code. Con un
enlace (y no una copia), `git pull` trae todo lo que la skill aprendió en otra
máquina:

```bash
git clone https://github.com/migueedlsantos97/revision-impecable ~/revision-impecable
ln -s ~/revision-impecable/skill ~/.claude/skills/revision-impecable
pip install -r ~/revision-impecable/skill/scripts/requirements.txt
python -m playwright install chromium
```

En Windows, con PowerShell (como administrador, o con el modo de desarrollador):

```powershell
git clone https://github.com/migueedlsantos97/revision-impecable "$env:USERPROFILE\revision-impecable"
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\revision-impecable" -Target "$env:USERPROFILE\revision-impecable\skill"
```

Se carga en la sesión siguiente. Después alcanza con pedirlo:

> revisá todo antes de mostrárselo al cliente

O invocarla por nombre: `/revision-impecable`. Para la noche:

> revisá todo y dejalo corriendo toda la noche

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

## In English

**Revisión impecable** is a Claude Code skill that reviews, tests and polishes
any running web app. A script measures everything mechanical (contrast, touch
targets, overflow, native controls, focus, half-applied themes, and how many
shapes each component has across screens and sub-apps); parallel reviewers cover
what needs judgment, including driving every feature end to end; every finding
must survive a refutation pass; fixes land in the shared component; and the skill
rewrites its own checks based on what it missed. Apple's Human Interface
Guidelines are the default design standard. It can run unattended overnight on a
branch, never deploying or touching real data.

That last part is the point. Each run measures its own failure — defects found
*after* the review declared itself done, read straight from git history — and
edits its own checklists accordingly. Checks that never fire for three runs get
deleted, so it sharpens instead of bloating.

The skill is written in Spanish, which is the language it reviews in. Copy
`skill/` into `~/.claude/skills/revision-impecable` to install.

## Licencia

MIT. Ver [LICENSE](LICENSE).
