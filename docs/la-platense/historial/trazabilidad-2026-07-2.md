<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-05 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-07 (3 bloques archivados)

- 2026-07-30 12:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc
- 2026-07-30 13:00 - presupuesto-mvc
- 2026-07-30 14:00 - orquestador (cierre de presupuesto)

---

### 2026-07-30 12:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuesto-mvc
- Etapa: Analisis → Diseno → Arquitectura → Presupuesto (ajuste en cadena)
- Cambio: dos decisiones de Joaquín. (a) **Nuevo alcance confirmado**: el cliente tiene una ticketeadora de código de barras (propios y de fábrica) — se agrega el módulo "Código de barras — etiquetado + lectura en venta" (7h, Etapa 1) para hacer la carga de la venta más dinámica. (b) **Se retira la migración de catálogo como etapa del presupuesto** — el problema de stock que la motivaba ya está resuelto por el módulo de puesta a punto de stock inicial (independiente de la migración); Joaquín va a hacer un segundo relevamiento tras aprobar este presupuesto para evaluar acceso directo a la base de datos actual del cliente, lo que bajaría mucho el costo real de importación frente a depender de un archivo Excel — se cotiza aparte, más adelante.
- Motivo: alinear el presupuesto con hardware real del cliente (ticketeadora) y no cobrar por adelantado una migración cuya incertidumbre está a punto de resolverse con mejor información (acceso a BD real).
- Impacto en capas: Datos (`Producto.codigoBarras`), Negocio (`EtiquetaService`, `CodigoBarrasLookupService`; se retira `CatalogoMigracionService` de este alcance), Presentación (impresión de etiquetas, campo de escaneo en venta).
- Riesgos/supuestos: **R de Etapa 1+2 bajó de 70,6% a 68,5% — el proyecto pasa de Tier 1 (30% descuento) a Tier 2 (15% descuento)**, tal como se había advertido en la ronda anterior (colchón sobre el umbral ya era mínimo). Nueva pregunta abierta: marca/modelo de la ticketeadora (define si la impresión de etiquetas es simple —impresora estándar de Windows— o requiere protocolo propietario ZPL/EPL, más costoso). Total del proyecto actualizado: Etapa 1 ≈ USD 1.649, Etapa 2 ≈ USD 597 — Total ≈ USD 2.246 (la migración queda fuera, se cotiza en una fase posterior).
### 2026-07-30 13:00 - presupuesto-mvc
- Etapa: Presupuesto (cierre comercial)
- Cambio: Joaquín reestructuró el precio final como dos modalidades de pago del **total del proyecto** (ya no desglosado por etapa en el documento del cliente): **USD 1.500 en hasta 3 pagos**, o **USD 1.800 en hasta 12 pagos**. Además, simplificó el mantenimiento a un único plan **PREMIUM** desde el arranque — año 1 sin costo, USD 500/año desde el año 2 (reemplaza la transición PRO→PREMIUM de versiones anteriores).
- Motivo: cierre comercial — ofrecer flexibilidad de pago al cliente y simplificar el plan de mantenimiento dado que el sistema completo excede ampliamente el rango de tablas de PRO.
- Impacto en capas: económico/comercial, sin impacto técnico.
- Riesgos/supuestos: chequeo de margen con los números propios de Joaquín (30h reales + USD 200 tokens IA) confirma que ambas modalidades quedan por encima del objetivo de USD 35/h (≈USD 43,3/h en la de 3 pagos, ≈USD 53,3/h en la de 12 pagos) — ninguna compromete la rentabilidad esperada.
### 2026-07-30 14:00 - orquestador (cierre de presupuesto)
- Etapa: Presupuesto → Cierre (gate hacia Implementación)
- Cambio: **Cliente aprobó el presupuesto** — modalidad USD 1.500 en hasta 3 pagos, con plan de mantenimiento PREMIUM (año 1 sin costo).
- Motivo: aprobación formal del cliente, habilita el inicio de Implementación según la secuencia obligatoria de `CLAUDE.md` ("No iniciar Implementación sin Presupuesto aprobado por el cliente").
- Impacto en capas: ninguno técnico todavía — gate administrativo.
- Riesgos/supuestos: quedan preguntas abiertas de `1-analista-funcional.md` (§9) sin cerrar antes de Implementación: quién puede anular una venta facturada (admin/vendedor + límite de tiempo). La migración de catálogo sigue pospuesta a una fase posterior (pendiente el segundo relevamiento con acceso a BD real). Antes de desplegar, revisar capacidad de infraestructura disponible en SmarterASP (cupo de bases de datos 17/20 al 2026-07-30) — ver memoria `project-hosting-sharding-smarterasp.md`.
