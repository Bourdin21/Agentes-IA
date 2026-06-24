# Plan de Importación FABA AOL V2 → LabIPAC

> **Estado:** PLAN DEFINIDO — pendiente aprobación para implementar  
> **Alcance:** sólo lo útil para el sistema actual (sin módulo de autorizaciones por ahora)

---

## ✅ Qué provee el WS — verificado en vivo con datos reales

| Categoría solicitada | ¿FABA lo provee? | Operación WS | Modo |
|---|---|---|---|
| **Mutuales** | ✅ Completo | `UsuariosMutuales` + `DatosMutual` | Bulk / sincronización |
| **Unidades Bioquímicas** | ✅ CONFIRMADO — `PracticasPorMutual` devuelve analitos individuales | `PracticasPorMutual` | Bulk por mutual |
| **Prácticas (paquetes)** | ❌ No existe en FABA | — | Concepto interno LabIPAC |
| **Afiliados / Pacientes** | ⚠️ On-demand — requiere nro de afiliado o DNI | `ConsultarAfiliado` | Búsqueda individual |

### ⚠️ Corrección al análisis previo — confirmado con llamada real al WS

**`PracticasPorMutual` devuelve tests bioquímicos individuales, no paquetes.**

Datos reales IOMA (idMutual=1):
- **731 tests individuales**
- Campos: `idPractica` (int), `Nombre` (string) — sin precio, sin categoría
- Rango de IDs: 2 a 9993 (no secuenciales)
- Ejemplos: `[2] ACETONURIA CUALITATIVA`, `[22] AMILASEMIA`, `[66] HIV ANTICUERPOS TOTALES`, `[101] ALBUMINA`, `[9993] DETECCION DE LA MUTACION DEL GEN JAK2`

**Conclusión:**

| Concepto FABA | Equivalente en LabIPAC | Corresponde a |
|---|---|---|
| "Práctica" (`idPractica` + `Nombre`) | **`UnidadBioquimica`** | ✅ Match directo |
| No existe | **`Practica`** (paquete compuesto) | Concepto interno — no tiene par en FABA |

La entidad `Practica` en LabIPAC es un **paquete interno de facturación** agrupando múltiples `UnidadBioquimica`. FABA no conoce este concepto — sólo conoce el analito individual.

**Implicación para autorizaciones (futuro):**  
Cuando se someta una `Practica` compuesta a FABA (`ValidarOrdenV4`), se deben descomponer sus `PracticaDetalle` → cada `UnidadBioquimica` → buscar su `CodigoFaba` por mutual → enviar como `IntIdPractica1..24` (máx. 24 analitos por orden).

---

## Entidades nuevas / modificadas

### Nueva: `Mutual`

```csharp
// LabIPAC.Domain/Entities/Mutual.cs
public class Mutual : SoftDestroyable
{
	public int    IdFaba             { get; set; }   // clave FABA (unique)
	public string Nombre             { get; set; }   // max 150
	public int?   CodigoFacturante   { get; set; }   // CodFacturante del WS
	public bool   EsOsde             { get; set; }   // bifurca flujo ValidarOrden en futuro
	public bool   Activo             { get; set; } = true;
	public DateTime? UltimaSincMutuales  { get; set; }
	public DateTime? UltimaSincPracticas { get; set; }

	// Nav
	public ICollection<UnidadBioquimicaFabaCodigo> CodigosFaba { get; set; } = [];
}
```

### Nueva: `UnidadBioquimicaFabaCodigo` (mapeo analito FABA ↔ UB local, por mutual)

```csharp
// LabIPAC.Domain/Entities/UnidadBioquimicaFabaCodigo.cs
// No hereda SoftDestroyable — tabla de referencia
public class UnidadBioquimicaFabaCodigo
{
	public int Id { get; set; }

	public int    MutualId                   { get; set; }  // FK -> Mutual
	public Mutual Mutual                     { get; set; } = null!;

	public int    CodigoFaba                 { get; set; }  // idPractica del WS
	public string NombreFaba                 { get; set; } = string.Empty;  // max 200
	public bool   Activo                     { get; set; } = true;

	// Vínculo opcional al analito local (el operador vincula a posteriori)
	public int?              UnidadBioquimicaId { get; set; }
	public UnidadBioquimica? UnidadBioquimica   { get; set; }

	// Unique index: (MutualId, CodigoFaba)
}
```

> El mismo analito tiene códigos distintos por mutual: ALBUMINA = 101 en IOMA, otro valor en PAMI.  
> `UnidadBioquimicaId` es nullable: se importan todos los analitos del WS aunque aún no tengan par local.

### Modificada: `Paciente`

```csharp
// Agregar a Paciente.cs (todos nullables, no rompen datos existentes)
public int?    MutualId            { get; set; }
public Mutual? Mutual              { get; set; }
public string? DigitoAfiliado      { get; set; }  // max 3
public string? RelacionAfiliado    { get; set; }  // max 5 — "01"=Titular, "02"=Familiar
public int?    TipoDocumentoFabaId { get; set; }
```

> `ObraSocial` y `NroAfiliado` existentes se conservan.

---

## Etapas de implementación

---

### ETAPA 1 — Cliente SOAP + Configuración segura

**Objetivo:** infraestructura HTTP reutilizable para llamar al WS. Base de todas las demás etapas.

#### Archivos a crear

| Archivo | Capa | Descripción |
|---------|------|-------------|
| `Application/Settings/FabaSettings.cs` | Application | POCO de configuración |
| `Application/Interfaces/IFabaClient.cs` | Application | Interfaz de transporte SOAP |
| `Application/Interfaces/IFabaImportService.cs` | Application | Interfaz de negocio de importación |
| `Application/DTOs/Faba/FabaMutualDto.cs` | Application | DTO mutual |
| `Application/DTOs/Faba/FabaUnidadBioquimicaDto.cs` | Application | DTO analito FABA (idPractica + Nombre) |
| `Application/DTOs/Faba/FabaAfiliadoDto.cs` | Application | DTO afiliado/paciente |
| `Infrastructure/Services/Faba/FabaClient.cs` | Infrastructure | Implementación HTTP SOAP raw |
| `Infrastructure/Services/Faba/FabaResponseParser.cs` | Infrastructure | Parser XDocument de respuestas |
| `Infrastructure/Services/Faba/FabaImportService.cs` | Infrastructure | Lógica de sincronización |

#### `FabaSettings`

```csharp
public class FabaSettings
{
	public const string SectionName = "Faba";
	public string EndpointUrl    { get; set; } = string.Empty;
	public int    IdUsuario       { get; set; }
	public int    Password        { get; set; }
	public string TerminalId     { get; set; } = "LABIPAC-01";
	public int    TimeoutSeconds  { get; set; } = 30;
}
```

#### `appsettings.json` (sin credenciales reales)

```json
"Faba": {
  "EndpointUrl": "http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx",
  "IdUsuario": 0,
  "Password": 0,
  "TerminalId": "LABIPAC-01",
  "TimeoutSeconds": 30
}
```

#### User Secrets (desarrollo — ejecutar una vez)

```powershell
dotnet user-secrets set "Faba:IdUsuario" "5903" --project LabIPAC.Web
dotnet user-secrets set "Faba:Password"  "8491" --project LabIPAC.Web
```

#### Técnica SOAP (no WCF)

```csharp
// FabaClient construye el envelope dinámicamente:
private static string BuildEnvelope(string operation, string paramsXml) => $"""
	<?xml version="1.0" encoding="utf-8"?>
	<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
				   xmlns:tns="http://tempuri.org/">
	  <soap:Body>
		<tns:{operation}>
		  {paramsXml}
		</tns:{operation}>
	  </soap:Body>
	</soap:Envelope>
	""";

// Envío:
var content = new StringContent(envelope, Encoding.UTF8, "text/xml");
request.Headers.Add("SOAPAction", $"\"http://tempuri.org/{operation}\"");
var response = await _http.SendAsync(request);
var xml = await response.Content.ReadAsStringAsync();
// Extraer Result del envelope de respuesta
var doc = XDocument.Parse(xml);
var result = doc.Descendants("Result").FirstOrDefault()?.Value ?? string.Empty;
return result; // XML embebido como string
```

#### Registro en `DependencyInjection.cs`

```csharp
// Agregar al método AddInfrastructure():
services.Configure<FabaSettings>(configuration.GetSection(FabaSettings.SectionName));
services.AddHttpClient("faba", (sp, client) =>
{
	var settings = sp.GetRequiredService<IOptions<FabaSettings>>().Value;
	client.BaseAddress = new Uri(settings.EndpointUrl);
	client.Timeout = TimeSpan.FromSeconds(settings.TimeoutSeconds);
});
services.AddScoped<IFabaClient, FabaClient>();
services.AddScoped<IFabaImportService, FabaImportService>();
```

---

### ETAPA 2 — Entidades + Migraciones EF

**Objetivo:** crear las tablas en la base de datos. Sin lógica de negocio aún.

#### Archivos a crear/modificar

| Archivo | Acción | Capa |
|---------|--------|------|
| `Domain/Entities/Mutual.cs` | Crear | Domain |
| `Domain/Entities/PracticaFaba.cs` | Crear | Domain |
| `Domain/Entities/Paciente.cs` | Modificar (+4 campos FABA) | Domain |
| `Infrastructure/Data/AppDbContext.cs` | Modificar (3 DbSets + config Fluent) | Infrastructure |

#### Config Fluent API a agregar en `AppDbContext.OnModelCreating`

```csharp
// Mutual
modelBuilder.Entity<Mutual>(e => {
	e.Property(x => x.Nombre).HasMaxLength(150).IsRequired();
	e.HasIndex(x => x.IdFaba).IsUnique();
});

// PracticaFaba
modelBuilder.Entity<PracticaFaba>(e => {
	e.Property(x => x.NombreFaba).HasMaxLength(200).IsRequired();
	e.HasIndex(x => new { x.MutualId, x.CodigoFaba }).IsUnique();
	e.HasOne(x => x.Mutual).WithMany(m => m.PracticasFaba)
		.HasForeignKey(x => x.MutualId).OnDelete(DeleteBehavior.Restrict);
	e.HasOne(x => x.PracticaLocal).WithMany()
		.HasForeignKey(x => x.PracticaLocalId).IsRequired(false)
		.OnDelete(DeleteBehavior.SetNull);
});

// Paciente — agregar FK Mutual
modelBuilder.Entity<Paciente>(e => {
	e.Property(x => x.DigitoAfiliado).HasMaxLength(3);
	e.Property(x => x.RelacionAfiliado).HasMaxLength(5);
	e.HasOne(x => x.Mutual).WithMany()
		.HasForeignKey(x => x.MutualId).IsRequired(false)
		.OnDelete(DeleteBehavior.SetNull);
});
```

#### Migraciones (orden obligatorio)

```powershell
# 1 — Mutuales y PracticasFaba
dotnet ef migrations add AddMutualYPracticaFaba `
	--project LabIPAC.Infrastructure --startup-project LabIPAC.Web

# 2 — Campos FABA en Paciente
dotnet ef migrations add PacienteAddFabaFields `
	--project LabIPAC.Infrastructure --startup-project LabIPAC.Web

# Aplicar
dotnet ef database update --project LabIPAC.Infrastructure --startup-project LabIPAC.Web
```

---

### ETAPA 3 — Importar Mutuales

**Objetivo:** poblar la tabla `Mutuales` con datos reales de FABA. Botón manual en UI.

#### Flujo técnico

```
[Botón "Sincronizar Mutuales" en UI]
		↓
FabaImportService.SincronizarMutualesAsync()
		↓
FabaClient.UsuariosMutuales()    →  Result: XML list<(IdMutual, Nombre, ...)>
		↓
Para cada mutual:
  FabaClient.DatosMutual(idMutual)  →  Result: XML (CodigoFacturante, EsOsde, ...)
		↓
Upsert en DB por IdFaba (Insert si nuevo, Update si cambia nombre/código)
Soft-delete mutuales que ya no están en la lista
		↓
Actualizar UltimaSincMutuales en cada Mutual
		↓
Devolver ServiceResult con resumen: X insertadas, Y actualizadas, Z eliminadas
```

#### Archivos afectados

| Archivo | Capa | Acción |
|---------|------|--------|
| `Application/Interfaces/IFabaImportService.cs` | App | + `SincronizarMutualesAsync()` |
| `Infrastructure/Services/Faba/FabaClient.cs` | Infra | + `UsuariosMutualesAsync()`, `DatosMutualAsync()` |
| `Infrastructure/Services/Faba/FabaImportService.cs` | Infra | Implementación |
| `Infrastructure/Services/Faba/FabaResponseParser.cs` | Infra | + parsers para mutuales |
| `Web/Controllers/MutualesController.cs` | Web | Nuevo (CRUD + acción Sincronizar) |
| `Web/Models/MutualViewModels.cs` | Web | Nuevo |
| `Web/Views/Mutuales/Index.cshtml` | Web | Nueva vista |
| `Web/Views/Mutuales/Edit.cshtml` | Web | Nueva vista |

#### UI — `MutualesController`

- `GET Index` → DataTables server-side: Id, IdFaba, Nombre, Código Facturante, EsOsde, Activo, Última Sync
- `POST Sincronizar` → llama `SincronizarMutualesAsync()` → `TempData["SuccessMessage"]` con resumen
- `GET/POST Edit` → permite editar `EsOsde`, `Activo`, `Nombre` local (sin alterar `IdFaba`)

---

### ETAPA 4 — Importar Prácticas FABA

**Objetivo:** poblar `PracticasFaba` con códigos de facturación de cada mutual. Permite luego mapear a `Practica` local.

#### Flujo técnico

```
[Botón "Sincronizar Prácticas" en pantalla de una Mutual]
		↓
FabaImportService.SincronizarPracticasAsync(int mutualId)
		↓
FabaClient.UltimoCambioPractica(idFaba)  →  timestamp del WS
Si timestamp == UltimaSincPracticas → "Sin cambios" → retornar
		↓
FabaClient.PracticasPorMutual(idFaba)    →  Result: XML list<(CodigoFaba, Nombre, ...)>
		↓
Upsert en DB por (MutualId, CodigoFaba)
Soft-delete prácticas que ya no estén en la respuesta
Actualizar UltimaSincPracticas en Mutual
		↓
Devolver ServiceResult: X insertadas, Y actualizadas, Z eliminadas
```

#### Mapeo a Practica local (paso manual posterior)

Pantalla: en `PracticasController.Edit` → sección "Código FABA por mutual":

```
| Mutual         | Código FABA | Nombre FABA          | [Vincular] |
|----------------|-------------|----------------------|------------|
| IOMA           | 501         | Hemograma completo   | ✓ Vinculado|
| OSDE           | 1205        | Hemograma c/recuento | [Vincular] |
| Swiss Medical  | —           | Sin código           |            |
```

Acción: `PracticasController.VincularFaba(practicaId, practicaFabaId)` → setea `PracticaFaba.PracticaLocalId`.

#### Archivos afectados

| Archivo | Capa | Acción |
|---------|------|--------|
| `IFabaImportService.cs` | App | + `SincronizarPracticasAsync(int mutualId)` |
| `FabaClient.cs` | Infra | + `PracticasPorMutualAsync()`, `UltimoCambioPracticaAsync()` |
| `FabaImportService.cs` | Infra | Implementación |
| `FabaResponseParser.cs` | Infra | + parser prácticas FABA |
| `MutualesController.cs` | Web | + `POST SincronizarPracticas(int id)` |
| `PracticasController.cs` | Web | + sección Códigos FABA en Edit |
| `PracticaViewModels.cs` | Web | + `IEnumerable<PracticaFabaItemVm> CodigosFaba` |

---

### ETAPA 5 — Búsqueda de Afiliado en Pacientes

**Objetivo:** al crear/editar un paciente, buscar sus datos en FABA para auto-completar el formulario.  
**NO es una importación masiva** — FABA no provee dump de pacientes.

#### Flujo técnico

```
[Usuario escribe DNI o Legajo en formulario Paciente]
		↓  (AJAX — GET)
PacientesController.BuscarAfiliadoFaba?mutualId=X&tipo=D&valor=12345678
		↓
FabaImportService.ConsultarAfiliadoAsync(request)
		↓
FabaClient.ConsultarAfiliado(idMutual, tipoBusqueda, ...)
		↓
FabaResponseParser.ParseAfiliado(xmlResult)  →  FabaAfiliadoDto
		↓
JSON response:
{
  "encontrado": true,
  "nombre": "GARCIA",
  "apellido": "JUAN CARLOS",
  "sexo": 1,
  "fechaNacimiento": "1980-05-14",
  "nroAfiliado": "0012345678",
  "digito": "01",
  "relacion": "01",
  "tipoDocumento": 1,
  "nroDocumento": 12345678,
  "mutual": { "idFaba": 15, "nombre": "IOMA" }
}
		↓
JS pre-completa campos del form con los datos recibidos
```

#### Modos de búsqueda

| `IdTipoBusqueda` | Descripción | Parámetros usados |
|---|---|---|
| `"L"` | Por número de legajo | `strLegajo`, `strDigito`, `strRelacion` |
| `"D"` | Por número de documento | `strTipoDocumento`, `intNroDocumento` |

La UI ofrecerá ambas opciones en el formulario de Paciente.

#### Archivos afectados

| Archivo | Capa | Acción |
|---------|------|--------|
| `IFabaImportService.cs` | App | + `ConsultarAfiliadoAsync(FabaAfiliadoRequest)` |
| `Application/DTOs/Faba/FabaAfiliadoDto.cs` | App | Nuevo DTO |
| `Application/DTOs/Faba/FabaAfiliadoRequest.cs` | App | Nuevo request |
| `FabaClient.cs` | Infra | + `ConsultarAfiliadoAsync()` |
| `FabaImportService.cs` | Infra | Implementación |
| `FabaResponseParser.cs` | Infra | + `ParseAfiliado()` |
| `PacientesController.cs` | Web | + `GET BuscarAfiliadoFaba(...)` |
| `PacienteViewModels.cs` | Web | + campo `MutualId`, `DigitoAfiliado`, `RelacionAfiliado` |
| `Views/Pacientes/Create.cshtml` | Web | + sección "Buscar en FABA" con AJAX |
| `Views/Pacientes/Edit.cshtml` | Web | Ídem |

---

### ETAPA 6 — Panel de Administración FABA

**Objetivo:** pantalla unificada de estado de sincronización. No agrega nueva lógica.

#### UI: `Views/Mutuales/Index.cshtml` (expandida)

```
┌─────────────────────────────────────────────────────────────┐
│  Mutuales FABA                           [Sincronizar todo] │
├──────┬────────────────┬──────────┬──────────┬───────────────┤
│ FABA │ Nombre         │ Prácticas│ Últ. Sync│ Acciones      │
├──────┼────────────────┼──────────┼──────────┼───────────────┤
│  15  │ IOMA           │ 312      │ 03/01/25 │ [Sync] [Edit] │
│  22  │ OSDE           │ 287      │ 03/01/25 │ [Sync] [Edit] │
│  31  │ Swiss Medical  │ —        │ Nunca    │ [Sync] [Edit] │
└──────┴────────────────┴──────────┴──────────┴───────────────┘
```

---

## Resumen de cambios por capa

| Capa | Nuevos archivos | Archivos modificados |
|------|----------------|---------------------|
| **Domain** | `Mutual.cs`, `PracticaFaba.cs` | `Paciente.cs` (+4 campos) |
| **Application** | `IFabaClient.cs`, `IFabaImportService.cs`, `FabaSettings.cs`, `FabaMutualDto.cs`, `FabaPracticaDto.cs`, `FabaAfiliadoDto.cs`, `FabaAfiliadoRequest.cs` | — |
| **Infrastructure** | `FabaClient.cs`, `FabaImportService.cs`, `FabaResponseParser.cs` | `AppDbContext.cs` (+3 DbSets, +Fluent config), `DependencyInjection.cs` (+registros) |
| **Web** | `MutualesController.cs`, `MutualViewModels.cs`, `Views/Mutuales/*.cshtml` | `PacientesController.cs`, `PacientesViewModels.cs`, `Views/Pacientes/Create+Edit.cshtml`, `PracticasController.cs`, `Views/Practicas/Edit.cshtml`, `appsettings.json`, sidebar `_Layout.cshtml` |

**Total archivos:** ~20 nuevos, ~8 modificados.

---

## Migraciones EF (orden de ejecución)

```
1. AddMutualYPracticaFaba      → crea tablas Mutuales + PracticasFaba
2. PacienteAddFabaFields       → agrega 4 columnas nullable a Pacientes
```

---

## Unidades Bioquímicas — conclusión

> FABA **no provee** este dato. Las "prácticas FABA" (`PracticasPorMutual`) son códigos de facturación para obras sociales — equivalen a las `Practica` locales, no a las `UnidadBioquimica`.  
> Las `UnidadesBioquimicas` son componentes internos del laboratorio y **deben cargarse manualmente** (ya existe el módulo en el sistema).  
> El vínculo entre ambos mundos es: `PracticaFaba.PracticaLocalId → Practica → UnidadesBioquimicas` (vía `PracticaDetalle`).

---

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| XML de respuesta varía entre mutuales | `FabaResponseParser` tolerante a nulos + logging de raw XML en caso de error |
| WS en HTTP (sin TLS) | Aceptable para LAN/intranet; no enviar por internet abierto |
| Credenciales en código | User Secrets (dev) + variables de entorno (prod) — NUNCA en appsettings commiteado |
| `PracticasPorMutual` devuelve miles de registros | Procesamiento en chunks de 100 con `SaveChangesAsync` por lote |
| Timeout del WS en horas pico | `TimeoutSeconds` = 30; reintentar 1 vez con back-off de 2s |
| Afiliado no encontrado en FABA | Flujo degrada gracefully: form se llena manualmente igual |
