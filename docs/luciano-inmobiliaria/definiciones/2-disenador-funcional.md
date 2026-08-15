# Memoria - Diseñador funcional

## Proyecto: luciano-inmobiliaria
## Ultima actualizacion: 2026-08-14

---

## 0. Resultado del escaneo de reutilización

Escaneados `docs/*/definiciones/{2-disenador-funcional,5-implementador}.md` de todo el historial.

| Pieza de Luciano | Proyecto de referencia | Qué se reutiliza |
|---|---|---|
| Motor de firma/emisión ARCA (WSAA/WSFEv1) | `marihogar` → `delicias-naturales` → `la-platense` (`AfipService`/`AfipTokenCache`, código real leído para este rediseño) | Lógica SOAP hand-rolled ya probada 3 veces. Se extiende de "1 CUIT en config" a "N CUIT en base de datos". El contrato de `ComprobanteRequestDto` de §2 está armado a partir de los campos reales que ya usa `AfipService.ArmarFecaeSolicitarEnvelope` (Concepto, DocTipo/DocNro, CbteFch, ImpNeto/ImpIVA/ImpTotal, CondicionIVAReceptorId, Iva), no de una suposición abstracta. |
| Cifrado de credenciales sensibles por tenant | `century-21` (`WhatsAppCredentialCipherService`, cifra por `Grupo`) | Mismo patrón de cifrado en reposo, aplicado al certificado `.p12` + password de cada CUIT. |
| Modelo de suscripción/plan con límite y aislamiento por tenant | `century-21` (`Plan`/`Grupo`/`ITenantContext`) | Base conceptual para `Suscripcion`/`Cuit`/`PuntoVenta`. |
| Emisión de NC/ND sobre un comprobante ya emitido | `century-21`/`la-platense` (extensión del mismo `AfipService`) | Reutilizable si Luciano llega a necesitar notas de crédito — no confirmado, extensión natural en Etapa 2. |
| **Sin precedente**: API pública multi-tenant a escala ~100 CUIT, ingesta de certificados por FTP compartido, extracción de datos de contrato por PDF con IA | — | Diseño nuevo, documentado abajo. |

**Cambio de forma respecto de la v1 de este documento (2026-08-14, primera reunión real con el cliente)**: el proyecto **ya no tiene ninguna pantalla** — el cliente confirmó "desarrollo exclusivamente de una Web API". Se elimina por completo el panel self-service de certificados (reemplazado por ingesta FTP) y el backoffice interno (reemplazado por endpoints administrativos que Joaquín consume directo). La sección "Flujo de pantallas" de la v1 queda reemplazada por "Contrato de API".

## 1. Alcance funcional resumido

Web API pura (sin Identity, sin vistas Razor) con 3 áreas de endpoints — **Comprobantes** (emisión ARCA individual/lote para el ERP/SaaS del cliente), **Administración** (alta de clientes/CUIT/puntos de venta y control de uso, consumido solo por Joaquín) — más un **proceso de ingesta de certificados por FTP** (sin endpoint, corre en background) y, como rama funcionalmente independiente, **Contratos** (extracción de datos de PDF con IA, pedida por el cliente el 2026-08-14, a confirmar alcance en Presupuesto).

## 2. Contrato de API

### 2.1 Comprobantes (consumido por el SaaS de Luciano) — pasado a ASÍNCRONO (2026-08-14, decisión final)

Individual y lote **ya no responden el resultado en la misma llamada** — se confirma recepción (202) y el resultado se consulta después. Elimina el riesgo de timeout/tope de tamaño de lote.

**`POST /api/v1/comprobantes`** — emisión individual. Header `X-Api-Key` resuelve punto de venta → CUIT → certificado.
```jsonc
// Response 202 — recibido, no procesado todavía
{ "id": "a1b2c3", "estado": "Pendiente" }
```
**`GET /api/v1/comprobantes/{id}`** — consulta de estado (polling). Mismo shape que antes cuando `estado=Emitido` o `estado=Rechazado`.

**Confirmado 2026-08-14: polling.** El cliente consulta el estado — no hay webhook, no hay endpoint de registro de callback. Más simple de implementar y de integrar de su lado.

```jsonc
// Request — campos alineados 1:1 con lo que ya exige WSFEv1 (ver AfipService.cs real)
{
  "tipoComprobante": 6,              // WSFEv1 CbteTipo: 1=Factura A, 6=Factura B, 11=Factura C
  "concepto": 2,                     // WSFEv1 Concepto: 1=Productos, 2=Servicios, 3=Productos y Servicios
  "fechaComprobante": "2026-08-14",  // WSFEv1 CbteFch
  "periodoServicio": {               // OBLIGATORIO si concepto=2 o 3 (WSFEv1 lo exige para servicios)
    "desde": "2026-08-01", "hasta": "2026-08-31", "vencimientoPago": "2026-09-10"
  },
  "receptor": {
    "tipoDocumento": 80,              // WSFEv1 DocTipo: 80=CUIT, 96=DNI, 99=Consumidor Final
    "numeroDocumento": "20345678901",
    "condicionIva": 5                 // WSFEv1 CondicionIVAReceptorId: 1=RI, 4=Exento, 5=CF, 6=Monotributo
  },
  "importes": {
    "neto": 100000.00, "iva": 21000.00, "total": 121000.00,
    "alicuotaIva": 21                 // % → mapea a WSFEv1 AlicIva.Id (tabla ya resuelta en AfipService: 0/2.5/5/10.5/21/27)
  },
  "descripcion": "Honorarios administración alquiler - Agosto 2026"  // texto libre, no va a WSFEv1, uso interno/comprobante
}
```
```jsonc
// Response 200 — éxito
{ "exito": true, "cae": "71234567890123", "vencimientoCae": "2026-08-24", "numeroComprobante": 145, "puntoVenta": 3, "tipoComprobante": 6 }
// Response 200 — rechazo de ARCA (no es error HTTP, es un resultado de negocio)
{ "exito": false, "detalleError": "10015 - CondicionIVAReceptorId inválido para el DocTipo informado" }
```

**`POST /api/v1/comprobantes/lote`** — `{ "comprobantes": [ ... ] }`, **sin tope de tamaño** (ya no aplica R6, era un límite del modo síncrono). Responde 202 con `{ "loteId": "...", "estado": "Pendiente", "cantidadItems": N }`. El resultado de cada ítem se consulta después vía `GET /api/v1/comprobantes/lote/{loteId}` — un ítem rechazado no aborta el resto del lote, cada uno tiene su propio resultado.

**⚠️ Pendiente, bloqueante para cerrar este contrato**: el tipo "sueldos" que mencionó el cliente no tiene mapeo claro a `tipoComprobante`/`concepto` de ARCA (ver `1-analista-funcional.md` §0.10-4) — falta confirmar con Luciano antes de congelar el enum `TipoComprobante`.

### 2.2 Administración — consumido por el propio sistema del cliente (2026-08-14, cambio de consumidor)

**Corrección respecto de la v1**: la alta de CUIT/puntos de venta **la gestiona el sistema de Luciano**, no Joaquín manualmente vía Postman. Esto no cambia los endpoints en sí, cambia quién los llama — pasan a ser parte del contrato público que el equipo técnico de Luciano integra (junto con Comprobantes), no una herramienta interna. Sube levemente la vara de calidad esperada (validaciones, mensajes de error claros) porque ahora los consume un sistema externo en producción, no un uso manual ocasional.

- `POST /api/v1/admin/clientes` — alta de `Suscripcion`.
- `POST /api/v1/admin/clientes/{id}/cuits` — alta de `Cuit` (recalcula el pack de precio, ver `4-presupuestador.md`).
- `POST /api/v1/admin/cuits/{id}/puntos-venta` — alta de `PuntoVenta`, incluye `volumenDeclaradoMensual` (insumo del control de uso — el cliente lo declara al dar de alta cada punto de venta).
- `GET /api/v1/admin/control-de-uso` / `GET /api/v1/admin/control-de-uso/{puntoVentaId}` — **estos dos siguen siendo de uso exclusivo de Joaquín** (requieren la API key administrativa, no la del cliente) — es el único par de endpoints que no pasa a manos del cliente, porque es la herramienta de Olvidata para vigilar uso indebido, no algo que el cliente deba poder auto-consultar.

### 2.3 Ingesta de certificados por FTP — alcance final simplificado (2026-08-14, tercera y última revisión de este punto)

Recorrido de esta decisión en la misma sesión: panel self-service → FTP con Olvidata trackeando vencimiento activamente → pass-through sin persistencia → **versión final: FTP, pero la validez es responsabilidad del cliente, Olvidata solo reacciona si falla.**

El cliente **administra sus certificados de su lado** (renovación, vigencia) y los publica en una carpeta FTP compartida — nombre de archivo = CUIT (`30123456789.p12`, confirmado). Olvidata **consume** esa carpeta, no la gestiona activamente:

- **No hay job de vencimiento proactivo** (se cae la transición `Vigente→PorVencer` de la v1 — no tiene sentido si Olvidata no es responsable de avisar con anticipación).
- **Detección reactiva únicamente**: si al usar un certificado (en la ingesta o al intentar firmar) ARCA lo rechaza por vencido/inválido, el sistema manda un **mail automático** al cliente informando qué CUIT tiene el certificado con problema — no hay dashboard, no hay alerta anticipada de "vence en 30 días", solo aviso de "esto ya está roto, arreglalo".
- El certificado se lee de la carpeta, se usa para firmar, y se cachea en memoria (no en disco) solo por practicidad operativa de corto plazo — Olvidata no asume responsabilidad de custodia a largo plazo ni de vigencia.

**Proceso** (`CertificadoFtpIngestaHostedService`, simplificado): lee la carpeta periódicamente, intenta validar/usar cada certificado, y si falla dispara el mail de aviso — sin máquina de estados de vencimiento, sin job separado de chequeo anticipado. Pendiente confirmar con el cliente: convención de la contraseña del `.p12` (propuesta: archivo hermano `{cuit}.txt`).

### 2.4 Contratos — extracción de datos de PDF con IA (rama nueva e independiente, pedida 2026-08-14)

**`POST /api/v1/contratos/extraer`** (multipart/form-data, un PDF) — envía el documento a la API de Claude (Anthropic) con una consulta que pide la extracción estructurada de campos de un contrato inmobiliario, devuelve JSON con lo detectado. **No autocompleta nada por sí sola** — el frontend del cliente es quien decide cómo usar la respuesta, y el diseño asume que un humano revisa/corrige antes de guardar (ver riesgo de precisión en `1-analista-funcional.md` §0.11).

```jsonc
// Response (shape propuesto, a validar con el cliente qué campos de contrato necesitan realmente)
{
  "campos": {
    "partes": [{ "rol": "locador", "nombre": "...", "dni": "..." }, { "rol": "locatario", "nombre": "...", "dni": "..." }],
    "inmueble": { "direccion": "...", "ciudad": "..." },
    "montoMensual": 250000.00,
    "fechaInicio": "2026-09-01",
    "duracionMeses": 24
  },
  "camposNoDetectados": ["fechaInicio"],   // transparencia: qué no pudo extraer, para que el frontend lo resalte
  "advertencia": "Revisar todos los campos antes de guardar — extracción automática, no validada."
}
```

## 3. Contratos de datos (DTOs) — reemplaza "ViewModels" (no hay UI en este proyecto)

**`ComprobanteRequestDto`/`ResponseDto`, `LoteRequestDto`/`ResponseDto`**: ver §2.1, ya en formato final informado por WSFEv1 real.

**`ClienteAdminDto`**: `RazonSocial`, `Cuits[]` (cada uno con `PuntosVenta[]`), `PlanPack` (derivado de `COUNT(Cuits)`, solo lectura) — mismo contenido que la v1, ahora expuesto por API en vez de pantalla.

**`ControlUsoDto`**: `Cliente`, `PuntoVenta`, `VolumenDeclarado`, `VolumenReal30dias`, `PorcentajeSobreLimite`, `Estado` (enum semáforo), `CantidadSenalesActivas`.

**`SenalesAntirreventaDto`**: `ReceptoresDistintosMesActual`/`MesAnterior`, `SaltoVolumenVsPromedio3Meses` (%), `IpsDistintasMes`, `PorcentajeRequestsFueraDeHorario`, `PorcentajeComprobantesSinTerminoEsperado`, cada uno con su umbral y estado (Normal/Alerta).

**`ContratoExtraidoDto`**: ver §2.4.

## 4. Máquina de estados

### 4.1 Certificado (simplificado 2026-08-14 — sin seguimiento proactivo de vencimiento)

| Estado origen | Evento | Estado destino | Guarda | Acción |
|---|---|---|---|---|
| — | Ingesta FTP lee archivo, se usa para firmar con éxito | Válido | ARCA acepta la firma | Emite normalmente |
| — / Válido | ARCA rechaza el certificado (vencido/inválido) al intentar firmar | Inválido | rechazo de ARCA | **Mail automático al cliente** con el CUIT afectado — única acción, sin bloqueo administrativo adicional más allá de que ese CUIT no puede emitir hasta que lo arreglen |
| Inválido | Ingesta FTP detecta reemplazo del archivo | Válido | próximo intento de firma exitoso | Vuelve a emitir normalmente |

*Sin estado "Por vencer" ni job de anticipación — la responsabilidad de renovar a tiempo es del cliente, Olvidata solo reacciona cuando ARCA ya rechazó.*

### 4.2 Comprobante
`Pendiente → Emitido` (CAE obtenido) | `Pendiente → Rechazado` (motivo real devuelto, CU-01/02).

### 4.3 Suscripción (control de uso)
`Activa → Bloqueada` (`VolumenReal > VolumenDeclarado × Multiplicador` en algún punto de venta) → `Activa` (Joaquín revisa vía `GET /api/v1/admin/control-de-uso` y desbloquea manualmente).

## 5. Reglas de negocio

- Aislamiento por tenant: toda consulta se filtra por `SuscripcionId` resuelto desde la API key — un punto de venta nunca ve datos de otro CUIT/suscripción, ni siquiera del mismo cliente.
- No se emite contra un CUIT con certificado `Vencido` ni contra un punto de venta con `Suscripcion` `Bloqueada`.
- El password del certificado nunca se devuelve en ninguna respuesta ni se loguea en texto plano.
- Los endpoints `/api/v1/admin/*` requieren una API key administrativa distinta de las de punto de venta — nunca la misma credencial que usa el ERP del cliente.

## 6. Impacto funcional por capa

- **Presentación**: ninguna — 0 pantallas. Solo contrato HTTP (JSON) en los 3 grupos de endpoints de §2.
- **Negocio**: extensión del motor AFIP a multi-tenant (a escala ~100 CUIT, ver Arquitectura), orquestación de lote síncrono, ingesta y validación de certificados por FTP, cálculo de precio por `COUNT(Cuit)`, control de uso + 4 señales técnicas, integración con la API de Claude para extracción de contratos.
- **Datos**: entidades — `Suscripcion`, `Cuit`, `PuntoVenta`, `Certificado`, `ApiKey`, `Comprobante` (sin cambios de forma respecto de la v1, ver `3-arquitecto-mvc.md` para el detalle a escala).

## 7. Riesgos y supuestos

- Hereda R1-R4, S1 de `1-analista-funcional.md`, y R5-R7 de `3-arquitecto-mvc.md` (v1).
- **Cae (2026-08-14)**: el manual de usuario para autogestión de certificados **ya no aplica** — no hay panel que documentar, el cliente gestiona sus certificados con sus propias herramientas y solo los publica en la carpeta FTP acordada.
- **Nuevo (2026-08-14)**: la convención de nombres/estructura de la carpeta FTP es una dependencia bloqueante para implementar la ingesta — no se puede escribir `CertificadoFtpIngestaHostedService` sin ese acuerdo previo con el cliente.
- **Nuevo (2026-08-14)**: a escala ~100 CUIT, "1 usuario administrador por CUIT" ya no es la asunción correcta — no hay panel de usuarios de todos modos (es todo vía API), pero si el cliente espera algún tipo de autogestión de permisos entre las ~100 unidades de negocio, hay que preguntarlo explícitamente (no hay indicio de esto en la reunión, no se asume).
- Riesgos de las 4 señales técnicas (heurísticas, no bloqueantes por sí solas) sin cambios respecto de la v1 — siguen aplicando igual, solo que ahora se consultan por API en vez de verse en una grilla.

## 8. Plan funcional por etapas

**Etapa 1 (MVP — lo mínimo para que el SaaS de Luciano pueda facturar)**: endpoints de Comprobantes (individual + lote), autenticación por API key, extensión multi-tenant del motor AFIP a escala ~100 CUIT, ingesta de certificados por FTP, endpoints de Administración (alta de clientes/CUIT/puntos de venta, control de uso con las 4 señales).

**Etapa 2 (candidatos, a confirmar con Joaquín antes de Presupuesto)**: notas de crédito/débito (NC/ND), notificación automática de vencimiento de certificado (hoy solo consultable por API, no hay push), y — **a decidir explícitamente, no asumir por defecto**: el módulo de extracción de contratos por PDF+IA (§2.4). El cliente lo planteó como pregunta de viabilidad, no como pedido confirmado — se presupuesta como ítem aparte, el cliente decide si lo suma ahora o después.

## Historial de ajustes
- 2026-08-13: primera versión del diseño funcional. Arquitectura híbrida (API + panel + backoffice). Reutilización de `AfipService` y patrón de cifrado/tenant de `century-21`.
- 2026-08-13 (ampliación): agregadas 4 señales técnicas al Control de Uso.
- 2026-08-14 (rediseño mayor, primera reunión real): eliminado el panel self-service (certificados entran por FTP) y el backoffice interno (pasa a endpoints `/api/v1/admin/*`) — el proyecto es 100% Web API, confirmado explícitamente por el cliente. Contrato de `Comprobantes` reescrito con los campos reales de WSFEv1 (leídos del `AfipService.cs` de `la-platense`, no una suposición). Agregada rama nueva e independiente de extracción de contratos por PDF con IA (Claude), como candidato de Etapa 2 sin confirmar todavía. Manual de usuario de certificados dado de baja (ya no hay panel que documentar).
- 2026-08-14 (certificados — vuelta final): tras evaluar brevemente un modelo pass-through (CUIT+certificado por request, sin FTP), Joaquín confirmó quedarse con FTP pero **sin responsabilidad de Olvidata sobre la vigencia** — se cae el job de vencimiento anticipado y el estado "Por vencer"; queda solo detección reactiva (ARCA rechaza → mail al cliente). Simplifica el módulo de ingesta y elimina la máquina de estados de 3 pasos a 2.