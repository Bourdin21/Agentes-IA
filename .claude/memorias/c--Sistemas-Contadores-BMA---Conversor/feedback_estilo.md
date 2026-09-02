---
name: feedback estilo conversor-bma
description: Preferencias y correcciones del usuario para este proyecto
type: feedback
originSessionId: 38a0ef0f-ff90-48d7-91ef-6284ce35c41d
---
Logo OlvidataSoft: usar siempre `C:\Sistemas\olvidatasoft-new` como fuente de verdad, nunca recrear a mano.  
**Why:** El usuario tiene el logo original en ese proyecto y cualquier recreación manual queda inexacta.  
**How to apply:** Antes de usar cualquier logo de OlvidataSoft, copiar el SVG directamente desde `C:\Sistemas\olvidatasoft-new\public\brand\`.

Patrón de footer: usar la estructura HTML `ov-footer` / `ov-footer-inner` / `ov-footer-links` con isotipo SVG + texto `Olvidata<strong>Soft</strong>`, igual al nav de olvidatasoft-new.  
**Why:** El usuario tiene un sistema de diseño consistente entre proyectos.  
**How to apply:** Copiar el patrón del Navbar.astro de olvidatasoft-new (font Inter 600/700, color #1e293b / #2B9DE4).
