# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-06-11 10:00 - analista-funcional
- Etapa: Discovery + Analisis
- Cambio: relevamiento inicial del proyecto KOI. Análisis exhaustivo de los dos Excel fuente (Estado de Resultados 2024/2025/2026 y Reparto de Utilidades con 100 puntos / 15 inversores). Alcance base de 10 bloques funcionales, 15 casos de uso, criterios de aceptación y banderas (EF sí, integración externa no en base, máquina de estados acotada, migración de datos sí).
- Motivo: pedido del cliente — sistema web con dashboard para inversores que reemplace ambos Excel.
- Impacto en capas: Presentacion, Negocio y Datos (sistema nuevo completo).
- Riesgos/supuestos: fórmulas inconsistentes en el Excel (bases A/B mezcladas en impuestos — el sistema normaliza sobre Ventas A por regla confirmada del cliente); reparto = Resultado Ejercicio sin ajustes; un solo local.

### 2026-06-11 10:30 - analista-funcional
- Etapa: Analisis
- Cambio: tres decisiones de alcance confirmadas por el cliente: (1) cámaras vía web client Hik-Connect embebido (sin RTSP nativo), (2) carga inicial de históricos 2024–2026 INCLUIDA como excepción a la exclusión estándar, (3) integración Ayres POS declarada etapa 2, solo mención sin precio.
- Motivo: definición de alcance previa al diseño para no presupuestar funcionalidades indefinidas.
- Impacto en capas: Negocio y Datos (módulo de importación), Presentacion (pantalla de cámaras).
- Riesgos/supuestos: migración de datos con riesgo alto declarado, acotado a su módulo.

### 2026-06-11 11:00 - disenador-funcional
- Etapa: Diseno
- Cambio: 13 pantallas con wireframes textuales, 12 ViewModels, máquina de estados de período (Abierto/Cerrado/Reabierto) y liquidación (Pendiente/Pagada), lógica de distribución estándar (cards KPI → gráficos → tabla) y theme dark/light sobre tokens del design system Olvidata.
- Motivo: bajar el análisis aprobado a diseño implementable, con el dashboard como core de UX.
- Impacto en capas: Presentacion (pantallas/ViewModels), Negocio (contratos de cálculo y cierre), Datos (requerimientos por pantalla).
- Riesgos/supuestos: iframe Hik-Connect con fallback a pestaña nueva; vista anual solo lectura.

### 2026-06-11 11:30 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: arquitectura sobre blankproject OlvidataSoft (.NET 10 + EF Core + MySQL 8): 15 entidades nuevas (~21 tablas con Identity), 6 servicios de Application, policies por rol con aislamiento del inversor en Application, migración EF inicial + seed. Snapshot de % aplicado por movimiento para no recalcular meses cerrados. Gate aprobado para presupuesto.
- Motivo: validar soporte técnico del diseño y declarar EF/permisos antes de estimar.
- Impacto en capas: Domain/Application/Infrastructure/Web.
- Riesgos/supuestos: volumen bajo (12 períodos/año, 16 usuarios); migración de históricos reconstruye vigencias de puntos.

### 2026-06-11 12:00 - presupuestador
- Etapa: Presupuesto
- Cambio: presupuesto inicial v1 con anclaje histórico (Paso 0 sobre lumitrack/recotrack/delicias/ganaderia): 14 módulos, M total 65.5 h, PERT base 68.79 h, techo interno 78.27 h, fórmula vigente M × $16.80 → USD 1.134 + plan de mantenimiento PREMIUM USD 400/año. Sanity check del total vs delicias-naturales: 4.91 vs 5.0 h base/módulo (ratio 0.98, sin recalibrar). Único ítem con recargo extra: carga inicial de históricos (+25 % riesgo de migración, excepción documentada). Documento cliente emitido en /docs/koi/presupuesto.md.
- Motivo: cierre de la cadena 1→4 para entregar presupuesto al cliente antes de implementar.
- Impacto en capas: n/a (documento).
- Riesgos/supuestos: gatillo de reestimación si los Excel finales difieren de los analizados o si aparece integración no relevada; pendiente aprobación del cliente y cierre de calibración estimado vs real al fin del sprint.

### 2026-06-11 13:00 - presupuestador
- Etapa: Presupuesto
- Cambio: presupuesto v2. (1) Nueva regla global en 27-presupuesto-parametros: cargo fijo de USD 100 por uso de tokens IA en todo presupuesto de proyecto — aplicado a KOI: total desarrollo USD 1.234 (1.134 módulos + 100 tokens IA). (2) manual-de-uso.md actualizado: tarifa USD 14/h reemplazada por la política vigente (USD 35/h, fórmula M × $16.80, horas no expuestas al cliente, cargo tokens IA). (3) Documento cliente /docs/koi/presupuesto.md rehecho con la especificación funcional detallada (11 secciones) para envío al cliente.
- Motivo: pedido del cliente interno — incorporar costo de tokens IA y entregar al cliente final un detalle funcional completo junto al precio.
- Impacto en capas: n/a (documentos y parámetros).
- Riesgos/supuestos: sin cambios en módulos ni horas (M total 65.5 h); solo se agregó la línea fija de tokens IA.

### 2026-06-11 14:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuestador
- Etapa: Analisis → Presupuesto (cascada por cambio de alcance)
- Cambio: nueva funcionalidad pedida por el cliente: notificación automática por correo a los inversores al cerrar el ejercicio mensual (resumen del mes + liquidación personal + aviso de disponibilidad en la web). Cascada completa: CU-16 y criterios en 1-analista (exclusión de correos acotada a "otros envíos"); pantalla P-14, plantilla HTML y efecto en el cierre en 2-disenador; entidades NotificacionConfig/NotificacionEnvio, NotificacionService e IEmailSender (MailKit, post-commit, no bloqueante) en 3-arquitecto (~23 tablas); módulo 15 en 4-presupuestador: M 4.0 h (ref. delicias Notificaciones 3.5 base, ratio 1.24 justificado), USD 67.20. Total desarrollo: USD 1.301 (1.201 módulos + 100 tokens IA) + USD 400/año. Documento cliente actualizado (sección 3.12 y tabla de precios).
- Motivo: pedido del cliente posterior al presupuesto v2; bandera de integración externa pasa a "Sí, acotada (SMTP)".
- Impacto en capas: Presentacion (P-14, plantilla), Negocio (NotificacionService, idempotencia por período), Datos (2 entidades nuevas).
- Riesgos/supuestos: entregabilidad del correo depende del servicio SMTP del cliente; fallos de envío no bloquean el cierre; re-cierre no duplica correos sin confirmación.

### 2026-06-11 15:00 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuestador
- Etapa: Análisis → Presupuesto (cascada por sesión de definición — cierre P-A01 a P-A07)
- Cambio: 7 preguntas abiertas cerradas en sesión con el cliente. Cambios incorporados a los 4 documentos:
  - **P-A01** (comensales): campo `CantidadComensales` agregado a `IndicadorVenta` y a P-06; Ayres en etapa 2.
  - **P-A02** (ventas 4 campos): `VentaMensual` pasa a `VentasASalon / VentasBSalon / VentasADelivery / VentasBDelivery`. Agregados calculados: VentasA, VentasTotales, VentasSalon, VentasDelivery. Nueva torta Salón/Delivery en Dashboard. Riesgo M14 elevado: históricos pueden no tener apertura Salón/Delivery desagregada.
  - **P-A03** (TC con selector): integración `ICotizacionService` copiada de VirtualWallet (ArgentinaDatos histórico + DolarApi hoy, cache 30min/6h). UX: tabla de cotizaciones por casa + default blue promedio + edición manual antes de guardar.
  - **P-A04** (error post-cierre): sin mecanismo técnico. Estado Reabierto del período **eliminado**. Admin + SuperUsuario operan fuera del sistema.
  - **P-A05** (dashboard mes abierto): Dashboard muestra mes abierto con datos parciales; TC pendiente → valores USD como "pendiente".
  - **P-A06** (notificaciones sin expiración): confirmado, sin cambio de arquitectura.
  - **P-A07** (preview editable): P-08 opera en dos modos — Modo A (preview antes del cierre, consumos editables, botón "Confirmar y cerrar") y Modo B (gestión post-cierre). Nuevo ViewModel `LiquidacionPreviewVM`. Nueva entidad `AjusteLiquidacion` para auditar ajuste manual de monto a repartir.
- Motivo: sesión de definición con el cliente — cierre de todas las hipótesis abiertas.
- Impacto en capas: Presentacion (P-03 4 campos, P-06 comensales, P-08 preview dual, Dashboard parcial+torta), Negocio (CotizacionService, eliminación Reabierto, flujo preview→cierre), Datos (VentaMensual 4 campos, AjusteLiquidacion nueva, IndicadorVenta+comensales, ~24 tablas).
- Presupuesto: v3 → **v4 = USD 1.411** (+USD 110 por P-A01/02/03/05/07; ahorro eliminación Reabierto absorbido por complejidad M14 y CotizacionService). Tabla de precios actualizada en presupuesto.md.
- Riesgos/supuestos: riesgo M14 re-elevado y luego **CERRADO en la misma sesión** — ver entrada siguiente.

### 2026-06-11 15:30 - analista-funcional
- Etapa: Análisis (cierre de riesgo M14)
- Cambio: confirmado por el cliente que los Excel históricos **no traen apertura Salón/Delivery** (solo A/B). Estrategia de migración M14 cerrada: `VentasADelivery = VentasBDelivery = 0`; `VentasASalon = VentasA`, `VentasBSalon = VentasB`. Cada período migrado recibe observación automática `"Desglose Salón/Delivery no disponible en datos fuente"`. El Dashboard mostrará 100 % Salón en los períodos históricos hasta el primer mes con datos reales. Delta USD 17 en M14 confirmado y justificado.
- Motivo: respuesta del cliente a la pregunta abierta de M14.
- Impacto en capas: Datos (ImportacionInicialService: lógica de mapeo definida). Sin cambio en entidades ni en el resto del modelo.
- Riesgos/supuestos: R-A2 del arquitecto cerrado. No quedan preguntas abiertas en el análisis funcional de KOI.
