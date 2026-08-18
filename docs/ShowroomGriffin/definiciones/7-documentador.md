# 7 — Documentador (Resumen al cliente)
## Sistema de Gestión Comercial — ShowroomGriffin

**Cliente:** Ulises
**Proveedor:** OlvidataSoft
**Versión:** 1.0 — borrador
**Fecha:** 2026-01-15
**Inputs:** `5-implementador.md` (cambios entregados) + `6-qa.md` (validación)

---

## 1. Resumen del sprint

Se completó la construcción del sistema de gestión comercial para Showroom Griffin. Quedaron operativos los nueve módulos previstos (seguridad, maestros, productos, stock, compras, ventas, devoluciones, resumen semanal y aumentos de precios) más el panel principal. La aplicación está instalada en el servidor productivo y validada técnicamente por QA, sin defectos funcionales abiertos.

## 2. Cambios principales entregados

- **Acceso seguro por roles**: ingreso con tres perfiles (Súper Usuario, Administrador, Vendedor). Cada perfil ve solo lo que le corresponde.
- **Gestión de catálogo**: alta y mantenimiento de categorías, subgrupos, clientes, proveedores y productos con sus variantes (talles, colores, modelos, etc.).
- **Control de stock con historial**: cada movimiento queda registrado (carga inicial, ajustes, ventas, compras, devoluciones) y el sistema avisa cuando hay stock bajo.
- **Compras a proveedores**: flujo guiado de pedido → revisión → recepción, con control de cantidades recibidas/dañadas/devueltas y actualización automática del último precio de compra.
- **Ventas a clientes**: pantalla única de venta con búsqueda rápida de productos, múltiples medios de pago (efectivo, tarjeta, cuotas, transferencia) y generación de remito en PDF.
- **Devoluciones y cambios**: asistente paso a paso para devolver dinero, cambiar por igual valor o por mayor valor, con reingreso de stock automático.
- **Resumen semanal de transferencias**: reporte de lunes a domingo con exportación a Excel.
- **Aumento masivo de precios**: previsualización por categoría/marca antes de aplicar, con redondeo y protección ante actualizaciones simultáneas.
- **Panel principal (Dashboard)**: indicadores diferenciados según el perfil del usuario.

## 3. Beneficio para el cliente

- **Operación más rápida**: una sola pantalla para vender, con cálculos y validaciones automáticas que evitan errores manuales.
- **Información confiable**: el stock siempre refleja la realidad porque toda operación queda trazada.
- **Menos riesgo en devoluciones**: el asistente impide devolver más de lo vendido y reingresa stock automáticamente.
- **Control gerencial**: el resumen semanal y los indicadores del panel permiten ver el negocio sin pedirle datos a nadie.
- **Aumentos de precios sin sustos**: se ve el impacto antes de aplicarlo y el sistema evita pisarse entre dos personas trabajando a la vez.
- **Seguridad por rol**: los vendedores no acceden a costos, ganancias ni configuración del sistema.

## 4. Pendientes / fuera de alcance

- **Pruebas finales con datos reales** (a cargo de Ulises o equipo): generar una venta completa, emitir un remito en PDF, descargar el resumen semanal en Excel, hacer una devolución por el asistente y probar un aumento masivo en dos pestañas a la vez.
- **Endurecimiento de credenciales del servidor**: las claves de la base productiva y del correo deben moverse fuera del archivo de configuración antes de exponer la aplicación a usuarios reales (tarea de despliegue).
- Quedan **fuera del alcance v1**: integración con AFIP / facturación electrónica, app móvil, integraciones con e-commerce, notificaciones push.

## 5. Riesgos y consideraciones visibles para negocio

- **Credenciales productivas**: hoy están dentro del paquete de instalación. No es seguro habilitar el sistema a usuarios externos hasta resolverlo. Es la única condición bloqueante antes del lanzamiento.
- **Backups**: se aplicó un cambio estructural a la base productiva. Conviene confirmar con el hosting la política de respaldo automático y, si es posible, dejar pactado un backup diario.
- **Capacitación inicial**: el sistema está listo pero conviene una sesión corta con el equipo de ventas para el flujo de venta y el asistente de devoluciones (las dos pantallas más densas).
- **Escalabilidad**: la versión actual está pensada para una sola instancia del servidor. Si en el futuro se suman locales o usuarios concurrentes intensos, habrá que revisar la infraestructura.

## 6. Próximo paso sugerido

Coordinar una **sesión de pruebas guiada con Ulises (≈1 h)** para ejecutar los smoke tests pendientes (venta, devolución, remito PDF, resumen Excel, aumento masivo) y, en paralelo, **resolver el tema de credenciales productivas**. Con esos dos puntos cerrados, el sistema queda formalmente liberado para producción.

---

> Estado del documento: **borrador sujeto a smoke final**. La firma del entregable se realizará una vez completadas las pruebas de la sección 4 y el cierre del bloqueante de seguridad.

## Memoria acumulativa

- **2026-01-15** — v1.0 borrador. Generado a partir del cierre técnico de E0–E8 (build verde, migraciones aplicadas en local y producción) y el reporte QA v1.1 (0 defectos funcionales abiertos, gate condicional). Pendientes: smoke manual con cliente y cierre del bloqueante de credenciales (RR-01 / D-04).
- **2026-07-02** — V9 (fast-path): en la pantalla de **Ajuste manual de stock**, al guardar el ajuste de un producto, el sistema ahora permanece en la misma pantalla (con el mensaje de confirmación) en vez de volver al listado general de stock. Pensado para cargar ajustes de varios productos seguidos sin tener que renavegar cada vez. Sin impacto en permisos, validaciones ni otras pantallas. QA técnico aprobado sin observaciones (ver `6-qa.md`, entrada V9). Costo: 0,3 h / USD 12 (tasa USD 40/h).
- **2026-08-16** — V12: la Vista Matriz pasa a cubrir accesorios sin talle y alta de color nuevo (con o sin stock inicial), y se retiran del menú los botones de Ajuste Manual y Carga Masiva. Primera feature de este proyecto que corrió el flujo completo del estudio (Discovery→Diseño→Arquitectura→Presupuesto→Implementación→QA→Documentación) en vez de fast-path, a raíz de que el cambio anterior sobre esta misma pantalla (alta desde celda vacía) había sido rechazado por QA con 2 defectos bloqueantes ya en producción. QA encontró 8 defectos más sobre V12 (2 corregidos antes de deploy, 1 bloqueaba el retiro del menú y también se corrigió, el resto son observaciones menores o fuera de alcance). Presupuesto: USD 105,84, aprobado por el cliente el mismo día.

---

# OlvidataSoft
**Resumen de sprint — Carga masiva de stock por Marca + filtros completos de Consulta de Stock**
**OlvidataSoft · Julio 2026**

## Sobre el proyecto
Sistema de gestión comercial para Showroom Griffin, en producción. Este sprint responde a un pedido puntual: agilizar la carga de stock cuando llega mercadería nueva de una marca completa, y poder encontrar cualquier producto en el listado de stock filtrando por cualquier dato que se ve en pantalla.

## 1. Resumen del sprint
Hasta ahora, cargar el stock de un envío nuevo significaba entrar producto por producto, talle por talle, color por color, uno a la vez. Este sprint agrega una pantalla que permite cargar todo el stock de una marca en un solo paso, y completa los filtros de la consulta de stock para que se pueda buscar por talle y por estado (bajo/límite/OK) sin salir de la misma pantalla. QA revisó el código en detalle: **0 defectos funcionales**, con 2 observaciones menores sin impacto en el uso normal (detalladas más abajo).

## 2. Cambios principales entregados
- **Carga masiva de stock por Marca**: elegís una marca y ves, agrupado por modelo, todo su stock actual con un campo para escribir la cantidad nueva de cada talle/color. Un solo botón guarda todo el lote.
- **Alta de variantes nuevas en el momento**: si llega un talle o color que todavía no existía en el sistema, se puede crear ahí mismo (color, talle, precio y stock mínimo) sin ir primero a la pantalla de Productos.
- **Carga segura por lote**: si algo está mal cargado en una fila, no se guarda nada del lote hasta corregirlo — y no se pierde lo que ya se había tipeado en las demás filas, solo hay que arreglar la fila marcada con error.
- **Filtro por Talle** en la Consulta de Stock, igual que ya existían los filtros por Marca, Modelo y Color.
- **Filtro por Estado** (Todo / OK / Límite / Bajo) integrado a los demás filtros, en reemplazo del botón "Solo alertas" — se combina con el resto sin tener que recargar la pantalla.

## 3. Beneficio para el cliente
- **Menos tiempo cargando stock**: lo que antes eran decenas de pasos repetidos (uno por talle/color) ahora es una sola carga por marca.
- **Menos idas y vueltas**: dar de alta un talle/color nuevo ya no obliga a salir de la pantalla de stock.
- **Menos errores costosos**: la carga por lote no permite quedar "a medio cargar" — o se guarda todo correctamente, o se avisa exactamente qué corregir sin perder el resto del trabajo ya hecho.
- **Búsquedas más rápidas**: encontrar stock por talle o por nivel de alerta ya no requiere mirar toda la lista.

## 4. Pendientes / fuera de alcance
- **Importación desde Excel/CSV**: no forma parte de este sprint (quedó explícitamente fuera de alcance en el relevamiento).
- **Carga masiva cruzando varias marcas a la vez**: hoy se carga una marca por vez.
- Verificación manual en el sistema real por parte de Ulises (guía de pasos ya preparada — ver punto 6).

## 5. Riesgos o consideraciones visibles para negocio
- QA dejó 2 observaciones menores, sin defectos: el filtro de Talle muestra todo el catálogo de talles posibles de la marca (no solo los que tienen stock cargado) — funciona bien, solo es una pequeña inconsistencia visual frente al filtro de Color. Ninguna de las dos requiere corrección antes de usar la función.
- El código de esta mejora todavía no fue confirmado en el repositorio (commit) al momento de este resumen — antes de darla por desplegada, coordinar ese paso con el equipo técnico.

## 6. Próximo paso sugerido
Coordinar con Ulises una prueba guiada breve (≈15-20 min) sobre la carga masiva de una marca real y los filtros nuevos de Talle/Estado, y confirmar el commit de los cambios antes de considerar el sprint cerrado en producción.

---

> Estado del documento: **borrador sujeto a verificación manual del cliente**, según el punto 6.

---

# OlvidataSoft
**Resumen de sprint — Vista Matriz: accesorios y alta de color nuevo, en reemplazo de Ajuste Manual y Carga Masiva**
**OlvidataSoft · Agosto 2026**

## Sobre el proyecto
Sistema de gestión comercial para Showroom Griffin, en producción. Este sprint completa la Vista Matriz (la pantalla principal de Stock desde hace unos días) para que cubra el 100% de los casos que hasta ahora obligaban a usar otras dos pantallas más lentas.

## 1. Resumen del sprint
La Vista Matriz ya permitía ver y editar el stock de calzado en una grilla tipo planilla (Marca → Modelo → Color × Talle), pero tenía dos huecos: no mostraba los productos que no usan talle (bijou, carteras, accesorios en general) y no dejaba cargar un color completamente nuevo, solo completar un talle faltante de un color que ya existía. Ambos huecos ya están cerrados. Con eso, los botones de "Ajuste manual" y "Carga masiva" — las dos pantallas más lentas que quedaban — se sacaron del menú de Stock: todo se hace ahora desde la Matriz.

## 2. Cambios principales entregados
- **Accesorios en la Matriz**: los productos sin talle (bijou, carteras, etc.) ahora aparecen en la Matriz con una tabla simple de Color y Cantidad, en vez de quedar afuera.
- **Alta de un color nuevo desde la Matriz**: cada sección de la grilla tiene ahora una fila "+ Nuevo color" para cargar un color que todavía no existía — con o sin talle según el producto, cargando cantidad, precio y stock mínimo en el momento.
- **Alta con stock inicial en cero**: se puede dar de alta un color nuevo con 0 unidades (por ejemplo, un pedido hecho pero que todavía no llegó), sin necesidad de escribir ninguna cantidad.
- **Menú simplificado**: "Ajuste manual" y "Carga masiva" ya no aparecen como botones en Consulta de Stock — la Matriz cubre todo lo que hacían esas dos pantallas.

## 3. Beneficio para el cliente
- **Una sola pantalla para todo el stock**: calzado, accesorios, productos existentes y colores nuevos se manejan todos desde la Matriz.
- **Menos clics para cargar mercadería nueva**: dar de alta un color nuevo ya no requiere salir a otra pantalla.
- **Se puede catalogar por adelantado**: un producto pedido que todavía no llegó se puede cargar con 0 unidades desde ya, sin esperar a que llegue para registrarlo.

## 4. Pendientes / fuera de alcance
- Verificación manual en el sistema real (guía de pasos ya preparada para el equipo técnico) antes de dar el sprint por cerrado del todo.
- Las rutas de "Ajuste manual" y "Carga masiva" siguen existiendo por si hiciera falta volver atrás — solo se sacaron del menú, no se borró nada.

## 5. Riesgos o consideraciones visibles para negocio
- Durante este sprint se encontró y corrigió un problema que venía de un cambio de esa misma mañana: en un escenario puntual, el sistema podía guardar un precio 100 veces más alto del real sin avisar. Se confirmó contra la base real que **nadie llegó a usar esa función todavía**, así que no hubo ningún precio incorrecto cargado — quedó corregido antes de que pudiera pasar.
- Como medida extra de seguridad para este tipo de problema, se agregó un control que impide desde la base de datos que se carguen dos veces el mismo color y talle de un producto (antes solo lo evitaba el sistema, ahora también lo respalda la base).

## 6. Próximo paso sugerido
Probar en el sistema real: dar de alta un color nuevo con varios talles a la vez, dar de alta un accesorio, y cargar un color nuevo con 0 unidades. Confirmar que todo se ve y guarda como se espera antes de considerar el sprint cerrado.

---

> Estado del documento: **borrador sujeto a verificación manual del cliente**, según el punto 6.

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
