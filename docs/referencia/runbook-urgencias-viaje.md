# Runbook de urgencias — operación remota desde el celular

Relevado el **2026-10-15** con medición en vivo (TLS handshake real contra cada dominio + MCP de SmarterASP).
Reemplaza las tablas de vencimientos de la memoria de infraestructura, que estaban desactualizadas al 2026-07-30.

Modo de uso: la notebook queda prendida en casa con la sesión de Claude Code abierta; desde el celular se entra
por `claude.ai/code` y se le pide el procedimiento por nombre ("corré el paso 2 del runbook para vinoysefue").

---

## 1. Acción ANTES de salir (no se resuelve desde el celular)

| # | Qué | Por qué | Dónde |
|---|---|---|---|
| 1 | **Verificar y renovar `olvidata.com.ar` en nic.ar** | La memoria lo tiene venciendo el **18/10/2026**. Si cae, se van juntos el sitio del estudio, `portal.olvidata.com.ar` (CRM), `agentes.olvidata.com.ar` y **el correo**. nic.ar no tiene MCP ni API: es manual, con clave fiscal | nic.ar |
| 2 | **SSL de `vinoysefue.ar` — VENCIDO el 30/09/2026.** ⏳ Preparado el 2026-10-15, **falta emitir** | El `web.config` ya tiene el bloque de validación (PAT-067) y se verificó end-to-end que la ruta ACME sirve 200 `text/plain`. Falta un paso manual: emitir el certificado desde la **UI del panel** (`ssl_request` del MCP no sirve, ver 4c). Hasta entonces el sitio sigue sirviendo el certificado vencido | Panel SmarterASP → SSL |
| 3 | **SSL de `elevenlaplata.com.ar` — vence 19/10 (4 días)** | Sectigo, NO auto-renueva. Cae durante el viaje. Su `web.config` tiene el mismo patrón que vinoysefue, así que **necesita el bloque PAT-067 antes de poder emitir Let's Encrypt** | Panel SmarterASP + web.config |
| 4 | **SSL de `piapartments.es` — vence 31/10 (16 días)** | Sectigo, NO auto-renueva. Cae durante el viaje. **No hay repo local** de este proyecto: su `web.config` hay que mirarlo en el servidor | Panel SmarterASP + web.config |
| 4b | Actualizar la password en los 24 perfiles de publicación | Todos tienen la vieja (`olvidata123`); el primer deploy va a fallar la autenticación | Visual Studio / `.pubxml.user` |
| 5 | Pausar Windows Update en la notebook (5 semanas) | Horas activas 08:00–01:00 → puede reiniciar solo de madrugada y matar la sesión sin forma de levantarla | Configuración → Windows Update |
| 6 | Dejar la notebook **enchufada** | Con batería suspende a los 30 min (enchufada ya está en "nunca") | — |
| 7 | Prueba de humo del circuito celular → notebook | Confirmar que responde antes de estar a 3.000 km | `claude.ai/code` |

**Regla general del SSL:** los certificados **Let's Encrypt** renuevan 100% automático server-side en SmarterASP
(confirmado KB a1885/a2162) — no hay que tocarlos. Los **Sectigo** son manuales y pagos. Hoy 15 de 17 dominios
siguen en Sectigo: migrarlos a Let's Encrypt ahorra ≈USD 29/sitio/año (≈USD 400/año) **y elimina esta clase de
urgencia de raíz**. Es la tarea de mayor impacto y menor riesgo pendiente — para después del viaje.

## 2. Vencimientos de SSL en la ventana del viaje (medición en vivo 2026-10-15)

| Dominio | Vence | Días | Emisor | Riesgo |
|---|---|---|---|---|
| **vinoysefue.ar** | 2026-09-30 | **-15** | Sectigo | 🔴 YA VENCIDO |
| **elevenlaplata.com.ar** | 2026-10-19 | 4 | Sectigo | 🔴 manual |
| portal.olvidata.com.ar | 2026-10-19 | 4 | Let's Encrypt | 🟢 auto-renueva |
| **piapartments.es** | 2026-10-31 | 16 | Sectigo | 🟠 manual |
| estanciasantarosa.com.ar | 2026-11-22 | 38 | Sectigo | 🟡 vigilar |
| olvidata.com.ar | 2026-12-22 | 68 | Let's Encrypt | 🟢 auto-renueva |
| lumitrack.com.ar | 2026-12-31 | 77 | Sectigo | verde |
| portal.lab-ipac.com.ar | 2027-01-03 | 80 | Sectigo | verde |

El resto (deliciasnaturales, recotrack, marihogar, contadoresbma, ferreterialaplatense, portaldelinversor,
virtualwallet, agentes.olvidata, showroomgriffin) vence entre febrero y abril de 2027: fuera de la ventana.

Nota: `virtualwallet.com.ar` y `showroomgriffin.com.ar` figuraban como los más urgentes en la memoria vieja.
**Ya fueron renovados** — vencen 31/03/2027 y 17/04/2027. No son un problema.

## 3. Mapa sitio ↔ dominio ↔ siteId (para pedir acciones por MCP)

| Sistema | Dominio productivo | siteId |
|---|---|---|
| OlvidataCRM | portal.olvidata.com.ar | `site-1860209` |
| AgentesIA | agentes.olvidata.com.ar | `site-1884659` |
| MariHogar | marihogar.com.ar | `site-1862338` |
| LaPlatense | ferreterialaplatense.com.ar | `site-1868186` |
| ganaderia | estanciasantarosa.com.ar | `site-1831240` |
| labipac | portal.lab-ipac.com.ar | `site-1846587` |
| elevenlp | elevenlaplata.com.ar | `site-1812542` |
| RecoTrack | recotrack.com.ar | `site-1797596` |
| Lumitrack | lumitrack.com.ar | `site-1714110` |
| deliciasnaturales | deliciasnaturales.com.ar | `site-1554440` |
| vinoysefue | vinoysefue.ar | `site-1806565` |
| VirtualWallet | virtualwallet.com.ar | `site-1269853` |
| piapartments | piapartments.es | `site-1456111` |
| showroomgriffin | showroomgriffin.com.ar | `site-1823142` |
| KoiDumplings | portaldelinversor.com.ar | `site-1857210` |

Los 15 están en el plan `plan-10954015` (cuenta `olvidatasoft-002`, Premium, vence 06/04/2027).

---

## 4. Procedimientos

### P1 — El sitio no abre / error 500
1. `project_health_check` + `website_get_logs` del siteId → leer la excepción real antes de tocar nada.
2. Si es pool colgado o memoria: `website_restart`. Resuelve la mayoría de los 500 transitorios.
3. Si el log muestra error de conexión a MySQL: `database_get_capacity` y `hosting_get_resource_usage` —
   el límite de conexiones de MySQL en Premium es el sospechoso histórico (KB dice 20; pendiente de confirmar).
4. Si el log muestra una excepción de código: **mitigar, no arreglar.** Reiniciar y avisar al cliente que el fix
   queda para la vuelta. Editar y deployar código desde el celular es posible pero es la peor idea del runbook:
   sin poder ver la app andando no hay forma de verificar, y la regla del estudio es que quien construye no califica.

### P2 — SSL vencido o advertencia del navegador
1. Confirmar cuál es: pedir la medición en vivo (el script de TLS handshake quedó en el historial de esta sesión).
2. Si es **Let's Encrypt**: esperar. Renueva solo, server-side.
3. **`ssl_request` del MCP no sirve** en estos sitios (ver 4c): el preflight exige 200 sin redirect. La emisión
   va por la UI del panel de SmarterASP, que no tiene ese preflight.
4. Antes de emitir, confirmar que el sitio sirve `/.well-known/acme-challenge/` como estático: subir un archivo
   de prueba por FTPS a `/<sitio>/.well-known/acme-challenge/x` y pedirlo por **http** (sin `-L`). Si responde
   200 `text/plain`, la validación va a pasar. Si responde el 404 de la app, falta el bloque `<location>` del
   `web.config` (ver 4d).
5. Si es **Sectigo** y hay que pagarlo: **avisar el costo y esperar OK antes de ejecutar.**
6. Tras emitir: volver a medir el handshake TLS y confirmar emisor + fecha nueva. No confiar en el "listo" del panel.

### 4d — Bloque de web.config para que ande Let's Encrypt
Los sitios ASP.NET Core de la flota tienen `<handlers><add name="aspNetCore" path="*" verb="*">`, que se come
`/.well-known/acme-challenge/*`: la app responde su propio 404 y la validación HTTP-01 falla. **El redirect a
HTTPS no es el problema** — Let's Encrypt sigue redirects e ignora certificados inválidos; se comprobó midiendo.
El arreglo es un `<location path=".well-known/acme-challenge">` que limpia handlers y sirve estático con
mimeMap `.` → `text/plain`. Aplicado y verificado en vinoysefue el 2026-10-15; el bloque exacto está en
`C:\Sistemas\vino-y-se-fue\VinoSeFue.Web\web.config`. **Los otros sitios de la flota lo necesitan igual.**

Al editar un `web.config` en el servidor: bajarlo primero y parchear **esa** copia, nunca subir la del repo.
El publish reescribe `processPath` (`dotnet` en el repo vs. `.\<App>.exe` en el servidor) y agrega un comentario
`ProjectGuid` al final — subir la del repo pisa ambos.

### P3 — No me llega / no sale el mail
1. `email_get_smtp_settings` + `email_test_smtp` del dominio → separa "no sale" de "no llega".
2. `email_get_capacity` y `email_list_mailboxes` → casilla llena es la causa más común. `email_update_mailbox_quota`.
3. Si rebota por credenciales: `email_rotate_credential` y actualizar el secret del sitio con
   `website_set_environment_secret` (no hardcodear en appsettings).
4. Si `olvidata.com.ar` dejó de resolver: ir a P5 — es el dominio, no el mail.

### P4 — Datos mal / hay que volver atrás
1. **Primero el backup, siempre:** `database_create_backup` antes de cualquier restore. Sin excepción.
2. `database_restore_backup` solo con el OK explícito del cliente por escrito: pisa datos y es irreversible.
3. Un restore es una decisión de negocio, no técnica. Si el cliente no contesta, no se restaura.

### P5 — El dominio dejó de resolver
1. `dns_list_records` del dominio → ver si los registros están.
2. Si los registros están bien pero no resuelve: es el **registro en nic.ar**, no el DNS. Se renueva con clave
   fiscal de Joaquín, manual, desde el celular en nic.ar. No hay MCP para esto.
3. `dns_upsert_record` / `domain_attach_to_website` solo si falta el apuntamiento al sitio.
4. `olvidata.com.ar` resuelve por `ns9/ns10.hostmar.com` (DonWeb/Ferozo), **no** por SmarterASP: los cambios de
   DNS de ese dominio van en el panel de DonWeb, no acá.

### P6 — Nada de lo anterior / no se entiende
`support_create_ticket` en SmarterASP. Soporte responde razonablemente rápido y desde el celular el ticket se
sigue con `support_get_ticket` / `support_reply_ticket`.

---

## 4b. Estado real del deploy (verificado 2026-10-15)

**FTPS por el puerto 21 funciona** con `olvidatasoft-002` / la password vigente (está en
`docs/credenciales.local.md`, actualizada ese día). Es el único camino operativo y es suficiente para subir
archivos sueltos, que es lo que cubre una urgencia.

- **Los 24 perfiles de publicación del disco tienen la password vieja** (`olvidata123`), incluido el más
  reciente, de 2026-09-23. Un deploy desde Visual Studio va a fallar la autenticación hasta actualizarlos.
- **Web Deploy NO sirve desde la red de casa**: habilitado del lado del servidor
  (`deployment_get_status` → `enabled`), pero el **puerto 8172 es inalcanzable** (TCP test falla; no hay VPN
  de por medio, verificado con un solo adaptador activo y ruta única). MSDeploy corta con
  `ERROR_DESTINATION_NOT_REACHABLE`. La notebook se queda en esta red durante el viaje, así que **seguirá
  bloqueado** salvo que se pruebe desde otra conexión.
- **Web Deploy**: habilitado del lado del servidor (`deployment_get_status` → `enabled`), pero el
  **puerto 8172 es inalcanzable** desde esta red (TCP test falla). MSDeploy corta con
  `ERROR_DESTINATION_NOT_REACHABLE`.
- **Crear un usuario FTP acotado por MCP**: `ftp_create_user` falla **5 veces** con `ftp_user_create_failed`
  (el servicio de hosting no completa la operación), probando 3 variantes de `path`, login y quota. No es un
  problema de parámetros; no quedó ningún usuario a medio crear. **Esa tool no sirve** — para un usuario FTP
  nuevo, usar el panel.

## 4c. `ssl_request` del MCP no sirve en sitios que fuerzan HTTPS (verificado 2026-10-15) 🔴

El preflight de `ssl_request` exige **HTTP 200 en la raíz del dominio mapeado, sin redirect**. Todos los sitios
del estudio redirigen (canónico a `www` y/o forzado de HTTPS), así que **el preflight falla siempre** — no es un
problema de vinoysefue. Medido ahí: `http://vinoysefue.ar/` → 301, `http://www.vinoysefue.ar/` → 301,
`https://vinoysefue.ar/` → 301; sólo `https://www.vinoysefue.ar/` → 200. Falla igual pidiendo el dominio
desnudo que el `www`.

Satisfacer ese preflight exigiría apagar el forzado de HTTPS del sitio durante la emisión — una regresión de
seguridad en un sitio con login. **No hacerlo.** Para emitir Let's Encrypt, usar la UI del panel de SmarterASP,
que no pasa por este preflight.

**Implicancia para el viaje:** si surge una urgencia que requiera subir un archivo, hoy no se puede — ni desde
el celular ni desde la notebook. Resolver ANTES de salir: traer la clave de FTP vigente del panel
(FTP Manager en SmarterASP), guardarla en `docs/credenciales.local.md`, actualizar los perfiles de publicación
y **probar un deploy real de punta a punta**. Un deploy que nunca se probó no es un camino de deploy.

## 5. Qué NO se puede resolver desde el celular

- **Código y deploy.** Técnicamente sí (la notebook tiene los repos), pero sin poder verificar la app andando
  el riesgo es mayor que el beneficio. Mitigar y postergar.
- **nic.ar.** Manual con clave fiscal. Es la razón del punto 1 de la lista de antes de salir.
- **Si se corta la luz o internet en casa**, se cae la sesión y queda solo lo que es MCP remoto puro
  (SmarterASP, Gmail, Drive, Meta Ads) desde `claude.ai/code`. Eso igual cubre P1 a P6 completo —
  ninguno de esos procedimientos necesita la notebook.
- **Facturación de SmarterASP / AFIP.** Nada vence en la ventana del viaje (cuenta: 06/04/2027).
