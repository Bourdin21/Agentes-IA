---
name: koi-e25-pendiente
description: KOI — la migración de datos E25 (importes Manual en la columna equivocada) quedó sin aplicar, y el deploy del código sin ella deja la vista anual mostrando el número equivocado
metadata:
  type: project
---

En KOI, la migración **E25_NormalizarImportesManuales** (sólo datos, commit `5a52462`, 2026-09-23) quedó **generada pero sin aplicar**. El script está en el scratchpad de esa sesión y lo corre el orquestador con backup previo.

**Why:** el código de ese commit unificó la lectura del importe de un concepto de gasto en `ImporteConceptoHelper` (Manual → `ImporteManual`). Los cuatro conceptos viejos afectados (CMV, Otros gastos, Honorarios, Publicidad) tienen el importe en `ImporteCalculado` con `ImporteManual = 0`, así que **hasta que el script no corra, el código nuevo hace que la vista anual empiece a mostrar el mismo número equivocado (optimista) que ya mostraba la mensual** para agosto 2025 y mayo 2026. Antes divergían; después del deploy-sin-script coinciden en el valor malo.

**How to apply:** antes de dar por cerrado cualquier trabajo sobre totales de gastos en KOI, confirmar si E25 ya se aplicó (buscar `20260923175638_E25_NormalizarImportesManuales` en `__EFMigrationsHistory`, o `Action = 'NormalizacionImporteManual'` en `AuditLogs`). Si todavía no, el deploy y el script van en la misma ventana. Decisión del dueño ya tomada: **las liquidaciones de esos dos meses no se tocan**, aunque después muestren un resultado peor que el que se repartió.

Ver también [[implementador-solo-commitea-repo-de-codigo]].
