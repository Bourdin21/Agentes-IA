# Memoria - Disenador funcional

## Proyecto: recotrack
## Ultima actualizacion: 2025-07 (migrado a esta ubicacion 2026-08-11)

> Contenido migrado desde `C:\Sistemas\recotrack\docs\recotrack\definiciones\2-disenador-funcional.md`, que era la unica copia existente. Esta ubicacion centralizada pasa a ser la fuente de verdad.

## Definiciones vigentes

### Flujos de pantalla acordados

**Iteracion 1 — Duplicado masivo de Trabajos + Estado Empleado + Formato Legajo** (Estado: Diseno funcional COMPLETADO)

- D-01: La columna de checkboxes ocupa el primer lugar en la tabla de Trabajos (col fija izquierda, 40px).
- D-02: El boton "Duplicar seleccionados" vive en la barra de accion contextual que aparece al seleccionar >=1 trabajo. No reemplaza ni convive con el boton "Nuevo Trabajo".
- D-03: La seleccion masiva de todos los filtrados se gestiona mediante un segundo confirm dialog, no en el mismo checkbox del header (para evitar operaciones accidentales).
- D-04: El modal de duplicacion tiene una seccion de resumen progresivo: se procesa en el servidor y devuelve el resultado completo, luego se renderiza la tabla de resultados.

### ViewModels definidos

- D-05: El campo Legajo en Create/Edit de Empleado se divide en dos inputs separados (`CodigoRazonSocial` + `NumeroLegajo`) con preview en tiempo real. El campo hidden `Legajo` es el que se postea.
- D-07: El campo `EstadoEmpleado` se posiciona en el mismo grupo de campos administrativos (Categoria / TipoServicio / RolPorDefecto).

### Validaciones de UI acordadas

- D-06: `CodigoRazonSocial` usa `<datalist>` HTML5 nativo (compatible con Bootstrap 5). No se agrega dependencia de libreria de autocomplete externa.
- D-08: La lista de Empleados muestra el Estado con badge de color semantico (verde=Disponible, amarillo=Licencia/Ausente/Vacaciones, rojo=Suspendido/Baja).

### Contratos funcionales para Services

- Sin contratos nuevos especificos de esta etapa; ver `3-arquitecto-mvc.md` para las decisiones tecnicas de `DuplicarMasivoAsync` y `GetCodigosRazonSocialAsync`.

## Historial de ajustes
- 2025-07: Iteracion 1 cerrada — diseno funcional completado, listo para revision del arquitecto.
- 2026-08-11: migrado el contenido desde el repo local a esta ubicacion centralizada. **Pendiente**: no existe diseno funcional formal para las iteraciones posteriores (vencimientos por rol, estado de camiones, rol Taller, tipo de camion, reporte de disponibilidad) — ver nota en `5-implementador.md`.
