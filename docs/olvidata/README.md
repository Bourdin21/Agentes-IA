# docs/olvidata — la memoria de negocio

Hasta el 2026-10-15 la memoria de Olvidata guardaba **reglas y supuestos** (dentro de los
`.agent.md`, que llegaron a 66 y 75 KB) pero no **lo que efectivamente pasa con clientes y ventas**.
El plan financiero proyectaba con un ticket estimado de USD 426 por cliente sin que nadie hubiera
medido el real; el pipeline existía deal por deal en la cabeza de quien lo atendía; y el número que
gobierna la decisión más importante del plan —el recurrente que permite dejar el Ministerio— no se
registraba en ninguna parte.

Esta carpeta es ese registro.

## Qué hay acá

| Archivo | Qué contesta | Cómo se mantiene |
|---|---|---|
| `clientes.md` | Quién paga, qué plan, cuánto, cuándo renueva, qué renovación está vencida | **Generado** del CRM |
| `pipeline.md` | El embudo por etapa, la conversión real y los leads que están vivos hoy | **Generado** del CRM |
| `metricas.md` | Una fila por mes: recurrente, altas, upsells, y el semáforo del umbral del Ministerio | **Generado** del CRM |
| `costos.md` | Hosting, IA, mensajería y herramientas — para que el "neto" sea un número | A mano |
| `casos.md` | Qué se puede afirmar de cada cliente, y qué no | A mano |
| `precios.md` | Fuente única de precios de catálogo y planes | A mano, con línea obligatoria en `trazabilidad.md` |
| `reglas-comerciales.md` | Las reglas vigentes con ID citable (`COM-NNN`) | A mano |
| `decisiones.md` | Lo que espera una definición de Joaquín | A mano |
| `trazabilidad.md` | Log de cambios de precios y reglas | A mano, append |
| `datos-manuales.yml` | Lo que el CRM no sabe (frente por cliente, umbrales) y los scripts necesitan | A mano |
| `marca/` | MARCA.md, el plan de comercialización del Second Brain, la línea editorial y el posicionamiento NL (`posicionamiento-nl.md`) | A mano |
| `nl/` | Cuenta de Instagram en inglés para Países Bajos: `feed.md` (inventario de lo publicado y su versión EN) y `perfil.md` (configuración del perfil) | A mano, por `olvidata-traductor` / `olvidata-revisor-en` |

## Los tres generados no se editan a mano

```
python scripts/olvidata_datos.py todo        # clientes + pipeline + metricas
python scripts/olvidata_datos.py clientes --dry-run
```

Leen el CRM productivo (`clientes`, `upsells`, `contactos`) con la connection string del repo del
CRM, que está fuera de este repo: **ningún secreto entra acá**. Si se edita un generado a mano, el
cambio se pierde en la próxima corrida — lo que haya que agregar va en `datos-manuales.yml`.

Conviene regenerarlos antes de cualquier conversación de plan, pricing o pipeline: un snapshot de
hace dos meses miente con la misma cara que un dato bueno.

## Lo que el CRM todavía no puede contestar

Está anotado al pie de `metricas.md` y no es un problema de cálculo, es que falta el dato de origen:
la **tasa demo → cierre** (el CRM registra el presupuesto enviado, no la demo), la **conversión
asistida de Instagram** (no hay forma de atribuir un cierre a una publicación) y el **frente
comercial de un contacto** (`FrenteComercial` existe en el catálogo de módulos, no en el contacto, así
que el frente de un lead se infiere del gancho).

## Para los agentes de negocio

- `olvidata-ceo` → `metricas.md` y `clientes.md` antes de hablar de plan o breakeven; `precios.md` para
  cualquier número de catálogo.
- `olvidata-sales` → `pipeline.md` para saber qué está abierto, `casos.md` para mandar un caso de
  seguimiento, `precios.md` para cotizar.
- `olvidata-marketing` y `olvidata-cm` → `casos.md` (qué se puede afirmar) y `reglas-comerciales.md`
  (qué se puede decir y cómo).
- `olvidata-traductor` y `olvidata-revisor-en` → `marca/posicionamiento-nl.md` (glosario y tono), `casos.md` y `nl/feed.md`.
- `olvidata-infra` → `costos.md` es el espejo comercial de lo que ese agente decide técnicamente.

Todos → `decisiones.md` antes de asumir que algo está definido.
