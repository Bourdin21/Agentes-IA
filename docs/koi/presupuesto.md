# Propuesta de desarrollo — Sistema de Gestión para Inversores KOI
**OlvidataSoft · Junio 2026**

---

## 1. Descripción general

Sistema web de gestión para la franquicia gastronómica KOI que reemplaza las planillas actuales por una plataforma profesional, accesible desde cualquier navegador (computadora, tablet o celular), con usuarios y contraseñas y dos perfiles diferenciados: el **Administrador** (inversor principal), que gestiona toda la información del local, y los **Inversores**, que consultan el estado del negocio y de su propia inversión.

El sistema cubre cuatro ejes principales:

- **Estado de resultados del local**: carga mensual de ventas y gastos por rubro, con cálculos automáticos de impuestos, comisiones y previsiones, resultado del ejercicio, rentabilidad y valores en dólares.
- **Dashboard de métricas**: el corazón de la aplicación — un tablero visual organizado en tarjetas, con gráficos analíticos, evolución histórica completa y tema claro/oscuro a elección de cada usuario.
- **Inversiones**: el esquema de puntos de cada inversor, la liquidación mensual de utilidades con descuento de consumos, y la vista personal "Mi inversión" con dividendos, recupero y rentabilidad.
- **Cámaras del local**: pantalla dedicada para ver las cámaras de seguridad a través de Hik-Connect.

El sistema se entrega **con todo el historial 2024–2026 ya cargado**, tomado de las planillas actuales y validado contra sus totales.

---

## 2. Usuarios y accesos

| Perfil | Cantidad | Qué puede hacer |
|---|---|---|
| **Administrador** | 1 | Cargar el estado de resultados, configurar el sistema, gestionar puntos y liquidaciones, crear usuarios inversores y configurar las cámaras |
| **Inversor** | Hasta 15 | Consultar el dashboard de métricas, su propia inversión y las cámaras del local |

- Cada inversor ve únicamente **su propia** información de inversión; los datos de los demás inversores no le son visibles.
- El menú se adapta al perfil: el Inversor solo ve Dashboard, Mi inversión y Cámaras.

---

## 3. Especificación funcional detallada

### 3.1 Acceso y gestión de usuarios

- Ingreso al sistema con usuario y contraseña.
- El Administrador da de alta, modifica, desactiva y restablece la contraseña de cada usuario Inversor.
- Cada usuario Inversor queda vinculado a su ficha de inversor (la que define sus puntos y su capital), garantizando que solo acceda a sus propios datos.

### 3.2 Configuración del sistema

**Rubros y subgrupos de gastos**
- El sistema se entrega con la estructura actual de la planilla ya cargada: Costo de Mercadería Vendida (Mercadería KOI, Barriles, Verdulería, Bebidas), Fee de Franquicia, Sueldos y Cargas Sociales, Gastos Varios (Almacén, Aceite, Cristalería, Papelería, Limpieza, Mantenimiento, etc.), Alquiler, Servicios (Luz, Gas, Internet, Agua, Alarma, Software de Ventas, Contador, Seguro, etc.), Impuestos, Previsión y Reservas, y Gastos Extras.
- El Administrador puede agregar, renombrar o dar de baja rubros y subgrupos. Los que tienen historial no se eliminan: se desactivan y conservan sus datos.

**Porcentajes parametrizables**
- Los conceptos que hoy la planilla calcula con fórmulas quedan parametrizados y se calculan solos: regalías (3 %), canon de publicidad (2,5 %), comisiones de tarjetas / Mercado Pago (5 %), Ingresos Brutos (3,5 %), impuesto a los débitos y créditos (1,2 %), tasa municipal de Seguridad e Higiene (1 %), fondo de juicios laborales (1 %) y reposición de maquinaria (1 %).
- Cada porcentaje define sobre qué base se aplica. Los impuestos y comisiones se calculan **únicamente sobre las ventas facturadas (Ventas "A")**; las regalías, el canon y las previsiones, sobre las ventas totales.
- Si un porcentaje cambia (por ejemplo, sube una alícuota), el cambio rige desde ese momento hacia adelante: **los meses ya cerrados conservan sus valores originales**.

**Tipo de cambio mensual**
- El Administrador carga el tipo de cambio del mes desde una **pantalla con las cotizaciones del día** (dólar oficial, blue, MEP, CCL y otros), que el sistema obtiene automáticamente de fuentes públicas. El campo se pre-carga con el **promedio blue del día** (la referencia habitual) y el Administrador puede seleccionar otra cotización o editar el valor a mano antes de guardar.
- El TC registrado es único por mes y se usa para todos los valores en dólares del sistema.

### 3.3 Estado de resultados mensual

- Pantalla de carga mensual organizada en secciones, en el mismo orden que la planilla actual.
- Carga de ventas separada en **cuatro campos**: Ventas A Salón, Ventas A Delivery, Ventas B Salón y Ventas B Delivery. Los totales (Ventas A, Ventas B, Ventas Salón, Ventas Delivery y Ventas Totales) se calculan solos en tiempo real.
- Carga de los gastos de cada subgrupo. Los conceptos porcentuales (regalías, canon, comisiones, impuestos, previsiones) **se calculan automáticamente** y se muestran como solo lectura; el IVA y los demás importes fijos se cargan a mano como hasta ahora.
- Panel de totales en tiempo real mientras se carga: total de gastos, **resultado del ejercicio**, **rentabilidad (%)** y los equivalentes en dólares según el tipo de cambio del mes.
- **Cierre de mes**: antes de confirmar el cierre, el sistema muestra una pantalla de **preview** con las liquidaciones calculadas para todos los inversores. El Administrador puede revisar y ajustar los consumos de cada uno, y desde esa misma pantalla confirma el cierre. Una vez confirmado, el sistema congela los números, genera las liquidaciones y **envía la notificación por correo a cada inversor** (ver 3.12). Para cerrar, el sistema exige que estén cargados las ventas, el tipo de cambio y los rubros obligatorios.

### 3.4 Estado de resultados anual

- Vista de consulta tipo planilla: rubros y subgrupos en filas, los 12 meses y el total anual en columnas — la misma lectura que el Excel actual.
- Selector de año (2024, 2025, 2026 y siguientes) y **exportación a Excel**.

### 3.5 Indicadores de venta del local

- Carga mensual de los indicadores del sistema de ventas Ayres: **cantidad de comensales, ticket promedio, ítems por ticket y cubierto promedio** (ingreso manual desde los totalizadores de Ayres).
- Estos indicadores se muestran a los inversores en el dashboard, junto a las métricas económicas.

### 3.6 Dashboard de métricas (núcleo de la aplicación)

Tablero organizado en **tarjetas por módulos**, con diseño cuidado y selector de mes/año:

- **Tarjetas de indicadores del mes**: ventas totales con desglose por facturado/no facturado, desglose Salón/Delivery, total de gastos, resultado del ejercicio, rentabilidad (%), valores en dólares e indicadores de venta (incluye cantidad de comensales).
- **Gestión del mes en curso**: el dashboard muestra el **mes abierto con los datos parciales ya cargados**; si falta el tipo de cambio, los valores en dólares aparecen como "TC pendiente" sin bloquear el resto de la vista.
- **Gráficos analíticos**:
  - Evolución mensual de ventas, gastos y resultado, con comparación entre años.
  - Composición de ventas Salón vs. Delivery (nuevo, P-A02) y composición de gastos por rubro del mes.
  - Rentabilidad histórica mes a mes.
  - Resultado del ejercicio en dólares, histórico completo.
- **Tabla resumen** del año en curso (mini estado de resultados mes a mes).
- **Tema claro/oscuro**: cada usuario elige su modo preferido y el sistema lo recuerda entre sesiones.
- Los meses sin datos se muestran como "sin información del período", nunca con errores.

### 3.7 Puntos de inversión

- Registro de los **100 puntos** del local: número, valor de aporte de cada punto (USD 3.000 / 3.500 / 4.500) y puntos bonificados (sin aporte), tal como están en la planilla actual.
- Asignación de puntos a cada inversor **con historial de cambios**: si un inversor compra o cede puntos, el sistema registra desde qué mes rige el cambio, y los meses anteriores conservan la distribución que tenían.
- Tarjeta resumen: total recaudado (USD 287.500), puntos asignados y disponibles.
- El sistema controla que nunca se asignen más de 100 puntos a la vez.

### 3.8 Liquidaciones mensuales de utilidades

- Al cerrar el mes, el sistema calcula automáticamente la **utilidad por punto** (resultado del ejercicio ÷ 100) y genera la liquidación de cada inversor según sus puntos vigentes.
- Sobre cada liquidación el Administrador puede registrar los **consumos** del inversor en el local, que se descuentan del monto a cobrar (siempre visibles como detalle, nunca ocultos).
- Cada liquidación muestra: puntos, monto bruto, consumos, neto a cobrar, equivalente en dólares, **renta mensual** sobre el capital aportado y fecha de pago.
- Estados **Pendiente / Pagada**: al marcarla como pagada se registra la fecha y la liquidación queda protegida contra cambios. Solo el Administrador puede reabrirla, con motivo registrado.
- Vista de **reparto general histórico**: la serie mensual completa (utilidad por punto, montos totales, dólares, renta y fechas de pago) con gráfico de evolución — el equivalente a la hoja "GENERAL" de la planilla.

### 3.9 Mi inversión (vista personal del inversor)

La pantalla con la que cada inversor sigue su inversión de manera profesional:

- **Tarjetas principales**: capital aportado, dividendos acumulados (en pesos y dólares), **recupero de la inversión** (% del capital ya recuperado, con barra de progreso) y rentabilidad mensual promedio.
- **Gráficos**: dividendos mensuales en dólares y recupero acumulado en el tiempo.
- **Historial completo mes a mes**: puntos, utilidad por punto, monto en pesos, monto en dólares, renta del mes, consumos descontados y fecha de pago.
- Incluye todo el historial desde noviembre 2024 (carga inicial incluida).

### 3.10 Cámaras del local

- Opción de menú y pantalla dedicada que muestra las cámaras de seguridad a través del **web client de Hik-Connect** (la plataforma del fabricante Hikvision que se usa actualmente), con alternativa de apertura en una pestaña propia.
- El Administrador configura los datos de acceso desde el sistema; los datos serán provistos al momento de la implementación.
- El Inversor accede a la visualización con un clic, sin configurar nada.

### 3.11 Carga inicial de datos históricos (2024–2026)

- Migración de toda la información de las dos planillas actuales: los tres años del estado de resultados y el historial completo de puntos, liquidaciones y dividendos de los 15 inversores.
- La carga se valida contra los totales anuales y los acumulados de cada inversor de las planillas fuente, de modo que el dashboard y "Mi inversión" nazcan con el historial completo y los mismos números que hoy maneja el cliente.

### 3.12 Notificación por correo al cierre del mes

- Cuando el Administrador cierra el ejercicio del mes, el sistema envía **automáticamente un correo a cada inversor** con:
  - El **resumen del mes**: ventas, resultado del ejercicio, rentabilidad y utilidad por punto.
  - **Su liquidación personal**: puntos, monto bruto, consumos descontados, neto a cobrar y equivalente en dólares.
  - El aviso de que **el resumen completo ya está disponible en la web**, con un botón de acceso directo al sistema.
- El correo tiene diseño propio (HTML) alineado con la imagen del sistema.
- El Administrador configura una sola vez la casilla emisora (con correo de prueba incluido) y dispone de un **historial de envíos** por mes, con el estado de cada correo (enviado / fallido) y la opción de reenviar.
- Si un correo falla (por ejemplo, una casilla llena), el cierre del mes no se ve afectado: el envío queda registrado para reenviarlo.

---

## 4. Qué no incluye este desarrollo

- Conexión directa con la base de datos del sistema de ventas Ayres: queda prevista como **segunda etapa** y se cotiza por separado luego de un relevamiento técnico (en esta etapa los indicadores se cargan manualmente desde los totalizadores de Ayres).
- Transmisión propia del video de las cámaras: la visualización usa la plataforma Hik-Connect del fabricante.
- Facturación electrónica ante AFIP / ARCA.
- Aplicación móvil nativa (el sistema es totalmente usable desde el navegador del celular).
- Otros envíos de correo o notificaciones distintos de la notificación de cierre mensual (recordatorios de pago, alertas, newsletters).
- Cambios de alcance posteriores al inicio (se presupuestan por separado).

---

## 5. Precio por área funcional

| Área | Precio | Δ respecto a v3 |
|---|---:|:---:|
| Acceso y gestión de usuarios inversores | USD 84 | — |
| Configuración del sistema (rubros, porcentajes, tipo de cambio + **selector cotización dólar**) | USD 168 | +USD 25 (TC P-A03) |
| Estado de resultados mensual y anual (**4 campos ventas, preview editable**) | USD 235 | +USD 33 (P-A02+P-A07) |
| Indicadores de venta del local (**+ cantidad de comensales**) | USD 34 | +USD 9 (P-A01) |
| Dashboard de métricas con tema claro/oscuro (**mes abierto parcial + torta Salón/Delivery**) | USD 160 | +USD 26 (P-A05+P-A02) |
| Inversiones: puntos, liquidaciones y reparto | USD 269 | — |
| Mi inversión (vista del inversor) | USD 67 | — |
| Cámaras del local | USD 42 | — |
| Carga inicial de datos históricos 2024–2026 (**riesgo M14 elevado — ver nota**) | USD 185 | +USD 17 (P-A02 migración) |
| Notificación por correo al cierre del mes | USD 67 | — |
| Uso de infraestructura IA (tokens) | USD 100 | — |
| **Total del proyecto** | **USD 1.411** | **+USD 110 respecto a v3** |

> **Nota carga inicial (M14):** los Excel históricos no traen la apertura Salón/Delivery (solo tienen A/B). Los períodos 2024–2026 se migrarán con `VentasADelivery = VentasBDelivery = 0`; cada tipo queda íntegro en Salón. Cada período migrado lleva la observación `"Desglose Salón/Delivery no disponible en datos fuente"`. La torta Salón/Delivery del Dashboard mostrará 100 % Salón hasta el primer mes con datos reales. El esfuerzo extra de validación y marcado justifica el delta de USD 17.

**Mantenimiento anual — Plan PREMIUM: USD 400/año.** Incluye servidor (hosting), actualizaciones de seguridad, soporte prioritario y 2 rondas de ajuste por año. Es un servicio continuo posterior al desarrollo; no cubre cambios funcionales nuevos.

---

## 6. Condiciones generales

- El precio incluye desarrollo, pruebas internas, carga inicial de los datos históricos y puesta en funcionamiento.
- Moneda: dólares estadounidenses.
- Forma de pago: 50 % al inicio, 50 % a la entrega.
- Dependencias del cliente: planillas actualizadas al momento de la carga inicial, datos de acceso de Hik-Connect, totalizadores mensuales de Ayres y casilla de correo emisora para las notificaciones.
- El plazo de entrega se define en el acuerdo inicial según disponibilidad acordada.

---

*Propuesta válida por 30 días desde la fecha de emisión.*
