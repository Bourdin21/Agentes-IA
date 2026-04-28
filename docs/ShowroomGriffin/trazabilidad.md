# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-01-15 19:45 - implementador
- Etapa: Implementacion - E1 Maestros comerciales (cierre)
- Cambio: Reconciliacion con estado real. Entidades (5), configs (5), services (5), controllers (5), vistas y migracion M1 ya estaban presentes con policies correctas segun matriz arquitectura. Unico gap real: `ClienteService.InactivarAsync` no aplicaba la guarda D5. Fix aplicado: validacion `AnyAsync(v => v.ClienteId == id)` antes de soft delete; mensaje "No se puede inactivar un cliente con ventas registradas.".
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings. Tiempo 12.48 s.
- Motivo: Cerrar D5 dentro del service (frontera de negocio), preservar el resto del CRUD existente y mantener cambios minimos.
- Impacto en capas: Infrastructure (ClienteService). Domain, Application y Web sin cambios.
- Riesgos/supuestos: R2 no aplica en E1 (queda vigente para E2 con Sku/CodigoBarra). R-MAE-01 (case-insensitive en Categoria) y R-MAE-05 (bloqueo Categoria con productos) ya implementados previamente.
- Pruebas minimas pendientes en QA: CRUD por maestro, nombre duplicado Categoria, inactivar Categoria con productos, inactivar Cliente con ventas (D5), permisos Vendedor/Admin por endpoint, AJAX Subgrupos por categoria y busqueda Clientes, DataTables server-side. Despliegue: `dotnet ef database update` en entorno destino.
- Gate: APROBADO tecnicamente. Listo para iniciar E2 - Productos y Variantes (M2 + RowVersion + indices unicos Sku/CodigoBarra) tras confirmacion.

### 2026-01-15 19:15 - implementador
- Etapa: Implementacion - E0 Seguridad y armado base (cierre)
- Cambio: Reconciliacion con estado real del repo. Seed RolVendedor, policies RequireAdministrador/RequireVendedor, sidebar dinamico y migracion M1 ya estaban presentes (no se modifican). Se cierran los pendientes reales: HomeController (CS9113 _logger + CS0114 `public new StatusCode`) y upgrade MailKit 4.14.1 -> 4.16.0 (arrastra MimeKit 4.16.0) para cerrar NU1902.
- Evidencia de build: `dotnet build` OK, 0 errores, 0 warnings (mejora vs baseline 8 warnings). Tiempo 30.63 s.
- Motivo: Aplicar cambios minimos manteniendo lo ya correcto, dejar baseline limpio antes de E1.
- Impacto en capas: Web (HomeController), Infrastructure (csproj). Domain y Application sin cambios.
- Riesgos/supuestos: nuevo R-E0-1 (upgrade MailKit/MimeKit requiere smoke test de email en QA: EmailService, ErrorEmailNotifierMiddleware, SmtpHealthCheck). S6 confirmado.
- Pruebas minimas pendientes en QA: login por rol, sidebar por rol, /Home/Error, /Home/StatusCode, smoke test email.
- Gate: APROBADO tecnicamente. Listo para iniciar E1 - Maestros comerciales tras confirmacion.

### 2026-01-15 18:30 - implementador
- Etapa: Implementacion (plan)
- Cambio: Creacion de `5-implementador.md` v1.0. Se define plan tecnico por etapas E0..E8 alineado a F0..F8 del diseno y a M1..M6 del arquitecto. Se listan cambios por capa (Domain 5 enums + 20 entidades; Application 14 interfaces; Infrastructure 20 configs + ApplyConfigurationsFromAssembly + 14 services + DI + seed RolVendedor + 6 migraciones; Web 13 controllers + ~35 ViewModels + ~30 vistas + 7 AJAX + 2 policies + sidebar dinamico + 3 JS). Se confirma migracion EF SI con 6 migraciones M1..M6. Se incluye matriz de pruebas minimas por etapa y checklist de merge.
- Evidencia de build inicial: `dotnet build` OK, 0 errores, 8 warnings (NU1902 MailKit/MimeKit, NETSDK1057 preview, CS0114 y CS9113 en HomeController). Tiempo 4.61 s.
- Motivo: Habilitar ejecucion por etapas con build verde como gate, preservando fronteras por capa y decisiones D1..D6.
- Impacto en capas: Domain (entidades/enums + RowVersion), Application (14 contratos + parametro incluirCostos), Infrastructure (configs, services, DI, seed, transacciones serializables, 6 migraciones), Web (13 controllers, policies, sidebar, JS, ajustes a HomeController).
- Riesgos/supuestos: vigentes R1..R8 y S1..S5 de arquitectura; nuevo supuesto S6 (correcciones de warnings heredados de HomeController y evaluacion MailKit/MimeKit se hacen en E0 sin refactor adicional).
- Gate: APROBADO el plan. Pendiente arrancar E0 - Seguridad y armado base.

### 2026-01-15 10:00 - analista-funcional
- Etapa: Analisis
- Cambio: Cierre de análisis funcional v1.1. Se agregaron casos de uso (CU-01..CU-26), banderas tempranas (EF=SI, Integracion=NO, Maquina de estados=SI) y se resolvieron decisiones D1..D6.
- Motivo: Habilitar handoff a Diseño sin ambigüedades funcionales.
- Impacto en capas: Presentacion, Negocio, Datos (definiciones funcionales que condicionan las tres capas).
- Riesgos/supuestos: R1..R4 vigentes; supuestos S1..S5 verificados sobre el codebase existente.

### 2026-01-15 17:00 - presupuestador
- Etapa: Presupuesto
- Cambio: Creación de `4-presupuestador.md` v1.0. Estimación PERT por módulo funcional con contingencia variable por riesgo (8/15/25%), aplicada una sola vez. Total: 86,57 h base / 101,1 h finales / USD 1.415 a tasa USD 14/h. Bloque de autocorrección contra históricos: 9 de 11 ítems en rango (0,85–1,15); 2 ítems con ratio >1,15 justificados (Resumen Semanal y Dashboard, drivers concretos). Comparación agregada con Delicias Naturales (ratio 0,91, en tolerancia). Cierre dos pasos A=B (sin ajuste post-autocorrección).
- Motivo: Cerrar la fase de presupuesto con número auditable, trazable a drivers funcionales y calibrado contra dataset histórico Abril 2026.
- Impacto en capas: ninguna directa; se cuantifica el esfuerzo planificado.
- Riesgos/supuestos: RP1 (HasFilter MySQL), RP2 (deadlocks venta), RP3 (cuotas como N filas si cambia D2), RP4 (backup adjuntos). Supuestos: hosting/AFIP/migración legacy fuera de alcance.
- Gate: APROBADO para entregar oferta al cliente / pasar a Implementación.

### 2026-01-15 15:00 - arquitecto-mvc
- Etapa: Arquitectura
- Cambio: Creación de `3-arquitecto-mvc.md` v1.0. Se cuantifica impacto por capa (Domain: 5 enums + 20 entidades; Application: 14 interfaces; Infrastructure: 20 configs + 20 DbSets + 14 services + 6 migraciones EF; Web: 13 controllers + ~35 ViewModels + ~30 vistas + 2 policies). Se resuelven las 5 preguntas técnicas abiertas del diseñador: RowVersion para D6, VentaPago único para D2, índices únicos condicionales con fallback, IsolationLevel.Serializable en venta/compra/devolución, filtrado de costos por parámetro `incluirCostos` resuelto en controller. Se confirma migración EF: SÍ, 6 migraciones M1–M6.
- Motivo: Habilitar gate de aprobación a Presupuesto con todas las definiciones técnicas cerradas.
- Impacto en capas: Domain (RowVersion en VarianteProducto), Application (parámetro incluirCostos en contratos), Infrastructure (transacciones serializables, two-save NroVenta, plan M1–M6, seed RolVendedor), Web (policies RequireAdministrador / RequireVendedor + sidebar dinámico).
- Riesgos/supuestos: R1 orden migraciones, R2 índices únicos condicionales en MySQL, R4 concurrencia stock, R5 concurrencia aumento masivo, R6 two-save NroVenta, R7 cascade vs soft delete, R8 adjuntos en disco. Supuestos S1–S5 confirmados.
- Gate: APROBADO para pasar a Presupuesto.

### 2026-01-15 12:30 - disenador-funcional
- Etapa: Diseno
- Cambio: Creación de `2-disenador-funcional.md` v1.0. Consolidación de flujo de pantallas, ViewModels y permisos por acción. Se agrega máquina de estados en formato tabla (Compra, Venta, Devolución, Maestros soft delete, Aumento masivo). Se incorporan decisiones D1..D6 al diseño. Plan funcional por etapas F0..F8 para arquitecto.
- Motivo: Faltaba la máquina de estados tabular y un plan por etapas; se requiere memoria oficial del agente diseñador según `metadata.md`.
- Impacto en capas: Presentacion (pantallas, ViewModels, sidebar dinámico, JS de Venta/Recepción/Devolución), Negocio (14 interfaces de service, transiciones de estado encapsuladas, política de costos por rol), Datos (transacciones serializables, RowVersion en VarianteProducto para D6, adjuntos en disco con GUID).
- Riesgos/supuestos: R1..R6 (se agregan R5 concurrencia aumento masivo y R6 redondeo cuotas); S1..S4 (S1: MVC clásico a confirmar con arquitecto si la guía operativa cambia).
- Preguntas abiertas para Arquitectura: mecanismo de bloqueo optimista (RowVersion vs lock pesimista), persistencia del redondeo de cuotas, índices únicos, IsolationLevel, estrategia de filtrado de payload por rol.
