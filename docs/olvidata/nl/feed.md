# Feed NL — inventario de lo publicado y su versión en inglés

Una fila por pieza publicada en `@olvidata.soft` (castellano), con su estado para la cuenta en inglés
dirigida a Países Bajos. Lo traduce `olvidata-traductor`, lo califica `olvidata-revisor-en`, lo
publica Joaquín a mano. **Ninguna pieza se pauta sin estar `aprobada` y publicada en la cuenta EN**:
los avisos se levantan por post ID del orgánico, no como dark post.

Creado 2026-10-29. Posicionamiento, glosario y tono: `docs/olvidata/marca/posicionamiento-nl.md`.

## Estados

`por traer` (falta el texto original) → `por traducir` → `traducida — pendiente revisión` →
`aprobada` | `rechazada — ver revisión <fecha>` → `publicada EN <fecha> · <post ID>` → `pautable`.
`descartada` = depende de Argentina (AFIP, factura, pesos…) o de un claim no afirmable; lleva motivo.

## Inventario

Fuente de cada fila: lo que el repo documenta como publicado. **No es el feed completo** — ver
"Carga pendiente" abajo.

| ID | Pieza original | Tipo | Publicada | Clasificación NL | Estado | Pauta | Fuente |
|---|---|---|---|---|---|---|---|
| NL-001 | *Un prompt no es una regla* (carrusel `d`, línea Second Brain, P1) | Carrusel | 2026-10-03 · pautada `AD-R5` | Trasladable con cambios: abre con el dolor del olvido, molde dado de baja el 2026-10-11 en castellano. En la cuenta EN no hay pieza publicada que proteger: **se traduce con la apertura nueva** (el concepto, no el dolor) | por traer | candidata a primera pieza pautada (argumento, sin caso argentino) | `marca/linea-second-brain.md` líneas 109 y 147 |
| NL-002 | Reel de la ferretería (producto operando) | Reel | sí — fecha a confirmar | Trasladable: es el molde de "resultado operando" (`MARCA.md` § 1). Pantalla en castellano → regla 6 del traductor | por traer | candidata: caso con producto andando | `marca/MARCA.md` línea 256 |
| NL-003 | `AD-R2 · Andrea` (caso con persona) | Reel / aviso | sí — fecha a confirmar | A clasificar con el texto: mejor CTR (1,86%) de la cuenta en AR; trasladable si el caso no depende de facturación argentina | por traer | candidata si es trasladable | `.claude/agents/olvidata-cm.md` § Meta Ads |
| NL-004 | Reveal del chatbot (agente de ventas IA en WhatsApp) | Reel (inserto) | sí — fecha a confirmar | Trasladable: frente Chatbots, encendido en producción desde 2026-09-14. Sin métricas de conversión (no están medidas) | por traer | candidata | `olvidata-cm.md` (reveals `chatbot.mp4`) |
| NL-005 | Reveal web 3D (frente Landing) | Reel (inserto) | sí — fecha a confirmar | Trasladable: Landing es el frente con menos dependencia local | por traer | candidata | `olvidata-cm.md` (reveals `web 3d.mp4`) |

### Lo que va a quedar `descartada` casi seguro (no traducir sin revisar)

Cualquier pieza cuyo eje sea facturación electrónica AFIP/ARCA, padrones, constancias, cuenta
corriente en pesos o cuotas. No hay equivalente que podamos prometer en NL (`olvidata-traductor`,
regla 4).

### Lo que no se traduce porque todavía no está publicado en castellano

P2 a P11 de la línea Second Brain (`marca/linea-second-brain.md`). Entran al feed NL cuando salgan en
castellano, en el mismo orden — la cuenta EN sigue la cadencia de la ES con desfase, no la adelanta.

## Carga pendiente — traer el feed completo

El repo no guarda los textos publicados (viven en Instagram y en `C:\Sistemas\BotPublicitario`, que
no está en git). Para completar este inventario:

1. **Reautorizar el conector Meta Ads** en claude.ai (Settings → Connectors). Al 2026-10-29 pide
   login de nuevo.
2. Pedir: `/olvidata-traductor traé todo el feed de @olvidata.soft y cargalo en docs/olvidata/nl/feed.md`.
   El traductor lista la media con `ads_get_ig_accounts` + `ads_get_ig_media` (cuenta publicitaria
   de Olvidata), agrega una fila por post con permalink, post ID, tipo y fecha, y clasifica.
   Sólo lectura: no pauta ni publica.
3. Alternativa sin conector: copiar a `docs/olvidata/nl/originales/` los captions y textos de placa
   de `BotPublicitario\Instagram\` (`CAPTIONS-OCT-DIC.md` y carpetas de posts).

## Orden de publicación propuesto en la cuenta EN

Las primeras 9 publicaciones arman la grilla de 3×3 que ve un holandés al entrar desde un aviso. No
se pauta nada hasta que la grilla tenga al menos 6 piezas: un perfil vacío convierte el clic en
rebote.

1. Fijada 1 — quién soy y desde dónde (pieza de presentación, `perfil.md` § Publicaciones fijadas)
2. Fijada 2 — NL-002 (producto operando)
3. Fijada 3 — NL-001 (argumento Second Brain)
4. NL-004 · 5. NL-005 · 6. NL-003 (si es trasladable) · 7–9. lo que salga de la carga completa

Las fijadas se ajustan cuando esté cerrado `posicionamiento-nl.md`.
