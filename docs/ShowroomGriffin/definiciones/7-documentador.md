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

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
