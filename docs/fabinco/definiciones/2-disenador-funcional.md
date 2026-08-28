# Memoria - Disenador funcional

## Proyecto: fabinco
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisado `docs/patrones/catalogo.yml` y `docs/*/definiciones/`. **Match de dominio mas fuerte del historial del estudio: `ShowroomGriffin`** (indumentaria/calzado, codigo real ENTREGADO y en produccion) — Productos+Variantes (Color/Talle), Stock por variante, Compras a proveedores, Ventas con pago multi-medio y cuotas (PAT-003), Devoluciones y Cambios (wizard 3 tipos), Aumento masivo de precios, Dashboard. El mensaje outbound de FABINCO menciona explicitamente "cuotas" y "devoluciones" — funcionalidad ya construida ahi.

Reutilizables por codigo real: PAT-003 (MetodoPago), PAT-004 (RowVersion MySQL), PAT-005 (Maquina de estados, si Compras usa workflow), PAT-008 (DataTables+filtros). El diseño completo de ShowroomGriffin (`docs/ShowroomGriffin/definiciones/`) se usa como base directa, adaptando entidades a perfil B2B (Cliente = empresa, no persona).

### Diferencia de perfil frente a ShowroomGriffin — ajustes de diseño
FABINCO es B2B (fabricante/distribuidor, 50 años, venta a empresas por presupuesto) vs. ShowroomGriffin (venta minorista de mostrador). Ajustes:
- `Cliente` gana campos de empresa (RazonSocial, CUIT, CondicionIVA, Contacto) en vez de solo persona fisica.
- Sin necesidad de facturacion electronica AFIP en el alcance base (a diferencia de las dietéticas) — FABINCO ya factura a empresas hace decadas, se asume resuelto en su "otro sistema" actual, a confirmar en demo.
- Dos modulos NO incluidos en el alcance base, solo como pregunta abierta para la demo (ver `1-analista-funcional.md`): gestion de presupuestos/cotizaciones B2B, y trazabilidad de produccion propia (corte y confeccion). Si se confirman, requieren diseño y presupuesto separado — no se fuerza el catalogo de indumentaria minorista sobre una necesidad B2B/industrial que podria ser distinta.

### Historias de usuario (nucleo, anclado en ShowroomGriffin)
- **HU-01 — Productos y variantes**: alta de producto con variantes Color/Talle, SKU/codigo de barra unico, formulario dinamico segun tipo de prenda/calzado.
- **HU-02 — Stock por variante**: descuento automatico al vender, alerta de stock bajo, ajuste manual auditado.
- **HU-03 — Clientes empresa**: alta de cliente B2B (razon social, CUIT, condicion IVA, contacto), historial de compras.
- **HU-04 — Compras a proveedor**: registro de compra que repone stock y actualiza ultimo costo.
- **HU-05 — Venta con cobro multi-medio y cuotas**: carrito, N lineas de pago (PAT-003), cuotas con recargo.
- **HU-06 — Devolucion o cambio**: wizard con 3 tipos (devolucion de dinero, cambio mismo valor, cambio mayor valor), reingreso/decremento de stock segun corresponda.
- **HU-07 — Aumento masivo de precios**: filtros (categoria/subgrupo/marca), preview antes de aplicar, bloqueo optimista (RowVersion).
- **HU-08 — Usuarios y roles**: 3 personas declaradas — roles Administracion / Vendedor / Deposito (a confirmar reparto exacto en demo).
- **HU-09 — Dashboard**: indicadores de ventas, stock critico, deudas de clientes empresa.

*(Fuera del alcance base, a confirmar en demo)* **HU-10 — Presupuestos/cotizaciones B2B**: como vendedor, quiero armar una cotizacion para un cliente empresa (sin cobro inmediato) y hacerle seguimiento hasta que la aprueben o rechacen.
*(Fuera del alcance base, a confirmar en demo)* **HU-11 — Orden de produccion propia**: como administrador, quiero registrar una orden de corte y confeccion (consumo de tela/insumos, cantidad producida) para trazar mi produccion propia, no solo lo que compro ya hecho.

### ViewModels, validaciones, contratos de Services
Identicos en estructura a ShowroomGriffin (`ProductoVarianteViewModel`, `VentaFormViewModel` con `Pagos[]`, `DevolucionWizardViewModel`, etc.) — adaptados con los campos B2B de Cliente. Ver `docs/ShowroomGriffin/definiciones/2-disenador-funcional.md` si existe, o `3-arquitecto-mvc.md`/`4-presupuestador.md` de ese proyecto para el detalle de contratos ya construidos.

## Historial de ajustes
- 2026-08-26: primera version. Diseño anclado directamente en ShowroomGriffin (codigo real en produccion, match de dominio mas fuerte del historial), con Cliente adaptado a perfil B2B y dos modulos candidatos (presupuestos B2B, produccion propia) explicitamente fuera del alcance base hasta confirmar en demo.
