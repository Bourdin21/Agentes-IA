---
description: Como se construye la PAGINA NAVEGABLE (artifact) de un documento de entrega al cliente — envoltorio visual de marca Olvidata, capturas de produccion, estructura e indice. Complementa la 31, que define el contenido y el tono del .md fuente.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# 41 - Documento navegable para el cliente (artifact con marca Olvidata)

La `31-formato-documento-cliente` define **que dice** un documento de entrega y **como esta escrito**.
Esta define **como se ve y como se construye la pagina** que el cliente abre y comparte con su personal.

**Cuando hay `.md`, el `.md` es la fuente y la pagina es la copia de lectura.** Si los dos existen no
pueden contradecirse, y el que vale es el que se verifico contra produccion.

Un entregable puede nacer **directo como pagina**, sin `.md`, y es legitimo: pasa cuando se escribe
recorriendo produccion en vez de resumiendo documentos. En ese caso **la pagina es la fuente** y hay
que decirlo en `7-documentador.md`, para que el siguiente no la trate como una copia de un `.md` que
no existe. Lo que no es legitimo es tener los dos y que digan cosas distintas.

## Cuando aplica

- Manual de uso del sistema (completo o acotado a una entrega).
- Resumen de sprint que el cliente va a leer mas de una vez o compartir con su equipo.
- Instructivos de tramite (certificado AFIP, alta de un servicio externo).
- Cualquier entregable que el cliente vaya a **reenviar**: una pagina con link gana a un `.md` adjunto.

**No aplica** a las memorias internas de los agentes (`docs/<proyecto>/definiciones/*.md`) ni al
presupuesto cuando se manda por WhatsApp como texto.

## Regla 0 — el contenido se verifica contra PRODUCCION, no contra los documentos

Es la regla que mas cuesta cuando se omite. Los manuales previos, las definiciones y la memoria del
documentador **envejecen**: el 2026-10-14 el manual vigente de La Platense declaraba como "todavia no
esta activo" el cobro de cuenta corriente, que llevaba nueve dias funcionando en produccion.

Antes de escribir:

1. Entrar a produccion con un usuario real y **leer el menu renderizado**, no el `_Layout.cshtml`.
2. Recorrer cada pantalla y copiar **los textos que el sistema efectivamente muestra** — titulos,
   ayudas de campo, nombres de estado, opciones de combo. Esos textos son el vocabulario del manual:
   si la pantalla dice "Cuenta del negocio", el manual no dice "caja consolidada".
3. Enumerar las acciones por `grep` de los Controllers del repo **deployado**, no de la rama de trabajo.
4. Lo que no exista en produccion se declara como pendiente, con **de que depende**, nunca como
   "en proceso".

## El envoltorio visual

Marca Olvidata V2. La fuente de los tokens es `/olvidata-diseno` (`references/tokens.md`); lo que sigue
es como se aplican a una pagina de lectura larga.

### Decision de tema: oscuro, uno solo

La marca tiene **un solo oscuro** (`#0A0A0A`) y **un solo acento** (`#2B9DE4`). Una pagina de entrega
se compromete con ese mundo y **no** implementa el par claro/oscuro: se declara
`color-scheme: dark` en `:root`, se pinta `body` con su token y **todo color sale de un token**, para
que la pagina se vea igual sobre cualquier fondo del visor. Blanco, naranja y rojo estan prohibidos
como acento (el rojo de un estado de error **dentro de una captura** no cuenta: es parte de la captura).

### Tokens minimos

```css
:root {
  color-scheme: dark;
  --dark: #0A0A0A; --dark2: #111111;
  --accent: #2B9DE4;          /* no se negocia */
  --bajada: #CBD5E1;          /* texto de lectura */
  --muted: #7C8A9C;           /* terciario, rotulos */
  --blanco: #F4F7FA;          /* titulos y enfasis */
  --linea: rgba(255,255,255,.12);
  --vidrio:       linear-gradient(170deg, rgba(18,21,26,.80), rgba(10,11,13,.91));
  --vidrio-claro: linear-gradient(170deg, rgba(255,255,255,.058), rgba(255,255,255,.020));
  --vidrio-borde: rgba(255,255,255,.17);
  --glow-accent: rgba(43,157,228,.14);   /* TECHO de alfa para luz de superficie */
  --glow-fuerte: rgba(43,157,228,.42);   /* solo box-shadow de elementos chicos */
  --grilla: rgba(255,255,255,.028); --grilla-paso: 60px;
  --medida: 70ch;
}
```

- **Tipografia: Inter, una sola familia**, pesos 400/500/600/700. Mono no se usa; para cifras,
  `font-variant-numeric: tabular-nums`. Titulares con `text-wrap: balance`.
- **Fondo:** un unico resplandor de acento por debajo de `.14` de alfa, mas la reticula tecnica de 60px.
  Nada mas. Arriba de `.14` la pagina lee como neon y se abarata.

### Los dos vidrios — es la regla que arruina la pieza si se elige mal

| Clase | Va sobre |
|---|---|
| `.vidrio` (ahumado) | **contenido**: una captura del sistema, una foto |
| `.vidrio-claro` | **fondo oscuro plano**: tarjetas, tablas, avisos, numeros de paso |

**Las capturas de los sistemas de Olvidata son claras**, asi que el marco de una captura va siempre
con `.vidrio`. Un vidrio claro sobre una captura da un panel casi blanco con texto blanco encima, y
**ningun chequeo de contraste lo detecta**, porque no mira lo que hay detras del panel.

### El bloque de marca

Isotipo **real** inline (`BotPublicitario/Motion/assets/img/isotipo-color.svg`: anillo exterior, nodo
central, cuatro satelites y sus conexiones), con `fill`/`stroke` en `currentColor` y el color puesto
por token. Al lado, el logotipo `Olvidata<b>Soft</b>` **como una sola unidad de texto**.

Tres cosas que se rompen solas:

1. **El logotipo no puede ser hijo directo de un contenedor flex con `gap`**, o "Olvidata" y "Soft"
   caen como items separados y el wordmark se parte en dos. Va envuelto en su propio `<span>`.
2. **Zona de respeto = el radio del anillo exterior**, puesta como separacion real (a 30px de
   isotipo, ~13px). No se pone a ojo.
3. **El isotipo va SIN resplandor.** Un `drop-shadow` de acento sobre el trazo lo convierte en un
   logo de gaming — registro opuesto al de la marca, y ademas pasa el techo de `.14`.

El nombre del sistema del cliente (`La Platense`) **no compite con el logotipo**: va debajo, separado
por una linea de corte, como rotulo en versalita con el punto de acento. Es el sistema, no la marca.

El pie cierra con el mismo bloque en chico mas el contacto, segun el pie de firma de la `31`.

## Estructura de la pagina

```
indice lateral sticky  |  columna de lectura (max-width: var(--medida))
```

- **Indice lateral** agrupado por tema, sticky, con scroll propio. **Resalta la seccion que se esta
  leyendo** (`aria-current="true"`) y, si queda fuera de vista dentro del propio indice, se trae sola
  — con `scrollTop` calculado sobre el `<nav>`, nunca con `scrollIntoView`, que arrastra la pagina.
  En ancho de telefono el indice pasa a una fila de pildoras arriba.
- **Secciones numeradas** (`01`, `02`, …) solo si el documento se lee en orden. La numeracion es
  informacion, no decoracion: si el orden no importa, no van.
- **Pasos numerados** para cada flujo no trivial, con la frase inicial en negrita — es el mismo
  criterio de la `31`, llevado a HTML.
- **Tablas** para variantes por categoria (medios de pago, estados, roles), cada una en su contenedor
  con `overflow-x: auto`: el cuerpo de la pagina nunca scrollea en horizontal.
- **Avisos** en dos tonos y nada mas: `.aviso` (acento) para lo que hay que saber, y
  `.aviso--pendiente` (gris) para lo que todavia no esta. Un pendiente se escribe con **de que
  depende y que consecuencia tiene**, nunca como "proximamente".
- **Tarjetas de hueco** al principio, cuando el documento tiene que explicar *que resuelve*: rotulo
  "Antes", titulo = el hueco, cuerpo = como lo tapa el sistema. Una por hueco real del negocio.
- **Ultima seccion: plan de arranque u orden sugerido**, cuando el cliente todavia no opera el sistema.

## Las capturas

- **De produccion, con datos reales**, no de desarrollo ni con datos inventados.
- **Solo GET.** El unico POST que se hace es el login. No se confirma, no se emite, no se cierra nada.
- Ventana de 1500×940, `deviceScaleFactor: 2`, `locale: 'es-AR'`,
  `timezoneId: 'America/Argentina/Buenos_Aires'`. Se incluye el menu lateral: ubica al lector.
- Se bajan a **1500px de ancho, WebP calidad 80** (~45 KB cada una) antes de publicar. 30 capturas
  entran en menos de 2 MB.
- **Cada captura lleva epigrafe y el epigrafe dice que mirar**, no repite el titulo de la pantalla.
- Si el sistema todavia no tiene operaciones cargadas, los listados salen vacios: el peso de las
  capturas se pone en los **formularios**, que si muestran como se usa.

### Privacidad

Las capturas de produccion traen nombres, CUIT y saldos reales. El artifact **nace privado** y eso se
le dice al cliente en la misma linea en que se le pasa el link. Nunca se publica una captura con una
pantalla de credenciales, ni se escriben usuarios o contraseñas en el documento.

## Verificacion antes de publicar

1. Renderizar la pagina una vez y mirarla. **Una pasada de correcciones, no un ciclo.**
2. **Ancho de telefono (400px): `scrollWidth === innerWidth`.** Se mide, no se supone.
3. **Cero errores de consola** (`pageerror`).
4. El indice marca la seccion correcta al abrir, en el medio y al final del documento.
5. Toda afirmacion del texto tiene su origen: una pantalla de produccion, un documento de definiciones
   o una decision registrada en `trazabilidad.md`. **Lo verosimil no se publica** (`MARCA.md` §0).

## Trampas medidas, para no volver a pagarlas

- **El navegador se apunta a `https://127.0.0.1`, nunca a `localhost`** cuando la captura es local:
  Chromium resuelve `localhost` a `::1` y Kestrel escucha en IPv4.
- **Los endpoints `Listar` de los listados son POST** (DataTables server-side): pedirlos por GET
  devuelve un 405 maquillado de pagina. Los ids se cosechan del DOM **despues** de que la tabla cargo
  (esperar ~5 s), no del endpoint.
- **`page.click('form button[type=submit]')` engancha el boton de logout del layout.** Para enviar un
  formulario: `document.querySelector('input[name=...]').closest('form').requestSubmit()`.
- Los scripts de captura se escriben con la herramienta de escritura de archivos, **nunca con un
  heredoc de bash**: se come los backslashes de las rutas de Windows.

## Donde queda cada cosa

- El `.md` fuente, en `docs/<proyecto>/`.
- La pagina, publicada como artifact privado. **Su URL se anota en `7-documentador.md`**, junto al
  nombre del `.md` que la origina — si no queda anotada, la proxima entrega publica una pagina nueva
  en vez de actualizar la que el cliente ya tiene.
- Para actualizar una pagina ya entregada se republica **sobre la misma URL**: el cliente ya la
  compartio con su personal y un link nuevo deja al equipo leyendo la version vieja.
