# 📋 Memoria Acumulativa - Analista Funcional
**Proyecto:** ShowroomGriffin  
**Agente:** Analista Funcional Senior  
**Fecha creación:** 2026-04-23  
**Última actualización:** 2026-04-23  

---

## 1️⃣ DECISIONES FUNCIONALES REGISTRADAS

### 🔹 Decisión #1: Modelo Producto + Variantes (2026-04-23)

**Contexto:**  
El negocio de indumentaria/calzado requiere manejar un mismo artículo comercial (ej. "Zapatilla Nike Air Max") en múltiples combinaciones de talle, color, número, género, temporada.

**Decisión tomada:**  
Modelar como **Producto (agrupador) + VarianteProducto (unidad de stock/venta)** en lugar de productos planos categorizados.

**Justificación:**
- **Un Producto** representa la identidad comercial (ej. "Nike Air Max Modelo X").
- **Cada VarianteProducto** representa una SKU vendible (ej. "Nike Air Max Modelo X – Talle 39 – Negro").
- Stock, precio y SKU viven en la variante (unidad real de comercio).
- Evita explosión de filas (6 talles × 3 colores = 18 "productos" distintos en modelo plano).
- Facilita reportes por modelo y aumentos masivos de precio.

**Impacto funcional:**
- Grilla de productos muestra agrupadores (Producto).
- Detalle de venta/compra apunta a la variante.
- Reportes distinguen "ventas del modelo" vs "ventas del talle 39 negro".

**Estado:** ✅ Aprobado  
**Documentado en:** README.md del proyecto (pendiente), conversación inicial.

---

### 🔹 Decisión #2: Redefinición del Modelo de Dominio (2026-04-23)

**Contexto:**  
El usuario definió la estructura conceptual del negocio:
- **Categorías:** Indumentaria, Zapatillas, Accesorios.
- **Subgrupos:** Marcas (ej. Nike, Adidas, Puma).
- **Variantes:** Modelo + Color + Talle.

**Decisión tomada:**  
- **Categoría** pasa a ser un set cerrado (enum o validación): `Indumentaria`, `Zapatillas`, `Accesorios`.
- **Subgrupo** se reinterpreta semánticamente como **Marca** (aunque la tabla se mantiene como `Subgrupo` por compatibilidad).
- **Marca** y **Modelo** pasan de `VarianteProducto` a **`Producto`**.
- **VarianteProducto** solo mantiene atributos específicos de la combinación: `Color`, `Talle`, `Numero`, `Genero`, `Temporada`.

**Justificación:**
- Alinea el modelo técnico con la terminología del negocio.
- **Marca** y **Modelo** son propiedades del agrupador (Producto), no de cada variante individual.
- Simplifica filtros y combos anidados (Marca → Modelo → Color → Talle).
- Reduce redundancia de datos (Marca/Modelo no se repiten en cada variante).

**Impacto funcional:**
- Creación de Producto ahora requiere Marca y Modelo.
- Creación de Variante **no** requiere Marca/Modelo (se heredan del Producto padre).
- Los combos de selección de productos en Ventas/Compras siguen la jerarquía: Marca → Modelo → Color → Talle.

**Migración de datos requerida:**
- Agrupar variantes existentes por (Marca, Modelo) → crear Productos únicos.
- Reasignar `VarianteProducto.ProductoId` al nuevo agrupador.
- Eliminar columnas `Marca`, `Modelo` de `VarianteProducto`.

**Estado:** ✅ Aprobado  
**Requiere:** Migración EF (M2_RefactorProductoMarcaModelo).

---

## 2️⃣ REQUERIMIENTOS FUNCIONALES PENDIENTES DE IMPLEMENTACIÓN

### 🔸 R1: Campo Anotaciones en Venta

**Alcance:**  
Agregar campo de texto libre `Anotaciones` en la entidad `Venta` para que el usuario pueda registrar observaciones adicionales (ej. "Cliente pidió envío urgente", "Descuento especial autorizado por gerencia").

**Casos de uso:**
1. Al crear una venta, el usuario puede opcionalmente ingresar anotaciones.
2. Al editar una venta, el usuario puede modificar las anotaciones.
3. Las anotaciones se visualizan en el detalle de la venta.

**Criterios de aceptación:**
- Campo `Anotaciones` es opcional (nullable).
- Longitud máxima: 500 caracteres.
- Se muestra como `<textarea>` en formularios de Crear/Editar Venta.
- Se visualiza en el detalle de la venta (solo si tiene valor).

**Capas afectadas:**
- Domain: agregar propiedad.
- Infrastructure: migración EF.
- Application: incluir en ViewModels.
- Web: agregar control en vistas.

**Riesgos:** Ninguno.  
**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R2: Modal para Crear Cliente desde Venta

**Alcance:**  
Permitir al usuario crear un nuevo cliente desde el formulario de Alta/Edición de Venta mediante un modal, sin necesidad de abandonar la pantalla de venta.

**Casos de uso:**
1. Usuario está creando/editando una venta y el cliente no existe en el combo.
2. Usuario hace clic en botón "Crear Cliente".
3. Se abre modal con formulario de alta de cliente (Nombre, Teléfono, WhatsApp, Dirección, CUIT).
4. Usuario completa y guarda.
5. El modal se cierra, el combo de clientes se refresca y el nuevo cliente queda seleccionado automáticamente.

**Criterios de aceptación:**
- Modal se abre sin recargar la página.
- Validaciones del formulario de cliente se aplican (Nombre obligatorio, CUIT único si se ingresa).
- Si hay error (ej. CUIT duplicado), se muestra en el modal sin cerrar.
- Al guardar exitosamente, el combo de clientes se actualiza vía AJAX y selecciona el nuevo cliente.

**Capas afectadas:**
- Application: reutilizar `IClienteService.CrearAsync()` existente.
- Web: nuevo partial view `_CrearClienteModal.cshtml`, endpoint AJAX en `ClientesController`, JavaScript en vistas de Venta.

**Riesgos:**  
- Validaciones de duplicados (CUIT) deben funcionar igual que en el CRUD normal de clientes.

**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R3: Combos Anidados para Selección de Productos en Venta

**Alcance:**  
Reemplazar el selector actual de variantes por una interfaz de combos en cascada: Marca → Modelo → Color → Talle.

**Casos de uso:**
1. Usuario selecciona **Marca** en el primer combo.
2. Se cargan dinámicamente los **Modelos** disponibles para esa marca.
3. Usuario selecciona **Modelo**.
4. Se cargan dinámicamente los **Colores** disponibles para ese modelo.
5. Usuario selecciona **Color**.
6. Se cargan dinámicamente los **Talles/Números** disponibles para esa combinación Modelo+Color **que tengan stock > 0**.
7. Usuario selecciona el Talle final y se agrega la variante al detalle de la venta.

**Criterios de aceptación:**
- Los combos se refrescan automáticamente al cambiar el combo anterior.
- Solo se muestran variantes con stock > 0 en Ventas.
- Si no hay stock para una combinación Modelo+Color, se muestra mensaje "Sin stock disponible".
- La selección final identifica unívocamente una `VarianteProducto`.

**Capas afectadas:**
- Application: nuevos métodos en `IProductoService`:
  - `ObtenerMarcasAsync()`.
  - `ObtenerModelosPorMarcaAsync(string marca)`.
  - `ObtenerColoresPorModeloAsync(string marca, string modelo)`.
  - `ObtenerTallesPorModeloColorAsync(string marca, string modelo, string color)` → retorna variantes con stock.
- Web: endpoints AJAX en `ProductosController`, JavaScript de combos en cascada en `VentaCrear/Editar.cshtml`.

**Riesgos:**  
- Performance si hay muchas variantes (>1000) → mitigación con caché de marcas/modelos.

**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R4: Autocompletar Importe de Pago con Total de Venta

**Alcance:**  
Al abrir el modal de "Agregar Pago" en una venta, el campo "Importe" debe autocompletarse con el total pendiente de pago de la venta.

**Casos de uso:**
1. Usuario crea una venta con total de $10,000.
2. Usuario hace clic en "Agregar Pago".
3. El modal se abre con el campo "Importe" ya completado con $10,000.
4. Usuario puede modificar el importe si desea (ej. pago parcial de $5,000).

**Criterios de aceptación:**
- El campo "Importe" se autocompleta con `Venta.Total - SUM(Pagos.Importe)` (total menos pagos ya registrados).
- Si la venta está totalmente paga, el campo se autocompleta con 0 (o se deshabilita el botón "Agregar Pago").
- El usuario puede modificar manualmente el importe.

**Capas afectadas:**
- Web: JavaScript en `_AgregarPagoModal.cshtml` que toma el valor del total pendiente y lo asigna al input.

**Riesgos:** Ninguno.  
**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R5: Combos Anidados para Selección de Productos en Compra

**Alcance:**  
Igual que R3, pero en el módulo de Compras. La diferencia funcional es que **no se filtra por stock** (en Compras se pueden agregar productos sin stock).

**Casos de uso:**
1-7. Igual que R3 (Marca → Modelo → Color → Talle).

**Criterios de aceptación:**
- Igual que R3, pero **sin filtro de stock > 0** (se muestran todas las variantes).

**Capas afectadas:**
- Application: reutilizar los mismos métodos de R3, agregando parámetro `bool incluirSinStock`.
- Web: JavaScript en `CompraCrear.cshtml`.

**Riesgos:** Ninguno.  
**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R6: Pantalla de Consulta Stock Rápida

**Alcance:**  
Nueva pantalla de solo lectura para que el usuario pueda consultar rápidamente el stock disponible, filtrando por Marca, Modelo y/o Talle.

**Casos de uso:**
1. Usuario accede a "Consulta Stock".
2. Puede filtrar por:
   - Marca (combo).
   - Modelo (combo, se carga al seleccionar Marca).
   - Talle (opcional).
3. Se muestra grilla con:
   - Producto (Marca + Modelo).
   - Variante (Color + Talle/Número).
   - Stock actual.
   - Stock mínimo.
   - Alerta si Stock < Stock Mínimo.

**Criterios de aceptación:**
- Filtros son opcionales (sin filtros, muestra todo el stock).
- Grilla es de solo lectura (no permite edición).
- Se resalta en rojo las filas con stock por debajo del mínimo.
- Permite exportar a Excel/PDF (opcional).

**Capas afectadas:**
- Application: reutilizar `IStockService.ObtenerStockConFiltroAsync()`.
- Web: nuevo `StockController.ConsultaRapida()`, vista `Stock/ConsultaRapida.cshtml`.

**Riesgos:** Ninguno.  
**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R7: Cambio/Devolución de Productos desde Venta Finalizada

**Alcance:**  
Permitir al usuario buscar una venta finalizada y realizar cambio (swap de producto) o devolución (reingreso de stock) de manera rápida.

**Casos de uso principales:**

**Caso 1: Devolución total**
1. Usuario busca venta por Fecha, Cliente o Producto.
2. Accede al detalle de la venta.
3. Hace clic en "Realizar Devolución".
4. Selecciona los productos a devolver.
5. Sistema reingresa el stock de las variantes devueltas.
6. Se registra el movimiento de devolución (tabla `VentaCambio`).

**Caso 2: Cambio parcial**
1-3. Igual que devolución.
4. Hace clic en "Realizar Cambio".
5. Selecciona el producto a cambiar.
6. Selecciona el nuevo producto (vía combos anidados).
7. Sistema ajusta stock: reingresa el producto devuelto, egresa el nuevo producto.
8. Ajusta el importe si hay diferencia de precio (genera nota de crédito o cobro adicional).

**Criterios de aceptación:**
- Búsqueda rápida por:
  - Rango de fechas.
  - Cliente (combo o texto libre).
  - Producto (texto libre, busca en Marca+Modelo).
- Solo se pueden cambiar/devolver ventas en estado `Confirmada` o `Entregada`.
- Al devolver, stock se reingresa a la variante original.
- Al cambiar, si hay diferencia de precio:
  - Precio nuevo > precio original → se genera cobro adicional.
  - Precio nuevo < precio original → se genera nota de crédito (saldo a favor del cliente).
- Se registra el movimiento en tabla `VentaCambio` (VentaOrigenId, VentaDestinoId si aplica, Estado, Motivo, Fecha).

**Validaciones:**
- No se puede devolver/cambiar una venta ya devuelta/cambiada (estado `Devuelta` o `Cambiada`).
- Stock de la variante a cambiar debe ser > 0 (no se puede cambiar por un producto sin stock).

**Permisos:**
- Requiere rol `Vendedor` o superior.

**Estados involucrados:**
- `EstadoVenta`: agregar estados `Devuelta`, `Cambiada`.
- `EstadoVentaCambio`: `Pendiente`, `Confirmado`, `Cancelado`.

**Capas afectadas:**
- Domain: nueva entidad `VentaCambio`.
- Application: nuevo servicio `IVentaCambioService`.
- Infrastructure: migración `M4_AgregarVentaCambio`, implementar servicio.
- Web: nuevo controller `VentaCambiosController`, vistas de búsqueda y registro.

**Riesgos:**  
- **Alto:** lógica de negocio compleja (ajuste de stock, cálculo de diferencias de precio, generación de comprobantes).
- **Alto:** riesgo de descuadre de stock si falla a mitad del proceso.
- **Mitigación:** transacciones atómicas, casos de prueba exhaustivos.

**Supuestos:**
- Los cambios/devoluciones se registran **sin flujo de aprobación** (se ejecutan directamente).
  - **⚠️ VALIDAR CON USUARIO:** si requiere aprobación, agregar estado "Pendiente Aprobación" y flujo correspondiente.

**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R8: Rol Empleado con Acceso Restringido

**Alcance:**  
Crear nuevo rol `Empleado` con permisos de acceso **solo** a:
- Ventas (CRUD completo).
- Cambios/Devoluciones (CRUD completo).
- Control de Stock (solo lectura, vía Consulta Stock).

**Casos de uso:**
1. Administrador crea usuario con rol `Empleado`.
2. Usuario `Empleado` inicia sesión.
3. Tiene acceso a:
   - Módulo Ventas.
   - Módulo Cambios/Devoluciones.
   - Consulta Stock (solo lectura).
4. **No tiene acceso** a:
   - Compras.
   - Productos (ABM de productos/variantes).
   - Maestros (Categorías, Subgrupos, Clientes, Proveedores).
   - Configuración.

**Criterios de aceptación:**
- Rol `Empleado` creado en seed de datos.
- Policy `RequireEmpleado` en `Program.cs` que incluye: `SuperUsuario`, `Administrador`, `Vendedor`, `Empleado`.
- Controllers decorados:
  - `VentasController` → `[Authorize(Policy = "RequireEmpleado")]`.
  - `VentaCambiosController` → `[Authorize(Policy = "RequireEmpleado")]`.
  - `StockController.ConsultaRapida` → `[Authorize(Policy = "RequireEmpleado")]`.
  - Resto de controllers → `[Authorize(Policy = "RequireAdministracion")]` (solo SuperUsuario/Administrador).
- Menú de navegación se adapta según rol (oculta opciones sin permiso).

**Capas afectadas:**
- Infrastructure: seed del rol en `SeedData.cs`.
- Web: policies en `Program.cs`, decoradores en controllers, lógica de menú en `_Layout.cshtml`.

**Riesgos:**  
- **Medio:** si se olvida decorar un endpoint, puede quedar expuesto.
- **Mitigación:** auditoría de todos los controllers, pruebas de acceso con cada rol.

**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R9: Importes de Venta Editables Manualmente

**Alcance:**  
Permitir al usuario editar manualmente los campos `PrecioUnitario` (en `VentaDetalle`), `Subtotal` (en `VentaDetalle` y `Venta`) y `Total` (en `Venta`), aunque por defecto se calculen automáticamente.

**Casos de uso:**

**Caso 1: Cálculo automático (comportamiento por defecto)**
1. Usuario agrega producto a la venta.
2. Sistema calcula automáticamente:
   - `VentaDetalle.Subtotal = Cantidad × PrecioUnitario`.
   - `Venta.Subtotal = SUM(VentaDetalle.Subtotal)`.
   - `Venta.Total = Venta.Subtotal - DescuentoMonto`.

**Caso 2: Edición manual de precio unitario**
1. Usuario agrega producto con precio automático de $100.
2. Usuario edita manualmente el precio unitario a $90 (descuento especial).
3. Sistema muestra advertencia: "⚠️ Has editado manualmente el precio. El subtotal no se recalculará automáticamente."
4. Usuario puede:
   - Confirmar → se guarda con el precio editado.
   - Recalcular → restaura el precio automático.

**Caso 3: Edición manual de subtotal o total**
1. Usuario edita el campo `Subtotal` o `Total` directamente.
2. Sistema muestra advertencia: "⚠️ Has editado manualmente el importe. Puede haber inconsistencias."
3. Sistema **no impide** guardar, pero registra un log de auditoría.

**Criterios de aceptación:**
- Por defecto, los importes se calculan automáticamente.
- Todos los campos de importes (`PrecioUnitario`, `Subtotal`, `Total`) son editables en la UI.
- Si el usuario edita manualmente:
  - Se muestra advertencia visible.
  - Se desactiva el recálculo automático para ese campo.
  - Se registra en log de auditoría (Serilog): `Usuario X editó manualmente el precio de la venta Y`.
- Existe botón "Recalcular Todo" que restaura los valores automáticos.
- Se valida coherencia mínima (ej. Total no puede ser negativo).

**Validaciones:**
- `PrecioUnitario >= 0`.
- `Subtotal >= 0`.
- `Total >= 0`.
- Si `Total < Subtotal - DescuentoMonto`, mostrar advertencia (pero no bloquear).

**Capas afectadas:**
- Application: validación `VentaService.ValidarCoherenciaImportes()`.
- Web: JavaScript que maneja la edición manual y el recálculo, checkboxes para activar/desactivar recálculo automático.

**Riesgos:**  
- **Alto:** errores contables si el usuario introduce valores incorrectos.
- **Alto:** posibilidad de fraude (registrar ventas con importes adulterados).
- **Mitigación:**
  - Auditoría obligatoria (log de Serilog).
  - Validaciones mínimas.
  - Revisar reportes periódicamente para detectar inconsistencias.
  - Considerar requerir doble autorización (ej. password de supervisor) para edición manual (⚠️ VALIDAR CON USUARIO).

**Supuestos:**
- El usuario es confiable y tiene motivos legítimos para editar manualmente (ej. descuentos especiales, ajustes por faltantes).
- **⚠️ VALIDAR CON USUARIO:** si se requiere doble autorización o límite de edición (ej. máximo 10% de descuento manual).

**Estado:** 📝 Pendiente diseño técnico.

---

### 🔸 R10 + R12: Refactor del Modelo (Marca/Modelo a Producto)

**Descripción:** Ver **Decisión #2** arriba.

**Estado:** ✅ Aprobado funcionalmente, 📝 Pendiente diseño técnico y migración.

---

### 🔸 R11: Catálogo de Talles Predefinidos

**Alcance:**  
Crear maestro de talles de zapatillas predefinidos con dos rangos:
- **Adultos:** del 34 al 46.
- **Niños:** del 22 al 33.

**Casos de uso:**
1. Administrador accede a "Maestro de Talles de Zapatillas".
2. Ve dos rangos predefinidos (creados por seed).
3. Opcionalmente puede agregar rangos adicionales (ej. "Bebés: 18-21").

**Criterios de aceptación:**
- Tabla `TalleZapatilla` con columnas:
  - `Id` (PK).
  - `RangoTipo` (enum: `Adulto`, `Niño`).
  - `NumeroInicio` (int).
  - `NumeroFin` (int).
- Seed inicial crea:
  - Registro 1: RangoTipo = Adulto, NumeroInicio = 34, NumeroFin = 46.
  - Registro 2: RangoTipo = Niño, NumeroInicio = 22, NumeroFin = 33.
- Opcional: CRUD para administrar rangos (solo SuperUsuario/Administrador).

**Capas afectadas:**
- Domain: nueva entidad `TalleZapatilla`.
- Infrastructure: migración + seed.
- Web: (opcional) CRUD `TallesZapatillaController`.

**Riesgos:** Ninguno.  
**Estado:** 📝 Pendiente diseño técnico.

---

## 3️⃣ PREGUNTAS PENDIENTES DE VALIDACIÓN CON EL USUARIO

### ❓ P1: Flujo de Aprobación en Cambios/Devoluciones (R7)

**Pregunta:**  
¿Los cambios/devoluciones se ejecutan inmediatamente o requieren aprobación de un supervisor/gerente?

**Hipótesis A (asumida por ahora):**  
Se ejecutan directamente (sin flujo de aprobación). El usuario registra el cambio/devolución y el stock se ajusta automáticamente.

**Hipótesis B:**  
Requiere aprobación. Al registrar un cambio/devolución, queda en estado "Pendiente Aprobación" hasta que un supervisor lo confirma.

**Impacto si es B:**
- Agregar estados `Pendiente`, `Aprobado`, `Rechazado` en `VentaCambio`.
- El ajuste de stock solo se ejecuta cuando el estado pasa a `Aprobado`.
- Agregar pantalla de "Aprobar Cambios/Devoluciones" para supervisor.

**Decisión necesaria:** ⚠️ VALIDAR CON USUARIO.

---

### ❓ P2: Doble Autorización para Edición Manual de Importes (R9)

**Pregunta:**  
¿La edición manual de precios en ventas requiere autorización adicional (ej. password de supervisor) o cualquier vendedor puede hacerlo libremente?

**Hipótesis A (asumida por ahora):**  
Cualquier usuario con rol `Vendedor` o superior puede editar manualmente, solo se registra en log de auditoría.

**Hipótesis B:**  
Requiere password de supervisor. Al intentar editar manualmente, el sistema pide confirmación con credenciales de un usuario con rol `Administrador` o `SuperUsuario`.

**Impacto si es B:**
- Implementar modal de "Autorizar Edición Manual" con input de password.
- Validar credenciales del supervisor.
- Registrar en log quién autorizó la edición.

**Decisión necesaria:** ⚠️ VALIDAR CON USUARIO.

---

### ❓ P3: Límite de Descuento en Edición Manual (R9)

**Pregunta:**  
¿Existe un límite máximo de descuento que se puede aplicar manualmente? (ej. máximo 20% del precio original)

**Hipótesis A (asumida por ahora):**  
No hay límite. El usuario puede editar el precio a cualquier valor >= 0.

**Hipótesis B:**  
Hay límite configurado (ej. 20%). Si el usuario intenta aplicar más descuento, se requiere autorización de supervisor.

**Impacto si es B:**
- Agregar configuración `MaximoPorcentajeDescuento` en `appsettings.json`.
- Validar en el frontend y backend.
- Si supera el límite, redirigir a flujo de autorización (P2).

**Decisión necesaria:** ⚠️ VALIDAR CON USUARIO.

---

### ❓ P4: Rol Empleado: ¿Puede Ajustar Stock? (R8)

**Pregunta:**  
El rol `Empleado` tiene acceso de solo lectura a Stock, o también puede realizar ajustes manuales de stock?

**Hipótesis A (asumida por ahora):**  
Solo lectura. No puede ajustar stock, solo consultar.

**Hipótesis B:**  
Puede ajustar stock (ej. corregir diferencias de inventario, registrar roturas).

**Impacto si es B:**
- Agregar policy adicional `RequireAjusteStock`.
- Decorar `StockController.Ajustar()` con esa policy.
- Incluir roles `SuperUsuario`, `Administrador`, `Empleado` en esa policy (pero no `Vendedor`).

**Decisión necesaria:** ⚠️ VALIDAR CON USUARIO.

---

### ❓ P5: Exportación a Excel/PDF en Consulta Stock (R6)

**Pregunta:**  
¿La pantalla de Consulta Stock debe permitir exportar los resultados a Excel o PDF?

**Hipótesis A (asumida por ahora):**  
Opcional, baja prioridad. No se implementa en la primera versión.

**Hipótesis B:**  
Requerido. El usuario necesita exportar para hacer inventarios físicos o reportes.

**Impacto si es B:**
- Implementar endpoint `StockController.ExportarConsultaStockExcel()` y `ExportarConsultaStockPdf()`.
- Utilizar librerías EPPlus (Excel) y QuestPDF (PDF, ya presente en el proyecto).

**Decisión necesaria:** ⚠️ VALIDAR CON USUARIO.

---

## 4️⃣ BANDERAS TEMPRANAS

### 🚩 Requiere Migración EF: **SÍ**

| Migración | Descripción | Riesgo | Requiere Script SQL Manual |
|-----------|-------------|--------|----------------------------|
| **M2_RefactorProductoMarcaModelo** | Mover Marca/Modelo de VarianteProducto a Producto | 🔴 Alto | ✅ Sí |
| **M3_AgregarAnotacionesVenta** | Agregar columna Anotaciones en Venta | 🟢 Bajo | ❌ No |
| **M4_AgregarVentaCambio** | Crear tabla VentaCambio | 🟡 Medio | ❌ No |
| **M5_AgregarTalleZapatilla** | Crear tabla TalleZapatilla + Seed | 🟢 Bajo | ❌ No |

**Migración crítica:** M2 requiere script de validación previo (ver Plan de Implementación, ETAPA 1).

---

### 🚩 Requiere Integración Externa: **NO**

No hay integraciones con servicios externos en este alcance.

---

### 🚩 Requiere Máquina de Estados: **SÍ (Parcial)**

- **Venta:** estados existentes (`Borrador`, `Confirmada`, `Cancelada`).  
  - **Nuevos estados requeridos:** `Devuelta`, `Cambiada`.
- **VentaCambio (nuevo):** estados `Pendiente`, `Confirmado`, `Cancelado` (si se confirma P1 = requiere aprobación).

---

## 5️⃣ SUPUESTOS Y RESTRICCIONES

### Supuestos

1. **No hay variantes sin Marca/Modelo en la BD de producción.**  
   - Validación previa requerida antes de ejecutar M2.

2. **Usuario acepta advertencias de inconsistencia** en importes editados manualmente (R9).

3. **Cambios/devoluciones se ejecutan sin aprobación** (hipótesis A de P1).

4. **Edición manual de precios no requiere doble autorización** (hipótesis A de P2).

5. **No hay límite de descuento en edición manual** (hipótesis A de P3).

6. **Rol Empleado tiene acceso de solo lectura a Stock** (hipótesis A de P4).

7. **Exportación de Stock no es requerida en la primera versión** (hipótesis A de P5).

### Restricciones

1. **Compatibilidad con MySQL:** el proyecto usa MySQL, no SQL Server. `RowVersion` (concurrency token) se gestiona manualmente.

2. **No tocar código de módulos no afectados:** Compras, Remitos, Maestros (Proveedor, TipoPrecioZapatilla) no se modifican salvo por refactor de modelo (R10).

3. **Mantener consistencia de auditoría:** todos los cambios sensibles (edición manual de precios, cambios/devoluciones) deben loguearse en Serilog.

---

## 6️⃣ PRÓXIMOS PASOS (WORKFLOW DEL AGENTE)

1. ✅ **ETAPA 0 (actual):** validar existencia de docs de diseño funcional, arquitectura, presupuesto.
2. 📝 **Esperar aprobación del cliente** de este análisis funcional.
3. 📝 **Derivar al Diseñador Funcional** para que genere `2-disenador-funcional.md` (mockups, flujos de pantallas).
4. 📝 **Derivar al Arquitecto MVC** para que genere `3-arquitecto-mvc.md` (decisiones técnicas, estructura de capas).
5. 📝 **Derivar al Presupuestador** para que genere `4-presupuestador.md` (estimación de horas, riesgos).
6. 📝 **Ejecutar ETAPA 1** (Implementador): refactor crítico del modelo (M2).

---

## 7️⃣ TRAZABILIDAD DE CAMBIOS

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-23 | Creación de documento, registro de decisiones #1 y #2, 12 requerimientos funcionales. | Agente Analista Funcional |

---

**Fin del documento - Analista Funcional**
