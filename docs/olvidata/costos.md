# Costos — para que el "neto" sea un número y no una estimación

El plan financiero habla de recurrente **bruto** y descuenta el crédito de IA a ojo. Este archivo
junta lo que realmente sale, para poder restarlo. Los costos de hosting vivían solo en
`olvidata-infra.md` (que los usa para decidir escalado, no para calcular margen) y las tarifas de
IA y WhatsApp solo en la base del CRM, donde ningún agente las podía leer.

**Se edita a mano**, salvo las tarifas de IA y WhatsApp, que son un espejo de las tablas
`tarifasllm` y `tarifaswhatsapp` del CRM y se actualizan cuando cambian ahí.

Última revisión: **2026-10-15**.

## Hosting e infraestructura (fijo anual)

| Concepto | USD/año | Detalle |
|---|---:|---|
| SmarterASP.NET cuenta `olvidatasoft-002` (Windows Premium) | 120 | Factura real de abril 2026. **No usar el precio de lista de 95,40**: no es lo que se paga. Vence 06/04/2027 |
| Backup diario SmarterASP | 24 | Sobre la misma cuenta |
| SSL Sectigo que siguen sin migrar | ≈400 | ≈USD 29/sitio/año. Migrar a Let's Encrypt (que renueva 100% automático server-side) elimina este costo entero — ver `docs/referencia/runbook-urgencias-viaje.md` |
| Servidor DonWeb "Cloud Server" (Linux, sitios de front) | *falta* | Infraestructura separada de SmarterASP. El monto no está en ningún archivo: pedírselo a Joaquín o sacarlo de la factura |
| Dominios | *falta* | El inventario de dominios está en la memoria de infraestructura, el costo por renovación no |

**Subtotal verificable: USD 544/año (≈USD 45/mes).** Con los dos faltantes cargados, este número es
el que hay que restarle al recurrente de `metricas.md` para hablar de neto.

> Regla de escalado ya decidida (no recalcular): el addon de BD conviene hasta 4 extra sobre el cupo
> de 20; el addon de RAM **nunca** conviene (≈6x peor que abrir cuenta nueva); y ningún tier superior
> de SmarterASP mejora el USD/MB. Detalle y números en `.claude/agents/olvidata-infra.md`.

## Crédito de IA por cliente

El cargo de **Tokens IA es 25%** y desde 2026-08-20 se distribuye dentro del precio de cada módulo
(×1,25), sin aparecer como línea separada al cliente. El costo real que ese cargo cubre se proyecta
por módulo a precio de lista de API, como costo sombra interno — invisible al cliente.

Tarifas vigentes, espejo de `tarifasllm` del CRM (USD por millón de tokens):

| Modelo | Entrada | Salida | Cache lectura | Cache escritura |
|---|---:|---:|---:|---:|
| claude-opus-5 | 5,00 | 25,00 | 0,50 | 6,25 |
| claude-sonnet-5 | 2,00 | 10,00 | 0,20 | 2,50 |
| claude-haiku-4-5 | 1,00 | 5,00 | 0,10 | 1,25 |

**Lo que no está resuelto:** la suscripción (Claude Code) se paga por plan, no por token, así que el
costo sombra calculado con estas tarifas **no es una erogación real** mientras el consumo entre en el
plan. Sirve para presupuestar y para saber cuánto costaría el mismo trabajo vía API, no para restar
del neto. Para el neto, lo que corresponde restar es la **cuota de la suscripción**, que falta cargar
acá.

## Mensajería (variable, por contacto)

Tarifas de WhatsApp Business por conversación, espejo de `tarifaswhatsapp` del CRM (en ARS):

| País | Marketing | Utility |
|---|---:|---:|
| Argentina (54) | 89,56 | 37,68 |
| Chile (56) | 128,84 | 28,98 |
| Uruguay / resto de LatAm (598) | 107,24 | 16,38 |
| Fallback (otros) | 87,53 | 11,16 |

El CRM también registra consumo diario de **Google Maps Places** (`consumosmapsdiarios`:
text searches, place details y details evitados por el cache). El dato está, el costo unitario no:
falta cargar el precio por búsqueda para poder valorizar la prospección.

## Herramientas de contenido

| Herramienta | Costo | Estado del dato |
|---|---|---|
| Google VEO | USD 11,52 por tanda aprobada (referencia real de `BotPublicitario/PLAN-PUBLICACIONES.md`) | Se aprueba gasto por tanda, no es un abono |
| higgsfield.ai | *falta* | Se usa para los Reels; el plan y su costo mensual no están escritos en ningún lado |
| Meta Ads | *falta* | Hay campañas reales corriendo (ver `BotPublicitario/CAMPANAS-POR-FRENTE.md`); el gasto mensual sale de la cuenta de Meta, no de acá |

## Lo que falta para cerrar el neto

Cinco datos, y ninguno requiere trabajo técnico — son facturas que hay que mirar una vez:

1. DonWeb: monto anual.
2. Dominios: costo de renovación del inventario.
3. Suscripción de Claude Code: cuota mensual.
4. higgsfield.ai: plan mensual.
5. Meta Ads: gasto mensual promedio de los últimos 3 meses.

Mientras falten, `metricas.md` dice **recurrente bruto** y lo aclara. No se descuenta un número
inventado para que el neto "parezca" calculado: eso es exactamente lo que este archivo viene a
reemplazar.
