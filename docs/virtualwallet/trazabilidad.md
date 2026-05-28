# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-05-11 - implementador
- Etapa: Implementacion — Dolar historico
- Cambio: nueva seccion "Dolar Historico": `ICotizacionService`, `CotizacionService`, `DolarController`, `DolarHistoricoViewModel`, vista `Dolar/Historico.cshtml`. `MovimientosController` actualizado para integrar cotizacion en Create/Edit. Menu actualizado.
- Motivo: permitir ver la cotizacion del dolar a la fecha de cada movimiento y convertir importes en pesos a dolares.
- Impacto en capas: Application (interface), Infrastructure (service), Presentacion (controller + vistas).
- Riesgos/supuestos: sin migracion EF. `CotizacionService` consulta API externa con fallback. Build OK.

### 2026-05-05 - implementador
- Etapa: Implementacion — Mejoras importacion resumen + defectos D-04/D-09/D-10 + mejoras dashboard M-04/M-05/M-06/M-07
- Cambio: cierre defectos QA (D-04 flag EsPagoTarjeta en formulario manual, D-09 rename CuotasActualizadas->CuotasReutilizadas, D-10 persistencia filtros dashboard en Session). Mejoras dashboard: M-04 badge Pendiente Top 10, M-05 columnas Restantes/MontoPendiente en Cuotas Activas, M-06 columna SaldoArrastrado Deuda Tarjeta, M-07 alerta crecimiento categoria >=30%. Migracion `ConstrainDescripcionOriginalLength`. Parsers actualizados. `Program.cs` actualizado.
- Motivo: calidad post-QA y nuevas funcionalidades del dashboard solicitadas por el cliente.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Script idempotente `ConstrainDescripcionOriginalLength.sql` pendiente en produccion.
