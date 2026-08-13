# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-12 09:00 - orquestador (arranque de proyecto)
- Etapa: Discovery
- Cambio: creada la carpeta `docs/yaghan-rental/` desde `docs/templates/proyecto/`. Examinada la web del cliente (`https://yaghanrental.com.ar/tienda/`) para relevar catálogo, precios, canales de contacto. Escaneado `docs/*/definiciones/` de todo el historial: reutilización identificada en CRM WhatsApp (`crm-olvidata`) y caja diaria (`la-platense`); comisión por referido, QR de devolución y pricing escalonado por días quedan sin precedente (nuevos).
- Motivo: pedido explícito del cliente (Joaquín) de armar presupuesto para Yaghan Rental vía `/agentes-ia-orquestador`, con instrucción de examinar la web y escanear el historial antes de proponer.
- Impacto en capas: N/A (etapa de relevamiento).
- Riesgos/supuestos: la web no publica política de depósito/seña ni proceso formal de reserva — queda como pregunta abierta para el cliente final (Yaghan), no resoluble solo con lo publicado.

### 2026-08-12 09:05 - orquestador (dato adicional del usuario)
- Etapa: Discovery
- Cambio: Joaquín aporta que Yaghan también maneja **promociones de alquiler por cantidad de días** (ya visible parcialmente en la web como "alquiler x 3 días con descuento"), confirmando que el pricing no es un valor fijo por día sino escalonado.
- Motivo: precisión de alcance antes de cerrar el análisis funcional.
- Impacto en capas: Negocio (cálculo de tarifa) y Datos (tabla de tarifas por artículo/rango de días).
- Riesgos/supuestos: no se conoce aún si los escalones son fijos (1/3/7 días) o el descuento es dinámico por día adicional — queda como pregunta abierta en `1-analista-funcional.md`.

### 2026-08-12 09:30 - orquestador (gate de Análisis — cierre de las 9 hipótesis)
- Etapa: Análisis — cierre de gate
- Cambio: Joaquín respondió las 9 preguntas abiertas del Análisis. Resueltas: cotización manual (combos automáticos a Etapa 2), pago manual con comprobante (Mercado Pago a Etapa 2), QR enviado al cliente + búsqueda manual como alternativa, comisión configurable por referente (20% default), talleres con seguimiento completo (costo/fecha retorno/bloqueo de stock), un solo perfil Administrador, tarifas por rangos fijos configurables, aviso de atraso único. El punto del número de WhatsApp se resolvió con una aclaración técnica: por defecto un número opera en la app de teléfono o en la Business Platform/Cloud API, no ambas — se decide usar el número existente (+5492901652524) apostando a la función de "coexistencia" de Meta, con verificación de elegibilidad pendiente al inicio de Implementación (riesgo R1 actualizado).
- Motivo: cerrar el gate "no iniciar Diseño sin Análisis aprobado" de `CLAUDE.md`.
- Impacto en capas: Negocio (reglas confirmadas) y Datos (confirma entidades Referente, OrdenTaller, TarifaPorDias).
- Riesgos/supuestos: R1 (WhatsApp) queda como riesgo operativo a verificar en Meta Business Manager antes de migrar en producción — no bloquea Diseño/Arquitectura/Presupuesto, pero debe comunicarse al cliente antes de la Implementación.

### 2026-08-12 10:00 - orquestador (Diseño funcional cerrado)
- Etapa: Diseño
- Cambio: cerrado `2-disenador-funcional.md` — 12 pantallas, ViewModels, 3 máquinas de estados (Reserva, Artículo, OrdenTaller), 16 historias de usuario. Reutilización confirmada de La Platense (caja diaria) y Ganadería (checklist/job diario). Compras y Talleres quedan marcados como candidatos a Etapa 2 en el plan funcional, a confirmar en Arquitectura/Presupuesto.
- Motivo: siguiente paso obligatorio tras el cierre del Análisis.
- Impacto en capas: Presentación (flujos/ViewModels), Negocio (máquinas de estados y reglas), Datos (14 entidades identificadas).
- Riesgos/supuestos: lectura de QR por navegador requiere HTTPS y permisos de cámara — a validar en dispositivo real durante Implementación/QA.

### 2026-08-12 10:15 - orquestador (Arquitectura técnica cerrada)
- Etapa: Arquitectura
- Cambio: cerrado `3-arquitecto-mvc.md` — 17 entidades de dominio, arquitectura de 4 capas sobre `blankproject`, reutilización explícita de `WhatsAppClient`/webhook (`crm-olvidata`) y `CajaMovimiento`/`CierreCajaDiario` (`la-platense`). Rol único Administrador. Migración EF requerida (proyecto nuevo). Quedaron 2 preguntas de gate para Joaquín antes de presupuestar.
- Motivo: siguiente paso obligatorio tras el cierre del Diseño.
- Impacto en capas: Domain/Application/Infrastructure/Web (detalle completo en el archivo).
- Riesgos/supuestos: R5 (ventana de carrera en validación de no-solapamiento de fechas, a nivel Service no DB constraint) y R6 (máquina de estados no configurable desde UI) agregados como riesgos nuevos de arquitectura.

### 2026-08-12 10:20 - orquestador (gate de Arquitectura — respuesta de Joaquín)
- Etapa: Arquitectura — cierre de gate
- Cambio: Joaquín confirmó (1) Compras a proveedores y Talleres van en Etapa 1 junto con el resto del alcance pedido (no se separan a Etapa 2), y (2) el repo se arranca copiando y saneando un proyecto reciente (criterio ya usado con La Platense) — en este caso `la-platense` (ya trae caja diaria integrada), portando además el módulo de WhatsApp desde `crm-olvidata` (que La Platense no conservó, fue removido en su propio saneamiento).
- Motivo: cerrar el gate "no iniciar Presupuesto sin Arquitectura aprobada".
- Impacto en capas: N/A (decisión de alcance y de estrategia de bootstrap, ya reflejada en el WBS del Presupuesto).
- Riesgos/supuestos: ninguno nuevo.

### 2026-08-12 10:45 - orquestador (Presupuesto cerrado — pendiente aprobación del cliente)
- Etapa: Presupuesto
- Cambio: cerrado `4-presupuestador.md` y `presupuesto-cliente.md`. 16 módulos (14 Etapa 1 + 2 Etapa 2), 73h M base. Ratio de reutilización R = 26.7% → Tier 3 (sin descuento de expansión agresiva) — declarado explícitamente como resultado honesto, no forzado a un tier más agresivo, porque el núcleo del dominio (alquiler con QR, comisión por referido, talleres) no tiene precedente en el estudio pese a la reutilización real de WhatsApp/caja diaria/checklist/bootstrap. Precio final: **USD 1.534** (Etapa 1 USD 1.042 + Etapa 2 USD 185 + Tokens IA USD 307). Mantenimiento anual: Plan PREMIUM USD 500/año (17 tablas nuevas).
- Motivo: cierre del flujo Discovery→Presupuesto pedido por Joaquín vía `/agentes-ia-orquestador`, listo para revisión y envío al cliente (Yaghan Rental aún no confirmó nada — es la primera propuesta).
- Impacto en capas: N/A (documento comercial).
- Riesgos/supuestos: sin descuento por referido aplicado (prospecto nuevo, sin acuerdo previo); si Joaquín necesita palanca de cierre ante objeción de precio, la política vigente es regalar el primer año de mantenimiento caso por caso, no bajar el precio del Build.

### 2026-08-12 11:15 - orquestador (garantía con tarjeta — agregado post-presupuesto)
- Etapa: Análisis → Diseño → Arquitectura → Presupuesto (las 4 memorias actualizadas en la misma sesión, sin reabrir gates ya cerrados con el cliente porque el presupuesto aún no fue enviado)
- Cambio: Joaquín pidió agregar un bloqueo de garantía con tarjeta de crédito (cubrir robo/rotura), con research especial previo por ser una rama sin cobertura en el estudio. Research confirmó **Mercado Pago Advanced Payments** (`capture:false`) como vía técnica viable — mismo mecanismo que usan las rentadoras de auto en Argentina. Restricciones documentadas: hold vence a los 7 días, solo tarjetas Visa/Master/Cabal/Amex, tokenización obligatoria vía SDK de Mercado Pago (evita alcance PCI-DSS pleno). 4 decisiones de diseño confirmadas con Joaquín: hold al retirar (no al reservar), re-autorización para alquileres >7 días, monto fijo por reserva, depósito alternativo si no hay tarjeta compatible. Agregada entidad `GarantiaTarjeta` + 2 módulos de WBS (17. integración MP, 18. depósito alternativo) = +12h M. Confirmado en Etapa 1 (pedido explícito del cliente).
- Motivo: pedido del cliente, con instrucción explícita de research previo dado que es la rama menos cubierta hasta ahora.
- Impacto en capas: Domain (`GarantiaTarjeta`, enum `EstadoGarantia`), Application (`IMercadoPagoGarantiaClient`, `IGarantiaService`), Infrastructure (`MercadoPagoGarantiaClient`, extensión de `ChecklistDiarioHostedService`), Web (pantalla `Reserva/Retirar` con SDK tokenizado embebido).
- Riesgos/supuestos: R7 (vencimiento 7 días, mitigado con re-autorización manual), R8 (tarjetas no compatibles, mitigado con depósito alternativo), R9 (dependencia del SDK de Mercado Pago cargando correctamente — debe degradar a depósito alternativo, no bloquear el retiro). Precio de lista calculado en este paso: USD 1.785 (antes USD 1.533) — **reemplazado en el siguiente ajuste, ver abajo**. Mantenimiento anual de lista sin cambios en este paso (PREMIUM USD 500/año).

### 2026-08-12 11:45 - orquestador (override comercial — CRM aparte + precio fijo + mantenimiento con año 1 gratis)
- Etapa: Presupuesto — segundo ajuste sobre el ya cerrado
- Cambio: Joaquín instruyó reestructurar la propuesta: (1) sacar el CRM de WhatsApp (bandeja + avisos automáticos, módulos 2+8 del WBS) del build comprometido — pasa a módulo opcional futuro, cotizado aparte (USD 176 de lista) y pagadero cuando el cliente lo decida; (2) fijar el precio final de desarrollo del núcleo (resto del sistema, incluida la garantía con tarjeta) en **USD 850**, por debajo del calculado por fórmula (USD 1.359 de lista para el núcleo); (3) mantenimiento anual en **USD 600/año, con el primer año sin cargo** (por encima del PREMIUM de lista de USD 500). Actualizados los 4 documentos técnicos (`1-analista-funcional.md` §0.9, `2-disenador-funcional.md` plan por etapas, `3-arquitecto-mvc.md` §6b, `4-presupuestador.md` WBS + sección de override) y `presupuesto-cliente.md` reescrito con la nueva estructura.
- Motivo: decisión comercial de Joaquín — dueño de la política de precios del estudio, no requiere justificación adicional más allá de quedar documentada para calibración futura.
- Impacto en capas: Web/Application/Infrastructure del módulo CRM (WhatsAppClient, webhook, ConversacionWhatsApp/MensajeWhatsApp, disparo de avisos) quedan fuera de esta implementación — se retoman cuando el cliente pague el módulo aparte. El bootstrap deja de portar WhatsApp desde `crm-olvidata` en este build.
- Riesgos/supuestos: tasa efectiva del núcleo baja a ≈USD 28/h, por debajo del piso de referencia USD 30/h del estudio — registrado como excepción explícita autorizada por Joaquín, no como desvío a corregir.

### 2026-08-12 12:00 - orquestador (corrección: el CRM sí se implementa en Etapa 1, solo se difiere el cobro)
- Etapa: Presupuesto — corrección inmediata sobre el ajuste anterior
- Cambio: Joaquín aclaró que la entrada anterior interpretó mal su pedido — el CRM de WhatsApp **se construye e implementa en Etapa 1** junto con el resto del sistema, sin ningún recorte técnico ni funcional. Lo único que se difiere es el **cobro** de ese módulo (USD 176), separado del pago inicial del núcleo (USD 850), a pagar cuando el cliente lo defina. Revertidas las notas de "módulo futuro"/"sale del build" en `1-analista-funcional.md` §0.9, `2-disenador-funcional.md` (plan por etapas) y `3-arquitecto-mvc.md` §6b — las tres vuelven a describir el CRM como parte plena de la implementación (WhatsAppClient, webhook, entidades, bootstrap con port de WhatsApp, botón "Enviar por WhatsApp" en Cotización, avisos automáticos activos desde la entrega). `4-presupuestador.md` restaurado a 74h M en Etapa 1 (85h con Etapa 2), con el desglose de facturación (pago inicial vs. diferido) documentado aparte del WBS técnico. `presupuesto-cliente.md` reescrito: el sistema se describe completo y funcionando desde la entrega, con una sección de inversión que muestra "Desarrollo — pago inicial USD 850" y "CRM de WhatsApp — incluido en esta entrega, pago diferido USD 176" como dos líneas separadas por forma de cobro, no por alcance.
- Motivo: corregir la interpretación antes de que el documento le llegue al cliente con una descripción de alcance incorrecta (hubiera dicho que el CRM no está incluido, cuando sí lo está).
- Impacto en capas: ninguno nuevo — el build vuelve a ser idéntico al de antes del ajuste anterior; solo cambia la documentación de facturación.
- Riesgos/supuestos: riesgo de negocio explícito — el estudio entrega el CRM funcionando sin fecha de cobro asegurada, extensión de crédito comercial a un prospecto todavía no confirmado. Registrado como excepción puntual de Joaquín, no como precedente para otros proyectos.

### 2026-08-13 09:00 - orquestador (cierre final del precio — un solo pago)
- Etapa: Presupuesto — cierre definitivo
- Cambio: Joaquín simplificó la estructura de facturación una vez más: en vez de "pago inicial USD 850 (núcleo) + CRM USD 176 diferido", queda un **único precio final de USD 850 que cubre todo el desarrollo** (núcleo + garantía con tarjeta + CRM de WhatsApp), pagadero 50/50 igual que cualquier otro proyecto del estudio — sin cobro diferido. Mantenimiento sin cambios: USD 600/año, primer año sin cargo. Etapa 2 (combos automáticos + Mercado Pago cobro online) sigue opcional aparte, USD 185, no tocada por este ajuste. Ante la ambigüedad de si "850 final" incluía o no el CRM, se confirmó explícitamente con Joaquín antes de tocar el documento (AskUserQuestion) — evitó repetir el error de interpretación del ajuste anterior.
- Motivo: decisión comercial de Joaquín, simplificación de la propuesta antes de enviarla al cliente.
- Impacto en capas: ninguno técnico — el build implementado sigue siendo el mismo (74h M, CRM incluido). Solo cambia la presentación comercial: una sola línea de inversión en `presupuesto-cliente.md`, un solo pago 50/50.
- Riesgos/supuestos: el riesgo de crédito comercial (entregar el CRM sin cobro asegurado) registrado en la entrada anterior queda sin efecto — ya no hay cobro diferido. Tasa efectiva final ≈USD 23,9/h, la excepción de precio más agresiva del dataset del estudio a la fecha — registrada explícitamente en `4-presupuestador.md` como decisión puntual de Joaquín, no recalibración de la política general.
