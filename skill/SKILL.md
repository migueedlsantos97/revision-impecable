---
name: revision-impecable
description: Revisión final exhaustiva de una web antes de mostrársela a un cliente o desplegarla. Úsala cuando te pidan "revisá todo", "que quede impecable", "antes de mostrarlo", "no quiero novatadas", o cuando una web esté por salir a producción. Despacha once revisores especializados en paralelo, hace refutar cada hallazgo antes de aceptarlo, los ordena por lo que le cuesta la venta, deja un informe y aprende de lo que se le escapó. No se cierra hasta que nada parezca accidental.
---

# Revisión impecable

Quien encarga una web la revisa hasta el último detalle, y tiene razón: para
quien la hizo es su carta de presentación y de ahí sale el boca a boca. Esta
skill existe para llegar a esos detalles **antes** que el cliente.

Y para que cada vez llegue más lejos: el paso 7 hace que la skill se corrija a
sí misma con lo que se le escapó.

## Por qué en paralelo y no en lista

Un revisor solo, por atento que sea, arrastra sus propios puntos ciegos: da por
bueno lo que él mismo decidió hace dos horas. La única forma de romper eso es
que miren varios, **cada uno con un encargo estrecho y sin ver los hallazgos de
los otros**.

No es teoría. En el primer proyecto donde se usó, yo ya había recorrido el formulario entero
cuando un revisor de accesibilidad encontró que el botón "Cómo usamos tus
datos" vivía dentro del label del consentimiento y, al abrirlo, marcaba o
desmarcaba la casilla. Lo había mirado y no lo vi.

Y al revés: más revisores sin refutación son más ruido. En la misma sesión una
sospecha de bypass por codificación de URL resultó falsa al probarla contra
producción. **Sin el paso 3 esto no sirve.**

## El procedimiento

### 1. Preparar el terreno y medir la vez anterior

- Levantá el sitio y dejá la URL a mano. Los revisores de la ronda B la
  necesitan.
- Corré los tests que ya existan y anotá el número. Es la línea de base.
- Leé `CLAUDE.md` o equivalente: lo que ya está decidido no se vuelve a
  discutir, y lo que figura como pendiente son hallazgos ya conocidos.
- Leé `references/bitacora.md`. Si hay una entrada previa **de este proyecto**,
  buscá los escapes antes de empezar:

```bash
git log --oneline --since="<fecha de la revisión anterior>" -- <rutas que cubrió>
```

Todo commit posterior que arregle algo que la revisión debió haber encontrado es
un **escape**. Anotalos: son la nota de la vez pasada y la materia prima del
paso 7. Si tenés a mano a quien encargó el sitio, preguntale qué encontró
después.

### 2. Despachar los once revisores

Los encargos completos están en `references/encargos.md`. Las técnicas
compartidas, en `references/tecnicas.md`. Pasale a cada revisor **su sección
entera**, la raíz del proyecto y el contrato de salida de abajo.

Van en dos rondas porque la segunda necesita el sitio corriendo. Dentro de cada
ronda se despachan **todos a la vez, en un solo mensaje**.

**Ronda A, sobre el código:**

| # | Revisor | Busca |
|---|---|---|
| 1 | Consistencia visual | quince valores donde debería haber cinco |
| 2 | Controles del sistema | lo que dibuja el navegador y no la marca |
| 3 | Contraste y color | razones calculadas, no miradas |
| 4 | Teclado y lectores | lo que no se puede hacer sin mouse |
| 5 | Textos y nomenclatura | dos nombres para la misma cosa |
| 6 | Compatibilidad y Safari | lo que rompe fuera de Chromium |

**Ronda B, sobre el sitio andando:**

| # | Revisor | Busca |
|---|---|---|
| 7 | Anchos y reflujo | el hueco entre breakpoints |
| 8 | Estados límite | vacío, cargando, caído, desbordado |
| 9 | Rendimiento | peso, primer dibujo, gama baja |
| 10 | Conversión y cómo se comparte | qué ve quien llega y quien recibe el link |
| 11 | Dirección de arte | las imágenes como conjunto |

Si el encargo es un repaso puntual y no un prelanzamiento, elegí los revisores
que correspondan y decilo en el informe. Once es para cuando la web se va a
mostrar.

**Contrato de salida.** Cada revisor entrega una lista, y cada hallazgo lleva:

- `archivo:línea` o la URL y el ancho donde pasa.
- Una frase con **qué se rompe**, no qué regla se incumple.
- **La prueba**: el número calculado, la salida del comando, el selector que no
  matchea. Sin prueba no es hallazgo, es opinión.
- Un **escenario concreto**: qué hace una persona y qué le pasa.
- Severidad propuesta, con el criterio del paso 4.
- Si es gusto y no error, decirlo. Eso no se arregla, se reporta.

Pedile además **una línea final**: qué se quedó con ganas de revisar y no pudo,
y qué le faltó en su encargo. Eso alimenta el paso 7.

### 3. Refutar antes de aceptar

Ningún hallazgo se arregla por venir de un revisor. Por cada uno, **intentá
demostrar que está mal**: reproducilo en el navegador, calculá el número vos,
probá el caso contra el sitio real. Recién ahí ponés veredicto.

- **CONFIRMADO**: lo reprodujiste.
- **PLAUSIBLE**: el razonamiento se sostiene pero no pudiste reproducirlo. Va al
  informe como tal, no se arregla a ciegas.
- **DESCARTADO**: se cae. Queda en el informe con el motivo, para que nadie lo
  vuelva a levantar.

Para lo que sea barato, despachá la refutación en paralelo igual que la
revisión. Un verificador por dimensión alcanza.

### 4. Ordenar por lo que cuesta

Ochenta hallazgos sin orden se convierten en un píxel corregido mientras la
vista previa de WhatsApp sigue rota. Tres cajones, en este orden:

1. **Le cuesta la venta.** Algo no funciona, no se entiende, no se puede usar, o
   el sitio se ve mal donde el cliente lo va a mostrar. Se arregla todo.
2. **Parece de principiante.** Funciona pero delata falta de oficio: controles de
   fábrica, valores casi iguales, textos con dos nombres. Se arregla todo, y es
   lo que más define la impresión.
3. **No lo nota nadie.** Se arregla si sale barato. Si no, va al informe.

Los de gusto no entran en ningún cajón: van aparte, sin tocar.

### 5. Arreglar y fijar

- Un commit por tema, con el mensaje explicando **qué se rompía** y por qué.
- Cada invariante que costó encontrar queda con un test y un comentario que dice
  el porqué, para que nadie lo deshaga sin enterarse.
- Después de arreglar, **volvé a correr la fase**. Un arreglo destapa otro: al
  dibujar la casilla de consentimiento se rompió el globo de validación nativo,
  que ya no tenía dónde anclarse.

### 6. Dejar el informe

Escribí `docs/revision-<fecha>.md` con la plantilla de
`assets/plantilla-informe.md`. Tiene que entenderse solo, sin haber estado en la
sesión: alguien que abre ese archivo dentro de seis meses tiene que saber qué se
revisó, qué se encontró y qué se decidió dejar.

### 7. Aprender

**Este paso es el que hace que la skill valga más cada vez. No es opcional y no
se hace "si da el tiempo".**

La pregunta no es "cómo salió". Es **qué se le escapó a este procedimiento**.

Respondé las cinco, con nombre y apellido, nada de generalidades:

1. **Escapes.** De lo que encontraste en el paso 1, o lo que encontró quien encargó el sitio
   después: por cada uno, ¿qué encargo debió haberlo cazado? ¿Por qué no lo
   hizo, faltaba el check o estaba mal escrito? ¿Qué línea exacta lo habría
   cazado?
2. **Falsos positivos.** De lo descartado, ¿hubo un encargo que los indujo?
   Un check redactado como sospecha genera ruido; uno redactado como prueba, no.
3. **Checks dormidos.** ¿Qué check no disparó ni acá ni en las dos entradas
   anteriores de la bitácora? Un check que nunca encuentra nada **se saca**. La
   skill se hace inútil por larga mucho antes que por corta.
4. **Técnicas nuevas.** ¿Qué tuviste que averiguar a mano que debería estar en
   `tecnicas.md`? Un comando, una fórmula, una trampa del entorno.
5. **Revisores flojos.** ¿Alguno entregó poco o genérico? Casi siempre es que su
   encargo es vago. ¿Qué habría que agregarle?

Después, **aplicá los cambios**, no los propongas:

- Lo que tenga evidencia de esta corrida se escribe ya en `encargos.md` o en
  `tecnicas.md`, con una línea que diga en qué proyecto se aprendió.
- Lo que sea una corazonada se anota en la bitácora como hipótesis y espera a
  repetirse en otro proyecto antes de convertirse en check.
- Lo que esté dormido hace tres corridas se borra, y se deja constancia de que
  se borró y por qué. Si vuelve a aparecer, vuelve con más razón.

Y agregá la entrada a `references/bitacora.md`, con el formato que está ahí.

## Criterio de salida

La revisión se cierra cuando **todas** estas son ciertas:

- Los revisores corrieron y entregaron, o se documentó cuáles no y por qué.
- Todo hallazgo tiene veredicto. Ninguno quedó en "habría que ver".
- Los cajones 1 y 2 están vacíos.
- El cajón 3 y los de gusto están en el informe, no en tu memoria.
- Los tests pasan y hay más que al empezar.
- Nada del sitio se ve como si lo hubiera decidido el navegador.
- **El paso 7 está hecho: la bitácora tiene la entrada nueva y los encargos
  cambiaron, aunque sea para borrar algo.** Una corrida que no cambió nada de la
  skill casi siempre es una corrida en la que no se miró.

La regla de fondo, por si alguna fase deja duda: **no se termina cuando
funciona, se termina cuando nada parece accidental**. Un valor que no se
eligió, un control que dibujó el sistema, dos cosas parecidas que no son
iguales: cada uno es una novatada que un cliente nota sin saber nombrarla.

## Qué no arreglar por tu cuenta

Un titular, el tono de un botón, un color de marca fuera de paleta, el nombre de
una sección. Eso se **reporta** con el motivo y se deja como está. La web es de quien la encargó:
una decisión de gusto tomada sin preguntar es otra forma de novatada.
