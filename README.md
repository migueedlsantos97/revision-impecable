# Revisión impecable

Una skill para Claude Code que revisa una web antes de que la vea el cliente.

No es un linter ni una lista de buenas prácticas. Es un procedimiento que
despacha **once revisores especializados en paralelo**, obliga a **refutar cada
hallazgo** antes de aceptarlo, los ordena por **lo que le cuesta la venta**, y
después **se corrige a sí misma** con lo que se le escapó.

Esa última parte es la que importa. Cada revisión termina midiendo su propio
fracaso y reescribiendo sus propias instrucciones. La skill que usás en el
proyecto diez no es la que instalaste.

## El problema

Un revisor solo, por atento que sea, arrastra sus puntos ciegos: da por bueno lo
que él mismo decidió hace dos horas.

En el proyecto donde nació esta skill yo había recorrido el formulario entero,
con cuidado, dos veces. Un revisor de accesibilidad despachado aparte encontró
que el botón "Cómo usamos tus datos" vivía dentro del `<label>` del
consentimiento: abrirlo marcaba o desmarcaba la casilla sin que se viera, en el
único campo con peso legal del formulario. Lo había mirado y no lo vi.

Y al revés: más revisores sin refutación son más ruido. En la misma sesión una
sospecha de vulnerabilidad resultó falsa al probarla contra producción. Sin el
paso que intenta desmentir cada hallazgo, once revisores son once veces más
ruido, no once veces más criterio.

## Qué revisa

**Sobre el código**

| Revisor | Busca |
|---|---|
| Consistencia visual | quince valores donde debería haber cinco |
| Controles del sistema | lo que dibuja el navegador y no la marca |
| Contraste y color | razones calculadas, no miradas |
| Teclado y lectores | lo que no se puede hacer sin mouse |
| Textos y nomenclatura | dos nombres para la misma cosa |
| Compatibilidad y Safari | lo que rompe fuera de Chromium |

**Sobre el sitio andando**

| Revisor | Busca |
|---|---|
| Anchos y reflujo | el hueco entre breakpoints |
| Estados límite | vacío, cargando, caído, desbordado |
| Rendimiento | peso, primer dibujo, gama baja |
| Conversión y cómo se comparte | qué ve quien llega y quien recibe el link |
| Dirección de arte | las imágenes como conjunto |

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

Copiá la carpeta `skill/` a tus skills de Claude Code, con el nombre
`revision-impecable`:

```bash
# Para todos tus proyectos
cp -r skill ~/.claude/skills/revision-impecable

# Solo para este proyecto
cp -r skill .claude/skills/revision-impecable
```

En Windows, con PowerShell:

```powershell
Copy-Item -Recurse skill "$env:USERPROFILE\.claude\skills\revision-impecable"
```

Se carga en la sesión siguiente. Después alcanza con pedirlo:

> revisá todo antes de mostrárselo al cliente

O invocarla por nombre: `/revision-impecable`.

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

**Revisión impecable** is a Claude Code skill for the final review of a website
before a client sees it.

It dispatches eleven specialised reviewers in parallel, requires every finding to
survive a refutation pass before it is accepted, triages by what actually costs
the sale, and then rewrites its own instructions based on what it missed.

That last part is the point. Each run measures its own failure — defects found
*after* the review declared itself done, read straight from git history — and
edits its own checklists accordingly. Checks that never fire for three runs get
deleted, so it sharpens instead of bloating.

The skill is written in Spanish, which is the language it reviews in. Copy
`skill/` into `~/.claude/skills/revision-impecable` to install.

## Licencia

MIT. Ver [LICENSE](LICENSE).
