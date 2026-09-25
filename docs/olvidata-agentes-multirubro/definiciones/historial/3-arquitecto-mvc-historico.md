<!-- Archivado de docs/olvidata-agentes-multirubro/definiciones/3-arquitecto-mvc.md el 2026-09-25 por scripts/archivar_memoria.py. Bloques cerrados: no editar aca, el estado vigente vive en el archivo de origen. -->

# 3-arquitecto-mvc - historico (1 bloques archivados)

- M18 — Portal del cliente del estudio (rol Cliente)

---

# M18 — Portal del cliente del estudio (rol Cliente)

Estado: **Arquitectura cerrada**. Entrada: análisis M18 (RF-M18-01..36) y `docs/diseno-portal-cliente.md` (D-M18-1..12).

**Escaneo de reutilización.** `cma-centro-medico/3-arquitecto-mvc.md` dejó planteado un `PortalController` con el alta
de credenciales sin resolver; nunca se implementó, así que **no hay código**: se toma su criterio (service dedicado
que fuerza el scoping en un solo lugar). Ningún otro proyecto del historial tiene un tercero autenticado adentro del
tenant. De este repo se reutilizan **sin tocar**: el pipeline de documentos de M5 (`IDocumentoCarteraService`,
lectura a partes, archivo fuera de `wwwroot`), el patrón de propuesta de M4b/M7b, `ControlGasto` de M6, el rate
limiting del portal y el `TareasHub` de M7. Patrón nuevo: **`PAT-042`**.

## 1. Mapa de componentes

```
┌─ Web ─────────────────────────────────────────────────────────────────────┐
│ AccesoClienteController (AllowAnonymous)  → ICodigosAccesoService          │
│ Portal{,Documentos,Pedidos,Consultas}Controller  [RequirePortalCliente]    │
│ PedidosController (estudio)  [RequireMiembro]                             │
│ Cartera/Details · Documentos · Configuracion · Consumo  (agregados)       │
└───────────────┬───────────────────────────────────────────────────────────┘
┌─ Application ─┴───────────────────────────────────────────────────────────┐
│ IPortalClienteService  ← ÚNICO punto de entrada del portal del cliente    │
│ IPedidosDocumentacionService · ICodigosAccesoService                      │
│ IContextoUsuario.ClienteCarteraId · IPermisosOrganizacion.EsCliente       │
└───────────────┬───────────────────────────────────────────────────────────┘
┌─ Infrastructure ┴─────────────────────────────────────────────────────────┐
│ AppDbContext.FiltroCliente + AplicarReglasCliente (escritura)             │
│ ResolvedorSesion (resuelve ClienteCarteraId)                             │
│ ProcesadorTareas + ResolvedorHerramientas (tarea acotada, escalado)      │
│ HerramientasPedidoDocumentacion (proponer, nunca crear)                  │
└───────────────────────────────────────────────────────────────────────────┘
```

## 2. Desglose por capa

**Domain.** `RolOrganizacion.Cliente = 3`. `ApplicationUser.ClienteCarteraId (int?)` + navegación. Dos marcadores,
porque las dos formas existen en el modelo: `IClienteOwned { int ClienteCarteraId }` (DocumentoCartera, Pedido, Item)
e `IClienteOwnedOpcional { int? ClienteCarteraId }` (`TareaAgente`, que ya tiene la columna nullable). Entidades
nuevas: `CodigoAccesoCliente`, `PedidoDocumentacion`, `ItemPedidoDocumentacion`, `PropuestaPedidoDocumentacion`.
Agregados: `DocumentoCartera.VisibleParaCliente (bool)` y `.Origen (OrigenDocumento)`; `Tenant.PortalClientesHabilitado`,
`.TopeUsuariosPorCliente`, `.LimiteGastoClientePorDefecto`; `TipoTarea.ConsultaCliente = 5`.

**Application.** `IPortalClienteService` — todas las firmas **sin** `clienteCarteraId` en los parámetros: lo resuelve
del contexto. `ObtenerInicioAsync(ct)`, `ListarMisDocumentosAsync(filtros, ct)`, `SubirAsync(dto, ct)`,
`RenombrarAsync(id, nombre, ct)`, `DarDeBajaAsync(id, ct)`, `DescargarAsync(id, ct)`, `ListarPedidosAsync(ct)`,
`ResponderItemAsync(itemId, archivo, ct)`, `ListarMisConsultasAsync(ct)`, `CrearConsultaAsync(dto, ct)`,
`ObtenerMiFichaAsync(ct)`, `ActualizarContactoAsync(dto, ct)`. **Que ningún método reciba el id del cliente es la
garantía, no una comodidad.**
`ICodigosAccesoService`: `GenerarAsync(clienteCarteraId, ct)` → código en claro una sola vez;
`RegistrarConCodigoAsync(dto, ct)`; `RevocarAccesoAsync(usuarioId, ct)`.
`IPedidosDocumentacionService` (estudio): CRUD, `RevisarItemAsync(itemId, decision, motivo, ct)`,
`AplicarPropuestaAsync(propuestaId, ct)`.

**Infrastructure.** `AppDbContext`: `ClienteCarteraIdActual` (null salvo rol Cliente), `FiltroCliente` aplicado por
reflexión junto a los otros dos, y `AplicarReglasCliente()` en `SaveChanges` — **una escritura de un cliente sobre
otro cliente tira excepción**, igual que hoy con el tenant. `ResolvedorSesion`: trae `ClienteCarteraId` y verifica
que el `ClienteCartera` esté vigente; si no, bloquea (cascada de la baja lógica, RF-M18-07).

**Motor.** `ResolvedorHerramientas`: para `TipoTarea.ConsultaCliente` devuelve una lista blanca fija (lectura de la
carpeta + `pedido_documentacion_proponer`), **construida por inclusión, nunca filtrando la lista completa**.
`AprobacionService`: si la tarea es `ConsultaCliente`, el nivel efectivo es `Director` cualquiera sea el declarado.

**Web.** Policy `RequirePortalCliente` con un `PermisoOrganizacionRequirement.Cliente` nuevo. Los usuarios cliente
llevan el rol Identity `UsuarioCliente` que ya existe (no abre nada de staff: `RequireAdministracion` y
`RequireSuperUsuario` van por otros roles).

## 3. Cambios de datos y migración

Migración **`PortalCliente`**:
- `AspNetUsers`: `+ClienteCarteraId int NULL`, FK a `ClientesCartera` con `ON DELETE RESTRICT`, índice
  `(TenantId, ClienteCarteraId)`; **check constraint** `CK_Usuario_Cliente`: `RolOrganizacion = 3 ⟺ ClienteCarteraId IS NOT NULL`.
- `DocumentosCartera`: `+VisibleParaCliente bit NOT NULL DEFAULT 0`, `+Origen int NOT NULL DEFAULT 1` (Estudio).
  **Backfill explícito**: todo lo existente queda Estudio y no visible — el default hace el trabajo, pero se escribe
  en la migración para que se lea.
- `Tenants`: `+PortalClientesHabilitado bit NOT NULL DEFAULT 0`, `+TopeUsuariosPorCliente int NOT NULL DEFAULT 3`,
  `+LimiteGastoClientePorDefecto decimal(10,2) NULL`.
- Tablas nuevas: `CodigosAccesoCliente` (hash del código, `VenceAt`, `UsadoAt`, `UsadoPorUsuarioId`, `RevocadoAt`,
  índice único sobre el hash), `PedidosDocumentacion`, `ItemsPedidoDocumentacion` (FK al `DocumentoCartera` que lo
  respondió, nullable), `PropuestasPedidoDocumentacion`. Todas `ITenantOwned`; las tres primeras también `IClienteOwned`.
- `AgentesHabilitadosCliente` (TenantId, AgenteOrganizacionId) — qué puede consultar un cliente. Vacía por defecto.

Sin cambios en índices existentes. El `FiltroCliente` agrega una condición sobre columnas ya indexadas.

## 4. Riesgos técnicos

- **AR-M18-1 (alto, ya medido).** El grep de `RolOrganizacion` encontró **dos fugas reales** que hay que arreglar en
  la misma etapa que el rol: `MiembroService` (listado y `Nombre(rol)`) devolvería clientes como miembros, y
  **`HerramientasAsistente:143`** los listaría como «Empleado» **haciéndolos asignables de trabajo por el asistente
  del Director**. Ambas consultas tienen que excluir `RolOrganizacion.Cliente` explícitamente.
- **AR-M18-2 (alto).** `FiltroCliente` sobre `TareaAgente` es el único que toca una tabla caliente. Si
  `ClienteCarteraIdActual` se resolviera distinto de null para un miembro, el estudio dejaría de ver sus tareas: test
  explícito de que es null para Director, Empleado, staff y procesos de sistema.
- **AR-M18-3 (medio).** La caché de 60 s de `ResolvedorSesion` retrasa el corte de acceso. Se invalida igual que hoy
  al bloquear un miembro; hay que acordarse de invalidarla también al dar de baja el `ClienteCartera`.
- **AR-M18-4 (medio).** `TipoTarea.ConsultaCliente` no puede mover el hash de contexto de las tareas del estudio:
  los 5 goldens tienen que quedar **idénticos**.
- **AR-M18-5 (bajo).** El check constraint obliga a ordenar el alta (crear usuario y setear las dos columnas en el
  mismo `SaveChanges`).

## 5. Estrategia de pruebas

**Aislamiento (la batería que justifica el módulo).** Un test parametrizado que recorre **todos** los controllers del
portal del estudio con una sesión de cliente y exige 403/404 — falla solo si alguien agrega un controller y lo abre
sin querer. Más: cliente contra cliente (documento, pedido, ítem, tarea, por Id directo → 404), escritura cruzada
(excepción en `SaveChanges`), `ClienteCarteraIdActual` null para los cuatro perfiles que no son cliente.

**Motor.** La solicitud de una `ConsultaCliente` no contiene ninguna herramienta de conector ni de escritura;
la aprobación escala a Director aunque el autor sea el cliente; con el límite alcanzado no sale ninguna llamada;
los 5 goldens de hash, idénticos.

**Alta.** Código usado, vencido, revocado e inexistente → mismo mensaje; tope de intentos; tope de usuarios por
cliente; email distinto al de la ficha → entra y notifica.

**Visibilidad.** Documento sin `VisibleParaCliente` no aparece ni por Id; lo que sube el cliente lo ve siempre;
apagar oculta en el acto.

**Pedidos.** La propuesta del agente no crea nada; aplicar dos veces la misma propuesta falla; rechazar sin motivo
falla.

**Manual (QA).** Los dos temas a 390 px, el estado vacío del portal, y la prueba de que un cliente logueado que pega
una URL del estudio en la barra no ve ni el menú.

## 6. Etapas de implementación (commit local por etapa)

| # | Etapa | Qué cierra |
|---|---|---|
| **E1** | **La frontera** | Rol, `ClienteCarteraId`, `EsCliente`/`EsMiembro`, policy, `FiltroCliente`, `AplicarReglasCliente`, arreglo de las dos fugas de AR-M18-1, migración. **Sin una sola pantalla** y con la batería de aislamiento verde |
| **E2** | **Entrar** | Habilitación por organización, código de acceso, registro anónimo, `_LayoutCliente`, Inicio y Mi ficha |
| **E3** | **Documentos** | `VisibleParaCliente` y `Origen`, subida del cliente, interruptor y badge del lado del estudio |
| **E4** | **Pedidos** | Pedidos e ítems, revisión con motivo, herramienta de propuesta y tarjeta para aplicarla |
| **E5** | **Consultas** | Agentes habilitados, `TipoTarea.ConsultaCliente`, herramientas acotadas, escalado de aprobación, consumo por cliente |

E1 es la etapa que no se puede apurar: si sale mal, todo lo demás está construido sobre una frontera rota.
