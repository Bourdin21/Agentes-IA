# Memoria - Documentador

## Proyecto: marihogar
## Ultima actualizacion: 2026-07-24

## Definiciones vigentes

### Alcance entregado al cliente

Etapa 1 completa (16 modulos, 6 sprints de implementacion, todos con QA en GO): Usuarios y roles, Catalogo de productos, Control de stock, Presupuestos y cotizaciones, Gestion de ventas (pantalla POS elevada), Entregas a domicilio, Cuenta corriente del local, Compras a proveedores, Cuenta corriente de proveedores, Cheques 30/60/90, Caja mensual, Gastos del negocio, Panel de metricas y dashboard, Aumento masivo de precios, Proyeccion financiera, Facturacion electronica AFIP/ARCA. Documentos entregados: `docs/marihogar/resumen-etapa1-2026-07-24.md` (resumen ejecutivo de cierre) y `docs/marihogar/manual-usuario-2026-07-24.md` (manual de uso paso a paso, 15 secciones, una por modulo/flujo, con tabla de accesos por rol — no incluye el modulo "Super Usuario" del sidebar, reservado para uso interno del proveedor por regla vigente). Sistema ya desplegado en produccion: `http://olvidatasoft-002-site16.jtempurl.com/`.

### Pendientes o fuera de alcance

- Etapa 2 (CRM de Leads + Bot WhatsApp) en pausa por decision explicita del cliente (2026-07-24) — no comunicada como "entregada", queda fuera de este resumen salvo la mencion de que sigue pendiente de arranque.
- Certificado digital ARCA (.p12) del cliente — dependencia externa ya documentada desde el analisis funcional. Facturacion AFIP queda en modo homologacion (pruebas) hasta recibirlo.
- 5 checklists de verificacion manual acumuladas (Sprints 2 a 6, ~50 pasos totales) sin ejecutar por el usuario — comunicado como pendiente de su parte antes de dar la Etapa 1 por definitivamente cerrada en produccion.

### Beneficios comunicados

Reemplazo completo de Contagram, automatizacion de stock/CC/caja (sin carga manual duplicada), proyeccion financiera para anticipar la caja, pantalla de ventas rapida para el mostrador, roles diferenciados Administrador/Vendedor.

### Proximo paso sugerido

Que el cliente recorra las checklists de verificacion manual (ofrecida sesion conjunta), gestione el certificado ARCA, y confirme cuando quiere retomar Etapa 2.

### Nota de transparencia incluida

Se comunico al cliente, en lenguaje simple y sin alarmar, el incidente de proceso de Sprint 5 (colision de dos ejecuciones paralelas del implementador, ya investigado y descartado como riesgo real) — decision de incluirlo por regla de transparencia del estudio, aclarando explicitamente que no requiere accion de su parte.

## Historial de ajustes
- 2026-07-28: Guía técnica `certificado-afip.md` redactada — trámite paso a paso (portal AFIP + OpenSSL) para obtener el `.p12` real del negocio, adaptada del template del estudio (`docs/templates/afip-certificado-digital.md`) y del precedente ya ejecutado en `delicias-naturales/certificado-afip.md`. No es un documento de cara al cliente con el formato de marca (`31-formato-documento-cliente.instructions.md`) — es una guía operativa interna/técnica, a pedido explícito del usuario, para acompañar al cliente en el trámite. Datos del CUIT/alias reales del negocio quedan pendientes de completar cuando el cliente los provea. `.gitignore` del repo actualizado (`*.p12`/`Certificados/`) para que el certificado nunca se suba a git.
- 2026-07-24: Documento de cierre de Etapa 1 completa redactado y entregado (`resumen-etapa1-2026-07-24.md`), cubriendo los 6 sprints/16 modulos con QA en GO. Formato `31-formato-documento-cliente.instructions.md` aplicado completo.
- 2026-07-24: Manual de usuario redactado y entregado (`manual-usuario-2026-07-24.md`). Estructura de manual (indice + 1 seccion por modulo) en vez de resumen de sprint, a pedido explicito del cliente — se mantuvo el encabezado de marca, tono voseo y pie de firma de `31-formato-documento-cliente.instructions.md`, pero no la restriccion de "media pagina" (no aplica a un manual de uso completo). Fuente: `5-implementador.md`/`6-qa.md` (los 6 sprints, solo lo validado) para el contenido funcional, y el sidebar real de `Views/Shared/_Layout.cshtml` para los nombres exactos de menu (Principal/Administracion/Ventas/Compras/Financiero/Catalogo/Super Usuario) y su agrupacion por rol. Diferenciacion Administrador/Vendedor explicita en tabla al inicio. Incluye seccion final de pendientes (certificado ARCA, checklists manuales) igual que el resumen de Etapa 1.
