# Trazabilidad de la memoria de negocio

Log de cambios de **precios** y **reglas comerciales**. No es estado: el estado vigente vive en
`precios.md` y `reglas-comerciales.md`. Acá queda el rastro de qué cambió, cuándo y por decisión de
quién.

**Obligatorio:** todo cambio a `precios.md` deja una línea acá. `scripts/doctor.py` lo verifica y
avisa si un commit toca los precios sin registrarlo. Un precio que cambia sin rastro es un precio
que nadie puede defender frente a un cliente que pregunta por qué le cotizaron distinto el mes
pasado.

Formato: `### <fecha> — <qué cambió>` y, abajo, de dónde a dónde y quién lo decidió.

## Entradas

### 2026-10-15 — nace esta carpeta: la memoria de negocio deja de ser solo reglas y supuestos
- **Cambio:** se crean `clientes.md`, `pipeline.md`, `metricas.md` (generados del CRM),
  `costos.md`, `casos.md`, `precios.md`, `reglas-comerciales.md`, `decisiones.md` y
  `datos-manuales.yml`; se mueven `MARCA.md`, el plan de comercialización del Second Brain y la línea
  editorial desde `BotPublicitario` a `marca/`.
- **Motivo:** la memoria guardaba reglas y supuestos pero no lo que pasa de verdad con clientes y
  ventas. El plan proyectaba con un ticket de USD 426 sin medir el real, y el umbral que gobierna la
  salida del Ministerio (USD 1.173/mes) no se registraba en ningún lado.
- **Precios:** `precios.md` sale de `olvidata-ceo.md` **sin cambiar un solo número** — es un
  movimiento de archivo, no una revisión de lista. El agente quedó con un puntero.
- **Reglas:** `reglas-comerciales.md` es índice, no cuerpo: cada regla sigue viviendo con su contexto
  en el archivo que la decidió, y acá tiene ID citable (`COM-NNN`) más puntero.
- **Hallazgos que el dato real dejó a la vista** (anotados en `decisiones.md`): el ticket real es USD
  294 contra los 426 del plan (DEC-004); dos clientes activos tienen recurrente en 0 (DEC-005); la
  renovación de ESCABA venció hace 13 días (DEC-006); el recurrente cobrable hoy es USD 152/mes, el
  13% del umbral del Ministerio; y la lista post-promo 2027 figura confirmada en un agente y sin
  confirmar en otro (DEC-003).
- **Impacto:** `olvidata-ceo.md` 66 → 39 KB y `olvidata-cm.md` 75 → 69 KB, por extracción de los
  precios y del inventario de casos. Menos contexto gastado al arrancar, y los datos quedan donde los
  pueden leer los cuatro agentes en vez de uno.

### 2026-10-15 — MARCA.md § 0c reescrito: prevalece la promesa del CEO
- **Cambio:** § 0c pasaba de prohibir toda la familia de "la IA hace tu trabajo" a distinguir el
  **reemplazo de la persona** (prohibido) del **alivio del trabajo cotidiano** (habilitado, COM-005).
- **Decisión:** Joaquín, 2026-10-15, consultado explícitamente.
- **Motivo:** la redacción anterior vetaba la promesa vigente del CEO desde el 2026-10-11. La
  contradicción vivió semanas sin detectarse porque los archivos estaban en repos distintos; por eso
  el mismo día MARCA.md se movió acá.
- **Registrado como:** `decisiones.md` DEC-000 (resuelta).
