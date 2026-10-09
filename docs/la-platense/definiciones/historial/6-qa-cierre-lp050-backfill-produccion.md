# Historial de QA - La Platense

Bloque archivado desde `6-qa.md` el 2026-10-08 por curaduria a mano (39 seccion 6: el techo se sostiene archivando, no reescribiendo). El texto esta completo y sin resumir.

---

# Cierre de `LP-050` — ensayo del backfill contra los datos reales de producción (2026-10-07, rama `entrega-1-migracion`, HEAD `fcfa077`)

## **`LP-050` CERRADO. GO para el deploy, con una condición dura: la base y el sitio en la MISMA ventana.**

Contexto fresco: no se leyó la transcripción del implementador. Se leyeron sus artefactos (los 5 archivos
`ensayo-lp050_*`), y **cada número se volvió a medir**. Repo del sistema en read-only: `git status --porcelain`
limpio al cerrar (sólo `?? .claude/`, que ya estaba al abrir la sesión y no es mío).

### Bases usadas, declaradas para que no se confundan

| Base | Rol en esta corrida | Acceso |
|---|---|---|
| `db_a7251f_laplaten` @ `mysql8001.site4now.net` | **producción** — verificación de que sigue intacta | **sólo SELECT** |
| `laplatense_ensayo_prod` (local) | copia viva ya migrada que dejó el implementador | sólo SELECT |
| `laplatense_qa_rollback` (local) | **restore del snapshot hecho por mí**, baseline independiente | creada y **borrada** por mí |
| `laplatense_dev` (local) | control, no se tocó | sólo SELECT (18 migraciones) |

### Criterio de cierre de `LP-050`

| Criterio | Estado | Evidencia observada |
|---|---|---|
| Ningún `CajaMovimientos` queda con `MedioPago` NULL tras migrar | **PASS** | `SELECT COUNT(*) ... WHERE MedioPago IS NULL` → **0** sobre `laplatense_ensayo_prod` (1 fila total) |
| El valor backfilleado es **semánticamente** correcto, no sólo no-NULL | **PASS** | fila `OrigenTipo='Gasto'` → `MedioPago=4`; `Gasto.FormaPago=2`; enums: `FormaPagoGasto.Transferencia=2` → `MedioPagoCaja.Transferencia=4` |
| El `UPDATE` del `LIKE`/`ELSE NULL` filtra por `OrigenTipo IN ('Venta','CobroCC')` | **PASS** | línea 158 de `LedgerCaja_Identidad_MedioPago_AnulacionVenta.cs`, leída textual |
| Producción no tiene filas de esos `OrigenTipo` | **PASS** | `SELECT OrigenTipo,Tipo,COUNT(*) ... GROUP BY` en prod → una sola fila: `Gasto / 2 / 1` |
| Ninguna fila perdida, ningún valor preexistente cambiado | **PASS** | **hash propio**, 28/28 tablas idénticas (conteo + `MD5` sobre columnas preexistentes) contra **mi** restore del snapshot |
| Las 4 columnas nuevas de `CajaMovimientos` presentes con default correcto | **PASS** | `EsReversion NO/0`, `MedioPago YES/NULL`, `PagoVentaId YES/NULL`, `UsuarioId YES/NULL` |
| Producción sigue intacta (8 migraciones, sin columnas nuevas) | **PASS** | consulta directa: 8 migraciones, última `20261005151611_D9_...`, **0** de las 4 columnas, 29 tablas |
| El snapshot de rollback es **restaurable** | **PASS** | restaurado en `laplatense_qa_rollback` en **17 s**, exit 0 → 8 migraciones / 29 tablas / 112.485 productos / 2.990 clientes |

### La corrección de la premisa del parte (el dato era mío y era falso)

`LP-050` decía que producción tenía **"5 ventas y 4 movimientos de caja"**. Medido sobre el dump y confirmado
contra prod: **0 ventas y 1 movimiento de caja**. El parte citaba ese número como *"verificado por consulta
directa"* y no lo estaba. Volumen real de prod: **112.485 productos, 2.990 clientes, 85 proveedores, 1 gasto**.

**Y el motivo del PASS no es el que el parte suponía.** El `UPDATE` heurístico no acierta: **no se ejecuta sobre
ninguna fila**. No hace falta `UPDATE` correctivo ni migración extra — se confirma la conclusión del implementador.

### La condición que invalidaría el GO — y no es la que el parte suponía

El parte (y el brief) asumían: *"si producción empieza a vender antes del deploy, ese `UPDATE` pasa a tener filas
reales y el ensayo deja de valer"*. **Medido en el código viejo `628cb7a`, eso es falso**, y por tres hechos:

1. El enum `MedioPago` de entonces es `Efectivo=1, Debito=2, CreditoCuotas=3, CuentaCorriente=4`. No existe `Transferencia=5` (es de CR-05, código nuevo).
2. `CuentaCorriente` está **excluida** del posteo a caja (`VentaWorkflowService.cs:491`, `p.MedioPago != MedioPago.CuentaCorriente`).
3. El único sitio que postea caja por venta escribe la descripción con el sufijo del medio entre paréntesis (`:497`). La descripción *sin* sufijo del `:482` es la del movimiento de **cuenta corriente**, no la de caja.

O sea: las 3 ramas del `CASE` (`Efectivo`/`Debito`/`CreditoCuotas`) **cubren todo lo que el código viejo puede
emitir**, y una venta hecha *antes* de migrar se backfillearía bien. Además el código viejo **no tiene ningún
posteo de caja con `OrigenTipo='CobroCC'`**: sus únicos escritores de caja son `GastoService` (egreso + reversión)
y `VentaWorkflowService`.

**La ventana peligrosa es la otra: DESPUÉS de migrar y ANTES de deployar el sitio.** Ahí el backfill ya corrió y
no vuelve a correr nunca, y el modelo EF viejo no conoce las columnas nuevas, así que las omite en el `INSERT`:

- todo `CajaMovimientos` que escriba el código viejo queda **`MedioPago` NULL de forma permanente** → `LP-050` reabierto en producción, invisible;
- una **reversión de gasto** del código viejo entra con `EsReversion=0` cuando corresponde `1` (el paso 1 del backfill la habría marcado, pero ya corrió);
- un **proveedor nuevo** entra con `Moneda=0`, que **no es un valor válido** de `MonedaProveedor{Peso=1,Dolar=2}` — el `UPDATE Proveedores SET Moneda=1 WHERE Moneda=0` de la línea 323 arregló los 85 existentes y tampoco vuelve a correr.

**Condición que invalida el GO, en una línea: cualquier movimiento de caja, venta, gasto o alta de proveedor
hecho por el código viejo DESPUÉS de aplicar las migraciones.** No "antes".

### ¿Es seguro aplicar las 10 migraciones antes de deployar el sitio?

**Estructuralmente sí — no se rompe. Funcionalmente no — se ensucia en silencio.** Medido columna por columna
sobre las **31 columnas nuevas en tablas preexistentes**:

- **NOT NULL sin default: NINGUNA.** Las 5 NOT NULL tienen default real a nivel BD, verificado en `information_schema.columns`: `CajaMovimientos.EsReversion=0`, `Productos.PrecioVentaDesactualizado=0`, `Proveedores.Moneda=0`, `Proveedores.SaldoInicial=0.00`, `Ventas.Facturar=1`. Las otras 26 son nullable con `DEFAULT NULL`.
- **`sql_mode` de producción = `STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION`.** Importa: con ese modo, una columna NOT NULL sin default habría hecho **fallar** el `INSERT` del código viejo. No falta ninguna, así que no falla.
- **Índice único nuevo sobre tabla preexistente: uno solo, `IX_Proveedores_CUIT`** (`non_unique=0`). Convive con **85 filas de `CUIT` NULL** — MySQL admite N NULLs en un índice único, y está probado por ejecución: la migración corrió sobre esas 85 filas. El código viejo no escribe `CUIT`, así que nunca colisiona.
- **FK nueva sobre tabla preexistente: una, `FK_PagosVenta_Tarjetas_TarjetaId`**, y es **nullable** → el código viejo inserta NULL y pasa.

**Veredicto: no es "sí" ni "no", es un condicional.** Se puede migrar la base antes del sitio **si y sólo si no
hay actividad de caja / ventas / gastos / altas de proveedor en el medio**. Y producción **está activa**: su único
movimiento de caja es de ayer (`CreatedAt 2026-10-06 19:31:41`, idéntico en prod y en el snapshot → sin actividad
nueva desde que se tomó). **Recomendación: base y sitio en la MISMA ventana.** Migrar ahora para destrabar el
bloqueo de FTP cambia un problema de deploy, que es visible y reversible, por uno de integridad de datos que es
silencioso e irreversible (ningún `Down` revierte los backfills). Si por fuerza mayor hubiera que separarlos: que
la ferretería **no opere** entre las dos mitades.

### Volumen y duración

10 migraciones en **14 s** sobre el volumen real. Los `UPDATE` del backfill tocan **86 filas** (85 `Proveedores`
+ 1 `CajaMovimientos`), verificado por conteo; los **112.485 productos no entran en ninguno**. **No hace falta
ventana de servicio por duración** — la ventana que hace falta es por las razones de arriba, no por el reloj.

### Trampas de medición propias (declaradas)

1. **Mi primer `diff` de hashes dio "sin diferencias" — y era un falso PASS.** Los dos lados habían fallado
   **idéntico** con `ERROR 1064` de sintaxis SQL, así que el `diff` comparó dos mensajes de error iguales. Lo
   destapó imprimir la salida en vez de creerle al `diff`. **Un `diff` vacío no es evidencia de igualdad si no se
   verificó que los dos lados produjeron algo.** Rehecho por tabla en Python → 28/28 real.
2. **`information_schema.table_rows` mintió en tres tablas**: dio `gastos=0`, `productos=111.453`,
   `modelos=0`. El conteo real es **1 / 112.485 / 1**. En InnoDB `table_rows` es un **estimado**. El archivo
   `ensayo-lp050_chk_copia.txt` del implementador tenía los números correctos; el estimado era la mentira.
3. **Dato heredado del brief que se cae: las "6 tablas nuevas" son 15** — `aumentosmasivosprecio`,
   `candadosperiodocaja`, `comprobantesafip`, `comprobantesafipitems`, `interesestarjetacuota`, `itemspresupuesto`,
   `lineasecheq`, `movimientosccempleado`, `movimientosccproveedor`, `movimientosstock`, `ordencompraitems`,
   `ordenescompra`, `pagosordencompra`, `presupuestos`, `tarjetas`. Medidas por diferencia de conjuntos
   (`comm` entre el listado de la copia y el de prod), y el sentido inverso da **0**: ninguna tabla de prod
   desapareció.

### Partes de defecto

- **De la corrida anterior: `LP-050` `major` → CERRADO.** Criterio de re-verificación cumplido con las 8 filas de la tabla de arriba, arrancando en FAIL.
- **`LP-051` `trivial`** — fuera del alcance de este lote, sigue **ABIERTO**.
- **Emitidos en esta corrida: NINGUNO.** Catálogo cross-proyecto sin cambios: **192 ítems**, sin duplicados.

No se emite parte por la ventana código-viejo/esquema-nuevo: **no es un defecto del sistema**, es una restricción
de secuencia del deploy, y queda como condición del GO y en el checklist.

### Cobertura del catálogo cross-proyecto

| Ítem | Aplica | Resultado | Nota |
|---|---|---|---|
| `LP-050` (backfill probado contra una base con cero filas del tipo afectado) | sí | **PASS → CERRADO** | El backfill no tenía trabajo que hacer en prod, y eso se verificó, no se supuso |
| `KOI-012` (migración de datos con ids a mano mueve plata al concepto equivocado) | sí | **PASS** | Mapeo `FormaPagoGasto→MedioPagoCaja` verificado contra los dos enums, no sólo contra no-NULL |
| `GAN-002` (backfill que no reconstruye un campo para filas históricas) | sí | **PASS** | El `ELSE NULL` existe pero no alcanza ninguna fila; las 3 ramas cubren el enum viejo completo |
| `MH-001` (familia: enum con default 0 que no es valor válido) | sí | **PASS con residuo** | `Proveedores.Moneda` default `0` inválido; corregido para los 85 existentes, reaparece si el código viejo da de alta en la ventana |

### Validación de reglas cross-proyecto

`6-qa.md` declaraba **2026-10-07** (hoy). Verificado:
`git log --since=2026-10-07 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
→ **sin commits**. El catálogo sigue en **192 ítems** con `LP-050` y `LP-051` presentes en `cat_resumen.txt`.
**Ninguna regla nueva ni modificada desde la última validación.**

### Riesgos de liberación

1. **La ventana código-viejo / esquema-nuevo (el único riesgo real que queda).** Mitigación: base y sitio en la misma ventana, o la ferretería sin operar en el medio.
2. **El rollback es sólo el snapshot.** Ningún `Down` revierte los backfills: volver atrás es **restaurar**, no desmigrar. Probado restaurable en 17 s, así que es un camino de vuelta válido — pero pierde todo lo que se haya escrito después de las 09:43 del 2026-10-07.
3. **FTP/Web Deploy con `530`** — bloqueante del deploy del sitio, lo resuelve Joaquín, no es un defecto. Agrava el riesgo 1: es justo lo que tienta a separar las dos mitades.

### Checklist de merge / deploy

- [x] `LP-050` cerrado con evidencia ejecutada
- [x] Producción verificada intacta en lectura (8 migraciones, 0 columnas nuevas)
- [x] Snapshot de rollback probado **restaurable** (17 s, exit 0)
- [x] 28/28 tablas sin pérdida ni cambio de valores preexistentes (hash propio)
- [x] Esquema nuevo compatible con el código viejo (0 NOT NULL sin default, único UNIQUE tolera NULLs, FK nullable)
- [x] `git status --porcelain` limpio en el repo del sistema
- [ ] **Credencial de FTP/Web Deploy rotada y funcionando** ← bloqueante del deploy del sitio (Joaquín)
- [ ] **Base y sitio deployados en la MISMA ventana**, o ferretería sin operar entre las dos mitades ← condición del GO
- [ ] `LP-051` `trivial` — pendiente, no bloqueante

**Veredicto del lote: `LP-050` CERRADO. GO para el deploy.** La condición no es técnica del código: es de
**secuencia**. El esquema nuevo aguanta al código viejo sin romperse, pero cada escritura que el código viejo haga
después de migrar deja un dato que ningún backfill va a volver a arreglar.

---


---

