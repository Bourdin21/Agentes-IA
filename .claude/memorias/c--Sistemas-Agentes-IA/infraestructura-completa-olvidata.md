---
name: infraestructura-completa-olvidata
description: "Inventario completo de infraestructura de Olvidata Soft al 2026-07-30 — SmarterASP (sitios .NET + BD MySQL + SSL), servidor DonWeb (sitios reseller Linux), dominios nic.ar, con vencimientos y umbrales de capacidad"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-09-02T03:30:58.446Z
---

Inventario relevado directamente por Joaquín el 2026-07-30 (paneles de SmarterASP.NET y DonWeb + nic.ar). Complementa [[project-hosting-sharding-smarterasp]] (que ya tenía la regla de break-even BD/RAM y el historial de fusión de pools) con el detalle completo de sitios, SSL y dominios, y agrega el servidor DonWeb que no estaba documentado antes.

## SmarterASP.NET — cuenta `olvidatasoft-002` (Windows Server 2022 Premium, vence 06/04/2027)

**16 sitios .NET activos** (más `laslatas`/`koidumplings` sin dominio propio, solo tempurl):
belclau (belclau.com.ar) · virtualwallet (virtualwallet.com.ar) · piapartments (piapartments.es) · deliciasnaturales (deliciasnaturales.com.ar) · laslatas (solo tempurl) · lumitrack (lumitrack.com.ar) · recotrack (recotrack.com.ar) · vinoysefue (vinoysefue.ar) · elevenlp (elevenlaplata.com.ar) · showroomgriffin (showroomgriffin.com.ar) · ganaderia (estanciasantarosa.com.ar) · labipac (portal.lab-ipac.com.ar) · koidumplings (solo tempurl) · olvidatacrm (portal.olvidata.com.ar) · marihogar (marihogar.com.ar)

**Bases de datos MySQL: 17/20 usadas** (subió de 15/20 el 2026-07-14 a 17/20 el 2026-07-30 — 2 nuevas en ~2 semanas). Disco 7750/10000 MB — **falsa alarma, no es el límite real** (cada BD reserva 500 MB fijos por defecto, el uso real es marginal; ver [[project-hosting-sharding-smarterasp]]). Una de las 17 (`db_a7251f_eleven`, la vieja, 50 MB) está marcada "ya migrada, a borrar" — al borrarla quedan 16 activas + 4 slots libres reales.
**Umbral de alerta ya señalado en la memoria hermana: avisar entre 20-21 BD activas.** Al ritmo de 2 nuevas cada ~2 semanas, y con La Platense recién aprobado (sumaría 1 sitio + 1 BD más), **el cupo de 20 podría alcanzarse en pocos meses si el ritmo de altas se sostiene** — vale la pena monitorear cada vez que se agregue un cliente nuevo, no esperar a la próxima revisión trimestral.

**RAM de application pools: CONFIRMADO 2026-07-30, 3072/3072 MB (100%, sin margen).** La fusión de pools recomendada el 2026-07-14 (ver [[project-hosting-sharding-smarterasp]]) **nunca se ejecutó** (o se revirtió) — el panel real muestra 3 pools separados, no 2:

| Pool | Runtime | Bit | RAM | Sitios (16 total) |
|---|---|---|---|---|
| `olvidatasoft-002` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | Eleven, belclau, piapartments, laslatas, Lumitrack, labipac, KoiDumplings, OlvidataCRM (8) |
| `olvidatasoft-002sjn` | .NET Core 10.x→2.x | 64-bit | 1024 MB | VirtualWallet, RecoTrack, vinoysefue, elevenlp, showroomgriffin, ganaderia, MariHogar (7) |
| `olvidatasoft-002xdn` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | deliciasnaturales (1, sola en todo un pool) |

**Acción de mayor apalancamiento, costo cero, pendiente desde el 2026-07-14 y todavía no ejecutada:** fusionar `olvidatasoft-002xdn` (1 sitio) dentro de `olvidatasoft-002` (mismo runtime ASP.NET 4.x, mismo bitness 32-bit) — libera un pool entero de 1024 MB sin costo, exactamente lo que hace falta para alojar clientes nuevos con aislamiento propio (ej. La Platense, aprobado el 2026-07-30).

**Para el próximo sitio nuevo en el stack actual (.NET 10), no hace falta pool nuevo ni fusión:** sumarlo directamente a `olvidatasoft-002sjn` no consume RAM de cuota adicional (compartir un pool existente es gratis) — solo hay que vigilar que ese pool no empiece a mostrar reciclados por memoria a medida que crece de 7 a 8+ sitios.

**Plan de acción confirmado por `olvidata-infra` (2026-07-30, pendiente de ejecutar):**
1. Fusionar `olvidatasoft-002xdn` (deliciasnaturales) dentro de `olvidatasoft-002` → RAM pasa de 3072/3072 (100%) a 2048/3072 (67%), costo cero.
2. Desplegar La Platense en `olvidatasoft-002sjn` (pool .NET Core/64-bit, ya compatible con .NET 10) — sin costo adicional, no usar el margen liberado en el paso 1.
3. No comprar addon de RAM, no upgradear a Semi Ultimate, no abrir cuenta nueva ni mover nada a VPS todavía — ninguna alternativa se justifica hoy (todas salen peor en USD/MB que fusionar).
4. Confirmar si se borró `db_a7251f_eleven` (pendiente desde antes) para saber si BD queda en 17/20 o 18/20 tras sumar La Platense.

**⚠️ CORRECCIÓN 2026-07-30 (dato real de factura, reemplaza el precio de lista usado hasta ahora):** el precio publicado de Premium (USD 7,95/mes = USD 95,40/año) **no es lo que se paga en la práctica**. Joaquín confirmó la factura real de abril 2026: **USD 120/año por el plan Premium + USD 24/año por backup diario** (este último coincide exacto con el addon "DataBackup" de la tabla de precios). Total real de la cuenta actual: **USD 144/año**. Todos los cálculos de break-even y comparación de tiers de abajo estaban anclados en el precio de lista (95,40) — quedan corregidos con el precio real (120, sin contar el backup que es opcional/aparte).

**Descuento por compromiso multi-año (SmarterASP, confirmado por Joaquín 2026-07-30) — palanca no evaluada todavía:** 13% off si se contrata a 2 años, 30% off si se contrata a 3 años. Aplicado sobre el precio real de USD 120/año:
| Compromiso | Precio total | Efectivo USD/año | Ahorro vs. 1 año |
|---|---:|---:|---:|
| 1 año | 120 | 120,00 | — |
| 2 años (13% off) | 208,80 | 104,40 | 13% |
| 3 años (30% off) | 252,00 | 84,00 | 30% |

**Implicación directa: si se van a abrir cuentas Premium nuevas para escalar (ver plan de duplicar clientes más abajo), contratarlas a 3 años baja el costo efectivo de USD 120 a USD 84/año por cuenta — un ahorro real del 30% sin ninguna desventaja técnica**, siempre que haya confianza en seguir usando esa cuenta al menos 3 años (razonable dado el ritmo de crecimiento del negocio). **Confirmar con soporte de SmarterASP si el descuento aplica también a la renovación de la cuenta YA existente** (vence 06/04/2027) o solo a altas nuevas — no asumido todavía.

**Research real de TODOS los planes de SmarterASP (2026-07-30, vía WebFetch de smarterasp.net/hosting_plans y semi_dedi + whtop.com) — precios de lista recalculados con el precio REAL de Premium (120, no 95,40) — conclusión sin cambios: seguir apilando cuentas Premium, ningún tier superior es mejor negocio:**

| Plan | RAM total | $/año (lista) | $/MB-año |
|---|---|---|---|
| .NET Premium (W1050) — precio REAL confirmado | 3.072 MB | **120,00** | **0,0391** |
| Semi Basic (W2000) | 3.072 MB | 359,40 | 0,117 (3,0x peor) |
| Semi Advance (W2050) | 6.144 MB | 599,40 | 0,098 (2,5x peor) |
| Semi Premium (W2100) | 9.216 MB | 959,40 | 0,104 (2,67x peor) |
| Semi Ultimate (W2150) | 12.288 MB | 1.421,40 | 0,116 (2,96x peor) |

*Nota: los precios de los tiers Semi Dedicated son de lista (WebFetch), no confirmados contra factura real como Premium — es posible que también tengan una brecha lista-vs-real similar (+25,8%), pero no cambiaría la conclusión (Premium sigue siendo 2,5x-3x más barato por MB en cualquier escenario).*

El $/MB sigue empeorando cuanto más subís de tier — la conclusión no cambia con el precio real, solo el margen es un poco menor (2,5x-3x en vez de 3,1x-3,8x). **Para duplicar la base de clientes (~17→~34 sitios, ~18→~36 BD): abrir 3 cuentas Premium nuevas (total 4) a precio real de 1 año = USD 360/año adicionales (USD 480/año total) — o USD 252/año adicionales (USD 84×3) si se contratan a 3 años (30% off), total USD 336/año con las 4 cuentas si también se renueva la actual a 3 años.** Comparado contra Semi Ultimate (USD 1.421,40/año por la misma RAM, sin cupo de BD confirmado), la ventaja de apilar Premium se mantiene clara incluso al precio real. Nota aparte: la doc oficial dice "mínimo 512 MB por pool" para Premium, no confirma un máximo de 1024 MB — los 3 pools actuales están en 1024 MB por ser exactamente 3072÷3, no por un techo documentado; en teoría se podría resizear algún pool por debajo de 1024 MB para ganar margen sin abrir cuenta, pero es más riesgoso operativamente — no es la vía recomendada como plan principal.

**Precios de add-ons vigentes (SmarterASP, relevados 2026-07-30) — referencia para decisiones de escalado:**
- RAM extra: 256 MB = USD 60/año · 1 GB = USD 240/año (**con el precio real de cuenta nueva (120), el addon de RAM sigue siendo mal negocio: USD 0,234/MB-año vs. USD 0,0391/MB-año de cuenta nueva — 6,0x peor, no 7,5x como se calculó con el precio de lista, pero la conclusión no cambia: nunca conviene**).
- BD MySQL extra: USD 30/año · espacio extra BD: USD 30/GB/año. **Break-even BD recalculado con precio real: 120/30 = 4,0 — hasta 4 BD extra sobre el cupo de 20 conviene addon; más de 4, cuenta nueva** (antes se decía "hasta 3" con el precio de lista de 95,40/30≈3,18).
- SSL: Single domain USD 29/año · Multi-subdominio (wildcard) USD 169/año · Organization Validation USD 199/año · Extended Validation USD 199/año.
- Sitio extra: USD 25/año · Static IP: USD 60/año (VPS/Cloud) o USD 24/año (shared).
- Backup: DataBackup USD 24/año (= el que ya paga Joaquín) · SiteBackup USD 35,40/año · ServerBackup USD 120/año · CustomBackup (1 BD) USD 17,70/año.
- **Upgrade de plan evaluado (no ejecutado):** Premium → "Semi Ultimate .Net" (espacio/sitios/BD/email ilimitados, 12 GB de RAM) cuesta USD 1.421,40/año a precio de renovación completa, o USD 973,56 por los 250 días restantes del ciclo actual (≈USD 3,89/día). Sigue sin convenir frente a abrir cuentas Premium nuevas, incluso al precio real de 120/año.

## SSL — certificados Sectigo Positive (todos activos al 2026-07-30)

Vencimientos ordenados — **acción antes de octubre 2026** para los dos más próximos:
| Dominio | Vence | Urgencia |
|---|---|---|
| **virtualwallet.com.ar** | **30/08/2026** | 🔴 ~1 mes — renovar ya |
| **showroomgriffin.com.ar** | **29/09/2026** | 🟠 ~2 meses |
| contadoresbma.com.ar | 19/02/2027 | verde |
| deliciasnaturales.com.ar | 11/02/2027 | verde |
| recotrack.com.ar | 11/02/2027 | verde |
| vinoysefue.ar | 16/03/2027 | verde |
| belclau.com.ar | 05/04/2027 | verde |
| piapartments.es | 05/04/2027 | verde |
| elevenlaplata.com.ar | 05/04/2027 | verde |
| estanciasantarosa.com.ar | 08/05/2027 | verde |
| lab-ipac.com.ar (portal.lab-ipac.com.ar) | 19/06/2027 | verde |
| lumitrack.com.ar | 18/06/2027 | verde |
| conversor.contadoresbma.com.ar | 26/06/2027 | verde |
| olvidata.com.ar | 28/07/2027 | verde |
| marihogar.com.ar | 29/07/2027 | verde |

## Dominios nic.ar (todos delegados/registrados al 2026-07-30)

Vencimientos próximos a vigilar:
| Dominio | Vence | Urgencia |
|---|---|---|
| **virtualwallet.com.ar** | **13/09/2026** | 🔴 ~6 semanas — renovar |
| olvidata.com.ar | 18/10/2026 | 🟠 ~2,5 meses |
| recotrack.com.ar | 10/02/2027 | verde |
| deliciasnaturales.com.ar | 21/02/2027 | verde |
| vinoysefue.ar | 03/03/2027 | verde |
| showroomgriffin.com.ar | 16/04/2027 | verde |
| estanciasantarosa.com.ar | 08/05/2027 | verde |
| lumitrack.com.ar | 18/06/2027 | verde |
| lab-ipac.com.ar | 12/06/2027 | verde |
| marihogar.com.ar | 28/07/2027 | verde |

**virtualwallet.com.ar es el activo más urgente de toda la infraestructura: SSL vence 30/08/2026 y el dominio 13/09/2026, ambos en las próximas semanas.**

## Servidor DonWeb "Cloud Server" — infraestructura separada, NO documentada antes de este relevamiento

**DonWeb = Ferozo (confirmado por Joaquín, 2026-09-02) — es un único proveedor, no dos.** Los nameservers de `olvidata.com.ar` (`ns9/ns10.hostmar.com`) son infraestructura tecnica de backend de ese mismo proveedor, no un segundo proveedor distinto — no confundir "Hostmar" con una cuenta/contrato aparte.

Servidor Linux aparte de SmarterASP, usado para sitios de front/estáticos y reseller hosting (probablemente WordPress/PHP, a confirmar stack real por sitio):
- Plan Cloud Server, vence 05/01/2027, pago anual.
- Hardware: 2 vCPU (Intel Broadwell), ~1965 MB RAM total (590 MB usado), disco 57 GB (8,1 GB usado, 49 GB libres) — **máquina chica, con mucho margen de disco pero RAM ajustada** (1965 MB total es poco para un servidor con varios sitios + panel de reseller).
- Sitios alojados: bourdinbienesraices.com.ar · dunasvillage.ar · escaba.org.ar · lab-ipac.com.ar · olvidata.com.ar (5 sitios, todos "Activa").
- **Nota importante:** `lab-ipac.com.ar` y `olvidata.com.ar` aparecen TANTO acá (DonWeb/Ferozo) como en SmarterASP (portal.lab-ipac.com.ar / portal.olvidata.com.ar) — son subdominios distintos del mismo dominio raíz sirviendo cosas distintas (landing/marketing en DonWeb, aplicación en SmarterASP, confirmado por IP: `portal.olvidata.com.ar` resuelve a `208.98.35.232`, IP de SmarterASP — completamente distinta de la del sitio principal). Confirmar esta separación landing-vs-app antes de tocar cualquiera de los dos.

### Estructura real de `public_html` de `olvidata.com.ar` (relevado 2026-09-02, via zona DNS completa + listado de archivos)

El dominio principal (`olvidata.com.ar`, IP `168.197.50.202`) y varios subdominios/carpetas conviven mezclados en la raíz de `public_html`. Mapa confirmado:

- **`front`** (nueva, recién creada, todavía vacía): destino del nuevo build de Astro del sitio principal (olvidatasoft-new). Se creó una cuenta FTP dedicada `front@olvidata.com.ar` apuntando ahí — el plan es migrar el sitio principal a esta carpeta y despues apuntar el Document Root del dominio ahí (ver plan de migración abajo).
- **`bot`** (carpeta `crossfybot` en el filesystem, subdominio real `bot.olvidata.com.ar` en DNS, CNAME a `olvidata.com.ar`) — **confirmado por Joaquín: ya tiene su propia carpeta separada en `public_html`**, correctamente aislado. No tocar su ubicación.
- **`club`** (subdominio `club.olvidata.com.ar`, para el proyecto `kite-punta-lara`) — **NO tiene registro DNS todavía porque el proyecto no está en producción** (confirmado por Joaquín, no es un blocker ni un error, es el estado esperado mientras kite-punta-lara sigue en implementación).
- **`api`, `precios`, `productos`, `servicios`, `brand`** — NINGUNO tiene registro DNS propio → son carpetas sueltas colgando del docroot del dominio principal (resueltas como `olvidata.com.ar/precios`, etc.), NO subdominios aislados. Deben moverse/copiarse dentro de `front/` junto con el build de Astro antes de cambiar el Document Root, o se rompen (404) el día del cutover.
- **`webhook.olvidata.com.ar`** (solo un TXT `_acme-challenge`, sin A/CNAME visible) — Joaquín: "puede ser un certificado de seguridad o una redirección a SmarterASP" — **decisión: conservarlo, no tocar**, no vale la pena investigar más a fondo.
- **`portal.olvidata.com.ar`** — vive en SmarterASP (`208.98.35.232`), no en este servidor — no forma parte de esta reorganización.
- **Legado a archivar (no borrar todavía)**: `wp-includes` (rastro de WordPress, probablemente muerto), `tmpsite` (nombre típico de staging olvidado), `crossfybot_env.php` suelto en la raíz (debería vivir dentro de `bot/`, no en la raíz), `index.html`/`favicon.svg`/`robots.txt` viejos de la raíz (remanentes del front antes de la carpeta `front/`).
- **No tocar nunca**: `cgi-bin` (exigido por el panel en la raíz de toda cuenta).

**Plan de migración acordado con `olvidata-infra` (pendiente de ejecutar, sin fecha):**
1. Backup completo de `public_html` tal cual está hoy (no negociable, hay producción real conviviendo).
2. Subir el build de Astro completo a `front/` vía la cuenta FTP ya creada — riesgo cero, nada apunta ahí todavía.
3. Mover/copiar `api`, `precios`, `productos`, `servicios`, `brand` (y cualquier otra carpeta suelta que el front necesite servir en la raíz) adentro de `front/`.
4. Verificar que `front/` sirve completo antes de tocar el dominio principal (ideal: subdominio de prueba temporal).
5. Cutover: cambiar el Document Root del dominio principal de `public_html` a `public_html/front` (instantáneo, sin downtime si el paso 3 está completo).
6. Verificación post-cutover: `olvidata.com.ar` carga bien Y `bot`/crossfybot sigue andando sin cambios (no debería verse afectado, pero se confirma).
7. Archivar (no borrar) el legado listado arriba; borrar definitivo recién después de un tiempo prudencial sin problemas.

**Pendiente de confirmar (no bloqueante para arrancar el plan):** con qué panel exacto administra Joaquín este Cloud Server (cPanel/WHM, Plesk, otro) — dado que DonWeb/Ferozo es el proveedor, lo más probable es cPanel/WHM clásico, pero no se confirmó en vivo contra el panel.

## ⚠️ Relevamiento en vivo 2026-09-21 (vía MCP `smarterasp`, solo lectura — corrige el snapshot de arriba)

**16 sitios activos (cambiaron 2 desde el 2026-07-30):** `laslatas` ya no existe en la cuenta. Se sumaron `LaPlatense` (ferreterialaplatense.com.ar — **ya desplegada y con dominio propio**, no "pendiente de desplegar" como decía el snapshot anterior) y `AgentesIA` (agentes.olvidata.com.ar — **sitio nuevo, sin documentar en ninguna memoria hasta ahora**, confirmar con Joaquín qué es y agregarlo al inventario). `KoiDumplings` ya tiene dominio propio (portaldelinversor.com.ar), dejó de estar "sin dominio propio".

**Bases de datos: 16 activas** (bajó de 17), incluye `db_a7251f_laplaten` y `db_a7251f_agentes` nuevas. `db_a7251f_eleven` (la vieja marcada "a borrar" desde 2026-07-14) **sigue sin borrarse**. Con 16/20, cupo real hoy = 4 libres — la presión de "se agota en pocos meses" bajó respecto al snapshot anterior, pero sigue siendo el límite a vigilar en cada alta.

**No se pudo confirmar RAM real de pools ni fecha exacta de vencimiento de SSL/dominio** — el MCP de solo-lectura no expone agrupación por pool (no hay forma de saber si la fusión pendiente `002xdn`→`002` se hizo) ni fechas de expiración de certificado/dominio (solo un booleano `configurado`/`sin avisos`). Tampoco hay tool de FTP/cPanel para tocar el servidor DonWeb desde acá. **La cuenta de recursos del plan (`hosting_get_resource_usage`) devolvió `databaseCount: 44`, que no coincide con las 16 BD reales listadas — no confiar en ese campo, usar el listado directo.**

**Ningún cambio de infraestructura se ejecutó en esta pasada** — ver pendientes y por qué no se tocaron en [[project-hosting-sharding-smarterasp]] y en la trazabilidad del pedido del 2026-09-21.

### Actualización 2026-09-21 (respuestas de Joaquín + re-chequeo vía API)

1. **`AgentesIA` (agentes.olvidata.com.ar) identificado**: es el proyecto **"Olvidata Agentes Multi Rubro"** (`docs/olvidata-agentes-multirubro/`) — sitio 17 de la cuenta (contando La Platense), queda agregado al inventario activo.
2. **`laslatas`: confirmado sin ningún resto en el servidor.** Se verificó explícitamente `websites_list`, `databases_list`, `domains_list` y `ftp_list_users` — no aparece ningún sitio, BD, dominio ni usuario FTP con ese nombre. No hizo falta borrar nada (ya estaba completamente limpio, probablemente dado de baja en algún momento entre el 2026-07-30 y hoy sin quedar registrado en esta memoria).
3. **`KoiDumplings` con dominio propio confirmado**: `portaldelinversor.com.ar`, dnsStatus/sslStatus "configured".
4. **`db_a7251f_eleven` (la vieja, marcada para borrar desde 2026-07-14) ya no existe** — confirmado por `databases_list`: la cuenta bajó de 16 a 15 BD activas. **Cupo real hoy: 15/20, 5 slots libres** (mejor margen que el 16-17/20 de los snapshots anteriores).
5. **SSL de `virtualwallet.com.ar` renovado por Joaquín** — no se pudo re-verificar la fecha de vencimiento vía API (`ssl_get_status` solo devuelve datos del dominio tempurl por defecto del sitio, no del dominio custom mapeado; no expone fechas, solo un booleano `expirationWarning`). Se toma como confirmado por Joaquín directamente. **Sigue pendiente el dominio nic.ar de virtualwallet.com.ar (vencía 13/09/2026 según el snapshot viejo) — no mencionado en la confirmación, chequear aparte.**
6. **Fusión de pools — sigue sin ejecutarse**, no hay tool de API para mover un sitio entre application pools (`website_update_application_pool_runtime` solo cambia runtime/pipeline del pool propio de un sitio, no reasigna a otro pool). Es 100% manual en el panel. Pasos entregados a Joaquín:
   - Pool Manager (Control Panel V10 → Advance options → Pool Manager) → confirmar que la distribución de sitios por pool sigue igual a la última foto confirmada (2026-07-30: `olvidatasoft-002` con 8 sitios ASP.NET 4.x 32-bit, `olvidatasoft-002sjn` con 7 sitios .NET Core 64-bit, `olvidatasoft-002xdn` con solo `deliciasnaturales`).
   - Websites → `deliciasnaturales` → cambiar su Application Pool de `olvidatasoft-002xdn` a `olvidatasoft-002` (mismo runtime ASP.NET 4.x Integrated, mismo bitness 32-bit, sin reconfiguración adicional).
   - Guardar — IIS recicla el proceso de `deliciasnaturales` (downtime esperado: segundos, solo ese sitio, nadie más se toca).
   - Verificar `deliciasnaturales.com.ar` carga bien.
   - Volver a Pool Manager: `olvidatasoft-002xdn` en 0 sitios → eliminarlo/dejarlo en 0 MB. RAM de la cuenta pasa de 3072/3072 (100%) a 2048/3072 (67%), libera 1024 MB (un pool entero) para el próximo cliente que necesite aislamiento propio.
   - No se sabe si `LaPlatense` y `AgentesIA` (altas nuevas desde el último relevamiento) ya están en algún pool con margen o forzaron una redistribución — confirmar su pool actual en el mismo Pool Manager antes de dar la fusión por completa.

### Corrección 2026-09-21 (v2) — config real de los 3 pools pegada por Joaquín desde el panel + cruce contra el stack real de cada repo local

**`olvidatasoft-002xdn` NO se eliminó — sigue existiendo, vacío, y sigue consumiendo 1024 MB de la cuota.** Mi lectura anterior (que asumía que al no tener sitios el pool ya no contaba para la cuota) era incorrecta — **RAM real hoy: 3072/3072 MB (100%, SIN margen)**, no 2048/3072 como se había registrado antes. Config confirmada de los 3 pools (tal cual la ve Joaquín en el panel):

| Pool | Runtime | Bitness | RAM | Load User Profile | Sitios |
|---|---|---|---|---|---|
| `olvidatasoft-002` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | Disabled | belclau, deliciasnaturales, KoiDumplings, labipac, Lumitrack, OlvidataCRM, piapartments (7) |
| `olvidatasoft-002xdn` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | Disabled | **ninguno — vacío, pendiente de eliminar** |
| `olvidatasoft-002sjn` | .NET Core | 64-bit | 1024 MB | Disabled | AgentesIA, elevenlp, ganaderia, LaPlatense, MariHogar, RecoTrack, showroomgriffin, vinoysefue, VirtualWallet (9) |

**Hallazgo nuevo — 3 sitios de `olvidatasoft-002` están en el pool equivocado.** Se cruzó cada sitio de `002` contra el `TargetFramework` real de su `.csproj` en `C:/Sistemas/<repo>` (no contra metadata desactualizada):
- `deliciasnaturales` → `v4.7.2` (.NET Framework) — **correcto en `002`**.
- `Lumitrack` → `v4.7.2` (.NET Framework) — **correcto en `002`**.
- **`KoiDumplings` → `net10.0`, `OlvidataCRM` → `net10.0`, `labipac` → `net10.0` — LAS TRES SON .NET 10 (ASP.NET Core), están mal ubicadas en un pool "ASP.NET 4.x Integrated" 32-bit en vez de `002sjn` ("`.NET Core`" 64-bit, donde SÍ están correctamente los otros 9 sitios .NET 10 confirmados por csproj: VirtualWallet, RecoTrack, vinoysefue, elevenlp/Eleven, showroomgriffin, ganaderia, MariHogar, LaPlatense, AgentesIA).** Riesgo concreto, no solo prolijidad: un pool 32-bit de ASP.NET 4.x puede no tener instalado el hosting bundle de .NET Core en 32-bit — si el pool recicla o hay un redeploy, esos 3 sitios pueden fallar a arrancar (502.5) aunque hoy figuren "Active".
- `belclau` → **no es un sitio .NET, es WordPress/PHP** (confirmado por archivos `wp-admin`, `wp-config.php`, etc. en `C:/Sistemas/belclaunew`) — corre bajo IIS vía FastCGI, no depende del Managed Runtime del pool, así que convivir en `002` no lo rompe, pero es una mezcla rara (WordPress + .NET Framework en el mismo pool). No urgente, solo anotado.
- `piapartments` → no se encontró repo local en `C:/Sistemas` ni `ruta_repositorio` en su metadata (proyecto "cerrado") — no se pudo confirmar su stack real. Pendiente de confirmar con Joaquín si sigue necesitando estar activo.

**Plan de acción concreto (ninguno ejecutado — todo requiere el panel, no hay tool de API para mover sitios entre pools ni para borrar/editar un pool):**
1. **Eliminar `olvidatasoft-002xdn`** (vacío, cero sitios) → libera 1024 MB de inmediato. **Downtime: cero**, no hay nada corriendo ahí. RAM pasa de 3072/3072 (100%) a 2048/3072 (67%).
2. **Mover `KoiDumplings`, `OlvidataCRM` y `labipac` de `002` a `002sjn`** (coincide con su stack real, .NET 10) — uno por uno, en horario de baja carga. **Downtime: segundos por sitio** (recycle individual al cambiar de pool), no afecta a los demás sitios del pool de origen ni destino. Pool `002` queda en 4 sitios (belclau, deliciasnaturales, Lumitrack, piapartments), `002sjn` en 12.
3. **(Recomendado, no urgente) Habilitar "Load User Profile" en `002sjn`** — los 9 (pronto 12) sitios son ASP.NET Core con cookies de sesión/antiforgery vía Data Protection API; con Load User Profile deshabilitado, las claves de cifrado no persisten de forma confiable entre reciclados de pool → cada recycle puede desloguear a todos los usuarios activos o invalidar tokens. **Downtime: recicla TODO el pool de una sola vez** (los 12 sitios simultáneamente, no uno por uno) — hacerlo recién después del paso 2, en horario de bajísimo tráfico, no antes (para no reciclar el pool dos veces). Para `002` no es urgente (ASP.NET Framework usa `machineKey` a nivel de máquina por defecto, no depende tanto del perfil de usuario).
4. Confirmar con Joaquín si `piapartments` sigue activo/necesario (repo no encontrado localmente) antes de tocar nada de `002`.

**Resultado esperado tras 1+2:** RAM 2048/3072 MB (67%), 1024 MB libres para el próximo pool aislado; `002` con 4 sitios bien tipados (3 .NET Framework/PHP), `002sjn` con 12 sitios .NET Core, todos donde corresponde por stack real.

### Decisión 2026-09-21 (v3) — Joaquín NO borra `002xdn`: lo usa como pool dedicado para el portal Agentes IA

**Cambia el paso 1 del plan de arriba: no se borra `002xdn`.** Se reconfigura y se usa como pool aislado para `AgentesIA` (agentes.olvidata.com.ar, proyecto `docs/olvidata-agentes-multirubro/`, repo `C:\Sistemas\Olvidata Agentes Multi-rubro`, stack real confirmado: ASP.NET Core .NET 10 + EF Core + MySQL, `OlvidataAgentes.Web`). Stack revisado contra el repo y `docs/deploy-smarterasp.md`:

- **Data Protection ya persiste a filesystem** (`Program.cs`: `AddDataProtection().PersistKeysToFileSystem(ContentRoot/keys)`) — **no depende de Load User Profile**, a diferencia del caso genérico de VirtualWallet/RecoTrack/etc. en `002sjn` (que sí quedó recomendado habilitarlo, ver más arriba). Para `002xdn` no hace falta tocar ese switch.
- **Hallazgo de secretos — `website_list_environment_secrets` confirmó `"scope": "application-pool"`: las variables de entorno son del POOL, no del sitio.** El listado actual de `AgentesIA` (hoy en `002sjn`) devuelve 16 secretos, **incluyendo uno de RecoTrack** (`ConnectionStrings__RecoTrackMySql`) — confirma que los 9 sitios de `002sjn` comparten un mismo pool de variables de entorno visibles entre todos (mala higiene de secretos, aparte del tema RAM). De los 4 que `deploy-smarterasp.md` dice que Agentes IA necesita (`Anthropic__ApiKey`, `ConnectionStrings__DefaultConnection`, `Olvidata_Email__Smtp__Password`, `Seed__SuperUser__Password`), **solo `Olvidata_Email__Smtp__Password` aparece en el pool actual** — los otros tres no están como env var del pool, así que deben estar escritos directo en `appsettings.Production.json` en el servidor (no confirmado, preguntar a Joaquín antes de mover).

**Pasos concretos en el panel (en este orden):**
1. `Pool Manager` → `olvidatasoft-002xdn` → **"Change to .Net Core"** (hoy está en ASP.NET 4.x Integrated). Pool vacío, downtime cero.
2. Mismo pool → **cambiar a 64-bit** (hoy 32-bit; el .NET 10 real corre en 64-bit, igual que `002sjn`). Downtime cero, sigue vacío.
3. Dejar **Load User Profile en Disabled** (no hace falta para este sitio, ver arriba).
4. **Antes de mover el sitio:** cargar en `002xdn` → Environment Variables los mismos 4 secretos que usa hoy (`Anthropic__ApiKey`, `ConnectionStrings__DefaultConnection`, `Olvidata_Email__Smtp__Password`, `Seed__SuperUser__Password`) — **confirmar primero con Joaquín si los 3 que no aparecen en el pool viejo están en `appsettings.Production.json` del servidor** (en ese caso no hace falta cargarlos como env var, alcanza con que ese archivo siga en el sitio tras el move) o si hay que agregarlos como variable nueva.
5. `Websites` → `AgentesIA` → cambiar su Application Pool de `002sjn` a `002xdn`. **Downtime: segundos** (recycle de ese sitio solo; los otros 8 sitios de `002sjn` no se tocan, sus env vars de pool quedan intactas).
6. Verificar: `agentes.olvidata.com.ar` carga, `/health` OK, login funciona, revisar `Logs/arranque-*.log` por si falta alguna clave.

**Impacto en RAM: con esta decisión, `002xdn` deja de estar libre — RAM queda en 3072/3072 MB (100%, sin margen), no se libera nada.** El paso "mover `KoiDumplings`/`OlvidataCRM`/`labipac` de `002` a `002sjn`" (plan v2, más arriba) **sigue vigente y ahora es más importante**: es la única acción de costo cero que queda para sacar esos 3 sitios de un pool 32-bit que no les corresponde, ya que no va a quedar ningún pool de reserva para aislar nada más sin pagar (addon de RAM o cuenta nueva).

### Ejecutado y verificado 2026-09-21 (v4) — move de AgentesIA a `002xdn` confirmado OK

Joaquín ejecutó los pasos 1-5 (pool reconfigurado, secretos confirmados **en `appsettings.Production.json` del servidor, no como env var** — no hacía falta cargar nada en el pool nuevo, no se perdió nada) y movió `AgentesIA` de `002sjn` a `002xdn`. Verificación hecha desde acá (paso 6):

- `website_get_application_pool_settings(site-1884659)` → **`bitness: 64`, pool configurado, 1024 MB** — confirmado .NET Core 64-bit como se pidió.
- `https://agentes.olvidata.com.ar/` → 200. `https://agentes.olvidata.com.ar/health/vivo` → 200 (tardó ~7,7s la primera vez, esperable sin AlwaysRunning — PA-07 del proyecto sigue abierto, no es un problema nuevo). `/health` → 302 (redirige a login, esperable: es un endpoint autenticado, no un error).
- `website_get_logs(site-1884659)` → solo dos entradas de actividad de hosting (`changepool Running` / `changepool Success`), sin errores. No se pudo leer `Logs/arranque-*.log` de la app (son archivos del sitio, no expuestos por este MCP de solo-lectura) — si Joaquín quiere el chequeo más fino de `ValidacionArranque`, hay que mirarlo por FTP/panel directamente.

**Distribución de pools final (2026-09-21):**
| Pool | Runtime | Bitness | RAM | Sitios |
|---|---|---|---|---|
| `olvidatasoft-002` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | belclau, deliciasnaturales, KoiDumplings, labipac, Lumitrack, OlvidataCRM, piapartments (7) — **KoiDumplings/OlvidataCRM/labipac siguen mal ubicados, ver plan v2 arriba, sigue pendiente** |
| `olvidatasoft-002sjn` | .NET Core | 64-bit | 1024 MB | elevenlp, ganaderia, LaPlatense, MariHogar, RecoTrack, showroomgriffin, vinoysefue, VirtualWallet (8) |
| `olvidatasoft-002xdn` | .NET Core | 64-bit | 1024 MB | AgentesIA (1) |

RAM: **3072/3072 MB (100%, sin margen)** — los 3 pools están al tope de RAM y todos con sitios adentro, no queda ningún pool libre para un cliente nuevo. **Pendiente real más urgente de infraestructura hoy: mover `KoiDumplings`, `OlvidataCRM` y `labipac` a `002sjn`** (gratis, corrige el stack mal ubicado) — es la única palanca que queda sin pagar; después de eso, cualquier cliente nuevo que necesite pool propio ya implica addon de RAM o cuenta nueva.

### Ejecutado y verificado 2026-09-21 (v5) — move de KoiDumplings/OlvidataCRM/labipac confirmado OK, plan de fusión CERRADO

Joaquín movió los 3 sitios de `002` a `002sjn`. Verificado desde acá:
- `website_get_application_pool_settings` de los 3 (`KoiDumplings` site-1857210, `OlvidataCRM` site-1860209, `labipac` site-1846587) → **`bitness: 64`, `runtime: no-managed-code`** (.NET Core) — quedaron bien tipados.
- `website_get_logs` de los 3 → solo `changepool Success`, sin errores.
- Dominios productivos: `portaldelinversor.com.ar` (KoiDumplings), `portal.olvidata.com.ar` (OlvidataCRM), `portal.lab-ipac.com.ar` (labipac) → **los 3 responden 200**.
- **Bonus confirmado de paso:** `loadUserProfile: true` en los 3 y también en `VirtualWallet` (chequeado aparte) — **`002sjn` ya tiene Load User Profile habilitado** (la recomendación de la sección anterior ya se aplicó, no quedó pendiente).

**Distribución de pools FINAL (2026-09-21, cierra el plan de fusión/reubicación iniciado el 2026-07-14):**
| Pool | Runtime | Bitness | RAM | Load User Profile | Sitios |
|---|---|---|---|---|---|
| `olvidatasoft-002` | ASP.NET 4.x Integrated | 32-bit | 1024 MB | Disabled | belclau (WordPress/PHP), deliciasnaturales, Lumitrack, piapartments (4) |
| `olvidatasoft-002sjn` | .NET Core | 64-bit | 1024 MB | **Enabled** | AgentesIA no — ver abajo; KoiDumplings, OlvidataCRM, labipac, elevenlp, ganaderia, LaPlatense, MariHogar, RecoTrack, showroomgriffin, vinoysefue, VirtualWallet (11) |
| `olvidatasoft-002xdn` | .NET Core | 64-bit | 1024 MB | Disabled | AgentesIA (1) |

RAM sigue en 3072/3072 MB (100%, sin margen — sin cambios, esto solo reubicaba sitios, no liberaba pools). **No queda ninguna acción de infraestructura pendiente sin costo.** Todo lo que sigue (sumar un cliente nuevo con pool propio, más BD, etc.) ya requiere addon o cuenta nueva — ver regla de break-even en [[project-hosting-sharding-smarterasp]]. Únicos pendientes reales que quedan abiertos, no de infraestructura de pools: confirmar stack de `piapartments` (repo no encontrado localmente) y el vencimiento del dominio nic.ar de virtualwallet.com.ar (13/09/2026 según snapshot viejo, no confirmado si Joaquín ya lo renovó junto con el SSL).

## Why (por qué importa este documento)

Antes de este relevamiento, la única memoria de infraestructura era [[project-hosting-sharding-smarterasp]], enfocada solo en la cuenta SmarterASP y su techo de RAM/BD. No existía registro de: el servidor DonWeb separado, el inventario completo de SSL con vencimientos, ni los dominios nic.ar con sus fechas. Cualquier decisión de arquitectura (dónde poner un cliente nuevo, cuándo escalar, qué certificado renovar) necesita este cuadro completo, no solo la parte de SmarterASP.

## How to apply

Usar este documento como snapshot base para el agente `olvidata-infra` (ver `~/.claude/agents/olvidata-infra.md`) y para cualquier análisis de capacidad, costo o riesgo de infraestructura. **Es un snapshot de un momento dado (2026-07-30) — antes de tomar una decisión real (ej. dónde desplegar La Platense), confirmar con Joaquín si hay altas/bajas de sitios o BD desde esta fecha, y si la RAM de los pools sigue en el estado del 2026-07-14 o cambió.** Actualizar este documento cada vez que se haga un relevamiento nuevo del panel de hosting, no dejar que se desactualice silenciosamente.

### Baja belclau — 2026-09-21

- **Sitio `belclau` (WordPress/PHP, pool `olvidatasoft-002`) eliminado de SmarterASP** por baja del servicio del cliente. BD `db_a7251f_bcnew_1` (MYSQL5049.site4now.net) incluida en la baja.
- **Resguardo interno (solo Joaquín)** en `C:/Sistemas/_backups/belclau/2026-09-21/`: `db/db_a7251f_bcnew_1.sql` (mysqldump completo, 38 MB, 22 tablas) + `sitio/` (13.119 archivos, 5,15 GB: uploads, themes, plugins y 6 `.wpress` de All-in-One WP Migration, el último del 31/08/2026 con el sitio entero). Faltaron 11 carpetas de código WordPress/plugins + cache google-fonts (reconstruibles, sin contenido del cliente).
- Pool `002` queda con un sitio menos (sin impacto en RAM: la cuota es por pool, no por sitio). Pendiente: decidir qué hacer con el dominio `belclau.com.ar` (vence 05/04/2027) y su correo si lo tuviera.
- Aprendizaje operativo: el FTP de SmarterASP (IIS) no soporta MLSD y corta conexiones en descargas largas — para backups grandes usar descarga con reconexión y resume; la API MCP de alta/rotación de usuarios FTP falló 5 veces (`ftp_user_create_failed`).
