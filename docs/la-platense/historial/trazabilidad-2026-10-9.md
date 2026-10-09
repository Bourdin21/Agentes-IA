<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-08 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (1 bloques archivados)

- 2026-10-07 (14) - qa (CR-04 plan de echeqs + cierre de los 5 partes LP-044..LP-048: GO CONDICIONADO - todos los criterios de CR-04 en PASS, 3 de 5 partes cerrados, 1 defecto nuevo low; con esto los 5 CR quedan funcionalmente completos)

---

### 2026-10-07 (14) - qa (CR-04 plan de echeqs + cierre de los 5 partes LP-044..LP-048: GO CONDICIONADO - todos los criterios de CR-04 en PASS, 3 de 5 partes cerrados, 1 defecto nuevo low; con esto los 5 CR quedan funcionalmente completos)

- **Alcance**: `CR-04` (plan de echeqs 0/30/60/90/120 — financiero, lote único) + re-verificación de `LP-044`, `LP-045`, `LP-046`, `LP-047`, `LP-048`. Rama `entrega-1-migracion`, commits `57f06ea`..`e2da786`.
- **Veredicto: GO CONDICIONADO.** Ningún bloqueante de producción: lo que queda abierto son dos comentarios, un arnés y una línea de reporte.
- **Fixture**: `laplatense_gate_cr04` = clon de `laplatense_dev` + las 4 migraciones que faltaban (14 → 18). Se midió sobre el fixture **con historia**, no sobre base virgen. El repo del sistema no se tocó (todo sobre `git archive` en el scratchpad).
- **PF19 con el plazo 0, que era la trampa**: plan de 5 plazos sobre una compra de $100.000 → 5 `LineasEcheq` + 5 `PagosOrdenCompra` **todos `Pendiente`**, incluido el de $20.000 que **vence hoy**, con `CajaMovimientos` 9 → 9 y `MovimientosCCProveedor` 0 → 0. **No salió un peso al crear el plan.**
- **Migración `CR04_PlanDeEcheqs`: aditiva pura CONFIRMADA** operación por operación (1 `CreateTable` + 3 `CreateIndex`, `Down` = 1 `DropTable`, cero `AddColumn`/`AlterColumn`/`Sql()`).
- **Partes cerrados: `LP-046`, `LP-047`, `LP-048`.** `LP-048` cierra porque `ArnesSeisSitiosRestantes` ahora da 32/32/0 **sobre el clon de dev**, el fixture donde antes daba 31/1.
- **Partes que NO cierran: `LP-044` y `LP-045`** — cada uno dejó viva una instancia de la misma afirmación falsa que vino a borrar. `LP-044`: `InteresesTarjeta.cshtml` línea 233 sigue diciendo "Un `<form>` hijo de `<tr>` lo saca el parser". `LP-045`: `OrdenCompraService.EtiquetaEstado` dice "Sin `_ =>`" dos líneas arriba de un `_ => estado.ToString()`.
- **Defecto nuevo `LP-049` `low`**: el barrido de `LP-048` fue dentro del archivo y no cross-archivo; `ArnesEntrega3Item4c` tiene la misma forma en su afirmación de limpieza (cuenta agregados globales). Par de control: una sola orden de compra ajena lo pasa de `TODO OK` a `1 FALLA`.
- **La explicación del build 8-vs-9 es falsa**: son 9, y la novena es `CS0114` en `HomeController.cs(38,26)`, una advertencia **de código** preexistente de Entrega 1 — no una `NU1902` que oscile con el restore.
- **Incidente de `dev` verificado de forma independiente**: 112.485 productos, 2.993 clientes, 0 órdenes de compra, 14 migraciones, sin `CandadosPeriodoCaja`. Las 4 filas `ZZ%` son catálogo legado real del 2026-08-21, no residuo. La guarda nueva aborta con **exit 2** contra `dev`, probada por ejecución.
- **Barrido de la misma forma en el resto del tooling**: los 5 `Arnes*` leen el entorno y tienen guarda de cadena. **`tools/MigracionCatalogo` no**: `laplatense_dev` hardcodeado, cero lectura del entorno, y su guarda de "catálogo vacío" no cubre los 3 modos correctivos, que exigen catálogo cargado. Riesgo 1 de liberación.
- **Desviación del flujo 14 (pantalla propia en vez de bloque): ACEPTADA.** La puerta está oculta y aparece al elegir *Cheque electrónico*; la pantalla propia conserva compra + proveedor + total y tiene 3 links de vuelta. El operador no pierde el contexto.
- **Hallazgo de cobertura del instrumento**: `3.10` está marcada `[COBERTURA]` y **sí discrimina** — el mutante `M9` de QA (la unicidad devuelta a consultar `LineasEcheq`) la tumba, 48/49. Es la afirmación del hallazgo propio del implementador, y es la única que su relabel no midió.
- **Líneas base reproducidas** (afirmaciones evaluadas, sobre el clon de dev): `ArnesPlanEcheqs` 49/49/0 + reparto 24/21/4, `ArnesTarjetaYTransferencia` 41/41/0, `ArnesSeisSitiosRestantes` 32/32/0 + 2 NM, `ArnesReconciliacionTx` 153/153/0.
- Detalle completo en `definiciones/6-qa.md` (bloque v19). Catálogo cross-proyecto: `LP-049` agregado.
