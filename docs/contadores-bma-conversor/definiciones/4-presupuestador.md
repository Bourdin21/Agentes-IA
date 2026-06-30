# Presupuestador — contadores-bma-conversor

Estado: CERRADO — Presupuesto retroactivo completado 2026-06-29

---

## Contexto

Sistema entregado y en producción desde 2026-06-25. Este documento es el presupuesto
retroactivo / de cierre que faltaba generar. Sirve como referencia de calibración histórica
para futuros proyectos similares (conversores Excel, parsers propietarios).

Cliente: Contadores BMA / SERVICIO TERAPIA RENAL S.A.  
URL producción: http://conversor.contadoresbma.com.ar

---

## Ajustes aplicados al cierre (2026-06-29)

- **Hosting:** sin costo adicional — el sistema corre sobre el servidor existente de
  www.contadoresbma.com.ar (plan ya pago por el cliente). No aplica mantenimiento STARTER.
- **Deploy/Config:** ajustado a 3h reales (superó la estimación original de 1h).
  Incluye configuración web, subdominio y primer deploy completo.
- **Documentación:** eliminada del presupuesto (sin costo al cliente).
- **Horas totales reales:** 8h (anclaje retroactivo).
- **Descuento referido:** 15% sobre el total bruto.

---

## Módulos funcionales identificados

### Módulo 1 — Motor de Conversión (convert.php)

**PASO 0 — Anclaje histórico**

Tipo más cercano: "módulo financiero o con lógica compleja" (M = 5-8h base).  
No existe referencia exacta de parser jerárquico en proyectos cerrados → incertidumbre media.  
Referencia usada: techo del rango "módulo financiero" (M = 8h) como punto de partida, ajustado
hacia abajo por ausencia de BD/EF (no hay migración, no hay estados persistentes).  
M base de referencia: 6.5h (promedio de rango 5-8h).

**PASO 1** — Motor de conversión Informe de Liquidación Bejerman → STR ENCABEZADO VALIDO.

**PASO 2** — Clasificación: módulo de exportación con lógica compleja + múltiples inputs.

**PASO 3 — Drivers de esfuerzo:**
- Parsing jerárquico de formato propietario (bloques por empleado, sin cabecera plana)
- Detección de 4 tipos de fila (empleado, SIPA, concepto, resumen) por heurísticas de col2
- 3 inputs independientes con formatos distintos (Informe, Grilla, Cubo)
- Pivot tall→wide sobre ~200 columnas de conceptos
- Lookup dinámico de códigos sobre template externo (fila 2)
- 14 columnas labeled con fórmulas especiales (TOTAL PROV, TOTAL CARGAS, Neto, etc.)
- Normalización: legajos con puntos/espacios, importes en formato argentino
- Post-proceso: eliminación automática de columnas todo-cero
- Estilos Excel aplicados: zebra, freeze, autosize cols 1-9, width fija cols 10+
- Caso edge documentado: empleado Barquet (licencia vacacional con estructura diferente)

**PASO 4 — M real (retroactivo):** 4h  
Distribución proporcional sobre 5h disponibles (8h totales − 3h deploy): ratio 7:2 original
→ 4h motor (80%) / 1h UI (20%). Ajuste a la baja respecto a la estimación original (7h)
confirmado por eficiencia IA en fase de implementación.

**USD cliente:** 4 × $16.80 = **USD 67.20** → USD 67

---

### Módulo 2 — UI Web (index.php + style.css)

**PASO 0 — Anclaje histórico:** ABM simple, M = 1-2h.

**PASO 1** — Pantalla de carga con 3 zonas drag-and-drop y descarga automática.

**PASO 2** — ABM simple (pantalla única).

**PASO 3 — Drivers:**
- 3 drop-zones independientes (Informe obligatorio, Grilla y Cubo opcionales) con badges de estado
- Spinner de procesamiento + descarga automática al completar
- CSS responsive (card, drop-zone, botón)
- Footer branding OlvidataSoft (isotipo SVG + texto HTML patrón ov-*)

**PASO 4 — M real (retroactivo):** 1h  
Distribución proporcional sobre 5h disponibles: 1h UI (vs 2h estimados originalmente).
Reducción confirmada por eficiencia IA en pantalla de una sola vista sin BD.

**USD cliente:** 1 × $16.80 = **USD 16.80** → USD 17

---

### Módulo 3 — Configuración web, dominio y deploy

**PASO 0:** Ajuste puntual elevado. M original estimado: 1h. M real: 3h.

**PASO 1** — Configuración de subdominio conversor.contadoresbma.com.ar, deploy FTPS con
vendor.zip sobre servidor Ferozo, .htaccess LiteSpeed y primer deploy verificado.

**PASO 2** — Ajuste puntual con complejidad mayor a la esperada.

**PASO 3 — Drivers del desvío (1h→3h):**
- Configuración del subdominio y document root en Ferozo (panel de hosting)
- Script FTPS Python con manejo de vendor.zip + extracción vía PHP ZipArchive
- Iteraciones de ajuste del .htaccess para PHP 8.3 en LiteSpeed
- Verificación end-to-end del primer deploy en producción

**PASO 4 — M real (retroactivo):** 3h

**USD cliente:** 3 × $16.80 = **USD 50.40** → USD 50

---

### Módulo 4 — Documentación

**Sin costo.** Incluida sin cargo al cliente.

---

## Tabla de estimación

| Módulo | M real (h) | USD bruto |
|---|---|---|
| Motor de conversión | 4 | 67 |
| UI web | 1 | 17 |
| Configuración web, dominio y deploy | 3 | 50 |
| Documentación | — | — |
| **Subtotal desarrollo** | **8** | **134** |
| Tokens IA | — | 100 |
| **Total bruto** | | **234** |
| Descuento referido 15% | | −35 |
| **Total neto** | | **USD 199** |

---

## PASO 8 — Sanity check del total

| Referencia | H base | Módulos | H/módulo |
|---|---|---|---|
| vinosefue (cerrado) | 30h | 16 | 1.9h |
| eleven-la-plata (cerrado) | 50h | 27 | 1.85h |
| **este proyecto** | **8h reales** | **3** | **2.67h** |

Ratio 2.67h/módulo vs 1.85-1.9h histórico = 1.40x → aceptable. La concentración del esfuerzo
en el motor de conversión (4h/8h = 50%) explica el ratio elevado por módulo. ✓

---

## PASO 9 — Cierre

**Paso A preliminar:** USD 134 (desarrollo) + USD 100 (tokens IA) = USD 234  
**Paso B ajustado:** USD 234 − USD 35 (descuento referido 15%) = **USD 199**

**Total a presentar al cliente: USD 199**  
**Hosting:** cubierto por el servidor existente de www.contadoresbma.com.ar. Sin cargo adicional.

---

## Riesgos y supuestos

- La estructura del Informe de Liquidación Bejerman Web es la documentada en mapeo-archivos.md.
  Si Bejerman cambia el formato de exportación en una versión futura, convert.php requerirá ajuste.
- El template STR ENCABEZADO VALIDO.xlsx está versionado en el servidor. Cambios de columnas
  por el cliente requieren subir el template actualizado.
- Columna 9 (Fecha Ingreso) vacía por decisión explícita del cliente; no es un bug.
- El sistema no tiene BD propia: no hay plan de migración de datos ni backup de datos aplicable.

---

## Cierre de calibración (real vs estimado)

El proyecto fue implementado en un sprint único el 2026-06-25.
No se registraron horas reales al momento del cierre. Estimación retroactiva.

Observación para futuros proyectos similares (parsers Excel propietarios):
- El motor de conversión con parsing jerárquico por bloques tiene alta complejidad de descubrimiento
  (estructura no documentada formalmente).
- El tiempo real de análisis + mapeo de columnas (ver mapeo-archivos.md) puede ser mayor al
  tiempo de implementación. Incluir explícitamente en el M un bloque de "discovery de formato".
