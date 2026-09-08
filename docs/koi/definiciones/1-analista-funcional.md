# 1 - Analista funcional — Proyecto KOI

> Memoria acumulativa del agente analista funcional.
> Etapa: Discovery + Análisis + Sesión de definición + Cierre P-A01→P-A07. Estado: ✅ ANÁLISIS FUNCIONAL CERRADO (Etapa 1) — todas las hipótesis y preguntas respondidas · cascada a diseño, arquitectura y presupuesto habilitada. Módulo E2-02 (Fichador) con Análisis cerrado en §11 — Implementación bloqueada por token QuickPass pendiente.
> Fecha: 2026-06-11. Última actualización: 2026-08-13 — Análisis funcional de dividendos/recupero en pesos en Mi Inversión cerrado (§13), cascada a Diseño/Arquitectura/Presupuesto disparada.

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
| Documentación/mapeo de endpoints API Ayres | Desarrollador → MaxiSistemas | ✅ **RESUELTO 2026-08-13** — documentación pública encontrada y analizada, ver §10.1.1 |
| Decisión: Opción A (API) vs Opción B (MySQL directo) | Desarrollador + cliente | ✅ **RESUELTO** — Opción A (API REST). La documentación cubre los 9 KPIs pedidos; el acceso directo a MySQL queda descartado (rompía encapsulamiento y exigía credenciales que nunca llegaron) |
| Contraseña MySQL usuario `pop10` o `root` | Desarrollador → MaxiSistemas | ❌ Ya no aplica (se descartó la Opción B) |
| Credenciales de login de la API (email + password + idsucursal) | Cliente / MaxiSistemas | ⏳ **Nuevo bloqueante principal** |
| Acceso de red al endpoint de la API desde el sistema web externo | Técnico de red del local | ⏳ — ver §10.1.1, se resuelve con el mismo gateway/túnel ya diseñado para las cámaras (E2-03) |

---

#### 10.1.1 Research de la API REST de Ayres (2026-08-13)

Fuente: documentación oficial pública de **Ayres POP — App Servidor**, `https://ayresit.ar/documentacion/pos/api/index.html` (analizadas todas las secciones del índice + changelog).

**Autenticación:** `POST http://{ENDPOINT}/login` con body JSON `{ email, pass, idsucursal }` (o `cod_cli`, uno de los dos, nunca ambos). Devuelve `content.tokenAccess` (JWT) y `content.aliveTime` (segundos de vigencia, ej. 3599 ≈ 1 hora). El token se envía luego como `Authorization: Bearer {token}`. **Diferencia clave contra QuickPass (E2-02):** acá el token EXPIRA (~1h) — hace falta lógica de renovación automática, no alcanza con una key estática en configuración.

**Convención de respuestas:** todas devuelven `{ resultCode, resultDescription, content }`. Códigos: `SUCCESS`, `UNAUTHORIZED_ACCESS`, `INVALID_PARAMS`, `LONG_PARAMS`, `ERROR_INTERNO`.

**Restricción crítica de todos los endpoints con rango de fechas: máximo 10 días por consulta** (formato `yyyy-MM-dd`). Para un mes completo hacen falta **3 o 4 llamadas encadenadas** y agregar del lado nuestro. Es el mismo patrón que ya se resolvió en el Fichador (QuickPass, límite de 31 días), pero más estricto.

**Endpoint principal — `GET /ventas`** (`fechaContableDesde`, `fechaContableHasta`, `estado?`): devuelve **detalle venta por venta**, con los campos que importan para los KPIs:
- `facturaMontoTotal` (decimal) — importe de la venta
- `cantidadConsumidores` (int) — **cubiertos/comensales** (el dato que hoy se carga a mano)
- `items[]` — array por artículo con `cantidad`, `precioUnitario`, `montoConIVA`
- `sectorTipo` (string) — canal de venta (ej. `"ME"` = mostrador) → alimenta el desglose Salón/Delivery/Mostrador que hoy se carga a mano
- `fechaContable`, `fechaHoraApertura`, `fechaHoraCierre`

**Endpoint complementario — `GET /articulosvendidos`** (`fechaDesde`, `fechaHasta`): devuelve cantidades **ya agregadas por fecha + sectorTipo + artículo** (`cantidadPropia`, `cantidadEnCombo`, `montoConImpuestos`). Más liviano que recorrer los `items[]` de cada venta si solo se necesitan totales de unidades.

**`GET /estadisticas/fullinvoicebydate`** (`from`, `to`): detalle fiscal comprobante por comprobante (cabecera + ítems + formas de cobro). **No sirve para totales** — es aún más granular; se descarta para este alcance.

**No existe ningún endpoint de KPIs/agregados/resúmenes** (verificado contra el índice completo y el changelog): toda la agregación queda del lado del sistema KOI.

**Mapeo de los 9 KPIs pedidos → todos obtenibles desde `GET /ventas`:**

| KPI | Cálculo |
|---|---|
| Importe total de ventas | Σ `facturaMontoTotal` |
| Ticket promedio | Σ `facturaMontoTotal` ÷ cantidad de ventas |
| Cantidad de ventas | count de ventas |
| Cantidad de ventas por día (promedio) | count ÷ días del período |
| Ítems promedio por venta | Σ `items[].cantidad` ÷ count de ventas |
| Total de ítems vendidos | Σ `items[].cantidad` (o vía `/articulosvendidos`) |
| Promedio de cubiertos por día | Σ `cantidadConsumidores` ÷ días del período |
| Total de cubiertos | Σ `cantidadConsumidores` |
| Venta promedio por cubierto | Σ `facturaMontoTotal` ÷ Σ `cantidadConsumidores` |

**Conclusión:** la API alcanza para automatizar **todo** lo que hoy el Administrador carga a mano en Indicadores de Venta y en el desglose por canal del Estado de Resultados — no hace falta pedirle a MaxiSistemas ningún endpoint nuevo (el borrador de mensaje que se había preparado para eso queda sin efecto).

**Bloqueante que queda (el mismo de siempre, pero con solución ya diseñada):** la URL base es `http://{ENDPOINT}` — un endpoint por instalación, que corre en el servidor local del restaurante (puerto 8510 según el relevamiento original). El sistema KOI está hosteado afuera, así que necesita alcanzar esa API. **Se resuelve con exactamente la misma infraestructura ya diseñada para las cámaras (§10.3): el equipo 24/7 del local + Cloudflare Tunnel** — un solo túnel saliente puede exponer tanto el stream de las cámaras como la API de Ayres, sin abrir puertos en el router ni tocar la red aislada. Esto convierte dos bloqueantes de infraestructura separados en una sola pieza compartida.

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

#### Variante confirmada (2026-08-13): cámaras nuevas en la red normal del local, no en la LAN aislada

El cliente decidió que las cámaras IP nuevas se conectan a la **red normal del local** (la que ya sale a internet), no a la LAN aislada de vigilancia donde está el NVR actual. Esto simplifica bastante el armado:

- El gateway (MediaMTX + cloudflared) se instala en el mismo equipo 24/7 ya confirmado (§ arriba), pero ahora conectado a la red normal — **no hace falta ningún acceso a la LAN aislada** para este flujo.
- Se destraba la dependencia de marca/modelo/IP/credenciales del NVR actual **para este alcance puntual** — esos datos siguen siendo necesarios solo si más adelante se quiere integrar también las cámaras existentes detrás del NVR (queda como variante separada, no bloqueante para avanzar con las cámaras nuevas).
- Sigue aplicando todo lo demás ya definido: RTSP de la cámara → MediaMTX (HLS/WebRTC) → Cloudflare Tunnel → player nativo en P-11, sin exponer puertos en el router.
- Nueva contrapartida a tener presente: la red normal del local pierde el aislamiento que tenía la red de vigilancia (si esa separación era una decisión de seguridad deliberada, el cliente debe confirmarla explícitamente — no es una regresión técnica, es una decisión de negocio que ya tomó).

**Nuevos pendientes (reemplazan a los del NVR para esta variante):**

| Campo | Estado |
|---|---|
| Marca/modelo de las cámaras IP nuevas a comprar (recomendado: cualquier cámara con RTSP/ONVIF estándar — Hikvision mantiene el mismo formato de URL ya investigado, pero no es excluyente) | ⏳ |
| Cantidad de cámaras nuevas y ubicación en el local | ⏳ |
| Confirmación de que el equipo 24/7 ya identificado está en la misma red donde van a conectarse las cámaras nuevas (debería ser así por default, pero a verificar) | ⏳ |
| Decisión del cliente: ¿reemplaza a futuro las cámaras del NVR, o quedan ambos sistemas en paralelo (NVR aislado + cámaras nuevas en red normal)? | ⏳ |

---

### 10.4 Resumen de alcance y pendientes Etapa 2

| Módulo | Necesidad cliente | Estado relevamiento | Bloqueante principal |
|---|---|---|---|
| **E2-01** Ventas Ayres | Carga automática de ventas desde POS | ✅ Relevado + **API documentada y analizada (2026-08-13, §10.1.1)** — los 9 KPIs pedidos son 100% obtenibles vía `GET /ventas`; opción MySQL directo descartada | Credenciales de login de la API + acceso de red (mismo túnel que E2-03) |
| **E2-02** Fichador QuickPass | Pantalla de asistencia de empleados | ✅ Relevado — Análisis/Diseño/Arquitectura/Presupuesto cerrados (2026-08-10, ver §11 y `2-disenador-funcional.md`/`3-arquitecto-mvc.md`/`4-presupuestador.md`) | Token de API QuickPass |
| **E2-03** Cámaras IP (red normal) | Streaming nativo de cámaras nuevas, en la red normal del local | 🟡 Arquitectura simplificada confirmada (2026-08-13): cámaras nuevas fuera de la LAN aislada, sin depender del NVR actual — falta elegir marca/modelo y cantidad de cámaras | Elección de cámaras a comprar |

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

---

## 13. Análisis funcional — Mi Inversión: dividendos y recupero en pesos (Agosto 2026)

> Fecha: 2026-08-13. Estado: ✅ ANÁLISIS CERRADO. Pedido directo del dueño del estudio: agregar a Mi Inversión el desglose de dividendos cobrados y recupero también en pesos, no solo en dólares (hoy la pantalla solo muestra la valuación en USD).

### 13.1 Investigación previa (evita implementar sobre un supuesto equivocado)

Se investigó la hipótesis inicial de que liquidaciones "Pagada" sin conversión a USD (`NetoUsd` nulo) quedaban excluidas del cálculo actual — **descartada con datos reales**: las 264 liquidaciones "Pagada" en producción tienen `NetoUsd`/`TipoCambio` cargados sin excepción, así que hoy no hay dinero "invisible" en el cálculo existente.

Segunda hipótesis evaluada (moneda real en la que se pagó cada liquidación, pesos vs. dólares en mano) — **el cliente confirmó explícitamente que NO es esto**, prefiere seguir con la idea original.

### 13.2 Definición confirmada

- **Dividendos cobrados (pesos)**: suma de `Neto` (pesos) de todas las liquidaciones `Pagada` del inversor — sin conversión, dato ya existente por liquidación.
- **Recupero (pesos)**: suma, liquidación por liquidación, de `Neto ÷ (CapitalAportadoUsd × TipoCambio de esa liquidación) × 100`. Si alguna liquidación pagada no tuviera `TipoCambio` cargado (no ocurre hoy en producción, pero puede ocurrir a futuro), esa liquidación se excluye del cálculo de este % puntual, sin afectar el total de "Dividendos cobrados (pesos)" (que no depende de TC).
- **Aclaración explícita ya dada al cliente y aceptada**: con los datos actuales, este número va a salir prácticamente idéntico al "Recupero (dólares)" ya existente (misma cuenta, mismo TC por liquidación) — no es un bug, es la naturaleza de la fórmula elegida. Queda igual como métrica preparada para cuando exista alguna liquidación sin conversión limpia.

### 13.3 Alcance

- Aplica a Mi Inversión (P-10), mismo criterio de visibilidad que hoy (Inversor ve la propia, Admin puede ver cualquiera).
- No aplica a ninguna otra pantalla (Dashboard, Reparto General, etc.) — es puntual a Mi Inversión.
- Sin migración EF — todos los datos necesarios (`Neto`, `TipoCambio`, `CapitalAportadoUsd`) ya existen.

### 13.4 Criterios de aceptación

- La pantalla Mi Inversión muestra, junto a "Dividendos cobrados" y "Recupero %" (USD, ya existentes), dos KPIs nuevos: "Dividendos cobrados (pesos)" y "Recupero (pesos)".
- Los valores coinciden con la fórmula de §13.2, verificable a mano contra el historial de liquidaciones del propio inversor.
- No cambia ningún valor de los KPIs en USD ya existentes.

---

## 14. Análisis funcional — Sprint de correcciones y catálogo real (Agosto 2026)

> Fecha: 2026-08-13. Estado: ✅ ANÁLISIS CERRADO — 6 ítems. Tres definiciones ambiguas resueltas con el dueño del estudio antes de cerrar (rubros, edición de cerrados, diseño del recupero). Incluye **migración de datos sobre producción** (ítem 4), único ítem de riesgo alto del lote.

### 14.1 Ítems

**1. Nombre del remitente de los correos.** Hoy los mails del sistema salen con `FromName = "Koi Dumplings - Olvidata"` (`appsettings.Production.json`, sección `Olvidata_Email.Smtp`). Pasa a **"KOI Dumplings"** — sin la marca del proveedor, que no corresponde en un mail que reciben los inversores del cliente.

**2. Mi Inversión — recupero mes a mes (corrección + ampliación de §13).** El recupero debe verse calculado sobre los valores de cada mes cerrado, cada uno con el TC de su propio mes. **Hallazgo:** eso ya ocurre a nivel dato — la columna "Renta" de cada fila del historial ES exactamente la contribución de recupero de ese mes (`NetoUsd ÷ CapitalAportadoUsd × 100`, y `NetoUsd` ya fue calculado con el TC del mes cerrado). Lo que falta no es el cálculo mensual sino **verlo acumulado y ver su progresión**. Decisión tomada: se agrega (a) columna "Recupero acumulado %" por fila del historial y (b) un gráfico de evolución del recupero acumulado. No se duplica la columna "Renta" con otro nombre — sería el mismo número dos veces.
  - Supuesto explícito a validar con el cliente: el acumulado sigue contando **solo liquidaciones Pagada** (plata efectivamente recibida = recuperada), no todas las de meses cerrados. Hoy es indistinto en la práctica (264 de 265 liquidaciones están Pagada), pero es una definición de negocio, no técnica.

**3. Editar estados de resultados de meses cerrados.** Hoy el sistema bloquea toda edición de un período cerrado (`EstadoResultadosService`, guards en `GuardarVentas` y `GuardarConceptoGastoAsync`). **Esto revierte una decisión explícita previa** (D-04 y P-A04 de la sesión de definición de junio: "el período no puede reabrirse" / "no hay mecanismo técnico de corrección post-cierre, se gestiona operativamente"). El cliente ahora necesita corregir errores de carga.
  - Decisión tomada: el Admin puede editar ventas y gastos de un período cerrado. Al hacerlo, **se recalculan automáticamente las liquidaciones en estado Pendiente** de ese período; **las ya marcadas Pagada quedan intactas** y el sistema avisa en pantalla cuáles no se tocaron.
  - Toda edición sobre un período cerrado queda auditada (quién, cuándo, qué valor cambió) — es plata de inversores reales, no puede quedar sin rastro.

**4. Catálogo real de rubros y subgrupos.** El catálogo cargado hoy es el **genérico del seed inicial** (6 rubros: "Impuestos y Cargas", "Costo de Mercadería (CMV)", "Personal", "Servicios", "Alquileres", "Gastos Generales" / 21 subgrupos), no la estructura real del cliente. La estructura real está en `KoiDumplings/docs/Estado de Resultados KOI - Agosto.pdf` (agosto 2026): **8 rubros y ~40 subgrupos**:
  | Rubro | Subgrupos |
  |---|---|
  | Costo Mercadería Vendida | Mercadería KOI, Barriles, Verdulería, Bebidas |
  | Fee de Franquicia | Regalías (3 %), Cánon de publicidad (2,5 %) |
  | Sueldos y CCSS | Sueldos, Cargas Sociales, Sindicato |
  | Gastos Varios | Almacén, Aceite, Cristalería & Equipamiento, Insumos Barra / Hielo, Papelería & Descartables, Limpieza, Fletes y Transporte, Pastillas Horno Rational, Mantenimiento y Reparaciones |
  | Alquiler | (sin subgrupos — importe directo) |
  | Servicios | Luz, Gas, Internet, Agua, Alarma, Software de Ventas, Máquina AQA, Sanitización de Canillas, Fumigación, Contador, Seguro Integral de Comercio, Sistema de Reservas Online, Mantenimiento Cuenta Bancaria, Comisiones Tarjetas / Merc Pago, Comisiones PedidosYa / Rappi |
  | Impuestos | IVA, Ingresos Brutos, Imp a los débitos y créditos, Anticipo de Ganancias, Publicidad y Propaganda, Tasa Insp. Seg e Hig municipal, Ocupación del Esp Público, Serv Urbanos Municipales, Recolección Basura (Esur) |
  | Previsión y Reservas | Fondo de juicios laborales (1 %), Reposición maquinaria (1 %) |
  - **Decisión tomada: reemplazar el catálogo Y remapear los 373 gastos históricos** a la estructura nueva donde haya equivalencia, para que toda la historia quede bajo una sola estructura. Es migración de datos sobre producción con valores ya conciliados al centavo → exige backup previo y verificación de que los totales por período no cambian (ver Arquitectura para el mapeo propuesto y los casos sin equivalencia clara).
  - Cambio de tipo de concepto a definir en el mapeo: el PDF muestra Regalías (3 %), Cánon (2,5 %), Fondo de juicios (1 %) y Reposición maquinaria (1 %) como porcentajes (siguen calculados), pero IIBB, comisiones de tarjeta, débitos/créditos y tasa municipal aparecen como **importes cargados a mano**, no como % — hoy están configurados como calculados.

**5. Importación de Excel recurrente.** El cliente va a seguir usando el Excel en paralelo y quiere poder importarlo cuando haga falta. **Hallazgo: la funcionalidad ya existe** (`ImportacionInicialController` con descarga de plantilla, validación previa e importación; pantalla visible solo para SuperUsuario) y **ya es idempotente** — al reimportar, todo lo que ya existe se omite con una advertencia (`"Período 2026/08 ya existe — se omitirá"`). La limitación real: **omite en vez de actualizar**, así que hoy no sirve para corregir un período ya importado, solo para agregar nuevos. Eso es lo que hay que resolver.
  - **Los archivos Excel no están disponibles**: no hay ningún `.xlsx` en el repositorio ni en la memoria del proyecto. Los Excel originales se usaron en la migración de julio pero nunca quedaron versionados. Pendiente del cliente/dueño del estudio conseguirlos de nuevo.

**6. Reparto General — orden de los meses.** La tabla ordena por el texto del período ("Agosto 2026"), o sea alfabéticamente por nombre de mes. Debe ordenar por año y después por número de mes, descendente. El formato visible del mes no cambia. **Es exactamente el mismo bug ya corregido en Historial de Resultados** (§ trazabilidad 2026-08-13) — misma causa, misma solución.

### 14.2 Criterios de aceptación

- **1**: un mail enviado por el sistema llega con remitente "KOI Dumplings".
- **2**: en Mi Inversión, cada fila del historial muestra el recupero acumulado hasta ese mes, y un gráfico muestra la progresión; el acumulado del último mes coincide con el KPI de Recupero de arriba.
- **3**: el Admin edita un gasto de un mes cerrado y el sistema lo guarda; las liquidaciones Pendientes de ese mes quedan recalculadas con el nuevo resultado; las Pagadas conservan sus importes originales y el sistema informa cuáles no tocó; queda registro de auditoría del cambio.
- **4**: la pantalla de carga del estado de resultados muestra los 8 rubros y ~40 subgrupos del PDF; los 373 gastos históricos siguen sumando exactamente los mismos totales por período que antes de la migración (verificación obligatoria post-migración).
- **5**: reimportar un Excel de un período ya cargado actualiza los valores en vez de omitirlos, informando qué se actualizó.
- **6**: en Reparto General, agosto 2026 aparece antes que julio 2026, y 2026 antes que 2025.

### 14.3 Riesgos

- **Ítem 4 es el de mayor riesgo del lote**: toca datos financieros históricos ya validados contra los Excel fuente. Backup previo obligatorio y verificación de totales post-migración. El mapeo de los subgrupos genéricos sin equivalencia clara (Expensas, Otros gastos, Honorarios, y el "CMV" único que en la estructura nueva se abre en 4) debe revisarse con el cliente antes de ejecutarse.
- **Ítem 3 revierte una decisión de diseño previa** (D-04/P-A04). Queda documentado que fue un pedido explícito posterior del cliente, no un descuido.


---

## 15. Discovery + Análisis — Módulo E2-01 "Integración Ayres POS" (Fase 6, Septiembre 2026)

Reactivación del módulo E2-01, bloqueado desde 2026-08-13 por credenciales. El dueño del estudio aportó la credencial rotada el 2026-09-08 y **la API autentica**. Esta sección actualiza y en dos puntos **corrige** el research documental de §10.1.1, ahora que hay acceso a datos reales.

### 15.1 Estado del bloqueo

| Bloqueante de §10.1 | Estado 2026-09-08 |
|---|---|
| Documentación/mapeo de endpoints | ✅ Resuelto 2026-08-13 (§10.1.1) |
| Credenciales de login de la API | ✅ **RESUELTO** — `POST /login` devuelve `200 SUCCESS` + `tokenAccess` (JWT) y `aliveTime: 3599`. La clave anterior ahora da `401`: fue rotada. El `ERROR_INTERNO` que se había atribuido a un bug de Ayres era eso. |
| Acceso de red desde el sistema web externo | ⚠️ **CAMBIA LA PREMISA** — ver 15.2 |

### 15.2 Corrección de premisa: la API es pública, NO hace falta el túnel

§10.1.1 asumía que la API corre en el servidor local del restaurante y que el acceso se resolvería con el gateway + Cloudflare Tunnel compartido con las cámaras (E2-03). **Es falso para E2-01**: `koi.ayresit.com` resuelve a `190.245.226.181`, una IP pública, y responde desde internet sin ningún túnel. El endpoint real es `http://koi.ayresit.com:8520` (no el puerto 8510 del relevamiento original).

**Consecuencia de alcance:** E2-01 deja de depender de la infraestructura de E2-03. Se desacoplan dos módulos que estaban atados y desaparece el costo de infraestructura que se le imputaba a E2-01.

**Riesgo nuevo que lo reemplaza (R-A01, abierto):** el sistema KOI está hosteado en SmarterASP (shared hosting). Falta verificar que el servidor de producción pueda abrir conexiones **salientes al puerto 8520**, que no es estándar y suele estar filtrado en hosting compartido. **Es el único bloqueante técnico que queda y condiciona la viabilidad del módulo entero.** Debe resolverse ANTES de presupuestar: si el puerto está cerrado, el módulo vuelve a necesitar un proxy/túnel y el costo cambia.

### 15.3 Corrección de premisa: forma real de la respuesta

La respuesta viva difiere de lo que sugería la documentación. Mapeo real verificado:

- El sobre es `content.{ fechas, cantidad, ventas[] }` y **cada elemento viene anidado bajo una clave `venta`**: `content.ventas[i].venta.facturaMontoTotal`. No es una lista plana.
- Las fechas se **consultan** en `yyyy-MM-dd` pero **vuelven** en `dd/MM/yyyy`. Asimetría a contemplar en el parseo.
- Campos de KPI confirmados sobre datos reales: `facturaMontoTotal`, `cantidadConsumidores`, `sectorTipo`, `items[].cantidad`, `fechaContable`.
- Límite de 10 días confirmado: agosto 2026 requirió 4 llamadas encadenadas (1-10, 11-20, 21-30, 31).

### 15.4 Validación contra datos reales — agosto 2026

Prueba de concepto completa: se trajo agosto 2026 entero de Ayres y se comparó contra lo que el Administrador cargó a mano en ese período (hoy cerrado).

| Concepto | Cargado a mano | Ayres (real) | Desvío |
|---|---|---|---|
| **Ventas totales** | 63.131.209,00 | **63.131.109,00** | **−100,00 (−0,0002 %)** |
| Salón | 54.837.560,00 | `ME` 52.404.760,00 | +2.432.800 |
| Pedidos | 8.293.549,00 | `PE` 8.293.849,00 | −300 |
| Mostrador | 100,00 | `MO` 2.432.500,00 | −2.432.400 |
| Comensales | 1.678 | 1.735 | −57 |
| **Cantidad de ventas** | **2.000** | **1.062** | **+938 (+88 %)** |

Otros KPIs reales de agosto: ticket promedio $59.445,49 · venta por cubierto $36.386,81 · ítems totales 5.924 · ítems por venta 5,58 · ventas por día 34,26.

**Conclusión: el total cierra al centavo, el detalle no.** Tres hallazgos de calidad de dato, todos a favor de automatizar:

1. **El desglose por canal es incorrecto.** El operador sumó Mostrador dentro de Salón (`ME + MO = 54.837.260` ≈ el Salón cargado) y dejó $100 simbólicos en Mostrador. El desglose Salón/Pedidos/Mostrador de los períodos históricos **no es confiable**, y es justamente el que alimenta los indicadores por canal.
2. **La "Cantidad de ventas" está cargada casi al doble** (2.000 vs 1.062 reales). Impacta directo en el ticket promedio, que hoy se muestra subestimado ~47 %.
3. La diferencia de $100 en el total es exactamente el valor simbólico puesto en Mostrador.

**Corrección a §10.1.1:** ahí se documentó `sectorTipo "ME" = mostrador`. Los datos reales lo desmienten: `ME` son 812 ventas por $52,4 M (el grueso del restaurante) y existe un `MO` separado de 54 ventas por $2,4 M. El mapeo correcto es **`ME` = Salón (mesa), `PE` = Pedidos, `MO` = Mostrador**, y la conciliación aritmética de arriba lo confirma. Debe validarse con el cliente antes de escribirlo en código (P-A08).

### 15.5 Alcance propuesto

**Incluido:**
- `IAyresService` + cliente HTTP tipado, con login y **renovación automática de token** (vence en 3599 s).
- Chunking automático de rangos mayores a 10 días, con agregación del lado KOI.
- Cálculo de los 9 KPIs de §10.1.1 + desglose por canal vía `sectorTipo`.
- Acción "Traer ventas de Ayres" en el Estado de Resultados mensual, **con preview y confirmación explícita antes de escribir** — nunca escritura automática.
- Solo períodos **abiertos**: los meses históricos no se tocan (regla vigente del proyecto).

**Excluido:**
- Sincronización automática o programada sin intervención humana.
- Reescritura de los períodos históricos ya conciliados, incluida la corrección del desglose por canal detectada en 15.4 — es decisión del cliente, no del sistema.
- Endpoints de Compras, Caja, Stock y Datos Maestros: fuera de alcance de esta fase.

### 15.6 Criterios de aceptación (verificables)

- **CA-1**: con el período abierto, el Admin pide traer las ventas de un mes y el sistema muestra un preview con totales, desglose por canal, comensales y cantidad de ventas, **sin haber escrito nada** todavía.
- **CA-2**: al confirmar, el Estado de Resultados queda con esos valores y los conceptos porcentuales se recalculan solos.
- **CA-3**: un mes completo se resuelve en varias llamadas de ≤ 10 días sin que el usuario tenga que saberlo.
- **CA-4**: si el token vence a mitad de una importación, el sistema lo renueva y continúa sin error visible.
- **CA-5**: sobre agosto 2026, el total traído es `63.131.109,00` (tolerancia $0) y la cantidad de ventas `1.062`.
- **CA-6**: con la API caída o inalcanzable, la pantalla informa el problema y **el período queda intacto**.
- **CA-7**: intentar traer ventas sobre un período cerrado se rechaza con mensaje claro.

### 15.7 Preguntas abiertas

| # | Pregunta | Destinatario | Estado |
|---|---|---|---|
| P-A08 | ¿Confirma el mapeo `ME`=Salón, `PE`=Pedidos, `MO`=Mostrador? | Cliente | ✅ **CONFIRMADO 2026-09-08** por el dueño del estudio. Se implementa así, igual configurable (un `sectorTipo` nuevo va a "Otros" y se advierte). |
| P-A09 | El desglose por canal y la cantidad de ventas de los períodos históricos están mal cargados (15.4). ¿Se corrigen con datos de Ayres o se dejan como están? Los **totales** no cambian, así que no afecta repartos ya liquidados. | Cliente | ⏳ Abierta |
| P-A10 | ¿La importación reemplaza siempre lo cargado, o solo completa lo que está en cero? | Cliente | ⏳ Abierta |
| R-A01 | ¿El hosting de producción permite salida al puerto 8520? | Estudio (verificable) | ✅ **CERRADO 2026-09-08 — SÍ, habilitándolo en el panel. Ver 15.9 y 15.10. Módulo VIABLE.** |

### 15.8 Riesgos

- **R-A01 (RESUELTO — ver 15.10):** se habilitó la salida a `190.245.226.181:8520` desde el panel de hosting. El login real desde producción devuelve `200 SUCCESS` en 220 ms. Queda como **dependencia operativa**: la regla está atada a una IP fija; si Ayres cambia de servidor, la integración se corta y el síntoma será el mismo WSAEACCES.
- **R-A02 (medio):** la API va por **HTTP plano, sin TLS**, y la credencial viaja en el body. Exposición a intercepción en tránsito. Debe plantearse a Ayres/MaxiSistemas; no lo resuelve el código de KOI.
- **R-A03 (medio):** volumen — 1.062 ventas/mes con sus `items[]`. Conviene agregar por chunk y descartar el detalle en vez de sostener el mes entero en memoria.
- **R-A04 (bajo):** el parámetro `estado` de la venta no se filtró en las pruebas. Hay que verificar si existen ventas anuladas que no deban sumar. El total cerró al centavo, así que probablemente no las haya en agosto, pero no está probado.

### 15.9 R-A01 CERRADO — el hosting bloquea la salida al puerto 8520 (2026-09-08)

Se resolvió el bloqueante de viabilidad con una sonda desplegada en producción (`System/DiagnosticoAyres`, solo SuperUsuario, temporal). **Resultado negativo: el módulo no es viable con la infraestructura actual.**

| Destino desde el servidor de producción | Resultado |
|---|---|
| `koi.ayresit.com:8520` (Ayres) | ❌ `SocketException` WSAEACCES — *"access to a socket forbidden by its access permissions"* — en **60 ms** |
| `api.argentinadatos.com:443` (HTTPS) | ✅ `200` en 723 ms |
| `api.argentinadatos.com:80` (HTTP) | ✅ `200` en 502 ms |

**Lectura:** los 60 ms descartan un problema de red o de firewall del lado de Ayres — un puerto filtrado en tránsito da timeout, no un rechazo inmediato. WSAEACCES es el sistema operativo negando el `connect()` por política local. Y como 80 y 443 sí salen, **SmarterASP no bloquea la salida: la restringe a puertos estándar** (whitelist). La misma API responde perfecto desde una máquina de escritorio, así que la credencial y el endpoint están bien: el problema es exclusivamente el puerto de salida desde el hosting.

**Opciones para destrabarlo, en orden de conveniencia:**

1. **Pedir a Ayres/MaxiSistemas que expongan la API en 443 con TLS** (ya tienen el nombre público `koi.ayresit.com`). **Es la mejor opción: resuelve R-A01 y R-A02 de una sola vez** — habilita la conexión y elimina el viaje de la credencial en texto plano. Costo de infraestructura para el estudio: cero. Depende de un tercero.
2. **Pedir a SmarterASP que habilite la salida al 8520.** Improbable en un plan compartido, y aunque salga deja intacto R-A02 (sigue siendo HTTP plano).
3. **Relay propio**: un proceso mínimo en un host que sí alcance el 8520, expuesto por 443. Nos independiza de terceros pero **agrega infraestructura, costo mensual y un punto de falla**, y hay que presupuestarlo aparte.
4. **Cloudflare Tunnel**, la infraestructura ya diseñada para las cámaras (E2-03). Vuelve a atar E2-01 con E2-03 — justo lo que 15.2 había desacoplado — pero si E2-03 se ejecuta igual, el costo marginal es bajo.

**Impacto en el flujo:** Diseño, Arquitectura y Presupuesto **quedan frenados**. La arquitectura del módulo depende de cuál de las cuatro opciones se tome (la 1 y la 2 no agregan componentes; la 3 y la 4 agregan infraestructura y cambian la cotización). Presupuestar antes de esa definición sería cotizar sobre un supuesto.

**Nota:** el diagnóstico quedó desplegado y commiteado (`81e8928`) para poder re-verificar en un minuto cuando se resuelva el acceso. Debe eliminarse al cerrar el módulo.

### 15.10 R-A01 RESUELTO — se habilita la salida por panel (2026-09-08)

La conclusión de 15.9 ("depende de un tercero") era **incorrecta y quedó corregida el mismo día**: el panel de hosting de SmarterASP tiene una función **"Outgoing Port"** que habilita la salida del plan hacia una IP y puerto remotos concretos. La tabla estaba vacía, que es por qué solo salían los puertos habilitados por defecto.

**Medición que aisló la causa** (agregando `portquiz.net`, que acepta conexiones en cualquier puerto, para separar "bloquean el puerto" de "bloquean el destino"):

| Destino | Antes de la regla | Después de la regla |
|---|---|---|
| `koi.ayresit.com:8520` | ❌ WSAEACCES 68 ms | ✅ **`405`** (el GET de prueba contra `/login`, que solo acepta POST: la conexión llega) 434 ms |
| `portquiz.net:8520` | ❌ WSAEACCES 2 ms | ❌ WSAEACCES 2 ms |
| `portquiz.net:8080` | ✅ 200 | ✅ 200 |
| `portquiz.net:3306` | ✅ 200 | ✅ 200 |
| `:443` y `:80` | ✅ 200 | ✅ 200 |

Los puertos 8080 y 3306 salían **desde el principio**: no era una whitelist de "puertos estándar" como se dedujo en 15.9, sino que el 8520 puntualmente no estaba habilitado. Y que `portquiz.net:8520` **siga fallando** después de la regla confirma que el permiso quedó correctamente acotado a **IP + puerto**, no al puerto en general.

**Verificación funcional definitiva:** `POST /login` a Ayres **desde el servidor de producción** → `200 SUCCESS`, `tokenAccess` recibido, **220 ms**.

**Regla cargada:** IP `190.245.226.181`, puerto `8520`.

**Dependencia operativa nueva (D-A01):** la regla apunta a una **IP fija**. Si Ayres migra de servidor, la integración se corta sin aviso y el síntoma será exactamente este error. Debe quedar documentado en el manual de operación del módulo.

**R-A02 sigue abierto:** la API continúa siendo `http://` sin TLS, con la credencial en el body. Habilitar el puerto nos destrabó sin depender de terceros, pero el pedido a Ayres de exponerla en 443 con certificado mantiene sentido por seguridad. **Deja de ser bloqueante y pasa a ser tema para el cliente.**

**Estado del módulo: VIABLE.** Se levanta el freno sobre Diseño, Arquitectura y Presupuesto.

