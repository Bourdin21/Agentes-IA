# 1 - Analista funcional — Proyecto KOI

> Memoria acumulativa del agente analista funcional.
> Etapa: Discovery + Análisis + Sesión de definición + Cierre P-A01→P-A07. Estado: ✅ ANÁLISIS FUNCIONAL CERRADO (Etapa 1) — todas las hipótesis y preguntas respondidas · cascada a diseño, arquitectura y presupuesto habilitada. Módulo E2-02 (Fichador) con Análisis cerrado en §11 — Implementación bloqueada por token QuickPass pendiente.
> Fecha: 2026-06-11. Última actualización: 2026-08-12 — Análisis funcional del sprint UX/UI Inversor + fixes cerrado (§12), cascada a Diseño/Arquitectura/Presupuesto disparada.

## 1. Contexto del cliente

Franquicia gastronómica KOI con 15 inversores externos que aportaron capital bajo un esquema de 100 puntos de inversión (USD 287.500 recaudados). El inversor principal (administrador) gestiona hoy la operación con dos Excel:

1. **"Estado de Resultados KOI (Inversores)"**: totaliza ingresos y egresos del local por mes (hojas por año: 2024, 2025, 2026).
2. **"Reparto de Utilidades Inversores"**: esquema de puntos por inversor y liquidación mensual de dividendos.

Las ventas se registran en **Ayres POS** (punto de venta gastronómico); el administrador usa sus totalizadores mensuales para nutrir el Excel. Las cámaras del local se ven hoy por **Hik-Connect** (Hikvision).

Necesidad: un sistema web que reemplace ambos Excel y dé a cada inversor un **dashboard profesional** con las métricas del local, el resultado mensual de su inversión, los valores históricos y el estado de su inversión, con especial foco en UX/UI.

## 2. Alcance funcional

### Incluido (alcance base)

1. **Autenticación y gestión de usuarios**: login con usuario y contraseña; el Administrador crea, edita, desactiva y blanquea contraseñas de usuarios Inversores (solo consulta).
2. **Configuración del estado de resultados**: catálogo de rubros y subgrupos de gastos (editable), parámetros de porcentajes (regalías 3 %, canon 2,5 %, comisiones tarjetas 5 %, IIBB 3,5 %, débitos/créditos 1,2 %, tasa municipal 1 %, previsiones 1 % + 1 %), tipo de cambio mensual.
3. **Carga mensual del estado de resultados**: ventas A (facturadas) y B (no facturadas), gastos por rubro/subgrupo, conceptos calculados automáticamente por porcentaje, totalizadores (Total Gastos, Resultado Ejercicio, Rentabilidad) y conversión a USD por tipo de cambio del mes.
4. **Indicadores de venta (Ayres, carga manual)**: ticket promedio, ítems por ticket, cubierto promedio, por mes.
5. **Dashboard de métricas (core de la aplicación)**: estructura en cards por módulos, gráficos analíticos, tema dark/light, totalizador por mes e histórico multi-año de ingresos, gastos, resultado del ejercicio, rentabilidad y valores en USD; indicadores de venta.
6. **Esquema de puntos de inversión**: registro de los 100 puntos, valor de aporte de cada punto (3.000 / 3.500 / 4.500 USD, puntos bonificados con valor 0), asignación a inversores con vigencia temporal (los puntos de un inversor pueden cambiar de mes a mes).
7. **Reparto de utilidades / liquidaciones mensuales**: utilidad por punto (= Resultado Ejercicio del mes ÷ 100), liquidación por inversor (puntos × utilidad por punto), descuento de consumos del inversor en el local, monto en USD por tipo de cambio, renta mensual, fecha de pago.
8. **Vista "Mi inversión" del inversor**: capital aportado, dividendos mensuales e históricos, dividendos acumulados, recupero (% del capital recuperado), rentabilidad mensual y promedio, en pesos y USD.
9. **Cámaras IP**: opción de menú y pantalla dedicada que embebe el web client de Hik-Connect; el Administrador configura los datos de acceso, el Inversor solo visualiza.
10. **Carga inicial de datos históricos**: migración de los datos 2024–2026 de ambos Excel para que el dashboard histórico nazca completo (excepción acordada a la exclusión estándar).
11. **Notificación por correo al cierre del ejercicio mensual**: cuando el Administrador cierra el mes, el sistema envía automáticamente un correo a cada inversor activo con un resumen del mes (ventas, resultado, rentabilidad, utilidad por punto y su liquidación personal) y el aviso de que el resumen completo ya está disponible en la web, con registro de envíos.

### No incluido (exclusiones)

- Integración directa con la base de datos de Ayres POS (declarada **etapa 2**; en esta etapa la carga es manual).
- Streaming nativo RTSP/WebRTC de cámaras (se usa el web client de Hik-Connect embebido).
- Facturación electrónica AFIP/ARCA.
- Aplicación móvil (el sitio es responsive, no app nativa).
- Configuración y costo de servidor/hosting (cubierto por plan de mantenimiento).
- Otros envíos de correo o notificaciones externas distintos de la notificación de cierre mensual (recordatorios de pago, alertas, newsletters, etc.).
- Cambios de alcance posteriores al inicio (se presupuestan aparte).

### Dependencias del cliente

- Entrega de los dos Excel actualizados al momento de la carga inicial.
- Datos de acceso de Hik-Connect en la implementación.
- Definición del tipo de cambio mensual (lo carga el Administrador).
- Totalizadores mensuales de Ayres para la carga manual.
- Cuenta de correo emisora (casilla o servicio SMTP) para la notificación de cierre.

## 3. Casos de uso principales

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-01 | Iniciar sesión | Admin / Inversor | Acceso con usuario y contraseña; redirección al dashboard. |
| CU-02 | Gestionar usuarios inversores | Admin | ABM de usuarios Inversor, vinculación con su ficha de inversor, blanqueo de contraseña, activar/desactivar. |
| CU-03 | Configurar rubros y subgrupos | Admin | ABM de rubros de gasto y subgrupos (ej.: Servicios → Luz, Gas, Internet, Agua). Baja lógica si tienen movimientos. |
| CU-04 | Configurar parámetros porcentuales | Admin | Editar % de conceptos calculados (regalías, canon, comisiones, impuestos, previsiones) con vigencia por período. |
| CU-05 | Cargar tipo de cambio mensual | Admin | Un TC por mes/año; requerido para los valores en USD y liquidaciones. |
| CU-06 | Cargar estado de resultados del mes | Admin | Cargar ventas A y B, gastos por subgrupo; el sistema calcula los conceptos porcentuales, totales, resultado y rentabilidad. |
| CU-07 | Cargar indicadores de venta | Admin | Ticket promedio, ítems por ticket, cubierto promedio del mes (origen Ayres, manual). |
| CU-08 | Consultar dashboard | Admin / Inversor | Cards con métricas del mes seleccionado + gráficos históricos (ingresos, gastos, resultado, rentabilidad, USD, indicadores). Tema dark/light. |
| CU-09 | Gestionar puntos de inversión | Admin | ABM de puntos (valor de aporte, bonificado) y asignación a inversores con vigencia mensual. |
| CU-10 | Generar liquidación mensual | Admin | A partir del resultado del mes: utilidad por punto, liquidación por inversor, carga de consumos a descontar, fecha de pago, marca de pagado. |
| CU-11 | Consultar "Mi inversión" | Inversor | Capital, dividendos del mes y acumulados, recupero, rentabilidad, historial completo en pesos y USD. |
| CU-12 | Consultar reparto general | Admin | Vista tipo hoja GENERAL: serie mensual de utilidad por punto, total, USD, renta, fechas de pago. |
| CU-13 | Configurar cámaras | Admin | Alta/edición de los datos de acceso del web client Hik-Connect (URL/credenciales/notas). |
| CU-14 | Ver cámaras | Admin / Inversor | Pantalla dedicada con el web client de Hik-Connect embebido. |
| CU-15 | Carga inicial de históricos | Proveedor con Admin | Importación de los datos 2024–2026 de ambos Excel (única vez, al implementar). |
| CU-16 | Notificar cierre por correo | Sistema (dispara Admin al cerrar) | Al cerrar el período, envía a cada inversor activo un mail con resumen del mes + su liquidación + link a la web; registra el resultado de cada envío. |

## 4. Criterios de aceptación (verificables)

**CU-06 — Estado de resultados**
- Dado un mes con ventas A y B cargadas, el total de Ventas = A + B.
- Los conceptos porcentuales se calculan sobre la base correcta: regalías y canon sobre Ventas totales; comisiones de tarjetas, IIBB, débitos/créditos y tasa municipal **solo sobre Ventas A** (regla confirmada por el cliente; el Excel actual mezcla bases y el sistema la normaliza); previsiones (1 % + 1 %) sobre Ventas totales.
- Total Gastos = suma de los totales de todos los rubros del mes.
- Resultado Ejercicio = Ventas − Total Gastos; Rentabilidad = Resultado ÷ Ventas; con ventas en cero no se muestra error de división (se muestra "—").
- Valores USD = valores en pesos ÷ TC del mes; si falta TC, el bloque USD del mes queda pendiente con aviso.
- El total anual por rubro y por concepto coincide con la suma de los 12 meses.

**CU-08 — Dashboard**
- El inversor ve los mismos totales del mes que el Excel actual para los meses migrados (validación contra 3 meses de muestra).
- Permite alternar dark/light y la preferencia se recuerda por usuario.
- Muestra al menos: card de ventas (A+B), card de gastos por rubro, card de resultado y rentabilidad, card de valores USD, card de indicadores de venta, gráfico de evolución mensual multi-año.

**CU-09 / CU-10 — Puntos y liquidaciones**
- La suma de puntos asignados vigentes nunca supera 100; los no asignados quedan visibles como disponibles.
- Utilidad por punto del mes = Resultado Ejercicio ÷ 100 (coincide con la hoja GENERAL para los meses migrados).
- Liquidación del inversor = puntos vigentes del mes × utilidad por punto − consumos del mes; nunca oculta el detalle del descuento.
- Renta mensual del inversor = monto USD ÷ capital aportado; recupero acumulado = dividendos USD acumulados ÷ capital aportado.
- Una liquidación marcada como pagada registra fecha de pago y queda inmutable (solo el Admin puede reabrirla con motivo).

**CU-11 — Mi inversión**
- El inversor solo ve sus propios datos (nunca los de otros inversores).
- El historial reproduce los valores del Excel migrado (validación contra la hoja del inversor para 3 meses de muestra).

**CU-13 / CU-14 — Cámaras**
- El Inversor accede a la pantalla de cámaras solo si el Admin configuró el acceso.
- La pantalla embebe el web client de Hik-Connect; si el servicio externo no responde, se muestra mensaje claro (la disponibilidad del video es responsabilidad de Hikvision).

**CU-15 — Carga inicial**
- Cerrada la migración, los totales anuales 2024 y 2025 y los acumulados por inversor coinciden con los Excel fuente.

**CU-16 — Notificación de cierre por correo**
- Al cerrar un período, cada inversor activo con email válido recibe un correo con: ventas del mes, resultado del ejercicio, rentabilidad, utilidad por punto, su liquidación personal (puntos, bruto, consumos, neto, USD) y enlace al sistema.
- Un fallo de envío NO bloquea ni revierte el cierre del período: queda registrado como fallido y el Admin puede reenviar manualmente.
- Cada envío queda registrado (inversor, fecha/hora, estado enviado/fallido).
- La reapertura y nuevo cierre de un período no duplica correos sin confirmación explícita del Admin.

## 5. Permisos, estados y validaciones

**Roles**
- **Administrador** (inversor principal): carga y configura todo, gestiona usuarios, genera liquidaciones, configura cámaras. Ve todos los datos de todos los inversores.
- **Inversor**: solo consulta dashboard, "Mi inversión" y cámaras. Sin acceso a pantallas de carga ni configuración.
- (Super usuario interno del proveedor para soporte: fuera de la documentación al cliente.)

**Estados**
- Período mensual: `Abierto` (editable) → `Cerrado` (genera liquidaciones) → `Reabierto` (con motivo, recalcula liquidaciones no pagadas).
- Liquidación por inversor: `Pendiente` → `Pagada` (fecha de pago); `Pagada` es inmutable salvo reapertura por Admin con motivo.
- Usuario: `Activo` / `Inactivo`.

**Validaciones clave**
- Importes ≥ 0 con dos decimales; TC > 0; un solo registro de TC por mes/año.
- No se puede cerrar un período sin ventas, TC y al menos los rubros obligatorios cargados.
- No se puede asignar a inversores más de 100 puntos vigentes en un mismo período.
- Consumos del inversor nunca pueden superar el monto de su liquidación del mes (queda saldo a favor del local fuera de alcance: validación bloqueante con mensaje).
- Subgrupo no se elimina físicamente si tiene movimientos históricos (baja lógica).

## 6. Riesgos y supuestos

**Riesgos**
- R1 — Migración de datos: los Excel tienen fórmulas inconsistentes entre meses (bases A/B mezcladas en impuestos, celdas pisadas a mano). La migración respeta los **valores** históricos tal como están, no los recalcula. Riesgo medio-alto, acotado al módulo de carga inicial.
- R2 — Hik-Connect: el embebido depende de un servicio de terceros (políticas de iframe/login de Hikvision). Mitigación: pantalla con enlace de apertura en pestaña dedicada como alternativa si el iframe es bloqueado por el proveedor.
- R3 — Esquema de puntos: los puntos cambian de dueño/cantidad en el tiempo; si la vigencia histórica no se releva bien, los acumulados no van a coincidir. Mitigación: asignación con vigencia mensual y validación contra hojas por inversor.

**Supuestos**
- S1 — Un solo local (la franquicia KOI); multi-local fuera de alcance.
- S2 — Moneda de carga: pesos argentinos; USD solo como conversión por TC mensual.
- S3 — ~~La utilidad a repartir es el Resultado Ejercicio sin ajustes~~ **REVISADO**: el Admin puede ajustar el monto a repartir con motivo (D-01 confirmado).
- S4 — El descuento de consumos se carga como monto mensual por inversor (el detalle de cada consumo no se registra).
- S5 — Hasta 16 usuarios (1 admin + 15 inversores); pueden crecer con el plan de mantenimiento.

## 7. Banderas tempranas

| Bandera | Valor | Nota |
|---|---|---|
| Migración EF | **Sí** | Modelo de datos nuevo completo (~18 tablas). |
| Integración externa | **Sí, acotada** | Envío de correo saliente (SMTP) para la notificación de cierre. Hik-Connect es embebido (no consume API); Ayres POS declarado etapa 2. |
| Máquina de estados | **Sí, acotada** | Ciclo del período mensual (Abierto/Cerrado/Reabierto) y de la liquidación (Pendiente/Pagada). |
| Migración de datos | **Sí (excepción acordada)** | Carga inicial 2024–2026 de ambos Excel. |

## 8. Preguntas pendientes — ESTADO AL CIERRE DE SESIÓN DE DEFINICIÓN

### Hipótesis originales: CERRADAS
| # | Hipótesis original | Resolución |
|---|---|---|
| H-01 | ¿Utilidad a repartir admite ajuste manual? | ✅ **Opción B confirmada** — Admin puede ajustar el monto con motivo obligatorio |
| H-02 | ¿Inversores ven Ventas B discriminadas? | ✅ **Opción B confirmada** — Dashboard muestra solo total. **Nueva categorización: Salón / Delivery** |

### Preguntas nuevas derivadas de sesión — ✅ TODAS CERRADAS

| ID | Pregunta | ✅ Respuesta confirmada |
|---|---|---|
| P-A01 | ¿"Cantidad de comensales" manual o Ayres? | **Manual** — dato de Ayres cargado a mano. En el futuro se integrará (etapa 2). Agrega `CantidadComensales` a `IndicadorVenta`. |
| P-A02 | ¿Salón/Delivery reemplazan A/B o conviven? | **Conviven como 2 dimensiones** — `VentaMensual` pasa a 4 campos: `VentasASalon`, `VentasBSalon`, `VentasADelivery`, `VentasBDelivery`. Bases porcentuales: "Ventas A" = ASalon+ADelivery; "Ventas Totales" = suma de los 4. |
| P-A03 | ¿Qué API de dólar y qué cotización? | **ArgentinaDatos + DolarApi** (mismo esquema que VirtualWallet · `ICotizacionService`). UX: Admin ve cotizaciones del día por casa (oficial/blue/MEP/CCL), selecciona una como base (default: blue promedio), puede editarla antes de guardar como TC del mes. |
| P-A04 | ¿Mecanismo para error post-cierre? | **No hay mecanismo técnico** — error post-cierre lo gestiona el Admin + SuperUsuario del sistema operativamente. Simplifica el alcance. |
| P-A05 | ¿Dashboard "actual" muestra mes Abierto o solo Cerrado? | **Mes Abierto con datos parciales** — P-02a muestra lo cargado hasta el momento; si falta TC, los valores USD se muestran como "pendiente". |
| P-A06 | ¿Notificaciones in-app con expiración? | **No** — no expiran. El usuario las marca como leídas; se acumulan. Compatible con `INotificationService` de BlankProject. |
| P-A07 | ¿Preview editable o solo informativo? | **Editable y con cierre desde el preview** — el Admin edita consumos por inversor en el preview y confirma el cierre desde ahí mismo. El botón "Confirmar cierre" está en el preview. |

---

## 9. Sesión de definición — Junio 2026
| P-A01 | **¿"Cantidad de comensales" se carga manualmente o viene de Ayres POS (etapa 2)?** Si es manual: va en M6 (Indicadores de Venta). Si es de Ayres: fuera de alcance base. | M6 (Indicadores) + Dashboard | 🔴 Bloqueante para M6 |
| P-A02 | **¿"Ventas Salón" y "Ventas Delivery" reemplazan completamente a "Ventas A/B (facturadas/no facturadas)" o se suman?** Si reemplazan: la base de cálculo de comisiones/IIBB/débitos (antes: Ventas A) ahora es ¿Salón? ¿Delivery? ¿Total? Si conviven: ¿hay 4 campos (VentasASalón, VentasBSalón, VentasADelivery, VentasBDelivery)? | M4 (Estado de Resultados) + `VentaMensual` + cálculos porcentuales | 🔴 Bloqueante para M4 |
| P-A03 | **¿Qué API de cotización del dólar y cuál cotización?** Hipótesis A: DolarAPI (blue / MEP / CCL / oficial). Hipótesis B: BCRA API oficial. Hipótesis C: Bluelytics. La cotización elegida afecta significativamente los valores USD de los inversores. | M3 (TC) + nueva integración | 🔴 Alto |
| P-A04 | **Con el período no reabreble: si hay un error en un gasto después de cerrar, ¿qué hace el Admin?** Hipótesis A: el error queda registrado, se admite una "nota de corrección" sin recalcular. Hipótesis B: hay un mecanismo de ajuste (nuevo concepto "Ajuste de corrección") que recalcula el resultado. | M10 (Liquidaciones) + máquina de estados | 🟡 Medio |
| P-A05 | **Dashboard "actual": ¿muestra datos del mes Abierto (con datos parciales) o solo del último Cerrado?** El cliente dice "datos del mes actual". Hipótesis A: muestra el último mes Cerrado siempre (más consistente). Hipótesis B: muestra el mes en curso Abierto con lo que se haya cargado hasta ahora (más dinámico, pero puede confundir con datos incompletos). | M7 (Dashboard) + P-02 rediseño | 🟡 Medio |
| P-A06 | **¿Las notificaciones in-app tienen expiración o se acumulan?** Hipótesis A: el inversor las marca como leídas; se archivan pero no desaparecen. Hipótesis B: expiran a los N días (ej.: 30 días). Hipótesis C: el Admin puede eliminarlas manualmente. | Módulo nuevo Notificaciones | 🟡 Medio |
| P-A07 | **Preview antes de cerrar: ¿el Admin puede modificar consumos en el preview o solo ver y confirmar?** Hipótesis A: el preview es solo informativo (ver calculado → confirmar). Hipótesis B: el preview es editable (muestra las liquidaciones y permite editar consumos antes de confirmar el cierre). | M10 (Liquidaciones) + UX de cierre | 🟡 Medio |

---

## 9. Sesión de definición — Junio 2026

> Respuestas recibidas en reunión presencial. 31 decisiones confirmadas y 7 nuevas preguntas abiertas.

### 9.1 Decisiones confirmadas

| # | Punto | Decisión confirmada | Impacto en alcance |
|---|---|---|---|
| D-01 | Ajuste de monto a repartir (H-01) | **Opción B**: Admin ajusta el monto con motivo obligatorio antes de generar liquidaciones | ➕ Expansión M10; nuevo campo `MontoAjustado` + `MotivoAjuste` |
| D-02 | Categorías de venta (H-02) | **Opción B** + redefinición: sin A/B en dashboard; categorías: **Salón / Delivery** | 🔴 Redefinición de `VentaMensual`; bases de cálculo porcentuales A CONFIRMAR (P-A02) |
| D-03 | Rubros obligatorios para cerrar | Solo Ventas (Salón + Delivery) y TC son obligatorios; gastos pueden quedar en $0 | Simplifica validación de cierre |
| D-04 | Estado Reabierto | **Eliminado**: período no puede reabrirse una vez cerrado (una vez que hay liquidaciones) | ➖ Simplifica máquina de estados → solo Abierto → Cerrado |
| D-05 | Consumos: momento de carga | Se cargan **antes** de cerrar el período; editables mientras liquidación en `Pendiente` (⚠️ P-A07 a confirmar si aplica en preview) | Impacta P-08 y flujo de cierre |
| D-06 | Pago masivo de liquidaciones | **Hipótesis C confirmada**: selección múltiple (checkboxes) + botón "Pagar seleccionadas" con fecha única | Impacta P-08 UI |
| D-07 | Resultado negativo del mes | Liquidación con monto **$0** si el resultado es negativo; el inversor no pierde plata | Regla de negocio: `Max(0, utilidad × puntos)` |
| D-08 | Consumos: granularidad | Monto único mensual por inversor (S-4 confirmado); sin detalle de ítems | Sin cambio |
| D-09 | Capital del inversor | Fijo, sin historial de cambios (Hipótesis A confirmada) | Sin cambio |
| D-10 | Tipo de cambio | **Nueva integración**: API de cotización del dólar para pre-cargar TC automáticamente | ➕ Nuevo módulo/expansión M3; bandera integración → Sí (SMTP + API dólar) |
| D-11 | Dashboard por defecto | Último período **Cerrado** disponible al abrir | Sin cambio de entidades |
| D-12 | Tema por defecto | **Oscuro** para usuarios nuevos | Solo UI |
| D-13 | Admin sin "Mi inversión" | Admin NO tiene pantalla "Mi inversión" personal (Hipótesis B confirmada) | Simplifica P-10 |
| D-14 | CMV siempre manual | Confirmado | Sin cambio |
| D-15 | Grilla liquidaciones | P-08 muestra todos los inversores; select múltiple para filtrar | Impacta P-08 UI |
| D-16 | Nota libre en liquidación | **Hipótesis B confirmada**: campo `Observaciones` libre por inversor | Nuevo campo `LiquidacionInversor.Observaciones` |
| D-17 | Barra progreso recupero | Hitos 25/50/75/100% con celebración visual al 100% | Solo UI P-10 |
| D-18 | Dashboard: dos pantallas | **(1)** Dashboard del mes actual / liquidación corriente; **(2)** Histórico / evolución mes a mes | ➕ Expansión M7 → puede requerir pantalla nueva |
| D-19 | KPIs del Dashboard | Ventas total (torta Salón/Delivery), Resultado vs. mes anterior (barras), Rentabilidad%, Utilidad por punto, Valores USD, Ticket/cubierto/**comensales** | Nuevo KPI "comensales" → depende de P-A01 |
| D-20 | Cámaras | iframe preferido con fallback a pestaña nueva | Sin cambio |
| D-21 | Correo de cierre — contenido | **Simplificado**: solo aviso de que la liquidación está disponible + botón de acceso. Sin resumen del mes en el email | ➖ Simplifica M15 (`NotificacionService`) |
| D-22 | Excel fuente | Ambos Excel listos para entregar ✅ | Sin riesgo de demora en M14 |
| D-23 | Validación migración | El SuperAdmin (proveedor) valida internamente los totales | Sin cambio de proceso |
| D-24 | Migración de históricos | Se migran todos los datos hasta el último mes con datos en el Excel (incluyendo meses 2026 parciales) | Acota el alcance de M14 |
| D-25 | Exportación Excel | **Eliminada** del alcance (P-04 solo lectura, sin export) | ➖ Simplifica M5; reduce precio |
| D-26 | Puntos de inversión | Los 100 puntos ya están definidos y **no van a cambiar**; gestión de puntos = ABM de solo lectura / asignaciones históricas | ➖ Simplifica M9 significativamente |
| D-27 | Configuración SMTP | Se configura desde el código por el proveedor, no hay pantalla de configuración en la UI | ➖ Elimina P-14 de config SMTP; simplifica M15 |
| D-28 | Preview antes de cerrar | **Nueva UX**: modal/pantalla de preview con liquidaciones calculadas antes de confirmar el cierre del período | ➕ Expande M10 (flujo de cierre) |
| D-29 | Panel de notificaciones in-app | **Nueva funcionalidad**: Admin crea notificaciones dirigidas; select múltiple destinatarios (todos o algunos inversores); visible en navbar de todos los roles | ➕ Nuevo módulo; usa `INotificationService` BlankProject |
| D-30 | Reabrir liquidación individual | Solo Admin puede reabrir liquidación individual (`Pagada → Pendiente`) con motivo obligatorio; el período global no se puede reabrir | Sin cambio de entidades (ya estaba en D-04) |
| D-31 | "Cantidad de comensales" | Nuevo KPI declarado por el cliente para el Dashboard | Depende de P-A01 (manual → expande M6 / Ayres → etapa 2) |

### 9.2 Cambios netos en alcance

| Tipo | Cambio | Módulo | Impacto en precio |
|---|---|---|---|
| ➕ Adición | Ajuste manual del monto a repartir + motivo | M10 | Sube |
| ➕ Adición | Integración API dólar para TC automático | M3 (expansión) | Sube |
| ➕ Adición | Segunda pantalla Dashboard (Histórico) | M7 (expansión) | Sube |
| ➕ Adición | Panel de notificaciones in-app con targeting por usuario | Módulo nuevo | Sube |
| ➕ Adición | Preview de liquidaciones antes de confirmar el cierre | M10 | Sube leve |
| ➕ Adición | Campo `Observaciones` en liquidación del inversor | M10 | Sube leve |
| ➕ Adición | "Cantidad de comensales" (si es manual) | M6 | Sube leve |
| ➖ Eliminación | Exportación Excel del estado de resultados | M5 | Baja |
| ➖ Eliminación | Estado Reabierto del período | M10 | Baja |
| ➖ Eliminación | Pantalla de configuración SMTP | M15 | Baja |
| ➖ Simplificación | Contenido del correo de cierre (solo aviso + botón) | M15 | Baja |
| ➖ Simplificación | Puntos de inversión fijos (sin gestión dinámica) | M9 | Baja |
| 🔄 Redefinición | Ventas A/B → 4 propiedades: `VentasASalon`, `VentasBSalon`, `VentasADelivery`, `VentasBDelivery` | M4, `VentaMensual` | Sube leve (4 campos) |
| ➕ Adición | Estrategia M14 confirmada: históricos migran con Delivery=0; Salón=A+B completo; badge "sin desglose" por período | M14 migración | ✅ Cerrado |

> ✅ **Análisis funcional cerrado.** P-A01→P-A07 confirmadas. Presupuesto v3 requiere recálculo → ver `4-presupuestador.md`.

### 9.3 Banderas tempranas actualizadas

| Bandera | Valor anterior | Valor actualizado | Nota |
|---|---|---|---|
| Migración EF | Sí | **Sí** | Sin cambio |
| Integración externa | Sí, acotada (SMTP) | **Sí — 2 integraciones**: SMTP (correo de cierre) + API cotización dólar (TC automático) | API dólar es nueva |
| Máquina de estados | Sí, acotada | **Sí, simplificada** | Período: solo Abierto→Cerrado (eliminado Reabierto); Liquidación: Pendiente↔Pagada sin cambios |
| Migración de datos | Sí (excepción acordada) | **Sí** | Sin cambio |

---

## 9.4 Cierre de preguntas P-A01 a P-A07 — Junio 2026

### Modelo de ventas redefinido (P-A02)

La entidad `VentaMensual` pasa de 2 a **4 campos de entrada** organizados como una matriz 2×2:

| | Facturado (A) | Sin factura (B) |
|---|---|---|
| **Salón** | `VentasASalon` | `VentasBSalon` |
| **Delivery** | `VentasADelivery` | `VentasBDelivery` |

Agregados calculados (no persistidos, derivados al vuelo):

| Agregado | Fórmula | Uso |
|---|---|---|
| `VentasA` | ASalon + ADelivery | Base de cálculo porcentual — comisiones, IIBB, débitos, tasa municipal |
| `VentasTotales` | ASalon + BSalon + ADelivery + BDelivery | Base de cálculo porcentual — regalías, canon, previsiones |
| `VentasSalon` | ASalon + BSalon | Torta del Dashboard (eje de canal) |
| `VentasDelivery` | ADelivery + BDelivery | Torta del Dashboard (eje de canal) |

Pantalla P-03 de carga: 4 inputs de ventas + totales calculados en tiempo real.
**Estrategia de migración M14 confirmada ✅**: los Excel históricos solo tienen A/B sin apertura Salón/Delivery. Los períodos históricos se migran con `VentasADelivery = 0` y `VentasBDelivery = 0`; la totalidad de cada tipo queda en Salón (`VentasASalon = VentasA`, `VentasBSalon = VentasB`). Cada período migrado recibirá una observación `"Desglose Salón/Delivery no disponible en datos fuente"`. La torta Salón/Delivery del Dashboard mostrará 100 % Salón para períodos históricos hasta que el Admin cargue el primer mes real con los 4 campos.

### TC con selección de cotización (P-A03)

Flujo UX al cargar el TC del mes:
1. Admin abre la pantalla de TC del mes.
2. El sistema consulta `ICotizacionService.ObtenerCotizacionesPorCasaParaFecha(hoy)` (ArgentinaDatos + DolarApi, mismo esquema que VirtualWallet).
3. Se muestra una tabla con las casas disponibles: Oficial, Blue (compra/venta/promedio), MEP, CCL, Cripto, etc.
4. El campo TC pre-carga con **blue promedio del día** (`ObtenerPromedioBlue`).
5. Admin puede seleccionar otra casa haciendo clic en la fila correspondiente (actualiza el campo).
6. Admin puede editar el valor numérico antes de guardar.
7. Al guardar, el TC queda registrado en `PeriodoMensual.TipoCambio`.

Referencia de implementación: copiar `ICotizacionService` + `CotizacionService` de `C:\Sistemas\virtualwallet`.
Apis: `https://dolarapi.com/v1/dolares` (hoy) + `https://api.argentinadatos.com/v1/cotizaciones/dolares` (histórico).
Cache: 30 min para hoy, 6 h para histórico.

### Preview de cierre — flujo definitivo (P-A07)

El preview ES la pantalla de edición de consumos antes del cierre. Flujo:

```
Admin en P-03 (Estado de resultados abierto)
        ↓
   [Botón “Cerrar período”]
        ↓
   P-08 (Preview/Liquidaciones)
   ┌──────────────────────────────────────────────────┐
   │ Monto a repartir: [Resultado Ejercicio] [editable + motivo] │
   │ Utilidad por punto: $X.XXX                               │
   │                                                          │
   │ Inversor     Puntos  Bruto   Consumos [edit]  Neto   USD  │
   │ García         10   $X.XXX  [    0   ]      $X.XXX $XXX  │
   │ López          8   $X.XXX  [  500   ]      $X.XXX $XXX  │
   │ ...                                                      │
   │                                                          │
   │         [Cancelar]  [Confirmar y cerrar período]          │
   └──────────────────────────────────────────────────┘
        ↓ [Confirmar y cerrar período]
   Período pasa a Cerrado
   Liquidaciones generadas (Pendiente)
   Email de aviso enviado a inversores activos
```

El preview es la pantalla P-08 reutilizada como paso de confirmación. Los consumos son editables en este paso. Una vez que el Admin confirma, ya no hay vuelta atrás sin reabrir la liquidación individual.

### Nueva regla de negocio (P-A04)

No existe mecanismo técnico de corrección post-cierre. Si el Admin detecta un error en un gasto después del cierre:
- El error queda registrado en el período cerrado tal como está.
- El Admin y el SuperUsuario del sistema lo resuelven operativamente (fuera del sistema).
- **No se agrega ningún módulo de ajuste** — esto simplifica el alcance.

### Nuevo supuesto actualizado

- S-3 revisado: la utilidad a repartir **puede ajustarse manualmente** por el Admin antes del cierre, con motivo obligatorio. El default es el Resultado del Ejercicio.

---

## 10. Etapa 2 — Relevamiento de integraciones del local

> Fecha de relevamiento: 2026-06-24. Responsable: Olvidata Soft. Estado: **⏳ PENDIENTE DE RESOLUCIÓN** — múltiples credenciales y decisiones técnicas abiertas.

Este bloque documenta los tres módulos relevados para la Etapa 2. **No forman parte del alcance de la Etapa 1 actualmente en producción.** Ninguno impacta el código ni las entidades existentes.

---

### 10.1 Módulo E2-01 — Integración con sistema de ventas Ayres

#### Necesidad del cliente
El cliente quiere que los **ingresos mensuales del período** (ventas A salón, B salón, A delivery, B delivery y cantidad de comensales) se completen automáticamente desde Ayres, eliminando la carga manual que hoy hace el Administrador.

#### Arquitectura relevada
- **Proveedor**: MaxiSistemas S.R.L.
- **Tipo**: API REST propia sobre ASP.NET Core, puerto **8510**.
- **Autenticación**: JWT (key conocida: `EstaEsUnaClaveSuperSecretaDeJWT1234567890`, expiración 999 h).
- **Base de datos**: MySQL 8.0.21 Community, puerto **3320** (no estándar), bases `koisucursal9` y `koicentral`. No accesible directamente desde red externa; solo el proceso servidor Ayres la consume internamente.
- **Documentación API**: sin Swagger habilitado — `/swagger` devuelve 404. Requiere análisis de tráfico o documentación de MaxiSistemas.

#### Opciones de integración

| Opción | Descripción | Ventajas | Riesgos |
|---|---|---|---|
| **A — API REST Ayres** *(recomendada)* | Consumir la API en puerto 8510 con JWT | No depende de credenciales de BD; más estable ante actualizaciones | Endpoints sin mapear; requiere documentación de MaxiSistemas |
| **B — Acceso directo MySQL 3320** | Conectar el sistema web a MySQL con credenciales del usuario `pop10` | Acceso total a datos; consultas personalizadas | Contraseña pendiente; requiere acceso remoto al puerto 3320; rompe encapsulamiento del proveedor |

#### Alcance funcional propuesto para E2-01
- **CU-E2-01**: al abrir el período mensual, el sistema consulta la API de Ayres (o MySQL) y pre-carga automáticamente los totalizadores de ventas (A/B Salón + A/B Delivery) y la cantidad de comensales del mes.
- El Administrador puede revisar y corregir los valores antes de guardarlos.
- Los datos se importan por mes completo (no en tiempo real).
- **Pantalla afectada**: P-03 Estado de resultados — agrega botón "Importar desde Ayres" junto a los inputs de ventas.

#### Capas afectadas (estimación)
- **Presentación**: botón "Importar desde Ayres" en P-03 con feedback de resultado (SweetAlert2).
- **Negocio**: nuevo servicio `IAyresService` con método `ObtenerVentasMesAsync(int anio, int mes)`.
- **Datos**: sin nuevas entidades; usa `VentaMensual` y `PeriodoMensual` existentes.
- **Infraestructura**: `HttpClient` hacia API Ayres (o conexión MySQL secundaria). Requiere configuración de URL, puerto y JWT en `appsettings`.

#### Banderas
- ⚠️ **Integración externa**: Sí (nueva — API Ayres o MySQL directo).
- ⚠️ **Migración EF**: No (no hay nuevas tablas).
- ⚠️ **Máquina de estados**: No.
- ⚠️ **Infraestructura de red**: si el sistema web es externo (internet), se requiere port forwarding del router local para exponer el puerto 8510 o 3320. Debe coordinarse con el técnico de red del local.

#### Pendientes bloqueantes
| Pendiente | Responsable | Estado |
|---|---|---|
| Documentación/mapeo de endpoints API Ayres | Desarrollador → MaxiSistemas | ⏳ |
| Decisión: Opción A (API) vs Opción B (MySQL directo) | Desarrollador + cliente | ⏳ |
| Contraseña MySQL usuario `pop10` o `root` | Desarrollador → MaxiSistemas | ⏳ |
| Acceso remoto al puerto 8510 o 3320 desde sistema web externo | Técnico de red del local | ⏳ |

---

### 10.2 Módulo E2-02 — Fichador de empleados (QuickPass / ZKTeco)

#### Necesidad del cliente
El cliente quiere una **pantalla en el sistema web** donde pueda ver los registros de asistencia de los empleados del local: fichadas de entrada/salida, horas trabajadas y estado de presentismo.

#### Arquitectura relevada
- **Hardware**: reloj biométrico ZKTeco MB360 (huella + reconocimiento facial, Ethernet/WiFi). Protocolo ADMS — push hacia servidor cloud.
- **Software**: QuickPass versión 4 — SaaS cloud, hosting AWS (EE.UU.).
- **URL**: `https://qpv4.quickpassweb.com`
- **API**: ✅ REST disponible, autenticación Bearer Token.
- **Contacto técnico**: `desarrollo@quickpassweb.com`

#### Ventaja clave
Al ser SaaS cloud, la integración **no requiere acceso a la red local del cliente**. Funciona desde cualquier lugar con el token de API. No hay dependencia de que la PC del local esté encendida.

#### Alcance funcional propuesto para E2-02
- **CU-E2-02a — Ver asistencia del día**: pantalla que muestra las fichadas del día actual (entrada/salida por empleado).
- **CU-E2-02b — Consultar rango de fechas**: filtro por empleado y rango de fechas con resumen de horas trabajadas.
- **CU-E2-02c — Ver empleados registrados**: listado de empleados activos con su estado en QuickPass.
- Actor: solo **Administrador** (los inversores no tienen acceso a datos del personal).

#### Capas afectadas (estimación)
- **Presentación**: nueva pantalla P-E2-02 "Fichador" con filtros de fecha (daterangepicker) y DataTable. Nuevo link en sidebar (solo Admin).
- **Negocio**: nuevo servicio `IQuickPassService` con métodos `ObtenerFichadasAsync(rango)`, `ObtenerEmpleadosAsync()`.
- **Datos**: sin nuevas tablas. Datos traídos en tiempo real desde QuickPass (no se persisten localmente en esta etapa).
- **Infraestructura**: `HttpClient` hacia `https://qpv4.quickpassweb.com`. Token Bearer configurado en `appsettings`.

#### Banderas
- ⚠️ **Integración externa**: Sí (nueva — API QuickPass REST).
- ⚠️ **Migración EF**: No.
- ⚠️ **Máquina de estados**: No.

#### Pendientes bloqueantes
| Pendiente | Responsable | Estado |
|---|---|---|
| Credenciales admin del local en QuickPass | Encargado del local | ⏳ |
| Token de API de QuickPass | Desarrollador (desde panel o vía `desarrollo@quickpassweb.com`) | ⏳ |
| Documentación de endpoints disponibles (asistencia, empleados) | Desarrollador → QuickPass | ⏳ |

---

### 10.3 Módulo E2-03 — Cámaras IP (NVR local / RTSP)

> 🟡 **Relevamiento técnico en curso** (actualizado 2026-08-10) — restricción de red confirmada por el cliente; investigación de arquitectura de integración completada; faltan datos puntuales del NVR y decisión de infraestructura antes de poder Analizar/Diseñar/Presupuestar.

#### Restricción confirmada por el cliente (2026-08-10)

El local tiene **un único NVR centralizado** que agrega todas las cámaras del local sobre una **red aislada** ("insolada" — LAN dedicada a videovigilancia, sin salida directa a internet). No hay forma de llegar a las cámaras individuales por URL: el único punto de acceso es el NVR, y hoy solo es alcanzable por cable dentro del local. Esto descarta cualquier integración que asuma una IP pública o URL directamente alcanzable por el navegador del inversor — hace falta un componente intermedio.

#### Investigación: cómo se obtiene el stream RTSP de un NVR Hikvision

Fuente: [Hikvision Support — How do I get my RTSP stream?](https://supportusa.hikvision.com/support/solutions/articles/17000129064-how-do-i-get-my-rtsp-stream-)

- Formato de URL con autenticación: `rtsp://<usuario>:<contraseña>@<IP del NVR>:<puerto RTSP>/Streaming/channels/<canal><stream>`
- Puerto por defecto: **554** (sin autenticación en la URL) u **10554** (con usuario/contraseña embebidos).
- Cada cámara conectada al NVR tiene su propio número de canal dentro de la misma IP del grabador (canal 1 = `101`/`102`, canal 2 = `201`/`202`, etc.). El sufijo `01` es el stream principal (main, alta resolución) y `02` el sub-stream (menor resolución, más liviano — recomendado para embeber en la web en vez del principal).
- Esto confirma que **si** se logra alcanzar el NVR, cada cámara se obtiene como una URL RTSP independiente y estandarizada — no hace falta credenciales por cámara, solo las del NVR.

#### El problema real a resolver: RTSP no se reproduce nativo en un navegador

RTSP es un protocolo pensado para clientes de escritorio/VLC, no para `<video>` HTML. Para mostrarlo en la web del inversor hace falta un **gateway intermedio** que traduzca RTSP a un formato que el navegador sí entienda (HLS o WebRTC) — el "por stream" que le recomendaron al cliente se refiere a este tipo de solución, no a exponer el NVR directamente.

**Arquitectura recomendada (evaluada contra el escenario de red aislada):**

```
[Cámaras] --cable--> [NVR, LAN aislada del local]
                          │  RTSP (554/10554), solo alcanzable dentro de la LAN
                          ▼
              [Gateway de streaming — equipo siempre encendido en el local]
                     (ej. MediaMTX: single binary, gratis, bajo consumo,
                      toma RTSP del NVR y lo re-publica como HLS / WebRTC)
                          │  HLS/WebRTC, sale por la conexión a internet del local
                          ▼
                [Túnel saliente — sin abrir puertos en el router]
                   (ej. Cloudflare Tunnel: gratis, el equipo del local
                    inicia la conexión hacia afuera, no requiere IP
                    pública ni configurar el router)
                          │  URL pública HTTPS (subdominio propio)
                          ▼
              [KOI Web — pantalla Cámaras (P-11), <video> + hls.js]
                  reemplaza el iframe de HikConnect por un player nativo
```

- **MediaMTX** (ex rtsp-simple-server, open source, un solo binario, sin dependencias): toma el/los stream(s) RTSP del NVR y los re-publica simultáneamente como HLS y/o WebRTC. Soporta autenticación por path, así que cada pantalla de cámara puede tener su propia URL protegida.
- **Cloudflare Tunnel** (gratis en el plan free): resuelve exactamente la restricción que describiste — el equipo del local abre la conexión hacia Cloudflare (saliente), nunca hace falta abrir puertos en el router ni tener IP pública fija. Funciona incluso si el proveedor de internet del local usa CGNAT.
- Con esto, la pantalla P-11 dejaría de embeber el iframe de HikConnect (dependiente de la política de terceros de Hikvision) y pasaría a embeber un player HLS/WebRTC nativo (`video.js` + `hls.js`), apuntando a la URL pública del túnel.
- Esta arquitectura reemplaza además la necesidad de credenciales HikConnect por usuario/rol — solo hace falta la credencial admin del NVR y no depende de la cuenta cloud de Hikvision.

**Requisito nuevo, no relevado hasta ahora:** hace falta un equipo que quede **encendido 24/7 en el local** corriendo el gateway (MediaMTX + cloudflared). ✅ **Confirmado por el cliente (2026-08-10): ya hay un equipo siempre prendido en el local** (candidato: la PC donde corre Ayres POS, a confirmar cuál puntualmente) — se reutiliza, **sin costo de hardware adicional** para este módulo. Solo instalación de software (MediaMTX + cloudflared) sobre ese equipo existente.

#### Datos pendientes de relevar

| Campo | Estado |
|---|---|
| Marca/modelo exacto del NVR (confirmar si es Hikvision u otra marca — cambia el formato de URL RTSP) | 🟡 Marca confirmada (Hikvision — dato de Hik-Connect: Device Domain/Serial `AA5187560`, alias "KOI"), **modelo puntual aún no** — ese código de 9 caracteres es el identificador corto de registro en Hik-Connect, no el serial completo de fábrica que trae el modelo embebido. Pendiente: etiqueta física del equipo, o `System > System Information` en la web local del NVR, o SADP Tool en la LAN del local (el cliente ya tiene acceso por cable) |
| Cantidad de cámaras / canales conectados al NVR | ⏳ |
| IP del NVR en la LAN aislada | ⏳ |
| Usuario y contraseña admin del NVR (para armar las URLs RTSP) | ⏳ |
| Equipo que corre el gateway 24/7 | ✅ Ya existe en el local, se reutiliza — sin costo de hardware |
| Velocidad de subida de la conexión a internet del local (el streaming consume ancho de banda de subida constante mientras haya un visor conectado) | ⏳ |
| ¿El local ya tiene o puede conseguir un dominio/subdominio propio para el túnel? (KOI ya tiene dominio del sistema web, se puede reutilizar) | ⏳ |

> Nota: con esta arquitectura, HikConnect (cuenta cloud) deja de ser un requisito — se puede dar de baja como dependencia si el cliente lo prefiere, o mantenerse en paralelo como respaldo. A confirmar con el cliente en la próxima ronda.

---

### 10.4 Resumen de alcance y pendientes Etapa 2

| Módulo | Necesidad cliente | Estado relevamiento | Bloqueante principal |
|---|---|---|---|
| **E2-01** Ventas Ayres | Carga automática de ventas desde POS | ✅ Relevado | Credenciales + decisión opción A/B |
| **E2-02** Fichador QuickPass | Pantalla de asistencia de empleados | ✅ Relevado — Análisis/Diseño/Arquitectura/Presupuesto cerrados (2026-08-10, ver §11 y `2-disenador-funcional.md`/`3-arquitecto-mvc.md`/`4-presupuestador.md`) | Token de API QuickPass |
| **E2-03** Cámaras NVR/RTSP | Streaming nativo de cámaras vía NVR local | 🟡 Arquitectura de integración investigada (2026-08-10); hardware del gateway resuelto (equipo ya existente, sin costo adicional) — faltan datos puntuales del NVR | Marca/modelo, IP y credenciales admin del NVR |

> **Condición para iniciar Etapa 2**: resolver los pendientes bloqueantes de al menos uno de los módulos para poder presupuestar y diseñar. Hasta entonces, la Etapa 2 queda en espera.

#### Contactos relevados
| Entidad | Contacto | Para |
|---|---|---|
| MaxiSistemas S.R.L (Ayres) | Sin dato aún | Credenciales MySQL + documentación API |
| QuickPass | `desarrollo@quickpassweb.com` | Documentación API + token del cliente |
| Encargado del local | — | Credenciales admin QuickPass + cámaras |
| Propietario del local | — | Credenciales NVR + HikConnect |

---

## 11. Análisis funcional — Módulo E2-02 "Fichador de empleados" (Etapa 2 en curso)

> Fecha: 2026-08-10. Estado: ✅ ANÁLISIS CERRADO — habilita Diseño. Cascada disparada a pedido explícito del dueño del estudio: avanzar Análisis→Diseño→Arquitectura→Presupuesto ahora, usando el relevamiento de §10.2 como Discovery (sin repetir visita). **Implementación queda bloqueada** hasta que el cliente entregue el token de API y las credenciales admin de QuickPass (pendientes, ver §10.2).

### 11.1 Alcance funcional

**Incluido:**
1. Pantalla "Fichador" (solo Administrador) con dos vistas: asistencia del día actual y consulta por rango de fechas.
2. Filtro por rango de fechas (`daterangepicker`, estándar del proyecto) + filtro por empleado.
3. Resumen de horas trabajadas por empleado en el rango consultado.
4. Listado de empleados registrados en QuickPass con su estado (activo/inactivo en el dispositivo).
5. Los datos se consultan **en vivo** contra la API de QuickPass en cada visita a la pantalla — no se persisten localmente en esta etapa (decisión de diseño, ver §11.4).

**Excluido (de esta iteración):**
- Alta/baja/edición de empleados o huellas — eso se gestiona en el panel de QuickPass/hardware ZKTeco, fuera del sistema web.
- Acceso de Inversores a estos datos (dato de personal, exclusivo del Administrador — mismo criterio que el resto del sistema).
- Persistencia histórica local de fichadas (si en el futuro se requiere reporting offline o cruce con nómina, es una iteración posterior con migración EF).
- Notificaciones o alertas de ausentismo (fuera de alcance salvo pedido explícito).

### 11.2 Casos de uso (formalizados desde §10.2)

| # | Caso de uso | Actor | Resumen |
|---|---|---|---|
| CU-E2-02a | Ver asistencia del día | Administrador | Pantalla muestra las fichadas de entrada/salida del día actual por empleado, consultando la API de QuickPass en el momento. |
| CU-E2-02b | Consultar rango de fechas | Administrador | Filtro por empleado (opcional) + rango de fechas (`daterangepicker`); el sistema calcula y muestra el resumen de horas trabajadas por empleado en ese rango. |
| CU-E2-02c | Ver empleados registrados | Administrador | Listado de empleados activos en QuickPass con su estado, traído en vivo desde la API. |

### 11.3 Criterios de aceptación (verificables)

- **CU-E2-02a**: al abrir la pantalla, se listan todas las fichadas del día actual agrupadas por empleado (entrada/salida); si un empleado no fichó aún, se muestra su fila con estado "Sin fichada hoy" (nunca una fila vacía sin explicación).
- **CU-E2-02b**: dado un rango de fechas y un empleado (o "todos"), las horas trabajadas mostradas = suma de los intervalos entrada→salida dentro del rango; fichadas incompletas (entrada sin salida) se marcan explícitamente como "Turno abierto / incompleto", no se computan como 0 ni se ocultan.
- **CU-E2-02c**: el listado de empleados coincide 1 a 1 con los empleados activos configurados en el panel de QuickPass al momento de la consulta (sin caché mayor a lo declarado en Arquitectura).
- Si la API de QuickPass no responde o el token es inválido/expiró, la pantalla muestra un mensaje claro de error (SweetAlert2) sin romper el layout, y loguea el fallo (sin exponer el token en el log).

### 11.4 Decisión de diseño: sin persistencia local (a confirmar en Arquitectura)

El relevamiento (§10.2) ya proponía "sin nuevas tablas, datos en tiempo real". Se ratifica en Análisis: QuickPass es la fuente de verdad y el volumen de consulta es bajo (pantalla de uso ocasional del Administrador) — persistir localmente agregaría una migración EF y un mecanismo de sincronización sin necesidad funcional confirmada por el cliente todavía. Si en el futuro se pide cruce con nómina o reporting offline, se reestima como iteración nueva con migración EF (gatillo de reestimación).

### 11.5 Riesgos y dependencias (actualizado)

- **R-E2-02 (bloqueante para Implementación):** token de API y credenciales admin del local en QuickPass — el cliente confirmó (2026-08-10) que todavía no las tiene. Análisis, Diseño, Arquitectura y Presupuesto pueden cerrarse igual (no dependen del token); Implementación no puede arrancar sin él.
- Riesgo técnico: sin Swagger/documentación formal de endpoints más allá de lo relevado (`desarrollo@quickpassweb.com` como contacto) — si el mapeo real de la API difiere de lo asumido, gatillo de reestimación (regla estándar de 28-estimacion-avanzada).
- Dependencia del cliente: token de API QuickPass, credenciales admin del local, confirmación de qué endpoints expone la API para asistencia y empleados.

### 11.6 Banderas (módulo E2-02)

| Bandera | Valor |
|---|---|
| Migración EF | No |
| Integración externa | Sí — API REST QuickPass v4, Bearer token estático |
| Máquina de estados | No |
| Migración de datos | No (consulta en vivo, sin carga inicial) |

---

## 12. Análisis funcional — Sprint UX/UI Inversor + fixes (Agosto 2026)

> Fecha: 2026-08-12. Estado: ✅ ANÁLISIS CERRADO — 9 ítems, sobre sistema en producción, sin migración EF. Pedido directo del dueño del estudio. Ambigüedades resueltas en el chat antes de cerrar: alcance por rol (solo Inversor, no toca el Dashboard del Administrador) y estructura final de pantallas (3, no 2).

### 12.1 Ítems del sprint

1. **Pantalla "Mes actual" (nueva, solo Inversor)** — reemplaza el link "Dashboard" que ve el Inversor. Sin selector de mes/año (siempre el mes/año actual del sistema). Título dinámico: "Rendimiento {Mes} {Año}" (ej. "Rendimiento Agosto 2026"). KPIs: Ventas Totales, Ticket Promedio, Cantidad de Tickets, % de venta por canal (Mostrador / Salón / Delivery — mapea al campo ya existente "Pedidos"). El Administrador no ve este cambio — sigue entrando a su Dashboard actual sin ninguna modificación.
2. **"Dashboard Histórico" (relabel, solo Inversor)** — mismo controller/vista/URL del Dashboard actual (`/Dashboard`), sin tocar su contenido. Solo cambia el texto del link del sidebar: para el rol Inversor pasa a decir "Dashboard Histórico" en vez de "Dashboard". Para Administrador el link sigue diciendo "Dashboard".
3. **Rol nuevo "Encargado"** — decidido en el chat (vs. reutilizar `Empleado`): rol Identity nuevo, sembrado junto a los 5 existentes. Ve ÚNICAMENTE la opción de menú "Fichador" — ninguna otra pantalla, ni Dashboard, ni Mi Inversión, ni nada del resto del sistema.
4. **Fix del bug de puntos ("Wang")** — **no es una corrección de datos, es un bug de código.** Investigado en el chat (ver `trazabilidad.md` 2026-08-12): `InversionesService.AsignacionesVigentesQuery` no descarta las vigencias superadas de un mismo inversor, a diferencia de `EstadoResultadosService` (que sí lo hace correctamente con `GroupBy` + `OrderByDescending().First()` en dos lugares — el cálculo de liquidaciones **nunca estuvo mal**, solo la pantalla de reporte de Puntos). El fix es puramente de código: aplicar el mismo patrón de deduplicación por inversor que ya usa `EstadoResultadosService`. Con el fix, la pantalla de Puntos muestra el total correcto (95, no 102) para cualquier período desde abril 2025, y Wang aparece una sola vez con sus 8 puntos vigentes. **No se borra ni modifica ninguna fila de `asignacionpuntos` en producción.**
5. **Reparto General — simplificación** — la tabla deja de listar una columna por inversor (hoy: Período, Ventas, Resultado, Util/Punto, Util/Punto USD + N columnas de inversores + Estado). Queda solo el reparto general del período: Período, Ventas, Resultado, Utilidad/Punto, Utilidad/Punto USD, Estado — sin ningún desglose individual por inversor en esta pantalla (el desglose individual sigue disponible en Liquidaciones y en Mi Inversión de cada uno).
6. **Vista Anual del Estado de Resultados → "Historial de Resultados"** — cambia el título de la página (hoy literal "Estado de Resultados {año}") y el texto del link del sidebar (hoy "Vista Anual ER"), ambos a "Historial de Resultados" (manteniendo el año donde corresponda, ej. "Historial de Resultados 2026"). Aplica a todos los roles que hoy ven esa pantalla (Admin, SuperUsuario e Inversor) — este ítem no está acotado a Inversor.
7. **Notificaciones — módulo de composición nuevo** — el sistema in-app YA EXISTE de punta a punta (entidad `Notification`, `INotificationService`, `NotificationsController`, campanita+dropdown en el layout) pero hoy **nada lo usa para crear notificaciones** — no hay pantalla donde el Admin componga y envíe una. Se agrega: (a) opción de menú "Notificaciones" persistente en el sidebar (hoy solo es alcanzable desde la campanita); (b) pantalla nueva donde el Admin arma una notificación (asunto/mensaje) dirigida a **todos los usuarios de un rol** (combo de rol → carga automáticamente la lista de usuarios con ese rol asignado, con la posibilidad de sacar usuarios puntuales de esa lista antes de enviar) — no se pide targeting usuario-por-usuario desde cero, es "por rol con exclusión manual"; (c) dos checkboxes independientes: **Enviar por correo** (reutiliza `IEmailService` ya existente) y **Crear notificación in-app** (reutiliza `INotificationService.CreateAsync` ya existente, hoy sin ningún llamador) — pueden marcarse uno, el otro, o los dos.
8. **Mi Inversión — sacar puntos propios** — se quita la columna "Puntos" de la tabla de historial (`#tablaHistorial`, `Views/MiInversion/Index.cshtml`). El inversor ya conoce su propia cantidad de puntos, no hace falta repetirla en cada fila del historial.
9. **Mi Inversión — reformateo de la tabla de historial** (mismo `#tablaHistorial`): la tabla deja de ser ordenable por click en cualquier columna (se saca la interacción, no solo se fija un orden). Se separa la columna "Período" en dos columnas nuevas al principio de la tabla: **Año** y **Mes** (el DTO `MiInversionFilaDto` ya tiene `Anio`/`Mes` como enteros separados, no hace falta tocar el modelo de datos). El mes se muestra en palabras, con la primera letra en mayúscula (ej. "Agosto", no "agosto" ni "08"). El orden (fijo, no interactivo) es Año descendente y, dentro del año, Mes descendente por número de mes (mes 8 antes que mes 7, no alfabético). Se saca la columna "TC" (Tipo de Cambio) — queda sin uso una vez que Neto U$D ya muestra el valor convertido.
10. **Fix global — importes cortados a una segunda línea por el signo "$"** — reproducido en Dashboard, Mi Inversión, Reparto General (y potencialmente cualquier otra tabla con importes) cuando la columna se angosta: el espacio entre "$"/"U$D" y el número permite el salto de línea del navegador ahí. Se corrige con una regla CSS **global** (no parche por pantalla) en el design system compartido (`olvidata-theme.css`), y se documenta como regla de implementación obligatoria en `Agentes-IA` (`.github/instructions/`) para que los proyectos nuevos del estudio no repitan el problema — mismo criterio que ya se usó con el bug de tema oscuro de KOI (Etapa 9), que también se generalizó al design system compartido.

### 12.2 Alcance excluido
- Dashboard del Administrador: sin cambios.
- Sin nuevas tablas ni migración EF — todo el sprint reutiliza entidades/servicios ya existentes.
- Sin borrado de datos de producción (ítem 4 es un fix de código).

### 12.3 Criterios de aceptación (verificables)
- **Ítem 1**: un usuario Inversor que entra al sistema ve "Mes actual" en el sidebar (no "Dashboard"); la pantalla muestra el mes/año en curso sin ningún selector; el título coincide con el mes/año real del servidor.
- **Ítem 2**: el mismo usuario Inversor, al entrar a "Dashboard Histórico", ve exactamente el mismo contenido que hoy ve en "Dashboard" (sin regresión); un Admin sigue viendo "Dashboard" como texto de link.
- **Ítem 3**: un usuario con rol único "Encargado" que inicia sesión solo puede navegar a `/Fichador`; cualquier otra URL del sistema (Dashboard, Mi Inversión, etc.) le devuelve acceso denegado.
- **Ítem 4**: la pantalla de Puntos, para el período actual (o cualquiera desde abril 2025), muestra Total Asignado = 95 y a Wang una sola vez con 8 puntos. Una liquidación ya cerrada de un período anterior a abril 2025 no cambia sus valores históricos.
- **Ítem 5**: la tabla de Reparto General no tiene ninguna columna con nombre de inversor.
- **Ítem 6**: el texto "Vista Anual ER" no existe más en el sidebar; el título de la página dice "Historial de Resultados {año}".
- **Ítem 7**: el Admin elige un rol, ve la lista de usuarios de ese rol precargada, puede sacar a alguno puntual, tilda "correo"/"in-app"/ambos, envía — cada usuario que quedó en la lista recibe lo que corresponda según los checks tildados.
- **Ítem 8/9**: la tabla de historial de Mi Inversión no reacciona a clicks de header; muestra Año y Mes como columnas separadas antes que el resto; no tiene columnas Puntos ni TC; el orden visual es año desc, mes desc dentro del año.
- **Ítem 10**: ningún importe con signo "$"/"U$D" se corta en dos líneas al angostar la ventana, en ninguna pantalla del sistema.

