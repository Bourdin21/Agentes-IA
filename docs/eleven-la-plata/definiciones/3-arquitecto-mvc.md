# Memoria - Arquitecto MVC

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

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

## Arquitectura — Lote 2026-10-01 (F1-F5)

Sobre Diseño del 2026-10-01. **Sin migración EF** — ningún ítem toca el esquema. Riesgo global: **Bajo**, salvo F5 (Medio por efecto sobre operación diaria).

### Mapa por capa

| Ítem | Capa | Archivo | Cambio |
|---|---|---|---|
| F1 | Negocio | `Eleven.Infrastructure/Services/MovimientoService.cs:72-73` | Agregar desempate: `.ThenByDescending(m => m.Id)` en la rama `desc` y `.ThenBy(m => m.Id)` en la rama `asc` |
| F2 | Presentación | `Eleven.Web/Controllers/MovimientosController.cs:56-62` | En el `Create` GET, setear `vm.TipoMovimiento = TipoMovimiento.Egreso` |
| F3 | Presentación | `Eleven.Web/Controllers/MovimientosController.cs:104` | Reemplazar `RedirectToAction(nameof(Index))` por redirect a `Cuentas/Details` con `vm.CuentaId`, con fallback al Index si no hay cuenta |
| F4 | Presentación | `Views/Cuentas/Details.cshtml`, `Views/Clientes/Details.cshtml`, `Views/Movimientos/Index.cshtml` | `<th>` nuevo + entrada en `columns:` con `data: 'numeroComprobante'` |
| F5 | Negocio | `Eleven.Infrastructure/Services/MaquinaService.cs` (`CreateContadorAsync:268`, `UpdateContadorAsync`) | Validar contra contador anterior/siguiente antes de persistir |
| F5 | Negocio | `Eleven.Infrastructure/Services/AlquilerService.cs:317-335` | `AgregarHistoriaContadorSiCorresponde` deja de insertar sin comparar en el caso "sin anterior ni siguiente" |

**Capa de Datos: sin cambios en ningún ítem.** `NumeroComprobante` ya está mapeado y ya viaja en `MovimientoDto`.

### Decisiones técnicas

**F1 — por qué el desempate va en la query y no en memoria.** El listado es DataTables server-side con `Skip/Take`: sin un `ORDER BY` total, MySQL puede devolver la misma fila en dos páginas distintas o ninguna. El desempate por clave primaria hace el orden **total y estable**, que es además condición necesaria para que la paginación sea correcta — o sea, arregla un segundo bug latente de paginación, no solo el síntoma reportado. `GetSaldosAcumuladosAsync` **no se toca**: ya ordena `Fecha, Id`.

**F5 — reutilizar, no duplicar.** `AlquilerService` ya tiene `ValidarContadoresAsync(maquinaId, fecha, contadorBN, contadorColor)` (extraído en el fix H1 del 2026-08-20), que resuelve exactamente esta regla: busca anterior y siguiente, compara, respeta `maquina.Color`. **La validación de `MaquinaService` debe reutilizar esa lógica, no reescribirla.** Opción recomendada: mover el método a un lugar compartido (helper de dominio o servicio interno de contadores) y que ambos services lo consuman. Si eso resulta más invasivo de lo previsto, la alternativa aceptable es replicarlo con el mismo texto de mensajes — pero **duplicar criterio con mensajes distintos no es aceptable**, es la receta de la próxima asimetría.

**F5 — excluir la fila que se está editando.** En `UpdateContadorAsync`, la búsqueda de anterior/siguiente debe **excluir el propio `Id`**; si no, el registro se valida contra sí mismo y nunca pasa. `MaquinaService.ObtenerUltimoContadorBNAsync` ya recibe un id a excluir — mismo criterio.

**F3 — no introducir `returnUrl`.** El `cuentaId` ya está en el ViewModel. Un `returnUrl` agregaría superficie de validación (`Url.IsLocalUrl`) sin necesidad.

### Impacto en datos existentes
Ninguno. **Importante:** la validación de F5 es **prospectiva** — no corre sobre las 110 filas en 0 que ya están en producción, no las corrige ni las bloquea. El saneamiento de esas 69 filas regresivas es un trabajo aparte, fuera de este alcance.

### Riesgos técnicos

| Riesgo | Nivel | Mitigación |
|---|---|---|
| F5 frena una carga legítima que el operador hace todos los meses | **Medio** | La regla ">= anterior" solo rechaza retrocesos, que son siempre errores reales. Avisar al cliente antes del deploy de que ahora el formulario puede rechazar. |
| F5: al tocar `AgregarHistoriaContadorSiCorresponde` se regresiona el alta de alquiler (ya refactorizada en H1) | Medio | Prueba de regresión explícita de alta de alquiler (prueba 4 del ciclo H1, ya en el playbook de QA). |
| F1: cambiar el orden altera la primera página que ve el usuario | Bajo | Es el efecto buscado. Sin impacto en datos. |
| F4: la columna nueva desalinea el índice de columnas del JS de DataTables (`order`, `columnDefs`, `targets`) | Bajo | Revisar en cada vista que ninguna referencia por índice numérico quede corrida al insertar la columna. |
| F2: el default afecta un flujo no previsto | Bajo | Se setea en el VM de `Create`, que es consumido por una sola acción. `CreateUnificado` tiene su propio VM. |

### Estrategia de pruebas funcionales (para QA)
1. Cuenta con 3+ movimientos el mismo día: el acumulado de la primera fila en orden descendente == saldo del encabezado. **Y** paginar hacia adelante y atrás sin que se repita ni se pierda una fila.
2. Cuentas propias → cuenta → Nuevo movimiento: abre en Egreso. Cambiarlo a Ingreso y guardar: respeta lo elegido.
3. Cargar un egreso desde Efectivo → al guardar, caer en el detalle de Efectivo con el mensaje de éxito y el movimiento visible.
4. Transferencia desde cuenta A hacia B → vuelve a A.
5. Entrar a `Movimientos/Create` sin `cuentaId` → sigue yendo al listado (regresión).
6. Las 3 grillas muestran Nro. Comprobante; un movimiento sin comprobante muestra `—`; el filtro por comprobante del detalle de cuenta sigue filtrando.
7. Máquina con último contador 4.018.041: cargar 0 → rechaza nombrando el mínimo. Cargar 4.018.041 → acepta. Cargar 4.100.000 → acepta.
8. Máquina sin ningún contador: cargar 0 → **acepta** (CA-F5.4).
9. Editar un contador existente sin cambiarle el valor → guarda (no se valida contra sí mismo).
10. Editar un contador dejándolo por encima del siguiente → rechaza.
11. Máquina B/N (`Color = false`): el contador color no se valida.
12. Alta de alquiler con contador inicial menor al historial de la máquina → rechaza. Alta normal → sigue funcionando (regresión H1).

### Gate de aprobación
Arquitectura cerrada. 6 archivos, sin migración EF, sin cambio de esquema. Pasa a Presupuesto.

### Corrección de Arquitectura — 2026-10-01 (post-implementación, 2 desvíos aceptados)

El implementador levantó dos desvíos contra esta arquitectura. **Ambos aceptados por el orquestador; la arquitectura de arriba queda corregida en estos dos puntos.**

**1. `AlquilerService.AgregarHistoriaContadorSiCorresponde` NO se toca.** La arquitectura original pedía que dejara de insertar en el caso "sin contador anterior ni siguiente". **Eso era un error de la arquitectura: contradice CA-F5.4** (máquina sin contadores previos acepta cualquier valor, 0 incluido) y la prueba funcional 8. El código no puede distinguir "máquina recién instalada con contador 0" de "campo dejado en blanco" — y el criterio que eligió el owner es justamente ">= al anterior", que en ausencia de anterior no restringe nada. Además, el alta de alquiler **ya validaba** desde el fix H1 del 2026-08-20 (`CreateAsync` llama a `ValidarContadoresAsync`), así que CA-F5.3 queda cubierto sin tocar nada. La brecha real de F5 estaba **solo en `MaquinaService`**, que es exactamente lo que señalan los datos de producción (117 de 126 ceros con BN y Color en 0, firma de formulario en blanco; solo 15 de 110 coinciden con fecha de alquiler).

**2. F4 son 2 vistas, no 3.** Verificado por el orquestador: `Views/Clientes/Details.cshtml` **no tiene grilla propia de movimientos** — su única referencia es un link a `/Cuentas/Details/{id}` (línea 336), que es la misma grilla que ya se modificó. Los 3 puntos de uso que pidió el owner (cuenta propia, cuenta corriente de cliente, listado global) quedan cubiertos con `Cuentas/Details.cshtml` y `Movimientos/Index.cshtml`. **La cuenta corriente de cliente — el caso que el owner marcó como más importante — queda cubierta.**

**Archivo nuevo no previsto en la arquitectura, aceptado:** `Eleven.Infrastructure/Services/ContadorValidator.cs`. Es la materialización de la decisión "reutilizar `ValidarContadoresAsync`, no reescribirla": se movió a un helper compartido con `excludeId`, consumido por `MaquinaService` y por `AlquilerService` vía delegación. Es la opción recomendada por esta misma arquitectura.

Total real: **7 archivos** (6 previstos − 1 vista inexistente − 1 método no tocado + 1 helper nuevo).
