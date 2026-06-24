# Referencia Web Service FABA AOL V2 — LabIPAC

**Fuente:** `LabIPAC.Web/Documentos/Documentacion_Web_Service.pdf` (FABA, 05/10/2016, rev. 2019)  
**Análisis de implementación:** comparado contra código de LabIPAC al mes de junio 2026  
**Ubicación WSDL:** `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsdl`  
**Endpoint ASP:** `http://www.faba.org.ar/fabawsaolv2/FABAWSAOLV2.ASP`

---

## Características técnicas del WS

| Atributo | Valor |
|---|---|
| Protocolo | SOAP 1.1 RPC/encoded |
| WSDL | `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsdl` |
| WSML | `http://www.faba.org.ar/fabawsaolv2/fabawsaolv2.wsml` |
| Servicio | `FABAWSAOLV2` |
| Puerto | `ClsAolV2SoapPort` |
| Namespace | `http://tempuri.org/FABAWSAOLV2/wsdl/` |
| Modo desarrollo | `ProcessingId = "D"` |
| Modo producción | `ProcessingId = "P"` |

> ⚠️ El WSDL es RPC/encoded legacy. **No usar `dotnet-svcutil`** — incompatible con .NET 10. La implementación en LabIPAC usa HTTP raw con SOAP envelope construido manualmente (`FabaClient.cs`).

---

## Credenciales

Todos los métodos requieren `idUsuario` (int) y `Password` (int) asignados por FABA al laboratorio.  
En LabIPAC se configuran vía User Secrets o variables de entorno (`Faba:IdUsuario`, `Faba:Password`).

---

## Catálogo completo de operaciones

### Grupo 1 — Maestros (catálogos y configuración)

---

#### `DatosMutual`
**Propósito:** Devuelve la estructura del número de afiliado de una mutual: longitud de legajo, dígito, relación, y si requiere bono y coseguro.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `idUsuario` | Numérico | Usuario habilitado |
| `Password` | Numérico | Clave del usuario |
| `IdMutual` | Numérico | Id de la mutual |

**Respuesta:** String directo (no XML): `B000 L12D0R0BtCt`

| Parte | Significado |
|---|---|
| `L12` | Legajo de 12 posiciones |
| `D0` | Dígito de 0 posiciones |
| `R0` | Relación de 0 posiciones |
| `Bt` | Requiere bono (`t`=sí, `f`=no) |
| `Ct` | Requiere coseguro (`t`=sí, `f`=no) |

**Estado en LabIPAC:** ❌ NO implementado. Mencionado en comentario de `FabaMutualDto.cs` pero sin llamada. Útil para validar formato del número de afiliado al ingresar una orden.

---

#### `TiposDocumentos`
**Propósito:** Retorna los tipos de documento válidos para una mutual.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `idUsuario` | Numérico | Usuario habilitado |
| `Password` | Numérico | Clave del usuario |
| `IdMutual` | Numérico | Id de la mutual |
| `ProcessingId` | Alfanumérico | `D`=Desarrollo / `P`=Producción |
| `Terminal` | Alfanumérico | Identificación del terminal |

**Respuesta XML:**
```xml
<idestado>…</idestado>
<idTipoDocumento>…</idTipoDocumento>
<Descripcion>…</Descripcion>
```

**Estado en LabIPAC:** ❌ NO implementado. Los tipos de documento están hardcoded (DNI=1, Pasaporte=2, CUIL=3).

---

#### `TiposBonos`
**Propósito:** Retorna los tipos de bono válidos para una mutual. Se recomienda invocar una vez por jornada (datos dinámicos).

Mismos parámetros que `TiposDocumentos`.

**Respuesta XML:**
```xml
<idestado>…</idestado>
<idTipoBono>…</idTipoBono>
<Descripcion>…</Descripcion>
```

**Estado en LabIPAC:** ❌ NO implementado. No aplica hasta implementar ingreso de órdenes.

---

#### `Diagnosticos`
**Propósito:** Retorna diagnósticos válidos para una mutual. Se recomienda invocar una vez por jornada.

Mismos parámetros que `TiposDocumentos`.

**Respuesta XML:**
```xml
<idestado>…</idestado>
<idDiagnostico>…</idDiagnostico>
<Diagnostico>…</Diagnostico>
<Descripcion>…</Descripcion>
```

**Estado en LabIPAC:** ❌ NO implementado. No aplica hasta implementar ingreso de órdenes.

---

#### `DiagnosticosV3` *(01/10/2010)*
**Propósito:** Igual que `Diagnosticos` pero agrega filtro `MuestraCombo` (`S`=listado reducido, `N`=todos) y campos adicionales en respuesta (`MuestraCombo`, `CodigoOMS`).

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `DiagnosticosAlfabetico` *(03/10/2016)*
**Propósito:** Retorna diagnósticos que comienzan con un string dado, para autocompletar.

| Parámetro extra | Tipo | Descripción |
|---|---|---|
| `Nombre` | Alfanumérico | Prefijo de búsqueda (ej: `"a"`) |

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `Coseguros`
**Propósito:** Retorna los coseguros válidos para una mutual.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `Prestadores` *(02/05/2012)*
**Propósito:** Busca prestadores médicos por nombre parcial dentro de una mutual. Devuelve `idPrestador` necesario para cargar órdenes en mutuales que lo requieran.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `idUsuario` | Numérico | |
| `Password` | Numérico | |
| `IdMutual` | Numérico | |
| `Nombre` | Alfanumérico | Nombre o apellido a buscar |

**Respuesta XML:**
```xml
<RECORD>
  <idEstado>B000</idEstado>
  <idPrestador>6280097</idPrestador>
  <Nombre>LOPEZ JORGE</Nombre>
  <TipoMatricula>No suministrada</TipoMatricula>
  <Matricula>No suministrada</Matricula>
</RECORD>
```
Máximo 50 registros.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `UsuariosMutuales` *(19/07/2017)* ✅
**Propósito:** Retorna las mutuales asignadas al usuario autenticado.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `idUsuario` | Numérico | |
| `Password` | Numérico | |
| `ProcessingId` | Alfanumérico | |
| `Terminal` | Alfanumérico | |

**Respuesta XML:**
```xml
<idEstado>B000</idEstado>
<IdMutual>1</IdMutual>
<Nombre>I.O.M.A.</Nombre>
…
```
Múltiples RECORD, uno por mutual.

**Estado en LabIPAC:** ✅ **IMPLEMENTADO** — `FabaImportService.SincronizarMutualesAsync()`.  
Upsert por `IdFaba`. Restaura soft-deleted si reaparece. Acción: `POST /Faba/SincronizarMutuales`.

> ⚠️ **Campos no mapeados:** el WS devuelve solo `IdMutual` y `Nombre`. `CodFacturante` (necesario para `ValidarOrdenOsdeWS`) y el flag OSDE **no vienen en esta operación** — deben cargarse manualmente en la entidad `Mutual`.

---

#### `PracticasPorMutual` *(19/07/2017)* ✅
**Propósito:** Retorna las prácticas reconocidas por una mutual particular.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `idUsuario` | Numérico | |
| `Password` | Numérico | |
| `IdMutual` | Numérico | Id FABA de la mutual |
| `ProcessingId` | Alfanumérico | |
| `Terminal` | Alfanumérico | |

**Respuesta XML (estructura especial):**
```xml
<RECORD>
  <IdPractica>5</IdPractica>
  <Nombre>ACIDO BASE ESTADO(PH,PCO2,BIC,E,B).</Nombre>
  <IdPractica>8</IdPractica>
  <Nombre>ACIDO URICO</Nombre>
  …
</RECORD>
```
Un solo RECORD con pares `IdPractica`/`Nombre` repetidos (no un RECORD por práctica).

**Estado en LabIPAC:** ✅ **IMPLEMENTADO** — `FabaImportService.SincronizarAnalitosAsync(mutualId)`.  
Parser especial en `FabaResponseParser.ParseAnalitos()` que itera pares de elementos hermanos.  
Upsert por `(MutualId, CodigoFaba)`. Marca inactivos los que desaparecen. Acción: `POST /Faba/SincronizarAnalitos`.

---

#### `UltimoCambioUsuario` *(19/07/2017)*
**Propósito:** Retorna la fecha de última modificación en las mutuales asignadas al usuario. Permite saber si es necesario re-sincronizar mutuales.

**Respuesta XML:**
```xml
<idEstado>B000</idEstado>
<Descripcion>Aceptado</Descripcion>
<FechaUltimaModificacion>17/07/2016 05:22:00 pm</FechaUltimaModificacion>
```

**Estado en LabIPAC:** ❌ NO implementado. Útil para sincronización inteligente: comparar contra `Mutual.UltimaSincMutuales` antes de invocar `UsuariosMutuales`.

---

#### `UltimoCambioPractica` *(19/07/2017)*
**Propósito:** Retorna la fecha de última actualización de prácticas para una mutual específica.

| Parámetro extra | Tipo |
|---|---|
| `IdMutual` | Numérico |

**Estado en LabIPAC:** ❌ NO implementado. Útil para sincronización inteligente: comparar contra `Mutual.UltimaSincPracticas` antes de invocar `PracticasPorMutual`.

---

### Grupo 2 — Afiliados

---

#### `ConsultarAfiliado` ✅
**Propósito:** Verifica la existencia de un afiliado y retorna sus datos personales y de cobertura.

| Parámetro | Tipo | Valores posibles |
|---|---|---|
| `idUsuario` | Numérico | |
| `Password` | Numérico | |
| `IdMutual` | Numérico | Id FABA de la mutual |
| `IdTipoBusqueda` | Alfanumérico | `D`=Documento / `A`=Afiliado |
| `Legajo` | Alfanumérico | Número de afiliado si busca por `A`, `""` si busca por `D` |
| `Digito` | Alfanumérico | Dígito verificador o `""` |
| `Relacion` | Alfanumérico | Relación del titular o `""` |
| `TipoDocumento` | Numérico | Id del tipo de documento (o `0`) |
| `NroDocumento` | Numérico | Número de documento (o `0`) |
| `ProcessingId` | Alfanumérico | |
| `Terminal` | Alfanumérico | |

**Respuesta XML (IOMA y genérica):**
```xml
<idestado>…</idestado>
<DescripcionEstado>…</DescripcionEstado>
<NroAfiliado>…</NroAfiliado>
<Digito>…</Digito>
<RelacionParentezco>…</RelacionParentezco>
<TipoDocumento>…</TipoDocumento>
<NumeroDocumento>…</NumeroDocumento>
<NombreBeneficiario>…</NombreBeneficiario>
<Sexo>…</Sexo>
<FechaNaciomiento>…</FechaNacimiento>
<Plan>…</Plan>
<CategoriaIva>…</CategoriaIva>
<DescripcionCategoriaIva>…</DescripcionCategoriaIva>
```

Si no existe: `M004 Afiliado Inexistente`

**Estado en LabIPAC:** ✅ **IMPLEMENTADO** — `FabaImportService.ConsultarAfiliadoAsync()`.  
Usado en dos lugares:
- `GET+POST /Faba/ConsultarAfiliado` (lookup standalone desde módulo FABA)
- `POST /Pacientes/BuscarAfiliadoFaba` (AJAX desde formulario de Pacientes)

> ⚠️ **Discrepancia detectada:** El PDF define `IdTipoBusqueda = "A"` para búsqueda por afiliado.  
> El código `FabaAfiliadoRequest` usa `"L"` (Legajo) en vez de `"A"`. Algunas mutuales (IOMA) pueden aceptar "L" como alias o la estructura puede variar. Verificar con FABA si "A" y "L" son equivalentes o si "L" es un valor no documentado que IOMA acepta.

> ⚠️ **Campos no mapeados en la respuesta:** `Plan`, `CategoriaIva`, `DescripcionCategoriaIva` son devueltos por el WS pero no se guardan en `FabaAfiliadoDto` ni en la entidad `Paciente`.

---

#### `ConsultarAfiliadoOsde` *(04/10/2019)*
**Propósito:** Igual que `ConsultarAfiliado` pero con firma diferente, exclusivo para OSDE. Usa credencial + código de seguridad + código facturante en vez de documento.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `IdTipoBusqueda` | Alfanumérico | Solo `A`=Afiliado |
| `Legajo` | Alfanumérico | Número de credencial OSDE |
| `CodSeguridad` | Alfanumérico | Código de seguridad OSDE |
| `CodFacturante` | Numérico | Código del facturante |

**Estado en LabIPAC:** ❌ NO implementado. Necesario si el laboratorio opera OSDE con circuito propio (`ValidarOrdenOsdeWS`).

---

### Grupo 3 — Órdenes (no implementado en LabIPAC)

> Estas operaciones son el núcleo del WS FABA para laboratorios que facturan directamente a obras sociales. Su implementación habilitaría la **validación y registro de órdenes online** con FABA.

---

#### `ValidarOrdenV3` *(09/09/2010)*
**Propósito:** Envía una orden, la valida, la graba en FABA y retorna resultado por práctica + datos del afiliado + número de transacción. Soporta hasta 24 prácticas como parámetros individuales.

Parámetros clave adicionales: `FechaPrescripcion`, `FechaRealizacion`, `NombreMedico`, `MatriculaMedica`, `TipoMatricula` (N=Nacional/P=Provincial), `TipoBono`, `NroBono`, `Coseguro`, `IdDiagnostico1`, `IdDiagnostico2`, `strTelefono`, `IdPractica1`…`IdPractica24`.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ValidarOrdenfV3` *(09/09/2010)*
**Propósito:** Igual que `ValidarOrdenV3` pero las prácticas se envían concatenadas en un único string (un campo `practicas`), para lenguajes con límite de parámetros. Cada código ocupa 4 dígitos, ej: `"00020005"`.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ValidarOrdenV4` *(06/12/2018)*
**Propósito:** Igual que `ValidarOrdenV3` + campo `Observacion` adicional (alfanumérico).

**Estado en LabIPAC:** ❌ NO implementado. **Versión recomendada** para mutuales genéricas.

---

#### `ValidarOrdenfV4` *(06/12/2018)*
**Propósito:** Igual que `ValidarOrdenfV3` + `strObservacion`.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ValidarOrdenOsde` *(04/10/2018)*
**Propósito:** Versión de `ValidarOrdenV4` exclusiva para OSDE. Agrega `NombreAfiliado` y `CategoriaIVA` (`G`=Gravado / `NG`=No Gravado). Si el afiliado no existe en el padrón OSDE, lo agrega automáticamente.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ValidarOrdenOsdeWS` *(04/10/2019)*
**Propósito:** Variante de OSDE que además envía la información directamente a la mutual (integración online). Requiere `CodSeguridad` y `CodFacturante`. No recibe documento ni diagnósticos — solo legajo + prácticas.

**Estado en LabIPAC:** ❌ NO implementado. Requiere `CodFacturante` en la entidad `Mutual` (campo existe pero no se popula desde `UsuariosMutuales`).

---

#### `ConsultarOrden`
**Propósito:** Retorna el estado de una orden ingresada, detallando el estado por práctica.

Respuesta incluye: `idEstado`, `NumeroTransaccion`, datos del afiliado, estado y descripción por cada práctica (`Practica1`…`PracticaN`), `Observacion1`…`N`.

**Estado en LabIPAC:** ❌ NO implementado.

---

### Grupo 4 — Bonos

---

#### `AgregarBono`
**Propósito:** Agrega un bono a una transacción existente (mientras no esté facturada o esté en auditoria). Soporta bono de barras (13 posiciones en `NroBonoNuevo`) y bono común (`Coseguro` + `TipoBono` + `NroBono`).

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `EliminarBono`
**Propósito:** Elimina un bono de una transacción existente. Mismas condiciones que `AgregarBono`.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ModificarFechaRealizacion`
**Propósito:** Modifica la fecha de realización de una transacción, si la mutual lo admite y no fue facturada.

Formato fecha: `ddmmaaaa`.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ConsultarBonos`
**Propósito:** Devuelve los números de bonos (código de barras, 13 posiciones) asignados a una transacción.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ConsultarTransaccionDeBono`
**Propósito:** Dado un número de bono, retorna el número de transacción al que está asignado.

**Estado en LabIPAC:** ❌ NO implementado.

---

### Grupo 5 — Mensajería y Auditoría

---

#### `ConsultarMensajes`
**Propósito:** Devuelve los mensajes del Auditor y del Laboratorio para una transacción.

**Respuesta XML:**
```xml
<idestado>…</idestado>
<DescripcionEstado>…</DescripcionEstado>
<Origen>OP</Origen>
<Fecha>06/09/2010 01:34:11 p.m.</Fecha>
<Mensaje>…</Mensaje>
```

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `GrabarMensajes`
**Propósito:** Envía un mensaje asociado a una transacción existente (máx. 200 caracteres).

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `Recurrir` *(01/06/2017)*
**Propósito:** Permite recurrir una orden que está en condición de recurrir, con un mensaje justificatorio.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `AceptarAuditoria` *(23/09/2019)*
**Propósito:** Da por aceptada una orden auditada. Requiere que sea el mismo usuario que la cargó.

**Estado en LabIPAC:** ❌ NO implementado.

---

#### `ConsultaConfirmacionAuditoria` *(23/09/2019)*
**Propósito:** Consulta si una orden auditada fue aceptada o no.

**Estado en LabIPAC:** ❌ NO implementado.

---

## Resumen de estado de implementación

| Operación | Grupo | Estado LabIPAC | Relevancia |
|---|---|---|---|
| `UsuariosMutuales` | Maestros | ✅ Implementado | Alta |
| `PracticasPorMutual` | Maestros | ✅ Implementado | Alta |
| `ConsultarAfiliado` | Afiliados | ✅ Implementado | Alta |
| `DatosMutual` | Maestros | ❌ No implementado | Media — útil para validar formato de afiliado |
| `UltimoCambioUsuario` | Maestros | ❌ No implementado | Media — optimizar sincronización |
| `UltimoCambioPractica` | Maestros | ❌ No implementado | Media — optimizar sincronización |
| `TiposDocumentos` | Maestros | ❌ No implementado | Baja (hardcoded es suficiente) |
| `ValidarOrdenV4` | Órdenes | ❌ No implementado | **Muy alta** — habilita facturación FABA |
| `ValidarOrdenfV4` | Órdenes | ❌ No implementado | **Muy alta** — alternativa a V4 |
| `ValidarOrdenOsde` | Órdenes | ❌ No implementado | Alta si opera OSDE |
| `ValidarOrdenOsdeWS` | Órdenes | ❌ No implementado | Alta si opera OSDE con circuito web |
| `ConsultarAfiliadoOsde` | Afiliados | ❌ No implementado | Media si opera OSDE |
| `ConsultarOrden` | Órdenes | ❌ No implementado | Alta — seguimiento de transacciones |
| `AgregarBono` / `EliminarBono` | Bonos | ❌ No implementado | Media — gestión de bonos |
| `ModificarFechaRealizacion` | Bonos | ❌ No implementado | Media |
| `ConsultarBonos` | Bonos | ❌ No implementado | Baja |
| `ConsultarTransaccionDeBono` | Bonos | ❌ No implementado | Baja |
| `ConsultarMensajes` / `GrabarMensajes` | Auditoría | ❌ No implementado | Media — auditoria |
| `Recurrir` | Auditoría | ❌ No implementado | Media |
| `AceptarAuditoria` | Auditoría | ❌ No implementado | Baja |
| `ConsultaConfirmacionAuditoria` | Auditoría | ❌ No implementado | Baja |
| `TiposBonos` / `Coseguros` | Maestros | ❌ No implementado | Baja hasta implementar órdenes |
| `Diagnosticos` / `DiagnosticosV3` | Maestros | ❌ No implementado | Baja hasta implementar órdenes |
| `DiagnosticosAlfabetico` | Maestros | ❌ No implementado | Baja |
| `Prestadores` | Maestros | ❌ No implementado | Media si mutual requiere idPrestador |

---

## Discrepancias detectadas: PDF vs. implementación

### 1. `IdTipoBusqueda` en `ConsultarAfiliado`

| | Valor |
|---|---|
| **PDF dice** | `D`=Documento / `A`=Afiliado |
| **Código usa** | `D`=Documento / `L`=Legajo |

`FabaAfiliadoRequest.TipoBusqueda` envía `"L"` cuando busca por número de afiliado. El PDF define `"A"`. IOMA podría aceptar ambos. **Pendiente verificar** — si la búsqueda por legajo falla en alguna mutual, cambiar a `"A"`.

---

### 2. Campos de respuesta `ConsultarAfiliado` no mapeados

El WS devuelve `Plan`, `CategoriaIva` y `DescripcionCategoriaIva` que `FabaAfiliadoDto` no expone. Si en el futuro se necesita categoría IVA del afiliado para facturación, extender el DTO.

---

### 3. `CodFacturante` no importado desde FABA

`ValidarOrdenOsdeWS` requiere `CodFacturante`. La entidad `Mutual` tiene la columna pero no se popula desde `UsuariosMutuales` (que no devuelve ese campo). Debe cargarse manualmente o consultarse vía `DatosMutual`.

---

### 4. Sincronización reactiva (sin control de cambios)

`UltimoCambioUsuario` y `UltimoCambioPractica` no están implementados. El sistema re-sincroniza todo cada vez. Implementarlos permitiría sincronizar solo cuando FABA tenga cambios desde la última sincronización.

---

## Códigos de respuesta (`idEstado`)

> `B*` = graba en base de datos FABA. `M*` = solo informa, no graba nada.

| Código | Descripción |
|---|---|
| `B000` | Aceptado |
| `B001` | Aceptado (Prácticas rechazadas) |
| `B002` | Orden pendiente de auditoria |
| `B030` | Práctica autorizada |
| `B032` | Requiere auditoria |
| `B034` | No se fundamenta repetición según fecha última realización — requiere Auditoria |
| `B035` | Sin fundamentos clínicos según diagnósticos — requiere Auditoria |
| `M001` | Prestador no identificado |
| `M002` | Matrícula médica no identificada |
| `M003` | Fecha de prescripción no válida |
| `M004` | Afiliado inexistente |
| `M005` | No se ingresaron prácticas |
| `M006` | Código de diagnóstico inexistente |
| `M007` | Código de Tipo de Bono inexistente o no corresponde a la mutual |
| `M008` | Código de Coseguro inexistente o no corresponde a la mutual |
| `M010` | No hay datos para esa mutual |
| `M011` | Transacción no Aceptada |
| `M020` | No puede consultar esa transacción o transacción inexistente |
| `M021` | No existen prácticas para esa transacción |
| `M024` | Transacción Inexistente |
| `M030` | Práctica ya realizada |
| `M031` | Práctica inexistente |
| `M033` | Práctica no autorizada |
| `M036` | Práctica fuera de Diagnósticos-Tiempos |
| `M037` | Práctica Fuera de Diagnósticos |
| `M038` | Práctica fuera de Tiempos |
| `M039` | El afiliado no se realizó la etapa de Screening |
| `M040` | Ingresar en IOMA por prestación |
| `M041` | Autorización via fax |
| `M042` | Número de Bono Incorrecto |
| `M043` | Bono no corresponde a mutual |
| `M044` | Número de Bono ya Ingresado |
| `M045` | Parámetros De Bonos Incorrectos |
| `M046` | Transacción Inexistente o cerrada |
| `M047` | Fecha de realización no válida |
| `M048` | La mutual no acepta fecha de realización |
| `M049` | Número de Bono no pertenece a la Transacción |
| `M050` | La mutual no acepta más de un bono |
| `M051` | Ingresar en OSSEG por Prestación |
| `M052` | No cumple con normativa de urgencia |
| `M053` | Debe ingresar Teléfono |
| `M054` | La Etapa A se realizó el día xx/xx/xxxx. Deben pasar 45 días para la próxima etapa |
| `M055` | Prestador Médico inválido |
| `M100` | Usuario no válido o no autorizado para esta mutual |
| `M101` | La cantidad de prácticas supera la cantidad permitida |
| `M900` | Error no identificado |

---

## Notas de implementación en LabIPAC

### Cómo funciona el cliente SOAP (`FabaClient.cs`)

Dado que el WSDL usa SOAP 1.1 RPC/encoded (formato legacy incompatible con `dotnet-svcutil` en .NET 10), LabIPAC construye el envelope XML manualmente:

```csharp
// Namespace de mensaje
const string NsMsg = "http://tempuri.org/FABAWSAOLV2/message/";
// SOAPAction header
const string NsAction = "http://tempuri.org/FABAWSAOLV2/action/ClsAolV2.{operacion}";
```

El método `LlamarAsync(operacion, parametros)` construye el envelope, agrega siempre `idUsuario` + `Password` al inicio, y extrae el nodo `Result` de la respuesta.

### Modo desarrollo vs. producción

Pasar `ProcessingId = "D"` activa el ambiente de desarrollo en FABA (no graba en producción).  
`ProcessingId = "P"` (o un GUID real) activa producción.  
LabIPAC usa `Guid.NewGuid().ToString()` — producción por defecto.  
Para pruebas con FABA, cambiar a `"D"` en `FabaImportService`.

### Fechas

El WS espera fechas en formato `ddmmaaaa` (sin separadores) en los parámetros de órdenes.  
La respuesta de `ConsultarAfiliado` devuelve `FechaNacimiento` en `dd/MM/yyyy`.  
`FabaResponseParser` normaliza a `yyyy-MM-dd` para binding MVC.
