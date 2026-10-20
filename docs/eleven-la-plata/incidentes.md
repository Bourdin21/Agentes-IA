# Incidentes de produccion

Registro de la via rapida (`42-incidente-produccion.instructions.md` / `/agentes-ia-emergencia`).
Solo P1 (caida o corrupcion en curso) y P2 (operacion diaria bloqueada sin workaround). Un pedido urgente **sin**
caida es P3 y no se anota aca: va por el flujo normal.

Reglas de este archivo: **entradas con id** (`29-trazabilidad-conversacion`) — una definicion nueva no pisa el texto
viejo; techo de 150 KB, archivado con `python scripts/archivar_memoria.py incidentes.md --aplicar`.

Estados, en orden y sin saltos: **`abierto`** (en curso) -> **`restablecido`** (el cliente trabaja, smoke propio) ->
**`cerrado`** (paso la corrida de QA independiente).

## Incidentes

### INC-001 — Sitio caido (503) por deploy interrumpido  ·  estado: restablecido
- **nivel:** P1
- **abierto:** 2026-10-19 (durante el deploy de ELV-010/011/012)
- **sintoma observado:** `https://www.elevenlaplata.com.ar/` devolvia **HTTP 503**. Verificado por request directo,
  no inferido.
- **alcance:** sitio completo, todos los usuarios.
- **cobertura:** interno — lo causamos nosotros deployando, no es un fallo del sistema ni del hosting.
- **causa raiz:** **observada.** El perfil de Web Deploy tiene `SkipExtraFilesOnServer=false`, asi que sincroniza
  borrando del servidor todo lo que no esta en el build — incluida la carpeta `Logs\` del sitio, con meses de
  archivos. En medio de ese borrado masivo MSDeploy corto con `ERROR_CONNECTION_TERMINATED` ("Fin inesperado de
  archivo"). Como el perfil tambien tiene `EnableMsDeployAppOffline=true`, el `app_offline.htm` ya estaba puesto y
  **nadie lo saco**: el sitio quedo offline por un deploy que ni fallo ni termino.
- **contencion:** no hizo falta mitigar aparte — la via mas rapida para sacar el `app_offline` era completar el
  deploy, asi que se fue directo al fix.
- **plan de vuelta atras:** el commit anterior seguia en `dev` y el publish local estaba intacto; si el segundo
  intento tambien cortaba, el paso siguiente era subir por FTP el contenido ya generado en
  `Eleven.Web\bin\Release\net10.0\publish\` y borrar el `app_offline.htm` a mano.
- **backup:** no aplica — el deploy no toca la base (sin migracion EF y sin `Migrate()` al arrancar, verificado en
  `Program.cs`). MSDeploy ademas tiene `EnableMSDeployBackup=true`.
- **filas medidas:** N/A, no se escribio sobre datos.
- **fix aplicado:** republicar con `SkipExtraFilesOnServer=true` (+ `RetryAttempts=20`), que sincroniza sin borrar
  lo que ya esta en el servidor. Termino con "Se publico correctamente".
- **aviso enviado:** no hizo falta — la caida duro minutos, fuera de una operacion en curso, y se restablecio antes
  de que el cliente la reportara. El aviso de ELV-004 (el formulario de contadores ahora rechaza) ya lo habia
  mandado Joaquin antes del deploy.
- **restablecido:** 2026-10-19, `https://www.elevenlaplata.com.ar/` responde **HTTP 200**, 8.901 bytes.
- **cerrado:** pendiente.
- **horas reales:** ~15 min entre el corte y el 200.
- **regresion catalogada:** N/A — no es un bug del sistema sino del procedimiento de deploy. La leccion va abajo.

#### Leccion operativa (esto es lo unico que hay que recordar)
**Para este hosting, un deploy con `SkipExtraFilesOnServer=false` es fragil**: el borrado masivo de `Logs\` es
suficiente para que SmarterASP corte la conexion, y un corte a mitad con `EnableMsDeployAppOffline=true` deja el
sitio caido sin que nada falle de forma visible — el comando devuelve error, pero el estado que deja es "offline",
no "sin cambios". Los dos candidatos a dejar fijos en el perfil, a decidir con infra:
1. `SkipExtraFilesOnServer=true` por defecto, limpiando el servidor a mano cuando de verdad haga falta; o
2. una `MsDeploySkipRule` para `Logs\` igual a la que ya existe para la carpeta `keys` de Data Protection.
La opcion 2 es la mejor de las dos: conserva la limpieza de archivos huerfanos (que es para lo que esta el flag) y
saca del medio la carpeta que hace volumen. **Queda pendiente de decision, no aplicada.**

#### Deuda que deja abierta
El segundo intento corrio con `SkipExtraFilesOnServer=true`, asi que **en el servidor pueden haber quedado archivos
huerfanos** del deploy anterior (los que el primer intento alcanzo a no borrar). No afectan el funcionamiento, pero
el proximo deploy limpio deberia contemplarlo.

### INC-002 — Certificado SSL vencido: el sistema queda inaccesible  ·  estado: abierto
- **nivel:** P1
- **abierto:** 2026-10-20 (reportado por Joaquin; el certificado vencio el 2026-10-19 a las 21:00)
- **sintoma observado:** handshake TLS rechazado en `https://www.elevenlaplata.com.ar/` y en el apex. Certificado
  leido por handshake directo: `CN=elevenlaplata.com.ar`, emisor **Sectigo Public Server Authentication CA DV
  R36**, valido hasta **2026-10-19 20:59:59**. No es uno de los Let's Encrypt que renuevan solos server-side.
- **alcance:** todos los usuarios. **Nadie puede iniciar sesion**, ni siquiera por la URL de backup: la cookie de
  autenticacion es `CookieSecurePolicy.Always` (`Program.cs:77`), asi que el navegador no la manda por HTTP.
  Sumado a `UseHsts()`, en el dominio propio Chrome tampoco deja saltear el aviso del certificado.
- **cobertura:** mantenimiento vigente.
- **contencion:** URL de backup entregada — `http://olvidatasoft-002-site8.stempurl.com/` responde 200. Sirve para
  constatar que el sitio esta vivo, **no para trabajar** (ver alcance).
- **causa raiz:** **observada**, y tiene dos capas. La primera es que el certificado Sectigo vencio y no se
  renovo. La segunda es la que impidio arreglarlo rapido: **el sitio no podia emitir un certificado nuevo porque
  el certificado estaba vencido.** IIS redirigia con 301 todo el HTTP a HTTPS, incluido
  `/.well-known/acme-challenge/`, y el handshake de HTTPS fallaba. Circulo cerrado.
- **plan de vuelta atras:** los cambios de `web.config` y `appsettings.Production.json` estan versionados;
  revertir es un `git checkout` del archivo y un publish.
- **backup:** no aplica, no se toco la base en ningun momento.
- **filas medidas:** N/A.
- **fix aplicado (parcial):** tres cambios, los dos primeros **permanentes y correctos** mas alla de este
  incidente:
  1. `web.config` — regla `ACME challenge passthrough` **primera de todas**, que sirve
     `/.well-known/acme-challenge/` por HTTP sin redirigir. Verificado: pasa de 301 a 404, y la home sigue
     redirigiendo a HTTPS. **Esto es lo que evita que el circulo vicioso se repita en la proxima renovacion.**
  2. `appsettings.Production.json` — `AllowedHosts` suma el apex `elevenlaplata.com.ar`. Hasta ahora el apex
     devolvia **400** si llegaba a la app: funcionaba de casualidad, porque la regla canonica de IIS lo
     interceptaba antes. El preflight de SSL exige 200 en el dominio mapeado, que es justamente el apex.
  3. `web.config` — las reglas `Canonical Domain` y `Force HTTPS` quedaron en **enabled false**, que es
     **temporal y hay que revertir** en cuanto haya certificado.
- **estado del bloqueo:** con eso el preflight de SmarterASP **pasa** (el apex devuelve 200), pero la emision
  sigue fallando del lado del hosting: `ssl_request` responde *"The hosting service did not queue the SSL
  request"* en tres intentos. Hipotesis mas probable, **no verificada**: el Sectigo vencido sigue instalado y el
  panel no deja pedir el gratuito encima sin removerlo primero. No hay herramienta de API para borrar un
  certificado ya instalado.
- **aviso enviado:** pendiente de decision de Joaquin.
- **restablecido:** **NO.** El sistema sigue sin poder usarse.
- **cerrado:** pendiente.
- **horas reales:** ~40 min hasta aca.
- **regresion catalogada:** N/A — es infraestructura, no un bug del sistema.

#### Lo que queda por hacer, en orden
1. **Quitar el certificado Sectigo vencido desde el panel de SmarterASP** y volver a pedir el gratuito (o abrir
   ticket de soporte). Es el unico paso que no se puede hacer por API con las herramientas disponibles.
2. Con el certificado emitido, **volver `Canonical Domain` y `Force HTTPS` a enabled true** y publicar. Hasta que
   eso pase, el sitio responde por HTTP sin forzar HTTPS.
3. Verificar el handshake y que el login funcione.
4. **Revisar el resto de los sitios con Sectigo:** si este vencio sin aviso, los demas del mismo lote van por el
   mismo camino. La migracion a Let's Encrypt estaba en piloto justamente por esto.

#### Leccion operativa
**Un redirect a HTTPS sin excepcion para `/.well-known/acme-challenge/` convierte un certificado vencido en un
problema que no se puede arreglar solo.** La excepcion no cuesta nada y hay que tenerla puesta ANTES de
necesitarla, en todos los sitios del estudio, no solo en este. Segundo: `AllowedHosts` sin el apex es una bomba de
tiempo silenciosa, porque funciona mientras IIS intercepte y falla el dia que se toca una regla de rewrite.

## Historial de ajustes
- 2026-10-19: alta del archivo con INC-001, primer incidente registrado por la via rapida (`42`).
