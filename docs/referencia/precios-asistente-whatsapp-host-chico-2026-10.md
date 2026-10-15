# Precio de referencia — Asistente de WhatsApp para host/microemprendedor

Fecha: 2026-10-15. **Número fijado a mano por Joaquín**, no sale de ninguna matriz: al momento de cotizar no había precio de lista para este perfil. Primer caso: DEPARTAMENTO SOUTHERN LIVING (Bariloche, host de un depto en Airbnb, outbound frío del bot).

Complementa `research-precios-landing-build-2026-09.md` y `docs/olvidata-agentes-multirubro/research-precios-ai-agents-2026-09.md` (ese research sigue marcado "propuesta, no vigente").

## Precio de referencia

| Concepto | Precio |
|---|---|
| **Setup del asistente** | **USD 300, pago único** |
| **Recurrente** | **USD 35/mes** |

**Forma de pago:** en pesos, al dólar blue del día del pago.

## Perfil al que aplica

Microemprendedor con **una unidad o un servicio y un solo dueño atendiendo**, que ya recibe las consultas por WhatsApp y las pierde por falta de tiempo. **No** es el perfil de empresa con varias áreas o equipos.

Contraste con el precedente que había: **BMA, USD 2.500 de setup + USD 170/mes** — pero eran 6 personas y varias ramas. No es comparable y no sirve de ancla para un host solo.

## Dónde cae contra el mercado y contra la lista propia

- **Por debajo del Starter vigente de Chatbots pyme (USD 40/mes)** y debajo del piso del SaaS de mercado (USD 29-49/mes: Cliengo 45, Chattigo/Aivo/Botmaker 49). Ojo: esos SaaS incluyen plataforma propia.
- **Muy por debajo del piso de agencia para un chatbot** (~USD 1.300 de setup + 15-20%/mes, Segundo Enfoque). El setup de USD 300 es un número de entrada para microemprendedor, no de lista.
- Queda **explícitamente abajo de todos los tiers del research de AI Agents** (Básico: setup 1.500-2.500 + 2.400/año). Este producto no es un agente de empresa: es un asistente de una sola tarea.

**Conclusión:** sirve como precio de entrada para abrir el segmento microemprendedor, no como precio de lista del frente Chatbots. Si se repite, hay que decidir si nace como tier propio (algo tipo "Host / unipersonal") o si queda como excepción comercial.

## Alcance que respalda el precio

**Entra en el setup (es base, no extra):** conectar el calendario real de la unidad propia (iCal de Airbnb o el canal que use). Sin eso el asistente repite el problema que el cliente ya tiene — un mensaje plantilla que no dice si hay lugar.

**MVP:** el asistente contesta fechas, precio y disponibilidad real **de la unidad propia**, y deriva el resto al dueño.

**FULL:** unidades de colegas (solo si consiguen calendario accesible), rent a car, y la web 3D del depto.

**NO prometer:** disponibilidad de las unidades de colegas a dueño directo — no hay calendario accesible. Ahí el asistente contesta precio y condiciones generales y deriva a un humano. Nunca decirle "contesta la disponibilidad de todo lo que manejás".

**Restricción de plataforma a tener presente:** según el research de septiembre (fuente `tecnochat`, **sin verificar**), Meta prohibiría desde el 15/01/2026 los chatbots de IA de propósito general en WhatsApp — cada bot debe estar acotado a una tarea. Este caso cumple por diseño (consultas de disponibilidad de una unidad), pero conviene verificarlo antes de escalar el producto.

## Pendiente

Falta cerrar el precio de lista del frente **Chatbots**: `pricing-agentes-multirubro.md` dice "bajo revisión". (**Landing 3D** quedó fijado el 2026-10-15: USD 1.000 el 1er año + 400/año, `precios-landing-3d-2026-10.md`.)
