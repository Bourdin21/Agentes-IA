<!-- Archivado de docs/crm-olvidata/trazabilidad.md el 2026-10-15 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-09 (1 bloques archivados)

- 2026-09-14 (6) — analista-funcional: Discovery + Analisis de "reorientar el bot de prospeccion a los 4 frentes" (pendiente de aprobacion)

---

## 2026-09-14 (6) — analista-funcional: Discovery + Analisis de "reorientar el bot de prospeccion a los 4 frentes" (pendiente de aprobacion)

- **Agente/etapa:** `analista-funcional`, Discovery + Analisis, modo Ask (sin codigo). Entrada: el brief de `olvidata-ceo` de la entrada (5). Detalle completo en `definiciones/1-analista-funcional.md`, seccion "Feature en analisis".
- **Contexto de negocio al momento del analisis:** Landing 2D USD 375/año y 3D USD 600/año; precios de AI Agents y Chatbots confirmados por Joaquin como **promo de entrada hasta 2026-12-31**. Ninguno de esos precios entra al bot (la IA sigue sin poder cotizar).
- **Verificado en codigo, corrige 1 supuesto del brief:** el campo `website` de Google Places **ya se pide y se guarda** en `Contacto.PaginaWeb` desde la migracion `AddPaginaWebContacto` (2026-08-20), dentro del SKU de Details que ya se paga — no es un dato nuevo ni tiene costo extra. Salvedad: los contactos anteriores a esa fecha, manuales o de ads lo tienen vacio sin que eso signifique "sin web".
- **Hallazgo nuevo (riesgo R1):** `BotFlowService` indexa `Questions[contacto.Categoria!]` sin chequear la clave — un contacto clasificado por la IA con una categoria nueva (`ai_agents`/`chatbot`) que caiga al arbol de fallback tiraria error. Queda como criterio de aceptacion obligatorio (CU-33 CA4).
- **`merge`** confirmado en 3 lugares (`ConversacionIaService.CategoriasValidas`, `BotFlowService.Questions`, `BotFlowService.CategoryNames`); hoy solo la IA puede asignarlo (el menu del arbol no lo ofrece).
- **Otros hechos:** `Contacto.Categoria` es texto libre varchar(20), sumar claves no requiere migracion; el contenido que usa la IA por rubro sale del catalogo de modulos de Build (no hay nada para los frentes nuevos); Places no trae cantidad de reseñas (señal propuesta por el brief para Chatbots).
- **Salida:** 6 CU propuestos (CU-30 a CU-35) con criterios de aceptacion, 8 riesgos, 4 supuestos, 8 preguntas al cliente con variantes (P1 donde se decide el frente — campaña/automatico/hibrido; P2 web vacia historica; P3 redes cuentan como web; P4 2D vs 3D; P5 merge historico; P6 contenido de la IA por frente; P7 metrica por frente; P8 señal de volumen de consultas).
- **Banderas:** migracion EF probable (depende de P1), integracion externa si (3 plantillas nuevas en Meta), maquina de estados no.
- **Impacto en capas:** Presentacion (Contactos/Chats/Campañas/Bot), Negocio (`ConversacionIaService`, `BotFlowService`, `OutboundCampaignService`, regla perfil→frente), Datos (posible campo de frente, filas de `TemplatesWhatsApp`).
- **Gate:** Diseño bloqueado hasta aprobacion de Joaquin y respuesta a P1-P8.
- **Actualizacion mismo dia — ANALISIS APROBADO por Joaquin, P1-P8 respondidas:** (P1) frente asignado automatico por contacto, campañas siguen por rubro/ciudad; (P2) web vacia = sin web → Landing, riesgo R2 aceptado explicitamente; (P3) solo Instagram/Facebook/Linktree = sin web propia → Landing; (P4) Landing 3D para rubros visuales, 2D el resto → **4 plantillas nuevas** en vez de 3; (P5) `merge` historico se deja como "discontinuado" y un cliente actual pidiendo mejora se escala a humano; (P6) **modulos por frente en el catalogo de modulos** (nueva dependencia con `olvidata-presupuesto-bot` y migracion); (P7) solo filtro por frente en Contactos/Chats, dashboard fuera; (P8) Chatbots solo por rubro, sin reseñas de Google. Migracion EF: si. Diseño habilitado.
