# Memoria - Diseñador funcional

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Escaneo de reutilización cross-proyecto
Revisado: ningún otro proyecto en `/docs/*/definiciones/` tiene un flujo de "validar contador de máquina al editar" equivalente — es específico del dominio de alquiler de equipos de impresión por copia (único caso en el historial de Olvidata con este modelo de facturación). No hay nada para reutilizar; se toma como base el propio `AlquilerService.CreateAsync` (mismo proyecto) que ya implementa la validación correcta para el alta.

### H1 — Diseño (2026-08-20)

**Pantallas/acciones:** Ninguna pantalla nueva. Se reutiliza `Alquileres/Edit` (`AlquilerEditViewModel`) tal cual existe hoy — ya pide `MaquinaId`, `ContadorBNInicial`, `ContadorColorInicial` como campos requeridos. No se agrega ningún campo ni control nuevo a la vista.

**Reglas de validación:**
- La validación se dispara en el POST de `AlquileresController.Edit` → `AlquilerService.UpdateAsync`, solo cuando `dto.MaquinaId != alquiler.MaquinaId` (la máquina guardada cambió respecto a la que tenía el registro).
- Mismas reglas que `CreateAsync` ya aplica hoy:
  - Si existe un `HistoriaContador` anterior (fecha ≤ hoy) de la máquina nueva: `ContadorBNInicial` debe ser ≥ a su `ContadorBN` (y `ContadorColorInicial` ≥ su `ContadorColor` si la máquina es color).
  - Si existe un `HistoriaContador` siguiente (fecha ≥ hoy): `ContadorBNInicial` debe ser ≤ a su `ContadorBN` (ídem color).
  - Si no pasa: `ServiceResult.CreateError` con la misma lista de mensajes que usa Create (`"El contador B/N debe ser mayor o igual a {X}"`, etc.) — el controller ya sabe mostrar esos errores (mismo patrón que Create).
- Si pasa la validación y corresponde (mismo criterio "Regla de Negocio Legacy" de Create): insertar un `HistoriaContador` nuevo para dejar registrado el contador inicial de la nueva máquina en ese punto del tiempo.

**Mensajes al usuario:** Reutilizar el mismo texto/formato de error que ya muestra `Alquileres/Edit` cuando `UpdateAsync` devuelve `ServiceResult` con errores (no hay UI nueva que diseñar, el mecanismo de mostrar errores de validación ya existe en la vista).

**Impacto por capa:** Solo Negocio (`AlquilerService.cs`). Presentación no cambia (mismo ViewModel, misma vista, mismo mecanismo de mostrar errores). Datos no cambia (mismas tablas, sin migración).

**Riesgos de implementación:**
- Refactor menor: la lógica de validación de contadores hoy vive inline dentro de `CreateAsync` — para no duplicar código, extraerla a un método privado reutilizable `ValidarContadores(maquinaId, fecha, contadorBN, contadorColor)` y llamarlo desde ambos (`CreateAsync` y `UpdateAsync`). Esto es refactor de bajo riesgo (mismo archivo, mismo comportamiento para Create, solo cambia que ahora es un método en vez de código inline).
- Verificar que la comparación "¿cambió la máquina?" se haga contra el valor **actual en base** (`alquiler.MaquinaId` antes de sobreescribir), no contra `dto.MaquinaId` dos veces.

### Historias de usuario

**HU1.** Como usuario Administrador o Técnico, quiero que el sistema rechace guardar un alquiler si cambio la máquina a una con un contador inicial inconsistente con su historial, para no romper la facturación por copia de esa máquina.
- CA: ver CA1 en `1-analista-funcional.md`.

**HU2.** Como usuario Administrador o Técnico, quiero poder editar un alquiler sin que me pida contadores si no cambié la máquina, para no tener fricción en ediciones simples (cambiar ubicación, observaciones, fecha de devolución, etc.).
- CA: ver CA3 en `1-analista-funcional.md`.

**HU3.** Como usuario Administrador o Técnico, quiero poder cambiar la máquina de un alquiler a una máquina libre con contador inicial válido, para poder reflejar un reemplazo de equipo real.
- CA: ver CA2 en `1-analista-funcional.md`.

## Historial de ajustes
- 2026-08-20: Diseño de H1 (fix de validación en AlquilerService.UpdateAsync). Sin pantallas nuevas, sin migración. H2 (Avisos) y el resto quedan sin diseñar, pendientes de definición con el cliente.
