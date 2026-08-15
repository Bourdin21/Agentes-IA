# Memoria - Arquitecto MVC

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-07-30

## Definiciones vigentes

### Componentes por capa

Proyecto sin capas de negocio/datos en sentido MVC — es un sitio estático generado con Astro:
- **Presentación**: Astro + Tailwind CSS (mismo stack que `labipac-front`), `Layout.astro` compartido + 7 páginas/secciones institucionales confirmadas con contenido real (Inicio, Nosotros/Sectores, Servicios con 3 ramas — Infraestructura/Provisión de equipos/Eventos, Clientes agrupados por rubro, Certificaciones/Confianza, Contacto) + Content Collection de Clientes (nueva) + Content Collection de Trabajos realizados (Etapa 2, sin contenido todavía).
- **"Negocio"**: ninguno — sitio 100% estático en build time, sin lógica de servidor propia salvo el endpoint de contacto.
- **"Datos"**: sin base de datos. El contenido de Clientes y (en Etapa 2) Trabajos vive como archivos versionados en el propio repositorio (Content Collections de Astro), no en una BD.
- **Integración externa**: endpoint PHP de envío de mail (`/api/contact.php`), reutilizado tal cual del patrón ya construido para `labipac-front` — remitente `no-reply@olvidata.com.ar`, destinatario `administracion@diercas.com.ar` (confirmado 2026-08-13). **Hosting confirmado: DonWeb** (ya no es un supuesto — soporta PHP, mismo tipo de plan que aloja `labipac-front`).

### Entidades y configuraciones EF
No aplica — sin base de datos.

### Migraciones requeridas
No aplica — sin base de datos. El "contenido" se versiona como archivos markdown en el repositorio Git.

### Riesgos tecnicos activos

- **Fidelidad de marca — riesgo activo, no resuelto**: el cliente confirmó (2026-08-13) que el logo vectorial llega en una **segunda etapa** — el desarrollo arranca solo con el PDF de referencia del brandbook. Riesgo operativo real: si el sitio se completa antes de tener el vector, o se recrea el logo por trazado como solución temporal (con riesgo de fidelidad), o se deja un placeholder y se reemplaza después del deploy inicial — a definir con Joaquín cuál de las dos antes de arrancar el maquetado del header/logo.
- **QR Data Fiscal — dependencia del cliente, no generable por el estudio**: Diercas debe generar el QR desde su propio portal de ARCA (Formulario 960/D) y proveerlo como imagen — mismo tipo de dependencia que el logo vectorial, bloqueante solo para esa sección puntual, no para el resto del sitio.
- **Hosting — resuelto**: DonWeb confirmado, soporta PHP (ver arriba).
- **Autorización de marcas de terceros — reducido pero no cerrado**: la sección de Clientes ahora incluye instituciones de mayor peso (Presidencia de la Nación) — mismo criterio ya documentado (es responsabilidad de Diercas contar con la autorización), pero vale la pena que Joaquín confirme explícitamente que el cliente ya gestionó esas autorizaciones antes de publicar logos de organismos nacionales, dado el perfil institucional más alto que el resto del listado.
- **Servicios — bloqueo de maquetado, no de arquitectura**: la página `/servicios` no se termina de maquetar hasta que Joaquín confirme si Ciberseguridad/Audio-Video se agregan como bloques 4/5 (ver `1-analista-funcional.md` y `2-disenador-funcional.md`) — el layout ya está pensado para soportarlo sin rediseño si la respuesta es sí, así que no bloquea el arranque de las otras páginas.

### Mapa de reutilización cross-proyecto

| Componente / patrón | Proyecto origen | Qué se reutiliza |
|---|---|---|
| Stack Astro + Tailwind + Layout compartido | `labipac-front` | Base técnica completa reutilizada, solo cambia el sistema visual (branding de Diercas) |
| Estructura de secciones de página (hero, cards, grid de servicios) | `labipac-front` | Patrón de maquetación reutilizado, restyleado según branding de Diercas |
| Formulario de contacto + endpoint `contact.php` | `labipac-front` | Reutilizado directo, solo cambia el destinatario/campos si aplica |
| Content Collection de trabajos realizados (listado + detalle) | Sin precedente exacto en el estudio | Desarrollo nuevo (Etapa 2) — primer uso de Astro Content Collections como blog/portfolio en el estudio |
| Content Collection de Clientes agrupados por rubro (nuevo 2026-08-13) | Mismo patrón técnico que la Collection de Trabajos, aplicado a un dominio distinto | Reutiliza el criterio "contenido versionado, no hardcodeado" ya definido en v1 para Trabajos — no es una pieza nueva de arquitectura, es el mismo patrón aplicado de nuevo |

## Historial de ajustes
- 2026-07-30: Arquitectura v1 — stack 100% reutilizado de `labipac-front` (Astro + Tailwind + Layout + contacto PHP), única pieza nueva es la Content Collection de trabajos realizados. Sin base de datos ni capas de negocio — proyecto fuera del patrón MVC habitual del estudio.
- 2026-07-30 (v2): confirmada la estructura real de 6 páginas institucionales (antes era una analogía genérica de 4-5) tras recibir el dossier corporativo real de Diercas. Nueva sección "Clientes/Nodos de confianza" con riesgo de autorización de marca de terceros. Riesgo de fidelidad de marca bajó (hay brandbook real), pero persiste la necesidad de archivos fuente editables del logo.
- 2026-08-13 (v3 — presupuesto aprobado, arranca implementación): hosting confirmado (DonWeb), remitente/destinatario del contacto confirmados, nueva Content Collection de Clientes (mismo patrón que Trabajos). 2 dependencias del cliente quedan explícitas y no bloqueantes para el resto del sitio: logo vectorial (Etapa 2, según el cliente) y QR Data Fiscal (a generar por el cliente desde ARCA). 1 bloqueo real de maquetado, acotado a la página de Servicios: confirmar el estado de Ciberseguridad/Audio-Video antes de cerrar esa página puntual.
