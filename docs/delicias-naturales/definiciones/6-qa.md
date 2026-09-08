# Memoria - QA

## Proyecto: DeliciasNaturales
## Ultima actualizacion: 2026-09-07

## Estado go/no-go

**GO CONDICIONADO** para el deploy de las 18:00 del 2026-09-07 (iteracion 3 "Editar Pago").

La feature esta funcionalmente completa y correcta: HU1-HU7 PASS por trazado de codigo, T1/T2/T3/T5 cerrados, build limpio verificado por QA (no solo reportado). Se detectaron 3 defectos; 2 auto-fixeados por QA en esta misma etapa (DN-003 major y un defecto menor de orden de guards), y 1 major NO corregido (DN-004) que es una decision de negocio, no un bug de implementacion.

Las 3 condiciones del GO estan listadas en "Condiciones del GO" mas abajo. Ninguna requiere tocar codigo; dos son verificaciones previas al deploy y una es una comunicacion operativa al usuario final.

---

## Alcance funcional validado
Boton unico "Editar pago" (Fecha + Monto + Metodo + Motivo obligatorio) sobre el listado de pagos de una Venta, que reemplaza a "Editar fecha" (`ActualizarFechaPago`, eliminada). Toda edicion pasa por reversion + alta enlazada por `PagoAnteriorId` (PAT-023). Refactor de `RegistrarPago`/`EliminarPago` a `Services/PagoService.cs`. Migracion `202609071405299_AddCamposEdicionPago` (4 columnas nullable + 3 FK + 3 indices).

**Fuera de alcance, correctamente excluido (no se reporta como gap):** gestion de devoluciones punta a punta y la resolucion de la venta 9444 en si (ya resuelta a mano, NC AFIP CAE 86361847162185).

---

## Camino de verificacion usado (declaracion explicita)

**El servidor MCP de Playwright NO estuvo disponible en esta sesion** (no expone herramientas `mcp__playwright__*`). Segun la regla del rol, se declara explicitamente y se cae al procedimiento manual: **toda la cobertura funcional de abajo es por revision estatica rigurosa (trazado linea por linea de cada escenario contra el codigo real) + build real + verificacion de esquema contra MySQL local.** No hubo ejecucion end-to-end por navegador.

Verificaciones que SI ejecuto QA de forma independiente (no se tomo el reporte del implementador como dado):
- `MSBuild DeliciasNaturales.sln /t:Rebuild /p:Configuration=Debug /p:MvcBuildViews=true` → **EXITCODE 0**, 0 errores, 35 warnings preexistentes. Corrido dos veces: antes y despues de los auto-fixes de QA.
- Esquema de la base local `delicias` (MySQL 8, `information_schema`): migracion presente en `__MigrationHistory`, 4 columnas nuevas confirmadas nullable (`movimientoscaja.PagoId int`, `pagos.UsuarioId varchar(128)`, `pagos.Observacion varchar(500)`, `pagos.PagoAnteriorId int`), collation uniforme `utf8mb4_0900_ai_ci` en `pagos`/`movimientoscaja`/`aspnetusers` (las 3 FK se crearon sin conflicto de charset).
- Volumen de la base local: 5.799 pagos, 5.525 movimientoscaja, 3.572 ventas, 307 usuarios. **No es una base de juguete** — es del mismo orden de magnitud que produccion (Diseño estima ~15.000 pagos), lo que reduce sustancialmente el riesgo T4 en su componente de DDL.
- Grep exhaustivo de referencias huerfanas a `ActualizarFechaPago` / `editarFechaPago`: solo quedan comentarios, ningun call site vivo.

---

## Cobertura por criterio de aceptacion (HU1-HU7)

| HU | Criterio | Resultado | Evidencia |
|---|---|---|---|
| HU1 | Editar monto: viejo soft-deleted, nuevo con `PagoAnteriorId`, `MovimientoCaja` refleja el nuevo monto | **PASS** | `PagoService.EditarPago` pasos 1-4; `MovimientoCaja.Pago = pago` en `RegistrarPagoInterno` |
| HU1 | Editar hacia abajo un pago que genero credito por sobrepago (caso tipo venta 9444) | **PASS** | Trazado numerico: reversion borra el credito viejo, `SaveChanges` intermedio actualiza `GetMontoRestante`, el credito se recalcula sobre el estado post-reversion. Sin el guard `esEdicion` el escenario quedaba bloqueado |
| HU1 | Editar un pago de una Venta Facturada funciona igual que en Ingresada/Finalizada | **PASS** | `EditarPago` no consulta `venta.Estado` (decision D7) |
| HU2 | Cadena completa visible con 2-3 ediciones sucesivas | **PASS** | `ObtenerPagosDeVenta`: `visibles = !DeletedAt \|\| reemplazadoPor.ContainsKey(Id)`. Trazado con cadena P1→P2→P3: las 3 filas se renderizan, solo la vigente lleva saldo |
| HU2 | Motivo visible en la fila del pago reemplazado | **PASS** | `MotivoReemplazo` resuelto desde la `Observacion` del pago nuevo (decision D6) |
| HU3 | Sin motivo: rechazado en UI y en request forzado | **PASS** | Triple guard: JS `enviarEdicionPago`, `PagosController.EditarPago`, `PagoService.EditarPago` |
| HU4 | No toca `Factura` ni `ProductosVenta` ni recalcula `Venta.Estado` | **PASS** | Grep confirma 0 asignaciones a `venta.Estado` en `PagosController`/`PagoService`. Cumple ademas la regla (d) de MH-020 |
| HU5 | Boton oculto en filas reemplazadas | **PASS** | `PagoVentaViewModel.PuedeEditar => !Reemplazado` |
| HU5 | Request forzado sobre un pago reemplazado rechazado con error explicito | **PASS (post auto-fix)** | El guard existia pero era **inalcanzable**: un pago reemplazado siempre queda tambien soft-deleted, y el chequeo de `DeletedAt` iba primero. Se rechazaba igual, pero con el mensaje generico "El pago fue eliminado...". Guards reordenados por QA |
| HU6 | Editar solo la fecha exige motivo y genera el mismo par viejo/nuevo | **PASS con salvedad** | Mismo camino unico, sin atajo. **Salvedad: ver DN-004** — ahora depende de que haya una caja chica abierta |
| HU7 | Cambiar Metodo hacia/desde SaldoFavor revalida saldo como alta nueva | **PASS** | `RegistrarPagoInterno` corre las 4 validaciones de SaldoFavor sobre `venta.Cliente.GetSaldoCuentaCorriente` ya post-reversion (los MCC viejos quedan con `DeletedAt` y salen del calculo) |

---

## Cobertura de los 9 puntos de la estrategia de pruebas de Arquitectura

| # | Punto | Resultado |
|---|---|---|
| 1 | Regresion de `RegistrarPago`/`EliminarPago` tras el refactor (T1) | **PASS** — ver seccion T1 abajo |
| 2 | `EditarPago`: solo fecha / solo monto / solo metodo / combinaciones | **PASS** por trazado (no por navegador) |
| 3 | HU2 cadena de 2+ ediciones | **PASS** por trazado |
| 4 | HU3 sin motivo (UI y request directo) | **PASS** |
| 5 | HU4 Venta Facturada sin efectos colaterales | **PASS** |
| 6 | HU5 pago ya reemplazado | **PASS** post auto-fix |
| 7 | Concurrencia (T2): 2 requests simultaneas | **BLOCKED** — no ejecutable sin entorno de carga. El lock esta correctamente colocado (verificado estaticamente) |
| 8 | SaldoFavor cruzado (hacia y desde) | **PASS** por trazado |
| 9 | Migracion contra copia de produccion | **BLOCKED** — no hay dump de produccion local. Ver "Condiciones del GO" |

---

## Riesgos tecnicos de Arquitectura (T1-T5)

**T1 — Regresion por refactor de codigo ya hardeneado. PASS.** Se comparo el codigo actual contra el previo (`git diff`) metodo por metodo:
- `RegistrarPago`: mismos mensajes de error literales (movidos a `PagoNegocioException`, cuyo `Message` se devuelve tal cual, sin prefijo). Mismo `lock (_registrarPagoLock)` en la misma posicion, misma transaccion, mismo guard de `Estado == Ingresada`, mismo Include de `Pagos` + `Cliente.MovimientosCuentaCorriente`. Unico cambio de orden: las validaciones ahora ocurren DENTRO de la transaccion en vez de antes; el efecto observable es identico (rollback de una transaccion sin escrituras).
- Calculo del excedente: `Math.Max(0, monto - Math.Max(0, montoRestante))` vs. el anterior `Math.Max(0, monto - montoRestante)`. **Provablemente identico en el alta normal**: ahi el guard `montoRestante <= 0 && !esEdicion` garantiza `montoRestante > 0`, con lo cual el clamp interno es la identidad. El clamp solo actua en ediciones sobre ventas con `montoRestante` negativo, donde evita inflar el credito de cuenta corriente.
- `EliminarPago`: mismo cuerpo, misma ausencia de lock (igual que antes), misma transaccion. La reversion delegada a `ReversarPago` es equivalente: para pagos historicos cae al mismo predicado de siempre; para pagos nuevos usa la FK exacta, que es estrictamente mas preciso.
- **Conclusion: la desviacion del guard `esEdicion` esta bien justificada y NO tapa un bug.** Es un guard que solo se relaja en un camino que antes no existia, y se demostro que el camino de alta normal es bit a bit el mismo.

**T2 — El lock debe envolver reversion + alta. PASS.** `lock (_registrarPagoLock)` se abre en `PagosController.EditarPago` **antes** de la transaccion y de la llamada al service, que hace reversion y alta adentro.

**T3 — `MovimientoCaja.PagoId` seteado en TODA alta. PASS.** `RegistrarPagoInterno` es el unico lugar del sistema que crea `Pago` + `MovimientoCaja`, y setea la navegacion `Pago = pago` siempre (no solo en ediciones). `CajasController` crea movimientos no vinculados a pagos, donde `PagoId = NULL` es lo correcto.

**T4 — Migracion contra copia de produccion. ABIERTO (condicion del GO).** Ver "Condiciones del GO".

**T5 — Otros consumidores de `Pago`. PASS.** `_TablaPagos` se renderiza solo desde `Ventas/Details` y `Ventas/Edit`, y ambas acciones publican `ViewBag.PagosVenta` y `ViewBag.MetodosPago` (esta ultima ya existia para el modal de Registrar Pago; `Edit` la obtiene via `SetViewBag`). `PagosController.Index`/`ListarPagos`/`ExportarExcel` y `DashboardController` filtran por `.Active()` y se comportan bien sin tocarlos.

---

## Cobertura del catalogo cross-proyecto (`docs/qa/regresiones-manuales.yml`)

| id | aplica | resultado | accion |
|---|---|---|---|
| LP-003 (decimal es-AR en `input type=number`, salida) | no | **N/A** | `Global.asax.Application_BeginRequest` fuerza `NumberDecimalSeparator = "."` en cada request, lo que cierra la mitad de SALIDA. Ademas el implementador uso `InvariantCulture` explicito en `_TablaPagos` y en el modal de Registrar Pago |
| GAN-005 (decimal es-AR, mitad de ENTRADA) | no | **N/A** | Misma causa: la cultura parcheada del request hace que el binder parsee `1500.50` correctamente. Verificado en `Global.asax.cs:36-40` |
| GAN-006 (step del input < precision de la columna) | si | **PASS** | `#editarPagoMonto` usa `step="any"`; no hay bloqueo de jquery-validate |
| MH-020 regla (d) (no recalcular estado del comprobante al tocar un pago) | si | **PASS** | Grep confirma 0 asignaciones a `venta.Estado` en el camino de pagos |
| MH-020 regla (b) (reversar por contramovimiento, nunca borrar el movimiento original) | si | **FAIL** | `ReversarPago` hace soft-delete del `MovimientoCaja`/`MovimientoCuentaCorriente` original. Catalogado como **DN-004**, no corregido (decision de negocio) |
| MH-021 (fecha efectiva pisada con la fecha real de la accion) | no | **N/A** | Aca la fecha del pago es un dato editable a proposito por el usuario, no una confirmacion diferida |
| DN-001 (500 en `ListarVentas` por Include + Skip/Take) | si | **PASS** | Fix previo intacto; esta iteracion no toco `ListarVentas` |
| DN-002 (mismo patron en `PagosController.ListarPagos`) | si | **SIN CAMBIO** | Sigue abierto, fuera de alcance, no autorizado. Esta iteracion no lo agravo |
| DN-003 (fallback heuristico no acotado a filas sin FK) | si | **FAIL → FIXED** | Detectado y auto-fixeado en esta etapa. Item nuevo del catalogo |
| DN-004 (reversion que reescribe un periodo/caja ya cerrado) | si | **FAIL** | Detectado en esta etapa. Item nuevo del catalogo. **No corregido** |
| REG-001..010, KOI-*, CRM-*, MH-001..019, SG-*, LP-001/004/005, LIP-*, ELV-*, VSF-*, GAN-001..004 | no | **N/A** | Modulos o stacks sin equivalente en el alcance de esta iteracion (EF Core / .NET 10 / tag helpers / DataTables no tocados) |

---

## Defectos detectados en esta etapa

**DN-003 — MAJOR — Fallback de `ReversarPago` no acotado a movimientos sin FK. AUTO-FIXEADO.**
- Pasos: venta con un pago historico de $X (movimiento con `PagoId = NULL`) + un pago nuevo del mismo importe $X (movimiento con `PagoId` seteado). Eliminar o editar el pago **historico**.
- Sintoma: el fallback `VentaId + Monto` podia elegir el movimiento del pago **nuevo**, dejandolo sin ingreso de caja y descuadrando el arqueo, mientras el movimiento huerfano seguia sumando.
- Causa: al pasar de busqueda heuristica a FK exacta, el fallback se conservo sin la condicion que lo hace mutuamente excluyente. Arquitectura seccion 2 lo habia especificado ("fallback exclusivamente para movimientos con `PagoId == null`"); la implementacion omitio ese filtro.
- Fix aplicado por QA: `Services/PagoService.cs`, `ReversarPago` — se agrego `m.PagoId == null` como primera condicion del `FirstOrDefault` del fallback. Sin logica de negocio nueva: alinea el codigo con la arquitectura aprobada.

**QA-DN-004(menor) — MINOR — Guards de `EditarPago` en orden que hacia inalcanzable el mensaje de HU5. AUTO-FIXEADO.**
- El chequeo `pagoViejo.DeletedAt.HasValue` iba antes del de "ya reemplazado". Como todo pago reemplazado queda ademas soft-deleted, el segundo guard era codigo muerto y HU5 respondia "El pago fue eliminado y ya no se puede editar." en vez del mensaje que orienta al pago vigente de la cadena. El rechazo funcional ocurria igual (HU5 nunca estuvo abierta), pero el mensaje era el equivocado.
- Fix aplicado por QA: `Services/PagoService.cs`, `EditarPago` — guards reordenados. Solo cambia el texto devuelto, no el resultado.

**DN-004 — MAJOR — Editar un pago reescribe el arqueo de una caja ya cerrada y exige caja chica abierta. NO CORREGIDO (decision de negocio).**
- Variante A: sin caja chica abierta, editar **solo la fecha** de un pago falla con "No hay una caja chica abierta para registrar el ingreso." — un error que no tiene relacion con corregir un typo, y que deja al usuario sin salida. El viejo `ActualizarFechaPago` funcionaba siempre porque solo hacia UPDATE de la fecha.
- Variante B: si el `MovimientoCaja` del pago pertenece a una caja **ya cerrada**, la reversion lo da de baja logica ahi (el saldo recalculado de esa caja deja de coincidir con su arqueo de cierre — `CajasController` recalcula sumando `MontoDecorado` de los movimientos no eliminados) y el movimiento nuevo se agrega a la caja abierta de HOY, fechado con la fecha del pago. Dos cajas quedan mal: la vieja de menos, la nueva de mas.
- Naturaleza: el efecto ya existia en `EliminarPago` (preexistente, y era exactamente el workaround manual que esta feature viene a reemplazar). **Lo genuinamente nuevo es que ahora tambien alcanza a la correccion de solo-fecha**, que antes era liviana y no tocaba cajas. Diseño riesgo #4 solo previo "mas filas tachadas" como costo del camino unico; este costo es mayor y no estaba enumerado.
- Por que NO lo auto-fixeo QA: la solucion correcta (reversar por contramovimiento en la caja abierta, segun MH-020 regla (b) / PAT-020) es **logica de negocio nueva** y cambia como se ve el arqueo historico. Fuera del mandato de auto-fix. Escalado al orquestador/implementador.

---

## Auto-fixes aplicados

| id | archivos | resultado post-parche |
|---|---|---|
| DN-003 | `Services/PagoService.cs` (`ReversarPago`) | Build `MvcBuildViews=true` EXITCODE 0, 0 errores, mismos 35 warnings preexistentes |
| QA-DN-004(menor) | `Services/PagoService.cs` (`EditarPago`, orden de guards) | idem |

Ninguno introduce logica de negocio nueva. DN-003 replica la especificacion de Arquitectura seccion 2; el reordenamiento de guards solo hace alcanzable un mensaje que ya estaba escrito.

---

## Condiciones del GO (las 3 deben cumplirse antes de ejecutar el deploy de las 18:00)

**C1 — Verificar `__MigrationHistory` de produccion ANTES de correr `Update-Database`. (BLOQUEANTE)**
Esta memoria registra en su historial de 2026-07-01 que hubo al menos una "migracion EF aplicada por SQL directo" en este proyecto. Si produccion tiene columnas aplicadas a mano sin la fila correspondiente en `__MigrationHistory`, `Update-Database` va a intentar re-aplicar esas migraciones y fallar con "Duplicate column name" — y en MySQL el DDL no es transaccional, con lo cual puede quedar a medias.
Verificacion previa (solo lectura, no destructiva):
```sql
SELECT MigrationId FROM __MigrationHistory ORDER BY MigrationId DESC LIMIT 5;
```
Debe contener `202608270055400_LoginAudit` y `202608042138277_FacturaDeletedBy`. Si falta alguna, **no correr `Update-Database`**: generar el script con `Update-Database -Script -SourceMigration:202608270055400_LoginAudit` y aplicar solo el DDL de `AddCamposEdicionPago` a mano, insertando despues la fila de historial.

**C2 — Backup de `pagos` y `movimientoscaja` inmediatamente antes del DDL. (BLOQUEANTE)**
Sustituye a la prueba contra copia de produccion que pedia T4 y que no se pudo hacer (no hay dump local). Justificacion de por que esto alcanza: el DDL son 4 `ADD COLUMN` nullable + 3 indices + 3 FK sin backfill ni UPDATE, ya verificado por QA aplicandose limpio sobre una base local de 5.799 pagos / 5.525 movimientos con collation uniforme `utf8mb4`, y las FK a `AspNetUsers.Id` tienen precedente exitoso en produccion (`202608042138277_FacturaDeletedBy` ya creo una). El riesgo residual real es de historial de migraciones (C1), no de la forma del DDL. `Down()` esta completo y es reversible.

**C3 — Avisar a los usuarios que "Editar pago" requiere la caja chica abierta (DN-004 variante A). (OPERATIVO, no bloqueante para el deploy pero si para la experiencia del dia 1)**
Y decidir con Joaquin, como item de la proxima iteracion, si la reversion pasa a contramovimiento (DN-004 variante B). Mientras tanto, evitar editar pagos cuyo movimiento pertenezca a una caja ya cerrada.

**Nota:** `Web.config` apunta a `Conexiones\ConectionDB-PROD.config`. Cualquier `Update-Database` corrido desde una maquina de desarrollo con la configuracion por defecto **impacta produccion**. Confirmado que NO hay inicializador `MigrateDatabaseToLatestVersion` ni `AutomaticMigrationsEnabled` (esta en `false`), asi que el deploy del binario por si solo no dispara DDL — es una operacion deliberada y controlada. Bien.

---

## Riesgos de liberacion y mitigaciones

| Riesgo | Nivel | Mitigacion |
|---|---|---|
| DN-004: arqueo de cajas cerradas alterado por ediciones de pago | **MEDIO-ALTO** | C3 + decision de negocio en la proxima iteracion. Preexistente en `EliminarPago`, ampliado por esta feature al caso solo-fecha |
| Historial de migraciones de produccion desalineado (T4 real) | **MEDIO** | C1 + C2 |
| Sin verificacion por navegador (Playwright MCP caido) | **MEDIO** | Todo el cableado de UI se verifico estaticamente con precedente fuerte: los nombres de campos del form coinciden exactamente con la firma de la accion; `swal(...)` usa la misma forma exacta que `eliminarPago`, que funciona en produccion; el combo de metodo se prellena por texto de la opcion (la `SelectList` se construye sin `dataValueField`, igual que el modal de Registrar Pago vigente). Aun asi, **hacer un smoke manual de las 3 pruebas minimas apenas termine el deploy** |
| Concurrencia `EliminarPago` vs `EditarPago` sobre la misma venta | **BAJO** | `EliminarPago` sigue sin tomar `_registrarPagoLock` (preexistente, no introducido). La superficie crecio; anotar para la proxima iteracion |
| `EditarPago` sin `[ValidateAntiForgeryToken]` | **BAJO** | Preexistente y consistente con `RegistrarPago`/`EliminarPago`. No es una regresion, pero es una mutacion financiera sin token CSRF: vale una pasada global futura |
| DN-002 (`PagosController.ListarPagos`) | **MEDIO** | Sin cambios. Sigue fuera de alcance y sin autorizacion |

---

## Pruebas minimas a ejecutar a mano tras el deploy (no automatizables en esta sesion)

1. Venta Facturada con 2 pagos → editar el monto del segundo hacia abajo con motivo → aparecen las 2 filas (vieja tachada con motivo y usuario, nueva vigente), el saldo pendiente es correcto, la Factura y el estado de la Venta no cambian.
2. Editar **solo la fecha** de un pago (con caja chica abierta) → exige motivo, genera el par viejo/nuevo, el `MovimientoCaja` nuevo lleva la fecha corregida.
3. Editar dos veces seguidas el mismo pago → el detalle muestra la cadena de 3 filas completa, y el boton "Editar" aparece solo en la vigente.
4. Registrar un pago normal y eliminarlo (sin editar nada) → mensajes y saldos identicos a los de antes del deploy (regresion T1).
5. Cambiar el metodo de un pago a `SaldoFavor` con un cliente sin saldo → rechazo con "El cliente no tiene saldo a favor disponible." y nada persistido.
6. Papelera: confirmar que un pago reemplazado por una edicion **no** aparece como restaurable.

---

## Defectos resueltos (historico)
- DEF-001 CRITICO: Vendedor creaba en VerificadoDeposito -- fixed controller+vista
- DEF-002 MAYOR: Default modal Sumar -- fixed a Pisar
- DEF-003 MAYOR: Falta banner rol en Create -- fixed
- DEF-004 MENOR: Falta badge Actualizado -- fixed

## Defectos catalogados en etapas anteriores
- DN-001 BLOCKER (catalogo cross-proyecto `regresiones-manuales.yml`): NullReferenceException en `MySql.Data.EntityFramework.SelectStatement.AddColumn` al filtrar `/Ventas/ListarVentas` por numero, con 3 Include de coleccion + WHERE/OrderBy dinamico + Skip/Take combinados. FIXED por el implementador en `Controllers/VentasController.cs` (separacion pageIds / ventasDB). Validado por QA (build real + trazado de los 7 escenarios).
- DN-002 MAJOR (catalogo cross-proyecto, NO corregido): mismo patron de riesgo confirmado por lectura de codigo en `Controllers/PagosController.cs::ListarPagos` (linea ~168). No hay reporte de sintoma real en produccion todavia. NO corregido: requiere autorizacion explicita.

## Historial de ajustes
- 2026-05-27: QA inicial ciclo mejoras stock. 4 defectos detectados y auto-fixed. Build OK.
- 2026-07-01: QA de HOTFIX de produccion. Alcance `Controllers/VentasController.cs::ListarVentas`. 7/7 escenarios PASS por revision estatica + Rebuild limpio. Se catalogaron DN-001 (fixed) y DN-002 (no corregido). GO para merge.
- 2026-09-07: QA de la iteracion 3 "Editar Pago" (deploy programado 18:00 del mismo dia). Playwright MCP no disponible → verificacion estatica + build + esquema, declarado explicitamente. HU1-HU7 PASS; T1/T2/T3/T5 cerrados; T4 y el punto 7 (concurrencia) BLOCKED. Se confirmo de forma independiente que las **dos desviaciones del implementador estan bien justificadas y no tapan bugs**: el guard `esEdicion` es demostrablemente un no-op en el alta normal y desbloquea el caso central de HU1, y la exclusion de los pagos reemplazados de `RecycleBinService` evita una duplicacion real de importes cobrados. Se detectaron 3 defectos: **DN-003** (major, fallback de reversion no acotado a filas sin FK — auto-fixeado), un defecto **menor** de orden de guards que hacia inalcanzable el mensaje de HU5 (auto-fixeado), y **DN-004** (major, editar un pago reescribe el arqueo de cajas cerradas y exige caja chica abierta incluso para corregir solo la fecha — NO corregido, es decision de negocio, escalado). DN-003 y DN-004 dados de alta en el catalogo cross-proyecto. **Veredicto: GO CONDICIONADO** a C1 (verificar `__MigrationHistory` de produccion), C2 (backup de `pagos`/`movimientoscaja` antes del DDL) y C3 (aviso operativo por DN-004).
