# Memoria - Presupuestador

## Proyecto: olvidata-agentes-multirubro
## Ultima actualizacion: 2026-09-14

## Definiciones vigentes

### Estado de la etapa
**Presupuesto OMITIDO por decisión de Joaquín (2026-09-14): "Saltear el presupuesto porque es un proyecto personal".** Producto propio de Olvidata Soft sin cliente externo: no hay precio, tasa, contingencia ni Tokens IA a cotizar. El gate "Implementación requiere presupuesto aprobado por el cliente" queda cumplido por la dispensa explícita del cliente (Joaquín).

### WBS funcional vigente
Sin WBS valorizada. Referencia de alcance: plan funcional por etapas de `3-arquitecto-mvc.md` (Base de organización → Áreas → Miembros + backoffice → Cartera → Tareas por rol).

### Estimaciones PERT por item
No aplica (omitido).

### Tasa vigente y contingencia aplicada
No aplica.

### Resumen economico (con Tokens IA como item individual)
No aplica: proyecto personal sin cotización.

### Calibraciones historicas usadas
Ninguna.

### Cierre estimado vs real (si disponible)
**Cierre M4b Configurador de reglas (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent, incluye borrador del prompt del configurador) | — | ~72 min de agente, 257 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (sin auto-fix) | — | ~29 min de agente, 104 acciones | n/a | sin estimado |

Sin cambios de alcance. **Lecciones M4b:** (1) el simulador con guion por palabras clave permitió probar los 4 tipos de propuesta sin cargar datos: incluir guiones de herramientas desde el diseño en toda feature con tool use; (2) la verificación de contraste en el implementador funcionó (0 defectos en lo nuevo) pero destapó deuda global del theme (OLV-004): conviene un ítem de mantenimiento propio; (3) la implementación de features con herramientas del modelo tiene costo similar a M4 (~70 min): estimar tool use + permisos en segundo plano como complejidad alta.

**Cierre M4 Agentes de la organización (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (incluye cambio de alcance en el gate de Diseño: sin revisión del Director) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~70 min de agente, 300 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (subagent, 1 auto-fix CSS) | — | ~39 min de agente, 85 acciones | n/a | sin estimado |

Cambio de alcance: se sacó la revisión del Director (reduce alcance). **Lecciones M4:** (1) M4 fue la feature más grande hasta ahora (implementación ~2x M3b): features con entidad nueva + versiones + integración con constructor/tareas/reglas/núcleo/licencias deben estimarse como varias features; (2) el test golden de hash calculado con el código previo evitó romper tareas existentes: hacerlo obligatorio en todo cambio del constructor de contexto; (3) tercera vez que QA encuentra contraste en tema oscuro (OLV-001/002/003): mover la verificación de contraste al checklist del implementador como paso obligatorio.

**Cierre M3b Seguir conversando (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (conversación con Joaquín, incl. definición de tareas programadas → M12) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~37 min de agente, 130 acciones | n/a | sin estimado |
| QA en navegador con modelo simulado (subagent, 1 auto-fix CSS) | — | ~32 min de agente, 98 acciones | n/a | sin estimado |

Sin cambios de alcance. **Lecciones M3b:** (1) el proveedor de modelo simulado solo en Development permitió QA de punta a punta sin costo: incluirlo desde el inicio en toda feature del motor; (2) la normalización de la conversación para la API fue la parte crítica y se resolvió con tests de casos borde antes de UI: mantener ese orden; (3) componentes visuales nuevos siguen fallando primero en tema oscuro (OLV-001 en M2, OLV-002 en M3b): sumar verificación de contraste en tema oscuro al checklist del implementador; (4) EF InMemory no es transaccional: la atomicidad se prueba contra MySQL real.

**Cierre M3 Reglas (2026-09-14)** — sin estimación (presupuesto omitido); desvío no calculable. Esfuerzo real registrado:

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (conversación con Joaquín, incl. pedidos nuevos N-01/N-02 y ajustes de simplificación) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent) | — | ~52 min de agente, 160 acciones | n/a | sin estimado |
| QA en navegador (subagent, sin auto-fix) | — | ~28 min de agente, 89 acciones | n/a | sin estimado |

Cambios de alcance durante la ejecución: ninguno en M3 (N-01, N-02, M3b y reglas sugeridas se enviaron al roadmap). Comparado con M2: implementación ~20% más larga (constructor de contexto + cambio de firma del motor) y QA más corta sin defectos, confirmando que reutilizar helpers/vistas de M2 bajó el costo de UI.

**Lecciones M3:** (1) cambiar contratos del motor (`SolicitudModelo`) arrastra tests de M1: estimarlo como ítem propio; (2) el proveedor MySQL generó bien el check constraint esta vez: la lección de M2 se mantiene como verificación, no como trabajo manual fijo; (3) funcionalidades con prompts dejan una validación que solo se cierra con corrida paga: presupuestarla explícitamente como ítem "validación con modelo real".

**Cierre M2 Organización (2026-09-14)** — sin estimación previa (presupuesto omitido), por lo que no hay desvío calculable. Se registra el esfuerzo real para calibrar futuras features de este producto.

| Item | Estimado (h) | Real | Desvío | Causa principal |
|---|---:|---:|---:|---|
| Etapas 0–3 (análisis, diseño, arquitectura; conversación con Joaquín) | — | no registrado en horas humanas | n/a | sin estimado |
| Implementación (subagent implementador) | — | ~43 min de agente, 148 acciones | n/a | sin estimado |
| QA en navegador + 2 auto-fix (subagent QA) | — | ~32 min de agente, 125 acciones | n/a | sin estimado |
| Revisión humana | — | no registrada | n/a | — |

Desvío total: no calculable. Cambios de alcance durante la ejecución: ninguno (solo decisiones menores del implementador ante ambigüedades, documentadas en `5-implementador.md`).

**Lecciones aprendidas (para estimar las próximas features M3–M12):**
- `MySql.EntityFrameworkCore 10.0.9` ignora `stored: true` en columnas computadas y exige orden manual de índices con FK: sumar margen fijo en toda migración con columnas generadas, check constraints o reemplazo de índices sobre FKs.
- Cambios transversales de sesión/autorización (middleware, resolvedor, policies) arrastran ajustes en tests existentes y en el hub de SignalR: tratarlos como ítem propio, no como parte de una pantalla.
- Reutilizar literal (formularios, Select2, bajas AJAX de la-platense) redujo trabajo de UI pero QA encontró huecos de tema oscuro en componentes portados: incluir verificación de tema oscuro de cada componente portado.
- Features con reglas de aislamiento/invariantes (último Director, IDOR) justifican el tiempo de QA con ids manipulados y concurrencia real: mantenerlo en el alcance de QA.

**Ajustes recomendados:** registrar horas humanas de revisión por feature desde M3 para tener base real; si en el futuro se presupuesta este producto, usar M2 como referencia de complejidad "ABM x3 + cambio transversal de sesión + migración con SQL manual".

**Acción obligatoria para el próximo presupuesto (si se hace):** anotar al cierre de cada etapa la duración real (agentes + revisión humana).

## Historial de ajustes
- 2026-09-14: Etapa omitida por decisión de Joaquín (proyecto personal). Arquitectura M2 aprobada implícitamente al pedir saltear el presupuesto.
- 2026-09-14: M3 Reglas — presupuesto omitido (proyecto personal, criterio vigente). Implementación habilitada tras aprobar Arquitectura M3.
- 2026-09-14: Cierre de calibración M2 (etapa 8): esfuerzo real registrado sin estimado; lecciones sobre migraciones con MySql.EntityFrameworkCore, cambios transversales de sesión y tema oscuro de componentes portados.
