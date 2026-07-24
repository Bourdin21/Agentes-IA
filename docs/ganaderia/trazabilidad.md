# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-07-23 - orquestador (barrido cross-proyecto) — mergeada iteracion v13 (delivery post-reunion con cliente) desde la carpeta local del proyecto
- Etapa: 5 - Implementacion (mergeo retroactivo de memoria)
- Cambio: se detecto que el repo local `C:\Sistemas\ganaderia - emo\docs\ganaderia\` tenia una entrega completa (analisis `6-analisis-mejoras-entrega2.md` + entrada de implementacion en su propio `5-implementador.md`, ambos fechados 2026-07-22/23) que nunca se habia mergeado a este repo central. Se incorporo como "Iteracion v13" en `definiciones/5-implementador.md`: (1) fix de bug transversal de formularios (`asp-items` sin `asp-for` en 2 grillas dinamicas indexadas), (2) fila de totales en listados de Egresos y Facturas, (3) rename end-to-end `Cuotas`→`Ingresos` (entidad, enum, FK, controller, vistas, migracion `RenameCuotaToIngreso`), (4) Dashboard dividido en `/Dashboard` (stock puro, con kg vendidos y precio promedio ponderado por kg) y `/Dashboard/TableroAnual` (dinero puro, con filtro mes), (5) Facturas de venta con IVA/IngresosBrutos/OtrasPercepciones editables independientemente (migracion `FacturaVenta_ImpuestosEditables`, reescrita a mano para evitar corrupcion de montos historicos) e Ingresos (ex-cuotas) 100% personalizables por el usuario.
- Motivo: pedido explicito del usuario de auditar cada carpeta de proyecto individual en busca de especificaciones que debieran vivir en la memoria centralizada de Agentes-IA, y mergearlas.
- Impacto en capas: Domain/Application/Infrastructure/Web (ver detalle completo en `5-implementador.md` iteracion v13).
- Riesgos/supuestos: **riesgo operativo abierto de alta prioridad** — las 4 migraciones de esta entrega (incluidas 2 de iteraciones previas aun no deployadas) ya fueron aplicadas contra la base de produccion el 2026-07-23 **sin backup previo** (herramientas de backup no disponibles en el entorno de esa sesion; riesgo aceptado explicitamente por el cliente), y el deploy del codigo nuevo a produccion **todavia esta pendiente** — la base de prod tiene el esquema nuevo pero la app publicada corre codigo viejo. Ver seccion dedicada en `5-implementador.md` iteracion v13.

### 2026-07-03 - presupuestador — precio comercial real corregido + Ganaderia fijado como proyecto de referencia
- Etapa: 8 - Cierre de calibracion (correccion posterior el mismo dia)
- Cambio: el precio efectivamente facturado al cliente fue **USD 950** (no USD 1.212, que era la estimacion interna via PERT × tasa historica USD 12/h, nunca cobrada tal cual). Los USD 950 incluyen 15% de descuento por referido ya aplicado y el primer año del plan de mantenimiento (USD 300) empaquetado dentro del precio. Desarrollo puro implicito: USD 650 ≈ USD 32.5/h efectivo — cercano al objetivo vigente de USD 35/h (a diferencia del calculo previo de USD 60.6/h que no separaba mantenimiento ni descuento). Plan anual continuo desde el 2do año: USD 300/año. `4-presupuestador.md` y `27-presupuesto-parametros.instructions.md` actualizados con el precio corregido. **Ganaderia queda fijado explicitamente como proyecto de referencia comercial** para presupuestar futuros sistemas de alcance funcional similar (8-11 modulos, mezcla ABM+workflow+financiero), anclando en la relacion horas-reales/funcionalidad-entregada en vez de las horas PERT originales.
- Motivo: pedido explicito del usuario de fijar ganaderia como referencia de futuros presupuestos en base a la funcionalidad entregada y lo que costo realmente desarrollarla.
- Impacto en capas: N/A (documentos de calibracion/comerciales).
- Riesgos/supuestos: ninguno nuevo. El factor de eficiencia 2.5 de la formula vigente sigue sin recalibrarse (atado al cierre de Energy Nutrition); el ratio de horas (no de tarifa) sigue siendo la evidencia relevante para esa futura recalibracion.

### 2026-07-03 - presupuestador — cierre de calibracion final del proyecto (proyecto cerrado)
- Etapa: 8 - Cierre de calibracion
- Cambio: cierre real definitivo del proyecto base (Etapa 1 + Etapa 2): **20 h reales totales** (corregido el mismo dia desde un registro previo de 18 h), reemplazando la proyeccion previa de ~30 h. `4-presupuestador.md` actualizado con el detalle del cierre (ratio PERT-contingencia/real 5.05x, ratio formula-vigente/real 1.93x, ambos entre los mas altos del dataset del estudio). Dato incorporado a `.github/instructions/27-presupuesto-parametros.instructions.md`: nueva fila en la tabla de referencia de proyectos, actualizacion de las tablas de ratio PERT/real y de sobreestimacion sistematica, ajuste del rango real historico para proyectos de 8-11 modulos (25-30h → 20-30h), y nota en "Notas de calibracion" fechada 2026-07-03.
- Motivo: pedido explicito del usuario de calibrar el presupuestador del estudio con el cierre real de este proyecto finalizado.
- Impacto en capas: N/A (documentos de calibracion/comerciales).
- Riesgos/supuestos: el factor de eficiencia 2.5 de la formula vigente (`M/2.5×1.20×$35`) NO se modifico unilateralmente por este cierre — la politica vigente ata ese recalibrado al cierre de Energy Nutrition. Este dato queda documentado como evidencia adicional a favor de subirlo en esa instancia futura.

### 2026-07-02 - implementador-dotnet (iteración v12) — Select2 autocomplete (Egresos.Concepto, FacturaVenta.Motivo)
- Etapa: 5 - Implementación
- Cambio: reemplazo del `<datalist>` nativo por Select2 (AJAX + `tags:true`) en `Egresos/Create` (Concepto), reutilizando el endpoint existente `Egresos/SugerenciasDetalle`. `FacturaVenta.Motivo` migrado de enum cerrado (`MotivoVenta`, eliminado del Domain) a texto libre con Select2 sobre nuevo endpoint `Facturas/SugerenciasMotivo` (`IFacturaVentaService.SugerenciasMotivoAsync`, calcado 1:1 de `EgresoService.SugerenciasDetalleAsync`). Script JS único reutilizable `wwwroot/js/ov-autocomplete-select2.js`. Migración EF `FacturaVenta_MotivoTexto` (3 fases: columna nueva + backfill textual `1→Faena/2→Vacía/3→Enfermedad` + drop/rename), generada con `dotnet ef migrations add` y con `Up()`/`Down()` reescritos a mano para evitar el `AlterColumn` directo `int→varchar` (cast numérico) que el scaffold automático proponía por defecto.
- Motivo: pedido evolutivo del cliente (proyecto `ganaderia - emo` exclusivamente) — reemplazar el `<datalist>` nativo (defecto de UX conocido, `6-qa.md` §12/GAN-004) por un widget confiable y extender el mismo patrón de autocomplete a Motivo de Factura de venta.
- Impacto en capas: Domain (`FacturaVenta.Motivo` a `string`, eliminación de `MotivoVenta.cs`), Application (`IFacturaVentaService` con nuevo método), Infrastructure (`FacturaVentaService.SugerenciasMotivoAsync`, `AppDbContext` fluent config, migración EF), Web (`FacturasController.SugerenciasMotivo`, `FacturaVentaCreateVm.Motivo` a `string`, vistas `Egresos/Create.cshtml` y `Facturas/Create.cshtml`, script JS nuevo).
- Riesgos/supuestos: RT13 (riesgo bajo, mapeo backfill 1:1 sin ambigüedad) — se recomienda correr la migración primero contra staging antes de producción. Migración NO ejecutada contra ninguna base en esta sesión (sin conexión disponible en el entorno). Build `dotnet build` OK, 0 errores. Pendiente para QA: PF62–PF66 + PV17–PV18, y smoke test de navegador real de ambos Select2 antes de cerrar. `ganaderia - fausto` no tocado.

### 2026-07-02 - orquestador — gate presupuesto v12 aprobado
- Etapa: Gate — Presupuesto v12 aprobado por el cliente
- Cambio: presupuesto de la iteración v12 (USD 59.0, etapa única) aprobado. Se habilita el inicio de Implementación.
- Motivo: cumplir el gate duro "no iniciar Implementación sin presupuesto aprobado por el cliente".
- Impacto en capas: N/A.
- Riesgos/supuestos: ninguno nuevo.

### 2026-07-02 - presupuestador (iteración v12) — gate cliente
- Etapa: 4 - Presupuesto (autocomplete Select2) — **gate cliente**
- Cambio: `4-presupuestador.md` ampliado con "Iteración v12". WBS de 2 items (Select2 en Egresos, Motivo texto libre + migración), M total 3.5h, costo por fórmula vigente = USD 58.8 (sin cargo de Tokens IA por ser < 4h facturables). Total a comunicar: **USD 59.0**, etapa única.
- Motivo: anclar en el patrón ya calibrado del propio proyecto (item "extensión job diario" de v11).
- Impacto en capas: N/A (documento comercial).
- Riesgos/supuestos: **pendiente de aprobación explícita del cliente antes de iniciar Implementación** (gate duro).

### 2026-07-02 - arquitecto-mvc (iteración v12)
- Etapa: 3 - Arquitectura técnica (autocomplete Select2 de Concepto/Motivo)
- Cambio: `3-arquitecto-mvc.md` actualizado a v3 (§15). `FacturaVenta.Motivo` pasa de enum a `string(200)` NOT NULL (enum `MotivoVenta` eliminado); migración con backfill de menor riesgo que la de v2 (RT13, mapeo 1:1 sin ambigüedad, no requiere validación obligatoria contra copia de producción). Nuevo `IFacturaVentaService.SugerenciasMotivoAsync` calcado de `SugerenciasDetalleAsync`. Se retira el `<datalist>`/fetch manual de Egresos y se unifica el widget en un script JS reutilizable (`ov-autocomplete-select2.js`) para ambas pantallas.
- Motivo: traducir el diseño v3 a componentes técnicos concretos grounded en el código real.
- Impacto en capas: Domain (-1 enum, cambio de tipo de propiedad), Application (+1 método), Infrastructure (+1 implementación, 1 migración EF, config de AppDbContext), Web (1 acción nueva, 2 vistas modificadas, 1 script JS nuevo compartido).
- Riesgos/supuestos: RT13 (riesgo bajo, recomendado probar en dev/staging antes de producción como buena práctica, no obligatorio como RT9).

### 2026-07-02 - disenador-funcional (iteración v12)
- Etapa: 2 - Diseño funcional (autocomplete Select2 de Concepto/Motivo)
- Cambio: `2-disenador-funcional.md` actualizado a v3 (§8.1/§8.2). Widget Select2 único reutilizable (AJAX + tags) para Concepto de Egreso y Motivo de Factura de venta; nuevo contrato `IFacturaVentaService.SugerenciasMotivoAsync` simétrico al ya existente de Egreso. `FacturaVentaCreateVm.Motivo` cambia de enum a `string`.
- Motivo: traducir el análisis v12 a diseño implementable, reutilizando el patrón de sugerencias ya probado en Egresos.
- Impacto en capas: Presentación (2 pantallas, 1 componente JS reutilizable), Negocio (1 contrato nuevo simétrico).
- Riesgos/supuestos: RD9 (retirar código muerto del datalist viejo), RD10 (Motivo pierde lista cerrada), RD11 (migración de dato en producción, detallada en arquitectura v3).

### 2026-07-02 - analista-funcional (iteración v12)
- Etapa: 0-1 - Discovery + Análisis (autocomplete Select2 de Concepto/Motivo)
- Cambio: `1-analista-funcional.md` actualizado a v12. Autocomplete de Concepto (Egresos) migra de `<datalist>` a **Select2** (ya cargado globalmente, sin dependencias nuevas — se descartó Selectize por no ser el estándar del estudio). En Facturas de venta, `Motivo` deja de ser enum cerrado (`Faena`/`Vacía`/`Enfermedad`) y pasa a texto libre con autocomplete Select2, mismo patrón que Concepto. Agregadas PF62–PF66, PV17–PV18.
- Motivo: pedido explícito del cliente; se verificó primero (grep de uso) que `Motivo` no participa en ninguna lógica de negocio, sólo se persiste y se muestra, por lo que la conversión de enum a texto libre es segura.
- Impacto en capas: Presentación (Select2 en 2 pantallas), Negocio (nuevo endpoint de sugerencias para Motivo, simétrico al de Concepto), Datos (columna `FacturaVenta.Motivo` cambia de `int` a `string`, con backfill de datos históricos).
- Riesgos/supuestos: cambio exclusivo de `ganaderia - emo`. R27 (backfill de Motivo debe preservar valores históricos), R28 (pérdida de lista cerrada para reportes futuros, sin impacto actual verificado).

### 2026-07-02 - orquestador (bugfix post-release, reportado por usuario)
- Etapa: Post-QA — fix de 2 bugs reportados en uso real sobre `Egresos/Create`
- Cambio: usuario reportó "no anda el autocomplete de Concepto" y "no anda el botón de agregar pago". Reproducidos con Playwright headless contra la app real (`https://localhost:7200`, login SuperUsuario seed) antes de tocar código. **GAN-003 (major, corregido)**: el botón "Agregar pago" no agregaba filas porque la plantilla usaba `<script type="text/x-template">` con un `<partial>` de Razor adentro — Razor no procesa Tag Helpers dentro de `<script>` (raw text element de HTML5), el JS recibía el texto Razor sin procesar. Fix: `<script type="text/x-template">` → `<template>` (elemento HTML5 nativo, sí compatible con Tag Helpers), JS de `.textContent` a `.innerHTML`. Verificado end-to-end con Playwright: agregar/quitar filas con reindexado correcto, y alta completa de un Egreso con 2 pagos desde el navegador real. **GAN-004 (minor, corregido)**: el autocomplete de Concepto funcionaba correctamente a nivel de datos (endpoint + DOM verificados con Playwright), pero es un quirk conocido de `<datalist>` nativo que no siempre refresca el desplegable visible tras poblarse async; se agregó un nudge (reasignar el atributo `list`) como workaround estándar no disruptivo.
- Motivo: corregir defectos de UI no detectados por QA v11 porque esa etapa validó el binding del servidor con POST HTTP directo (sin JS real) en vez de un smoke test de navegador — hueco explícitamente documentado en `6-qa.md` §11 como pendiente.
- Impacto en capas: Web únicamente (`Ganaderia.Web/Views/Egresos/Create.cshtml`). Sin cambios de esquema ni migración EF.
- Riesgos/supuestos: ambos catalogados en `docs/qa/regresiones-manuales.yml` (GAN-003, GAN-004) y en `6-qa.md` §12. GAN-004 no es 100% verificable por automatización headless (popup nativo del navegador); queda pendiente de una validación visual manual. Lección de proceso registrada: JS de UI no trivial (grillas dinámicas, autocomplete) requiere smoke test real de navegador antes de cerrar QA, no sólo revisión estática + binding por HTTP.

### 2026-07-02 - orquestador (cierre iteracion v11)
- Etapa: 7-8 - Documentacion + Cierre de calibracion (pagos multiples de Egreso)
- Cambio: creado `7-documentador.md` (primera vez para este proyecto, desde plantilla) con el resumen de entrega en lenguaje de negocio. `4-presupuestador.md` ampliado con "Cierre de calibracion estimado vs real (2026-07-02)": tiempo real de sesion de agentes (~12.7 min implementacion + ~31.6 min QA) vs M estimado (17.0h), con advertencia metodologica explicita (wall-clock de agentes autonomos no equivale a horas-persona) y sin recalculo retroactivo del precio fijo ya aprobado (USD 415.0).
- Motivo: cerrar el ciclo completo Discovery -> Cierre de calibracion para la iteracion v11, dejando trazabilidad para el cliente y para futuras calibraciones del estudio.
- Impacto en capas: N/A (documentos de cierre).
- Riesgos/supuestos: leccion de proceso registrada (confusion de agentId al delegar Implementacion, sin impacto en el resultado tecnico final). Pendiente real de negocio: aplicar la migracion en produccion con backup previo (RT9), fuera del alcance de este ciclo de agentes.

### 2026-07-02 - qa-mvc
- Etapa: 6 - QA (pagos múltiples de Egreso, iteración v11) — end-to-end contra app real
- Cambio: ejecución completa de PF53–PF61 y PV13–PV16 del análisis funcional v11 **end-to-end** (login autenticado, POST HTTP reales con antiforgery token contra `https://localhost:7200`, MySQL 8 local `ganaderia_dev` — servicio Windows ya corriendo, no simulado). Se aplicó y validó la migración `20260702181125_EgresoPago_PagosMultiples` contra `ganaderia_dev` (RT9 mitigado en entorno dev: `dotnet ef database update` OK, las 3 queries de validación documentadas en la propia migración dieron resultado correcto: `COUNT(Egresos)==COUNT(EgresoPagos)`, `MovimientosCaja.EgresoPagoId` poblado 1:1 respecto al `EgresoId` previo, 0 `EgresoPago` vigentes sin `MovimientoCaja`). Se forzó dos veces la corrida del job diario (`AcreditacionCuotasHostedService`, manipulando `JobEjecuciones` en la BD dev) para probar PF57 (acreditación de cheque vencido) y PF58 (idempotencia, segunda corrida no duplica). Se verificó el saldo de caja con deltas exactos en cada paso de PF59/PF60/PF61. Se verificó la regresión de `CajaService`/`Caja/Index.cshtml` (ajuste no previsto por el implementador) habilitando temporalmente el feature flag `Features:Etapa2` (deshabilitado por defecto, preexistente, no relacionado con v11) — drill-down a Egresos funcional. **Defecto encontrado y corregido (auto-fix, BUG-G-009 / GAN-001 en catálogo cross-proyecto)**: el guard "al menos un pago" en `EgresosController.Create` nunca se disparaba por su condición original (el model binder de MVC no vacía `vm.Pagos` cuando el POST no envía ningún `Pagos[i].*`, preserva el valor por defecto del constructor: 1 fila con `Importe=0`); el bloqueo funcional ya era correcto por casualidad (vía `[Range]` del importe), pero el mensaje era engañoso. Corregido cambiando el guard a `vm.Pagos.All(p => p.Importe <= 0)`. Se documentó además GAN-002 (no bug): el backfill de la migración deja `FechaVencimiento=NULL` en cheques históricos migrados, comportamiento esperado (el modelo v10 no tenía ese campo), catalogado para evitar falso positivo en QA futuro.
- Motivo: validación funcional formal de la iteración v11 antes de autorizar el merge/deploy, con evidencia real contra BD (no solo revisión estática) dado que había MySQL disponible localmente.
- Impacto en capas: Web (`Ganaderia.Web/Controllers/EgresosController.cs`, guard de validación corregido). Ningún cambio de esquema ni de lógica de negocio.
- Riesgos/supuestos: RT9 validado en entorno dev (`ganaderia_dev`, dataset pequeño); la validación contra copia real de producción con dataset grande sigue pendiente, responsabilidad del equipo de despliegue. Smoke test de navegador real (foco de inputs, click en agregar/quitar fila) no ejecutado por falta de herramienta de automatización de UI en este entorno — se validó el binding del servidor enviando `Pagos[0..2]` indexados manualmente por HTTP (PF55), lo cual prueba la capa de servidor pero no el comportamiento del JS en un navegador real. Veredicto: **apto para release con deuda técnica documentada** (no bloqueado). Ver `6-qa.md` sección "Iteración v11" para el detalle completo.

### 2026-07-02 - implementador-dotnet
- Etapa: 5 - Implementacion (pagos multiples de Egreso, iteracion v11)
- Cambio: implementado el modulo de pagos multiples de Egreso en `C:\Sistemas\ganaderia - emo` (exclusivo, `ganaderia - fausto` no tocado). Nueva entidad `EgresoPago` (Domain) + enum `EstadoPagoEgreso`; `MovimientoCaja.EgresoId` reemplazado por `EgresoPagoId`; `EgresoService.CreateAsync/AnularAsync` reescritos con validaciones de suma exacta y propagacion de baja logica; nuevo `EgresoPagoService` calcado 1:1 de `CuotaService` (rechazo, regularizacion 3a/3b, acreditacion de cheques vencidos); `AcreditacionCuotasHostedService` extendido (no duplicado) para procesar tambien pagos de egreso; nuevo `EgresoPagosController` + vistas `Rechazar`/`Regularizar`; `Egresos/Create` con grilla dinamica de pagos (JS, reindexado `Pagos[i]`); `Egresos/Details` con tabla de pagos y acciones. Migracion EF `20260702181125_EgresoPago_PagosMultiples` reescrita manualmente en 3 fases (schema aditivo -> backfill SQL -> drop destructivo) porque el `Up()` auto-generado por EF perdia la trazabilidad historica de los Egresos ya cargados en produccion. Ajustes no previstos explicitamente en el diseño pero necesarios para compilar: `CajaService.ListAsync` y `Caja/Index.cshtml` tambien consumian la FK vieja `MovimientoCaja.Egreso` para drill-down y se adaptaron a `EgresoPago.Egreso`.
- Motivo: implementar el alcance aprobado en presupuesto (USD 415.0, gate cliente OK) siguiendo la arquitectura §13 de `3-arquitecto-mvc.md`, que tiene prioridad sobre el plan v1 (§1-12) del mismo documento.
- Impacto en capas: Domain (+1 entidad, +1 enum, +1 columna en `JobEjecucion`), Application (+1 interfaz, cambio de firma de `EgresoCreateInput`), Infrastructure (+1 servicio nuevo, 2 servicios existentes modificados, hosted service extendido, DI actualizado, 1 migracion EF con backfill), Web (+1 controller, +1 ViewModel con lista anidada, +4 vistas nuevas, 4 vistas existentes modificadas).
- Riesgos/supuestos: RT9 (critico, heredado) — el backfill de la migracion NO fue ejecutado ni validado contra ninguna base de datos en esta sesion; queda documentado con queries de validacion comentadas en el propio archivo de migracion, a cargo del equipo de despliegue con backup previo de `Egresos`/`MovimientosCaja`. RT10/RT11/RT12 cubiertos segun arquitectura. Sin match de reutilizacion cross-proyecto (escaneado `docs/*/definiciones/5-implementador.md`); referencia unica es intra-proyecto (`CuotaService`). Build OK en Debug y Release (0 errores). Pruebas funcionales PF53-PF61/PV13-PV16 quedan pendientes de ejecucion por QA.

### 2026-07-02 - orquestador
- Etapa: Gate — Presupuesto aprobado por el cliente
- Cambio: presupuesto de la iteración v11 (USD 415.0, etapa única) aprobado. Se habilita el inicio de Implementación.
- Motivo: cumplir el gate duro "no iniciar Implementación sin presupuesto aprobado por el cliente".
- Impacto en capas: N/A.
- Riesgos/supuestos: ninguno nuevo.

### 2026-07-02 - presupuestador
- Etapa: 4 - Presupuesto (pagos múltiples de Egreso) — **gate cliente**
- Cambio: `4-presupuestador.md` ampliado con sección "Iteración v11". WBS de 4 items (Egreso multi-pago, extensión job diario, migración con backfill de datos de producción, UI Egresos), M total 17.0h, costo por fórmula vigente (M/2.5×1.2×$35) = USD 315.0 desarrollo + USD 100 Tokens IA + USD 29.4 riesgo excepcional documentado (migración de datos en producción) = **USD 415.0 total**, etapa única.
- Motivo: anclar el presupuesto en el patrón ya calibrado del propio proyecto (evita repetir la sobreestimación 3.4x-6.7x ya documentada en `27-presupuesto-parametros.md` I-7) y cuantificar el riesgo de la migración de datos en producción.
- Impacto en capas: N/A (documento comercial).
- Riesgos/supuestos: **pendiente de aprobación explícita del cliente antes de iniciar Implementación** (gate duro). Plan de mantenimiento anual sin cambios (PREMIUM, ya contratado).

### 2026-07-02 - arquitecto-mvc
- Etapa: 3 - Arquitectura técnica (pagos múltiples de Egreso)
- Cambio: `3-arquitecto-mvc.md` actualizado a v2 (§13, grounded en código real). Nueva entidad `EgresoPago` + enum `EstadoPagoEgreso`; `MovimientoCaja.EgresoId` reemplazado por `EgresoPagoId`; nuevo `IEgresoPagoService`/`EgresoPagoService` calcado de `ICuotaService`; extensión de `AcreditacionCuotasHostedService` existente (sin segundo job). **Punto crítico**: migración EF con backfill de datos de producción en 3 fases (schema aditivo → backfill SQL → drop de columnas viejas), con validación obligatoria contra copia de producción antes del deploy real (RT9).
- Motivo: traducir el diseño v2 a componentes técnicos concretos, preservando la historia de Egresos ya cargados en producción.
- Impacto en capas: Domain (+1 entidad, +1 enum, cambio de FK), Application (+1 interfaz), Infrastructure (+1 servicio, extensión de hosted service, migración con backfill), Web (grilla dinámica + controller nuevo).
- Riesgos/supuestos: RT9 (pérdida de trazabilidad si el backfill falla — mitigación: backup + validación de conteos antes de aplicar en prod), RT10 (evitar reimplementar desde cero, copiar patrón de CuotaService), RT11 (transacciones independientes por colección en el job), RT12 (binding de grilla dinámica en MVC).

### 2026-07-02 - disenador-funcional
- Etapa: 2 - Diseño funcional (pagos múltiples de Egreso)
- Cambio: `2-disenador-funcional.md` actualizado a v2 sobre análisis v11. Rediseño de `Egresos/Create` con grilla dinámica de pagos, nuevas pantallas `EgresoPagos/Rechazar` y `EgresoPagos/Regularizar`, nuevo contrato `IEgresoPagoService` (simétrico a `ICuotaService`), extensión del job diario existente (`AcreditacionCuotasHostedService`) para acreditar cheques de egreso vencidos. Se alineó la nomenclatura del documento (`Egreso`, no `Gasto`) a la del código real. Agregados RD6–RD8, PD8–PD10.
- Motivo: traducir el análisis v11 a diseño implementable respetando separación de capas y reutilizando el patrón ya probado de Cuotas.
- Impacto en capas: Presentación (grilla dinámica + 2 pantallas nuevas), Negocio (nuevo servicio + extensión de job), Datos (nueva entidad `EgresoPago`, FK en `MovimientoCaja`).
- Riesgos/supuestos: cambio exclusivo de `ganaderia - emo`. RD6 (validación suma exacta cliente+servidor), RD7 (idempotencia del job extendido), RD8 (reutilizar patrón de `CuotaService` para evitar divergencia).

### 2026-07-02 - analista-funcional
- Etapa: 0-1 - Discovery + Análisis (pagos múltiples de Egreso)
- Cambio: `1-analista-funcional.md` actualizado a v11. Egresos pasa de forma de pago única con acreditación inmediata a pagos múltiples (`EgresoPago`), habilitando cheques diferidos (fecha efectiva + fecha de vencimiento propia) que no cubren el total más un pago compensatorio. Cheque diferido replica ciclo Pendiente→Acreditado del job diario ya usado para Cuotas de venta; admite rechazo/regularización (Opción 3 a/b) simétricos. Agregadas PF53–PF61, PV13–PV16.
- Motivo: pedido explícito del cliente para reflejar la forma real de pago de compras (varios cheques diferidos + compensatorio).
- Impacto en capas: Presentación, Negocio y Datos (nueva entidad, cambio de FK en MovimientoCaja, extensión del job diario).
- Riesgos/supuestos: cambio **exclusivo del repositorio `C:\Sistemas\ganaderia - emo`** — confirmado con el usuario, NO aplica a `ganaderia - fausto`. Suma de pagos debe cuadrar exactamente contra el importe (R25). Job diario ahora procesa dos colecciones (R26). No se agrega edición de Egreso (S34).

### 2026-04-22 17:58 - presupuestador
- Etapa: Presupuesto
- Cambio: se ejecuto la estimacion funcional del sistema ganaderia con WBS por modulos visibles, PERT por item, contingencia por tipo de modulo y autocorreccion contra historicos.
- Motivo: contar con una base presupuestaria trazable antes de implementacion.
- Impacto en capas: Presentacion, Negocio y Datos.
- Riesgos/supuestos: alcance estimado sobre analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1; se contemplan 2 migraciones EF y reutilizacion de componentes ya resueltos de la solucion base.

### 2026-05-22 - deploy produccion
- Etapa: Cierre — deploy a produccion
- Cambio: sistema completo desplegado a produccion. Todas las etapas (0-6) implementadas. QA formal completado con defectos conocidos documentados.
- Motivo: primera version lista para uso productivo del cliente.
- Impacto en capas: todas.
- Riesgos/supuestos: 3 FAILs de QA conocidos no bloqueantes (§3.3, §5.7, §9). Defectos documentados en `6-qa.md`.

### 2026-05-07 - qa
- Etapa: 7 - QA integral
- Cambio: reporte QA generado sobre `1-analista-funcional.md` v10, `2-disenador-funcional.md` v1 y `5-implementador.md`. FAILs encontrados: §3.3 (cuotas enum libre en lugar de cerrado), §5.7 (unicidad Inicial por Grupo no validada), §9 (bandeja Novedades no implementada). Auto-fix aplicados: BUG-G-001 (bloqueo rechazo cuota Pendiente), BUG-G-003 (forma de pago real en regularizacion 3b).
- Motivo: validacion formal antes de deploy a produccion.
- Impacto en capas: Infrastructure (servicios corregidos).
- Riesgos/supuestos: 3 FAILs aceptados como deuda tecnica. Sistema considerado apto para produccion con esas limitaciones conocidas.

### 2026-05-07 - implementador
- Etapa: 5 - Egresos; 6 - Dashboard + usuarios + transversales
- Cambio: Etapa 5 — `EgresosController` + vistas CRUD + `IEgresoService`/`EgresoService` con comprobantes en `App_Data/`. Migraciones: `Egreso_FormaDePago`, `FacturaVenta_Comprobante`. Etapa 6 — `DashboardController` con KPIs anuales; `UsersController` (ABM usuarios); `NotificationsController`; `JobEjecucion` entidad + `AcreditacionCuotasHostedService` con tracking de ejecuciones. Migracion `JobEjecucion`. Renombrado `Factura` → `FacturaVenta` en toda la solucion (migracion + code).
- Motivo: completar modulos de egresos, dashboard y cierre de transversales del sistema.
- Impacto en capas: todas.
- Riesgos/supuestos: build OK. Sistema listo para QA integral.

### 2026-05-06 - implementador
- Etapa: 3 - Ventas + Facturas + Cuotas + Caja; 4 - Cuotas rechazo/regularizacion
- Cambio: `FacturasController` + `CuotasController` + `CajaController` con vistas completas. `IFacturaVentaService`/`FacturaVentaService`: creacion de facturas multi-item con IVA, numeracion correlativa `F-NNNNNN`, generacion automatica de cuotas (1/2/3 a 30/60/90 dias), comprobante PDF. `ICuotaService`/`CuotaService`: `AcreditarAsync`, `RechazarAsync`, `RegularizarAsync` (3a ErrorDeCarga + 3b CobroPosterior). `ICajaService`/`CajaService`: saldo = Σ movimientos Acreditados. Migraciones: `RenameFacturaToFacturaVenta`, `FacturaVenta_ItemKilosPrecioPorKilo_PlazoNullable`, `MovimientoCaja_DrillDownNav`.
- Motivo: implementar el nucleo de ingresos del sistema (ventas a compradores con facturacion y cuotas).
- Impacto en capas: todas.
- Riesgos/supuestos: `CajaController` marcado con `[Etapa2Only]` (diferido segun analisis funcional v10 §3.5).

### 2026-04-22 - implementador
- Etapa: 2 - Stock y movimientos + ABM catalogos UI
- Cambio: `StockController` con vistas Index, Detalle, CargaInicial, Movimientos; logica de stock calculado via `IStockService.GetStockAsync`. `GruposController`, `RubrosController`, `ProveedoresController` con CRUD completo. `MovimientoStock` tipos: Inicial, Nacimiento, Compra, Muerte, Venta, Compensacion. Migracion `Ganaderia_Etapa1_Catalogos_Operacion` aplicada.
- Motivo: dar acceso UI a los catalogos y permitir carga y consulta de stock ganadero.
- Impacto en capas: todas.
- Riesgos/supuestos: stock calculado dinamicamente (sin campo persitido), operaciones criticas en transaccion explicita.

### 2026-04-22 - implementador
- Etapa: 0 - Preparacion y fundaciones
- Cambio: creacion de estructura de carpetas Ganaderia en las 4 capas, alta de los 9 enums del dominio, constantes `RolesGanaderia` y `MatrizTransicionesCategoria`, y helpers Web `CalculoIvaHelper` y `FormatoCorrelativoHelper`.
- Motivo: dejar fundaciones tecnicas listas antes de modelar entidades y migraciones.
- Impacto en capas: Domain (enums + constantes), Web (helpers). Application e Infrastructure solo carpetas.
- Riesgos/supuestos: ninguno especifico de etapa. Solucion ya renombrada a `Ganaderia.*` y conexion `ganaderia_dev` configurada.