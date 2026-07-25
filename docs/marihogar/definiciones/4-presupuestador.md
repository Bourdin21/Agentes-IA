# Memoria - Presupuestador

## Proyecto: decorhogar *(nombre provisional)*
## Ultima actualizacion: 2026-07-06

## Perfil del proyecto

- Sistema: Gestión comercial completo — reemplazo de Contagram (decoración y hogar)
- Módulos funcionales: 18 (16 E1 + 2 E2)
- Stack: ASP.NET Core MVC .NET 10, EF Core 10, MySQL (Oracle provider), Identity, QuestPDF, Serilog, MailKit
- Integraciones: ARCA WSAA+WSFE (.p12), WhatsApp Business Cloud API (referral Meta), IHostedService cheques
- Horas M total (PERT): 113h (E1: 100h / E2: 13h)
- **Método de precio:** horas reales estimadas × tasa/h real
- Horas reales estimadas: 40h totales (E1: ~35.4h / E2: ~4.6h — distribución proporcional a M)
- Tasa real: USD 30/h
- USD E1: $700 / USD E2: $200
- Total desarrollo: $900
- Tokens IA: no aplica (excluido en este presupuesto)
- Descuento referido: no aplica (eliminado)
- **Total neto al cliente: $900 (primer año de mantenimiento PREMIUM incluido)**
- Mantenimiento: USD 400/año Plan PREMIUM — primer año incluido en total; desde 2do año $400/año
- Tablas reales estimadas: 36 (29 negocio + 7 Identity) → SCALE técnico; conservado PREMIUM por decisión comercial referido
- Fecha de presupuesto: 2026-07-06
- Estado: BORRADOR — pendiente aprobación del cliente

## Nota: excepción AFIP documentada

AFIP/ARCA es exclusión estándar. El cliente confirmó P2-B explícitamente. Incluido en E1 como excepción documentada.

## Mapa de reutilización cross-proyecto (PASO 0)

Código confirmado reutilizable de proyectos del estudio — mismo stack, mismo autor, ya testeado y aprobado en producción:

| Componente reutilizable | Proyecto fuente | Módulo beneficiario | M sin reuso → M adj. |
|---|---|---|---|
| `WhatsAppClient.cs` + `MessagingService.cs` + webhook handler + referral object | BotPublicitario | M8 | 7h → **6h** |
| `AfipService` + `IHostedService` token 24h + `.p12` pattern (WSAA+WSFE) | delicias-naturales | M7 | (rango 7-9h confirmado) |
| `AcreditacionCuotasHostedService` + estados Pendiente→Acreditado→Rechazado | ganadería (v11+) | M14 | 8h → **6h** |
| `AumentoMasivoController` + preview no persistido + batch con RowVersion | ShowroomGriffin | M16 | 4h (feature idéntico) |
| `StockController` ajuste manual + `MovimientoStock` pattern | ShowroomGriffin | M3 | 8h → **6h** |
| `MovimientoCCProveedor` ledger pattern + `CuentaCorrienteController` | vinosefue | M13 | patrón conocido → **4h** |
| `CajaService` + `MovimientoCaja` pattern | ganadería | M11, M15 | reducción aplicada |
| `EgresoService` pattern (sin comprobantes) | ganadería | M18 | 5h → **3h** |

## Anclaje histórico (PASO 1)

| Módulo | Tipo | Referencia principal | M base ref. | M adj. | Motivo reducción |
|---|---|---|---:|---:|---|
| M10 Usuarios | ABM intermedio | ganadería Identity+roles (M=5.5h) | 5.5h | **4h** | 2 roles simples vs 4 de ganadería; policy única |
| M2 Catálogo | ABM complejo | ShowroomGriffin Productos+Variantes (M=10h) | 10h | **8h** | Sin variantes; 1 SKU por producto; sin padre/hijos |
| M3 Stock | ABM complejo | ganadería Stock (M=8h) + ShowroomGriffin ajuste | 8h | **6h** | Reutiliza StockController ajuste manual; sin matriz transiciones |
| M4 Presupuestador + PDF | ABM complejo + PDF | v1 M=9h | 9h | **8h** | Mismo alcance v1; Alpine.js + QuestPDF |
| M5 Ventas + CC local | Financiero workflow | v1 M=12h | 12h | **12h** | Agrega impacto CC local — patrón compensado |
| M6 Entregas | Workflow estados | v1 M=7h | 7h | **6h** | 4 estados directos; sin job diario |
| M7 AFIP ARCA | Integración crítica | delicias-naturales (.p12 + token 24h + WSFE) | 7–9h | **7h** | Patrón confirmado; nuevo CUIT y homologación |
| M11 CC del local | Ledger simple | ganadería MovimientoCaja (M~5h) | 5h | **5h** | Sin drill-down complejo; balance ingreso/egreso |
| M12 Compras + OC | ABM complejo + workflow | ShowroomGriffin M=10h; vinosefue M=10h | 10h | **9h** | 3 estados (vs 4 vinosefue); multi-pago incl. cheques |
| M13 CC proveedores | Ledger reutilizado | vinosefue MovimientoCCProveedor (patrón) | — | **4h** | Patrón ledger vinosefue conocido; implementación nueva |
| M14 Cheques + job diario | Workflow + IHostedService | ganadería EgresoPago + AcreditacionHostedService | 8h | **6h** | Reutiliza IHostedService + ciclo vida idéntico |
| M15 Caja mensual | Reporte + filtro | ganadería CajaService (M~5h) | 5h | **4h** | Solo reporte de período + comparativo; sin drill-down |
| M18 Gastos varios | ABM simple + CC | ganadería EgresoService (sin comprobantes) | 5h | **3h** | Sin adjuntos; categoría + forma pago + CC impact |
| M1 CRM Leads | Workflow + ABM | v1 M=8h | 8h | **7h** | 6 estados + historial; patrón CRM conocido |
| M8 Bot WhatsApp | Integración webhook | BotPublicitario WhatsAppClient; v1 M=7h | 7h | **6h** | Reutiliza WhatsAppClient + MessagingService directo |
| M9 Dashboard | Reporte + KPIs | v1 M=6h | 6h | **6h** | KPIs financieros expandidos; patrón dashboard conocido |
| M16 Aumento masivo | Feature reutilizado | ShowroomGriffin M=4h (feature idéntico) | 4h | **4h** | Copia directa: marca/categoría/modelo + preview + apply |
| M17 Proyección financiera | Alta complejidad | virtualwallet patrón (referencia conceptual) | — | **8h** | Promedio 3m + compromisos futuros + alerta déficit |

## WBS con PERT completo

**Metodología aplicada:** 40 horas reales estimadas × $30/h real = $1,200 total. Distribución por módulo proporcional a M (tasa implícita $10.62/M-hora).

### Etapa 1 — Operativo base (reemplaza Contagram desde el primer día)

| Módulo | Tipo | O | M | P | PERT | USD |
|---|---|---:|---:|---:|---:|---:|
| M10 Usuarios y roles | ABM intermedio | 2.5 | **4** | 6.0 | 4.08 | $30 |
| M2 Catálogo (precio compra/venta, marca, modelo, fotos) | ABM complejo | 5.0 | **8** | 11.0 | 8.00 | $55 |
| M3 Control de stock + ajuste manual | ABM complejo | 4.0 | **6** | 9.0 | 6.17 | $40 |
| M4 Presupuestador + PDF (Alpine.js) | ABM complejo + PDF | 5.5 | **8** | 11.5 | 8.17 | $55 |
| M5 Gestión de ventas + CC local | Financiero workflow | 8.0 | **12** | 17.0 | 12.17 | $85 |
| M6 Entregas a domicilio | Workflow estados | 4.0 | **6** | 8.5 | 6.08 | $40 |
| M7 Facturación ARCA (WSAA+WSFE) | Integración crítica | 5.0 | **7** | 10.0 | 7.17 | $50 |
| M11 Cuenta corriente del local | Ledger simple | 3.0 | **5** | 7.0 | 5.00 | $35 |
| M12 Compras + órdenes de compra | ABM complejo + workflow | 6.0 | **9** | 13.0 | 9.17 | $65 |
| M13 Cuenta corriente proveedores | Ledger reutilizado | 2.5 | **4** | 6.0 | 4.08 | $30 |
| M14 Cheques 30/60/90 + job diario | Workflow + IHostedService | 4.0 | **6** | 9.0 | 6.17 | $40 |
| M15 Caja mensual | Reporte + filtro | 2.5 | **4** | 6.0 | 4.08 | $30 |
| M18 Gastos varios | ABM simple + CC | 2.0 | **3** | 5.0 | 3.17 | $20 |
| M9 Dashboard (KPIs financieros) | Reporte + KPIs | 4.0 | **6** | 8.5 | 6.08 | $40 |
| M16 Aumento masivo de precios | Feature reutilizado | 2.5 | **4** | 6.0 | 4.08 | $30 |
| M17 Proyección financiera | Alta complejidad | 5.5 | **8** | 12.0 | 8.25 | $55 |
| **Subtotal E1** | | | **100h** | | **101.77h** | **$700** |

### Etapa 2 — Automatización por WhatsApp y CRM

| Módulo | Tipo | O | M | P | PERT | USD |
|---|---|---:|---:|---:|---:|---:|
| M1 CRM de Leads | Workflow + ABM | 4.5 | **7** | 10.0 | 7.08 | $110 |
| M8 Bot WhatsApp (referral Meta) | Integración webhook | 4.0 | **6** | 9.0 | 6.17 | $90 |
| **Subtotal E2** | | | **13h** | | **13.25h** | **$200** |

### Totales

| | M total | PERT base | USD |
|---|---:|---:|---:|
| E1 | 100h | 101.77h | $700 |
| E2 | 13h | 13.25h | $200 |
| **Total desarrollo** | **113h** | **115.02h** | **$900** |
| Tokens IA | | | — |
| Primer año mantenimiento PREMIUM | | | incluido |
| **Total neto al cliente** | | | **$900** |

## Autocorrección por ítem (PASO 2)

| Módulo | M adj. | Ref. base | Ratio | Decisión | Motivo |
|---|---:|---:|---:|---|---|
| M10 Usuarios | 4h | 5.5h | 0.73 ⚠️ justificado | Mantener | 2 roles vs 4 ganadería; sin superusuario ni conteo límite de usuarios |
| M2 Catálogo | 8h | 10h | 0.80 ⚠️ justificado | Mantener | Sin variantes padre/hijos; 1 SKU por producto |
| M3 Stock | 6h | 8h | 0.75 ⚠️ justificado | Mantener | Reutiliza patrón ajuste manual ShowroomGriffin; sin matriz transiciones |
| M4 Presupuestador | 8h | 9h | 0.89 ✅ | Mantener | Interpolación v1; mismos drivers Alpine.js + PDF |
| M5 Ventas | 12h | 12h | 1.00 ✅ | Mantener | CC impact adicional compensado con patrón conocido |
| M6 Entregas | 6h | 7h | 0.86 ✅ | Mantener | Sin job diario; 4 estados directos |
| M7 AFIP | 7h | 7h | 1.00 ✅ | Mantener | Patrón confirmado; rango 7-9h |
| M11 CC local | 5h | 5h | 1.00 ✅ | Mantener | Módulo financiero simple; sin drill-down complejo |
| M12 Compras | 9h | 10h | 0.90 ✅ | Mantener | Patrón vinosefue/ShowroomGriffin; 3 estados vs 4 |
| M13 CC proveedores | 4h | — | — | Mantener | Ledger simple; vinosefue confirma viabilidad del patrón |
| M14 Cheques + job | 6h | 8h | 0.75 ⚠️ justificado | Mantener | Reutiliza IHostedService + ciclo de vida idéntico ganadería |
| M15 Caja mensual | 4h | 5h | 0.80 ⚠️ justificado | Mantener | Solo reporte de período; sin drill-down de caja |
| M18 Gastos | 3h | 5h | 0.60 ⚠️ justificado | Mantener | Sin comprobantes adjuntos; EgresoService ganadería directo |
| M1 CRM Leads | 7h | 8h | 0.88 ✅ | Mantener | 6 estados + historial; patrón pedidos vinosefue |
| M8 Bot WhatsApp | 6h | 7–8h | 0.80 ⚠️ justificado | Mantener | Reutiliza WhatsAppClient.cs + MessagingService confirmado |
| M9 Dashboard | 6h | 6h | 1.00 ✅ | Mantener | KPIs expandidos compensados con patrón dashboard conocido |
| M16 Aumento masivo | 4h | 4h | 1.00 ✅ | Mantener | Feature idéntico ShowroomGriffin; copia directa |
| M17 Proyección | 8h | — | — | Aceptar | Sin cierre real comparable; top del rango financiero complejo |

**Nota sobre ratios bajos:** los módulos con ratio < 0.85 tienen reducción justificada exclusivamente por código reutilizable confirmado (mismo stack, mismo autor, ya aprobado en producción). Sin ese contexto, los rangos base sin reducción aplicarían.

## Sanity check del total (PASO 3)

| Comparable | Módulos | M total | Ratio vs decorhogar |
|---|---:|---:|---:|
| ShowroomGriffin (11 módulos + infra) | 11 | 86.6h | 0.77 ✅ — decorhogar tiene 7 módulos adicionales + 2 integraciones |
| Energy Nutrition (14 + 4 integ.) est. | 18 | ~100h | 1.13 ✅ — decorhogar más módulos financieros; EN más catálogo |
| ganadería (8 módulos) | 8 | ~81h | 0.72 ✅ — ganadería tiene mayor complejidad transaccional; decorhogar más módulos simples |

**Conclusión:** 113h M para 18 módulos es coherente. Ratio por módulo: 6.3h/mod (decorhogar) vs 10.1h/mod (ganadería) — correcto dado que decorhogar incluye módulos livianos (caja, gastos, CC proveedores).

## Cierre numérico (PASO 4)

- **Precio fijo:** E1 = $700 / E2 = $200 / Total = **$900**
- Sin descuento por referido (eliminado)
- Sin cargo de Tokens IA (excluido en este presupuesto)
- Primer año de mantenimiento PREMIUM incluido en el total
- **Total neto al cliente: $900** (primer año PREMIUM incluido)
- E1 cliente: **$700** (16 módulos — operación completa + dashboard + herramientas financieras)
- E2 cliente: **$200** (2 módulos — CRM + Bot WhatsApp)
- Mantenimiento desde 2do año: $400/año (Plan PREMIUM — conservado por referido; técnicamente SCALE 36 tablas)

## Requisitos pre-inicio

- **Pre E1:** Certificado digital ARCA (.p12) del CUIT del negocio
- **Pre E2:** Número de teléfono dedicado para el bot (distinto del personal del negocio)

## Riesgos internos

| Módulo | Riesgo | Gatillo de reestimación |
|---|---|---|
| M17 Proyección financiera | Sin referencia de cierre real — único comparable: virtualwallet | Si el cliente pide proyección desagregada por línea de producto |
| M7 AFIP | Homologación puede extender tiempo | Absorbido en M=7h; no genera recargo salvo certificado vencido |
| M14 Cheques | IHostedService job diario en SMARTEASP | Confirmado por ganadería en mismo servidor |
| M2 Catálogo | Si pide resize/CDN para fotos | Reestimar si confirma hosting externo de imágenes |

## Plan de mantenimiento

- Tablas reales contadas: **36** (29 negocio + 7 Identity) → técnicamente Plan SCALE (31+)
- Plan comercial: **PREMIUM USD 400/año** — conservado por tratarse de referido (SCALE sería USD 750/año)
- Primer año incluido en el total al cliente ($1,020). Desde 2do año: USD 400/año.

## Historial de ajustes

- 2026-06-29: Presupuesto v1 ejecutado. 10 módulos (6 E1 + 4 E2). Total bruto $1,378. Neto $1,171 con descuento 15% referido. Estado: borrador. Presupuesto v1 **reemplazado por v2**.
- 2026-07-06: Presupuesto v2 — iteración 1. 18 módulos (13 E1 + 5 E2). Tasa fórmula M×$16.80. Total bruto $2,088. Neto $1,775. Reemplazado en la misma sesión por v2 iteración 2.
- 2026-07-06: Presupuesto v2 — iteración 2. Ajustes: M9 Dashboard + M16 Aumento masivo + M17 Proyección movidos a E1 → 16 E1 + 2 E2. Sin Tokens IA. Tasa override: M×$35 directo. E1 $3,500 / E2 $455. Total $3,955. Desc. 15%: −$593. Neto: $3,362. Reemplazado por iteración 3.
- 2026-07-06: Presupuesto v2 — iteración 3. 40h reales × $30/h = $1,200. E1 $1,060 / E2 $140. Neto $1,020. Reemplazado por iteración 4.
- 2026-07-06: Presupuesto v2 — iteración 4. Traslado $300 de E1 a E2. E1 $760 / E2 $440. Neto $1,020. Reemplazado por iteración 5.
- 2026-07-06: Presupuesto v2 — iteración 5. Primer año PREMIUM incluido en $1,020. Reemplazado por iteración 6.
- 2026-07-06: Presupuesto v2 — iteración 6 (vigente — listo para entrega). Precio fijo: E1 $700 / E2 $200 / Total $900. Sin descuento referido. Primer año PREMIUM incluido. Desde 2do año: $400/año.
