---
description: Circuito de facturacion electronica AFIP/ARCA (WSAA + WSFEv1) — patron de referencia obligatorio para todo proyecto nuevo que necesite facturar electronicamente. Fuente real: marihogar (.NET 10, produccion), depurado en vivo el 20-21/08/2026.
applyTo: "**/*.{cs,cshtml,md,instructions.md}"
---

# 34 - Integracion AFIP/ARCA (WSAA + WSFEv1)

Este documento es la memoria tecnica reutilizable del circuito completo de facturacion electronica AFIP/ARCA. Antes de este archivo, cada proyecto que necesitaba facturar re-descubria los mismos gotchas desde cero (delicias-naturales primero, marihogar despues). **Todo proyecto nuevo con requisito de facturacion electronica arranca leyendo esto**, no reinventa el circuito.

## Dos referencias de codigo disponibles — cual usar segun el stack

- **`C:\Sistemas\delicias-naturales\Helper\FacturacionAfipService.cs` + `Models\Afip\LoginTicket.cs`**: .NET Framework 4.7.2, usa un proxy SOAP generado con Web References (`Reference.cs`, ~4000 lineas autogeneradas desde el WSDL real de AFIP). Util como **fuente de verdad del contrato XML** (orden de campos, tipos, nombres exactos) via sus atributos `XmlElementAttribute`/orden de propiedades — NO como codigo a portar literal (incompatible con .NET 10 moderno).
- **`C:\Sistemas\marihogar\MariHogar.Infrastructure\Services\AfipService.cs`**: .NET 10, arma el envelope SOAP a mano con `System.Xml.Linq` (`XElement`/`XNamespace`) + `HttpClient`, sin proxy generado (decision documentada en el propio archivo: evita depender de que el WSDL este disponible en build-time). **Esta es la referencia a portar/adaptar para cualquier proyecto .NET 5+**. Incluye login WSAA con cache de token 24hs (`AfipTokenCache.cs`), firma CMS/PKCS#7 del `LoginTicketRequest`, `FECompUltimoAutorizado`, `FECAESolicitar`, y (desde CR-55) Notas de Credito con `CbtesAsoc`.

**Advertencia sobre proxies WSDL viejos como fuente de verdad**: el `Reference.cs` de delicias-naturales quedo desactualizado respecto del WSDL real vigente de AFIP — no tiene `CondicionIVAReceptorId` (campo obligatorio agregado por RG 5616/2024). Al verificar el orden de un campo nuevo contra una copia local de un WSDL, **re-verificar siempre contra el WSDL de PRODUCCION real de AFIP en el momento** (o contra un proyecto que ya factura de verdad hoy), nunca confiar ciegamente en una copia de otro proyecto sin fecha de verificacion reciente.

## Certificado .p12 — el gotcha que costo 3 iteraciones en produccion

Cargar el certificado SIEMPRE con `X509KeyStorageFlags.MachineKeySet`:

```csharp
var certificado = X509CertificateLoader.LoadPkcs12FromFile(rutaResuelta, password, X509KeyStorageFlags.MachineKeySet);
```

**Por que**: el flag por defecto (`DefaultKeySet`) intenta persistir la clave privada en el perfil de usuario de Windows (`%USERPROFILE%\AppData\...`) del proceso que corre el sitio. En hosting compartido (IIS), si el Application Pool no tiene "Load User Profile" habilitado (comun, no siempre configurable por el cliente del hosting), esa carpeta no existe — y CryptoAPI devuelve el error **generico y enganoso "The system cannot find the file specified"**, aunque el .p12 este presente y en la ruta correcta. Facil de confundir con un problema de path.

**Orden de diagnostico real** (asi se resolvio en marihogar, documentado para no repetir el proceso de eliminacion completo):
1. Si el error es literal "The system cannot find the file specified" al invocar la emision: **no asumir que es la ruta del archivo** sin descartar primero el KeyStorageFlags. Resolver igual la ruta contra `IWebHostEnvironment.ContentRootPath` (nunca una ruta relativa cruda pasada directo a `LoadPkcs12FromFile` — se resuelve contra el directorio de trabajo del proceso, que no siempre coincide con el ContentRoot del sitio segun el modelo de hosting IIS/ANCM).
2. Si el error persiste identico despues de resolver la ruta y confirmar (con `File.Exists`) que el archivo esta ahi: es casi seguro el problema de KeyStorageFlags. `EphemeralKeySet` (clave solo en memoria) es la opcion "moderna" recomendada por Microsoft para este escenario, pero **en la practica no funciono en el hosting real usado (SmarterASP.NET/site4now)** — probablemente por restricciones del entorno compartido sobre operaciones de clave efimera. `MachineKeySet` si funciono, confirmado contra un sistema hermano (delicias-naturales) que ya factura de verdad en el mismo servidor. **Empezar directo por `MachineKeySet` en cualquier hosting compartido tipo IIS/SmarterASP** — no perder el ciclo de EphemeralKeySet primero.
3. Verificar SIEMPRE con un chequeo temprano (`File.Exists`) devolviendo un mensaje propio con la ruta resuelta exacta, en vez de dejar que la excepcion cruda de `LoadPkcs12FromFile` llegue al usuario — un "no se encontro el archivo en 'C:\ruta\real'" es diagnosticable, "The system cannot find the file specified" sin ruta no lo es.

## Punto de Venta — debe ser tipo "Web Services", no "Factura en Linea"

AFIP distingue el Punto de Venta usado para facturar manualmente desde su propio portal ("Factura en Linea") del Punto de Venta habilitado para que un sistema externo facture via Web Service. **Son objetos distintos en AFIP aunque compartan el mismo numero visual en la factura impresa** — un negocio puede tener facturas reales en papel con Punto de Venta 4 (portal manual) y necesitar dar de alta un Punto de Venta NUEVO (ej. 7) especificamente tipo Web Service para que el sistema pueda facturar.

**Sintoma si esto no esta bien configurado**: AFIP responde con el error real (no un bug de codigo) `11002 - El punto de venta no se encuentra habilitado a usar en el presente WS. Ver metodo FEParamGetPtosVenta`.

**Como diagnosticarlo sin adivinar**: agregar un metodo puntual (no expuesto en la interfaz publica ni en UI, es una herramienta de soporte) que llame `FEParamGetPtosVenta` y liste los puntos de venta que AFIP realmente tiene habilitados para WSFE:

```csharp
public async Task<string> ConsultarPuntosVentaAsync()
{
    var (token, sign) = await _tokenCache.ObtenerAsync(LoginWsaaAsync);
    var cuit = long.Parse(_settings.CUIT, CultureInfo.InvariantCulture);
    var ns = XNamespace.Get(WsfeNamespace);
    var body = new XElement(ns + "FEParamGetPtosVenta", ArmarAuthElement(ns, token, sign, cuit));
    return await PostSoapAsync(_settings.WsfeUrl, WsfeNamespace + "FEParamGetPtosVenta", ArmarEnvelope(ns, body));
}
```

Si la respuesta trae `Err Code 602 "Sin Resultados"`, no hay NINGUN punto de venta habilitado para WS todavia — hace falta que el cliente entre al portal AFIP/ARCA (Clave Fiscal) y de de alta uno nuevo, eligiendo el sistema **"RECE para aplicativo y web services"** en el ABM de Puntos de Venta / Emision (NO "Factura en Linea - Responsable Inscripto", que es la opcion visualmente mas parecida pero es para el portal manual — confusion real que ocurrio probando esto en vivo). Una vez dado de alta, `FEParamGetPtosVenta` devuelve el `PtoVenta` con `Bloqueado=N` y `EmisionTipo` (ej. "CAE - Ri Iva").

**Nunca asumir que un Punto de Venta "prueba y error" (probar 1, probar 4, probar 6...) es mas rapido que consultar `FEParamGetPtosVenta` primero** — la consulta da la respuesta autoritativa de una sola vez.

## Orden de campos XML — estricto, valida contra XSD

`FECAEDetRequest` (dentro de `FECAESolicitar`) exige un orden de campos exacto. Orden real verificado contra el WSDL de **produccion** de AFIP (no una copia vieja) al 21/08/2026:

```
Concepto, DocTipo, DocNro, CbteDesde, CbteHasta, CbteFch,
ImpTotal, ImpTotConc, ImpNeto, ImpOpEx, ImpTrib, ImpIVA,
MonId, MonCotiz, CanMisMonExt, CondicionIVAReceptorId,
CbtesAsoc, Tributos, Iva, ...
```

Puntos criticos:
- **`CondicionIVAReceptorId`** (RG 5616/2024) es obligatorio para TODO comprobante, no solo Factura A — incluye Notas de Credito A (`is 1 or 3`, no solo `== 1`). Si se deriva mal, AFIP puede aceptar el comprobante igual pero con el dato fiscal incorrecto (bug silencioso, no un rechazo).
- **`CbtesAsoc`** (comprobante asociado — obligatorio para Notas de Credito/Debito) va DESPUES de `CondicionIVAReceptorId` y ANTES de `Tributos`/`Iva`. Estructura:
  ```xml
  <CbtesAsoc>
    <CbteAsoc>
      <Tipo>N</Tipo>
      <PtoVta>N</PtoVta>
      <Nro>N</Nro>
    </CbteAsoc>
  </CbtesAsoc>
  ```
  `Cuit`/`CbteFch` dentro de `CbteAsoc` son opcionales, no hace falta enviarlos.
- Si el pedido de un cliente requiere agregar un campo nuevo al request (ej. `Tributos` para percepciones), **verificar el orden contra el WSDL real antes de insertar el `XElement`** — un orden incorrecto produce rechazo SOAP/XSD, no un error de negocio legible.

## Nota de Credito / Debito — patron completo (marihogar CR-55)

- `TipoComprobanteAfip` (enum): el valor ES el codigo real de AFIP, sin mapeo intermedio — `FacturaA=1`, `FacturaB=6`, `NotaCreditoA=3`, `NotaCreditoB=8` (agregar `NotaDebitoA=2`/`NotaDebitoB=7` si un proyecto llega a necesitarlos).
- Modelo de datos: el comprobante "Nota de Credito" es una fila mas de la misma tabla de comprobantes (no una entidad separada), con una auto-FK `ComprobanteAsociadoId` apuntando al comprobante que anula/ajusta.
- **Guard obligatorio en el metodo de "Facturar" normal**: una vez que el enum tiene mas de 2 valores (Factura + NotaCredito), el endpoint normal de emitir Factura DEBE rechazar explicitamente cualquier `TipoComprobante` que no sea Factura — de lo contrario, un POST manipulado (sin pasar por el flujo dedicado de Nota de Credito) puede crear un comprobante fiscal real mal formado (sin `CbtesAsoc`, con la logica de negocio de "reversion" corriendo al reves). Este bug real ocurrio en la primera implementacion de CR-55 en marihogar y lo encontro QA antes de deploy — no asumir que ampliar un enum es un cambio seguro sin revisar cada `switch`/comparacion que ya asumia solo 2 valores.
- Al emitir una NC con exito (CAE real), revertir la cantidad ya facturada del item original (si el sistema trackea facturacion parcial) para que la venta/operacion vuelva a estar disponible para re-facturar correctamente.
- El metodo de "Reintentar" generico (para comprobantes en Estado=Error) debe soportar tanto Facturas como Notas de Credito sin necesitar un metodo separado — pero revisar cualquier validacion que asuma "cantidad pendiente > 0" (una NC tiene pendiente 0 por definicion, no debe bloquear el reintento).

## Verificacion — nunca automatizar contra AFIP real

- **QA/Implementador nunca deben ejecutar una emision real contra AFIP Produccion** de forma automatizada — cualquier comprobante con CAE es un documento fiscal real e irreversible (no existe "deshacer"). Verificar primero que el ambiente de prueba (`appsettings` efectivo) tiene `Ambiente=Homologacion` y/o `CertificadoPath` vacio antes de correr cualquier prueba automatizada por navegador sobre una pantalla de facturacion — en ese estado, el guard de "AFIP no configurado" corta antes de llegar a la red, y es seguro.
- La verificacion real end-to-end contra AFIP (con CAE real) queda siempre a cargo manual del cliente/usuario, con una guia de pasos concretos dejada por el implementador — nunca simulada ni dada por buena sin evidencia real (captura del CAE, o consulta cruzada en el portal "Comprobantes en Linea" de AFIP).
- Para diagnosticar sin usar la UI completa, un metodo de soporte puntual (no expuesto en la interfaz publica, marcado en el codigo como herramienta de diagnostico) que llame `FECompUltimoAutorizado`/`FEParamGetPtosVenta` de solo lectura es seguro de correr cuantas veces haga falta — no emite nada, solo consulta.

## Configuracion (`AfipSettings`, patron ya estable)

Campos minimos: `Ambiente` (Homologacion/Produccion), `CertificadoPath` (relativo al ContentRoot o absoluto), `CertificadoPassword`, `CUIT`, `PuntoVenta`, `PorcentajeIva`, mas datos de solo-impresion del emisor para el PDF (RazonSocial, DomicilioComercial, CondicionIva, IngresosBrutos, FechaInicioActividades — estos NUNCA se envian al webservice, son solo para el PDF, usar los datos reales tal como figuran en una factura real ya emitida por AFIP como fuente de verdad, no adivinarlos). `WsaaUrlHomologacion/Produccion` y `WsfeUrlHomologacion/Produccion` como pares fijos, `Ambiente` decide cual par usar en runtime — nunca si/else de codigo para pasar de homologacion a produccion, es 100% cambio de configuracion.
