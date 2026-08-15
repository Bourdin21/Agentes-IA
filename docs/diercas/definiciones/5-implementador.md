# Memoria - Implementador .NET (Astro, excepción de stack)

## Proyecto: Diercas SA (sitio institucional)
## Ultima actualizacion: 2026-08-13 (v1 — Etapa 1 implementada)

## Definiciones vigentes

### 0. Resultado del escaneo de reutilizacion cross-proyecto

Se escaneó `docs/*/definiciones/5-implementador.md` de todo el historial del estudio antes de implementar. **No hay ningún otro proyecto Astro/estático en el historial** — todos los `5-implementador.md` existentes (koi, etc.) son ASP.NET Core MVC + EF Core + MySQL, sin superposición de stack. La reutilización real para este proyecto **no viene de `docs/*/definiciones/`, viene del repo técnico de referencia explícito del cliente/orquestador**: `C:\Sistemas\labipac-front` (proyecto real de otro cliente, no un artefacto del estudio de agentes). Se reutilizó de ahí, adaptando (no copiando contenido):

- Patrón de `astro.config.mjs` (Tailwind v4 vía `@tailwindcss/vite`, sin `astro add tailwind`).
- Estructura de `Layout.astro` (navbar sticky con scroll effect, mobile menu, WhatsApp FAB, scroll-progress bar, footer con crédito Olvidata Soft, IntersectionObserver para `.reveal`).
- Convención de `global.css` (Tailwind v4 `@theme` con tokens de color propios + capa `@layer components` con `.btn-primary`, `.card-service`, `.icon-box`, `.glass`, `.section-label`, `.grid-bg`, etc.) — recoloreada para el brandbook de Diercas (cian→azul→violeta sobre navy) en vez de la paleta sky/blanco de IPAC.
- Mecanismo exacto del formulario de contacto: `fetch('/api/contact.php')` con JSON, estado inline de éxito/error sin recarga, y el patrón de PHP plano (`server/api/contact.php` + `server/SmtpMailer.php` + config SMTP fuera del webroot en `/storagedir/`) — **`SmtpMailer.php` se copió sin cambios** (es genérico, sin datos de IPAC); `contact.php` y el archivo de config se adaptaron con datos/branding de Diercas.

Decisión: **reutilizar y adaptar**, no desarrollar desde cero — cumple la regla de oro de reutilización cross-proyecto aunque la fuente no sea un `metadata.md` de `docs/`.

### 1. Alcance funcional resumido (Etapa 1)

Sitio institucional Astro + Tailwind CSS, 100% estático, sin backend de negocio ni base de datos (excepción declarada al patrón MVC/EF Core habitual del estudio, ya documentada en `3-arquitecto-mvc.md`). 5 páginas + 1 sección embebida:

1. **Inicio** (`/`) — hero con propuesta de valor del dossier, resumen de las 3 ramas con link a `/servicios#ancla`, franja de confianza (RITE + apto Estado, sin QR Data Fiscal), muestra de 3 clientes públicos de mayor peso institucional con link a `/clientes`.
2. **Nosotros** (`/nosotros`) — visión institucional + 3 sectores (Público/Privado/Instituciones), **con copy placeholder marcado explícitamente** (`[PLACEHOLDER]`, ver §6) + sección embebida de Certificaciones (`#certificaciones`).
3. **Servicios** (`/servicios`) — exactamente 3 bloques (Infraestructura, Provisión de equipos e insumos, Infraestructura de eventos) en ese orden, con anclas propias (`#infraestructura`, `#equipamiento`, `#eventos`). Mención explícita de OTDR/Fusionadora propios en Infraestructura.
4. **Clientes** (`/clientes`) — Content Collection (`src/content/clientes/*.json`), agrupados Público primero / Privado después, 13 clientes cargados (4 público + 9 privado) según la lista confirmada por el cliente. Placeholders de texto (sin logos reales).
5. **Contacto** (`/contacto`) — mismo patrón que `labipac-front/contacto.astro`, datos reales de Diercas (mail, WhatsApp 221 570-6954), formulario con validación HTML5 y fetch a `/api/contact.php`.

**Fuera de Etapa 1 (explícitamente, por instrucción del orquestador y `1-analista-funcional.md` v5)**: Ciberseguridad y Audio/Video (bloques 4/5 de Servicios), QR Data Fiscal, `/trabajos` (Trabajos realizados) — no está en el menú ni tiene página/ruta creada.

### 2. Plan de ejecucion tecnica por etapas (ejecutado)

1. Scaffold `npm create astro@latest` (template minimal, TypeScript strict, sin git) en `C:\Sistemas\diercas-front` — Astro 7.2.2 (labipac-front usa 6.4.7; misma familia de API de Content Collections/config, sin breaking relevante para este alcance).
2. Instalación manual de `tailwindcss` + `@tailwindcss/vite` (mismo patrón que labipac, no `astro add tailwind`) y edición de `astro.config.mjs`.
3. `src/styles/global.css` — tema Diercas: tokens `--color-navy`, `--color-navy-light`, `--color-navy-surface`, `--color-navy-border`, `--color-cyan`, `--color-blue`, `--color-violet`, `--color-text`, `--color-muted` + componentes reutilizados/recoloreados de labipac.
4. `src/content.config.ts` + `src/content/clientes/*.json` (13 archivos) — Content Collection tipo `data` con `glob` loader, schema `{ nombre, logo?, rubro: "publico"|"privado", orden? }`.
5. `src/layouts/Layout.astro` — header con wordmark de texto "DIERCAS" (placeholder, ver §6), nav de 5 links (sin "Trabajos"), footer con datos de contacto reales y crédito Olvidata Soft.
6. 5 páginas (`index`, `nosotros`, `servicios`, `clientes`, `contacto`).
7. `server/api/contact.php` + `server/SmtpMailer.php` + `server/diercas_mail_cfg.php` (placeholder, gitignoreado).
8. `README.md` reescrito con estructura, comandos y guía de deploy pendiente de credenciales.
9. Build local (`npm run build`) — evidencia en §5.

### 3. Cambios por capa

Proyecto sin capas Domain/Application/Infrastructure en sentido MVC (confirmado en `3-arquitecto-mvc.md`: sitio estático sin backend de negocio). Mapeo aproximado a "capas" de presentación pura:

- **Presentación (Astro)**: `astro.config.mjs`, `tsconfig.json` (sin cambios, ya venía del scaffold), `src/layouts/Layout.astro`, `src/pages/*.astro` (5 archivos), `src/styles/global.css`. Motivo: todo el sitio.
- **"Datos" (Content Collections, sin BD)**: `src/content.config.ts`, `src/content/clientes/*.json` (13 archivos). Motivo: modelar Clientes como contenido versionado en vez de hardcodeado en el markup, por pedido explícito de `2-disenador-funcional.md`.
- **Integración externa (PHP, fuera del build de Astro)**: `server/api/contact.php`, `server/SmtpMailer.php`, `server/diercas_mail_cfg.php`. Motivo: endpoint de envío de mail del formulario de contacto — no se buildea con `npm run build`, se sube manualmente al hosting (documentado en `README.md`).
- **Config de repo**: `.gitignore` (se agregó `server/diercas_mail_cfg.php`), `README.md` (reescrito, ya no es el default del scaffold).

No hay Controllers/Services/Repositories — no aplica la regla de "lógica de negocio en Services" porque no hay lógica de negocio de servidor (el único server-side es el PHP plano de contacto, sin reglas de negocio, solo saneo/envío de mail).

### 4. Migraciones EF aplicadas

No aplica — sin base de datos (confirmado en `3-arquitecto-mvc.md`).

### 5. Evidencia de build

```
> diercas-front@0.0.1 build
> astro build

[build] output: "static"
[build] mode: "static"
[build] Collecting build info... ✓ Completed in 2.80s.
[build] Building static entrypoints...
[build] Rearranging server assets...
generating static routes
  ├─ /clientes/index.html
  ├─ /contacto/index.html
  ├─ /nosotros/index.html
  ├─ /servicios/index.html
  ├─ /index.html
[build] 5 page(s) built in 3.47s
[build] Complete!
```

Sin errores ni warnings. Verificación adicional post-build (grep sobre `dist/`):
- 4 ocurrencias de `PLACEHOLDER` confinadas a `dist/nosotros/index.html` (ninguna fuga a otras páginas).
- 13 tarjetas `.client-placeholder` en `dist/clientes/index.html` (4 público + 9 privado).
- Link a `rite.gob.ar` presente en `dist/index.html`.
- Nav a `/contacto` presente en todas las páginas verificadas.

**No se ejecutó smoke test funcional por navegador** (regla del rol) — ver §7 para la guía de pruebas manuales.

### 6. Riesgos y supuestos

- **Copy institucional de `/nosotros` es placeholder, marcado explícitamente** (`[PLACEHOLDER]` en hero + 3 tarjetas de sectores) — el dossier corporativo real de Diercas existe (mencionado en `1-analista-funcional.md`) pero su texto exacto no estaba disponible como cita literal en las definiciones de este proyecto ni en archivos accesibles desde este entorno. **Joaquín debe reemplazar estos párrafos con el copy real del dossier antes de publicar** — la estructura de secciones (hero + 3 sectores + certificaciones) ya está armada y no requiere tocar código, solo texto.
- **Logo vectorial pendiente (Etapa 2, confirmado por el cliente)** — el header usa un wordmark de texto "DIERCAS" sobre un ícono cuadrado con la letra "D" en gradiente cian→azul→violeta (`.brand-gradient`). Reemplazar el `<span>D</span>` de `Layout.astro` por un `<img>`/inline SVG del logo real cuando llegue — cambio acotado a un solo archivo.
- **Logos de clientes pendientes** — cada cliente en `/clientes` e `/inicio` se renderiza como `.client-placeholder` (nombre en texto). El schema de la Content Collection ya tiene el campo `logo` opcional listo — cuando lleguen los assets reales, alcanza con completar `logo` en cada `.json` y cambiar el componente de renderizado (`<span>{nombre}</span>` → `<img src={logo}>` con fallback), sin tocar el resto de la página.
- **QR Data Fiscal — dependencia del cliente** — la sección Certificaciones (`/nosotros#certificaciones`) incluye una nota explícita de que este ítem se agrega en Etapa 2 cuando Diercas lo genere desde ARCA.
- **Credenciales SMTP sin completar** — `server/diercas_mail_cfg.php` tiene `host` y `password` con placeholders `TODO_*`. El archivo está gitignoreado (no se commitea con secretos). Joaquín debe completar con el buzón real `no-reply@olvidata.com.ar` (mismo usado en `labipac-front`, ver `ipac_mail_cfg.php` como referencia de credenciales ya vigentes) antes de subir al hosting.
- **Deploy no ejecutado** — sin credenciales FTP de DonWeb (explícitamente fuera de alcance de esta etapa). `README.md` documenta los 4 pasos pendientes.
- **Decisión de implementación no explícita en Arquitectura**: la sección "Certificaciones / Confianza institucional" (listada como sección propia en el sitemap del orquestador) se implementó como sección embebida dentro de `/nosotros` (`#certificaciones`), no como página propia — `3-arquitecto-mvc.md` la dejaba "a definir en Arquitectura" sin resolver. Se optó por sección embebida para mantener el nav en 5 links simples y porque el contenido (RITE + texto de aptitud) es liviano, sin justificar una página propia. Reversible sin gran esfuerzo si Joaquín prefiere una página `/certificaciones` separada.
- **Astro 7.2.2 vs. 6.4.7 de `labipac-front`** — se usó la versión estable actual del scaffold (`npm create astro@latest`) en vez de fijar la misma versión que labipac. Misma API relevante para este alcance (Content Collections, Tailwind vía Vite plugin) — sin incompatibilidad detectada en el build.
- Favicon: se dejó el favicon default de Astro (cohete) generado por el scaffold — no estaba en el alcance explícito de esta etapa y no hay asset de marca de Diercas todavía; reemplazar cuando llegue el logo vectorial.

### 7. Pruebas minimas requeridas para QA

Guía de pasos manuales (el Implementador no ejecuta smoke test por navegador):

1. `cd C:\Sistemas\diercas-front && npm run dev` — abrir `http://localhost:4321`.
2. Navegar las 5 páginas desde el menú (Inicio, Nosotros, Servicios, Clientes, Contacto) — confirmar que cargan sin error 404 y que el link activo del nav se resalta correctamente.
3. En Inicio: confirmar que los 3 links de "ramas" (Infraestructura/Provisión de equipos/Eventos) llevan a `/servicios#<ancla>` y hacen scroll al bloque correcto.
4. En Servicios: confirmar que los 3 bloques se ven completos en mobile (viewport angosto, ~375px) sin que el texto se corte — la maqueta de tarjetas usa `grid-template-columns: repeat(auto-fit, minmax(320px, 1fr))`, revisar que en pantallas chicas caiga a una columna.
5. En Clientes: confirmar que "Sector Público" aparece antes que "Sector Privado" y que los 13 nombres coinciden con la lista confirmada por el cliente (ver `1-analista-funcional.md` §Contenido real de negocio).
6. En Contacto: completar el formulario y enviar — **en local va a fallar** (no hay servidor PHP corriendo con `astro dev`, es esperado); confirmar que el mensaje de error inline se muestra sin romper la página. La prueba real de envío de mail solo es posible una vez deployado en DonWeb con `server/diercas_mail_cfg.php` completo.
7. Confirmar visualmente que la paleta (cian/azul/violeta sobre navy) se aplica de forma consistente en todas las páginas (botones, acentos, franjas) — sin colores fuera de esa paleta (criterio de aceptación PF1 de `1-analista-funcional.md`).
8. Revisar `dist/nosotros/index.html` (post `npm run build`) para confirmar visualmente cuáles párrafos son placeholder antes de decidir si se publica así o se espera el copy real.

### 8. Checklist de salida para merge

- [x] Build local limpio (`npm run build`, sin errores/warnings).
- [x] 5 páginas de Etapa 1 generadas, `/trabajos` correctamente excluida (ni ruta ni link de nav).
- [x] Content Collection de Clientes con 13 registros, agrupación Público→Privado verificada en el HTML generado.
- [x] Formulario de contacto con mismo mecanismo (`fetch` a `/api/contact.php`) y mismo patrón de validación que `labipac-front`.
- [x] Credenciales SMTP NO commiteadas en texto plano funcional (placeholders `TODO_*`, archivo gitignoreado).
- [x] `README.md` documenta pasos de deploy pendientes de credenciales FTP.
- [ ] Pendiente Joaquín: copy real de `/nosotros`, logo vectorial, logos de clientes, credenciales SMTP, credenciales FTP DonWeb.
- [ ] Pendiente QA: correr la guía manual de §7 y confirmar antes de dar por cerrada la Etapa 1.

## Historial de ajustes

- 2026-08-13: Implementación v1 — Etapa 1 completa (5 páginas + Content Collection de Clientes + formulario de contacto). Reutilización del patrón técnico de `labipac-front` (repo externo real, no un artefacto de `docs/`), recoloreado y adaptado al brandbook de Diercas. Ciberseguridad, Audio/Video, QR Data Fiscal y `/trabajos` quedaron explícitamente fuera, confirmado por el cliente el mismo día (`1-analista-funcional.md` v5). Build local limpio. Deploy pendiente de credenciales FTP DonWeb y SMTP — no bloquea el cierre de esta etapa.
