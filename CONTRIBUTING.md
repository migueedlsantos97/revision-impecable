# Cómo contribuir

Esta skill es pública y general: sirve para cualquier app. Lo propio de un proyecto (nombres, pantallas, reglas) vive en
el adaptador de ese proyecto (`.claude/revision/`) y **no** viene a este repo. Un aporte útil agrega un check, afina uno o
borra uno que no sirve.

## Qué entra y qué no

Entra un check si cumple las tres:

1. **Es general**: el defecto puede pasar en cualquier app, no solo en la tuya.
2. **Tiene evidencia reproducible**: un caso mínimo (menos de 30 líneas de HTML, o un `server.py` stdlib chico) donde el
   defecto se ve, y cómo se detecta (selector, medida, comando o recorrido de teclado).
3. **No trae datos de proyecto**: ni nombres de personas, empresas o clientes, ni rutas, URLs, emails, textos de interfaz
   ni cifras reales. El caso mínimo se inventa; no se recorta del original.

Una corazonada no es un check: va a las hipótesis de la bitácora y espera a repetirse en otro proyecto o a ser un escape
real. Un check que no dispara en tres corridas seguidas se propone para borrar, con constancia de por qué.

## Paso a paso

1. **Escribí el candidato** en una frase: qué defecto, a qué revisor o al script pertenece, cómo se detecta.
2. **Armá el caso mínimo inventado** en `evals/casos-v2/<letra>-<nombre>/` (HTML suelto o `server.py` con `http.server`) y
   su clave en `evals/claves-v2/`, con peso (grave 3, medio 2, menor 1). Marcá si es "dorado" (la skill no lo tenía escrito).
3. **Comprobá que el defecto existe**: agregá su comprobación a `evals/verificar_casos_v2.py` y corrélo (0 fallas).
4. **Comprobá que hoy la skill no lo caza** (una vuelta sin tu cambio) **y que sí lo caza con él**. Si ya lo cazaba, el
   check sobra.
5. **Agregá la línea mínima** donde corresponde: `skill/scripts/medidas.js` si es medible (preferido: lo mecánico va a un
   script); si no, `skill/references/encargos.md` o `tecnicas.md`. Marcá `[caso real]` solo si fue un escape real; nunca con
   el nombre del proyecto.
6. **Pasá el filtro de privacidad** sobre todo lo que cambiaste:
   `python evals/filtrar_privacidad.py <archivos> --negra <proyecto> <clientes> <personas>`
   (o `--negra-archivo` con un término por línea; ese archivo no se versiona). Debe decir `limpio`.
7. **Actualizá `CHANGELOG.md`** (sección "Sin publicar") y abrí el PR con: el defecto en genérico, el caso mínimo, la salida
   del verificador y el resultado del filtro.

## Reglas del repo

- El español rioplatense es el idioma de la skill y de sus encargos. Los README tienen versión en inglés: si cambiás uno,
  cambiá el otro.
- No se commitean mediciones, capturas de proyectos reales ni `__pycache__`.
- No se edita un caso ni una clave para que la skill "pase": si falla, se edita la skill.
- Los casos se escriben sin mirar el SKILL.md. Un dorado se re-verifica cada vez: si la skill ganó una línea sobre eso,
  deja de ser dorado y se siembra otro.

## Aprender desde un proyecto sin filtrar datos

Cuando una revisión en tu proyecto deja un aprendizaje general: (1) se escribe primero en el proyecto, con todo el detalle
que quieras; (2) se redacta aparte como candidato genérico (puntos 1 y 2 de arriba); (3) se pasa por el filtro de
privacidad con el nombre del proyecto en la lista negra; (4) recién entonces se propone acá. La sesión de un proyecto
nunca escribe directo en la copia instalada de la skill.
