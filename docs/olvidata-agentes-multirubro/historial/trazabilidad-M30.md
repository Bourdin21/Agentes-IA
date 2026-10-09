<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-09 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - M30 (2 bloques archivados)

- 2026-10-03 - M30 (el menu en seis secciones) y M31 (la barra de opciones y el isotipo) CERRADOS
- 2026-10-05 - Despliegue a produccion de la quinta pantalla, M30 y M31

---

## 2026-10-03 - M30 (el menu en seis secciones) y M31 (la barra de opciones y el isotipo) CERRADOS

**QA: los dos APTO, 23/23 criterios PASS, 0 FAIL, 0 BLOCKED, cero defectos.** 1243 tests verdes, build limpio, sin
migracion, 2 commits locales sin push. **Nada publicado ni desplegado.**

### M30 — El menu, de cuatro secciones a seis

- **Pedido de Joaquin: «reestructurar opciones de menu».** Se le ofrecieron tres alcances y eligio **la reestructura
  completa**. El criterio **no cambio**: sigue siendo el de M27 —*el nombre de cada seccion contesta «¿cuando entro
  aca?»*—; lo que cambio es que se aplico a tres lugares donde el menu se habia escapado.
- **Los tres hallazgos, ninguno de gusto:**
  1. **Las cuatro conversaciones de plataforma habian quedado en TRES secciones distintas.** *Chat libre* en «Trabajo
     diario», *Automatizar* en «Empezar aca», *Configurar* y *Repartir* en «Tu forma de trabajar». **M28 metio la cuarta
     hermana en otra seccion y nadie reviso el conjunto.**
  2. **«Administracion y cuenta» tenia 9 items y tres no eran administracion, y la etapa de entrega lo demuestra:**
     *Pedidos* y *Material de Olvidata* caen en `PrimerosPasos` —se ven el dia uno y no exigen ser Director—, y
     *Pedidos* tiene escrito en su propio comentario *«cualquier miembro los arma y los revisa»*. Estar en la seccion
     que el codigo define como «lo del Director y lo de la cuenta» es una **contradiccion verificable**, no una opinion.
  3. **«Tu forma de trabajar» mezclaba escribir con correr.** Reglas/Instructivos/Memoria son `TuFormaDeTrabajar`;
     Programaciones/Resultados/Pruebas son `SistemaCompleto`: **la etapa ya las separaba y la seccion no.**
- **Reparto nuevo: 1 · 4 · 7 · 3 · 3 · 8 = 26.** **D-06: se movio SOLO de seccion.** Ningun rotulo, icono, ruta, etapa
  ni rol cambio, y `EtapasEntrega.cs` no se toco.
- **RD-01 era el riesgo y quedo cerrado con un test de mutacion.** Mover items es exactamente donde se escapa un
  permiso (antes de M27, *Miembros* colgaba de un `@if (EsDirector)` que envolvia a varios). El test compara, opcion por
  opcion, contra `OpcionesVisibles(etapa, esDirector)` —**la tabla rotulo→opcion esta duplicada a proposito en el
  test**, porque derivarla del menu haria que un cambio pasara los dos lados a la vez—. Quitandole su `OpcionMenu` a
  *Miembros*, el defecto literal de RD-01, **fallan las tres variantes**.
- **QA verifico las 6 combinaciones etapa × rol contra `OpcionesVisibles`: 12/10 · 19/14 · 26/19, exactas.** Las 26 rutas
  devuelven 200 y el Empleado contra las 7 de Director recibe acceso denegado en 6; la septima (`Pruebas`) abre en solo
  lectura **por decision declarada de M22** y `Correr` responde 403.

### M31 — La barra de opciones del chat, y la pieza que por fin es la marca

- **Dos pedidos de Joaquin:** las cuatro acciones a una **barra lateral derecha** como configuracion del chat, que **no
  ocupe mucho porque lo importante es el chat**; y que `piezaChatLibre`, que tenia un **icono generico**, sea algo de la
  **marca**, diseñado con el isotipo de Olvidata.
- **Sobre la herramienta pedida (`/motion-graphics`): se tomo la idea entera y se cambio el medio.** Esa tuberia produce
  un MP4 o un WebM con alfa, y para este destino es la herramienta equivocada **por una razon de fondo: un video trae
  los colores quemados**, asi que no puede seguir el tema claro y el oscuro, que es requisito del portal (CA-07.4), y
  pesa mas que lo que reemplaza. (Secundario: declara macOS o Linux y la maquina es Windows.) La pieza se anima **en la
  pagina**, con los tokens `--ov-*`, que es lo unico que hace que los dos temas salgan gratis.
- **El hallazgo que vale mas que el pedido:** **el isotipo de Olvidata YA ES el diagrama de esta pantalla.** Es un
  **nucleo central con cuatro nodos** radiando en diagonal: *una conversacion en el centro y cuatro cosas que se traen
  mencionando* — las mismas cuatro que ahora viven en la barra. No hubo que inventarle un significado: ya lo tenia. Por
  eso la pieza deja de ser un adorno con el color de la marca y pasa a ser **la figura de la pantalla**.
- **El isotipo se MIDIO, no se calco de memoria** (RD-04: un isotipo torcido se compara con el logo de la pestaña, que
  esta a diez centimetros). Transformada de distancia sobre el PNG real: nucleo r=164,3; nodos r=95,5 / 83,4 / 74,5 /
  125,4; semiancho de brazo 38,9. **Es asimetrico a proposito —los brazos van de 35° a 48°— y se copio asi.** QA
  confirmo que el SVG coincide numericamente con el PNG, asimetria incluida.
- **Dos decisiones del implementador, las dos buenas:** la rotacion **oscila** (±0,42 rad) en vez de dar la vuelta,
  porque una vuelta entera deja la figura de canto al lado del logo de la pestaña; y el pulso **no cambia de color**, es
  un engrosamiento del brazo, asi se ve igual en los dos temas.
- **La version plana dejo de ser dos anillos y un punto** —que no eran nada— y pasa a ser **el isotipo quieto en SVG**:
  con movimiento reducido la pantalla no pierde significado, solo pierde la animacion.
- **El plegado de movil reuso el mecanismo `ov-filtros` entero**, y encajo mejor de lo que suponia el diseño: su regla
  de *«arranca abierto si hay algo puesto»* **cuenta casillas tildadas**, que es exactamente RD-03 — no hubo que
  escribir nada. Lo unico cableado era el texto, que se parametrizo con los valores viejos como default, asi los
  diecisiete listados no cambian (QA lo verifico).
- **D-10 intacto y verificado de la forma correcta:** el test afirma que la compuerta de `prefers-reduced-motion` esta
  **antes del `import()` por posicion en el archivo**, no por presencia — es la unica forma de que signifique «no se
  baja un byte». QA lo confirmo en la pestaña de red, y que al enviar **el canvas sale del DOM** (rAF congelado).
- **Adjuntar se quedo en el compositor** (D-02): un archivo adjunto es **contenido del mensaje**, no configuracion, y
  partir una sola interaccion en dos lugares es peor que la inconsistencia que arregla.

### Dos trampas de medicion que QA dejo anotadas

El menu se lee **cacheado 60 s** (`ResolvedorSesion.Ttl`), y `jQuery.trigger('change')` **no dispara listeners nativos
de ancestros**. Las dos casi producen un FAIL falso; las dos quedaron en la memoria de QA.
## 2026-10-05 - Despliegue a produccion de la quinta pantalla, M30 y M31

- **`scripts/deploy-prod.ps1 -Force` contra agentes.olvidata.com.ar.** Arbol limpio, HEAD en `4c70808`,
  **1243 tests verdes corridos antes de tocar nada**. **Sin migraciones nuevas**: las dos de M29
  (`DocumentoSinClienteM29`, `DuenoDelTransitorioM29`) ya se habian aplicado en el despliegue del 2026-10-02, asi que
  el paso de migracion no cambio el esquema.
- **Lo que fue:** la quinta pantalla de subida (`Agentes/Ejecutar` sin cliente), **M30** (el menu en seis secciones) y
  **M31** (la barra de opciones del chat y la pieza que pasa a ser el isotipo). **21 archivos actualizados**, ninguno
  agregado ni borrado.
- **Verificado desde afuera, sin tocar datos:** `/health/vivo` 200 y `/Account/Login` 200; y los tres archivos que
  cambiaron llegaron con su tamaño nuevo — `site.js` 30.449 -> **31.216** (el plegado parametrizado), `site.css`
  71.420 -> **74.702** (la barra y el isotipo) y `chat-libre-3d.js` 8.505 -> **14.329** (la geometria del isotipo, con
  34 menciones de nucleo/nodo/brazo en el archivo servido: **la pieza nueva es la que esta en produccion**, no la vieja
  cacheada).
- **Lo que sigue sin cambiar: el saldo de Anthropic.** El codigo esta entero en produccion, pero **ninguna tarea de
  agente funciona** hasta que haya credito, y el chat libre sigue sin publicar (agente en Borrador, menu que no lo
  ofrece). Este despliegue no mueve esa aguja ni la empeora.
