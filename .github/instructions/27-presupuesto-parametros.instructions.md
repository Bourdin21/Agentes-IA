---
description: Parametros base de estimacion y presupuesto. Calibrado sobre proyectos reales de OlvidataSoft.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia - Proyectos calibrados

**Fuente estructurada (leer primero):** `/docs/calibracion/dataset.yml` tiene los rangos por tipo de modulo, la tabla de modificacion sobre modulo existente y los cierres reales en formato consultable, sin tener que releer toda la prosa historica de abajo. Este archivo sigue siendo la fuente de RAZONES y contexto de cada cierre — leerlo cuando se necesite entender por que paso algo, no para buscar un numero.

Los datos especificos de cada proyecto viven en /docs/<proyecto>/definiciones/4-presupuestador.md.
Para calibrar, leer primero ese archivo antes de estimar.

Proyectos de referencia disponibles:
- /docs/eleven-la-plata/definiciones/4-presupuestador.md (50 h reales, 27 modulos, .NET 10)
- /docs/vinosefue/definiciones/4-presupuestador.md (30 h reales, 16 modulos, maquinas de estado)
- /docs/delicias-naturales/definiciones/4-presupuestador.md (95 h base / 110 h con contingencia, 19 modulos, dataset por modulo)
- /docs/recotrack/definiciones/4-presupuestador.md (dataset ABM simple/intermedio con 30% incluido)
- /docs/lumitrack/definiciones/4-presupuestador.md (dataset ABM intermedio/complejo con 30% incluido)
- /docs/piapartments/definiciones/4-presupuestador.md (ABM intermedio con 30% incluido)
- /docs/energy-nutrition/definiciones/4-presupuestador.md (138 h estimadas, 14 modulos + 4 integraciones, referencia metodologica v4.0 — SIN CIERRE REAL, usar solo para integraciones externas y metodo)
- /docs/contadores-bma-conversor/definiciones/4-presupuestador.md (8 h reales, 3 modulos, PHP + parser Excel propietario — CIERRE REAL 2026-06-29)
- /docs/ganaderia/definiciones/4-presupuestador.md (20 h reales, 8 modulos funcionales, 101.0 h PERT con contingencia estimadas — CIERRE REAL 2026-07-03, ratio PERT/real record del dataset: 5.05x. Precio comercial real: USD 950 total con 15% desc. referido + 1er año de mantenimiento incluido; desarrollo puro ≈ USD 650 ≈ USD 32.5/h efectivo, cercano al objetivo USD 35/h. **Proyecto de referencia comercial para alcances similares.**)
- /docs/vinosefue/definiciones/4-presupuestador.md — sprint "Compras al proveedor: armado manual y cuenta corriente" (4 h reales total del lote, 8 items reconstruidos retroactivamente en 28.27 h PERT con contingencia — CIERRE REAL 2026-07-03, **nuevo record del dataset: ratio PERT/real 7.07x, ratio formula/real 2.86x**. Es una iteracion evolutiva (reutiliza CuentaCorriente/MovimientoCC de Cliente, AdjuntoService, MetodoPago), no un proyecto nuevo desde cero — ver regla de granularidad nueva abajo.)
- /docs/labipac/definiciones/4-presupuestador.md — SESION 3 (3 modulos: Unidad/PrecioPorUnidad en Perfiles, Carga masiva + alta rapida, fix ancho columna PDF; 11.5 h M base / 13.69 h con contingencia — CIERRE REAL 2026-07-08, 2.0 h reales totales incluyendo 3 fixes post-QA. **Segundo lugar del dataset: ratio PERT-contingencia/real 6.84x, ratio formula/real 2.76x** (detras de vinosefue 7.07x/2.86x). Es la 3ra ronda de mejoras evolutivas sobre el mismo sistema (reutiliza el patron visual/AJAX de la card IVA de F-002, el AJAX GetPrecioItem y CreateAsync ya existentes) — ver regla de "segunda/tercera ronda sobre el mismo modulo" agregada abajo.)
- /docs/vinosefue/definiciones/4-presupuestador.md — feature "Filtro de categoria al exportar catalogo de Productos" (6 items reconstruidos ya anclados en "iteracion evolutiva" desde el arranque — 5.75 h M base / 6.55 h con contingencia — CIERRE REAL 2026-07-13, 1.5 h reales totales incluyendo diseño, implementacion completa y deploy de migracion+script en produccion. **Ratio PERT-contingencia/real 4.37x, ratio formula/real 1.84x — el mas bajo del dataset entre los cierres "evolutivos"**, confirma que anclar la reconstruccion en reutilizacion de patrones desde el inicio (no solo corregir despues) sigue bajando el ratio de sobreestimacion.)

## Conclusion de calibracion

- Los proyectos historicos cerrados (Eleven, Vinosefue) confirman sus horas como referencia solida de esfuerzo. El costo se recalcula a la tasa vigente USD 35/h.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.
- La contingencia del 15% se aplica correctamente desde los 50h de base en adelante.
- Con IA asistida, las horas reales son una fraccion pequeña de las horas PERT estimadas, pero la fraccion varia por proyecto: ~1/4 en ShowroomGriffin (4.0x), ~1/5 en Ganaderia con cierre real (5.05x, record del dataset — CIERRE REAL 2026-07-03, reemplaza la proyeccion previa de ~1/3). No asumir un ratio fijo unico: anclar en el cierre real mas parecido antes de estimar.

## Tasa vigente

- Tasa base: USD 35 / hora (Junio 2026 — horas reales con contingencia temporal 20%).
- Tasa anterior: USD 40 / hora (Junio 2026 — probada con contingencia 20%, revertida por ajuste de precio).
- Tasa anterior: USD 30 / hora (Junio 2026 — usada en Energy Nutrition v4.0 como excepcion negociada).
- Tasa anterior historica: USD 14 / hora (proyectos hasta Abril 2026 — quedan como referencia de horas, no de costo).
- Aplicar a todos los presupuestos futuros salvo indicacion contraria del cliente.
- Si el cliente negocia descuento, no bajar de USD 30/h sin aprobacion explicita.
- La tasa aplica sobre horas reales con contingencia (ver formula en "Modelo de facturacion"), no sobre horas PERT.
- La tasa es independiente de la complejidad: proyectos mas complejos se expresan en mas horas, no en mayor tarifa.

## Rangos de referencia por tipo de modulo

Horas M (PERT caso probable) sin cambio. Costos calculados con formula vigente: M x $16.80 (= M/2.5 x 1.20 x $35).
Las "horas facturables" son M/2.5 x 1.20 — no se exponen al cliente (solo USD por area funcional).

| Tipo de modulo | Rango M (h) | Horas facturables | USD (a $35/h con 20% cont.) |
|---|---|---|---|
| Ajuste puntual (campo, validacion, logica menor) | 0.5 – 1 h | 0.2 – 0.5 h | USD 8 – 17 |
| Deploy inicial hosting compartido (subdominio + vendor + .htaccess) | 2 – 3 h | 0.96 – 1.44 h | USD 34 – 50 |
| ABM simple (sin relaciones, sin logica) | 1 – 2 h | 0.5 – 1.0 h | USD 17 – 34 |
| UI pantalla unica sin BD (drag-and-drop, sin framework) | 1 h | 0.48 h | USD 17 |
| ABM intermedio (con relaciones y validaciones) | 4 – 7 h | 1.9 – 3.4 h | USD 67 – 118 |
| Modulo con workflow / estados | 4 – 6 h | 1.9 – 2.9 h | USD 67 – 100 |
| Modulo financiero o con logica compleja | 5 – 8 h | 2.4 – 3.8 h | USD 84 – 134 |
| Parser Excel propietario (formato jerarquico, pivot, multi-input) | 4 – 6 h | 1.9 – 2.9 h | USD 67 – 100 |
| ABM complejo (padre/hijos, trazabilidad) | 7.7 – 11.5 h | 3.7 – 5.5 h | USD 129 – 193 |
| Integracion WS simple (OAuth + mapeo) | 3 – 4 h | 1.4 – 1.9 h | USD 50 – 67 |
| Integracion webhook (BackgroundService + HMAC) | 8 – 10 h | 3.8 – 4.8 h | USD 134 – 168 |
| Integracion ARCA/AFIP (codigo + cert + homologacion) | 7 – 9 h | 3.4 – 4.3 h | USD 118 – 151 |
| Integracion batch doble (rate limit + token refresh) | 15 – 18 h | 7.2 – 8.6 h | USD 252 – 302 |

## Calibracion incremental Abril 2026 (dataset real compartido)

Fuente: dataset de modulos de Delicias Naturales, Recotrack, Lumitrack y Piapartments.
Ver detalle por modulo en /docs/<proyecto>/definiciones/4-presupuestador.md de cada proyecto.

Regla de normalizacion obligatoria:
- Si una referencia historica viene con contingencia del 30% incluida, convertir primero a horas base: Horas base = Horas finales / 1.30.
- Evitar doble contingencia: no volver a aplicar 15% o 25% sobre una referencia ya inflada, salvo justificacion explicita por riesgo nuevo.

Resumen de rangos observados (horas finales con 30% incluida):
- ABM simple: 2 a 4 h (moda observada: 2 h).
- ABM intermedio: 5 a 7 h (moda observada: 6 h — dataset: 5h, 5.5h, 6.5h, 7h).
- ABM complejo: 10 a 15 h.
- ABM complejo con padre/hijos detalle: 10 h como referencia inicial.
- Notificaciones SignalR acotadas: 4.5 h como referencia inicial.

Dataset PHP / parser Excel propietario (horas reales sin contingencia — fuente: contadores-bma-conversor, cierre real 2026-06-29):
- Parser Excel jerarquico multi-input (pivot tall→wide, ~200 cols, 14 columnas calculadas): 4 h reales.
- UI pantalla unica sin BD (3 drop-zones, spinner, branding): 1 h real.
- Deploy inicial hosting compartido Ferozo (subdominio + vendor.zip + .htaccess + iteraciones): 3 h reales.
- Total proyecto (3 modulos): 8 h reales. M estimado original: 11 h. Ratio estimado/real: 1.375x.

Patron de desvio confirmado (contadores-bma-conversor):
- Motor de conversion (parser propietario): M estimado 7 h → real 4 h → ratio 1.75x (sobreestimado por IA efficiency).
- UI pantalla unica: M estimado 2 h → real 1 h → ratio 2.0x (sobreestimado — IA muy eficiente en pantallas sin BD).
- Deploy inicial: M estimado 1 h → real 3 h → ratio 0.33x (SUBESTIMADO 3x — primer deploy siempre subestimado).

Rangos de integraciones externas (horas base PERT, contingencia separada) — fuente: Energy Nutrition v4.0 (estimacion, sin cierre real):
- Integracion WS simple (OAuth + mapeo): 3 – 4 h base.
- Integracion webhook con BackgroundService (HMAC, async): 8 – 10 h base.
- Integracion batch doble con rate limit y token refresh: 15 – 18 h base.
- Integracion ARCA/AFIP (migracion codigo + cert .p12 + homologacion): 7 – 9 h base.
Nota: estas referencias son estimaciones metodologicas (no cierres reales). Recalibrar cuando EN tenga cierre.

Resumen de rangos base equivalentes (sin contingencia):
- ABM simple: 1.5 a 3.1 h.
- ABM intermedio: 3.1 a 5.4 h.
- ABM complejo: 7.7 a 11.5 h.
- ABM complejo con padre/hijos detalle: 7.7 h.
- Notificaciones SignalR acotadas: 3.5 h.

Reglas practicas de uso del dataset:
- Si el pedido nuevo coincide con un modulo comparable, leer primero el 4-presupuestador.md del proyecto de referencia y luego ajustar por drivers reales.
- Si la estimacion final supera 20% del techo historico de la banda elegida, documentar causa puntual.
- Si no hay modulo comparable claro, declarar incertidumbre y devolver rango por fase.

### Modificacion sobre modulo existente
- Agregar campo simple: M ~0.5 h → USD 10
- Agregar regla de negocio: M ~1 a 2 h → USD 20 a 40
- Nuevo reporte o exportacion: M ~1 a 2 h → USD 20 a 40
- Migracion EF requerida: M ~0.5 h → USD 10 por cada migracion
- **Refactor de vinculo/FK entre entidades existentes + migracion de datos** (ej. mover una relacion de nivel padre a nivel hijo, con script de backfill): M ~1.5 a 2 h → USD 25 a 34. Fuente: vinosefue sprint compras proveedor 2026-07-03 (item 3, reparto proporcional ~1.8h de las 4h reales del lote). NO usar el rango de "ABM complejo" (7.7-11.5h) para este patron cuando es sobre un sistema ya entregado.
- **Nuevo ledger/cuenta corriente reutilizando patron ya existente en el sistema** (ej. ya existe CuentaCorriente/MovimientoCC de otra entidad, se replica para una nueva): M ~1 a 1.5 h → USD 17 a 25. Fuente: misma referencia (item 4, ~1.0h reparto proporcional). NO usar el rango de "Modulo financiero" (5-8h) cuando hay un patron identico ya resuelto en el mismo repo.
- **ABM manual reutilizando servicios ya existentes** (adjuntos, metodos de pago, validaciones ya implementadas en otro flujo): M ~0.5 a 1 h → USD 10 a 17. Fuente: misma referencia (item 5, ~0.5h reparto proporcional).

**Regla de granularidad obligatoria (agregada 2026-07-03):** antes de clasificar un item como "modulo nuevo" (ABM/financiero/workflow con los rangos de la tabla principal), verificar primero si es una **iteracion evolutiva sobre un sistema ya entregado que reutiliza un patron ya resuelto en el mismo repo** (mismo tipo de entidad, mismo servicio, mismo flujo ya implementado para otra entidad/modulo). Si aplica, anclar en esta seccion ("Modificacion sobre modulo existente"), no en los rangos de modulo nuevo — el cierre de vinosefue (2026-07-03) confirmo que usar los rangos de "modulo nuevo" para este tipo de trabajo sobreestima 5-9x.

**Regla de segunda/tercera ronda sobre el mismo modulo (agregada 2026-07-08, fuente labipac SESION 3):** cuando un proyecto ya tuvo una o mas rondas previas de mejoras sobre el mismo sistema (no es la primera entrega), y la ronda nueva reutiliza patrones de UI/AJAX/servicios ya construidos en rondas anteriores del MISMO proyecto (no solo de otros proyectos), aplicar un descuento adicional sobre la banda M ya ajustada por reutilizacion generica: usar el **piso** del rango de "Modificacion sobre modulo existente" en vez de la mediana, incluso para lo que aparente ser una "pantalla nueva" (si esa pantalla nueva reutiliza AJAX/servicios/patrones visuales ya existentes en el mismo repo, no es una pantalla nueva desde cero a efectos de esfuerzo). El cierre de labipac SESION 3 (2026-07-08) confirmo ratio PERT-contingencia/real 6.84x y formula/real 2.76x — muy cercano al record de vinosefue — pese a que la banda M ya habia sido ajustada a la baja (0.67-0.76 del ratio M/mediana) por reutilizacion documentada. La correccion por reutilizacion simple no fue suficiente; hace falta un segundo ajuste cuando es ademas una ronda repetida sobre el mismo proyecto.

## Planes de mantenimiento anual (OlvidataSoft — servidor a cargo del proveedor)

Incluir siempre en el presupuesto como linea separada post-desarrollo. El plan corresponde al servicio continuo del servidor y soporte, NO es parte del costo de desarrollo.

**Vigente desde 2026-07-24** (suba aplicada tras research competitivo — ver `docs/analisis-pricing-2026-07.md` si existe, o el historial de la sesion que la evaluo). Reemplaza la tabla anterior (250/300/400/750).

| Plan     | Tablas BD        | USD/año | Incluye                                                  |
|----------|------------------|---------|----------------------------------------------------------|
| STARTER  | 1 – 5            | 300     | 1 admin, soporte email, actualizaciones de seguridad     |
| PRO      | 6 – 15           | 400     | Hasta 2 usuarios, soporte WhatsApp, 1 ronda de ajuste    |
| PREMIUM  | 16 – 30          | 500     | Hasta 3 usuarios, soporte prioritario, 2 rondas ajuste   |
| SCALE    | 31+              | 850     | Hasta 10 sesiones, usuarios ilimitados, 3 rondas ajuste  |

**Regla de usuarios vigente desde 2026-08-27 (reemplaza el cobro por usuario adicional dentro de este rango):** el "Hasta N usuarios" de cada plan (STARTER/PRO/PREMIUM) es orientativo, no un tope que dispare cobro extra — **no se cobra usuario adicional hasta que el total de usuarios del cliente supere los 10**. El plan sigue determinandose por cantidad de tablas (tabla de arriba), no por usuarios; los usuarios solo entran a upsell mas alla de ese piso de 10. Ejemplo: un cliente con 4 o 6 usuarios en plan PREMIUM (16-30 tablas) paga PREMIUM sin cargo adicional por usuario — el cargo de "usuario adicional" solo aplica desde el usuario 11 en adelante, en cualquier plan.

Upsells vigentes (fuera del alcance de la formula de Build, ver seccion "Extras opcionales" para lo que sí se calcula con `M x $16.80`): usuario adicional **desde el usuario 11** USD 125/año c/u, módulo nuevo desde USD 250. Reflejado en `src/pages/precios.astro` del sitio (`C:\Sistemas\olvidatasoft-new`) — actualizar ese archivo si la regla de 10 usuarios se traslada al sitio publico.

Reglas de aplicacion:
- Determinar el plan según la cantidad de tablas del sistema entregado (sigue sin depender de la cantidad de usuarios, salvo que se supere el piso de 10 — ver regla de usuarios arriba).
- Presentar el costo de desarrollo y el mantenimiento anual como dos lineas separadas en el presupuesto.
- Aclarar al cliente que el mantenimiento cubre hosting, seguridad y soporte — no cubre cambios funcionales nuevos.
- Los extras (usuario adicional mas alla de 10, módulo nuevo, etc.) se cotizan aparte y se suman al plan base si el cliente los requiere.

## Extras opcionales (vigente 2026)

Precios calculados con formula vigente (M x $16.80). Referencia a tasa USD 35/h con contingencia 20%:

| Extra                        | Precio    | M equiv. | Validez calibracion                                       |
|------------------------------|-----------|----------|-----------------------------------------------------------|
| Usuario adicional (desde el usuario 11) | USD 125/año | —      | Costo de servicio, no de desarrollo. Sin cargo hasta el usuario 10 (ver regla de usuarios en "Planes de mantenimiento anual"). |
| Modulo nuevo                 | USD 75+   | 4 h+     | ABM intermedio minimo M=4-7h = USD 75-135. Cotizar por complejidad. |
| UI personalizada             | USD 40    | ~2 h     | CSS/theming basico. Razonable.                            |
| Optimizacion de performance  | USD 60    | ~3 h     | Aceptable para un pase acotado de queries + carga.        |
| Ronda de ajuste extra        | USD 40    | ~2 h     | Cubre hasta 4 ajustes puntuales (0.5h c/u). Justo.        |
| Backup automatizado mensual  | USD 80/año | —      | Costo de infraestructura. OK.                             |

## Formato de entrega al cliente

**Estructura y estilo del documento (obligatorio, vigente Julio 2026):** ver `31-formato-documento-cliente.instructions.md` — define encabezado con marca, orden de secciones (`Sobre el sistema` → `Como funciona... paso a paso` cuando aplique → `Rol de usuario` → seccion de inversion → `Que incluye`/`Que no incluye` → `Lo que necesitamos de tu parte` → `Condiciones comerciales` → pie de firma), tono de voseo y convenciones de tablas/italica. Ese formato define **estilo y estructura**; el contenido de precios descripto en esta seccion (Etapa 1/Etapa 2/Tokens IA/Mantenimiento) no cambia.

- Documento simple, sin jerga tecnica
- Agrupado por area funcional (no por capa tecnica)
- Incluir tabla: Area | USD (las horas son internas — no se exponen al cliente)
- Incluir seccion Que esta incluido y Que NO esta incluido
- Dividir todo presupuesto en dos etapas: Etapa 1 (MVP — el minimo que permite al cliente operar el negocio) y Etapa 2 (resto del alcance). Cada etapa con su tabla Area | USD y subtotal; el total del proyecto es la suma de ambas.
- El cargo de Tokens IA (25% del total presupuestado, Etapa 1 + Etapa 2) se calcula sobre el subtotal de lista y se **distribuye dentro del precio de cada modulo** (factor constante x1.25 sobre el precio de lista de cada item/area funcional, ver "Cargo por uso de tokens IA" abajo) — NUNCA se muestra como linea separada en el documento de presupuesto cliente (regla invertida 2026-08-20). El desglose completo (precio de lista, Tokens IA, precio ya distribuido) queda documentado en la memoria interna 4-presupuestador.md, que si expone el detalle interno.
- Condiciones estandar: 50% al inicio / 50% a la entrega de cada etapa
- No incluir clausula de validez de la oferta (regla vigente Junio 2026; reemplaza la "validez 30 dias" usada hasta KOI)

## Exclusiones fijas (siempre aplicar salvo excepcion documentada)

- Migracion de datos desde sistema anterior
- Configuracion y costo del servidor / hosting
- Facturacion electronica AFIP / ARCA
- Aplicacion movil (iOS / Android)
- Integracion con hardware externo
- Cambios de alcance posteriores al inicio (se presupuestan por separado)

## Modelo de facturacion (Junio 2026)

Objetivo: cobrar USD 35/h sobre horas reales de desarrollo con IA asistida, con contingencia temporal del 20%.

Formula vigente:
  Horas facturables por modulo = (M / 2.5) x 1.20
  Costo modulo = Horas facturables x USD 35
  Simplificado: Costo = M x 0.48 x $35 = M x $16.80

- M es el valor "caso mas probable" del PERT (no el PERT calculado, no el P).
- El factor 2.5 representa la eficiencia IA calibrada sobre cierres reales (ShowroomGriffin, Ganaderia).
- El 20% de contingencia cubre reentregas, iteraciones menores y desvios de estimacion.
- No aplicar contingencia adicional sobre la formula: el 20% ya la absorbe.
- Excepcion: riesgo extremo documentado (integracion sin precedente, migracion de datos) puede sumarse justificado.

Cargo por uso de tokens IA (vigente Julio 2026, porcentaje actualizado 2026-07-24, forma de exposicion cambiada 2026-08-20):
- Todo presupuesto de proyecto suma un cargo por uso de tokens IA equivalente al **25% del total presupuestado** (Subtotal Etapa 1 + Subtotal Etapa 2, sin incluir mantenimiento anual). Formula: Tokens IA = (Subtotal Etapa 1 + Subtotal Etapa 2) x 0.25.
- Se calcula una unica vez sobre el total del proyecto (no por modulo, no por etapa por separado) — el CALCULO sigue siendo a nivel proyecto, lo que cambia es como se EXPONE (ver punto siguiente).
- **Distribuido dentro del precio de cada modulo — NUNCA se muestra como linea separada al cliente** (regla invertida 2026-08-20, reemplaza la regla anterior de linea explicita). Como el cargo es siempre 25% del subtotal de lista, el factor de distribucion es CONSTANTE: `Precio_modulo_mostrado_al_cliente = Precio_modulo_lista x 1.25`, aplicado a cada item/area funcional del documento cliente. La suma de los precios de modulo ya distribuidos da el mismo total que antes (Subtotal_lista + Tokens_IA) — no cambia el total del proyecto, cambia como se ve desglosado.
- Esta distribucion es independiente del descuento de expansion agresiva (seccion de abajo): el descuento sigue calculandose sobre Subtotal_lista SIN tokens IA y sigue mostrandose como su propia linea/nota cuando aplica ("Descuento por eficiencia de desarrollo") — solo Tokens IA se pliega dentro de los modulos, no el descuento.
- El calculo completo (Subtotal_lista, Tokens_IA, factor 1.25, precio de lista de cada modulo Y precio ya distribuido que ve el cliente) debe quedar documentado en la memoria interna `4-presupuestador.md` — el cliente ve solo el precio final por modulo, el desglose interno (cuanto es desarrollo puro vs. cuanto es la porcion de Tokens IA) sigue siendo dato de trazabilidad del estudio, no se oculta internamente, solo no se expone al cliente.
- No aplica a iteraciones evolutivas menores a 4 h facturables, salvo indicacion contraria.
- Regla anterior (vigente hasta 2026-08-20, ya no aplica): linea explicita y separada "Tokens IA" en la seccion "Total del proyecto", sin prorratear en los modulos.
- Regla anterior a esa (vigente 2026-07-03 a 2026-07-24, ya no aplica): 10% del total presupuestado.
- Regla anterior a esa (vigente hasta Junio 2026, ya no aplica): cargo fijo de USD 100 por proyecto.

## Costo interno de IA por consumo de motores de pensamiento (solo estudio — vigente desde 2026-08-15)

Distinto del cargo "Tokens IA" de arriba (25% del subtotal, visible al cliente como linea propia). Esto es un dato **exclusivamente interno**: el costo sombra proyectado de consumo real de IA para producir el modulo, dado que Implementador y QA corren por defecto en Claude Opus 5 desde 2026-08-14 (`model: opus` en `.claude/agents/agentes-ia-implementador.md` y `agentes-ia-qa.md`). Nunca aparece desglosado en `presupuesto-cliente.md`; vive solo en `4-presupuestador.md`.

**Nota de facturacion real:** el estudio paga Claude Code via suscripcion Stripe (`billingType: stripe_subscription`, confirmado en la cuenta), no por token via API. Este calculo es un "costo sombra" a precio de lista de la API Claude — no es un gasto variable que se factura mes a mes. Sirve para (a) verificar que el precio final de cada modulo cubre el costo real de produccion asistida por IA a pesar del cambio a Opus, y (b) tener visibilidad para decidir en el futuro si conviene migrar a facturacion API o cambiar de plan segun el volumen.

Precios de referencia (API Claude, cacheados 2026-06-24, ver `shared/models.md` del skill `claude-api` para vigencia):
- Claude Opus 5 (`claude-opus-5`): USD 5.00 / MTok input, USD 25.00 / MTok output.
- Claude Sonnet 5 (`claude-sonnet-5`): USD 3.00 / MTok input (intro USD 2.00 hasta 2026-08-31), USD 15.00 / MTok output (intro USD 10.00).

**Formula (por modulo):**
```
Costo_IA_modulo = Horas_facturables_modulo x tarifa_Opus_USD_hora
```
donde `Horas_facturables_modulo` es el mismo valor ya calculado para precio (`M / 2.5 x 1.20`) — se asume que practicamente todo ese tiempo de esfuerzo asistido por IA a nivel modulo corresponde a Implementador + QA (Opus), ya que Discovery/Analisis/Diseño/Arquitectura/Presupuesto/Documentacion son sesiones conversacionales cortas (Ask-mode, Sonnet) que ocurren una vez por proyecto, no por modulo.

**Overhead fijo por proyecto (una sola vez, no por modulo):**
```
Costo_IA_overhead_proyecto = Horas_Ask_mode_estimadas x tarifa_Sonnet_USD_hora
```
`Horas_Ask_mode_estimadas` = 4 h como placeholder (cubre Discovery + Analisis + Diseño + Arquitectura + Presupuesto + Documentacion combinados para un proyecto de complejidad tipica). Ajustar si el proyecto tuvo un discovery inusualmente largo o corto.

**Tarifas placeholder (sin calibrar con datos reales todavia — ver "Calibracion" abajo):**
- `tarifa_Opus_USD_hora` = USD 4/hora (rango estimado 3-10 USD/h). Estimacion basada en precio de lista + supuesto de throughput tipico de una sesion agentic con muchas llamadas a herramientas (thinking on por defecto en Opus 5, effort alto/xhigh), NO en datos medidos.
- `tarifa_Sonnet_USD_hora` = USD 1/hora (rango estimado 0.5-1.5 USD/h). Sesiones Ask-mode conversacionales, contexto mas acotado.

**Como se aplica al precio final (folded, sin linea visible nueva):**
1. Calcular `Costo_IA_modulo` para cada modulo y `Costo_IA_overhead_proyecto` una vez por proyecto.
2. Si `Costo_IA_modulo` supera el 15% del precio de lista del modulo (`M x $16.80`), sumar la diferencia directamente al precio final de ESE modulo especifico (ya calculado, sin generar linea nueva ni desglose visible al cliente) — el 25% de Tokens IA no alcanza a cubrir el costo real proyectado y el numero final debe absorberlo.
3. Si `Costo_IA_modulo` esta por debajo del 15%, no ajustar nada: el 25% de Tokens IA ya lo cubre.
4. Documentar el calculo completo (Costo_IA por modulo, overhead, umbral, ajuste aplicado si hubo) en `4-presupuestador.md`, seccion interna — nunca en `presupuesto-cliente.md`.

**Calibracion (reemplazar el placeholder con datos reales):** al cierre de cada sprint donde Implementador y/o QA corrieron como subagente, capturar el costo real de la sesion (comando `/cost` de Claude Code, o el reporte de uso de la cuenta) y registrarlo junto a las horas reales en `4-presupuestador.md`. Cuando haya 3+ cierres con dato real, recalcular `tarifa_Opus_USD_hora` y `tarifa_Sonnet_USD_hora` como la mediana observada (mismo metodo que la calibracion del factor de eficiencia 2.5), y reemplazar el placeholder de esta seccion.

## Descuento de expansion agresiva por reutilizacion cross-proyecto (vigente desde 2026-07-29)

Decision de negocio: la ganancia ya no se busca en el margen del Build, se busca en volumen de clientes nuevos x mantenimiento anual compuesto en el tiempo. El costo real de produccion de un Build ya es bajo cuando el proyecto reutiliza patrones ya construidos en otros proyectos (la formula M x $16.80 ya lo refleja via M chico en la seccion "Modificacion sobre modulo existente" de arriba). Esta seccion agrega un descuento ADICIONAL sobre el precio de lista para acelerar el cierre de clientes nuevos, financiado por ese ahorro de costo real — no es un descuento arbitrario.

**Cuando aplica:** solo a presupuestos de Build inicial para cliente NUEVO (o rewrite completo de un sistema de terceros). NO aplica a Mantenimiento anual, Extras opcionales (usuario adicional, modulo nuevo post-entrega, UI, performance, ronda de ajuste, backup) ni a Merge sobre sistema propio ya entregado — esos se cotizan siempre a precio de lista, sin descuento: ahi esta el margen real del negocio.

**Como calcular el ratio de reutilizacion (R):** en el Paso 4 del presupuestador, despues de clasificar cada modulo/item con la regla de granularidad vigente:

`R = (Σ M de items clasificados como reutilizacion de un patron ya construido, en este proyecto o en otro del historial) / (Σ M total del proyecto)`

Un item cuenta como "reutilizacion" si esta anclado en alguna fila de "Modificacion sobre modulo existente" (campo simple, regla de negocio, ledger/cuenta corriente reutilizando patron, ABM reutilizando servicios, etc.) o si el disenador-funcional/arquitecto-mvc documento en `docs/*/definiciones/` que el modulo replica un diseño/codigo ya entregado en otro proyecto (regla de reutilizacion cross-proyecto de `CLAUDE.md`). Un item cuenta como "nuevo" si usa los rangos de la tabla principal de modulos (ABM nuevo, financiero nuevo, workflow nuevo sin precedente).

| Tier | Ratio R | Descuento sobre Subtotal Etapa1+Etapa2 (precio de lista) |
|---|---|---|
| 1 — Expansion Agresiva | R >= 70% | 30% |
| 2 — Expansion Moderada | 40% <= R < 70% | 15% |
| 3 — Estandar | R < 40% | 0% (precio de lista sin cambios) |

### Descuento por volumen del proyecto (vigente desde 2026-08-19)

Segundo eje de descuento, independiente del ratio de reutilizacion R: a mayor volumen del proyecto (Subtotal_lista, precio de lista antes de cualquier descuento), menor el costo efectivo del total. Ataca un caso que el descuento por reutilizacion no cubre: **proyectos grandes con reuso bajo** (rubro nuevo, sin patron previo en el estudio) — hoy cotizan a precio de lista completo pese a ser el ticket mas valioso, sin ningun incentivo de cierre.

Research de mercado (estudios/consultoras chicas, no enterprise): el estandar para bloques de horas/retainers es 10-15% de descuento por volumen; descuentos de 20-40% son de otra escala de negocio (contratos enterprise USD 15K-100K+/mes) y no aplican al perfil de Olvidata (proyectos historicos USD 280-2.250, mayoria en USD 300-1.000).

| Tier | Subtotal_lista | Descuento volumen |
|---|---|---:|
| V0 — Estandar | < USD 600 | 0% |
| V1 — Volumen | USD 600 – 1.200 | 5% |
| V2 — Volumen alto | USD 1.200 – 2.000 | 10% |
| V3 — Volumen mayor | USD 2.000+ | 15% |

Los cortes estan calibrados para que la mayoria de los proyectos tipicos actuales (USD 300-1.000) caigan en V0/V1 — esta regla no toca el grueso del negocio actual, solo empieza a pesar en la cola de proyectos grandes.

**Mismo alcance que el descuento por reutilizacion:** solo Build inicial de cliente NUEVO (o rewrite completo). No aplica a Mantenimiento, Extras opcionales ni Merge sobre sistema propio ya entregado.

**Como combina con el descuento por reutilizacion — MAX, no suma:** `factor_tier = MAX(factor_tier_reutilizacion, factor_tier_volumen)`. No se suman los dos descuentos. Motivo (verificado contra el dataset real: vinosefue, Ganaderia-equivalente, La Platense-equivalente): en los proyectos con reuso alto (Tier 1 de reutilizacion, 30%) que son el caso tipico de Olvidata, sumar el descuento de volumen con un tope global solo agregaba +5 puntos marginales sobre el 30% ya vigente — ganancia insuficiente para justificar la complejidad de explicar dos descuentos + un tope. MAX es mas simple y no premia doblemente lo que ya esta premiado por reuso: el tier de volumen solo entra a jugar cuando el proyecto es grande pero **no** tiene reuso alto, que es el hueco real que esta regla busca cubrir. Con MAX, el descuento combinado nunca supera el 30% ya vigente hoy — el piso absoluto de USD 280 no corre ningun riesgo nuevo (el umbral minimo de V1, USD 600, ya deja margen de sobra frente al piso incluso con el maximo descuento combinado).

**Gatillo:** el mismo tablero de 5 señales de ciclos economicos que ya condiciona el descuento por reutilizacion (ver "Gatillo con el tablero de ciclos economicos" abajo) — es la misma decision de fondo (bajar precio para acelerar cierre mientras el contexto lo permite), no tiene gatillo independiente. Si el tablero pasa a rojo, se pausan ambos ejes de descuento a la vez.

**Formula de aplicacion (orden obligatorio, no alterar):**
1. `Subtotal_lista = Σ (M_item x $16.80)` — igual que hoy, sin cambios.
2. `Tokens_IA = Subtotal_lista x 0.25` — se calcula SIEMPRE sobre el subtotal de lista SIN descontar. Cubre costo real de infraestructura IA; nunca se resigna este cargo, sea cual sea el tier.
3. Calcular `factor_tier_reutilizacion` (segun R, tabla de arriba) y `factor_tier_volumen` (segun Subtotal_lista, tabla de arriba). `factor_tier = MAX(factor_tier_reutilizacion, factor_tier_volumen)`.
4. `Descuento_expansion = Subtotal_lista x factor_tier`.
5. `Precio_final_Build = (Subtotal_lista - Descuento_expansion) + Tokens_IA`.
6. **Piso absoluto:** `Precio_final_Build = MAX(Precio_final_Build, USD 280)`. Nunca cotizar Build por debajo de este piso, sea cual sea el resultado de la formula — protege la percepcion de valor ("barato = poco serio").

**Como se muestra al cliente:** nunca usar la palabra "cross-proyecto" ni mencionar otros clientes/proyectos en el documento entregado. Mostrar el descuento como linea propia en la seccion de precio, rotulada "Descuento por eficiencia de desarrollo" u "Optimizacion de desarrollo (componentes ya probados)". Sigue el formato de `31-formato-documento-cliente.instructions.md`.

**Gatillo con el tablero de ciclos economicos (verificar antes de cotizar):** esta agresividad aplica MIENTRAS el tablero de 5 señales (riesgo pais, brecha cambiaria, atraso cambiario, inflacion, ruido electoral) este en verde o amarillo (ventana de consolidacion vigente desde jul-2026). Checkpoint duro: octubre 2027 (eleccion presidencial) — revisar el tablero antes de esa fecha y en cualquier presupuesto nuevo. Si el tablero pasa a rojo: pausar Tier 1 y Tier 2 de inmediato, todo presupuesto nuevo cae a Tier 3 sin excepcion; no se revisan retroactivamente los contratos/mantenimientos ya firmados con descuento vigente al momento del cierre. Motivo: en ventana de riesgo cambiario alto, bajar precio en pesos convertidos a USD del dia erosiona margen real mas rapido de lo que el volumen nuevo puede compensar.

**Supuesto mas fragil de esta politica (declarar siempre, no ocultar):** asume que la tasa de cierre sube proporcional a la baja de precio y que la capacidad de onboarding de Joaquin (developer solista, delega puntualmente a Matias) aguanta el volumen nuevo sin degradar calidad/tiempos de entrega. Si la tasa de cierre no responde al precio, o si el onboarding se satura, el descuento agresivo solo reduce margen sin acelerar el hito 2028. Revisar cada trimestre: ¿subio la cantidad de Builds cerrados por mes desde que se aplica el descuento? Si no, pausar y volver a Tier 3.

Patron confirmado de ratio PERT / real en proyectos con IA asistida:

| Proyecto | Horas PERT | Horas reales | Ratio PERT/real | Horas formula (M/2.5x1.2) | Ratio formula/real |
|---|---:|---:|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x | ~40.6 h | 1.6x |
| Ganaderia (CIERRE REAL 2026-07-03) | 101.0 h | 20 h (total proyecto, Etapa 1 + Etapa 2, definitivo) | 5.05x | ~38.6 h | 1.93x |
| contadores-bma-conversor | ~13.1 h (PERT) | 8 h | 1.6x | ~5.3 h (formula) | 0.66x |
| vinosefue — sprint compras proveedor (CIERRE REAL 2026-07-03, reconstruccion retroactiva, sin presupuesto formal previo) | 28.27 h | 4 h (total del lote, sin desglose por item) | **7.07x — record del dataset** | ~11.42 h | **2.86x — record del dataset** |
| labipac — SESION 3 (M7+M8+M9 + 3 fixes post-QA, CIERRE REAL 2026-07-08) | 13.69 h | 2.0 h (total, incluye 3 fixes post-QA) | **6.84x — segundo lugar del dataset** | 5.52 h | **2.76x — segundo lugar del dataset** |
| vinosefue — feature filtro categoria en export catalogo (CIERRE REAL 2026-07-13, reconstruccion ya anclada en "iteracion evolutiva") | 6.55 h | 1.5 h (total, incluye deploy en produccion) | **4.37x — el mas bajo del grupo "evolutivo"** | 2.76 h | **1.84x — el mas bajo del grupo "evolutivo"** |

Ganaderia reemplaza su dato previo de "~30 h total" (proyeccion) por el cierre real de 20 h — ahora el ratio PERT/real (5.05x) es el mas alto del dataset y el ratio formula/real (1.93x) es el segundo mas alto. El dato empuja levemente el factor de eficiencia hacia arriba de 2.5, pero no se ajusta el factor unilateralmente por este cierre (ver regla debajo).

El ratio formula/real de 0.66x-1.93x confirma que la contingencia del 20% es en general un buffer razonable, aunque el rango se amplio con el cierre de Ganaderia: sigue sin inflar exageradamente frente a otros cierres, pero ya no es un rango angosto de 1.3x-1.6x.

Excepcion observada (contadores-bma-conversor): ratio formula/real = 0.66x. En este proyecto
la formula subbilo porque el real (8 h) superó las horas facturables calculadas (5.3 h).
Causa: el deploy inicial fue subestimado (1 h estimado → 3 h real) y el proyecto se cobró
sobre horas reales retroactivas, no sobre M estimado. No afecta la validez de la formula para
proyectos futuros donde se aplica correctamente desde el inicio con M real.

Factor de calibracion 2.5: fijo hasta que Energy Nutrition cierre. Recalibrar con ese cierre. El cierre real de Ganaderia (ratio PERT-contingencia/real 5.05x, el mas alto del dataset) es evidencia adicional a favor de subir el factor por encima de 2.5 en esa recalibracion futura.

**Tendencia confirmada por 2 cierres consecutivos (vinosefue 2026-07-13, y en menor medida labipac 2026-07-08):** cuando la reconstruccion PERT se ancla desde el arranque en "iteracion evolutiva / reutilizacion de patron existente" (en vez de partir de rangos de "modulo nuevo" y corregir despues), el ratio de sobreestimacion baja de forma consistente — de 7.07x/2.86x (vinosefue compras proveedor, la reconstruccion que origino la regla) a 6.84x/2.76x (labipac) a **4.37x/1.84x (vinosefue categoria, el mas bajo hasta ahora)**. La regla de granularidad sigue siendo correcta y vale la pena seguir aplicandola de entrada, no como correccion posterior — cada iteracion de calibracion la esta acercando mas a 1.0x.

## Alerta de subestimacion sistematica en deploy inicial (Junio 2026 — contadores-bma-conversor)

El deploy inicial en hosting compartido (Ferozo) fue subestimado en 3x: M estimado 1 h, real 3 h.
Causas: configuracion de subdominio en panel del hosting, mecanismo FTPS + vendor.zip no estandar,
iteraciones de .htaccess para PHP 8.3 en LiteSpeed, verificacion end-to-end en produccion.

Regla derivada: para cualquier primer deploy en hosting compartido (Ferozo u otro panel), usar
M minimo = 2 h. Si el mecanismo de deploy es no estandar (FTP + zip extraction, Passenger WSGI,
configuraciones PHP especificas), usar M = 3 h. El rango "Ajuste puntual 0.5-1 h" NO aplica
a primer deploy en servidor nuevo — usar la fila "Deploy inicial hosting compartido" de la tabla.

## Alerta de sobreestimacion sistematica confirmada (Junio 2026, actualizada Julio 2026)

Los proyectos cerrados muestran el mismo patron: las estimaciones PERT sin anclaje historico previo producen entre 3x y 6.7x las horas reales.

| Proyecto | Horas estimadas | Horas reales | Ratio estimado/real |
|---|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x |
| Ganaderia (CIERRE REAL 2026-07-03) | 101.0 h | 20 h (total proyecto Etapa 1 + Etapa 2, definitivo) | 5.05x |

Nota: el dato de Ganaderia reemplaza la fila anterior ("6.7x Etapa 1 / 3.4x total proyectado") — esa era una proyeccion parcial antes del cierre. El 5.05x es ahora el dato definitivo y el ratio mas alto confirmado en el dataset con cierre real.

Regla de recalibracion obligatoria derivada de este patron:
- El M (caso mas probable) debe anclarse en la mediana historica de proyectos similares ANTES de estimar.
- Los proyectos de 8-11 modulos de complejidad media-alta cierran en el rango de 20 a 30 horas reales totales (actualizado 2026-07-03: Ganaderia cerro con 8 modulos en 20 h reales, el piso mas bajo confirmado del rango — ver cierre real abajo).
- Para proyectos de 16-27 modulos de complejidad media, el rango real historico es 30-50 horas totales.
- No proyectar horas basandose unicamente en la suma de O/M/P sin comparar primero el total proyectado contra estos cierres reales.

## Notas de calibracion

- Parametros calibrados en base a proyectos reales cerrados y presupuestados desde 2025.
- Total combinado historico base: 175 horas - USD 2.450 - tasa efectiva historica USD 14/h.
- **Junio 2026 — primer ciclo real a tasa nueva:** iteracion evolutiva Delicias Naturales, 4 h reales, USD 160 a USD 40/h. Ratio estimado/real: 1.0 (estimacion exacta).
- **2026-06-03:** Relevamiento de Stock (Delicias Naturales), ABM intermedio. 5.5 h reales a USD 40/h. Dataset ABM intermedio: 5h, 5.5h, 6.5h, 7h. Rango confirmado 5-7h, mediana 6h.
- **2026-06-08:** Contingencia temporal del 20% incorporada a la formula. Tasa ajustada a USD 35/h (definitiva). Formula vigente: M/2.5 x 1.20 x $35 = M x $16.80. Energy Nutrition v6.1 calculado bajo esta formula.
- **2026-06-29:** contadores-bma-conversor cerrado. 8 h reales, 3 modulos (PHP + parser Excel + deploy). Datos incorporados al dataset. Desvio critico: deploy inicial 1 h estimado → 3 h real. Nueva fila en tabla de rangos: "Deploy inicial hosting compartido M=2-3 h". Nueva fila: "Parser Excel propietario M=4-6 h". UI pantalla unica: confirma M=1 h (piso de ABM simple). Proyecto cobrado sobre horas reales retroactivas con descuento referido 15% → USD 199.
- **2026-07-03: Ganaderia cerrado (CIERRE REAL, reemplaza la proyeccion previa de ~30 h).** Total real Etapa 1 + Etapa 2 = 20 h, 8 modulos funcionales (catalogos, usuarios, stock, ingresos con facturacion/cuotas, rechazos/regularizacion/job diario, egresos, caja, dashboard). Estimado: 81.5 h base / 101.0 h con contingencia PERT. Ratio PERT-contingencia/real = 5.05x (record del dataset, en horas). Ratio formula-vigente (M/2.5x1.20)/real = 1.93x (segundo mas alto del dataset, supera a ShowroomGriffin 1.6x).
  **Precio comercial real (corregido el mismo dia):** USD 950 facturados (no USD 1.212, que era solo la estimacion interna PERT × USD 12/h, nunca cobrada tal cual) — incluye 15% de descuento por referido ya aplicado (mismo tipo de descuento que contadores-bma-conversor) + el primer año del plan de mantenimiento (USD 300) empaquetado dentro del precio. Desarrollo puro implicito: USD 650 → tasa efectiva real ≈ **USD 32.5/h, muy cercana al objetivo USD 35/h** (equivalente al modelo nuevo 20h×$35=$700 quedo solo USD 50 por debajo). Plan anual continuo desde el 2do año: USD 300/año.
  **Ganaderia queda fijado como proyecto de referencia comercial** para presupuestos futuros de alcance funcional comparable (8-11 modulos, mezcla ABM+workflow+financiero, 2 migraciones EF): ancla la relacion horas-reales/funcionalidad-entregada (20 h ≈ 8 modulos de esa complejidad), no las 101.0 h PERT originales que sobreestimaron 5.05x. Ver detalle completo en `/docs/ganaderia/definiciones/4-presupuestador.md`. El factor de eficiencia 2.5 de la formula vigente sigue sin recalibrarse (atado al cierre de Energy Nutrition), pero el ratio de horas (1.93x-5.05x) sigue siendo evidencia a favor de subirlo — la tarifa por hora real, en cambio, ya valida el objetivo USD 35/h una vez separados mantenimiento y descuento.
- **2026-07-03: vinosefue — sprint "Compras al proveedor: armado manual y cuenta corriente" cerrado (CIERRE REAL, sin presupuesto formal — el cliente/owner implemento directamente).** 4 h reales totales para 8 items (2 fixes + 3 features + 2 ajustes post-QA + simplificacion de 2 reportes). Reconstruccion retroactiva PERT: 23.8 h base (M) / 28.27 h con contingencia. **Ratio PERT-contingencia/real = 7.07x (nuevo record del dataset, supera a Ganaderia 5.05x).** Ratio formula-vigente/real = 2.86x (nuevo record, supera a Ganaderia 1.93x). Causa principal identificada: este lote es una **iteracion evolutiva que reutiliza patrones ya resueltos en el mismo repo** (ledger `CuentaCorriente`/`MovimientoCC` de Cliente replicado para Proveedor, `AdjuntoService`, `MetodoPago` ya existentes) — clasificarlo con los rangos de "modulo nuevo" (ABM complejo, Financiero) sobreestima sistematicamente. Se agregaron 3 filas nuevas a "Modificacion sobre modulo existente" (refactor de vinculo/FK + migracion, ledger reutilizando patron existente, ABM manual reutilizando servicios existentes) y una regla de granularidad obligatoria: verificar reutilizacion de patron ya resuelto ANTES de clasificar como modulo nuevo. El real no vino desglosado por item (solo el total de 4h) — el reparto por item en `/docs/vinosefue/definiciones/4-presupuestador.md` es una aproximacion proporcional, no un dato medido.
- **2026-07-08: labipac — SESION 3 cerrada (3 mejoras: Unidad/PrecioPorUnidad en Perfiles con simplificacion de F-001, Carga masiva + alta rapida, fix ancho columna PDF, mas 3 fixes de una ronda posterior de QA manual — CIERRE REAL).** Presupuestado en 11.5 h M base / 13.69 h con contingencia (USD 212.52 con Tokens IA, aprobado por el cliente). Real: **2.0 h totales** (incluye los 3 fixes post-QA). **Ratio PERT-contingencia/real = 6.84x, ratio formula-vigente/real = 2.76x — segundo lugar del dataset, muy cerca del record de vinosefue (7.07x/2.86x).** Confirma el mismo patron: es la 3ra ronda de mejoras sobre el mismo proyecto (rondas previas: presupuesto inicial 2026-06-13, ampliacion FABA 2026-06-23), y la banda M de esta ronda ya habia sido ajustada a la baja por reutilizacion (ratio M/mediana 0.67-0.76 con justificacion documentada) — aun asi cerro con una sobreestimacion casi tan alta como vinosefue. Diferencia clave: no es la primera vez que se reutiliza un patron generico de otro proyecto, sino que se reutilizan patrones **construidos en rondas previas del mismo proyecto** (card AJAX de IVA de F-002, endpoint `GetPrecioItem`, `CreateAsync` de servicios ya existentes). Se agrego la regla "segunda/tercera ronda sobre el mismo modulo": cuando aplica esta señal, usar el PISO del rango de "Modificacion sobre modulo existente" en vez de la mediana, incluso si el item parece una pantalla nueva. Regla incorporada tambien al metodo de estimacion del agente presupuestador (`presupuesto-mvc.agent.md`, Paso 0 y Paso 4).
- **2026-07-29:** decision de negocio — expansion agresiva. Se agrega la seccion "Descuento de expansion agresiva por reutilizacion cross-proyecto": tiers de descuento (30%/15%/0%) sobre Subtotal Etapa1+Etapa2 segun ratio de reutilizacion R, piso absoluto USD 280, Tokens IA siempre sobre subtotal sin descontar. Condicionado al tablero de ciclos economicos (checkpoint octubre 2027). No aplica a mantenimiento, extras ni Merge.
- **2026-08-19:** agregado segundo eje de descuento — "Descuento por volumen del proyecto" (tiers V0-V3, 0%/5%/10%/15% segun Subtotal_lista: <600/600-1200/1200-2000/2000+). Research previo via agente `olvidata-ceo`: estandar de mercado para estudios chicos es 10-15% por volumen (no 20-40%, eso es enterprise). Combina con el descuento por reutilizacion via `MAX(factor_tier_reutilizacion, factor_tier_volumen)`, nunca suma — verificado contra el dataset real que sumar solo aportaba +5 puntos marginales sobre proyectos ya en Tier 1 de reutilizacion (30%), insuficiente para justificar la complejidad. Mismo alcance (solo Build inicial cliente nuevo) y mismo gatillo (tablero de ciclos economicos) que el descuento por reutilizacion — se pausan juntos si el tablero pasa a rojo.
- **2026-08-21:** primer caso real donde el eje de volumen (no el de reutilizacion) dispara el descuento — `cma-centro-medico` (sistema multi-sede de gestion de pacientes, ver `/docs/cma-centro-medico/definiciones/4-presupuestador.md`). R=2% (Tier 3, 0%) pero Subtotal_lista=USD 840 cae en Tier V1 (5%) → `factor_tier = MAX(0%, 5%) = 5%`. Confirma en la practica el caso de uso que motivo agregar el eje de volumen (proyecto grande con reuso bajo, rubro sin patron previo en el estudio). Sin cierre real todavia (propuesta pendiente de envio).
- **2026-08-27:** decision de negocio — "no cobrar usuario extra hasta superar los 10 usuarios". Reemplaza el criterio anterior de cobrar usuario adicional apenas se superaba el tope "incluido" de cada plan (2 en PRO, 3 en PREMIUM). Motivo: simplifica la conversacion comercial (no hay que explicar upsells de usuario a clientes chicos-medianos, que es la inmensa mayoria del pipeline actual) y el costo marginal real de un usuario adicional en un sistema ya construido es minimo. El plan se sigue determinando por cantidad de tablas, no por usuarios, hasta ese piso de 10. Aplicado el mismo dia a `peras-del-olmo` (PREMIUM+1 usuario USD 625/año → **PREMIUM sin cargo extra, USD 500/año**, 4 usuarios). Proyectos ya cotizados con upsell de usuario bajo el criterio anterior (`cma-centro-medico`, PRO+3 usuarios USD 775/año con 5 usuarios; `audifonos-bariloche`, YA ENVIADO al lead, PREMIUM+3 usuarios USD 800/año con 6 usuarios) quedan con sus numeros previos salvo que Joaquin pida explicitamente recalcularlos — no se tocan documentos ya enviados ni proyectos no mencionados sin pedido explicito.
- **2026-07-29 (aclaracion sobre objecion de precio en Build ya en Tier 1):** cuando un prospecto en Tier 1 (30% ya aplicado) sigue objetando precio, la palanca recomendada es **regalar el primer año de mantenimiento** (caso por caso, no estructural), NO extender el descuento de Build mas alla del 30% del tier. Motivo: (1) no existe una tabla de "Tier 0" por encima de 30% — inventar un descuento ad hoc rompe el sistema de tiers fijo pensado para cerrar rapido sin negociar caso por caso; (2) el mantenimiento regalado es un costo de UNA SOLA VEZ (se retoma a precio de lista completo desde el año 2), no toca el recurrente compuesto que sostiene el hito 2028 mas alla del año de cierre; (3) hay precedente comercial que funciono: Ganaderia (cierre real 2026-07-03) empaqueto el primer año de mantenimiento (USD 300 en ese momento) dentro del precio total y cerro exitosamente. Aplicado por primera vez bajo esta tabla de precios vigente en la propuesta de ferreteria (borrador 2026-07-25, ajustado 2026-07-29): desarrollo USD 1.485 sin cambios (Tier 1, 30% ya aplicado), mantenimiento PREMIUM año 1 regalado (USD 500), año 2 en adelante a precio de lista USD 500/año. Esto es una **excepcion explicita** a la regla "el mantenimiento nunca lleva descuento" (ver seccion "Descuento de expansion agresiva") — esa regla sigue vigente para descuentos estructurales/permanentes; regalar el año 1 como incentivo de cierre puntual no la contradice porque no es un descuento sobre el precio de lista del plan, es una promocion de arranque caso por caso que no se documenta como nueva fila de la tabla de planes. No usar por default en todo presupuesto — solo cuando haya objecion de precio real y el proyecto ya este en Tier 1.
- **2026-07-29 (tipo de cambio real observado H1 2026, para conversion ARS-USD honesta en seguimiento del hito 2028):** research de dolar blue Argentina, 2026: minimo USD 1 = $1.390 ARS (08/04/2026), maximo $1.570 ARS (28/07/2026), apertura de año $1.530 ARS (02/01/2026). Rango de referencia para convertir cobros en ARS a USD cuando no se tiene el TC exacto del dia de cada pago: **$1.390 - $1.570, promedio aproximado $1.480**. No usar un numero unico falso-preciso (ej. "$1.500 fijo") para reconstruir ingresos historicos en ARS — usar este rango y declarar el supuesto. Fuente: cotizacion-dolar.com.ar / rava.com, consultado 2026-07-29.
- Al referenciar historicos anteriores a Junio 2026, usar las horas como referencia de esfuerzo y recalcular el costo con la tasa vigente de USD 35/h.
- Revisar y actualizar la tasa cada 6 meses o ante cambio de contexto economico.
- La contingencia se aplica una unica vez segun la politica vigente (variable por riesgo 8/15/25 por defecto, o fija del cliente cuando aplique).
- Para proyectos que incluyan migracion de datos, agregar entre 20% y 30% al total como riesgo declarado.
- Facturacion AFIP/ARCA es exclusion estandar salvo excepcion documentada.
- Integraciones externas: ver rangos por tipo en seccion "Rangos de referencia por tipo de modulo".

## Auditoria de inconsistencias — Junio 2026

Detectadas al incorporar Energy Nutrition y definir objetivo USD 35/h. Estado de cada una:

| # | Inconsistencia | Causa | Estado |
|---|---|---|---|
| I-1 | Tasa vigente USD 30/h estaba POR DEBAJO del piso declarado USD 35/h en Energy Nutrition 4b | Tasa bajo de 45→30 sin actualizar el piso | CORREGIDO — tasa vigente = USD 35/h, piso = USD 30/h |
| I-2 | Extras opcionales referenciaban USD 45/h como tasa de validacion | No se actualizo la tabla al bajar la tasa | CORREGIDO — tabla recalculada a USD 35/h |
| I-3 | Rangos de costo por modulo calculados a USD 30/h | Tercera actualizacion de tasa no los sincronizo | CORREGIDO — rangos actualizados a USD 35/h |
| I-4 | Integraciones externas sin rango de referencia en dataset | Ningun proyecto anterior las incluia | CORREGIDO — 4 nuevos tipos de integracion agregados (fuente: EN v4.0, pendiente cierre real) |
| I-5 | Sobreestimacion sistematica detectada pero sin guia de uso para modelo de horas reales | La alerta existia pero no decia que hacer si se cobra por hora real | CORREGIDO — seccion "Modelo de facturacion" con regla de division por 2.5 |
| I-6 | Historial de tasa confuso (14→40→45→30 en mismo mes) sin razon explicita | Calibraciones rapidas sin documentar motivacion | CORREGIDO — historial simplificado en notas de calibracion |
| I-7 | Ganaderia en dataset con tasa USD 12/h, inconsistente con tasas actuales | El documento de ganaderia usa tasa historica del contrato | PENDIENTE — al usar ganaderia como referencia de horas, ignorar la columna USD; recalcular a USD 35/h |
| I-8 | Energy Nutrition sin cierre real, riesgo de usar sus horas como verdad | Proyecto en estado BORRADOR | MITIGADO — EN marcado explicitamente como "sin cierre real" en lista de proyectos y en su memoria |
| I-9 | Metodo PERT no diferencia entre precio fijo y horas reales | El PERT siempre produjo estimaciones de "precio fijo maximo" | MITIGADO — seccion "Modelo de facturacion" documenta la diferencia y la regla de ajuste |