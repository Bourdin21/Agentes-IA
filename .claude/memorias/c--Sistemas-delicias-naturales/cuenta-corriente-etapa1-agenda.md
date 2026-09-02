---
name: cuenta-corriente-etapa1-agenda
description: Estado de la implementación de la Etapa 1 (MVP Cuenta Corriente) de Delicias Naturales
metadata:
  node_type: memory
  type: project
  originSessionId: d598e711-73e1-4ffa-8130-c5cbb9032bfe
  modified: 2026-08-04T21:51:23.748Z
---

La Etapa 1 — MVP Cuenta Corriente para Delicias Naturales (presupuesto USD 227 del agente olvidata-ceo) se implementó el 2026-07-31 (a pedido explícito del usuario, adelantando la fecha originalmente pactada para el 10/08). **Ya está deployada en producción** (confirmado por el usuario el 2026-08-03; la tabla `movimientos_cuenta_corriente` y la columna `facturas.EliminadoPorId` ya existen en la base de producción, y la migración EF fue aplicada).

**Qué incluye, ya en producción:**
- `Models/MovimientoCuentaCorriente.cs` + enum `TipoMovimientoCuentaCorriente` (Credito/Debito/AjusteManual/SaldoInicial). Ledger con `Monto` **signado** (positivo = suma saldo a favor, negativo = lo consume).
- `Cliente.GetSaldoCuentaCorriente` + navegación `MovimientosCuentaCorriente`.
- `PagosController.RegistrarPago`: sobrepago genera Crédito real en la cuenta corriente; `MetodoPago == SaldoFavor` valida y debita saldo real (ya no es una etiqueta sin respaldo).
- `PagosController.EliminarPago`: revierte el `MovimientoCuentaCorriente` vinculado.
- `ClientesController.CuentaCorriente(id)` + `RegistrarAjusteCuentaCorriente` (Administrador-only) + vista `Views/Clientes/CuentaCorriente.cshtml`.
- Indicador de saldo en `Clientes/Index.cshtml`/`Details.cshtml`, aviso de saldo disponible en el modal Registrar Pago de Ventas.

**Cómo aplicar:** si se pregunta por el estado de "cuenta corriente", la respuesta es que está **implementada y en producción**, no pendiente. Para cambios futuros sobre este módulo, partir del código ya existente (no reimplementar desde cero).

**Relacionado, mismo lote de deploy (2026-08-03):** listado de Facturas con eliminadas visibles + quién eliminó (`Factura.EliminadoPorId`), fix de `Ventas.RegistrarPago`/roles Vendedor, hardening del flujo `FacturasController.Generar` (ver [[afip-generar-hardening]]), export server-side del catálogo de productos, y un fix de `NullReferenceException` en `Facturas/Details` cuando `Factura.Usuario` es null (facturas eliminadas históricas sin usuario asociado).
