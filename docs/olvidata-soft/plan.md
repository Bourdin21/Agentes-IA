# Plan de la empresa — Olvidata Soft

Dueño: `olvidata-ceo`. Precios: `precios.md`. Clientes: `clientes.md`. Revisar cada trimestre contra cierres reales.

## Meta

Que el **recurrente neto** de Olvidata reemplace el sueldo del Ministerio de Joaquín (**USD 1.173/mes neto**) en **2028**. Desde ahí, independencia financiera real.

## Modelo por frente — revisión 2026-10-15 (vigente)

**Propuesta de `olvidata-ceo`, a confirmar por Joaquín.** Reemplaza al plan del 2026-07-29, que calculaba todo con el ticket de Build y no incluía AI Agents, Chatbots ni los precios nuevos de Landing.

### Punto de partida (fin de 2026, estimado)

| Frente | Clientes | Recurrente neto USD/mes | De dónde sale |
|---|---|---|---|
| Build | 17 | ~604 | 16 activos de `clientes.md` + La Platense, × USD 426/año (ticket de planificación) |
| Landing | 2 | ~58 | Diercas 400/año + MACERATA 300/año |
| AI Agents | 1 | ~150 | BMA a precio piloto (170/mes) menos el crédito de IA |
| Chatbots | 0 | 0 | El bot del CRM es interno |
| **Total** | **20** | **~812** | **Falta ~360/mes para la meta** |

### Supuestos por cliente nuevo (lista vigente, conservadores)

| Frente | Recurrente neto USD/mes | Ingreso de entrada (one-time) | Bajas por año |
|---|---|---|---|
| Build | 35,5 (426/año) | 1.500 | 10% |
| Landing | 32 (375–400/año) | 600 (1er año menos el recurrente) | 10% |
| AI Agents | 105 (Organización S + 1 agente personalizado = 130, menos ~25 de crédito de IA a costo) | 2.500 | 10% |
| Chatbots | 40 (Starter/Pro, neto de crédito) | 900 | 15% |

AI Agents y Chatbots suben × 1,20 desde 2027 (lista 2027). Clientes ya firmados mantienen su precio.

### Escenario base — cierres nuevos por año

| Año | Build | Landing | AI Agents | Chatbots |
|---|---|---|---|---|
| 2027 | 8 | 6 | 3 | 2 |
| 2028 | 8 | 8 | 5 | 4 |
| 2029 | 8 | 8 | 7 | 5 |
| 2030 | 8 | 8 | 9 | 6 |

El escenario **conservador** cierra la mitad de eso.

### Resultado

| Año | Base: clientes | Base: recurrente neto/mes | Base: bruto/año | Conservador: recurrente neto/mes | Conservador: bruto/año |
|---|---|---|---|---|---|
| 2026 | 20 | ~812 | — | ~812 | — |
| 2027 | 37 | ~1.680 | ~41.700 | ~1.270 | ~27.400 |
| 2028 | 58 | ~2.870 | ~63.400 | ~1.760 | ~34.700 |
| 2029 | 80 | ~4.230 | ~85.800 | ~2.450 | ~47.800 |
| 2030 | 103 | ~5.750 | ~110.100 | ~3.110 | ~57.000 |

Bruto = ingresos de entrada del año + recurrente promedio del año. Script del cálculo: `scripts/plan_olvidata.py`.

### Lo que dice el modelo

1. **La meta de 2028 se adelanta a 2027 en los dos escenarios**, porque el plan viejo solo contaba Build. Con cerrar la mitad de lo previsto, el recurrente pasa los USD 1.173/mes en 2027.
2. **AI Agents es la palanca.** Un cliente de AI Agents deja ~3 veces el recurrente de uno de Build (105 contra 35,5 por mes). Desde 2029 es el frente que más aporta en los dos escenarios.
3. **Build sigue siendo la base**, pero no alcanza solo: con 8 cierres por año llega a ~1.000/mes recién en 2028.
4. **Landing y Chatbots suman volumen, no la meta.** Sirven de entrada al combo y a AI Agents.
5. **El cuello de botella es la tasa de cierre**, no el volumen de prospectos (igual que en el plan anterior).

### Riesgos del modelo (verificar antes de decidir cuándo dejar el Ministerio)

- **El recurrente de Build es un supuesto** (426/año por cliente). `clientes.md` no tiene el monto real de cada cliente: hay que cargarlo y recalcular el punto de partida.
- **AI Agents tiene un solo cliente, y a precio piloto.** Los 3–5 cierres por año no tienen historia todavía; es el supuesto más frágil y el que más mueve el resultado.
- **El crédito de IA es un supuesto de arranque** (`negocio.md` § 3): si el consumo real es mayor, el neto de AI Agents baja.
- **Capacidad:** 15–20 proyectos nuevos por año con un developer solo (más Matías puntual) es el techo práctico. El escenario base de 2029–2030 (25–28 cierres por año) probablemente requiera sumar a alguien.

### Gatillos trimestrales

- Cierres reales por frente contra la tabla de arriba. Si AI Agents cierra menos de 2 en el primer semestre de 2027, el escenario conservador pasa a ser el de referencia.
- Recurrente neto real (no proyectado) contra USD 1.173/mes: es el número que decide la salida del Ministerio, y tiene que sostenerse **6 meses seguidos** antes de decidir.

---

## Plan 2026-07-29 (solo Build) — superado por el modelo por frente del 2026-10-15

### La matemática del hito 2028
- Breakeven (cubre el sueldo del Ministerio): **35 clientes** activos con upsells → recurrente ≈ USD 1.243/mes (35 × 426 / 12).
- **43 clientes es el objetivo de referencia** (decisión 2026-07-29): recurrente ≈ USD 1.526/mes, con colchón.
- Ticket efectivo de planificación = USD 426/año (plan promedio 342 + upsells 84); observado H1 2026 = USD 474 (con precios pre-suba).
- Nunca se necesitan más de 8–10 contactos nuevos por semana. El cuello de botella es la tasa de cierre, no el volumen.

### Proyección

| Año | Clientes | Bruto USD (aprox.) | Hito |
|---|---|---|---|
| 2026 | 20 | ~19.000 | |
| 2027 | 32 | ~36.700 | |
| 2028 | 45 | ~53.100 | Recurrente cubre Ministerio (≥ 43, margen de 2) |
| 2029 | 59 | ~68.500 | |
| 2030 | 74 | ~83.300 | |

**Método:** 2026 arranca en 20 clientes (los activos a mitad de año); cada año suma el delta del plan original (+9, +10, +11, +12) más un bono conservador de +3 netos/año por la política de expansión agresiva (`27-presupuesto-parametros.instructions.md`). El bruto **no** es un modelo de Build one-time + recurrente acumulado: es una extrapolación del ratio bruto/cliente del plan anterior. Antes de decidir cuánto retirar o cuándo dejar el Ministerio, reconstruir el modelo separando ingreso one-time y recurrente.

**Gatillo trimestral:** si no sube la cantidad de Builds cerrados por mes, recalibrar el bono de +3/año a la baja.
