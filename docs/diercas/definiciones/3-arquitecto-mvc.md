# Memoria - Arquitecto MVC

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-07-30

## Definiciones vigentes

### Componentes por capa

Proyecto sin capas de negocio/datos en sentido MVC — es un sitio estático generado con Astro:
- **Presentación**: Astro + Tailwind CSS (mismo stack que `labipac-front`), `Layout.astro` compartido + 6 páginas institucionales (Inicio, Nosotros, Servicios con 3 tablas técnicas, Sectores/Verticales, Clientes/Nodos de confianza, Contacto) + Content Collection de trabajos realizados (listado + detalle).
- **"Negocio"**: ninguno — sitio 100% estático en build time, sin lógica de servidor propia salvo el endpoint de contacto.
- **"Datos"**: sin base de datos. El contenido del blog/portfolio vive como archivos markdown versionados en el propio repositorio (Content Collection de Astro), no en una BD.
- **Integración externa**: endpoint PHP de envío de mail (`/api/contact.php`), reutilizado tal cual del patrón ya construido para `labipac-front` — requiere hosting con soporte PHP (DonWeb, no SmarterASP, que es el hosting .NET del resto de la flota).

### Entidades y configuraciones EF
No aplica — sin base de datos.

### Migraciones requeridas
No aplica — sin base de datos. El "contenido" se versiona como archivos markdown en el repositorio Git.

### Riesgos tecnicos activos

- **Fidelidad de marca — riesgo reducido (2026-07-30)**: ya existe brandbook real (logo, paleta, tipografía, aplicaciones de marca). Riesgo residual: solo se tiene el PDF de referencia, no archivos fuente editables (logo vectorial AI/EPS/SVG, fuente tipográfica exacta) — puede requerir recrear el logo por trazado si no se consiguen los originales.
- **Hosting a confirmar**: si el destino final no soporta PHP (ej. si se aloja en un hosting puramente estático), el endpoint de contacto necesita un enfoque distinto (ej. un servicio de formularios de terceros, o una function serverless) — no asumir DonWeb/PHP hasta confirmarlo.
- **Autorización de marcas de terceros**: la sección "Nodos de confianza" lista clientes reales (ministerios, hotel, club) — confirmar con Diercas si están autorizados a mostrarse como logo o solo como mención de texto.

### Mapa de reutilización cross-proyecto

| Componente / patrón | Proyecto origen | Qué se reutiliza |
|---|---|---|
| Stack Astro + Tailwind + Layout compartido | `labipac-front` | Base técnica completa reutilizada, solo cambia el sistema visual (branding de Diercas) |
| Estructura de secciones de página (hero, cards, grid de servicios) | `labipac-front` | Patrón de maquetación reutilizado, restyleado según branding de Diercas |
| Formulario de contacto + endpoint `contact.php` | `labipac-front` | Reutilizado directo, solo cambia el destinatario/campos si aplica |
| Content Collection de trabajos realizados (listado + detalle) | Sin precedente exacto en el estudio | Desarrollo nuevo — primer uso de Astro Content Collections como blog/portfolio en el estudio |

## Historial de ajustes
- 2026-07-30: Arquitectura v1 — stack 100% reutilizado de `labipac-front` (Astro + Tailwind + Layout + contacto PHP), única pieza nueva es la Content Collection de trabajos realizados. Sin base de datos ni capas de negocio — proyecto fuera del patrón MVC habitual del estudio.
- 2026-07-30 (v2): confirmada la estructura real de 6 páginas institucionales (antes era una analogía genérica de 4-5) tras recibir el dossier corporativo real de Diercas. Nueva sección "Clientes/Nodos de confianza" con riesgo de autorización de marca de terceros. Riesgo de fidelidad de marca bajó (hay brandbook real), pero persiste la necesidad de archivos fuente editables del logo.
