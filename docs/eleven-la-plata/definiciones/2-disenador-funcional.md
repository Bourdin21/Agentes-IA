# Memoria - Diseñador funcional

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

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

## Diseño — Lote 2026-10-01 (F1-F5)

Sobre Análisis del 2026-10-01 (`1-analista-funcional.md`). **Sin pantallas nuevas, sin ViewModels nuevos, sin migración EF.** Todo el lote son ajustes sobre pantallas existentes.

### Historias de usuario

**HU-F1.** Como Administrador, quiero que los movimientos de una cuenta se ordenen de forma estable dentro de un mismo día, para que el saldo acumulado de la última fila coincida con el saldo de la cuenta y pueda conciliar.
- CA: CA-F1.1 a CA-F1.3.
- **Decisión de diseño:** desempate determinístico por `Id` (orden de creación), en la **misma dirección** que el orden de `Fecha` — descendente por fecha ⇒ descendente por `Id`. Es la decisión ya validada en marihogar CR-14. No se agrega un selector de orden ni se cambia la columna por defecto.
- **Nota:** `Id` es el único desempate confiable. No se usa `CreatedAt` porque las filas migradas lo tienen seteado al momento de la migración, no al de la operación real.

**HU-F2.** Como Administrador, quiero que al cargar un movimiento desde una cuenta propia el tipo venga en "Egreso", para no tener que cambiarlo en el 99% de las cargas.
- CA: CA-F2.1 a CA-F2.3.
- **Decisión de diseño:** se preselecciona en el **ViewModel** al abrir el formulario, no en el `enum` ni en la vista. Cambiar el default del `enum TipoMovimiento` afectaría `CreateUnificado`, los filtros y cualquier otro consumidor — queda descartado.
- **Alcance visual:** el combo sigue mostrando las 3 opciones, sin deshabilitar nada.

**HU-F3.** Como Administrador, quiero volver a la cuenta desde la que cargué el movimiento, para seguir trabajando sobre esa cuenta sin re-navegar.
- CA: CA-F3.1 a CA-F3.4.
- **Decisión de diseño:** el `cuentaId` de contexto ya llega al formulario (`Create(int? cuentaId)`) y queda en `vm.CuentaId`. Al guardar, se redirige a `Cuentas/Details` con esa cuenta — **exactamente el patrón que ya usa `CreateUnificado`** en el mismo controller. No se agrega `returnUrl` ni parámetro nuevo: el dato ya está.
- **Transferencia:** se vuelve a la cuenta **origen** (`vm.CuentaId`), no a la destino. Es desde donde partió el usuario.
- **Fallback:** si no hubo cuenta de contexto, se conserva el redirect actual al listado — no se rompe esa ruta.
- **Fuera de alcance:** la pantalla `Movimientos/Index` sigue existiendo y accesible; solo se deja de aterrizar ahí.

**HU-F4.** Como Administrador, quiero ver el número de comprobante en los listados de movimientos, sobre todo en cuentas corrientes de clientes, para identificar el respaldo de cada movimiento sin abrir el detalle.
- CA: CA-F4.1 a CA-F4.3.
- **Decisión de diseño:** columna nueva en las 3 grillas, ubicada **después de la fecha** (es un identificador del movimiento, acompaña a la fecha; no al final, donde quedaría lejos en pantallas angostas). Dato sin comprobante ⇒ `—` en gris, igual que `motivoNombre` y `notas` en esas mismas grillas.
- **Sin cambio de backend:** `NumeroComprobante` ya viaja en `MovimientoDto`. Es cambio de vista puro.
- Cierra la deuda con **PAT-008**: hoy hay filtro por comprobante sin columna visible.

**HU-F5.** Como Administrador, quiero que el sistema no me deje guardar un contador menor al anterior de esa máquina, para que la facturación por copia no se rompa con un 0 cargado por error.
- CA: CA-F5.1 a CA-F5.6.
- **Decisión de diseño (regla única, elegida por el owner):** `contador >= último contador anterior a esa fecha`. Cubre los dos casos de un solo criterio — la máquina nueva sin historial acepta 0, y la máquina con historial no puede retroceder. **No** se valida "> 0" (rompería el alta legítima de máquina nueva).
- **Simetría obligatoria:** la validación corre en alta **y** en edición de contador, y en el contador inicial del alta de alquiler. Es la misma clase de asimetría Create/Update que ya produjo H1 y ELV-002 en este proyecto — se cierra de una.
- **En edición**, además del anterior, se valida contra el **siguiente** (no puede quedar por encima del posterior). Es la regla que `AlquilerService.ValidarContadoresAsync` ya aplica — se reutiliza ese criterio, no se inventa uno.
- **Color:** solo se valida si la máquina tiene `Color = true`, igual que la regla vigente.
- **Mensaje:** nombra el mínimo admitido, con separador de miles — "El contador B/N debe ser mayor o igual a 4.018.041".
- **Campos del formulario:** dejan de aceptar vacío-como-0 silencioso. El `[Range(0, int.MaxValue)]` se conserva (0 sigue siendo válido para máquina nueva); lo que agrega la barrera es la validación de servicio, no el atributo.

### Validaciones y mensajes (resumen)

| Caso | Resultado | Mensaje |
|---|---|---|
| Contador BN < último anterior | Rechaza | "El contador B/N debe ser mayor o igual a {min}" |
| Contador Color < último anterior, máquina Color | Rechaza | "El contador color debe ser mayor o igual a {min}" |
| Contador Color cualquiera, máquina B/N | Acepta | — (no se valida) |
| Máquina sin contadores previos | Acepta cualquier valor, 0 incluido | — |
| Edición: contador > siguiente | Rechaza | "El contador B/N debe ser menor o igual a {max}" |

### Impacto en pantallas
| Pantalla | Cambio |
|---|---|
| `Cuentas/Details` | Columna Nro. Comprobante + orden estable de la grilla |
| `Clientes/Details` | Columna Nro. Comprobante |
| `Movimientos/Index` | Columna Nro. Comprobante + orden estable |
| `Movimientos/Create` | Abre en Egreso; al guardar vuelve a la cuenta |
| `Maquinas/Details` (Historia de Contadores) | Mensaje de rechazo al cargar/editar un contador regresivo |
| `Alquileres/Create` | Mensaje de rechazo si el contador inicial es regresivo |

### Gate de aprobación
Diseño cerrado. Sin pantallas nuevas, sin migración. Pasa a Arquitectura.
