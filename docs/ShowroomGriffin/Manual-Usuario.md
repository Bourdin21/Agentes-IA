# Manual de Usuario
## Sistema de Gestión Comercial — Showroom Griffin

**Cliente:** Ulises
**Versión:** 1.0
**Fecha:** 2026-01-15
**Destinatarios:** Administrador del negocio y vendedores del local.

---

## Índice

1. [Primeros pasos](#1-primeros-pasos)
2. [Perfiles de usuario y qué puede hacer cada uno](#2-perfiles-de-usuario)
3. [Pantalla principal (Dashboard)](#3-pantalla-principal-dashboard)
4. [Maestros: categorías, subgrupos, clientes, proveedores, tipos de precio](#4-maestros)
5. [Productos y variantes](#5-productos-y-variantes)
6. [Stock e inventario](#6-stock-e-inventario)
7. [Compras a proveedores](#7-compras-a-proveedores)
8. [Ventas a clientes](#8-ventas-a-clientes)
9. [Devoluciones y cambios](#9-devoluciones-y-cambios)
10. [Resumen semanal de transferencias](#10-resumen-semanal-de-transferencias)
11. [Aumento masivo de precios](#11-aumento-masivo-de-precios)
12. [Buenas prácticas y preguntas frecuentes](#12-buenas-prácticas-y-preguntas-frecuentes)
13. [Glosario](#13-glosario)
14. [Datos de soporte](#14-datos-de-soporte)

---

## 1. Primeros pasos

### Cómo ingresar al sistema
1. Abrí el navegador (Chrome, Edge o Firefox actualizados).
2. Ingresá a la dirección que te entregamos para el local.
3. Vas a ver la pantalla de **Inicio de sesión**.
4. Escribí tu correo y contraseña.
5. Hacé clic en **Ingresar**.

### Si olvidaste la contraseña
Por seguridad, la recuperación de contraseña en esta versión la realiza el Administrador desde **Usuarios → Editar**. Pedile a Ulises (o a quien tenga el rol Administrador) que te asigne una nueva.

### Cerrar sesión
Hacé clic en tu nombre arriba a la derecha → **Cerrar sesión**. Es importante cerrar sesión cuando termines de usar el sistema, especialmente si la computadora es compartida.

### Cómo está organizada la pantalla
- **Barra superior**: tu nombre, perfil y opción de cerrar sesión.
- **Menú lateral izquierdo**: módulos disponibles (cambia según tu perfil).
- **Área central**: el contenido del módulo que abriste.

---

## 2. Perfiles de usuario

El sistema tiene tres perfiles. Cada uno ve solo las funciones que necesita.

| Perfil | Para quién | Qué puede hacer |
|---|---|---|
| **Súper Usuario** | Soporte técnico (Olvidata) | Todo lo del Administrador + gestión avanzada. |
| **Administrador** | Ulises | Toda la operación del negocio: configuración, productos, compras, ventas, reportes, aumentos. |
| **Vendedor** | Personal del local | Vender, registrar devoluciones, consultar stock y clientes. **No** ve costos, ganancias, compras ni reportes. |

**Importante**: el Vendedor nunca ve el costo de un producto ni la ganancia de una venta. Esto está garantizado por el sistema en todas las pantallas.

---

## 3. Pantalla principal (Dashboard)

Al ingresar, lo primero que vas a ver es el panel principal. El contenido depende de tu perfil.

### Si sos Administrador
- Ventas del día, semana y mes con su total.
- Compras pendientes de recepcionar.
- Productos con stock por debajo del mínimo.
- Últimas ventas registradas.
- Ingresos por medio de pago (efectivo, tarjeta, cuotas, transferencia).

### Si sos Vendedor
- Tus ventas del día (las que hiciste vos).
- Tus últimas ventas.
- Alertas de stock bajo.

> Los datos se muestran al momento de abrir el dashboard. Si querés actualizar, refrescá la página.

---

## 4. Maestros

Los **maestros** son los datos base que después usás en compras, ventas y productos. Conviene tenerlos cargados antes de operar.

### Acceso
Menú → **Maestros**. Solo el Administrador puede crear, editar o inactivar; el Vendedor solo puede ver clientes.

### 4.1 Categorías
Son los grandes grupos de productos. En este sistema hay dos tipos especiales: **Ropa** y **Zapatillas**, porque cambian los datos que se piden por variante.

- **Crear**: nombre + descripción opcional.
- **Editar**: cambiá el nombre o la descripción.
- **Inactivar**: si la categoría tiene productos activos, el sistema **no permite** inactivarla y muestra un aviso.

### 4.2 Subgrupos
Son subdivisiones dentro de una categoría (ej: Remeras, Buzos dentro de Ropa).
- Cada subgrupo pertenece a **una sola** categoría.

### 4.3 Clientes
- Datos básicos: nombre, teléfono, email, dirección, CUIT (opcional, formato XX-XXXXXXXX-X).
- **Vendedor solo lectura**: el vendedor puede buscar y ver el listado pero no editar.
- **Inactivar**: si el cliente tiene ventas registradas, el sistema **no permite** inactivarlo.

### 4.4 Proveedores
- Razón social, CUIT (opcional), contacto, teléfono, email.
- Solo Administrador.

### 4.5 Tipos de precio para zapatillas
- Sirven para diferenciar precios por gama (ej: Premium, Standard, Outlet).
- Tienen un margen de ganancia de referencia (%).

---

## 5. Productos y variantes

### Concepto importante
Un **producto** es la prenda o calzado en general (ej: "Remera básica"). Una **variante** es la combinación específica que efectivamente se vende y se controla por stock (ej: Remera básica – Talle M – Color negro).

**El stock se controla por variante, no por producto.**

### Crear un producto (Administrador)
1. Menú → **Productos** → **Nuevo**.
2. Completá:
   - Nombre (ej: "Buzo canguro").
   - Descripción.
   - Categoría (Ropa o Zapatillas u otra).
   - Subgrupo (opcional).
3. Guardar.

### Crear una variante
Dentro del producto:
1. **Agregar variante**.
2. El formulario se adapta según la categoría:
   - **Ropa**: Talle, Color, Marca, Género, Temporada.
   - **Zapatillas**: Color, Marca, Número, Modelo, Tipo de precio.
3. **Precio de venta** (obligatorio).
4. **SKU** y **Código de barra** (opcionales, pero si se cargan deben ser únicos).
5. **Stock mínimo** (opcional; sirve para alertas).
6. Guardar.

### Lo que el sistema controla por vos
- Si repetís un SKU o código de barra, te avisa.
- Si querés inactivar una variante con stock mayor a 0, **no te deja** y muestra un mensaje.
- El **último precio de compra** se actualiza automáticamente cuando recibís una compra (no se carga a mano).

### Vista para Vendedor
El vendedor ve los productos pero **sin** las columnas de costo ni ganancia. Solo ve precio de venta y stock.

---

## 6. Stock e inventario

### Cómo se actualiza el stock
El sistema actualiza solo el stock en cada operación:
- **Carga inicial** (manual, una vez por variante nueva).
- **Compra recepcionada** (suma).
- **Venta confirmada** (resta).
- **Anulación de venta** (devuelve).
- **Devolución de cliente** (suma).
- **Cambio** (resta del nuevo, suma del devuelto).
- **Ajuste manual** (Administrador, con motivo).
- **Devolución a proveedor** (resta).

Todo movimiento queda registrado y se puede consultar el historial completo de cualquier variante.

### Carga inicial
Cuando agregás una variante nueva, el stock arranca en 0. Para cargar el stock inicial:
1. Menú → **Stock** → buscar la variante.
2. Botón **Carga inicial** (solo Administrador).
3. Ingresar cantidad (>0) y guardar.

> Solo se permite carga inicial **una vez** por variante. Después hay que usar Compra o Ajuste manual.

### Ajuste manual
Para corregir diferencias detectadas en un conteo físico:
1. Menú → **Stock** → buscar la variante.
2. Botón **Ajustar**.
3. Ingresar la cantidad real, motivo del ajuste y guardar.
4. El sistema registra cantidad anterior, nueva y motivo en el historial.

### Alertas de stock bajo
Si una variante tiene `stock actual ≤ stock mínimo`, aparece resaltada en el listado. Sirve para detectar reposiciones.

### Historial de movimientos
En el detalle de una variante hay una solapa **Historial**. Muestra cada movimiento con: fecha, tipo, cantidad, stock anterior, stock resultante y referencia (a qué venta/compra/ajuste corresponde).

---

## 7. Compras a proveedores

Solo Administrador.

### El flujo de una compra tiene 4 estados
```
Borrador  →  En Proceso  →  Verificada  →  Recibida
(editable)   (editable)    (revisión)     (mercadería ingresada)
```
**El flujo es lineal**: no se puede retroceder de estado.

### Crear una compra
1. Menú → **Compras** → **Nueva**.
2. Seleccionar proveedor y fecha.
3. Agregar líneas de detalle: variante, cantidad, costo unitario.
4. Guardar como **Borrador** (queda editable).

### Avanzar de estado
- **Borrador → En Proceso**: cuando confirmás el pedido al proveedor.
- **En Proceso → Verificada**: cuando llegó la mercadería y revisaste el remito.
- **Verificada → Recibida**: al ingresarla efectivamente al stock (recepción).

Cada cambio de estado pide confirmación.

### Recepción (paso clave)
Al pasar de Verificada a Recibida, el sistema te abre la pantalla de recepción. Por cada línea pedida, completás:
- **Cantidad recibida**: la que efectivamente llegó.
- **Cantidad dañada**: rota o defectuosa (no entra a stock).
- **Cantidad devuelta al proveedor**: la que rechazás (no entra a stock).

**Regla obligatoria**: Recibida + Dañada + Devuelta ≤ Pedida (por cada línea).

Al confirmar:
- Solo la **cantidad recibida** suma stock.
- El **último precio de compra** de cada variante se actualiza con el costo de la línea.
- Si alguna línea tiene un error, no se aplica nada (la operación es total o nada).

### Adjuntos
Podés adjuntar archivos (foto del remito, factura PDF) en cualquier estado. Límite: 5 MB por archivo.

### Edición
- En **Borrador** y **En Proceso**: editable.
- En **Verificada** y **Recibida**: solo lectura.

---

## 8. Ventas a clientes

Esta es la pantalla más usada. Funciona como un carrito de una sola página.

### Crear una venta
1. Menú → **Ventas** → **Nueva**.
2. **Sección 1 — Encabezado**:
   - Cliente (opcional, podés vender sin cliente si es consumidor final).
   - Observaciones.
3. **Sección 2 — Productos**:
   - Buscá la variante por nombre, SKU o código de barra (búsqueda inteligente).
   - Al elegirla, el sistema te muestra el stock disponible.
   - Ingresá cantidad y agregá al carrito.
   - El subtotal y el total se recalculan en vivo.
   - Repetí por cada producto.
4. **Sección 3 — Medios de pago**:
   - Botón **Agregar medio de pago**.
   - Opciones: Efectivo, Tarjeta, Cuotas, Transferencia.
   - Si elegís **Cuotas**, te pide cantidad de cuotas (≥2) y porcentaje de financiamiento.
   - Indicás el monto de cada medio.
   - El sistema te indica visualmente cuánto falta asignar (`Resta por asignar: $X`).
5. **Sección 4 — Confirmar**:
   - Revisá el resumen.
   - Botón **Confirmar venta** con confirmación.

### Lo que el sistema valida al confirmar
- Que haya al menos un producto.
- Que la suma de los medios de pago sea **exactamente igual** al total de la venta.
- Que haya stock suficiente para cada variante (si dos personas venden la misma última unidad, **solo una venta se confirma**, la otra recibe un aviso de stock insuficiente).
- Si hay error, **no se descuenta stock ni se crea la venta**.

### Número de venta
Cada venta recibe un número correlativo automático. No se puede repetir.

### Estados de una venta
```
Confirmada  →  Entregada
	 ↓
   Anulada
```

- **Confirmada**: al crearla. Ya descontó stock.
- **Entregada**: cuando el cliente se llevó la mercadería (botón **Marcar entregada**).
- **Anulada**: cancelación. Se puede anular **solo si está Confirmada**, no si ya fue Entregada. Al anular, el stock vuelve a quedar disponible.

> Si la venta ya está Entregada y el cliente quiere devolver, hay que usar el módulo de **Devoluciones**, no anular.

### Generar remito PDF
En el detalle de la venta, botón **Emitir remito**. Descarga un PDF con:
- Datos del local.
- Número y fecha de venta.
- Cliente.
- Detalle de productos.
- Medios de pago.
- Total.

### Adjuntar comprobante
Podés adjuntar comprobantes de transferencia o vouchers. Límite 5 MB por archivo.

### Vista para Vendedor
- Ve solo sus propias ventas en el listado.
- En el detalle no ve costos ni ganancias.

---

## 9. Devoluciones y cambios

El asistente tiene 4 pasos. Sirve para devolver dinero o cambiar productos.

### Cuándo se puede usar
Solo se puede registrar una devolución sobre una venta que esté **Confirmada** o **Entregada** (no sobre Anulada).

### Paso 1 — Seleccionar la venta
Buscá la venta por número o cliente. El sistema te muestra el resumen.

### Paso 2 — Items a devolver
Por cada línea de la venta, el sistema indica cuánto se vendió y cuánto ya fue devuelto en operaciones anteriores. Vos cargás cuánto querés devolver ahora.
- **Regla**: cantidad a devolver ≤ vendida − devoluciones previas.
- Tenés que escribir un **motivo** (texto libre, máx. 500 caracteres).

### Paso 3 — Tipo de operación
- **Devolución de dinero**: el cliente recibe la plata, los productos vuelven a stock. Fin.
- **Cambio por igual valor**: cliente entrega productos y recibe otros del mismo valor total. Hay que seleccionar los productos nuevos.
- **Cambio por mayor valor**: cliente entrega productos, recibe otros más caros y paga la diferencia. Hay que seleccionar los nuevos, el sistema calcula la diferencia y vos indicás el medio de pago.

### Paso 4 — Confirmar
El asistente te muestra el resumen completo (qué se devuelve, qué se entrega nuevo, qué diferencia hay). Confirmás.

### Lo que hace el sistema automáticamente
- Reingresa stock de los productos devueltos.
- Si es cambio, descuenta stock de los productos nuevos (validando que haya).
- Si es cambio de mayor valor, registra el pago de la diferencia.
- Si algo falla, no se aplica nada (operación atómica).

---

## 10. Resumen semanal de transferencias

Solo Administrador. Sirve para conciliar pagos por transferencia.

### Cómo se usa
1. Menú → **Resumen semanal**.
2. Elegí una fecha cualquiera. El sistema arma el período **lunes a domingo** de esa semana.
3. Se listan únicamente las ventas pagadas por **transferencia** que estén Confirmadas o Entregadas.
4. Se muestra: nro de venta, fecha, cliente, importe, agrupado por día y con total semanal.
5. Botón **Exportar Excel** descarga la planilla con totales y formato listo para revisar.

### Qué no incluye
- Ventas pagadas con efectivo, tarjeta o cuotas.
- Ventas anuladas o en borrador.

---

## 11. Aumento masivo de precios

Solo Administrador. Sirve para subir precios en lote.

### Flujo
1. Menú → **Aumento masivo**.
2. **Filtros**: elegí por categoría, subgrupo, marca o sin filtros (todas las variantes).
3. Ingresá el **porcentaje** de aumento (ej: 15%).
4. Botón **Previsualizar**: se muestra una tabla con cada variante, el precio actual y el precio nuevo.
5. **Excluir variantes** que no querés aumentar (desmarcando la casilla).
6. Botón **Aplicar** con confirmación → el sistema actualiza todos los precios seleccionados en un solo paso.

### Reglas
- El porcentaje debe ser mayor a 0 y menor o igual a 500% (protección anti-error de tipeo).
- Los precios nuevos se redondean a 2 decimales.

### Importante: trabajo simultáneo
Si dos personas abren la pantalla al mismo tiempo y modifican los mismos productos, **solo el primero aplica**. El segundo recibe un mensaje pidiéndole que vuelva a previsualizar. Esto evita pisar precios accidentalmente.

---

## 12. Buenas prácticas y preguntas frecuentes

### Buenas prácticas
- **Cerrá sesión** al terminar tu turno.
- **Cargá los maestros antes de operar** (categorías, subgrupos, proveedores, clientes).
- **Conteo físico mensual** + ajuste manual con motivo, en lugar de tocar carga inicial.
- **Generá el remito** desde el sistema en lugar de hacerlo a mano.
- **Adjuntá comprobantes de transferencia** dentro de la venta para tener todo en un solo lugar.
- **Antes de un aumento masivo**, hacé previsualización y revisá.

### Preguntas frecuentes

**¿Puedo deshacer una venta?**
Si está **Confirmada** y aún no se entregó, sí: usá **Anular**. Si ya está **Entregada**, no se anula: usá **Devoluciones**.

**¿Por qué no me deja inactivar un cliente?**
Porque tiene ventas asociadas. El sistema preserva el historial. Si querés "quitarlo del medio", podés cambiarle el nombre o dejarlo inactivo desde otro flujo.

**¿Por qué no me deja inactivar una variante?**
Porque tiene stock mayor a 0. Primero hay que llevar el stock a 0 (vendiéndola, ajustando o devolviéndola al proveedor).

**¿El stock puede quedar negativo?**
No. El sistema bloquea cualquier operación que dejaría stock negativo.

**¿Qué pasa si dos vendedores venden la misma última unidad al mismo tiempo?**
Solo se confirma una venta. La otra recibe un mensaje claro de stock insuficiente y no afecta el sistema. Si hay mucha contención (muchos accesos simultáneos), el sistema reintenta automáticamente unas veces antes de mostrar el mensaje.

**¿Quién puede ver costos y ganancias?**
Solo el Administrador y el Súper Usuario. Los Vendedores nunca, en ninguna pantalla.

**¿Cómo sé qué movimientos afectaron el stock de un producto?**
En el detalle de la variante, solapa **Historial**. Muestra todo desde la carga inicial.

**¿Puedo subir un archivo Word o un Excel como adjunto a una compra/venta?**
Se aceptan los formatos habituales (imagen, PDF). El límite es 5 MB. Otros formatos pueden ser rechazados.

**¿Me puedo conectar desde mi celular?**
Sí, el sistema es web y se ve correctamente en celulares modernos. Para operaciones largas (cargar una compra de muchas líneas) se recomienda PC o tablet.

---

## 13. Glosario

- **Variante**: combinación específica de un producto (ej: talle, color) que se vende y controla por stock individualmente.
- **SKU**: código interno opcional de la variante.
- **Stock mínimo**: cantidad por debajo de la cual el sistema avisa (alerta visual).
- **Recepción**: acto de ingresar al stock la mercadería de una compra.
- **Anular** (venta): cancelar una venta Confirmada y devolver el stock.
- **Devolución**: el cliente devuelve mercadería; reingresa stock.
- **Cambio**: el cliente entrega mercadería y recibe otra (mismo o mayor valor).
- **Carrito**: pantalla de venta donde se agregan los productos en una sola página.
- **Soft delete**: cuando "inactivás" algo, no se borra de verdad. Queda guardado para preservar el historial.

---

## 14. Datos de soporte

**Soporte técnico:** Olvidata Soft
**Email:** olvidatasoft@gmail.com
**Documentación interna:** este manual + reportes técnicos del proveedor.

### Antes de pedir soporte, verificá
1. ¿Estás conectado a internet?
2. ¿Refrescaste la página?
3. ¿Probaste cerrar sesión y volver a entrar?
4. ¿Probaste otro navegador (Chrome o Edge actualizados)?

### Para pedir soporte, mandá
- Tu correo de usuario.
- Qué módulo y pantalla estabas usando.
- Qué intentaste hacer.
- El mensaje de error completo (captura de pantalla preferentemente).
- Aproximadamente la fecha y hora.

---

> **Versión 1.0 — borrador inicial.** Este manual se ajustará tras la sesión de capacitación con el equipo y las pruebas finales con datos reales.
