# Modelo de negocio — Olvidata Soft

Dueño: `olvidata-ceo`. Precios: `precios.md` (no se repiten acá). Plan y metas: `plan.md`. Clientes: `clientes.md`. Reglas de comunicación: `comunicacion.md`.

## 1. Cuatro frentes de producción (vigente desde 2026-09-13)

El estudio se presenta en **cuatro frentes separados**, en este orden, en el sitio (rama `sitio-3d` de olvidatasoft-new) y en todo material nuevo:

1. **Landing** — landing pages institucionales: 2D, 2D autogestionable (panel de promociones) y 3D ("presencia digital con profundidad real").
2. **Build** (Build your own software) — sistema de gestión 100% a medida por rubro, más plan anual de mantenimiento.
3. **AI Agents / Second Brain corporativo** — agentes de IA **administrativos y operacionales** para el trabajo de oficina de todos los días (no ventas). Se entregan sobre el portal **Agentes Multi-rubro**, que **no es un SaaS aparte**: es el modo estandarizado de entregar agentes personalizados por organización (licencia, versionado, telemetría, conectores, aprobaciones). Corrección de Joaquín 2026-09-21.
4. **Chatbots** — **ventas y consultas automáticas**. Van **separados** de AI Agents a propósito: los clientes los piden por separado. El caso a mostrar es el agente de ventas IA del CRM propio, **encendido y en vivo en producción desde 2026-09-14** (`docs/crm-olvidata/trazabilidad.md`). Se puede afirmar que atiende conversaciones reales; no fabricar métricas de conversión. Hoy es herramienta interna: venderlo a un cliente implica construirle su propia instancia.

**Dados de baja (2026-09-13):** **Rent** y **Merge**. No ofrecerlos ni mencionarlos. Una ampliación sobre un sistema ya entregado se cotiza como upsell "módulo nuevo" (`precios.md`). Si alguien con sistema de terceros necesita mejoras, la respuesta es Build (reescritura) o descarte.

> Alerta técnica (2026-09-14, del CRM, no de este archivo): el bot del CRM todavía tiene `merge` como categoría válida en código (`ConversacionIaService.CategoriasValidas`, `BotFlowService.CategoryNames`). Avisar a la secuencia de agentes del CRM.

**century-21 nunca se llevó a cabo** (Joaquín, 2026-09-14): no usarlo como caso, canal ni argumento.

**Narrativa de marca** (arco del video del sitio, aprobado): universo → Big Bang (hero) → primeros cuerpos (Landing 3D) → la gravedad ordena los nodos = ordenar la operatoria (Build) → equipos conectados adaptando la IA (AI Agents) → los bots que trabajan para vos (Chatbots) → retorno al orden. Progresión "caos → orden → colaboración → IA a tu servicio".

## 2. Catálogo de Build por rubro (sin nombres comerciales)

- Indumentaria y calzado: stock con variantes, cuotas, compras, devoluciones.
- Alimentos y bebidas: 2 sistemas (dietéticas 19 módulos + vinos 16 módulos, facturación ARCA).
- Agropecuaria: ganadería (ingresos/egresos/stock/caja).
- Real estate: administración de edificios y propiedades.
- Servicios urbanos: **2 sistemas, se cuentan separados** (2026-10-14) — recolección de residuos (`recotrack`) y alumbrado público (`lumitrack`), los dos en producción.
- Gestión comercial multirubro: 27 módulos (alquiler de maquinaria + operación general).
- Salud: consultorios y centros (turnos, historia clínica, estudios).
- Finanzas personales: billetera virtual, gastos, proyecciones.
- A medida: cuando el rubro no encaja.

## 3. AI Agents — cómo se arma lo que se vende

**Tier de agente personalizado → configuración en el portal** (2026-09-21):
- **Básico:** agente propio de la organización, derivado de un agente del núcleo con instrucciones/tono propios; sin conectores; reglas básicas; sin subagentes.
- **Intermedio:** agente propio + 1 conector activo con credenciales de la organización; reglas más específicas; eventualmente un coordinador con 1 subagente.
- **Avanzado:** coordinador con subagentes, varios conectores, tarea programada posible, reglas de aprobación por rol para pasos sensibles.

**El driver de costo no es la cantidad de agentes** (un agente derivado por instructivo cuesta USD 0 de construir): son las integraciones a mantener, la ingeniería nueva genuina y el volumen de tokens (cubierto por crédito + excedente × 3).

**El núcleo se nutre en cada setup y eso no sube la licencia.** Lo generalizable de cada cliente pasa al núcleo del rubro y beneficia a los próximos; respalda las subas ya calendarizadas, nunca un recálculo cliente por cliente. **El cliente 1** que aporta el criterio que después se estandariza se reconoce con precio piloto, no con regalía.

**Relevamiento externo (Bernarda):** su entregable tiene que traer (1) vocabulario exacto del rubro, (2) reglas en formato condicional, (3) circuitos paso a paso con actor y herramienta, (4) ejemplos reales anonimizados, (5) excepciones que se resuelven a mano, (6) inventario de integraciones con tipo de acceso. Arranca **después del 50% de anticipo cobrado**.

**Crédito de IA:** se incluye a costo real, sin margen (el margen está en el servicio). Es un supuesto de arranque a validar con el consumo real de los primeros agentes en producción.

**Costo de IA de referencia** (verificado 2026-09-21): Sonnet 5 USD 2/10 por millón de tokens entrada/salida; Opus 5 USD 5/25; Haiku 4.5 USD 1/5; caché 5 min: escritura × 1,25, lectura × 0,1; búsqueda web USD 10 cada 1.000. Bot del CRM propio: USD 0,006–0,045 por conversación con Opus 5.

## 4. Proceso de venta — ciclo 7–10 días

Contacto (respuesta el mismo día) → demo 15 min → propuesta con vencimiento 7 días → 2 follow-ups (día 3 y día 6) → cierre con 50% de anticipo no negociable. **Cierre siempre pasivo**, nunca se presiona ni se pide fecha. La ejecución deal por deal es de `olvidata-sales`.

**Metodología PACS (obligatoria desde 2026-09-19):** `.github/instructions/36-metodologia-pacs.instructions.md` — Nicho → Autoridad → Mensaje conversacional → Sistematización. Objetivo: reuniones agendadas.

## 5. Canales y su rol

- **Referidos:** canal #1, cierre ~50%, costo cero → pedirlos sistemáticamente.
- **Instagram:** no vende — comunica y presenta proyectos (2026-10-01). El prospecto del bot mira el perfil antes de contestar. Persona o cliente real en cámara mide 65,9 de engagement contra 17,5 de las placas de producto.
- **LinkedIn:** posicionamiento consultor para tickets altos 2028–2030.
- **WhatsApp:** canal de cierre exclusivo — no mandar presupuesto por email y esperar.
- **Bot outbound:** volumen de prospectos fríos (Google Maps + Meta Ads).

## 6. Marca personal vs. marca corporativa (2026-09-02)

Se vende como **Joaquín**, con Olvidata Soft como respaldo detrás, también en los clientes de Build. Joaquín ya trabaja como Forward Deployed Engineer: embebido en la operación de cada cliente. No usar "FDE" como jerga con el cliente de catálogo; sí como ángulo de LinkedIn.

- **Excepción — sitio web** (2026-09-14): voz de marca, tono empresarial ("Olvidata Soft", "nosotros"). *"Una web tiene que mostrarse empresarial."*
- **Tensión a futuro (no urgente):** cuanto más se vende "Joaquín", más se ata el valor a su persona. Impacta (1) delegar a Matías, que requiere transferir confianza y no solo código, y (2) una eventual venta del negocio (no antes de 2028), que requeriría separar la marca de confianza del activo vendible.

## 7. Teorías de negocio aplicadas (servicio → producto)

- **Productized service como puente a SaaS:** Build ya es un servicio productizado (alcance fijo, precio por rango, workflow estandarizado). La señal del próximo candidato a productizar es una entrega técnica que se repite calcada entre rubros.
- **Vertical > horizontal:** los verticales crecen 18–32% anual contra 12–15% de los horizontales. Valida el catálogo por rubro; no diluirlo.
- **Land-and-expand:** la expansión más barata es upsell sobre la base (40–50% del ARR nuevo en SaaS maduro).
- **Métricas de salud:** NRR (> 106% es sano; SMB promedia ~97%), LTV:CAC (benchmark SMB ~2,5:1; referidos con CAC ~0 lo empujan), Rule of 40.
- **Category design:** cada rubro como categoría propia ("el sistema para consultorios"), en vez de competir en "software de gestión" contra Alegra, Contabilium o Xubio.
