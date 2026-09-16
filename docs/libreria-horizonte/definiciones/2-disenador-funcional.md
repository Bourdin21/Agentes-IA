# Memoria - Disenador funcional

## Proyecto: libreria-horizonte
## Ultima actualizacion: 2026-09-15

## Definiciones vigentes

### Resultado del escaneo de reutilizacion
- `catalogo.yml`: sin patron de sincronizacion con marketplace. Coincidencias parciales reutilizables:
  - **PAT-012** Importacion de archivo con preview → confirmar (koi `ImportacionExcelKoiService`, la-platense `tools/ImportarHistorico`): base del flujo "subir export de Fixed → ver diferencias → confirmar" del Paso 2 y del lector de exports del Paso 1.
  - **PAT-005** Maquina de estados: lote de cambios.
  - **PAT-008** DataTables server-side + filtro por columna: listados de cambios, pendientes y ventas.
  - **PAT-032 / PAT-034** (olvidata-agentes-multirubro): "cambios propuestos como tarjetas confirmables" y "aprobacion humana" — se toma el **concepto** (el agente propone, el humano aprueba, el servicio ejecuta), no el codigo (producto en implementacion, multi-tenant).
- `docs/*/definiciones/`: century-21 relevo la API de MercadoLibre (solo busqueda publica, sin OAuth de vendedor ni escritura) — referencia de research, no de diseño.
- Decision: **diseño nuevo** para el cruce en cascada y la sincronizacion; **reutilizar** PAT-012/005/008. Se agrega **PAT-036** al catalogo (diseñado, sin implementacion).

### Alcance funcional resumido
- Paso 1: servicio del estudio, sin pantallas para el cliente. Entregables: archivos de edicion masiva ML aplicados, reporte y listado de libros sin publicar.
- Paso 2: panel web chico para 1-3 empleados de la libreria.

### Flujo del Paso 1 (servicio, sin UI)
1. Recepcion: export Fixed (Excel/CSV) + export ML (Excel del editor masivo o API de solo lectura).
2. Normalizacion: ISBN solo digitos, ISBN-10 → ISBN-13; titulos en minusculas, sin tildes, sin signos ni sufijos de formato ("tapa blanda", "edicion").
3. Cruce en cascada: (1) ISBN exacto, (2) SKU/codigo, (3) titulo+autor aproximado con umbral, (4) residuo a revision.
4. Revision: coincidencias aproximadas y residuo → clasificacion asistida por IA (propone vinculo + confianza) → planilla de revision; los casos dudosos los confirma el estudio o el cliente.
5. Decision por publicacion: pausar / ajustar cantidad / activar (solo si estaba pausada y tiene stock) / sin cambios / a revision.
6. Salida: archivos de edicion masiva en tandas + reporte en lenguaje de negocio + listado de libros sin publicar.
7. Aplicacion: el cliente sube las tandas (o en llamada conjunta); verificacion de 30 publicaciones al azar.

### Historias de usuario (Paso 2)
- HU-01: Como operador, quiero conectar la cuenta de MercadoLibre una sola vez para que el sistema pueda actualizar las publicaciones.
  - CA: tras autorizar, el panel muestra el usuario de ML conectado y la fecha de vencimiento de la conexion; si vence, el panel lo avisa antes de aplicar.
- HU-02: Como operador, quiero subir el export diario de Fixed y ver que cambiaria en ML antes de tocar nada.
  - CA: el preview muestra cantidades por tipo (pausar / ajustar / activar / sin cruzar) y el detalle por fila; nada se escribe en ML en este paso.
- HU-03: Como operador, quiero aprobar el lote de cambios para que se aplique solo en ML.
  - CA: al aprobar, el lote pasa a Aplicando; al terminar cada cambio queda Aplicado o Fallido con motivo; puedo reintentar solo los fallidos.
- HU-04: Como operador, quiero ver las ventas de ML para descontarlas en Fixed.
  - CA: cada venta aparece una sola vez; puedo marcar una o varias como "Cargada en Fixed" y desaparecen de pendientes.
- HU-05: Como operador, quiero vincular a mano los libros que el sistema no pudo cruzar.
  - CA: el vinculo manual se guarda y se usa en los lotes siguientes; puedo marcar una publicacion como "a pedido" para que nunca se pause por stock 0.
- HU-06: Como operador, quiero ver el historial de lotes aplicados para saber que se cambio y cuando.

### Flujos de pantalla acordados (Paso 2)
| # | Pantalla | Contenido | Acciones |
|---|---|---|---|
| P1 | Inicio | Estado de la conexion ML, ultimo export subido, lote pendiente, ventas pendientes de descontar, publicaciones sin cruzar | Ir a cada bandeja |
| P2 | Subir export de Fixed | Zona de carga + resultado del analisis (resumen por tipo + tabla de cambios) | Analizar / Aprobar lote / Descartar |
| P3 | Lotes | DataTable de lotes (fecha, estado, cantidades, usuario) → detalle con cambios y resultado | Reintentar fallidos |
| P4 | Sin cruzar | DataTable de publicaciones sin vinculo con sugerencias | Vincular / Marcar "a pedido" / Ignorar |
| P5 | Ventas ML | DataTable de ventas pendientes (fecha, publicacion, codigo Fixed, cantidad) | Marcar como cargada (individual o en lote) |
| P6 | Conexion ML | Estado + boton conectar/reconectar | Conectar |

Distribucion: titulo → resumen en tarjetas → tabla → acciones al pie; mismo orden en todas las pantallas.

### ViewModels definidos (Paso 2)
- SubirExportVm: Archivo (xlsx/csv, requerido, max 20 MB).
- PreviewLoteVm: TotalPausar, TotalAjustar, TotalActivar, TotalSinCruzar, Cambios[] (PublicacionId, Titulo, CodigoFixed, EstadoActual, CantidadActual, EstadoNuevo, CantidadNueva, MetodoCruce).
- LoteDetalleVm: Id, Fecha, Estado, Usuario, Cambios[] + Resultado/Motivo.
- VincularVm: PublicacionId (requerido), ArticuloFixedId (requerido) | MarcarAPedido (bool).
- VentaPendienteVm: VentaId, Fecha, Titulo, CodigoFixed, Cantidad, Seleccionada.

### Maquina de estados — Lote de cambios
| Origen | Evento | Destino | Guarda | Accion | Error esperado |
|---|---|---|---|---|---|
| — | Analizar export | Propuesto | archivo valido | calcula cambios | "El archivo no tiene las columnas codigo/descripcion/stock" |
| Propuesto | Aprobar | Aprobado | conexion ML vigente; no hay otro lote Aplicando | encola aplicacion | "La conexion con MercadoLibre vencio, reconectá la cuenta" |
| Propuesto | Descartar | Descartado | — | — | — |
| Aprobado | Inicia proceso | Aplicando | — | aplica cambio por cambio | — |
| Aplicando | Termina sin fallos | Aplicado | — | — | — |
| Aplicando | Termina con fallos | Aplicado con errores | — | guarda motivo por cambio | — |
| Aplicado con errores | Reintentar fallidos | Aprobado | conexion ML vigente | re-encola solo fallidos | idem Aprobar |
- Un lote Propuesto con mas de 24 h se marca Descartado al subir un export nuevo (evita aplicar diferencias viejas).

### Reglas de negocio y permisos
- Solo Operador y superusuario acceden. Todas las acciones requieren login.
- Nunca eliminar publicaciones (RF-01). Una publicacion "a pedido" nunca se pausa por stock 0.
- Cantidad a publicar = stock de Fixed (sin reserva de seguridad en esta version — hipotesis a validar: el cliente podria querer publicar stock − 1).

### Impacto funcional por capa
- Presentacion: 6 pantallas (Paso 2). Paso 1 sin UI.
- Negocio: motor de cruce (compartido Paso 1/Paso 2), calculo de diferencias, maquina de estados de lote, aplicacion en segundo plano.
- Datos: articulos Fixed, publicaciones ML, vinculos, lotes/cambios, ventas, conexion ML.

### Riesgos y supuestos (heredados del analisis que este diseño asume)
- Asume S-01 (Fixed exporta stock a Excel). Si no, el Paso 2 no es viable tal cual.
- Asume S-03 (una cuenta ML) y S-04 (stock real mucho menor que publicaciones).
- Asume pregunta 3 opcion A (una publicacion = un libro). Variantes/packs quedan fuera hasta confirmar.
- Asume pregunta 4 opcion A por defecto, con la marca "a pedido" como salida si resulta B.
- Riesgo: un cruce aproximado equivocado pausa un libro que si hay → mitigado con revision + aprobacion + reversible.

### Plan funcional por etapas (para el arquitecto)
- Etapa 1 = Paso 1 (servicio): lector de exports, motor de cruce, revision asistida, generador de archivos y reporte.
- Etapa 2 = Paso 2 (agente): panel P1-P6 reutilizando el motor de la Etapa 1.

## Historial de ajustes
- 2026-09-15: Diseño inicial de Paso 1 (servicio) y Paso 2 (panel de sincronizacion) con escaneo de reutilizacion; PAT-036 agregado al catalogo.
