# Memoria - Implementador — crm-olvidata — historial 2026-08

Archivado el 2026-10-15 desde `5-implementador.md` para respetar el techo de 150 KB
(`39-presupuesto-contexto`). Son sprints CERRADOS: el estado vigente vive en el archivo activo.

## Implementación de gestión comercial y herramientas de canal/venta (2026-08-16)

### 0. Escaneo de reutilización

Se escanearon los `5-implementador.md` de los 20 proyectos de `docs/`. Resultado: **nada reutilizable a nivel entidad/servicio para el núcleo de este alcance.** Existe una entidad `Cliente` en `ShowroomGriffin`, `la-platense`, `marihogar` y `vino-y-se-fue`, pero es un cliente de venta de mostrador (cuenta corriente, condición de IVA, facturación AFIP) — dominio distinto del `Cliente` de este CRM (contacto que cerró, con plan, ticket anual, renovación y NRR). No hay en ningún proyecto `Upsell`, cálculo de NRR, catálogo de templates de WhatsApp, experimento A/B ni pipeline kanban. Sí se reutilizaron **patrones internos del propio proyecto** (criterio de "no desarrollar desde cero" aplicado hacia adentro): DataTables server-side con whitelist de orden por índice de columna (`IndustriasController`/`ContactosController`), acciones AJAX con respuesta JSON (`CampanasController`), confirmación SweetAlert2 (`Industrias/Index`), `ov-stat-card` (`Bot/Index`), y el modal Bootstrap + partial compartido para no duplicar el alta de cliente entre `Contactos/Details` y `Chats/Detail`.

### 1. Alcance funcional resumido

CU-21 a CU-29 (`1-analista-funcional.md`), 8 piezas: `Cliente`, `Upsell`, dashboard de negocio, dashboard de campañas, catálogo de templates, A/B testing, asistente de redacción y pipeline visual. 5 entidades nuevas + 1 enum + 1 campo en `ContactoRespuesta`, 1 migración EF, 3 controllers nuevos y 3 extendidos.

### 2. Plan de ejecución técnica ejecutado (por etapas)

1. Domain: 5 entidades + `EstadoAprobacionMeta` + `ContactoRespuesta.VarianteExperimento`.
2. Application: `NegocioStatsDto`, `CampanaStatsDto`, `NegocioSettings`.
3. Infrastructure: `AppDbContext` (5 `DbSet` + configuración), split A/B en `OutboundCampaignService`, registro de `NegocioSettings` en DI.
4. Web: 5 grupos de ViewModels, `ClientesController`/`NegocioController`/`TemplatesController` nuevos, `CampanasController`/`ContactosController`/`ChatsController` extendidos, 9 vistas nuevas y 7 modificadas.
5. Build → migración `AddGestionComercial` → aplicación en dev → smoke test autenticado local → aplicación en producción por SQL directo → deploy.

### 3. Cambios por capa

- **Domain**: `Cliente.cs`, `Upsell.cs`, `TemplateWhatsApp.cs`, `CampanaExperimento.cs`, `SugerenciaSeguimiento.cs`, `Enums/EstadoAprobacionMeta.cs` (nuevos); `ContactoRespuesta.cs` (+`VarianteExperimento`).
- **Application**: `DTOs/NegocioStatsDto.cs`, `DTOs/CampanaStatsDto.cs`, `Settings/NegocioSettings.cs` (nuevos). Sin interfaces nuevas ni cambios de firma en las existentes (`IWhatsAppClient`/`IOutboundCampaignService` intactas), según Arquitectura §2.
- **Infrastructure**: `AppDbContext.cs` (5 `DbSet` + configuración de precisión/longitudes/FK: `Cascade` en `Upsell`→`Cliente` y `CampanaExperimento`→`CampanaOutbound`, `Restrict` en los 2 FK a `TemplateWhatsApp` y en `Cliente`→`Contacto`); `OutboundCampaignService.cs` (split A/B con semilla determinística por contacto + baja de la lista fija `TemplatesDisponibles`); `DependencyInjection.cs` (`NegocioSettings`).
- **Web**: controllers `ClientesController.cs`, `NegocioController.cs`, `TemplatesController.cs` (nuevos); `CampanasController.cs` (+`Dashboard`, +`ConfigurarExperimento`, selector de template desde BD), `ContactosController.cs` (+`Pipeline`, +`ClienteId` en `Details`), `ChatsController.cs` (+`SugerirMensaje`, +`ClienteId` en `Detail`). ViewModels: `ClienteViewModels.cs`, `NegocioViewModels.cs`, `TemplateWhatsAppViewModels.cs`, `CampanaDashboardViewModels.cs`, `PipelineViewModels.cs` (nuevos) + campos en `ContactoViewModels`/`ChatViewModels`/`CampanaOutboundViewModels`. Vistas nuevas: `Clientes/Index|Details|Edit`, `Negocio/Dashboard`, `Templates/Index|Create|Edit`, `Campanas/Dashboard`, `Contactos/Pipeline`, `Shared/_ConvertirClienteModal`. Vistas modificadas: `Shared/_Layout` (sección "Negocio"), `Contactos/Details`, `Contactos/Index`, `Chats/Detail`, `Campanas/Edit`, `Campanas/Index`, `Bot/Index`.
- **Config**: `appsettings.json` → `Olvidata_Negocio:MetaAnualUsd` (default 0 = "meta no configurada").

### 4. Migración EF aplicada

`20260817003040_AddGestionComercial` — 5 tablas (`Clientes`, `Upsells`, `TemplatesWhatsApp`, `CampanasExperimento`, `SugerenciasSeguimiento`) + 1 columna aditiva (`ContactoRespuestas.VarianteExperimento varchar(1) NULL`). Sin `defaultValue` en ninguna columna de fecha/hora (problema conocido de DDL inválido con este proveedor MySQL). Aplicada en dev con `dotnet ef database update`; en producción por SQL directo generado con `dotnet ef migrations script` + su `INSERT` en `__EFMigrationsHistory`, sin correr `database update` contra la base productiva.

Migración de **datos** (no de código, según Arquitectura §3): 1 fila en `TemplatesWhatsApp` (`olv_frio_v3`, `EstadoAprobacionMeta=Aprobado`, `Activo=1`) en dev y producción, para que las campañas ya cargadas (85 activas en producción, todas con `olv_frio_v3`) no queden sin template válido el día del corte. Además, 6 filas de `SugerenciasSeguimiento` — ver riesgos.

### 5. Evidencia de build y pruebas

- `dotnet build -c Release` → **0 errores** (13 warnings, todos preexistentes). Las vistas Razor compilan en build en este proyecto (verificado a propósito introduciendo un error deliberado en una vista y confirmando que la compilación falla).
- Smoke test **autenticado** local (dev, HTTPS, sesión real por cookie): 200 en `/Clientes`, `/Negocio/Dashboard`, `/Templates`, `/Templates/Create`, `/Campanas/Dashboard`, `/Contactos/Pipeline`, `/Contactos/Details/{id}`, `/Chats/Detail/{id}`, `/Campanas/Edit/{id}`, `/Campanas/Create`, más los flujos POST reales: conversión Contacto→Cliente (302 a la ficha del cliente), alta de upsell (JSON OK), alta de template, alta de experimento A/B y su validación de A=B (rechazada, base sin cambios), y `SugerirMensaje` devolviendo el texto correcto con placeholders resueltos.
- Verificación numérica del NRR contra datos de prueba: base 1200 + upsell 300 → 125%; con el cliente dado de baja → 25%; sin período anterior → "Datos insuficientes". Los datos de prueba se borraron de dev al terminar.
- Producción: deploy Web Deploy exitoso al primer intento, `https://portal.olvidata.com.ar/` → 200, y las 5 rutas nuevas → 302 (redirect a login, rutas vivas).

### 6. Riesgos y supuestos

- **Bug encontrado y corregido durante la propia implementación:** el churn del NRR se comparaba tomando `.Date` directo sobre `UpdatedAt` (UTC) contra días calendario argentinos — una baja cargada después de las 21hs ART caía en el día UTC siguiente, quedaba fuera del período y el NRR salía inflado (125% en vez de 25% en la prueba). Corregido pasando por `ArgentinaTime.From()` antes de truncar. Es el mismo tipo de bug ya documentado en `ArgentinaTime`, reaparecido en código nuevo.
- **No hay campo de fecha de churn en el modelo aprobado.** El churn se marca con `Activo=false` y se fecha con el stamping de auditoría (`UpdatedAt`) como proxy: si un cliente dado de baja se edita después por otro motivo, su fecha de churn se corre a esa edición. Con la cartera actual (decenas de filas) es aceptable; si se vuelve un problema, hace falta un campo propio y una migración.
- **`SugerenciaSeguimiento` no tiene pantalla de mantenimiento** — ni el Diseño ni la Arquitectura definen una, y tampoco definen el contenido del catálogo. Se cargaron 6 filas genéricas como borrador para que el botón "Sugerir" no nazca inerte; hoy solo son editables por SQL. Los textos necesitan revisión del cliente (o de `olvidata-marketing`) antes de considerarse definitivos.
- **`AvanceMeta` no tiene valor definido en ninguna definición.** Se implementó como setting (`Olvidata_Negocio:MetaAnualUsd`), default 0 → la card muestra "Meta no configurada" en vez de inventar un porcentaje.
- **El split A/B no se probó con envíos reales** (implicaría mandar WhatsApp de verdad a contactos reales). La lógica está verificada por lectura: `new Random(contacto.Id)` es determinístico por contacto, así que un reintento no cambia de variante.
- **`Pais` del dashboard de campañas** se infiere de `ZonaHoraria` (mapa fijo de 7 zonas) y cae a `Region` si no matchea — riesgo ya asumido en Arquitectura §7.
- Todos los cruces contacto↔campaña y el cálculo de NRR se resuelven **en memoria** (`ToListAsync()` primero), nunca con `Contains()` sobre una colección local dentro de una query — el proveedor MySQL de este proyecto no lo traduce.

### 7. Pruebas mínimas requeridas para QA

1. `Contactos/Details` de un contacto en estado distinto de Cerrado: **no** debe verse el botón "Convertir en Cliente". Cambiar el estado a Cerrado → aparece.
2. Convertir un contacto Cerrado: el modal precarga fecha de alta = hoy y renovación = hoy + 1 año; cambiar la fecha de alta debe mover la renovación sola, salvo que ya se haya editado a mano. Al guardar redirige a `Clientes/Details`. Volver a `Contactos/Details` → ahora muestra "Ver cliente".
3. Intentar convertir dos veces el mismo contacto → error "ya tiene un cliente activo asociado" y redirección al cliente existente.
4. `Clientes/Index`: filtros por plan, estado y vencimiento; semáforo rojo (<30 días), ámbar (<90) y verde. Ordenar por cada columna.
5. `Clientes/Details`: alta de upsell sin recargar la página, actualización de "Upsells acumulados" y "Valor total"; eliminar un upsell con confirmación y ver que los totales bajan.
6. `Negocio/Dashboard`: con cartera vacía, NRR = "Datos insuficientes" (no 0%). Con clientes de más de un año y upsells, verificar el porcentaje a mano. Dar de baja un cliente y confirmar que el NRR baja.
7. `Templates`: alta de un template Borrador → **no** debe aparecer en el selector de `Campanas/Create`. Pasarlo a Aprobado + Activo → aparece. Intentar borrar un template usado por una campaña activa → bloqueado con mensaje.
8. `Campanas/Edit`: con menos de 2 templates aprobados, la card A/B avisa que faltan templates. Con 2, guardar un experimento 70/30, verificar el badge del header. Intentar A = B → rechazado.
9. `Campanas/Dashboard`: contrastar la tasa de respuesta de alguna campaña contra el mismo dato filtrado en `Contactos/Index`.
10. `Contactos/Pipeline`: los conteos por columna deben coincidir con el resumen de embudo de `Contactos/Index`; el link "Ver los N" de una columna debe abrir el listado ya filtrado por ese estado.
11. `Chats/Detail`: botón "Sugerir" prellena el textarea sin enviar nada; con texto ya escrito pide confirmación antes de pisarlo; en un contacto sin sugerencia aplicable avisa "Sin sugerencia disponible".
12. Regresión del outbound: con una campaña **sin** experimento activo, el envío diario debe comportarse igual que antes (mismo template configurado, `VarianteExperimento` nulo en `ContactoRespuestas`).

### 8. Checklist de salida para merge

- [x] `dotnet build -c Release` → 0 errores, sin warnings nuevos.
- [x] Migración `AddGestionComercial` generada, aplicada en dev y en producción (producción por SQL directo + `INSERT` manual en `__EFMigrationsHistory`).
- [x] Datos de arranque cargados en ambas bases (`olv_frio_v3` + 6 sugerencias), verificados con acentos correctos (utf8mb4).
- [x] Lógica de negocio en controllers/servicios, no en vistas; sin lógica nueva en Controllers que corresponda a un Service (se siguió el criterio explícito de Arquitectura §2 de no crear una capa de servicio para NRR/métricas).
- [x] Design system aplicado: DataTables server-side, SweetAlert2 en todas las confirmaciones, `ov-card`/`ov-stat-card`/`ov-badge`, sin CDNs nuevos.
- [x] Smoke test autenticado de las 11 pantallas/endpoints nuevos en dev + verificación de rutas en producción.
- [x] Deploy a producción por Web Deploy (nunca FTP), `https://portal.olvidata.com.ar/` → 200.
- [ ] QA funcional completo (ver guía arriba) — pendiente, hand-off al cliente.
- [ ] Revisión de los textos de `SugerenciasSeguimiento` con el cliente/`olvidata-marketing` — pendiente.
- [ ] Definir `Olvidata_Negocio:MetaAnualUsd` con el cliente — pendiente.

## Corrección de bugs/gaps de auditoría completa + 3 mejoras (2026-08-27)

### 0. Escaneo de reutilización

Escaneados los `5-implementador.md` de todos los proyectos de `C:/Sistemas/Agentes-IA/docs/*/definiciones/`. **Sin match reutilizable**: los 17 items son correcciones sobre lógica propia y específica de este CRM (pipeline outbound de WhatsApp, ventana de 24hs de Meta, embudo comercial de Olvidata) — no hay una entidad/flujo equivalente ya construido en otro proyecto del estudio del que copiar. Lo que sí se reutilizó fue **patrón interno del propio repo**: el bloqueo de `Delete` de `TemplatesController` como molde para B5, el helper de toast de `Campanas/Edit.cshtml` para G5, y el criterio de stamping manual de `UpdatedAt` al usar `ExecuteUpdateAsync` (G6) replicado después en G7/M-B.

### 1. Alcance funcional resumido

7 bugs (B1-B7) + 7 gaps (G1-G7) + 3 mejoras (M-A/M-B/M-C) del sprint cerrado en Análisis/Diseño/Arquitectura el 2026-08-27. Origen: auditoría funcional completa de `agentes-ia-qa`. **0 migraciones EF** (confirmado en Arquitectura §7.1 y respetado: no se generó ninguna).

### 2. Plan de ejecución técnica ejecutado (por etapas)

1. **Fundación compartida (M-A)** — `MensajeriaHelpers` en `Application` como fuente única de las etiquetas de mensaje saliente, el truncado y la fórmula de "Respuesta→Presupuesto". Todo lo demás se apoya en esto.
2. **Infrastructure (B1, B2, G1, G2, B6-fuente, M-C-servicio)** — `OutboundCampaignService` y los hosted services.
3. **Web/Chats (B3, B4, G5, G6)** — `ChatsController` + vistas de Chats.
4. **Web/resto (B5, B7, G3, G4, G7, M-B, M-C-vista)** — Templates, Contactos, Clientes, Industrias, Campañas, Bot.
5. **Build de verificación** tras cada etapa (4 corridas intermedias + 1 final).

> **Nota de continuidad**: la corrida anterior de este agente se cortó por watchdog a mitad de B3. Al retomar se auditó item por item contra el código en disco (no contra la memoria de la sesión), lo que detectó que B3 estaba **a medio hacer**: el lado servidor (`HiloParcial` con el parámetro nuevo) estaba escrito, pero el JS que debía mandarlo no — y como el fallback por diseño es "sin parámetro, comportamiento anterior", el bug **seguía reproduciéndose al 100%** pese a que el código "parecía" hecho y el build daba verde. Ver B3 abajo.

### 3. Cambios por capa

**Application** (2 archivos nuevos, 1 interfaz extendida)
- `Helpers/MensajeriaHelpers.cs` **(nuevo)** — **M-A**. Constantes de las 5 etiquetas salientes (incluida `EtiquetaErrorEnvio`, nueva de G1), `EsMensajeSaliente`/`EsMensajeEntrante`, `Truncar` (**B1**), `TuvoPresupuesto` + `TuvoPresupuestoExpr` + `CanalesOutbound` (**B6**). Decisión deliberada documentada en el archivo: las etiquetas son `const string` y las condiciones se siguen escribiendo inline en los `Where` de EF — el compilador inlinea la `const` en el árbol de expresión, así que la traducción a SQL de esas subqueries (ya afinadas contra este proveedor de MySQL) no cambia en absoluto.
- `DTOs/SaludOutboundDto.cs` **(nuevo)** — **M-C**. 5 bloques de diagnóstico + sub-DTOs.
- `Interfaces/IOutboundCampaignService.cs` — `GetSaludAsync` (**M-C**).

**Infrastructure**
- `Services/OutboundCampaignService.cs` — **B1** (`Truncar` en los puntos de escritura de `ContactoRespuesta.Respuesta` + `catch (DbUpdateException)` por contacto, para que un fallo de guardado no aborte la campaña entera dejando mensajes ya enviados sin registro); **B2** (`RebalancearMatrizAsync` expande cada campaña a sus días individuales en vez de agrupar por la combinación de flags; a una campaña multi-día se le aplica el factor de escala **más restrictivo** de sus días, para que ningún día quede por encima de la meta); **G1** (`BuildComponentsDinamico` cuenta los `{{N}}` reales del texto del catálogo en vez de mandar 3 parámetros fijos, + tope de reintentos por contacto y registro del fallo con `EtiquetaErrorEnvio`); **G2** (shuffle de equidad por día del año subido a `CampanasActivasHoyAsync`, el único punto por el que pasan tanto la corrida manual como la automática, + `UltimaCorridaUtc` sellado sin importar el disparador); **B6** (fuente de la fórmula, ahora delegada al helper); **M-C** (`GetSaludAsync`).
- `HostedServices/VentanaExpiracionSchedulerService.cs` — **M-A**: las 4 declaraciones locales duplicadas pasan a salir del helper, y se agrega `EtiquetaFollowUp`/`EtiquetaErrorEnvio` a las 3 subqueries de "último mensaje entrante" que las tenían desincronizadas.
- `HostedServices/MensajesProgramadosSchedulerService.cs` — **B3** (deja de tocar `FechaUltimaLecturaAgente` al disparar un envío: ese campo significa que un HUMANO leyó, no que el sistema mandó algo) + **M-A** + **B1**.
- `DependencyInjection.cs` — registro del scheduler de mensajes programados.

**Web — Chats**
- `Controllers/ChatsController.cs` — **B4** (6 literales faltantes agregados a `EtiquetasDeEvento`, verificados uno por uno contra los call sites reales de `BotFlowService`, no de memoria; además `EtiquetaErrorEnvio` se renderiza como evento centrado y no como burbuja saliente, que era la misma trampa que B4); **B3** (`HiloParcial(int id, int? ultimoIdVisto)` solo toca el estado de lectura si `ultimoIdActual > ultimoIdVisto`, con fallback retrocompatible); **G5** (`MarcarNoLeido`/`MarcarTodosLeidos` devuelven `Json(new { ok, mensaje })`); **G6** (`ExecuteUpdateAsync` en `MarcarTodosLeidos`); **M-A**.
- `Views/Chats/_ChatThread.cshtml` — **B3**: `data-msg-id` en cada burbuja/evento, para que el JS pueda calcular el máximo Id renderizado.
- `Views/Chats/Detail.cshtml` — **B3**: el polling manda `ultimoIdVisto` en cada tick, releyéndolo del DOM (no de una variable) para que quede correcto tras cada reemplazo del hilo.
- `Views/Chats/Index.cshtml` — **G5**: helper `toast()` (mismo patrón que `Campanas/Edit.cshtml`), `.done()/.fail()` en vez de `.always()`, y la lista solo se refresca si `ok=true`.

**Web — resto**
- `Controllers/TemplatesController.cs` — **B5**: `Edit` bloquea el **rename** si hay campañas activas apuntando al nombre viejo (editar texto/rubro/país/estado sigue permitido — es el caso frecuente y no rompe la referencia por nombre).
- `Controllers/ContactosController.cs` — **B6** (embudo sobre universo outbound + fórmula del helper), **B7**/**G4** (Create/Edit escriben `CanalOrigen`/`ReferidoPor`/`MotivoReferido`/`PresupuestoCotizadoUsd`, con `NormalizarReferido` descartando los datos de referido si el canal final no es Referido).
- `Controllers/CampanasController.cs` — **B6** (fórmula del helper en las 2 proyecciones del dashboard), **G7** (`EliminarIndustria` informa cuántos contactos quedan sin campaña que los alcance).
- `Controllers/ClientesController.cs` — **G3**: `ConvertirDesdeContacto` setea `PrimerAnioGratis`.
- `Controllers/IndustriasController.cs` — **G7** + **M-B**: `ImpactoDelete` (GET, JSON con el conteo de afectados + alternativas de reasignación) y `Delete(id, reasignarA)` que reasigna en la misma operación, validando que el destino exista en el catálogo.
- `Controllers/BotController.cs` — **M-C**: acción `Salud` (solo lectura).
- `Models/ContactoViewModels.cs` — **B7**/**G4**: 4 propiedades nuevas en `ContactoCreateViewModel` (heredadas por Edit).
- `Models/ClienteViewModels.cs` — **G3**: `PrimerAnioGratis` en `ConvertirClienteViewModel`.
- `Views/Contactos/_CamposCanalYPresupuesto.cshtml` **(nuevo)** — **B7**/**G4**: bloque compartido por Create y Edit, en un partial a propósito para que no puedan desincronizarse (misma clase de problema que M-A resuelve en el back).
- `Views/Contactos/Create.cshtml` / `Edit.cshtml` — incluyen el partial + JS de toggle de los campos de referido.
- `Views/Shared/_ConvertirClienteModal.cshtml` — **G3**: switch de primer año gratis.
- `Views/Industrias/Index.cshtml` — **G7**/**M-B**: el modal pide el impacto real al servidor y ofrece un `<select>` de reasignación (antes afirmaba, engañosamente, que los contactos "no se ven afectados").
- `Views/Bot/Salud.cshtml` **(nuevo)** + `Views/Bot/Index.cshtml` — **M-C**.

### 4. Migración EF

**Ninguna.** Confirmado contra Arquitectura §7.1 — los campos que hacían falta (`Contacto.CanalOrigen`/`ReferidoPor`/`MotivoReferido`/`PresupuestoCotizadoUsd`, `Cliente.PrimerAnioGratis`) ya existían en el esquema y solo faltaba exponerlos en ViewModels/Views. No se generó ni aplicó ninguna migración.

### 5. Evidencia de build

`dotnet build -c Release` → **`Compilación correcta. 0 Errores`** (13 advertencias en rebuild limpio, todas preexistentes — el baseline antes de este sprint era 14: `NU1902` de MailKit/MimeKit, `CS8524` de switches sobre `DayOfWeek`, `CS0114` de `HomeController.StatusCode`; las advertencias `CS8620` de `ChatsController` bajaron de 3 a 2 al quitar un `RouteValueDictionary`).

Verificación adicional: se comprobó explícitamente que **las vistas Razor sí se compilan en el build** de este proyecto (se introdujo un `@Model.PropiedadInexistente` deliberado en `Bot/Salud.cshtml`, el build falló con `CS1061` señalando archivo y línea, y se revirtió). Sin esa comprobación, un build verde no habría sido evidencia de que las 10 vistas tocadas son válidas.

**No se hizo deploy ni se tocó producción** (fuera de alcance de esta corrida).

### 6. Riesgos y supuestos

- **B3** es el item con mayor riesgo de "parecer hecho sin estarlo": el fallback retrocompatible (sin `ultimoIdVisto` → comportamiento anterior) es deliberado para no dejar chats marcados como no leídos durante la ventana de deploy, pero significa que **un cliente con la página vieja cacheada sigue reproduciendo el bug hasta que recargue**. QA debe validar con hard-refresh.
- **G6/M-B**: `ExecuteUpdateAsync` no pasa por `AppDbContext.SaveChangesAsync`, así que el stamping automático de `UpdatedAt`/`UpdatedByUserId` no corre. Se replica a mano en ambos call sites — si se agregan más usos de `ExecuteUpdateAsync` en el futuro, hay que repetirlo o se pierde auditoría en silencio.
- **G1** conserva el alcance reducido declarado en Diseño: N placeholders de texto sí, botones QUICK_REPLY dinámicos no. Deuda declarada.
- **B6**: el tablero Kanban de `Contactos/Pipeline` se sigue armando sobre TODOS los contactos a propósito (es la vista operativa de "qué tengo en cada etapa"); lo que se alineó al universo outbound es solo el **embudo de conversión**, que es la métrica comparable entre las 3 pantallas. Es una decisión de alcance, no un olvido.
- **B5** bloquea el rename pero no ofrece migrar las campañas automáticamente — el SuperUsuario tiene que desactivar o reasignar primero. Consistente con el patrón ya existente en `Delete`.
- **G5**: `MarcarNoLeido` tiene DOS invocadores con expectativas distintas (el AJAX de `Chats/Index` y un form POST normal de `Chats/Detail`). Se negocia la respuesta por `X-Requested-With` en vez de devolver JSON a secas — si se hubiera cambiado a JSON sin más, el usuario de `Chats/Detail` habría visto un volcado de JSON crudo en el navegador.

### 7. Pruebas mínimas requeridas para QA

1. **B3 (crítico)** — abrir un chat en una pestaña, dejarlo en background >8s, marcarlo "No leído" desde `Chats/Index` en otra pestaña, esperar 2-3 ticks: **debe seguir figurando No leído**. Después mandar un mensaje entrante real a ese contacto: el chat debe volver a marcarse leído solo cuando el hilo abierto lo renderice. Hacer hard-refresh antes de probar.
2. **B4** — abrir el hilo de un contacto que haya pasado por el cuestionario del bot: no debe aparecer ninguna burbuja saliente con texto como "Rubro", "Motivo de contacto", "Consulta inicial" o el aviso de away-message.
3. **B5** — intentar renombrar un template asignado a una campaña activa → debe bloquear con mensaje explícito. Editar solo su texto → debe permitir.
4. **B6** — comparar "Respuesta → Presupuesto" en `Bot/Outbound`, `Contactos/Pipeline` y `Campanas/Dashboard`: los 3 números deben coincidir. `Bot/Salud` lo verifica solo.
5. **B7 + G4** — alta manual de contacto con canal "Referido" + quién lo refirió + presupuesto cotizado; verificar que se ven en `Contactos/Details` y en la card de `Chats/Detail`. Cambiar el canal a otro y guardar → los datos de referido deben limpiarse.
6. **G3** — convertir un contacto cerrado en Cliente marcando "primer año gratis"; verificar que el ARR del Dashboard no lo cuenta.
7. **G5** — marcar no leído y "marcar filtrados como leídos" desde `Chats/Index`: debe aparecer un toast de confirmación en ambos casos. Probar también "Marcar como no leído" desde `Chats/Detail` → debe redirigir al listado, **no** mostrar JSON.
8. **G6** — "Marcar todos como leídos" con filtro "Todos" sobre la base completa: debe responder rápido y sin picos de memoria.
9. **G7 + M-B** — eliminar una industria con contactos asociados: el modal debe decir cuántos son y ofrecer reasignarlos; al confirmar con destino elegido, verificar que los contactos quedaron con el rubro nuevo. Repetir sin elegir destino → debe avisar cuántos quedaron huérfanos.
10. **M-C** — `/Bot/Salud` debe cargar sin error y sus conteos deben ser coherentes con lo que se ve en Templates/Campañas/Contactos.
11. **Regresión B1/B2/G1/G2** — correr el pipeline manualmente (`Bot/Ejecutar ahora`) y verificar que no aborta, que `UltimaCorridaUtc` queda sellada, y que el rebalanceo de matriz da un resumen coherente con el volumen real por día.

### 8. Checklist de salida para merge

- [x] `dotnet build -c Release` → 0 errores, sin advertencias nuevas.
- [x] 0 migraciones EF (confirmado contra Arquitectura §7.1 — no se generó ninguna).
- [x] Compilación de vistas Razor verificada explícitamente (no asumida).
- [x] Lógica de negocio en Services, no en Controllers (la fórmula de B6 y el truncado de B1 viven en `Application`, no en los controllers que los consumen).
- [x] Design system aplicado: SweetAlert2 en los modales nuevos (G7/M-B) y en los toasts (G5), `ov-card`/`ov-card-header`/`badge` en `Bot/Salud`, sin CDNs nuevos.
- [x] Los 17 items auditados uno por uno contra el código en disco, no contra la memoria de la sesión.
- [ ] QA funcional (ver §7) — pendiente, hand-off.
- [ ] Deploy a producción — pendiente, **explícitamente fuera de alcance de esta corrida**.

### 9. Corrección post-QA — CRM-007 / CRM-010 / CRM-012 (2026-08-27, misma fecha)

Respuesta al NO-GO de QA. Alcance acotado: los 2 defectos con causa raíz en el vocabulario de `Contacto.Rubro` (CRM-007 bloqueante + CRM-010, su gemelo no bloqueante) y CRM-012. **CRM-008 descartado por el cliente**: la migración `AddMensajeProgramado` sí está aplicada en producción — QA probó contra `olvidatacrm_dev` y confundió esa base con producción. **CRM-009 / CRM-011 / CRM-013 quedan documentados y fuera de esta corrida** por decisión explícita.

**Decisión de diseño que QA escaló (la que faltaba tomar):** el vocabulario canónico de `Contacto.Rubro` es **`CampanaOutboundIndustria.ClaveRubro`** (rubroBase, con sufijo de región opcional: `comercio-palermo`). No es `IndustriaCatalogo.Nombre`. Razones, en orden de peso: (1) es literalmente lo que compara `OutboundCampaignService.SendDailyBatchAsync` para decidir qué campaña alcanza a un contacto; (2) es lo que parte `BotFlowService` por el primer `-` para resolver la industria cuando el contacto responde; (3) `IndustriaCatalogo.Nombre` es de menor granularidad a propósito — `ganaderia` y `agro` comparten una fila de precio, y `farmacia`/`estudio` no tienen fila de catálogo en absoluto —, así que no puede representar el rubro operativo sin perder información; (4) los datos lo confirman: 434 de 435 contactos llevan claves, 0 llevan un nombre de catálogo.

**Cambios por capa:**

| Capa | Archivo | Cambio |
|---|---|---|
| Application | `Helpers/RubroHelpers.cs` **(nuevo)** | Fuente de verdad única del vocabulario. Se le movieron **tal cual** los 2 diccionarios que vivían privados en `BotFlowService` (`OutboundTypeToIndustry`, `IndustryToCatalogoNombre`), más `RubroBase()`, `IndustriaDeClaveRubro()`, `CatalogoNombreDeClaveRubro()` y `EtiquetaDeClaveRubro()`. Motivo: Web necesitaba traducir clave→industria→catálogo con el **mismo** mapeo que el bot; un segundo mapeo se desincroniza (es la clase de duplicación que ya causó B4 y M-A en este mismo sprint). |
| Application | `DTOs/SaludOutboundDto.cs` | CRM-012: `Alineadas` pasa de campo con setter (hardcodeado en `true`) a **propiedad calculada** sobre la nueva lista `PorPantalla` — ya no existe forma de fijarla a mano. Nuevo `PantallaFormulaDto` (pantalla, universo, numerador, denominador, tasa). |
| Infrastructure | `Services/BotFlowService.cs` | Los 2 diccionarios quedan como alias de `RubroHelpers`. Sin cambio de comportamiento (mismos datos, mismo comparador `OrdinalIgnoreCase`, mismos call sites). |
| Infrastructure | `Services/OutboundCampaignService.cs` | CRM-012: `GetSaludAsync` calcula la métrica "Respuesta→Presupuesto" **tres veces, una por pantalla, con el universo real de cada una** (Bot/Outbound y Contactos/Pipeline sobre outbound-que-respondió; Campañas/Dashboard sobre enviados-con-rubro-de-campaña y sin exigir respuesta). Contactos/Pipeline se evalúa con el overload **en memoria** del helper contra el `Expr` traducible de las otras, así que el bloque también cruza las 2 implementaciones de la fórmula. |
| Web | `Controllers/IndustriasController.cs` | CRM-007. `ImpactoDelete`/`Delete` cuentan y reasignan por `ClaveRubro`. Nuevo `ClavesDeLaIndustriaAsync` (resuelve por FK `IndustriaCatalogoId` y, si está en null, por el mapeo clave→industria→catálogo). `ContarContactosDeClavesAsync` compara en memoria contra el set de claves — mismo criterio que `GetSaludAsync` y sin chocar con MH-001. `AlternativasDeReasignacionAsync` devuelve **ClaveRubro de campañas activas**, excluyendo las que este mismo borrado deja huérfanas. El `Delete` valida el destino contra ese conjunto y hace un `ExecuteUpdateAsync` **por clave** (un `Contains()` sobre lista local de string no traduce a SQL en este proveedor). |
| Web | `Controllers/ContactosController.cs` | CRM-010. `GetRubrosDisponiblesAsync` deja de devolver `IndustriaCatalogo.Nombre` y devuelve las `ClaveRubro` reales, marcando cuáles tienen campaña activa. |
| Web | `Models/ContactoViewModels.cs` | Nuevo `RubroOpcionViewModel` (`Valor` = lo que se guarda, `Etiqueta` = presentación, `TieneCampanaActiva`). Separar los 2 es exactamente lo que faltaba: antes se guardaba la etiqueta. |
| Web | `Views/Contactos/Create.cshtml` + `Edit.cshtml` | El selector guarda la clave real y muestra la etiqueta amigable, en 2 `optgroup` ("Con campaña activa (entra al circuito outbound)" / "Sin campaña activa"). `Edit` conserva además el rubro actual como opción cuando ninguna campaña lo alcanza, para no pisarlo al editar otro campo. |
| Web | `Views/Industrias/Index.cshtml` | El modal manda la clave como `value` y muestra la etiqueta; lista las claves afectadas en el texto y distingue "esta industria no tiene rubros asociados" de "los tiene pero sin contactos". |
| Web | `Views/Bot/Salud.cshtml` | Tabla comparativa pantalla-por-pantalla + alerta cuando las tasas divergen. |

**Evidencia (medida contra `olvidatacrm_dev`, solo lecturas):** `dotnet build -c Release` → **0 errores**, 13 advertencias, todas preexistentes. El conteo de impacto con el criterio corregido deja de dar 0: Retail/comercio minorista **155**, Laboratorios/consultorios **104**, Alquiler de inmuebles **58**, Utilities **38**, Ganadería **35**, Estudios contables **28**, Farmacias **1** (las otras 9 industrias no tienen ninguna `ClaveRubro` asociada, así que 0 es la respuesta correcta y el modal ahora lo dice con esas palabras). Destinos de reasignación ofrecidos: **26 `ClaveRubro` de campañas activas** (antes: 16 nombres de catálogo, ninguno de los cuales matcheaba una campaña). En dev las 26 industrias de campaña tienen `IndustriaCatalogoId` poblado, así que el camino de respaldo por mapeo no se ejercitó — queda como red de seguridad, documentado.

**Riesgos y supuestos de esta corrección:**
- No se toca `BotFlowService`: al responder, el bot sigue reescribiendo `Contacto.Rubro` con el nombre de industria del diálogo. Es comportamiento legacy y deliberado (ese contacto ya salió del match de campañas). Por eso `ImpactoDelete` **no** cuenta esos contactos: reasignarlos les rompería la conversación en curso. Si se quiere unificar también ese tramo, es un sprint aparte con backfill de datos.
- El selector de Rubro ya no ofrece las 16 industrias del catálogo, sino las claves reales. Es un cambio visible de UI para el SuperUsuario: la lista es más larga y los valores tienen sufijo de región.
- `Alineadas` ahora puede dar **false** en dev y en producción, porque Campañas/Dashboard tiene un universo deliberadamente más angosto (el mismo punto que QA marcó en B6). Eso es la alerta funcionando, no una regresión: la tabla nueva dice qué pantalla difiere y por qué.
- 0 migraciones EF. Sin deploy: pendiente de re-test de QA.

**Pruebas mínimas para el re-test de QA:** (1) `GET /Industrias/ImpactoDelete/{id}` para las 16 industrias → los 7 números de arriba, no ceros; (2) `POST /Industrias/Delete/{id}` con `reasignarA` = una `ClaveRubro` activa → los contactos quedan con esa clave y `SendDailyBatchAsync` los levanta; repetir con un nombre de catálogo → debe **rechazarlo** con el mensaje de "no pertenece a ninguna campaña activa"; (3) alta manual de un Referido eligiendo un rubro del grupo "Con campaña activa" → verificar en BD que `Rubro` quedó con la clave y que el contacto entra al lote; (4) `Edit` de un contacto con rubro heredado → la opción actual sigue seleccionada y no se pisa al guardar; (5) `/Bot/Salud` → la tabla nueva muestra las 3 pantallas y el badge refleja de verdad si coinciden.

## Matriz de módulos valorizados + borrador de propuesta MVP/FULL (2026-08-27)

Feature nueva, diseñada y aprobada por el cliente antes de esta corrida (no fue una decisión abierta). Reglas de negocio: agente **`olvidata-presupuesto-bot`** (`C:\Users\joaco\.claude\agents\olvidata-presupuesto-bot.md`), dueño de la matriz y de las 9 reglas de redacción del mensaje. Datos: primera carga hecha por `olvidata-ceo` escaneando los **27 `4-presupuestador.md` reales** del estudio.

**Qué resuelve.** Después de la demo, Joaquín armaba el borrador de propuesta a mano desde cero. Ahora elige el rubro, ajusta un checklist pre-tildado con los imprescindibles y obtiene los 2 rangos (MVP/FULL) y el mensaje redactado. Es una **herramienta interna**: no reintroduce la cotización automática del bot (retirada el 2026-08-24) y nada sale sin que un humano lo revise y apriete Enviar.

### Escaneo de reutilización

Se buscó en `C:\Sistemas\Agentes-IA\docs\*\definiciones\5-implementador.md` una entidad/flujo comparable (catálogo valorizado por rubro + generador de propuesta). **Sin match**: los otros proyectos tienen catálogos de precios de productos/prácticas, no un catálogo de *módulos de software* con flag MVP/FULL por rubro. Sí se reutilizaron patrones **dentro de este mismo repo**, que es lo que corresponde: CRUD `IRepository<T>` + DataTable server-side de `IndustriasController`; acordeón/lista + AJAX inline de `Campanas/Edit.cshtml` para la asignación de rubros; SweetAlert2/DataTables/`ov-card`/`ov-badge` del design system; `SoftDestroyable` + query filter global.

### Modelo de datos y migración

| Tabla | Detalle |
|---|---|
| `ModulosCatalogo` | `NombreCliente` (vocabulario de cliente, se copia tal cual al WhatsApp), `TipoModulo` (**string libre, no enum** — la lista de tipos crece con cada presupuesto y no queremos una migración por tipo nuevo), `PrecioMinUsd`/`PrecioMaxUsd` (18,2), `Precedente` (proyectos reales que anclan el precio). |
| `ModuloCatalogoIndustrias` | Join N:N con `EsImprescindible`. El flag vive **en la relación y no en el módulo** porque el mismo módulo puede ser MVP en un rubro y sólo FULL en otro. FK a `ModulosCatalogo` en **Cascade**, FK a `IndustriasCatalogo` en **Restrict** — mismo criterio que `CampanaOutboundIndustria`. |

Migración **`20260828023654_AddModuloCatalogo`**: sólo `CREATE TABLE` de las 2 tablas + 3 índices. **No toca ninguna tabla existente**, así que el riesgo sobre datos de producción es nulo. Aplicada en `olvidatacrm_dev` (`dotnet ef database update`, `migrations list` sin pendientes). **NO aplicada en producción ni deployada** — por instrucción explícita del cliente.

### Seed de la matriz real

`SeedData.SeedModulosCatalogoAsync`, idempotente **por fila** (mismo criterio y mismo motivo que `SeedIndustriasCatalogoAsync`: un guard por-tabla dejaría sin sembrar cualquier módulo agregado después de la primera corrida — el bug real de julio con Farmacias/Estudios contables). Sobre un módulo ya existente sólo agrega rubros faltantes: **nunca pisa precios ni el flag MVP/FULL**, que después de la primera carga son dato curado a mano por el SuperUsuario.

Resultado verificado en dev: **84 `ModuloCatalogo`, 88 asignaciones, 9 industrias con matriz, 62 imprescindibles.**

| Rubro | Módulos | MVP | Rango MVP (USD) | Rango FULL (USD) |
|---|---|---|---|---|
| Retail / comercio minorista | 14 | 6 | 510 – 806 | 991 – 1653 |
| Laboratorios / consultorios médicos | 14 | 10 | 637 – 1051 | 871 – 1387 |
| Dietéticas y comercios de venta de productos | 11 | 8 | 386 – 774 | 487 – 942 |
| Alquiler de maquinaria | 11 | 7 | 452 – 713 | 769 – 1152 |
| Estudios contables / jurídicos | 10 | 9 | 354 – 587 | 404 – 654 |
| Ganadería / producción agropecuaria | 8 | 7 | 565 – 897 | 582 – 967 |
| Recolección de residuos / logística de campo | 7 | 4 | 168 – 304 | 360 – 551 |
| Landing page / sitio sin sistema de gestión | 7 | 6 | 194 – 260 | 261 – 344 |
| Utilities / gestión de reclamos y cuadrillas | 6 | 5 | 335 – 590 | 464 – 783 |

**88 asignaciones sobre 84 módulos** porque 3 módulos se comparten entre rubros (misma N:N que existe justamente para eso): "Usuarios y roles" (Retail + Dietéticas + Laboratorios), "Reportes básicos" (Dietéticas + Laboratorios) y "ABM Tipo de servicio" (Utilities + Residuos). Se comparten **sólo** cuando coinciden tipo, rango y flag; cuando algo difiere van filas separadas, porque precio y flag son datos del rubro y no del nombre — el caso testigo es "Facturación electrónica AFIP/ARCA" (67-151/FULL en Retail contra 100-184/MVP en Dietéticas).

**5 de las 14 industrias quedan sin matriz, a propósito**: E-commerce, Finanzas personales, Finanzas simples, Farmacias y **Alquiler de inmuebles**. Las 4 primeras las declaró el cliente; la quinta la detectó esta corrida (el pedido enumeraba 9 con datos + 4 sin datos = 13, y el catálogo tiene 14). No se inventó nada para ninguna: sin presupuesto real relevado no hay precio con ancla. La pantalla lo dice explícitamente en vez de mostrar un checklist vacío.

### Generador del mensaje — `IPropuestaMvpFullService`

Vive en **Application** (`Services/PropuestaMvpFullService.cs`), no en Infrastructure: no toca base, red ni reloj — es una función pura de (rubro, módulos tildados) a texto, y por eso es la única pieza del feature verificable leyendo su salida. **Determinístico: no llama a ningún agente de IA en runtime.** Las 9 reglas están marcadas `[R1]`..`[R9]` en el código, junto al renglón que las implementa.

3 decisiones que no estaban en el pedido y hubo que tomar:
- **Enumeración truncada.** Con más de 4 módulos, los 4 de mayor precio con comas y "y N más". La primera versión daba "…, stock e inventario **y** facturación AFIP/ARCA **y** 5 más" (dos "y" seguidas): se detectó ejecutando el generador y viendo el texto, no leyendo el código.
- **Sin ningún imprescindible tildado** → mensaje de **una sola opción** (no hay MVP que ofrecer aparte) + advertencia visible.
- **Sólo imprescindibles tildados** → MVP y FULL darían la misma lista y la misma plata; mostrar 2 opciones idénticas lee a relleno, así que también sale como una sola opción, con una advertencia que dice cómo obtener las dos.

### Archivos y capas

| Capa | Archivo | Detalle |
|---|---|---|
| Domain | `Entities/ModuloCatalogo.cs`, `Entities/ModuloCatalogoIndustria.cs` **(nuevos)** | `SoftDestroyable`, mismo patrón que el resto. |
| Application | `DTOs/PropuestaMvpFullDto.cs`, `Interfaces/IPropuestaMvpFullService.cs`, `Services/PropuestaMvpFullService.cs` **(nuevos)** | Generador + DTOs. Primera carpeta `Services/` de la capa Application. |
| Application | `Helpers/RubroHelpers.cs` | **`CatalogoNombreDeRubroContacto()` nuevo** (resuelve los 3 vocabularios de `Contacto.Rubro`) + corrección de 2 entradas del mapeo, ver Riesgos. |
| Infrastructure | `Data/AppDbContext.cs` | 2 DbSet + Fluent API (Cascade/Restrict). |
| Infrastructure | `Data/SeedData.cs` | `SeedModulosCatalogoAsync` + `ModulosMatriz()` (los 84 módulos reales). |
| Infrastructure | `Data/Migrations/20260828023654_AddModuloCatalogo` | 2 tablas nuevas, 0 cambios sobre tablas existentes. |
| Infrastructure | `DependencyInjection.cs` | Registro de `IPropuestaMvpFullService`. |
| Infrastructure | `Services/BotFlowService.cs` | Cambios al cuestionario, ver abajo. |
| Web | `Controllers/ModulosController.cs` **(nuevo)** | `RequireSuperUsuario`. CRUD + 3 endpoints AJAX de asignación de rubros + `Presupuesto`/`Checklist`/`Calcular`/`GenerarMensaje`. |
| Web | `Models/ModuloCatalogoViewModels.cs` **(nuevo)** | 7 ViewModels. |
| Web | `Views/Modulos/` **(nuevas)** | `Index`, `Create`, `Edit`, `Presupuesto`, `_ChecklistPresupuesto`. |
| Web | `wwwroot/js/presupuesto-modulos.js` **(nuevo)** | Un solo JS para las 2 entradas al checklist, por delegación sobre `document` (funciona con HTML inyectado por AJAX). |
| Web | `Controllers/ChatsController.cs` + `Views/Chats/Detail.cshtml` | Wiring del botón "Sugerir", ver abajo. |
| Web | `Views/Shared/_Layout.cshtml` | Link "Módulos / Presupuesto" en la sección Sistema del sidebar. |
| — | `.gitignore` | `OlvidataCRM.Web/DataProtection-Keys/` — ver Riesgos. |

**Un solo HTML para el checklist.** `_ChecklistPresupuesto.cshtml` se renderiza desde `/Modulos/Checklist` y lo consumen tanto `/Modulos/Presupuesto` como el modal de `Chats/Detail`. No hay copia: es la misma vista y el mismo JS.

**El flag MVP/FULL y el precio se releen siempre de la base.** `Calcular`/`GenerarMensaje` reciben del navegador sólo los ids tildados; el resto lo resuelve el servidor para ese rubro, así un checkbox manipulado desde el inspector no puede meter en el MVP un módulo que en la matriz es sólo FULL. El cruce contra los ids se hace **en memoria** (MH-001: `Contains()` sobre colección local no traduce en este proveedor de MySQL).

### Wiring en `Chats/Detail` — el botón "Sugerir" pasa a tener uso real

`SugerirMensaje` devuelve además un objeto `matriz` cuando el rubro del contacto tiene módulos cargados. El botón entonces ofrece **"Propuesta MVP/FULL"** (abre el checklist del rubro, pre-tildado, en un modal) o **"Sugerencia genérica"** (el comportamiento viejo). Si no hay sugerencia genérica para la etapa **pero sí matriz**, va derecho al checklist — que es justo el caso que dejaba al botón sin ningún uso. **Si el rubro no tiene matriz, el comportamiento es exactamente el de antes**: la funcionalidad vieja no se retira, sólo pierde prioridad. El mensaje generado vuelve al `#txtRespuesta` de siempre y se manda con `EnviarMensaje` — **no hay flujo de envío paralelo**.

La resolución de `Contacto.Rubro` es el punto delicado y es la otra cara de CRM-007: esa columna tiene **3 vocabularios** (ClaveRubro con sufijo de región opcional; nombre de industria del diálogo del bot, con el que el bot **reescribe** el rubro apenas el contacto responde; y nombre de catálogo ya resuelto). Comparar sólo contra `ClaveRubro` habría dejado afuera justo a los contactos que llegaron a la demo — los únicos para los que esta pantalla sirve. `RubroHelpers.CatalogoNombreDeRubroContacto()` cubre los 3, verificado con los 20 casos de la tabla de evidencia.

### Cambios al cuestionario del bot (`BotFlowService`)

1. **"¿Cuántas personas lo van a usar?" fuera de `rent` y `rent_other`**, más la eliminación del bloque de captura de dígitos hacia `Contacto.CantidadUsuarios`. Grep previo: ese campo **no lo lee nadie** en todo el sistema (único consumidor era la cotización automática, ya retirada), así que se estaba escribiendo una columna muerta. El campo se **deja** en el modelo, sin migración.
   - **Corrección de la premisa del pedido:** el pedido decía que rent/rent_other eran "las dos únicas categorías que la tienen" y pedía verificarlo. **No es así**: `Questions["build"]` tiene la variante `"¿Cuántas personas lo van a usar más o menos?"`, que además matcheaba el mismo `Contains("personas lo van a usar")`. Se dejó **intacta** — el alcance explícito era rent/rent_other, y `build` es otra línea de producto (desarrollo a medida, sin matriz ni sistema Rent detrás) donde el tamaño del equipo sí es dato de alcance. Su respuesta se sigue guardando como `ContactoRespuesta` y aparece en el brief; lo único que cambia es que ya no se copia al campo. **Revertirlo es borrar una línea.** Queda a criterio del cliente si la regla del agente ("NO preguntar cantidad de usuarios") debe leerse como global.
2. **Pregunta 1 (dolor) para rubros con matriz**: texto libre que lista los 3-4 imprescindibles del rubro en vocabulario de cliente y cierra con "contame cuáles de estos te complican hoy (y si lo tuyo es otra cosa, contámela igual)". **Texto libre y no lista interactiva**: la lista de WhatsApp permite elegir **una sola** opción y acá hace falta que el prospecto pueda decir "estos dos" o "ninguno". No se intentó emular un multi-select que la API no tiene.
3. **La matriz tiene prioridad sobre `DolorOptionsPorRubro`.** De sus 8 rubros, **7 pasan al mecanismo nuevo** y sólo **"Vinos y bebidas"** se queda con el menú fijo (su fila de catálogo, Gastronomía, se retiró el 2026-07-17). El menú viejo queda intacto para ese caso.
4. **`MecanismoPregunta1Async` es la fuente única de esa decisión**, y la consultan los **2 lados**: `SendCurrentQuestionAsync` para decidir qué mandar y `OnAnswerAsync` para interpretar lo que vuelve. Sin esto, un prospecto de un rubro que está en `DolorOptionsPorRubro` **y** en la matriz, que conteste literalmente "1" en texto libre, quedaba guardado con el título de una opción de menú que nunca vio. Es un bug que el pedido no anticipaba.
5. **`ArmarPitchPostDolor` extendido** (ahora `...Async`, instancia): la condición de "rubro con sistema real" era `DolorOptionsPorRubro.ContainsKey`. Ahora reconoce **las 2 fuentes** (menú fijo **o** matriz cargada). Sin esto, los 7 rubros que pasaron al mecanismo nuevo —más Salud/Medicina y Contabilidad, que nunca estuvieron en `DolorOptionsPorRubro` y ahora tienen matriz— perdían la prueba social y caían al pitch genérico.

### Evidencia

- **`dotnet build -c Release --no-incremental` → 0 errores, 13 advertencias**, todas preexistentes (mismo baseline que el sprint anterior). Las vistas Razor **sí** compilan en el build de este proyecto (verificado en sprints previos y consistente acá: las 5 vistas nuevas se escribieron antes del build).
- **Migración aplicada en dev**; `dotnet ef migrations list` sin pendientes.
- **Seed verificado en `olvidatacrm_dev`** con SQL directo: 84/88/9/62 y la tabla de rangos por rubro de arriba.
- **App levantada** (`http://127.0.0.1:5313` + `https://127.0.0.1:5444`, Development), autenticada como SuperUsuario y ejercitada por HTTP real: `/Modulos`, `/Modulos/Presupuesto`, `/Modulos/Create`, `/Industrias`, `/Chats` → **200**; **0 `[ERR]`/`[FTL]`** en el log de Serilog durante toda la sesión.
- `GET /Modulos/Checklist?industriaId=2` (Retail) → **14 checkboxes**. Mismo endpoint con Farmacias → el aviso *"Todavía no hay módulos cargados para Farmacias"*, no un checklist vacío.
- `POST /Modulos/Calcular` con los 6 imprescindibles de Retail → `mvp 510-806 / full 510-806`, coincidente con el SQL independiente.
- `POST /Modulos/GenerarMensaje` con 6 MVP + 3 FULL → mensaje completo, correcto contra las 9 reglas, `Ronda entre USD 510 y USD 1.250` (piso del MVP a techo del FULL).
- **`Chats/SugerirMensaje` probado contra 8 rubros reales de dev**: `indumentaria` → Retail (14 módulos); `indumentaria-once` (**con sufijo de región**) → Retail; `consultorio` → Laboratorios (14); `estudio` → Estudios contables (10); `inmobiliaria`, `restaurant`, `farmacia` e `Inmuebles / Real estate` (rubro ya reescrito por el bot) → `matriz: null`, o sea comportamiento viejo intacto.
- **Resolver verificado con 20 entradas** cubriendo los 3 vocabularios + los casos borde (`Otro rubro` → null, string vacío → null, `Vinos y bebidas` → nombre de una fila que ya no existe → null en la consulta).

### Riesgos y supuestos

1. **Se corrigieron 2 entradas de `RubroHelpers.IndustriaACatalogoNombre`**: `"Farmacia"` y `"Contabilidad / Estudios contables"` estaban en `null` desde el origen porque esas filas de `IndustriaCatalogo` **no existían** cuando se escribió el mapeo; existen desde el 2026-07-21 y `BackfillIndustriaCatalogoIdAsync` ya usa exactamente esos 2 nombres. Sin la corrección, un contacto de `estudio` nunca encontraba su fila de catálogo pese a que **Estudios contables es uno de los 9 rubros con matriz real (10 módulos)**. **No reintroduce cotización automática**: esa función ya no existe en el bot y el único consumidor de esas entradas que quedaba (`ResolveIndustriaCatalogoAsync` → `industria?.Plan` en el brief) sólo se usa `if (PresupuestoCotizadoUsd.HasValue)`, que el bot ya nunca setea. `CotizaAutomatico` de esas 2 filas sigue en `false`.
2. **`build` conserva su pregunta de cantidad de usuarios** (ver punto 1 de los cambios al bot). Decisión documentada, reversible en una línea.
3. **Algunos nombres de módulo del seed son más técnicos de lo ideal** para leerse en un WhatsApp al cliente ("Parser de Excel propietario", "Producción mensual por centro", "Vista de resultados para confirmar o rechazar"). Vienen tal cual de la matriz relevada; **`olvidata-presupuesto-bot` puede afinarlos desde `/Modulos/Edit` sin tocar código**, que es exactamente para lo que existe el CRUD.
4. **Soft-deletear un módulo NO soft-deletea sus asignaciones a rubros.** Los 4 lugares que consultan la matriz (`ModulosDelRubroAsync`, `RubrosConMatrizAsync`, `MatrizDelRubroAsync`, `ModulosMvpDelRubroAsync`) filtran **explícitamente** por `ModuloCatalogo.DeletedAt == null`. Cualquier consulta nueva sobre `ModuloCatalogoIndustrias` tiene que replicar ese filtro o un módulo borrado vuelve a aparecer sumando plata.
5. **`.gitignore`**: correr la app en local generó `OlvidataCRM.Web/DataProtection-Keys/key-*.xml` **sin ignorar** — es material de clave del keyring de Data Protection (agregado el 2026-08-27). Se agregó la regla. Vale confirmar que ese archivo **nunca se commiteó** antes.
6. **Sin deploy y sin tocar producción**, por instrucción explícita. La migración **falta aplicar en producción** (2 `CREATE TABLE`, sin `ALTER` sobre nada existente) y el seed corre solo al arrancar la app post-deploy.
7. Los 5 rubros sin matriz quedan sin módulos hasta que haya un caso real. No inventar precios ahí es regla del dominio, no una omisión.

### Pruebas mínimas para QA

1. `/Modulos` → 84 módulos, badges verdes (MVP) / grises (solo FULL) por rubro; los 3 módulos compartidos muestran 2-3 badges.
2. `/Modulos/Presupuesto` → elegir Retail: 14 módulos, **6 pre-tildados**, rangos MVP 510-806 y FULL 991-1653 al abrir. Destildar un imprescindible y "Recalcular": el MVP baja y el FULL también.
3. Elegir **Farmacias** (o cualquiera de los 5 sin matriz) → el aviso con link a `/Modulos/Create`, **no** un checklist vacío ni un error.
4. "Generar mensaje" con 6 MVP + 3 FULL → verificar las 9 reglas una por una, en especial: FULL antes que MVP, máximo 4 ítems explícitos por opción, `Ronda entre USD {mvpMin} y USD {fullMax}`, cierre `¿Cuál te cierra más?` y **ninguna tabla**.
5. Casos degradados: destildar **todo** lo imprescindible → mensaje de una opción + advertencia. Tildar **sólo** imprescindibles → mensaje de una opción + advertencia distinta. Nada tildado → error, sin texto.
6. `/Modulos/Edit/{id}` → asignar un rubro nuevo, cambiar el switch MVP, quitar el rubro; los 3 guardan por AJAX con toast y el rubro quitado **vuelve** al combo.
7. **Manipulación:** en `/Modulos/Presupuesto`, cambiar por inspector el `value` de un checkbox a un módulo de OTRO rubro y "Recalcular" → el servidor debe **ignorarlo** (no está en la lista del rubro).
8. `Chats/Detail` de un contacto `indumentaria` → "Sugerir" ofrece las 2 opciones; "Propuesta MVP/FULL" abre el modal; "Usar en la respuesta" llena `#txtRespuesta` y cierra el modal; "Enviar" sigue funcionando igual.
9. `Chats/Detail` de un contacto `inmobiliaria`/`restaurant` → "Sugerir" se comporta **exactamente** como antes (sugerencia genérica o el aviso de "sin sugerencia").
10. **Bot (sin enviar a Meta real):** verificar que `rent`/`rent_other` quedaron en **2 preguntas**; que un rubro con matriz recibe el texto libre con los 3-4 imprescindibles; que "Vinos y bebidas" **sigue** recibiendo el menú de 3 opciones; y que el pitch con prueba social sigue apareciendo para los 7 rubros que cambiaron de mecanismo.
11. Regresión de `SeedData`: reiniciar la app 2 veces → el log **no** debe volver a decir "Matriz de módulos sembrada" (idempotencia) y los conteos deben seguir en 84/88.
