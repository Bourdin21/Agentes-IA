---
description: Parametros base de estimacion y presupuesto. Calibrado sobre proyectos reales de OlvidataSoft.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Parametros de referencia - Proyectos calibrados

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

| Plan     | Tablas BD        | USD/año | Incluye                                                  |
|----------|------------------|---------|----------------------------------------------------------|
| STARTER  | 1 – 5            | 250     | 1 admin, soporte email, actualizaciones de seguridad     |
| PRO      | 6 – 15           | 300     | Hasta 2 usuarios, soporte WhatsApp, 1 ronda de ajuste    |
| PREMIUM  | 16 – 30          | 400     | Hasta 3 usuarios, soporte prioritario, 2 rondas ajuste   |
| SCALE    | 31+              | 750     | Hasta 10 sesiones, usuarios ilimitados, 3 rondas ajuste  |

Reglas de aplicacion:
- Determinar el plan según la cantidad de tablas del sistema entregado.
- Presentar el costo de desarrollo y el mantenimiento anual como dos lineas separadas en el presupuesto.
- Aclarar al cliente que el mantenimiento cubre hosting, seguridad y soporte — no cubre cambios funcionales nuevos.
- Los extras (usuario adicional, módulo nuevo, etc.) se cotizan aparte y se suman al plan base si el cliente los requiere.

## Extras opcionales (vigente 2026)

Precios calculados con formula vigente (M x $16.80). Referencia a tasa USD 35/h con contingencia 20%:

| Extra                        | Precio    | M equiv. | Validez calibracion                                       |
|------------------------------|-----------|----------|-----------------------------------------------------------|
| Usuario adicional            | USD 100/año | —      | Costo de servicio, no de desarrollo. OK.                  |
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
- El cargo de Tokens IA (10% del total presupuestado, Etapa 1 + Etapa 2) debe mostrarse como ITEM INDIVIDUAL en el documento de presupuesto cliente (linea separada, visible, en la seccion "Total del proyecto") y tambien en la memoria interna 4-presupuestador.md. No prorratear en los modulos.
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

Cargo por uso de tokens IA (vigente Julio 2026):
- Todo presupuesto de proyecto suma un cargo por uso de tokens IA equivalente al **10% del total presupuestado** (Subtotal Etapa 1 + Subtotal Etapa 2, sin incluir mantenimiento anual). Formula: Tokens IA = (Subtotal Etapa 1 + Subtotal Etapa 2) x 0.10.
- Se calcula una unica vez sobre el total del proyecto (no por modulo, no por etapa por separado).
- Va EXPLICITO en el presupuesto al cliente: se muestra como linea separada "Tokens IA" en la seccion "Total del proyecto", y no se mezcla con mantenimiento anual. No prorratear en los modulos. El mismo valor debe aparecer tambien en la memoria interna 4-presupuestador.md.
- No aplica a iteraciones evolutivas menores a 4 h facturables, salvo indicacion contraria.
- Regla anterior (vigente hasta Junio 2026, ya no aplica): cargo fijo de USD 100 por proyecto.

Patron confirmado de ratio PERT / real en proyectos con IA asistida:

| Proyecto | Horas PERT | Horas reales | Ratio PERT/real | Horas formula (M/2.5x1.2) | Ratio formula/real |
|---|---:|---:|---:|---:|---:|
| ShowroomGriffin | 101.1 h | 25 h | 4.0x | ~40.6 h | 1.6x |
| Ganaderia (CIERRE REAL 2026-07-03) | 101.0 h | 20 h (total proyecto, Etapa 1 + Etapa 2, definitivo) | 5.05x | ~38.6 h | 1.93x |
| contadores-bma-conversor | ~13.1 h (PERT) | 8 h | 1.6x | ~5.3 h (formula) | 0.66x |
| vinosefue — sprint compras proveedor (CIERRE REAL 2026-07-03, reconstruccion retroactiva, sin presupuesto formal previo) | 28.27 h | 4 h (total del lote, sin desglose por item) | **7.07x — record del dataset** | ~11.42 h | **2.86x — record del dataset** |
| labipac — SESION 3 (M7+M8+M9 + 3 fixes post-QA, CIERRE REAL 2026-07-08) | 13.69 h | 2.0 h (total, incluye 3 fixes post-QA) | **6.84x — segundo lugar del dataset** | 5.52 h | **2.76x — segundo lugar del dataset** |

Ganaderia reemplaza su dato previo de "~30 h total" (proyeccion) por el cierre real de 20 h — ahora el ratio PERT/real (5.05x) es el mas alto del dataset y el ratio formula/real (1.93x) es el segundo mas alto. El dato empuja levemente el factor de eficiencia hacia arriba de 2.5, pero no se ajusta el factor unilateralmente por este cierre (ver regla debajo).

El ratio formula/real de 0.66x-1.93x confirma que la contingencia del 20% es en general un buffer razonable, aunque el rango se amplio con el cierre de Ganaderia: sigue sin inflar exageradamente frente a otros cierres, pero ya no es un rango angosto de 1.3x-1.6x.

Excepcion observada (contadores-bma-conversor): ratio formula/real = 0.66x. En este proyecto
la formula subbilo porque el real (8 h) superó las horas facturables calculadas (5.3 h).
Causa: el deploy inicial fue subestimado (1 h estimado → 3 h real) y el proyecto se cobró
sobre horas reales retroactivas, no sobre M estimado. No afecta la validez de la formula para
proyectos futuros donde se aplica correctamente desde el inicio con M real.

Factor de calibracion 2.5: fijo hasta que Energy Nutrition cierre. Recalibrar con ese cierre. El cierre real de Ganaderia (ratio PERT-contingencia/real 5.05x, el mas alto del dataset) es evidencia adicional a favor de subir el factor por encima de 2.5 en esa recalibracion futura.

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