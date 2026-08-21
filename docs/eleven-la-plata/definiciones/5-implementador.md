# Memoria - Implementador

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Escaneo de reutilización cross-proyecto
- `docs/patrones/catalogo.yml`: sin match (la única coincidencia textual de "contador" es un contador de filas de importación, sin relación).
- Barrido de `docs/*/definiciones/5-implementador.md`: sin match funcional. Los hits de "contador" en otros proyectos son numeradores de factura (`ganaderia` → `ContadorFactura`) o contadores de UI/importación (`crm-olvidata`, `la-platense`, `vinosefue`, `marihogar`) — nada relacionado con facturación por contador de copias de equipos de impresión.
- **Decisión:** implementar en el propio proyecto reutilizando el código ya existente de `AlquilerService.CreateAsync` (extraído a métodos privados compartidos). No se agrega nada al catálogo: la lógica es específica del dominio de este cliente, no es un componente genérico reutilizable.

### H1 — Fix de validación de contadores en `AlquilerService.UpdateAsync` (2026-08-20)

**Archivo único modificado:** `C:\Sistemas\elevenlaplata\Eleven.Infrastructure\Services\AlquilerService.cs`

**Archivos y capas modificadas**
- **Negocio / Infrastructure** — `Eleven.Infrastructure/Services/AlquilerService.cs`:
  - Nuevo método privado `ValidarContadoresAsync(int maquinaId, DateTime fecha, int contadorBN, int contadorColor)`. Devuelve la tupla `(List<string> Errores, HistoriaContador? ContadorAnterior, HistoriaContador? ContadorSiguiente)`. Se extrajo tal cual del bloque que estaba inline en `CreateAsync` (queries de contador anterior/siguiente + las 4 comparaciones, con el mismo texto de mensajes). **Se devuelven también los contadores adyacentes** porque la "Regla de Negocio Legacy" que decide si insertar un `HistoriaContador` los necesita; devolver solo la lista de errores obligaba a repetir las dos queries.
  - Nuevo método privado `AgregarHistoriaContadorSiCorresponde(maquinaId, fecha, contadorBN, contadorColor, contadorAnterior, contadorSiguiente)`: encapsula la condición de 5 cláusulas de la "Regla de Negocio Legacy" y hace el `_context.Contadores.Add(...)`. No hace `SaveChanges` (queda a cargo del llamador, igual que antes).
  - `CreateAsync`: reemplaza el bloque inline por las dos llamadas. **Cero cambio funcional** — mismo orden de operaciones, mismos mensajes, mismo `ServiceResult<int>.CreateError("Error en la validación de contadores", validationErrors)`. Se conservó tal cual el pre-chequeo `maquina == null → "Máquina no encontrada."` que ya tenía.
  - `UpdateAsync`: agrega `bool maquinaCambio = alquiler.MaquinaId != dto.MaquinaId;` calculado **antes** de sobreescribir la entidad (la instancia viene de `FindAsync`, o sea el valor persistido en base). Si `maquinaCambio`, llama a `ValidarContadoresAsync` con los datos nuevos y, ante errores, hace `return ServiceResult.CreateError("Error en la validación de contadores", validationErrors)` **sin haber tocado ni un campo de la entidad**. Si pasa, tras asignar los campos llama a `AgregarHistoriaContadorSiCorresponde` con los adyacentes ya obtenidos. Si `maquinaCambio == false`, el método corre exactamente igual que antes del fix (ni una query extra).
- **Presentación:** sin cambios. `AlquileresController.Edit` (POST, líneas 131-140) ya vuelca `result.Errors` a `ModelState` con el mismo patrón que `Create`; `AlquilerEditViewModel` ya trae `MaquinaId`/`ContadorBNInicial`/`ContadorColorInicial` requeridos.
- **Datos:** sin cambios de esquema.

### Migraciones EF generadas
Ninguna. No hubo cambios de entidades ni de configuración EF.

### Riesgos residuales
- **Regresión en Create (bajo):** el refactor es un mover-código 1:1 verificado por relectura; la única diferencia real es que `ValidarContadoresAsync` hace su propio `_context.Maquinas.FindAsync(maquinaId)`. En `CreateAsync` esa máquina ya fue traída al change tracker de EF renglones antes, así que resuelve en memoria (sin roundtrip extra ni riesgo de leer otro estado).
- **Fricción de UX esperada y deliberada:** los alquileres migrados del sistema viejo tienen `ContadorBNInicial`/`ContadorColorInicial` en 0. La primera vez que alguien le cambie la máquina a uno de ellos, la validación nueva lo va a obligar a cargar un contador inicial real. Es el comportamiento correcto (CA1), pero puede sorprender — vale avisarlo al cliente.
- **Fuera de alcance, sigue vigente:** cambiar la máquina de un alquiler sigue reescribiendo retroactivamente "de qué máquina fue" todo el alquiler (`Alquiler.MaquinaId` es escalar). Este fix garantiza que el dato que se guarda es consistente, pero NO conserva el historial multi-máquina — decisión explícita del Análisis (H1, alcance excluido).
- `ValidarContadoresAsync` consulta `_context.Contadores` sin filtrar `DeletedAt == null`, igual que hacía el código original de `CreateAsync`. Se preservó el comportamiento legacy a propósito (no es un refactor pedido). `GetDetailsAsync` sí filtra soft-deletes — la inconsistencia es preexistente, no introducida acá.

### Próximos pasos pendientes
- QA sobre las 5 pruebas funcionales de `3-arquitecto-mvc.md` (sección "Estrategia de pruebas funcionales"). Prioridad en la prueba 4 (regresión de alta) por el refactor.
- H2 (Avisos/Notifications nunca disparados) y H3–H7 siguen sin implementar, pendientes de definición con el cliente.

## Historial de ajustes
- 2026-08-20: H1 implementado. Un solo archivo (`AlquilerService.cs`), 2 métodos privados nuevos + condicional en `UpdateAsync`, sin migración EF, sin cambios en Web. `dotnet build Eleven.slnx` → "Compilación correcta", 0 errores, 18 warnings todos preexistentes. Sin smoke test propio (por regla del rol): se entregó guía manual de verificación al usuario.
