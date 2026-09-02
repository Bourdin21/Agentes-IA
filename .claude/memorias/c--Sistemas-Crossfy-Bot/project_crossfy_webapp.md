---
name: project-crossfy-webapp
description: "Crossfy Bot webapp PHP — auth, panel admin, catálogo semanal, auto-sync. En bot.olvidata.com.ar."
metadata: 
  node_type: memory
  type: project
  originSessionId: 4de4e628-1d36-481a-ae5c-d51c92adf6bf
---

Webapp PHP en `webapp/` corriendo en bot.olvidata.com.ar (o /crossfybot en otro host).
BoxId Meetbox: 966. DB MySQL olvidata_soft en DonWeb.

## Crossfy API (base: https://www.crossfyapp.com/api/)
- Auth token: `GET /token?email=E&password=P&boxId=966`
- Header: `X-Token: <token>`
- Clases: `GET /clases?&fechaDesde=DD/MM/YYYY`
- Detalle: `GET /detalleClase/{id}`
- Reservar: `POST /turnos/clase/{id}/reserva`
- Lista espera: `POST /clase/{id}/listaEsperaClase`

## Auth (actualizado 2026-06-02)
- Login/registro usa directamente las credenciales de Meetbox (email + contraseña de la app Crossfy). Sin cuenta separada.
- `users.email` = crossfy_email (mismo campo desde migración v2).
- `users.password_hash` = bcrypt de la contraseña Crossfy (validación local rápida).
- Nuevos registros: `approved=0`. Admin aprueba desde `/admin.php`.
- Se eliminó el sistema GitHub authorized.json → reemplazado por `users.approved`.

## Panel de administración
- `admin.php` + `api/admin.php` — solo accesible si `users.is_admin=1`.
- Acciones: aprobar, activar/desactivar, dar/quitar admin.
- Para primer admin: `migrate.php?key=MeetboxMigrate2026&admin_email=tu@email.com`.

## Catálogo semanal
- `api/weekly.php:refreshCatalog()` arranca desde el lunes de la semana actual (cubre todos los días Lun-Sáb aunque ya pasaron).
- Fetch de 14 días (2 semanas) para cubrir el ciclo completo.

## Auto-sync tras acciones
- Cada mutación (agregar/toggle/eliminar clase) envuelve el fetch en `withSync(fn)`.
- Muestra toast "Guardando…" → "✓ Guardado" por 2.5s.

## Archivos clave
- `webapp/migrate.php` — migraciones (v1: token_cache, waitlist; v2: approved, is_admin)
- `webapp/config.php` — DB, cifrado, getAuthorizedEmails (DB-based), isAdmin, requireAdmin
- `webapp/api/auth.php` — login/register/logout/change-password
- `webapp/api/admin.php` — CRUD usuarios (protegido requireAdmin)
- `webapp/admin.php` — UI panel admin
- `webapp/api/weekly.php` — catálogo semanal + sync
- `webapp/cron/scheduler.php` — motor reservas, filtro AND u.approved=1

## Deployment
- Servidor: DonWeb, subdomain bot.olvidata.com.ar → public_html/crossfybot/
- Cron cada 5 min: `curl -sk "https://olvidata.com.ar/crossfybot/run_scheduler.php?key=BotRun2026"`
- Archivo env externo: `public_html/crossfybot_env.php` (fuera de la carpeta del bot)

**Why:** El usuario quería control total sobre quién usa el bot (aprobación manual), login simplificado con las mismas credenciales de Meetbox, y agenda cargada para toda la semana.
**How to apply:** Cambios de auth deben respetar: validar con Crossfy API → guardar → approved=0 → admin aprueba → usuario puede ingresar.
