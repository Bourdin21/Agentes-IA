# Memoria - Disenador funcional

## Proyecto: marihogar
## Ultima actualizacion: 2026-07-24

## Definiciones vigentes

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

## Historial de ajustes
- 2026-07-24: Diseno funcional v1 cerrado. 18 modulos, historias de usuario completas (con criterios de aceptacion) cubriendo flujos, estados, permisos y casos de borde. Patron transversal de filtros persistidos en sesion definido. Maquinas de estado detalladas (Lead, Presupuesto, Venta, Entrega, OC, Cheque). ViewModels y wireframes textuales por pantalla. Listo para Arquitectura.
- 2026-07-24: Elevacion de estandar UX para M5 Gestion de ventas, pedido explicito del cliente por ser la pantalla de mayor uso diario del sistema. Agregadas HU-5.5 a HU-5.9 (busqueda instantanea, resumen sticky con total, edicion inline sin recarga, advertencia no bloqueante de stock, pantalla de exito con acciones siguientes) y seccion dedicada "Especificacion UX elevada — Pantalla de Ventas" con layout de dos columnas (desktop/tablet) y checkout mobile de una columna, detalle de interacciones tipo POS profesional. No afecta ViewModels ni maquina de estados ya definidos (mismo contrato funcional, mayor inversion en interaccion/presentacion). Impacto: Sprint 2 de implementacion (Presupuestos + Ventas + CC local, aun no iniciado) debe tratar Ventas con prioridad de esfuerzo superior al resto de los ABMs de ese sprint.
