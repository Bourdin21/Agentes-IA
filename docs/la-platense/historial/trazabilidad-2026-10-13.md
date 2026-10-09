<!-- Archivado de docs/la-platense/trazabilidad.md el 2026-10-09 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# trazabilidad - 2026-10 (1 bloques archivados)

- 2026-10-08 — `LP-123` aplicado, `LP-122` NO CERRADO (implementacion, pase 2 sobre `LP-119`)

---

### 2026-10-08 — `LP-123` aplicado, `LP-122` NO CERRADO (implementacion, pase 2 sobre `LP-119`)

- **`LP-123` cerrado:** `ArnesReconciliacionTx` contaba los exitos de `FacturarAsync` por `Success`
  sin excluir `!EsAviso`, y `CreateAviso` deja `Success = true` a proposito -> "3 de 3" donde hubo 1
  emision y 2 avisos. Corregido y con la regla anotada en el lambda; **vuelve a 153/153, exit 0**.
  Barrido de los 6 metodos que pueden devolver aviso contra todos los `tools/`: era el unico conteo
  afectado (`ArnesLote1Guardas` ya lo resolvia con competidores distinguibles, `ArnesSeisSitiosRestantes`
  cuenta los avisos como exito a proposito, `ArnesDevoluciones` verificado por ejecucion 63/63).
- **`LP-122` NO cerrado, y el interino no puede cerrarlo.** La ventana paso de **dia de negocio** a
  **10 segundos** (`FacturacionParcialService.VentanaDobleSubmitSegundos`, publica y documentada), con
  familia 10 nueva en el arnes: control negativo (la misma tanda pasada la ventana emite y **no queda
  nada sin facturar**), control positivo (dentro de la ventana el doble clic colapsa) y **el piso
  MEDIDO** (la emision tarda 23 ms, margen 440x). Eso arregla el `LP-122` humano ("facturo 2 ahora y 2
  a la tarde").
- **Pero el fixture de `ArnesNotaCredito` hace sus dos tandas en MENOS DE UN SEGUNDO.** Medido: con la
  ventana en **1 segundo** sigue colapsando (62/1, `facturas #61 y #61`). **Ningun valor de ventana
  sirve**, porque los dos criterios de aceptacion son mutuamente excluyentes: `LP-119` exige que N
  POST identicos EN SERIE dejen uno, y `LP-122` exige que una segunda tanda identica sub-segundo
  despues emita. **Es el mismo evento observable** — solo lo separa un dato que identifique el RENDER
  (el nonce del gate pendiente).
- **El atajo que NO hay que tomar:** excluir de la clave los comprobantes ya acreditados por una NC
  pondria `ArnesNotaCredito` en 63/0 y dejaria `LP-122` abierto en su forma pura (sin NC de por
  medio). Cumple la letra del criterio y no el defecto.
- **Tres correcciones de QA aplicadas:** `LP-124` declarado (el atajo lo protege un
  `MySqlException: Deadlock found`, no la guarda — se corrigio la afirmacion, no el codigo); `9.16` ya
  no afirma la direccion de la NC (la lleva `9.22`) y **conserva `[DISCRIMINA]`** porque la tumban
  M1/M4/M6/M7; la rama del soft delete declarada **defensa en profundidad** (cero escritores de
  `ComprobanteAfip.DeletedAt`, re-contado).
- **Evidencia:** build `--no-incremental` 0 errores / 9 advertencias (8 `NU1902` + 1 `CS0114`);
  `ArnesVentaSinFacturaYParcial` 107 -> **111 OK / 0**; 11 mutantes, los dos de la ventana
  (`M10`, `M11b`) tumban exactamente `10.1`/`10.2`; `md5` del Service identico al pre-mutacion.
- **Cero migraciones.** `appsettings.json`, `Seed` y `SeedData.cs` sin tocar. **Sin commit.**
- **Estado: `LP-123` aplicado pendiente de re-verificacion; `LP-122` ABIERTO esperando el gate del
  nonce; `LP-124` declarado y no arreglado.** Ningun defecto marcado como cerrado.
