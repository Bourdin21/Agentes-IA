# Memoria Implementador — KoiDumplings
# Última actualización: 2026-06-29 17:57

## Módulos implementados

### Etapa 7 — ABM Inversores (sesión actual)
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
