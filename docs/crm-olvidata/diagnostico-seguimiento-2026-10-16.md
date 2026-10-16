# Dónde se cae el embudo — diagnóstico del 2026-10-16

Medido contra la base productiva del CRM, no estimado. El disparador fue otra pregunta (si convenía
alinear el prompt del bot con el criterio de los agentes comerciales); el dato dijo que el problema
estaba en otro lado.

## El número

De los **301 contactos que respondieron** (`EstadoEmbudo = Respondido`):

| Hecho medido | Cantidad |
|---|---:|
| Nunca tuvieron un follow-up **después** de responder | **276** |
| Tienen categoría cargada (están calificados) | 280 |
| Sin actividad desde hace más de 30 días | 282 |
| Pasaron por el bot LLM | 12 |
| Llegaron a presupuesto enviado (histórico, incluye los ya cerrados) | 32 |

Y el contraste que define la prioridad: **de los que llegan a presupuesto, cierra el 50%.** El cierre
no es el problema. El problema es que de 301 que contestaron, 32 recibieron una propuesta.

Cuándo respondieron: 62 en julio, **170 en agosto**, 62 en septiembre, 7 en octubre. El pico de
agosto es también el grueso de los que quedaron sin segundo mensaje.

## Qué significa

No es un problema de información ni de criterio del bot: **280 de 301 están calificados** — el
sistema sabe quiénes son, de qué rubro y qué les interesa. Contestaron, quedaron clasificados, y
nadie volvió a escribirles.

Tampoco es el bot: tocó 49 contactos en toda su historia (282 mensajes, 5,8 por conversación) sobre
un padrón de 10.235. Afinar su prompt mejora el borde de esas 49 conversaciones.

## Lo que ya existe en el CRM (y por eso el hueco sorprende)

| Pieza | Estado |
|---|---|
| `MensajesProgramadosSchedulerService` | Funciona: dispara envíos programados y **revalida la ventana de 24 h** antes de enviar |
| `OutboundSchedulerService` | Funciona: campañas con días y hora propios, cupo diario, control de corrida |
| `AvisosRenovacionSchedulerService` | Funciona, pero para clientes (renovaciones), no para prospectos |
| `SugerenciaSeguimiento` (entidad + tabla) | **Modelada y sin motor.** Tiene `EstadoEmbudo`, `DiasMinimo`, `DiasMaximo`, `Rubro` y `Texto` — exactamente el modelo de una cadencia de seguimiento |
| Botón "Sugerir" en `/Chats` | Existe, es **manual y por contacto**. El propio código lo dice: "las 6 filas de `SugerenciaSeguimiento` son borradores poco usados y el botón no tenía uso real" |
| Matriz de módulos MVP/FULL por rubro | Cargada, y el botón ya la ofrece cuando el rubro la tiene |
| `templateswhatsapp` | 23 plantillas aprobadas por Meta — la única forma de reabrir una conversación con la ventana cerrada |

**El hueco no es de capacidades: es de orquestación.** Están el motor de envío, el modelo de la
cadencia y las plantillas para reabrir. Falta **el que decide a quién le toca el próximo mensaje**.
Hoy esa decisión es un botón que alguien tiene que apretar 276 veces.

## El sistema que falta

Un `SeguimientoSchedulerService`, hermano de los tres que ya corren:

1. **Detecta el hueco:** contactos en estado abierto (Respondió, Presupuesto enviado, Derivado
   manual) sin próxima acción programada y con más de N días de inactividad.
2. **Elige el toque** con `SugerenciaSeguimiento` (el modelo ya existe: estado + ventana de días +
   rubro). Si el rubro tiene matriz MVP/FULL, el camino bueno es ofrecer la propuesta, no un
   recordatorio.
3. **Resuelve la ventana de 24 h.** Los 282 con más de 30 días de inactividad tienen la ventana
   cerrada: para esos el único camino es una **plantilla aprobada**, y eso cuesta (ARS 89,56 por
   conversación de marketing en Argentina, ARS 37,68 utility — ver `docs/olvidata/costos.md`). Para
   los que escribieron hace menos de 24 h, texto libre.
4. **Respeta el cierre pasivo (COM-011):** tope de toques por contacto, y si no contesta, se marca
   frío y se deja de gastar. Informa, no presiona.
5. **Lo que no puede decidir, lo escala:** precio y propuesta siguen siendo de Joaquín (el bot no
   cotiza por diseño — no existe la tool). El sistema le deja la cola ordenada, con la matriz del
   rubro ya resuelta.

### Lo que hay que definir antes de construirlo

- **Cadencia y topes:** cada cuántos días el primer toque y el segundo, y cuántos antes de marcar
  frío.
- **Gasto de plantillas:** reactivar los 276 por plantilla de marketing son ≈ARS 24.700 en
  conversaciones de Meta. Hay que autorizarlo antes, no después.
- **Qué dice el mensaje:** las 6 sugerencias cargadas son borradores que nadie usó. El texto lo
  define `olvidata-marketing`/`olvidata-sales` con las reglas vigentes, no el implementador.

### Cómo se mide si funcionó

La única métrica que importa acá es **respondió → presupuesto**: hoy 32 de 301 (10,6%). Está en
`docs/olvidata/pipeline.md`, que se regenera del CRM, así que el antes/después se mide solo.
