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

**2. Formulario de contacto** — mismo patrón que `labipac-front/src/pages/contacto.astro`: formulario con validación HTML5, envío vía `fetch` a un endpoint PHP (`/api/contact.php`), estado de éxito/error inline, sin recarga de página. **Remitente/destinatario confirmados (2026-08-13)**: el mail sale desde `no-reply@olvidata.com.ar` (buzón del estudio, ya usado para este tipo de envío en otros proyectos) hacia `administracion@diercas.com.ar` — el visitante no recibe copia automática salvo que se pida explícitamente (no confirmado, no se agrega por defecto).

**4. Sección de Clientes / Certificaciones (nuevo, 2026-08-13)** — el listado de logos de clientes se modela igual que el criterio ya usado en "trabajos realizados": datos en un archivo de contenido (JSON/YAML o Content Collection), no hardcodeado en el markup de la página — cada cliente es `{ nombre, logo, rubro: "publico"|"privado", categoria opcional }`. Agregar un cliente nuevo es agregar una fila al archivo de contenido, no tocar el componente de la grilla. La franja de Certificaciones (RITE/Data Fiscal/Apto Estado) es contenido estático simple (no necesita Content Collection, son 3 elementos fijos).

**3. Blog / portfolio de trabajos realizados (nuevo)**
- **Listado** (`/trabajos` o similar): grid de tarjetas, una por trabajo, con foto de portada + título + fecha.
- **Detalle** (`/trabajos/[slug]`): descripción completa + galería de fotos del trabajo.
- Contenido modelado como Astro Content Collection: cada trabajo es un archivo markdown con front-matter (`titulo`, `descripcion`, `fecha`, `fotos: []`) — agregar un trabajo nuevo es agregar un archivo, sin tocar código de las páginas de listado/detalle (ya genéricas).

**Ya no es hipótesis — sitemap confirmado con contenido real del cliente (2026-08-13):**

### Sitemap final

1. **`/` Inicio** — hero con propuesta de valor del dossier, resumen visual de las 3 ramas (Infraestructura / Provisión de equipos / Infraestructura de eventos) con link a `/servicios#<ancla>`, franja de confianza (RITE + Data Fiscal + "Apto para contratar con el Estado") visible sin scrollear demasiado, muestra acotada de logos de clientes (los de mayor peso institucional primero: Presidencia de la Nación, Ministerio de Salud, Poder Judicial) con link a `/clientes` para ver el listado completo.
2. **`/nosotros` Nosotros / Sectores** — contenido ya redactado en el dossier (visión institucional + sectores Público/Privado/Instituciones).
3. **`/servicios` Servicios** — 3 bloques según lo confirmado por el cliente (§ Análisis "Contenido real de negocio"):
   - **Infraestructura**: data centers, servidores, redes LAN, fibra óptica — con mención explícita de equipo propio (OTDR, Fusionadora) como diferencial de credibilidad técnica (no service tercerizado).
   - **Provisión de equipos y accesorios e insumos informáticos**: para organismos públicos y privados.
   - **Infraestructura de eventos**: configuración de dispositivos para conferencias, charlas y eventos.
   - **Resuelto 2026-08-13**: Ciberseguridad y Audio/Video quedan fuera de Etapa 1, marcados como posibles bloques 4/5 de Etapa 2 — el layout de la página reserva esa estructura sin necesidad de rediseño si se confirman más adelante.
4. **`/clientes` Clientes / Nodos de confianza** — agrupados por rubro, **dos grupos principales**: **Sector Público** (Presidencia de la Nación, Ministerio de Salud de la Provincia, Poder Judicial de la Provincia, Hospitales) y **Sector Privado** (EDELP, Club Estudiantes de La Plata, LPRC, Colegio Patris, Aloise, CAAITBA, Bodegón Urquiza, Flora Café, Lo de Edgardo). **Recomendación de research/criterio UX**: mostrar el grupo **Público primero** — es el activo de mayor peso institucional que tiene Diercas y refuerza directamente el mensaje de "aptos para contratar con el Estado" antes de que el visitante llegue a esa sección; el sector privado se muestra después, también agrupado (ej. subgrupos informales "Educación/Instituciones", "Gastronomía/Comercio", "Deporte/Clubes" si el volumen de logos lo justifica visualmente).
5. **Certificaciones / Confianza institucional** (nueva, 2026-08-13) — bloque propio (dentro de Nosotros o sección independiente enlazada desde el header, a definir en Arquitectura): badge RITE (con link al perfil público en `rite.gob.ar` si Diercas lo tiene) + texto "Diercas cumple los requisitos para contratar con el Estado argentino — Nación, Provincia y Municipio". **QR Data Fiscal resuelto 2026-08-13: pasa a Etapa 2** (dependencia del cliente, no bloquea el lanzamiento de Etapa 1) — la franja queda con espacio reservado para sumarlo sin rediseño cuando el cliente lo genere desde ARCA.
6. **`/trabajos` Trabajos realizados** — **Etapa 2, contenido aún no formulado por el cliente** (confirmado en Análisis). No se agrega al menú de navegación principal todavía — se suma cuando haya contenido real, mismo patrón de Content Collection ya diseñado en v1 (sin cambios de estructura técnica).
7. **`/contacto` Contacto** — mail `administracion@diercas.com.ar` y WhatsApp `221 570 6954` como datos de contacto directo, más el formulario (ver abajo) — mismo patrón visual que `labipac-front/contacto.astro` (tarjetas de datos + formulario), contenido adaptado a Diercas.

### Hipótesis a validar (reemplaza la de v1)
La existencia y ubicación exacta de Ciberseguridad/Audio-Video en el sitemap (punto 3) — no se maqueta esa parte de Servicios hasta tener la confirmación de Joaquín.

### ViewModels definidos
No aplica en sentido estricto (sitio estático sin backend de negocio) — el "modelo" relevante es el esquema de front-matter de las Content Collections:
- Trabajos (Etapa 2): `titulo: string`, `descripcion: string`, `fecha: date`, `fotos: string[]`.
- Clientes (nuevo, 2026-08-13): `nombre: string`, `logo: string (ruta de imagen)`, `rubro: "publico" | "privado"`, `orden: number` (opcional, para priorizar los de mayor peso institucional dentro de cada grupo).

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
- 2026-08-13 (v2 — presupuesto aprobado, contenido real recibido): sitemap final de 7 páginas/secciones con contenido real (3 ramas de Servicios, Clientes agrupados por rubro con Público primero por criterio UX, franja de Certificaciones RITE+Data Fiscal+Apto Estado, Trabajos pospuesto a Etapa 2 y fuera del menú por ahora). Confirmado remitente/destinatario exacto del formulario de contacto. Nuevo Content Collection de Clientes (antes solo existía el de Trabajos). Pendiente: confirmación de Joaquín sobre Ciberseguridad/Audio-Video antes de maquetar Servicios.
