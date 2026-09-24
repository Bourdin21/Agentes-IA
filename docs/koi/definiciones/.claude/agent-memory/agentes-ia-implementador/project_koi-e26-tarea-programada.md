---
name: koi-e26-tarea-programada
description: KOI — la actualización diaria de "Mes actual" necesita cinco pasos de puesta en marcha (script, clave, deploy, tarea programada) y con cuatro de cinco no funciona; además queda una decisión del dueño sobre inferencia A/B
metadata:
  type: project
---

En KOI, el ítem 3 del sprint "Fixes y mejoras" (commit `e7c24d8`, 2026-09-23) dejó la actualización diaria de la pantalla "Mes actual" **implementada pero sin poner en marcha**. Son **cinco pasos y todos son obligatorios**: (1) correr `E26_ventas_diarias_cache.sql`, (2) cargar `Integraciones:ApiKey` en `appsettings.Production.json` (gitignoreado), (3) deployar, (4) dar de alta la tarea programada diaria en el panel de SmarterASP, (5) probarla. El script y las instrucciones quedaron en el scratchpad de esa sesión.

**Why:** el pool de SmarterASP se apaga por inactividad a los 20 minutos (log de IIS del 2026-09-22), así que el disparo de la sincronización **tiene que venir de afuera** — no hay temporizador interno que valga, y ya se descartó explícitamente. Con cuatro de los cinco pasos, la pantalla no se rompe pero tampoco se actualiza: sólo muestra el cartel de "dato desactualizado" después de 26 h. Además **no está verificado** que el panel de SmarterASP permita POST con header propio; si sólo hace GET pelado, la alternativa documentada es una tarea de tipo batch con `curl` — y la clave **nunca** va en la query string (quedaría en los logs de IIS y en el historial del panel).

**How to apply:** antes de tocar "Mes actual", `VentasDiariasCache` o cualquier cosa de la integración con Ayres, confirmar si E26 ya está aplicada (buscar `20260923184512_E26_VentasDiariasCache` en `__EFMigrationsHistory`) y si la tarea programada ya existe. Y si el tema es el barrido legal E1: **quedó una decisión de negocio abierta del dueño** — Ayres informa el lado A, la tarjeta "Ventas Totales" de esa misma pantalla es A + B, así que un Inversor puede deducir B por diferencia sumando las barras a mano. No hay etiqueta ni endpoint que exponga el corte, pero la inferencia existe y las tres salidas posibles están anotadas en `5-implementador.md` → Pendientes. No implementarla por cuenta propia.

Ver también [[koi-e25-pendiente]] y [[implementador-solo-commitea-repo-de-codigo]].
