# Memoria - Arquitecto MVC

## Proyecto: dietetica-mitre
## Ultima actualizacion: 2026-08-26

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Arquitectura identica a `docs/desborder-sin-gluten/definiciones/3-arquitecto-mvc.md` — mismo dominio, mismo alcance, mismo dia habil de diferencia entre ambos leads. Reutilizables por codigo real: `AfipService`/`AfipTokenCache` (PAT-006, `marihogar`), `VentaPago` (PAT-003, `ShowroomGriffin`). Sin match de codigo entregado adicional (desborder-sin-gluten sigue sin implementar).

### Componentes por capa, entidades, migraciones
Identicos a desborder-sin-gluten (`Comprobante`/`ComprobanteItem`/`Producto` en el nucleo compartido B; `Proveedor`/`Compra`/`CompraItem`/`Venta`/`VentaItem`/`VentaPago`/`MovimientoStock` adicionales en A). Unica diferencia: Identity se configura con un solo rol de negocio activo (`Administracion`) en vez de dos, dado que Dietetica Mitre confirmo 1 sola persona sin ambiguedad — el rol `Vendedor` queda definido en el enum/seed de roles pero no se asigna a nadie en la puesta en marcha inicial.

### Riesgos tecnicos activos
Identicos a desborder-sin-gluten: condicion fiscal AFIP no confirmada (bloqueante para `AfipSettings` real), certificado .p12 y Punto de Venta tipo Web Services como dependencia dura del cliente, migracion aditiva sin perdida de datos si pasan de B a A mas adelante.

## Historial de ajustes
- 2026-08-26: primera version. Arquitectura identica a desborder-sin-gluten, con Identity simplificado a 1 rol de negocio activo por confirmarse 1 sola persona.
