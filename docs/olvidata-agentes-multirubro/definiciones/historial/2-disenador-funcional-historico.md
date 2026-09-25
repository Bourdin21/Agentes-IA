<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 2-disenador-funcional - historico (3 bloques archivados)

- M20 — Coprocesador aritmético · M21 — Ojos, segunda mitad (PDF escaneado)
- M18 — Portal del cliente del estudio (rol Cliente)
- M16 — Tablero de actividad al iniciar sesión

---

# M20 — Coprocesador aritmético · M21 — Ojos, segunda mitad (PDF escaneado)

Estado: **Diseño cerrado**. Entrada: `1-analista-funcional.md` M20 (RF-M20-01..09, D-M20-a..e) y M21 (RF-M21-01..07, D-M21-a..d).
Instrucción de pantallas aplicada: `38-diseno-pantallas-portal.instructions.md`.

**Escaneo de reutilización.** Ningún proyecto del historial tiene un evaluador de expresiones ni visión sobre documentos
(los cuatro hits del grep eran falsos positivos: la palabra «calculadora» dentro de un caso de prueba manual de
`marihogar`). El precedente conceptual de M21 es `luciano-inmobiliaria/1-analista-funcional.md` §viabilidad —misma vía
técnica, PDF nativo a Claude sin pipeline de OCR—, sin código. **La reutilización real es interna:** M16 (ojos) aporta el
camino completo de M21, y M19 (la impresora) aporta la heurística de «número escrito por una persona» de M20.

## Lo que NO tiene pantalla

**Los dos módulos no agregan una sola pantalla nueva**, y eso es una decisión, no una omisión: lo que agregan es
*capacidad del agente*. Meterle una pantalla de calculadora al portal sería construir la peor calculadora del mercado
para competir con la del sistema operativo. Lo que sí tiene diseño es **cómo se cuenta lo que hizo el agente** y **cómo
se le avisa a la persona lo que va a pasar antes de que pase**. Los dos son los lugares donde este producto se gana o
pierde la confianza.

## M20 — Dónde se ve

| Lugar | Qué muestra | Por qué |
|---|---|---|
| «Ver pasos» de la tarea | `Calculó: neto = 1.234,50 · iva = 259,25 · total = 1.493,75` | La cuenta auditable es la mitad del valor del módulo (D-M20-e). Los números con formato de acá, no con punto decimal |
| Una cuenta que falló | `No pudo hacer una cuenta: no se puede dividir por cero` y las demás igual | Un paso que dice «la herramienta falló» sin decir qué no sirve para nada |
| Ficha del agente (anatomía) | Rótulo llano **«Hacer una cuenta»** — *Resuelve una cuenta con la calculadora del sistema, en vez de escribir el número de memoria* | Es lo único que la persona necesita saber; el nombre técnico no se muestra nunca (PA-12) |
| Manual | Sale del «Qué no hace» y pasa a ser función | Hoy el manual promete lo contrario |

**Regla de redacción del paso:** hasta 5 cuentas se listan; de 6 en adelante, `Calculó 8 cuentas · total = 1.493,75`
(la última con nombre, que es la que suele importar). Una lista de veinte cuentas en el hilo tapa la conversación.

## M21 — Dónde se ve

| Lugar | Antes | Ahora |
|---|---|---|
| Al subir (mensaje de resultado) | «Documento subido, pero el agente no puede leer su contenido» | **«Documento subido. El agente lo puede mirar (escaneado, 12 páginas). Mirarlo cuesta más que leer un PDF con texto.»** |
| Al subir, si pasa el tope | lo mismo, sin motivo | «…no puede leerlo: es un escaneado de 60 páginas y el máximo para mirar es 20.» |
| Estado en el listado y en la ficha | «El agente la mira» (hablaba de imágenes) | «El agente lo mira» + tooltip que nombra el escaneado |
| Pantalla del documento | «Es una imagen: el agente la mira…» | Para un PDF: «Es un PDF escaneado: el agente lo mira cuando se lo pedís en una tarea. No tiene texto para leer.» y el botón **Descargar** que ya está |
| Paso de la tarea | «Miró «Frente.png»» | «Miró «Extracto marzo.pdf» (4 páginas)» |

**Decisión de alcance con motivo (D-M21-e, nueva en diseño):** **no se embebe una vista previa del PDF** en la pantalla
del documento. Embeber pide una acción nueva que sirva el archivo con `Content-Disposition: inline` —o sea, una segunda
puerta al binario—, y el navegador ya abre el PDF descargado. No agrega nada al trabajo del agente, que es de lo que se
trata el módulo.

**El aviso de costo va en el mensaje de la subida, no en un cartel aparte** (§0 de la instrucción 38: lo que la persona
vino a hacer entra en la primera pantalla). Es una oración al final del mensaje que ya existe.

## ViewModels y contratos

**Ninguno nuevo en Web.** Lo que cambia:

- `SubidaDocumentoResultadoDto.Mensaje` — el texto, no la forma.
- `DocumentoListItemDto` / `DocumentoDetalleDto` — sin cambios de forma; cambian los textos que salen de
  `TiposArchivoDocumento.TextoLectura` y `DocumentosTextos.TooltipLectura`, que hoy dicen «imagen» a secas.
- `ResumenHerramientaDto` (ya existe) lleva el paso de M20 y el de M21, como cualquier otra familia.
- Nuevo DTO de Application, no de Web: `CuentaCalculada(string? Nombre, string Expresion, decimal Exacto, decimal Redondeado, int Decimales, string? Error)`.

## Impacto por capa

| Capa | M20 | M21 |
|---|---|---|
| Domain | — | — (el estado `SeMira` ya existe) |
| Application | evaluador puro, helper de número compartido, opciones, mensajes, nombres de herramienta | mensajes de ojos con páginas, textos de lectura |
| Infrastructure | herramienta + resumidor de pasos, registro en DI y en el resolvedor | extractor de PDF, archivos para mirar, proveedor Anthropic (bloque de documento), rehidratado con tope propio |
| Web | rótulo llano en la ficha del agente (tabla de descripciones) | textos de estado y la pantalla del documento |
| Datos | sin cambios, sin migración | sin cambios, sin migración |

## Historias de usuario

- **HU-M20-01.** Como contadora, quiero que el agente resuelva las cuentas con una calculadora y no de memoria, para poder usar el número sin recalcularlo a mano. **CA:** con la herramienta ofrecida, una cuenta de IVA sobre 40 importes da el total exacto al centavo (CA-M20-01, CA-M20-02).
- **HU-M20-02.** Como Directora, quiero ver en «Ver pasos» qué cuenta hizo y con qué números, para auditar de dónde salió el resultado sin abrir nada. **CA:** el paso muestra nombre, expresión y resultado formateado en castellano, y no muestra el nombre de la función ni JSON (CA-M20-05).
- **HU-M20-03.** Como empleado, quiero que una cuenta imposible no me tire la tarea, para no perder el trabajo hecho por un paréntesis mal puesto. **CA:** la cuenta devuelve el motivo en palabras, las demás de la misma llamada se resuelven y la tarea termina bien (CA-M20-04).
- **HU-M21-01.** Como empleada de un estudio, quiero que el agente pueda mirar el extracto escaneado que me mandó el cliente, para no tener que transcribirlo. **CA:** el PDF sube como «lo puede mirar» y en la tarea el agente cita datos que solo están en la imagen del papel (CA-M21-01, CA-M21-02).
- **HU-M21-02.** Como empleada, quiero saber **al subir** si el agente va a poder mirarlo y que me avise que cuesta más, para decidir antes de gastar. **CA:** el mensaje de subida dice el estado, la cantidad de páginas y el aviso de costo; si no entra en los topes, dice por qué (CA-M21-03).
- **HU-M21-03.** Como Directora, quiero que un escaneado enorme no se le mande al agente una y otra vez, para que una tarea no se coma el tope del mes. **CA:** solo los últimos 2 PDF viajan en una conversación; el resto va como una línea de texto (RF-M21-03).

## Riesgos de implementación

- **Los textos de `SeMira` están escritos para imágenes en cuatro lugares** (mensaje de subida, texto de estado, tooltip, pantalla del documento) más el mensaje al modelo. Si se cambia solo uno, el portal se contradice a sí mismo. Se tocan los cinco en el mismo commit.
- **El tope por conversación cuenta bloques, no tipos.** Hoy `RehidratarImagenesAsync` cuenta todas las referencias juntas; con PDFs hace falta distinguirlas o un PDF de 20 páginas desplaza siete fotos (o peor, viaja siete veces). Es el punto más fácil de hacer mal y el más caro.
- **El paso de M20 se arma desde la entrada del modelo**, igual que en M19: si se lee del texto que devolvió la herramienta, cualquier cambio de redacción rompe la pantalla.
- **La heurística de número se comparte con M19.** Al moverla a Application hay que dejar los tests de M19 en verde sin tocarlos: si hay que tocarlos, el movimiento cambió el comportamiento y está mal.
# M18 — Portal del cliente del estudio (rol Cliente)

Estado: **Diseño cerrado**. Entrada: `1-analista-funcional.md` M18 (RF-M18-01..36, D-M18-a..d).
**Diseño completo: `Olvidata Agentes Multi-rubro/docs/diseno-portal-cliente.md`** (11 pantallas, 20 ViewModels,
4 máquinas de estado, 15 historias, 5 riesgos de implementación). Acá quedan solo las decisiones.

**Escaneo de reutilización.** El precedente más cercano del historial es **cma-centro-medico HU-07** (portal de
autogestión del paciente, `PAT-017`): un tercero entra al sistema del cliente y ve solo lo suyo, con un service
dedicado que resuelve el id **desde el usuario autenticado y nunca desde la URL**. Quedó en propuesta, nunca se
implementó: **se toma el criterio, no hay código**. `audifonos-bariloche` lo listó como exclusión; `century-21` dejó
escrito que no hay autoregistro en el estudio — confirma que este flujo es nuevo y por eso se diseña con cuidado.
De este mismo repo se reutiliza entero: el pipeline de documentos de M5, el patrón «el agente propone y nunca crea»
de M4b/M7b, el gasto por miembro de M6 y las reglas de pantalla de la instrucción 38. Patrón nuevo propuesto:
**`PAT-042` — portal de un tercero adentro del tenant del cliente**.

**D-M18-1 — El cliente no es un miembro degradado; es alguien de afuera que entra a un cuarto chico de la casa.**
De ahí sale todo: menú propio, portada propia, service propio y frontera como **lista blanca**.

**D-M18-2 — La frontera sale casi gratis, y el riesgo es arruinarla.** Hoy `EsMiembro` es «tiene tenant y tiene rol»:
agregar `RolOrganizacion.Cliente` sin tocar nada le abriría **los 29 controllers del portal de un saque**. La primera
línea del módulo es que **un cliente no es miembro** (`EsMiembro` excluye el rol Cliente); con eso los controllers
existentes lo rechazan sin tocarlos, y uno nuevo también, aunque nadie se acuerde de M18. Lo que se abre es explícito:
policy `RequirePortalCliente` en los 5 controllers del portal.

**D-M18-3 — Tres capas, no una.** (1) autorización por policy; (2) `IPortalClienteService` como **único** punto de
entrada, que resuelve el `ClienteCarteraId` del contexto y jamás de la URL (anti-IDOR, criterio de cma); (3)
`AppDbContext.FiltroCliente` global sobre `IClienteOwned`, con nombre propio para poder ignorarlo con justificación.
`ClienteCarteraIdActual` es null para todo el mundo salvo un usuario cliente: el estudio y el staff no cambian en nada.

**D-M18-4 — Las garantías del motor no se cumplen en la pantalla.** Una tarea `ConsultaCliente` recibe solo lectura de
su carpeta más `pedido_documentacion_proponer`; **ninguna** herramienta de conector (M11), ninguna de escritura de
configuración, sin búsqueda web; y toda aprobación **escala a Director aunque el autor sea el cliente**. Va en
`ProcesadorTareas` y `IResolvedorHerramientas`, no en una vista.

**D-M18-5 — El código de acceso se dicta por teléfono.** 12 caracteres en 3 grupos, alfabeto sin `0/O` ni `1/I/L`,
`RandomNumberGenerator`, hasheado, un solo uso, vence a los 7 días. Inválido, vencido y usado dan **el mismo** mensaje:
no se confirma qué existe. 5 intentos por IP cada 15 minutos.

**D-M18-6 — Inicio del cliente es una pantalla de arranque, no un tablero.** Tres bloques en orden fijo: lo que te
piden · lo último que subiste · tus consultas. Estado vacío con **una** sola acción (instrucción 38, §4).

**D-M18-7 — «Lo que me piden» es un checklist, no una tabla.** Cinco estados con su acción propia; el motivo de
rechazo escrito por el estudio es lo único que el cliente va a leer para entender qué corregir, así que es obligatorio.

**D-M18-8 — La conversación del cliente es la del portal, recortada.** Columna única y medida de lectura de la
instrucción 38; se sacan «Ver pasos», la barra de costo, el selector de cliente y las tarjetas de propuesta. Con el
límite de gasto alcanzado, el cuadro se deshabilita **sin mostrar un número**.

**D-M18-9 — La propuesta del agente va al estudio, no al cliente.** El agente crea una propuesta Pendiente; al cliente
no le llega nada hasta que una persona toca «Pedírselo al cliente». Mismo patrón, palabra por palabra, de M4b y M7b.

**D-M18-10 — «Lo ve el cliente» pide confirmación al encender y no al apagar.** Encender expone; apagar protege. Y lo
que subió el cliente lo ve siempre, sin interruptor.

**D-M18-11 — Mi ficha edita contacto, no identidad.** Nombre y CUIT/DNI son del estudio: se muestran en gris con
«si esto está mal, avisale a tu estudio».

**D-M18-12 — El portal se habilita por organización y los agentes de a uno, todo apagado por defecto.** Sin eso,
`/acceso` responde 404 y no existe ninguna de estas pantallas.

Riesgos de implementación: **DI-M18-1 (alto)** el cambio de `EsMiembro` toca todo el portal — grepear `RolOrganizacion ==`
antes de empezar · **DI-M18-2 (alto)** hace falta una batería de aislamiento **cliente contra estudio** y **cliente
contra cliente**, controller por controller · **DI-M18-3 (medio)** `FiltroCliente` sobre `Tarea` rompe consultas del
estudio si `ClienteCarteraIdActual` se resuelve mal para un miembro · **DI-M18-4 (medio)** los goldens de hash de
contexto tienen que quedar idénticos · **DI-M18-5 (bajo)** `_LayoutCliente` duplica maqueta.

Decisiones abiertas: **DA-M18-1** un usuario cliente no cuenta como miembro en el plan (decisión comercial antes de
publicar) · **DA-M18-2** aviso por email al cliente, cuando exista el módulo de email.
# M16 — Tablero de actividad al iniciar sesión

Estado: **Diseño cerrado**. Entrada: `1-analista-funcional.md` M16 (RF-M16-01..06).

**D-M16-1 — Tres bloques en orden de urgencia, siempre los tres.** *Ahora* · *Te espera* · *Lo que pasó*. El orden no cambia según haya o no actividad: mover bloques según el estado hace que la pantalla se sienta distinta cada vez y la persona pierde el mapa. Cuando *Ahora* está vacío dice **«No hay nada corriendo en este momento»** y ofrece *Pedir una tarea* — no un espacio en blanco.

**D-M16-2 — El gráfico ilustra, no reemplaza.** Arriba van las listas, que son lo accionable; el gráfico va **al costado en escritorio y abajo en mobile**. Motivo: un diagrama de nodos es lindo para entender el sistema y malo para trabajar. Quien entra apurado necesita «tenés 2 aprobaciones», no una constelación.

**D-M16-3 — Qué dibuja el gráfico.** Nodos: personas, agentes y clientes. Aristas: «pidió» (persona → agente), «le pidió ayuda a» (agente → agente, las partes de M7a) y «trabaja sobre» (agente → cliente). Lo vivo se distingue **con movimiento y con etiqueta**, nunca solo con color. Al tocar un nodo, su detalle y el salto a la pantalla real. Sin actividad viva, dibuja la del día en gris.

**D-M16-4 — Reemplaza Inicio.** `Home/Index` pasa a ser el tablero. El staff de Olvidata, que no tiene organización en sesión, sigue viendo su portada actual con los accesos del backoffice: no se le inventa un tablero vacío.

**D-M16-5 — En vivo con respaldo.** SignalR empuja los cambios (ya existe `TareasHub` con su grupo por tarea; acá hace falta un grupo **por organización**). Si el socket no conecta, sondeo cada 15 s. **Sin JavaScript la pantalla igual renderiza los tres bloques**, servidos por el servidor: el tablero es HTML con mejoras, no una aplicación de página única.

**D-M16-6 — Qué NO se muestra.** Ni el texto del pedido, ni el de la respuesta, ni los documentos. El tablero dice **qué** está pasando y **entre quiénes**. Para el contenido se entra a la tarea, que ya tiene sus permisos.

**D-M16-7 — Vocabulario.** «Ahora», «Te espera», «Lo que pasó». En las aristas, el mismo criterio de M7a: **«le pidió ayuda a»**, nunca «delegó» ni «subagente». Los estados con ícono y texto, por los helpers que ya existen.

Pantallas: **P-M16-01 Tablero** (`Home/Index`, todo miembro) con los tres bloques y el gráfico · **P-M16-02** ajuste del layout, porque *Inicio* pasa a llamarse **Tablero** en el menú.

Riesgos de diseño: **R-M16-05 — el gráfico con muchos nodos se vuelve ilegible**: tope de nodos y agrupar el resto en «y N más». **R-M16-06 — el movimiento molesta**: respetar `prefers-reduced-motion`. **R-M16-07 — «Lo que pasó» se puede leer como vigilancia** de un Director sobre su equipo: se muestra por agente y por cliente, **no un ranking de personas**.
