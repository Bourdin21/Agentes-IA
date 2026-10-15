# Memoria - Documentador

## Proyecto: marihogar
## Ultima actualizacion: 2026-10-02

## Definiciones vigentes

### Alcance entregado al cliente

**Cierre de septiembre y octubre — ventas y compras (2026-10-15)** — pagina navegable, instruccion 41.

**URL: https://claude.ai/artifact/QtmKxjbNLUe7k6DyZ9GEwx** — *las proximas versiones se republican SOBRE ESTA MISMA URL*.

Responde "donde quedo la plata". Verificado contra produccion: ventas y OC no anuladas del 01/09 al 13/10 (43 dias), gastos no anulados, stock valorizado a PrecioCompra. **Ningun numero sale de los docs ni de memoria.**

**Decision de redaccion:** el titular no es el resultado sino su causa. Decir "ganaste $136.786 sobre $23,5M" invita a discutir si los gastos estan bien imputados; decir "compraste $16,99M y vendiste $11,96M a costo" senala donde esta la plata y es incontestable. El resultado va igual, en la primera tabla, con el desglose completo.

**Lo que el informe pone en primer plano, por orden de plata:** $13,1M de stock dormido (88 productos sin una unidad vendida en 43 dias, el 65% del inventario), compras 42% por encima de las ventas a costo, $4,98M comprado en el periodo que todavia no movio nada, y recien al final el costo de cobranza ($2,08M, 15 veces el resultado). **El orden es deliberado**: el trabajo de los dias anteriores fue sobre cobranza, y era la palanca mas chica de las tres.

**El dato que corrige una lectura facil:** la cobertura general de 73 dias parece sobrestock, pero mirando solo lo que rota son **26 dias**, con 166 productos bajo minimo. El negocio no esta sobrestockeado, esta mal stockeado — y por eso la recomendacion no es "comprar menos" sino "comprar otra cosa".

**Tres salvedades declaradas, cada una con de que depende:** el resultado depende de que los gastos del periodo esten bien imputados; "no vendio en 43 dias" puede ser estacionalidad o mercaderia recien llegada y hay que mirar producto por producto antes de liquidar; y la deuda de $11,7M es solo la de las OC del periodo, sin saldos anteriores.

**Informe de medios de pago (2026-10-15)** — entregable publicado como **pagina navegable** (instruccion 41, skill `documento-navegable-cliente`):

**URL: https://claude.ai/artifact/UnKcoPVRcaqrxDBdDyx2Yq** — *la proxima version se republica SOBRE ESTA MISMA URL*. Un link nuevo deja al cliente leyendo la version vieja.

**Version 2 (2026-10-15), republicada sobre la misma URL.** El cliente aporto el panel completo de Mercado Pago y el dato del adelanto (6,03%), y eso corrigio la conclusion principal: los $458.855 no son el ahorro de cambiar de terminal sino el de DOS decisiones — **$275.927 dejar de adelantar + $182.927 cambiar de terminal** —, y cambiar de terminal sin dejar de adelantar da **$0**. La correccion se declara dentro del propio informe en vez de reescribirla en silencio: el cliente leyo la version 1 y el numero que recordaba cambio de significado.

Fuente editable (Claude Docs, misma bajada y mismas tablas): https://claude.ai/code/artifact/369fcc07-8a40-4951-9241-2d249a41b91d

Responde "que medio de pago conviene y cual no". Contenido verificado contra produccion (regla 0): los porcentajes salen de `TasasCostoCobranza` y `ConfiguracionesCuotaTarjeta` vigentes al 15/10/2026, el volumen de `PagosVenta` desde el 01/09, y el recargo de lista (21,07%) del promedio de los 230 productos con los dos precios cargados. **No lleva capturas**: es un informe de numeros, no un manual de uso, asi que el envoltorio usa `.vidrio-claro` sobre fondo oscuro plano y no `.vidrio` (que es para capturas, que son claras).

**Decision de redaccion:** el titular es el hallazgo con plata, no el tema. Las cuotas se estan cobrando por Payway cuando Mercado Pago sale 7,67 puntos mas barato en 6 cuotas: **$458.855** sobre el volumen de septiembre-octubre. Abre con eso porque es lo unico del informe sobre lo que hay que hacer algo manana, y el resto de la tabla es contexto para entenderlo. El segundo hallazgo (la tarjeta de debito deja ~5% menos que el efectivo, porque cobra precio de contado y tiene costo) va despues y explicitamente rotulado como **decision comercial, no defecto del sistema** — la regla de precio de debito esta acordada con el cliente.

**Lo declarado como no contemplado**, cada uno con de que depende: el plazo de acreditacion (MP a 21 dias contra Payway en dias, que puede dar vuelta la recomendacion si el capital de trabajo esta justo — se declara porque sin eso el informe recomendaria a ciegas), el 18,61% de Payway en 6 cuotas como unico numero estimado, la cuenta de Oscar sin arancel, el IVA de la comision sin computar como credito fiscal, y prepaga/credito del exterior sin configurar.

**MH-055 a MH-059 (2026-10-14)** — resumen entregado en `docs/marihogar/resumen-mh055-2026-10-14.md`: el costo de cobranza pasa a calcularse con la estructura impositiva real (tres bases distintas), las tasas de Payway quedan abiertas por concepto (arancel, plan MiPyME, cobro anticipado) y se cargan los recargos por cuotas que cubren el costo. Comunicado con los numeros: 6 cuotas 25% -> 37%, 9 cuotas 0% -> 34%, 12 cuotas 0% -> 43%, y los dos recalculos pendientes (octubre $43.340,87, septiembre $214.048,79). **Decision de redaccion:** el documento abre reconociendo que el sistema estaba calculando mal y mostrando los dos numeros enfrentados ($104.695 calculado contra $133.355 reales), porque el cliente ya vio el sintoma y empezar por otro lado se leeria como esquivarlo. Los recargos nuevos llevan la explicacion de **por que el recargo es mas alto que el costo** (se cobra sobre el precio ya recargado): sin eso, un 43% al lado de un costo de 30% parece un error de cuenta. Se incluye la tabla de las cinco verificaciones contra comprobantes reales, que es lo que sostiene todo lo demas. Declarado fuera de alcance: el IVA de la comision como credito fiscal, la segunda cuenta de MP sin tasa, y que el costo de 6 cuotas de octubre es el unico numero estimado y no medido.

**CR-86 (2026-10-02)** — resumen entregado en `docs/marihogar/resumen-cr86-2026-10-02.md`: pantalla de Costos de cobranza con filtro de periodo y totales por plataforma; impuesto al cheque (Ley 25.413, 0,600%) registrado automaticamente como gasto al acreditar; la acreditacion de un cheque ahora **pide la fecha del extracto** (cambio de procedimiento para el cliente); pantalla de regularizacion de los cheques ya acreditados; y reporte de gastos superpuestos de solo lectura. Comunicado con los numeros: 19 cheques de septiembre = $39.719,67 al regularizar, 16 pendientes = $41.522,56 al acreditarse, 10 de agosto afuera. **Reescrito el 02/10 tras la decision del cliente de no tocar las fechas de los cheques ya cargados:** el documento ya no le pide correr la regularizacion de fechas ni le avisa de los 3 cheques que cambiaban de mes; ahora le pide registrar **solo el impuesto de septiembre**, aclarando que "no toca ningun dato de los cheques". Los 3 cheques por **$1.452.133,30** que quedan en un mes distinto del que el banco los debito pasaron a `## Lo que no esta incluido`, redactados como decision suya y con la aclaracion de que **de aca en adelante no vuelve a pasar** porque la fecha la carga el. Declarado fuera de alcance en lenguaje llano: impuesto al credito ($45.064,72 en septiembre), impuesto al debito de no-cheques, ARBA, Sellos, y que **la caja todavia no va a cuadrar peso por peso** con el extracto.

Etapa 1 completa (16 modulos, 6 sprints de implementacion, todos con QA en GO): Usuarios y roles, Catalogo de productos, Control de stock, Presupuestos y cotizaciones, Gestion de ventas (pantalla POS elevada), Entregas a domicilio, Cuenta corriente del local, Compras a proveedores, Cuenta corriente de proveedores, Cheques 30/60/90, Caja mensual, Gastos del negocio, Panel de metricas y dashboard, Aumento masivo de precios, Proyeccion financiera, Facturacion electronica AFIP/ARCA. Documentos entregados: `docs/marihogar/resumen-etapa1-2026-07-24.md` (resumen ejecutivo de cierre) y `docs/marihogar/manual-usuario-2026-07-24.md` (manual de uso paso a paso, 15 secciones, una por modulo/flujo, con tabla de accesos por rol — no incluye el modulo "Super Usuario" del sidebar, reservado para uso interno del proveedor por regla vigente). Sistema ya desplegado en produccion: `http://olvidatasoft-002-site16.jtempurl.com/`.

### Pendientes o fuera de alcance

- Etapa 2 (CRM de Leads + Bot WhatsApp) en pausa por decision explicita del cliente (2026-07-24) — no comunicada como "entregada", queda fuera de este resumen salvo la mencion de que sigue pendiente de arranque.
- Certificado digital ARCA (.p12) del cliente — dependencia externa ya documentada desde el analisis funcional. Facturacion AFIP queda en modo homologacion (pruebas) hasta recibirlo.
- 5 checklists de verificacion manual acumuladas (Sprints 2 a 6, ~50 pasos totales) sin ejecutar por el usuario — comunicado como pendiente de su parte antes de dar la Etapa 1 por definitivamente cerrada en produccion.

### Beneficios comunicados

Reemplazo completo de Contagram, automatizacion de stock/CC/caja (sin carga manual duplicada), proyeccion financiera para anticipar la caja, pantalla de ventas rapida para el mostrador, roles diferenciados Administrador/Vendedor.

### Proximo paso sugerido

Que el cliente recorra las checklists de verificacion manual (ofrecida sesion conjunta), gestione el certificado ARCA, y confirme cuando quiere retomar Etapa 2.

### Nota de transparencia incluida

Se comunico al cliente, en lenguaje simple y sin alarmar, el incidente de proceso de Sprint 5 (colision de dos ejecuciones paralelas del implementador, ya investigado y descartado como riesgo real) — decision de incluirlo por regla de transparencia del estudio, aclarando explicitamente que no requiere accion de su parte.

## Historial de ajustes
- 2026-10-02: Resumen de CR-86 **reescrito** tras la decision del cliente de dejar las fechas de los cheques como estan. Cambio de fondo en el documento: lo que era una **accion pedida** ("corre la regularizacion, mueve 3 cheques de mes") paso a ser una **limitacion declarada** (esos 3 cheques quedan en el mes equivocado, por tu decision, y no vuelve a pasar de aca en adelante). Se mantuvo el pedido de registrar el impuesto de septiembre, con la aclaracion explicita de que no toca ningun dato de los cheques — la distincion importa porque es justo lo que el cliente pidio preservar.
- 2026-10-15: Informe de medios de pago publicado como pagina navegable (instruccion 41). **Es el primer entregable del proyecto que nace como pagina y no como `.md`**, asi que fija el precedente: la URL queda anotada arriba y las proximas versiones se republican sobre ella. Decision de formato: el mismo contenido vive ademas como doc editable, porque es material que el cliente va a querer ajustar (los recargos son precio, y el precio lo decide el). La pagina es la copia de lectura; el doc, la fuente que se discute.

- 2026-10-14: Resumen de MH-055/059 redactado y entregado (`resumen-mh055-2026-10-14.md`), formato `31-formato-documento-cliente.instructions.md` completo. Decision de redaccion: se comunica como **correccion**, no como mejora — el cliente reporto el sintoma y el documento lo nombra en el primer parrafo. Los dos recalculos van en `## Lo que necesito de tu parte` con los importes, y el de septiembre explicitamente como **decision suya** por tratarse de un mes cerrado. Se comunico como aplicado lo que efectivamente esta en produccion (tasas, recargos, estructura) y como pendiente lo que no se corrio (los dos recalculos).

- 2026-10-02: Resumen de CR-86 redactado y entregado (`resumen-cr86-2026-10-02.md`), formato `31-formato-documento-cliente.instructions.md` completo. Decision de redaccion: el aviso de los 3 cheques que cambian de mes por $1.452.133,30 va en **`## Lo que necesitamos de tu parte`**, no escondido en pendientes, porque es lo unico del sprint que le mueve un numero ya cerrado — y con la frase de que "no es plata nueva, es la misma plata quedando en el mes en que de verdad salio", para que no se lea como un error del sistema. Tambien se comunico el **cambio de procedimiento** (al acreditar un cheque hay que poner la fecha del extracto, no la de hoy): es un paso nuevo para el usuario y sin el, todo lo demas queda mal fechado. No se comunico nada como aplicado: la actualizacion no esta desplegada y el backfill no se corrio.
- 2026-07-28: Guía técnica `certificado-afip.md` redactada — trámite paso a paso (portal AFIP + OpenSSL) para obtener el `.p12` real del negocio, adaptada del template del estudio (`docs/templates/afip-certificado-digital.md`) y del precedente ya ejecutado en `delicias-naturales/certificado-afip.md`. No es un documento de cara al cliente con el formato de marca (`31-formato-documento-cliente.instructions.md`) — es una guía operativa interna/técnica, a pedido explícito del usuario, para acompañar al cliente en el trámite. Datos del CUIT/alias reales del negocio quedan pendientes de completar cuando el cliente los provea. `.gitignore` del repo actualizado (`*.p12`/`Certificados/`) para que el certificado nunca se suba a git.
- 2026-07-24: Documento de cierre de Etapa 1 completa redactado y entregado (`resumen-etapa1-2026-07-24.md`), cubriendo los 6 sprints/16 modulos con QA en GO. Formato `31-formato-documento-cliente.instructions.md` aplicado completo.
- 2026-07-24: Manual de usuario redactado y entregado (`manual-usuario-2026-07-24.md`). Estructura de manual (indice + 1 seccion por modulo) en vez de resumen de sprint, a pedido explicito del cliente — se mantuvo el encabezado de marca, tono voseo y pie de firma de `31-formato-documento-cliente.instructions.md`, pero no la restriccion de "media pagina" (no aplica a un manual de uso completo). Fuente: `5-implementador.md`/`6-qa.md` (los 6 sprints, solo lo validado) para el contenido funcional, y el sidebar real de `Views/Shared/_Layout.cshtml` para los nombres exactos de menu (Principal/Administracion/Ventas/Compras/Financiero/Catalogo/Super Usuario) y su agrupacion por rol. Diferenciacion Administrador/Vendedor explicita en tabla al inicio. Incluye seccion final de pendientes (certificado ARCA, checklists manuales) igual que el resumen de Etapa 1.
