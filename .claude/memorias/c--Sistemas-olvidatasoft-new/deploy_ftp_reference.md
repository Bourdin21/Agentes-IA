---
name: deploy-ftp-reference
description: "Cómo y con qué se deployea olvidata.com.ar a producción (Ferozo/DonWeb, FTP)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8baa4f43-f54f-4a16-b7cc-d5afd45dc06c
  modified: 2026-08-18T01:43:17.029Z
---

El deploy de olvidata-web (sitio Astro estático) a producción es manual por FTP a hosting Ferozo/DonWeb (OpenLiteSpeed, Alma Linux 8). Ver `MANUAL-DEPLOY.md` en la raíz del repo para el flujo completo documentado para humanos.

**Para deployar desde un agente:** correr `scripts/deploy.sh` desde la raíz del proyecto (`c:\Sistemas\olvidatasoft-new`). Ese script:
1. Corre `npm run build`
2. Sube el contenido de `dist/` a `public_html/` en el servidor vía FTP
3. Verifica que `/`, `/precios/`, `/productos/`, `/servicios/` respondan 200 en `https://olvidata.com.ar`

**Credenciales**: viven en `.env.deploy` en la raíz del proyecto (gitignoreado vía el patrón `.env.*` — nunca se commitea). Ese archivo NO está en este sistema de memoria a propósito: es un secreto de producción, no contexto de negocio. Si `.env.deploy` no existe (proyecto clonado de nuevo, o se perdió), hay que pedirle al usuario las credenciales del panel Ferozo — no reconstruirlas ni inventarlas.

**Nota de la cuenta FTP**: el hosting es compartido — el mismo login FTP (`ftp@olvidata.com.ar`) tiene acceso a otras carpetas ajenas al sitio (`crossfybot/`, `wp-includes/`, `mail/`, etc. en la raíz del FTP, fuera de `public_html/`). El deploy solo debe tocar `public_html/` — nunca subir ni tocar esas otras carpetas.
