# Memoria - QA

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-10-03 (QA M30+M31: menu en seis secciones y pantalla del chat libre -- APTO los dos, 23 criterios PASS, 0 defectos) | 2026-10-02 (QA M29 RONDA DE RE-VERIFICACION y CIERRE: OLV-038, OLV-039 y OLV-040 cerrados; 1 defecto nuevo OLV-041 minor -- M29 APTO CON REPAROS, liberable) | 2026-10-02 (QA M29 lote 1 de 2: la casilla de internet, la frontera del portal del cliente y el dueno del transitorio -- APTO, 1 defecto menor OLV-040) | 2026-10-02 (QA M29 lote 2 de 2: subir sin cliente, guardar/descartar y la purga -- apto con reparos, OLV-036 cerrado, 2 defectos nuevos) | 2026-10-02 (QA M28 RONDA DE RE-VERIFICACION: los seis defectos cerrados, los cuatro BLOCKED calificados, tres defectos nuevos) | 2026-10-02 (QA M28 lote 3 de 3: propuestas, adjuntos y la pantalla) | 2026-10-02 (QA M28 lote 2 de 3: menciones, resolucion y delegacion) | 2026-10-02 (QA M28 lote 1 de 3: arranque, permisos e historial del chat libre) | 2026-10-01 (plan de QA de M27 escrito, sin ejecutar)

## Definiciones vigentes

# QA M30 + M31 - El menu en seis secciones y la pantalla del chat libre (2026-10-03)

**VEREDICTO DE LIBERACION: M30 APTO - liberable. M31 APTO - liberable.** 23 criterios en PASS, 0 FAIL, 0 BLOCKED,
**0 defectos nuevos**, ningun parte de defecto emitido. No quedan defectos abiertos de la corrida anterior (OLV-041 se
cerro el 2026-10-02 con M29).

- Repo bajo prueba: `C:\Sistemas\Olvidata Agentes Multi-rubro`, commits **`27c2814`** (M30) y **`4c70808`** (M31).
  **Read-only**: `git status --porcelain` limpio al cerrar (solo `.claude/worktrees/`, ajeno a esta corrida).
- Entrada leida por artefactos, sin la transcripcion del implementador: `5-implementador.md` lineas 8 (M31) y 104 (M30),
  «Diseno M31» (D-01..D-11, RD-01..RD-04) y «Diseno M30» (H1/H2/H3, D-01..D-07, tabla literal, que ve cada etapa,
  RD-01..RD-04) en `2-disenador-funcional.md` linea 8, e instruccion `38` completa.
- Organizacion propia **tenant 31 `qa-m30`** (Directora `dirm30@qa.test`, Empleado `empm30@qa.test`), creada y
  **borrada entera** al cerrar (39 tablas con `TenantId` + `AspNetUsers` + `Licencias` + `Tenants`; verificado en 0).
- Costo cero verificado: linea **«Motor de agentes con MODELO SIMULADO ... el costo es cero»** en los **tres** arranques
  y `grep -c anthropic.com` = **0** en los tres logs.
- MCP de Playwright: **funciono** (contextos aislados, `addInitScript`, `MutationObserver`, `reducedMotion`, cookie
  `crm-tema`). Nada se califico por lectura de codigo.
- Ultima validacion de reglas cross-proyecto: **2026-10-03**. `git log --since=2026-10-02` sobre
  `32-estandares-qa-implementador.instructions.md`, `38-diseno-pantallas-portal.instructions.md` y
  `docs/qa/regresiones-manuales.yml`: **ninguna regla agregada ni modificada**. No hubo reglas nuevas que ejecutar.

## Trampa de medicion que casi produjo dos falsos FAIL (queda escrita)

1. **El menu se lee cacheado 60 s.** `ResolvedorSesion.Ttl` cachea la sesion -incluida `EtapaEntrega`- por usuario y por
   proceso. Cambiar la etapa con `tenant-config` y releer el menu en el mismo minuto devuelve la etapa **anterior**:
   `TuFormaDeTrabajar` se leia identica a `PrimerosPasos` con la base ya en `2`. Es el limite declarado RT-01, no un
   defecto. Entre cambio de etapa y lectura hay que dejar pasar el TTL.
2. **`jQuery.trigger('change')` no dispara los `addEventListener` de los ancestros.** El contador de filtros escucha
   `change` en la tarjeta: movido por jQuery parecia roto (siempre «Filtros»), y con
   `dispatchEvent(new Event('change',{bubbles:true}))` cuenta perfecto. El guion de memoria para mover los Select2 sirve
   para la XHR, **no** para verificar un listener nativo de arriba.

## M30 - cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| Las 26 opciones en 6 secciones, orden y reparto 1·4·7·3·3·8 | **PASS** | `SistemaCompleto`+Director renderiza exactamente: Empezar aca(1) · Conversando(4) · Trabajo diario(7) · Tu forma de trabajar(3) · Lo que corre solo(3) · Administracion y cuenta(8) = **26**, rotulos identicos a la tabla literal |
| 3 etapas × 2 roles = exactamente `EtapasEntrega.OpcionesVisibles` | **PASS** | 6 renders leidos del DOM: PP 12 Dir / 10 Emp · TFT 19 / 14 · SC 26 / 19. Ni una opcion de mas ni de menos contra el contrato (`SoloDirector` = Miembros, Areas, Conexiones, Configurar, Repartir, PortalClientes, Pruebas) |
| Ningun rotulo ni ruta cambio; cada opcion llega a donde dice | **PASS** | Las **26 rutas visitadas: 26 × HTTP 200** con el `<title>` correspondiente (`/`, `/ChatLibre`, `/Analista`, ..., `/Programaciones/Resultados`, `/Notifications`). Iconos observados en los 12 de `PrimerosPasos`, identicos a `MenuOrganizacion` |
| Las dos secciones nuevas no se dibujan vacias (D-M27-19) | **PASS** | En `PrimerosPasos`, con los dos roles, **no existe el encabezado** «Tu forma de trabajar» ni «Lo que corre solo»; en `TuFormaDeTrabajar` tampoco «Lo que corre solo» |
| «Conversando» 2 de 4 en `PrimerosPasos` es deliberado | **PASS** | Chat libre + Automatizar (ambos `PrimerosPasos`); Configurar y Repartir faltan por etapa **y** por rol, incluso para la Directora |
| Resaltado del item activo, incluido Programaciones/Resultados | **PASS** | `/Programaciones` → solo «Programaciones»; `/Programaciones/Resultados` → solo «Resultados»; `/ChatLibre` → «Chat libre»; `/Tareas` → «Tareas» |
| RD-04 — el scroll a 1440 y a 390 | **PASS** | `.ov-sidebar-nav` 1691/755 px: hay scroll, pero «TRABAJO DIARIO» queda a **373 px** (vh 900) y a **242 px** (vh 844). **No hay que scrollear para llegar a lo de todos los dias** |
| Un enlace de mas no se abre | **PASS con observacion** | Empleado contra las 7 rutas de Director: **6 dan `Acceso denegado`** (`/Account/AccessDenied?ReturnUrl=...`). `/Pruebas` **abre en solo lectura**, que es la decision declarada de M22 («ver, cualquier miembro; correr, quien dirige»), y `POST /Pruebas/Correr` devuelve **403 «Las pruebas de la empresa las maneja quien la dirige.»**: el gasto esta fail-closed del lado del servidor |

**El riesgo numero uno de M30 -que se escape un permiso al mover items- no se materializo.** Las 9 opciones que
cambiaron de seccion conservaron etapa y rol; el contrato se verifico contra `EtapasEntrega`, no contra «lo mismo que
antes».

## M31 - cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| D-01 — la barra a la derecha y por debajo del chat | **PASS** | `aside.ov-chat-opciones.ov-filtros` en x=1181 (ancho 221 px), `background: rgba(0,0,0,0)`, `box-shadow: none`, 13 px / `rgb(100,116,139)` contra el compositor en 16 px sobre tarjeta blanca |
| D-01 (juicio pedido) — ¿el ojo va al chat o a la barra? | **PASS** | Mirada a la captura de viewport, claro y oscuro: el orden es **pieza → cuadro de escribir → barra**. La barra es lo ultimo que se registra; no compite |
| RD-01 — el compositor no baja de ~62 ch a 1440 | **PASS** | 819,5 px / 10,09 px por `ch` = **81,2 ch** |
| D-03 — las cuatro acciones escriben la mencion, no una pregunta | **PASS** | Las 4 dejan exactamente `@` · `@regla ` · `@tarea-programada ` · `@instructivo `, `selectionStart` al final y el textarea enfocado. La primera abre el autocomplete `.ov-menciones` |
| Fail-closed de la casilla, las dos condiciones por separado | **PASS** | Con `BusquedaWeb__Habilitada=false` **y** (reinicio aparte) con `BusquedaWeb__PrecioPorBusquedaUsd=0`: `input[name=PermiteBusquedaWeb]` **no existe** y la barra queda con las 4 acciones |
| D-02 — adjuntar se quedo en el compositor | **PASS** | `input[type=file]` y el boton «Adjuntar documentos» **fuera** del `<aside>`, pegados al textarea |
| D-05 — a 390 no hay barra, hay plegado cerrado | **PASS** | aside de 41,6 px de alto, solo «Opciones del chat», **debajo** del compositor (bottom 564) y **encima** de Enviar (top 775). Al tocarlo pasa a 270 px con las 4 acciones y la casilla |
| RD-03 — arranca abierto si la casilla esta marcada | **PASS** | Tras el POST con la casilla puesta: `ov-filtros--abierto ov-filtros--con-filtros` y el rotulo dice **«Buscar en internet, activado»** |
| Los 16 listados no cambiaron con la parametrizacion | **PASS** | `/Tareas`, `/Reglas`, `/Aprobaciones`, `/Instructivos`: siguen con rotulo «Filtros» y sin `data-plegable-*`. Contador verificado con eventos nativos: **«1 filtro puesto» → «2 filtros puestos»** |
| `ov-form-actions` sticky contra el grid (riesgo declarado) | **PASS** | A 390, scrolleando de verdad: Enviar en top 794 → 678 → 794 con vh 844, **siempre dentro del viewport**. `position: sticky; bottom: 0px` intacto |
| D-07/RD-04 — el isotipo, no una figura de memoria | **PASS** | SVG medido contra `isotipo_sin_anillo_color.png`: nucleo (749,749) r164 · nodos (414,414) r96 · (1109,495) r83 · (1154,1064) r75 · (390,1154) r125. **Asimetrico igual que el PNG** (brazos a ~45° a la izquierda y ~37° a la derecha, nodos izquierdos mas grandes) |
| D-08 — el movimiento se puede mirar de reojo | **PASS** | 22 muestras en 24 s: el ancho del dibujo va de 127 a 132 px (**4 %**) y el centro se mueve 4 px. **Oscila, nunca queda de canto, no tira del ojo**. Pulsos visibles viajando del nodo al nucleo en brazos distintos |
| D-10 — con `prefers-reduced-motion` no se baja un byte | **PASS** | Emulado con `reducedMotion:'reduce'`: en la pestana de red **no aparece `three.module.js`** (si aparece en el camino normal: `cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js`). Queda el SVG quieto |
| D-09 — sin WebGL y con el CDN bloqueado queda el isotipo | **PASS** | `getContext('webgl')` anulado: 0 canvas, SVG con 5 circulos + 4 lineas, alto 198 px. Con `route('**/three*', abort)`: lo mismo. **Ni hueco ni dos anillos** |
| D-10 — al enviar, la pieza se DESMONTA | **PASS** | `MutationObserver` sobre `#piezaChatLibre` guardado en `sessionStorage` y leido **despues** de navegar: `{"quitado":"CANVAS","rafAlQuitar":214}` con el contador de `requestAnimationFrame` congelado en 214 (iba en 210 al enviar). **Sale del DOM, no `display:none`** |
| CA-07.4 — claro y oscuro, a 1440 y a 390, con tokens | **PASS** | Todo invierte: barra `rgb(100,116,139)`→`rgb(148,163,184)`, rotulo `rgb(30,41,59)`→`rgb(241,245,249)`, textarea `#fff`→`rgb(30,41,59)`. **Ningun color literal clavado**; `--ov-primary` = `#2b9de4` en los dos |

## Cobertura del catalogo cross-proyecto

| Id | Aplica | Resultado |
|---|---|---|
| REG-010 · KOI-003 | Si (menu por rol) | **PASS** — 6 renders contra `OpcionesVisibles`, sin item de mas ni de menos |
| KOI-005 · KOI-006 | Si (link de sidebar a controller inexistente) | **PASS** — 26/26 rutas en 200, ningun 404 |
| OLV-028 | Si (item de conversacion de plataforma sin version publicada) | **PASS** — los 4 agentes de plataforma con version `Publicada` y las 4 pantallas en 200 |
| OLV-035 | Si (el arreglo en el menu y la otra superficie olvidada) | **PASS** — M30 no cambio **ninguna** ruta, asi que las tarjetas del tablero y `Primeros pasos` apuntan a las mismas 26 URLs, todas en 200 |
| OLV-001..004 · OLV-009 | Si (contraste por tema en pantalla nueva) | **PASS con observacion** (ver abajo) |
| OLV-021 · OLV-022 | No | M30/M31 no agregan rol ni publico nuevo |

## Observaciones (no son defectos, no bloquean)

1. **El texto apagado de la barra mide 4,3:1 en tema claro** (`#64748B` sobre `#F0F4F8`), apenas por debajo de AA 4,5
   para 13 px. **No se reporta como defecto de M31**: es el token `muted` compartido de todo el portal, no un color que
   esta entrega haya elegido. Queda anotado para el disenador si algun dia se toca el token.
2. **A 1440×900 hay que scrollear para llegar a «Administracion y cuenta»** (nav de 1691 px con 755 visibles). Es el
   costo aceptado de D-M30-07 y es la seccion que menos se abre; lo que RD-04 pedia proteger -«Trabajo diario»- queda
   arriba del pliegue en los dos anchos.
3. **`/Pruebas` es la unica de las 7 opciones de Director cuya URL abre.** Es la decision declarada de M22 y la escritura
   esta cerrada con 403 del lado del servicio. No es un hueco de M30, que no toco permisos.

## Checklist de merge

- [x] Build limpio y 1243 tests verdes segun el implementador; sin migracion EF (verificado: ninguna entidad tocada).
- [x] 23/23 criterios en PASS con evidencia observada; 0 FAIL, 0 BLOCKED.
- [x] Riesgo RD-01 de M30 (permiso que se escapa al mover un item) cerrado contra el contrato, no contra el diff.
- [x] Riesgo declarado del `ov-form-actions` sticky cerrado en navegador real a 390.
- [x] Datos de QA borrados; base devuelta al estado previo.
- [x] `git status --porcelain` limpio en el repo bajo prueba.
- [ ] Sin push ni deploy: queda a criterio de Joaquin.


# QA M29 RONDA DE RE-VERIFICACION y CIERRE - El chip del hilo, el camino unico de guardar y el mensaje de la subida (2026-10-02)

**VEREDICTO DE LIBERACION DE M29 COMPLETO: APTO CON REPAROS - liberable.** Los **tres defectos abiertos quedan
CERRADOS** con evidencia observada, incluida la prueba que ya habia salido mal una vez (los bytes despues del movimiento
de carpeta). El unico reparo es **OLV-041 (minor, nuevo)**: el arreglo cerro la mitad de D-02 que faltaba -la leyenda del
transitorio- y dejo afuera la otra mitad -el nombre del cliente-, asi que en el hilo un archivo guardado no dice donde
quedo. No bloquea: no hay perdida de datos, no hay camino sin salida y el cambio de estado si se ve. Se cierra en la
proxima ronda.

- Repo bajo prueba: `C:\Sistemas\Olvidata Agentes Multi-rubro`, commit **`1e71bed`** (base de los arreglos: `8fef7ae`).
- Entrada leida por artefactos, sin la transcripcion del implementador: `5-implementador.md` linea 8 (la ronda de
  arreglos y sus 8 pruebas minimas), los partes de los lotes 1 y 2 de este mismo archivo, D-02/D-03/D-04 y RD-02/RD-04 de
  "Diseno M29" (`2-disenador-funcional.md` linea 8).
- Organizacion propia **tenant 30 `qa-m29r`** (Directora `dirq@qa.test`, Empleado `otroq@qa.test`, clientes 80 Alfa / 81
  Beta / 82 Gama), creada y **borrada entera** al cerrar. Un solo portal en el 7200: ningun motor ajeno corriendo tareas
  propias, al reves de lo que paso en el lote 2.
- Costo cero verificado: linea **"Motor de agentes con MODELO SIMULADO ... el costo es cero"** en los dos arranques y
  `grep -c anthropic.com` sobre el log = **0**. Agente del chat libre: artefacto 121 version 147, ya `Publicada`.
- MCP de Playwright: **funciono** (contextos aislados, `setInputFiles`, `getComputedStyle`, cookie `crm-tema` para el
  oscuro). Nada se probo por lectura de codigo salvo lo que se declara como tal.
- Ultima validacion de reglas cross-proyecto: **2026-10-02**. Se rehizo el diff de `32` y del catalogo desde el lote 1 de
  hoy (`git log --since`): **ninguna regla agregada ni modificada**, asi que las 5 que aplican (MH-041, ELV-008, ELV-009,
  MH-045, MH-047) se arrastran con el PASS del lote 1 y no se re-ejecutan.

## Los tres defectos

| Defecto | Estado | Evidencia observada |
|---|---|---|
| **OLV-038** (major) | **CERRADO** | Reabierta `/Tareas/Detalle/9289` (tarea finalizada, no el compositor del arranque): `#conversacion [data-guardar-adjunto]` = **`[140,141,142]`** -era 0- y el adjunto que ya tiene cliente (138) sigue en **0** (control negativo). Guardado el 140 desde el chip del hilo: `POST /Documentos/AsignarCliente -> 200 {success:true}`, `GET /Tareas/Progreso/9289 -> 200` (el hilo lo vuelve a pedir al servidor), base `ClienteCarteraId=81` y `VersionToken 0->1` **sin volver a subir**, blob movido de `30/_organizacion/5fd7eb80...` a `30/81/5fd7eb80...` y **nada quedo** en `_organizacion`. |
| **OLV-039** (minor) | **CERRADO** | Chip del transitorio en el hilo: `borderStyle: dashed`, `borderColor rgb(148,163,184)` (= `--ov-gray-400`), texto "solo en esta conversacion". Chip con cliente: `solid`, `rgb(226,232,240)`. En **oscuro**: `dashed rgb(148,163,184)` contra `solid rgb(51,65,85)` - distinguible en los dos temas. **Sin fecha ni cuenta regresiva** (regex de fecha/dias/horas/vence sobre el texto del chip: sin coincidencias; los unicos digitos son los del nombre del archivo). Mismas clases y misma leyenda que el compositor. |
| **OLV-040** (minor) | **CERRADO** | `POST /Documentos/Subir` con el archivo presente y **28 valores distintos** de `clienteId` (`abc`, `../../otro`, `0`, `-1`, `1.5`, `99999`, `2147483648`, `-2147483649`, `null`, `[]`, `{}`, `%00`, `NaN`, `true`, arabe-indio, `1e2`, `Infinity`, `80;81`, `80,81`, `abc`+`80` duplicado, vacio, un espacio, ausente, `0x50`, `+80`, `80 `, ` 80`, `80.0`): **ninguno** devuelve "Elegi un archivo". Los que no parsean -> **404 "El cliente no existe."**. Control positivo en la misma tanda: **sin** archivo -> "Elegi un archivo.", tanto con `clienteId=80` como con `clienteId=abc`. |

## Criterios tocados

| Criterio | Estado | Evidencia |
|---|---|---|
| **CA-03.1 / HU-04** (guardar despues de enviar) | **PASS** | La accion existe en el hilo reabierto y guarda de verdad (fila + blob + version). |
| **Las dos superficies funcionan** | **PASS** | Hilo (`#conversacion`, Razor) y compositor de `Detalle` (`#chipsSeguimiento`, JS): los dos marcan el boton y los dos guardan. Compositor: `POST ... {success:true}` y el chip repinta a "unico-uno.txt | Cliente Beta QA" sin recargar. |
| **El boton sobrevive al repintado del hilo** | **PASS** | Guardado el 140, el hilo se reemplaza entero (el nonce puesto en el chip del 141 desaparece) y **acto seguido el boton del 141, nacido en el DOM regenerado, abre el modal y guarda** (`modalGuardarEnCliente` abierto, `success:true`, acciones `[140,141,142] -> [141,142] -> [142]`). Es exactamente lo que un listener directo no habria sobrevivido. **Matiz honesto:** el sondeo de 10 s **no corre en una conversacion terminada** (`if (!esFinal()) iniciar()`), asi que el reemplazo observado es el que dispara `ov:adjunto-guardado`, no el del intervalo. Es el mismo `refrescar()` y el mismo reemplazo de `cont.innerHTML`: el mecanismo queda probado, el disparador del intervalo queda probado por construccion. |
| **El chip cambia de estado en las dos superficies** | **PASS parcial - OLV-041** | Hilo: `dashed + leyenda + accion` -> `solid, sin leyenda, 0 acciones`. Compositor: -> `solid + "Cliente Beta QA"`. El cambio se ve en las dos, **pero solo el compositor nombra el cliente**. |
| **RD-04** (duplicado por hash contra ESE cliente) | **PASS** | Guardar un transitorio en el cliente que ya tiene esos bytes -> `{success:false, "Este archivo ya esta cargado para este cliente como <<testigo2 (2).txt>>."}`, toast de error en el momento, modal abierto y el archivo **sigue transitorio** (dashed + leyenda + accion). |
| **RD-04** (cuota por cliente) | **PASS** | Con `Documentos__MaxPorCliente=1`: guardar en Cliente Beta QA (2 documentos) -> `{success:false, "Este cliente ya tiene 1 documentos..."}` y el archivo queda transitorio. **Control positivo en la misma tanda:** el MISMO archivo en Cliente Gama QA (0 documentos) -> guardado. La cuota se evalua contra **ese** cliente, no global. |
| **Los bytes despues del movimiento** | **PASS** | `GET /Documentos/Descargar/140` -> 200, **7854 bytes, 202 lineas**, primera "M29 re-verificacion OLV-038: bytes testigo 2026-10-02", ultima "linea 0199 de control para el checksum", hash32 `386125290` - identico al original y al del doc 141 (mismo origen). En disco, `sha256` del blob movido = `8fa73306900083a7...`, el del archivo subido. **El movimiento no toco un byte.** |
| **CA-02.1** (OLV-040) | **PASS** | Los 28 valores de arriba. |
| **CA-02.4** (el transitorio en ningun listado) | **PASS, sin aflojar** | Modal "elegir": los checkboxes ofrecidos son **solo** `[138]`, los transitorios no aparecen. `POST /Documentos/Listar` con `clienteId` vacio/80/81/82: los ids 137, 139 y 142 **no salen en ninguno** (vacio y 82 devuelven `recordsTotal:0`). `/Documentos/Index` de los tres clientes: solo los que tienen cliente. |
| **B-07** (id de otra conversacion) | **PASS, sin aflojar** | `POST /Tareas/EnviarSeguimiento` con `TareaId=9290` y `DocumentoIds=142` (transitorio de la 9289) -> `success:false, "Uno de los documentos no es de este cliente."`. Idem con los dos huerfanos (137, 139). **Control positivo:** el 142 en **su propia** 9289 -> `success:true`. |
| **RD-02 / D-02 / D-04** | **PASS con reparo** | D-04 y RD-02 completos (ver OLV-039). D-02 a medias: el contraste "solo en esta conversacion **contra el nombre del cliente**" tiene un solo lado en el hilo -> **OLV-041**. |
| **El miembro que no es el autor** (punto 5, declarado sin test) | **BLOCKED - el caso no existe** | `otroq@qa.test` sobre `/Tareas/Detalle/9289` -> **404**, y el candado esta **aislado**: `ServicioTareas.Visibles()` filtra `t.UsuarioId == usuarioId` para todo el que no sea staff, asi que **ningun** miembro no-autor abre **ninguna** tarea. El `else if` de `Detalle.cshtml` no se llega por ahi. Se intentaron los otros dos caminos de `PuedeAdjuntar = esAutor && tareaPrincipal is null && !clienteDadoDeBaja`: una subtarea no tiene adjuntos de persona, y `clienteDadoDeBaja` **fabricado** sobre la 9289 apaga tambien `Disponible`, asi que `SePuedeGuardar` cae y con el la condicion del modal. **Lo que si queda probado es el riesgo que importaba:** el chip ofrece sii `SePuedeGuardar && PuedeNuevaTarea`, y el modal entra sii `PuedeAdjuntar || (PuedeNuevaTarea && HayAdjuntosParaGuardar)` con `HayAdjuntosParaGuardar` = "algun adjunto con `SePuedeGuardar`"; entonces **si algun chip ofrece, el modal esta** - no hay estado donde el boton abra nada en silencio. Observado en el estado alcanzable (los dos encendidos) y en el fabricado (los dos apagados juntos). La rama queda sin ejercer y **no se aprueba por interpretacion**: es un BLOCKED que vuelve al disenador, que tiene que decir si ese estado debe existir o si la rama es codigo muerto. |

## Defectos y partes de defecto emitidos

**Estado de los de la ronda anterior:** OLV-038 **cerrado**, OLV-039 **cerrado**, OLV-040 **cerrado**. OLV-036 ya estaba
cerrado en el lote 2 y no se re-califico.

**OLV-041 - minor - En el hilo, un archivo guardado no dice en que cliente quedo.**
- Reproduccion: en un turno ya enviado, un adjunto con cliente y un transitorio; guardar el transitorio desde el chip del
  hilo y leer el chip repintado. Control: el mismo documento en el chip del compositor.
- Evidencia: hilo -> `con-cliente-m29.txt` y `reverif-m29 (2).txt` sin leyenda de destino, en claro y en oscuro;
  compositor -> `unico-uno.txt | Cliente Beta QA`. El selector
  `#conversacion .ov-chip-adjunto:not(.ov-chip-adjunto--transitorio) .ov-chip-adjunto__destino` en **0**.
- `archivos_fix` sugeridos (hipotesis, no instruccion): `AdjuntoMensajeDto` suma `NombreCliente` proyectado en la misma
  consulta que ya trae `ClienteCarteraId`; `_Conversacion.cshtml` gana el `else` del `@if (a.SinCliente)`.
  `migracion_ef`: **no**.
- Criterio de re-verificacion: en el hilo reabierto, el chip de un adjunto con cliente muestra el nombre del cliente en
  los dos temas, y el chip repintado despues de guardar muestra el cliente elegido sin recargar; el chip del transitorio
  sigue sin fecha (D-04 intacto).
- Item creado en `regresiones-manuales.yml` + `cat_resumen.txt`.

## Observaciones sin parte (no son defectos de M29)

- **El binder de `clienteId` es permisivo:** `0x50`, `+80`, `80 ` y ` 80` se aceptan y resuelven al cliente 80 (`0x50` es
  80 en hexadecimal). No es un agujero -el cliente resuelto sigue validandose contra el tenant y uno inexistente da 404-
  pero conviene saberlo si alguna vez se audita por el valor literal del parametro.
- **Copy de M5, no de M29:** "Este cliente ya tiene **1 documentos**" (plural con 1) y "**Da** de baja" escrito con tilde.
  Son `MensajesDocumentos` preexistentes.
- **Un transitorio no se chequea por duplicado** mientras no tiene cliente: tres subidas del mismo archivo a
  `_organizacion` entraron las tres, renombradas `(2)`/`(3)`. Es coherente con que el duplicado se define **por cliente**,
  y la cuota de la organizacion si las cuenta.

## Higiene del catalogo cross-proyecto

- **`KOI-016` duplicado: resuelto.** Eran dos items distintos del proyecto koi con el mismo id. Se renumero el segundo
  (confidencialidad por rol / dato derivable entre pantallas) a **`KOI-017`**, con un campo `renumerado_desde` que deja
  constancia de que era duplicado **de numeracion y no de contenido**. El id elegido no es arbitrario: dos items ya lo
  citaban en sus textos ("misma familia que KOI-017", "cubrir el mismo conjunto (KOI-017)") y esas referencias estaban
  colgadas; ahora resuelven. `KOI-007` y `KOI-008` no existen en el catalogo y **no** se reutilizaron.
- Verificado al cerrar: el YAML parsea, **151 items y cero ids duplicados** en todo el catalogo.
- Se completo el titulo de `KOI-016` en `cat_resumen.txt`, que estaba vacio -y es parte de por que el duplicado era
  dificil de ver. Quedan **3 filas mas con el titulo vacio** (`GAN-003`, `LP-003`, `OLV-008`): es un artefacto del
  generador del indice, no del YAML, y queda anotado como pendiente de higiene.

## Riesgos de liberacion

- **Bajo - OLV-041.** Quien vuelve a un hilo de ayer ve cuales archivos son transitorios (eso ya se arreglo) pero no de
  quien son los guardados: tiene que abrir `Documentos/Ver` uno por uno. No pierde nada y no se equivoca de destino,
  porque el modal confirma el cliente antes de guardar y el toast lo dice al terminar.
- **Bajo - la rama sin ejercer de `Detalle.cshtml`.** No pudo alcanzarse ningun estado que la encienda. El riesgo real
  (un boton que abre nada) esta cerrado por la condicion compartida, pero el codigo de esa rama **nunca corrio** ni en
  test ni en navegador.
- **Nulo - regresiones.** CA-02.4 y B-07, los dos que el arreglo de OLV-038 podia aflojar, pasan con control positivo.
  Sin migracion EF y sin cambio de esquema: el rollback de este commit es un `git revert` y nada mas.

## Checklist de merge

- [x] **OLV-038, OLV-039 y OLV-040 cerrados** reproduciendo el caso original, no leyendo el diff.
- [x] Los bytes del archivo movido comparados contra el original (el defecto que no falla en el momento).
- [x] CA-02.4 y B-07 re-verificados con control positivo: el arreglo no aflojo ninguno.
- [x] Base devuelta al estado del implementador: tenant 30 borrado entero y checksum exacto - tareas **171**, eventos
      **763** (max id **880**), documentos **81** (max id **105**), 7 tenants, 0 usuarios del tenant 30. Blobs del
      tenant 30 borrados de `App_Data/documentos`; ningun archivo del dia en las otras carpetas.
- [x] `git status --porcelain` del repo bajo prueba **identico** al del arranque: ni un cambio de QA.
- [ ] **OLV-041 (minor) abierto.** No bloquea el merge; se cierra en la ronda siguiente, en contexto nuevo.
- [ ] **El miembro no-autor / la rama del modal suelto: BLOCKED.** Vuelve al disenador, no a QA.
- [ ] Sin push y sin deploy: lo decide Joaquin con este veredicto a la vista.

- Ultima validacion de reglas cross-proyecto: 2026-10-02


# QA M29 lote 1 de 2 — La casilla de internet, la frontera del portal del cliente y el dueno del transitorio (2026-10-02)

**VEREDICTO: apto.** Los tres modulos del lote pasan con evidencia observada, y el riesgo central de M29 —que un
usuario del portal del cliente vea un archivo sin cliente— **no se materializa por ninguno de los siete caminos**,
incluidos **dos que la implementacion no habia cubierto**. Unico defecto: **OLV-040 (minor)**, un residuo del mensaje
mentiroso de OLV-036 en el camino mas angosto. Ningun bloqueante.

- Ultima validacion de reglas cross-proyecto: 2026-10-02
- Entorno: commit `8fef7ae`, build limpio (0 errores, 15 advertencias conocidas). Portal propio en `https://localhost:7200`
  con `Anthropic:Simulado=true` (**"MODELO SIMULADO ... el costo es cero"** en cada uno de los 6 arranques: **costo real USD 0**).
  Organizaciones propias `qa-m29` (tenant 28) y `qa-m29b` (tenant 29), creadas y borradas por esta corrida. MCP de
  Playwright: **funciono**, todo en contextos aislados. El lote 2 corrio en paralelo sobre el tenant 27, intacto.
- Esquema post-migracion verificado con `SHOW CREATE TABLE`: `ClienteCarteraId int DEFAULT NULL`, `TareaOrigenId int DEFAULT NULL`,
  unico `(TenantId, ClienteCarteraId, NombreVigente)`, FK `ON DELETE RESTRICT` opcional, los otros 4 indices intactos.

## Cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-01.1** casilla al arrancar y en el ajuste, apagada por defecto | **PASS** | `/ChatLibre`: `input[name=PermiteBusquedaWeb]` con `checked=false`, texto *"Buscar en internet si hace falta"*, `title` de siempre. En el ajuste de la tarea 280: `#busquedaWebSeguimiento` presente con `checked=true`, o sea **con la marca que trae la tarea**. A **390px en claro y oscuro**: visible, dentro del viewport, sin scroll horizontal. |
| **CA-01.2** fail-closed, **cada condicion sola** | **PASS** | (a) `PrecioPorBusquedaUsd=0` con `Habilitada=true`: casilla ausente en arranque y en el ajuste; POST forzado con `PermiteBusquedaWeb=true` -> tarea **9287** con `PermiteBusquedaWeb=0`, 0 busquedas, costo 0. (b) `Habilitada=false` con precio 0,01: idem -> tarea **9288**, 0 busquedas, costo 0, y el **ajuste** forzado tampoco busca. Las dos alcanzan solas. |
| **CA-01.3** costo en el paso, en `EventoUso.Busquedas` y en el hilo | **PASS** | Tarea 280: paso 922 con `CostoUsd=0.020000` y 2 bloques `busqueda_web`/`resultado_busqueda_web`; `EventosUso` con `Accion=paso_chat_libre`, `Busquedas=2`, `CostoUsd=0.020000`; barra del hilo **"USD 0,02"** con "0 tokens". Fuentes enlazables con `target=_blank rel="noopener noreferrer nofollow"`. |
| **CA-01.4** `MaxBusquedasPorTarea` sigue valiendo | **PASS** | Con `MaxBusquedasPorTarea=1` y `PrecioPorBusquedaUsd=0.07` (el precio raro identifica **mi** proceso): tarea **9286** -> **1** bloque `busqueda_web` en el paso, `EventoUso.Busquedas=1`, **USD 0,07** en pantalla, con un pedido que pedia explicitamente *dos* busquedas. Control negativo: la 9285, con el mismo pedido pero levantada por el proceso del otro lote (tope 5, precio 0,01), hizo **2**. |
| **CA-01.5** no aparece en los tres, ni forzando el POST | **PASS** | `/Analista/Nueva`, `/ConfiguracionReglas/Nueva`, `/Asistente/Nueva`: sin `input[name=PermiteBusquedaWeb]`, sin el texto y sin ningun elemento con "usqueda" en id/class. POST forzado en `Iniciar` **y** en `/Tareas/EnviarSeguimiento`: tareas **281** (Tipo=4), **282** (Tipo=2), **283** (Tipo=3) quedan en `PermiteBusquedaWeb=0`, `Busquedas=0`, `CostoUsd=0`. **Control positivo en la misma tanda**: la 280 (Tipo=6) subio de 0,02 a 0,04. |
| **CA-01.6** no es herramienta del motor ni pasa por el guardia | **PASS** | Con 2 busquedas corridas: el paso 922 **no tiene ningun bloque `uso_herramienta`** (solo `texto`/`busqueda_web`/`resultado_busqueda_web`), `AprobacionesAccion` del tenant = **0** y `LlamadasConector` = **0**. La ejecuta el proveedor. |
| **Efecto lateral** la `ConsultaCliente` ya no ve la casilla, y nada mas se rompio | **PASS (con reparo)** | Por dos caminos: (1) `Views/PortalConsultas/Ver.cshtml` —la unica pantalla de consulta del cliente— **no contiene la casilla en absoluto** (0 ocurrencias; su compositor es solo `textarea[name=texto]` + submit); (2) con una `ConsultaCliente` (Tipo=5) en `/Tareas/Detalle`, no hay `#busquedaWebSeguimiento` ni el texto, mientras el chat libre 280 en la misma sesion si los tiene. **Reparo:** en ese camino el cuadro de ajuste **entero** no se renderiza para un Tipo=5, asi que el observable no distingue "la lista blanca se la saco" de "nunca hubo compositor ahi". La otra mitad —*nada mas se le rompio*— si quedo cerrada: recorrido completo del portal con **los dos** usuarios cliente (portada, Mis documentos, Lo que me piden, Mi ficha) sin un solo error y con subir/renombrar/dar de baja funcionando. |
| **CA-T.2** ningun usuario del portal del cliente ve un archivo sin cliente, **por ningun camino** | **PASS** | Ver la tabla de abajo. |
| **CA-T.3** multi-tenant: ni se lee, ni se guarda, ni se descarta | **PASS** | Sesion de `qa-m29b` (tenant 29) forzando el id 124 (tenant 28): `Ver` **404**, `Descargar` **404**, `AsignarCliente` **404 "El documento no existe."**, `DarDeBaja` **404**. El documento **quedo intacto** (`VersionToken=0`, `DeletedAt NULL`, nombre sin cambios). **Control positivo en la misma sesion**: su propio sin-cliente (id 130) se descarga **200** con su contenido. Y el discriminador que pedia el brief: en el adjunto, el id de otra organizacion devuelve **"Uno de los documentos ya no esta disponible. Revisa los adjuntos."** —mensaje de la **guarda de tenant**—, distinto del mensaje de la guarda de conversacion. |
| **CA-T.4** dos orgs, mismo nombre, sin colisionar | **PASS** | `secreto-organizacion.txt` sin cliente en tenant 28 (id 124) y en tenant 29 (id 130): **las dos sin sufijo** (`avisoNombre: null`), carpetas separadas `28/_organizacion/` y `29/_organizacion/`. **El otro lado, que el indice NO garantiza** (en MySQL los NULL no colisionan en un unico): el **segundo** sin-cliente con el mismo nombre en la **misma** organizacion se guardo como **`secreto-organizacion (2).txt`** (id 129) con el aviso. Lo garantiza el sufijado, verificado. |
| **CA-T.5** la ruta no se arma con un valor del pedido | **PASS** | El sin-cliente quedo en `App_Data/documentos/28/_organizacion/486a85f3...` (constante del codigo). `clienteId=0`, `-1` y un id de otra organizacion -> **404 "El cliente no existe."**, nada guardado. `clienteId=../../otro` -> el binder falla y **nada se guarda ni se arma ninguna ruta** (pero el mensaje miente: **OLV-040**). |
| **B-07** el id de otra conversacion de la propia organizacion no se adjunta | **PASS** | Transitorio 132 adoptado por la conversacion A (**`TareaOrigenId=9281`**). Forzado en la conversacion B (9282): **"Uno de los documentos ya no esta disponible en esta conversacion. Volve a subirlo."**, no se adjunta. **Control positivo en la misma tanda**: el mismo id en la propia A -> *"Mensaje enviado"*, y `AdjuntosMensajeTarea` suma la fila del paso 4. Con **otro usuario** (emp29) arrancando una conversacion con ese id: **no se creo ninguna tarea** y el transitorio solo tiene adjuntos en la 9281. Cross-tenant tambien rechazado (ver CA-T.3). |
| **B-07 / huerfano** los dos lados | **PASS** | Orden que importa: **primero el ajeno**. emp29 sube el huerfano 133 (`TareaOrigenId=NULL`, `SubidoPorUsuarioId=emp29`); **dir29** intenta llevarselo: en el arranque la pantalla vuelve con *"Uno de los documentos ya no esta disponible en esta conversacion"* y **sin crear tarea**, y en el ajuste de su propia 9282 `success:false` con el mismo mensaje. **Despues** emp29 lo usa al arrancar -> tarea **9283** creada y `TareaOrigenId=9283`. |

### CA-T.2 — los siete caminos, cada "no lo ve" con su "esto si lo ve" en la misma sesion

Sembrado el **peor caso**: doc **124** con `ClienteCarteraId NULL` **y** `VisibleParaCliente=1` escrito a mano en la base
(lo que el servicio impide y la base no). Y los tres documentos con `VisibleParaCliente=1`, para que **el unico motivo
de no ver sea la frontera**.

| Camino del portal del cliente | sin cliente (124) | control positivo, misma sesion |
|---|---|---|
| `GET /PortalDocumentos` (Mis documentos) | no lo lista | lista `papel-del-cliente78.txt` |
| `GET /Portal` (portada) | no lo lista | lista el propio |
| `GET /PortalDocumentos/Descargar?id=` | **404** | id 125 -> **200** con *"papel visible para el cliente 78"* |
| `GET /PortalPedidos` (Lo que me piden) | no lo nombra | pantalla sana, sin pedidos |
| `GET /Portal/MiFicha` | no lo nombra | ficha completa |
| **`POST /PortalDocumentos/Renombrar`** (id forzado) | **404 "El documento no existe."** | su propio 127 -> **200 "Documento renombrado."** |
| **`POST /PortalDocumentos/DarDeBaja`** (id forzado) | **404 "El documento no existe."** | su propio 127 -> **200 "Documento dado de baja."** |
| El vecino (126, cliente 79) | **404** en descarga y en renombrar | — |
| El **Director** sobre el mismo archivo | **200 con "CONTENIDO PRIVADO DEL ESTUDIO sin cliente"** | (es el control que hace que los negativos prueben algo) |

**Los dos caminos de mutacion no estaban en los 6 casos de la implementacion** (que cubrio los listados, la descarga, el
vecino y el Director). Los encontre aplicando **MH-041**: cerrar el inventario por la **lista de LECTORES** de
`DocumentosCartera` (grep sobre services + controllers) en vez de por recorrido de pantallas. Eso saco a la luz que
`PortalClienteService.RenombrarAsync`/`DarDeBajaAsync` **delegan directo** al servicio del estudio, asi que la frontera
ahi es el mismo filtro. **Pasan igual** — es un hallazgo de proceso, no un defecto.

**El caso que AISLA el filtro** (lo que ninguna de las dos pruebas anteriores hacia): el doc 124 tiene un **segundo
candado** en las mutaciones (`soloCliente is not null && Origen != Cliente -> NotFound`). Le puse `Origen = Cliente` a
mano para desactivar ese candado y **sigue dando 404** -> lo que lo deja afuera es `ApplyClienteFilterOpcional`, no el
candado de origen. Despues restaure `Origen = Estudio`.

**CA-T.2 bis (segundo candado):** `POST /Documentos/VisibleParaCliente` con `id=124` -> *"Este archivo todavia no es de
ningun cliente: primero guardalo en la carpeta de uno."* Control positivo: el 126 (con cliente) cambio de visibilidad.

## Lo que mire aunque nadie lo pidio — regresion de M5 (la columna de los cinco indices)

**PASS.** Todo el camino viejo, como Director, en el workspace del cliente 78: subir (136) -> renombrar
(*"regresion-m5-renombrada.txt"*) -> `Ver` 200 -> descargar **200 con el contenido** -> `VisibleParaCliente` 200
(*"Desde ahora lo ve el cliente"*) -> dar de baja 200. Sin ningun 500 en el log de la corrida. La grilla del cliente
dice **"1 a 2 de 2"** y **no** lista los sin-cliente.

**El medidor de espacio, con la aritmetica hecha:** la pantalla dice **"179 bytes de 1 GB"** y
`SUM(TamanoBytes) WHERE TenantId=28 AND DeletedAt IS NULL` = **179**, de los cuales **108 son de los sin-cliente**. Las
dos cosas a la vez: el espacio **si** los cuenta y el listado **no** los muestra.

**Evidencia colateral de la baja:** el transitorio 132 dado de baja quedo con `ArchivoEliminadoAt` no nulo y su binario
`2191a93e...` **no esta en el disco**.

## Cobertura de reglas nuevas/modificadas desde la ultima corrida

Ultima validacion registrada: **2026-10-02**. Diferencia contra el estado vigente: el commit **`1c5b7b7`** (2026-10-02
11:44) agrego **24 items** al catalogo y **3 reglas** a la instruccion 32. Ejecutadas en esta corrida:

| Regla / item nuevo | Origen | Aplica | Resultado |
|---|---|---|---|
| **MH-041** el inventario se cierra por la lista de LECTORES, no por recorrido de pantallas | catalogo | **si, directo** | **PASS — y se gano el lugar**: encontro los 2 caminos de mutacion del portal que los 6 casos de la implementacion no cubrian. Pasan, pero nadie los habia mirado. |
| **ELV-008** la guarda se escribe sobre los campos que de verdad no pueden, y al re-verificar se prueba **cada rama por separado** | instruccion 32 | si, por analogia (la guarda de 3 casos de B-07) | **PASS**: las cuatro ramas probadas por separado (con cliente / con dueno distinto de la tarea / sin dueno + otro usuario / sin dueno + el que lo subio), cada una definiendo su propio resultado. |
| **ELV-009** `recordsTotal` cuenta filas que el `INNER JOIN` descarta | catalogo | si (grilla de documentos con FK nulable) | **PASS**: "1 a 2 de 2" = filas servidas, sin inflacion por los sin-cliente. |
| **MH-045** lo que postea el sistema se puede anular a mano desde el CRUD generico | catalogo | si, por analogia | **PASS**: dar de baja el transitorio 132 que una conversacion **viva** estaba usando funciona y la conversacion sigue abriendo sana, mostrando **"transitorio-A.txt (dado de baja)"**. No queda rota ni lo lee. |
| **MH-047** un valor creado para aislar aparece igual en todos los combos que iteran todo | catalogo | si, por analogia | **PASS**: `/Documentos/Opciones?clienteId=78` y `/Documentos/Opciones` **no** traen los transitorios; el propio del cliente si. |
| MH-033 / MH-034 (ledger de caja, cuentas reales) | instruccion 32 | **no** | N/A: este producto no tiene ledger de caja. |
| MH-027, MH-035..MH-040, MH-042..MH-044, MH-048, ELV-003..ELV-007 | catalogo | **no** | N/A: ledger/backfill/contadores/grillas DataTables de otros proyectos. |

**Dato para el lote 2:** el chequeo de reglas nuevas lo hizo este lote (lote 1) y su resultado es el de arriba.

## Cobertura del catalogo cross-proyecto

| id | aplica | resultado | accion |
|---|---|---|---|
| **OLV-036** | si (es lo que M29 responde) | **PASS en el caso reportado** | `POST /Documentos/Subir` con un File y **sin** `clienteId` -> `success:true`, id 124, `sinCliente:true`. Con `clienteId=""` idem. Cerrado para el valor vacio/ausente; ver **OLV-040** por el residuo. |
| **KOI-013** el hidden en false antes del checkbox hace que el bool llegue siempre false | si (la casilla nueva) | **PASS** | El form emite `PermiteBusquedaWeb:checkbox` y despues `PermiteBusquedaWeb:hidden`; marcada, la tarea 280 quedo en `PermiteBusquedaWeb=1` y busco. |
| **OLV-005** una `List<int>` no anulable recibe `[Required]` implicito | si (`DocumentoIds`) | **PASS** | Arranques y ajustes sin `DocumentoIds` entran sin problema (tareas 280, 9282, 9287, 9288). |
| **MH-041 / ELV-008 / ELV-009 / MH-045 / MH-047** | si | **PASS** | Ver la tabla de reglas nuevas. |
| **PAT-017** (IDOR en portal de usuario final) | si | **PASS** | Los 7 caminos de CA-T.2 + los 4 de CA-T.3, cada uno con control positivo; identidad resuelta server-side. |
| OLV-020 (GROUP BY por nombre sin TenantId) | no | N/A | M29 no agrega ningun agregado de staff. |
| SG-001, GAN-005, CRM-023, OLV-012, MH-006, GAN-001 | no | N/A | Grillas editables, cultura de numeros, multiselect por query string, filtros persistidos: fuera del alcance de este lote. |

**Higiene del catalogo (no mio, no lo toque):** `KOI-016` esta **duplicado** en `regresiones-manuales.yml` (linea 3499
guarda de privilegio fail-open; linea 3533 confidencialidad derivable por resta). Son dos items distintos con el mismo
id, preexistentes del proyecto koi. Renumerar uno ajeno con otro lote leyendo el archivo es riesgoso: queda **para el
orquestador**.

## Defectos detectados

| id | sev | que |
|---|---|---|
| **OLV-040** | **minor** | `POST /Documentos/Subir` con un File presente y un `clienteId` que **no parsea** como `int` (`../../otro`, `abc`) vuelve a contestar **"Elegi un archivo."** — el mensaje mentiroso de OLV-036, en el unico camino que el fix por `int?` no cubrio. **Es seguro** (nada se guarda, ninguna ruta se arma), y un formulario del navegador nunca manda eso; pero el `criterio_aceptacion` textual de OLV-036 decia *"Ningun camino de error devuelve 'Elegi un archivo' con el archivo presente"* y **ese criterio no se cumple**. Item nuevo creado en el catalogo. |

**Auto-fixes aplicados: 0.** No se escribio una sola linea en el repo del sistema (`git status --porcelain` verificado al cierre).

## Partes de defecto emitidos

**OLV-040 (minor) — para el Implementador.**
- **Reproduccion:** con sesion de Director, en `/Documentos?clienteId=<id>` tomar el token antiforgery y mandar
  `POST /Documentos/Subir` con `Archivo` (un .txt chico) y `clienteId=../../otro`.
- **Evidencia observada:** `200 {"success":false,"message":"Elegi un archivo.","datos":null}` con el File presente en el
  FormData. **Controles positivos en la misma tanda:** `clienteId=""` -> `success:true` (sin cliente); `clienteId=78` ->
  `success:true`; `clienteId=0` -> `404 "El cliente no existe."`.
- **Causa raiz (observada en el codigo, como hipotesis):** `DocumentosController.cs:113` sigue siendo una sola guarda,
  `if (!ModelState.IsValid || model.Archivo is null)`, que traduce **todo** ModelState invalido al unico mensaje del
  ViewModel. Volver el parametro `int?` cambio el conjunto de entradas que hacen fallar al binder; no desarmo el colapso
  de las dos validaciones en un mensaje.
- **`archivos_fix` sugeridos:** `src/OlvidataAgentes.Web/Controllers/DocumentosController.cs`. **`migracion_ef`: ninguna.**
- **Criterio de re-verificacion (arranca en FAIL):** el POST con `Archivo` presente y `clienteId` no parseable **no**
  devuelve `"Elegi un archivo."`, y en la misma tanda `clienteId=""` y `clienteId=<valido>` siguen entrando.

### Estado de los partes de la corrida anterior

Los de M28 (OLV-030..OLV-037) los cerro la ronda de re-verificacion y el lote 2 de M29; **no entran en el alcance de
este lote** y no los re-califico. De lo que si toque: **OLV-036 PASS en el caso reportado**, con el residuo OLV-040
abierto.

## Riesgos de liberacion

- **Ninguno bloqueante.** El riesgo R-01 del analisis (el `NULL` que se cuela por el filtro del portal) **no se
  materializa**: 7 caminos, cada uno con control positivo, el peor caso sembrado en la base, y el caso que aisla el
  filtro desactivando el candado de origen.
- **Riesgo residual (bajo), para que quede escrito:** las mutaciones del portal del cliente
  (`PortalClienteService.RenombrarAsync` / `DarDeBajaAsync`) **delegan directo** al servicio del estudio y su unica
  frontera es el filtro global + el candado `Origen == Cliente`. Es **preexistente de M18**, no de M29, pero M29 apoya
  una frontera de privacidad sobre ese mismo filtro: cualquier cambio futuro a `ApplyClienteFilterOpcional` toca cinco
  endpoints del portal a la vez, no dos. Mitigacion: dejar los 7 casos de CA-T.2 como regresion fija.
- **Trampa de entorno que puede falsear una corrida futura (la sufri):** con dos portales levantados contra la **misma
  base**, el `MotorAgentesWorker` del otro proceso **puede levantar una tarea de mi organizacion** y procesarla con **su**
  configuracion. Mi primera medicion de CA-01.4 dio 2 busquedas con el tope en 1 por eso. **Como atribuir:** poner un
  valor distintivo en la config del proceso propio (use `PrecioPorBusquedaUsd=0.07`) y verificar que el costo de la
  tarea lo refleja. Sin eso, cualquier criterio que dependa de la configuracion del motor es ruido.

## Pruebas minimas ejecutadas

6 arranques del portal (4 configuraciones distintas de `BusquedaWeb`), 2 organizaciones, 5 usuarios (Director,
Empleado, 2 del portal del cliente, Director de otra organizacion), 13 documentos, 10 tareas. Todo por HTTP real y
navegador; cada negativo con su positivo en la misma sesion. Costo en Anthropic: **USD 0**.

## Checklist de salida para merge

- [x] **CA-01.1 a CA-01.6** PASS, con las dos condiciones del fail-closed probadas **por separado**.
- [x] **CA-T.2** PASS por **7 caminos** (2 mas que la implementacion), con el peor caso sembrado y el filtro aislado.
- [x] **CA-T.3, CA-T.4, CA-T.5** PASS, con el discriminador de la guarda de tenant y los dos lados del nombre unico.
- [x] **B-07** PASS, incluidos los dos lados del huerfano y el cruce de organizaciones.
- [x] Regresion de **M5** completa PASS; medidor de espacio con la aritmetica verificada; 0 errores 500.
- [x] **5 reglas nuevas** del commit `1c5b7b7` ejecutadas contra el sistema (resultado pasado como dato al lote 2).
- [x] Repo del sistema **sin un solo cambio mio**.
- [ ] **OLV-040 (minor) sin arreglar.** No bloquea el merge; se cierra en la corrida siguiente.

---

# QA M29 lote 2 de 2 — Subir sin cliente, guardar/descartar y la purga (2026-10-02)

**VEREDICTO: apto con reparos.** El nucleo de M29 anda y anda bien: OLV-036 esta **CERRADO** en las cuatro
conversaciones, la correccion B-03b del `Mover` esta **verificada con los bytes en la mano**, la purga acierta en los
dos lados y el `0` apaga. Lo que frena el "apto" liso son **dos defectos nuevos en la superficie persistida del hilo**:
la accion que convierte el transitorio en documento de un cliente **no existe despues de enviar el mensaje** (OLV-038),
que es justo el momento que describe HU-04, y en el hilo el transitorio **se ve igual** que uno guardado (OLV-039, el
riesgo RD-02 que la propia etapa declaro obligatorio).

Entrada leida por artefactos, sin la transcripcion del implementador: `5-implementador.md` (tandas B1/B2, commits
`37b215b`/`ee7f198`/`8fef7ae`), `2-disenador-funcional.md` linea 8 (D-01..D-07, Estados, Textos, RD-01..RD-05),
`3-arquitecto-mvc.md` linea 8 (B-03b, B-05, B-07), `1-analista-funcional.md` (CA-02.x/CA-03.x) y `docs/qa/cat_resumen.txt`.
Repo del sistema **read-only**: cero `Edit`/`Write`/`sed -i` sobre el, verificado al cierre con `git status --porcelain`.
**El chequeo de reglas nuevas lo hizo el lote 1** (no se repite, por brief).

### Montaje
- Portal propio `https://localhost:7201` (`--no-build --no-launch-profile -- --urls`), **organizacion propia** `qa-l2`
  (tenant **27**, SistemaCompleto, licencia `inmobiliario,general`), `dir2@qa.test` (Directora), `emp2@qa.test`
  (Empleado) y `cli2@qa.test` (usuario del portal del cliente, fabricado en base), clientes 75/76/77, tarea 279,
  documentos 110-135. **Todo borrado al cierre** (tenant 27 inexistente, `App_Data/documentos/27` borrada).
- `Anthropic__Simulado=true`. Evidencia de costo cero en los cuatro arranques: *"Motor de agentes con MODELO SIMULADO
  ... el costo es cero."* **Costo real de la corrida: USD 0,00.** **MCP de Playwright: funciono**, todo en contextos
  aislados para no desloguear al lote 1.
- Tres reinicios a proposito, por variables de entorno (nunca editando `appsettings`): `DiasGracia=7` (default),
  `=0` (apagada), `=1` + `MaxPorCliente=1`.

### Cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-02.1** (OLV-036) | **PASS** | En las **cuatro** (`/ChatLibre`, `/Analista/Nueva`, `/Asistente/Nueva`, `/ConfiguracionReglas/Nueva`): `POST /Documentos/Subir?clienteId=` (vacio) -> **200** y *"Documento subido. El agente lo puede leer."* El mensaje *"Elegi un archivo"* **no aparece en ninguna**. Nombre unico por tenant: `manual-l2.txt`, `(2)`, `(3)`, `(4)`. |
| **CA-02.2** | **PASS** | «¿Donde va este archivo?» visible, *«Usar solo en esta conversacion»* **`checked`** y *«Guardar en la carpeta de un cliente»* sin marcar, en las cuatro. Eligiendo cliente: `?clienteId=75` -> 200, doc 114 con `ClienteCarteraId=75`, `Origen=1`, `VisibleParaCliente=0`, y aparece en la carpeta de ese cliente. **(a)** elegir cliente y no decir cual: **0 pedidos HTTP** y toast *«Elegi el cliente en cuya carpeta va, o usalo solo en esta conversacion.»* |
| **CA-02.3** | **PASS** | Firma real: `falso.pdf` con texto adentro -> *"El archivo no es un .pdf valido."* (rechazado **sin cliente**). MIME mentido: `.txt` posteado como `application/pdf` -> guardado `TipoContenido=text/plain` (doc 116). Bytes: 21 MB -> *"El archivo supera el maximo de 20 MB."* en cliente **y** en POST forzado. Cuota de la organizacion: el medidor paso de `671 bytes` a `5,1 MB` con un transitorio de 5 MB. Partes: 126 partes y *"Es muy largo: el agente va a leer hasta la parte 126."* Servido: `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff` (ver reparo menor abajo). |
| **CA-02.4** | **PASS** | Los 10 transitorios no aparecen en `/Documentos/Index?clienteId=75` ni 76 ni 77, ni en `/Cartera`, ni en `/Conocimiento`. `GET /Documentos/Opciones` (sin cliente y con cliente) -> `[]`. En el servicio la clausula `ClienteCarteraId != null` esta nombrada. |
| **D-07** | **PASS** | *"Subir un documento"* se ofrece y **funciona** en las cuatro conversaciones; ya no hay 404 «el cliente no existe». |
| **CA-03.1** (ventana del compositor) | **PASS** | Chip -> *«Guardar en un cliente»* -> buscador -> doc 118 queda `ClienteCarteraId=76`, `VersionToken=1`, y el chip pasa a `ov-chip-adjunto` **solido** con el texto **«Cliente Dos L2»**, sin volver a subir nada. |
| **CA-03.1** (despues de enviar) | **FAIL — OLV-038** | Reabierto `/Tareas/Detalle/279`, `.ov-chip-adjunto__accion` = **0**; `/Documentos/Ver/117` ofrece solo Descargar/Renombrar/Dar de baja; `#chipsSeguimiento` vacio; el modal excluye transitorios. **No hay camino.** |
| **B-03b (el `Mover`)** | **PASS — lo mas importante** | Antes: `App_Data/documentos/27/_organizacion/68e62f77…`. Despues de guardar en el cliente 76: el blob esta en **`27/76/68e62f77…`**, **ya no esta en `_organizacion`**, y `GET /Documentos/Descargar/118` devuelve **los bytes exactos del original** (comparacion de contenido `=== true`, 44 bytes). |
| **RD-04 duplicado** | **PASS** | *«Este archivo ya esta cargado para este cliente como «sigma-l2.txt».»* — **dice con que nombre** — y el documento **sigue transitorio** (`/Documentos/Ver` sigue diciendo «solo de esta conversacion»). |
| **RD-04 cuota del cliente** | **PASS** | Con `MaxPorCliente=1`: *«Este cliente ya tiene 1 documentos. Da de baja alguno para subir otro.»*, y sigue transitorio. |
| **CA-03.2** | **PASS** | Baja del doc 123: `DeletedAt` + `ArchivoEliminadoAt` sellados, **0** filas en `DocumentoCarteraPartes`, blob **ausente** del disco, `/Documentos/Ver/123` -> **404**. |
| **CA-03.5** | **PASS** | Medidor: `5,1 MB` -> **`671 bytes`** tras descartar. |
| **CA-03.3** | **PASS, los dos lados** | Con plazo 7 y la conversacion 279 terminada hace **3 dias**: `documentos-limpiar` **no** la incluye. Con plazo **1**, el worker (pasada a los 2 min) **descarto** 117: `DeletedAt`+`ArchivoEliminadoAt`, 0 partes y el blob fuera de `27/_organizacion/`. Los 4 transitorios de hoy **no** se tocaron. |
| **CA-03.4** | **PASS, 0 y -1** | Arranque con `=0`: *"Purga de archivos sin cliente **apagada** (Documentos:DiasGraciaAdjuntoSinCliente = 0)."* `documentos-limpiar --aplicar` con 0 y con -1: *"la purga esta **APAGADA** … Un plazo en 0 no descarta nada."* y los 13 documentos vigentes siguieron en 13. |
| **CA-03.6** | **PASS, aislado** | Doc 114 **con cliente 75**, `CreatedAt` a **60 dias** y **nunca adjuntado a ninguna conversacion** (el escenario que aisla la primera clausula): `documentos-limpiar` **no lo lista** y la pasada del worker **no lo toco**. Idem 118 y 119. |
| **Huerfano que nunca se mando** (mas alla del brief) | **PASS, con su negativo** | Doc 120 (sin dueno, 60 dias): listado con el motivo en palabras — *"nunca llego a una conversacion (se subio el 2026-08-03 22:22 UTC)"* — y descartado por el worker. Doc 121/122 (sin dueno, de hoy) y 117 antes de mover la fecha: **intactos**. Un archivo que si se mando no se fue por su fecha de subida. |
| **Mirar no borra** | **PASS** | `documentos-limpiar` sin `--aplicar`: imprime el caso y *"Para descartarlos, repeti con --aplicar"*; 13 documentos vigentes antes y despues. |
| **D-01** | **PASS** | El reversible viene marcado; el bloque de destino **no aparece** cuando el modal viene con cliente (`/Documentos/Index?clienteId=75`). |
| **D-02 / RD-02** (compositor) | **PASS** | Transitorio: `border-style: dashed`, `--ov-gray-400`, leyenda **«solo en esta conversacion»** + accion. Guardado: `solid`, `--ov-border`, **nombre del cliente**, sin accion. Se distinguen en claro y en oscuro. |
| **D-02 / RD-02** (hilo) | **FAIL — OLV-039** | En `/Tareas/Detalle/279` el chip del transitorio mide `borderStyle: "solid"` y dice solo `omega-l2.txt`: **identico** a uno con cliente. Mitiga parcialmente que `/Documentos/Ver` si diga «Sin cliente (solo de esta conversacion)». |
| **D-04** | **PASS** | El chip dice *«solo en esta conversacion · Guardar en un cliente»* y **nada mas**: sin cuenta regresiva y sin fecha. |
| **Textos que importan** | **PASS** | Los cinco textos coinciden **palabra por palabra** con el Diseno M29, incluida la linea de ayuda. |
| **Pantalla (`38`)** | **PASS** | 1440 y 390 px, claro y oscuro: sin scroll horizontal, el chip de dos renglones (64 px) **no desborda** (right 352 de 385) ni empuja el compositor, el bloque de destino y el buscador caben dentro del modal. **Solo tokens `--ov-*`**: barrido de `cssText` sobre las reglas `.ov-chip-adjunto*` y `.ov-lista-clientes` -> **0 colores literales**. |
| **B-07 (id forjado)** | **PASS, con control positivo** | Negativos: dir2 forzando el id 117 (dueno = tarea 279) en un chat libre nuevo, emp2 forzando el huerfano 120 (que subio dir2) y emp2 forzando 117 -> los tres: *«Uno de los documentos ya no esta disponible en esta conversacion. Volve a subirlo.»* y no se adjunta. **Positivo:** el mismo 117 en **su** conversacion entra (*"Mensaje enviado"*), asi que los negativos prueban algo. |
| **CA-T.1** (`adjunto_leer`) | **PASS** | `EjecucionesHerramienta` de la tarea 279: `adjunto_leer` sobre `documento_id: 117` (**sin cliente**), sin rama nueva. |
| **CA-T.2** (portal del cliente) | **PASS, positivo y negativo** | `cli2@qa.test` (rol Cliente, cliente 76) en `/PortalDocumentos`: ve **solo** `sigma-l2.txt` (suyo y visible) y **ningun** transitorio. `/PortalDocumentos/Ver` y `/Descargar/128` -> **404**. `/Documentos/Ver` y `/Descargar/128` y `/Documentos/Descargar/114` -> **redireccion opaca**, los bytes **nunca** vuelven. |
| **CA-T.3** (multi-tenant) | **PASS** | Transitorio 124 de la org del lote 1: `Ver`/`Descargar` -> **404**, `AsignarCliente` y `DarDeBaja` -> **404 «El documento no existe.»**, adjuntarlo -> rechazado. Y `AsignarCliente` a un cliente de otra org (74) -> **404 «El cliente no existe.»** |
| **CA-T.5** (ruta en disco) | **PASS** | La carpeta del transitorio es la **constante** `_organizacion` (`App_Data/documentos/27/_organizacion/<archivoId>`); ningun valor del pedido entra en la ruta. |
| Concurrencia optimista | **PASS** | `AsignarCliente` con `version` equivocada -> *«Otra persona cambio o dio de baja este documento. Recarga la pagina.»* |
| **Regresion M5** | **PASS** | Desde la carpeta del cliente 75: subir (`sinCliente:false`), renombrar (*"Documento renombrado."*), descargar (29 bytes), aparecer en `Opciones`, dar de baja (*"Documento dado de baja."*). Renombrar un transitorio tambien anda. |
| **Regresion M19** | **PASS** | `GeneradoEnTareaId` intacto: `COUNT(*) WHERE TareaOrigenId IS NOT NULL AND GeneradoEnTareaId IS NOT NULL` = **0**, y la tarea 279 —con dos transitorios adoptados— **no dibuja** la seccion «Lo que armo». Es lo que se habria roto reusando la columna. |
| **Adopcion del huerfano** | **PASS** | Doc 117 nacio sin dueno en la pantalla de arranque y quedo con `TareaOrigenId=279` al mandarse; 121, adjuntado despues a la misma tarea, tambien. Idempotente. |

**Cobertura: 29 PASS · 2 FAIL · 0 BLOCKED.**

### Cobertura del catalogo cross-proyecto

| id | aplica | resultado | accion |
|---|---|---|---|
| **OLV-036** | si | **CERRADO** | El parametro es `int?` y el pipeline chequea cliente solo si viene. Verificado en las **cuatro** conversaciones. |
| OLV-023 (tipo nuevo + herramienta) | si | PASS | `adjunto_leer` corrio de verdad sobre un transitorio; no hay herramienta ofrecida que falle. |
| OLV-024 (escritura por GET) | si | PASS | `AsignarCliente` y `DarDeBaja` son `[HttpPost, ValidateAntiForgeryToken]`; sin token no entran. |
| OLV-025 / OLV-029 / OLV-034 / OLV-037 (rotulos con default) | si | PASS en lo que toca M29 | Los textos del chip y del modal no tienen rama default; el transitorio se nombra por su estado. |
| OLV-027 (tope de 0 implementado como carrera) | si | PASS | `DiasGracia <= 0` **apaga**; probado con 0 y con -1, en el worker y en el comando. |
| OLV-020 (GROUP BY sin TenantId) | si | PASS | El nombre unico del transitorio es por tenant: dos orgs con el mismo nombre no colisionan (124 y mis `manual-l2.txt` convivieron). |
| OLV-021 / OLV-022 (frontera de dos publicos) | si | PASS | El usuario del portal del cliente no ve el transitorio ni por listado ni por id, y las pantallas de staff lo redirigen. |
| OLV-032 (atributo que se emite vacio) | no | N/A | Sin atributo opcional nuevo en este lote. |
| OLV-028/030/031/033/035 (menu, partes, autocomplete, propuestas) | no | N/A | Alcance del lote 1 / M28. |
| MH-040 / MH-045 (fila vieja que sobrevive) | si | PASS | La baja de un transitorio borra fila logica, partes y blob; nada queda a medio camino. |
| **OLV-038** | — | **NUEVO** | Item creado en `regresiones-manuales.yml` + `cat_resumen.txt`. |
| **OLV-039** | — | **NUEVO** | Item creado en `regresiones-manuales.yml` + `cat_resumen.txt`. |

### Reglas nuevas desde la ultima corrida
Hecho por el **lote 1** por indicacion del brief (instruccion 33: una vez por corrida). Este lote no lo repite y toma
su resultado como dato.

### Defectos y partes de defecto emitidos

**OLV-038 — major — La accion que cierra el ciclo no existe despues de enviar el mensaje.**
- Reproduccion: subir un archivo con el destino reversible en `/ChatLibre`, **enviar** el mensaje, dejar que el agente
  lo lea, reabrir el hilo y buscar como guardarlo en un cliente.
- Evidencia: `/Tareas/Detalle/279` -> `document.querySelectorAll('.ov-chip-adjunto__accion').length` = **0**; el chip es
  un `<a href="/Documentos/Ver/117">` plano; `/Documentos/Ver/117` ofrece **Descargar / Renombrar / Dar de baja** y nada
  mas; `#chipsSeguimiento` vacio al reabrir; `OpcionesParaAdjuntarAsync` excluye los sin cliente (y debe hacerlo, CA-02.4).
  Control positivo: el mismo flujo **antes** de enviar funciona entero.
- `archivos_fix` sugeridos (hipotesis): `Views/Tareas/_Conversacion.cshtml` (el chip del turno necesita saber si es
  transitorio), `Views/Documentos/Ver.cshtml` (la ficha ya dice que es transitorio: ahi la accion es una linea), y el DTO
  del adjunto del mensaje, que hoy no trae `SinCliente`. `migracion_ef`: **no**.
- Criterio de re-verificacion: reabierta la conversacion, el chip del transitorio de un turno ya enviado ofrece la accion
  (`.ov-chip-adjunto__accion` >= 1), al usarla el documento queda con `ClienteCarteraId` en base **sin volver a subir el
  archivo**, y un adjunto que ya tiene cliente **no** la ofrece.

**OLV-039 — minor — En el hilo, el transitorio y el guardado se dibujan igual.**
- Reproduccion: adjuntar un transitorio y un documento con cliente en un mismo turno, enviar, reabrir y comparar.
- Evidencia: `getComputedStyle` del chip del hilo -> `borderStyle: "solid"`, texto `omega-l2.txt`, sin leyenda; el mismo
  archivo en el compositor -> `dashed` + `--ov-gray-400` + «solo en esta conversacion».
- `archivos_fix` sugerido: `Views/Tareas/_Conversacion.cshtml` (el mismo dato que pide OLV-038). `migracion_ef`: **no**.
- Criterio de re-verificacion: en el hilo, el chip del transitorio tiene leyenda propia y `borderStyle` distinto del
  chip con cliente, medido con `getComputedStyle`, en claro y en oscuro.

### Reparo menor, sin parte (no es de M29)
`GET /Documentos/Descargar/<id>` sirve el **TipoContenido propio** del documento (`text/plain` para un `.txt`), no
`application/octet-stream`. Es identico con cliente y sin cliente —comportamiento de M5, no una regresion de M29— y
esta contenido por `Content-Disposition: attachment` + `X-Content-Type-Options: nosniff`, asi que el navegador no lo
renderiza. La letra de CA-02.3 («nada se sirve con su propio tipo de contenido») **no** se cumple en sentido literal
para ninguno de los dos casos; la parte que M29 tenia que demostrar —que el archivo sin cliente se sirve **igual** que
uno con cliente— si. Decision: queda como observacion para el Arquitecto, no como defecto de M29.

### Observacion de entorno (no es defecto)
`documentos-limpiar` corre con el `ContentRoot` del proyecto **Admin**, asi que su `App_Data/documentos` es **otra
carpeta** que la del portal: en dev, un `--aplicar` desde Admin da de baja la fila pero no encuentra el blob del portal.
La purga de verdad corre en el worker del portal, que si lo borra (verificado). Vale para no confundir una limpieza
manual con la purga.

### Riesgos de liberacion
- **Alto si se libera tal cual: la promesa de la feature queda a medias.** La eleccion del momento de subir se
  entiende y funciona; lo que no se puede es **cambiar de opinion despues**, que es la mitad reversible del diseno
  (D-01 eligio el reversible precisamente para poder deshacer «en los dos sentidos»). Con OLV-038 abierto, el unico
  sentido disponible es *dejar que se descarte*.
- **Medio: invisibilidad en relectura (OLV-039).** Quien vuelve a un hilo de ayer no sabe cual de sus archivos se va a
  borrar. Mitigacion parcial: la ficha del documento si lo dice.
- **Bajo: la purga.** Es el codigo nuevo que borra archivos y es el que mejor se porto: cuatro condiciones por
  inclusion, el `0` apaga, `DarDeBaja` como unico camino y el comando para mirar antes. No se encontro un solo caso en
  que alcanzara algo con cliente.
- Nada de M6/M14 tocado; `adjunto_leer` sin cambios de universo; multi-tenant y la frontera del portal del cliente, en pie.

### Checklist de salida para merge
- [x] OLV-036 **cerrado** y verificado en las cuatro conversaciones.
- [x] B-03b verificado con los bytes: el blob se mueve y el archivo se descarga igual al original.
- [x] Purga: alcanza / no alcanza / apagada en 0 y en -1, con borrado fisico y liberacion de cuota.
- [x] CA-03.6 probado **aislando** la primera clausula (papel viejo con cliente, nunca adjuntado).
- [x] B-07 con control positivo y tres negativos (dos usuarios).
- [x] Frontera del portal del cliente con control positivo y negativo.
- [x] Pantalla a 1440/390 en claro y oscuro, solo tokens `--ov-*`.
- [x] Regresiones M5 y M19 verdes.
- [x] Base devuelta a su estado (tenant 27 borrado entero, blobs del dia borrados) y repo **sin cambios de QA**
      (`git status --porcelain` igual al de la apertura; el `M CLAUDE.md` es del lote 1, nota de precios del 2026-10-02).
- [ ] **OLV-038 y OLV-039 abiertos.** No se cierran en esta corrida: el ciclo es Implementador -> QA en contexto nuevo.

- Ultima validacion de reglas cross-proyecto: 2026-10-02 (la hizo el lote 1 de esta corrida)

# QA M28 — RONDA DE RE-VERIFICACION de los tres lotes (2026-10-02)

**VEREDICTO: apto con reparos. Los seis defectos de los tres lotes estan CERRADOS, los cuatro criterios BLOCKED se
pudieron calificar y dieron PASS, y el motor y el aislamiento siguen en pie. Lo que frena el "apto" liso es un defecto
nuevo que la ronda destapo al ejercer el camino de CA-04.1: desde una conversacion SIN cliente no se puede SUBIR un
adjunto (OLV-036), y el mensaje que le sale a la persona la culpa de no haber elegido el archivo que si eligio.**

Entrada leida por artefactos, sin la transcripcion del implementador: los tres lotes de `6-qa.md`, `5-implementador.md`
(ronda de arreglos, commit `7b508d5`), `3-arquitecto-mvc.md` linea 8 (A-10) y `docs/qa/cat_resumen.txt`.
Repo del sistema **read-only**: cero `Edit`/`Write`/`sed -i` sobre el, verificado al cierre con `git status --porcelain`.

### Montaje
- Portal `https://localhost:7200`, `Anthropic__Simulado=true`, `Subagentes__SegundosBarrido=2`. Evidencia de costo cero
  en el arranque: *"Motor de agentes con MODELO SIMULADO (Anthropic:Simulado = true, entorno Development): no se llama a
  Anthropic y el costo es cero."* **Costo real de la corrida: USD 0,00.** MCP de Playwright **funciono**.
- **Organizacion propia**, creada y borrada por esta corrida: `qa-org-e` (tenant **26**, etapa SistemaCompleto, licencia
  de `inmobiliario,general` = **18 agentes mencionables**, el borde exacto de OLV-031), con `dire@qa.test` (Directora) y
  `empe@qa.test` (Empleado), ambos `Super123!`; cliente de cartera 74; 14 tareas (265-278).
- **El guion de chat libre del `ProveedorModeloSimulado` funciona y levanta los cuatro BLOCKED.** Marcadores usados:
  `"adjunt"`/`"archivo"` -> `adjunto_leer`; `"once"` -> once propuestas de un saque; dos `@agente` -> pregunta a cual;
  `"deleg"` + `"aprob"` -> parte colgada esperando aprobacion (el montaje de OLV-030).
- **Orden obligado:** OLV-028 se probo **antes** de publicar, bajando a Borrador las cuatro versiones de plataforma
  (147, 110, 79, 116) y restaurandolas a Publicada despues. Es el unico momento en que ese criterio es observable.

### Los seis defectos de los tres lotes

| id | sev | estado | evidencia observada que lo cierra |
|---|---|---|---|
| **OLV-028** | major | **CERRADO** | Con las **cuatro** versiones en Borrador, ni la Directora ni el Empleado ven en el menu *Chat libre*, *Automatizar lo que repetis*, *Configurar conversando* ni *Repartir trabajo conversando*, y las cuatro URLs siguen contestando *"Todavia no esta disponible."* (el cuadro del chat libre, ademas, `disabled`). Publicadas las cuatro: a la Directora le aparecen **las cuatro**; al Empleado **solo dos** (*Automatizar* y *Chat libre*), sin *Configurar* ni *Repartir*. **Reparo: el arreglo cerro el menu y no el tablero — ver OLV-035.** |
| **OLV-030** | major | **CERRADO, los tres sitios** | Chat libre 269 en `EsperandoSubtareas`: `document.querySelectorAll('.ov-parte').length` = **1** (antes 0), y la secuencia *En curso -> Esperando a otros agentes* se vio en el DOM. La parte 270 queda esperando aprobacion y la tarjeta del padre **dice de que** (*"Espera una aprobacion"*) y **ofrece Resolver** -> `/Tareas/Detalle/270`, donde hay **2** elementos `[data-accion-aprobacion]` que la resuelven: el `_ScriptAprobaciones` se carga en el chat libre. Contador: la cabecera cuenta las dos familias (*"1 propuesta pendiente"* en 265 con una propuesta de regla; *"10 propuestas pendientes"* en 273). **Control negativo:** configurador (267), asistente (268) y analista (271) siguen con **0** partes y **sin** el script de aprobaciones. |
| **OLV-031** | major | **CERRADO en el borde que fallo** | Con **18** agentes usables (`/ChatLibre/Mencionables` = 22 = 18 + 4): con la arroba sola el menu dibuja **2** `.ov-menciones__grupo` (*Agentes* y *Configurar*), **20** items = 16 agentes recortados + **las 4** opciones de Configurar enteras, y 16 `ArrowDown` llegan a `@regla` **sin tipear ningun filtro**. El tope ahora es por grupo. |
| **OLV-032** | trivial | **CERRADO** | Conversacion del analista (271): `document.querySelector('textarea').hasAttribute('data-menciones')` = **false**, escribir `@` no abre menu y **no genera ni un pedido** en el panel de red. Control positivo: el chat libre lo trae completo (`/ChatLibre/Mencionables`). |
| **OLV-033** | major | **CERRADO, las dos compuertas** | **Empleado** sobre su preferencia (chat libre 265): `POST /Propuestas/Aplicar` **200**, nace `Reglas` 117 con `Alcance=3` y `UsuarioId` del Empleado, propuesta `Estado=2`. **Directora** sobre la suya (266): 200, regla 118, `Alcance=3`. Y el piso de permisos no se aflojo: POST forzado del Empleado sobre una propuesta de **alcance empresa** -> **403** *"Solo un Director puede configurar reglas conversando."* **Contraejemplo intacto:** una preferencia personal fabricada en el **configurador** (267) falla con el mismo mensaje de siempre (*"El configurador no crea ni cambia preferencias personales: solo reglas de la empresa, de areas, por agente o de clientes."*) y queda **Fallida**; en el **asistente** (268) el POST forzado devuelve **el mismo mensaje**. |
| **OLV-034** | minor | **CERRADO** | *"Donde aplica: **Solo en tus tareas**"* en las tarjetas de alcance personal de 265, 266 y las diez de 273. Ni una raya. |
| **OLV-029** (lote 2) | major | **CERRADO (confirmado de paso)** | Detalle de las 10 tareas de chat libre: encabezado *"Chat libre"*; fila de `/Tareas`: *"Chat libre | Chat libre | ... | Sin cliente"*. Ningun *"plataforma"* ni *"Configuracion de reglas"*. |

### Los cuatro criterios que estaban BLOCKED

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-04.1** Adjunto sin cliente leido con `adjunto_leer` | **PASS** | Chat libre **276**, `ClienteCarteraId = NULL`, con `qa-adjunto-a.txt` adjuntado: `PasosTarea` Numero 1 trae `{"nombre":"adjunto_leer","entrada":{"documento_id":108,...}}`, el paso 2 devuelve el contenido **sin** `esError`, y la respuesta dice *"Lei el adjunto de esta conversacion. Empieza asi: «…»"*. |
| **CA-04.2** El universo es solo lo adjuntado a **esa** conversacion | **PASS** | Tres observaciones, no una: (a) 276 lee **108** y 277 lee **109**, cada una la suya; (b) chat libre **278 sin adjunto**, con la carpeta del cliente 74 **llena de dos documentos legibles de la misma organizacion**, pide leer el adjunto y contesta *"No veo ningun archivo adjuntado a este mensaje."* -> la carpeta del cliente **no entra**; (c) con el adjunto de 276 reapuntado a mano al documento **47 (tenant 19)**, la pantalla lo muestra *"ajeno-tenant19.csv **(dado de baja)**"* y **nunca se lee**, y el adjunto de otro **turno** tampoco se arrastra (el seguimiento contesta *"No veo ningun archivo"*). |
| **CA-03.3** `TopePropuestas` = **10** en el chat libre | **PASS** | Tarea 273: el guion pide **once** `proponer_regla` en **un mismo paso** -> `PropuestasRegla` de la tarea = **10** exactas, cabecera *"10 propuestas pendientes"*, y el resultado de la herramienta numero once trae *"Ya registraste 10 propuestas en esta respuesta…"* con **`"esError":true`**. Corta en 10, no en 3. |
| **D-05** Dos menciones: se pide elegir | **PASS** | Tarea 272, mensaje `@inmo-ceo @inmo-legal …`: **0** tareas hijas (`COUNT(*) WHERE TareaPadreId=272` = 0), **0** `.ov-parte`, y la respuesta es *"Mencionaste a @inmo-ceo y a @inmo-legal en el mismo mensaje y no elijo por vos: ¿a cual le paso el pedido, a @inmo-ceo o a @inmo-legal?"* — las dos a la vista, el sistema no elige. |

### Lo que la ronda mando a mirar aunque nadie lo pidio

- **HU-04 re-corrida con los botones vivos: PASS.** En la tarea 273, con **diez** tarjetas pendientes y `Reglas` del
  tenant en 2: se toco **una sola** (la tercera), el POST real devolvio 200, nacio **una sola** regla (119,
  *"Preferencia simulada 3 de 11"*, `Alcance=3`), esa tarjeta quedo con el sello **Aplicada** y las otras nueve
  conservaron sus tres botones. El contador paso de **10 a 9 propuestas pendientes**. Nada cambio hasta el boton.
- **Las otras tres conversaciones de plataforma no se vieron afectadas** por el arreglo de OLV-030 (0 partes, sin
  script de aprobaciones, sin `data-menciones`), y su contador de propuestas sigue andando (267 y 271: *"1 propuesta
  pendiente"*).
- **De los tres "huecos cosmeticos declarados como decision y no defecto", uno SI es defecto.** Los otros dos se
  sostienen: que *"pendientes para mi"* no liste las propuestas del chat libre es coherente con el analista y el
  configurador (cada una vive en su conversacion). Pero lo declarado sobre el enlace y la leyenda **no es lo que pasa**:
  la regla 118, nacida en el chat libre 266, **si tiene** el enlace *"Ver conversacion"* (y apunta bien, a
  `/Tareas/Detalle/266`) y su leyenda dice **"ORIGEN: Propuesta del configurador"**, con el historial en *"Alta desde el
  configurador"*. No esta ausente: esta **mal**, y le atribuye la regla a una pantalla que la persona nunca uso. Es el
  molde de OLV-029 / OLV-025 en otra superficie. **Defecto nuevo OLV-037 (minor).**

### Defectos nuevos de esta ronda
| id | sev | que | estado |
|---|---|---|---|
| **OLV-036** | **major** | **Desde una conversacion sin cliente no se puede SUBIR un adjunto.** El modal del chat libre (y el del analista) postea `POST /Documentos/Subir?clienteId=` con el parametro **vacio**; la accion es `Subir(int clienteId, SubirDocumentoViewModel model)`, el binder falla sobre `clienteId`, `ModelState` queda invalido y la **primera linea** de la accion traduce eso al unico mensaje del ViewModel: **"Elegi un archivo."** — con el archivo adentro del `FormData`. Control positivo: el **mismo** `File` a `?clienteId=74` devuelve `success:true` (documento 108). Con `?clienteId=0`: 404 *"El cliente no existe."* Rompe de frente *"las tres conversaciones aceptan documentos adjuntos, sin cliente"* por el camino de subir. Adjuntar un documento **ya existente** si funciona (es como se pudo calificar CA-04.1). | **parte emitido** |
| **OLV-037** | minor | Una regla nacida en un chat libre se rotula **"Propuesta del configurador"** en el detalle y *"Alta desde el configurador"* en el historial. Declarado por el implementador como decision (*"no le da el enlace ni la leyenda"*); lo observado es distinto: el enlace esta y es correcto, y la leyenda esta equivocada. | **parte emitido** |
| **OLV-035** | trivial | El arreglo de OLV-028 cerro el **menu** y no el **tablero**: con las cuatro versiones en Borrador, la tarjeta del camino de arranque sigue ofreciendo *"Empezar a contar -> /Analista"*, que lleva a la pantalla muerta. La guarda quedo en `VeEnMenuAsync` y el camino de arranque arma sus pasos con su propia regla (etapa + rol). | **parte emitido** |

**Partes de defecto emitidos: 3 (OLV-035, OLV-036, OLV-037)**, los tres con item nuevo en
`docs/qa/regresiones-manuales.yml` (causa raiz, `archivos_fix` como **hipotesis**, criterio de re-verificacion y leccion
cross-proyecto) y su linea en `cat_resumen.txt` — el catalogo queda en **147** items.
**Auto-fixes aplicados: 0. Ninguno de los tres se cierra en esta corrida.**

### Criterio de re-verificacion (el que decide el PASS en la proxima corrida)
- **OLV-036:** desde el modal de un chat libre **sin cliente**, "Subir un documento" con un `.txt` legible deja el
  documento en la cola con resultado de exito y lo adjunta; y ningun camino de error devuelve *"Elegi un archivo"*
  teniendo el archivo presente.
- **OLV-037:** `/Reglas/Detalle/<id>` de una regla aplicada desde un chat libre **no** dice *"del configurador"* ni en
  ORIGEN ni en el historial.
- **OLV-035:** con las cuatro versiones de plataforma en Borrador, **ningun** `a[href]` del tablero apunta a
  `/Analista`, `/ChatLibre`, `/ConfiguracionReglas` ni `/Asistente`.

### Cobertura del catalogo cross-proyecto
Del indice `cat_resumen.txt` (144 items al arrancar) se corrieron por modulo equivalente: **OLV-028** (guarda de
visibilidad que vive en la vista y no en la condicion) -> **encontro OLV-035**, la misma guarda faltando en la otra
superficie; **OLV-025 / OLV-029** (rotulo de un valor nuevo que hereda el de otro) -> **encontro OLV-037**;
**MH-041** (inventario enumerado a mano; cerrarlo por los **lectores**) -> **APLICADA**, es la que hizo barrer todos los
`a[href]` del tablero en vez del `aside` y asi aparecio OLV-035; **OLV-024** (aplicar una propuesta por GET) -> **PASS**:
los dos aplicares son POST con antiforgery y el forzado sin rol da 403; **MH-047** (valor nuevo del enum en los combos)
-> **PASS**, los rotulos de `/Tareas` y del detalle dicen *Chat libre*; **OLV-015** (boton con dos guardas excluyentes)
-> **PASS**, el *Resolver* de la tarjeta de parte abre `/Tareas/Detalle/270` y ahi hay con que resolver.
**Molde nuevo que esta ronda agrega al catalogo:** una accion que mezcla un **parametro de ruta** con un **ViewModel** y
valida las dos cosas con un solo `!ModelState.IsValid` devuelve el mensaje del campo cuando lo que falla es el
parametro (OLV-036) — un mensaje de validacion que manda a QA a buscar donde no esta.

### Reglas nuevas o modificadas desde la ultima corrida
El chequeo de la `33` lo hizo la corrida de los tres lotes el mismo dia (`2026-10-02`): desde `2026-09-25` entro un solo
commit (`1c5b7b7`) y de el aplicaban **ELV-008, MH-027 y MH-047**, las tres ya con PASS. **No se recalculo** (la `33`
permite pasarlo como dato dentro de la misma fecha de validacion) y **esta ronda no tenia regla nueva propia que correr**:
los tres items que agrego son suyos, de salida.

### Riesgos de liberacion
- **Bloqueante por datos, plata o aislamiento: ninguno.** El aislamiento multi-tenant del adjunto aguanta por los tres
  caminos probados, el piso de permisos del Empleado sigue dando 403, y el tope de propuestas corta.
- **Reparo que condiciona el "apto": OLV-036.** La promesa escrita del modulo es que las conversaciones de plataforma
  aceptan documentos **sin cliente**; hoy eso solo se cumple adjuntando algo que ya estaba en la carpeta de **algun**
  cliente. Una organizacion recien arrancada, sin cartera, no tiene **ningun** camino para mandarle un manual al agente
  — que es literalmente el texto del modal (*"Si ya tenes escrito como trabajan —un manual, un instructivo, una
  planilla— mandaselo y lo lee"*). Y el mensaje de error culpa a la persona.
- **No bloqueantes:** OLV-037 y OLV-035, mas los reparos que ya declararon los lotes (el `.txt` servido como
  `text/plain` con `attachment` + `nosniff`, la pastilla *Ver pasos* sin icono, y que no haya regla global de
  `prefers-reduced-motion`).
- **Orden del deploy:** publicar los cuatro agentes de plataforma **antes** de que el portal los ofrezca, porque
  OLV-035 deja la tarjeta de arranque enlazando la pantalla muerta aunque el menu ya la oculte.
- **Lo que esta ronda sigue sin poder cubrir:** el texto de la mencion que **no resuelve** y el `delegar_subagente` con
  un codigo manipulado (los dos del prompt, piden `13-chat-libre.yml` con modelo real). Ya no es el caso de CA-03.3,
  CA-04.1, CA-04.2 ni D-05: el guion del simulador los dejo observables de forma permanente y sin costo.

### Checklist de merge
- [x] **Los seis defectos de los tres lotes, cerrados reproduciendo el caso original**, cada uno con el criterio
      arrancando en FAIL y con control negativo donde correspondia.
- [x] OLV-030 verificado en **los tres** sitios, incluido el tercero que ningun lote habia visto (la tarjeta de
      aprobacion con su *Resolver*).
- [x] OLV-031 reproducido en el **borde** que fallaba (18 agentes), no con pocos.
- [x] OLV-033 verificado por **las dos** compuertas y con los dos roles, y el contraejemplo del configurador y del
      asistente sigue en pie.
- [x] OLV-028 probado **antes** de publicar y sobre **las cuatro** conversaciones.
- [x] Los cuatro criterios BLOCKED, calificados con evidencia observada.
- [x] HU-04 re-corrida con los botones vivos: una tarjeta aplicada, una sola regla nacida.
- [x] Base devuelta a su estado y `git status --porcelain` del repo del sistema **sin un solo cambio mio**.
- [ ] **OLV-036 sin arreglar — reparo que condiciona la liberacion.**
- [ ] OLV-037 y OLV-035 sin arreglar.

### Base devuelta a su estado
Toda la corrida vivio en una organizacion **propia** (tenant 26), borrada entera al cerrar: sus 2 usuarios, su licencia
(15), su cliente (74), sus **14** tareas (265-278) con sus `PasosTarea`, `EjecucionesHerramienta`, `AprobacionesAccion`
y `AdjuntosMensajeTarea`, sus propuestas de las dos familias, las reglas 117-119, el instructivo 14, los documentos
108-109 con sus partes, los 38 `EventosUso` y la carpeta de blobs `App_Data/documentos/26`. Las cuatro versiones de
plataforma (147, 110, 79, 116) quedaron **Publicada**, exactamente como estaban al arrancar. Checksum contra el
snapshot previo, **todos iguales**: `TareasAgente=171, EventosUso=763, Reglas=77, Instructivos=6,
ProgramacionesTarea=16, AgentesOrganizacion=55, PropuestasRegla=35, PropuestasTrabajo=24, DocumentosCartera=81,
Recuerdos=10, Tenants=7`. **Nada de otras organizaciones se toco.** `.playwright-mcp/` vaciada.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-10-02


# QA M28 — El chat libre, LOTE 3 de 3: propuestas, adjuntos y la pantalla (2026-10-02)

**VEREDICTO: NO liberable como esta. Los dos defectos que la implementacion dijo haber arreglado estan arreglados de
verdad, la pieza 3D cumple todo lo que se le pidio y el aislamiento del adjunto aguanta. Lo que falla son las dos
cosas por las que existe el modulo: la preferencia personal propuesta NO se puede aplicar nunca (OLV-033), y el grupo
que ensena a configurar NO aparece al escribir la arroba (el OLV-031 que registro el lote 2, reproducido tambien aca).**

Alcance del lote: (a) las propuestas desde el chat libre, (b) los adjuntos sin cliente, (c) la pantalla, el motion y
la pieza 3D. Entrada leida por artefactos, sin la transcripcion del implementador: `1-analista-funcional.md` linea 10
y CA textuales (lineas 106-132), `2-disenador-funcional.md` lineas 8-100 (D-01, D-08, Estados, RD-01..05),
`5-implementador.md` TANDA 1b y TANDA 2, e instruccion `38` completa. Repo del sistema **read-only**: cero
`Edit`/`Write`/`sed -i` sobre el, verificado al cierre con `git status --porcelain`.

### Montaje
- Portal local propio en **`https://localhost:7201`** (`dotnet run --no-build --no-launch-profile -- --urls ...`), para
  no chocar con el lote 2 en el 7200. Modelo **simulado**, evidencia de costo cero en el log de arranque: *"Motor de
  agentes con MODELO SIMULADO (Anthropic:Simulado = true, entorno Development): no se llama a Anthropic y el costo es
  cero."* **Costo real de la corrida: USD 0,00.**
- **Organizacion propia**, creada y borrada por esta corrida: `qa-org-d` (tenant **25**, etapa SistemaCompleto, licencia
  de `inmobiliario,general`), con `dird@qa.test` (Directora) y `empd@qa.test` (Empleado), ambos `Super123!`. El
  aislamiento multi-tenant del producto alcanzo para trabajar en paralelo con el lote 2 sin tocarle nada.
- La version **147** del agente `chat-libre` ya estaba **Publicada** al arrancar (la publico el lote 2): **no se toco**.
- **El MCP de Playwright funciono.** Importante para la proxima corrida: el perfil del MCP **comparte cookies entre
  puertos** (la cookie no distingue 7200 de 7201), asi que todo se hizo en contextos aislados
  (`browser.newContext({ignoreHTTPSErrors:true})`) para no desloguear a la sesion del otro lote.
- **El simulador no tiene guion de las cuatro propuestas del chat libre**, pero `GuionReglaPropuesta` si es alcanzable:
  un pedido con **"de ahora en m"** deja una tarjeta de regla real en un chat libre. Es el unico camino sin costo para
  ver una propuesta de verdad; el resto de las familias se fabrican en `PropuestasRegla` / `PropuestasTrabajo`.

### Cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-03.1** Cero filas nuevas tras un turno de configuracion | **PASS** | Turno de la tarea 251 que deja una tarjeta. En base, tenant 25: `Reglas=0, Instructivos=0, ProgramacionesTarea=0, AgentesOrganizacion=0, Recuerdos=0` y **una sola** fila en `PropuestasRegla` (Estado=1, Pendiente). |
| **CA-03.2 / HU-05** El rol se chequea al aplicar | **PASS** | Propuesta de alcance **Organizacion** en el chat libre del **Empleado** (tarea 261): el Empleado **ve la tarjeta entera** ("Donde aplica: En toda la empresa") y **no tiene ni un boton**; el POST forzado a `/Propuestas/Aplicar` con el token antiforgery devuelve **403** *"Solo un Director puede configurar reglas conversando."* y `Reglas` del tenant sigue en 0. Despues la Directora la aplica y recien ahi nace la regla 116. |
| **CA-03.3** `TopePropuestas` = 10 | **BLOCKED** | No hay forma de observarlo: el tope solo se manifiesta cuando el modelo intenta la propuesta 11 **en un mismo paso**, y el simulado no tiene guion que proponga mas de dos. Estructuralmente `TopePropuestas.PorRespuesta` es `tipo == Trabajo ? 3 : 10`, asi que el chat libre cae en el 10 **por no ser trabajo**, no por una rama propia — pero eso es lectura de codigo, no evidencia. Lo cubre el test del implementador. |
| **CA-03.4** Las cuatro cosas quedan cubiertas | **PASS parcial** | Aplicadas de verdad las cuatro desde un chat libre: **regla** (Regla 116, alcance empresa), **instructivo** (*"Como armamos un resumen semanal"*, v1, visible en `/Instructivos`), **tarea programada** (Programacion 22, *"Todos los lunes a las 09:00"*) y **agente propio** (Agente 68, *"Consultas del estudio"*). **Parcial porque la regla de alcance personal —el default del chat libre— no se puede aplicar: OLV-033.** |
| **CA-03.5** Una instruccion no se convierte en memoria | **PASS (la mitad prohibida) / BLOCKED (la mitad permitida)** | Pedido escrito como orden (*"De ahora en mas…"*) en dos chats libres: deja **tarjeta de regla** y `Recuerdos` del tenant queda en **0**. La otra mitad —que un hecho si se anote como recuerdo sin confirmar— necesita que el modelo llame a `recordar`, y el simulado no tiene guion para eso en un chat libre. |
| **HU-04** El Director revisa y aplica; nada cambio hasta el boton | **PASS** | Antes de tocar nada: 0 reglas, 0 instructivos, 0 programaciones, 0 agentes. Tocando un boton por vez aparecio exactamente lo de esa tarjeta (116 → 22 → 68 → el instructivo), y las otras quedaron pendientes. |
| **CA-04.1** Adjunto sin cliente leido con `adjunto_leer` | **BLOCKED** | El chat libre ofrece `adjunto_leer` (lo confirma el frontmatter y el resolvedor), pero **el simulado no tiene guion que la llame**: `GuionDocumentos` esta condicionado a que la llamada ofrezca `documento_leer`, que en un chat libre no se ofrece. Verificarlo pide el modelo real (costo) o un guion nuevo. |
| **CA-04.2** El universo es solo lo adjuntado a esa conversacion | **BLOCKED** | Misma razon: sin una llamada real a la herramienta no hay nada que observar. La guarda esta escrita (`AdjuntosMensajeTarea` por `TareaAgenteId` + `TenantId`), pero leer el codigo no es evidencia. |
| **CA-04.3** Ningun formato se rechaza; no se sirve con su propio tipo | **PASS con reparo** | Subido `raro-qa3.qa3xyz` (extension inventada): **entra** (documento 107, Tipo=Otro). `GET /Documentos/Descargar/107` → `content-type: application/octet-stream`, `content-disposition: attachment`, `x-content-type-options: nosniff`. **Reparo:** el `.txt` (documento 106) se sirve `content-type: text/plain`, o sea **su propio tipo**; es inocuo porque igual va `attachment` + `nosniff`, pero el criterio escrito dice "nunca". |
| **CA-T.1 (adjunto) — pendiente que dejo el lote 1** | **PASS** | **Control positivo conseguido:** el documento **106 de la propia organizacion, que SI tiene cliente (73)**, adjuntado a un chat libre **sin cliente**, se acepta y crea la tarea 264 → la regla de "sin cliente" **no** es la que frena. Con el documento **105 (tenant 19)**: rechazado, sin crear tarea; con el id **99999**: **el mismo mensaje**, asi que tampoco filtra si existe. El que frena es el **filtro de tenant** de `ValidarAdjuntosAsync`. |
| **CA-07.1** Instruccion `38` | **PASS con dos reparos** | En `Tareas/Detalle` de un chat libre: compositor **`position: sticky; bottom: 16px`**, barra de contexto **`sticky; top: 68px`**, cuerpo de la respuesta medido en caracteres reales = **74 ch** (672 px a 14,4 px), y lo fijo (*"El chat libre no cambia nada por su cuenta…"*) en el **`card-header`**, no en el cuerpo. Reparos: *"Ver pasos (3)"* es pastilla (`border-radius: 9999px`, inline-flex, fondo y padding) pero **sin icono**, y el boton **Enviar** del arranque vive en una tarjeta aparte, separado del compositor por las pastillas. |
| **CA-07.2** La pieza 3D carga diferida | **PASS** | Pestana de red: `three.module.js` **no esta** entre los `<script src>` del HTML (12 scripts, ninguno es three) y se pide como `import()` dinamico a los **103 ms**, con **FCP a los 100 ms** y `domContentLoaded` a los 104 ms: el primer render ya habia ocurrido. |
| **CA-07.3 / HU-08** `prefers-reduced-motion: reduce` | **PASS con reparo** | Con `reducedMotion: 'reduce'`: `three.module.js` **no se pide, ni un byte**; `canvas` en el DOM = **0**; la pieza plana se dibuja (198 px, `animation-name: none`); pantalla completa, `textarea` y **Enviar** habilitados. Reparo: no hay regla global de movimiento reducido, asi que botones del design system conservan `transition-duration: 0.2s`. |
| **CA-07.4** Solo tokens `--ov-*`, 1440 y 390, claro y oscuro | **PASS** | Capturas de **viewport** (no de pagina completa) a 1440x900 y 390x844 en los dos temas, con datos reales. Sin scroll horizontal en ninguna de las cuatro (`scrollWidth <= innerWidth`); el fondo invierte (`rgb(240,244,248)` ↔ `rgb(15,23,42)`); la pieza 3D toma el primario del theme (lee `--ov-primary` del contenedor). |
| **CA-07.5** Degrada en silencio sin 3D | **PASS** | (a) CDN de jsdelivr bloqueado: queda el anillo plano (`ov-chat-pieza__plano` con sus dos anillos y el nucleo), **ningun cartel de error** en la pantalla, solo un `ERR_FAILED` en la consola. (b) Sin WebGL (`getContext('webgl*')` devuelve null): la libreria **ni se pide**, misma pieza plana, **cero errores de consola**. |
| **RD-02** La pieza se DESMONTA, no se oculta | **PASS** | Medido envolviendo `ovChatLibre3D.desmontar` y guardando el antes/despues en `sessionStorage` durante el **envio real**. Antes: 1 `canvas` `ov-chat-pieza__lienzo`, `display: block`, en el DOM, contador de `requestAnimationFrame` = 5. Despues: **`canvas` = 0 en todo el documento** (sacado del DOM, no `display:none`) y el contador **se congela en 5** (ningun frame nuevo). En `Tareas/Detalle` no queda ningun canvas. |
| **D-08 / RD-01** Las pastillas escriben menciones | **PASS** | Las cuatro: `data-escribe` = `@`, `@regla `, `@tarea-programada `, `@instructivo `. Al tocarlas el `textarea` queda exactamente con ese texto, el caret al final (1/7/18/13), el foco en el textarea y **sin navegar ni enviar**. Ninguna manda una pregunta armada. La primera abre el menu. |
| **HU-03** Escribiendo `@` se descubre que tambien se puede configurar | **FAIL** | `/ChatLibre/Mencionables` devuelve **22** opciones en **dos** grupos (18 Agentes + 4 Configurar). El menu dibuja **16 items y un solo grupo: "Agentes"**. Las cuatro opciones de configuracion **no estan en el DOM** y las flechas nunca llegan. Solo aparecen escribiendo `@re`, `@inst`, `@tarea` o `@agente`: o sea, solo si ya sabias. Es el **OLV-031** del lote 2, reproducido de forma independiente. |
| **D-03** El autocomplete es compartido | **PASS parcial** | En *Seguir conversando* de un chat libre el `textarea` lleva `data-menciones="/ChatLibre/Mencionables"` y `@` abre el menu. La contraparte (que en el configurador **no** abra) quedo sin verificar: esas pantallas no exponen un `textarea` en la ruta que probe. |
| **RD-04** El menu se abre hacia arriba cuando no hay lugar | **PASS** | A **390x600**: `data-lado="arriba"`, menu de 6 a 431 px, `textarea` arriba en 437 px → **no lo tapa**. Tambien a 1440 abre hacia arriba, por la posicion del compositor. |
| **CA-02.1** Teclado del menu | **PASS** | `ArrowDown` mueve el item activo (`ov-menciones__item es-activo`), `Enter` inserta `@consultas ` en el textarea, `Escape` cierra el menu (`display: none`). |

**Resumen: 13 PASS (4 de ellos con reparo declarado), 1 PASS parcial, 1 FAIL, 3 BLOCKED.**

### Los dos defectos que el lote 3 tenia que verificar, no creer
1. **La tarjeta de propuesta del chat libre no la veia nadie (`PropuestaReglaService` caia en `_ => false`) — ARREGLADO,
   reproducido.** La tarjeta de la tarea 251 se ve entera para su autora (titulo, texto, *por que* y los tres botones), y
   la de la tarea 261 se ve para el Empleado **incluso cuando no le corresponde aplicarla** (ahi se ve sin botones, que
   es lo correcto). Visibilidad y permiso quedaron separados de verdad.
2. **`TieneTarjetasDeTrabajo` dejaba al chat libre afuera y ninguna tarjeta de trabajo se podia aplicar — ARREGLADO, y el
   boton acciona de verdad.** Con dos tarjetas de familia *trabajo* fabricadas en el chat libre 251: el script
   `_ScriptPropuestasTrabajo` se carga, los botones llevan su `data-accion-propuesta-trabajo`, y al tocarlos sale el
   **POST real** a `/Propuestas/Aplicar` → `200 {"success":true}` con efecto en la base: `urlProgramacion:
   "/Programaciones/Detalle/22"` y `urlAgente: "/Agentes/Editar/68"`. No es un boton dibujado.

### Defectos
| id | sev | que | estado |
|---|---|---|---|
| **OLV-033** | major | Una **preferencia personal** propuesta en un chat libre **no se puede aplicar nunca**: falla con *"El configurador no crea ni cambia preferencias personales…"* —el mensaje de otra conversacion— y la propuesta se quema como **Fallida**. Pasa igual al Director y al Empleado sobre su propia preferencia. Causa raiz: `ReglaService.EsPropuestaDeTrabajoAsync` es una **lista blanca de un solo tipo** (`Tipo == TipoTarea.Trabajo`), y `ChatLibre` queda afuera. Es el molde **inverso** de R-A1: no es un default que traga el valor nuevo, es una lista blanca que lo excluye. **Ojo: `AnalistaAutomatizaciones` tambien esta afuera de esa lista**, asi que conviene revisar si M15 arrastra lo mismo. | **parte emitido** |
| **OLV-031** (del lote 2) | major | El grupo *Configurar* del autocomplete desaparece al escribir solo `@` cuando hay 16 agentes o mas (`TOPE = 16` aplicado a la lista **plana** en `site.js`). **Reproducido de forma independiente en este lote**, con 18 agentes: es el que hace fallar HU-03. | **ya catalogado por el lote 2** |
| **OLV-034** | minor | La tarjeta de una propuesta de alcance **personal** dice *"Donde aplica: —"*: `ConfiguradorTextos.DondeAplica` no tiene rama para `AlcanceRegla.Usuario` y cae al descarte. Preexistente, pero M28 lo vuelve el caso frecuente porque el alcance personal es el **default** del chat libre. | **parte emitido** |

**Partes de defecto emitidos: 2 (OLV-033, OLV-034)**, los dos con item nuevo en `docs/qa/regresiones-manuales.yml`
(causa raiz, `archivos_fix` como **hipotesis**, criterio de re-verificacion y leccion cross-proyecto), mas la
confirmacion independiente de **OLV-031**. **Auto-fixes aplicados: 0.** **Ningun defecto se cierra en esta corrida.**
Estado de los partes de la corrida anterior (lote 1): **OLV-029 aparenta estar arreglado** —el titulo dice *"Chat libre
#251"* y la fila del listado dice *"Chat libre | Chat libre"*, sin el rubro tecnico—, pero lo arreglo el commit `6d679d8`
**despues** del lote 1 y lo cierra quien lo reporto, no yo; **OLV-028 no se pudo re-verificar** porque habria que
despublicar la version 147, que es del lote 2.

### Criterio de re-verificacion (el que decide el PASS en la proxima corrida)
- **OLV-033:** `POST /Propuestas/Aplicar` sobre una propuesta de `Alcance=3` (Usuario) de un chat libre devuelve
  `success:true`, nace una fila en `Reglas` con `Alcance=3`, y el **Empleado** puede hacerlo sobre su propia
  conversacion. El alcance de empresa sigue dando **403** para el Empleado.
- **OLV-034:** la tarjeta de una propuesta de alcance personal muestra una frase en la linea *Donde aplica* y no una raya.
- **OLV-031 (del lote 2):** con 18 agentes mencionables, escribir solo `@` dibuja **los dos** encabezados de grupo y las
  flechas llegan a `@regla` sin tipear ningun filtro.

### Cobertura del catalogo cross-proyecto
Del indice `cat_resumen.txt` se corrieron por modulo equivalente: **OLV-025** (rotulos por enum con default util) →
**encontro OLV-034**, el mismo molde en el helper de alcance; **OLV-024** (aplicar una propuesta por GET) → **PASS**:
los dos botones de aplicar son `POST` con antiforgery, y el forzado sin rol da 403; **OLV-021** (layout del publico
equivocado) → **PASS**; **OLV-015** (boton con dos guardas excluyentes) → **PASS**: ningun enlace de las tarjetas lleva
a 404 (`/Reglas/Detalle/116`, `/Programaciones/Detalle/22`, `/Agentes/Editar/68` abren). **MH-047** (valor de enum nuevo
en los combos) la corrio el lote 2; su **molde inverso** —la lista blanca de un valor— es lo que encontro OLV-033 y
quedo anotado como leccion del item.

### Reglas nuevas o modificadas desde la ultima corrida
Dato del lote 1, no recalculado (`33` permite pasarlo entre lotes de la misma corrida): desde 2026-09-25 entro un solo
commit (`1c5b7b7`); de el, **lo unico que aplica a este sistema es ELV-008, MH-027 y MH-047**. ELV-008 y MH-027 ya
dieron **PASS** en el lote 1 y MH-047 la corrio el lote 2. **Este lote no tenia regla nueva propia que correr.**

### Riesgos de liberacion
- **Bloqueante: OLV-033.** El chat libre se vende como *"dejame armada una regla"* y el alcance con el que propone por
  defecto es el personal: hoy esa tarjeta aparece, invita a tocarla y **siempre** falla, con un mensaje que nombra otra
  pantalla. Es el camino mas probable del usuario real, no un borde.
- **Bloqueante blando: OLV-031.** Con un rubro de 18 agentes, el mecanismo que el modulo existe para ensenar
  (*"escribi `@` y enterate de que tambien podes configurar"*) **no se descubre**. En dev no se ve porque hay pocos agentes.
- **No bloqueantes:** OLV-034 (cosmetico), el `.txt` servido como `text/plain` (va `attachment` + `nosniff`), la pastilla
  *Ver pasos* sin icono, y que no haya regla global de `prefers-reduced-motion`.
- **Lo que esta corrida NO pudo cubrir y hay que mirar antes de liberar:** `adjunto_leer` de punta a punta (CA-04.1 y
  CA-04.2) y el tope de 10 propuestas (CA-03.3). Las tres piden el modelo real o un guion nuevo del simulador. **La
  decision barata: agregarle al `ProveedorModeloSimulado` un guion de chat libre que adjunte y lea, y otro que proponga
  de a once.** Sin eso, estos tres criterios se van a seguir yendo en BLOCKED corrida tras corrida.

### Checklist de merge
- [x] La pieza 3D cumple las cinco condiciones que se le pusieron (diferida, desmontada, reduced-motion, sin WebGL, CDN caido).
- [x] La pantalla cumple la `38` en lo medible (compositor acoplado, 74 ch, lo fijo en el rotulo, trazabilidad como pastilla).
- [x] 1440 y 390, claro y oscuro, con datos de verdad, por captura de **viewport** y scroll real.
- [x] Aislamiento del adjunto verificado **con control positivo** (cierra el BLOCKED del lote 1).
- [x] Las cuatro cosas que se cargan se aplican de verdad desde un chat libre.
- [x] Base devuelta a su estado y `git status --porcelain` del repo del sistema **sin un solo cambio mio**.
- [ ] **OLV-033 sin arreglar — bloqueante.**
- [ ] **OLV-031 sin arreglar (del lote 2) — HU-03 no se cumple.**
- [ ] OLV-034 sin arreglar.
- [ ] CA-03.3, CA-04.1 y CA-04.2 en BLOCKED: hace falta guion del simulador para poder calificarlos alguna vez.

### Base devuelta a su estado
Toda la corrida vivio en una organizacion **propia** (tenant 25), borrada entera al cerrar junto con sus 2 usuarios, su
licencia, su cliente, sus 3 tareas (251, 261, 264), sus propuestas, la regla 116, el instructivo, la programacion 22, el
agente 68, sus documentos y sus blobs (`App_Data/documentos/25` eliminada). Checksum contra el snapshot previo, todos
iguales: `Reglas=77, Instructivos=6, ProgramacionesTarea=16, AgentesOrganizacion=55, PropuestasRegla=35,
PropuestasTrabajo=24, DocumentosCartera=81, Recuerdos=10`. **Nada de otras organizaciones se toco**, y la version 147
quedo **Publicada**, exactamente como la dejo el lote 2. `.playwright-mcp/` vaciada.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-10-02


# QA M28 — El chat libre, LOTE 2 de 3: menciones, resolucion y delegacion (2026-10-02)

**VEREDICTO: aprobado con reparos. El motor de la delegacion esta bien: el aislamiento entre los dos modos de
subagentes aguanta, el hilo se despierta en los TRES finales (completada, fallida y cancelada) y el agente de la
parte corre con su propio contexto. Lo que falla es la PANTALLA de la mencion: el grupo que ensena a configurar
desaparece cuando la organizacion tiene muchos agentes, y la tarjeta de parte no se dibuja nunca en un chat libre.**

Alcance: (a) autocomplete de menciones, (b) resolucion de la mencion en el servidor, (c) delegacion / espera /
despertar. Entrada leida por artefactos (`1` linea 10 y CA 97-103, `2` lineas 31-34 y 95-97, `5` TANDA 1 y TANDA 2),
sin la transcripcion del implementador. Repo del sistema **read-only**: `git status --porcelain` verificado al cierre.

### Montaje
- Organizacion propia **24 `qa-org-c`** (licencia 13: inmobiliario + general, 18 agentes publicados usables) con
  `empc@qa.test` (Empleado) y `dirc@qa.test` (Directora), clonando el `PasswordHash` de `empa@qa.test` (`Super123!`).
  Se eligio org propia porque el **lote 3 escribe en la misma base** (creo el tenant 25 y 3 tareas durante mi corrida).
- Portal `https://localhost:7200` con `Anthropic__Simulado=true` y `Subagentes__SegundosBarrido=2`: el barrido por
  defecto es **60 s** y hace inobservable el despertar. **Costo real: USD 0,00.** MCP de Playwright **funciono**, con
  `newContext({ignoreHTTPSErrors:true})` + `storageState` en archivo (`globalThis` no sobrevive entre llamadas).
- Artefacto 121 version **147 publicada** con `evaluacion-excepcion` + `publicar`, y **dejada publicada** para el
  lote 3. Guion del simulado: **"deleg"** dispara la delegacion; **"falle"** en el pedido de la parte la hace fallar;
  **"aprob"** la deja esperando aprobacion — asi se consigue un hilo colgado a voluntad.

### Cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-02.1** `@` abre el menu; flechas, Enter/Tab, Escape | **PASS** | `@` abre `.ov-menciones`; ArrowDown x2 -> `aria-activedescendant=ov-mencion-2`, ArrowUp -> `-1`; **Enter** deja `"@consultas "`, **Tab** deja `"@inmo-tasador "`, **Escape** cierra y el texto queda literal (`"@"`). **Ctrl+Enter con el menu abierto ENVIA** (fue a `/Tareas/Detalle/246`). |
| **CA-02.1 / D-06** el menu viene en **dos grupos** | **FAIL** | Con 18 agentes usables, `@` sola pinta **16 items y un solo rotulo: "Agentes"**. El endpoint devuelve 22 (18 + 4 de "Configurar") y el grupo que ensena **no aparece**. `var TOPE = 16` con `.slice(0, TOPE)` sobre la lista plana. Defecto **OLV-031**. |
| **CA-02.2 / A-08 / R-A2** ofrece solo lo usable; sin version publicada no aparece | **PASS** | `/ChatLibre/Mencionables` = **18 agentes**, identicos a los 18 del catalogo `/Agentes` de esa persona (comparados uno por uno) e identicos a los **18 codigos que la herramienta autorizo** (`subagentes_listar`, paso 2 de la tarea 249). Sin `qa-m4` (rubro sin licencia), sin plataforma, **sin los agentes de empresa de la org 1**. Al despublicar `inmo-tasador` (version 15 a Borrador) los **tres** bajaron a 17 en simultaneo y ninguno lo trajo. Con la licencia revocada: 0 agentes y el grupo Configurar completo. |
| **CA-02.3** mencion manipulada / de otra organizacion no resuelve ni filtra que exista | **PASS (otra organizacion y sin publicar) / BLOCKED (codigo forzado y el texto del turno)** | Los agentes de la org 1 (`o-12`, `o-13`) y el despublicado **no estan** ni en la pantalla ni en la lista que autoriza — y la lista **es** la autorizacion (una sola operacion, A-08). Lo que **no** se pudo observar: forzar un `delegar_subagente` con un codigo manipulado (no hay via de inyeccion desde el cliente; el guion del simulado solo manda codigos de la lista) y que **el turno lo diga sin confirmar si existe**, que es comportamiento del prompt. Cobertura disenada: caso 3 de `13-chat-libre.yml`, que **necesita modelo real**. |
| **CA-02.4** abre tarea del agente; el hilo pasa a `EsperandoSubtareas`; **muestra la tarjeta de parte** | **PASS (estado) / FAIL (tarjeta)** | Estado observado en el DOM: "En curso" -> **"Esperando a otros agentes"** (tareas 249, 254, 256) y en base `Estado=7`. Parte creada, **UNA sola** por delegacion en las 4 corridas (`COUNT(*) WHERE TareaPadreId` = 1; el defecto 1 de la tanda 1 sigue arreglado). Pero `document.querySelectorAll('.ov-parte').length` = **0** en todo momento. Defecto **OLV-030**. |
| **CA-02.5** se despierta solo, y **tambien si la parte falla** | **PASS** | Tres finales, los tres sin recarga y sin quedar colgado: **completada** (249, *"Junte lo que me contestaron los otros agentes"*), **fallida** (254/255, `Estado=5`: *"Una parte no salio: El otro agente no pudo terminar..."*) y **cancelada** (256/257, cancelada mientras esperaba aprobacion: *"Una parte no salio: La parte se cancelo antes de terminar."*). **R-04 no reproduce.** |
| **CA-02.6** `ProfundidadMaxima` sigue valiendo | **PASS** | Las partes 250 y 253 nacen con `Profundidad=1` y `ProfundidadMaxima=1`. El pedido de la parte **contiene "deleg"** (lo arrastra del mensaje del padre), asi que el guion del simulado habria delegado **si la herramienta estuviera ofrecida** (`ofreceDelegar` es literalmente "`delegar_subagente` esta en la lista"); las dos cerraron en **1 paso de texto**, sin `subagentes_listar`. Segunda capa independiente: el guard de `PrepararAsync`. |
| **CA-02.7** corre con SU prompt, SUS herramientas y las reglas de la empresa | **PASS** | `ReglasAplicadasJson` de la tarea 258 (chat libre): `formatoVersion:6, configuradorVersionId:147, instruccionVersionIds:[126]`, **sin clave `reglas`**. De su parte 259: `formatoVersion:1, agenteVersionId:130, instruccionVersionIds:[], reglas:[{nivel:3,reglaId:115}]` — la regla de empresa que cree para el caso. En la parte 253: `agenteVersionId:12` e `instruccionVersionIds:[17..26]`, las del rubro inmobiliario. `HashContexto` distinto en cada uno. |
| **D-05** dos menciones de agente: se pide elegir | **BLOCKED** | Es comportamiento del prompt (`chat-libre.md` linea 62: *"Un agente por mensaje... preguntale a cual"*); **no hay codigo que cuente menciones: el servidor nunca parsea la arroba** (D-04 llevado al extremo). Con el modelo simulado el guion siempre delega al primero de la lista. Cobertura disenada: caso 2 de `13-chat-libre.yml`, **requiere modelo real**. |
| **RD-04** a 390 px se abre hacia arriba | **PASS** | En `Tareas/Detalle` a **390x844** y a **390x420** (teclado abierto), con el compositor abajo: `data-lado="arriba"`, menu en `top 6 / bottom 631` y `6 / 207`, textarea en `637` y `213` — dentro del viewport, **sin solaparse** y sin scroll horizontal. En el arranque, donde el compositor esta arriba, abre `abajo` y entra igual (838 de 844). A 1440x900 con 16 items tambien abre `arriba`. |
| **R-A3** una tarea de TRABAJO sigue viendo solo los hijos de su base | **PASS — el dato mas importante del lote** | Misma delegacion por los dos caminos: chat libre 249 -> **18** codigos `b-<rubro>/<slug>` (incluye `b-general/en-blanco` y `b-general/consultas`); tarea de Trabajo 252 con base `inmo-orquestador` -> **15** codigos `b-<slug>`, **exactamente sus hijos**, sin los dos de `general`, sin `inmo-orquestador` y sin prefijo de rubro. El modo abierto **no se filtro**. |
| **D-03** el autocomplete funciona en `Tareas/Detalle` y **no** en las otras conversaciones | **PASS (con reparo)** | El compositor de *Seguir conversando* de un chat libre trae `data-menciones="/ChatLibre/Mencionables"` y el menu abre. En la conversacion del analista (tarea 260) escribir `@` **no abre nada**. Reparo: el atributo igual se emite, **vacio**, y dispara un `fetch('')` mudo. Defecto **OLV-032**. |
| **D-08 / RD-01** las pastillas escriben menciones | **PASS (con el reparo de OLV-031)** | Las 4 `[data-escribe]` dejan `"@"`, `"@regla "`, `"@tarea-programada "`, `"@instructivo "`, cursor al final, **ninguna envia el formulario** (la URL no cambia) ni manda una pregunta armada. La primera abre el menu — pero solo con el grupo "Agentes", que es justo lo que OLV-031 le saca. |

**Resumen: 9 PASS (2 con reparo), 2 FAIL, 2 BLOCKED (mas la mitad de CA-02.3).**

### Maquina de estados (D-02 y tabla de `2-disenador` linea 55)
`En cola -> En curso -> EsperandoSubtareas ("Esperando a otros agentes") -> En cola -> Completada`, observado en las
tareas 249, 254, 256 y 258. Nunca se vio el enum crudo en pantalla (OLV-013 no reaparece). El estado **"Mencion que
no resolvio"** de la tabla no se pudo recorrer: es del prompt, BLOCKED junto con D-05.

### Cobertura del catalogo cross-proyecto
Del indice `cat_resumen.txt` (141 items al arrancar) se corrieron **9** por modulo equivalente:
**REG-003** (autocomplete que no devuelve resultados) PASS; **REG-005** (resultados sin texto) PASS — cada item trae
nombre, rubro y mencion; **OLV-019 / MH-052** (la baja de un valor se implementa solo en el combo y el POST lo sigue
aceptando) **PASS** — es el molde exacto de la mencion, y se probo en el negativo despublicando un agente: cayo de la
pantalla **y** de la lista que autoriza; **MH-027** (un valor nuevo del enum vuelve ambiguo un lookup) PASS, 1 parte
por delegacion en 4 corridas; **MH-047** (valor nuevo de enum en todos los combos que iteran el enum) **PASS** en los
tres combos de `/Tareas`, en los rotulos del detalle y en `/Consumo`; **OLV-025 / OLV-029** (rama default que le pone
a un valor nuevo el rotulo de otro) **PASS: OLV-029 esta arreglado**; **OLV-013** (enum crudo en pantalla nueva) PASS;
**KOI-009** (AJAX con URL absoluta) PASS — la url sale de `Url.Action`, no hardcodeada; **MH-041** (un inventario
enumerado a mano omite pantallas; cerrarlo por los **LECTORES** de la fuente) **APLICADA y es la que encontro
OLV-032**: el inventario se cerro por el unico lector de `data-menciones` en vez de por la lista de pantallas.
**OLV-007 / OLV-001** (Select2) N/A: el autocomplete es propio, no Select2. **OLV-027** N/A.

### Reglas nuevas o modificadas desde la ultima corrida
El delta lo calculo el lote 1 (commit `1c5b7b7`, unico desde 2026-09-25) y **no se recalculo**: de las 19 reglas e
items nuevos, los que aplican a este sistema son **ELV-008, MH-027 y MH-047**. ELV-008 y MH-027 quedaron PASS en el
lote 1; **MH-047 se volvio a correr aca sobre los combos y rotulos de la pantalla nueva y dio PASS** — el defecto que
habia destapado (OLV-029) esta arreglado por el commit `6d679d8`, que el lote 1 no tenia en su diff.

### Defectos
| id | sev | que | estado |
|---|---|---|---|
| **OLV-030** | major | La **tarjeta de parte no se dibuja nunca** en un chat libre: `_Conversacion.cshtml` decide las partes del turno con `Model.EsDePlataforma ? Array.Empty<SubtareaDto>() : Model.SubtareasDelTurno(t)`, y el chat libre entra a ese flag a proposito (es la palanca que le da las herramientas de plataforma). Rompe **CA-02.4** y **D-07** de frente. El caso peor: una parte que espera aprobacion deja el hilo en *"Esperando a otros agentes"* sin decir de que ni ofrecer el enlace *Resolver* que la tarjeta trae. No hay switch de enum: es un **booleano viejo cuyo significado se desdoblo**, invisible a un relevamiento de switches por `TipoTarea`. | **parte emitido** |
| **OLV-031** | major | El autocomplete **se come el grupo "Configurar"** en cuanto la organizacion tiene 16 agentes o mas: `var TOPE = 16` con un `.slice(0, TOPE)` sobre la lista ya concatenada, y el grupo fijo va ultimo. Rompe **D-06**, **HU-03** y la prueba minima 20. El test de la suite afirma el borde contrario (el grupo con **cero** agentes) y por eso pasa. **El lote 3 lo reprodujo de forma independiente.** | **parte emitido** |
| **OLV-032** | trivial | `_CuadroSeguimiento.cshtml` emite `data-menciones` **siempre**, vacio cuando no es chat libre (la nota de implementacion dice "solo si `EsChatLibre`"). El selector `[data-menciones]` matchea el vacio, `fetch('')` se trae la pagina entera, `r.json()` lanza y el `catch` lo silencia: un pedido de pagina completa por cada compositor que no deberia estar escuchando. | **parte emitido** |

**Partes emitidos: 3 (OLV-030, OLV-031, OLV-032)**, los tres con item nuevo en `docs/qa/regresiones-manuales.yml`
(causa raiz, `archivos_fix` como **hipotesis**, criterio de re-verificacion y leccion cross-proyecto).
**Auto-fixes aplicados: 0.** Ningun defecto se cierra en esta corrida.

**Partes de la corrida anterior (lote 1):**
- **OLV-028** (el menu ofrece "Chat libre" sin version publicada): **no re-verificado** — llegue con el artefacto en
  Borrador y lo publique para poder probar mi alcance, asi que el criterio dejo de ser observable. Sigue abierto.
- **OLV-029** (el chat libre rotulado "Configuracion de reglas"): **re-verificado y PASS**, con el criterio arrancando
  en FAIL. `document.title` = **"Chat libre #247"**; la fila de `/Tareas` dice **"Chat libre | Chat libre"** y su
  `innerText` **no contiene "plataforma"**. Lo arreglo el commit `6d679d8`, posterior al diff que leyo el lote 1.
  **Propuesta: cerrarlo.**

### Criterio de re-verificacion (el que decide el PASS en la proxima corrida)
- **OLV-030:** con un chat libre en `EsperandoSubtareas`, `document.querySelectorAll('.ov-parte').length >= 1`; y con
  la parte en espera de aprobacion la tarjeta ofrece el camino para resolverla. En una conversacion del configurador
  el mismo selector sigue dando 0.
- **OLV-031:** en una organizacion con **mas de 16** agentes usables, con la arroba sola:
  `document.querySelectorAll('.ov-menciones__grupo').length === 2` y el grupo "Configurar" conserva sus 4 opciones.
- **OLV-032:** en la conversacion del analista, `document.querySelector('textarea').hasAttribute('data-menciones')`
  da `false`, y escribir `@` no agrega ningun pedido en el panel de red.

### Riesgos de liberacion
- **Bloqueante por datos, plata o aislamiento: ninguno.** Nada de lo que encontre toca el motor ni el tenant: el
  aislamiento de los dos modos y el contexto de la parte son los dos puntos mas caros de M28 y los dos aguantan.
- Pero **OLV-030 y OLV-031 vacian los dos pedidos de M28**: la trazabilidad de la delegacion (que el diseno llama
  diferencial del producto, no nota al pie) y el descubrimiento de que tambien se puede configurar mencionando.
  Liberar la pantalla con los dos abiertos es liberarla sin lo que la justifica.
- **OLV-031 empeora con el tiempo:** una organizacion arranca con pocos agentes y el grupo se ve; al pasar de 16
  desaparece sin que nada falle. Es el peor perfil posible para detectarlo en produccion.
- **Lo que este lote no cubrio:** D-05 y el texto de la mencion que no resuelve (los dos del prompt: piden una corrida
  de `13-chat-libre.yml` con modelo real, 12 casos con Opus) y el codigo de delegacion forzado.

### Checklist de merge
- [x] Aislamiento de los dos modos de subagentes verificado con las dos listas reales (18 contra 15), no por lectura.
- [x] Una sola parte por delegacion, 4 veces.
- [x] El hilo se despierta en los tres finales (completada, fallida, cancelada): R-04 no reproduce.
- [x] El contexto de la parte verificado en la instantanea (`ReglasAplicadasJson`), con una regla de empresa real.
- [x] La pantalla y la herramienta autorizan lo mismo, probado en el positivo y en el negativo.
- [x] Base devuelta a su estado (ver abajo) y `git status --porcelain` del repo del sistema **sin un cambio mio**.
- [ ] **OLV-030, OLV-031 y OLV-032 sin arreglar** — vuelven al Implementador.
- [ ] **OLV-028 sigue abierto**; OLV-029 propuesto para cierre.

### Base devuelta a su estado
Borradas mis **16 tareas** de la org 24 (partes antes que padres por la FK) con sus `PasosTarea`,
`EjecucionesHerramienta`, `AprobacionesAccion` y 40 `EventosUso`; la regla 115 con su `ReglaEvento`; los 2 usuarios
con sus `AspNetUserRoles`; la licencia 13 con sus `LicenciaRubros`; y el tenant 24. Restaurados a mano los dos cambios
temporales **antes** de borrar: version 15 (`inmo-tasador`) de nuevo **Publicada** y licencia 13 **no revocada**.
`TareasAgente` quedo en **174** = los 171 del arranque mas las **3 del lote 3**, que no se tocaron; `EventosUso` en
771. Sin adjuntos subidos, asi que ningun blob nuevo en `App_Data/documentos`.
**Lo unico que queda cambiado a proposito:** la version **147 publicada** (con su `evaluacion-excepcion`), porque el
lote 3 la necesitaba; el lote 1 la habia dejado en Borrador.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-10-02


# QA M28 — El chat libre, LOTE 1 de 3: arranque, permisos e historial (2026-10-02)

**VEREDICTO: aprobado con reparos. Los dos defectos graves que la implementacion dijo haber arreglado estan
arreglados de verdad, y el aislamiento aguanta. Lo que falla es que el menu ofrece la pantalla cuando el agente no
esta publicado, y que el tipo nuevo hereda el rotulo de otro tipo.**

Alcance del lote: (a) arranque y disponibilidad, (b) permisos y aislamiento multi-tenant, (c) historial y filtro.
Entrada leida por artefactos, sin la transcripcion del implementador: `1-analista-funcional.md` linea 10 y CA
textuales (lineas 89-135), `5-implementador.md` TANDA 1 / 1b / 2, y el diff de los commits `d7ee4c8`, `0c16930`,
`87530b2`. Repo del sistema **read-only**: cero `Edit`/`Write` sobre el, verificado al cierre.

### Montaje (lo que los lotes 2 y 3 pueden reusar tal cual)
- `olvidata_agentes_dev` migrada; portal local `https://localhost:7200` con **modelo simulado**, evidencia de costo
  cero en el log de arranque: *"Motor de agentes con MODELO SIMULADO (Anthropic:Simulado = true, entorno
  Development): no se llama a Anthropic y el costo es cero."* **Costo real de la corrida: USD 0,00.**
- **El MCP de Playwright FUNCIONO** en esta sesion (no hizo falta caer al procedimiento manual de la instruccion 33).
  `browser_run_code_unsafe` con `newContext({ignoreHTTPSErrors:true})` para las sesiones paralelas del IDOR.
- `dotnet build OlvidataAgentes.slnx` → **0 errores** (15 advertencias, todas preexistentes).
- Suite de contexto/goldens/chat libre: **97 de 97 verdes** (`FullyQualifiedName~Contexto|Golden|ChatLibre`).
- Usuarios: `empa@qa.test` (Empleado, org 1, autor de todos los chats), `dira@qa.test` (Directora, org 1),
  `dirb@qa.test` (Director, org 4, para el cross-tenant). `qa-m21@test.local` **no entra** con la contrasena comun
  (un intento, no se insistio para no bloquear la cuenta).
- **Para los lotes 2 y 3: el artefacto `chat-libre` ya esta importado** (artefacto 121, version **147**), y quedo
  **en Borrador** al cerrar. No hace falta importar: alcanza con
  `evaluacion-excepcion 147 --motivo "..."` + `publicar 147` (el `evaluar --aprobada` NO sirve desde M8).
  **Probar CA-01.2 antes de publicar ya esta hecho y dio FAIL: no hace falta repetirlo.**

### Cobertura por criterio

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| **CA-01.1** Cualquier miembro activo abre la pantalla | **PASS** | `empa@qa.test` (`RolOrganizacion=2`, Empleado) abre `/ChatLibre` con 200, sin elegir agente, cliente ni rubro; `textarea[name=Texto]` habilitado. |
| **CA-01.2** Sin version publicada: no esta en el menu y la URL avisa | **FAIL** | Con el artefacto inexistente en la base, el sidebar **si** muestra `Chat libre → /ChatLibre`. La URL **si** responde bien ("Todavia no esta disponible."). El catalogo de Agentes **si** lo oculta. Defecto **OLV-028**. |
| **CA-01.3** Turno en vivo por SignalR + respaldo de polling | **PASS** | Con el hub conectado, la tarea 243 paso de "En curso" → "Esperando a otros agentes" → "Completada" en el DOM **sin recargar**. Repetido con `routeWebSocket(close)` + `/negotiate` abortado (3 errores de consola de SignalR): el turno de la tarea 245 llego igual a los 8 s, sin recarga. |
| **CA-01.4** Reanuda tras reiniciar el proceso, mismo contexto, costo en la barra | **PASS** | Seguimiento encolado con el motor a 90 s de sondeo; `Stop-Process -Force` sobre el PID del 7200 con la tarea 243 en `Estado=1`. Al relanzar: `Estado=4`, **`HashContexto` byte a byte identico** (`2b06f880…a48e… 25322`) antes y despues del reinicio, partes seguian en **1**, pasos 5 → 7. Barra con costo fabricado: **"USD 0,37 · con sus partes USD 0,49"**. |
| **CA-01.5** Con el tope de gasto alcanzado no arranca y dice por que | **PASS** | `LimitesGastoMiembro` = USD 5 + un paso con `CostoUsd=9,50`. Pantalla: *"Llegaste a tu limite de gasto de octubre (USD 5,00). Se renueva el 1 de noviembre; para ampliarlo, habla con un Director de tu empresa."* Boton Enviar **deshabilitado**, y el **POST forzado** a `/ChatLibre/Iniciar` devolvio la misma vista **sin crear ninguna tarea** (verificado en base). Ningun valor de M6 se toco. |
| **CA-05.1 / 05.2** Solo el autor continua | **PASS** | Defensa en el **servidor**, no solo en la UI: `POST /Tareas/EnviarSeguimiento` sobre la tarea 241 → autor **200** *"Mensaje enviado"*; Directora de la misma org **403** *"Solo quien pidio la tarea puede seguir esta conversacion."*; Director de otra org **404** *"La tarea no existe."* La Directora **si** lee el contenido (200 en el detalle) y no tiene ni el boton ni el textarea. |
| **HU-07** El Empleado encuentra sus chats libres y los reabre | **PASS** | En `/Tareas` el Empleado ve su chat (#241) junto a sus 2 tareas viejas y **solo** las suyas (3 filas, todas con su `UsuarioId`). Filtro `Tipo=ChatLibre` → devuelve exactamente el chat; `Tipo=Trabajo` → lo excluye. Reabre con el historial entero y "Seguir conversando". **A-09 arreglado.** |
| **CA-T.1** Manipular ids en URL y en el adjunto | **PASS (URL) / BLOCKED (adjunto)** | URL: `/Tareas/Detalle/241` desde la org 4 → **404**; ids `99999`, `-1`, `0` → **404**. `/ChatLibre/Mencionables` devuelve solo agentes de los rubros licenciados de la org 1 (y ninguna mencion es un codigo interno). Adjunto: el documento **37 (org 4)** se rechaza con un mensaje **indistinguible** del de un id inexistente y sin crear tarea — pero **todos** los documentos de la org 1 en esta base tienen cliente, y un chat libre no lo tiene, asi que **no hay control positivo** y no puedo probar que el rechazo sea la guarda de tenant y no la regla de "sin cliente". **Lo cierra el lote que prueba la subida de un adjunto sin cliente.** |
| **CA-T.3** El formato 6 no cambio el hash de ninguna tarea vieja | **PASS** | Snapshot de `Id,Tipo,HashContexto` de las **171** tareas previas antes de importar, y `diff` contra el mismo query despues de importar **y publicar** el agente de formato 6: **sin una sola diferencia**. El `importar` reporto *"1 artefactos nuevos, 1 versiones nuevas, 8 sin cambios"*. Goldens 1 a 5 intactos (97/97 verdes). **Limite declarado:** no se pudo reanudar una tarea vieja para ver si el **recomputo** da el mismo hash (ninguna tarea vieja con hash pertenece a un usuario al que pude entrar); la cobertura mecanica de eso son los goldens. |

**Resumen: 7 PASS, 1 FAIL, 1 parcial (PASS en la URL / BLOCKED en el adjunto).**

### Los dos defectos graves de la implementacion: verificados, no creidos

1. **`ProcesadorTareas`, el lookup de partes — ARREGLADO, reproducido.** Chat libre con delegacion real
   (la palabra "deleg" dispara el guion del simulado): la tarea 243 estuvo en `EsperandoSubtareas` con el motor
   sondeando **cada 1000 ms**, se desperto sola y cerro citando a la parte. En base:
   `SELECT COUNT(*) FROM TareasAgente WHERE TareaPadreId=243` → **1**. Con el defecto habrian sido una por sondeo.
   **Confirmado una segunda vez tras el reinicio del proceso**: la reanudacion no agrego ninguna parte (siguio en 1).
2. **Visibilidad de la tarjeta de propuesta** — no se cruzo en este lote (ningun turno dejo tarjeta). Queda del
   lote 3, como estaba previsto.

### Cobertura del catalogo cross-proyecto
Del indice `cat_resumen.txt` (139 items) se seleccionaron por modulo equivalente y se corrieron **6**:
OLV-015 (boton con dos guardas excluyentes) **PASS** — ningun enlace del chat libre lleva a 404; OLV-021 (layout del
publico equivocado en pantallas compartidas) **PASS** — los 404 del cross-tenant dibujan el layout propio;
OLV-022 (acciones de cuenta propia detras de la policy) **PASS** — ningun item del menu del Empleado termina en
AccessDenied; MH-027 (un valor nuevo del enum vuelve ambiguo un lookup por otra clave) **PASS** — el lookup de partes
quedo acotado por lista blanca de tipo y da 1; **MH-047 (un valor de enum nuevo aparece solo en todos los combos que
iteran el enum) → PASS en el combo** (el filtro de `/Tareas` ofrece "Chat libre", que es lo que se quiere) **pero
destapo OLV-029**: el molde inverso, los **rotulos** por ternario, donde el tipo nuevo no tiene rama y hereda la de
otro; OLV-027 (`CancelAfter(TimeSpan.Zero)`) **N/A** — M28 no agrego topes de tiempo.

### Reglas nuevas o modificadas desde la ultima corrida — RESULTADO PARA LOS LOTES 2 Y 3
Ultima validacion registrada: **2026-09-25**. Diferencia calculada con
`git log --since=2026-09-25 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
→ un solo commit, `1c5b7b7` (2026-10-02). Lo que entro:

- **Instruccion 32: 3 reglas nuevas.** **MH-033** y **MH-034** (el ledger de caja registra toda salida real de dinero;
  un solo ledger para varias cuentas reales no se concilia) → **NO APLICAN**: este producto no tiene ledger de caja,
  ni cuentas bancarias, ni conciliacion. **ELV-008** (una validacion "esto no puede ser negativo" se escribe sobre los
  campos que de verdad no pueden) → **APLICADA y PASS**: el unico piso que M28 toca es el tope de gasto de M6, que es
  un solo campo (`LimiteMensualUsd`) y no mete campos ajenos en el calculo; se probo el borde exacto (gasto 9,50
  contra tope 5,00) y el bloqueo nombra la situacion real del usuario, con el mes y el monto.
- **Catalogo: 16 items nuevos** (MH-027, MH-033 a MH-048, MH-052, MH-054, ELV-003 a ELV-007). Todos de dominio
  financiero de marihogar o de contadores de maquinas de eleven-la-plata **salvo MH-027 y MH-047**, que son los dos
  conceptuales sobre **agregar un valor a un enum**, y los dos aplican directo a `TipoTarea.ChatLibre = 6`: se
  corrieron y estan arriba (MH-027 PASS; MH-047 PASS en el combo y **encontro OLV-029**).
- **Conclusion que los lotes 2 y 3 no tienen que recalcular:** del delta de reglas, **lo unico que aplica a este
  sistema es ELV-008, MH-027 y MH-047**; las otras 17 son de dominio financiero ajeno. ELV-008 y MH-027 ya estan
  cubiertas por este lote. **MH-047 conviene volver a correrla en el lote 2** sobre los combos y rotulos de la
  pantalla nueva, porque es la que destapo el defecto.

### Defectos
| id | sev | que | estado |
|---|---|---|---|
| **OLV-028** | major | El menu lateral ofrece "Chat libre" sin version publicada del agente, y lleva a una pantalla muerta. El catalogo de Agentes si lo oculta, el controller si lo frena: falta la guarda en el menu. Causa raiz: `PuedeUsarChatLibre => EsMiembro && !EsStaff` es rol puro y `VeEnMenu` nunca llama a `IChatLibre.DisponibleAsync`. | **parte emitido** |
| **OLV-029** | minor | El detalle de un chat libre se rotula "Configuracion de reglas" (titulo del navegador y encabezado) y en el listado la fila cae al rubro tecnico "plataforma". Causa raiz: cadenas ternarias con el else final como default, en `Detalle.cshtml:15` (Razor) y `Index.cshtml:219` (JS) — la variante de **vista** de R-A1, que el relevamiento de switches de C# no cubre. | **parte emitido** |

**Partes de defecto emitidos: 2 (OLV-028, OLV-029).** Los dos con item nuevo en `docs/qa/regresiones-manuales.yml`
(causa raiz, `archivos_fix` como **hipotesis**, criterio de re-verificacion y leccion cross-proyecto).
**Auto-fixes aplicados: 0** — desde 2026-09-25 QA no parchea. **Ningun defecto se cierra en esta corrida.**
**Partes de la corrida anterior: ninguno** (M27 quedo con el plan escrito y sin ejecutar).

### Criterio de re-verificacion (el que decide el PASS en la proxima corrida)
- **OLV-028:** con el artefacto `chat-libre` en Borrador (`UPDATE ArtefactoVersiones SET Estado=1 WHERE Id=147`), el
  `innerText` del sidebar de un Empleado **no contiene** "Chat libre"; y despues de publicar, si lo contiene.
- **OLV-029:** `document.title` y el encabezado de un chat libre contienen su nombre propio y **no** "Configuracion de
  reglas"; y el `innerText` de su fila en `/Tareas` **no contiene** "plataforma".

### Riesgos de liberacion
- **Bloqueante para el merge: ninguno.** OLV-028 es visible para todo usuario pero solo mientras el agente no este
  publicado, o sea en el momento del deploy y hasta que se publique; OLV-029 es cosmetico. Ninguno de los dos toca
  datos, plata ni aislamiento.
- **Lo que no cubrio este lote y hay que mirar antes de liberar:** la pantalla y el 3D, las menciones de
  configuracion y las tarjetas de propuesta (lotes 2 y 3), y el adjunto sin cliente, que es lo que deja CA-T.1 a
  medias.
- **Orden del deploy:** publicar el agente de plataforma **antes** de que el menu lo ofrezca, o arreglar OLV-028
  primero. Si se publica despues, cada miembro va a ver un item muerto en el medio.

### Checklist de merge
- [x] Build limpio (0 errores) y suite de contexto/goldens/chat libre 97/97.
- [x] Sin migracion EF (confirmado: `TipoTarea` cae en la convencion de enums y el snapshot no cambio).
- [x] Aislamiento multi-tenant verificado con dos sesiones reales (404 cross-org en lectura y en escritura).
- [x] Defensa de "solo el autor" verificada en el **servidor** (403), no solo por ausencia del control.
- [x] CA-T.3 verificado en base: 171 hashes de tareas viejas byte a byte identicos.
- [x] Base devuelta a su estado (ver abajo) y `git status --porcelain` del repo del sistema **sin un solo cambio mio**.
- [ ] **OLV-028 y OLV-029 sin arreglar** — vuelven al Implementador.
- [ ] Lotes 2 y 3 (pantalla/menciones/3D y propuestas) pendientes.

### Base devuelta a su estado
Borradas las 5 tareas de la corrida (241 a 245, con la parte 244 **antes** que su padre por la FK
`FK_TareasAgente_TareasAgente_TareaPadreId`) y sus filas colgadas; `EventosUso` 881 a 898 borrados (quedo en 763
filas, max Id 880); `LimitesGastoMiembro` en 0; costos fabricados revertidos; version 147 de vuelta a **Borrador**
con `PublicadaAt = NULL` y su registro de excepcion borrado. `TareasAgente` = **171**, el mismo numero del snapshot
previo. Sin blobs nuevos en `App_Data/documentos` (5 archivos, ninguno de hoy). `.playwright-mcp/` vaciada.

### Reglas cross-proyecto validadas
- Ultima validacion de reglas cross-proyecto: 2026-10-02

# QA M27 — PLAN ESCRITO, SIN EJECUTAR (2026-10-01)

**Estado: el plan está, la corrida no.** 105 casos en tres lotes con 46 regresiones nombradas, escritos por tres
evaluadores independientes durante la auditoría de pre-implementación (criterio Default-FAIL: cada caso arranca en FAIL
y solo pasa con evidencia observada). Lo que SÍ está hecho: `dotnet build` limpio, **1120 tests verdes** y la
verificación en navegador real a 1440 y 390 px en tema claro y oscuro. Lo que NO: la corrida funcional de estos 105.

**El criterio de cierre del módulo está en el lote 2 y no lo puede ejecutar QA:** es la **tarea 17 de producción** con
ocho o más idas y vueltas hasta un resultado, y la prueba la hace Joaquín. Y hoy está bloqueada por algo que no es
código — **PA-45, la clave de la API sin saldo** (la tarea 18 de producción, del 2026-10-01 21:07, quedó `Fallida` con
«Your credit balance is too low»).

**Tres avisos de los evaluadores que cambian el plan y conviene leer antes de ejecutarlo:** (1) `docs/qa/regresiones-manuales.yml`
**no existe en este repo** — el catálogo vive en `C:\Sistemas\Agentes-IA\docs\qa
egresiones-manuales.yml`
(OLV-001..OLV-027), y **OLV-025 es textualmente el problema de los `_ =>`** que M27 arregló; (2) los tests corren sobre
EF InMemory, que **no aplica índices únicos ni valida largos**, así que todo lo que dependa de unicidad o de un
`varchar` se verifica contra MySQL y no con un test verde; (3) para CA-M27-06 hace falta **un `.xls` binario real como
fixture** — el que había eran 24 bytes de firma OLE2, no un libro.

> Tres lotes, como manda la instruccion 39 §5. Se ejecuta DESPUES de la implementacion; el criterio de cierre del lote 2 es la tarea 17 de produccion, que prueba Joaquin.

**Las tablas completas de los 105 casos** —con pasos, esperado y tipo de verificacion por caso— estan en
[`historial/qa-m27-plan-de-casos.md`](historial/qa-m27-plan-de-casos.md): son material de referencia para ejecutar,
no memoria para cargar en cada sesion. Resumen: **lote 1 unificacion de agentes** 37 casos y 15 regresiones ·
**lote 2 motor y conversacion** 35 casos y 14 regresiones (incluye el criterio de cierre: la tarea 17) ·
**lote 3 documentos y menu** 33 casos y 17 regresiones.

---

## Historial de ajustes

### Bloques archivados (2026-10-02)

Movidos a `historial/` para mantener este archivo bajo el techo de 150 KB (`39-presupuesto-contexto.instructions.md`). Se leen solo si el trabajo los toca.

- **M20** — 1 bloques (2026-09-25 a 2026-09-25) → [`6-qa-M20.md`](historial/6-qa-M20.md)
- **M18** — 1 bloques (2026-09-24 a 2026-09-24) → [`6-qa-M18.md`](historial/6-qa-M18.md)
- **M07** — 1 bloques (2026-09-16 a 2026-09-16) → [`6-qa-M07-2.md`](historial/6-qa-M07-2.md)
