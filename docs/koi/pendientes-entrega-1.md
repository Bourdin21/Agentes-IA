# KOI Dumplings — Pendientes antes de la entrega al cliente

**Estado al 2026-09-10.** Este documento lista lo que **NO** está resuelto y hay que decidir, verificar o comunicar antes de dar la Entrega 1 por cerrada. Lo que ya está entregado y verificado no aparece acá — eso vive en `trazabilidad.md`.

Orden: primero lo que bloquea la operación del cliente, después lo que necesita su definición, y al final lo que es deuda nuestra.

---

## 🔴 1. BLOQUEANTE — Agosto 2026 no cierra

**Situación:** el Estado de Resultados de agosto muestra **$99.948.507 de gastos contra $63.131.109 de ventas**. No es un error de cálculo del sistema: es que el mes tiene **cargados los dos catálogos a la vez**.

**Por qué pasó:** el sprint del catálogo real reemplazó la estructura pero no remapeó los gastos históricos. El cliente empezó a recargar los meses abiertos sobre el catálogo nuevo, y el viejo conservó su importe. Pares exactos duplicados:

| Catálogo viejo | | Catálogo nuevo | |
|---|---:|---|---:|
| Sueldos y Jornales | 11.662.231 | Sueldos | 11.662.231 |
| Alquiler del local | 4.500.000 | Alquiler | 4.500.000 |
| CMV | 14.346.505 | Mercadería KOI + 3 | 14.346.505 |

**Por qué no lo resolvimos nosotros:** decisión explícita del dueño del estudio — *"los datos que ya recargó el cliente no se tocan"*. Definir cuál de las dos filas vale en cada caso es dato del cliente, no del sistema. Los **18 meses cerrados sí** se consolidaron (356 conceptos, totales verificados al centavo).

**Qué hace falta:** sentarse con Juani y, para cada uno de los 4 meses abiertos (**2026-01, 07, 08 y 09**), decidir qué filas quedan. Una vez definido, es una operación de minutos.

**Riesgo si no se hace:** el mes no cierra, y sin cierre no hay reparto a inversores.

---

## 🔴 2. BLOQUEANTE — Seis subgrupos históricos sin destino

La consolidación migró 10 de 16 subgrupos del catálogo viejo. **Seis quedaron sin mapear porque no tienen equivalente claro en el catálogo nuevo**, y no corresponde que lo decidamos nosotros:

| Subgrupo viejo | Total 18 meses | Problema |
|---|---:|---|
| **CMV** | $442.172.058 | El rubro nuevo lo abre en 4 (Mercadería KOI, Barriles, Verdulería, Bebidas). No es 1:1 — hay que definir el reparto |
| **Otros gastos** | $212.710.167 | No existe equivalente. Es el 17 % de los gastos históricos |
| Previsión I (1 %) | $13.421.537 | ¿Es "Fondo de juicios laborales"? Probable, no confirmado |
| Previsión II (1 %) | $13.410.991 | ¿Es "Reposición maquinaria"? Probable, no confirmado |
| Honorarios | $5.151.000 | ¿Va a "Contador"? Dudoso |
| Publicidad | $980.206 | ¿Va a "Publicidad y Propaganda"? Ese es un **impuesto**, no un gasto de publicidad |

**Impacto mientras tanto:** los meses históricos siguen mostrando esas seis filas del catálogo viejo. **Los totales son correctos** — es un problema de legibilidad, no de números.

**Qué hace falta:** que el cliente confirme el mapeo de los seis. Con eso, extender la migración es directo y ya está el procedimiento probado (backup → foto previa → traslado atómico → verificación al centavo).

---

## 🟡 3. Corrección aplicada que conviene que el cliente valide

**"Mercadería KOI" de agosto estaba en $111.396.734.** Se corrigió a **$11.139.654**, con backup previo de la fila.

**Por qué se tocó:** autorización explícita del dueño del estudio. La evidencia de que era un error de tipeo es fuerte: `111.396.734 ÷ 10 = 11.139.673`, y el valor que hace cuadrar la familia CMV contra el CMV histórico del mes es `11.139.654` — **a $19 de diferencia**. Un dígito de más al cargar.

**Qué hace falta:** que Juani confirme el número. Si el valor real era otro, se corrige en un minuto (el original está en `bkp_20260909_conceptos`).

---

## 🟡 4. Preguntas del cliente sin responder

Cuatro quedaron abiertas del relevamiento y **no bloquean la entrega**, pero conviene cerrarlas:

| # | Pregunta | Por qué importa |
|---|---|---|
| P-B01 | "Que los meses cerrados se puedan reabrir" — **ya está implementado** desde hace semanas, con motivo obligatorio. ¿No encuentra el botón, o pide algo distinto (editar sin reabrir, o que no se descarten las liquidaciones)? | Se cotizó como pendiente algo que ya existe |
| P-B02 | "En Servicios figuran 4 cuando son más de 10" — **hoy se ven 16**. ¿En qué mes lo vio? | Probablemente lo vio antes del despliegue del catálogo real |
| P-B06 | ¿El perfil Gerente debe ver el Dashboard completo, con importes de resultado? | Hoy tiene acceso. Si el cliente dice que no, es sacar el link y poner la policy |
| P-B08 | El texto del importador: ¿se saca o se reformula? | Se reformuló; falta que confirme que ahora se entiende |

---

## 🟡 5. Decisión de negocio registrada, no implementada

**Redondeo de importes.** Se implementó **sólo en pantalla**: la base conserva los centavos y la conciliación contra el Excel del cliente sigue dando exacta.

El dueño pidió **dejar registrada como opción 2** la variante de redondear también al guardar. **No está implementada.** Si se decide activarla, hay que evaluar antes que los totales del EDR sigan cuadrando contra el Excel.

---

## 🟠 6. Deuda técnica y de infraestructura (nuestra, no del cliente)

| # | Tema | Detalle |
|---|---|---|
| D-A01 | **La conexión con Ayres depende de una IP fija** | La regla de firewall del hosting apunta a `190.245.226.181`. Si Ayres migra de servidor, la integración se corta sin aviso. Ya está documentado en el manual en lenguaje de cliente |
| R-A02 | **La API de Ayres va por HTTP sin TLS** | Usuario y contraseña viajan en texto plano en cada llamada. No lo resuelve nuestro código: hay que pedirle a Ayres que la exponga en 443 con certificado. **Pedido redactado, sin enviar** |
| VUL-001 | 8 advertencias `NU1902` de MailKit/MimeKit | Preexistentes, sin resolver |
| — | **Clave por defecto del SuperUsuario** | `no-reply@olvidata.com.ar` / `Super123!` sigue activa en un sitio público. **Cambiarla antes de la entrega** |
| — | **ApiKey de QuickPass** | Estuvo versionada en el repo de blankproject. Conviene rotarla |
| — | Prueba manual en navegador | Varias entregas se verificaron por HTTP, no visualmente. Falta el recorrido con mouse |
| — | Acceso efectivo de los roles | Todo se verificó con la cuenta SuperUsuario. **Falta entrar con un usuario Administrador, uno Inversor y uno Gerente** y confirmar qué ve cada uno |

---

## ✅ Lo que sí quedó cerrado y verificado en producción

Para que el contraste sea claro: crear/editar/eliminar inversores (no persistía **nada**), recuperar contraseña antes del login, `/System` fuera del menú del Administrador, orden de las columnas de importe en Reparto General, cámaras ocultas por feature flag, rol Gerente con barrera de cierre en el servidor, consolidación de los 18 meses cerrados con totales idénticos al centavo, y la integración con Ayres trayendo las ventas del mes con preview y confirmación.

---

## 🟡 7. Agregados por la Ola 2 (2026-09-10)

| # | Tema | Detalle |
|---|---|---|
| 7.1 | **El barrido legal se verificó por código, no en navegador** | Es el ítem más sensible del sprint. Los pasos 25-30 de la guía manual (`5-implementador.md`, Etapa 23) **no son opcionales**: hay que entrar con un usuario **Inversor real** y confirmar que no ve "facturado vs informal" en ninguna pantalla ni exportable |
| 7.2 | **El importador puede revivir un concepto sacado del mes** | Si el Excel lo trae, vuelve. Es el comportamiento correcto —el Excel es la fuente de verdad— pero **hay que avisarle al cliente** para que no lo lea como un error |
| 7.3 | **Regla técnica nueva a respetar** | Cualquier código futuro que busque un `ConceptoGasto` para insertarlo si no existe **debe** usar `IgnoreQueryFilters()`. Sin eso, con los conceptos sacados del mes, se produce una violación de índice único visible para el usuario |
| 7.4 | **Caché de 5 minutos en el gráfico diario** | El mes en curso puede verse desactualizado hasta 5 minutos. Fue deliberado: sin caché, cada carga del Dashboard disparaba 4 llamadas a Ayres |
| 7.5 | **La opción 2 del redondeo sigue sin implementar** | Ver punto 5. Hoy el redondeo es sólo de pantalla |



---

## 🔴 8. Hallazgos del análisis del Excel de reparto (2026-09-10)

| # | Tema | Situación | Qué hace falta |
|---|---|---|---|
| 8.1 | **Septiembre cerrado sobre un mes parcial** | Cerrado el 10/9 con 8 días de ventas y sin gastos reales. 15 liquidaciones por **$9.802.746** (el doble por punto que agosto). Una marcada pagada, aparentemente de prueba. **No salió ningún mail.** | ✅ **Reabierto el 2026-09-10** por decisión del dueño. Las 15 liquidaciones quedaron descartadas. |
| 8.2 | **El recupero en pesos está mal calculado** | El sistema muestra el mismo número en pesos y en dólares, en los 15 inversores. El Excel usa el capital a un **TC de ingreso fijo por inversor** (980 / 1.000 / 1.180 / 1.200) que el sistema no tiene. | ✅ **Deployado el 2026-09-10** (`f7d8413`). Verificado en producción: el recupero en pesos da mayor que en dólares. |
| 8.3 | **El recálculo automático pisa los porcentuales del cliente** | Regresión de la Etapa 19b: en cada vista de un mes abierto reescribe Regalías, Cánon y Previsiones con base × %, aunque el cliente haya cargado otro número. | ✅ **Deployado el 2026-09-10:** ya no pisa en silencio y abrir un mes no escribe nada. Restaurar julio y agosto sigue pendiente de aprobación del cliente; julio se recupera con datos del propio sistema. |
| 8.4 | **Conciliación de los tres meses abiertos** | ✅ **Aprobada y aplicada el 2026-09-10.** Julio 57.287.371,34 y agosto 58.034.260,47, al centavo contra el Excel; enero 55.112.086,89 (sacadas del mes las 4 filas duplicadas). Backup `bkp_20260910b_conceptos`, una fila de auditoría por mes. | — |
| 8.5 | **El Excel del cliente tiene errores** | Julio: la celda "VENTAS" está $3.000.000 por debajo de A + B (el sistema y Ayres tienen el número bueno). La rentabilidad promedio usa tres fórmulas distintas según la hoja. El Excel de E.R. no tiene enero–junio 2026. | Avisarle a Juani. El resultado de julio no es 939.550 sino **3.939.551**, y julio todavía no se repartió. |
| 8.6 | **Junio 2026 no existe** | No hay período cargado ni en el sistema ni en el Excel de E.R. Ayres tiene ventas de ese mes. | Confirmar con el cliente si junio se cargó en otro lado o falta. |
| 8.7 | **Minjo Wang: 7 u 8 puntos** | La imagen del cliente dice 7; el sistema y la propia hoja del Excel tienen 8 desde abril 2025. El capital sigue en 21.000 (7 × 3.000). | Confirmar si el octavo punto se pagó. |
| 8.8 | **Datos de pago que el sistema no modela** | Pago en efectivo (Welchen), liquidación partida en dos (Luciano Aued), pago en USD a un TC propio (Salas y cia, 1.380 contra 1.520 del mes). | Decidir si se incorporan. |
| 8.9 | **La cuenta SuperUsuario se usa desde tres IPs** | Sigue con la clave de fábrica en un sitio público. | **Decisión del dueño (2026-09-10): la clave queda igual.** |
| 8.10 | **Duplicación al reabrir meses del catálogo viejo** | ✅ **Resuelto el 2026-09-10** (`7cdfe20`). En un mes con porcentuales vivos del catálogo viejo el recálculo ya no crea filas nuevas, sólo actualiza las que hay. Verificado: abrir enero en producción no recrea nada. Era requisito para que la conciliación de enero se sostuviera. | — |
| 8.11 | **Corte de la rentabilidad promedio** | ✅ **Decidido y deployado el 2026-09-10** (`7cdfe20`): se divide por los meses desde el ingreso hasta el **último mes cerrado** (hoy mayo 2026). Wang: 19 meses, 2,3 % U$D / 3,0 % $. | — |
