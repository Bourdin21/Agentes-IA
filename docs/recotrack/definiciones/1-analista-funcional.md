# Memoria - Analista funcional

## Proyecto: recotrack
## Ultima actualizacion: 2025-07 (migrado a esta ubicacion 2026-08-11)

> Contenido migrado desde `C:\Sistemas\recotrack\docs\recotrack\definiciones\1-analista-funcional.md`, que era la unica copia existente. Esta ubicacion centralizada pasa a ser la fuente de verdad; el archivo en el repo del sistema debe considerarse legacy/duplicado a partir de ahora.

## Definiciones vigentes

### Modulos/features analizados

**Iteracion 1 — Duplicar trabajos masivo + Estado empleado + Formato legajo** (Estado: Analisis funcional CERRADO)

Pedido original del cliente:
> Modificar funcionalidad para Duplicar trabajo: agregar check por trabajo para seleccionar uno o muchos y duplicarlos. El usuario selecciona la fecha destino. Verificar duplicados para ese dia. El titulo de columna debe tener opcion seleccionar todos/ninguno. Los trabajos duplicados se validan automaticamente; el supervisor filtra por fecha del dia para validarlos manualmente. Para empleados, agregar propiedad Estado (disponible, licencia, ausente, etc.) con "disponible" preseleccionado. Formato legajo: CodigoRazonSocial-NumeroLegajo, con campo recomendado entre valores ya cargados o nuevo ingreso a mano.

### Reglas funcionales acordadas

| P# | Pregunta | Decision |
|----|----------|----------|
| P-01 | Criterio de duplicado exacto | **Opcion B**: mismo `TipoTrabajo` + `TipoServicio` + `CamionId` en la fecha destino, sin importar empleados. |
| P-02 | Estado empleado durante duplicacion | **Opcion B (bloqueo)**: si un empleado esta en estado != Disponible, el trabajo que lo incluye no se duplica y se informa el motivo. |
| P-03 | Valores enum `EstadoEmpleado` | `Disponible`, `Licencia`, `Ausente`, `Vacaciones`, `Suspendido`, `Baja`. |
| P-04 | Alcance "seleccionar todos" | **Opcion B**: todos los registros que coinciden con el filtro activo, con confirmacion explicita al usuario. |
| P-05 | Naturaleza de `CodigoRazonSocial` | **Opcion A**: string derivado del prefijo del legajo. Autocomplete dinamico desde prefijos existentes en BD. |
| P-06 | Migracion de legajos existentes | Los legajos existentes quedan como estan. Nuevo formato solo para altas/ediciones futuras. |

### Criterios de aceptacion vigentes

- Bloqueante: empleado ya asignado a otro trabajo en la misma fecha (`ValidateAsync`).
- No bloqueante: categoria vs rol, tipo servicio incompatible.
- Ya existia flujo de duplicado unitario (boton "Duplicar" por fila -> `Create?duplicarDesdeId=`) antes de esta iteracion; la duplicacion masiva es una extension del mismo patron.

### Supuestos y dependencias

| Entidad | Capa | Notas |
|---------|------|-------|
| `Trabajo` | Domain | Fecha, TipoTrabajo, TipoServicio, CamionId, Observacion. Sin campo Estado propio. |
| `TrabajoEmpleado` | Domain | Relacion N:N con Rol, Justificacion. |
| `Empleado` | Domain | Nombre, Apellido, Legajo (string unico), DNI, Categoria, TipoServicio, EstadoEmpleado (agregado en esta iteracion). |
| `DomainEnums` | Domain | CategoriaEmpleado, TipoServicio, TipoTrabajo, RolEnTrabajo, EstadoNotificacion, EstadoEmpleado (agregado en esta iteracion). |

### Exclusiones confirmadas

- No se migran legajos existentes al nuevo formato (P-06): solo aplica a altas/ediciones futuras.

## Historial de ajustes
- 2025-07: Iteracion 1 cerrada — todas las preguntas respondidas y confirmadas por el cliente.
- 2026-08-11: migrado el contenido desde el repo local a esta ubicacion centralizada. **Pendiente**: no existe analisis funcional formal para las iteraciones posteriores (vencimientos por rol jun-2026, estado de camiones, rol Taller, tipo de camion, reporte de disponibilidad) — se implementaron directamente sin pasar por esta etapa (ver nota en `5-implementador.md`). Registrar retroactivamente si se necesita trazabilidad completa.
