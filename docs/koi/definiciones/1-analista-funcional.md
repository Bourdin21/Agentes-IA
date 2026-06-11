# 1 - Analista funcional — Proyecto KOI

> Memoria acumulativa del agente analista funcional.
> Etapa: Discovery + Análisis funcional. Estado: CERRADO (aprobado para diseño).
> Fecha: 2026-06-11.

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
- S3 — La utilidad a repartir es el Resultado Ejercicio del estado de resultados (mismo número, sin ajustes intermedios), como hace hoy el Excel.
- S4 — El descuento de consumos se carga como monto mensual por inversor (el detalle de cada consumo no se registra).
- S5 — Hasta 16 usuarios (1 admin + 15 inversores); pueden crecer con el plan de mantenimiento.

## 7. Banderas tempranas

| Bandera | Valor | Nota |
|---|---|---|
| Migración EF | **Sí** | Modelo de datos nuevo completo (~18 tablas). |
| Integración externa | **Sí, acotada** | Envío de correo saliente (SMTP) para la notificación de cierre. Hik-Connect es embebido (no consume API); Ayres POS declarado etapa 2. |
| Máquina de estados | **Sí, acotada** | Ciclo del período mensual (Abierto/Cerrado/Reabierto) y de la liquidación (Pendiente/Pagada). |
| Migración de datos | **Sí (excepción acordada)** | Carga inicial 2024–2026 de ambos Excel. |

## 8. Preguntas pendientes (hipótesis a validar con el cliente)

Las decisiones de cámaras (embebido Hik-Connect), históricos (incluidos) e integración Ayres (etapa 2) ya fueron confirmadas por el cliente. Quedan abiertas, sin bloquear el presupuesto:

1. **¿La utilidad a repartir admite ajustes manuales antes de liquidar?**
   - Opción A (hipótesis): se reparte exactamente el Resultado Ejercicio del mes, como el Excel.
   - Opción B (hipótesis): el Admin puede ajustar el monto a repartir (ej. retener una reserva extra un mes puntual) dejando registro del ajuste.
   - Se presupuesta con la opción A (comportamiento actual del Excel).
2. **¿Los inversores deben ver las Ventas "B" identificadas como tales?**
   - Opción A (hipótesis): el dashboard muestra ventas A y B discriminadas, como el Excel que hoy circula entre inversores.
   - Opción B (hipótesis): el dashboard muestra solo el total de ventas, sin discriminar.
   - Se presupuesta con la opción A (réplica del Excel actual).
