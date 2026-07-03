# Memoria - Analista funcional

## Proyecto: meta-ads — extensión "Bot de respuesta automática WhatsApp"
## Última actualización: 2026-07-01

---

## Análisis funcional — borrador (pendiente 2 definiciones antes de Diseño)

### Contexto del negocio

- Negocio: OlvidataSoft (software factory, La Plata). Ya opera dos canales de captación por WhatsApp:
  - **Canal A — Ads pagos:** campañas Meta Ads (Instagram/Facebook) con clic-to-WhatsApp. Ya en producción desde 2026-05-14 (`create_olvidata_campaigns.py`, `olvidata_ads_ids.json`).
  - **Canal B — Outbound frío:** contacto directo a PyMEs relevadas por Google Maps o referidos (`OutboundCampaignService`, plan documentado en `plan_contacto_whatsapp.md`).
- Catálogo de industrias/rubros que el bot puede calificar y cotizar: ver tabla completa en "Fuente de precios — reconciliada" más abajo. Reemplaza los nombres de marca ficticios (HEAVEN/SIGMA/OLVIDATES/FORGE/CREW/FLOW/BUILD/LANDING) de `plan_contacto_whatsapp.md` por la industria real de cada sistema ya construido en `C:\Sistemas\`.

### Estado actual (relevado en código, `C:\Sistemas\BotPublicitario`)

- **Outbound:** completo. Envía Script A/B/C (frío/referido/nurturing), trackea estado en `outbound_state.json`.
- **Inbound:** `Webhook/Program.cs` recibe el POST de Meta y **solo loguea** el mensaje (`MessageLogService.LogMessageAsync`) en `messages_log.jsonl`. No parsea el objeto `referral` de Meta (de qué anuncio vino el clic). No hay ninguna respuesta automática: el protocolo documentado (`plan_contacto_whatsapp.md`, Paso 3) es 100% manual — Joaquín lee y contesta a mano.
- **Gap a cubrir:** todo el tramo entre "el prospecto responde" y "se le envía un presupuesto" está sin automatizar, en ninguno de los dos canales.

### Decisiones confirmadas con el cliente (2026-07-01)

1. **Alcance de canales:** el bot de respuesta automática cubre **ambos** — clics en ads (Canal A) y respuestas a outbound frío (Canal B). Se unifica el manejo de la primera respuesta del contacto sea cual sea el origen.
2. **Segmentación:** **no** se usa el `referral` de Meta para inferir la industria directamente. El bot **pregunta el rubro/tipo de negocio** al prospecto y lo mapea a una industria según la tabla de "Fuente de precios" (con su sistema de referencia real y plan correspondiente).
3. **Presupuesto:** se calcula con el **precio base de tabla + un ajuste por una variable simple** relevada durante la calificación (no es precio fijo puro, tampoco un cálculo complejo).

### Proceso objetivo

1. Prospecto escribe al WhatsApp del negocio (por ad o por respuesta a outbound).
2. Si es su primer mensaje sin conversación previa calificada → el bot inicia el flujo guiado.
3. Bot pregunta el rubro/tipo de negocio (texto libre).
4. Bot mapea la respuesta a una industria (ver tabla en "Fuente de precios") por palabras clave del rubro.
5. Bot pregunta cantidad de usuarios (variable de ajuste de precio, ver N4).
6. Bot calcula el presupuesto (precio base + ajuste) y lo envía por WhatsApp.
7. Bot ofrece agendar demo de 15' (proceso ya documentado, Paso 4-5 de `plan_contacto_whatsapp.md`); si acepta, notifica a Joaquín (ya existe `ADMIN_NOTIFY_PHONE` en la config del Webhook).
8. Si la respuesta del prospecto no matchea ninguna opción esperada (texto libre fuera de guion) → fallback "un representante te va a contactar" + notificación a Joaquín. Igual que el criterio ya usado en decorhogar M8.

### Módulos a construir (extensión de `BotPublicitario`)

| # | Módulo | Descripción |
|---|---|---|
| N1 | Parser de `referral` | Ampliar `Webhook/Models.cs` (`IncomingMessage`) para capturar `referral` (ad_id, source, headline) — se guarda como dato de origen aunque no decida el sistema, útil para reporting |
| N2 | Máquina de estados por contacto | Nuevo → CalificandoRubro → CalificandoAjuste → PresupuestoEnviado → [DemoSolicitada \| DerivadoManual] |
| N3 | Motor de calificación por reglas | Preguntas cerradas (interactive buttons/list de WhatsApp) → mapeo rubro→sistema |
| N4 | Calculador de presupuesto | Precio base por sistema + ajuste por variable simple |
| N5 | Envío de presupuesto | Reutiliza `MessagingService.cs` existente |
| N6 | Persistencia de conversación | Extiende el store de estado (evaluar reuso de `outbound_state.json` vs. nuevo, ver abierto #3) para unificar leads de ambos canales |
| N7 | Notificación a Joaquín | Reutiliza `ADMIN_NOTIFY_PHONE` ya configurado en `Webhook` |

### Casos de uso

- **CU-N1:** Lead nuevo escribe (ad o respuesta a outbound) → bot inicia calificación automáticamente.
- **CU-N2:** Lead responde rubro + ajuste → bot arma y envía presupuesto automático.
- **CU-N3:** Lead pide demo → bot notifica a Joaquín con el contexto completo (sistema detectado, respuestas, presupuesto ya enviado).
- **CU-N4:** Lead da respuesta fuera de guion → fallback humano, sin bloquear la conversación.

### Máquina de estados (por contacto)

`Nuevo → CalificandoRubro → CalificandoAjuste → PresupuestoEnviado → [DemoSolicitada | SinRespuesta | Cerrado]`
Desde cualquier estado, fallback → `DerivadoManual`.

### Componentes reutilizables identificados

| Componente | Fuente | Reutilización |
|---|---|---|
| `WhatsAppClient.cs`, `MessagingService.cs` | `BotPublicitario/WhatsApp/` | Envío de preguntas y presupuesto — sin cambios |
| `TemplateCreationService.cs` | `BotPublicitario/WhatsApp/` | Si se necesitan nuevas plantillas para reabrir ventana de 24h |
| Patrón M8 decorhogar (calificación por categoría + `referral`) | `docs/decorhogar/definiciones/1-analista-funcional.md` | Mismo enfoque conceptual, aplicado a 13 industrias reales en vez de categorías de decoración |
| `ADMIN_NOTIFY_PHONE`, config `.env` | `BotPublicitario/Webhook/Program.cs` | Ya existe, reusar tal cual |

---

## Fuente de precios — reconciliada (2026-07-01)

Se detectó una contradicción entre dos fuentes: `plan_contacto_whatsapp.md` (precio fijo por sistema vertical con nombre de marca: HEAVEN/SIGMA/OLVIDATES/FORGE/CREW/FLOW/BUILD/LANDING) vs. la página pública vigente `C:\Sistemas\olvidatasoft-new\src\pages\precios.astro` (4 planes genéricos por cantidad de tablas de BD: STARTER 1-5 tablas USD 250, PRO 6-15 USD 300, PREMIUM 16-30 USD 400, SCALE 31+ USD 750; upsell usuario adicional USD 100/año sobre los incluidos por plan).

**Resuelto con el cliente (actualizado 2026-07-01):** se reemplazan los nombres de marca ficticios por la **industria real** a la que aplica cada sistema, releída directamente del código de los sistemas ya construidos en `C:\Sistemas\` (conteo de tablas desde EF Core `DbContext`/migraciones, no estimado). El plan resultante sale del rango real de tablas de cada sistema construido, salvo dos ajustes de negocio explícitos del cliente (ver notas):

| Industria | Sistema de referencia | Tablas (código real) | Plan | Precio base | ¿Cotiza automático? |
|---|---|---:|---|---:|---|
| Gastronomía (restaurantes, franquicias, vinotecas) | Delicias Naturales (26), KOI Dumplings (22), Vino y Se Fue (17) | 17–26 | PREMIUM | USD 400/año | Sí |
| Retail / comercio minorista (indumentaria, calzado, decoración) | ShowroomGriffin (21) | 21 | PREMIUM | USD 400/año | Sí |
| Venta de entradas / eventos | TicketMarket | 29 | PREMIUM | USD 400/año | Sí |
| Alquiler de maquinaria | Eleven (19), Eleven La Plata (23) | 19–23 | PREMIUM | USD 400/año | Sí |
| Laboratorios / consultorios médicos | LabIPAC (11 tablas actuales — build parcial) | — | **SCALE** *(nota 1)* | USD 750/año | Sí |
| Ganadería / producción agropecuaria | Ganadería (Emo/Fausto) | 15 | PRO | USD 300/año | Sí |
| E-commerce / tiendas online | CellPic | 13 | PRO | USD 300/año | Sí |
| Utilities / gestión de reclamos y cuadrillas | LumiTrack | 12 | PRO | USD 300/año | Sí |
| Alquiler de inmuebles / gestión de propiedades | Alquileres/Roaming (9), Las Latas (9) | 9 | PRO | USD 300/año | Sí |
| Recolección de residuos / logística de campo | RecoTrack | 8 | PRO | USD 300/año | Sí |
| Finanzas personales (gestión completa) | VirtualWallet | 8 | PRO | USD 300/año | Sí |
| Finanzas simples / gestión de cuentas | SaldoClaro | 5 | STARTER | USD 250/año | Sí |
| Landing page / sitio sin sistema de gestión | — *(nota 2)* | 1–5 | STARTER | USD 250/año | Sí |
| A medida / rubro sin precedente | — | — | Variable | A cotizar | **No** — deriva a Joaquín |

**Nota 1 — Laboratorios/consultorios médicos:** el sistema de referencia real (LabIPAC) hoy tiene solo 11 tablas porque es un desarrollo parcial (calculadora de montos a cobrar). El cliente confirmó que la oferta completa para este rubro apunta a un sistema integral de mayor alcance → se cotiza en **SCALE (USD 750/año)**, no en el plan que le correspondería a las tablas actuales de LabIPAC.

**Nota 2 — Landing page:** confirmado por el cliente — páginas de front-end/landing sin sistema de gestión de datos van directo a **STARTER (USD 250/año)**, consistente con la propia descripción del plan Starter en `precios.astro` ("...o una página de front-end / landing page").

**Inmobiliarias (venta/corretaje, no alquiler):** Century 21 está presupuestado en `docs/century-21/` pero **no tiene código construido todavía** — sin precedente real de tablas. Se trata como "a medida / rubro sin precedente" hasta que exista un sistema de referencia.

Ajuste por usuarios (upsell fijo de `precios.astro`): cada plan incluye N usuarios (Starter=1, Pro=2, Premium=3, Scale=ilimitado); usuario adicional = **+USD 100/año** cada uno. Esta es la "variable simple" de ajuste de precio (N4): el bot pregunta cuántas personas van a usar el sistema y suma el excedente sobre los incluidos por plan.

**Regla resultante:** el bot cotiza automático para las 13 industrias con sistema de referencia real. Para "a medida / rubro sin precedente", califica el lead igual pero no calcula precio — pasa directo a `DerivadoManual` con nota, porque el precio real depende de un relevamiento que el bot no puede hacer por WhatsApp.

## Decisiones cerradas (ya no bloquean Diseño)

1. ~~Variable de ajuste de precio~~ → Resuelto: cantidad de usuarios, upsell USD 100/año c/u sobre los incluidos por plan (ver tabla arriba).
2. ~~Mecánica de la pregunta de calificación~~ → Resuelto: **texto libre** con reglas simples de palabras clave (no botones interactivos). Implica mayor tasa de fallback a `DerivadoManual` esperada — aceptado por el cliente.
3. ~~Unificación de persistencia~~ → Resuelto: **mismo registro unificado** — antes de crear un contacto nuevo, el bot busca el número en el store existente (`outbound_state.json` o su reemplazo) y continúa desde ahí si ya existía, sea cual sea el canal de origen.

## Supuestos confirmados

- Reutilizar toda la infraestructura de mensajería existente (`WhatsAppClient`, `MessagingService`) sin reescritura.
- El presupuesto se envía como mensaje de WhatsApp (no se definió aún si además PDF — a confirmar en Diseño).
- La demo de 15' y el cierre siguen siendo manuales (Joaquín), el bot solo califica y cotiza.
- Precio fuente de verdad: `precios.astro` (planes públicos), no los montos fijos de `plan_contacto_whatsapp.md` — este último debería actualizarse para reflejar la tabla de mapeo de arriba (fuera de alcance de este proyecto, es un doc de proceso comercial).

## Historial de ajustes

- 2026-07-01: Discovery + análisis funcional cerrado. Relevado el estado actual del código (`BotPublicitario`): outbound completo, inbound solo logueado sin respuesta automática. Confirmado con el cliente: automatizar ambos canales (ads + outbound), segmentación por pregunta al usuario, calificación por texto libre, persistencia unificada por número de teléfono. Detectada y resuelta contradicción entre `plan_contacto_whatsapp.md` y la página pública de precios vigente — se usa esta última como fuente de verdad, con mapeo sistema→plan por cantidad de tablas. BUILD y LANDING quedan fuera de la cotización automática (derivación manual). Análisis funcional cerrado, listo para pasar a Diseño.
