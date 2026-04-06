---
description: Reglas de frontend y design system Olvidata para vistas MVC.
applyTo: "**/Web/**/*.{cshtml,css,js}"
---

# Librerias UI
- Bootstrap 5 (override en olvidata-theme.css)
- Font Awesome 6.5.1
- jQuery local
- SweetAlert2
- DataTables 1.13.8 + Bootstrap 5 theme
- Select2 + Bootstrap 5 theme
- DateRangePicker + Moment.js

# Tokens visuales clave
- Primary: #2b9de4
- Primary hover: #1f8ad0
- Background: #f0f4f8
- Sidebar gradient: #0c1222 -> #0f172a

# Convenciones
- Prefijo CSS: ov-
- BEM-like: ov-sidebar-link, ov-topbar-avatar, ov-brand-icon-img
- Tablas siempre dentro de div.table-responsive

# Archivos CSS
- olvidata-theme.css: tokens, layout, componentes, overrides.
- site.css: ajustes especificos del proyecto.
