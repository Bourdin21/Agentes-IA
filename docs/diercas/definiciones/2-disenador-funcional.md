# Memoria - Disenador funcional

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-07-30

## Definiciones vigentes

### Historias de usuario

- Como visitante, quiero navegar el sitio y reconocer la identidad de marca de Diercas de forma consistente en todas las páginas.
- Como visitante, quiero completar el formulario de contacto y recibir confirmación de que mi consulta se envió.
- Como visitante, quiero ver los trabajos realizados por Diercas (listado + detalle con fotos) para evaluar su experiencia.
- Como Joaquín (mantenedor del sitio), quiero agregar un trabajo nuevo al portfolio editando solo un archivo de contenido, sin tocar código de página.

### Flujos de pantalla acordados

**1. Navegación institucional** — Layout común (header con navegación + logo, footer) aplicado a todas las páginas, siguiendo el patrón técnico de `labipac-front` (`src/layouts/Layout.astro`) pero con el sistema visual (colores/tipografía/logo) de Diercas en vez del de IPAC.

**2. Formulario de contacto** — mismo patrón que `labipac-front/src/pages/contacto.astro`: formulario con validación HTML5, envío vía `fetch` a un endpoint PHP (`/api/contact.php`), estado de éxito/error inline, sin recarga de página.

**3. Blog / portfolio de trabajos realizados (nuevo)**
- **Listado** (`/trabajos` o similar): grid de tarjetas, una por trabajo, con foto de portada + título + fecha.
- **Detalle** (`/trabajos/[slug]`): descripción completa + galería de fotos del trabajo.
- Contenido modelado como Astro Content Collection: cada trabajo es un archivo markdown con front-matter (`titulo`, `descripcion`, `fecha`, `fotos: []`) — agregar un trabajo nuevo es agregar un archivo, sin tocar código de las páginas de listado/detalle (ya genéricas).

*Hipótesis a validar: la cantidad de páginas institucionales (Inicio/Nosotros/Servicios/Contacto + adicionales) depende del rubro real de Diercas, no confirmado todavía — ver dependencia en `1-analista-funcional.md`.*

### ViewModels definidos
No aplica en sentido estricto (sitio estático sin backend de negocio) — el "modelo" relevante es el esquema de front-matter de la Content Collection de trabajos (`titulo: string`, `descripcion: string`, `fecha: date`, `fotos: string[]`).

### Validaciones de UI acordadas
- Formulario de contacto: campos requeridos (nombre, apellido, email, motivo, mensaje) validados en el cliente antes de enviar — mismo patrón que `labipac-front`.

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprensión inmediata del flujo
- ubicar primero información y acciones críticas; dejar secundario en segundo plano
- mantener jerarquía consistente (título, contexto, contenido, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribución en todas las páginas del sitio
- **Con la salvedad de que acá el sistema visual (paleta/tipografía/logo) lo define el branding de Diercas, no un criterio de diseño libre del estudio — la jerarquía y disposición siguen el criterio del estudio, los estilos visuales siguen el branding del cliente.**

### Contratos funcionales para Services
No aplica (sin backend de negocio) — el único "servicio" es el endpoint PHP de envío de contacto, reutilizado sin cambios de contrato respecto de `labipac-front`.

## Historial de ajustes
- 2026-07-30: Diseño v1 — estructura de navegación, formulario de contacto y blog/portfolio definidos por analogía directa con `labipac-front`. Queda pendiente confirmar el conteo real de páginas institucionales según el rubro de Diercas.
