# Implementador — LabIPAC
> Memoria acumulativa del agente implementador. Actualizar al inicio y cierre de cada etapa.

---

## Historial de sesiones

### Sesión 1 — Análisis de integración FABA AOL WS V2
**Fecha:** 2025  
**Estado:** ANÁLISIS COMPLETO — pendiente aprobación para implementar

---

### Sesión 2 — Implementación FABA (Etapas 1–4 + Web Layer)
**Fecha:** 2026-06-17/18  
**Estado:** ✅ BUILD OK — Migración generada, pendiente aplicar a DB (credenciales no configuradas en entorno de desarrollo)

#### Archivos creados

**Application:**
- `LabIPAC.Application/Settings/FabaSettings.cs`
- `LabIPAC.Application/Interfaces/IFabaClient.cs`
- `LabIPAC.Application/Interfaces/IFabaImportService.cs`
- `LabIPAC.Application/DTOs/Faba/FabaMutualDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaUnidadBioquimicaDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoRequest.cs`
- `LabIPAC.Application/DTOs/Faba/FabaAfiliadoDto.cs`
- `LabIPAC.Application/DTOs/Faba/FabaImportResumenDto.cs`

**Domain:**
- `LabIPAC.Domain/Entities/Mutual.cs` — hereda SoftDestroyable
- `LabIPAC.Domain/Entities/UnidadBioquimicaFabaCodigo.cs` — sin SoftDestroyable (gestión por campo Activo)
- `LabIPAC.Domain/Entities/Paciente.cs` — extendido con `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

**Infrastructure:**
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs`
- `LabIPAC.Infrastructure/Services/Faba/FabaImportService.cs`

**Web:**
- `LabIPAC.Web/Controllers/FabaController.cs` — acceso `RequireAdministracion`
- `LabIPAC.Web/Models/FabaViewModels.cs`
- `LabIPAC.Web/Views/Faba/Index.cshtml` — listado de mutuales + sincronización
- `LabIPAC.Web/Views/Faba/Analitos.cshtml` — analitos por mutual + vinculación AJAX a UB local
- `LabIPAC.Web/Views/Faba/ConsultarAfiliado.cshtml` — consulta afiliado por DNI o legajo

#### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `LabIPAC.Infrastructure/Data/AppDbContext.cs` | DbSets Mutuales, UnidadesBioquimicasFabaCodigos; config Fluent API; FK Paciente→Mutual |
| `LabIPAC.Infrastructure/DependencyInjection.cs` | Registro FabaSettings, HttpClient "faba", IFabaClient, IFabaImportService |
| `LabIPAC.Web/appsettings.json` | Sección `Faba` placeholder |
| `LabIPAC.Web/Views/Shared/_Layout.cshtml` | Entrada "Integración FABA" en sidebar bajo Administración |

#### Migración EF generada
- Nombre: `AddFabaMutualYAnalitos`
- Script SQL: `docs/labipac/migrations/AddFabaMutualYAnalitos.sql`
- Estado: **generada, pendiente aplicar** (requiere connection string en User Secrets)
- Tablas nuevas: `Mutuales`, `UnidadesBioquimicasFabaCodigos`
- Columnas nuevas en `Pacientes`: `MutualId`, `DigitoAfiliado`, `RelacionAfiliado`, `TipoDocumentoFabaId`

#### Corrección modelo de datos
- ⚠️ FABA "prácticas" (PracticasPorMutual) son **analitos bioquímicos individuales** → mapean a `UnidadBioquimica`, NO a `Practica` (que es un paquete interno del sistema)
- La entidad `UnidadBioquimicaFabaCodigo` reemplaza el nombre `PracticaFabaMapping` del plan original

#### Pendiente (Etapas 5–6)
- [ ] Aplicar migración a DB de desarrollo (configurar User Secrets: `Faba:IdUsuario`, `Faba:Password`)
- [ ] Etapa 5: Módulo Autorizaciones (`AutorizacionFaba`, `ValidarOrdenV4`)
- [ ] Etapa 6: Catálogos auxiliares (Diagnósticos, Prestadores)
- [ ] Integración lookup FABA desde formulario Create/Edit de Paciente

---

## 0. Escaneo de reutilización
No existe `/docs/indice.md` ni otros proyectos en el historial. Implementación desde cero.

---

## 1. Análisis del Web Service FABA AOL V2

**WSDL:** `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsdl`  
**Endpoint SOAP 1.1 / HTTP POST**  
**Auth:** `idUsuario` (int) + `password` (int) en cada llamada  
**Respuestas:** todas retornan `Result: xsd:string` — contiene XML embebido como texto

### 1.1 Inventario completo de operaciones (37)

| # | Operación | Grupo | Parámetros clave (sin auth) |
|---|-----------|-------|-----------------------------|
| 1 | `UsuariosMutuales` | Maestros | — |
| 2 | `DatosMutual` | Maestros | `Idmutual` |
| 3 | `TiposDocumentos` | Maestros | `Idmutual` |
| 4 | `Coseguros` | Maestros | `Idmutual` |
| 5 | `TiposBonos` | Maestros | — |
| 6 | `ConsultarAfiliado` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strDigito`, `strRelacion`, `strTipoDocumento`, `intNroDocumento` |
| 7 | `ConsultarAfiliadoOsde` | Afiliados | `Idmutual`, `IdTipoBusqueda`, `strLegajo`, `strCodSeguridad`, `CodFacturante` |
| 8 | `ConsultarAfiliadoTransaccion` | Afiliados | `NroTransaccion` |
| 9 | `PracticasPorMutual` | Catálogos | `Idmutual` |
| 10 | `DiagnosticosV3` | Catálogos | `Idmutual`, `MuestraCombo` |
| 11 | `Diagnosticos` | Catálogos | (versión anterior de DiagnosticosV3) |
| 12 | `DiagnosticosAlfabetico` | Catálogos | — |
| 13 | `Prestadores` | Catálogos | `Idmutual`, `nombre` (búsqueda) |
| 14 | `UltimoCambioPractica` | Sincronización | `Idmutual` |
| 15 | `UltimoCambioUsuario` | Sincronización | — |
| 16 | `ValidarOrdenV4` | Autorizaciones | `Idmutual`, datos afiliado, datos médico, hasta 24 prácticas (int), coseguro, bono, diagnósticos |
| 17 | `ValidarOrdenfV4` | Autorizaciones | Igual pero prácticas como `string` (lista separada) |
| 18 | `ValidarOrdenV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenV4 |
| 19 | `ValidarOrdenfV3` | Autorizaciones (old) | Versión anterior de ValidarOrdenfV4 |
| 20 | `ValidarOrdenOsde` | Autorizaciones OSDE | Específico OSDE (versión anterior) |
| 21 | `ValidarOrdenOsdeWS` | Autorizaciones OSDE | Específico OSDE (versión actual, hasta 24 prácticas) |
| 22 | `ConsultarOrden` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 23 | `ConsultarOrdenConValoresSugeridos` | Gestión órdenes | `Idmutual`, `NroTransaccion` |
| 24 | `ModificarFechaRealizacion` | Gestión órdenes | `NroTransaccion`, `FechaRealizacion` |
| 25 | `SuspenderOrden` | Gestión órdenes | `NroTransaccion` |
| 26 | `EliminarSuspensionOrden` | Gestión órdenes | `NroTransaccion` |
| 27 | `ConsultarSuspension` | Gestión órdenes | `NroTransaccion` |
| 28 | `Recurrir` | Apelaciones | `NroTransaccion`, `Mensaje` |
| 29 | `AgregarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 30 | `EliminarBono` | Bonos | `NroTransaccion`, `Coseguro`, `TipoBono`, `NroBono`, `BonoNuevo` |
| 31 | `ConsultarBonos` | Bonos | `NroTransaccion` |
| 32 | `ConsultarTransaccionDeBono` | Bonos | `NroTransaccion` |
| 33 | `AceptarAuditoria` | Auditoría | `NroAutorizacion` |
| 34 | `ConsultaConfirmacionAuditoria` | Auditoría | `NroAutorizacion` |
| 35 | `ConsultarMensajes` | Mensajería | — |
| 36 | `GrabarMensajes` | Mensajería | — |
| 37 | `ValidarUsuario` | Sistema | — |
| 38 | `CambioClave` | Sistema | — |

### 1.2 Notas técnicas del WS
- SOAP 1.1, estilo RPC/encoded (antiguo)
- Todas las respuestas son `Result: xsd:string` conteniendo **XML embebido como string**
- El XML de respuesta debe parsearse con `XDocument.Parse(result)`
- `ProcessingId` = GUID generado por el cliente por llamada
- `Terminal` = identificador de la máquina cliente (ej: nombre del host)
- **No usa WS-Security** — credenciales van en el body de cada operación

---

## 2. Funcionalidades del WS relevantes para LabIPAC

### Prioridad ALTA — Impacto directo en flujo de trabajo

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Maestro de Mutuales sincronizado | `UsuariosMutuales`, `DatosMutual` | Nuevo módulo `Mutuales` |
| Validación/búsqueda de afiliado | `ConsultarAfiliado`, `ConsultarAfiliadoOsde` | Módulo `Pacientes` (lookup en carga) |
| Catálogo de prácticas por mutual | `PracticasPorMutual`, `UltimoCambioPractica` | Módulo `Practicas` (mapeo FABA codes) |
| Autorización de órdenes | `ValidarOrdenV4`, `ValidarOrdenfV4` | Nuevo módulo `Autorizaciones` |
| Consulta de orden autorizada | `ConsultarOrden`, `ConsultarOrdenConValoresSugeridos` | Nuevo módulo `Autorizaciones` |

### Prioridad MEDIA

| Funcionalidad | Operaciones WS | Módulo LabIPAC afectado |
|---|---|---|
| Gestión de bonos/coseguros | `AgregarBono`, `EliminarBono`, `ConsultarBonos` | Módulo `Autorizaciones` (sub-flujo) |
| Diagnósticos CIE-10 | `DiagnosticosV3` | Nuevo módulo `Diagnosticos` (catálogo) |
| Modificar / suspender órdenes | `ModificarFechaRealizacion`, `SuspenderOrden`, etc. | Módulo `Autorizaciones` |
| Prestadores médicos | `Prestadores` | Nuevo catálogo `Prestadores` |
| Apelaciones | `Recurrir` | Módulo `Autorizaciones` |

### Prioridad BAJA (backlog)

| Funcionalidad | Operaciones WS |
|---|---|
| Auditoría médica FABA | `AceptarAuditoria`, `ConsultaConfirmacionAuditoria` |
| Mensajería interna FABA | `ConsultarMensajes`, `GrabarMensajes` |
| Soporte OSDE específico | `ValidarOrdenOsdeWS`, `ConsultarAfiliadoOsde` |
| Gestión de credenciales | `ValidarUsuario`, `CambioClave` |

---

## 3. Plan de implementación por etapas

### Etapa 1 — Infraestructura SOAP y configuración (prereq de todo)

**Objetivo:** cliente SOAP reutilizable, configuración segura de credenciales.

**Archivos a crear:**
- `LabIPAC.Application/Settings/FabaSettings.cs` — POCO con `IdUsuario`, `Password`, `TerminalId`, `EndpointUrl`
- `LabIPAC.Application/Interfaces/IFabaClient.cs` — interfaz de bajo nivel (enviar/recibir SOAP)
- `LabIPAC.Application/Interfaces/IFabaService.cs` — interfaz de alto nivel (métodos de negocio)
- `LabIPAC.Infrastructure/Services/Faba/FabaClient.cs` — implementación HTTP SOAP (raw envelope, `IHttpClientFactory`)
- `LabIPAC.Infrastructure/Services/Faba/FabaResponseParser.cs` — parseador `XDocument` de respuestas
- `appsettings.json` (sección `Faba`) — sólo placeholder, sin credenciales reales
- User Secrets: `Faba:IdUsuario` y `Faba:Password`

**Técnica:** `IHttpClientFactory` + SOAP 1.1 envelope generado dinámicamente (sin WCF). Evitar `dotnet-svcutil` ya que el WSDL es RPC/encoded y genera código difícil de mantener en .NET 10.

**Patrón SOAP envelope:**
```xml
POST http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://tempuri.org/{OperationName}"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
	<{OperationName} xmlns="http://tempuri.org/">
	  <idUsuario>5903</idUsuario>
	  <password>8491</password>
	  <!-- params -->
	</{OperationName}>
  </soap:Body>
</soap:Envelope>
```

---

### Etapa 2 — Módulo Mutuales (maestro sincronizado)

**Objetivo:** Entidad `Mutual` local sincronizada con `UsuariosMutuales` + `DatosMutual`.

**Domain:**
- Nueva entidad `Mutual : SoftDestroyable`
  - `IdFaba` (int) — clave del WS, unique index
  - `Nombre` (string)
  - `CodigoFacturante` (int?)
  - `EsOsde` (bool) — para bifurcar entre ValidarOrdenV4 / ValidarOrdenOsdeWS
  - `Activo` (bool)

**Application:**
- `IFabaService.SincronizarMutualesAsync()` → llama `UsuariosMutuales`, upsert en DB

**Infrastructure:**
- `FabaService.SincronizarMutualesAsync()`

**Web:**
- `MutualesController` — CRUD local + botón "Sincronizar con FABA"
- Vista `Index` con DataTables server-side, badge activo/inactivo, columna `IdFaba`

**Migración EF:** `AddMigration AddMutual`

---

### Etapa 3 — Mapeo Prácticas ↔ FABA por mutual

**Objetivo:** Cada `Practica` local tiene un código FABA por mutual para poder incluirla en una autorización.

**Domain:**
- Nueva entidad `PracticaFabaMapping : SoftDestroyable`
  - `PracticaId` (FK → Practica)
  - `MutualId` (FK → Mutual)
  - `CodigoFaba` (int) — `IdPractica` del WS
  - Índice único (`PracticaId`, `MutualId`)

**Application:**
- `IFabaService.SincronizarPracticasAsync(int mutualId)` → llama `PracticasPorMutual`, upsert mappings
- `IFabaService.UltimoCambioPracticaAsync(int mutualId)` → para invalidar caché

**Web:**
- En `PracticasController.Edit`: nueva sección "Códigos FABA por mutual" — tabla de mappings

**Migración EF:** `AddMigration AddPracticaFabaMapping`

---

### Etapa 4 — Lookup de afiliado en módulo Pacientes

**Objetivo:** Al crear/editar un paciente, buscar en FABA para completar datos de mutual y validar afiliación.

**Domain — expansión `Paciente`:**
- `MutualId` (int?, FK → Mutual)
- `DigitoAfiliado` (string?) — `strDigito` del WS
- `RelacionAfiliado` (string?) — `strRelacion` (titular/familiar)
- `TipoDocumentoFabaId` (int?) — tipo de documento según la mutual

**Application:**
- `IFabaService.ConsultarAfiliadoAsync(FabaAfiliadoRequest)` → devuelve `FabaAfiliadoDto`
- DTO `FabaAfiliadoDto`: NombreCompleto, Sexo, FechaNacimiento, NroAfiliado, Mutual, Estado

**Web:**
- `PacientesController`: nuevo endpoint `[HttpGet] BuscarAfiliadoFaba` (AJAX, devuelve JSON)
- En `Create`/`Edit` Paciente: botón "Buscar en FABA" que dispara AJAX y pre-completa campos

**Migración EF:** `AddMigration PacienteAddMutualFields`

---

### Etapa 5 — Módulo Autorizaciones (core)

**Objetivo:** Registrar y gestionar autorizaciones de órdenes FABA.

**Domain:**
- Nueva entidad `AutorizacionFaba : SoftDestroyable`
  - `PacienteId` (FK → Paciente)
  - `MutualId` (FK → Mutual)
  - `NroTransaccion` (int?) — asignado por FABA al autorizar
  - `NroAutorizacion` (string?) — número legible de autorización
  - `Estado` (enum `EstadoAutorizacion`: Borrador, Autorizada, Rechazada, Suspendida, Apelada)
  - `FechaPrescripcion` (DateOnly)
  - `FechaRealizacion` (DateOnly)
  - `NombreMedico` (string)
  - `MatriculaMedico` (string)
  - `TipoMatricula` (string) — Nacional/Provincial
  - `IdDiagnostico1` (string?), `IdDiagnostico2` (string?)
  - `Telefono` (string?)
  - `Observacion` (string?)
  - `TipoBono` (int?), `NroBono` (int?), `Coseguro` (int?)
  - `RespuestaXmlFaba` (string?) — XML completo de respuesta para auditoría
  - Navegación: `ICollection<AutorizacionDetalle>`

- Nueva entidad `AutorizacionDetalle`
  - `AutorizacionFabaId` (FK)
  - `PracticaId` (FK → Practica)
  - `CodigoFaba` (int) — código enviado al WS
  - `Orden` (int) — posición 1..24

**Application:**
- `IFabaService.ValidarOrdenAsync(FabaOrdenRequest)` → devuelve `FabaOrdenResultDto`
- `IFabaService.ConsultarOrdenAsync(int mutual, int nroTransaccion)` → estado actual
- `IFabaService.SuspenderOrdenAsync(int nroTransaccion)`
- `IFabaService.RecurrirAsync(int nroTransaccion, string mensaje)`
- DTO `FabaOrdenRequest`, `FabaOrdenResultDto`

**Web:**
- `AutorizacionesController`: CRUD completo + acción `Autorizar` (POST → WS → guarda resultado)
- Vistas: `Index` (DataTables server-side), `Create`, `Details`, `Autorizar` (wizard 3 pasos)

**Migración EF:** `AddMigration AddAutorizacionFaba`

---

### Etapa 6 — Diagnósticos y Prestadores (catálogos auxiliares)

**Objetivo:** Catálogos locales con sincronización on-demand.

**Domain:**
- `DiagnosticoFaba` (sin herencia SoftDestroyable — sólo lectura): `Codigo`, `Descripcion`, `MutualId`
- `Prestador` (sin herencia): `IdFaba`, `Nombre`, `MutualId`

**Application:** `IFabaService.ObtenerDiagnosticosAsync(int mutual)`, `IFabaService.BuscarPrestadoresAsync(int mutual, string nombre)`

**Web:** Endpoints AJAX para autocompletar en formulario de autorización.

---

## 4. Cambios por capa — resumen

| Capa | Nuevos archivos | Archivos modificados |
|------|----------------|---------------------|
| Domain | `Mutual`, `PracticaFabaMapping`, `AutorizacionFaba`, `AutorizacionDetalle`, `DiagnosticoFaba`, `Prestador` + enum `EstadoAutorizacion` | `Paciente` (+ campos mutual) |
| Application | `IFabaClient`, `IFabaService`, `FabaSettings`, DTOs: `FabaAfiliadoDto`, `FabaOrdenRequest`, `FabaOrdenResultDto` | — |
| Infrastructure | `FabaClient`, `FabaService`, `FabaResponseParser` + config `AddFabaServices()` | `AppDbContext` (DbSets nuevos + config Fluent) |
| Web | `MutualesController`, `AutorizacionesController` + ViewModels + Vistas | `PacientesController` + vista Create/Edit, `appsettings.json`, `Program.cs` |

---

## 5. Migraciones EF requeridas

```
1. AddMutual
2. AddPracticaFabaMapping
3. PacienteAddMutualFields
4. AddAutorizacionFaba
5. AddCatalogsFabaAux  (DiagnosticoFaba, Prestador)
```

---

## 6. Configuración segura de credenciales

**appsettings.json** (placeholder sin valor real):
```json
"Faba": {
  "EndpointUrl": "http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.asmx",
  "IdUsuario": 0,
  "Password": 0,
  "TerminalId": "LABIPAC-01",
  "TimeoutSeconds": 30
}
```

**User Secrets (desarrollo) — ejecutar:**
```powershell
dotnet user-secrets set "Faba:IdUsuario" "5903" --project LabIPAC.Web
dotnet user-secrets set "Faba:Password"  "8491" --project LabIPAC.Web
```

**Producción:** variables de entorno `Faba__IdUsuario` / `Faba__Password`.  
❌ **NUNCA hardcodear credenciales en código ni en appsettings.Production.json**.

---

## 7. Paquetes NuGet necesarios

| Paquete | Capa | Justificación |
|---------|------|---------------|
| Ninguno nuevo | — | Se usa `IHttpClientFactory` (ya en `Microsoft.AspNetCore.App`) + `System.Xml.Linq` (BCL). No se necesita WCF ni `dotnet-svcutil` |

---

## 8. Riesgos y supuestos

| Riesgo | Mitigación |
|--------|------------|
| El WS responde con XML mal formado o con entidades HTML | `FabaResponseParser` debe ser tolerante; loguear raw response |
| Timeout en validaciones (el WS es lento) | `TimeoutSeconds` configurable; mostrar spinner en UI |
| Mutual OSDE requiere flujo diferente (`ValidarOrdenOsdeWS`) | Campo `EsOsde` en `Mutual` bifurca la lógica en `FabaService` |
| Los códigos de prácticas FABA difieren entre mutuales | `PracticaFabaMapping` resuelve el M:N |
| Respuestas varían entre mutuales (no todas implementan todo) | Manejo defensivo en parser, `ServiceResult.IsSuccess = false` con detalle |
| WSDL en HTTP (no HTTPS) | Riesgo en producción; usar proxy HTTPS si es posible |

---

## 9. Decisión de arquitectura

- **No usar WCF / `dotnet-svcutil`**: el WSDL es RPC/encoded (no Document/Literal), genera proxies difíciles de mantener en .NET 10. En su lugar, envelopes SOAP construidos con interpolación de strings o `XDocument`, enviados con `HttpClient`.
- **`IFabaClient`** (Infrastructure): responsable del transporte HTTP SOAP puro.
- **`IFabaService`** (Application interface / Infrastructure impl): responsable de la lógica de negocio, mapeo de DTOs y orquestación.
- **No exponer `FabaClient` a Controllers**: los controllers solo inyectan `IFabaService`.

---

## 10. Próximos pasos (pendiente aprobación)

- [ ] Aprobar plan por etapas
- [ ] Comenzar Etapa 1 (cliente SOAP + config)
- [ ] Test de conectividad con `ValidarUsuario` antes de continuar
- [ ] Definir qué mutuales están activas (de `UsuariosMutuales`) para priorizar Etapa 3
