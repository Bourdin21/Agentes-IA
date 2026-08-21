# Memoria - Arquitecto MVC

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Escaneo de reutilización cross-proyecto
Sin coincidencias — es lógica de negocio específica de este proyecto (facturación por contador de copias). Se reutiliza el propio código de `CreateAsync` como base, extraído a un método compartido.

### H1 — Arquitectura (2026-08-20)

**Componente modificado:** `Eleven.Infrastructure/Services/AlquilerService.cs` únicamente.

**Desglose por capa:**
- **Presentación:** sin cambios. `AlquileresController.Edit` (POST) ya propaga `ServiceResult.Errors` a la vista vía el mecanismo existente (mismo que usa Create).
- **Negocio:** 
  - Nuevo método privado `Task<List<string>> ValidarContadoresAsync(int maquinaId, DateTime fecha, int contadorBN, int contadorColor)` en `AlquilerService`, extraído del bloque de validación que hoy está inline en `CreateAsync` (líneas ~169–199 del archivo actual). Devuelve la lista de errores (vacía si es válido).
  - `CreateAsync` se refactoriza para llamar a este método en vez de tener el bloque inline (mismo comportamiento, cero cambio funcional para Create).
  - `UpdateAsync` se modifica: antes de sobreescribir campos, guardar `var maquinaCambio = alquiler.MaquinaId != dto.MaquinaId;`. Si `maquinaCambio`, llamar a `ValidarContadoresAsync` con los datos nuevos; si devuelve errores, `return ServiceResult.CreateError(...)` sin tocar la entidad (mismo patrón que ya usa `CreateAsync` al fallar validación). Si pasa, aplicar la misma regla de "crear `HistoriaContador` si corresponde" que tiene `CreateAsync` (también candidata a extraer a un método compartido `Task CrearHistoriaContadorSiCorrespondeAsync(...)` para no duplicar la condición larga de 5 cláusulas que hoy tiene `CreateAsync`).
- **Datos:** sin cambios de esquema. Se siguen usando `Alquileres` y `Contadores` (`HistoriaContador`) tal cual existen. **Sin migración EF.**

**Cambios de datos y migraciones:** Ninguno.

**Riesgos técnicos:**
- Bajo. Es un refactor de extracción de método + una validación condicional nueva en un solo service ya bien entendido (interviene en esta misma sesión varias veces). No toca DI, no toca controllers, no toca DbContext/configuraciones EF.
- Riesgo de regresión en Create: mitigado porque el refactor debe preservar exactamente el mismo comportamiento (mover código, no reescribirlo). El implementador debe correr un alta de alquiler de prueba (o revisar que la lógica extraída sea 1:1) antes de dar por cerrado.

**Estrategia de pruebas funcionales (para QA):**
1. Editar un alquiler cambiando SOLO observación/ubicación (sin cambiar máquina) → debe guardar sin pedir validación de contadores (regresión: hoy funciona, no debe romperse).
2. Editar un alquiler cambiando la máquina a una con contador inicial menor al último `HistoriaContador` de esa máquina → debe rechazar con mensaje de error.
3. Editar un alquiler cambiando la máquina a una libre con contador inicial válido → debe guardar y (si corresponde) crear el `HistoriaContador`.
4. Alta de un alquiler nuevo (Create) → debe seguir comportándose exactamente igual que antes del refactor (regresión sobre el camino ya existente).
5. Consulta rápida en base antes de cerrar: ¿hay algún alquiler activo hoy cuyo contador actual ya esté fuera de rango de su máquina? **Ejecutada 2026-08-20: sí, la gran mayoría de los alquileres tiene `ContadorBNInicial=0`/`ContadorColorInicial=0`, muy por debajo del rango real de `HistoriaContador` de su máquina (ej. Alquiler 2 → Máquina 289 con contador real entre 7.241 y 28.831).** Es consistente con un artefacto de la migración desde el sistema viejo (el campo no se trackeaba igual en OLD y quedó en 0 por default), no con datos recientes corruptos. **Esto confirma que el diseño es correcto tal cual está**: la validación nueva solo se dispara cuando `MaquinaId` cambia en un Edit — nunca corre sobre estos registros existentes mientras nadie les cambie la máquina, así que no bloquea nada retroactivamente. Consecuencia a tener presente: si algún día un técnico edita uno de estos alquileres y sí cambia la máquina, la validación nueva lo va a obligar a cargar un contador inicial real (ya no va a poder dejarlo en 0) — es el comportamiento correcto, pero puede sorprender la primera vez que pase.

## Historial de ajustes
- 2026-08-20: Arquitectura de H1 cerrada. Un solo archivo afectado (`AlquilerService.cs`), sin migración, riesgo bajo.
