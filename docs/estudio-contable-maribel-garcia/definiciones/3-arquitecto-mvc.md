# Memoria - Arquitecto MVC

## Proyecto: estudio-contable-maribel-garcia
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Consultado `docs/patrones/catalogo.yml` y escaneados `docs/*/definiciones/`. No existe en el estudio un proyecto previo de conciliacion bancaria (matching entre dos fuentes de movimientos) — dominio nuevo. Candidatos de reutilizacion de **patron tecnico** (no de dominio):
- Parser de archivo Excel/CSV a filas tipadas con validacion de columnas — patron ya resuelto en `contadores-bma-conversor` (parser Excel propietario), aunque ahi era jerarquico/pivot y aca es tabular simple — se reutiliza el enfoque (parseo + validacion + reporte de errores), no el codigo linea por linea.
- ASP.NET Identity con login basico sin roles diferenciados — patron estandar del estudio.

Sin match de dominio para el motor de conciliacion ni para el modelo de datos Banco/MercadoPago — se construye desde cero.

### Nota tecnica: como se implementa "con IA" (justificacion del enfoque hibrido)
El pedido del lead es "IA para conciliar" — la implementacion tecnica correcta NO es enviar cada par de movimientos a un modelo de lenguaje (lento e innecesariamente costoso para lo que es, en la mayoria de los casos, un join exacto por monto+fecha). El enfoque de este diseño:
1. **Motor deterministico primero** (HU-03): matching por monto exacto + fecha dentro de tolerancia. Resuelve la mayoria del volumen sin IA, rapido y gratis en tiempo de ejecucion.
2. **IA solo para el remanente ambiguo** (HU-08, Etapa 2): los movimientos que el motor deterministico no concilia con certeza (candidatos multiples, diferencias de monto/fecha, conceptos parecidos) se pasan a la API de Claude para sugerir el candidato mas probable con una justificacion breve, que el contador confirma o rechaza (nunca auto-concilia sin revision humana).

Esto es honesto sobre que hace la IA realmente (asiste en el 10-20% dificil, no reemplaza el matching del 80-90% facil) y evita sobre-prometer "IA magica" al cliente.

### Primera integracion de API de IA en un producto entregado (sin precedente en el estudio)
Todos los proyectos previos del estudio son sistemas MVC tradicionales sin llamadas a un modelo de lenguaje en el producto final — la IA hasta ahora se usa en el proceso de DESARROLLO (este mismo estudio de agentes), nunca en tiempo de ejecucion del sistema entregado al cliente. Esta es la primera vez. Implicancias a resolver antes de implementar (Etapa 2, no bloquea Etapa 1):
- **Credencial de API**: se necesita una API key de Anthropic. A definir con el cliente si la provee el estudio (facturado en el mantenimiento) o el cliente (cuenta propia).
- **Costo operativo continuo**: cada corrida de conciliacion con casos ambiguos consume tokens de API en PRODUCCION — esto es distinto y ademas del costo interno de IA para el desarrollo (ver 4-presupuestador.md). Es un costo variable recurrente que no existia en ningun proyecto anterior del estudio y debe quedar explicito en la conversacion comercial, no asumido en silencio.
- Volumen esperado bajo (estudio de 1-2 personas, conciliaciones periodicas, no miles de movimientos por dia) — el costo operativo deberia ser marginal (unos pocos USD/mes), pero se declara como pregunta abierta, no como costo cero asumido.

### Componentes por capa
- **Domain**: `ExtractoBancario`, `MovimientoBancario`, `ExtractoMercadoPago`, `MovimientoMercadoPago`, `Conciliacion` (enum Estado: Conciliado/Sugerido/SinConciliar).
- **Application**: DTOs de importacion/listado, `IConciliacionService`, `IImportadorExtractoService`, `IAsistenteConciliacionIAService` (Etapa 2, interface para la llamada a Claude).
- **Infrastructure**: `ConciliacionService` (matching deterministico), `ImportadorExtractoBancarioService` / `ImportadorExtractoMercadoPagoService` (parsers especificos por formato), `AsistenteConciliacionIAService` (Etapa 2 — cliente HTTP a la API de Claude, prompt estructurado con los candidatos ambiguos, respuesta parseada a sugerencia + justificacion).
- **Web**: `ConciliacionController` (panel, importar, confirmar/rechazar sugerencia), `ReporteController` (exportar).

### Entidades y configuraciones EF
- `ExtractoBancario` / `ExtractoMercadoPago`: Id, FechaImportacion, NombreArchivoOriginal, ImportadoPorUserId.
- `MovimientoBancario` / `MovimientoMercadoPago`: Id, ExtractoId (FK), Fecha, Monto, Concepto, Estado (enum), ConciliacionId? (FK nullable).
- `Conciliacion`: Id, MovimientoBancarioId (FK), MovimientoMercadoPagoId (FK), Estado (Confirmado/Rechazado — solo existe si hubo sugerencia o match automatico), OrigenMatch (Automatico/IA/Manual), ConfirmadoPorUserId?, FechaConfirmacion?.

### Migraciones requeridas
- Migracion inicial: crea las 5 tablas de negocio + tablas estandar de Identity.
- Index en `MovimientoBancario.Fecha` y `MovimientoMercadoPago.Fecha` (soporte al matching por rango de fecha).

### Riesgos tecnicos activos
- **Formato real de los extractos**: sin confirmar con el lead (ver supuestos en 1-analista-funcional.md) — si el banco no exporta CSV/Excel tabular (solo PDF), el parser requiere OCR o extraccion de PDF, fuera de este alcance y presupuesto.
- **Ambiguedad de matching**: mas de un movimiento bancario podria calzar con mas de un movimiento de MP en el mismo rango de tolerancia (ej. dos pagos del mismo monto el mismo dia) — el diseno debe mostrar todos los candidatos posibles, nunca auto-resolver una ambiguedad real sin confirmacion humana.
- **Dependencia de servicio externo (Etapa 2)**: si la API de Claude no responde o excede timeout, el sistema debe degradar a mostrar el movimiento como "Sin conciliar" (revision 100% manual), nunca bloquear el flujo principal de conciliacion deterministica.

## Historial de ajustes
- 2026-08-20: primera version. Sin match de dominio cross-proyecto; reuso limitado a patron de parser de archivos. Primera integracion de API de IA en tiempo de ejecucion de un producto del estudio — sin precedente, riesgos y costo operativo declarados explicitamente.
