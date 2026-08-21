# Memoria - Presupuestador

## Proyecto: cma-centro-medico
## Ultima actualizacion: 2026-08-21

## Definiciones vigentes

### [DECISION 2026-08-21, Joaquin] Alcance acotado a UNA sola sede (La Plata)
Version anterior de este documento presupuestaba las 4 sedes (Subtotal_lista USD 840, total USD 1008). Reestimado completo con el alcance acotado — se elimina el item de catalogo de Sedes y la dimension multi-sede de Pacientes/Turnos/Historia clinica/Panel del dia/Reportes. El resto del nucleo funcional (Pacientes, Turnos, Historia clinica, Adjuntos, Portal de autogestion del paciente, Especialidades/Profesionales) se mantiene.

### WBS funcional vigente (Etapa 1 = MVP, Etapa 2 = complementario)

| # | Item | Etapa | Clasificacion |
|---|---|---|---|
| 1 | Usuarios y roles (Administracion / Profesional / Paciente) | 1 | Modulo nuevo — ABM simple (3 roles en vez de 2, sin precedente exacto) |
| 2 | Especialidades + Profesionales (catalogo) | 1 | Modulo nuevo — ABM simple |
| 3 | Pacientes (ABM: nombre, DNI, edad, telefono, obra social) | 1 | Modulo nuevo — ABM intermedio (identico a audifonos-bariloche item 2) |
| 4 | Turnos / agenda por profesional (workflow de estados) | 1 | Modulo nuevo — workflow/estados (identico a audifonos-bariloche item 3) |
| 5 | Historia clinica (padre/hijo Paciente→Consultas) | 1 | Modulo nuevo — ABM complejo (identico a audifonos-bariloche item 4) |
| 6 | Adjuntos de documentos en historia clinica | 1 | **Reutilizacion** — AdjuntoService ya construido en el estudio (PAT-002) |
| 7 | Portal de autogestion del paciente (login propio, ver turnos + historia solo lectura) | 1 | Modulo nuevo — sin precedente en el estudio (audifonos-bariloche lo excluyo explicitamente), reutiliza entidades de items 3-5 (solo agrega capa de lectura scoped + rol Identity nuevo) |
| 8 | Panel de turnos del dia | 1 | Modulo nuevo — UI simple (identico a audifonos-bariloche item 6) |
| 9 | Puesta en marcha (deploy hosting compartido, dominio) | 1 | Deploy inicial (regla de subestimacion sistematica — M minimo 2h) |
| 10 | Reportes basicos (turnos por profesional, ausentismo) | 2 | Modulo nuevo — reporte/exportacion simple (identico a audifonos-bariloche item 9) |

**Excluido del alcance (no cotizado):** las otras 3 sedes de CMA (Claypole, Malvinas Argentinas, R. Calzada) — expansion futura, proyecto aparte. Integracion con Bot Silvio (WhatsApp) o AgendaPro — ya resueltos externamente por el cliente.

### Estimaciones PERT por item

| # | Item | O | M | P | PERT=(O+4M+P)/6 | M usado para costo (regla: M crudo, no PERT) |
|---|---|---:|---:|---:|---:|---:|
| 1 | Usuarios y roles (3 roles) | 2 | 3 | 5 | 3.17 | 3 |
| 2 | Especialidades + Profesionales | 2 | 3 | 4 | 3.00 | 3 |
| 3 | Pacientes | 3 | 5 | 8 | 5.17 | 5 |
| 4 | Turnos/agenda | 5 | 8 | 12 | 8.17 | 8 |
| 5 | Historia clinica | 6 | 9 | 14 | 9.33 | 9 |
| 6 | Adjuntos (reuso) | 0.5 | 1 | 2 | 1.08 | 1 |
| 7 | Portal de autogestion del paciente | 5 | 7 | 11 | 7.33 | 7 |
| 8 | Panel del dia | 1 | 2 | 3 | 2.00 | 2 |
| 9 | Deploy inicial | 1.5 | 2 | 3 | 2.08 | 2 |
| **Subtotal Etapa 1** | | | | | **41.3 h PERT** | **40 h** |
| 10 | Reportes basicos | 1 | 2 | 3 | 2.00 | 2 |
| **Subtotal Etapa 2** | | | | | **2.0 h PERT** | **2 h** |
| **Total proyecto** | | | | | **43.3 h PERT** | **42 h (M)** |

### Autocorreccion contra historicos (obligatoria antes del cierre)
Referencia comparable elegida: **audifonos-bariloche** (mismo nucleo funcional exacto: pacientes + turnos + historia clinica + adjuntos, una sola ubicacion), M total 35h para 9 items.

Ratio = M total estimado (42h) / M de audifonos-bariloche (35h) = **1.20x** — diferencial minimo y explicado: items 1-6+8-9 son practicamente identicos a audifonos-bariloche (mismo M cada uno, salvo Usuarios que sube de 2h a 3h por el tercer rol), mas el item 7 nuevo (Portal de autogestion, 7h) que no existe en el comparable. Sin la dimension multi-sede, este proyecto queda casi calcado del comparable — el ratio 1.20x es coherente y no dispara ninguna alerta de sobreestimacion.

**Advertencia declarada:** ninguno de los dos comparables (audifonos-bariloche y este) tiene CIERRE REAL todavia — ambos son estimaciones de propuesta sin implementar.

### Ratio de reutilizacion (R) — descuento de expansion agresiva
`R = M reutilizacion / M total = 1 / 42 = 2.4%`

Solo el item 6 (Adjuntos, PAT-002) cuenta como reutilizacion en sentido estricto (codigo YA ENTREGADO en otro proyecto). Los items 3/4/5 (Pacientes/Turnos/Historia clinica) son identicos al diseno de audifonos-bariloche, pero ese proyecto no tiene implementacion real todavia — no cuenta para R.

**Tier 3 — Estandar (R < 40%)** → 0% de descuento de expansion agresiva por reutilizacion.

### Descuento por volumen del proyecto
`Subtotal_lista = 42 x $16.80 = USD 705.60`

USD 705.60 cae en **Tier V1 — Volumen (USD 600-1.200) → 5% de descuento**.

`factor_tier = MAX(factor_tier_reutilizacion, factor_tier_volumen) = MAX(0%, 5%) = 5%`

### Tasa vigente y contingencia aplicada
- Tasa vigente: USD 35/h.
- Formula: Costo = M x $16.80 (= M/2.5 x 1.20 x $35). La contingencia 20% ya esta incluida en la formula.
- Riesgo del proyecto: **medio** — mismo perfil que audifonos-bariloche (modulos acoplados: paciente↔turno↔historia clinica↔adjunto), mas la superficie de seguridad nueva del portal de autogestion (IDOR). Reflejado en el M del item 7, no se suma contingencia adicional aparte.

### Calculo de costo por item (Costo = M x $16.80)

| # | Item | M | USD (lista) |
|---|---|---:|---:|
| 1 | Usuarios y roles | 3 | 50.40 |
| 2 | Especialidades + Profesionales | 3 | 50.40 |
| 3 | Pacientes | 5 | 84.00 |
| 4 | Turnos/agenda | 8 | 134.40 |
| 5 | Historia clinica | 9 | 151.20 |
| 6 | Adjuntos (reuso) | 1 | 16.80 |
| 7 | Portal de autogestion del paciente | 7 | 117.60 |
| 8 | Panel del dia | 2 | 33.60 |
| 9 | Deploy inicial | 2 | 33.60 |
| **Subtotal Etapa 1** | | **40** | **672.00** |
| 10 | Reportes basicos | 2 | 33.60 |
| **Subtotal Etapa 2** | | **2** | **33.60** |
| **Subtotal_lista (proyecto)** | | **42** | **705.60** |

### Precios distribuidos al cliente (factor x1.25, Tokens IA plegado — regla vigente desde 2026-08-20)

| # | Item | USD lista | USD distribuido (x1.25) |
|---|---|---:|---:|
| 1 | Usuarios y roles | 50.40 | 63.00 |
| 2 | Especialidades + Profesionales | 50.40 | 63.00 |
| 3 | Pacientes | 84.00 | 105.00 |
| 4 | Turnos/agenda | 134.40 | 168.00 |
| 5 | Historia clinica | 151.20 | 189.00 |
| 6 | Adjuntos | 16.80 | 21.00 |
| 7 | Portal de autogestion del paciente | 117.60 | 147.00 |
| 8 | Panel del dia | 33.60 | 42.00 |
| 9 | Deploy inicial | 33.60 | 42.00 |
| **Subtotal Etapa 1 distribuido** | | **672.00** | **840.00** |
| 10 | Reportes basicos | 33.60 | 42.00 |
| **Subtotal Etapa 2 distribuido** | | **33.60** | **42.00** |
| **Subtotal distribuido (proyecto)** | | **705.60** | **882.00** |

### Resumen economico
- Subtotal_lista (Etapa 1 + Etapa 2): USD 705.60
- Tokens IA (25% de Subtotal_lista, SIEMPRE sobre lista sin descontar): USD 176.40
- Subtotal distribuido a mostrar (Subtotal_lista x 1.25, ya incluye Tokens IA plegado por modulo): USD 882.00
- Descuento por eficiencia de desarrollo (Tier V1 volumen, 5% sobre Subtotal_lista SIN tokens): -USD 35.28 → **redondeado a -USD 35 para el documento cliente**
- **Total cliente: USD 847** (882.00 - 35.28 = 846.72, redondeado a 847 para presentacion; ver nota de redondeo abajo)

**Verificacion de formula (sin redondeo):** `Precio_final_Build = (Subtotal_lista - Descuento_expansion) + Tokens_IA = (705.60 - 35.28) + 176.40 = 846.72`.

**Nota de redondeo:** a diferencia del caso multi-sede (donde 840x0.05=42.00 daba un numero exacto), aca el 5% de 705.60 da 35.28 — no es un numero redondo. Se redondea a USD 35 para el documento cliente (mismo criterio que audifonos-bariloche redondeo 176.7→177). Total mostrado: USD 847 (882-35). El numero exacto interno es USD 846.72 — diferencia de USD 0.28, irrelevante.

Piso absoluto USD 280 — no aplica (muy por encima).

### Plan de mantenimiento anual
Tablas de negocio estimadas: 6 (Especialidad, Profesional, ProfesionalEspecialidad, Paciente, Turno, HistoriaClinicaEntry, Adjunto — 7 si se cuenta la tabla de union aparte; se estima como 6 "tablas de negocio" igual criterio que antes) → cae en **PRO (6-15 tablas), USD 400/año, hasta 2 usuarios**.

Usuarios declarados por el lead: "5" — dato levantado ANTES de acotar a una sola sede, podria estar sobreestimado (ver supuesto en `1-analista-funcional.md`). Se mantiene como numero de trabajo por ser el unico dato disponible.

- **PRO (USD 400/año) + 3 usuarios adicionales** × USD 125/año = USD 375 → **Total USD 775/año**, sin cambios respecto de la version multi-sede (el numero de usuarios declarado no dependia de la cantidad de sedes en el dato original).
- Alternativa SCALE (USD 850/año, usuarios ilimitados) pierde parte de su justificacion original (la razon para sugerirla era el crecimiento entre sedes) — con el alcance acotado a 1 sede, **PRO+3 usuarios (USD 775/año) es la recomendacion clara**, sin necesidad de ofrecer alternativa salvo que el lead confirme que va a crecer en profesionales.

### Costo interno de IA (dato exclusivamente interno, no aparece en presupuesto-cliente.md)
- Horas facturables totales (Etapa1+Etapa2) = 42/2.5 x 1.20 = 20.16 h.
- Costo_IA_modulos = 20.16h x USD 4/h (tarifa Opus placeholder) = USD 80.64.
- Costo_IA_overhead_proyecto = 4h x USD 1/h (tarifa Sonnet placeholder) = USD 4.00.
- Costo_IA total proyectado ≈ USD 84.64 — muy por debajo del cargo Tokens IA visible al cliente (USD 176.40).
- Verificacion por item (umbral 15%): item mas caro (Historia clinica, M=9): horas fact.=9/2.5x1.2=4.32h → Costo_IA=USD 17.28 sobre lista USD 151.20 → 11.4%, por debajo del umbral. Ningun item supera el 15% — sin ajuste de precio por modulo necesario.

### Calibraciones historicas usadas
- audifonos-bariloche (comparable de dominio identico, sin cierre real) — ratio 1.20x, el mas bajo/cercano a 1.0x del historial de comparables por diferir en un solo item real (Portal de autogestion).
- Regla de "Modificacion sobre modulo existente" aplicada solo al item 6 (Adjuntos) por reutilizacion de PAT-002.
- Regla de subestimacion sistematica en deploy inicial aplicada a item 9 (M minimo 2h).
- Descuento por volumen (V1, 5%) se mantiene aplicando pese a la reduccion de alcance — Subtotal_lista bajo de USD 840 a USD 705.60 pero sigue dentro del rango V1 (600-1.200).

### Cierre estimado vs real (si disponible)
No disponible — proyecto en etapa de propuesta, sin aprobacion del lead todavia.

## Historial de ajustes
- 2026-08-21: primera version (alcance multi-sede, 4 sedes). Total USD 1008 (desarrollo) + mantenimiento PRO+3 usuarios USD 775/año (o SCALE USD 850/año).
- 2026-08-21: **reestimado a pedido explicito de Joaquin, acotando el alcance a UNA sola sede (La Plata).** Eliminado el item de catalogo de Sedes y toda la dimension multi-sede de Pacientes/Turnos/Historia clinica/Panel del dia/Reportes — el WBS baja de 11 a 10 items, M total de 50h a 42h. Nuevo total: **USD 847** (desarrollo, bajo desde USD 1008) + mantenimiento **PRO+3 usuarios USD 775/año sin cambios** (recomendacion unica, ya no se ofrece SCALE como alternativa porque la razon de crecimiento entre sedes ya no aplica al alcance acotado). Sigue cayendo en Tier V1 de descuento por volumen (5%) pese a la reduccion de alcance.
