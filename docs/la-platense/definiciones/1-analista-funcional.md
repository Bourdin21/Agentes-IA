# Memoria - Analista funcional

## Proyecto: La Platense (ferretería — sistema de gestión integral)
## Ultima actualizacion: 2026-07-30 (v2 — preguntas abiertas respondidas por el cliente)

## Definiciones vigentes

### Modulos/features analizados

1. **Usuarios y roles**: Admin, Vendedor, Repartidor. Cada empleado tiene usuario propio. El repartidor **ve todas las entregas** (no solo las asignadas a él) — confirmado.
2. **Catálogo de productos**: precio compra, precio venta, precio con descuento, IVA por producto (10,5%/21%), marca, modelo, categorías.
3. **Unidades de medida y conversión compra↔venta**: venta por unidad, peso, metro o bulto; hay productos comprados por bulto y vendidos por unidad. **Pieza de mayor novedad técnica del proyecto** — sin precedente exacto en el estudio (ver §6.1).
4. **Stock**: control de inventario + alertas de stock mínimo.
5. **Ventas + cuenta corriente de clientes**: venta rápida, cualquier medio de pago, fiado con seguimiento por cliente, tarjeta de crédito en 3/6 cuotas con % de recargo configurable, venta totalmente configurable (precio unitario/cantidad/subtotal/total/%IVA editables), uno o varios pagos por venta, comprobante AFIP a cliente cargado o consumidor final, edición de productos/valores antes de emitir el comprobante (workflow Borrador→Facturada). **La venta facturada admite anulación mediante nota de crédito — no queda inmutable (confirmado).**
6. **Proveedores + compras**: registro de compras con actualización automática de stock; pago a proveedores con echeck o transferencia (registrado, sin gestión de cheques diferidos propios); lista de precios por proveedor con TC propio configurable y % de descuento particular; importación de listas de precios de proveedor aplicando TC + descuento.
7. **Caja**: ingresos, egresos, cierre diario y cierre mensual (dos niveles). **Un único punto de venta/caja física — confirmado.**
8. **Gastos varios**: gastos operativos clasificados en caja chica (diarios) o caja mensual (sueldos, alquileres).
9. **Cuenta corriente propia del negocio**: vista consolidada de cierres de caja diarios/mensuales + ingresos + egresos.
10. **Cuenta corriente de empleados**: autoservicio — cada empleado ve su propio sueldo pagado y retiros, gestionado por el admin, visible solo por el propio empleado.
11. **Presupuestos y cotizaciones en PDF**: cotizar a clientes.
12. **Entregas a domicilio**: seguimiento (repartidor ve todas); markup configurable como % del valor del producto; distinción entre entrega propia y tercerizada.
13. **Cheques (30/60/90 días) — alcance reducido**: sin pagos diferidos propios; se absorbe como campo de forma de pago dentro de Compras.
14. **Aumento masivo de precios**: por categoría, proveedor o marca en un solo paso.
15. **Dashboard — "foto completa del negocio" (CONFIRMADO, pantalla más importante del sistema)**: el cliente pidió explícitamente una vista integral en base a todo el modelo de datos, priorizando diseño y estructura por sobre otras pantallas. Ver §6.4 y §6.6 — se trata como la pieza de mayor prioridad de diseño de todo el proyecto, no como un dashboard genérico de KPIs sueltos.
16. **Devoluciones de mercadería + Notas de crédito/débito AFIP (NUEVO — confirmado 2026-07-30)**: aplican devoluciones de mercadería (NO aplican cambios/canjes por otro producto). La venta facturada puede anularse mediante nota de crédito. Ver §6.5.
17. **Migración de catálogo de productos — POSPUESTA, fuera de este presupuesto (ACTUALIZADO 2026-07-30)**: se saca como etapa del presupuesto actual. Motivo: (a) el problema real que la motivaba —no tener stock confiable— ya queda resuelto por el módulo de puesta a punto de stock inicial (§6.7, dentro de Etapa 1); (b) Joaquín va a hacer un **segundo relevamiento tras la aprobación de este presupuesto** para evaluar acceso directo a la base de datos del sistema actual del cliente, lo que bajaría el costo real de importación al mínimo comparado con depender de un archivo Excel exportado de formato desconocido. Se cotiza aparte, en una fase posterior, con datos reales en mano. Ver §6.2 y `4-presupuestador.md`.
18. **Código de barras — vinculación del código escaneado al producto (NUEVO — confirmado y simplificado 2026-07-30)**: el cliente tiene una ticketeadora **manual** (no se integra con el sistema — es un aparato físico independiente que ya usa para etiquetar). El sistema solo necesita vincular el código de barras escaneado a un producto (propio o de fábrica) y agregarlo automáticamente en la pantalla de venta. **No hay desarrollo de generación/impresión de etiquetas** — eso lo sigue haciendo el cliente con su ticketeadora, fuera del sistema. Ver §6.8.

### Funcionalidad adicional detectada (no pedida explícitamente — a validar, NO incluida en presupuesto salvo confirmación)

1. ~~Devoluciones/cambios de mercadería~~ → **Resuelto**: aplican devoluciones, no cambios (ver módulo 16).
2. Reservas de stock/apartados para clientes contratistas — sigue sin confirmar.
3. ~~Notas de crédito/débito AFIP~~ → **Resuelto**: sí aplican (ver módulo 16).
4. ~~Permisos granulares de repartidor~~ → **Resuelto**: ve todas las entregas.
5. ~~Múltiples puntos de venta/cajas físicas~~ → **Resuelto**: un único punto de venta.
6. Historial de precios por producto — sigue sin confirmar.
7. Alerta de lista de precios de proveedor desactualizada — sigue sin confirmar.

### Reglas funcionales acordadas

- R1: % de recargo por cuotas de tarjeta configurable por el admin.
- R2: % de markup de envío configurable por el admin.
- R3: TC propio y % de descuento configurables por proveedor (no globales).
- R4: producto con `UnidadCompra != UnidadVenta` requiere factor de conversión definido antes de poder comprarse.
- R5: venta en estado Borrador totalmente editable; al emitir comprobante AFIP pasa a Facturada. **Una venta Facturada puede anularse mediante nota de crédito (confirmado) — no es inmutable.** Queda abierto para Diseño: quién puede iniciar la anulación (¿solo admin, o también vendedor?) y si hay límite de tiempo — ver nueva pregunta abierta en §9.
- R6: cuenta corriente de empleado visible solo por ese empleado y por el admin — ningún otro rol, ni siquiera otro vendedor.
- R7: gasto clasificado en el alta como caja chica o caja mensual, no ambos.
- R8 (nueva): devolución de mercadería reingresa stock y genera una nota de crédito vinculada a la venta original. No existe flujo de "cambio" (canje por otro producto) — es siempre devolución simple.
- R9 (nueva): el repartidor ve el listado completo de entregas, no solo las propias asignadas.
- Permisos: Admin (todo) · Vendedor (ventas, catálogo consulta, stock consulta, su propia CC) · Repartidor (entregas — todas, no solo asignadas —, su propia CC).

- R10 (nueva): el stock inicial de los productos "A" (mayor rotación/valor) se carga con conteo físico real; los productos "B/C" arrancan en stock 0 o "sin verificar" y se permite venderlos con stock en negativo durante la transición (aviso, no bloqueo), hasta que se reconcilien por conteo cíclico o por uso real.
- R11 (nueva): un producto puede tener código de barras propio (asignado por el negocio) o reutilizar el de fábrica — el campo es único, sin importar el origen. La venta permite agregar un ítem escaneando su código, sin necesidad de buscarlo manualmente.

### Criterios de aceptacion vigentes (historias de mayor riesgo/novedad)

- PF1: compra por bulto/venta por unidad descuenta stock correctamente en cada unidad de venta.
- PF2: edición de precio/cantidad/IVA/descuento de una venta antes de emitir AFIP, sin anular/recrear.
- PF3: cobro con tarjeta en 3/6 cuotas mostrando el recargo antes de confirmar.
- PF4: TC propio + % descuento de proveedor aplicados correctamente al importar su lista.
- PF5: importación de lista de precios de proveedor (Excel) sin carga manual producto por producto.
- PF6: empleado ve su propia cuenta corriente, no la de sus compañeros.
- PF7: cierre de caja diario y mensual como reportes separados.
- PF8: cuenta corriente consolidada del negocio (cierres de caja + ingresos + egresos) en una sola vista.
- PF9 (nueva): anular una venta facturada emite una nota de crédito AFIP válida, vinculada a la factura original.
- PF10 (nueva): registrar una devolución de mercadería reingresa el stock correspondiente y queda vinculada a la nota de crédito.
- PF11 (nueva): el repartidor ve el listado completo de entregas sin filtrarse por las suyas.
- PF12 (nueva): la migración de catálogo (Etapa 3) procesa ~17.000 productos con reporte de éxitos/errores, sin bloquear el sistema durante la carga.
- PF13 (nueva): un producto sin stock verificado puede venderse igual (stock queda en negativo con aviso), no bloquea la venta.
- PF14 (nueva): un empleado puede ajustar manualmente el stock de un producto con motivo, y el ajuste queda auditado (quién, cuándo, motivo).
- PF15 (nueva): al escanear el código de barras de un producto en la pantalla de venta, se agrega automáticamente al carrito (propio o de fábrica, sin distinción para el usuario).

### Supuestos y dependencias

- ~~Supuesto: un solo punto de venta/caja física~~ → **Confirmado por el cliente.**
- Supuesto: AFIP/ARCA se factura desde el arranque del proyecto (pedido explícito del cliente, no exclusión).
- **Migración de catálogo pospuesta (ya no es dependencia de este presupuesto):** se saca como etapa — se cotiza aparte más adelante, después del segundo relevamiento donde Joaquín evaluará acceso directo a la base de datos del sistema actual (ver módulo 17). No bloquea la aprobación ni el inicio de Etapa 1/Etapa 2.
- ~~Dependencia: marca/modelo de la ticketeadora~~ → **Ya no aplica: la ticketeadora es manual, no se integra con el sistema.** Solo hace falta vincular el código escaneado al producto — ver §6.8.
- Dependencia para cerrar el dashboard: el cliente pidió "foto completa del negocio en base al modelo de datos" como la pantalla más importante — se recomienda una sesión de diseño dedicada para priorizar qué KPIs van primero (ver §6.4), en vez de presuponer un set cerrado.
- ~~Dependencia: confirmar si el repartidor ve todas las entregas o solo las propias~~ → **Resuelto: ve todas.**
- ~~Dependencia: confirmar si aplican devoluciones/cambios de mercadería~~ → **Resuelto: aplican devoluciones, no cambios.**
- ~~Dependencia: confirmar si la venta facturada admite anulación/NC o queda inmutable~~ → **Resuelto: admite anulación por NC.**
- Nueva dependencia (ver §9): definir quién puede anular una venta facturada y si hay límite de tiempo para hacerlo.
- Nueva dependencia (ver §9): confirmar si el archivo de migración incluye stock actual — es un dato crítico para no arrancar el sistema nuevo con stock desactualizado.

### Exclusiones confirmadas

- Gestión de cheques diferidos propios (emitidos por el negocio) — el cliente no opera con pagos diferidos, solo echeck/transferencia como forma de pago a proveedores.
- Cambios/canjes de mercadería por otro producto — solo devolución simple.
- Reservas de stock/apartados, historial de precios por producto y alerta de lista de proveedor vencida quedan excluidos del presupuesto hasta confirmación explícita del cliente.
- Migración de catálogo de productos — pospuesta, se cotiza aparte en una fase posterior (ver módulo 17).
- Integración con hardware externo (balanzas, ticketeadora de etiquetas u otros dispositivos) — sigue excluida; el único punto de contacto con hardware es el lector de código de barras en la venta, que funciona como teclado estándar (sin integración real).

## 6. Puntos de diseño actualizados

### 6.2 Migración de catálogo — actualizado (pospuesta, fuera de este presupuesto)

Confirmado: ~17.000 productos, archivo aún no recibido. Se retira como etapa de este presupuesto: Joaquín va a hacer un segundo relevamiento tras la aprobación, para evaluar acceso directo a la base de datos del sistema actual del cliente — con eso el costo real de importación bajaría al mínimo comparado con mapear un archivo Excel de formato desconocido. Se cotiza en una fase posterior, con datos reales en mano, no como parte de este presupuesto.

### 6.4 Dashboard — actualizado (pantalla de mayor prioridad de diseño)

El cliente confirmó que el dashboard es la pantalla más importante del sistema ("foto completa del negocio en base al modelo de datos") y pidió priorizar diseño y estructura por sobre el resto. Se recomienda una sesión de diseño dedicada (no solo email) antes de cerrar el detalle final, para evitar que "foto completa" derive en scope creep indefinido. Ver propuesta estructurada en `2-disenador-funcional.md`.

### 6.5 Devoluciones + Notas de crédito/débito AFIP (nuevo módulo)

- Devolución de mercadería: reingresa stock, requiere motivo, queda vinculada a la venta original y a la nota de crédito emitida.
- Nota de crédito AFIP: extiende el servicio de facturación ya resuelto (mismo patrón WSAA/WSFE) para emitir NC vinculada al comprobante original.
- Anulación de venta facturada: transición de estado Facturada→Anulada, disparada por la emisión de una NC (no hay anulación "silenciosa" sin comprobante fiscal).
- Reutiliza el patrón de devoluciones ya resuelto en `ShowroomGriffin`.
- No hay flujo de cambio/canje (confirmado) — simplifica el alcance respecto de lo que suele pedirse en retail.

### 6.6 KPIs del dashboard — reemplaza la hipótesis anterior

Ya no se propone un set fijo de antemano — dado que el cliente lo definió como la pantalla de mayor prioridad, se define en una sesión de diseño dedicada. Punto de partida sugerido (a validar, no a asumir cerrado): ventas del día/mes, stock crítico, cobros pendientes (CC clientes), pagos pendientes (CC proveedores), gastos del mes por categoría, top productos, estado de entregas del día, saldo de caja consolidado. *La sesión de diseño debe acotar cuáles de estos (u otros) son realmente prioritarios — no construir los ocho de una sola vez sin jerarquía.*

### 6.7 Plan de puesta a punto de stock inicial (nuevo, 2026-07-30)

**Problema real declarado por el cliente:** hoy no hay stock confiable — se maneja de memoria por la rotación de artículos, y son ~17.000 productos a migrar. Ni "arrancar de cero total" ni "contar físicamente los 17.000 productos antes de arrancar" son razonables: lo primero rompe las alertas de stock mínimo desde el día 1 para todo el catálogo; lo segundo es inviable en tiempo con el equipo actual y probablemente no sería mucho más preciso que la memoria de hoy, dado el ritmo de rotación.

**Enfoque recomendado — clasificación ABC + arranque suave + reconciliación progresiva:**

1. **Clasificar productos por rotación/valor (ABC) — la hace el propio cliente (CONFIRMADO 2026-07-30), no Olvidata.** El sistema brinda la posibilidad de configurar la clasificación (campo `clasificacionABC` en el producto, editable desde el catálogo) — el cliente decide qué es "A" según su propio conocimiento del negocio, sin que Olvidata tenga que involucrarse en esa decisión comercial.
2. **Contar físicamente solo los productos "A"** antes o durante el arranque — es factible en pocos días con el equipo actual. Es donde más importa tener stock exacto (evita quiebres en lo que más se vende).
3. **Los productos "B/C" (la mayoría) arrancan en stock 0 o "sin verificar"** — el sistema debe permitir venderlos igual aunque el stock quede en negativo durante la transición (aviso, no bloqueo duro) — ver R10/PF13.
4. **Ajuste manual de stock con motivo**, disponible para cualquier empleado autorizado, para corregir sobre la marcha cuando note una diferencia real en el mostrador — reutiliza patrón ya resuelto (`ShowroomGriffin`, ajuste manual de stock) — ver PF14.
5. **Conteo cíclico post-arranque** (recomendación operativa, no funcionalidad de software): revisar una categoría por semana durante 2-3 meses hasta reconciliar el 100% del catálogo, en vez de un inventario general de una sola vez.
6. Si el archivo de migración trae una columna de stock, se importa como **punto de partida de referencia, no como dato confiable** — mismo criterio que si no la trajera, dado que el cliente ya advirtió que no confía en ese número hoy.

**Qué es desarrollo y qué es proceso del cliente:** los puntos 1 (clasificación ABC), 2 (conteo físico) y 5 (conteo cíclico) son trabajo operativo del propio negocio — el cliente decide y ejecuta, no llevan horas de desarrollo por sí mismos. Lo que sí es desarrollo es que el sistema **permita configurar** esa clasificación (campo editable) y sostener el resto del flujo — puntos 3, 4 y 6 — ver el módulo ampliado de Stock (Etapa 1) en `4-presupuestador.md`. *Nota: al sacarse la migración como etapa de este presupuesto, la funcionalidad de ajuste manual de stock queda como el mecanismo principal (no complementario) para que el cliente construya un stock confiable desde el arranque.*

### 6.8 Código de barras — vinculación al producto + lectura en venta (módulo simplificado, 2026-07-30)

- **La ticketeadora es manual (confirmado por el cliente)** — no se integra con el sistema, no hay generación/impresión de etiquetas de por medio. El cliente sigue etiquetando físicamente por su cuenta, igual que hoy.
- **Lo único que necesita el sistema**: vincular el código de barras (propio o de fábrica) al producto en el catálogo, y en la pantalla de venta, un campo que detecte el escaneo (lector USB tipo teclado, sin driver especial) y agregue el producto automáticamente al carrito.
- Esto redujo bastante el alcance de este módulo respecto de la versión anterior (que asumía integración con una impresora de etiquetas) — ver `4-presupuestador.md`.

## 9. Preguntas abiertas (actualizado)

1. ~~¿La venta facturada admite anulación/nota de crédito?~~ → **Cerrada: sí, admite anulación por NC.**
2. ~~¿Cuál es el archivo/formato real del catálogo?~~ → **Ya no aplica a este presupuesto: la migración se saca como etapa y se cotiza aparte más adelante (ver módulo 17).**
3. ~~¿Uno o varios puntos de venta/cajas físicas?~~ → **Cerrada: uno solo.**
4. ~~¿El repartidor ve todas las entregas o solo las asignadas?~~ → **Cerrada: ve todas.**
5. ~~¿Aplican devoluciones/cambios de mercadería?~~ → **Cerrada: aplican devoluciones, no cambios.**
6. ~~¿Set exacto de KPIs del dashboard?~~ → **Cerrada parcialmente: se define en sesión de diseño dedicada, no por email — ver §6.6.**
7. **(Nueva)** ¿Quién puede iniciar la anulación de una venta facturada — solo el admin, o también el vendedor? ¿Hay un límite de tiempo (ej. solo el mismo día)?
8. ~~¿El archivo de migración de catálogo va a incluir el stock actual?~~ → **Ya no aplica: la migración se pospone, se resuelve cuando se cotice esa fase futura.**
9. ~~¿Quién define la clasificación ABC de productos?~~ → **Cerrada: la hace el cliente por su cuenta. El sistema solo brinda la posibilidad de configurarla (campo editable en el catálogo).**
10. ~~¿Marca/modelo de la ticketeadora?~~ → **Cerrada: ya no aplica — la ticketeadora es manual, no se integra con el sistema.**

## Historial de ajustes
- 2026-07-30: Análisis v1 creado post-relevamiento presencial en La Platense.
- 2026-07-30 (v2): el cliente respondió las 6 preguntas abiertas de la v1. Cambios de alcance resultantes: (a) nuevo módulo "Devoluciones + Notas de crédito/débito AFIP" (venta facturada anulable por NC, devoluciones sin cambios); (b) migración de catálogo confirmada en ~17.000 productos, formato aún no recibido, promovida a **Etapa 3 independiente** del presupuesto por pedido explícito del cliente; (c) dashboard confirmado como pantalla de mayor prioridad de diseño ("foto completa del negocio"), ya no un KPI-set genérico; (d) confirmado un único punto de venta/caja y que el repartidor ve todas las entregas (sin cambio de esfuerzo, solo cierre de incertidumbre). Surgieron 2 preguntas nuevas (quién anula una venta facturada y si el archivo de migración trae stock).
- 2026-07-30 (v3): agregado el plan de puesta a punto de stock inicial (§6.7) — el cliente confirmó que hoy no hay stock confiable (se maneja de memoria). Enfoque recomendado: clasificación ABC + conteo físico solo de los productos de mayor rotación/valor + arranque suave (stock negativo permitido, con aviso) para el resto + ajuste manual con motivo + conteo cíclico post-arranque. La pregunta abierta #8 deja de ser bloqueante. Nueva pregunta abierta #9 (quién hace la clasificación ABC). Impacto en presupuesto: Stock (Etapa 1) ampliado con ajuste manual/flag de venta con stock negativo; Etapa 3 suma la extensión del importador para aceptar conteo real como columna opcional — ver `4-presupuestador.md`.
- 2026-07-30 (v4): cerrada la pregunta #9 — **la clasificación ABC la hace el propio cliente**, no Olvidata; el sistema solo brinda la posibilidad de configurarla (campo editable en el catálogo). No cambia el esfuerzo estimado (ya estaba contemplado como campo simple en `Producto`), solo cierra la incertidumbre de proceso.
- 2026-07-30 (v5): dos cambios de alcance importantes. (a) **Se agrega el módulo "Código de barras — etiquetado con ticketeadora + lectura en venta"** (§6.8): el cliente tiene una ticketeadora física y códigos de barra propios además de los de fábrica; el sistema debe poder imprimir etiquetas y agregar productos a la venta por escaneo. Nueva pregunta abierta sobre marca/modelo de la ticketeadora (define si es integración simple o requiere protocolo propietario). (b) **Se saca la migración de catálogo como etapa de este presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de puesta a punto de stock inicial (Etapa 1), y Joaquín va a evaluar en un segundo relevamiento el acceso directo a la base de datos actual del cliente para bajar el costo real de importación; se cotiza aparte, más adelante. Impacto en el presupuesto: ver `4-presupuestador.md` — el nuevo módulo de código de barras (bajo reuse) hizo caer el ratio de reutilización de Etapa 1+2 por debajo del 70%, pasando de Tier 1 a **Tier 2**.
- 2026-07-30 (v6): Joaquín aclaró que **la ticketeadora es manual** — no se integra con el sistema. Se simplifica el módulo de código de barras a solo vincular el código escaneado al producto (sin generación/impresión de etiquetas). Se cierra la pregunta abierta #10 (marca/modelo, ya no aplica). Impacto en presupuesto: módulo de código de barras baja de 7h a 3h — ver `4-presupuestador.md` para el efecto en el ratio de reutilización y el precio final (Joaquín además fijó el precio a cobrar en USD 1.800, con su propia estimación de 30h reales + USD 200 de tokens IA).
