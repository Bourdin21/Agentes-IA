# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-07-23 - orquestador (barrido cross-proyecto) — mergeada feature reintegros Mastercard/Visa desde la memoria local del proyecto
- Etapa: 2-3-5 (diseño + arquitectura + implementacion, mergeadas juntas)
- Cambio: se detecto que `C:\Sistemas\virtualwallet\docs\virtualwallet\definiciones\{2-disenador-funcional,3-arquitecto-mvc,5-implementador}.md` (memoria local del proyecto, dated hasta 2026-07-07) tenian una cadena completa de 4 etapas sobre el importador de resumenes de tarjeta que nunca se habia mergeado a este repo central: (1) reintegros M2/M5/M7 (persistir como Ingreso+EsPagoTarjeta=true, dedupe por cupon en linea cruda), (2) ajustes funcionales (cuenta TC por filtro de texto, fecha desde el PDF, USD como fuente de verdad), (3) reescritura completa del parser Visa contra un PDF real (el parser original no matcheaba el formato real del banco), (4) importes ARS/USD en dos columnas + filtros nuevos de Movimientos + KPIs de proyeccion en dashboards. Todo mergeado como bloque unico en `definiciones/5-implementador.md`.
- Motivo: pedido explicito del usuario de auditar cada carpeta de proyecto individual en busca de especificaciones que debieran vivir en la memoria centralizada de Agentes-IA, y mergearlas.
- Impacto en capas: Application (DTOs), Infrastructure (parsers Mastercard/Visa, importer), Web (controller, ViewModels, vistas). Domain sin cambios en ninguna de las 4 partes.
- Riesgos/supuestos: sin migracion EF en ninguna de las 4 partes. **Pendiente de visto bueno de stakeholder**: R5 — reintegros modelados como `Ingreso+EsPagoTarjeta=true` podrian no ser contemplados por reportes historicos que asuman que "Ingreso" nunca lleva ese flag. QA manual end-to-end con PDFs reales (incluyendo un Visa con consumos en USD) tambien pendiente.

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
