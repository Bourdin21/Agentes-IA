# Precio de lista — Landing 2D autogestionable (blog de promociones)

Fecha: 2026-10-02. **Vigente como referencia para futuros presupuestos**, fijado por Joaquín. Producto nuevo del catálogo de Landing: Landing 2D + panel de autogestión de promociones/novedades.

Continúa `research-precios-landing-build-2026-09.md` (ese archivo ya proponía como alternativa para Landing 2D "setup 250 + 300/año"; lo que se fijó acá va en esa dirección). Primer deal: MACERATA FIAMBRERIA (La Plata, outbound frío del bot).

TC de referencia: USD 1 = ARS 1.555 (blue venta, 02/10/2026).

## Precio de lista

| Concepto | Precio | Nota |
|---|---|---|
| **Landing 2D autogestionable — primer año** | **USD 500, todo incluido** | Diseño y desarrollo + panel de promos + dominio + hosting + SSL + SEO técnico básico + capacitación 20-30 min e instructivo de 1 página + soporte y mantenimiento del 1er año |
| **Mantenimiento anual, desde el 2º año** | **USD 300/año** | Dominio, hosting, SSL, soporte, mantenimiento y sostenimiento del panel |
| **Upgrade a 3D** (estética olvidata.com.ar) | **+USD 100** | Fijado a mano por Joaquín, muy por debajo del tier 3D del catálogo (setup 2.000-3.000 + 600-900/año en el research de sep). **No es precio de lista del frente Landing 3D** |
| Módulo "Blog de promociones autogestionable" suelto | USD 240 de lista | M = 11,5 h, fórmula Merge/Extras (M × USD 16,80 × factor 2,5 × 1,25 de Tokens IA) |

**Forma de pago:** una vez por año, en pesos, al valor del dólar blue **del día del pago** (no al del día de la propuesta). Al TC de referencia: 1er año ≈ ARS 777.000, anual ≈ ARS 466.000, upgrade 3D ≈ ARS 155.000.

## Relación con el cálculo formal

El cálculo por fórmula daba **USD 615 el 1er año** (Landing 2D 375 + módulo 240) y 375/año desde el 2º. Joaquín lo pisó a 500 / 300 para competir en el segmento de comercio de barrio. Queda documentado que:

- El piso de fórmula del módulo de autogestión es **USD 193** (sin el colchón de Tokens IA). A USD 500 todo incluido, el módulo va **sin margen**.
- El recurrente de 300/año sigue dentro del rango de mercado (USD 200-410/año por hosting + dominio + mantenimiento por separado), en la franja media.
- El precio de lista del módulo suelto se mantiene en **USD 240**: lo de Macerata no es excepción de catálogo sino el precio del nuevo producto empaquetado.

## Alcance técnico que respalda el precio

Opción git-based, sobre el stack de `diercas-front` (Astro + Tailwind estático, deploy por FTP):

1. Sveltia/Decap CMS en `/admin` del propio sitio, colección `promos` (título, imagen, vigencia, cuerpo, destacada).
2. Repo en GitHub + GitHub Action: commit del CMS → `astro build` → deploy por FTP. **Este pipeline no existe todavía** — en diercas-front el deploy es manual.
3. Login del cliente vía OAuth de GitHub: broker propio en Cloudflare Workers (tier gratis). **Se monta una sola vez y queda como activo reusable** para todos los clientes de catálogo; la inversión inicial la absorbe el estudio, igual que cualquier patrón nuevo.
4. Sección Promos (listado + detalle) como Content Collection — reusa el patrón de "Trabajos realizados" de diercas.
5. El cliente necesita cuenta propia de GitHub (gratis) con acceso **solo a ese repo**, nunca a la cuenta/org de Olvidata.

**SEO:** lo que se promete es SEO técnico básico (que Google indexe y el negocio aparezca en búsquedas), **no** posicionamiento mensual ni rankings garantizados.

**Riesgo abierto a definir:** si el build de la Action falla, el sitio no se actualiza y el cliente no tiene aviso visible — puede creer que publicó y no. Falta resolver a qué casilla llega la notificación de falla.

## Research de mercado que respalda el precio (02/10/2026)

Dos mercados distintos; el producto se posiciona en el segundo:

| Segmento | Landing | Institucional | Autoadministrable con panel |
|---|---|---|---|
| Freelance / estudio chico | USD 50-130 | USD 115-230 | no lo ofrecen |
| Agencia | USD 195-325 | USD 325-580 | **USD 580-1.420** (ARS 900.000-2.200.000); con blog/CMS hasta USD 2.580 |

- Competidor platense real: **BacchisWork** (La Plata) — landing ARS 100.000 ≈ USD 65, web completa ARS 200.000 ≈ USD 130, e-commerce ARS 800.000 ≈ USD 515. Hosting y dominio aparte, sin autogestión. Suscripción alternativa desde ARS 30.000/mes.
- Recurrentes de mercado: hosting USD 6-8/mes, dominio USD 5/año, mantenimiento USD 10-26/mes → **USD 200-410/año** todo junto, sin panel.

**Conclusión:** los USD 500 del 1er año quedan por debajo del piso del segmento autoadministrable de agencia (580). El riesgo comercial real no es el precio sino el comparable barato: un comercio de barrio que pide otro presupuesto en La Plata recibe USD 65-130 por "una página", 4x menos. **Por eso el argumento de venta es el desglose del "todo incluido" y la palabra *autogestionable*, nunca "una página"** — bajar el precio no cierra esa brecha, el desglose sí.

Fuentes: bacchiswork.com.ar/paginas-web-la-plata, farostudio.com.ar (10/05/2026), bigredes.com, tradeweb.com.ar.

## Salvedades

1. Casi todas las fuentes son blogs de agencias optimizados para SEO: los rangos sirven como orden de magnitud, no como precios verificados.
2. Los números de las fuentes de mayo 2026 vienen retrasados por inflación respecto de octubre.
3. El upgrade 3D a +USD 100 es un número comercial de este deal. Si se repite, hay que revisarlo contra el tier 3D del research de septiembre antes de volverlo lista.
