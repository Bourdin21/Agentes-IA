---
description: Decisiones de diseño de pantallas del portal (ASP.NET Core MVC + design system Olvidata) — listados, conversaciones, tarjetas, formularios y estados vacíos. Qué hacer y qué NO, con el motivo medido detrás de cada regla. Origen: rediseño de olvidata-agentes-multirubro, 2026-09.
applyTo: "**/*.{cshtml,css,js}"
---

# 38 — Diseño de pantallas del portal

Memoria de diseño reutilizable para cualquier portal del estudio hecho sobre **ASP.NET Core MVC + el design system
Olvidata** (`olvidata-theme.css` + `site.css`). No son gustos: cada regla salió de mirar la pantalla real con datos
reales y medir qué tapaba qué.

**Antes de maquetar una pantalla nueva, leer esto.** Y antes de darla por terminada, mirarla en un navegador real a
**1440 y a 390 px, en tema claro y oscuro, con datos de verdad** — no con tres filas de ejemplo.

---

## 0. La regla que ordena todas las demás

> **Lo que la persona vino a hacer entra en la primera pantalla. Todo lo demás se pliega.**

El error más caro que cometimos fue tratar a todas las partes de una pantalla como igual de importantes. Un panel de
filtros, un encabezado de tres renglones y una barra de herramientas ocupaban 580 px antes de la primera fila de datos:
en una pantalla de 1000 px entraban **tres filas**. Con lo mismo plegado entran nueve.

---

## 1. Pantallas de listado

Son la mayor parte de cualquier portal. Patrón obligatorio:

### Filtros plegados por defecto

- La tarjeta de filtros lleva la clase **`ov-filtros`** y **nada más**: el comportamiento vive una sola vez en
  `site.js`. No duplicar la lógica en cada vista.
- Arranca **cerrada** si no hay ningún filtro puesto y **abierta** si hay alguno.
- Cuando hay filtros puestos, la barra los cuenta a la vista (*«2 filtros puestos»*). **Nunca** puede pasar que alguien
  mire una lista recortada creyendo que es la lista entera: es la forma más común de tomar una decisión sobre datos
  incompletos.
- Un desplegable cuenta como filtro puesto cuando **no está en su primera opción**, no cuando tiene valor. Varios
  listados usan un valor propio como comportamiento por defecto (`Ocultar`, `Todas`) y contarlo por valor da falsos
  positivos que abren el panel siempre.

### La grilla

- Clase **`ov-tabla-datos`** en la `<table>`: densidad, encabezado en versalitas y hover, todo desde el design system.
- **Nada de encabezado pegajoso.** La grilla vive dentro de un contenedor con scroll horizontal y ahí `position: sticky`
  se despega de la fila y queda flotando sobre los datos. Un adorno que se ve roto es peor que no tenerlo.
- **Un valor vacío no se escribe quince veces.** «Sin cliente» repetido en toda una columna es ruido: va una raya
  apagada (`ov-vacio`).
- **Dato secundario debajo del principal, no en otra columna** (`ov-celda-secundaria`). El nombre del agente y su rubro
  son una celda.
- **Lo normal se susurra, lo excepcional se ve.** Quince insignias verdes de «Completada» esconden la única roja, que es
  la que hay que mirar. El estado habitual va tenue (`ov-estado-tenue`); el color pleno se reserva para lo que pide
  atención.

### Cuando la tabla no entra

Medir antes de opinar: `tabla.scrollWidth` contra `contenedor.clientWidth`. Si no entra, **no achicar la fuente ni
esconder columnas a mano**: el portal ofrece plegar la barra lateral desde el botón de menú (recupera 264 px y la
elección se recuerda). Si aun así no entra, sobran columnas: mandarlas al detalle.

---

## 2. Pantallas de conversación (hilo con un agente)

No son mensajería, son un **expediente**. La diferencia cambia toda la maqueta.

- **Columna única con línea de tiempo a la izquierda.** El chat de dos lados deja media pantalla vacía en el medio y
  obliga al ojo a saltar de un lado al otro. Peor: aprieta la respuesta del agente —que suele ser un documento largo—
  contra un borde.
- **Medida de lectura acotada a ~74 caracteres** en la respuesta. Un párrafo de 120 caracteres de ancho no se lee.
- **El pedido de la persona es la pregunta, no la respuesta**: más angosto, teñido y sin sombra. La respuesta es el
  contenido.
- **Barra de contexto pegajosa** con estado, costo y pendientes. En un hilo largo, el estado arriba de todo se pierde
  justo cuando más importa.
- **El cuadro para escribir queda acoplado abajo**, en dos renglones que crecen. Escribir no puede exigir scrollear
  hasta el final. Cada renglón que ocupa es un renglón de conversación que tapa: lo que no cambia nunca (avisos fijos,
  frases de encuadre) sube al rótulo; abajo queda solo lo que varía.
- **La trazabilidad se ve.** «Ver pasos» era un enlace gris que nadie encontraba; es una pastilla con ícono. Lo que hizo
  el agente para llegar a la respuesta es un diferencial del producto, no una nota al pie.
- **Lo que el agente propone se alinea con la respuesta que lo pidió** y arranca con un encabezado que dice cuántas son.
  Un botón de «aplicar todas» flotando lejos de las tarjetas sobre las que actúa no se asocia con ellas.

---

## 3. Grillas de tarjetas

- **Recortar el texto a una cantidad fija de renglones** (`ov-recorte-3`). Descripciones de largo dispar hacen una
  grilla imposible de comparar de un vistazo, que es justamente para lo que sirve una grilla.
- Cuidado: si el párrafo es un flex-item que crece para empujar los botones al pie, el recorte por líneas **deja de
  aplicar** y asoma un renglón cortado por la mitad. Hace falta también un tope de alto.
- Una sección con **una sola tarjeta** en una grilla de tres columnas se ve rota. O se llena, o esa sección no es una
  grilla.

---

## 4. Estados vacíos

- Un estado vacío es una **pantalla de arranque**, no un cartel de error. Ícono, una línea de qué va a aparecer acá, y
  **la acción concreta** que lo llena.
- No repetir la misma acción dos veces en la misma pantalla (encabezado + estado vacío): la persona no sabe cuál tocar.
- **Cuidado con la ventana de tiempo.** Un tablero que mira «esta semana» está vacío casi siempre para un estudio que
  trabaja por mes. La ventana se elige según el ciclo real del cliente, no según lo que es fácil de consultar.

---

## 5. Encabezado de pantalla

- Título + acción principal en la misma línea. El subtítulo corrido con puntos medios (`·`) encadenando cinco datos no
  se lee: van **chips** (`ov-tarea-chip`), uno por dato, con su ícono.
- Con chips, el bloque del título necesita `flex: 1 1 22rem; min-width: 0` **solo en escritorio**: en móvil el
  encabezado se apila en columna y ahí un `flex-grow` estira la altura, no el ancho, y abre un agujero enorme.

---

## 6. Cómo se hacen los cambios

- **Sistémico antes que por pantalla.** Un comportamiento compartido en `site.js` + una clase por vista le gana a
  reescribir veinte vistas: menos código, un solo lugar donde arreglarlo y consistencia gratis. El pase completo de los
  listados fueron ~140 líneas de CSS/JS y una clase en 16 vistas.
- **Solo tokens del theme** (`--ov-*`). Nada de colores literales: el tema oscuro se invierte solo y cualquier literal
  se nota al instante.
- **Verificar en navegador real.** Tres de los cambios se veían bien en el código y estaban rotos en pantalla: el
  encabezado pegajoso, el contador de filtros y el recorte de tres renglones. Ninguno lo habría encontrado leyendo el
  diff.
- Ojo con la captura de página completa: estira el viewport y **miente sobre todo lo que sea `sticky` o `fixed`**. Para
  juzgar una barra pegajosa o una barra lateral, captura de viewport y scroll de verdad.
