# Memoria - Presupuestador

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-07-30 (v2 — recalculado con contenido real: brandbook + dossier corporativo)

## Definiciones vigentes

### Nota de calibración — primer proyecto de este tipo en el dataset del estudio

Todo el histórico de calibración (`27-presupuesto-parametros.instructions.md`) está anclado en proyectos MVC con backend/BD. Este es el **primer sitio puramente estático (Astro, sin backend de negocio) que se presupuesta en el estudio** — no hay cierre real de referencia para "página institucional Astro" ni para "blog/portfolio con Content Collections". La tasa (USD 35/h) y la fórmula (M×$16.80) se aplican igual (son independientes del tipo de proyecto), pero el M de cada ítem es una estimación de primera vez, no anclada en un cierre real propio.

**Ancla de cruce (no de cálculo):** el propio bot de CRM del estudio (`OlvidataCRM`) cotiza automático "Landing page / sitio sin sistema de gestión" a **USD 300** (plan Starter) para un sitio simple sin blog. El resultado de este presupuesto (~USD 425, ver abajo) es coherente con esa referencia — más alto porque suma el blog/portfolio, 3 tablas técnicas de servicios y una sección de clientes/prueba social que un sitio institucional simple no tiene.

### WBS funcional vigente (v2 — recalculado con la estructura real de páginas)

| # | Módulo | M (h) | Base de reutilización |
|---|---|---:|---|
| 1 | Setup base + Layout + sistema de diseño con branding de Diercas (brandbook real: logo, paleta cian/violeta, tipografía) | 6 | `labipac-front` (stack Astro+Tailwind+Layout, 2h reuse) + 4h nuevo (implementar el sistema visual real de Diercas con fidelidad) |
| 2 | Páginas institucionales: Inicio, Nosotros, Sectores/Verticales, Contacto (4 páginas simples) | 4 | `labipac-front` (patrones hero/cards, 3h reuse) + 1h nuevo (contenido/estructura específica) |
| 3 | Página de Servicios (3 tablas técnicas: Redes LAN, Fibra Óptica, Ciberseguridad) | 2 | `labipac-front` (patrón de sección con cards, 1h reuse) + 1h nuevo (maquetación de datos tabulares técnicos, responsive) |
| 4 | Sección Clientes / "Nodos de confianza" (listado curado por categoría) | 1,5 | `labipac-front` (grid/cards, 0,5h reuse) + 1h nuevo (layout específico tipo "nodos", pendiente definir logos vs. texto) |
| 5 | Formulario de contacto + endpoint PHP de envío | 1 | `labipac-front` (`contact.php`), reuse total |
| 6 | Blog/portfolio de trabajos realizados (Content Collection: listado + detalle) | 5 | Sin precedente exacto — 100% desarrollo nuevo (primer uso de Content Collections en el estudio) |
| 7 | SEO básico, responsive, deploy inicial | 3 | Patrón de deploy ya resuelto (2h reuse) + 1h nuevo (ajustes propios del hosting de destino) |
| | **Total** | **22,5 ≈ 23** | |

*Nota: proyecto pequeño y cohesivo — se presupuesta como una sola entrega, no se divide en Etapa 1/Etapa 2 como en los proyectos MVC del estudio.*

### Cálculo de reutilización (R) y Tier aplicable

| | Horas |
|---|---:|
| Total M | 23h |
| Horas ancladas en reuse directo (stack/patrones de `labipac-front`) | 10h |
| Horas de desarrollo nuevo (branding específico + tablas técnicas + nodos de confianza + blog/portfolio) | 13h |

**R = 10 / 23 = 43,5%** → **Tier 2 (40% ≤ R < 70%): 15% de descuento**, según `27-presupuesto-parametros.instructions.md`. No llega a Tier 1 porque el blog/portfolio (5h, la pieza más grande) sigue siendo 100% nuevo, sin precedente, y ahora se suman las tablas técnicas de Servicios y la sección de Nodos de confianza (también mayormente nuevas).

Gatillo económico: tablero de ciclos económicos en verde/consolidación a la fecha (2026-07-30) → Tier 2 habilitado sin restricción.

### Tasa vigente y contingencia aplicada
- Tasa vigente: USD 35/h. Fórmula: `Costo = M × $16.80` (M/2.5 × 1.20 × $35, contingencia del 20% ya incorporada).

### Resumen economico (con Tokens IA como item individual)

| Concepto | USD |
|---|---:|
| Subtotal (lista, 23h × $16.80) | 386,40 |
| Tokens IA (25% del subtotal de lista) | 96,60 |
| Descuento Tier 2 (15% del subtotal de lista) | −57,96 |
| **Total cliente** | **≈ 425** |

Por encima del piso absoluto de USD 280 (`27-presupuesto-parametros.instructions.md`) — no aplica ningún ajuste por piso.

### Calibraciones historicas usadas
- `labipac-front` (repo real, no un proyecto "cerrado" con horas registradas — se usó como referencia estructural/técnica directa, no como dato de horas reales).
- `OlvidataCRM` — `IndustriaCatalogo` seed "Landing page / sitio sin sistema de gestión" (Plan Starter, USD 300) como ancla de cruce de precio de mercado interno.
- Dossier corporativo y brandbook reales de Diercas (2026-07-30) — usados para confirmar alcance de páginas y reducir la incertidumbre de fidelidad de marca, no aportan horas reales de cierre.
- Sin cierre real propio de este tipo de proyecto — recalibrar cuando este presupuesto (o uno similar) cierre con horas reales.

### Cierre estimado vs real (si disponible)
Pendiente — proyecto en etapa de presupuesto, aún no iniciado.

## Historial de ajustes
- 2026-07-30: Presupuesto interno v1 — WBS de 5 módulos (20h totales), R=45% → Tier 2 (15% descuento). Total cliente ≈ USD 370. Declarado explícitamente como primer proyecto puramente front-end presupuestado en el estudio, sin cierre real de referencia propio.
- 2026-07-30 (v2): recibidos brandbook y dossier corporativo reales de Diercas — la estructura genérica de 5 módulos se reemplaza por 7 módulos anclados en contenido real: 4 páginas institucionales simples, 1 página de Servicios con 3 tablas técnicas (Redes LAN/Fibra Óptica/Ciberseguridad), 1 sección nueva de Clientes/"Nodos de confianza" (prueba social con clientes reales), formulario, blog/portfolio y deploy. Total subió de 20h a 23h y de R=45%→43,5% (mismo Tier 2, sin cambio de tier). **Total cliente actualizado: ≈ USD 425** (antes ≈ USD 370). No incluye hosting ni mantenimiento anual — se cotiza aparte una vez definido el destino de hosting.
