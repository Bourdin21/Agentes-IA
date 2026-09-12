# Plan de refactorización del frontend del CRM

**Fecha:** 2026-09-09 · **Estado:** propuesta, pendiente de aprobación (no se implementó nada todavía)

Origen: aplicar al CRM las mejoras del agente `implementador-astro-front`, que se actualizó **hoy**
con 23 reglas nuevas (AG-01..AG-13 "se copia", AG-N1..AG-N10 "no se copia") derivadas de un estudio
medido de `antigravity.google` (Playwright + Lighthouse + axe, evidencia en
`docs/referencia/antigravity-google.md`).

---

## 1. Triage: qué transfiere de Astro a un CRM MVC, y qué no

El agente Astro construye **sitios institucionales estáticos**. El CRM es una **herramienta interna
de uso diario, con backend, sesión y datos**. Aplicar sus reglas en bloque sería cargo-cult, así que
lo primero es separar.

### Transfiere (son reglas de frontend, no de Astro)

| Regla | Por qué aplica igual acá |
|---|---|
| **AG-02** — tokens de 2 niveles (`--palette-*` crudo → `--theme-*` semántico) | El CRM ya tiene tema claro/oscuro por cookie `crm-tema`. Es exactamente el problema que los tokens semánticos resuelven. |
| **AG-N10** — no cargar maquinaria que no se usa | El hallazgo más grande del relevamiento (ver §2). |
| **AG-N9** — nada clickeable sin acceso por teclado | Herramienta de uso diario intensivo; hay violaciones reales. |
| **AG-N6** — cache largo en assets con hash | `asp-append-version` ya genera el hash; falta la cabecera. |
| **AG-N1** — evitar el peso de las fuentes de iconos | FA ya está self-hosted (09-04), pero sigue siendo icon font. |
| **AG-01** — selectores de comportamiento por `data-*`, no por clase | Desacopla estilo de JS; el CRM mezcla las dos cosas hoy. |
| **AG-12** — movimiento de hover chico, transiciones 150-200 ms | Escala de referencia para no sobre-animar una herramienta de trabajo. |
| **AG-N5** — dropdowns/modales cierran con `Escape`, `aria-expanded` sincronizado | Aplica a los `collapse`/modales propios. |
| **AG-N4** — foco visible ≥3:1, `:focus-visible` separado de `:hover` | Uso intensivo de teclado. |
| Cards: **jerarquía por estilo, no por tamaño** | Aplica a las grillas de cards del panel. |

### No transfiere (y por qué)

| Regla | Motivo |
|---|---|
| **ScrollSmoother** (AG-08..AG-11) | Alto riesgo declarado por el propio agente, y **secuestrar el scroll en una herramienta de trabajo es directamente malo** — el usuario navega listados largos todo el día. Excluido a propósito, no por falta de tiempo. |
| **AG-03** (facade de video), **AG-05** (SplitText accesible), **AG-N7** (Three.js), **AG-N8** (cursor propio) | El CRM no tiene video de terceros, ni texto animado, ni fondos 3D, ni cursor custom. N/A. |
| **AG-06** (canvas con IntersectionObserver) | El único `<canvas>` es un gráfico de datos (Chart.js), no un fondo decorativo. |
| **AG-07** (detección de entorno) | Pantallas detrás de login, sin CTA público. |
| **Reveal-on-scroll / tilt 3D / botones magnéticos** | Son recursos de sitio de marketing. En una pantalla operativa agregan ruido y latencia percibida sin aportar nada. |
| **Content Collections, View Transitions de Astro, deploy FTP** | Específicos del stack Astro. |

> **Excepción a evaluar:** la **View Transitions API nativa** (`@view-transition { navigation: auto }`)
> sí funciona en navegación MVC same-origin en Chromium, sin JS ni librería. Es la única idea de la
> sección "navegación client-side" que transfiere, y cuesta 3 líneas de CSS. Va como ítem opcional.

---

## 2. Hallazgos medidos sobre el CRM (2026-09-09)

Todo medido, no estimado.

### 2.1 · 615 KB de librerías en cada pantalla, 74% para pantallas que no las usan

`_Layout.cshtml` carga 12 assets de terceros en **las 48 vistas**, sin importar cuál se abra:

| Librería | Peso | Vistas que la usan | Desperdicio |
|---|---|---|---|
| Chart.js | 200,4 KB | 3 de 48 | 94% |
| DataTables (js+css+tema) | 99,4 KB | **1 de 48** | 98% |
| Select2 (js+css+tema bs5) | 117,8 KB | 4 de 48 | 92% |
| daterangepicker + moment | 90,3 KB | 3 de 48 | 94% |
| SweetAlert2 | 106,8 KB | 13 de 48 | 73% |
| **Total** | **614,8 KB** | | **457,7 KB (74%) es para libs de ≤4 vistas** |

`moment.js` (50 KB) existe **solo** porque lo pide daterangepicker.

### 2.2 · Tokens de color de un solo nivel + 43 hex sueltos

- 67 custom properties `--ov-*` definidas, pero **de un solo nivel** (no hay separación
  paleta cruda → rol semántico).
- **43 valores hex hardcodeados en vistas `.cshtml`** — cada uno es un color que el tema oscuro no
  puede reasignar. (`site.css` está limpio: 0.)

### 2.3 · Superficies clickeables sin teclado (AG-N9)

- `Views/Negocio/Dashboard.cshtml:196` — `<tr style="cursor:pointer" onclick="window.location=...">`.
  **No se puede llegar ni activar con teclado.** Es el patrón exacto que AG-N9 marca como error.
- `.ov-clickable-card` y `.ov-estado-row` en `Bot/Index.cshtml` — a auditar (las stat-cards del panel
  sí están envueltas en `<a>`, o sea esas están bien; las filas de estado hay que verificarlas).
- 29 handlers `$(...).on('click')` en vistas — revisar cuáles cuelgan de un elemento no-focusable.

### 2.4 · Iconos: 297 KB de fuente para 89 iconos

- 89 iconos FA distintos en todo el CRM; se sirven **297 KB de woff2** (4 familias completas).
- 89 SVG inline pesan del orden de **30-45 KB en total**, y solo viajan los de cada pantalla.
- FA ya está self-hosted (hecho el 09-04), así que esto ya no es un problema de dependencia externa
  — es solo peso.

### 2.5 · Cache de estáticos sin configurar (AG-N6)

`Program.cs:223` → `app.UseStaticFiles()` pelado, sin `Cache-Control`. Las vistas ya usan
`asp-append-version="true"` (hash en la query), así que **se puede servir `immutable` con seguridad**
y hoy no se está aprovechando.

### 2.6 · Lo que ya está bien

- `outline: none`: **0 ocurrencias** — no se está matando el foco del navegador (AG-N4 se cumple por
  omisión; el default del navegador es una resolución válida según la propia regla).
- `site.css` sin hex hardcodeados.
- Font Awesome self-hosted.
- Solo 3 `<img>` en todo el sistema → AG-N2 es marginal acá, no amerita fase propia.

---

## 3. Fases propuestas

Ordenadas por **impacto medido ÷ riesgo**. Cada fase es independiente y deployable sola.

### Fase 1 — Carga por pantalla de las librerías pesadas · *impacto alto, riesgo bajo*

Mover Chart.js, DataTables, Select2 y daterangepicker+moment de `_Layout` a las vistas que
realmente los usan.

- Agregar una sección `Styles` a `_Layout` (hoy solo existe `Scripts`), para poder mover también el CSS.
- Mover cada `<script>`/`<link>` a la `@section` de las 1-4 vistas que lo usan.
- SweetAlert2 (13 vistas) queda global: mover 13 vistas para ahorrar 107 KB no compensa el riesgo de
  olvidarse una y romper una confirmación.

**Resultado esperado:** de 615 KB a ~157 KB en la mayoría de las pantallas (**-75%**).
**Riesgo:** que una vista use una librería sin que el grep lo detecte (ej. invocada desde una partial).
Se mitiga revisando partials y probando cada pantalla afectada antes de cerrar.

### Fase 2 — Accesibilidad de superficies clickeables · *impacto medio, riesgo bajo*

- `Negocio/Dashboard.cshtml:196`: reemplazar el `<tr onclick>` por una fila cuya primera celda tenga
  un `<a>` real al detalle del cliente (mismo destino, alcanzable por Tab, abrible en pestaña nueva
  con Ctrl+click — que hoy tampoco funciona).
- Auditar los 29 handlers de click y las clases `ov-clickable-*`; donde el destino sea una navegación,
  que sea un `<a>`; donde sea una acción, un `<button>`.
- Agregar `:focus-visible` propio con contraste medido ≥3:1, separado de `:hover` (AG-N4).

### Fase 3 — Tokens de color de dos niveles · *impacto medio, riesgo medio*

- Partir los 67 `--ov-*` en `--ov-palette-*` (valor crudo) y `--ov-color-*` (rol semántico:
  superficie, borde, texto, acento…).
- Migrar los 43 hex de las vistas a tokens semánticos.
- **Beneficio real:** el tema oscuro deja de depender de que cada vista se haya acordado de usar la
  variable correcta; cambiar un tono pasa a ser un solo valor.
- **Riesgo:** es el cambio que más superficie visual toca. Conviene hacerlo pantalla por pantalla,
  no en un commit masivo.

### Fase 4 — Cache de estáticos · *impacto medio, riesgo bajo*

Configurar `UseStaticFiles` con `Cache-Control: max-age=31536000, immutable` para `/lib`, `/css`, `/js`
(seguro porque `asp-append-version` versiona por hash), y TTL corto/`no-cache` para el HTML.

### Fase 5 (opcional) — Iconos a SVG inline · *impacto medio, riesgo medio-alto*

Reemplazar los 89 iconos FA por SVG inline (~-250 KB). **Es la fase con peor relación
esfuerzo/beneficio**: toca casi todas las vistas y el ahorro solo se nota en la primera carga (después
la fuente queda cacheada). Recomendación: **dejarla para el final o no hacerla**, y decidir recién
después de medir el efecto real de las fases 1 y 4.

### Fase 6 (opcional, 3 líneas) — View Transitions nativas

`@view-transition { navigation: auto; }` + `prefers-reduced-motion` respetado. Suaviza la navegación
entre pantallas sin JS ni librerías. Degrada a nada en navegadores que no lo soportan.

---

## 4. Lo que este plan NO hace, a propósito

- **No mete GSAP ni animaciones de scroll.** El agente Astro las usa para vender; acá se navegan
  listados de cientos de filas todo el día. Agregarían latencia percibida y ruido.
- **No toca ScrollSmoother.** Ver §1.
- **No cambia Bootstrap ni el layout general.** El objetivo es sacar peso y arreglar accesibilidad,
  no rediseñar.
- **No unifica Select2/Selectize**: ya se resolvió el 09-04 dejando solo Select2.

---

## 5. Conflicto de reglas a resolver antes de implementar

El agente Astro **sí hace smoke test real** (`## Verificacion — este rol SI hace smoke test real
(diferencia deliberada del track .NET)`), mientras que `00-operativa-global` prohíbe explícitamente
que el implementador .NET levante la app o pruebe por navegador (esa separación de roles es
deliberada: quien escribe el código no lo verifica).

**Este plan no importa esa regla.** La verificación de las fases 1 y 2 (que son las que pueden romper
una pantalla en silencio) queda en QA, con una condición concreta: **probar cada pantalla afectada,
no solo compilar** — un `<script>` movido de lugar compila perfecto y rompe en runtime.

---

## 6. Verificación por fase

| Fase | Cómo se comprueba que funcionó |
|---|---|
| 1 | Abrir las 48 vistas y confirmar 0 errores de consola; medir el peso transferido antes/después en 3 pantallas testigo. |
| 2 | Recorrer con Tab cada pantalla tocada: todo lo clickeable tiene que ser alcanzable y activable con Enter. |
| 3 | Tema claro y oscuro en cada pantalla migrada; `grep` de hex en `.cshtml` tiene que dar 0. |
| 4 | `curl -I` sobre un asset: `Cache-Control: max-age=31536000, immutable`; y que un deploy nuevo igual sirva el archivo nuevo (gracias al hash). |
| 5 | Recuento de iconos rotos = 0 en las 48 vistas. |
| 6 | Navegación con `prefers-reduced-motion: reduce` → sin transición, sin errores. |
