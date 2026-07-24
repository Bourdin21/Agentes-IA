# ShowroomGriffin — Metadata del Proyecto

**Fecha creación:** 2026-04-23
**Última actualización:** 2026-07-23 (reemplazado con la version as-built mas reciente del repo local del proyecto — ver nota de mergeo abajo)

> Nota de mergeo (2026-07-23): este archivo reemplaza la version anterior (dated 2026-04-23, con items "⏳ Pendiente" ya completados hace meses) por el snapshot as-built vigente al 2026-05-19, encontrado en `C:\Sistemas\ShowroomGriffin\docs\ShowroomGriffin\metadata.md` durante el barrido cross-proyecto de memorias. La seccion "Decisiones tecnicas historicas" al final preserva contexto valioso del documento anterior que no estaba en la version local.

---

## Identificación

| Campo              | Valor                                          |
|--------------------|------------------------------------------------|
| Proyecto           | ShowroomGriffin                                |
| Cliente            | Griffin Showroom                               |
| Desarrollador      | Olvidata Soft                                  |
| Repositorio        | https://gitlab.com/olvidata/ShowroomGriffin    |
| Rama principal     | `main`                                         |
| Estado actual      | En producción (v1 entregada)                   |
| Fecha relevamiento (snapshot as-built) | 2026-05-19                 |

---

## Stack tecnológico

| Componente             | Tecnología / Versión                          |
|------------------------|-----------------------------------------------|
| Framework              | ASP.NET Core MVC — .NET 10                    |
| ORM                    | Entity Framework Core 10.0.2                  |
| Base de datos          | MySQL (MySql.EntityFrameworkCore 10.0.1)      |
| Autenticación          | ASP.NET Core Identity + Cookie Auth (90 días) |
| Logging                | Serilog 9.0.0 (file + console)                |
| PDF                    | QuestPDF 2025.12.4 (Community License)        |
| Excel                  | ClosedXML 0.105.0                             |
| Email                  | MailKit 4.16.0                                |
| Frontend               | Bootstrap 5 + jQuery + olvidata-theme.css     |
| Compresión HTTP        | Brotli + Gzip (Response Compression)          |
| Hosting                | IIS InProcess (olvidatasoft hosting compartido) |

---

## Arquitectura

Solución de 4 proyectos con separación de capas estricta:

```
ShowroomGriffin.Domain          → Entidades, Enums, contratos base
ShowroomGriffin.Application     → DTOs, Interfaces, Helpers
ShowroomGriffin.Infrastructure  → EF Core, Repositorios, Servicios, Email, Export
ShowroomGriffin.Web             → Controllers, Views, Middleware, Program.cs
```

Patrón: **Repository + Service Layer + MVC**
No usa CQRS ni Mediator. La lógica de negocio reside en `Infrastructure/Services`.

---

## Módulos implementados

| Módulo                  | Controller                  | Notas                                       |
|-------------------------|------------------------------|-----------------------------------------------|
| Autenticación           | AccountController           | Login, Logout, Cambiar Password, Perfil     |
| Dashboard               | HomeController              | Resumen métricas clave                      |
| Productos               | ProductosController         | CRUD + variantes                            |
| Variantes               | VariantesController         | Talle/precio por variante                   |
| Marcas                  | MarcasController            | Maestro                                     |
| Modelos                 | ModelosController           | Maestro — entidad base del producto         |
| Categorías              | CategoriasController        | Maestro                                     |
| Proveedores             | ProveedoresController       | Maestro                                     |
| Clientes                | ClientesController          | Maestro                                     |
| Talles Config           | TallesConfigController      | Maestro tipos de talle                      |
| Tipos Precio Zapatilla  | TiposPrecioController       | Maestro precios                             |
| Compras                 | ComprasController           | Ciclo completo: crear, editar, recepcionar  |
| Ventas                  | VentasController            | Ciclo completo + pagos + adjuntos           |
| Devoluciones/Cambios    | DevolucionesController      | Postventa                                   |
| Stock                   | StockController             | Ajuste, carga inicial, historial            |
| Remitos                 | RemitosController           | Generación de remitos PDF                   |
| Resumen Semanal         | ResumenSemanalController    | Reporte exportable                          |
| Aumento Masivo          | AumentoMasivoController     | Actualización masiva de precios             |
| Notificaciones          | NotificationsController     | Sistema de notificaciones internas          |
| Usuarios                | UsersController              | ABM usuarios + roles                        |
| Auditoría               | AuditController              | Log de cambios                              |
| Sistema                 | SystemController             | Health checks, info técnica                 |

---

## Roles de usuario

| Rol           | Descripción                                      |
|---------------|----------------------------------------------------|
| SuperUsuario  | Acceso total                                     |
| Administrador | Acceso administrativo + reportes                 |
| Vendedor      | Operativa de ventas                              |
| Empleado      | Operativa diaria: ventas, cambios, stock         |

Policies: `RequireSuperUsuario`, `RequireAdministracion`, `RequireAdministrador`, `RequireVendedor`, `RequireEmpleado` (más inclusiva).

---

## Migraciones EF aplicadas

| Nro | Nombre                         | Fecha      |
|-----|--------------------------------|------------|
| M0  | InitialCreate                  | 2026-03-02 |
| M1  | AddMaestrosComerciales         | 2026-04-16 |
| M2a | AddRowVersionToVariante        | 2026-04-28 |
| M2b | FixRowVersionVariante          | 2026-04-29 |
| M2c | AddCantidadCuotasToVentaPago   | 2026-04-29 |
| V2  | ProductTaxonomyRename          | 2026-05-18 |
| V3  | ProductoModeloId               | 2026-05-18 |
| V4  | VarianteTalleConfigId          | 2026-05-18 |
| V5  | VentaAnotaciones               | 2026-05-18 |
| V6  | RemoveRedundantFields          | 2026-05-18 |
| V7  | ModeloTipoTalleYPrecio         | 2026-05-18 |

Scripts manuales de producción: `ShowroomGriffin.Web/Migrations-Scripts/` e `Infrastructure/Data/Migrations/Scripts/`. Runbook de aplicación en produccion: `docs/ShowroomGriffin/runbook-migraciones-produccion.md`.

---

## Configuración por ambiente

| Archivo                          | Uso                                         |
|-----------------------------------|-----------------------------------------------|
| `appsettings.json`               | Base (sin secretos)                         |
| `appsettings.Development.json`   | Desarrollo local                            |
| `appsettings.Production.json`    | Producción (no versionado con secretos)     |
| User Secrets                     | Dev local — ID: `aspnet-ShowroomGriffin-ee6600a9-5a4a-4942-9c8f-2bc5026de7b1` |

Claves configurables: `ConnectionStrings:DefaultConnection`, `Olvidata_Email:Smtp`, `Olvidata_ErrorEmail:Destinatarios`, `Seed:SuperUser`.

---

## Publicación

- **Perfil**: olvidatasoft-002-site10 (FTP + Web Deploy)
- **Hosting**: IIS InProcess
- **Logs**: `Logs/` relativa a `AppContext.BaseDirectory`
- **Uploads**: `wwwroot/uploads/compras/` y `wwwroot/uploads/ventas/`

---

## Decisiones tecnicas historicas (preservadas del documento anterior, 2026-04-23)

1. **MySQL en lugar de SQL Server**: hosting compartido economico. Impacto: `RowVersion` para concurrencia optimista se gestiona manualmente (MySQL no tiene rowversion auto-generado) — ver tambien `32-estandares-qa-implementador.instructions.md` (REG-001).
2. **Clean Architecture sin Repository Pattern explicito**: los servicios acceden directamente a `AppDbContext`. Justificacion: proyecto de tamaño medio, no se justifica la abstraccion adicional.
3. **Soft Delete global**: implementado via middleware `SoftDestroyMiddleware` que inyecta filtro `IsDeleted == false` en todos los queries. Permite recuperacion de datos sin borrado fisico.
4. **QuestPDF para generacion de PDFs**: licencia Community (gratuita para uso no comercial o comercial de bajo volumen). Uso: remitos, reportes de ventas/compras.

---

**Fin del documento - Metadata**
