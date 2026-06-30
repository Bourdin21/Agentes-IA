# Memoria - Presupuestador

## Proyecto: decorhogar *(nombre provisional)*
## Ultima actualizacion: 2026-06-29

## Perfil del proyecto

- Sistema: Gestión y automatización de ventas — casa de decoración y hogar
- Módulos funcionales: 10 (6 E1 + 4 E2)
- Stack: ASP.NET Core MVC .NET 10, EF Core 10, MySQL, Identity, QuestPDF
- Horas M total: 76h
- Horas PERT base: 77.17h
- Horas finales (con contingencias variables): 90.97h
- Horas facturables (M/2.5×1.20): 36.48h
- USD desarrollo (M×$16.80): $1,278
- Tokens IA: $100 (prorrateados en E1, no visibles al cliente)
- Total presentado al cliente: $1,378 → E1 $907 / E2 $471
- Mantenimiento: USD 400/año (Plan PREMIUM, ~21 tablas)
- Tasa: USD 35/h (vigente Junio 2026)
- Fecha de presupuesto: 2026-06-29
- Estado: BORRADOR — pendiente aprobación del cliente

## Nota: excepción AFIP documentada

AFIP/ARCA es exclusión estándar. El cliente confirmó P2-B explícitamente. Incluido en E2 como excepción documentada. Precio propio: $118.

## Anclaje histórico (PASO 0)

| Módulo | Tipo | Referencia elegida | Horas base ref | Motivo |
|---|---|---|---:|---|
| M10 Usuarios | ABM intermedio | Ganadería: Usuarios y permisos (M=5.5h) | 5.5h | Mismo tipo: Identity + roles + permisos |
| M2 Catálogo | ABM intermedio | Mediana dataset (4.5h base); Delicias Proveedores (5.4h base) | 4.5–5.4h | ABM con relaciones; fotos = driver extra |
| M3 Stock | ABM complejo | Ganadería: Stock y movimientos (M=14h) — reducción justificada | 14h (proxy) | Sin matriz transiciones ni compensaciones inter-categoría |
| M4 Presupuestador | ABM complejo + PDF | EN: Compras 5 estados (9.8h base); Ganadería Egresos (M=8h) | 8–9.8h | Sin referencia directa — incertidumbre media declarada |
| M5 Ventas | Financiero + workflow | EN: Ventas wizard (M=14.5h); Ganadería Ingresos (M=18h) | 14.5h / 18h | Multi-pago + 5 estados + stock; menos complejo que ambas |
| M6 Entregas | Workflow estados | Ganadería: Rechazos/regularización (M=10.2h) — proxy | 10.2h | 4 estados directos; sin job diario ni lógica 3a/3b |
| M8 WhatsApp | Integración webhook | EN: Sync TN webhooks (8.3h base) | 8.3h | HMAC + BackgroundService; reducción por reutilización BotPublicitario |
| M7 AFIP | Integración crítica | EN: ARCA migración + cert (7.3h base) | 7.3h | WSAA + WSFE + .p12; patrón conocido delicias-naturales |
| M1 CRM Leads | Workflow + ABM | Delicias: Gestión pedidos (7.7h base) | 7.7h | Máquina de estados + ABM; menos complejidad financiera |
| M9 Dashboard | Reporte | Ganadería: Dashboard anual (M=5h) | 5h | Más KPIs que ganadería → M=6h |

## WBS con PERT completo

### Etapa 1 — MVP Operativo

| Módulo | Tipo | Ref. base | O | M adj. | P | PERT | Cont. | Hrs fin. | Hrs fact. | USD |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| M10 Usuarios y roles | ABM intermedio | 5.5h | 3.5 | **5** | 7.0 | 5.08 | 15% | 5.84 | 2.40 | $84 |
| M2 Catálogo productos + fotos | ABM intermedio | 4.5h | 5.0 | **7** | 9.5 | 7.08 | 15% | 8.15 | 3.36 | $118 |
| M3 Control de stock | ABM complejo | 14h↓ | 5.5 | **8** | 11.0 | 8.08 | 15% | 9.29 | 3.84 | $134 |
| M4 Presupuestador + PDF | ABM complejo + PDF | 8–9.8h | 6.5 | **9** | 12.5 | 9.17 | 15% | 10.55 | 4.32 | $151 |
| M5 Gestión de ventas | Financiero + workflow | 14.5h↓ | 8.0 | **12** | 17.0 | 12.17 | 25% | 15.21 | 5.76 | $202 |
| M6 Entregas a domicilio | Workflow estados | 10.2h↓ | 5.0 | **7** | 10.0 | 7.17 | 15% | 8.24 | 3.36 | $118 |
| **Subtotal E1** | | | | **48** | | 48.75 | | 57.28 | 23.04 | **$807** |

### Etapa 2 — Integraciones y Automatización

| Módulo | Tipo | Ref. base | O | M adj. | P | PERT | Cont. | Hrs fin. | Hrs fact. | USD |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| M8 Bot WhatsApp | Integración webhook | 8.3h | 5.0 | **7** | 10.0 | 7.17 | 25% | 8.96 | 3.36 | $118 |
| M7 Facturación AFIP ⚠️ excepción | Integración crítica | 7.3h | 5.0 | **7** | 10.0 | 7.17 | 25% | 8.96 | 3.36 | $118 |
| M1 CRM de Leads | Workflow + ABM | 7.7h | 5.0 | **8** | 11.0 | 8.00 | 15% | 9.20 | 3.84 | $134 |
| M9 Dashboard | Reporte | 5h | 4.0 | **6** | 8.5 | 6.08 | 8% | 6.57 | 2.88 | $101 |
| **Subtotal E2** | | | | **28** | | 28.42 | | 33.69 | 13.44 | **$471** |

### Totales

| | M | PERT base | Hrs fin. | Hrs fact. | USD |
|---|---:|---:|---:|---:|---:|
| E1 | 48h | 48.75h | 57.28h | 23.04h | $807 |
| E2 | 28h | 28.42h | 33.69h | 13.44h | $471 |
| **Total** | **76h** | **77.17h** | **90.97h** | **36.48h** | **$1,278** |
| Tokens IA (en E1) | | | | | $100 |
| **Total cliente** | | | | | **$1,378** |

## Autocorrección por ítem (PASO 7)

| Módulo | Ref. base | PERT base | Ratio | Decisión | Motivo |
|---|---:|---:|---:|---|---|
| M10 Usuarios | 5.5h | 5.08h | 0.92 ✅ | Mantener | 2 roles vs 5 usuarios con límite; sin superusuario productor |
| M2 Catálogo | 4.5h | 7.08h | 1.57 ⚠️ justificado | Mantener | Upload hasta 5 fotos por producto (ProductoFoto + gallery) |
| M3 Stock | 14h | 8.08h | 0.58 ⚠️ justificado | Mantener | Sin matriz de transiciones ni compensaciones inter-categoría |
| M4 Presupuestador | 8–9.8h | 9.17h | 0.97–1.15 ✅ | Mantener | Interpolación entre referencias; PDF + Alpine.js |
| M5 Ventas | 14.5h (EN) | 12.17h | 0.84 borderline justificado | Mantener | Sin wizard/sin autorización precio; sin cuotas ni IVA |
| M6 Entregas | 10.2h | 7.17h | 0.70 ⚠️ justificado | Mantener | Sin job diario, sin opciones 3a/3b, sin acreditación automática |
| M8 WhatsApp | 8.3h | 7.17h | 0.86 ✅ | Mantener | Reutiliza WhatsAppClient + MessagingService de BotPublicitario |
| M7 AFIP | 7.3h | 7.17h | 0.98 ✅ | Mantener | Patrón conocido delicias-naturales; nuevo cert y homologación |
| M1 CRM Leads | 7.7h | 8.00h | 1.04 ✅ | Mantener | 6 estados + historial de contacto + filtros por vendedor |
| M9 Dashboard | 5h | 6.08h | 1.22 ⚠️ justificado | Mantener | 4 KPIs vs 1 de ganadería; conversión leads + top productos |

## Sanity check del total (PASO 8)

| Comparable | Módulos | Hrs base | Ratio vs decorhogar |
|---|---:|---:|---:|
| Ganadería (sin integraciones ext.) | 8 | 81.5h | 0.95 ✅ |
| Vinosefue (workflows) | 16 | ~60h equiv. | 1.29 — justificado: decorhogar tiene integraciones |
| Energy Nutrition (14 + 4 integ.) | 18 | 117.3h | 0.66 — justificado: EN tiene más módulos |

**Conclusión:** total 77.2h es coherente. Sin ajuste adicional.

## Cierre numérico (PASO 9)

- Paso A (preliminar): $1,278 desarrollo + $100 tokens = $1,378
- Paso B (ajustado): sin cambio. $1,378 final.
- E1 cliente: **$1.025** (incluye $118 AFIP + $100 tokens)
- E2 cliente: **$353**
- Subtotal: **$1.378**
- Descuento referido 15%: −$207
- **Total con descuento: $1.171**
- Mantenimiento: $400/año (descuento no aplica a mantenimiento)
- Nota AFIP: movido a E1 por decisión del cliente (2026-06-29)
- Nota bot: M8 incluye reconocimiento de anuncio de origen (referral object Meta API). Flujo por producto específico + preguntas de calificación por categoría. Sin cambio de precio — dentro del alcance y contingencia de M8.

## Plan de mantenimiento

- Tablas estimadas: ~21 (14 negocio + 7 Identity)
- Plan: **PREMIUM (16-30 tablas) — USD 400/año**

## Requisitos del cliente (pre-inicio E2)

- Certificado digital AFIP (.p12) para el CUIT del negocio
- Número de teléfono dedicado al bot WhatsApp (distinto del personal)

## Riesgos internos

| Módulo | Riesgo | Gatillo de reestimación |
|---|---|---|
| M4 Presupuestador | Sin referencia exacta — incertidumbre media | Si el cliente pide PDF con diseño muy personalizado |
| M7 AFIP | Homologación puede extender tiempo | No genera recargo; absorbido en 25% contingencia |
| M2 Catálogo | Si pide resize/CDN para fotos | Reestimar si confirma hosting externo de imágenes |

## Historial de ajustes

- 2026-06-29: Presupuesto inicial ejecutado sobre análisis funcional cerrado. Sin diseño ni arquitectura previos (alcance suficientemente claro para PERT). Total $1,378. E1 $907 / E2 $471. Estado: borrador pendiente aprobación.
