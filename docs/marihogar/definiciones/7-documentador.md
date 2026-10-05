# Memoria - Documentador

## Proyecto: marihogar
## Ultima actualizacion: 2026-10-02

## Definiciones vigentes

### Alcance entregado al cliente

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
- 2026-10-02: Resumen de CR-86 redactado y entregado (`resumen-cr86-2026-10-02.md`), formato `31-formato-documento-cliente.instructions.md` completo. Decision de redaccion: el aviso de los 3 cheques que cambian de mes por $1.452.133,30 va en **`## Lo que necesitamos de tu parte`**, no escondido en pendientes, porque es lo unico del sprint que le mueve un numero ya cerrado — y con la frase de que "no es plata nueva, es la misma plata quedando en el mes en que de verdad salio", para que no se lea como un error del sistema. Tambien se comunico el **cambio de procedimiento** (al acreditar un cheque hay que poner la fecha del extracto, no la de hoy): es un paso nuevo para el usuario y sin el, todo lo demas queda mal fechado. No se comunico nada como aplicado: la actualizacion no esta desplegada y el backfill no se corrio.
- 2026-07-28: Guía técnica `certificado-afip.md` redactada — trámite paso a paso (portal AFIP + OpenSSL) para obtener el `.p12` real del negocio, adaptada del template del estudio (`docs/templates/afip-certificado-digital.md`) y del precedente ya ejecutado en `delicias-naturales/certificado-afip.md`. No es un documento de cara al cliente con el formato de marca (`31-formato-documento-cliente.instructions.md`) — es una guía operativa interna/técnica, a pedido explícito del usuario, para acompañar al cliente en el trámite. Datos del CUIT/alias reales del negocio quedan pendientes de completar cuando el cliente los provea. `.gitignore` del repo actualizado (`*.p12`/`Certificados/`) para que el certificado nunca se suba a git.
- 2026-07-24: Documento de cierre de Etapa 1 completa redactado y entregado (`resumen-etapa1-2026-07-24.md`), cubriendo los 6 sprints/16 modulos con QA en GO. Formato `31-formato-documento-cliente.instructions.md` aplicado completo.
- 2026-07-24: Manual de usuario redactado y entregado (`manual-usuario-2026-07-24.md`). Estructura de manual (indice + 1 seccion por modulo) en vez de resumen de sprint, a pedido explicito del cliente — se mantuvo el encabezado de marca, tono voseo y pie de firma de `31-formato-documento-cliente.instructions.md`, pero no la restriccion de "media pagina" (no aplica a un manual de uso completo). Fuente: `5-implementador.md`/`6-qa.md` (los 6 sprints, solo lo validado) para el contenido funcional, y el sidebar real de `Views/Shared/_Layout.cshtml` para los nombres exactos de menu (Principal/Administracion/Ventas/Compras/Financiero/Catalogo/Super Usuario) y su agrupacion por rol. Diferenciacion Administrador/Vendedor explicita en tabla al inicio. Incluye seccion final de pendientes (certificado ARCA, checklists manuales) igual que el resumen de Etapa 1.
