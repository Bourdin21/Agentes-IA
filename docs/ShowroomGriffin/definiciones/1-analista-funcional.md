# Analista Funcional — ShowroomGriffin v2
**Fecha última actualización:** 2025-07  
**Estado:** Análisis de impacto completado. Decisiones validadas. Listo para diseño técnico.

---

## Decisiones validadas por el cliente

| # | Pregunta | Decisión confirmada |
|---|---|---|
| P1 | ¿`Anotaciones` es interna o para imprimir? | **A — Nota interna del vendedor** |
| P2 | ¿Unificar `Observaciones` + `Anotaciones`? | **B — Unificar en un solo campo** (renombrar o reutilizar `Observaciones`) |
| P5 | Autofill importe de pago | **A — Sugiere saldo restante** (Total − pagos ya en lista) |
| P11 | ¿Subtotal de línea editable? | **A — No. Solo PrecioUnitario y Cantidad son editables** |
| P12 | ¿Total de venta editable directamente? | **A — No. Es resultado del cálculo** |
| P14 | ¿Marca en Producto = FK a Subgrupo? | **A — Subgrupo se renombra a Marca. SubgrupoId = MarcaId** |
| P13 | ¿Datos en DB son consistentes? | **A — Sí, migración segura** |
| P4 | ¿Combos varían por categoría? | **B — Varía por categoría** |
| P15 | Talles de indumentaria predefinidos | **B — Sí, también predefinidos** (XS, S, M, L, XL, XXL ✅) |
| PC02 | ¿Vendedor crea cliente desde modal? | **B — Sí, datos mínimos (nombre + teléfono)** |
| P10 | ¿Empleado puede crear ventas? | **A — Sí (Vendedor con acceso reducido)** |
| P8 | ¿Devolución desde qué estado? | **B — Desde Confirmada y Entregada** |
| P9 | ¿Combos en modal de cambio? | **A — Sí, mismos combos anidados** |
| P6 | ¿Stock rápido = nueva vista o existente? | **B — Misma vista mejorada visualmente + acceso Empleado** |

---

## Decisión clave adicional (por el cliente)

> **"Marcas y Modelos van a ser entidades anidadas. Subgrupos cambiar por Marcas y modelar nuevo esquema."**

### Nuevo esquema de clasificación

```
Categoría (Indumentaria / Zapatillas / Accesorios)
  └── Marca  [renombrado desde Subgrupo]
        └── Modelo  [NUEVA entidad — hija de Marca]
                └── Producto  [CategoriaId + MarcaId + ModeloId]
                      └── VarianteProducto  [Color + Talle/Numero — SIN Marca ni Modelo]
```

---

## Alcance funcional v2

### INCLUIDO

| Ref | Cambio | Tipo |
|---|---|---|
| C01 | Unificar campo: renombrar Observaciones → Anotaciones (nota interna) | Aditivo |
| C02 | Modal crear cliente rápido (nombre+tel) desde venta, disponible para Vendedor | Nuevo flujo |
| C03 | Combos anidados Marca→Modelo→Color→Talle en ventas (varía por categoría) | Nuevo flujo |
| C04 | Autofill importe pago = saldo restante | UI/JS |
| C05 | Combos anidados en Compras (reutiliza C03) | Nuevo flujo |
| C06 | Vista stock mejorada visualmente + acceso Empleado | Mejora UI + rol |
| C07 | Búsqueda rápida venta (fecha/cliente/producto) en Cambios; desde Confirmada y Entregada | Mejora flujo |
| C08 | Nuevo rol Empleado: Ventas + Cambios + Stock (sin Admin) | Nuevo rol |
| C09 | PrecioUnitario y Cantidad editables; Subtotal/Total calculados (no editables) | UI/JS |
| C10 | Refactor: Subgrupo→Marca, nueva entidad Modelo, quitar Marca/Modelo de VarianteProducto | Refactor estructural |
| C11 | TalleConfig: Zapatilla Adulto 34–46, Zapatilla Niño 22–33, Indumentaria XS–XXL | Nueva entidad + seed |
| C12 | Seed categorías + renombrar labels Subgrupo→Marca en UI | Seed + labels |

### NO INCLUIDO
- Edición directa de Total o Subtotal por línea
- Impresión de anotaciones en remito
- Reportes por Empleado
- Integración con sistemas externos

### DEPENDENCIAS
```
C10 → desbloquea C03, C05, C07
C11 → alimenta C03, C05 (combo talle)
C12 → requiere C10
C08 → requiere definir menú por rol
```

---

## Entidades nuevas y modificadas

### RENOMBRADAS (semántica + labels)
- `Subgrupo` → `Marca` (tabla puede renombrarse `Marcas`)

### MODIFICADAS
| Entidad | Antes | Después |
|---|---|---|
| `Producto` | CategoriaId, SubgrupoId | CategoriaId, MarcaId, ModeloId |
| `VarianteProducto` | Marca (str), Modelo (str), Talle/Numero (str libre) | SIN Marca/Modelo; TalleId FK a TalleConfig |

### NUEVAS
| Entidad | Propiedades | Relación |
|---|---|---|
| `Modelo` | Id, Nombre, MarcaId | Hijo de Marca; padre de Producto |
| `TalleConfig` | Id, Valor (str), Tipo (enum) | FK en VarianteProducto.TalleId |

---

## Casos de uso principales

### CU-01 · Alta de Venta con combos anidados
**Criterios de aceptación:**
- [ ] Al cambiar Categoría se resetean Marca, Modelo, Color, Talle
- [ ] Solo se muestran talles/colores con stock > 0
- [ ] Si no hay variante para la combinación, mensaje claro
- [ ] PrecioUnitario precargado desde VarianteProducto.PrecioVenta, editable
- [ ] Subtotal = PrecioUnitario × Cantidad (no editable)
- [ ] Total = Suma subtotales − Descuento (no editable)
- [ ] Autofill importe pago = Total − pagos ya agregados

### CU-02 · Crear cliente rápido desde modal
**Criterios de aceptación:**
- [ ] Accesible para Vendedor y Empleado
- [ ] Nombre obligatorio; teléfono opcional
- [ ] Nuevo cliente queda seleccionado automáticamente en el Select2 de la venta
- [ ] Visible en módulo Clientes para completar datos después

### CU-03 · Consulta rápida de stock
**Criterios de aceptación:**
- [ ] Rol Empleado puede acceder a /Stock/Index
- [ ] Filtros por Categoría, Marca, Modelo, Color, Talle
- [ ] Precio de costo oculto para Empleado y Vendedor
- [ ] Alerta visual en stock <= StockMinimo

### CU-04 · Cambio/Devolución con búsqueda rápida
**Criterios de aceptación:**
- [ ] Búsqueda por fecha, nombre de cliente (parcial), descripción producto/variante
- [ ] Solo ventas Confirmada o Entregada
- [ ] Para cambio: selección con combos anidados (igual C03)
- [ ] Stock ajustado automáticamente y trazado en MovimientoStock

### CU-05 · Rol Empleado
**Criterios de aceptación:**
- [ ] Puede crear y ver sus propias ventas
- [ ] Puede operar cambios/devoluciones
- [ ] Puede consultar stock (sin precio de costo)
- [ ] NO accede a: Compras, ABM Productos/Variantes, Configuración, Clientes ABM, Usuarios, Auditoría, Resumen semanal, Aumento masivo

---

## Validaciones clave

| Cambio | Validación |
|---|---|
| C01 Anotaciones | Texto libre, max 1000 chars, opcional |
| C02 Modal cliente | Nombre obligatorio; deduplicación por nombre+teléfono |
| C03/C05 Combos | Combinación Marca+Modelo+Color+Talle debe resolver VarianteProductoId existente |
| C07 Dev/Cambio | Venta Confirmada o Entregada; cantidad devuelta ≤ cantidad original |
| C10 Refactor | Migración: no dejar variantes huérfanas; backup previo |
| C11 TalleConfig | Talle debe pertenecer al catálogo de la categoría |

---

## Riesgos

| Riesgo | Mitigación |
|---|---|
| R1 — C10 es el cambio más invasivo | Backup + migración en 2 pasos (agregar columnas, luego quitar) |
| R2 — Combos sin stock confunden usuario | Solo mostrar talles/colores con stock > 0 |
| R3 — Solapamiento Empleado/Vendedor en permisos | Definir menú por rol explícitamente |
| R4 — BuscarVenta solo acepta ID exacto hoy | Ampliar con búsqueda multi-criterio |
| R5 — TalleConfig indumentaria: valores resueltos | ✅ XS, S, M, L, XL, XXL |

---

## C11a — Talles de Indumentaria ✅ RESUELTO

**Decisión confirmada — Opción A:** Solo talle por letra (adulto).  
Valores seed: `XS`, `S`, `M`, `L`, `XL`, `XXL`

### Catálogo TalleConfig completo

| Tipo (enum) | Valores |
|---|---|
| `ZapatillaAdulto` | 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46 |
| `ZapatillaNino` | 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33 |
| `Indumentaria` | XS, S, M, L, XL, XXL |

---

## Banderas de implementación

| Flag | Estado |
|---|---|
| ✅ Requiere migración EF | SÍ — C01, C10, C11, C12 |
| ❌ Integración externa | NO |
| ✅ Máquina de estados impactada | SÍ — C07 (Confirmada + Entregada habilitan devolución) |
| ✅ Nuevo rol/policy | SÍ — C08 Empleado |
| ✅ Nuevas entidades de dominio | SÍ — Modelo, TalleConfig |
| ✅ Refactor entidad existente | SÍ — Subgrupo→Marca, VarianteProducto, Producto |
