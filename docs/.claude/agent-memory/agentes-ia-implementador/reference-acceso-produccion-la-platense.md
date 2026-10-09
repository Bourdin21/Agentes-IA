---
name: reference-acceso-produccion-la-platense
description: Como se lee la base de produccion de La Platense sin FTP, y que la password de FTP/Web Deploy de credenciales.local.md no autentica (2026-10-07)
metadata:
  type: reference
---

**La base de produccion de la-platense se puede leer directo desde la maquina de Joaquin.** La
cadena vive en `FerreteriaLaPlatense.Web/appsettings.Production.json` (host
`mysql8001.site4now.net`, base `db_a7251f_laplaten`) y el cliente `mysql.exe` esta en
`C:/Program Files/MySQL/MySQL Server 8.0/bin/`. Conecta y permite `SELECT` y `mysqldump`. Eso hace
que **medir el estado real de produccion no dependa del panel ni del FTP** — es el camino que
desbloqueo el ensayo de `LP-050`. Limitacion conocida: el usuario **no tiene privilegio para
`show events`**, asi que `mysqldump` va sin `--events` (ver
[[feedback-exit-code-de-herramienta]]).

**La password de FTP / Web Deploy de `C:/Sistemas/Agentes-IA/docs/credenciales.local.md` NO
autentica.** El 2026-10-07 el FTP de `win8232.site4now.net` devolvio `530 User cannot log in.` para
`olvidatasoft-002`, con y sin TLS explicito. El usuario root del plan existe y esta `Active`
(verificado con `ftp_list_users` del MCP de SmarterASP), asi que lo que esta mal es la password —
**probablemente rotada**.

**How to apply:** antes de cualquier deploy de la-platense (o de otro sitio de la misma cuenta
reseller), confirmar esa credencial con Joaquin: **Web Deploy usa la misma**, asi que el problema no
bloquea solo la bajada de un backup, bloquea el deploy del sitio. Si hay que leer o respaldar la
base, no hace falta esperar a eso: se usa `mysqldump` directo, que ademas es evidencia mas
verificable que un backup generado desde el panel.
