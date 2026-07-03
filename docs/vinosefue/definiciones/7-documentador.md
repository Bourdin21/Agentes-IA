# Memoria - Documentador

## Proyecto: vinosefue
## Ultima actualizacion: 2026-07-03

## Definiciones vigentes

### Alcance entregado al cliente

**Sprint: Compras al proveedor — desacople y cuenta corriente (2026-07-03)**

1. Resumen del sprint (para el cliente)
2. Cambios entregados
3. Beneficio para el negocio
4. Pendientes / fuera de alcance
5. Riesgos o consideraciones visibles
6. Próximo paso sugerido

Ver detalle completo abajo — este mismo texto es el que se comparte con el cliente.

**Documento entregable (v1, Artifact HTML):** nota de entrega formateada libremente (memo/ficha) para compartir vía Artifact. Archivo fuente: `C:\Users\joaco\AppData\Local\Temp\claude\c--Sistemas-Agentes-IA\9825ae3b-d196-4158-bf15-7b2e5e79a5ed\scratchpad\vinosefue-entrega-compras-proveedor.html` (ruta de sesión, temporal).

**Documento entregable (v2, formato oficial OlvidataSoft):** tras detectar `.github/instructions/31-formato-documento-cliente.instructions.md` (formato obligatorio para todo documento a cliente, estilo OlvidataSoft Julio 2026), se regeneró el resumen de sprint en ese formato: wordmark + titulo/subtitulo, `## Sobre el proyecto`, `## Cómo funciona: armar una compra al proveedor — paso a paso` (flujo nuevo, amerita explicación), cambios entregados, beneficio, pendientes, pie de firma. Guardado como archivo Markdown versionado (no Artifact temporal) en `C:\Sistemas\Agentes-IA\docs\vinosefue\resumen-sprint-compras-proveedor-2026-07.md` — este es el archivo fuente de contenido vigente. La v1 (Artifact HTML de formato libre) queda obsoleta.

**Documento entregable (v3, Artifact del formato oficial) — RECHAZADO por el cliente:** se publicó una versión con diseño propio (paleta garnet/brass, serif Constantia + sans Corbel). El usuario lo rechazó explícitamente: "no me sirvió porque me cambia el formato, las letras, y todo el documento". Ningún documento a cliente debe llevar diseño custom — corregido en memoria del estudio (`feedback-formato-documento-cliente.md`).

**Documento entregable (v4, Google Doc en Drive — vigente):** el pedido real era un archivo Word con el formato ya establecido en el Drive de Olvidata (texto plano prolijo, sin paleta/tipografías propias — verificado contra `Presupuesto Ulises - OlvidataSoft.docx` y otros). Se detectó que ya existía en Drive un `.docx` con este mismo título, generado desde el markdown, con la numeración de los 5 pasos y los niveles de encabezado rotos por la conversión. Se generó el contenido como HTML semántico (headings/listas reales, sin CSS) y se subió vía `mcp__claude_ai_Google_Drive__create_file` a la carpeta de Drive donde viven el resto de los documentos de Olvidata (`parentId 0AKdL2qlDPnZIUk9PVA`), quedando como Google Doc nativo — verificado leyendo el archivo de vuelta que encabezados y numeración sobrevivieron. **Este es el entregable vigente:** https://docs.google.com/document/d/1An45iVfcU_3LnQVHKpDnld_T_SFweHm-w_Lx-05iOSM/edit (el usuario puede descargarlo como Word desde ahí). El `.docx` viejo con formato roto sigue en Drive, no se borró sin permiso.

### Pendientes o fuera de alcance

- Aplicar las migraciones y scripts de datos en el sistema de producción (requiere aprobación explícita + backup previo, por tratarse de datos financieros).
- Probar a mano, en el navegador, el circuito completo de "crear una compra nueva" y "cargar un pago/nota de crédito" (el QA automático validó todo lo que se puede verificar por código y base de datos, pero el click a click final en pantalla queda para que el usuario lo recorra una vez).
- Migraciones de sprints anteriores (reversión de estados de pedido, stock propio) que ya estaban pendientes de producción antes de este sprint — no se originan en este trabajo.

### Beneficios comunicados

- El stock propio deja de mezclarse con lo que hay que comprarle al proveedor.
- El listado de compras es más fácil de leer (fecha primero, más reciente arriba).
- Se puede armar una compra al proveedor eligiendo exactamente qué productos comprar, sin esperar a que el sistema lo haga solo ni depender del estado del pedido del cliente.
- La cuenta corriente del proveedor en el sistema ahora es un espejo directo del extracto real que manda el proveedor — más fácil de conciliar.
- Se puede cargar pagos y notas de crédito del proveedor de forma simple, sin tener que atarlos a una compra puntual.

### Próximo paso sugerido

Revisar en el navegador el circuito de "crear compra nueva" y "cargar pago/nota de crédito" con datos reales, y coordinar la ventana para aplicar las migraciones en producción (con backup previo).

## Historial de ajustes
- 2026-07-03: Documentación de cierre del sprint "Compras al proveedor — desacople y cuenta corriente", tras Análisis, Diseño, Arquitectura, Implementación (2 rondas de ajuste) y QA (GO condicionado, 2 defectos encontrados y corregidos) aprobados el mismo día.
- 2026-07-03: A pedido explícito del usuario ("armar documento para entregarle al cliente"), se generó una nota de entrega formateada (Artifact HTML) con el mismo contenido de los 6 bloques, para compartir directamente con el cliente.
- 2026-07-03: A pedido explícito del usuario ("...con el nuevo formato de documentos de olvidata"), se regeneró el documento aplicando `31-formato-documento-cliente.instructions.md` (formato oficial OlvidataSoft: wordmark, secciones estandarizadas, voseo, pie de firma), guardado como `.md` versionado en `docs/vinosefue/` en vez de Artifact temporal.
- 2026-07-03: El usuario rechazó la versión con diseño propio publicada como Artifact y pidió el archivo Word con el formato ya establecido en su Drive. Se subió como Google Doc nativo a la carpeta de Drive de Olvidata (ver detalle arriba). Corregida la instrucción de memoria que pedía diseño custom en cada documento a cliente.
