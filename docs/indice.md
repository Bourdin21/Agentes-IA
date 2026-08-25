# Indice de proyectos

Registrar una fila por cada proyecto con memoria activa en /docs.

| Proyecto | Fecha inicio | Estado | Carpeta |
|---|---|---|---|
| eleven-la-plata | 2025-07-01 | activo, en producción (dominio propio + HTTPS desde 2026-07-23) — Discovery 2026-08-20: 2 gaps críticos confirmados (cambio de máquina de alquiler/contrato sin validar contadores ni dejar historial; Notifications con 0 filas históricas, nunca se disparó un aviso), pendiente confirmación del cliente para pasar a Análisis | /docs/eleven-la-plata |
| vinosefue | 2025-07-01 | activo | /docs/vinosefue |
| delicias-naturales | 2025-06-01 | cerrado | /docs/delicias-naturales |
| recotrack | 2026-01-01 | cerrado | /docs/recotrack |
| lumitrack | 2026-01-01 | cerrado | /docs/lumitrack |
| piapartments | 2026-01-01 | cerrado | /docs/piapartments |
| ganaderia | 2026-04-22 | abierto | /docs/ganaderia |
| ShowroomGriffin | 2026-04-28 | abierto | /docs/ShowroomGriffin |
| virtualwallet | 2026-04-28 | abierto | /docs/virtualwallet |
| meta-ads | 2026-05-13 | activo | /docs/meta-ads |
| labipac | 2026-06-12 | activo | /docs/labipac |
| contadores-bma-conversor | 2026-06-24 | activo | /docs/contadores-bma-conversor |
| century-21 | 2026-06-25 | activo | /docs/century-21 |
| marihogar | 2026-06-29 | Etapa 1 en producción. CR-44 a CR-55 deployados (19-21/08): pagos de OC programables, fechas editables (compra/recepción/cheque/transferencia), precios de Producto renombrados y editables, CR-52 — bug crítico de facturación AFIP resuelto (certificado + MachineKeySet + Punto de Venta 7 tipo Web Service), confirmado con la primera factura real (CAE 86349291101930), y CR-55 — Nota de Crédito AFIP (flujo formal completo con gate de presupuesto, implementación + QA delegados a subagentes, 1 defecto bloqueante encontrado y corregido antes de deploy). Facturación electrónica AFIP/ARCA operativa end-to-end en producción. Etapa 2 en pausa | /docs/marihogar |
| crm-olvidata | 2026-07-14 | en producción, operativo | /docs/crm-olvidata |
| la-platense | 2026-07-30 | Entrega 1 + Etapa 3 + **Entrega 2 completa (Ventas/Pagos/CC/Caja/Gastos/Entregas/Dashboard) en PRODUCCIÓN REAL** desde 2026-08-24, rama `entrega-1-migracion`. 2 vueltas de QA reales (D1-D16), Descuento/Recargo a %, PAT-016 en 6 listados. Facturación AFIP implementada pero deshabilitada a propósito (sin certificado real) — D8/D9 quedan como riesgo conocido hasta corregirlos | /docs/la-platense |
| diercas | 2026-08-13 | Etapa 1 implementada — sitio Astro (5 páginas + Content Collection de Clientes + formulario de contacto), build local limpio, sin Ciberseguridad/Audio-Video/QR Data Fiscal/Trabajos (Etapa 2) — repo `C:\Sistemas\diercas-front`, deploy pendiente de credenciales FTP DonWeb y SMTP | /docs/diercas |
| koi (KoiDumplings) | 2026-06-11 | Etapa 1 en producción · módulo E2-02 Fichador con Análisis/Diseño/Arquitectura/Presupuesto cerrados (2026-08-10), Implementación en espera de token QuickPass | /docs/koi |
| yaghan-rental | 2026-08-13 | Presupuesto cerrado: desarrollo USD 850 (sistema completo, CRM WhatsApp incluido) + Etapa2 opcional USD 185 + mantenimiento USD 600/año (año 1 gratis) — pendiente envío y aprobación del cliente | /docs/yaghan-rental |
| luciano-inmobiliaria | 2026-08-14 | Presupuesto CERRADO, listo para enviar: Opción A SaaS USD 950 + USD 750/año (año 1 incluido), Opción B código USD 2.250 (números finales fijados por Joaquín) — pendiente confirmar "sueldos" y campo WSFEv1 de facturación por cuenta y orden de terceros antes de Implementación | /docs/luciano-inmobiliaria |
| audifonos-bariloche | 2026-08-19 | Propuesta enviada (pendiente aprobación del lead): sistema de turnos + historia clínica digital con adjuntos, USD 559 desarrollo (Etapa 1 USD 488 + Etapa 2 USD 101, descuento expansión agresiva Tier 1 -USD 177, Tokens IA USD 147) + mantenimiento PREMIUM+3 usuarios USD 800/año — versión funcional sin precios también disponible | /docs/audifonos-bariloche |
| estudio-contable-maribel-garcia | 2026-08-20 | Presupuesto en preparación (no enviado): sistema de conciliación Banco + Mercado Pago, dos opciones cotizadas — Opción A (PHP conversor liviano) USD 325 + STARTER USD 300/año, Opción B (.NET sistema profesional con historial e IA) USD 578 + PRO USD 400/año — pendiente revisión de Joaquín antes de enviar al lead, y confirmar formato real de extractos | /docs/estudio-contable-maribel-garcia |
| cma-centro-medico | 2026-08-21 | Presupuesto en preparación (no enviado): sistema de gestión de pacientes acotado a la sede La Plata (4 sedes existen, alcance reducido a pedido de Joaquín) con historia clínica digital y portal de autogestión del paciente, USD 847 desarrollo (Tier V1 volumen, 5% descuento) + mantenimiento PRO+3 usuarios USD 775/año — discovery el más débil del historial (pain point "Portal de pacientes" sin desarrollar), pregunta abierta central sobre alcance real a confirmar en demo, pendiente revisión de Joaquín antes de enviar | /docs/cma-centro-medico |