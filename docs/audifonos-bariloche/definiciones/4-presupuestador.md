# Memoria - Presupuestador

## Proyecto: audifonos-bariloche
## Ultima actualizacion: 2026-08-19

## Definiciones vigentes

### WBS funcional vigente (Etapa 1 = MVP, Etapa 2 = complementario)

| # | Item | Etapa | Clasificacion |
|---|---|---|---|
| 1 | Usuarios y roles (Recepcion / Profesional) | 1 | Modulo nuevo — ABM simple |
| 2 | Pacientes (ABM: nombre, DNI, edad, telefono, obra social) | 1 | Modulo nuevo — ABM intermedio |
| 3 | Turnos / agenda por profesional (workflow de estados + vista calendario) | 1 | Modulo nuevo — workflow/estados (ajustado al alza por UI de calendario) |
| 4 | Historia clinica (padre/hijo Paciente→Consultas) | 1 | Modulo nuevo — ABM complejo |
| 5 | Adjuntos de documentos en historia clinica | 1 | **Reutilizacion** — AdjuntoService ya construido en el estudio (vinosefue y otros) |
| 6 | Panel de turnos del dia | 1 | Modulo nuevo — UI simple |
| 7 | Puesta en marcha (deploy hosting compartido, dominio) | 1 | Deploy inicial (regla de subestimacion sistematica — M minimo 2h) |
| 8 | Recordatorios de turno por WhatsApp | 2 | **Reutilizacion parcial** — patron WhatsAppClient/webhook ya construido en crm-olvidata, pero requiere alta de cuenta WhatsApp Business propia del cliente |
| 9 | Reportes basicos (turnos por profesional, ausentismo) | 2 | Modulo nuevo — reporte/exportacion simple |

### Estimaciones PERT por item

| # | Item | O | M | P | PERT=(O+4M+P)/6 | M usado para costo (regla: M crudo, no PERT) |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles | 1 | 2 | 3 | 2.00 | 2 |
| 2 | Pacientes | 3 | 5 | 8 | 5.17 | 5 |
| 3 | Turnos/agenda | 5 | 8 | 12 | 8.17 | 8 |
| 4 | Historia clinica | 6 | 9 | 14 | 9.33 | 9 |
| 5 | Adjuntos (reuso) | 0.5 | 1 | 2 | 1.08 | 1 |
| 6 | Panel del dia | 1 | 2 | 3 | 2.00 | 2 |
| 7 | Deploy inicial | 1.5 | 2 | 3 | 2.08 | 2 |
| **Subtotal Etapa 1** | | | | | **29.83 h PERT** | **29 h** |
| 8 | Recordatorios WhatsApp (reuso parcial) | 3 | 4 | 6 | 4.17 | 4 |
| 9 | Reportes basicos | 1 | 2 | 3 | 2.00 | 2 |
| **Subtotal Etapa 2** | | | | | **6.17 h PERT** | **6 h** |
| **Total proyecto** | | | | | **36.0 h PERT** | **35 h (M)** |

### Autocorreccion contra historicos (obligatoria antes del cierre)
Referencia comparable elegida: **Ganaderia** (proyecto de referencia comercial fijado en `27-presupuesto-parametros.instructions.md` para alcances de 8-11 modulos, mezcla ABM+workflow+financiero, 2 migraciones EF). Ganaderia: 81.5 h base (M) / 101.0 h con contingencia, 8 modulos, CIERRE REAL 20 h.

Ratio = M total estimado (35h) / M base historico de Ganaderia (81.5h) = **0.43** — por debajo del umbral 0.85, dispara la regla "revisar omisiones o justificar simplificacion real".

**Justificacion de la simplificacion (no es omision):** Ganaderia incluye modulos financieros pesados (facturacion con cuotas, caja, egresos, rechazos/regularizacion con job diario) que no existen en este alcance — audifonos-bariloche no tiene facturacion, cuotas ni caja, es un sistema de ABM + calendario + documentos sin logica financiera. La complejidad real es menor pese a un numero de items similar (9 vs 8). Ademas 2 de los 9 items (Adjuntos, Recordatorios WhatsApp) estan clasificados como reutilizacion de patrones ya construidos en el estudio, bajando el M respecto a si fueran modulos nuevos desde cero. Se mantiene la estimacion sin ajustar al alza — el ratio bajo esta justificado por alcance funcional real, no por omision de items.

### Ratio de reutilizacion (R) — descuento de expansion agresiva
`R = M reutilizacion / M total = (1 + 4) / 35 = 5/35 = 14.3%`

**Tier 3 — Estandar (R < 40%)** → 0% de descuento de expansion agresiva sobre el subtotal. Precio de lista sin cambios (no hay proyecto de dominio comparable en el historial para aplicar Tier 1/2 — el reuso es solo de patrones tecnicos puntuales, ya reflejado en el M chico de esos 2 items, no en un descuento estructural adicional).

### Tasa vigente y contingencia aplicada
- Tasa vigente: USD 35/h.
- Formula: Costo = M x $16.80 (= M/2.5 x 1.20 x $35). La contingencia 20% ya esta incluida en la formula (no se aplica una segunda vez).
- Riesgo del proyecto: **medio** (multiples modulos acoplados — turno↔paciente↔historia clinica↔adjunto — sin integraciones externas obligatorias en Etapa 1). Ya reflejado en la formula vigente, no se suma contingencia adicional aparte.

### Calculo de costo por item (Costo = M x $16.80)

| # | Item | M | USD (lista) |
|---|---|---:|---:|
| 1 | Usuarios y roles | 2 | 33.60 |
| 2 | Pacientes | 5 | 84.00 |
| 3 | Turnos/agenda | 8 | 134.40 |
| 4 | Historia clinica | 9 | 151.20 |
| 5 | Adjuntos (reuso) | 1 | 16.80 |
| 6 | Panel del dia | 2 | 33.60 |
| 7 | Deploy inicial | 2 | 33.60 |
| **Subtotal Etapa 1** | | **29** | **487.20** |
| 8 | Recordatorios WhatsApp | 4 | 67.20 |
| 9 | Reportes basicos | 2 | 33.60 |
| **Subtotal Etapa 2** | | **6** | **100.80** |

Agrupado por area funcional para el documento cliente (redondeado):
- Gestion de pacientes y turnos (items 2+3): USD 218
- Historia clinica digital con documentos adjuntos (items 4+5): USD 168
- Usuarios y accesos por rol (item 1): USD 34
- Panel de turnos del dia (item 6): USD 34
- Puesta en marcha (item 7): USD 34
- **Subtotal Etapa 1: USD 488**
- Recordatorios de turno por WhatsApp (item 8): USD 67
- Reportes basicos (item 9): USD 34
- **Subtotal Etapa 2: USD 101**

### Resumen economico (con Tokens IA como item individual)
- Subtotal Etapa 1: USD 488
- Subtotal Etapa 2: USD 101
- Subtotal desarrollo (Etapa 1 + Etapa 2, sin Tokens IA): USD 589
- **Descuento de expansion agresiva: USD 177 (30%, Tier 1) — override explicito de Joaquin, ver nota abajo.**
- Tokens IA (25% del subtotal desarrollo, SIEMPRE sobre subtotal sin descontar, nunca sobre el neto post-descuento): USD 147
- **Total cliente: USD 559** (589 - 177 + 147)
- Piso absoluto USD 280 — no aplica (ya por encima).

**Nota sobre el override de tier (2026-08-19):** el calculo objetivo de R (14.3%, ver seccion "Ratio de reutilizacion" arriba) da Tier 3 (0% descuento) segun la regla de `27-presupuesto-parametros.instructions.md`. Joaquin pidio explicitamente aplicar el descuento por expansion agresiva — interpretado como Tier 1 (30%, el tier "insignia" de la politica, nombrado tal cual en su pedido) dado que es un Build inicial para cliente nuevo (elegible por regla) y el checkpoint del tablero de ciclos economicos (octubre 2027) todavia no llego. Es una decision de negocio explicita que pisa el calculo por R — no se recalculo R para justificarlo artificialmente. Documentado para trazabilidad, no para cuestionar la decision.

### Plan de mantenimiento — nota de zona gris (no hay regla exacta en 27-presupuesto-parametros para este caso)
Tablas de negocio estimadas: 5 (Paciente, Turno, HistoriaClinicaEntry, Adjunto, + roles/Identity no cuentan como tabla de negocio) → cae en rango **PRO (6-15 tablas)** por el limite inferior, aunque tecnicamente son 5 (podria leerse como STARTER 1-5 tambien — ambiguo en el borde). El problema real es el **limite de usuarios incluidos**: el cliente declaro ~6 usuarios, pero:
- STARTER: 1 admin.
- PRO: hasta 2 usuarios.
- PREMIUM: hasta 3 usuarios.
- SCALE: usuarios ilimitados (pensado para 31+ tablas, sistema mucho mas grande que este).

Ningun plan calza exacto (sistema chico en tablas, pero con mas usuarios que los planes chicos incluyen). Dos caminos calculados:
- **PREMIUM (USD 500/año) + 3 usuarios adicionales** (6 necesarios − 3 incluidos) × USD 100/año = USD 300 → **Total USD 800/año**.
- **SCALE (USD 850/año)** — usuarios ilimitados, 3 rondas de ajuste en vez de 2, sin administrar upsells cada vez que sumen una fonoaudiologa nueva. Solo USD 50/año mas que la opcion anterior.

**Decision recomendada (a confirmar con Joaquin, no incluida como ambiguedad en el documento cliente):** ofrecer PREMIUM + 3 usuarios adicionales (USD 800/año) como el numero calculado segun tabla vigente — mencionar SCALE como alternativa de mejor valor si el centro espera crecer en cantidad de profesionales. Esto es una interpretacion mia sobre un caso no cubierto explicitamente por la politica de planes (tablas vs. usuarios) — dejarlo flexible en la conversacion comercial, no rigido en el documento.

### Calibraciones historicas usadas
- Ganaderia (referencia comercial, 8 modulos, 81.5h base / 101h PERT, cierre real 20h) — usada para autocorreccion, ratio 0.43 justificado por ausencia de modulos financieros.
- Regla de "Modificacion sobre modulo existente" aplicada a items 5 (Adjuntos) y 8 (Recordatorios WhatsApp) por reutilizacion de patron tecnico ya construido en el estudio (AdjuntoService, WhatsAppClient).
- Regla de subestimacion sistematica en deploy inicial aplicada a item 7 (M minimo 2h, no el rango de "ajuste puntual").

### Costo interno de IA (dato exclusivamente interno, no aparece en presupuesto-cliente.md)
- Horas facturables totales (Etapa1+Etapa2) = 35/2.5 x 1.20 = 16.8 h.
- Costo_IA_modulos = 16.8h x USD 4/h (tarifa Opus placeholder) = USD 67.2.
- Costo_IA_overhead_proyecto = 4h x USD 1/h (tarifa Sonnet placeholder) = USD 4.
- Costo_IA total proyectado ≈ USD 71.2 — muy por debajo del cargo Tokens IA visible al cliente (USD 147), sin necesidad de ajuste de precio por modulo (ningun item supera el umbral 15% del precio de lista de ese item en costo IA proyectado).

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta, sin aprobacion del lead todavia.

## Historial de ajustes
- 2026-08-19: primera version. Total propuesto USD 736 (desarrollo) + mantenimiento PREMIUM+3 usuarios USD 800/año (o SCALE USD 850/año, alternativa de mejor valor). Discovery minimo (3 respuestas de cuestionario automatico) — presupuesto sujeto a reestimacion si el alcance cambia al confirmar con el lead.
- 2026-08-19: aplicado descuento por expansion agresiva Tier 1 (30%) a pedido explicito de Joaquin, pisando el calculo objetivo de R=14.3%/Tier 3. Total desarrollo baja de USD 736 a **USD 559**. Mantenimiento sin cambios (la politica explicitamente excluye mantenimiento del descuento).
- 2026-08-19: restructurado `presupuesto-cliente.md` a pedido explicito de Joaquin ("presupuesto de desarrollo por modulo y funcionalidad que quieran incluir en el sistema") — sin cambio de alcance, PERT ni precio total. Las tablas de Etapa 1 y Etapa 2 pasan de 5+2 bundles agrupados por area funcional a los 9 items individuales ya calculados en la tabla "Calculo de costo por item" de arriba (34/84/134/151/17/34/34 en Etapa 1, 67/34 en Etapa 2 — mismos subtotales USD 488 y USD 101). Se agrego nota de dependencia funcional (Usuarios→Turnos/Pacientes→Historia clinica→Adjuntos) para que el cliente entienda que esos 5 modulos no son elegibles por separado dentro del MVP, mientras que los 2 items de Etapa 2 si son independientes y opcionales. Total del proyecto sin cambios (USD 559).
