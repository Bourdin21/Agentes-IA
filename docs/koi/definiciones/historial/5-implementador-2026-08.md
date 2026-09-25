<!-- Archivado de docs/koi/definiciones/5-implementador.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 5-implementador - 2026-08 (2 bloques archivados)

- Etapa 14 — Fixes post-QA (4 ítems, sesión actual, 2026-08-13)
- Etapa 13 — Sprint UX/UI Inversor + fixes (2026-08-12)

---

### Etapa 14 — Fixes post-QA (4 ítems, sesión actual, 2026-08-13)

**Contexto:** 4 bugs puntuales detectados en QA manual del dueño del estudio sobre lo construido en Etapa 13. No pasaron por Análisis/Diseño/Arquitectura/Presupuesto — bugs ya relevados, causa raíz identificada de antemano por el pedido. Sin migración EF en ninguno. Sin escaneo de reutilización cross-proyecto (no son entidad/flujo nuevo, son correcciones puntuales sobre código propio ya existente).

1. **Dashboard Histórico no debía permitir ver meses abiertos ni futuros** — `DashboardService.ObtenerPeriodosAsync()` (`KoiDumplings.Infrastructure/Services/DashboardService.cs`) ahora filtra `.Where(p => p.Estado == EstadoPeriodo.Cerrado)` antes de materializar la query (confirmado por grep: único caller es `DashboardController.Index`, sin riesgo de romper otra pantalla). `DashboardController.Index` (`KoiDumplings.Web/Controllers/DashboardController.cs`) ajustó el fallback de período por defecto: con la lista ya filtrada a solo cerrados, toma `periodos.FirstOrDefault()` (el cierre más reciente, la lista ya viene ordenada desc) en vez de comparar contra `DateTime.Today`; `hoy.Year`/`hoy.Month` quedó solo como último fallback si no hay ningún período cerrado (ambiente vacío).
2. **EstadoResultados/Anual ordenaba alfabéticamente en vez de cronológicamente** — `Views/EstadoResultados/Anual.cshtml`: se agregó `data-order="@($"{m.Anio}{m.Mes:D2}")"` al `<td>` de la columna Período (ej. "202608" para agosto 2026), y se cambió `order: [[0, 'asc']]` a `order: [[0, 'desc']]` (más reciente primero, pedido explícito) más `columnDefs: [{ type: 'num', targets: 0 }]` explícito para que DataTables trate la columna como numérica (verificado con prueba aislada en Node que confirma que, al tener todos los valores el mismo largo fijo de 6 dígitos, la comparación como string ya coincidía con la numérica — se dejó `type: 'num'` de todas formas para no depender de esa coincidencia).
3. **Rename "Dashboard Histórico" → "Rendimiento Histórico"** — `Views/Shared/_Layout.cshtml` (única ocurrencia del texto, confirmado por grep, sección "Mi Cuenta" del bloque Inversor). `Views/Dashboard/Index.cshtml`: `ViewData["Title"]` pasó de fijo `"Dashboard"` a condicional `User.IsInRole("Inversor") ? "Rendimiento Histórico" : "Dashboard"` — Admin/SuperUsuario sin cambios. El `<h3>` visible de la página (línea ~14, texto "Dashboard" fijo) no se tocó — el pedido fue específico al título (afecta el `<title>` del navegador vía `_Layout.cshtml` línea 7), no un refactor cosmético del encabezado visible.
4. **Notificaciones — texto invisible en `<option>` de `#selectRol`** — causa raíz: `[data-theme="dark"] .form-select { color: var(--ov-text) }` (casi blanco) se hereda en el popup nativo de `<option>` que el navegador renderiza casi siempre con fondo claro real, sin heredar `background-color` del `<select>` de forma confiable. Fix en `KoiDumplings.Web/wwwroot/css/olvidata-theme.css`, sección "Form controls" (fuera de cualquier bloque `[data-theme]`, para que aplique siempre): regla nueva `.form-select option { color: var(--ov-gray-800); background-color: #ffffff; }`. Es global a todos los `<select class="form-select">` del sistema — cubre `Notifications/Crear.cshtml` y cualquier otro select existente o futuro con el mismo riesgo, sin trabajo adicional.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/Services/DashboardService.cs` (filtro `EstadoPeriodo.Cerrado`).
- `KoiDumplings.Web/Controllers/DashboardController.cs` (fallback de período por defecto).
- `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml` (`data-order` + `order desc` + `columnDefs` numérico).
- `KoiDumplings.Web/Views/Shared/_Layout.cshtml` (rename link sidebar).
- `KoiDumplings.Web/Views/Dashboard/Index.cshtml` (`ViewData["Title"]` condicional por rol).
- `KoiDumplings.Web/wwwroot/css/olvidata-theme.css` (`.form-select option` color/background explícitos).

**Migración EF:** ninguna.

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio) — evidencia de cierre: build limpio + revisión de código propia. Excepción puntual: fix 2 se verificó de forma aislada (fuera de la app) con un script Node que compara el orden de los valores `data-order` como string vs. como número sobre datos sintéticos con el mismo formato ("202601".."202608") — confirma que el orden coincide en ambos casos, dado el largo fijo de 6 dígitos; no reemplaza la prueba manual en la app real.

**Guía de pasos para prueba manual del dueño del estudio:**
1. **Dashboard Histórico**: como Inversor o Admin, entrar a "Rendimiento Histórico"/"Dashboard" → el combo de año/mes debe listar únicamente meses ya cerrados (no debe aparecer el mes en curso si todavía está abierto) → por defecto debe abrir en el cierre más reciente, no en el mes calendario actual.
2. **Historial de Resultados (Anual)**: entrar a `/EstadoResultados/Anual` de un año con varios meses cargados → la tabla debe mostrar los meses en orden cronológico descendente (ej. Agosto, Julio, Junio... no Abril, Agosto, Diciembre alfabético).
3. **Rename**: como Inversor, el link del sidebar en "Mi Cuenta" debe decir "Rendimiento Histórico" (no "Dashboard Histórico") y el título de la pestaña del navegador debe decir lo mismo. Como Admin, debe seguir diciendo "Dashboard" en sidebar y pestaña.
4. **Notificaciones**: como Admin, ir a "Nueva Notificación" → hacer click en el combo de Rol para abrir el popup nativo de opciones → el texto de cada opción debe verse en negro/oscuro y legible, tanto en tema claro como en tema oscuro.
### Etapa 13 — Sprint UX/UI Inversor + fixes (2026-08-12)

**Escaneo de reutilización (obligatorio antes de implementar):** re-confirmado el escaneo ya hecho en Diseño §11.0 — sin match cross-proyecto. Los 9 ítems son 100% reutilización de servicios/entidades propios de KOI (Dashboard, `IIndicadoresService`, `InversionesService`, sistema de notificaciones in-app ya existente). No se copió código de ningún otro proyecto del estudio.

**Alcance implementado (9 ítems, ver `1-analista-funcional.md` §12 para criterios de aceptación completos):**

1. **"Mes actual" (nueva, solo Inversor)** — `MesActualController` (`[Authorize]` simple) + `Views/MesActual/Index.cshtml`. Sin selector de período: siempre mes/año actual calculado en huso horario Argentina (`TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, "America/Buenos_Aires")`, mismo patrón que `CotizacionService.HoyArgentina()`/`FichadorController`, para no depender del huso del hosting site4now.net EE.UU.). Título dinámico "Rendimiento {Mes} {Año}". KPIs: Ventas Totales, Ticket Promedio, Cant. de Tickets, torta % por canal (Salón/Pedidos/Mostrador — se mantuvo el término "Pedidos" porque es el nombre real del campo en `IndicadoresDto`/`VentaMensual` y el que ya usa el Dashboard actual). Reutiliza `IIndicadoresService.ObtenerAsync(anio, mes)` tal cual — cero lógica de cálculo duplicada.
2. **"Dashboard Histórico" (relabel, solo Inversor)** — mismo `DashboardController`/`Views/Dashboard/Index.cshtml`/URL de siempre, sin tocar contenido. Solo el sidebar cambia el texto del link para Inversor.
3. **Rol "Encargado"** — `SeedData.RolEncargado` sembrado. Ve únicamente "Fichador" en el sidebar (bloque excluyente, no evalúa el resto de secciones). `FichadorController` usa una policy nueva `SoloAdministracionOFichador` (no se tocó `SoloAdministrador`, usada por otros 6 controllers).
4. **Fix del bug de puntos ("Wang")** — `InversionesService.AsignacionesVigentesQuery` → `AsignacionesVigentesAsync`, dedupe por inversor igual que `EstadoResultadosService`. Sin migración, sin tocar datos de producción. Verificación aislada de la lógica (detalle abajo): 95/15 tras el fix vs 102/16 antes.
5. **Reparto General simplificado** — tabla sin columna por inversor; `RepartoGeneralViewModel.NombresInversores` eliminado (sin uso). Desglose individual intacto en `RepartoFilaDto.Inversores` (Application), solo se dejó de renderizar en esta vista.
6. **Rename "Vista Anual ER" → "Historial de Resultados"** — título de página + `<h3>` en `Anual.cshtml`, y el link del sidebar en sus 2 apariciones (Admin/SuperUsuario e Inversor). Aplica a todos los roles, no solo Inversor.
7. **Notificaciones — composición nueva** — `INotificacionAdminService`/`NotificacionAdminService` nuevo (orquesta `INotificationService`+`IEmailService`, ninguno de los dos se modificó). `NotificationsController` extendido con `Crear`/`UsuariosPorRol`/`Enviar` (`SoloAdministrador`). Vista `Crear.cshtml`: combo de rol → AJAX → chips removibles → 2 checkboxes (correo/in-app, ≥1 obligatorio) → confirmación SweetAlert2 → resumen post-envío con detalle de fallos de email (no aborta el resto, mismo criterio que `NotificacionCierreService`). Link "Notificaciones" persistente para todos los roles autenticados (bandeja personal) + "Nueva Notificación" solo Admin/SuperUsuario.
8/9. **Mi Inversión — tabla de historial** — sin columnas Puntos/TC; Período dividido en Año/Mes (usa `MiInversionFilaDto.Anio`/`.Mes` ya existentes). Mes en palabras capitalizado vía helper nuevo `FormatoFecha.NombreMes(int)`. `ordering: false` en el DataTable (se saca el click-to-sort completo); el orden Año desc/Mes desc ya lo entregaba el servicio sin cambios.
10. **Fix global `.ov-monto`** — clase `white-space: nowrap` en `olvidata-theme.css`, aplicada en Dashboard/Liquidaciones/RepartoGeneral/MiInversión/MesActual/EstadoResultados (Mensual+Anual+PreviewCierre, solo celdas con patrón símbolo+espacio+número). Puntos/Index.cshtml revisada y descartada (no tiene celdas de importe monetario).

**Archivos nuevos:**
- `KoiDumplings.Web/Controllers/MesActualController.cs`, `KoiDumplings.Web/Models/MesActualViewModels.cs`, `KoiDumplings.Web/Views/MesActual/Index.cshtml`.
- `KoiDumplings.Web/Helpers/FormatoFecha.cs` (nombre de mes capitalizado, reutilizado por `MesActualController` y `MiInversion/Index.cshtml`).
- `KoiDumplings.Application/Interfaces/INotificacionAdminService.cs`, `KoiDumplings.Infrastructure/Services/NotificacionAdminService.cs`, `KoiDumplings.Web/Models/NotificationsViewModels.cs`, `KoiDumplings.Web/Views/Notifications/Crear.cshtml`.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/Services/InversionesService.cs` (fix Wang — `AsignacionesVigentesAsync` + caller).
- `KoiDumplings.Infrastructure/Data/SeedData.cs` (`RolEncargado`).
- `KoiDumplings.Web/Program.cs` (policy `SoloAdministracionOFichador`).
- `KoiDumplings.Web/Controllers/FichadorController.cs` (nueva policy).
- `KoiDumplings.Web/Controllers/RepartoGeneralController.cs`, `KoiDumplings.Web/Models/InversionesViewModels.cs` (sin `NombresInversores`).
- `KoiDumplings.Web/Views/RepartoGeneral/Index.cshtml`, `KoiDumplings.Web/Views/EstadoResultados/Anual.cshtml`, `KoiDumplings.Web/Views/MiInversion/Index.cshtml`, `KoiDumplings.Web/Views/Shared/_Layout.cshtml` (sidebar reestructurado: bloque Encargado excluyente, Dashboard/Mes actual condicional, Notificaciones persistente, rename Historial de Resultados x2).
- `KoiDumplings.Web/Controllers/NotificationsController.cs` (3 acciones nuevas), `KoiDumplings.Web/Views/Notifications/Index.cshtml` (botón "Nueva notificación" para Admin/SuperUsuario).
- `KoiDumplings.Infrastructure/DependencyInjection.cs` (registro `INotificacionAdminService`).
- `KoiDumplings.Application/DTOs/NotificationDtos.cs` (`UsuarioRolDto`/`EnviarNotificacionDto`/`ResultadoEnvioNotificacionDto`).
- `KoiDumplings.Web/wwwroot/css/olvidata-theme.css` (`.ov-monto`).
- `KoiDumplings.Web/Views/Dashboard/Index.cshtml`, `Views/Liquidaciones/Index.cshtml`, `Views/EstadoResultados/Mensual.cshtml`, `Views/EstadoResultados/Anual.cshtml` (celda adicional), `Views/EstadoResultados/PreviewCierre.cshtml` — clase `.ov-monto` aplicada a celdas de importe.

**Verificación del fix de puntos (Wang) — evidencia sin smoke test de la app:** se armó un proyecto console aislado (fuera del repo, en el scratchpad de la sesión) que reproduce EXACTAMENTE la misma lógica LINQ del fix (`GroupBy(InversorId)` + `OrderByDescending(VigenteDesdeAnio).ThenByDescending(VigenteDesdesMes).First()`) contra datos sintéticos calcados del escenario real documentado en `trazabilidad.md` (14 inversores de una sola vigencia + Wang con 2 vigencias: 7 pts desde 2024-01, 8 pts desde 2025-04). Resultado ejecutado:
```
=== ANTES del fix (bug) ===
Filas devueltas: 16
TotalAsignado: 102
Apariciones de 'Wang': 2

=== DESPUÉS del fix ===
Inversores devueltos: 15
TotalAsignado: 95
Wang aparece 1 sola vez, con 8 puntos vigentes (vigencia 2025/4)

RESULTADO: OK
```
Coincide exactamente con lo validado manualmente contra producción por el orquestador antes de presupuestar (`trazabilidad.md`, entrada 2026-08-12 orquestador). **No se tocó ninguna fila de `asignacionpuntos` en producción** — es un fix de query, no de datos.

**Migración EF:** ninguna — confirmado en las 9 ítems, coincide con Arquitectura §9.1.

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio) — evidencia de cierre: build limpio + revisión de código propia + verificación aislada de la lógica del fix Wang (detallada arriba, no es una prueba contra la app real ni contra producción).

**Decisiones técnicas tomadas en implementación (no explícitas en las 4 definiciones):**
1. Policy `SoloAdministracionOFichador` nueva para `FichadorController` en vez de agregar `Encargado` directo a `SoloAdministrador` (que la arquitectura citaba como opción) — se verificó por grep que otros 6 controllers (`Camaras`, `Inversores`, `EstadoResultados`, `Users`, `TipoCambio`, `Configuracion`) usan `SoloAdministrador`; modificarla habría abierto esas pantallas al rol nuevo, violando el criterio de aceptación del ítem 3.
2. Link "Notificaciones" (bandeja) visible a TODOS los roles autenticados (no solo Admin) — el diseño dejaba la decisión abierta ("decidí vos"); se optó por visibilidad universal porque la funcionalidad de bandeja personal ya existía y estaba abierta a cualquier autenticado (`NotificationsController` con `[Authorize]` simple desde antes de este sprint), solo faltaba el link. El Encargado no lo ve por el bloque excluyente del ítem 3.
3. Sidebar: el link "Dashboard"/"Mes actual" en la sección superior ("KOI") ahora tiene 3 ramas (Admin/SuperUsuario → Dashboard, Inversor → Mes actual, cualquier otro rol autenticado → Dashboard sin cambios) para no dejar sin link a Vendedor/Empleado, roles sembrados pero sin pantallas asignadas hoy — decisión conservadora, sin regresión, fuera del alcance explícito del sprint.
4. Helper `FormatoFecha.NombreMes(int)` nuevo en vez de reutilizar el `NombreMes(anio, mes)` privado de `InversionesService`/`DashboardService` — porque esos devuelven "Mes Año" (para el nombre del período) y la vista necesitaba solo la palabra del mes, sin año; se creó un helper de capa Web en `Helpers/` (mismo patrón que `FormatoMoneda`) en vez de exponer un método nuevo en Infrastructure, ya que es puramente de presentación.
5. Item 10: se aplicó `.ov-monto` con criterio — únicamente en celdas con el patrón literal del bug (símbolo `$`/`U$D`/prefijo "USD "/"TC:" + espacio + número). Las celdas de `EstadoResultados` que muestran solo un número `N2` sin símbolo (mayoría de `Mensual.cshtml`) se dejaron sin tocar por no reproducir el bug reportado (el diseño explícitamente no obligaba a tocar TODAS las celdas, solo las de importe con signo). `Puntos/Index.cshtml` no tiene celdas de importe monetario — se descartó tras revisión, no se tocó.

**Guía de pasos para prueba manual del dueño del estudio** (uno por ítem, calcado de los criterios de aceptación de `1-analista-funcional.md` §12.3):
1. **Mes actual**: login como Inversor → el sidebar debe decir "Mes actual" (no "Dashboard") → la pantalla debe mostrar "Rendimiento {mes actual} {año actual}" sin ningún selector, con Ventas Totales/Ticket Promedio/Cant. de Tickets y la torta Salón/Pedidos/Mostrador. Login como Administrador → debe seguir viendo "Dashboard" sin ningún cambio.
2. **Dashboard Histórico**: como Inversor, entrar a "Dashboard Histórico" (sección "Mi Cuenta") → debe verse exactamente igual al Dashboard actual, con su selector de mes/año y sus 3 secciones. Como Admin, el link debe seguir diciendo "Dashboard".
3. **Rol Encargado**: crear un usuario con rol único "Encargado" (vía `/Users` o directamente en Identity) → loguearlo → el sidebar debe mostrar ÚNICAMENTE "Fichador" → entrar a `/Fichador` debe funcionar → probar navegar manualmente a `/Dashboard`, `/MiInversion`, `/Inversores`, etc. → todas deben denegar el acceso (redirect a Access Denied, no contenido).
4. **Fix de puntos**: entrar a `/Puntos` con el período actual (o cualquiera desde abril 2025) → el total debe decir **95** (no 102) y Wang debe aparecer una sola vez con **8 puntos**. Revisar un período anterior a abril 2025 (ej. 2024) → sus valores no deben haber cambiado.
5. **Reparto General**: entrar a `/RepartoGeneral` → la tabla no debe tener ninguna columna con nombre de inversor, solo Período/Ventas/Resultado/Util. Punto/Util. Punto USD/Estado.
6. **Historial de Resultados**: el texto "Vista Anual ER" no debe aparecer en ningún lado del sidebar (ni para Admin ni para Inversor) → debe decir "Historial de Resultados" en ambos → el título de la página debe decir "Historial de Resultados {año}".
7. **Notificaciones**: como Admin, click en "Nueva Notificación" (sidebar o botón en "Notificaciones") → elegir un rol → debe cargar automáticamente los usuarios de ese rol como chips → sacar algún chip puntual con "×" → completar Asunto/Mensaje → tildar "correo", "in-app", o ambos → confirmar con el diálogo de SweetAlert2 → debe llegar la notificación in-app (campanita) y/o el email a los usuarios que quedaron en la lista, no a los que se sacaron. Probar enviar sin tildar ningún canal → debe bloquear con mensaje claro.
8/9. **Mi Inversión**: entrar como Inversor → la tabla de historial no debe reaccionar al click en los encabezados de columna (sin flechitas de orden, sin reordenar) → debe mostrar Año y Mes como columnas separadas al principio (mes en palabras, ej. "Agosto") → no debe tener columnas "Puntos" ni "TC" → el orden visual debe ser año más reciente primero, y dentro del año, mes más reciente primero.
10. **Importes sin salto de línea**: angostar la ventana del navegador (o usar el modo responsive de las devtools) en Dashboard, Mi Inversión, Reparto General, Estado de Resultados (mensual y anual), Liquidaciones — ningún importe con signo "$"/"U$D"/"USD" debe cortarse en dos líneas.
