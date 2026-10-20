# Incidentes de produccion

Registro de la via rapida (`42-incidente-produccion.instructions.md` / `/agentes-ia-emergencia`).
Solo P1 (caida o corrupcion en curso) y P2 (operacion diaria bloqueada sin workaround). Un pedido urgente **sin**
caida es P3 y no se anota aca: va por el flujo normal.

Reglas de este archivo: **entradas con id** (`29-trazabilidad-conversacion`) — una definicion nueva no pisa el texto
viejo; techo de 150 KB, archivado con `python scripts/archivar_memoria.py incidentes.md --aplicar`.

El `INC` se **abre en el paso 0 del triage**, con los cinco campos de arranque, y se completa mientras avanza. El
informe que se deja para el final no se escribe nunca.

Estados, en orden y sin saltos: **`abierto`** (en curso) -> **`restablecido`** (el cliente trabaja, smoke propio) ->
**`cerrado`** (paso la corrida de QA independiente). `doctor.py` avisa a los 7 dias sin cerrar y marca error a los 30.

## Incidentes

### INC-001 — "No abre el sistema: el navegador dice que el certificado no es seguro"  ·  estado: restablecido
- **nivel:** P1 — nadie puede entrar al CRM por HTTPS desde un navegador.
- **abierto:** 2026-10-19 21:15 (UTC)
- **sintoma observado:** `https://portal.olvidata.com.ar/` falla el handshake TLS con
  `SEC_E_CERT_EXPIRED` (curl 35). Con `-k` (sin verificar el certificado) el sitio responde **200**: la
  aplicacion y la base estan sanas, el problema es exclusivamente el certificado. `http://` devuelve 301
  al https roto, asi que no hay via de entrada.
- **alcance:** todos los usuarios del CRM, todas las pantallas. El webhook de WhatsApp y el de Instagram
  tambien dejan de recibir: Meta **si** valida el certificado del endpoint, a diferencia de Let's Encrypt.
  **Impacto medido no evaluado**: no se conto cuantos mensajes entrantes se perdieron en la ventana.
- **cobertura:** infraestructura propia del estudio (sistema interno). Sin discusion de plata.
- **contencion:** **no se contuvo.** No hay contencion posible del lado de la app: un certificado vencido
  solo se arregla emitiendo otro. Se descarto apagar el forzado de HTTPS para habilitar la entrada por
  HTTP plano: el sitio tiene login con cookie de Identity y serviria credenciales en claro.
  Deploy en las ultimas 72 h: **si** (2026-10-15, 10-17 y 10-19, canal de Instagram). **Descartado como
  causa con evidencia**: el `web.config` de produccion era byte a byte el del repo y **nunca** tuvo el
  bloque `.well-known/acme-challenge`; la renovacion venia fallando desde ~2026-09-19 (certificado
  emitido el 21/07, vigencia 90 dias), un mes antes del primer deploy.
- **plan de vuelta atras:** el `web.config` anterior quedo respaldado en
  `scratchpad/web.config.prod.antes` (1212 bytes). Restaurarlo revierte el cambio completo; no hay nada
  mas que deshacer, el fix no toca datos ni codigo de negocio.
- **backup:** no corresponde — el fix no toca la base. (El ultimo backup de BD es
  `/db/db_a7251f_olvidat.sql`, del 2026-10-15.)
- **filas medidas:** N/A — el fix no escribe datos.
- **causa raiz:** **observada.** La validacion HTTP-01 de Let's Encrypt no podia completarse nunca: el
  handler `aspNetCore` (`path="*" verb="*"`) del `web.config` se comia `/.well-known/acme-challenge/*` y
  la aplicacion respondia su propio 404. Evidencia: `curl -skL` a esa ruta devolvia el 404 **branded**
  (`<title>Página no encontrada - OlvidataCRM</title>`), no el de IIS. Es **PAT-067**, identico al de
  vinosefue del 2026-10-15.
  **Lo que NO es la causa, y parecia serlo:** el redirect a HTTPS. Let's Encrypt sigue redirects en
  HTTP-01 y no valida el certificado del destino (nota de PAT-067, medida en vinosefue). Culpar al
  redirect lleva a un parche que no arregla nada.
- **archivos del fix:** `OlvidataCRM.Web/web.config` — bloque
  `<location path=".well-known/acme-challenge">` que limpia handlers, sirve con `StaticFileModule`,
  mapea `mimeMap "." -> text/plain` y hace `<clear />` de las reglas de rewrite. Aplicado al repo **y**
  a produccion (via publish, que aplica la transformacion correcta del archivo).
- **migracion EF:** no.
- **aviso enviado:** no hacia falta — el fix no cambia nada de lo que el usuario ve ni de lo que el
  sistema acepta. El aviso que **si** corresponde es el de la ventana de caida, y lo da el cliente.
- **restablecido:** **todavia no.** El fix habilita la emision pero no emite: el certificado lo tiene que
  pedir una persona desde la **UI del panel de SmarterASP**. La tool `ssl_request` del MCP se intento y
  fallo con `ssl_preflight_failed` ("the domain must resolve directly and return HTTP 200 before SSL can
  be requested"), exactamente como documenta PAT-067: su preflight exige 200 sin redirect y este sitio
  fuerza HTTPS. Satisfacerlo exigiria apagar el forzado durante la emision — no se hace en un sitio con
  login.
  Verificacion de que la emision va a pasar (smoke propio, 2026-10-19 21:40): `curl` por **HTTP plano y
  sin seguir redirects** a `/.well-known/acme-challenge/prueba` devuelve **404 de IIS**
  (`Server: Microsoft-IIS/10.0`, XHTML Strict) en vez del 404 de la app — el handler estatico tomo el
  control y solo falta el archivo del token. `/` y `/Account/Login` responden 200 con `-k`.
- **emision (2026-10-19 20:55 UTC):** certificado **emitido**, vence **2027-01-17**. La via de este
  sitio no es el panel: SmarterASP **no ofrece Let's Encrypt** para este plan — el panel de SSL de
  OlvidataCRM solo tiene *CSR Request / Buy SSL / Import SSL*. El certificado del 21/07 se habia
  emitido con **Certbot manual** (`--config-dir C:\Certbot`, cuenta ACME ya registrada) y subido con
  *Import SSL*; es manual de punta a punta, por eso vencio a los 90 dias exactos sin que nadie se
  entere. Ver `historial/trazabilidad-2026-07.md` entrada del 2026-07-21.
  **Diferencia con aquella vez:** se valido por **HTTP-01** en vez de DNS-01, que es justamente lo que
  habilita el bloque PAT-067 de este incidente — el token lo sube un hook por FTP y no hace falta que
  el cliente toque el DNS ni esperar propagacion. El `renewal/portal.olvidata.com.ar.conf` quedo con
  `pref_challs = http-01` y los hooks (`C:\Certbot\hook-auth.bat` / `hook-cleanup.bat`), asi que la
  **renovacion ya corre sola** por la tarea programada de certbot. Lo que sigue manual es la importacion
  del `.pfx` en el panel cada 90 dias — deuda abierta, no resuelta por este incidente.
- **falta para restablecer:** importar `C:\Certbot\portal_olvidata_2026-10-19.pfx` desde
  *Sitio OlvidataCRM -> SSL -> Import SSL*. Lo hace una persona; no hay API para eso.
- **restablecido (2026-10-19 21:55 UTC):** el cliente importo el `.pfx` por *Import SSL* y confirmo
  ("listo ya funciona"). Smoke propio, **sin `-k`**: handshake TLS valido, `/` → 200,
  `/Account/Login` → 200, y el certificado que sirve el server es el nuevo
  (`notAfter = Jan 17 20:55:04 2027 GMT`, emisor `CN=YE2`). Webhooks con token invalido:
  `/webhook/instagram` → 403 correcto.
- **cerrado:** —
- **horas reales:** ~1,0 h de incidente (triage, diagnostico, fix, el error propio de abajo y verificacion).
- **regresion catalogada:** PAT-067 ya existe en `docs/patrones/catalogo.yml`; se agrega `crm-olvidata` a
  `proyectos_que_lo_usan`. **Pendiente de catalogar como regla propia**: el incidente operativo de abajo.

#### Error propio durante el incidente (2026-10-19 21:30)

Al intentar parchear el `web.config` de produccion por **FTPS**, la conexion de datos del hosting fallo a
mitad de la escritura (`ConnectionResetError` en el cierre TLS) y **dejo el servidor sin `web.config`**: los
`RETR` siguientes devolvian `550 The system cannot find the file specified` y un `LIST` no mostraba el
archivo. El sitio siguio respondiendo 200 porque IIS tenia la configuracion cargada en memoria — si el
application pool se hubiera reciclado en esa ventana, el sitio pasaba de "certificado vencido" a **502.5
caido del todo**, un escalon peor que el incidente original.

Se restauro publicando por **Web Deploy** (11 cambios, 1 agregado = el `web.config` recreado), que ademas
deja el repo y el servidor en sinc.

**Leccion, para el catalogo:** el `web.config` de un sitio en produccion **no se edita por FTP**. Es el
unico archivo cuya ausencia tira el sitio entero, y el FTPS de este hosting falla de forma transitoria y
documentada (el propio perfil de Web Deploy lista `ERROR_CONNECTION_TERMINATED` entre sus fallas
conocidas). Se edita en el repo y se publica — el publish es atomico por archivo y aplica la
transformacion correcta de `processPath`. La nota de PAT-067 que dice "bajar esa copia y parchearla, nunca
subir la del repo" aplica cuando repo y servidor **divergen**; aca eran identicos, asi que publicar era la
via segura desde el principio y no se evaluo.

#### Hallazgo que explica el error propio: el FTPS de este hosting no sube con PROT P (2026-10-19 20:45)

Probadas las 5 variantes contra `/olvidatacrm/.well-known/acme-challenge/`, verificando **releyendo el
archivo**, no el codigo de retorno del `STOR`:

| variante | resultado |
|---|---|
| FTPS `PROT P` pasivo | `STOR` → `TimeoutError`, **el archivo no queda** |
| FTPS `PROT P` + reuso de sesion TLS | igual, `TimeoutError` |
| FTPS `PROT C` directo | `503 Bad sequence of commands` (falta el `PBSZ 0`) |
| **FTPS `prot_p()` + `prot_c()`** | **sube y se relee igual** |
| FTP plano | sube, pero manda la credencial en claro — descartado |

O sea: el canal de **datos** cifrado esta roto en subida en este hosting (en bajada funciona, por eso
los `RETR` del parche anterior andaban). `prot_p()` manda `PBSZ 0` + `PROT P` y recien despues el server
acepta `PROT C`: queda el **control cifrado** — la credencial viaja protegida — y los **datos en claro**,
que para un token ACME publico no protege nada de todos modos.

**Esto es la causa del `web.config` borrado de mas arriba**: no fue una falla transitoria, es
determinista. El `STOR` por `PROT P` abre el archivo en el server, lo trunca y despues muere — por eso
quedo en cero y despues ni listaba. Reintentar no iba a arreglarlo nunca.

## Historial de ajustes
- 2026-10-19: certificado emitido por Certbot/HTTP-01 y documentada la via real de este sitio
  (panel sin Let's Encrypt + import manual del .pfx). Agregado el hallazgo del FTPS `PROT P`.
- 2026-10-19: archivo creado desde la plantilla al abrir INC-001 (primer incidente registrado por la via
  rapida en este proyecto).
