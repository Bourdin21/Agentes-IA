# Memoria Documentador — KoiDumplings
# Última actualización: 2026-07-13 (sesión actual)

## Manual de usuario completo — entregado (sesión actual)

Se redactó `docs/koi/manual-usuario.md` — manual de usuario completo (no un resumen de sprint) a pedido explícito del cliente, en formato `.md` (excepción puntual al canal habitual de Google Doc en Drive — el cliente pidió el archivo directamente). Cubre: cómo ingresar, roles (Administrador/Inversor, SuperUsuario no expuesto), Dashboard, carga de Estado de Resultados, cierre de período y liquidaciones, Reparto General, Mi Inversión, Configuración, y una sección final "De dónde salen los números" con el resumen de la migración histórica ya ejecutada. **Excluye a pedido del cliente**: Cámaras IP, Fichador/huellas, integración automática Ayres (las tres son candidatas a Etapa 2, no entregadas).

Se creó además un usuario de prueba real en **producción** para que el cliente siga el manual con su propio acceso: `juani.skari@gmail.com` / rol Administrador (contraseña provista por el cliente, no se repite aquí) — creado vía la pantalla real de Usuarios (no por SQL directo, para que quede con el hash de contraseña correcto de Identity) y verificado con login exitoso. Se confirmó además que el hosting productivo (`https://olvidatasoft-002-site15.jtempurl.com`) ya está en línea sirviendo la app real — se referenció esa URL en el manual.



## Instrucción permanente para el manual de usuario

Cuando se redacte el manual de usuario (o cualquier resumen orientado al cliente) de KOI, incluir una **sección comparativa "Excel reemplazado → funcionalidad del sistema"** que muestre, en lenguaje de negocio, qué hacía cada Excel manualmente y qué pantalla/funcionalidad del sistema lo reemplaza. Pedido explícito del cliente (2026-07-13): que el manual deje trazado el reemplazo, no solo el uso de las pantallas.

Base para esa sección — mapeo verificado (ver auditoría en `trazabilidad.md` del 2026-07-13):

| Excel / hoja | Qué calculaba a mano | Pantalla del sistema que lo reemplaza |
|---|---|---|
| "Estado de Resultados KOI (Inversores)" — hojas 2024/2025/2026, ventas A/B por mes | Ventas, Costo de Mercadería, Fee de Franquicia (regalías 3% + canon 2,5%), Sueldos y Cargas Sociales, Gastos Varios, Alquiler, Servicios, Impuestos (IVA, IIBB, débitos/créditos, tasa municipal, previsiones) — todo tecleado y sumado a mano por mes, con fórmulas de % inconsistentes entre meses (bases A/B mezcladas) | **Estado de Resultados** (carga mensual) + **Dashboard** (sección Ventas/Gastos + Evolución Histórica): el sistema calcula los conceptos porcentuales de forma automática y con la base normalizada (regalías/canon sobre Ventas Totales; comisiones, IIBB, débitos/créditos y tasa municipal solo sobre Ventas A) — corrige la inconsistencia que tenía el Excel |
| "Reparto de Utilidades Inversores" — hoja "Puntos" | Tabla de 100 puntos de inversión repartidos entre 15 inversores, valor de aporte por punto | **Inversores** + **Puntos** (asignación con vigencia mensual) |
| "Reparto de Utilidades Inversores" — hoja "GENERAL" | Utilidad por punto = Resultado del mes ÷ 100, total, USD, renta, fecha de pago | **Reparto General** — mismo cálculo, automático |
| "Reparto de Utilidades Inversores" — una hoja por inversor (Minjo Wang, Andrés Welchen, etc.) | Liquidación mensual (puntos × utilidad − consumos), dividendos acumulados, % de recupero del capital, renta mensual promedio | **Liquidaciones** (vista Admin) + **Mi Inversión** (vista Inversor, ve solo sus propios datos) — mismas fórmulas, con el agregado de que el sistema bloquea si los consumos superan la liquidación bruta (el Excel no tenía ese control) |

**Verificado en código** (no solo en documentación): las fórmulas de `EstadoResultadosService`, `InversionesService` (recupero, renta mensual) y el cierre de período (`CerrarPeriodoAsync`) reproducen exactamente la lógica de las hojas del Excel, con las bases de cálculo normalizadas según la regla que confirmó el cliente en el análisis funcional.

## ✅ Migración histórica ejecutada y validada (2026-07-13)

La migración de datos históricos (CU-15) ya se ejecutó en el entorno local y quedó validada. El manual de usuario **puede afirmar el reemplazo total** de ambos Excel, incluido el histórico. Detalle completo en `trazabilidad.md` (entrada 2026-07-13, implementador-dotnet). Resumen para citar en el manual:

- 19 períodos migrados (nov-2024 a may-2026), 373 líneas de gasto, 15 inversores reales, 16 asignaciones de puntos con vigencia, 265 liquidaciones históricas.
- Total Gastos de los 19 períodos reconcilia al centavo contra el "Total Gastos" que el propio Excel calculaba (incluidas varias inconsistencias reales del Excel entre meses, replicadas fielmente en vez de "corregidas").
- Capital total de inversores migrado: USD 287.500 — coincide exactamente con el dato del análisis funcional ("15 inversores externos... USD 287.500 recaudados").
- Validado visualmente en Dashboard, Reparto General y Liquidaciones con datos reales (no solo a nivel de base).

**Limitaciones a mencionar en el manual** (transparencia con el cliente, no defectos):
- El Excel fuente nunca trackeó "Cantidad de comensales" ni "Cantidad de ventas" por mes — esos indicadores quedan vacíos ("—") en los períodos migrados hasta que se cargue el primer mes con datos reales desde el sistema.
- El Excel fuente no distinguía canal Pedidos/Mostrador en el histórico (solo Facturado A / No facturado B) — los períodos migrados muestran 100% "Salón" hasta el primer mes cargado nativamente en el sistema (mismo criterio ya aprobado para el riesgo M14 del arquitecto).
- ~5 a 11 de los 100 puntos de inversión por mes no tienen un inversor nombrado con historial propio en el Excel (aparecen como "disponibles" en Puntos) — es una característica del Excel original, no un dato perdido en la migración.
