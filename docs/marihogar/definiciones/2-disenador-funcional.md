# Memoria - Disenador funcional

## Proyecto: marihogar
## Ultima actualizacion: 2026-08-16

## Definiciones vigentes

> Nota de consolidación (2026-08-16): las 8 secciones "Diseño v2" a "v9" (antes de nivel 2, apiladas por fecha de Change Request) pasaron a subsecciones de este único bloque — contenido sin resumir, ver `## Historial de ajustes` para el resumen de una línea por versión.

### Alcance funcional resumido

18 modulos sobre analisis funcional v2 cerrado (`1-analista-funcional.md`). Etapa 1 (16 modulos, operacion completa) + Etapa 2 (2 modulos, CRM + bot WhatsApp). Roles: Administrador (acceso total) y Vendedor (contactos, presupuestos, ventas, entregas, facturacion — sin costos/compras/financiero/config). Requisitos transversales del cliente para esta ejecucion: casos de uso + casos de prueba por modulo (cubierto en Historias de usuario abajo, QA los materializa como casos de prueba en etapa 6), UX optimizada, filtros de listados persistidos en sesion, formularios verificados al 100%.

### Patron transversal — Filtros de listado persistidos en sesion

Aplica a **todo** listado DataTables server-side del sistema (regla obligatoria, no opcional por modulo):
- Cada filtro de columna (texto, select/Select2, daterangepicker) se guarda en `Session` bajo una clave por pantalla: `Filtros:<Controller>:<Accion>` (ej. `Filtros:Productos:Index`).
- Al enviar el filtro (submit AJAX de DataTables), el Controller persiste el `DataTableRequest` completo (o el subset de filtros) en `Session` antes de resolver el query.
- Al reingresar a la pantalla (`GET Index`), el Controller lee la `Session`, si existe la reinyecta en el ViewModel inicial para que los controles de filtro carguen con el valor previo y el primer draw de DataTables ya salga filtrado.
- Boton "Limpiar filtros" visible junto a los filtros: limpia los controles + la clave de `Session` asociada + recarga el grid sin filtro.
- Session timeout ya definido en `23-web.instructions.md` (60 min) — al expirar, el listado vuelve a estado sin filtro (comportamiento esperado, no requiere manejo especial).
- Esto afecta a los listados de: Productos, Stock (movimientos), Leads, Presupuestos, Ventas, Entregas, Comprobantes AFIP, Movimientos CC local, Proveedores, Ordenes de compra, Movimientos CC proveedor, Cheques, Gastos, Usuarios.

### Historias de usuario

Formato: "Como `<rol>`, quiero `<accion>` para `<beneficio>`." Agrupadas por modulo. Los criterios de aceptacion (CA) referencian los ya definidos en `1-analista-funcional.md` cuando existen (CA-N#) y agregan los especificos de UI/flujo de pantalla.

#### M10 — Usuarios y roles *(base ya bootstrapeada por template BlankProject — ver Arquitectura)*
- HU-10.1: Como Administrador, quiero dar de alta un usuario con rol Administrador o Vendedor para que cada persona del equipo tenga el acceso que le corresponde.
  - CA: el formulario de alta exige rol; sin rol seleccionado no permite guardar; el usuario nuevo recibe email de bienvenida (ya resuelto por template).
- HU-10.2: Como Administrador, quiero editar o bloquear un usuario para revocarle el acceso cuando deja de trabajar en el negocio.
  - CA: bloquear un usuario le impide loguear (ya resuelto — `EstadoUsuario.Bloqueado`); no se puede bloquear al propio usuario logueado.
- HU-10.3: Como Vendedor, quiero que el menu lateral solo me muestre las secciones a las que tengo acceso para no confundirme con opciones que no puedo usar.
  - CA: sidebar renderiza items condicionados por policy/rol; acceso directo por URL a una seccion no autorizada devuelve 403 (AccessDenied).

#### M2 — Catalogo de productos
- HU-2.1: Como Administrador, quiero cargar un producto con nombre, descripcion, precio de compra, precio de venta, marca, modelo, categoria y stock minimo para tenerlo disponible en presupuestos y ventas.
  - CA: precio de venta no puede ser menor al precio de compra sin confirmacion explicita (warning, no bloqueo — margen negativo es decision del negocio); stock minimo >= 0.
- HU-2.2: Como Administrador, quiero subir hasta 5 fotos por producto para que el vendedor las use al armar presupuestos y el catalogo sea visual.
  - CA: limite duro de 5 fotos, mensaje claro al intentar subir la 6ta; primera foto cargada es la portada por defecto, reordenable.
- HU-2.3: Como Vendedor, quiero buscar productos por nombre, marca, modelo o categoria para armar un presupuesto rapido.
  - CA: listado con filtro por cada columna visible (nombre, marca, modelo, categoria, stock, precio venta), filtros persistidos en sesion.
- HU-2.4: Como Administrador, quiero dar de baja (softdelete) un producto discontinuado sin perder su historial en ventas/compras pasadas.
  - CA: producto softdeleted no aparece en combos de alta de presupuesto/OC nuevos, pero sigue visible en el detalle de ventas/OCs historicas ya emitidas.

#### M3 — Control de stock
- HU-3.1: Como Administrador, quiero ver el stock actual de cada producto y su historial de movimientos (venta, compra, ajuste) para auditar variaciones.
  - CA: listado de movimientos con filtro por producto, tipo de movimiento y rango de fecha; cada movimiento muestra cantidad, tipo, origen (venta/OC/ajuste) y usuario.
- HU-3.2: Como Administrador, quiero registrar un ajuste manual de stock (positivo o negativo) con motivo para corregir diferencias de inventario fisico.
  - CA: ajuste exige motivo obligatorio (texto libre); no permite dejar el stock en negativo salvo confirmacion explicita con warning.
- HU-3.3: Como Administrador o Vendedor, quiero ver una alerta visual en el dashboard y en el listado de productos cuando el stock cae debajo del minimo configurado para reponer a tiempo.
  - CA: badge/color distintivo (rojo) en la fila del producto y contador en el dashboard; el Vendedor ve la alerta pero no puede ajustar stock (solo lectura).
- HU-3.4 (sistema): Como sistema, quiero descontar stock automaticamente al confirmar una venta e incrementarlo al recibir una OC para que el stock refleje la realidad sin intervencion manual.
  - CA: transaccion atomica venta+movimiento de stock (o OC+movimiento); si falla el movimiento de stock, la venta/recepcion no se confirma.

#### M4 — Presupuestos y cotizaciones
- HU-4.1: Como Vendedor, quiero armar un presupuesto eligiendo productos y cantidades para que el sistema calcule el total automaticamente.
  - CA: al agregar una linea se recalcula el total sin recargar pantalla (AJAX/Alpine.js); valida stock disponible informativamente (no bloquea presupuestar sin stock, solo advierte).
- HU-4.2: Como Vendedor, quiero generar el PDF del presupuesto para enviarlo al cliente por WhatsApp o email.
  - CA: PDF incluye datos del negocio, items, cantidades, precios unitarios, total y vigencia; boton "Descargar PDF" disponible desde el detalle del presupuesto en cualquier estado.
- HU-4.3: Como Vendedor, quiero convertir un presupuesto aprobado en venta con un clic sin volver a cargar los productos para agilizar el cierre.
  - CA: boton "Convertir a venta" solo visible en estado Aprobado; la venta creada hereda items/cantidades/precios del presupuesto; el presupuesto pasa a estado Convertido y queda inmutable.
- HU-4.4: Como Vendedor, quiero marcar un presupuesto como Rechazado o dejar que expire para llevar registro de conversion.
  - CA: presupuesto sin respuesta despues de N dias configurables pasa a Expirado (regla de negocio, no requiere job — se calcula al leer/listar); Rechazado requiere motivo opcional.

#### M5 — Gestion de ventas ⭐ pantalla prioritaria del sistema (ver spec elevada dedicada abajo)

La pantalla de Ventas es la de mayor uso diario de todo el sistema (el vendedor la abre decenas de veces por dia) — por pedido explicito del cliente, este modulo recibe un nivel de inversion UX/UI superior al resto de los ABMs. Ver seccion **"Especificacion UX elevada — Pantalla de Ventas"** mas abajo para el detalle completo de interaccion; las historias de usuario funcionales originales se mantienen y se amplian con las de experiencia:

- HU-5.1: Como Vendedor, quiero registrar una venta con productos, cantidades y una o mas formas de pago combinadas (efectivo + transferencia + MercadoPago) para reflejar como pago realmente el cliente.
  - CA: suma de pagos debe igualar el total de la venta para poder confirmarla como Pagada; permite guardar como Pendiente/Pagada parcialmente si la suma es menor.
- HU-5.2: Como sistema, quiero generar automaticamente un movimiento de ingreso en la cuenta corriente del local al confirmar una venta (CA-N1) para no depender de carga manual.
  - CA: el movimiento CC se genera en la misma transaccion que la confirmacion de venta; si la venta se cancela, se revierte con un movimiento de reversion (nunca se borra el original, por trazabilidad).
- HU-5.3: Como Administrador, quiero ver el listado de ventas con filtro por estado, vendedor, forma de pago y rango de fecha para controlar la operacion diaria.
  - CA: filtros persistidos en sesion; Vendedor ve solo sus propias ventas o todas segun policy (a confirmar en Arquitectura — por defecto Vendedor ve todas para poder retomar leads de otros).
- HU-5.4: Como Vendedor, quiero cancelar una venta antes de que tenga entrega/factura asociada para corregir un error de carga.
  - CA: cancelar una venta con entrega o comprobante AFIP emitido esta bloqueado — debe primero anular esos registros o pedir soporte al Administrador; cancelar revierte el movimiento de stock y CC.
- HU-5.5: Como Vendedor, quiero buscar y agregar productos a la venta escribiendo el nombre/marca/modelo sin salir de la pantalla ni recargar, para armar una venta completa en menos de un minuto en el mostrador.
  - CA: buscador con resultados en <300ms percibidos (debounce + indice por nombre/marca/modelo), cada resultado muestra foto miniatura, precio y stock disponible; Enter sobre el resultado resaltado agrega la linea sin usar el mouse.
- HU-5.6: Como Vendedor, quiero ver el total de la venta actualizado en todo momento en una zona fija de la pantalla (sin tener que scrollear hasta abajo) para saber en cualquier momento cuanto le tengo que cobrar al cliente.
  - CA: panel de resumen (carrito) fijo/sticky en desktop y tablet; en mobile se comporta como barra inferior fija con el total y boton de continuar.
- HU-5.7: Como Vendedor, quiero corregir la cantidad o quitar una linea de la venta sin recargar la pantalla ni perder el resto de lo cargado, para no tener que rearmar todo si me equivoco.
  - CA: edicion de cantidad inline con steppers +/- y input numerico; quitar linea con confirmacion liviana (no SweetAlert2 bloqueante — un boton "Deshacer" tipo toast alcanza, no es una accion irreversible hasta confirmar la venta).
- HU-5.8: Como Vendedor, quiero que el sistema me avise si estoy por vender mas cantidad de la que hay en stock, sin impedirme completar la venta si igual quiero hacerlo (ej. venta contra pedido a proveedor), para no perder una venta real por una regla demasiado rigida.
  - CA: badge de advertencia en la linea (no bloqueante) cuando cantidad > stock disponible; el bloqueo real de stock negativo sigue existiendo solo en el ajuste manual (M3), no en la venta.
- HU-5.9: Como Vendedor, quiero que al confirmar la venta la pantalla me ofrezca inmediatamente las acciones siguientes tipicas (nueva venta, ver comprobante, programar entrega, facturar) para no tener que navegar buscando que hacer despues de cobrar.
  - CA: pantalla de exito post-confirmacion con esas 4 acciones como botones grandes, ademas del acceso normal al detalle de la venta.

### Especificacion UX elevada — Pantalla de Ventas (ABM prioritario)

Nivel de exigencia: esta pantalla no se disena como "un ABM mas" — es el equivalente funcional a un punto de venta (POS) profesional. Se aplica el mismo criterio de diseñador senior del resto del sistema (`25-frontend-design-system.instructions.md`) pero llevado a un estandar mas alto de pulido, velocidad percibida y tolerancia a error del operador. Referencia de calidad: experiencia tipo POS moderno (busqueda instantanea + carrito persistente + cobro rapido), no un formulario largo de carga secuencial.

**Layout (desktop/tablet — el uso real es mayormente mostrador):**
- Dos columnas. Izquierda (ancha, ~65%): buscador de productos arriba (autocomplete Select2 con foto+precio+stock por resultado) + grilla/lista de items agregados a la venta, cada fila con foto miniatura, nombre, precio unitario, stepper de cantidad, subtotal y boton quitar.
- Derecha (angosta, ~35%, columna fija/sticky mientras la izquierda scrollea): card "Resumen de venta" con cantidad de items, total en tipografia grande (es el dato mas importante de la pantalla, maxima jerarquia visual), seccion de formas de pago (filas dinamicas metodo+monto, indicador de "falta cobrar $X" o "vuelto $X" en vivo), boton primario "Confirmar venta" grande, deshabilitado hasta que la suma de pagos sea valida segun el estado buscado.

**Layout (mobile — reutilizado para cobro en destino de Entregas, M6):**
- Una columna, mismo orden de prioridad: buscador arriba, lista de items en el medio (scrolleable), barra inferior fija con total + boton "Confirmar venta" (siempre visible sin scrollear, patron checkout mobile estandar).

**Interacciones clave (lo que separa esta pantalla de un ABM generico):**
- Agregar producto: buscar -> flechas o mouse para resaltar resultado -> Enter/click agrega con cantidad 1 -> foco vuelve automaticamente al buscador para seguir agregando sin clicks intermedios. Flujo pensado para cargar una venta de 5-6 items en menos de 30 segundos.
- Recalculo de totales: solo se actualiza el nodo DOM de la fila y del total afectados (nunca re-renderizar toda la tabla — ver regla `32-estandares-qa-implementador.instructions.md` REG-008 de no perder foco/no destruir el contenedor completo).
- Formas de pago: botones de acceso rapido para los 2-3 combos mas frecuentes (ej. "Todo efectivo", "Todo transferencia") que autocompletan el monto con el total, ademas del alta de filas manual para pagos combinados. El indicador de saldo pendiente/vuelto se recalcula en cada tecla, sin submit.
- Feedback de stock: badge de advertencia (no error) en la linea cuando la cantidad supera el stock disponible — informativo, nunca bloquea el flujo de venta (HU-5.8).
- Estados vacios: buscador sin resultados muestra mensaje claro + opcion de crear producto rapido si el usuario es Administrador (accion secundaria, no interrumpe el flujo del Vendedor).
- Confirmacion: la accion de confirmar venta es la unica accion primaria de toda la pantalla — todo lo demas (quitar linea, editar cantidad) es secundario y visualmente mas liviano.
- Pantalla de exito: tras confirmar, reemplaza el contenido (no un modal que tapa todo) con check visual + resumen breve + las 4 acciones siguientes de HU-5.9, para que el vendedor pueda encadenar la proxima venta sin fricción.
- Performance percibida: toda accion dentro del armado de la venta (agregar item, cambiar cantidad, cambiar forma de pago) debe sentirse instantanea (sin spinner de pagina completa); el unico punto donde un loading state es aceptable es el submit final de "Confirmar venta" (con boton en estado disabled+spinner mientras se procesa la transaccion de stock+CC en el servidor).

**Este nivel de detalle es especifico de Ventas.** El resto de los ABMs del sistema siguen el estandar general de `25-frontend-design-system.instructions.md` (cards, DataTables+filtros, jerarquia titulo/acciones) sin necesidad de esta inversion adicional — la priorizacion de esfuerzo en Ventas es una decision explicita del cliente por ser la pantalla de mayor uso diario.

#### M6 — Entregas a domicilio
- HU-6.1: Como Vendedor, quiero programar una entrega con direccion, fecha y vendedor asignado para coordinar la logistica de reparto.
  - CA: entrega solo se puede crear desde una venta confirmada; direccion obligatoria; fecha no puede ser anterior a hoy.
- HU-6.2: Como Vendedor, quiero abrir la entrega desde el celular en el domicilio del cliente, registrar el cobro (si quedaba pendiente) y cerrarla para dejar todo asentado en el momento.
  - CA: vista de entrega mobile-first (botones grandes, minimo scroll); registrar cobro en destino genera el mismo flujo de PagoVenta que en el local.
- HU-6.3: Como Vendedor, quiero marcar una entrega como "No entregada" y reagendarla si el cliente no estaba para recibir el pedido.
  - CA: motivo obligatorio; reagendar exige nueva fecha; historial de intentos visible en el detalle de la entrega.

#### M7 — Facturacion electronica AFIP/ARCA
- HU-7.1: Como Vendedor, quiero elegir que items y cantidades de una venta facturar (todo, parte, o un solo item) para adaptarme a lo que el cliente necesita facturado.
  - CA: pantalla de seleccion muestra items de la venta con checkbox + cantidad editable (no mayor a la cantidad vendida no facturada aun); permite facturar en mas de un comprobante la misma venta (facturacion parcial acumulativa).
- HU-7.2: Como Vendedor, quiero elegir tipo de comprobante (Factura A o B) segun la condicion fiscal del cliente.
  - CA: seleccion obligatoria antes de emitir; datos del cliente (CUIT/DNI) requeridos segun tipo elegido.
- HU-7.3: Como sistema, quiero obtener el CAE de AFIP y generar el PDF del comprobante para entregar un documento fiscal valido.
  - CA: si AFIP no responde o rechaza, el comprobante queda en estado "Error" con el detalle del rechazo visible, sin bloquear el resto del sistema; reintentable desde la misma pantalla.
- HU-7.4: Como sistema, quiero renovar automaticamente el token de autenticacion WSAA cada 24hs para no interrumpir la emision de comprobantes.
  - CA: si el token vencio al momento de facturar, se renueva de forma transparente antes del intento (patron delicias-naturales).

#### M11 — Cuenta corriente del local
- HU-11.1: Como Administrador, quiero ver el balance actual del local (ingresos por ventas menos egresos por compras y gastos) para conocer la salud financiera del negocio en todo momento.
  - CA-N3: saldo visible con detalle de cada movimiento (fecha, tipo, monto, origen); filtro por rango de fecha y tipo de movimiento, persistido en sesion.
- HU-11.2: Como Administrador, quiero que cada pago a proveedor y cada gasto generen automaticamente un movimiento de egreso (CA-N2) sin carga manual duplicada.

#### M12 — Compras a proveedores
- HU-12.1: Como Administrador, quiero crear una orden de compra con lineas de producto, cantidad y precio de compra para formalizar un pedido a un proveedor.
  - CA-N4: OC en estado Borrador editable libremente; al menos 1 linea para poder Confirmar.
- HU-12.2: Como Administrador, quiero confirmar la OC y luego marcarla como Recibida cuando llega la mercaderia para que el stock se actualice solo (CA-N5).
  - CA: OC Confirmada ya no permite editar lineas (solo cancelar); al marcar Recibida se dispara el incremento de stock de cada linea en una unica transaccion.
- HU-12.3: Como Administrador, quiero registrar el pago de una OC en efectivo, transferencia, cheque o deposito (CA-N6) y que impacte la cuenta corriente del proveedor (CA-N7).
  - CA: pago con cheque abre el sub-formulario de datos del cheque (numero, banco, fecha de vencimiento, dias 30/60/90); un pago puede combinar mas de un metodo igual que en ventas.
- HU-12.4: Como Administrador, quiero cancelar una OC en Borrador o Confirmada (no Recibida) si el proveedor no puede cumplir el pedido.
  - CA: OC Recibida no se puede cancelar (ya impacto stock) — solo se puede registrar una nota de devolucion futura (fuera de alcance v1, documentar como exclusion).

#### M13 — Cuenta corriente de proveedores
- HU-13.1: Como Administrador, quiero ver el saldo adeudado a cada proveedor con su historial de movimientos y pagos (CA-N8) para priorizar pagos.
  - CA: listado de proveedores con columna de saldo actual, filtro por proveedor y rango de fecha en el detalle; saldo se actualiza automaticamente con cada pago de OC (CA-N9).

#### M14 — Cheques 30/60/90 dias
- HU-14.1: Como Administrador, quiero ver el cheque emitido como pago con su fecha de vencimiento y cuota (CA-N10) para hacer seguimiento de compromisos futuros.
- HU-14.2: Como Administrador, quiero ver en el dashboard los cheques que vencen en los proximos 30 dias (CA-N11) para anticipar la caja.
- HU-14.3: Como sistema, quiero acreditar automaticamente un cheque al llegar su fecha de vencimiento (CA-N12, job diario) y notificar in-app al Administrador para no depender de revision manual.
  - CA: job idempotente — un cheque se acredita exactamente una vez aunque el job corra mas de una vez el mismo dia (patron ganaderia); notificacion in-app queda en el centro de notificaciones ya existente (`INotificationService`).
- HU-14.4: Como Administrador, quiero marcar manualmente un cheque como Rechazado (CA-N13) cuando el banco lo rebota, para reflejar la realidad y reabrir la deuda con el proveedor.
  - CA: rechazar un cheque revierte el movimiento de CC proveedor generado al pagar (reabre la deuda) y registra motivo.

#### M15 — Caja mensual
- HU-15.1: Como Administrador, quiero ver ingresos y egresos del periodo con filtro de fechas y totales (CA-N14) para el cierre mensual.
- HU-15.2: Como Administrador, quiero ver el comparativo con el mes anterior en la misma vista (CA-N15) para detectar tendencias sin exportar a otra herramienta.

#### M18 — Gastos del negocio
- HU-18.1: Como Administrador, quiero registrar un gasto (alquiler, servicios, sueldos, flete, otro) con monto, forma de pago y fecha (CA-N24) para llevar el control completo de egresos operativos.
- HU-18.2: Como sistema, quiero generar el movimiento correspondiente en CC local y caja del periodo al guardar un gasto (CA-N25) sin doble carga.

#### M9 — Panel de metricas y dashboard
- HU-9.1: Como Administrador, quiero ver en un solo panel: ventas del periodo, stock critico, cheques por vencer, conversion de leads, productos mas vendidos y balance de caja, con filtro de fechas, para tener una foto completa del negocio al entrar al sistema.
  - CA: cada KPI carga de forma independiente (no bloquea el resto si uno tarda); filtro de fecha unico afecta a todos los KPIs sensibles a periodo.
- HU-9.2: Como Vendedor, quiero ver un dashboard simplificado (sin datos financieros) con mis leads pendientes y ventas del dia para orientar mi jornada.
  - CA: KPIs financieros (CC local, caja, proyeccion) ocultos para Vendedor por policy, no solo por CSS (verificar en Arquitectura).

#### M16 — Aumento masivo de precios
- HU-16.1: Como Administrador, quiero seleccionar productos por marca, categoria o modelo y aplicar un porcentaje de aumento sobre precio de compra y/o venta, viendo antes y despues, para actualizar precios en lote sin editar producto por producto.
  - CA-N16 a CA-N19: previsualizacion obligatoria (tabla precio actual -> precio nuevo) antes de habilitar el boton "Confirmar aumento"; el aumento no se aplica hasta la confirmacion explicita; operacion registrada en auditoria (quien, cuando, cuantos productos, % aplicado).

#### M17 — Proyeccion financiera
- HU-17.1: Como Administrador, quiero ver una proyeccion de ingresos y egresos del proximo periodo basada en el promedio de los ultimos meses mas los compromisos ya conocidos (cheques por vencer + OCs pendientes) para anticipar la caja.
  - CA-N20 a CA-N22: alerta visible si gastos comprometidos superan ingresos proyectados; texto explicativo junto al numero aclarando que es una estimacion (no un compromiso exacto), para fijar expectativa del cliente (riesgo documentado en analisis).
- HU-17.2: Como Administrador, quiero ajustar el periodo base de la proyeccion entre 1, 3 y 6 meses (CA-N23) para comparar distintos horizontes.

#### Etapa 2 — M1 CRM de Leads
- HU-1.1: Como Vendedor, quiero ver el panel de contactos generados por WhatsApp con producto consultado, anuncio de origen y estado para retomar la conversacion sin perder contexto.
  - CA: listado con filtro por estado, vendedor asignado y rango de fecha, persistido en sesion; cada lead muestra el historial completo de interacciones (mensajes bot + notas del vendedor).
- HU-1.2: Como Vendedor, quiero cambiar el estado de un lead (Nuevo -> Contactado -> Presupuesto enviado -> Vendido/Perdido) para reflejar el avance real de la negociacion.
  - CA: transicion "Vendido" solo se habilita si el lead tiene al menos un presupuesto convertido a venta asociado; "Perdido" pide motivo opcional.
- HU-1.3: Como Administrador, quiero asignar o reasignar un lead a un vendedor especifico para distribuir la carga de trabajo.

#### Etapa 2 — M8 Bot WhatsApp
- HU-8.1: Como cliente (usuario final), quiero que al escribir despues de ver un anuncio el bot ya sepa que producto consulte, sin tener que repetirlo, para no perder tiempo.
  - CA: el bot lee el `referral` del webhook de Meta y lo asocia al producto configurado para ese anuncio antes de la primera respuesta.
- HU-8.2: Como cliente (usuario final), quiero que el bot me haga preguntas especificas segun la categoria del producto (ambiente/medidas/color para muebles, interior-exterior/instalacion para iluminacion, medidas/color para textiles) para que el vendedor ya tenga el contexto util cuando me contacte.
  - CA: si el cliente no responde las preguntas de calificacion, el lead queda registrado igual con las respuestas que si se obtuvieron (caso especial ya confirmado en analisis).
- HU-8.3: Como cliente (usuario final), que escribe sin venir de un anuncio, quiero recibir una pregunta abierta de bienvenida para poder consultar igual sin quedar afuera del flujo.
- HU-8.4: Como Administrador, quiero configurar las categorias y preguntas de calificacion del bot antes de la puesta en marcha para adaptarlo al catalogo real del negocio.

### Flujos de pantalla acordados (wireframe textual)

Convencion de layout (aplica a toda pantalla nueva, ver `25-frontend-design-system.instructions.md`): Titulo + breadcrumb arriba -> fila de filtros (si es listado) -> accion primaria a la derecha del titulo -> contenido agrupado en cards -> acciones destructivas siempre diferenciadas visualmente.

- **Listado generico** (Productos, Leads, Presupuestos, Ventas, Entregas, Comprobantes AFIP, Movimientos CC, Proveedores, OCs, Cheques, Gastos, Usuarios): Titulo + boton "Nuevo" arriba a la derecha -> fila de filtros por columna (persistidos en sesion) + boton "Limpiar filtros" -> DataTable server-side con badge de estado por color cuando aplica -> acciones por fila (Ver/Editar/Eliminar) en dropdown si son mas de 2.
- **Alta/Edicion generica** (Producto, Proveedor, Gasto, Usuario): card unica si <= 8 campos; si supera, cards separadas por grupo logico (ej. Producto: card "Datos generales" + card "Precios y stock" + card "Fotos"). Acciones Guardar/Cancelar fijas abajo a la derecha.
- **Presupuesto (alta)**: card superior con datos del cliente/lead de origen (si viene de un lead) -> tabla editable de items (buscador de producto tipo Select2 + cantidad + precio editable + subtotal por fila, recalculo AJAX) -> card total con boton "Generar PDF" (deshabilitado hasta tener al menos 1 item) -> boton "Enviar / Guardar" segun estado.
- **Presupuesto (detalle)**: header con estado actual como badge + boton "Convertir a venta" (visible solo en Aprobado) + boton "Descargar PDF" + boton "Rechazar/Marcar expirado" (Administrador).
- **Venta (alta)**: pantalla prioritaria del sistema — ver seccion dedicada **"Especificacion UX elevada — Pantalla de Ventas"** mas arriba para el detalle completo (layout dos columnas con resumen sticky, buscador instantaneo, pago rapido). Si viene de conversion de un Presupuesto, los items llegan precargados (editable solo cantidad); confirmar venta dispara stock + CC en una unica transaccion.
- **Entrega (mobile)**: card unica: datos del cliente/direccion arriba, mapa/link a direccion, boton grande "Registrar cobro" (si aplica) y boton grande "Marcar entregada" / "No entregada" abajo, thumb-friendly.
- **Comprobante AFIP (alta desde Venta)**: tabla de items de la venta con checkbox + cantidad editable (tope = pendiente de facturar) -> selector Factura A/B -> datos fiscales del cliente -> boton "Emitir" (deshabilitado sin al menos 1 item marcado) -> tras emitir: card con CAE, vencimiento CAE y boton "Descargar PDF".
- **Orden de compra (alta)**: card de datos del proveedor (Select2) -> tabla editable de items (producto + cantidad + precio compra) -> total -> acciones segun estado (Confirmar / Marcar recibida / Cancelar, cada una con confirmacion SweetAlert2).
- **Pago de OC / Pago de venta (sub-formulario)**: lista de metodos agregables (Efectivo, Transferencia, Cheque, Deposito/MercadoPago segun contexto); al elegir Cheque se despliegan campos numero/banco/vencimiento/cuota inline (no modal aparte, para no perder contexto del pago).
- **Cheques (listado)**: badge de color por estado (Pendiente=amarillo, Acreditado=verde, Rechazado=rojo); filtro por estado, proveedor y rango de vencimiento; fila de cheques venciendo en <=7 dias resaltada.
- **Dashboard Administrador**: fila de filtro de fecha global arriba -> grid de KPI cards (ventas del periodo, stock critico, cheques por vencer, conversion leads, balance caja) -> grafico de productos mas vendidos -> card de alerta de deficit (proyeccion) si corresponde, color de alerta.
- **Dashboard Vendedor**: version reducida sin cards financieras — leads pendientes asignados + ventas del dia + accesos directos a "Nuevo presupuesto"/"Nueva venta".
- **Aumento masivo de precios**: paso 1 (formulario: criterio marca/categoria/modelo + valor + target precio compra/venta/ambos + %) -> paso 2 previsualizacion (tabla precio actual/nuevo, sin persistir) -> boton "Confirmar" solo habilitado tras generar la previsualizacion.
- **Proyeccion financiera**: selector de periodo base (1/3/6 meses) -> card de ingresos proyectados vs egresos comprometidos -> alerta de deficit si aplica, con texto aclaratorio de que es una estimacion.
- **Lead / CRM (detalle)**: header con estado como badge + selector de cambio de estado -> card con producto consultado + anuncio de origen -> timeline de interacciones (mensajes bot + notas manuales del vendedor) -> boton "Nuevo presupuesto desde este lead".

### ViewModels propuestos

Convencion: DataAnnotations en espanol argentino, sin exponer entidades de Domain (`23-web.instructions.md`). Se listan los campos funcionales; el detalle tecnico final (tipos, nullability) lo cierra Arquitectura.

| ViewModel | Campos principales | Validaciones funcionales |
|---|---|---|
| `ProductoViewModel` | Nombre, Descripcion, PrecioCompra, PrecioVenta, MarcaId, ModeloId/Texto, CategoriaId, StockMinimo, Fotos (max 5) | Requeridos: Nombre, PrecioVenta, CategoriaId. PrecioVenta < PrecioCompra -> warning no bloqueante. Max 5 fotos. |
| `AjusteStockViewModel` | ProductoId, Cantidad (+/-), Motivo | Motivo requerido. Resultado negativo -> confirmacion explicita. |
| `PresupuestoViewModel` + `PresupuestoItemViewModel` | LeadId (opcional), Items[ProductoId, Cantidad, PrecioUnitario], Vigencia (dias) | Al menos 1 item para generar PDF/enviar. |
| `VentaViewModel` + `VentaItemViewModel` + `PagoVentaViewModel` | Items, Pagos[Metodo, Monto], PresupuestoOrigenId (opcional) | Suma de pagos <= total para Pendiente/Parcial; = total para Pagada. |
| `EntregaViewModel` | VentaId, Direccion, FechaProgramada, VendedorAsignadoId | Direccion requerida. FechaProgramada >= hoy. |
| `RegistrarCobroEntregaViewModel` | EntregaId, Pagos[Metodo, Monto] | Igual regla que PagoVenta. |
| `ComprobanteAfipViewModel` | VentaId, TipoComprobante (A/B), Items[VentaItemId, Cantidad], DatosFiscalesCliente | Al menos 1 item marcado. Cantidad <= pendiente de facturar por item. CUIT/DNI requerido segun tipo. |
| `ProveedorViewModel` | RazonSocial, CUIT, Telefono, Email, Direccion | RazonSocial y CUIT requeridos. CUIT formato valido. |
| `OrdenCompraViewModel` + `OrdenCompraItemViewModel` | ProveedorId, Items[ProductoId, Cantidad, PrecioCompra] | Al menos 1 item para Confirmar. |
| `PagoOrdenCompraViewModel` | OrdenCompraId, Pagos[Metodo, Monto, DatosCheque?] | DatosCheque requerido si Metodo = Cheque (Numero, Banco, FechaVencimiento, Cuota 30/60/90). |
| `ChequeRechazadoViewModel` | ChequeId, Motivo | Motivo requerido. |
| `GastoViewModel` | Categoria (enum), Monto, FormaPago, Fecha, Descripcion | Monto > 0. Fecha no futura. |
| `AumentoMasivoPrecioViewModel` | Criterio (Marca/Categoria/Modelo), CriterioValorId, TargetPrecio (Compra/Venta/Ambos), Porcentaje | Porcentaje != 0. Preview antes de Confirmar (obligatorio en el flujo, no solo UI). |
| `ProyeccionFinancieraViewModel` | PeriodoBaseMeses (1/3/6) | Solo lectura + selector de periodo. |
| `DashboardAdminViewModel` / `DashboardVendedorViewModel` | RangoFecha, KPIs por seccion | Filtro de fecha con rango por defecto (mes actual). |
| `LeadViewModel` | Nombre, Telefono, ProductoConsultadoId, AnuncioOrigen, Estado, VendedorAsignadoId, Interacciones[] | Estado solo editable via transiciones validas de la maquina de estados. |
| `ConfiguracionBotViewModel` (Etapa 2) | CategoriaProductoId, Preguntas[Texto, Orden] | Al menos 1 pregunta por categoria configurada. |

### Validaciones de UI acordadas

- Mensajes de validacion en espanol argentino, junto al campo (no solo resumen arriba).
- Formularios con mas de 8 campos agrupados en cards con encabezado propio (Producto, Venta, OC).
- Toda accion destructiva o irreversible (eliminar, cancelar venta/OC, rechazar cheque, marcar lead perdido) exige confirmacion SweetAlert2 explicita con el detalle de la consecuencia (ej. "Esta OC ya impacto stock, cancelarla no lo revertira" cuando corresponda).
- Validacion de "suma de pagos = total" en tiempo real client-side (feedback inmediato) + revalidacion server-side obligatoria antes de persistir (nunca confiar solo en client-side).
- Combos de relacion (Marca, Categoria, Proveedor, Vendedor asignado) usan Select2; en pantallas de Editar se inicializan siempre con el valor ya asignado, nunca vacios (regla `32-estandares-qa-implementador.instructions.md`).
- Verificacion 100% funcional de formularios (pedido explicito del cliente): cada formulario del sistema pasa por matriz de casos QA en etapa 6 — caso valido, cada campo requerido vacio, formato invalido, limites de negocio (ej. 6ta foto, suma de pagos distinta al total, cantidad a facturar mayor a la pendiente).

### Maquina de estados (formato tabla)

**Lead** (Etapa 2)
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Alta (bot o manual) | Nuevo | — | Registrar lead | — |
| Nuevo | Vendedor contacta | Contactado | — | Registrar interaccion | — |
| Contactado | Envia presupuesto | Presupuesto enviado | Presupuesto asociado existe | Vincular presupuesto | "No hay presupuesto asociado" |
| Presupuesto enviado | Presupuesto convertido a venta | Vendido | Venta asociada existe | Cerrar lead | — |
| Cualquiera excepto Vendido | Marcar perdido | Perdido | — | Motivo opcional | — |

**Presupuesto**
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Crear | Borrador | Al menos 0 items | — | — |
| Borrador | Enviar | Enviado | Al menos 1 item | Generar PDF | "Agregue al menos un item" |
| Enviado | Cliente aprueba | Aprobado | — | Habilitar conversion | — |
| Aprobado | Convertir | Convertido | — | Crear Venta, heredar items | — |
| Enviado | Cliente rechaza | Rechazado | — | Motivo opcional | — |
| Enviado | Vence plazo de vigencia | Expirado | Fecha actual > Fecha envio + Vigencia | Calculado al leer, sin job | — |

**Venta**
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Confirmar venta | Pendiente / Pagada parcialmente / Pagada | Segun suma de pagos vs total | Descontar stock + movimiento CC | "Stock insuficiente" (warning, no bloqueo salvo confirmacion) |
| Pagada / Pagada parcialmente | Programar entrega | Con entrega pendiente | — | Crear Entrega | — |
| Con entrega pendiente | Entrega cerrada | Entregada | Entrega en estado Entregada | — | — |
| Pendiente/Pagada (sin entrega/factura) | Cancelar | Cancelada | Sin Entrega ni Comprobante AFIP asociados | Revertir stock + CC | "Venta con entrega o factura asociada, no se puede cancelar" |

**Entrega**
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Crear desde venta | Pendiente | Venta confirmada | — | — |
| Pendiente | Vendedor sale a repartir | En camino | — | — | — |
| En camino | Cliente recibe | Entregada | — | Registrar cobro si pendiente | — |
| En camino | Cliente ausente | No entregada | — | Motivo obligatorio | — |
| No entregada | Reagendar | Pendiente | Nueva fecha >= hoy | — | — |

**Orden de compra**
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Crear | Borrador | — | — | — |
| Borrador | Confirmar | Confirmada | Al menos 1 linea | Bloquear edicion de lineas | "Agregue al menos una linea" |
| Confirmada | Recibir | Recibida | — | Incrementar stock por linea (transaccion unica) | — |
| Borrador / Confirmada | Cancelar | Cancelada | Estado != Recibida | — | "OC ya recibida, no se puede cancelar" |

**Cheque**
| Estado origen | Evento | Estado destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Registrar como pago de OC | Pendiente | Fecha vencimiento >= hoy | — | — |
| Pendiente | Job diario detecta vencimiento | Acreditado | Fecha actual >= Fecha vencimiento | Notificacion in-app, idempotente | — |
| Pendiente | Administrador marca rechazo | Rechazado | — | Reabrir deuda con proveedor (revertir CC) | — |

### Reglas de negocio y permisos por pantalla / accion

Tabla base = tabla "Permisos por rol" ya cerrada en `1-analista-funcional.md`. Ampliacion funcional por pantalla:

| Pantalla / accion | Administrador | Vendedor |
|---|---|---|
| Ver precio de compra / costo en cualquier pantalla (Producto, OC, reportes) | Ve | No ve (columna/campo oculto, no solo deshabilitado) |
| Convertir presupuesto a venta | Si | Si |
| Cancelar venta | Si | Si (propia o de cualquier vendedor — a validar con cliente si se restringe a "propia") |
| Emitir comprobante AFIP | Si | Si |
| Ver listado de OCs / proveedores / cheques | Si | No (403 si accede por URL) |
| Dashboard financiero (CC local, caja, proyeccion) | Si | No — ve version reducida sin esas cards |
| Aumento masivo de precios | Si | No |
| Configurar categorias/preguntas del bot | Si | No |

### Impacto funcional por capa

- **Presentacion**: ~15 controllers nuevos (Productos, Stock, Presupuestos, Ventas, Entregas, ComprobantesAfip, CCLocal, Proveedores, OrdenesCompra, CCProveedores, Cheques, Caja, Gastos, Dashboard, AumentoMasivoPrecios, Leads, ConfiguracionBot). Cada uno con su set de Views (Index/Create/Edit/Details segun aplique) + ViewModels de la tabla anterior. Sidebar ampliado con secciones nuevas condicionadas por policy.
- **Negocio**: Services por modulo con las maquinas de estado de arriba: `PresupuestoService`, `VentaService` (orquesta stock + CC en transaccion), `EntregaService`, `ComprobanteAfipService` (integra `AfipService`), `OrdenCompraService`, `PagoOrdenCompraService`, `ChequeService` (+ `IHostedService` de acreditacion diaria), `CajaService`, `ProyeccionFinancieraService`, `AumentoMasivoPrecioService`, `LeadService`, `BotWhatsAppService` (Etapa 2).
- **Datos**: ~24 entidades nuevas (detalle y migraciones en Arquitectura), todas heredando `SoftDestroyable` salvo ledgers de movimientos (inmutables, no se soft-deletean, se revierten con contramovimiento).

### Riesgos y supuestos

- Filtros en sesion: si el negocio corre en mas de una pestaña/dispositivo simultaneo con el mismo usuario, los filtros se comparten por sesion (no por pestaña) — comportamiento estandar aceptado, no es multi-tab aware.
- M17 Proyeccion financiera: riesgo de expectativa de precision ya documentado en analisis — el diseno lo mitiga con texto aclaratorio visible junto al numero, no solo en documentacion de alcance.
- M7 AFIP: la UI de seleccion parcial de items para facturar es el punto de mayor complejidad de validacion (cantidad pendiente por item, facturacion en mas de un comprobante) — cubrir con casos de prueba dedicados en QA.
- Permiso "Vendedor ve ventas de otros vendedores": queda como supuesto abierto (ver tabla de permisos) — si el cliente pide restriccion por vendedor propio, es un ajuste de policy menor, no de arquitectura.

### Contratos funcionales para Services

- Todo Service que puede fallar por regla de negocio retorna `ServiceResult` / `ServiceResult<T>` (ya definido en Application) — el Controller nunca interpreta excepciones de negocio, solo el resultado.
- `VentaService.ConfirmarAsync`, `OrdenCompraService.RecibirAsync`, `ChequeService.AcreditarAsync/RechazarAsync`, `GastoService.CrearAsync` son los puntos donde se genera movimiento de stock y/o CC — deben ejecutar en una unica transaccion de base de datos (todo o nada).
- `ChequeAcreditacionHostedService` (IHostedService, patron ganaderia) corre diariamente, es idempotente (no reacredita un cheque ya Acreditado) y dispara `INotificationService` al finalizar cada acreditacion.

### Diseño v2 — Change request feedback primera demo (2026-07-27, CR-1 a CR-7)

Sobre análisis v3 aprobado (`1-analista-funcional.md`). No reabre ni contradice el diseño v1 — son extensiones puntuales sobre pantallas ya existentes.

### CR-1 — Orden de compra: tipo de comprobante + impuestos

**Pantalla afectada**: `OrdenesCompra/Create` (alta, ver diseño v1 "Orden de compra (alta)"). Se agrega, debajo de la tabla de ítems y antes del total:
- Card "Comprobante": radio Facturada / No facturada (en negro). Si Facturada → combo Tipo (A/B/C), requerido.
- Card "Impuestos" (solo si Facturada, colapsada/deshabilitada si No facturada — impuestos = 0 automático en OC no facturada): 3 filas Porcentaje + Monto (IVA, Ingresos Brutos, Otros), cada Monto se recalcula en vivo al tipear el Porcentaje (base: Subtotal para IVA; Subtotal+IVA para IIBB/Otros) pero el Monto queda editable a mano si el cálculo sugerido no coincide con la factura real (mismo criterio "sugerido pero editable" de ganadería).
- Total de la card pasa a mostrar: Subtotal (de los ítems) + los 3 montos de impuesto = Total final, en la misma jerarquía visual que ya tiene el total de la pantalla.

- HU-12.5: Como Administrador, quiero indicar si la compra que cargo tiene factura (A/B/C) o es en negro, y cargar los impuestos discriminados cuando corresponde, para que el total de la OC refleje lo que realmente pagué y no solo el precio de los productos.
  - CA: Tipo obligatorio solo si Facturada=true. Los 3 campos de impuesto se pre-calculan pero son editables. Total = Subtotal + suma de montos de impuesto.
- HU-12.6: Como sistema, quiero que las OC ya cerradas antes de este cambio mantengan su saldo pendiente sin alteración, para no generar deudas o saldos a favor fantasma con proveedores tras la migración.
  - CA: migración de datos fija impuesto 0% en las OC históricas (Total sin cambio).

### CR-2 — Cheque: fecha de emisión

**Pantalla afectada**: sub-formulario de pago con cheque (dentro de `OrdenesCompra/Details` → Registrar pago, ver diseño v1). Se agrega el campo **Fecha de emisión** (date picker) junto a los ya existentes (Numero/Banco/Cuota). Al elegir la Cuota (30/60/90) y ya tener la Fecha de emisión cargada, **Fecha de vencimiento se autocompleta** (Emisión + Cuota) pero sigue siendo un campo editable (mismo criterio "sugerido, editable" de CR-1).

- HU-14.5: Como Administrador, quiero cargar la fecha real de emisión del cheque además de su vencimiento, para que el registro coincida exactamente con el cheque físico que tengo en la mano.
  - CA: Fecha de emisión requerida. Fecha de vencimiento se sugiere automáticamente (Emisión + días de la Cuota elegida) y se puede corregir a mano.

### CR-3 — Ventas: Tarjeta de crédito en cuotas + Banco Carrefour

**Pantalla afectada**: sección "Formas de pago" de `Ventas/Create` (ver "Especificación UX elevada — Pantalla de Ventas"). Se agregan 2 opciones al selector de método de pago existente (Efectivo/Transferencia/MercadoPago):
- **Tarjeta de crédito**: al elegirla, la fila despliega 2 campos inline (sin salir de la pantalla, mismo criterio ya usado para el sub-formulario de cheque en OC): combo Cuotas (3/6/9/12) y campo % Interés (opcional, vacío = sin interés).
- **Banco Carrefour**: sin campos adicionales, mismo comportamiento que Efectivo/Transferencia/MercadoPago.

- HU-5.10: Como Vendedor, quiero registrar un pago con tarjeta de crédito indicando la cantidad de cuotas y, si corresponde, el interés de la financiación, para que la venta refleje cómo pagó realmente el cliente.
  - CA: Cuotas obligatorio si Metodo=TarjetaCredito (3/6/9/12, sin otros valores). % Interés opcional, default vacío/0.
- HU-5.11: Como Vendedor, quiero poder cobrar con Banco Carrefour como un medio de pago más, igual que efectivo o transferencia.
  - CA: aparece en el selector de métodos de Ventas; NO aparece en el selector de métodos de Compras a proveedores (ver nota de alcance abajo).

**Nota de alcance (aclarada en Arquitectura)**: `MetodoPago` es compartido entre Venta y OC — Tarjeta de crédito y Banco Carrefour se agregan al enum pero la lista de métodos habilitados por pantalla (ya filtrada hoy en el ViewModel/Controller, ver `3-arquitecto-mvc.md`) NO los incluye para Compras — son exclusivos de Ventas salvo que el cliente pida lo contrario.

### CR-4 — Descargar y enviar comprobante por WhatsApp

**Pantalla afectada**: `Ventas/Details` (agrega lo que hoy ya existe en Presupuestos y Comprobantes AFIP, unificado). Dos botones nuevos junto a los ya existentes:
- **"Descargar PDF"**: mismo comprobante ya generado (Comprobante AFIP si existe, o el detalle de la venta como remito/recibo simple si todavía no fue facturada — a definir con el cliente cuál PDF exacto se descarga cuando no hay factura AFIP emitida, marcado como hipótesis abierta abajo).
- **"Enviar por WhatsApp"**: visible solo si `Venta.ClienteTelefono` tiene dato. Abre `wa.me/<telefono>?text=<mensaje prellenado con el link de descarga>` en una pestaña nueva. El vendedor confirma el envío manualmente desde WhatsApp Web/App — el sistema no envía nada por sí mismo (confirmado con el cliente, ver `1-analista-funcional.md` CR-4).

- HU-7.5: Como Vendedor, quiero mandarle al cliente el comprobante de su compra por WhatsApp con un clic, sin tener que buscar el archivo y adjuntarlo a mano en otra app, para agilizar la postventa.
  - CA: botón oculto (no solo deshabilitado) si no hay teléfono cargado. El link generado abre WhatsApp con el número correcto y un mensaje en español claro ("Hola! Te paso el comprobante de tu compra: <link>").

**Confirmado por el cliente (2026-07-27)**: cuando la venta no tiene Comprobante AFIP emitido, el PDF a descargar/enviar es el **comprobante remito de la venta** (documento interno de entrega, no fiscal — mismo estilo visual que el resto de los PDF del sistema, listando ítems/cantidades/total y los datos del cliente, sin CAE). Si la venta ya tiene un Comprobante AFIP emitido, se descarga ese (ya existe desde Sprint 6). El botón "Descargar PDF"/"Enviar por WhatsApp" en `Ventas/Details` elige automáticamente cuál de los dos corresponde según si hay o no un `ComprobanteAfip` con Estado=Emitido asociado a la venta.

### CR-5 — Gastos: categorías nuevas

**Pantalla afectada**: `Gastos/Create` e `Index` (filtro de Categoría). Sin cambio de estructura de pantalla — solo cambia la lista de opciones del combo Categoría: Sueldos, Impuestos, Luz, APR, Publicidad, Otro (6, ver análisis CR-5 para el resguardo "Otro").

- HU-18.3: Como Administrador, quiero elegir la categoría de gasto de una lista corta y clara (Sueldos/Impuestos/Luz/APR/Publicidad/Otro) para no tener que interpretar categorías libres inconsistentes como en el sistema anterior.
  - CA: combo cerrado de 6 opciones, sin texto libre.

### CR-6 — Importación de datos históricos

No es una pantalla nueva de uso diario — es una herramienta de una sola vez (mismo patrón que `tools/SeedTestData/`, pero leyendo los 4 Excel reales de `Importacion/` en vez de generar datos ficticios). Plan funcional (detalle técnico en Arquitectura):
1. Proveedores (32): mapeo directo a la entidad `Proveedor` ampliada (CR ya acordado con el cliente).
2. Compras (239, 464 líneas): requiere resolver primero qué Producto de línea corresponde a qué Producto del catálogo real del cliente — **no se puede automatizar 100% sin intervención humana** (nombres de producto en texto libre del sistema viejo). Plan: generar un Producto nuevo por cada nombre distinto no reconocido (con precio de compra = el del histórico, precio de venta a completar después por el cliente), en vez de bloquear el import completo por productos faltantes.
3. Ventas (634, 983 líneas): igual criterio de Producto. Se importan como Ventas ya Pagadas (histórico cerrado), **sin generar Comprobante AFIP** (columna "ARCA" del histórico confirma que casi ninguna fue facturada realmente — no se re-factura retroactivo).
4. Gastos (481): mapeo de categoría libre → una de las 6 categorías nuevas (ver tabla de mapeo propuesta en `1-analista-funcional.md` CR-5, a confirmar con el cliente antes de correr el import).

- HU-Import.1: Como Administrador, quiero que mi historial de compras, ventas, gastos y proveedores del sistema anterior aparezca cargado en marihogar, para no perder mi historial comercial ni arrancar de cero en las cuentas corrientes y reportes.
  - CA: los 4 archivos se importan en el orden Proveedores → Productos (derivados) → Compras → Ventas → Gastos (por dependencias de FK). Reporte final de importación: cuántas filas se importaron OK, cuántas requirieron crear un Producto nuevo, cuántas quedaron con categoría "Otro" por no matchear el mapeo.

### CR-7 — Cheques: acreditación manual

**Pantalla afectada**: `Cheques/Details` (el botón "Acreditar" ya existe en el diseño v1 — hoy no se ejercita porque el job lo hacía solo). Sin cambio de pantalla. Cambia el comportamiento del job de fondo (ver Arquitectura) y el contenido de la notificación in-app: pasa de "Se acreditaron N cheques" a "El cheque Nº X venció hoy, pendiente de acreditar" (una notificación por cheque, no agrupada, para que el Administrador pueda ir directo al cheque desde la notificación).

- HU-14.6: Como Administrador, quiero que el sistema me avise cuando un cheque llega a su fecha de vencimiento, pero que la acreditación quede en mis manos, para poder confirmar primero con el banco que el cheque efectivamente se cobró antes de darlo por acreditado en el sistema.
  - CA: el cheque NO cambia de estado solo al vencer. La notificación aparece una única vez por cheque (no se repite todos los días mientras siga Pendiente). "Acreditar" sigue siendo una acción manual explícita, disponible en cualquier momento desde que vence (no solo el día exacto).

### Diseño v3 — Sprint CR-B: CR-8 (sugerir monto) + CR-9 (desglose facturado/no facturado)

Sobre análisis v4 (`1-analista-funcional.md`, "Discovery + Análisis v4"). Extensiones puntuales sobre pantallas ya existentes (Ventas/Create, OrdenesCompra/Details, Dashboard, Caja, Proyección financiera) — no reabren diseño v1/v2.

### CR-8 — Sugerir el total/saldo pendiente como monto de pago por defecto

**Pantallas afectadas**: sub-formulario de pago de `Ventas/Create.cshtml` y de `OrdenesCompra/Details.cshtml` (registrar pago).

- HU-5.12: Como Vendedor, quiero que al agregar una fila de pago nueva en la venta el campo Monto ya venga completado con lo que falta cobrar, para no tener que calcularlo ni tipearlo a mano en el caso más común (pago único).
  - CA: al click en "Agregar" (forma de pago), el Monto se precompleta con `Total − suma de filas de pago ya cargadas` (nunca negativo — si ya está cubierto, el campo queda vacío); el valor sigue siendo editable libremente. No cambia el comportamiento de "Todo efectivo"/"Todo transferencia" (ya autocompletan con el total).
- HU-12.7: Como Administrador, quiero el mismo comportamiento al registrar un pago de Orden de compra, para no tener que calcular a mano el saldo pendiente cada vez que agrego una forma de pago.
  - CA: idéntico criterio que HU-5.12, usando el saldo pendiente de la OC como base en vez del total de la venta.

### CR-9 — Reportes: distinguir ventas facturadas de no facturadas

**Pantallas afectadas**: `Dashboard/Admin.cshtml` (card "Ventas del período"), `Caja/Index.cshtml` (resumen del período), `ProyeccionFinanciera/Index.cshtml` (card "Ingresos proyectados").

- HU-9.3: Como Administrador, quiero ver cuánto de lo vendido en el período está facturado y cuánto no, en la card de Ventas del período del Dashboard, para dimensionar la proporción real de venta en blanco del negocio.
  - CA: desglose Facturado/No facturado (cantidad y monto) según si la Venta tiene un `ComprobanteAfip` con `Estado=Emitido` asociado (clasificación binaria por venta, facturada total o parcialmente cuenta como "facturada" — CA-CR9.1). La suma de ambos segmentos coincide siempre con el total ya mostrado (no duplica ni omite ventas).
- HU-15.3: Como Administrador, quiero ver el mismo desglose en el resumen de Caja mensual, para que el cierre del período distinga ingresos facturados de no facturados.
  - CA: mismo criterio que HU-9.3, aplicado a los ingresos del período (CA-CR9.2).
- HU-17.3: Como Administrador, quiero ver, junto al ingreso promedio histórico de la Proyección financiera, qué proporción de ese promedio corresponde a ventas ya facturadas, para no interpretar el ingreso proyectado como si fuera todo en blanco.
  - CA: dato informativo (porcentaje), no altera ninguna fórmula de proyección ya definida en M17 (CA-CR9.3).

### Diseño v4 — CR-10/CR-11/CR-12: auditoría de columnas del histórico

Sobre análisis v5 (`1-analista-funcional.md`, "Discovery + Análisis v5"). 3 campos nuevos sobre pantallas ya existentes — no reabre diseño v1/v2/v3.

### CR-10 — Orden de compra: Punto de Venta + Número de comprobante

**Pantalla afectada**: `OrdenesCompra/Create.cshtml` y `Details.cshtml` — el bloque de comprobante ya existente desde CR-1 (checkbox Facturada + select Tipo A/B/C) suma 2 campos de texto.

- HU-12.8: Como Administrador, quiero poder cargar el punto de venta y número de comprobante de la factura del proveedor al confirmar una Orden de Compra facturada, para poder ubicar esa factura física o conciliarla con un reclamo del proveedor más adelante.
  - CA: los 2 campos (Punto de Venta, Número de Comprobante) solo se muestran/habilitan cuando Facturada = true (mismo patrón condicional ya usado para el select Tipo). Ambos opcionales — no bloquean la confirmación de la OC. Se muestran como columna en `OrdenesCompra/Index` (buscable) y en el detalle.

### CR-11 — Gasto: Subcategoría

**Pantalla afectada**: `Gastos/Create.cshtml`/`Edit` y `Gastos/Index.cshtml`.

- HU-18.4: Como Administrador, quiero poder anotar una subcategoría de texto libre al cargar un Gasto, además de la categoría fija, para poder identificar el detalle real del gasto (ej. "Gastos bancarios PCIA", "Sueldo Juan") sin forzarlo dentro de una de las 6 categorías cerradas.
  - CA: campo de texto libre opcional, debajo del select de Categoría. Se muestra en el listado de Gastos como columna secundaria (bajo el nombre de categoría) y es filtrable por texto junto al filtro de categoría ya existente (mismo cuadro de búsqueda, sin filtro dedicado nuevo).

### CR-12 — Venta: Nota interna

**Pantalla afectada**: `Ventas/Create.cshtml` (campo nuevo, colapsado/opcional) y `Ventas/Details.cshtml` (visible).

- HU-5.13: Como Vendedor, quiero poder dejar una nota interna de texto libre al cargar una venta, para anotar aclaraciones que no van en el remito del cliente (ej. una condición de pago especial, un pedido puntual del cliente).
  - CA: campo de texto libre opcional, fuera del bloque de pago/productos (no interrumpe el flujo POS ya optimizado de Ventas — ver "Especificación UX elevada"). Visible en `Ventas/Details` para Administrador y Vendedor. **Nunca** se incluye en el PDF del remito ni del comprobante AFIP (`GenerarRemitoPdfInterno`/`ComprobanteAfipService` no la leen) — es exclusivamente interna.

### Nota de alcance
Los 3 ítems son extensiones de un campo sobre un formulario ya diseñado — no generan wireframe nuevo ni cambian ninguna máquina de estados. El diseño de detalle de UI (posición exacta del campo, si va colapsado detrás de un "Agregar nota") queda a criterio del implementador dentro del patrón visual ya establecido, sin volver a este gate.

### Diseño v5 — CR-14/CR-15/CR-16/CR-18: mejoras post-migración

Sobre análisis v7. Extensiones puntuales sobre pantallas ya existentes, sin wireframe nuevo.

- HU-11.4 (CR-14): Como Administrador, quiero ver el saldo acumulado junto a cada movimiento del listado de CC Local, para leer el estado de la cuenta en cualquier punto del historial sin sumar a mano.
  - CA: columna "Saldo" nueva en el listado, ordenado cronológicamente, acumulado desde el primer movimiento.
- HU-13.3 (CR-14): mismo criterio que HU-11.4, aplicado al detalle de CC de cada Proveedor.
- HU-12.9 (CR-15): Como Administrador, quiero que al elegir "Cheque" como forma de pago de una OC la fecha de emisión ya venga en la fecha de hoy, para no tener que completarla a mano en el caso más común (pago inmediato con cheque del día).
  - CA: al cambiar el método a Cheque, si no hay fecha cargada, se precompleta con hoy + Cuota=30 (ambos editables), disparando el autocálculo de vencimiento ya existente (CR-2).
- HU-2.5 (CR-16): Como Administrador, quiero que el nombre de Proveedores y Productos se guarde siempre en mayúsculas, para mantener el catálogo prolijo y consistente sin depender de cómo lo tipeen distintos usuarios.
  - CA: normalización automática al guardar (crear/editar), sin pedir nada nuevo en el formulario.

CR-17 no requiere diseño (operación de datos, sin pantalla nueva ni cambio de flujo). CR-18 no requiere diseño (cambio interno del script de importación, sin UI).

### Diseño v6 — CR-21/CR-22: doble precio + edición de precio/subtotal en Ventas (solo Administrador)

Sobre análisis v8. Extiende `Productos/{Create,Edit,Index}` y la pantalla de mayor uso diario (`Ventas/Create`) — se mantiene el layout ya elevado (dos columnas desktop/checkout mobile), solo se agregan controles dentro de la fila de cada línea.

### CR-21 — Catálogo de productos
- HU-2.6: Como Administrador, quiero ver el Precio de Lista (con el 21% ya calculado) junto al Precio Efectivo en el catálogo, para no tener que calcularlo a mano al cotizar en blanco.
  - CA: `Productos/Index` agrega una columna "Precio Lista" (solo lectura, calculada). `Productos/Create`/`Edit` muestran "Precio Efectivo" como el único campo editable de precio de venta, con un texto auxiliar bajo el campo ("Precio de Lista: $X, calculado automático") que se actualiza en vivo mientras se tipea.

### CR-22 — Ventas: precio/subtotal editables (Administrador) + selector de IVA por línea
- HU-5.14: Como Administrador, quiero poder editar el precio unitario y el subtotal de cualquier línea de la venta, para poder aplicar descuentos puntuales o corregir el precio en casos excepcionales.
  - CA: en el carrito de `Ventas/Create`, si el usuario es Administrador, "Precio Unit." y "Subtotal" de cada fila son inputs numéricos editables (antes eran texto fijo). El Total General se recalcula en vivo (mismo patrón que ya existe para Cantidad).
- HU-5.15: Como Administrador, quiero un botón rápido por línea para pasar el precio de esa línea entre Precio Efectivo y Precio de Lista (con IVA), para no tener que calcular el 21% a mano cuando la venta es en blanco.
  - CA: cada fila tiene un toggle/botón "+IVA" — al activarlo, Precio Unit. de esa línea pasa de `Producto.PrecioEfectivo` a `Producto.PrecioLista`; al desactivarlo, vuelve a Precio Efectivo. Es un atajo de carga — el Administrador puede seguir editando el número a mano después, el toggle no bloquea el input.
  - CA: si el Subtotal de una línea fue editado a mano, dejar de recalcularse automáticamente al cambiar Cantidad/Precio de esa línea (queda "fijado" hasta que el Administrador lo vuelva a tocar). Indicador visual sutil (ej. un icono) en la fila para que quede claro que ese subtotal es manual, no calculado.
- HU-5.16: Como Vendedor, quiero seguir viendo el precio de catálogo tal cual está, sin poder editarlo, para no tener margen de error ni de manipulación en mis ventas del día a día.
  - CA: para el rol Vendedor, sin cambios respecto del comportamiento actual — Precio Unit. y Subtotal de cada línea siguen siendo texto fijo (no input), calculados server-side, sin ningún control de IVA visible.
- **Nota de seguridad explícita para Arquitectura**: la restricción de edición no puede ser solo de UI (ocultar/mostrar el input según el rol) — el servidor debe revalidar el rol en `VentaService.ConfirmarAsync` y descartar cualquier precio/subtotal recibido de un usuario que no sea Administrador, igual que hace hoy para todos los roles.

### Diseño v7 — CR-24: precio de línea con 4 elementos, Total editable, pagos posteriores en Ventas

Sobre análisis v10. Extiende `Ventas/Create.cshtml` y `Ventas/Details.cshtml` (pantalla de mayor uso diario) — mismo layout ya elevado, solo cambios dentro de la fila/carrito y una capacidad nueva en Details.

- HU-5.17 (CR-24.1/24.2): Como Administrador, quiero que el precio con IVA se calcule sobre lo que yo cargué en el precio de la línea (no sobre el precio de catálogo fijo), para no perder un precio negociado al activar el IVA.
  - CA: columna de precio con 4 elementos en orden: Precio (input), botón IVA, "c/IVA" (calculado, solo lectura, Precio×1,21), Subtotal (input). El botón decide si el subtotal por defecto usa Precio o "c/IVA" — sigue editable a mano aparte.
- HU-5.18 (CR-24.3): Como Administrador, quiero poder escribir el Total final de la venta y que se reparta automáticamente entre los productos, para cerrar una venta a un número redondo sin tener que ajustar línea por línea.
  - CA: fila "Total" al pie de la tabla de productos con un input. Al editarlo, cada línea ajusta su Subtotal en proporción a su peso actual en el total (ej. una línea que hoy es el 30% del total absorbe el 30% de la diferencia). El Resumen de venta se actualiza en vivo.
- HU-5.19 (CR-24.4): Como Administrador/Vendedor, quiero poder registrar un pago adicional sobre una Venta que quedó con saldo pendiente, para poder cobrar el resto más adelante sin tener que anular y recrear la venta.
  - CA: `Ventas/Details.cshtml` gana una card "Registrar pago" (visible solo si `Estado` es `Pendiente` o `PagadaParcial`), mismo patrón visual que el sub-formulario de pago de `OrdenesCompra/Details.cshtml` (selector de método, monto con precarga del saldo pendiente, botón confirmar). Al registrar, el `Estado` de la Venta se recalcula (puede pasar a `Pagada`).
- HU-5.20 (CR-24.5): Como Vendedor/Administrador, quiero caer directo en el detalle de la venta recién creada, para poder seguir operando sobre ella (cobrar el resto, programar entrega, facturar) sin un paso intermedio.
  - CA: al confirmar una Venta desde `Ventas/Create`, redirige a `Ventas/Details/{id}` (reemplaza la pantalla de éxito in-page ya existente).

### Diseño v8 — CR-25/CR-26: comprobante AFIP editable + rediseño de PDFs

Sobre análisis v11.

- HU-7.6 (CR-25): Como Administrador/Vendedor, quiero poder ajustar cantidad, precio, subtotal y total de cada línea al facturar, para poder emitir el comprobante real acordado con el cliente aunque difiera de lo cargado originalmente en la venta.
  - CA: `ComprobantesAfip/Create.cshtml` — columnas Cantidad/Precio Unit./Subtotal editables (inputs abiertos, sin `max`). Aviso visual (no bloqueante) por línea cuando la cantidad supera lo pendiente/vendido de esa línea en la Venta. Fila "Total" editable al pie con reparto proporcional (mismo mecanismo de `Ventas/Create`, CR-24.3). Sin buscador de productos nuevos — el universo de líneas es el de la Venta.
  - CA: la pantalla deja de bloquear el acceso cuando la Venta ya está 100% facturada.
- HU-7.7 (CR-26): Como Administrador, quiero que el remito y la factura tengan una presentación más profesional, con los datos del negocio, para entregarle al cliente un documento con mejor imagen.
  - CA: encabezado con nombre del negocio, CUIT y logo en ambos PDF. Tablas con números alineados a la derecha. Total destacado.
- HU-7.8 (CR-26, cumplimiento): la factura AFIP muestra el código QR exigido por AFIP (RG 4291), visible en el pie de la primera página.

### Diseño v9 — CR-32/CR-33/CR-34: precio dual + recargo tarjeta, edición de Venta, acreditación diferida

Sobre análisis v13. Extiende `Ventas/Create.cshtml`/`Ventas/Details.cshtml` (sin cambio de layout general) y agrega una pantalla nueva (`Ventas/Edit.cshtml`).

- HU-5.21 (CR-32.1): Como Vendedor/Administrador, quiero ver siempre el precio contado y el precio con tarjeta de cada producto al armar la venta, para poder informarle al cliente ambas opciones sin tener que calcular a mano.
  - CA: columna de precio de línea con "Precio contado/transf" (input, edición Administrador-only sin cambio del gate de CR-22) + "Precio tarjeta" (solo lectura, ×1,21, visible para ambos roles) — se saca el toggle IVA manual de CR-24.1, ambas columnas quedan siempre visibles.
- HU-5.22 (CR-32.2/32.3): Como Vendedor/Administrador, quiero registrar cuánto de la venta se cobra con tarjeta y cuánto con otro método, y que el sistema calcule el recargo del 21% solo sobre la parte con tarjeta, para que la caja refleje la plata real que entra por cada medio.
  - CA: al agregar una línea de pago con método Tarjeta de Crédito, el campo de monto pasa a pedir el "monto base a cubrir" (contra el saldo pendiente de la Venta); al lado se muestra en vivo "Total a cobrar con recargo" = monto base × 1,21. El saldo pendiente de la Venta se calcula sobre la suma de montos base, no sobre lo efectivamente cobrado.
- HU-5.23 (CR-33): Como Administrador, quiero poder editar una venta ya creada (productos, cantidades, precios, cliente), para corregir un error de carga sin tener que cancelarla y recrearla.
  - CA: nueva pantalla `Ventas/Edit`, mismo layout que `Create`, precargada. Disponible mientras la Venta no esté `Cancelada`, no tenga ninguna Entrega asociada y no tenga ningún Comprobante AFIP emitido — mismo guard combinado que ya bloquea "Cancelar" hoy; si aplica, el botón "Editar" no aparece y un mensaje explica el motivo. Al guardar: se revierte y reaplica el stock de los items (mismo patrón que `Cancelar`), se recalcula el Total; los pagos ya registrados no se tocan por esta vía.
- HU-5.24 (CR-34): Como Administrador, quiero que un pago con tarjeta quede "pendiente de acreditar" hasta la fecha real en que entra el dinero, para que la Caja no muestre como disponible una plata que todavía no llegó al banco.
  - CA: al registrar un pago con tarjeta, se pide la "fecha efectiva de acreditación" (sugerida, editable). El pago queda con badge "Pendiente hasta dd/mm/aaaa" en la tabla de Pagos de `Ventas/Details`. Botón "Marcar acreditado" (Administrador) para confirmarlo manualmente antes/en esa fecha — recién ahí el ingreso aparece en Caja, con la fecha de acreditación real (no la fecha del cobro).
  - CA: Proyección Financiera suma los pagos con tarjeta pendientes de acreditar al mismo bloque informativo ya creado por CR-29 ("pagos de venta por acreditar"), sin cambiar la fórmula de déficit ya establecida.

### CR-55 (Diseño) — Nota de Crédito para anular una Factura AFIP emitida por error

**Escaneo de reutilización (obligatorio antes de diseñar)**: revisados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial. Único hit real fue vinosefue (`RegistrarNotaCreditoProveedorViewModel`) — es un concepto homónimo pero NO relacionado (nota de crédito manual de Cuenta Corriente de Proveedor, sin AFIP/CAE/CbtesAsoc). Ningún proyecto del estudio implementó todavía una Nota de Crédito AFIP real (WSFEv1 + `CbtesAsoc`) — se diseña reutilizando el circuito ya construido dentro del propio marihogar (`AfipService`/`ComprobanteAfipService`), no hay código externo para portar. Verificado contra el WSDL real de AFIP (`C:\Sistemas\delicias-naturales\Web References\ws_factura_afip\Reference.cs`, proxy generado) el orden exacto de campos de `FECAEDetRequest`: `CbtesAsoc` va después de `MonCotiz` y antes de `Tributos`/`Iva` — dato técnico para Arquitectura.

**Pantalla/acción**: en `ComprobantesAfip/Details` (o donde se muestre el comprobante Emitido), nuevo botón "Generar Nota de Crédito" — visible solo si `Estado=Emitido` y no tiene ya una NC asociada. Mismo patrón visual que "Cancelar orden de compra"/"Rechazar cheque": SweetAlert2 con `input: 'textarea'` pidiendo el motivo (obligatorio), sin necesidad de pantalla nueva completa.

**ViewModel/Input**: `GenerarNotaCreditoInput { ComprobanteAfipId, Motivo }` (Motivo: requerido, max 500, mismo criterio que `ChequeRechazoInput.Motivo`). No requiere elegir ítems/montos (NC siempre total, replica 1:1 la factura original).

**Flujo funcional**:
1. Administrador o Vendedor (mismo acceso que Facturar) hace click en "Generar Nota de Crédito" sobre una factura `Emitido`.
2. Confirma motivo (SweetAlert2).
3. El sistema arma un nuevo `ComprobanteAfip` (TipoComprobante = NotaCreditoA/B según la factura original, mismos ítems/cantidades/precios/cliente, `ComprobanteAsociadoId` = Id de la factura original) y lo emite contra AFIP (mismo circuito que Facturar, con el bloque `CbtesAsoc` apuntando a la factura original).
4. Si AFIP aprueba (CAE real): la NC queda `Estado=Emitido`, se revierte `VentaItem.CantidadFacturada` de cada ítem por la cantidad que cubría la factura original (vuelven a estar disponibles para facturar de nuevo), y la factura original se muestra visualmente "Anulada" (badge) al tener una NC `Emitido` asociada — sin campo booleano nuevo, se infiere de la relación.
5. Si AFIP rechaza: la NC queda `Estado=Error`, reintentable (mismo patrón ya existente) — la factura original sigue vigente, `CantidadFacturada` no se toca todavía.

**Historias de usuario**:
- HU-7.6 (CR-55): Como Administrador o Vendedor, quiero generar una Nota de Crédito de una factura AFIP ya emitida por error, para anularla formalmente ante AFIP y poder volver a facturar la venta correctamente.
  - CA: el botón "Generar Nota de Crédito" solo aparece sobre un comprobante `Estado=Emitido` sin NC ya asociada. Pide motivo obligatorio. Al emitirse con éxito, la factura original muestra un badge "Anulada" con el número/fecha de la NC, y los ítems de la Venta vuelven a estar disponibles en la pantalla de Facturar (columna "Cantidad pendiente" ya existente se actualiza sola, sin cambios de UI ahí).
- HU-7.7 (CR-55): Como Administrador o Vendedor, si la emisión de la Nota de Crédito falla contra AFIP, quiero poder reintentarla, para no perder el motivo ya cargado ni tener que empezar de nuevo.
  - CA: mismo patrón ya existente para Factura (`Estado=Error` + botón "Reintentar" + `DetalleError` visible). Mientras la NC esté en Error, la factura original NO se muestra como anulada.
- HU-7.8 (CR-55): Como Administrador, quiero que el PDF de la Nota de Crédito tenga el mismo formato oficial que ya usa la Factura, para poder entregarlo al cliente como comprobante válido.
  - CA: reutiliza `ComprobanteAfipService.GenerarPdfAsync` (ya rediseñado en CR-43), mostrando "NOTA DE CRÉDITO" y el código de comprobante (003/008) en vez de "FACTURA".

**Impacto por capa**: ver detalle técnico completo en `3-arquitecto-mvc.md`, sección CR-55.

**Riesgos de implementación**: primera vez que este sistema arma el bloque `CbtesAsoc` contra AFIP real — validar con una NC de bajo monto antes de confiar el flujo a una corrección real. El orden de campos XML es estricto (XSD de AFIP), ya verificado contra el WSDL real (ver escaneo de reutilización arriba).

### CR-59 (Diseño) — Pagos con tarjeta de crédito a liquidar

**Escaneo de reutilización (obligatorio antes de diseñar)**: revisados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial. Sin hits externos relevantes — el patrón a reutilizar es 100% interno a marihogar: `Cheques/Index.cshtml` + `ChequeService.ListarAsync` + `ChequesController` (M14, ya en producción) son un clon casi exacto de lo que necesita este CR, solo cambia la entidad de origen (`PagoVenta` en vez de `Cheque`) y el criterio de negocio (`Metodo=TarjetaCredito` en vez de "todos"). No hay código externo para portar.

**Pregunta de diseño resuelta** (el cliente la planteó como pregunta abierta, no como pedido cerrado): ¿pantalla nueva o card de Dashboard? Se descarta "solo Dashboard" — el Dashboard tiene una regla fija ya establecida (HU-9.1): cada card es un KPI que carga solo vía AJAX, nunca una tabla con acciones (mismo motivo por el que "Cheques por vencer" es una card chica que linkea a `Cheques/Index`, no una tabla embebida). Se diseñan **las dos cosas**: pantalla nueva (el listado real, con la acción de liquidar) + card de acceso en el Dashboard.

**Pantalla/acción**: `PagosTarjeta/Index.cshtml` (Administrador-only — `AcreditarPagoAsync` ya es Administrador-only desde CR-34.2, mismo criterio que Cheques). Filtros: Estado (Pendiente/Acreditado — sin Rechazado, `PagoVenta` no tiene ese estado, a diferencia de Cheque) y rango de fecha de acreditación. Columnas: Venta (link a `Ventas/Details`), Cliente (`Venta.ClienteNombre`, texto libre — no hay entidad Cliente separada en este sistema, así que no hay combo de filtro por cliente, a diferencia del combo de Proveedor que sí tiene Cheques), Cuotas, Monto, Fecha de pago, Fecha de acreditación efectiva, Estado. Resaltado de fila "vence próximo" (≤7 días) igual que Cheques. Botón "Acreditar" (solo si Pendiente) — mismo SweetAlert2 de confirmación que Cheques, apunta a una acción nueva del controller que reutiliza `IVentaService.AcreditarPagoAsync` sin tocarlo.

**ViewModel/DTO**: `PagoTarjetaListItemDto { Id, VentaId, ClienteNombre, Monto, CantidadCuotas, Fecha, FechaAcreditacionEfectiva, Estado, VenceProximo }`, `PagoTarjetaFiltro { Estado?, AcreditacionDesde?, AcreditacionHasta? }` — mismo shape que `ChequeListItemDto`/`ChequeFiltro`.

**Card de Dashboard**: "Pagos con tarjeta por acreditar" (Administrador-only), mismo patrón AJAX independiente que "Cheques por vencer" — cantidad + monto de `PagoVenta` con `Metodo=TarjetaCredito` y `EstadoAcreditacion=Pendiente`, sin filtro de período (es una obligación pendiente, no un dato del período seleccionado — mismo criterio que "Cheques por vencer", que tampoco depende del filtro de fecha del Dashboard). Link a `PagosTarjeta/Index`.

**Historias de usuario**:
- HU-9.3 (CR-59): Como Administrador, quiero ver en un único listado todos los pagos con tarjeta de crédito pendientes de acreditar, para poder gestionar su liquidación sin tener que revisar venta por venta.
  - CA: pantalla `PagosTarjeta/Index` con filtro por Estado y rango de fecha de acreditación, ordenada por fecha de acreditación ascendente por defecto (mismo criterio que Cheques). Fila resaltada si la fecha de acreditación está a 7 días o menos.
- HU-9.4 (CR-59): Como Administrador, quiero poder marcar un pago con tarjeta como acreditado directamente desde ese listado, para no tener que entrar a la venta individual.
  - CA: botón "Acreditar" visible solo si el pago está Pendiente, con confirmación (SweetAlert2). Reutiliza la validación y el posteo de `AcreditarPagoAsync` sin duplicar lógica.
- HU-9.5 (CR-59): Como Administrador, quiero ver de un vistazo en el Dashboard cuántos pagos con tarjeta están pendientes de acreditar, para saber si hay que revisar el listado completo.
  - CA: card "Pagos con tarjeta por acreditar" con cantidad + monto total Pendiente, link directo al listado.

**Impacto por capa**: ver detalle técnico completo en `3-arquitecto-mvc.md`, sección CR-59.

**Riesgos de implementación**: ninguno funcional nuevo — es superficie de lectura (1 query nueva) + 1 acción ya existente y ya probada en producción (`AcreditarPagoAsync`, en uso desde CR-34).

### CR-61 (Diseño) — Stock: listado de productos con edición inline reemplaza Ajuste manual

**Escaneo de reutilización (obligatorio)**: revisados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial. Único hit real: ShowroomGriffin, `Stock/MatrizEditar.cshtml` — grilla de stock editable por celda (Marca→Modelo→Color×Talle), con la misma semántica de "reemplaza, no delta" y `min="0"` que elimina la necesidad de confirmar negativo. Se reutiliza esa idea de diseño, pero **no el código de guardado**: ShowroomGriffin guarda con un único `<form>` en lote (`Celdas[i].CantidadNueva`, un solo POST), mientras que acá el cliente eligió guardado por fila al instante (AJAX on-demand por celda) — mecanismo de transporte distinto, sin precedente directo, se diseña de cero.

**Pantalla `Stock/Index.cshtml` (reemplaza el listado de movimientos)**: clon del patrón de `Productos/Index.cshtml` (mismo `ProductoService.ListarAsync`, mismos filtros Nombre/Marca/Categoría/Modelo — se excluyen los filtros de precio, no aplican acá). Columnas: Nombre, Marca, Categoría, **Stock** (columna editable: `<input type="number" min="0">` en vez de texto plano, con el mismo badge "Bajo mínimo" que ya tiene `Productos/Index` cuando `StockActual < StockMinimo`), Stock mínimo (solo lectura, contexto). Sin columna de Acciones — no hace falta navegar a otra pantalla para editar.

**Interacción de edición** (HU-3.3, reemplaza HU-3.2 de Ajuste manual):
1. El Administrador tipea un nuevo valor en la celda Stock de una fila y sale del campo (blur) o presiona Enter.
2. El campo se deshabilita momentáneamente (feedback de "guardando") y dispara un POST AJAX a `Stock/ActualizarStock` con `productoId` + `nuevoStock`.
3. Si el servidor confirma: el campo se re-habilita, breve destello verde de confirmación, y si `nuevoStock < StockMinimo` el badge "Bajo mínimo" de esa fila se actualiza sin recargar la tabla completa (ídem si deja de estar bajo mínimo).
4. Si el servidor rechaza (ej. `nuevoStock < 0`, aunque el `min="0"` del input ya lo previene la mayoría de las veces — validación server-side de todos modos, nunca confiar solo en el cliente): el campo vuelve al valor anterior, borde rojo breve + mensaje de error (toast, no bloqueante).
5. Sin motivo pedido — decisión explícita del cliente. El sistema genera internamente `Motivo = "Ajuste desde listado de Stock"` para el `MovimientoStock`, sin mostrarlo en ningún formulario.
6. Si `nuevoStock` editado es igual al valor actual (usuario tocó el campo sin cambiarlo): no se postea nada, no se genera un `MovimientoStock` de cantidad 0 (ruido innecesario en el ledger).

**Link "Ver historial de movimientos"**: en la cabecera de `Stock/Index.cshtml`, lleva a `Stock/Movimientos` — el listado de movimientos actual (`MovimientoStockListItemDto`, filtros Producto/Tipo/rango de fecha, sin cambios funcionales), solo renombrado de ruta. Deja de estar en el menú lateral como ítem propio — el menú sigue apuntando a `Stock/Index`, que ahora es la pantalla nueva.

**Retiro de "Ajuste manual"**: `Stock/Ajuste` (GET/POST), `Stock/GetStockActual`, la vista `Ajuste.cshtml` y el ViewModel `AjusteStockFormViewModel` se eliminan del código — no quedan alcanzables ni por menú ni por URL directa. El botón "Ajustar stock" de `Productos/Index.cshtml` (ícono `fa-boxes-stacked`, hoy linkea a `Stock/Ajuste?productoId=X`) pasa a linkear a `Stock/Index?nombre={nombreProducto}` (reutiliza el filtro por Nombre ya existente, deja al producto como única fila del listado filtrado, foco natural en su celda de Stock).

**Historias de usuario**:
- HU-3.3 (CR-61): Como Administrador, quiero editar el stock de un producto directamente desde el listado, sin abrir un formulario aparte, para cargar el conteo físico de muchos productos rápido.
  - CA: escribir un valor en la celda Stock y salir del campo guarda el nuevo stock al instante, sin pedir motivo. El valor escrito reemplaza el stock (no se suma ni resta).
- HU-3.4 (CR-61): Como Administrador, quiero seguir viendo el historial completo de movimientos de stock (compras, ventas, ajustes), para poder auditar cómo llegó cada producto a su stock actual.
  - CA: `Stock/Movimientos` mantiene exactamente las mismas columnas/filtros que tiene hoy `Stock/Index`, accesible con un link desde la pantalla nueva.

**Impacto por capa**: ver detalle técnico completo en `3-arquitecto-mvc.md`, sección CR-61.

**Riesgos de implementación**: primera vez que este proyecto implementa guardado AJAX por celda de un DataTable (no hay precedente exacto en el propio repo) — cuidar especialmente el caso de doble-submit (usuario edita y sale rápido de varias celdas seguidas) y la sincronización del badge "Bajo mínimo" sin recargar toda la tabla.

### CR-62 (Diseño) — Gastos (categoría/forma de pago/recurrentes) + Cuenta Corriente Local (usuario/origen clickeable/saldo filtrado)

**Escaneo de reutilización (obligatorio)**: revisados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todos los proyectos del historial. Sin hits — "gasto recurrente" y "resolución de nombre de usuario en un ledger" son patrones nuevos, aunque el segundo ya tiene precedente **dentro** del propio marihogar (`StockService.ListarMovimientosAsync`, reutilizado tal cual). El CRUD de plantillas se diseña clonando `MarcasController`/`Marcas/*.cshtml` (catálogo simple ya probado, Administrador-only).

**1-2. Categoría y forma de pago nuevas**: agregado puro a `CategoriaGasto`/`FormaPagoGasto` — ningún cambio de vista (los `<select>` ya se generan desde `Enum.GetValues<T>()`).

**3. Gastos recurrentes**: nueva entidad `GastoRecurrente` (Nombre, Categoría, Subcategoría, Forma de pago, Descripción) — una plantilla reutilizable, no un gasto en sí. Pantallas nuevas `GastosRecurrentes/Index` (listado + Crear/Editar/Eliminar, clon de Marcas) — link de acceso desde `Gastos/Index`, no un ítem de menú lateral propio (mismo criterio que "Ver historial de movimientos" en Stock: pantalla de configuración secundaria, no un módulo de primer nivel). En `Gastos/Create.cshtml`: nuevo `<select>` "Cargar desde plantilla" — al elegir una, completa Categoría/Subcategoría/Forma de pago/Descripción vía JS (client-side, la lista de plantillas activas viaja con la vista). **Monto y Fecha nunca se autocompletan** — decisión confirmada con el cliente, el usuario siempre los tipea y confirma con el dato real del resumen bancario.

**4. Nombre de usuario en CC Local**: `MovimientoCCLocal` gana `UsuarioId` (columna estructurada, no más GUID embebido en el texto de `Descripcion`). Los 2 call sites que hoy concatenan el GUID (`VentaService.AcreditarPagoAsync`/`EliminarPagoAsync`) pasan a setear el campo estructurado y dejan de interpolar `usuarioId` en el string de `Descripcion`. `CCLocalService.ListarAsync` resuelve `UsuarioNombre` con el mismo patrón ya usado por `StockService` (traer usuarios distintos de la página a memoria, diccionar por Id — MySQL/EF Core 10 no soporta `Contains` sobre colección local). La vista muestra "{Descripcion} (por {UsuarioNombre})" cuando corresponde. **Corrección retroactiva**: script dedicado (dry-run + apply, mismo patrón ya usado en este proyecto varias veces) que busca el patrón GUID dentro de `Descripcion` de los movimientos históricos, lo resuelve contra `Users` y reemplaza el GUID por el nombre en el texto ya guardado — para que el historial también quede legible, no solo los movimientos nuevos.

**5. Origen clickeable**: nueva pantalla `Gastos/Details/{id}` (no existía — Gasto es inmutable, solo tenía Index/Create), de solo lectura (Categoría/Subcategoría/Forma de pago/Monto/Fecha/Descripción/Estado). La columna "Origen" de `CCLocal/Index.cshtml` arma el link en JS según `row.origenTipo`: `Venta` → `Ventas/Details/{origenId}`, `Gasto` → `Gastos/Details/{origenId}` — mismo patrón técnico que ya usan Cheques/PagosTarjeta (href construido en el render de la columna), pero es la primera vez que el link es condicional por tipo (esta pantalla tiene 2 orígenes posibles, no uno fijo).

**6. Filtro de mes actual + saldo filtrado**: `CCLocalController.Index` arranca con `FechaDesde`/`FechaHasta` = primer/último día del mes actual cuando no hay filtro guardado en sesión (mismo criterio que ya usa `DashboardController.Index` para su propio período por defecto). Nuevo `ICCLocalService.ObtenerSaldoFiltradoAsync(MovimientoCCLocalFiltro filtro)` — suma Ingresos menos Egresos **solo de los movimientos que matchean el filtro activo** (fecha/tipo). El card "Saldo actual" se recalcula vía AJAX cada vez que el usuario cambia el filtro (mismo evento que ya dispara el reload del DataTable). **`ObtenerSaldoActualAsync()` (el saldo histórico completo, sin filtro) no se toca** — sigue siendo el que usa el Dashboard para "Balance de caja", que debe seguir mostrando el saldo real total, no uno acotado a una selección de UI. La columna "Saldo" por fila (saldo acumulado histórico, CR-14) tampoco cambia — sigue sin ser relativa al filtro, es un concepto distinto del "Saldo actual" de la cabecera.

**Historias de usuario**:
- HU-18.5 (CR-62): Como Administrador, quiero categorizar un gasto como "Comisiones bancarias" y pagarlo como "Débito automático", para reflejar correctamente los descuentos que hace el banco solo de la cuenta.
- HU-18.6 (CR-62): Como Administrador, quiero guardar plantillas de gastos que se repiten todos los meses, para no tener que volver a tipear la categoría/forma de pago/descripción cada vez — solo el monto real y la fecha.
- HU-11.5 (CR-62): Como Administrador, quiero ver el nombre de quien acreditó un pago con tarjeta en el historial de la Cuenta Corriente Local, en vez de un identificador interno sin sentido.
- HU-11.6 (CR-62): Como Administrador, quiero poder hacer click en el origen de un movimiento de Cuenta Corriente Local para ir directo a la Venta o el Gasto que lo generó.
- HU-11.7 (CR-62): Como Administrador, quiero que la Cuenta Corriente Local arranque mostrando el mes actual y el saldo de ese período, para no tener que filtrar manualmente cada vez que entro.

**Impacto por capa**: ver detalle técnico completo en `3-arquitecto-mvc.md`, sección CR-62.

**Riesgos de implementación**: el script de corrección retroactiva de `Descripcion` toca texto ya escrito en un ledger financiero histórico — dry-run obligatorio antes de aplicar, y verificación puntual contra algunos movimientos conocidos antes de confiar el resultado masivo. La migración de `UsuarioId` es sobre una tabla de producción con volumen real (movimientos ya cargados).

## Historial de ajustes
- 2026-08-31 — CR-62 (Diseño): ver sección completa "CR-62 (Diseño) — Gastos (categoría/forma de pago/recurrentes) + Cuenta Corriente Local (usuario/origen clickeable/saldo filtrado)" más arriba. 6 puntos, 5 historias de usuario nuevas (HU-18.5/18.6/11.5/11.6/11.7). Plantillas de gasto recurrente solo prellenan el formulario (confirmado con el cliente, sin automatizar la creación ni recordar). Pendiente Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-08-27 — CR-61 (Diseño): ver sección completa "CR-61 (Diseño) — Stock: listado de productos con edición inline reemplaza Ajuste manual" más arriba. `Stock/Index` pasa a ser un listado de productos (clon de `Productos/Index.cshtml`) con Stock editable inline (guardado AJAX por celda al instante, sin motivo pedido al usuario). Movimientos se muda a `Stock/Movimientos` (link secundario). Ajuste manual se retira del código. 2 historias de usuario nuevas (HU-3.3/3.4). Reutiliza la semántica "reemplaza, no delta" de ShowroomGriffin, pero el guardado por celda AJAX es diseño nuevo (sin precedente exacto). Pendiente Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-08-27 — CR-59 (Diseño): ver sección completa "CR-59 (Diseño) — Pagos con tarjeta de crédito a liquidar" más arriba. Pantalla nueva `PagosTarjeta/Index.cshtml` (clon de `Cheques/Index.cshtml`) + card de acceso en Dashboard. Reutiliza `AcreditarPagoAsync` sin tocarlo. 3 historias de usuario nuevas (HU-9.3/9.4/9.5). Pendiente Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-08-21 — CR-55 (Diseño): ver sección completa "CR-55 (Diseño) — Nota de Crédito para anular una Factura AFIP emitida por error" más arriba. Botón "Generar Nota de Crédito" sobre factura Emitido (SweetAlert2 + motivo, mismo patrón que Cancelar OC/Rechazar cheque), reutiliza 100% el circuito AFIP ya construido. 3 historias de usuario nuevas (HU-7.6/7.7/7.8). Sin código externo reutilizable (escaneado, ningún otro proyecto tiene NC AFIP real) — se diseña sobre el propio circuito de marihogar. Pendiente Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-08-11: Diseño v9 cerrado — CR-32 (HU-5.21/5.22, precio contado/tarjeta visible + recargo real sobre el monto base cubierto por tarjeta), CR-33 (HU-5.23, edición completa de Venta bloqueada solo si ya tiene CAE real) y CR-34 (HU-5.24, acreditación diferida de tarjeta con fecha efectiva, ingreso en Caja recién al acreditar). Sobre análisis v13, 4 decisiones ya confirmadas con el cliente. Pendiente Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-07-28: Diseño v5 cerrado — CR-14 (saldo calculado en CC Local/Proveedores), CR-15 (fecha de emisión de cheque por defecto en OC), CR-16 (mayúsculas Proveedor/Producto). 4 historias de usuario nuevas (HU-11.4, HU-13.3, HU-12.9, HU-2.5). Sin wireframe nuevo.
- 2026-07-27: Diseño v4 cerrado — CR-10 (Nº comprobante en OC), CR-11 (Subcategoría de Gasto), CR-12 (Nota interna de Venta), sobre análisis v5. 3 historias de usuario nuevas (HU-12.8, HU-18.4, HU-5.13). Alcance menor, sin wireframe nuevo. Pendiente: Arquitectura y Presupuesto antes de habilitar implementación.
- 2026-07-27: Diseño v3 cerrado — Sprint CR-B (CR-8 sugerir monto de pago por defecto, CR-9 desglose facturado/no facturado en Dashboard/Caja/Proyección). Historias de usuario nuevas HU-5.12, HU-12.7, HU-9.3, HU-15.3, HU-17.3, definidas por el implementador siguiendo el mismo formato del resto del documento (alcance menor, ya presupuestado y aprobado en la adenda de `4-presupuestador.md`, sin gate de aprobación nuevo).
- 2026-07-27: Diseño v2 cerrado — change request feedback primera demo (CR-1 a CR-7). Historias de usuario nuevas HU-12.5/12.6 (OC impuestos), HU-14.5 (cheque fecha emisión), HU-5.10/5.11 (nuevas formas de pago), HU-7.5 (WhatsApp), HU-18.3 (categorías gasto), HU-Import.1 (importación histórico), HU-14.6 (acreditación manual). 1 hipótesis abierta marcada explícitamente (qué PDF se envía por WhatsApp cuando no hay Comprobante AFIP emitido) — a confirmar con el cliente antes de implementar esa parte puntual, no bloquea el resto del change request.
- 2026-07-24: Diseno funcional v1 cerrado. 18 modulos, historias de usuario completas (con criterios de aceptacion) cubriendo flujos, estados, permisos y casos de borde. Patron transversal de filtros persistidos en sesion definido. Maquinas de estado detalladas (Lead, Presupuesto, Venta, Entrega, OC, Cheque). ViewModels y wireframes textuales por pantalla. Listo para Arquitectura.
- 2026-07-24: Elevacion de estandar UX para M5 Gestion de ventas, pedido explicito del cliente por ser la pantalla de mayor uso diario del sistema. Agregadas HU-5.5 a HU-5.9 (busqueda instantanea, resumen sticky con total, edicion inline sin recarga, advertencia no bloqueante de stock, pantalla de exito con acciones siguientes) y seccion dedicada "Especificacion UX elevada — Pantalla de Ventas" con layout de dos columnas (desktop/tablet) y checkout mobile de una columna, detalle de interacciones tipo POS profesional. No afecta ViewModels ni maquina de estados ya definidos (mismo contrato funcional, mayor inversion en interaccion/presentacion). Impacto: Sprint 2 de implementacion (Presupuestos + Ventas + CC local, aun no iniciado) debe tratar Ventas con prioridad de esfuerzo superior al resto de los ABMs de ese sprint.
