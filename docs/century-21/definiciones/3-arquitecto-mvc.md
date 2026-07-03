# Memoria - Arquitecto MVC

## Proyecto: century-21
## Ultima actualizacion: 2026-07-02

## Definiciones vigentes

### 1. Alcance funcional resumido
Arquitectura técnica sobre el Diseño (etapa 2) vigente: plataforma SaaS multi-agencia con aislamiento de datos por `GrupoId` (revisado — antes era `AgenciaId`), CRM + Chatbot WhatsApp, agregador de portales con cache global, y catálogo propio con CRUD por grupo. Baseline: ASP.NET Core MVC .NET 10, EF Core 10, MySQL, Identity, Serilog (sin cambios de framework).

**Cambio de modelo de roles (2026-07-02):** el sistema pasa de 3 roles (SuperAdmin/Gerente/Asesor) a **2 roles** (SuperAdmin/Asesor). El plan se contrata por Grupo, no por Agencia. Esto mueve `PlanId` y la configuración de WhatsApp de `Agencia` a `Grupo`, y cambia el filtro de tenant principal de `AgenciaId` a `GrupoId`.

### 2. Entidades de dominio

**Nuevas / revisadas**
| Entidad | Campos clave | Notas |
|---|---|---|
| `Agencia` | Nombre, RazonSocial | Hereda `SoftDestroyable`. Contenedor liviano de Grupos — **ya no tiene** `PlanId`, `Estado` propio ni datos de WhatsApp (se movieron a `Grupo`). |
| `Plan` | Nombre, LimiteAsesores | Catálogo fijo (3 filas seed: Básico/Pro/Enterprise), sin alta/baja desde UI en Fase 1. |
| `Grupo` | Nombre, AgenciaId (FK), **PlanId (FK, nuevo acá)**, **Estado (enum EstadoGrupo, nuevo acá)**, **WhatsAppNumero, WhatsAppTokenCifrado (nuevo acá)** | Hereda `SoftDestroyable`. Es ahora la **unidad de facturación y de aislamiento de datos** — reemplaza a `Agencia` en ese rol. |
| `PropiedadPropia` | Titulo, TipoOperacion (enum), Precio, Moneda, Zona, Ambientes, Superficie, Descripcion, **GrupoId (FK, antes AgenciaId)** | Hereda `SoftDestroyable`. |
| `PropiedadFoto` | PropiedadPropiaId (FK), RutaArchivo, Orden | Hereda `SoftDestroyable`. Sin cambios. |

**Modificadas (agregan `GrupoId` en vez de `AgenciaId`)**
| Entidad | Cambio |
|---|---|
| `ApplicationUser` | Agrega **`GrupoId`** (nullable — null solo para `SuperAdmin`). Se **elimina** `AgenciaId` directo en el usuario (se deriva via `Grupo.AgenciaId` si hace falta para reportes de SuperAdmin) y se **elimina** el rol `Gerente`. |
| `Cliente` | Agrega `GrupoId` (requerido, antes `AgenciaId`). `Telefono` único por `(GrupoId, Telefono)`. |
| `Consulta` | Agrega `GrupoId`, `CategoriaConsulta` (enum), `Estado` (enum `EstadoConsulta`), `AsesorId` (FK a ApplicationUser, nullable — se completa por self-assign). **Agrega `RowVersion` (concurrencia optimista)** para evitar que dos asesores tomen la misma consulta libre al mismo tiempo. |

**Sin cambio de tenancy (global, ya definidas en Análisis)**
- `PropiedadesCache`: sin `GrupoId`/`AgenciaId` — cache de portales compartido entre toda la plataforma.

### 3. Enums (Domain/Enums)
- `EstadoGrupo`: Activo = 1, Suspendido = 2. *(reemplaza a `EstadoAgencia` — Agencia ya no tiene ciclo de vida propio)*
- `EstadoConsulta`: Nueva = 1, Categorizada = 2, Asignada = 3, EnGestion = 4, Cerrada = 5.
- `CategoriaConsulta`: Comprador = 1, Alquiler = 2, Vendedor = 3, Valuacion = 4.
- `TipoOperacion`: Venta = 1, Alquiler = 2.
- Persistencia via `HasConversion<int>()`.

### 4. Impacto técnico por capa

**Domain**
- 5 entidades (Agencia simplificada, Plan, Grupo ampliado, PropiedadPropia, PropiedadFoto) + 4 enums.
- `ApplicationUser` extendido con `GrupoId` únicamente (ya no `AgenciaId`).
- `Consulta` agrega `RowVersion` (`byte[]`, `IsRowVersion()` en Fluent API) para concurrencia optimista del self-assign.

**Application**
- Interfaces: `IAgenciaService`, `IGrupoService` (ahora incluye gestión de plan/WhatsApp del grupo), `IPropiedadPropiaService`, `ITenantContext` (resuelve `GrupoId` y `EsSuperAdmin` del usuario autenticado — **ya no resuelve `AgenciaId`** como filtro operativo).
- DTOs: `GrupoMetricasDto` (para SA-04 y A-02 perfil de grupo), `PerfilAsesorDto` (para A-01), `PropiedadPropiaDto`.
- Se elimina cualquier interfaz/lógica que dependiera de un rol `Gerente` (ej. validaciones "solo Gerente puede reasignar").

**Infrastructure**
- `AppDbContext`: el `HasQueryFilter` global de tenant pasa de `AgenciaId` a **`GrupoId`** en `Cliente`, `Consulta`, `PropiedadPropia`, `PropiedadFoto`, resuelto desde `ITenantContext`. `Grupo` en sí se filtra por pertenencia a la Agencia solo en las pantallas de SuperAdmin (`IgnoreQueryFilters()`).
- **Self-assign concurrente:** el service de Consulta usa `RowVersion` (EF Core concurrency token) al ejecutar "Tomar" — si dos asesores intentan tomar la misma consulta libre, el segundo recibe `DbUpdateConcurrencyException`, se traduce a error funcional "Esta consulta ya fue tomada por un compañero" y refresca la bandeja.
- Consultas de `SuperAdmin` (SA-01 a SA-07) usan `IgnoreQueryFilters()` explícito, único punto autorizado de bypass del filtro.
- `WhatsAppCredentialCipherService`: ahora cifra credenciales **por Grupo**, no por Agencia.
- `ScrapingOrchestratorService` sin cambios (global). `AlertasFechasJob` ahora itera **grupos activos** (antes agencias) y usa las credenciales WhatsApp de cada grupo.
- Almacenamiento de fotos de `PropiedadPropia`: `wwwroot/uploads/{GrupoId}/{PropiedadId}/` (antes `{AgenciaId}`).
- Seed data: roles `SuperAdmin` y `Asesor` únicamente (se elimina el seed de `Gerente`), 3 filas fijas de `Plan`.

**Web**
- **2 áreas de navegación por rol** (SuperAdmin / Asesor, antes 3) con layouts diferenciados.
- Controllers nuevos: `AgenciaController`, `GrupoController` (SuperAdmin, ahora incluye asignación de plan y config. WhatsApp), `AsesorController` (SuperAdmin), `PerfilController` (Asesor — mi perfil + perfil de grupo), `PropiedadPropiaController`, `BusquedaController`.
- Se elimina cualquier autorización condicionada al rol `Gerente` en `ConsultaController`/`ClienteController` — pasan a autorizar solo por pertenencia a `GrupoId` (cualquier asesor del grupo).

### 5. Modelo de permisos (roles/claims/policies)
| Rol | Policy | Alcance |
|---|---|---|
| `SuperAdmin` | `RequireSuperAdmin` | Plataforma completa: Agencias, Grupos, Asesores, Planes, WhatsApp — uso interno del proveedor, no se documenta al cliente final. |
| `Asesor` | Autenticado + filtro de `GrupoId` a nivel de datos | Único rol de negocio. Todos los asesores de un mismo grupo tienen **los mismos permisos entre sí** — no hay jerarquía intermedia. |

- Se **elimina** la policy `RequireGerencia` y el rol `Gerente` completo.
- Verificación de pertenencia a grupo en escrituras (Update/Delete/Reasignar): cada service valida explícitamente que el `GrupoId` del recurso coincide con `ITenantContext.GrupoId` antes de persistir — defensa en profundidad contra IDOR.
- Claims agregados al login: `GrupoId` (si aplica) + `Role` (Identity).

### 6. Migraciones EF requeridas
**Sí, requerida.** Detalle (revisado respecto a la versión anterior):
1. `AddAgenciaPlanGrupo` — crea `Agencias` (liviana), `Planes`, `Grupos` (con `PlanId`, `Estado`, `WhatsAppNumero`, `WhatsAppTokenCifrado`) + seed de 3 planes.
2. `AddPropiedadPropiaYFotos` — crea `PropiedadesPropias` (con `GrupoId`) y `PropiedadFotos`.
3. `AddTenancyToUsuarioClienteConsulta` — agrega `GrupoId` a `AspNetUsers`, `Clientes`, `Consultas`; agrega `CategoriaConsulta`/`Estado`/`AsesorId` (nullable) a `Consultas`; agrega `RowVersion` a `Consultas`; agrega índice único compuesto `(GrupoId, Telefono)` en `Clientes`.
4. `SeedRolesSuperAdminAsesor` — seed de 2 roles únicamente (se quita `Gerente` del seed original de 3 roles).

**Nota:** si el proyecto ya tenía una migración previa con `AgenciaId` en estas tablas (iteración anterior de Arquitectura, antes del cambio de roles), corresponde consolidarla antes de aplicar en un entorno con datos — no hay datos reales todavía (proyecto sin Implementación iniciada), así que se puede resolver como una sola migración limpia sin necesidad de migración de datos.

### 7. Riesgos y supuestos técnicos

**7.1 — Conexiones a MySQL en hosting compartido (SmarterASP.NET, plan Premium) — CONFIRMADO 2026-07-02 por el cliente:** límite real de **10 conexiones simultáneas por usuario MySQL**, con **disponibilidad de crear hasta 5 usuarios MySQL** (techo teórico: 50 conexiones repartidas en 5 pools independientes). Decisión de arquitectura (sin cambios por el rediseño de roles):
   - **Usuario MySQL #1 — Web (OLTP):** `Maximum Pool Size=8`.
   - **Usuario MySQL #2 — Hangfire (jobs):** aislado del tráfico web en vivo.
   - **Usuario MySQL #3 — Staging/QA.**
   - **Usuarios MySQL #4 y #5 — reserva** (pool de métricas de SuperAdmin, o balanceo futuro).
   - Aclaración: el límite de 10 conexiones no equivale a 10 usuarios/IPs concurrentes — EF Core toma la conexión solo durante la query (10-50ms), no durante toda la sesión.
   - Checkpoint técnico en ~15-20 agencias/grupos pagos activos para evaluar upgrade de hosting.

**7.2 — Riesgos derivados del cambio de modelo de roles:**
1. **Concurrencia en self-assign:** dos asesores del mismo grupo pueden intentar tomar la misma consulta libre al mismo instante. Mitigado con `RowVersion` (concurrencia optimista) — ver sección 4/Infrastructure. Costo técnico adicional menor (una columna + manejo de excepción), no requiere locking pesimista.
2. **Sin control jerárquico intermedio:** cualquier asesor puede reasignar el trabajo de un compañero sin aprobación de nadie más que un `SuperAdmin` (que no opera el día a día). Es una decisión de negocio ya confirmada por el cliente, no un defecto de arquitectura — se documenta como comportamiento esperado.
3. **Gestión compartida de catálogo/clientes sin dueño único:** el modelo de datos no distingue "quién cargó" una propiedad o un cliente más allá de auditoría estándar (`AuditLog`) — cualquier asesor del grupo puede editar cualquier registro del grupo. Si el cliente pidiera más adelante restringir edición al creador original, es un cambio de reglas de negocio (gatillo de reestimación), no de arquitectura de datos (el dato de "creador" ya existe vía auditoría).
4. **Límite de 20 bases de datos del plan Premium** sigue confirmando que el modelo de tenant compartido (una sola BD, ahora filtrada por `GrupoId`) es la decisión correcta.
5. Cifrado de credenciales WhatsApp ahora por grupo — mismo patrón de secreto que antes (clave en configuración del servidor, no en BD ni en código), solo cambia el nivel de scoping.
6. Ruteo de Consulta a Grupo: con el cambio, el webhook resuelve el `GrupoId` **directamente** por el número de WhatsApp de destino (cada grupo tiene su propio número) — esto simplifica lo que en la iteración anterior era una decisión pendiente de Diseño ("ruteo automático vs. manual"), porque ahora no hay ambigüedad: 1 número de WhatsApp = 1 grupo.

### 8. Gate de aprobación para pasar a presupuesto
- Diseño (etapa 2) actualizado con el cambio de modelo de roles y cerrado nuevamente.
- Arquitectura (etapa 3) actualizada y cerrada con esta definición.
- Pendientes no bloqueantes para Presupuesto: gestión compartida de catálogo/clientes sin dueño único (hipótesis de Diseño), alerta de consulta sin tomar (fuera de alcance, mejora futura).
- **Aprobado para pasar a Presupuesto (etapa 4) — requiere reestimación de los módulos afectados por el cambio de roles (gatillo de reestimación: cambio de reglas de negocio y permisos).**

## Historial de ajustes
- 2026-06-25: Archivo creado en bootstrap del proyecto.
- 2026-07-02: Arquitectura completa sobre el pivot SaaS multi-agencia. 5 entidades nuevas, 4 enums, 4 migraciones EF planificadas, modelo de permisos de 3 roles con query filter global por AgenciaId, riesgos de hosting documentados. Gate abierto hacia Presupuesto.
- 2026-07-02 (limite de conexiones confirmado): usuario confirmo limite real de hosting (10 conexiones/usuario MySQL, 5 usuarios disponibles). Se agrego decision de arquitectura de pools segregados (Web/Hangfire/Staging/2 reserva).
- 2026-07-02 (cambio de modelo de roles): se elimina el rol Gerente. Ahora 2 roles (SuperAdmin/Asesor). Plan y configuracion de WhatsApp se mueven de Agencia a Grupo. Filtro de tenant principal pasa de AgenciaId a GrupoId. Se agrega RowVersion a Consulta para concurrencia optimista en self-assign. Webhook de WhatsApp resuelve GrupoId directamente. Reestimacion pendiente en Presupuesto.
