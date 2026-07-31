# Memoria - Presupuestador

## Proyecto: marihogar
## Ultima actualizacion: 2026-07-24 (cierre de calibracion Etapa 1)

## Cierre de calibracion — Etapa 1 (2026-07-24)

- **Estado: Etapa 1 aprobada por el cliente, implementada 100% (16/16 modulos, 6 sprints, QA GO en todos), documentacion de alcance entregada.**
- Alcance: sin desvio. Ningun modulo agregado ni recortado respecto de lo presupuestado.
- Horas: no comparable al dataset historico de `27-presupuesto-parametros.instructions.md`. Este proyecto se ejecuto con implementacion y QA 100% delegadas a agentes IA orquestados (ver detalle completo en `trazabilidad.md`, entrada "cierre de calibracion estimado vs real"), sin horas de desarrollador humano registradas — a diferencia de todo el dataset de referencia, que mide tiempo humano (asistido por IA). No se fuerza un numero de "horas reales" homologable para no violar la regla de no inventar datos de calibracion.
- Precio: USD 700 (Etapa 1) dentro del total fijo de USD 900, ya cobrado por precio cerrado — no afectado por el hallazgo anterior.
- **Recomendacion para el estudio**: si este modelo de entrega (implementacion agentic de punta a punta) se repite en otros proyectos, abrir una categoria de calibracion separada en `27-presupuesto-parametros.instructions.md` anclada en costo/tiempo de computo de agentes, no en horas humanas — recien despues de tener 2-3 cierres con este mismo patron para poder anclar un rango confiable.

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

| Comparable | Módulos | M total | Ratio vs marihogar |
|---|---:|---:|---:|
| ShowroomGriffin (11 módulos + infra) | 11 | 86.6h | 0.77 ✅ — marihogar tiene 7 módulos adicionales + 2 integraciones |
| Energy Nutrition (14 + 4 integ.) est. | 18 | ~100h | 1.13 ✅ — marihogar más módulos financieros; EN más catálogo |
| ganadería (8 módulos) | 8 | ~81h | 0.72 ✅ — ganadería tiene mayor complejidad transaccional; marihogar más módulos simples |

**Conclusión:** 113h M para 18 módulos es coherente. Ratio por módulo: 6.3h/mod (marihogar) vs 10.1h/mod (ganadería) — correcto dado que marihogar incluye módulos livianos (caja, gastos, CC proveedores).

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

## Presupuesto — Change Request #1: feedback primera demo (2026-07-27)

Sobre arquitectura v2 aprobada (`3-arquitecto-mvc.md`). Es un presupuesto de **modificación sobre módulo ya entregado** (Etapa 1 en producción), no un módulo nuevo — se ancla en la tabla "Modificación sobre módulo existente" de `27-presupuesto-parametros.instructions.md`, con excepción de CR-6 (import de histórico), que es esfuerzo comparable a un parser propietario nuevo.

### PASO 0 — Anclaje histórico
- CR-1/CR-2: reutilización directa de patrones ya resueltos en `ganaderia - emo` (`FacturaVenta`/`FacturaVentaIngreso`) — banda "Modificación sobre módulo existente" (0.5–2h), no "módulo nuevo".
- CR-3/CR-5/CR-7: campo condicional de un select / regla de negocio nueva sobre pantalla existente — banda 0.5–2h.
- CR-4: mezcla de campo nuevo + endpoint público — sin referencia 1 a 1 exacta, ancla entre "ajuste puntual" y "integración WS simple" (3–4h) por el componente de seguridad nuevo.
- CR-6: comparable a "Parser Excel propietario" (contadores-bma-conversor, 4h reales por archivo simple) pero con 4 archivos de estructura distinta y reglas de negocio propias cada uno (matching de producto, mapeo de categoría, saldo inicial) — se estima por encima del piso de esa banda, no como 4 parsers independientes completos.

### WBS con PERT

| Ítem | Tipo | O | M | P | PERT | Riesgo | USD (M×$16.80) |
|---|---|---:|---:|---:|---:|---|---:|
| CR-1 OC: tipo comprobante + impuestos (IVA/IIBB/Otros) + migración datos | Modificación módulo existente | 3.5 | **5** | 7.5 | 5.17 | Medio 15% | $84 |
| CR-2 Cheque: fecha de emisión + autocálculo vencimiento | Ajuste puntual con lógica derivada | 1.5 | **2** | 3 | 2.08 | Bajo 8% | $34 |
| CR-3 Venta: tarjeta de crédito (cuotas+interés) + Banco Carrefour | Campo condicional de un select | 2 | **3** | 4.5 | 3.08 | Bajo 8% | $50 |
| CR-4 Descargar/enviar comprobante por WhatsApp + endpoint público con token | Ajuste + mini-integración (seguridad) | 3 | **4** | 6 | 4.17 | Medio 15% | $67 |
| CR-5 Categorías de gasto (nuevo set + migración de datos existentes) | Regla de negocio + migración de datos | 2 | **3** | 4.5 | 3.08 | Medio 15% | $50 |
| CR-6 Importador de histórico (4 archivos reales: proveedores/compras/ventas/gastos) | Parser propietario multi-archivo | 7 | **10** | 15 | 10.33 | Alto 25% | $168 |
| CR-7 Cheques: acreditación manual (job pasa de acreditar a solo notificar) | Ajuste puntual de lógica | 1.5 | **2** | 3 | 2.08 | Bajo 8% | $34 |
| **Total** | | | **29h** | | **30.0h** | | **$487** |

### Autocorrección por ítem
Todos los ítems dentro de rango (ratio 0.85–1.15) respecto de la banda de referencia elegida — sin ajustes adicionales. CR-6 es el único sin referencia histórica exacta (parser multi-archivo con reglas de negocio distintas por archivo, no un solo parser homogéneo) — aceptado con incertidumbre declarada (Alto 25%), sujeto a reestimación si al analizar los 4 archivos en profundidad durante la implementación aparecen más casos de borde de los ya relevados en el análisis.

### Cierre numérico
- Tokens IA: **no aplica** — mismo criterio que el presupuesto original de Etapa 1 de este cliente (excluido explícitamente, no se introduce ahora un cargo nuevo no visto antes por el cliente).
- Sin descuento.
- **Total Change Request #1: USD 487.**
- Condición comercial: 100% al aprobar (a diferencia del 50/50 por etapa de un proyecto nuevo — es un ajuste puntual de alcance menor, no una etapa completa).

### Requisitos previos del cliente antes de implementar — **los 3 resueltos el 2026-07-27**
- **CR-4** ✅: confirmado — el PDF cuando no hay Comprobante AFIP emitido es el **comprobante remito de la venta**.
- **CR-5** ✅: confirmado — "Marketing"→Publicidad y "APR"→APR son correctos.
- **CR-6** ✅: confirmado, con una decisión adicional del cliente — los Excel son la fuente de verdad, no lo que hay hoy cargado en producción (incluida la propia actividad de prueba del cliente). **Se vacían las tablas de producción de las entidades con dato en los Excel antes de importar** (plan y salvaguardas en `3-arquitecto-mvc.md`, sección CR-6). Sin cambio de presupuesto por esta decisión — el vaciado es una operación de datos de bajo esfuerzo (`DELETE` scripteado), ya contemplado dentro del ítem CR-6 ($168).

### Riesgos y supuestos
Ver tabla de riesgos técnicos completa en `3-arquitecto-mvc.md` (sección Arquitectura v2). Riesgo comercial: CR-6 es el ítem de mayor incertidumbre del lote — si durante la implementación se detectan más de ~5 reglas de negocio adicionales no relevadas en el análisis (ej. formatos de fecha inconsistentes, productos con el mismo nombre pero distinto precio en distintas filas, etc.), se declara gatillo de reestimación explícito para ese ítem puntual, no para el resto del change request.

## Presupuesto — Adenda Change Request #1: CR-8 y CR-9 (2026-07-27)

Sobre análisis v4 (`1-analista-funcional.md`). Ambos ítems se pliegan al Sprint CR-B (todavía no arrancado) — no reabren el presupuesto ya aprobado de CR-1/2/7 (Sprint CR-A, ya en implementación).

| Ítem | Tipo | M | USD (M×$16.80) |
|---|---|---:|---:|
| CR-8 Sugerir total como monto de pago por defecto | Ajuste puntual de UI | 1h | $17 |
| CR-9 Reportes: desglose facturado/no facturado | Regla de negocio + ajuste de reporte | 3h | $50 |
| **Subtotal adenda** | | **4h** | **$67** |

**Nuevo total del Change Request #1: USD 487 + USD 67 = USD 554.** Mismas condiciones ya acordadas (100% al aprobar, sin Tokens IA). Sin necesidad de un nuevo gate de aprobación separado — son ítems menores que se suman al mismo Change Request ya aprobado por el cliente, informados en la misma conversación en la que se pidieron; se documenta el monto actualizado para que quede trazado, no para volver a pedir aprobación de cero.

## Presupuesto — Ampliación CR-10/CR-11/CR-12: auditoría de columnas del histórico (2026-07-27)

Sobre arquitectura v3 (`3-arquitecto-mvc.md`). Mismo criterio de anclaje que el resto del Change Request #1: "modificación sobre módulo existente", banda 0,5-2h por ítem (campo nullable simple sobre entidad ya existente, sin lógica de negocio nueva ni migración de datos sobre filas ya cargadas).

### WBS con PERT

| Ítem | Tipo | O | M | P | PERT | Riesgo | USD (M×$16.80) |
|---|---|---:|---:|---:|---:|---|---:|
| CR-10 OC: Punto de Venta + Nº de comprobante | Campo condicional sobre bloque ya existente | 1 | **1,5** | 2,5 | 1,58 | Bajo 8% | $25 |
| CR-11 Gasto: Subcategoría (campo + ajuste importador CR-6) | Campo nuevo + ajuste script | 1 | **1,5** | 2,5 | 1,58 | Bajo 8% | $25 |
| CR-12 Venta: Nota interna (campo + ajuste importador CR-6, con verificación de no-filtración a PDF) | Campo nuevo + ajuste script + verificación de seguridad | 1,5 | **2** | 3 | 2,08 | Bajo 8% | $34 |
| **Total** | | | **5h** | | **5,25h** | | **$84** |

### Autocorrección por ítem
Los 3 ítems dentro de rango (ratio 0,85-1,15) respecto de la banda "modificación sobre módulo existente" ya usada para CR-2/CR-3/CR-5/CR-7. CR-12 lleva 0,5h adicional sobre CR-10/CR-11 por la verificación explícita de que `NotaInterna` no aparezca en ningún PDF generado (control de seguridad/alcance, no complejidad de campo).

### Cierre numérico
- Tokens IA: no aplica (mismo criterio del resto del proyecto).
- Sin descuento.
- **Total ampliación CR-10/11/12: USD 84.**
- Condición comercial: 100% al aprobar, mismo criterio que el resto del Change Request #1.

**Nuevo total acumulado del Change Request #1: USD 554 + USD 84 = USD 638.** (CR-1 a CR-7: $487; adenda CR-8/CR-9: $67; ampliación CR-10/11/12: $84.)

### Requisitos previos del cliente antes de implementar
Ninguno — los 3 ítems no tienen preguntas abiertas (a diferencia de CR-4/CR-5/CR-6, que sí las tuvieron). **Estado: APROBADO por el cliente el 2026-07-27** (con implementación diferida a pedido del cliente — "apruebo, pero esperar" — y orden de arranque explícita dada después, ver `trazabilidad.md`). Implementado en Sprint CR-E, con QA GO.

### Riesgos y supuestos
Riesgo bajo en los 3 ítems — son campos `string?` nullable sin lógica de negocio ni migración de datos sobre filas ya cargadas (CR-6 aún no corrió en producción). Sin gatillo de reestimación previsto.

## Adenda — CR-14 a CR-18: mejoras post-migración (2026-07-28)

Sobre arquitectura v4. Mismo criterio que CR-8/CR-9/CR-13: adenda de bajo esfuerzo sobre el Change Request #1 ya aprobado, sin gate de presupuesto nuevo (se informa el costo agregado, no se vuelve a pedir aprobación de cero).

| Ítem | Tipo | M | USD (M×$16.80) |
|---|---|---:|---:|
| CR-14 Saldo calculado en CC Local + CC Proveedores | Cálculo derivado sobre listado existente | 1,5h | $25 |
| CR-15 Cheque OC: fecha de emisión por defecto | Ajuste puntual de JS | 0,5h | $8 |
| CR-16 Mayúsculas Proveedor/Producto (normalización + datos existentes) | Regla de negocio simple + fix de datos | 1h | $17 |
| CR-17 Unificación de Proveedor duplicado | Operación de datos (sin código) | 0,5h | $8 |
| CR-18 Ajuste de apertura saldo $0 | Extensión de script existente | 1,5h | $25 |
| CR-13 (refinamiento) ClienteCUIT en factura histórica | Ajuste menor sobre CR-13 ya presupuestado | 0,5h | $8 |
| **Subtotal adenda** | | **5,5h** | **$91** |

**Nuevo total acumulado del Change Request #1: USD 638 + USD 91 = USD 729.** Mismas condiciones ya acordadas (100% al aprobar, sin Tokens IA).

## Cierre — Change Request #1 completo, ejecutado en producción (2026-07-28)

**Estado: CERRADO.** Los 20 ítems del Change Request #1 (CR-1 a CR-20, total **USD 729**, sin incluir CR-19/CR-20 que fueron pedidos adicionales sin cargo por ser correcciones/mejoras de bajo esfuerzo sobre el mismo lote) están implementados, con QA en GO, y **ejecutados contra producción real** el 2026-07-28: 12 migraciones EF aplicadas, 20 tablas vaciadas y reimportadas con el histórico real (31 Proveedores/239 OC/634 Ventas/480 Gastos/207 Productos/286 Comprobantes AFIP), código deployado, certificado AFIP real conectado y verificado con un login WSAA exitoso contra AFIP producción. Detalle completo de la ejecución en `trazabilidad.md`, entrada "EJECUCIÓN REAL EN PRODUCCIÓN — Change Request #1 completo, CR-1 a CR-20".

## Presupuesto — Change Request #2: CR-21/CR-22, doble precio + edición de precio/subtotal en Ventas (2026-07-28)

Primer ítem fuera del Change Request #1 (que ya cerró en producción) — nuevo pedido del cliente sobre el sistema ya operando con datos reales. Se ancla igual que el resto del historial: "modificación sobre módulo existente" para CR-21 (campo + rename), y "financiero workflow sensible" para CR-22 (toca el service crítico de Ventas + un control de seguridad nuevo).

### WBS con PERT

| Ítem | Tipo | O | M | P | PERT | Riesgo | USD (M×$16.80) |
|---|---|---:|---:|---:|---:|---|---:|
| CR-21 Producto: Precio Efectivo + Precio de Lista calculado (rename + UI catálogo) | Modificación módulo existente | 2 | **3** | 4,5 | 3,08 | Bajo 8% | $50 |
| CR-22 Ventas: precio/subtotal editables (solo Admin) + selector IVA por línea + control de seguridad server-side | Financiero workflow sensible + control de acceso | 5 | **7** | 10,5 | 7,25 | Alto 25% (manejo de dinero + control de fraude) | $118 |
| **Total** | | | **10h** | | **10,33h** | | **$168** |

### Autocorrección por ítem
CR-21 dentro de la banda estándar de campo+rename ya usada en el proyecto (ratio 1,0). CR-22 se ancla por encima de un ajuste puntual típico porque, a diferencia del resto del historial de change requests, toca directamente el control de autorización de un flujo que maneja dinero real (riesgo de fraude si se implementa mal) — mismo criterio de "Alto 25%" ya usado para CR-6 (el otro ítem de mayor riesgo del historial), aunque por una razón distinta (seguridad, no incertidumbre de datos).

### Cierre numérico
- Tokens IA: no aplica (mismo criterio del resto del proyecto).
- Sin descuento.
- **Total Change Request #2: USD 168.**
- Condición comercial: 100% al aprobar, mismo criterio que el resto.

### Riesgos y supuestos
Riesgo principal ya identificado y mitigado en el diseño: el control de precio/subtotal debe revalidarse 100% server-side por rol, nunca confiar en que la UI oculte el campo — QA debe probar explícitamente un intento de bypass (POST directo simulando Vendedor con precio manipulado) antes de dar este ítem por cerrado.

## Presupuesto — Change Request #3: CR-24, correcciones y extensión de pagos en Ventas (2026-07-30)

| Ítem | Tipo | M | USD (M×$16.80) |
|---|---|---:|---:|
| CR-24.1/24.2 Fix IVA + layout de precio de línea (4 elementos) | Bugfix + ajuste de UI | 2h | $34 |
| CR-24.3 Total editable con reparto proporcional | Ajuste de UI con lógica derivada | 2h | $34 |
| CR-24.4 Pagos posteriores sobre Venta (mirror de Compras) + redirect a Details | Financiero workflow, mirror de patrón ya existente | 4h | $67 |
| **Total** | | **8h** | **$135** |

Anclado en la banda "modificación sobre módulo existente" salvo CR-24.4, que se ancla contra el propio `PagoOrdenCompraService` ya implementado en este proyecto (mismo patrón, menor incertidumbre que un desarrollo desde cero).

**Total Change Request #3: USD 135.** Mismas condiciones ya acordadas (100% al aprobar). Con esto, el trabajo fuera del Change Request #1 acumula: CR-21/22 (USD 168) + CR-24 (USD 135) = USD 303.

## Presupuesto — Change Request #4: CR-25/CR-26, comprobante editable + rediseño de PDFs + QR AFIP (2026-07-30)

| Ítem | Tipo | M | USD (M×$16.80) |
|---|---|---:|---:|
| CR-25 Comprobante AFIP totalmente editable | Ajuste de validación + UI (mirror de CR-24.3) | 3h | $50 |
| CR-26 Rediseño visual remito + factura PDF | Ajuste visual | 3h | $50 |
| CR-26 Código QR de AFIP (hallazgo de cumplimiento, no solicitado) | Integración nueva (paquete NuGet + spec externa) | 3h | $50 |
| **Total** | | **9h** | **$150** |

**Total Change Request #4: USD 150.** Mismas condiciones ya acordadas. Acumulado fuera del Change Request #1: CR-21/22 ($168) + CR-24 ($135) + CR-25/26 ($150) = **USD 453**.

## Presupuesto — CR-27: Cuenta Corriente de Proveedores real (2026-07-30)

La corrección del Total de las 239 OC históricas (impuestos reales, hallazgo 1) y el reemplazo de los pagos ficticios de CR-19 por los pagos reales (hallazgo 2) se tratan **sin cargo**, mismo criterio que CR-23: es una corrección de un dato ya migrado incorrectamente dentro del alcance ya cobrado de CR-6/CR-19 (Change Request #1), no una funcionalidad nueva — el cliente entregó un archivo más completo que el usado originalmente y el sistema debe reflejar la realidad.

Sí son alcance nuevo (no correctivo) las 2 capacidades que el sistema no tenía antes de CR-27:

| Ítem | Tipo | M | USD (M×$16.80) |
|---|---|---:|---:|
| CR-27.4 Mercado Pago habilitado para pagar a Proveedores | Ajuste de configuración + UI (mirror de método ya existente) | 1h | $17 |
| CR-27.5 Nota interna en OrdenCompra | Campo nuevo (mirror exacto de `Venta.NotaInterna`, CR-12) | 1.5h | $25 |
| **Total** | | **2.5h** | **$42** |

**Total Change Request #5: USD 42.** Mismas condiciones ya acordadas (100% al aprobar). Acumulado fuera del Change Request #1: CR-21/22 ($168) + CR-24 ($135) + CR-25/26 ($150) + CR-27 ($42) = **USD 495**.

## Historial de ajustes
- 2026-07-28: Presupuesto Change Request #2 (CR-21/CR-22) — USD 168. Primer ítem del proyecto fuera del Change Request #1 ya cerrado en producción. Orden de implementación ya dada por el cliente en el pedido original (aprobación implícita del alcance, mismo criterio que adendas de bajo monto anteriores).
- 2026-07-28: Adenda CR-14 a CR-18 (mejoras post-migración) + refinamiento de CR-13 — USD 91 adicionales. Nuevo total acumulado del Change Request #1: USD 729. CR-17 (unificación de Proveedor duplicado) y la normalización de mayúsculas sobre datos ya cargados se ejecutaron directamente contra `marihogar_dev` el mismo día. Sin gate de presupuesto nuevo — se implementa junto con el resto del lote (Sprint CR-F).
- 2026-07-27: Cliente aprobó el presupuesto de la ampliación CR-10/CR-11/CR-12 (USD 84) **pero pidió esperar antes de implementar** — no es un rechazo, es aprobación con implementación diferida. Nuevo total acumulado del Change Request #1: **USD 638, aprobado**. **Estado: APROBADO — implementación en espera de que el cliente dé la orden de arranque explícita** (no se inicia Implementación solo por esta aprobación; se necesita una confirmación nueva puntual, mismo criterio que la ejecución de CR-6 en producción, que también está en espera).
- 2026-07-27: Presupuesto ampliación CR-10/CR-11/CR-12 (auditoría columna por columna del histórico) — USD 84 adicionales. Nuevo total acumulado del Change Request #1: USD 638. **Estado: BORRADOR — pendiente aprobación del cliente (gate duro antes de Implementación).**
- 2026-07-27: Adenda CR-8 + CR-9 al Change Request #1 — USD 67 adicionales (total USD 554), a implementar en Sprint CR-B.
- 2026-07-27: Presupuesto Change Request #1 cerrado — feedback primera demo (CR-1 a CR-7). Total USD 487, sin Tokens IA (mismo criterio del presupuesto original), 100% al aprobar. Ítem de mayor riesgo: CR-6 (importador de histórico, Alto 25%, sin referencia histórica exacta 1 a 1). **Estado: BORRADOR — pendiente aprobación del cliente (gate duro antes de Implementación).**

- 2026-06-29: Presupuesto v1 ejecutado. 10 módulos (6 E1 + 4 E2). Total bruto $1,378. Neto $1,171 con descuento 15% referido. Estado: borrador. Presupuesto v1 **reemplazado por v2**.
- 2026-07-06: Presupuesto v2 — iteración 1. 18 módulos (13 E1 + 5 E2). Tasa fórmula M×$16.80. Total bruto $2,088. Neto $1,775. Reemplazado en la misma sesión por v2 iteración 2.
- 2026-07-06: Presupuesto v2 — iteración 2. Ajustes: M9 Dashboard + M16 Aumento masivo + M17 Proyección movidos a E1 → 16 E1 + 2 E2. Sin Tokens IA. Tasa override: M×$35 directo. E1 $3,500 / E2 $455. Total $3,955. Desc. 15%: −$593. Neto: $3,362. Reemplazado por iteración 3.
- 2026-07-06: Presupuesto v2 — iteración 3. 40h reales × $30/h = $1,200. E1 $1,060 / E2 $140. Neto $1,020. Reemplazado por iteración 4.
- 2026-07-06: Presupuesto v2 — iteración 4. Traslado $300 de E1 a E2. E1 $760 / E2 $440. Neto $1,020. Reemplazado por iteración 5.
- 2026-07-06: Presupuesto v2 — iteración 5. Primer año PREMIUM incluido en $1,020. Reemplazado por iteración 6.
- 2026-07-06: Presupuesto v2 — iteración 6 (vigente — listo para entrega). Precio fijo: E1 $700 / E2 $200 / Total $900. Sin descuento referido. Primer año PREMIUM incluido. Desde 2do año: $400/año.
