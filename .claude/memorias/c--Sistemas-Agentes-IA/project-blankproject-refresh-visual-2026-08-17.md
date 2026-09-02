---
name: project-blankproject-refresh-visual-2026-08-17
description: Actualizacion visual del template BlankProject (fuentes/iconos self-hosted, tema oscuro completo) tras comparar contra la-platense en produccion
metadata:
  type: project
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-08-18T02:15:22.554Z
---

El usuario actualizo el stack de `olvidata.com.ar` (Astro 4→7, fuentes self-hosted via `@fontsource/inter`, iconos SVG en vez de FontAwesome CDN, GSAP, "cero requests a CDN externos") y pidio portar el mismo esquema visual al template `blankproject` (`C:\Sistemas\blankproject`, repo base de todo proyecto MVC nuevo del estudio).

**Decision de alcance (no 1 a 1):** porta directo fuentes/iconos self-hosted (bajo riesgo, mismo objetivo). NO porta GSAP/scroll-reveal/canvas (patron de sitio de marketing, inapropiado para admin/CRUD — la app ya tiene microinteracciones CSS puras suficientes). NO porta View Transitions/SPA nav (especifico de la arquitectura de islas de Astro, no aplica a MVC full-page-reload — requeriria adoptar htmx/Turbo, decision de arquitectura aparte).

**Mid-turn el usuario agrego:** comparar BlankProject contra `la-platense` (Ferreteria La Platense, en produccion real: https://ferreterialaplatense.com.ar/) y actualizar Blank si estaba atrasado. La comparacion revelo que un merge previo (2026-07-30, ver `docs/blankproject/definiciones/5-implementador.md` del propio repo blankproject) ya habia traido la entidad `PreferenciaUsuario` y el helper `ArgentinaTime`, pero **nunca se completo el wiring del tema oscuro** (faltaba el bloque CSS `[data-theme="dark"]`, el boton toggle, el action `ToggleTema` del controller) — un feature a medio portar que nadie habia notado.

**Que se implemento (todo en `C:\Sistemas\blankproject`, verificado con `dotnet build` → 0 errores):**
- Fuentes Inter self-hosted (`wwwroot/fonts/inter/*.woff2` + `wwwroot/css/fonts.css`), reemplaza Google Fonts CDN.
- Font Awesome 6.5.1 self-hosted (`wwwroot/lib/fontawesome/`), reemplaza cdnjs CDN. Cero cambio de markup.
- Tema oscuro completo: CSS dark portado de la-platense, `data-theme` en `<html>`, boton toggle sol/luna, `AccountController.ToggleTema()`, aplicacion de preferencia al login, CSRF meta tag.
- Fix ortografia "Exito"→"Éxito" (violaba la propia regla del estudio de Agosto 2026) y "Iniciar sesion"→"Iniciar sesión".
- 2 usos residuales de `DateTime.Now` corregidos a `ArgentinaTime.Now` (quedaban del merge de julio sin corregir).
- `Home/Index.cshtml` con estructura visual mejorada (icono de marca, jerarquia).

**Documentado en:** `.github/instructions/25-frontend-design-system.instructions.md` (secciones "Fuentes e iconos self-hosted" y "Tema oscuro"), `.github/instructions/10-blankproject-base.instructions.md` (ArgentinaTime como bug/patron conocido del template, junto a los otros 2 ya documentados), `docs/patrones/catalogo.yml` (PAT-009 tema oscuro, PAT-010 ArgentinaTime), y la memoria propia del repo blankproject (`docs/blankproject/definiciones/5-implementador.md`).

**Pendiente (no se hizo, requiere el usuario):** levantar la app y verificar visualmente el toggle de tema y el render de fuentes/iconos — el Implementador nunca hace smoke test (regla del estudio), solo verifico build limpio. Relacionado: [[project-agentes-ia-mejoras-2026-08-15]].
