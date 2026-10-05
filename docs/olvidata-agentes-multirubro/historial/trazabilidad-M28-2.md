<!-- Archivado de docs/olvidata-agentes-multirubro/trazabilidad.md el 2026-10-03 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - M28 (1 bloques archivados)

- 2026-10-02 - Analisis (analista funcional) - M28: el chat libre

---

## 2026-10-02 - Analisis (analista funcional) - M28: el chat libre

- **Las cuatro preguntas se cerraron con decision de Joaquin.** P1 -> **cuarto agente de plataforma** con prompt propio
  (se acepta que arrastra evaluacion aprobada y publicacion; sin version publicada la pantalla no se ofrece). Se descarto
  el agente en blanco de `general` con un motivo: ese es el que **el cliente** escribe entero, y el chat libre tiene que
  saber de la plataforma para poder derivar. P2 -> **tarea aparte y el hilo espera** (`EsperandoSubtareas`), no delegacion
  en vivo: el costo queda **visible y contable por tarea** en vez de escondido dentro de un turno. P3 -> **la mencion
  propone, no crea**. P4 -> **3D acotado a una pieza**, diferida y apagada por `prefers-reduced-motion`.
- **6 casos de uso, 30 criterios de aceptacion.** Los que importan: la pantalla **no se ofrece** sin version publicada
  (CA-01.2); el autocomplete ofrece **solo** lo que esa persona ya podia usar y una mencion forzada por texto **no
  resuelve** (CA-02.2/02.3); el hilo **se despierta igual si la tarea del agente falla** (CA-02.5, que es el defecto de
  `CierreTurno` que M27 encontro, escrito como criterio antes de implementar); despues de una mencion de configuracion
  hay **cero filas nuevas** en base (CA-03.1); el 3D **degrada en silencio sin WebGL** (CA-07.5).
- **Riesgo nuevo que no estaba en Discovery: R-03, la mencion como canal de escalada.** Una mencion es texto que escribe
  la persona y **el modelo no puede ser el que decida si corresponde**. Se cierra por los dos lados que el sistema ya
  usa: la mencion solo resuelve contra lo que esa persona ya podia usar, y el rol se chequea **al aplicar**.
- **Banderas cerradas.** Migracion EF: **si** (valor nuevo de `TipoTarea`). Prompt nuevo del nucleo: **si**, con suite
  propia mas la suite comun de seguridad. **Formato de contexto nuevo: el 6**, reutilizando el armado de plataforma
  (`ArmarPlataformaAsync`) - y con criterio explicito de que **no cambia el hash de ninguna tarea vieja** (CA-T.3).
- **Estado: Analisis cerrado.** Presupuesto **omitido** (producto propio, proyecto personal). Siguiente: Diseno.
- **Entrada de definiciones afectada:** `definiciones/1-analista-funcional.md` -> `M28` (ampliada con el Analisis).
