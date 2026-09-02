# Memory Index

- [Verificar vistas Razor](verificar-vistas-razor.md) — el build normal no compila .cshtml; usar MvcBuildViews=true (y limpiar AspnetCompileMerge si da ASPCONFIG)
- [Cuenta corriente Etapa 1 - agenda](cuenta-corriente-etapa1-agenda.md) — implementada y deployada en producción (03/08/2026)
- [AFIP Generar hardening](afip-generar-hardening.md) — incidente de factura duplicada #4139/#4140 en AFIP y el fix aplicado a FacturasController.Generar
- [Pedidos Total sin IVA](pedidos-total-sin-iva.md) — bug real: 4 lugares recalculaban el total sin aplicar IVA en vez de usar el campo Subtotal ya persistido
- [Venta Total drift](venta-total-drift.md) — 23+ ventas en producción con Total desincronizado de la suma de sus líneas, causa no confirmada, sin arreglar
- [Cuenta corriente - gaps agosto](cuenta-corriente-gaps-agosto.md) — race condition en RegistrarPago (2 casos reales corregidos), DeleteConfirmed sin revertir movimientos, NC sin tocar cuenta corriente
- [Desconexiones Ventas - fix agosto](ventas-desconexiones-fix-agosto.md) — machineKey fija, rol Superusuario + auditoría logins, autoguardado localStorage (deploy 26/08/2026)
