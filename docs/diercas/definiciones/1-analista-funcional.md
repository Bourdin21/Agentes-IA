# Memoria - Analista funcional

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-07-30 (v2 — recibidos brandbook, dossier corporativo y presentación real de Diercas)

## Definiciones vigentes

### Perfil real del cliente (CONFIRMADO 2026-07-30 — antes desconocido)

Diercas SA es una empresa de **infraestructura de conectividad y ciberseguridad**: Redes LAN (cableado estructurado Cat6/Cat6A/Cat7), Fibra Óptica (Backbone & FTTH, empalme por arco voltaico, fibra OS2/OM3/OM4/OM5), y una unidad nueva de **Ciberseguridad** (Security by Design, Tríada CIA). Atiende 3 sectores: Público (ministerios, poder judicial, legislatura), Privado (ROI/continuidad de negocio, datacenters) e Instituciones (salud, educación, seguridad). Tiene clientes reales de peso institucional (ver §Nodos de confianza). Contacto real: `administracion@diercas.com.ar`, `www.diercas.com.ar`, Diego H. Castro (Gerente Comercial).

### Sitio actual (relevado 2026-07-30 vía `https://diercas.com.ar/`) — punto de partida real de la modernización

El sitio vigente es un **one-pager** (una sola página con anclas `#servicios`, `#clientes`, `#contacto`, sin páginas separadas): hero/slider con la propuesta "Venta de equipos, insumos y servicios", dos líneas de servicio — **Informática** (soporte técnico, redes, sistemas operativos, servidores, software a medida, backups, reparación de TPVs y cámaras CCTV) y **Audio y Video** (cámaras profesionales, monitores, ópticas, sistemas de grabación) —, una sección "Por qué elegirnos" (Crecimiento/Profesionalismo/Compromiso), una **galería de 14 logos de clientes reales con link a sus sitios** (ya existe hoy, sin necesidad de armarla de cero), y contacto solo por mail/teléfono/WhatsApp/redes — **sin formulario de contacto**. Paleta azul corporativa, sin blog ni portfolio.

**⚠️ Discrepancia real a resolver con el cliente antes de Diseño**: el sitio actual describe a Diercas como "venta de equipos, insumos y servicios" con foco en Informática + Audio/Video — el dossier corporativo y el brandbook (más nuevos, ver abajo) reposicionan a la empresa como especialista en **Redes LAN, Fibra Óptica y Ciberseguridad** para clientes institucionales de alto perfil, sin mencionar venta de equipos ni audio/video. Son dos narrativas de negocio distintas. **No asumido silenciosamente**: hay que confirmar con Diercas si el sitio nuevo (a) reemplaza completamente el posicionamiento viejo por el nuevo (caso ya presupuestado: Servicios = solo Redes LAN/Fibra/Ciberseguridad), o (b) mantiene también Informática y Audio/Video como líneas de negocio vigentes junto a las nuevas (sumaría 2 bloques de servicio más al alcance, con su propio ajuste de horas/precio).

### Modulos/features analizados

1. **Sitio institucional en Astro** — modernización del sitio actual de Diercas SA. Estructura técnica de referencia: `labipac-front` (repo real ya construido por el estudio, `C:\Sistemas\labipac-front`) — mismo stack (Astro + Tailwind CSS), mismo patrón de Layout compartido, mismo formulario de contacto con endpoint PHP (`/api/contact.php`). La estructura de **páginas/secciones** ya no es una analogía genérica — se define por el contenido real de Diercas (ver §Páginas confirmadas).
2. **Branding — ya no es una hipótesis, hay brandbook real** (`DIercas_Brandbook_OK.pdf`, abril 2022): logotipo "D" (curvas en gradiente cian→azul→violeta formando una D con motivo de flecha), versiones vertical/horizontal/reducida + grilla constructiva, tipografía bold sans-serif para el wordmark, fondo azul marino oscuro como superficie de marca predominante, tagline "Conectados a través de la tecnología". Ya existen aplicaciones de marca reales (firma de mail, plantilla social media, plantilla de mailing) — el sistema visual está maduro y consistente, no es un logo aislado sin contexto de uso.
3. **Blog / portfolio de trabajos realizados** — sección de "trabajos realizados" con actualización cada 6 meses. **Joaquín carga el contenido** (no el cliente, no hay panel de administración) — el cliente solo provee descripción y fotos de cada trabajo por fuera del sistema (mail/WhatsApp/Drive). Encaja con el patrón de Astro Content Collections: cada trabajo es un archivo markdown con front-matter (título, descripción, fecha, fotos), sin necesidad de CMS ni login.

### Páginas confirmadas (reemplaza la hipótesis genérica de la v1)

Basado en el dossier corporativo real:
1. **Inicio** — hero con propuesta de valor ("La arquitectura de la conexión" / "Conectados a través de la tecnología").
2. **Nosotros / Filosofía** — visión estratégica institucional (texto ya redactado en el dossier, reutilizable como base de contenido).
3. **Servicios** — 3 líneas técnicas con sus propias tablas de especificación:
   - Redes LAN (Cat6/Cat6A/Cat7, certificación de enlaces, escalabilidad, arquitectura de topologías).
   - Fibra Óptica / Backbone & FTTH (empalme por arco voltaico, fibra OS2/OM3/OM4/OM5, inmunidad EMI, certificación OTDR).
   - Ciberseguridad (Security by Design, Tríada CIA, 3 ejes: protección de infraestructura, integridad de datos, disponibilidad continua).
4. **Sectores / Verticales** — Público, Privado, Instituciones, cada uno con enfoque + soluciones propias (ya redactado en el dossier).
5. **Clientes / Nodos de confianza** — listado curado de clientes reales por categoría (sector público: Ministerio de Salud, Ministerio de Seguridad, Cámara de Diputados y Senadores, Poder Judicial — todos Prov. de Bs.As.; privado/cultura/deportes: Hotel Marriott Corrientes, GINSA SA, Aloise y Cia, Instituto Cultural Prov. de Bs.As., Club Estudiantes de La Plata). **Riesgo de autorización de marca reducido (2026-07-30): el sitio actual YA muestra 14 logos de clientes reales con link a sus sitios** — es práctica ya establecida de Diercas, no una novedad a autorizar desde cero. Igual conviene confirmar si son los mismos 14 logos (reutilizables tal cual) o si cambia el listado.
6. **Trabajos realizados** (blog/portfolio) — listado + detalle, ver módulo 3.
7. **Contacto** — formulario + datos de contacto reales.

### Reglas funcionales acordadas

- R1: el branding sigue el brandbook real de Diercas (logo, paleta cian/azul/violeta sobre fondo azul marino, tipografía) — no hay margen de interpretación visual libre del estudio.
- R2: la carga de contenido del blog/portfolio la hace Joaquín, no el cliente ni un panel de administración — el cliente entrega insumos (texto + fotos), Joaquín arma y publica.
- R3: cadencia de actualización del blog/portfolio: cada 6 meses (no continua, no requiere automatización de publicación).
- R4 (nueva): la sección de Servicios muestra contenido técnico específico por línea (tablas de especificación) — no es texto de marketing genérico, requiere maquetación de datos tabulares.

### Criterios de aceptacion vigentes

- PF1: todas las páginas respetan la paleta de colores, tipografía y logo del brandbook de Diercas, sin colores/fuentes fuera de ese lineamiento.
- PF2: el formulario de contacto envía el mensaje correctamente a `administracion@diercas.com.ar` (reutiliza patrón `contact.php` de `labipac-front`).
- PF3: la sección de trabajos realizados muestra un listado (grid) y una vista de detalle por trabajo, con foto(s) y descripción.
- PF4: agregar un trabajo nuevo al portfolio no requiere tocar código de página ni backend — solo agregar un archivo de contenido (markdown) con los datos del trabajo.
- PF5 (nueva): la página de Servicios muestra correctamente las 3 tablas técnicas (LAN/Fibra/Ciberseguridad) de forma legible en mobile (son datos densos, requieren diseño responsive cuidado).

### Supuestos y dependencias

- ~~Dependencia bloqueante: assets de marca reales~~ → **Parcialmente resuelta**: existe brandbook PDF real con logo, paleta y aplicaciones de marca. **Sigue pendiente**: archivos fuente editables (logo en vector AI/EPS/SVG, no solo el PDF de referencia; nombre exacto de la tipografía usada) — el PDF alcanza para implementar con fidelidad visual, pero los archivos fuente agilizan y evitan recrear el logo desde cero por trazado.
- ~~Dependencia bloqueante: rubro/actividad de Diercas no confirmada~~ → **Resuelta**: infraestructura de redes/fibra/ciberseguridad, confirmado con dossier real. Estructura de páginas definida en §Páginas confirmadas.
- ~~Dependencia: confirmar si la sección de clientes puede mostrar logos reales~~ → **Muy acotada**: el sitio actual ya lo hace (14 logos con link), solo confirmar si se reutiliza el mismo listado.
- **Nueva dependencia bloqueante para Diseño**: resolver la discrepancia entre el posicionamiento del sitio actual ("venta de equipos, Informática + Audio/Video") y el del dossier/brandbook ("Redes LAN, Fibra Óptica, Ciberseguridad para clientes institucionales") — define si Servicios tiene 3 o 5 bloques. Este presupuesto está anclado en la versión de 3 bloques (dossier); si el cliente confirma que quiere mantener también Informática y Audio/Video, se re-cotiza esa ampliación.
- Supuesto: el contenido de Servicios/Nosotros/Sectores puede partir del texto ya redactado en el dossier corporativo (reduce trabajo de copy, aunque sigue siendo tarea del estudio maquetarlo y adaptarlo a formato web).
- Supuesto: hosting del sitio nuevo — pendiente de definir (candidato natural: DonWeb, mismo servidor donde vive `labipac-front`). Confirmar con Joaquín antes de presupuestar el hosting como parte del proyecto o aparte.
- Supuesto: el formulario de contacto reutiliza el mismo patrón PHP ya construido para `labipac-front` — a confirmar que el hosting de destino soporte PHP.
- No se encontraron archivos de proyecto adicionales en `C:\Users\joaco\Downloads` más allá de los 3 PDF ya recibidos (brandbook, dossier corporativo, presentación de arquitectura digital) — no hay logo vectorial ni fuentes tipográficas todavía.

### Exclusiones confirmadas

- Panel de administración / CMS para el blog — la carga la hace Joaquín directamente en el repo (archivos de contenido), no el cliente.
- Copywriting/redacción de textos institucionales desde cero — el cliente ya provee una base real en el dossier corporativo; el estudio adapta/maqueta, no redacta desde cero.
- Automatización de publicación periódica — la cadencia de 6 meses es manual (Joaquín agrega contenido y redeploya cuando corresponde).
- Gestión de autorizaciones de marca de terceros (logos de clientes en "Nodos de confianza") — es responsabilidad de Diercas conseguirlas si se decide mostrar logos reales.

## Historial de ajustes
- 2026-07-30: Análisis v1 creado. Alcance definido por analogía genérica con `labipac-front` + blog/portfolio nuevo. 2 dependencias bloqueantes declaradas: assets de marca reales y rubro/alcance de páginas no confirmado.
- 2026-07-30 (v2): recibidos brandbook real, dossier corporativo y presentación de arquitectura digital de Diercas. **Ambas dependencias bloqueantes de la v1 quedan resueltas o muy acotadas**: se confirma el rubro real (infraestructura de redes/fibra/ciberseguridad), la estructura de páginas pasa de ser una analogía genérica a estar basada en contenido real (7 páginas/secciones, incluyendo una página de Servicios con 3 tablas técnicas y una sección nueva de "Nodos de confianza" con clientes reales), y el branding ya no es una incógnita (brandbook completo con logo, paleta, tipografía y aplicaciones de marca ya definidas). Impacto en presupuesto: WBS recalculado en `4-presupuestador.md` (20h→23h, ~USD 370→~USD 425) por el mayor número real de secciones confirmado.
- 2026-07-30 (v3): relevado el sitio actual real (`https://diercas.com.ar/`) — es un one-pager (Inicio/Servicios/Clientes/Contacto por anclas, sin páginas separadas), sin formulario de contacto, con 14 logos de clientes ya publicados. Confirma que el proyecto es una modernización real (de one-pager a sitio multi-página) y reduce el riesgo de la sección de clientes (ya es práctica existente). **Detectada discrepancia de posicionamiento** entre el sitio actual ("venta de equipos, Informática + Audio/Video") y el dossier/brandbook ("Redes LAN/Fibra/Ciberseguridad institucional") — declarada como nueva dependencia bloqueante para Diseño, no resuelta unilateralmente. El presupuesto vigente asume la versión del dossier (3 líneas de servicio); si el cliente pide mantener también Informática/Audio-Video, se re-cotiza esa ampliación.
