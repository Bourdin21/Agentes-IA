# Memoria - Presupuestador

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Nota de alcance: proyecto interno, sin facturación a cliente externo

`crm-olvidata` es la herramienta propia de OlvidataSoft (owner = Joaquín Bourdin, el mismo estudio) — no hay un cliente externo al que cotizar. Esta ficha se usa igual, con la misma metodología PERT/horas del resto del dataset, **solo como estimación interna de esfuerzo** (para priorizar y para llevar registro de costo real de mantener el propio sistema) — no se aplica el aparato de precio al cliente (Tokens IA 25%, descuento de expansión agresiva, planes de mantenimiento): esas secciones de `27-presupuesto-parametros.instructions.md` son para Build/Merge de clientes de pago, no aplican acá.

### Sprint vigente: corrección de bugs/gaps de auditoría completa + 3 mejoras (2026-08-27)

**Regla de granularidad aplicada:** los 17 items son correcciones/ajustes sobre un sistema ya entregado y en producción (no módulos nuevos desde cero) — todos clasificados con los rangos de "Modificación sobre módulo existente" de `27-presupuesto-parametros.instructions.md`, no con los rangos de módulo nuevo (serían 5-10x más caros y no reflejan el esfuerzo real esperado, mismo patrón ya confirmado en vinosefue/labipac).

### WBS funcional vigente

| # | Item | Clasificación | M (h, caso probable) |
|---|---|---|---:|
| B1 | Truncado defensivo + catch ampliado (8 call sites) | Regla de negocio repetida | 1.5 |
| B2 | Rebalanceo por día individual, no por combinación de flags | Regla de negocio | 1.5 |
| B3 | Polling no pisa "última lectura" sin novedad real | Ajuste con cambio de contrato JS↔controller | 1.5 |
| B4 | Sincronizar `EtiquetasDeEvento` (6 literales faltantes) | Ajuste puntual | 0.5 |
| B5 | Bloquear rename de template con campañas activas | Regla de negocio | 1.0 |
| B6 | Unificar fórmula "Respuesta→Presupuesto" (3→1) | Regla de negocio + refactor a método compartido | 1.5 |
| B7 | Habilitar canal Referido en Create/Edit de Contacto | Campo existente expuesto en 2 formularios | 1.0 |
| G1 | Templates de catálogo con N placeholders dinámicos | Regla de negocio (mayor complejidad, alcance acotado) | 2.0 |
| G2 | Corrida manual respeta shuffle + marca `UltimaCorridaUtc` | Regla de negocio | 1.0 |
| G3 | `PrimerAnioGratis` disponible en alta de Cliente | Campo simple | 0.5 |
| G4 | `PresupuestoCotizadoUsd` editable a mano | Campo simple | 0.5 |
| G5 | Acciones AJAX de Chats devuelven JSON (2 acciones) | Regla de negocio | 1.5 |
| G6 | `MarcarTodosLeidos` con `ExecuteUpdateAsync` | Ajuste puntual | 0.5 |
| G7 | Aviso + conteo de huérfanos al eliminar industria | Regla de negocio (2 controllers) | 1.5 |
| M-A | Constante de dominio compartida (mejora) | Refactor cross-archivo | 1.5 |
| M-B | Reclasificación asistida de huérfanos (mejora) | ABM intermedio menor | 2.0 |
| M-C | Endpoint `/Bot/Salud` de diagnóstico (mejora) | UI + agregación nueva | 2.5 |
| | **Total M base** | | **22.0 h** |

### Estimaciones PERT por item

No se desglosa O/P por item individual (17 items pequeños y muy acotados, mismo criterio ya usado en rondas de fixes de vinosefue/labipac) — PERT a nivel de sprint: O=15h (todo sale a la primera), M=22h (caso base de la tabla), P=32h (si alguno de los items de mayor incertidumbre —G1, M-B, M-C— requiere una vuelta extra).
PERT = (O + 4M + P) / 6 = (15 + 88 + 32) / 6 = **22.5 h**.
Con contingencia 20% (fórmula vigente, horas facturables = M/2.5 × 1.20): **10.56 h facturables** sobre el M base de 22h.

### Tasa vigente y contingencia aplicada

USD 35/h (tasa vigente del estudio) — usada acá solo como referencia de costo interno equivalente, no como cobro a cliente. Contingencia 20% ya incluida en la fórmula de horas facturables (no se aplica dos veces).

### Resumen economico (referencia interna, no se cobra a cliente)

- M base total: 22.0 h
- Horas facturables (M/2.5 × 1.20): 10.56 h
- Costo interno equivalente (10.56 h × USD 35/h): **≈ USD 370**
- Costo interno de IA por consumo (Opus, ver `27-presupuesto-parametros`, USD 4/h estimado sobre horas facturables): 10.56 h × USD 4/h ≈ USD 42 — dato de trazabilidad interna únicamente, no afecta ningún precio (no hay cliente).
- **No aplica:** Tokens IA al cliente, descuento de expansión agresiva, descuento por volumen, plan de mantenimiento — todos exclusivos de Build/Merge de clientes de pago.

### Calibraciones historicas usadas

- vinosefue "compras al proveedor" (2026-07-03) y labipac SESIÓN 3 (2026-07-08): confirman que rondas de fixes/mejoras sobre sistema ya entregado, clasificadas con "Modificación sobre módulo existente", sobreestiman 4-7x contra el real — mismo criterio aplicado acá (M base de 22h, no los rangos de módulo nuevo que hubieran dado 60-100h+ para 17 items).
- No hay cierre real propio de crm-olvidata todavía (primera vez que este proyecto pasa por el flujo formal) — el M base queda como primera referencia propia para calibrar futuras rondas de fixes de este mismo proyecto.

### Cierre estimado vs real (Cierre de calibración — 2026-08-27)

**Sprint cerrado y deployado a producción el mismo día.** Estimado: 22.0 h M base / 10.56 h facturables. Real: medido como tiempo de ejecución de los 4 subagentes que hicieron el trabajo (2 corridas de Implementador + 2 de QA — la primera de Implementador se cortó por watchdog a mitad de camino y se retomó, sumando ambas):

| Corrida | Duración real |
|---|---:|
| Implementador (continuación tras corte por watchdog) | 18.4 min |
| QA (pasada completa de los 17 items) | 27.0 min |
| Implementador (fix CRM-007/010/012 post-QA) | 12.2 min |
| QA (re-verificación acotada) | 13.1 min |
| **Total tiempo de agente** | **≈ 70.7 min ≈ 1.18 h** |

Sumando el tiempo propio de orquestación (Discovery→Presupuesto, deploy, documentación, coordinación entre corridas) — no medido con precisión pero del orden de 1-1.5 h adicionales — el total real ronda **2.5-3 h**.

**Ratio PERT-contingencia/real ≈ 7.5x-9x** — en línea con el extremo superior del dataset del estudio (vinosefue 7.07x es el record histórico) y coherente con la regla ya documentada en `27-presupuesto-parametros.instructions.md`: correcciones sobre un sistema ya entregado, con IA asistida, sobreestiman sistemáticamente contra los rangos de PERT tradicional. Primer cierre real propio de `crm-olvidata` — queda como ancla para calibrar la próxima ronda de fixes de este mismo proyecto (ver regla de "segunda ronda sobre el mismo módulo" — de aplicarse un criterio equivalente, la próxima estimación de un sprint de fixes similar en este proyecto debería anclarse más cerca de 3-4h reales que de 22h).

**Desvíos por causa, no por item** (los 17 items individuales no se cronometraron por separado):
- El corte por watchdog de la primera corrida de Implementador no se debió a la complejidad del trabajo sino a un problema de infraestructura de la sesión — no es una señal de que B3 en particular haya sido más costoso que el resto.
- El re-trabajo post-QA (CRM-007/010/012) fue necesario porque 2 items nuevos (G7/M-B, y B7) introdujeron un vocabulario de datos (`IndustriaCatalogo.Nombre` vs `ClaveRubro`) que no estaba explícito en el Diseño/Arquitectura original — un gap de especificación, no un error de implementación. Para el futuro: cuando un item toca `Contacto.Rubro`, la Arquitectura debería declarar explícitamente cuál es el vocabulario canónico antes de pasar a Implementación.

### Gate de aprobación

Gate cliente = Joaquín, mismo rol de owner y de "cliente" en este proyecto interno. Ya autorizado explícitamente en el pedido original ("arreglar todo lo detectado como bug y gaps, proponer 3 mejoras") — no requiere una segunda confirmación de precio (no hay precio a confirmar, es trabajo propio). Se pasa a Implementación.

## Historial de ajustes
- 2026-08-27: Primera ficha de presupuesto real de este proyecto (plantilla nunca se había completado — todo el trabajo previo fue ad-hoc en sesión de chat). Sprint "corrección de bugs/gaps + 3 mejoras": 17 items, 22.0 h M base, 10.56 h facturables, ≈USD 370 de costo interno equivalente (sin cobro a cliente, proyecto propio del estudio). Gate aprobado por el pedido explícito del cliente/owner.
- 2026-08-27: Cierre de calibración. Real ≈2.5-3 h (1.18 h de ejecución de subagentes + orquestación), contra 22.0 h M base estimadas — ratio ≈7.5x-9x, nuevo techo del dataset del estudio. Sprint deployado a producción el mismo día, QA final GO. Causa del único desvío real (retrabajo post-QA): vocabulario de `Contacto.Rubro` no declarado explícitamente en Arquitectura — regla derivada para la próxima vez.
