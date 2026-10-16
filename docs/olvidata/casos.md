# Casos reales — qué se puede afirmar de cada uno

Este archivo es el **inventario de claims verificables** de los sistemas en producción: qué se puede
decir de cada cliente en una pieza, en un mensaje de seguimiento o en una propuesta, y qué no.

Vivía dentro de `.claude/agents/olvidata-cm.md`, que lo usaba para producir contenido. Está acá
porque no es solo del CM: `olvidata-sales` manda casos como asset de follow-up y
`olvidata-marketing` los usa para elegir el mensaje por rubro. Un inventario de claims encerrado en
el agente que lo escribió obliga a los otros dos a reconstruirlo, y ahí nacen los claims inventados.

## La regla que lo gobierna

**Nada se afirma sin respaldo documental.** Todo claim de funcionalidad tiene que ser trazable a una
línea concreta de `docs/<proyecto>/`. Si no se puede respaldar, no entra en la pieza: no se
reformula con hedge, no se suaviza, se saca y la pieza se reconstruye sin eso.

Antes de nombrar una funcionalidad de un sistema de cliente:

1. Leer `docs/<proyecto>/metadata.md` (descripción, estado, stack).
2. Grepear la feature concreta en `docs/<proyecto>/definiciones/`.
3. Si el grep no devuelve nada, **la feature no existe** a los fines del contenido.

**Ojo con `estado:` en `metadata.md`** — refleja la etapa del proyecto, no la relación con el
cliente. Un proyecto "cerrado" puede seguir en producción y con features nuevas en discovery.
Verificar en `docs/<proyecto>/trazabilidad.md` antes de descartar un caso por su estado.

**Nunca asumir integraciones de hardware** (balanza, ticketeadora, lector de código de barras,
impresora fiscal) salvo que estén explícitamente documentadas. Es el error más fácil de cometer y el
más caro: un cliente que ve el Reel y pide algo que el sistema no hace.

### Precedentes: dos claims que se cayeron en verificación (2026-09-02)

Estos casos son la razón de existir de la regla. Servían para un guion narrativamente bien armado y
aun así hubo que reescribirlo entero.

| Claim propuesto | Por qué se cayó |
|---|---|
| "Delicias Naturales: integración con balanza" | Cero menciones de `balanza`, `granel` o `fraccionado` en todo `docs/delicias-naturales/`. Lo único documentado es `Producto.unidadMedida` (enum Kg/Unidades/Gramos): venta **por peso** sí; integración con **hardware** de balanza, no consta. En La Platense está escrito explícitamente que "la ticketeadora es manual, no se integra con el sistema". |
| "El cuaderno de fiado" como dolor compartido por los 3 clientes | En Delicias Naturales las únicas menciones de "cuenta corriente" refieren a la **cuenta bancaria del negocio**, no a fiado de clientes. Y en `docs/la-platense/definiciones/3-arquitecto-mvc.md` el origen de "Ventas + cuenta corriente de clientes (fiado)" figura como `marihogar`. El dolor no era común a los tres y era el eje del guion entero. |

---

## Fichas

### Delicias Naturales — dietética (`docs/delicias-naturales/`)

- **Afirmable:** venta por unidad **y por peso** (`Producto.unidadMedida`, enum Kg/Unidades/Gramos).
  Gestión comercial con 19 módulos. En producción real desde jun-2025 (+1 año de uso continuo, el
  cliente más antiguo — la prueba social más fuerte en durabilidad). Origen del patrón AFIP (.p12,
  WSAA, FECAESolicitar) que se reutiliza cross-proyecto.
- **NO afirmable:** integración con balanza. Cuenta corriente de clientes (fiado).
- **Riesgo de imagen:** ASP.NET MVC 5 / .NET Framework 4.7.2, skin visual más vieja que Marihogar y
  La Platense (que tienen el refresh de tema oscuro de ago-2026). Si el reveal es captura real, usar
  el **dashboard rehecho en 2026**, nunca grillas admin crudas. Alternativa: enmarcar la antigüedad
  como fortaleza ("más de un año de uso real, no una demo") en vez de esconderla.
- **Valor comercial:** hay pipeline abierto en el mismo rubro (`dietetica-mitre` y
  `desborder-sin-gluten`, propuestas preparadas). Un clip recortable de solo el beat de dietética
  sirve de asset de follow-up para `olvidata-sales` en esos deals.

### Ferretería La Platense — ferretería (`docs/la-platense/`)

- **Afirmable:** catálogo con conversión unidad de compra → unidad de venta (`UnidadCompra` +
  `UnidadVenta` + `FactorConversion`) — compra el rollo, vende el metro; compra la caja, vende la
  unidad. ~96.500 productos migrados. En producción desde el 24/08/2026
  (`ferreterialaplatense.com.ar`). Cuenta corriente de clientes/proveedores/empleados, caja
  diaria/mensual, compras con listas de precios de proveedor, entregas, presupuestos, dashboard.
- **NO mostrar:** **facturación / AFIP** — está bloqueada en ese sistema. Ninguna pantalla de
  comprobante en cuadro.
- **NO afirmable:** integración con ticketeadora (documentado como manual).

### Marihogar — casa de decoración y hogar (`docs/marihogar/`)

- **Afirmable:** catálogo, stock, presupuestos, ventas, entregas, facturación AFIP/ARCA, compras a
  proveedores, cheques, cuenta corriente de clientes y proveedores, caja, proyección financiera. En
  producción real con movimiento diario.
- Es el único de los tres con **cuenta corriente de clientes (fiado)** confirmada — si el contenido
  usa el ángulo del fiado, va solo acá.

### Contadores BMA — estudio contable (`docs/contadores-bma-agentes-ia/`, `docs/contadores-bma-conversor/`)

**Es el caso del frente AI Agents** (confirmado por Joaquín el 2026-10-16, DEC-007).

- **Afirmable:** **está en producción desde el 2026-10-07 con tres agentes productivos** —
  conciliación bancaria, liquidación de sueldos e impuestos/soporte de sistemas— corriendo en
  `agentes.olvidata.com.ar`. Confirmado por Joaquín y registrado en
  `docs/contadores-bma-agentes-ia/metadata.md` y `definiciones/5-implementador.md`. Es trabajo
  diario del estudio, no una prueba. El conversor del mismo cliente está entregado y en uso desde
  antes (proyecto aparte, `docs/contadores-bma-conversor/`).
- **NO afirmable:** las nueve capacidades del relevamiento original — el trabajo real son **tres**
  agentes, no nueve (`definiciones/2-disenador-funcional.md`). Tampoco los agentes que están en
  presupuesto y todavía no se construyeron.
- **NO mencionar:** precio ni plan. Los dos sistemas de este cliente están **regalados** (sin
  mantenimiento), así que el caso no sirve para hablar de recurrente ni de valor del plan.
- **Corregido el 2026-10-16:** esta ficha nació diciendo que el proyecto estaba "en
  Discovery/Diseño", y era falso — una corrida de evals (EV-NEG-005) mostró que el agente de ventas
  lo citaba mejor que la ficha, porque fue a `docs/contadores-bma-agentes-ia/` y leyó el estado real.
  El propio proyecto ya tenía anotado que tres agentes en producción no habían dejado rastro donde
  debían; esta ficha repitió el error.

### El CRM de Olvidata — el caso del frente Chatbots (producto propio)

**Es el caso del frente Chatbots** (confirmado por Joaquín el 2026-10-16, DEC-007), y se puede
mostrar aunque sea producto propio y no de un cliente.

- **Afirmable:** el agente de ventas IA (conversación agéntica con Claude vía API) está **encendido y
  en vivo en producción** desde 2026-09-14: contesta solo en WhatsApp y categoriza al contacto. Está
  registrado en `docs/crm-olvidata/trazabilidad.md`. Hay volumen real detrás —ver `pipeline.md`: más
  de 10.000 contactos y 9.000 respuestas registradas.
- **NO afirmable:** ninguna tasa de conversión o cierre del bot, que no está medida (y la conversión
  asistida no se puede atribuir, ver `metricas.md`). Que resuelva sin humano: **contesta y deriva**.
- **Cómo se presenta:** como lo que es — la herramienta con la que Olvidata vende, funcionando todos
  los días. No como "un cliente que usa Chatbots". Es más fuerte así: el que lo vende lo usa.

### El hallazgo que ata a los tres — linaje real de código

`docs/la-platense/definiciones/3-arquitecto-mvc.md` (línea 89) documenta que
`Producto.unidadMedida` (Kg/Unidades/Gramos) de **delicias-naturales** es la "base conceptual" de
`UnidadVenta` en **La Platense**, extendida con `UnidadCompra` + `FactorConversion`.

Esto habilita el mensaje más fuerte del catálogo, sin inventar nada: **"vendas por kilo, por metro o
por unidad, el mismo sistema lo entiende"** — no es un claim de marketing, es cómo evolucionó el
código. Usarlo como eje siempre que se pueda.

---

## Clientes activos sin ficha

Estos están en producción y pagando (ver `clientes.md`), pero **nadie verificó todavía qué se puede
afirmar de ellos**. La ausencia de ficha no significa "no se puede decir nada": significa que hay
que hacer el paso 1-2-3 de la regla antes de usarlos en una pieza. Armar la ficha cuesta un grep
dirigido y evita que el caso se descarte por desconocimiento.

| Cliente | Dónde verificar | Por qué puede valer la pena |
|---|---|---|
| Eleven La Plata | `docs/eleven-la-plata/` | En producción desde 2025, el caso más largo después de Delicias; movimientos y cuentas con uso diario real |
| Estancia Santa Rosa (ganadería) | `docs/ganaderia/` | Único caso de rubro agropecuario — abre un vertical entero sin competencia en el portfolio |
| KOI Dumplings | `docs/koi/` | Gastronomía + portal del inversor: el único caso con dos públicos distintos en un sistema |
| LABIPAC | `docs/labipac/` | Salud/laboratorio, rubro regulado; recurrente en 0 en el CRM (ver `clientes.md`) |
| ShowroomGriffin | `docs/ShowroomGriffin/` | Indumentaria con variantes (color/talle) — matchea el pipeline abierto de FABINCO y Peras del Olmo |
| Vino y se fue | `docs/vinosefue/` | Importación de listas de precios de proveedor (AQV/Sowi) ya resuelta |
| Lumitrack / Recotrack | `docs/lumitrack/`, `docs/recotrack/` | Dos sistemas del mismo cliente, caso de expansión (land-and-expand) |
| Diercas SA | `docs/diercas/` | Único caso del frente **Landing** con cliente real — hoy el frente se vende sin ningún caso propio |
| PiApartments | `docs/piapartments/` | Alquileres temporarios, rubro distinto a todo el resto |

> **Cobertura por frente, al 2026-10-16:** **Build** tiene tres fichas verificadas (Delicias, La
> Platense, Marihogar). **AI Agents** tiene Contadores BMA y **Chatbots** el CRM propio, los dos
> confirmados por Joaquín al resolver DEC-007 — con la salvedad de que ninguno de los dos tiene
> todavía claims verificados feature por feature, así que hay que hacer el 1-2-3 antes de usarlos.
> **Landing** es el único frente que queda sin ficha: su cliente real es Diercas, y además tiene el
> formulario con error 500 sin resolver (DEC-002, abierta).
