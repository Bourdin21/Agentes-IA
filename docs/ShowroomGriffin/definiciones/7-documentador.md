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
