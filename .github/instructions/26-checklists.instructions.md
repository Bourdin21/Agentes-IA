---
description: Checklists para nuevas entidades y nuevos servicios en la arquitectura BlankProject.
applyTo: "**/*.{cs,csproj,cshtml}"
---

# Checklist nuevas entidades
1. Crear entidad en Domain/Entities heredando SoftDestroyable.
2. Agregar DbSet<T> en AppDbContext.
3. Configurar Fluent API (lengths, indexes, relations).
4. Crear interfaz Application si requiere servicio dedicado.
5. Crear DTOs Application si requiere proyecciones.
6. Implementar servicio en Infrastructure/Services.
7. Registrar servicio en DependencyInjection.cs (Scoped).
8. Crear ViewModels en Web/Models con DataAnnotations en espanol.
9. Crear Controller en Web/Controllers.
10. Crear Views segun design system, con criterio de diseñador grafico senior (jerarquia visual, agrupacion logica de campos, ver `25-frontend-design-system.instructions.md`).
10a. Si la entidad tiene listado: renderizar con DataTables server-side, y agregar un filtro por cada columna visible de la grilla (ver `25-frontend-design-system.instructions.md` — regla obligatoria, no opcional).
10b. Si la entidad se edita y tiene alguna relacion configurable por combo (Select2 simple o multiple), la vista de Editar debe inicializar el combo con los valores ya asignados a la entidad, nunca vacio (ver `32-estandares-qa-implementador.instructions.md`).
11. Agregar link en sidebar de Shared/_Layout.cshtml.
12. Generar migracion EF.
13. Revisar ortografia y acentuacion de todo texto visible (labels, botones, titulos, mensajes de validacion, SweetAlert2) antes de cerrar la vista — ver `25-frontend-design-system.instructions.md`.

## Smoke-check automatizado (QA, ver `33-verificacion-automatizada-qa.instructions.md`)
1. `Index` carga sin error 500, el DataTable renderiza filas reales.
2. Cada columna visible tiene su filtro y al menos uno filtra correctamente.
3. `Create` con campos requeridos completos guarda y confirma; con un campo requerido vacio, bloquea con mensaje (no guarda).
4. `Edit` de un registro con relacion por combo: el combo llega pre-poblado con los valores ya asignados a la entidad (regla 10b arriba) — nunca vacio.
5. Baja logica: el registro desaparece del listado activo tras eliminarlo (verificar que sigue existiendo en BD si aplica, no chequeo visual solamente).
6. Link de sidebar: visible/accesible solo para los roles esperados; un usuario sin ese rol recibe 403 al intentar la ruta directa.

# Checklist nuevos servicios
1. Definir interfaz en Application/Interfaces.
2. Implementar en Infrastructure/Services.
3. Registrar como Scoped en DependencyInjection.cs.
4. Inyectar por constructor donde corresponda.

# Checklist modulo con workflow / maquina de estados
1. Definir enum de estados en Domain/Enums.
2. Mapear transiciones validas en el Service (no en Controller).
3. Validar guardas y permisos por transicion antes de persistir.
4. Registrar evento/auditoria del cambio de estado.
5. Cubrir transiciones invalidas con error funcional explicito.
6. ViewModel con estado actual + acciones disponibles segun rol.
7. QA debe recorrer todas las transiciones validas e invalidas.

## Smoke-check automatizado (QA, ver `33-verificacion-automatizada-qa.instructions.md`)
1. Con la entidad en estado inicial, los botones de accion visibles coinciden exactamente con las transiciones validas desde ese estado (ni de mas ni de menos) — contrastar contra la tabla de maquina de estados aprobada en `2-disenador-funcional.md`.
2. Ejecutar una transicion valida: el estado cambia y queda registrado el evento/auditoria.
3. Intentar una transicion invalida (manipulando el request si el boton no la ofrece en UI): rechazada con error funcional explicito, nunca un 500.
4. Repetir el chequeo de botones (punto 1) despues de al menos 2 transiciones mas del ciclo, no solo en el estado inicial.

# Checklist reporte o exportacion
1. DTO/proyeccion en Application sin exponer entidades.
2. Service en Infrastructure con consulta optimizada (no N+1).
3. Filtros y paginacion en ViewModel (un filtro por cada columna visible del listado, ver `25-frontend-design-system.instructions.md`).
4. Export Excel via ClosedXML o PDF via QuestPDF segun corresponda.
5. Permiso explicito para acceder al reporte.
6. Pruebas funcionales con datos representativos.

## Smoke-check automatizado (QA, ver `33-verificacion-automatizada-qa.instructions.md`)
1. El reporte/listado carga sin error 500 con datos reales del sistema.
2. Cada filtro definido en el ViewModel (uno por columna visible, regla 10a) filtra correctamente sobre datos reales — probar al menos 2 filtros distintos.
3. La exportacion (Excel/PDF) descarga un archivo valido y no vacio, con los mismos datos que se ven filtrados en pantalla.
4. Acceder a la ruta del reporte sin el permiso explicito requerido devuelve 403, nunca un 500 ni acceso silencioso.

# Checklist integracion externa
1. Interfaz en Application con contrato del proveedor.
2. Implementacion en Infrastructure con HttpClient tipado o SDK.
3. Configuracion en appsettings con seccion dedicada.
4. Manejo de timeouts, reintentos y errores controlados.
5. Logging estructurado con Serilog (sin secretos).
6. Pruebas funcionales con caso ok, caso error y caso timeout.

## Smoke-check automatizado (QA, ver `33-verificacion-automatizada-qa.instructions.md`)
1. Caso OK: la integracion responde y persiste/devuelve el resultado esperado contra el proveedor real (o su sandbox/homologacion).
2. Caso error controlado: forzar una respuesta de error del proveedor (o simularla) — la app no rompe con 500, muestra error funcional explicito.
3. Caso timeout, si es simulable sin credenciales de produccion: el timeout configurado corta la espera, la request no queda colgada.
4. Revisar logs (Serilog) tras el caso OK y el caso error: sin secretos expuestos en el log.

# Checklist modificacion sobre modulo existente
1. Identificar modulo y archivo(s) a tocar antes de codificar.
2. Confirmar que la regla nueva no contradice la maquina de estados vigente.
3. Mantener compatibilidad con datos existentes (migracion EF si aplica).
4. Actualizar ViewModel y validaciones de la pantalla afectada.
5. Probar regresion del flujo previo ademas del cambio nuevo.

## Smoke-check automatizado (QA, ver `33-verificacion-automatizada-qa.instructions.md`)
1. El flujo previo (comportamiento anterior al cambio) sigue funcionando exactamente igual para los casos NO afectados por la modificacion — regresion real, no solo el caso nuevo.
2. Si hubo migracion EF: los datos existentes previos a la migracion siguen siendo consistentes/visibles despues de aplicarla, no solo los registros nuevos.
3. Probar el caso que la nueva regla debia cubrir Y un caso limite que la regla anterior ya cubria, contra el ViewModel/validaciones actualizados.
