# Memoria Implementador — KoiDumplings
# Última actualización: 2026-08-12 (sesión actual)

## Módulos implementados

### Etapa 13 — Sprint UX/UI Inversor + fixes (sesión actual, 2026-08-12)

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

### Etapa 12 — Fichador de empleados (QuickPass) — E2-02

**Escaneo de reutilización (obligatorio antes de implementar):** se re-confirmó el escaneo ya hecho en Diseño/Arquitectura (`docs/*/definiciones/{2-disenador-funcional,3-arquitecto-mvc,5-implementador}.md` de todos los proyectos del estudio) — sin match. Ningún proyecto tenía todavía un `HttpClient` tipado contra un SaaS externo de solo lectura con headers de auth estáticos. Se implementó desde cero. Este módulo queda como el primer patrón de "integración REST de solo lectura con ApiKey/IdEmpresa estáticos + dos APIs con base URL distinta" del estudio — candidato a reutilizar si aparece un caso similar (ver también nota de E2-01 Ayres en `1-analista-funcional.md` §10.1, que sigue pendiente de decisión API vs MySQL directo).

**Alcance implementado:** pantalla P-15 "Fichador" (solo Administrador/SuperUsuario) con 3 tabs — Hoy (fichadas del día), Rango de fechas (resumen de horas con `daterangepicker`), Empleados (listado QuickPass). Datos en vivo, sin persistencia local (confirmado sin migración EF).

**Archivos nuevos:**
- `KoiDumplings.Application/DTOs/QuickPassDtos.cs` — `HoraTrabajadaDiaDto`, `ResumenHorasUsuarioDto`, `EmpleadoQuickPassDto`.
- `KoiDumplings.Application/Interfaces/IQuickPassService.cs`.
- `KoiDumplings.Application/Exceptions/QuickPassIndisponibleException.cs` — carpeta `Exceptions/` nueva en Application (primera excepción de dominio propia del proyecto).
- `KoiDumplings.Infrastructure/Services/QuickPassSettings.cs` — POCO de configuración (mismo patrón que `SmtpSettings.cs`).
- `KoiDumplings.Infrastructure/Services/QuickPassService.cs` — implementación completa.
- `KoiDumplings.Web/Models/FichadorViewModels.cs` — `FichadorIndexViewModel` + 3 sub-ViewModels de ítem.
- `KoiDumplings.Web/Controllers/FichadorController.cs` — `Index`/`Rango`/`Empleados`, todas renderizan `Views/Fichador/Index.cshtml`.
- `KoiDumplings.Web/Views/Fichador/Index.cshtml` — 3 tabs Bootstrap, `daterangepicker`, 3 DataTables client-side, SweetAlert2 para errores de conexión.

**Archivos modificados:**
- `KoiDumplings.Infrastructure/DependencyInjection.cs` — `Configure<QuickPassSettings>`, dos `AddHttpClient` nombrados (`QuickPassEntidades`/`QuickPassReporting`) resolviendo headers desde `IOptions<QuickPassSettings>`, `AddScoped<IQuickPassService, QuickPassService>`.
- `KoiDumplings.Web/appsettings.json` — sección `QuickPass` nueva con las credenciales reales del cliente (`ApiKey`, `IdEmpresa=4364`, `BaseUrlEntidades`, `BaseUrlReporting`, `TimeoutSeconds=10`).
- `KoiDumplings.Web/Views/Shared/_Layout.cshtml` — link "Fichador" en sidebar, sección "Gestión", después de "Tipo de Cambio", visible solo para Administrador/SuperUsuario.

**Schema real descubierto por inspección directa (no publicado en el instructivo — hecho con `curl`/credenciales reales del cliente, autorizado explícitamente por el pedido; los archivos temporales con PII de empleados se borraron apenas terminó la inspección):**

- `GET /Usuarios?excluirFotos=true` (API Entidades) → array plano. Campos usados: `id, nombre, apellido, legajo, email, habilitado, fechaIngreso` (string `"yyyyMMdd"`), `sector.{id, nombre}`. 13 empleados activos en el ambiente real del cliente al momento de la prueba (todos `habilitado:true`).
- `GET /HorasTrabajadas` (API Reporting) → array de objetos usuario×día, ~70 campos por registro (`ParteParaReporteDTO` interno de QuickPass). Campos usados: `idUsuario, nombreUsuario, legajo, nombreSector, fecha` (ISO), `tieneMarcaciones, impar, ausente, tarde, esSectorBajas, horasNetas, movimientosList` (array de strings `"HH:mm"`), `idsMovimientos` (array de ids). **Hallazgo clave:** el campo `impar` (booleano) es exactamente el flag de "turno abierto/incompleto" que el diseño pedía calcular — cantidad impar de marcaciones en el día (ej. una sola fichada = entrada sin salida). Se verificó en vivo un caso real: empleado con `movimientosList: ["09:35"]`, `impar: true`. Mapeo usado: `HoraEntrada = movimientosList[0]`; `HoraSalida = movimientosList[^1]` solo si `!impar && Count >= 2`. `esSectorBajas: true` marca empleados dados de baja (aparecen en el reporte histórico aunque ya no estén activos) — se filtran del tab "Hoy" para respetar el criterio de HU-1 ("empleados activos"); verificado que los 13 registros con `esSectorBajas:false` de "hoy" coinciden 1 a 1 con los 13 usuarios de `/Usuarios`.
- `GET /HorasTrabajadas/ResumenPorUsuario` (API Reporting) → un objeto por usuario. Campos usados: `idUsuario, nombreUsuario, legajo, horasTrabajadasNetasDecimal, horasTrabajadasNetas` (string `"H:MM"` ya formateado por QuickPass), `cantidadDiasTrabajados, cantidadDiasAusente, cantidadDiasTarde`. **No trae** conteo de "turnos incompletos" ni "cantidad de fichadas" — el diseño (`FichadorRangoVM`) pedía esos dos campos pero no existen en este endpoint. Decisión de implementación (no estaba en ninguna de las 4 definiciones previas): `ObtenerResumenPorRangoAsync` hace una segunda llamada en paralelo a `/HorasTrabajadas` para el mismo rango y **agrega** (`Count`/`Sum`, no recalcula horas) el campo `impar` y el largo de `idsMovimientos` por usuario para completar `TurnosIncompletos`/`CantidadFichadas`. Es una agregación de valores ya calculados por la API, consistente con la simplificación de arquitectura §8.2/§8.8 ("el sistema no recalcula, solo proyecta").

**Decisiones técnicas tomadas en implementación (no explícitas en las 4 definiciones):**
1. "Hoy" se calcula en huso horario Argentina explícito (`TimeZoneInfo.FindSystemTimeZoneById("America/Buenos_Aires")`, igual patrón que `CotizacionService.HoyArgentina()`) — evita que "hoy" quede mal calculado si el hosting corre en otro huso (KOI corre en site4now.net, EE.UU.).
2. Se usó la policy `[Authorize(Policy = "SoloAdministrador")]`, no `"RequireAdministracion"` como decía literalmente el texto de arquitectura — porque `InversoresController`/`ConfiguracionController` (citados como precedente explícito en la arquitectura) usan `SoloAdministrador` en el código real. Ambas policies son funcionalmente idénticas en `Program.cs` (`RequireRole(SuperUsuario, Administrador)`) — no es un desvío de permisos, solo de nombre de policy.
3. Las 3 acciones del controller (`Index`/`Rango`/`Empleados`) renderizan la misma vista y cargan Hoy+Empleados siempre (eager) más Rango si hay fechas — se evitó AJAX/partials por simplicidad y porque el volumen es bajo. Cada sección tiene su propio try/catch contra `QuickPassIndisponibleException`: si una falla, las otras dos igual muestran datos (nunca pantalla en blanco completa, criterio de HU-4).
4. Validación de rango máximo 31 días duplicada: en el Controller (antes de llamar al service, con mensaje amigable para SweetAlert2) y en `QuickPassService` (`ArgumentException` como red de seguridad) — mismo criterio que `32-estandares-qa-implementador.instructions.md` para validaciones numéricas de negocio.

**Migración EF:** ninguna (confirmado por las 4 definiciones — sin entidades nuevas, QuickPass es la fuente de verdad).

**Build:** `dotnet build` desde la raíz del repo → **Compilación correcta, 0 errores.** 9 warnings preexistentes sin cambios (NU1902 MailKit/MimeKit — ver VUL-001 pendiente — y CS0114 HomeController.StatusCode), ninguno introducido por esta etapa.

**Sin smoke test funcional** (regla del estudio — el Implementador nunca levanta la app ni prueba flujos por navegador/curl contra el sistema propio). La inspección de la API externa de QuickPass con `curl` fue una excepción explícitamente autorizada por el pedido para descubrir el schema de deserialización antes de codear los DTOs — no es un smoke test del sistema KOI, es descubrimiento de contrato de un tercero. Evidencia de cierre: build limpio + esta revisión de código propia documentada acá.

**Guía de pasos para prueba manual del dueño del estudio:**
1. Login como Administrador (o SuperUsuario) → debe aparecer el link "Fichador" en el sidebar, sección "Gestión".
2. Tab "Hoy": debe listar los empleados activos con su fichada del día — entrada/salida si fichó completo, badge "Turno abierto" si fichó solo entrada, badge "Sin fichada hoy" si no fichó. Ninguna fila debe faltar ni quedar vacía sin explicación.
3. Tab "Rango de fechas": elegir un rango real (ej. últimos 7 días) con el `daterangepicker` → botón "Consultar" → debe mostrar horas trabajadas, cantidad de fichadas, turnos incompletos y días ausente por empleado. Probar un rango de más de 31 días → debe mostrar el mensaje de error de rango máximo sin romper la pantalla.
4. Tab "Empleados": debe listar todos los empleados de QuickPass con su estado Activo/Inactivo, igual a lo que se ve en el panel de QuickPass.
5. Caso de error: cambiar transitoriamente el valor de `QuickPass:ApiKey` en `appsettings.json` a un valor inválido y reiniciar → visitar `/Fichador` → debe aparecer un SweetAlert2 con el mensaje "No se pudo conectar con el sistema de fichadas..." en vez de una excepción visible o pantalla en blanco. Restaurar la ApiKey real después de la prueba.
6. Verificar que un usuario con rol Inversor no puede acceder a `/Fichador` (debe redirigir/denegar, no mostrar contenido).

### Etapa 11 — Migraciones aplicadas en PRODUCCIÓN (sesión actual)
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migraciones aplicadas en PRODUCCIÓN"). Resumen: `dotnet ef database update` creó las 22 tablas en `db_a7251f_koidump` (site4now.net, estaba vacía — primer aprovisionamiento). Seed básico (roles/catálogo/SuperUsuario) y la migración histórica completa (misma plantilla validada en local) quedaron aplicados: 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones, capital USD 287.500 — idéntico a lo validado en local.
- **Nota operativa importante:** el hosting MySQL remoto cortó la conexión dos veces durante operaciones con muchas escrituras secuenciales chicas (el seed de catálogo, con un `SaveChangesAsync` por Rubro sin transacción envolvente, y el primer intento de import vía navegador). Si se vuelve a tocar esta base desde una herramienta con timeout corto, preferir sondeo directo a la base en vez de esperar la respuesta HTTP/navegación.
- SuperUsuario de producción quedó con las credenciales por defecto del código (decisión explícita del cliente) — pendiente cambiarlas antes de exponer el sitio públicamente.
- Sin cambios de código — solo despliegue de esquema (EF) y datos (mecanismo de importación ya existente).

### Etapa 10 — Migración histórica ejecutada en local
- Ver detalle completo en `trazabilidad.md` (entrada 2026-07-13, "migración histórica ejecutada"). Resumen: ambos Excel fuente transformados a la plantilla de `ImportacionInicialService` y cargados vía el endpoint real `/ImportacionInicial` (SuperUsuario), tras vaciar los datos de demo en la DB local. 19 períodos, 373 gastos, 15 inversores, 16 asignaciones, 265 liquidaciones — 0 advertencias. Total Gastos reconcilia al centavo contra el Excel en los 19 períodos; capital migrado = USD 287.500 (coincide con el análisis funcional).
- Sin cambios de código — solo datos, vía el mecanismo de importación ya existente.
- Ejecutado y validado en el **entorno local** únicamente (pendiente replicar en el entorno del cliente cuando corresponda).

### Etapa 9 — Fix sistémico tema oscuro
- Pedido del cliente: alinear el tema oscuro en la totalidad del sistema (no pantalla por pantalla) porque había elementos ilegibles.
- **Diagnóstico (Playwright headless contra la app corriendo local, login real + cookie `koi-tema=dark` para simular SSR fresco):**
  - **Causa raíz:** el proyecto usa Bootstrap **5.1.0** (no 5.3+), cuya `.table` fija `color: #212529` como literal — no vía variable CSS. El override existente `[data-theme="dark"] .table { --bs-table-color: ... }` seteaba una variable que Bootstrap 5.1 nunca lee, dejando el texto de **todas** las tablas/listados (DataTables incluidos) ilegible en oscuro en todo el sistema.
  - `.card-header`/`.card-footer` (y sus variantes `.ov-card-*`) usaban el token fijo `--ov-gray-50` (nunca redefinido en `[data-theme="dark"]`) → cabeceras de card blancas sobre fondo oscuro en toda la app.
  - Paginación de DataTables (`.page-link`, vía `dataTables.bootstrap5`) sin override de tema → botones "Anterior/Siguiente" blancos.
  - `#themeToggle` (botón, no link) sin `background:none` explícito → heredaba el fondo blanco por defecto del user-agent para `<button>`, visible como caja blanca en el topbar oscuro (bug independiente del tema, agravado en oscuro).
  - Alerts nativas de Bootstrap (`.alert-info/success/warning/danger`, usadas directo en varias vistas) sin override de tema.
  - Chart.js en sí NO tenía bug de renderizado (los `isDark` checks de cada vista funcionan bien en carga fresca), pero el toggle de tema es 100% client-side (solo cambia el atributo `data-theme`, sin reload) — los canvases ya creados quedan con los colores calculados en el load anterior hasta que el usuario navega a otra pantalla. Confirmado visualmente comparando toggle-en-vivo vs carga fresca con cookie ya seteada.
- **Fix aplicado (single-file, sin tocar vistas individuales):**
  - `KoiDumplings.Web/wwwroot/css/olvidata-theme.css`: dentro de `[data-theme="dark"]` se agregó `color: var(--ov-text)` directo en `.table`/`.table-light` (más `--bs-table-striped-color/--active-color/--hover-color`), override de `.card-header`/`.card-footer`/`.ov-card-header`/`.ov-card-footer` (fondo `rgba(255,255,255,.03)`), override de `.page-link`/`.page-item.active/.disabled` (paginación DataTables), y override de `.alert-info/success/warning/danger` + `.alert-link`. Fuera del bloque dark: `.ov-topbar-icon-btn` ahora fija `background:none; border:none` (fix general, no solo oscuro).
  - `Views/Shared/_Layout.cshtml`: el click de `#themeToggle` ya no togglea el atributo `data-theme` en vivo — espera la respuesta de `POST /Account/ToggleTema` (que ya persistía la cookie server-side) y hace `location.reload()`. Esto elimina de raíz toda la clase de bugs "toggle sin reload" (Chart.js con colores viejos, y cualquier futuro widget JS que lea el tema solo al cargar) sin necesitar un sistema de re-theming en vivo.
- **Validación:** recompilado (`dotnet build` OK) y verificado visualmente con Playwright headless (login real, click real en el botón de tema, screenshots antes/después) en Dashboard, Estado de Resultados Mensual, Vista Anual ER, Tipo de Cambio, Configuración/Rubros, Inversores — 0 errores de consola, todas las tablas/cards/paginación/alerts legibles en oscuro tanto en carga fresca como en toggle en vivo.
- **Sin migración EF** — cambio 100% de presentación (CSS + un handler JS).
- **Impacto cross-proyecto:** `olvidata-theme.css` es el design system compartido por todos los proyectos del estudio sobre el mismo blankproject base — si otro proyecto activo (ShowroomGriffin, vinosefue, virtualwallet, etc.) usa Bootstrap 5.1 con el mismo archivo de tema, probablemente tenga el mismo bug de tablas/card-headers en oscuro y valga la pena portar el mismo fix.

### Etapa 8 — Refactor UI/UX: fusión Dashboard + Indicadores
- Autorizado directamente por el cliente/dueño del estudio como refactor puntual de UI sobre dos pantallas ya aprobadas (sin ciclo completo Análisis→Diseño→Arquitectura→Presupuesto): sin entidades nuevas, sin migración EF, mismos DTOs/servicios reutilizados.
- **Escaneo de reutilización:** no aplica búsqueda cross-proyecto (no es una entidad/flujo nuevo) — el propio proyecto KOI ya tenía ambas piezas (`IIndicadoresService`/`IndicadoresService`/`IndicadoresDto` como fuente de verdad de KPIs de venta) y se reutilizaron tal cual desde `DashboardService`.
- **Cambio funcional:** pantallas `Dashboard` e `Indicadores` (KPIs de venta) se fusionan en una sola pantalla `Dashboard` con 3 secciones diferenciadas (Ventas / Gastos / Evolución Histórica) + hero de KPIs de resultado global (Ventas Totales, Total Gastos, Resultado, Resultado USD, Rentabilidad %). Todo el contenido —incluido el desglose Facturado(A)/Informal(B) antes solo-Admin— queda visible para todos los roles autenticados (Admin, SuperUsuario, Inversor) bajo `[Authorize]` simple.
- **Domain/Application:** `DashboardDto` (KoiDumplings.Application/DTOs/DashboardDtos.cs) se simplifica — se quitan los campos duplicados que ya calculaba `IndicadoresDto` (VentasA, VentasSalon, VentasPedidos, VentasMostrador, CantidadComensales, CantidadVentas, TicketPromedioA, TicketPromedio, CubiertoProm) y se agrega `public IndicadoresDto? Ventas { get; set; }` como fuente única para la sección "Ventas". Se mantienen los campos propios del hero (VentasTotales, TotalGastos, ResultadoEjercicio, Rentabilidad, TipoCambio, ResultadoUsd, TieneTipoCambio).
- **Infrastructure:** `DashboardService` (KoiDumplings.Infrastructure/Services/DashboardService.cs) inyecta `IIndicadoresService` y delega en él el cálculo de todos los KPIs de venta (`ObtenerAsync(anio, mes)` reutilizado tal cual); ya no recalcula manualmente ticket promedio, cubierto promedio, ventas por canal, etc. Solo conserva lógica propia: existencia de ventas del período (`AnyAsync`, no recalcula KPIs — solo determina `TieneDatos`), gastos por rubro, total de gastos, resultado del ejercicio, rentabilidad %, TC y resultado en USD. `DependencyInjection.cs` no requirió cambios (`IIndicadoresService` ya estaba registrado como Scoped).
- **Web:**
  - `Views/Dashboard/Index.cshtml` reescrita completa: header + selector (sin cambios), hero de 5 KPIs con el estilo de card de Indicadores (icon badge circular, `border-0 shadow-sm`), sección "Ventas" (todo el contenido de la ex-pantalla Indicadores: KPIs, torta canal + barras ticket, tabla desglose por canal, tabla A/B + torta + barras apiladas), sección "Gastos" (tabla Gastos por Rubro existente + nuevo gráfico de barras horizontales por rubro + torta Resultado-vs-Gastos reubicada desde el Dashboard viejo), sección "Evolución Histórica" (gráfico de líneas sin cambios funcionales, reubicado al cierre). Cada sección tiene encabezado diferenciado (icon badge + accent de color: azul=Ventas, rojo=Gastos, verde=Histórico).
  - `IndicadoresController.cs`, `Views/Indicadores/Index.cshtml` e `IndicadoresIndexViewModel` (en `IndicadoresViewModels.cs`) eliminados — sin otras referencias en el repo (verificado por grep antes de borrar).
  - `Views/Shared/_Layout.cshtml`: eliminado el link "Indicadores de Venta" del sidebar (sección "Gestión"). El link "Dashboard" ya era visible para todos los roles, sin cambios.
- **Permisos:** `DashboardController` sigue `[Authorize]` simple (Admin/SuperUsuario/Inversor), sin cambios. El contenido antes restringido a `RequireAdministracion` (Facturado vs Informal) ahora es visible para todos los roles autenticados dentro del Dashboard fusionado — cambio de negocio explícito del cliente, no un descuido de permisos. La policy `RequireAdministracion` sigue vigente y en uso en otros controllers (NotificacionCierre, RepartoGeneral, Liquidaciones, Puntos, Audit) — no se tocó.
- **Sin migración EF** — no se tocaron entidades de dominio ni `VentasMensuales`/`ConceptosGasto`.
- **Build:** `dotnet build` desde la raíz del repo → Compilación correcta, 0 errores (9 warnings preexistentes: NU1902 MailKit/MimeKit — ver VUL-001 pendiente — y CS0114 HomeController.StatusCode, ninguno introducido por este cambio).
- **No hay proyecto de tests automatizados en el repo** (`**/*Tests*.csproj` → sin resultados); validación queda a cargo de QA manual.

### Etapa 7 — ABM Inversores
- InversoresController.cs creado en KoiDumplings.Web/Controllers
- Acciones: Index, Create (GET/POST), Edit (GET/POST), Delete (POST, soft-delete vía IRepository<Inversor>)
- Guard en Delete: bloquea si el inversor tiene usuario vinculado (ApplicationUser.InversorId)
- ViewModels: InversorListViewModel, InversorListItemViewModel, InversorFormViewModel (en ConfiguracionViewModels.cs)
- Vistas: Views/Inversores/Index.cshtml, Create.cshtml, Edit.cshtml
- Sidebar: link 'Inversores' agregado en sección 'Inversiones' (antes de Puntos)
- Sin migración EF (entidad Inversor ya existía)
- Build: PASS

### Bugs resueltos en sesión anterior
- KOI-002: Export Excel ER Anual
- KOI-005: CamarasController
- KOI-006: Link Notificaciones → System

## Pendientes
- KOI-007: Users/Index DataTables
- KOI-008: TipoCambio/Index DataTable init
- VUL-001: MailKit/MimeKit → 4.17.0
- Etapa 13: sin pendientes técnicos nuevos — falta únicamente la prueba manual del dueño del estudio (guía completa en la entrada de la Etapa 13, arriba).
