# Memoria - Presupuestador

## Proyecto: ganaderia
## Ultima actualizacion: 2026-07-02

---

## Iteracion v12 — Autocomplete Select2 (Concepto de Egreso, Motivo de Factura de venta) (2026-07-02)

Repositorio exclusivo: `C:\Sistemas\ganaderia - emo`. Iteracion evolutiva chica y cohesiva sobre proyecto ya cerrado.

### Anclaje historico (Paso 0)

Referencia principal: el propio historico del proyecto — item "Extension job diario" de la iteracion v11 (M=1.5h, ajuste sobre servicio existente) y la fila "Modificacion sobre modulo existente: agregar regla de negocio, M~1-2h" de `27-presupuesto-parametros.md`. Se aplica el mismo modelo de facturacion vigente (`Costo = M x $16.80`).

### WBS e items

| Item | Tipo | Drivers | O (h) | M (h) | P (h) | Riesgo | Motivo M |
|---|---|---:|---:|---:|---:|---|---|
| A. Autocomplete Select2 en Egresos (reemplaza `<datalist>`) | Ajuste UI puntual | Retirar JS de v1/v2, inicializar Select2 (AJAX+tags) sobre endpoint ya existente, sin cambios de backend | 0.7 | 1.0 | 1.6 | Bajo | Widget ya cargado globalmente en el layout; el endpoint de sugerencias ya existe sin cambios |
| B. Motivo de Factura de venta: enum -> texto libre + autocomplete + migracion | Regla de negocio + migracion EF | Eliminar enum `MotivoVenta`, nuevo `SugerenciasMotivoAsync` (calcado del de Egreso), cambio de tipo de columna con backfill (RT13, riesgo bajo), Select2 en `Facturas/Create` | 1.7 | 2.5 | 4.0 | Bajo | Migracion sin ambiguedad (mapeo 1:1 de 3 valores); lógica calcada de un patron ya probado |
| **Total** | | | **2.4** | **3.5** | **5.6** | | |

### Costo por formula vigente

| Item | M (h) | Horas facturables (M/2.5x1.2) | Costo (USD) |
|---|---:|---:|---:|
| A. Select2 en Egresos | 1.0 | 0.48 | 16.8 |
| B. Motivo texto libre + migracion | 2.5 | 1.20 | 42.0 |
| **Subtotal desarrollo** | **3.5** | **1.68** | **58.8** |
| Tokens IA | — | — | No aplica (total facturable 1.68h < 4h) |
| **Total** | | | **58.8** |

### Cierre numerico (dos pasos)

- **Paso A (preliminar)**: USD 58.8.
- **Paso B (ajustado)**: sin ajustes adicionales (sin riesgo excepcional, ratio de calibracion dentro de banda). **USD 58.8** (redondeado a **USD 59** para comunicar al cliente).

### Etapa de entrega

Etapa unica:

| Area | USD |
|---|---:|
| Autocomplete Select2 (Concepto de Egreso + Motivo de Factura de venta) | 59.0 |
| **Total** | **59.0** |

### Plan de mantenimiento anual

Sin cambios (no se agregan tablas nuevas; `MotivoVenta` se elimina, no suma).

### Riesgos

- RT13 (bajo) — migracion de `Motivo` sin ambiguedad, recomendado probar en dev/staging antes de produccion como buena practica.

### Supuestos

- Se reutiliza el patron ya probado de `EgresoService.SugerenciasDetalleAsync`.
- Select2 ya esta cargado globalmente (sin costo de integracion de libreria nueva).

### Exclusiones

- Cambios en `ganaderia - fausto`.
- Cualquier reporte/filtro futuro por Motivo (queda fuera de alcance; R28 del analisis).

### Dependencias del cliente

- Aprobar el presupuesto de USD 59.0 antes de iniciar implementacion (gate duro).

### Criterios de aceptacion minimos

- PF62-PF66 y PV17-PV18 (analisis v12 §16) aprobados.
- Smoke test de navegador real (no solo revision estatica) del autocomplete en ambas pantallas, dado el antecedente de GAN-003/GAN-004.

### Condiciones comerciales

- 50% al inicio / 50% a la entrega.
- Sin clausula de validez de oferta.

---

## Iteracion v11 — Pagos multiples de Egreso (2026-07-02)

Repositorio exclusivo: `C:\Sistemas\ganaderia - emo` (NO aplica a `ganaderia - fausto`). Sistema **en produccion**; esta es una iteracion evolutiva sobre un proyecto ya cerrado, no un proyecto nuevo.

### Anclaje historico (Paso 0)

Referencia principal: el propio historico de `ganaderia` (mismo codebase, mismo patron `CuotaService`/`FacturaVentaCuota` ya implementado y probado). Modulo comparable mas cercano dentro del proyecto: `Rechazos, regularizacion y acreditacion automatica` (M historico = 10.0h base, referencia original Abril 2026). Como en v11 el patron se **copia 1:1** (no se disena desde cero), el M ajustado parte por debajo de esa mediana, documentado por item.

Se aplica el **modelo de facturacion vigente** (`27-presupuesto-parametros.md` — Modelo de facturacion Junio 2026): `Costo = M x $16.80` (M = caso mas probable, tasa USD 35/h, factor de eficiencia IA 2.5, contingencia 20% ya incluida en la formula). Se evita el metodo PERT-horas-directas-x-tasa que en este mismo proyecto produjo sobreestimacion de 3.4x-6.7x (ver Auditoria de inconsistencias I-7, `27-presupuesto-parametros.md`).

### WBS e items

| Item | Tipo | Referencia historica | Drivers | O (h) | M (h) | P (h) | Riesgo | Motivo M ajustado |
|---|---|---|---:|---:|---:|---|---|---|
| 1. Egreso multi-pago (Domain+Application+Infrastructure) | Workflow con estados | `Rechazos/regularizacion` (10.0h) | Nueva entidad `EgresoPago`, enum, `EgresoService.CreateAsync/AnularAsync` reescritos, nuevo `IEgresoPagoService` (rechazo+regularizacion 3a/3b+acreditacion cheques) | 4.5 | 6.5 | 10.0 | Medio | Por debajo de la referencia: se copia el patron ya probado de `CuotaService` en vez de disenarlo de cero |
| 2. Extension job diario (`AcreditacionCuotasHostedService` + columna `JobEjecucion`) | Ajuste sobre modulo existente | Regla de negocio nueva (0.5-2h parametro) | Agregar llamada + columna + notificacion consolidada | 1.0 | 1.5 | 2.5 | Bajo | Extension pequena sobre servicio ya activo en produccion |
| 3. Migracion EF con backfill de datos de produccion (RT9) | Migracion critica | Sin comparable directo (excede "migracion EF simple 0.5h") | Backfill SQL de `Egreso`→`EgresoPago`, `MovimientoCaja.EgresoId`→`EgresoPagoId`, validacion contra copia de produccion, backup previo | 2.5 | 3.5 | 7.0 | **Alto** | P excede el tope 1.8xM (documentado): riesgo de perdida de trazabilidad historica en sistema live justifica el sobrecosto |
| 4. UI Egresos (grilla dinamica Create+Details, `EgresoPagosController` Rechazar/Regularizar, vistas) | ABM complejo reducido | ABM complejo padre/hijos (7.7-11.5h) | Grilla dinamica de pagos con binding de lista, 2 pantallas de accion nuevas, reuso de partials existentes | 4.0 | 5.5 | 8.5 | Medio | Por debajo del rango ABM complejo completo: no hay ABM de catalogo nuevo, solo grilla + 2 acciones |
| **Total** | | | | **12.0** | **17.0** | **28.0** | | |

### Costo por formula vigente

| Item | M (h) | Horas facturables (M/2.5×1.2) | Costo formula (USD) | Riesgo excepcional | Costo final (USD) |
|---|---:|---:|---:|---|---:|
| 1. Egreso multi-pago | 6.5 | 3.12 | 109.2 | — | 109.2 |
| 2. Extension job diario | 1.5 | 0.72 | 25.2 | — | 25.2 |
| 3. Migracion con backfill (RT9) | 3.5 | 1.68 | 58.8 | +50% documentado (migracion de datos en produccion, excepcion explicita segun `27-presupuesto-parametros.md` §Modelo de facturacion) | 88.2 |
| 4. UI Egresos | 5.5 | 2.64 | 92.4 | — | 92.4 |
| **Subtotal desarrollo** | **17.0** | **8.16** | **285.6** | | **315.0** |
| Tokens IA (cargo fijo, aplica: total facturable > 4h) | — | — | — | — | 100.0 |
| **Total Etapa unica** | | | | | **415.0** |

### Cierre numerico (dos pasos)

- **Paso A (preliminar)**: 285.6 USD desarrollo (sin riesgo excepcional) + 100 USD Tokens IA = 385.6 USD.
- **Paso B (ajustado, a comunicar al cliente)**: + 29.4 USD de riesgo excepcional documentado en Item 3 (migracion de datos de produccion) = **415.0 USD**.

No se aplico doble contingencia: la formula ya incluye 20%; el +50% de Item 3 es la excepcion explicita permitida para migracion de datos, no una contingencia adicional generica.

### Etapas de entrega

Alcance chico y cohesivo — **una sola etapa** (no amerita dividir en MVP/Etapa 2):

| Area | USD |
|---|---:|
| Egresos con pagos multiples (cheque diferido, rechazo/regularizacion, job extendido, migracion de datos) | 315.0 |
| Tokens IA | 100.0 |
| **Total** | **415.0** |

### Plan de mantenimiento anual

Sin cambios: el sistema ya cuenta con plan de mantenimiento vigente (aprox. 16-18 tablas → **plan PREMIUM, USD 400/ano**, ya contratado desde el deploy a produccion de Mayo 2026). Esta iteracion no agrega tablas suficientes para cambiar de plan (+1 tabla `EgresoPago`). No se recotiza salvo pedido del cliente.

### Riesgos

- **RT9** (critico) — perdida de trazabilidad historica si el backfill de datos falla; mitigado con validacion contra copia de produccion + backup previo al deploy (ver `3-arquitecto-mvc.md` §13.4). Es el unico item con contingencia excepcional documentada.
- Alcance exclusivo de `ganaderia - emo`; si el cliente de `ganaderia - fausto` pide el mismo cambio, se recotiza aparte (no incluido).

### Supuestos

- Se reutiliza el patron ya probado de `CuotaService`/`FacturaVentaCuota` sin rediseno.
- No se modifica el modulo Ingresos ni Stock.
- El ambiente de staging/copia de produccion para validar el backfill esta disponible sin costo adicional de infraestructura.

### Exclusiones

- Cambios en `ganaderia - fausto`.
- Edicion de Egresos existentes (fuera de alcance del analisis v11).
- Rediseno de Notificaciones/Dashboard.
- Las exclusiones fijas estandar del estudio (AFIP, migracion desde sistema anterior a este, app movil, hardware externo).

### Dependencias del cliente

- Confirmar si necesita el mismo cambio en `ganaderia - fausto` (se cotizaria aparte).
- Aprobar el presupuesto de USD 415.0 antes de iniciar implementacion (gate duro).

### Criterios de aceptacion minimos

- PF53–PF61 y PV13–PV16 (analisis v11 §16) aprobados.
- Migracion validada contra copia de produccion con conteos verificados antes del deploy real.
- Egresos historicos preservan su forma de pago e importe tras la migracion.

### Condiciones comerciales

- 50% al inicio / 50% a la entrega.
- Sin clausula de validez de oferta.

### Cierre de calibracion estimado vs real (2026-07-02)

| Item | M estimado (h) | Tiempo real de sesion (agentes) | Desvio | Causa principal |
|---|---:|---:|---:|---|
| 1-4. Implementacion completa (Domain+Application+Infrastructure+Web+migracion) | 17.0 | ~12.7 min de trabajo efectivo del agente implementador (+ ~5.8 min de overhead por confusion de coordinacion, no imputable al desarrollo) | Extremo (~0.75h vs 17h) | Eficiencia de IA asistida ya documentada en este proyecto (patron 3.4x-6.7x sobre PERT); aqui el ratio es mayor aun porque se mide tiempo de pared de un agente autonomo, no horas-persona tradicionales |
| QA (PF53-PF61, PV13-PV16, migracion validada contra BD dev) | incluido en formula (parte de horas facturables) | ~31.6 min de trabajo efectivo del agente QA | Extremo | Idem — QA end-to-end contra base de datos real ejecutado en fraccion del tiempo de un ciclo QA manual tradicional |

**Advertencia metodologica**: el "tiempo real" de esta iteracion no es comparable 1:1 con las "horas reales" de cierres previos del proyecto (que median horas-persona de un desarrollador). Aqui se mide tiempo de pared (wall-clock) de agentes autonomos trabajando en paralelo/background durante una unica sesion. Se registra igual por transparencia y para reforzar el patron ya confirmado (ver `27-presupuesto-parametros.md`), pero **no se recalcula el precio retroactivamente**: el presupuesto de USD 415.0 ya fue comunicado y aprobado como precio fijo por etapa antes de iniciar, siguiendo la politica vigente del estudio.

**Leccion aprendida (proceso, no tecnica)**: hubo confusion de coordinacion entre agentId al delegar Implementacion (dos rondas sin avance real por desajuste de identificadores de agente antes de trabar contacto con el agente correcto). No afecto el resultado tecnico final (build 0 errores, QA 14/14 PASS) pero costo tiempo de orquestacion. Accion recomendada para proximas delegaciones: verificar el agentId devuelto por el spawn contra el agentId que el propio subagente reporta en su primera respuesta antes de asumir que los mensajes de seguimiento llegan al destinatario correcto.

**Ajuste de parametros recomendado**: ninguno al modelo de facturacion vigente (M/2.5x1.2x$35 ya absorbe la eficiencia de IA); no se detecto necesidad de recalibrar rangos por tipo de modulo a partir de esta iteracion.

---

## Alcance funcional resumido

Presupuesto funcional para un sistema de gestion ganadera con tres ejes principales: ingresos, egresos y stock, mas transversales de caja, dashboard, catalogos operativos, usuarios y novedades. La estimacion se basa en las definiciones vigentes de analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1.

Resumen economico recomendado:
- Horas base estimadas: 81.5 h
- Horas finales estimadas: 101.0 h
- Tasa aplicada: USD 12 / h
- Total estimado: USD 1,212
- Migraciones EF: si, 2 migraciones previstas (`Ganaderia_Catalogos` y `Ganaderia_Operativa`)

## Impacto tecnico por capa

- Presentacion: 13-14 controllers MVC, aproximadamente 26 vistas, formularios con validaciones, bandeja de novedades, upload de comprobantes y filtros historicos.
- Negocio: servicios para ventas, facturas, cuotas, stock, caja, dashboard, catalogos, usuarios, job diario e idempotencia de acreditaciones.
- Datos: 14 entidades nuevas, tabla tecnica para correlativo, 2 migraciones EF, query filters con lecturas historicas usando `IgnoreQueryFilters()` donde aplique.

## Riesgos y supuestos

- Se asume reutilizacion de componentes ya configurados en la solucion base: `SoftDestroyable`, `ServiceResult`, `IRepository<T>`, `INotificationService`, `AppDbContext`, roles Identity y convenciones MVC.
- No se contempla AFIP, migracion de datos, app mobile, hardware externo ni integraciones fuera de las ya definidas.
- Se asume despliegue single-node para el job diario en v1.
- El correlativo de facturas, la regeneracion de cuotas, el rechazo/regularizacion y las compensaciones de stock concentran el mayor riesgo funcional.
- Los ABM usan contingencia fija del 30% y dentro de esa contingencia quedan absorbidos pruebas, documentacion y riesgo ordinario; no se suman como adicionales.
- Los modulos no ABM usan contingencia variable segun riesgo del item, sin doble contingencia.

## WBS funcional vigente

| Modulo funcional | Tipo | Drivers principales | Requiere migracion EF |
|---|---|---|---|
| Catalogos base ganaderos | ABM intermedio | Grupo con stock minimo y baja logica, Rubro, Proveedor con ambito, Organismo intermediario | Si |
| Usuarios y permisos productor | ABM intermedio | alta/baja/modificacion, reset de password, limite de 5 productores, rol SuperUsuario | Si |
| Stock y movimientos | Workflow con estados | stock inicial unico, ingresos/egresos, compensaciones intra/inter categoria, matriz cerrada, alertas por stock minimo | Si |
| Ingresos: ventas, facturas y cuotas | Modulo financiero o logica sensible | venta multi-linea, factura correlativa, IVA snapshot, generacion y regeneracion de cuotas, bloqueo por estados | Si |
| Rechazos, regularizacion y acreditacion automatica | Workflow con estados | rechazo manual, opcion 3a/3b, job diario idempotente, notificacion in-app | Si |
| Egresos y comprobantes | ABM complejo | gasto, autocomplete de concepto, filtro de proveedor por ambito, comprobante adjunto, impacto en caja | Si |
| Caja y cuenta corriente | Modulo financiero o logica sensible | saldo por movimientos acreditados, filtros por estado/fecha, navegacion al origen | Si |
| Dashboard anual | Reporte o exportacion | mensualizacion por anio, comparativo, filtros por categoria y grupo, soporte historico de grupos inactivos | No adicional |

## Estimaciones PERT por item

Notas de lectura:
- `O`, `M` y `P` estan expresados en horas base por modulo completo.
- `Implementacion`, `Pruebas`, `Documentacion` y `Riesgo` son distribucion interna del esfuerzo final del modulo.
- En ABM con contingencia fija del 30%, pruebas, documentacion y riesgo ordinario ya estan absorbidos dentro de ese 30%.

| Modulo funcional | Tipo | Referencia historica usada | O | M | P | Horas PERT base | Implementacion | Pruebas | Documentacion | Riesgo | Contingencia | Horas finales | USD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| Catalogos base ganaderos | ABM intermedio | Recotrack/Lumitrack/Piapartments ABM intermedio + Delicias ABM Categorias/Proveedores | 13.0 | 15.0 | 18.0 | 15.2 | 14.0 | 2.7 | 0.8 | 2.2 | Fija 30% | 19.7 | 236.4 |
| Usuarios y permisos productor | ABM intermedio | Recotrack ABM Usuarios + Lumitrack ABM Usuarios | 4.5 | 5.5 | 7.0 | 5.6 | 5.2 | 1.0 | 0.3 | 0.8 | Fija 30% | 7.3 | 87.6 |
| Stock y movimientos | Workflow con estados | Lumitrack ABM Relevamientos + ABM intermedio historico + Delicias ABM Pedidos | 12.0 | 14.0 | 17.0 | 14.2 | 13.2 | 2.3 | 0.7 | 1.5 | Variable 25% | 17.7 | 212.4 |
| Ingresos: ventas, facturas y cuotas | Modulo financiero o logica sensible | Delicias ABM Ventas + Gestion de pedidos + ABM Pagos | 15.0 | 18.0 | 22.0 | 18.2 | 16.9 | 3.0 | 0.8 | 2.0 | Variable 25% | 22.7 | 272.4 |
| Rechazos, regularizacion y acreditacion automatica | Workflow con estados | Delicias Notificaciones SignalR + workflow de pedidos como comparable de estados | 8.0 | 10.0 | 13.0 | 10.2 | 8.8 | 1.9 | 0.5 | 1.5 | Variable 25% | 12.7 | 152.4 |
| Egresos y comprobantes | ABM complejo | Delicias ABM Pagos + ABM Proveedores + ajuste por upload/autocomplete | 6.5 | 8.0 | 10.0 | 8.1 | 6.7 | 1.4 | 0.4 | 0.8 | Variable 15% | 9.3 | 111.6 |
| Caja y cuenta corriente | Modulo financiero o logica sensible | Delicias ABM Pagos + consulta operativa comparable | 4.0 | 5.0 | 6.5 | 5.1 | 4.2 | 0.9 | 0.2 | 0.5 | Variable 15% | 5.8 | 69.6 |
| Dashboard anual | Reporte o exportacion | mezcla de consulta historica comparable + filtro anual/mensual | 4.0 | 5.0 | 6.0 | 5.0 | 4.1 | 0.9 | 0.3 | 0.5 | Variable 15% | 5.8 | 69.6 |
| **Total** |  |  | **67.0** | **80.5** | **99.5** | **81.5** | **73.1** | **14.1** | **4.0** | **9.8** |  | **101.0** | **1,212.0** |

## Tasa vigente y contingencia aplicada

- Tasa aplicada: USD 12 / hora.
- Contingencia fija 30%: `Catalogos base ganaderos`, `Usuarios y permisos productor`.
- Contingencia variable 25%: `Stock y movimientos`, `Ingresos: ventas, facturas y cuotas`, `Rechazos, regularizacion y acreditacion automatica`.
- Contingencia variable 15%: `Egresos y comprobantes`, `Caja y cuenta corriente`, `Dashboard anual`.
- No se aplico doble contingencia sobre referencias historicas que ya venian con 30% incluido: primero se normalizaron a horas base.

## Calibraciones historicas usadas

- `/docs/recotrack/definiciones/4-presupuestador.md`: ABM simple e intermedio con 30% incluido.
- `/docs/lumitrack/definiciones/4-presupuestador.md`: ABM intermedio y ABM complejo con 30% incluido.
- `/docs/piapartments/definiciones/4-presupuestador.md`: ABM intermedio con 30% incluido.
- `/docs/delicias-naturales/definiciones/4-presupuestador.md`: workflows, ventas, pagos, compras, proveedores, notificaciones.
- `/docs/vinosefue/definiciones/4-presupuestador.md`: referencia global de proyecto con workflows y alta complejidad por modulo.
- `/docs/eleven-la-plata/definiciones/4-presupuestador.md`: referencia global de proyecto de complejidad media.

## Autocorreccion pre-cierre

| Modulo funcional | Mediana historica base comparable | Base preliminar | Ratio preliminar | Ajuste aplicado | Base final | Ratio final | Motivo del ajuste |
|---|---:|---:|---:|---|---:|---:|---|
| Catalogos base ganaderos | 16.9 | 16.0 | 0.95 | -0.8 h | 15.2 | 0.90 | se desconto sinergia por reutilizacion del mismo patron ABM y componentes compartidos |
| Usuarios y permisos productor | 5.0 | 5.5 | 1.10 | +0.1 h | 5.6 | 1.12 | se mantuvo cercano a la mediana por limite de 5 usuarios y reset de password |
| Stock y movimientos | 12.7 | 15.0 | 1.18 | -0.8 h | 14.2 | 1.12 | se bajo para no salir de banda, manteniendo sobrecosto solo por matriz y compensaciones |
| Ingresos: ventas, facturas y cuotas | 19.2 | 19.0 | 0.99 | -0.8 h | 18.2 | 0.95 | se reconoce reutilizacion de patrones MVC/EF pero se conserva complejidad financiera central |
| Rechazos, regularizacion y acreditacion automatica | 11.2 | 10.5 | 0.94 | -0.3 h | 10.2 | 0.91 | se corrigio a la baja por reaprovechar notificaciones y servicio existente de jobs |
| Egresos y comprobantes | 9.2 | 8.5 | 0.92 | -0.4 h | 8.1 | 0.88 | se mantuvo por debajo de la mediana al no incluir AFIP ni integraciones externas |
| Caja y cuenta corriente | 5.3 | 5.0 | 0.94 | +0.1 h | 5.1 | 0.96 | se ajusto por necesidad de navegacion al origen y saldo por estado acreditado |
| Dashboard anual | 5.0 | 4.8 | 0.96 | +0.2 h | 5.0 | 1.00 | se sumo esfuerzo por filtros historicos y grupos inactivos en periodos previos |

Resumen de autocorreccion:
- Total preliminar base: 84.3 h
- Total final base ajustado: 81.5 h
- Total final con contingencia: 101.0 h
- Total final USD: 1,212.0

## Pruebas funcionales minimas requeridas

- Alta/edicion/anulacion de ventas sin factura y bloqueo con factura emitida.
- Emision de factura con correlativo unico, IVA snapshot y cuotas 30/60/90 con redondeo correcto.
- Rechazo de cuota desde `Pendiente` y `Acreditada`, con mutacion correcta del movimiento de caja.
- Regularizacion opcion 3a y 3b sin duplicar saldo ni romper auditoria.
- Job diario idempotente: acredita una sola vez y genera novedades del dia.
- Alta de gasto con proveedor filtrado por ambito, autocomplete de concepto y comprobante valido/invalido.
- Carga de stock inicial unica por grupo, compensaciones intra/inter categoria y bloqueo fuera de matriz.
- Baja logica de grupo solo con stock cero y presencia historica de grupos inactivos en consultas previas.
- Caja con saldo calculado solo por movimientos acreditados.
- Dashboard anual con filtros por categoria y grupo, incluyendo historia de grupos inactivos.

## Checklist de salida para merge

- [ ] 2 migraciones EF creadas y validadas (`Ganaderia_Catalogos`, `Ganaderia_Operativa`).
- [ ] Roles `Productor` y `SuperUsuario` sembrados correctamente.
- [ ] Tabla contador para factura inicializada y protegida contra concurrencia.
- [ ] Controllers sin logica de negocio compleja.
- [ ] Services con `ServiceResult`/`ServiceResult<T>` y operaciones transaccionales en flujos criticos.
- [ ] Validaciones de stock, matriz de transiciones, cuotas y comprobantes cubiertas funcionalmente.
- [ ] `NotificationService` o equivalente reutilizado para novedades in-app.
- [ ] Query historicas con `IgnoreQueryFilters()` donde se necesite ver grupos inactivos.
- [ ] Endpoint autenticado para descarga de comprobantes fuera de `wwwroot`.
- [ ] Pruebas funcionales minimas ejecutadas sobre ventas, facturas, cuotas, stock, gastos, caja y dashboard.

## Cierre de calibracion estimado vs real

**PROYECTO CERRADO (2026-07-03): total real Etapa 1 + Etapa 2 = 20 h.** Reemplaza la proyeccion anterior de ~30 h — este es el dato definitivo de cierre, no una proyeccion.

| Entrega | Horas estimadas | Horas reales | Desvio % | Motivo |
|---|---:|---:|---:|---|
| Etapa 1 — primera entrega | 81.5 h (base total) | 12 h | −85.3% | Sobreestimacion sistematica. |
| Etapa 1 — total con reentrega | 81.5 h (base total) | ~15 h | −81.6% | Reentrega incluida. Dato confirmado Junio 2026. |
| **Total proyecto (Etapa 1 + Etapa 2) — CIERRE REAL** | 81.5 h (base) / 101.0 h (con contingencia) | **20 h** | **−75.5% (vs base) / −80.2% (vs contingencia)** | Cierre definitivo confirmado 2026-07-03. Etapa 2 real fue menor a lo proyectado (~5 h reales vs ~15 h proyectadas). |

- Ratio PERT base/real: 81.5 / 20 = **4.08x**
- Ratio PERT con contingencia/real: 101.0 / 20 = **5.05x** — el mas alto del dataset, supera a ShowroomGriffin (4.0x) y a la propia proyeccion previa de Ganaderia (3.4x sobre 30 h proyectadas).
- Horas formula vigente (M/2.5×1.2 sobre M total = 80.5 h): 38.64 h → ratio formula/real = 38.64 / 20 = **1.93x** (segundo mas alto del dataset; ShowroomGriffin 1.6x, contadores-bma-conversor 0.66x).

### Precio comercial final (corregido 2026-07-03 — reemplaza el registro anterior de USD 1.212)

El **precio final efectivamente cobrado al cliente fue USD 950**, no USD 1.212 (ese numero era la estimacion interna via PERT × tasa historica USD 12/h, nunca facturada tal cual). El cierre comercial real fue:

- **Total facturado: USD 950**, con **15% de descuento por referido ya aplicado** (mismo tipo de descuento usado en contadores-bma-conversor).
- Incluye el **primer año del plan de mantenimiento anual (USD 300)** empaquetado dentro de esos USD 950 — no se cobro aparte.
- Desarrollo puro implicito: USD 950 − USD 300 (valor del 1er año de mantenimiento) = **USD 650**.
- Plan anual continuo desde el 2do año: **USD 300/año** (tarifa estandar, sin descuento — el 15% referido aplico solo al paquete inicial).

Tasa efectiva real sobre el cierre:
- Sobre el total facturado (950 / 20 h): **USD 47.5/h**.
- Sobre desarrollo puro, descontando el valor del mantenimiento (650 / 20 h): **USD 32.5/h** — **muy cercano al objetivo vigente de USD 35/h**, a diferencia de lo que sugeria el calculo anterior (USD 60.6/h) que no separaba mantenimiento ni descuento.
- Equivalente bajo el modelo nuevo (real × USD 35/h): 20 h × USD 35 = USD 700 de desarrollo → el desarrollo real (USD 650) quedo **USD 50 por debajo** de ese equivalente, no USD 512 por encima como se habia calculado antes de conocer el precio comercial real.

**Este proyecto queda fijado como referencia comercial para futuros presupuestos** (alcance: 8 modulos funcionales — catalogos, usuarios, stock, ingresos con facturacion/cuotas, rechazos/regularizacion/job diario, egresos, caja, dashboard anual — con 2 migraciones EF, workflows de estados y logica financiera): **20 h reales de desarrollo ≈ USD 650 de desarrollo puro a tasa efectiva ~USD 32.5/h**, con plan de mantenimiento PREMIUM USD 300/año. Al usar esta referencia para anclar M en un proyecto nuevo de alcance funcional comparable (8-11 modulos, mezcla ABM+workflow+financiero), partir de esta relacion horas-reales/funcionalidad en vez de las 101.0 h PERT originales, que sobreestimaron 5.05x.

Nota de calibracion: el ratio PERT-con-contingencia/real de 5.05x (en horas) sigue siendo el mas alto confirmado en el dataset. Pero en terminos de **precio**, corregido el error de no separar mantenimiento y descuento, este cierre en realidad valida el objetivo de USD 35/h en vez de contradecirlo — la sobreestimacion esta en las HORAS del metodo PERT, no en la tarifa por hora real aplicada. Refuerza la conclusion ya documentada: el metodo PERT sin anclaje en horas reales IA sobreestima sistematicamente las horas en proyectos con IA asistida. El factor de eficiencia 2.5 de la formula vigente sigue sin recalibrarse (atado al cierre de Energy Nutrition), pero este dato (ratio formula/real 1.93x en horas) sigue siendo evidencia a favor de subirlo en esa instancia futura.

## Historial de ajustes

- 2026-04-22: presupuesto inicial ejecutado sobre analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1, con calibracion contra datasets Abril 2026 y estructura de trazabilidad creada para el proyecto.
- 2026-06-02: cierre parcial registrado. Primera entrega: 15 h reales (valor provisional). Total proyectado al 100%: 30 h maximas. Desvio confirmado: ~−70%. Patron de sobreestimacion sistematica registrado.
- 2026-06-03: primera entrega corregida a 12 h reales definitivas (MVP Etapa 1). Costo: USD 144 a tasa USD 12/h. Desvio vs estimado base: −85.3%.
- 2026-06-08: Etapa 1 total con reentrega actualizada a ~15 h reales. Total proyecto proyectado: ~30 h. Analisis economico comparativo incorporado. Tasa efectiva real: USD 40.4/h (precio fijo) vs USD 35/h objetivo nuevo modelo.
- 2026-07-03: **PROYECTO CERRADO.** Total real definitivo Etapa 1 + Etapa 2 = 20 h (reemplaza la proyeccion de ~30 h; corregido desde un registro previo de 18 h el mismo dia). Ratio PERT-contingencia/real = 5.05x (record del dataset). Ratio formula-vigente/real = 1.93x. Dato incorporado a `27-presupuesto-parametros.instructions.md` como referencia historica de cierre real.
- 2026-07-03 (mismo dia, correccion posterior): **Precio comercial real corregido.** El precio efectivamente facturado fue **USD 950** (no USD 1.212, que era solo la estimacion interna PERT × USD 12/h nunca facturada). USD 950 incluye 15% de descuento por referido ya aplicado + el primer año del plan de mantenimiento (USD 300) empaquetado. Desarrollo puro implicito: USD 650 ≈ USD 32.5/h efectivo — cercano al objetivo USD 35/h (no USD 60.6/h como se habia calculado antes de separar mantenimiento y descuento). Plan anual continuo desde el 2do año: USD 300/año. **Proyecto fijado como referencia comercial para futuros presupuestos de alcance similar** (8 modulos, ABM+workflow+financiero).