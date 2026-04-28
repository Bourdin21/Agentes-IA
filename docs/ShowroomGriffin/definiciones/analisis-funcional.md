# Análisis Funcional
## Sistema de Gestión Comercial — Indumentaria y Calzado

**Cliente:** Ulises  
**Proveedor:** OlvidataSoft  
**Versión:** 1.1  
**Estado:** Análisis funcional cerrado — listo para handoff a Diseño  

---

## 1. Contexto y Objetivo

### 1.1 Contexto

El cliente "Ulises" opera un comercio de indumentaria y calzado. Actualmente gestiona sus operaciones de forma manual o con planillas. Necesita un sistema web que centralice la gestión de productos, stock, compras a proveedores, ventas a clientes, devoluciones/cambios, y reportes financieros.

### 1.2 Objetivo

Desarrollar un sistema de gestión comercial web (MVC, .NET 10, MySQL) que permita:

1. Administrar catálogos de productos (ropa y zapatillas) con variantes.
2. Controlar stock con trazabilidad de movimientos.
3. Gestionar compras a proveedores con flujo de estados y recepción parcial.
4. Registrar ventas con carrito dinámico, múltiples medios de pago y cuotas.
5. Procesar devoluciones y cambios con wizard guiado.
6. Generar remitos PDF, resúmenes semanales y aumentos masivos de precios.
7. Diferenciar roles (Administrador / Vendedor) con ocultamiento de costos y ganancias para vendedores.

### 1.3 Alcance

- **9 módulos funcionales + Dashboard.**
- **20 entidades de dominio.**
- **5 enums.**
- **3 roles:** SuperUsuario (existente), Administrador, Vendedor.
- **Estimación:** ~29 horas base — USD 500.

---

## 2. Actores del Sistema

| Actor | Rol | Descripción |
|---|---|---|
| SuperUsuario | SuperUsuario | Rol técnico existente. Acceso total al sistema incluida auditoría y configuración. |
| Administrador | Administrador | Gestión completa: maestros, productos, stock, compras, ventas, devoluciones, reportes, precios. Ve costos y ganancias. |
| Vendedor | Vendedor | Operaciones de venta y consulta limitada. **No ve** costos de compra, márgenes ni ganancias. No accede a compras, ajustes de stock, aumento masivo ni resumen semanal. |

### Matriz de acceso general

| Módulo | SuperUsuario | Administrador | Vendedor |
|---|---|---|---|
| Seguridad y Acceso | ✅ | ✅ (sin gestión de SuperUsuarios) | ❌ (solo perfil propio) |
| Maestros Comerciales | ✅ | ✅ | 👁️ (solo lectura Clientes) |
| Productos y Variantes | ✅ | ✅ | 👁️ (sin costos) |
| Stock e Inventario | ✅ | ✅ | 👁️ (consulta, sin ajuste) |
| Compras a Proveedores | ✅ | ✅ | ❌ |
| Ventas a Clientes | ✅ | ✅ | ✅ (sin costos en detalle) |
| Devoluciones y Cambios | ✅ | ✅ | ✅ |
| Resumen Semanal | ✅ | ✅ | ❌ |
| Aumento Masivo | ✅ | ✅ | ❌ |
| Dashboard | ✅ | ✅ | ✅ (versión limitada) |

---

## 3. Casos de Uso (índice maestro)

| ID | Caso de uso | Actor primario | Módulo |
|---|---|---|---|
| CU-01 | Iniciar sesión y navegar según rol | Admin / Vendedor | Seguridad |
| CU-02 | Editar perfil propio (nombre, contraseña) | Cualquier usuario | Seguridad |
| CU-03 | Gestionar usuarios y asignar roles | Admin | Seguridad |
| CU-04 | ABM Categorías / Subgrupos / Proveedores / TipoPrecioZapatilla | Admin | Maestros |
| CU-05 | ABM Clientes (Vendedor solo lectura) | Admin / Vendedor | Maestros |
| CU-06 | Crear/editar producto y variantes con campos dinámicos por tipo | Admin | Productos |
| CU-07 | Consultar catálogo (sin costos para Vendedor) | Admin / Vendedor | Productos |
| CU-08 | Carga inicial de stock por variante | Admin | Stock |
| CU-09 | Ajuste manual de stock con motivo | Admin | Stock |
| CU-10 | Consultar historial de movimientos de stock | Admin / Vendedor | Stock |
| CU-11 | Visualizar alertas de stock bajo | Admin / Vendedor | Stock |
| CU-12 | Crear orden de compra a proveedor (Borrador) | Admin | Compras |
| CU-13 | Avanzar estado de compra (Borrador → EnProceso → Verificada → Recibida) | Admin | Compras |
| CU-14 | Recepcionar compra con cantidades Recibida/Dañada/Devuelta | Admin | Compras |
| CU-15 | Adjuntar comprobantes a compra | Admin | Compras |
| CU-16 | Registrar venta con carrito AJAX y múltiples medios de pago | Admin / Vendedor | Ventas |
| CU-17 | Marcar venta como Entregada | Admin / Vendedor | Ventas |
| CU-18 | Anular venta Confirmada (repone stock) | Admin / Vendedor | Ventas |
| CU-19 | Generar remito PDF | Admin / Vendedor | Ventas |
| CU-20 | Adjuntar comprobante a venta | Admin / Vendedor | Ventas |
| CU-21 | Procesar devolución de dinero (wizard 4 pasos) | Admin / Vendedor | Devoluciones |
| CU-22 | Procesar cambio mismo valor | Admin / Vendedor | Devoluciones |
| CU-23 | Procesar cambio mayor valor con diferencia y medio de pago | Admin / Vendedor | Devoluciones |
| CU-24 | Generar resumen semanal de transferencias y exportar a Excel | Admin | Resumen Semanal |
| CU-25 | Aplicar aumento masivo de precios con preview y exclusiones | Admin | Aumento Masivo |
| CU-26 | Visualizar dashboard según rol | Admin / Vendedor | Dashboard |

---

## 4. Análisis por Módulo

---

### MÓDULO 1 — Seguridad y Acceso

**Descripción:** Autenticación y gestión de usuarios con roles diferenciados. El módulo base ya existe en ShowroomGriffin (AccountController, UsersController). Se requiere agregar el rol "Vendedor" y ajustar la visibilidad del sidebar.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-SEG-01 | Roles disponibles | SuperUsuario, Administrador, Vendedor. |
| R-SEG-02 | Creación de usuarios | Solo Administrador y SuperUsuario pueden crear usuarios. |
| R-SEG-03 | Asignación de rol | Administrador solo puede crear Administrador o Vendedor. SuperUsuario puede crear cualquier rol. |
| R-SEG-04 | Sidebar dinámico | Los ítems del menú lateral se ocultan según rol del usuario logueado. |
| R-SEG-05 | Perfil propio | Todo usuario puede editar su propio nombre y contraseña. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar usuarios | ✅ | ❌ |
| Crear usuario | ✅ | ❌ |
| Editar usuario | ✅ | ❌ |
| Inactivar usuario | ✅ | ❌ |
| Editar perfil propio | ✅ | ✅ |

#### Validaciones

- Email único por usuario.
- Contraseña mínima 6 caracteres.
- No se puede inactivar al propio usuario logueado.

#### Criterios de aceptación

- [ ] El rol Vendedor existe en el seed de datos.
- [ ] El sidebar muestra solo los módulos permitidos según rol.
- [ ] Un Vendedor no puede acceder a la gestión de usuarios (retorna 403).

---

### MÓDULO 2 — Maestros Comerciales

**Descripción:** ABMs de las entidades de soporte: Categorías, Subgrupos, Clientes, Proveedores y Tipos de Precio Zapatilla.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-MAE-01 | Categoría única | El nombre de la categoría debe ser único (case-insensitive). |
| R-MAE-02 | Subgrupo pertenece a categoría | Todo subgrupo tiene exactamente una categoría padre. |
| R-MAE-03 | Cascada categoría → subgrupo | Al seleccionar categoría en formularios de producto, los subgrupos se filtran por AJAX. |
| R-MAE-04 | Soft delete maestros | Inactivar un maestro no lo elimina físicamente. Se aplica soft delete (`DeletedAt`). |
| R-MAE-05 | Maestro con dependencias | No se puede inactivar una categoría que tiene productos activos. Mostrar mensaje de error. |
| R-MAE-06 | Vendedor solo consulta clientes | El vendedor puede ver el listado de clientes pero no crear, editar ni inactivar. |
| R-MAE-07 | CUIT opcional | El CUIT de clientes y proveedores es opcional. Si se ingresa, debe tener formato válido (XX-XXXXXXXX-X). |
| R-MAE-08 | TipoPrecioZapatilla con margen | Cada tipo de precio tiene un margen de ganancia (%) que se usa como referencia. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| CRUD Categorías | ✅ | ❌ |
| CRUD Subgrupos | ✅ | ❌ |
| CRUD Clientes | ✅ | 👁️ (solo lectura) |
| CRUD Proveedores | ✅ | ❌ |
| CRUD TipoPrecioZapatilla | ✅ | ❌ |

#### Validaciones

- Nombre categoría: required, max 100, unique.
- Nombre subgrupo: required, max 100.
- Nombre cliente: required, max 200.
- Razón social proveedor: required, max 200.
- CUIT (si se ingresa): formato XX-XXXXXXXX-X.
- MargenGanancia TipoPrecioZapatilla: >= 0.

#### Criterios de aceptación

- [ ] Categoría con nombre duplicado muestra error de validación.
- [ ] Subgrupos se filtran por categoría vía AJAX.
- [ ] Vendedor ve listado de clientes sin botones de acción (crear/editar/eliminar).
- [ ] Inactivar categoría con productos activos muestra error.

---

### MÓDULO 3 — Productos y Variantes

**Descripción:** Gestión de productos con variantes diferenciadas por tipo (ropa vs zapatillas). Cada variante tiene su propio precio, stock y atributos específicos.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-PRD-01 | Producto tiene categoría obligatoria | Todo producto pertenece a una categoría. Subgrupo es opcional. |
| R-PRD-02 | Variante hereda tipo de categoría | Los campos visibles de la variante dependen de la categoría del producto padre (Ropa vs Zapatillas). |
| R-PRD-03 | Campos Ropa | Si categoría = Ropa → Talle, Color, Marca, Género, Temporada. |
| R-PRD-04 | Campos Zapatillas | Si categoría = Zapatillas → Color, Marca, Número, Modelo, TipoPrecioZapatilla. |
| R-PRD-05 | SKU único | Si se ingresa SKU, debe ser único entre variantes activas. |
| R-PRD-06 | Código de barra único | Si se ingresa código de barra, debe ser único entre variantes activas. |
| R-PRD-07 | Vendedor no ve costos | El listado de productos para Vendedor no muestra `UltimoPrecioCompra` ni cálculos de ganancia. |
| R-PRD-08 | Inactivar variante requiere stock 0 | No se puede inactivar una variante que tiene stock > 0. |
| R-PRD-09 | PrecioVenta obligatorio | Toda variante debe tener precio de venta > 0. |
| R-PRD-10 | UltimoPrecioCompra automático | Se actualiza automáticamente al recepcionar una compra. No se edita manualmente. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar productos | ✅ (con costos) | ✅ (sin costos) |
| Crear/Editar producto | ✅ | ❌ |
| Crear/Editar variante | ✅ | ❌ |
| Ver detalle producto | ✅ (con costos) | ✅ (sin costos) |
| Inactivar variante | ✅ | ❌ |
| Buscar variantes (AJAX) | ✅ | ✅ |

#### Validaciones

- Nombre producto: required, max 200.
- CategoriaId: required.
- PrecioVenta: required, > 0, precision 18,2.
- SKU: optional, max 50, unique si no es null.
- CodigoBarra: optional, max 50, unique si no es null.
- Talle: max 20. Color: max 50. Marca: max 100.

#### Flujo del formulario dinámico

```
1. Admin selecciona Categoría del producto.
2. JS evalúa data-tipo-producto del producto padre.
3. Si Ropa → muestra: Talle, Color, Marca, Género, Temporada.
4. Si Zapatillas → muestra: Color, Marca, Número, Modelo, TipoPrecioZapatilla.
5. Campos no visibles no se envían al server.
```

#### Criterios de aceptación

- [ ] Formulario de variante muestra campos dinámicos según categoría.
- [ ] SKU duplicado muestra error de validación.
- [ ] Código de barra duplicado muestra error de validación.
- [ ] Vendedor no ve columnas de costo en el listado.
- [ ] Intentar inactivar variante con stock > 0 muestra error.

---

### MÓDULO 4 — Stock e Inventario

**Descripción:** Control de stock por variante de producto con trazabilidad completa de movimientos. Incluye carga inicial, ajuste manual y alertas de stock bajo.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-STK-01 | Stock por variante | Cada variante tiene exactamente un registro de Stock (relación 1:1). |
| R-STK-02 | Stock nunca negativo | El stock no puede quedar por debajo de 0 en ninguna operación. |
| R-STK-03 | Trazabilidad de movimientos | Toda operación que modifica stock genera un `MovimientoStock` con: tipo, cantidad, stock anterior, stock resultante, y referencia a la entidad origen. |
| R-STK-04 | Carga inicial | Solo se permite una vez por variante cuando el stock es 0 y no tiene movimientos previos. |
| R-STK-05 | Ajuste manual | Registra la cantidad anterior, cantidad nueva y motivo. Solo Administrador. |
| R-STK-06 | Alerta stock bajo | Variantes con `StockActual <= StockMinimo` se resaltan visualmente en el listado. |
| R-STK-07 | StockMinimo por defecto | Si no se define, StockMinimo = 0 (sin alerta). |
| R-STK-08 | Tipos de movimiento | CargaInicial, Venta, AnulacionVenta, CompraRecepcion, DevolucionCliente, AjusteManual, DevolucionProveedor. |
| R-STK-09 | FKs polimórficas | Cada movimiento referencia a la entidad origen (CompraId, VentaId, DevolucionCambioId o AjusteStockId). Solo una se popula por movimiento. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar stock | ✅ | ✅ |
| Ver alertas stock bajo | ✅ | ✅ |
| Carga inicial | ✅ | ❌ |
| Ajuste manual | ✅ | ❌ |
| Ver historial movimientos | ✅ | ✅ |

#### Validaciones

- Carga inicial: cantidad > 0, solo si variante no tiene movimientos previos.
- Ajuste manual: cantidad nueva >= 0.
- Toda operación de stock se ejecuta dentro de transacción serializable.

#### Criterios de aceptación

- [ ] Carga inicial incrementa stock y genera MovimientoStock tipo CargaInicial.
- [ ] Ajuste manual registra cantidad anterior/nueva y genera MovimientoStock tipo AjusteManual.
- [ ] Historial de movimientos muestra tipo, cantidad, stock anterior/resultante, fecha y referencia.
- [ ] Listado muestra alerta visual cuando StockActual <= StockMinimo.
- [ ] Vendedor no tiene acceso a carga inicial ni ajuste manual (403).

---

### MÓDULO 5 — Compras a Proveedores

**Descripción:** Gestión de compras con flujo de estados lineal (Borrador → EnProceso → Verificada → Recibida), recepción parcial con control de dañados/devueltos, y adjuntos.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-COM-01 | Flujo de estados lineal | Borrador → EnProceso → Verificada → Recibida. No se puede retroceder. |
| R-COM-02 | Edición según estado | Solo se puede editar la compra en estado Borrador o EnProceso. |
| R-COM-03 | Recepción parcial | Al recepcionar, por cada línea se indica: CantidadRecibida + CantidadDañada + CantidadDevueltaProveedor. |
| R-COM-04 | Validación recepción | Para cada línea: Recibida + Dañada + DevueltaProveedor <= Cantidad pedida. |
| R-COM-05 | Stock en recepción | Solo `CantidadRecibida` impacta stock positivamente (MovimientoStock tipo CompraRecepcion). |
| R-COM-06 | Dañadas no suman stock | Las cantidades dañadas se registran pero no afectan stock. |
| R-COM-07 | Devolución a proveedor | Las cantidades devueltas generan MovimientoStock tipo DevolucionProveedor (decrementan stock si ya habían sido recibidas). |
| R-COM-08 | UltimoPrecioCompra | Al recepcionar, se actualiza el `UltimoPrecioCompra` de cada variante con el `CostoUnitario` de la línea. |
| R-COM-09 | Adjuntos | Se pueden adjuntar archivos (imagen/PDF) a la compra. Se almacenan en `wwwroot/uploads/compras/` con nombre GUID. |
| R-COM-10 | Acceso exclusivo Admin | Solo el Administrador accede al módulo de compras. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar compras | ✅ | ❌ |
| Crear/Editar compra | ✅ | ❌ |
| Cambiar estado | ✅ | ❌ |
| Recepcionar | ✅ | ❌ |
| Adjuntar archivos | ✅ | ❌ |

#### Validaciones

- ProveedorId: required.
- FechaCompra: required.
- Al menos una línea de detalle.
- CostoUnitario > 0 por línea.
- Cantidad > 0 por línea.
- Recepción: Recibida + Dañada + Devuelta <= Pedida (por línea).

#### Flujo de estados

```
[Borrador] ──→ [EnProceso] ──→ [Verificada] ──→ [Recibida]
  (editable)     (editable)      (solo lectura)   (solo lectura)
                                                   ↑ Impacta stock
                                                   ↑ Actualiza UltimoPrecioCompra
```

#### Criterios de aceptación

- [ ] Compra creada en estado Borrador.
- [ ] Avance de estado lineal con confirmación SweetAlert.
- [ ] Edición bloqueada en estado Verificada y Recibida.
- [ ] Recepción valida Rec + Dañ + Dev <= Pedida por línea.
- [ ] Recepción impacta stock solo con cantidades recibidas.
- [ ] UltimoPrecioCompra de la variante se actualiza al recepcionar.
- [ ] Vendedor recibe 403 en cualquier ruta de compras.

---

### MÓDULO 6 — Ventas a Clientes ⭐

**Descripción:** Módulo más crítico del sistema. Carrito dinámico AJAX, múltiples medios de pago (Efectivo, Tarjeta, Cuotas, Transferencia), cuotas con financiamiento, remito PDF con QuestPDF.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-VTA-01 | Flujo de estados | Confirmada → Entregada. Anulada es un estado terminal accesible desde Confirmada. |
| R-VTA-02 | Stock al confirmar | Al confirmar la venta se decrementa stock de cada variante. Si stock insuficiente → error. |
| R-VTA-03 | Anulación repone stock | Al anular una venta Confirmada se repone el stock de cada línea. |
| R-VTA-04 | No anular entregada | Una venta Entregada no se puede anular (usar devolución). |
| R-VTA-05 | Múltiples medios de pago | Una venta puede tener N registros de VentaPago con distintos medios. |
| R-VTA-06 | Suma pagos = total | La suma de todos los VentaPago.Monto debe ser exactamente igual al total de la venta. |
| R-VTA-07 | Cuotas con financiamiento | Si MedioPago = Cuotas → se registra CantidadCuotas y PorcentajeFinanciamiento. El monto incluye el recargo. |
| R-VTA-08 | Número correlativo | Cada venta recibe un número correlativo autogenerado (int autoincremental o `MAX + 1`). |
| R-VTA-09 | Cliente opcional | La venta puede no tener cliente (venta anónima / consumidor final). |
| R-VTA-10 | Vendedor no ve costos | En el detalle de venta, el Vendedor no ve UltimoPrecioCompra ni columnas de ganancia. |
| R-VTA-11 | Remito PDF | Se genera con QuestPDF. Incluye: datos del local, número de venta, fecha, cliente, detalle de productos, medios de pago, total. |
| R-VTA-12 | Adjuntos | Se pueden adjuntar comprobantes (transferencia, voucher). Se almacenan en `wwwroot/uploads/ventas/` con nombre GUID. |
| R-VTA-13 | Transacción serializable | Toda la operación de crear venta (validar stock + decrementar + guardar) se ejecuta en transacción serializable para evitar concurrencia. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar ventas | ✅ (con costos) | ✅ (sin costos) |
| Crear venta | ✅ | ✅ |
| Ver detalle | ✅ (con costos) | ✅ (sin costos) |
| Anular venta | ✅ | ✅ |
| Marcar entregada | ✅ | ✅ |
| Generar remito PDF | ✅ | ✅ |
| Adjuntar comprobante | ✅ | ✅ |

#### Validaciones

- Al menos una línea de detalle.
- Cantidad > 0 por línea.
- Stock suficiente por variante (validación server-side en transacción).
- Al menos un medio de pago.
- Suma de pagos = total venta (tolerancia ±0.01 por redondeo).
- Si MedioPago = Cuotas → CantidadCuotas >= 2 y PorcentajeFinanciamiento >= 0.

#### Flujo de estados

```
[Confirmada] ──→ [Entregada]
      │
      └──→ [Anulada]  (repone stock)
```

#### Flujo del carrito (single-page)

```
SECCIÓN 1: Encabezado
  - Cliente (Select2 remoto, opcional)
  - Fecha (auto)
  - Observaciones

SECCIÓN 2: Productos (AJAX)
  - Buscar variante (Select2 por nombre/SKU/código barra)
  - Al seleccionar → consulta stock vía AJAX
  - Input cantidad → validación JS: cantidad <= stock
  - Botón agregar → tabla dinámica JS
  - Subtotal por línea = PrecioVenta × Cantidad
  - Total general se recalcula en tiempo real

SECCIÓN 3: Medios de Pago (dinámico)
  - Botón "Agregar medio de pago"
  - Select: Efectivo / Tarjeta / Cuotas / Transferencia
  - Si Cuotas → campos adicionales: CantidadCuotas, PorcentajeFinanciamiento
  - Input monto por cada medio
  - Validación JS: suma medios = total general
  - Indicador visual: "Resta por asignar: $X"

SECCIÓN 4: Confirmar
  - Resumen visual
  - Botón confirmar con SweetAlert
  - POST al server → transacción serializable
```

#### Criterios de aceptación

- [ ] Venta creada en estado Confirmada con stock decrementado.
- [ ] Venta con stock insuficiente retorna error (no se crea).
- [ ] Venta con suma de pagos ≠ total retorna error.
- [ ] Anulación repone stock y cambia estado a Anulada.
- [ ] Venta Entregada no se puede anular.
- [ ] Remito PDF se genera correctamente con QuestPDF.
- [ ] Vendedor no ve costos ni ganancias en ninguna vista de ventas.
- [ ] Carrito AJAX funciona correctamente con validación de stock en tiempo real.
- [ ] Número correlativo se genera automáticamente sin duplicados.

---

### MÓDULO 7 — Devoluciones y Cambios

**Descripción:** Procesamiento de devoluciones y cambios de productos vendidos. Wizard de 4 pasos con estado en JS y validación server-side completa al confirmar.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-DEV-01 | Tipos de devolución | DevolucionDinero, CambioMismoValor, CambioMayorValor. |
| R-DEV-02 | Referencia a venta | Toda devolución/cambio referencia a una venta existente (Confirmada o Entregada). |
| R-DEV-03 | Cantidad devolvible | La cantidad a devolver no puede superar la cantidad vendida de esa variante menos devoluciones previas. |
| R-DEV-04 | Stock de devolución | La devolución reingresa stock de los items devueltos (MovimientoStock tipo DevolucionCliente). |
| R-DEV-05 | Cambio decrementa stock nuevo | En cambio (mismo o mayor valor), los items nuevos decrementan stock. |
| R-DEV-06 | Diferencia en cambio mayor valor | Si el cambio es de mayor valor, se registra la diferencia a cobrar y el medio de pago. |
| R-DEV-07 | Validación stock items nuevos | Los items de cambio deben tener stock suficiente (misma validación que venta). |
| R-DEV-08 | Motivo obligatorio | Todo devolución/cambio requiere un motivo (texto libre, max 500). |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Listar devoluciones | ✅ | ✅ |
| Crear devolución/cambio | ✅ | ✅ |
| Ver detalle | ✅ | ✅ |

#### Wizard de 4 pasos

```
PASO 1: Seleccionar venta
  - Buscar por número de venta o cliente
  - Mostrar resumen de la venta seleccionada

PASO 2: Seleccionar items a devolver
  - Listado de items de la venta con cantidad vendida y cantidad ya devuelta
  - Input: cantidad a devolver por item (0 a disponible)
  - Motivo de devolución (textarea)

PASO 3: Seleccionar tipo
  - DevolucionDinero → fin
  - CambioMismoValor → seleccionar items nuevos (mismo valor total)
  - CambioMayorValor → seleccionar items nuevos + registrar diferencia + medio de pago

PASO 4: Confirmar
  - Resumen completo: items devueltos, items nuevos (si aplica), diferencia (si aplica)
  - Botón confirmar con SweetAlert
  - POST al server → transacción
```

#### Validaciones

- VentaId: required, debe existir y estar Confirmada o Entregada.
- Al menos un item devuelto con cantidad > 0.
- CantidadDevuelta <= CantidadVendida - DevolucionesPrevias (por variante por venta).
- Si cambio → al menos un item nuevo.
- Si CambioMismoValor → valor items nuevos = valor items devueltos.
- Si CambioMayorValor → diferencia > 0 y medio de pago informado.
- Motivo: required, max 500.
- Stock suficiente para items nuevos.

#### Criterios de aceptación

- [ ] Wizard completa los 4 pasos sin errores.
- [ ] Stock de items devueltos se reingresa correctamente.
- [ ] Stock de items nuevos (cambio) se decrementa correctamente.
- [ ] Cantidad devuelta no supera la disponible.
- [ ] Diferencia en cambio mayor valor se registra con medio de pago.
- [ ] Validación server-side completa al POST del paso 4.

---

### MÓDULO 8 — Resumen Semanal de Facturación

**Descripción:** Reporte semanal de ventas pagadas por transferencia para conciliación. Solo accesible por Administrador.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-RES-01 | Rango semanal | El resumen abarca lunes a domingo de la semana seleccionada. |
| R-RES-02 | Solo transferencias | Filtra únicamente los VentaPago con MedioPago = Transferencia de ventas en estado Confirmada o Entregada. |
| R-RES-03 | Agrupación | Agrupa por fecha, mostrando total transferencias por día y total semanal. |
| R-RES-04 | Exportación | Permite exportar a Excel (ClosedXML). |
| R-RES-05 | Acceso exclusivo Admin | Solo Administrador (y SuperUsuario) pueden acceder. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Ver resumen semanal | ✅ | ❌ |
| Exportar a Excel | ✅ | ❌ |

#### Validaciones

- Rango de fechas: la fecha inicio debe ser lunes.
- Query directo a VentaPago (no pasa por IVentaService).

#### Criterios de aceptación

- [ ] Resumen muestra solo transferencias de ventas Confirmada/Entregada.
- [ ] Agrupación por día con total semanal.
- [ ] Exportación Excel funciona correctamente.
- [ ] Vendedor recibe 403.

---

### MÓDULO 9 — Aumento Masivo de Precios

**Descripción:** Herramienta para aplicar aumentos porcentuales de precios de venta a múltiples variantes simultáneamente. Solo Administrador.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-AUM-01 | Filtros de selección | Se puede filtrar por: Categoría, Subgrupo, Marca, o selección manual. |
| R-AUM-02 | Porcentaje de aumento | Se ingresa un porcentaje (ej: 15%). Se aplica sobre el PrecioVenta actual. |
| R-AUM-03 | Exclusión manual | Antes de confirmar, el admin puede excluir variantes individuales del lote. |
| R-AUM-04 | Preview obligatorio | Antes de aplicar, se muestra una tabla con: variante, precio actual, precio nuevo. |
| R-AUM-05 | Aplicación batch | El aumento se aplica en una sola operación batch (UPDATE en lote). |
| R-AUM-06 | Redondeo | El precio nuevo se redondea a 2 decimales. |
| R-AUM-07 | Acceso exclusivo Admin | Solo Administrador (y SuperUsuario) pueden acceder. |

#### Permisos

| Funcionalidad | Admin | Vendedor |
|---|---|---|
| Acceder aumento masivo | ✅ | ❌ |
| Previsualizar | ✅ | ❌ |
| Aplicar aumento | ✅ | ❌ |

#### Validaciones

- Porcentaje: required, > 0, max 500 (protección contra errores de tipeo).
- Al menos una variante seleccionada después de exclusiones.

#### Flujo

```
1. Seleccionar filtros (categoría/subgrupo/marca).
2. Sistema muestra variantes coincidentes con checkbox.
3. Admin ingresa porcentaje de aumento.
4. Botón "Previsualizar" → tabla con precio actual y precio nuevo.
5. Admin puede desmarcar variantes individuales.
6. Botón "Aplicar" con SweetAlert confirm → batch update.
7. Mensaje de éxito con cantidad de variantes actualizadas.
```

#### Criterios de aceptación

- [ ] Filtros por categoría/subgrupo/marca funcionan.
- [ ] Preview muestra precio actual y nuevo correctamente.
- [ ] Variantes excluidas no se actualizan.
- [ ] Aumento se aplica correctamente con redondeo a 2 decimales.
- [ ] Vendedor recibe 403.

---

### DASHBOARD

**Descripción:** Pantalla principal con indicadores clave del negocio. Contenido diferenciado por rol.

#### Reglas de negocio

| Código | Regla | Descripción |
|---|---|---|
| R-DSH-01 | Dashboard Admin | Muestra: ventas del día/semana/mes, compras pendientes, stock bajo, últimas ventas, ingresos por medio de pago. |
| R-DSH-02 | Dashboard Vendedor | Muestra: ventas del día (propias), últimas ventas (propias). Sin montos de costos ni ganancias. |
| R-DSH-03 | Datos en tiempo real | Los indicadores se cargan al acceder al dashboard (no requiere refresh automático en v1). |

#### Permisos

| Indicador | Admin | Vendedor |
|---|---|---|
| Ventas del día/semana/mes (totales) | ✅ | ❌ |
| Ventas del día (propias) | ✅ | ✅ |
| Compras pendientes | ✅ | ❌ |
| Alertas stock bajo | ✅ | ✅ |
| Ingresos por medio de pago | ✅ | ❌ |

#### Criterios de aceptación

- [ ] Admin ve todos los indicadores.
- [ ] Vendedor ve versión limitada sin costos ni ganancias.
- [ ] Los datos se cargan correctamente según el rango temporal.

---

## 5. Decisiones funcionales resueltas (cierre v1.1)

| # | Tema | Decisión | Regla impactada |
|---|---|---|---|
| D1 | Numeración correlativa de venta | `int` autoincremental gestionado por la base de datos | R-VTA-08 |
| D2 | Redondeo en pago con Cuotas | El recargo por financiamiento se distribuye en cada cuota (no se prorratea sobre el total). Cada cuota = `(Monto + Recargo) / CantidadCuotas`, redondeo 2 decimales. La diferencia por redondeo se ajusta en la última cuota. | R-VTA-07 |
| D3 | Cantidades dañadas devueltas al proveedor antes de recepción | Si la devolución al proveedor ocurre **antes** de recepcionar, se **ignora** (no genera movimiento de stock ni descuenta del pedido). Solo se contabiliza tras tener stock recepcionado. | R-COM-06 / R-COM-07 |
| D4 | Persistencia de preview de Aumento Masivo | **No** se persiste registro `AumentoMasivo` si el admin cancela antes de aplicar. Solo se crea al confirmar. | R-AUM-04 / Entidad #20 |
| D5 | Soft delete de Cliente con ventas | Se **bloquea** la inactivación de un cliente con ventas asociadas (mismo criterio que categorías con productos). Mostrar mensaje de error. | R-MAE-05 (extendido a Cliente) |
| D6 | Concurrencia en Aumento Masivo | Si dos admins lanzan aumentos simultáneos sobre la misma variante, **prevalece el primero** que confirma (first-write-wins). Se implementa con bloqueo optimista por `RowVersion` o lock pesimista en la transacción del batch. El segundo recibe error y debe re-previsualizar. | R-AUM-05 (nuevo) |

---

## 6. Parámetros del Sistema

| Parámetro | Valor | Notas |
|---|---|---|
| Cultura | es-AR | Fija, sin selector de idioma. |
| Moneda | ARS ($) | Formato: `$ #.###,##` |
| Zona horaria | America/Argentina/Buenos_Aires | Para fechas y timestamps. |
| Paginación DataTables | 10, 25, 50, 100 | Configurable por el usuario en cada tabla. |
| Tamaño máximo adjunto | 5 MB | Imágenes y PDF. |
| Formatos adjunto permitidos | .jpg, .jpeg, .png, .pdf | Validación server-side. |
| Ruta de adjuntos | `wwwroot/uploads/{modulo}/` | Nombre GUID para evitar colisiones. |

---

## 7. Resumen de Entidades

| # | Entidad | Módulo | Relaciones clave |
|---|---|---|---|
| 1 | Categoria | Maestros | 1:N → Subgrupo, 1:N → Producto |
| 2 | Subgrupo | Maestros | N:1 → Categoria, 1:N → Producto |
| 3 | Cliente | Maestros | 1:N → Venta |
| 4 | Proveedor | Maestros | 1:N → Compra |
| 5 | TipoPrecioZapatilla | Maestros | 1:N → VarianteProducto |
| 6 | Producto | Productos | N:1 → Categoria, N:1 → Subgrupo, 1:N → VarianteProducto |
| 7 | VarianteProducto | Productos | N:1 → Producto, N:1 → TipoPrecioZapatilla, 1:1 → Stock |
| 8 | Stock | Stock | 1:1 → VarianteProducto |
| 9 | MovimientoStock | Stock | N:1 → VarianteProducto, FKs polimórficas |
| 10 | AjusteStock | Stock | N:1 → VarianteProducto |
| 11 | Compra | Compras | N:1 → Proveedor, 1:N → CompraDetalle, 1:N → CompraAdjunto |
| 12 | CompraDetalle | Compras | N:1 → Compra, N:1 → VarianteProducto |
| 13 | CompraAdjunto | Compras | N:1 → Compra |
| 14 | Venta | Ventas | N:1 → Cliente, 1:N → VentaDetalle, 1:N → VentaPago, 1:N → VentaAdjunto |
| 15 | VentaDetalle | Ventas | N:1 → Venta, N:1 → VarianteProducto |
| 16 | VentaPago | Ventas | N:1 → Venta |
| 17 | VentaAdjunto | Ventas | N:1 → Venta |
| 18 | DevolucionCambio | Devoluciones | N:1 → Venta, 1:N → DevolucionCambioDetalle |
| 19 | DevolucionCambioDetalle | Devoluciones | N:1 → DevolucionCambio, N:1 → VarianteProducto |
| 20 | AumentoMasivo | Aumento | Registro de log del aumento aplicado |

---

## 8. Impacto Técnico

| Área | Impacto |
|---|---|
| Domain | 20 entidades nuevas + 5 enums. Todas heredan SoftDestroyable. |
| Application | 14 interfaces de servicio nuevas. Todas retornan ServiceResult/ServiceResult<T>. |
| Infrastructure | 20 configuraciones Fluent API. 20 DbSets. 14 implementaciones de servicio. 6 migraciones (M1–M6). |
| Web | 13 controllers nuevos. ~30 vistas. ~35 ViewModels con DataAnnotations. 7 endpoints AJAX. |
| Seed | Agregar rol Vendedor y policies de autorización. |
| Frontend | jQuery + DataTables + Select2 + SweetAlert2. Lógica JS para carrito de venta y wizard de devolución. |

---

## 9. Banderas tempranas

| Bandera | Estado | Justificación |
|---|---|---|
| **¿Requiere migración EF?** | ✅ **SÍ** | 20 entidades nuevas + 5 enums + 20 configuraciones Fluent API. Se proyectan **6 migraciones (M1–M6)**. Impacta `AppDbContext`, seed de rol Vendedor y policies de autorización. |
| **¿Integración externa?** | ❌ **NO** | AFIP/ARCA, hardware fiscal, notificaciones email/push y backup están explícitamente excluidos (sección 11). El lector USB de código de barras opera como teclado: sin desarrollo de integración. Único componente externo: librerías locales (QuestPDF, ClosedXML). |
| **¿Máquina de estados?** | ✅ **SÍ** | Dos máquinas relevantes:<br>• **Compra**: Borrador → EnProceso → Verificada → Recibida (lineal, sin retroceso; efectos colaterales en Recibida: stock + UltimoPrecioCompra).<br>• **Venta**: Confirmada → Entregada \| Anulada (Anulada repone stock; Entregada bloquea anulación → forzar flujo de Devolución).<br>Las reglas de transición deben encapsularse en `ICompraService` e `IVentaService` para garantizar invariantes. |

---

## 10. Riesgos y Supuestos

### Riesgos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R1 | Concurrencia en stock (2 vendedores simultáneos) | Alto | Transacción serializable en CrearVentaAsync |
| R2 | Carrito en memoria JS se pierde si el navegador se cierra | Medio | Aceptado en v1; no se persiste borrador |
| R3 | Adjuntos en disco local sin backup | Medio | Nombre GUID, migrar a blob storage en v2 |
| R4 | Wizard devolución con estado en JS | Medio | Validación server-side completa al POST |

### Supuestos

| # | Supuesto | Verificación |
|---|---|---|
| S1 | El proyecto sigue MVC (Controllers/Views), no Razor Pages | Confirmado por estructura existente |
| S2 | ServiceResult<T> existente cubre todos los casos de retorno | Verificado en codebase |
| S3 | DataTables server-side ya tiene patrón implementado (DataTableRequest/Response) | Verificado en codebase |
| S4 | Clean Architecture de 4 capas ya implementada y funcional | Verificado en codebase |
| S5 | Soft delete global ya configurado en AppDbContext | Verificado en codebase |

---

## 11. Pruebas Mínimas Requeridas

### Integración (por service)

- [ ] `IVentaService.CrearAsync` → stock decrementado + movimientos generados + nro correlativo.
- [ ] `IVentaService.CrearAsync` con stock insuficiente → `ServiceResult.Failure`.
- [ ] `IVentaService.CrearAsync` con suma pagos ≠ total → `ServiceResult.Failure`.
- [ ] `ICompraService.RecepcionarAsync` → stock solo de recibidas + UltimoPrecioCompra actualizado.
- [ ] `ICompraService.RecepcionarAsync` con Rec+Dañ+Dev > Pedida → `ServiceResult.Failure`.
- [ ] `IDevolucionService.CrearAsync` → stock reingresado + validación cantidad disponible.
- [ ] `IAumentoMasivoService.AplicarAsync` → precios actualizados excluyendo variantes excluidas.
- [ ] `IResumenSemanalService.ObtenerAsync` → solo transferencias de ventas Confirmada/Entregada.

### Autorización

- [ ] Vendedor → 403 en `/Compras`, `/Stock/Ajuste`, `/AumentoMasivo`, `/ResumenSemanal`.
- [ ] Vendedor → no recibe `UltimoPrecioCompra` ni `Ganancia` en ningún endpoint.

### UI/Funcional

- [ ] Nueva Venta: agregar/quitar productos del carrito, validación stock JS.
- [ ] Nueva Venta: agregar múltiples medios de pago, validación suma = total.
- [ ] Recepción: validación JS por línea Rec+Dañ+Dev <= Pedida.
- [ ] Wizard Devolución: los 4 pasos completan sin errores.

---

## 12. Exclusiones

Las siguientes funcionalidades **NO** están incluidas en el alcance:

- ❌ Migración de datos desde sistema anterior.
- ❌ Configuración y costo del servidor / hosting.
- ❌ Facturación electrónica AFIP / ARCA.
- ❌ Aplicación móvil (iOS / Android).
- ❌ Integración con hardware externo (impresora fiscal, lector de código de barras como dispositivo — el lector USB funciona como teclado y es compatible sin desarrollo).
- ❌ Cambios de alcance posteriores al inicio (se presupuestan por separado).
- ❌ Backup automático de base de datos.
- ❌ Notificaciones push o por email automáticas.
- ❌ Multi-sucursal (el sistema es para un único punto de venta).

---

## 13. Checklist de Salida

```
ANÁLISIS FUNCIONAL — CHECKLIST DE SALIDA
────────────────────────────────────────────────────────────────────────
MÓDULOS
[✓] 9 módulos + Dashboard identificados y analizados
[✓] Reglas de negocio codificadas (R-XXX-NN)
[✓] Matrices de permisos por módulo
[✓] Flujos de estado documentados (Compras, Ventas)
[✓] Validaciones por módulo

ENTIDADES
[✓] 20 entidades identificadas con relaciones
[✓] 5 enums definidos con valores

ACTORES
[✓] 3 roles definidos (SuperUsuario, Administrador, Vendedor)
[✓] Matriz de acceso general documentada
[✓] Restricciones de Vendedor explícitas (sin costos/ganancias)

CRITERIOS DE ACEPTACIÓN
[✓] Definidos por módulo
[✓] Pruebas mínimas requeridas listadas

EXCLUSIONES
[✓] Exclusiones documentadas explícitamente

CIERRE v1.1
[✓] Casos de uso indexados (CU-01..CU-26)
[✓] Decisiones funcionales resueltas (D1..D6)
[✓] Banderas tempranas explícitas (EF: SÍ / Integración: NO / Máquina de estados: SÍ)
[✓] Listo para handoff a Diseño
────────────────────────────────────────────────────────────────────────
```

---

## 14. Handoff a Diseño

### Paquete entregado al agente de Diseño

1. **Alcance cerrado**: 9 módulos + Dashboard, 26 casos de uso, 20 entidades, 5 enums, 3 roles.
2. **Reglas de negocio codificadas**: R-SEG, R-MAE, R-PRD, R-STK, R-COM, R-VTA, R-DEV, R-RES, R-AUM, R-DSH (~60 reglas).
3. **Decisiones funcionales resueltas (D1–D6)**: numeración correlativa, redondeo de cuotas, dañadas pre-recepción, no persistencia de preview, bloqueo de cliente con ventas, first-write-wins en aumento masivo.
4. **Banderas tempranas**:
   - Migración EF: **SÍ** (6 migraciones M1–M6).
   - Integración externa: **NO**.
   - Máquina de estados: **SÍ** (Compra y Venta).
5. **Criterios de aceptación verificables** por módulo (~55 ítems).
6. **Riesgos y supuestos** (R1–R4 / S1–S5).
7. **Exclusiones explícitas** (sección 12).

### Foco esperado en la etapa de Diseño

- **Domain**: modelar las 20 entidades + enums + invariantes de las dos máquinas de estado.
- **Application**: 14 interfaces de service con contratos `ServiceResult<T>`, política de visibilidad de costos por rol, reglas de transición de estado.
- **Infrastructure**: Fluent API, plan de 6 migraciones M1–M6, transacciones serializables (Venta/Compra/Devolución), bloqueo optimista para Aumento Masivo (D6).
- **Web**: 13 controllers, ~30 vistas, ~35 ViewModels, 7 endpoints AJAX, sidebar dinámico por rol, formularios con campos condicionales (Ropa vs Zapatillas), wizard 4 pasos (Devolución), carrito single-page (Venta).

### Preguntas pendientes para el diseñador

Ninguna desde el plano funcional. Las cuestiones técnicas (mecanismo concreto de bloqueo en D6, estrategia de redondeo en D2 a nivel persistencia, índices únicos para SKU/CódigoBarra/correlativo de venta) se resuelven en la etapa de Diseño/Arquitectura.
