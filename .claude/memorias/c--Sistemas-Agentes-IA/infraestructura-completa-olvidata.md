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

## Why (por qué importa este documento)

Antes de este relevamiento, la única memoria de infraestructura era [[project-hosting-sharding-smarterasp]], enfocada solo en la cuenta SmarterASP y su techo de RAM/BD. No existía registro de: el servidor DonWeb separado, el inventario completo de SSL con vencimientos, ni los dominios nic.ar con sus fechas. Cualquier decisión de arquitectura (dónde poner un cliente nuevo, cuándo escalar, qué certificado renovar) necesita este cuadro completo, no solo la parte de SmarterASP.

## How to apply

Usar este documento como snapshot base para el agente `olvidata-infra` (ver `~/.claude/agents/olvidata-infra.md`) y para cualquier análisis de capacidad, costo o riesgo de infraestructura. **Es un snapshot de un momento dado (2026-07-30) — antes de tomar una decisión real (ej. dónde desplegar La Platense), confirmar con Joaquín si hay altas/bajas de sitios o BD desde esta fecha, y si la RAM de los pools sigue en el estado del 2026-07-14 o cambió.** Actualizar este documento cada vez que se haga un relevamiento nuevo del panel de hosting, no dejar que se desactualice silenciosamente.
