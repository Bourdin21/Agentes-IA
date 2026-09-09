# Estudio tecnico: antigravity.google

Analisis de ingenieria inversa del sitio de producto de Google Antigravity, hecho para extraer reglas
de construccion aplicables a los sitios institucionales Astro del estudio.

- **Sitio analizado:** https://antigravity.google/ (home)
- **Fecha de las mediciones:** 2026-09-09
- **Herramientas:** Playwright con Chrome real (canal `chrome`, headless), `curl`, Lighthouse 12.8.2,
  axe-core 4.10.2 inyectado en la pagina, CDP (`Performance.getMetrics`, `Accessibility.getFullAXTree`),
  Pillow para medicion de pixeles.
- **Alcance:** solo lectura. Se descargaron los 22 chunks JS y las 3 hojas CSS de la home para leerlos,
  mas el `sitemap`. No se descargo el sitio completo ni se toco `/blog/*` mas alla del sitemap.
- **Reglas derivadas:** ver la seccion "Reglas tomadas de antigravity.google" en
  `.github/agents/implementador-astro-front.agent.md`.

> Convencion de este documento: todo lo que se afirma esta medido o leido del bundle. Lo que no se pudo
> verificar desde afuera esta marcado explicitamente como **NO VERIFICADO**.

---

## 1. Stack confirmado

| Cosa | Evidencia |
|---|---|
| **Astro estatico** | 22 chunks bajo `/_astro/` con el patron de nombre `<Componente>.astro_astro_type_script_index_0_lang.<hash>.js`; `sitemap-index.xml` + `sitemap-0.xml` (`@astrojs/sitemap`); `/blog/rss.xml` (`@astrojs/rss`) |
| **Sin runtime de framework** | Ningun chunk contiene React/Vue/Svelte/Preact/Solid. Los 17 chunks de componente son TypeScript compilado plano |
| **Sin Tailwind** | Clases semanticas (`call-to-action--nav button button-primary button-compact download-button dropdown-nav`) + clase de scope de Astro. Cero clases utilitarias |
| **Scoped styles de Astro con `scopedStyleStrategy: 'where'`** | El CSS emite `.header:where(.astro-nen7h5rs){...}` — clase `astro-<hash>` envuelta en `:where()`, que es exactamente la salida de esa opcion (el default de Astro es `'attribute'` → `data-astro-cid-*`, que aca **no** aparece: 0 ocurrencias). 19 hashes de scope distintos en la home |
| **GSAP 3.15.0** | `.version=\`3.15.0\`` en `gsap.Bi_c5vh2.js`, `ScrollTrigger.BTGKJApg.js`, `SplitText.Bj_bHxnY.js`, `Draggable.G44Hfzvd.js` |
| **GSAP ScrollSmoother 3.15.0** | `C.version=\`3.15.0\`` dentro de `SmoothScrollLayout.astro_..._lang.BIBS_Ca_.js`; `#smooth-wrapper` / `#smooth-content` en el DOM |
| **Three.js r180** | `revision:\`180\`` y el string `three.js r180` en `Mouse.ZrlRGzn3.js` (548 KB sin comprimir / 166 KB gz) |
| **Poisson-disk sampling** | `new A.default({shape:[500,500], minDistance, maxDistance, tries:20}).fill()` en `MainParticlesComponent` — firma del paquete `poisson-disk-sampling` |
| **Sin View Transitions / ClientRouter** | 0 ocurrencias de `ClientRouter`, `astro-vt`, `view-transition`, `data-astro-transition`, `astro:before-swap` en el HTML. Verificado ademas navegando: se seteo `window.__probe`, se hizo click a `/pricing` y la variable **no** sobrevivio → recarga completa |
| **Hosting** | `server: Google Frontend`. Terceros: solo Google Fonts, GTM/GA y el `cookienotificationbar` de `gstatic.com` |

**NO VERIFICADO:** si usan Content Collections. Es *consistente* con lo observado (25 posts en
`/blog/<slug>/` mas `rss.xml` y sitemap generados), pero desde afuera no se puede distinguir una
Content Collection de un `getStaticPaths()` sobre un array.

---

## 2. Arquitectura de componentes

### 2.1 Un `<script>` por componente, sin bundle monolitico

Cada componente `.astro` con logica de cliente emite su propio chunk. Chunks de la home:

```
Header  MainParticlesComponent  TypedHeader  YoutubeVideoSection  AgentFirst
FeatureExplorerNew  CustomCursor  Slider  UseCases  MorphingParticlesComponent
LandingLatestBlogs  DownloadSection  AntigravityFooter  SmoothScrollLayout  index
+ page (prefetch de Astro) + deviceInfo (chunk compartido)
```

Todos son `<script type="module">` (defer implicito). Los chunks compartidos (`gsap`, `ScrollTrigger`,
`SplitText`, `Draggable`, `Mouse`=three, `deviceInfo`) se deduplican solos por el bundler.

**Peso medido (comprimido, home, escritorio):**

| | archivos | KiB gz |
|---|---|---|
| JS propio total (`/_astro/`) | 22 | **265,9** |
| — de eso: librerias (gsap + 3 plugins + three) | 5 | **228,8** |
| — de eso: codigo de componentes propios | 17 | **37,1** |
| JS de terceros (GTM + GA + cookie bar) | 3 | **315,5** |
| CSS | 7 | 15,5 |

El dato importante: **el codigo propio son 37 KB; el 86% del JS propio son las librerias de animacion.**
Three.js solo (166 KB gz) pesa 4,5 veces mas que todo el codigo del sitio.

### 2.2 Frontmatter → script de cliente: **siempre por `data-*`**

El script de un componente Astro es un modulo aparte: no puede cerrar sobre las variables del frontmatter.
El sitio resuelve esto de forma 100% consistente — el frontmatter escribe atributos `data-*` en el nodo raiz
y el script los lee. Sin excepciones en los 17 chunks.

Ejemplo real (`MainParticlesComponent`):

```js
document.querySelectorAll(`[data-main-particles-component]`).forEach(e => {
  const t = e.querySelector(`[data-container]`);
  const n = e.getAttribute(`data-theme`) || `light`;
  const r = parseFloat(e.getAttribute(`data-ring-width`) || `0.15`);
  const o = parseInt(e.getAttribute(`data-density`) || `200`);
  ...
});
```

Otros casos: `data-header` + `data-scroll-reactive="true"`, `data-youtube-url` en el `<dialog>`,
`data-cursor-persists`, `data-custom-cursor-wrapper`, `data-typed-header`.

**Corolario del patron:** los selectores de comportamiento son SIEMPRE `[data-*]`, nunca clases.
Las clases quedan solo para estilo. Eso hace que renombrar una clase no rompa la interactividad.

### 2.3 Guardas de doble inicializacion

Como no hay View Transitions, el init corre una sola vez, pero igual protegen contra doble init con una
marca en el nodo: `if (n._cursorInitialized) return; n._cursorInitialized = true;` (CustomCursor),
`if (n._youtubeSectionInitialized) return;` (YoutubeVideoSection).

Arranque estandar en todos los chunks:
```js
document.readyState === `loading` ? document.addEventListener(`DOMContentLoaded`, init) : init();
```

### 2.4 Layouts y `<head>`

- Dos capas de layout: `BaseLayout.css` (35,7 KB sin comprimir — tokens + tipografia + grilla + componentes
  base) y `SmoothScrollLayout.css` (15,2 KB — header, footer, dropdowns), mas `index.css` (9,2 KB) de la pagina.
- Las hojas de layout van como `<link rel=stylesheet>` externo; el CSS de los componentes de la pagina va
  **inline en un `<style>` del head** (comportamiento `inlineStylesheets: 'auto'` de Astro, que inlinea
  lo que baja de ~4 KB).
- `<head>` completo: charset, title, description, viewport, canonical, OG (7 metas), Twitter Card (4 metas),
  RSS alternate, favicon x2 + apple-touch-icon x2, `preconnect` a `fonts.googleapis.com` y
  `fonts.gstatic.com` (este con `crossorigin`), 3 hojas de Google Fonts, 2 hojas propias.
- **No hay `<meta name="generator">`** (lo quitaron), **no hay ningun `rel="preload"`** — ni de la fuente,
  ni del video del hero, ni de la imagen LCP.

### 2.5 Sistema de design tokens de dos niveles

204 custom properties en `:root`. Estan organizadas en dos capas:

- **`--palette-*`**: valores crudos. Ej. `--palette-blue-600: #3279f9`.
- **`--theme-*`**: roles semanticos que apuntan a la paleta. Ej. `--theme-primary-primary: #121317`,
  `--theme-surface-on-surface-variant`, `--theme-outline-variant`, `--theme-nav-button-hover`.

Escalas medidas:
```
--space-none/xs/sm/md/lg/xl/2xl/3xl/4xl/5xl/6xl/7xl = 0 4 8 16 24 36 48 60 80 88 120 180 px
--shape-corner-xs/sm/md/lg/xl/2xl/rounded          = 4 8 16 24 36 48 9999 px
```

Los componentes consumen **solo** `--theme-*` y `--space-*`, nunca un hex suelto — salvo dos excepciones
medidas: los colores del canvas estan hardcodeados en JS (`#7189ff`, `#2c64ed`, `#f84242`, `#ffcf03` en
`MainParticlesComponent`) y el header usa `background:#ffffffd9` literal.

Tipografia medida: `h1` 80px/88px peso 450, `h2` 42px/43,68px peso 450, familia
`"Google Sans Flex", "Google Sans", sans-serif`. Peso 450 es un eje de la fuente variable, no un peso estatico.

---

## 3. Scroll suavizado — como conviven con `sticky` y `fixed`

Este es el punto que mas importa para el estudio, porque es la trampa que ya rompio un sitio en produccion.

### 3.1 Que usan exactamente

**GSAP ScrollSmoother 3.15.0**, importado desde npm y bundleado dentro del chunk del componente
`SmoothScrollLayout` (no es una copia propia ni Lenis). Configuracion literal del bundle:

```js
const w = document.getElementById(`smooth-wrapper`);
const T = document.getElementById(`smooth-content`);
if (w && T && ScrollTrigger.isTouch !== 1) {
  w.addEventListener(`scroll`, () => {
    w.scrollTop  !== 0 && (w.scrollTop  = 0);
    w.scrollLeft !== 0 && (w.scrollLeft = 0);
  });
  const e = ScrollSmoother.create({
    wrapper: `#smooth-wrapper`,
    content: `#smooth-content`,
    normalizeScroll: { allowNestedScroll: true },
    smooth: 0.6,
    effects: true,
    smoothTouch: 0.1,
  });
  window.ScrollSmootherInstance = e;
  ScrollTrigger.refresh();
  ...
} else {
  // fallback nativo, ver 3.2
}
```

### 3.2 La decision clave: **se apaga entero en touch**

`ScrollTrigger.isTouch !== 1` es la guarda. `isTouch === 1` significa "dispositivo solo tactil, sin mouse".
En ese caso **ScrollSmoother nunca se crea** y el `else` cae a `scrollIntoView({behavior:'smooth'})` nativo
para los anchors. (El `smoothTouch: 0.1` que pasan queda muerto, nunca se aplica.)

Medido con Playwright emulando un Pixel 7:

| | escritorio 1440x900 | Pixel 7 |
|---|---|---|
| `window.ScrollSmootherInstance` | existe | **no existe** |
| `#smooth-wrapper` → `position` | `fixed` | `static` |
| `#smooth-wrapper` → `overflow` | `hidden` | `visible` |
| `#smooth-content` → `transform` | `matrix(1,0,0,1,0,-2500)` al scrollear | `none` |
| `body` → `touch-action` | `pan-x pinch-zoom` | `auto` |
| `body` → `height` | `10029px` (falseada) | `8726px` (real) |

### 3.3 Como resuelven los elementos fijos

- **El header vive FUERA de `#smooth-wrapper`** — verificado con `wrapper.contains(header) === false` — y es
  `position: fixed; top:0; z-index:100`, no `sticky`. Medicion de su posicion mientras se scrollea:

  | scrollY | `header.getBoundingClientRect().top` | clases |
  |---|---|---|
  | 0 | 0 | `header` |
  | 800 | -52 | `header scrolled hidden` |
  | 2500 | -52 | `header scrolled hidden` |
  | 5000 | -52 | `header scrolled hidden` |

  El -52 no es un bug: es el efecto deliberado de `.header.hidden { transform: translateY(-100%) }`
  (se esconde al scrollear hacia abajo, reaparece al subir, con umbral de 5px).

- **No usan `position: sticky` en ninguna parte de la home.** Existe una unica regla en `BaseLayout.css`
  (`.sticky-left-container .sticky-element { z-index:10; position:sticky }`) pero **cero elementos del HTML
  la usan** (0 matches de `class="...sticky..."`). O sea: evitaron el conflicto no usando sticky, no
  resolviendolo. **NO VERIFICADO** si esa regla funciona en alguna pagina interna.

- `window.scrollY` **sigue funcionando normal** con ScrollSmoother activo (la barra nativa sigue existiendo,
  el `body` tiene altura falseada). Lo que se rompe es cualquier cosa que dependa de que un elemento
  *realmente* scrollee.

### 3.4 Como resuelven los anchors — mejor que nuestro workaround actual

Manejo manual completo, con tres piezas:

1. **Hash en la carga inicial** — doble llamada, por la carrera con el layout:
   ```js
   window.location.hash && (w.scrollTop = 0,
     requestAnimationFrame(() => n(true)),
     setTimeout(() => n(true), 150));
   ```
2. **`hashchange` y `popstate`** con el mismo handler.
3. **Un unico handler delegado en `document`** que intercepta TODOS los `<a>`: resuelve el href contra
   `location`, y si es mismo origen + mismo pathname + tiene hash, hace `preventDefault()`,
   `history.pushState(null,'',hash)` y `smoother.scrollTo(target, true, 'top 80px')`.

**El detalle que nos importa:** el tercer argumento de `scrollTo` es un **string de posicion estilo
ScrollTrigger** (`'top 80px'`), no un numero. Eso resuelve el offset del navbar fijo sin hacer la resta a
mano de `smoother.offset(target,'top top') - 80` que documenta hoy nuestro rol. Es mas corto y menos fragil.

### 3.5 El fix que no esta documentado en ningun lado: el `scroll` del wrapper

```js
w.addEventListener(`scroll`, () => {
  w.scrollTop  !== 0 && (w.scrollTop  = 0);
  w.scrollLeft !== 0 && (w.scrollLeft = 0);
});
```

`#smooth-wrapper` es `position:fixed; overflow:hidden`. Cuando el navegador enfoca un elemento que quedo
fuera de la caja visible (tab, `autofocus`, ancla), **scrollea el wrapper** para traerlo — y como el wrapper
no deberia scrollear nunca, todo el contenido queda corrido y no vuelve. Este listener lo fuerza a 0.
ScrollSmoother trae su propio handler de `focusin` (que hace `O.scrollTop = 0` y
`scrollTo(target, false, 'center center')` si el elemento no esta en viewport), pero ellos agregaron esta
segunda red igual.

**Medido: la navegacion por teclado NO se rompe.** 18 `Tab` consecutivos: los 18 elementos enfocados
quedaron con `inView: true` y `#smooth-wrapper.scrollTop` se mantuvo en `0` en las 18 mediciones.

### 3.6 Costo que pagan sin usarlo

`effects: true` activa el motor de parallax por `[data-speed]`/`[data-lag]`. **La home tiene 0 elementos con
esos atributos** (medido). El motor se inicializa y corre en cada refresh para nada.

---

## 4. El canvas de particulas

### 4.1 Tecnica

No es Canvas2D: es **WebGL con simulacion GPGPU en ping-pong**, sobre Three.js r180.

- Las posiciones iniciales salen de un muestreo Poisson-disk 500x500 (distribucion azarosa pero sin grumos).
- Se codifican en una `DataTexture` `Float32` de 256x256 (65.536 slots).
- Dos `WebGLRenderTarget` (`rt1`/`rt2`) se alternan: un fragment shader de simulacion lee las posiciones del
  frame anterior, aplica ruido simplex en 3 escalas + un anillo de desplazamiento que sigue al mouse, y
  escribe las nuevas posiciones. `postRender()` swapea los dos targets.
- El pase de render dibuja `gl_Points` leyendo esa textura en el vertex shader; el fragment shader mezcla
  3 colores por ruido y recorta con un `sdRoundBox`.
- La interaccion con el mouse es un `Raycaster` contra un plano invisible de 12,5x12,5.

Config del renderer:
```js
new WebGLRenderer({ canvas, antialias:true, alpha:true,
  powerPreference:`high-performance`, preserveDrawingBuffer:true, stencil:false, precision:`highp` });
renderer.setPixelRatio(options.pixelRatio || window.devicePixelRatio);   // sin tope
```

Hay 4 `<canvas>` en la home (hero, dos de `MorphingParticles`, footer). En Pixel 7 el `devicePixelRatio`
medido es 2,625 y el canvas del hero queda en 1081x2202 px fisicos, sin tope de DPR.

### 4.2 Pausa fuera de viewport: SI, verificada hasheando pixeles

```js
let visible = false, raf = null;
const io = new IntersectionObserver(entries => entries.forEach(e => {
  visible = e.isIntersecting;
  e.isIntersecting ? scene.resume() : scene.stop();
}), { root:null, rootMargin:`0px`, threshold:0 });
io.observe(container);
const loop = () => { raf = requestAnimationFrame(loop); visible && scene.render(); };
loop();
```

Verificacion (hash del `canvas.toDataURL()` en dos momentos separados, no contando `requestAnimationFrame`):

| estado | hash t0 | hash t1 | cambia |
|---|---|---|---|
| hero en viewport | `3678545944` | `1517949825` | **si** |
| scrolleado a y=4000 (hero fuera) | `624112475` | `624112475` (+1,2 s) | **no — congelado** |
| de vuelta arriba | `1328964179` | `353024619` | **si** |

Detalle: el `requestAnimationFrame` **nunca se cancela**, solo se saltea el `render()`. Medido: 62 rAF/s
siguen ocurriendo con el hero fuera de pantalla. El costo residual es despreciable pero no es "apagado".

### 4.3 Lo que NO hacen

- **No escuchan `visibilitychange`.** Ni en `MainParticlesComponent` ni en `MorphingParticlesComponent`
  (grep sobre los 22 chunks: la unica ocurrencia esta dentro de la libreria ScrollTrigger). Se apoyan en el
  throttling nativo de rAF en pestañas ocultas.
- **No respetan `prefers-reduced-motion`.** Ver seccion 6.
- **Cleanup solo en `beforeunload`**: `io.disconnect(); cancelAnimationFrame(raf); scene.kill()`.
  `scene.kill()` si esta bien hecho (dispone geometria, materiales, los dos render targets, la textura de
  posiciones, el renderer, y saca el `<canvas>` del DOM). Pero `beforeunload` no dispara de forma confiable
  en mobile (bfcache / `pagehide`). Como no hay View Transitions, en la practica alcanza.

### 4.4 Costo de CPU

`Performance.getMetrics` de CDP, delta de `TaskDuration` sobre 4 s de reloj:

| escenario | TaskDuration |
|---|---|
| hero visible | 0,633 s / 4 s |
| hero fuera de viewport | 0,698 s / 4 s |

**Interpretacion honesta:** no baja al ocultarse porque lo que se apaga es trabajo de GPU, no de main thread,
y porque hay otros 3 canvas mas ScrollSmoother trabajando. **NO VERIFICADO: el costo real de GPU** — la
medicion se hizo en Chrome headless, que suele caer a SwiftShader (rasterizado por CPU) y no representa
el consumo en una maquina con GPU. Para medir GPU de verdad hace falta Chrome con ventana y el panel
Performance.

Lighthouse si captura el costo agregado: **bootup-time 1,6 s (escritorio) / 5,7 s (mobile)** y
**mainthread-work-breakdown 3,1 s / 10,5 s**.

---

## 5. Cursor propio (`CustomCursor`)

### 5.1 Como esta hecho

- Se aplica **solo a secciones marcadas** con `[data-custom-cursor-wrapper]` (3 en la home), nunca al
  documento entero.
- `cursor: none` se setea sobre el **elemento padre del wrapper**, y solo mientras el mouse esta adentro:
  `n.style.cursor = 'none'` en el `mouseenter`, `n.style.cursor = ''` en el `mouseleave`.
- El seguimiento es `gsap.quickTo(el,'x'/'y',{duration:.35, ease:'power2.out'})` — el mismo mecanismo que ya
  usamos para el tilt.
- Aparece con `scale 0→1` + `back.out(1.7)` y se va con `scale 1→0`.
- Recalcula posicion en `scroll` (passive) y se auto-apaga si el contenedor sale del viewport.
- El mismo bloque de codigo esta **duplicado literalmente** dentro de `YoutubeVideoSection`
  (unas 40 lineas identicas), con el agregado de un flag `s` para congelarlo mientras el modal esta abierto.

### 5.2 Touch

**Verificado en Pixel 7:** los 3 wrappers existen en el DOM, pero el `cursor` computado de sus padres es
`pointer`, no `none`. El cursor custom nunca se activa porque su unico disparador es `mouseenter`/`mousemove`.

Esto funciona **por construccion, no por chequeo explicito**: no hay ni un `matchMedia('(pointer: coarse)')`
ni un `'ontouchstart' in window` en el chunk. Si mañana alguien agregara un disparador de `pointerdown`
generico, un dispositivo tactil se quedaria con `cursor:none` pegado y un puntito flotando sin poder moverse.

### 5.3 Teclado

Neutro. El cursor es puramente decorativo, no captura foco ni intercepta clicks. `cursor:none` solo esta
activo mientras el mouse esta dentro del contenedor, asi que un usuario de teclado nunca lo ve.

Pero **el elemento sobre el que actua no es focuseable**: el bloque de video de `YoutubeVideoSection` es un
`<div data-video-wrapper>` con `cursor:pointer` y un `click` listener, no un `<button>`. Es decir: la accion
"abrir el video" existe **solo para mouse**. Con teclado no se puede abrir. Ese es el problema real del
patron, y no es el cursor en si.

### 5.4 Juicio

Para un sitio de producto de Google, donde el cursor custom es parte del lenguaje de marca y el publico es
mayoritariamente desktop, se sostiene. Para un sitio institucional de cliente **no aporta nada que justifique**:
suma ~750 B de JS y una dependencia de GSAP, duplica logica, y en la practica arrastra el antipatron de
convertir un `<div>` con `onclick` en el unico camino a una accion. Ver la regla correspondiente en el rol.

---

## 6. `prefers-reduced-motion`: no lo respetan, medido

Grep sobre los 22 chunks JS y las 3 hojas CSS: **0 ocurrencias** de `prefers-reduced-motion`,
`reducedMotion` o `matchMedia('(prefers-reduced-motion')`. (Las 2 apariciones de `matchMedia` estan dentro
de gsap/ScrollTrigger, para otra cosa.)

Verificado en un contexto de Playwright con `reducedMotion: 'reduce'`:

| | resultado |
|---|---|
| `matchMedia('(prefers-reduced-motion: reduce)').matches` | `true` |
| canvas del hero sigue animando (hash a t0 vs t+0,9 s) | **si, sigue animando** |
| `window.ScrollSmootherInstance` | **existe — el scroll suavizado sigue activo** |

Es una falla de WCAG 2.3.3 (Animation from Interactions) y del criterio del rol. **No se copia.**

---

## 7. Rendimiento — numeros reales

### 7.1 Lighthouse 12.8.2 (2026-09-09, throttling por defecto)

| categoria | escritorio | mobile |
|---|---|---|
| **Performance** | **71** | **55** |
| Accessibility | 95 | 95 |
| Best Practices | 100 | 100 |
| SEO | 85 | 85 |

| metrica | escritorio | mobile |
|---|---|---|
| FCP | 1,3 s | **71,7 s** |
| LCP | 2,0 s | **101,3 s** |
| Speed Index | 3,2 s | 71,7 s |
| TTI | 2,9 s | 103,7 s |
| TBT | 240 ms | 0 ms |
| CLS | 0,015 | 0 |
| TTFB (documento) | 40 ms | 50 ms |
| bootup-time | 1,6 s | 5,7 s |
| main-thread work | 3,1 s | 10,5 s |
| peso total | 28.673 KiB | 26.756 KiB |
| requests | 61 | 63 |

Elemento LCP en ambos: `<span class="typed-content" aria-hidden="true">` (el titular con efecto maquina de
escribir).

### 7.2 La causa de los 71,7 s en mobile: la fuente de iconos

Es un solo recurso. Verificado dos veces (Playwright y `curl` con UA de Chrome 141):

```
GET https://fonts.gstatic.com/s/googlesymbols/v459/HhyNU5Ak9u-oMExPeInvcuEmPpEJ.ttf
→ 200, content-type: font/ttf, transferido: 13.370.542 bytes (12,75 MiB)
```

El CSS que la pide es:
```css
@font-face {
  font-family: 'Google Symbols';
  font-weight: 100 700;
  font-display: block;                              /* ← bloquea el texto hasta cargar */
  src: url(.../HhyNU5Ak9u-oMExPeInvcuEmPpEJ.ttf) format('truetype');   /* ← TTF, no woff2 */
}
```

Tres errores acumulados: **TTF en vez de woff2**, **sin `unicode-range`** (ningun subsetting: viene la fuente
de iconos variable entera) y **`font-display: block`**. Lighthouse mobile lo reporta como
`render-blocking-resources: ahorro estimado 69.000 ms`.

Contraste: la fuente de **texto** (`Google Sans Flex`) esta bien hecha — woff2, `font-display: swap`,
partida en subsets por `unicode-range` (se descargo un solo subset, 493 KB).

### 7.3 Desglose de peso (Pixel 7, primera carga sin cache, 61 requests / 29,4 MB)

| tipo | requests | bytes |
|---|---|---|
| fuentes | 2 | **13,86 MB** |
| imagenes | 18 | **9,57 MB** |
| video | 3 | 5,27 MB |
| scripts | 27 | 0,63 MB |
| CSS | 7 | 15,8 KB |
| documento | 1 | 28,7 KB |

### 7.4 Imagenes: lo peor del sitio

Medido sobre el HTML: **21 `<img>`, 0 con `loading="lazy"`, 0 con `srcset`, 0 `<picture>`, 3 con `width`**.

Los tres peores:
```
landing-thumbnail-frontend.jpg    2.039 KiB  (ahorro estimado 1.953 KiB)
landing-thumbnail-fullstack.jpg   1.911 KiB  (ahorro estimado 1.831 KiB)
landing-thumbnail-enterprise.jpg  1.883 KiB  (ahorro estimado 1.804 KiB)
```

Oportunidades de Lighthouse: `modern-image-formats` 7.139 KiB, `uses-responsive-images` 8.722 KiB,
`uses-optimized-images` 2.831 KiB, `offscreen-images` 1.961 KiB.

Traduccion: no estan usando el componente `<Image />` de Astro ni nada equivalente. Son `<img src>` crudos
apuntando a `/assets/image/*`.

### 7.5 Cache

**Todo** el sitio responde `Cache-Control: public, max-age=600`, incluidos los archivos con hash de contenido
en el nombre:

```
GET /_astro/BaseLayout.zSiu0WRx.css  →  Cache-Control: public, max-age=600
GET /assets/image/landing/feature-3.jpg → Cache-Control: public, max-age=600
GET /                                 →  Cache-Control: public, max-age=600
```

Lighthouse: `uses-long-cache-ttl: 46 recursos`. Un archivo cuyo nombre contiene el hash del contenido puede
y debe ir con `max-age=31536000, immutable`.

### 7.6 Codigo muerto medido

El chunk `page.LAbJoB63.js` es el modulo de **prefetch de Astro**. Se llama sin opciones
(`prefetchAll` queda `false`, estrategia default `'hover'`), lo que significa que solo prefetchea links con
`data-astro-prefetch` explicito. **La home tiene 0 elementos con ese atributo.** Verificado: despues de
hacer hover sobre un link del nav y esperar 1,2 s, `document.querySelectorAll('link[rel=prefetch]').length`
sigue en **0**. El modulo se descarga, se parsea y registra listeners para nada.

### 7.7 Seguridad y cabeceras

```
content-security-policy: object-src 'none'; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: ...
strict-transport-security: max-age=2592000; includeSubdomains
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
```
CSP presente pero con `'unsafe-inline'` y `'unsafe-eval'` en `script-src` (necesarios por los `<script>`
inline), lo que limita bastante su valor. HSTS de solo 30 dias. `/no-existe-xyz` devuelve 404 correcto.

---

## 8. Accesibilidad

### 8.1 axe-core 4.10.2 sobre la home — solo 4 tipos de violacion

| impacto | regla | nodos | causa |
|---|---|---|---|
| serious | `aria-prohibited-attr` | 4 | `aria-label` sobre `<p>` sin `role` valido (`.feature-description`) |
| moderate | `landmark-no-duplicate-main` | 1 | **dos `<main>`** |
| moderate | `landmark-main-is-top-level` | 1 | el `<main>` interno esta dentro del externo |
| moderate | `landmark-unique` | 2 | `<main>` y `<nav>` sin nombres distinguibles |

Cero violaciones de contraste, de `alt` en imagenes, de nombre de link o de nombre de boton. Para un sitio
con este nivel de animacion, es un resultado bueno.

**El `<main>` duplicado es consecuencia directa del scroll suavizado**: envolvieron
`<main><div id="smooth-wrapper"><div id="smooth-content">…</div></div></main>` y adentro quedo el `<main>`
real de la pagina. Se arregla haciendo que el host del smoother sea un `<div>`.

### 8.2 Foco visible: falla, y esta medido

Se tabulo con teclado real y se comparo el mismo elemento enfocado vs no enfocado, recortando pixel a pixel:

| # | elemento | `outline-style` | `box-shadow` | contraste medido entre estado enfocado y no enfocado |
|---|---|---|---|---|
| 0 | link del logo | `auto` (default de Chrome) | none | 1,50 |
| 1 | boton "Products" | **none** | none | **1,14** |
| 2 | boton "Use Cases" | **none** | none | **1,14** |
| 3 | link "Pricing" | **none** | none | **1,11** |
| 4 | link "Enterprise" | **none** | none | **1,11** |
| 5 | boton "Resources" | **none** | none | **1,14** |
| 6 | link 🚀 | `auto` (default) | none | 1,65 |
| 7 | CTA "Download" | **none** | none | **1,47** |
| 8 | link "Documentation" | **none** | none | **1,07** |
| 9 | link "Blog" | **none** | none | **1,10** |

El anillo de foco esta desactivado a proposito y reemplazado por un tinte de fondo:
```css
.nav-button:hover, .nav-button:focus, .nav-button:focus-visible {
  background: var(--theme-nav-button-hover);
  outline: none;
}
.subnav-link:focus, .subnav-link:hover { background-color: ...; color: ...; outline: none; }
```

WCAG 2.2 SC 2.4.11 (Focus Appearance) pide **3:1** entre el estado enfocado y el no enfocado.
**Ninguno llega.** Ademas usan `:focus` y `:hover` en la misma regla, asi que el indicador de foco es
indistinguible del hover. axe no detecta esto (no evalua apariencia de foco) — por eso hay que medirlo.

### 8.3 Teclado

**Bien:**
- Los dropdowns del nav abren tanto con `mouseenter` como con **`focus`**, asi que son alcanzables por teclado.
- `aria-haspopup="true"` y `aria-expanded` en los triggers.
- Los items de dropdown estan dentro de `<nav role="menu">` con `<a role="menuitem">`.
- ScrollSmoother + el guard del wrapper mantienen todo lo enfocado en viewport (18/18 medidos).

**Mal, verificado:**
- **`Escape` no cierra el dropdown de escritorio.** Se abrio con click (`dropdown-open` presente), se apreto
  `Escape`, y la clase seguia presente. Solo cierra con `mouseleave` del header o click en el overlay —
  las dos cosas requieren mouse. `Escape` esta implementado, pero solo para el menu contextual del logo.
- No hay `focusout`: si un usuario de teclado tabula fuera del dropdown, queda abierto.
- `aria-expanded` se actualiza solo en los triggers **mobile**; los de escritorio quedan clavados en `"false"`
  aunque el panel este abierto (medido: `expanded: "false"` con el dropdown abierto).

### 8.4 Nombres accesibles y la fuente de iconos

Usar una fuente de iconos con ligaduras significa que el nombre del icono es **texto real en el DOM**
(`<span class="symbol">keyboard_arrow_down</span>`). Lo tapan poniendo `aria-label` en el elemento padre:

```
button: "Products"        ✔ (el aria-label gana sobre "Products keyboard_arrow_down")
button: "Use Cases"       ✔
link:   "Pricing"         ✔
link:   "Download download"   ✘  ← se les escapo: la ligadura entra en el nombre accesible
link:   "Launch Remote Control" ✔
```
(extraido de `Accessibility.getFullAXTree` via CDP)

Es una clase de bug que **solo existe porque usan icon font**. Con SVG inline no puede pasar.

### 8.5 Lo bueno que si vale copiar: texto animado accesible

El titular con efecto maquina de escribir usa `SplitText`, que envuelve cada caracter en un `<span>`.
Eso destruiria el texto para lectores de pantalla, para el traductor de Chrome y para el snippet de Google.
Lo resuelven con un par de nodos:

```html
<span class="typed-content" aria-hidden="true" translate="no" data-nosnippet>…animado…</span>
<span class="visually-hidden">Experience liftoff with the next-gen agent platform</span>
```
```css
.visually-hidden { clip: rect(0 0 0 0); white-space: nowrap; border:0; width:1px; height:1px;
                   margin:-1px; padding:0; position:absolute; overflow:hidden; }
```

Y el helper mantiene los dos sincronizados al cambiar el texto:
```js
setText(e) { ...; this.typedContent.innerHTML = e;
             const n = this.element.querySelector('.visually-hidden'); n && (n.innerHTML = e); ... }
```

`translate="no"` evita que el traductor de Chrome reordene los spans partidos; `data-nosnippet` evita que
Google use el markup mutilado como snippet.

### 8.6 SEO

Score 85 en ambos, con dos fallas:
- `link-text`: un link `"Read More"` a `/docs/enterprise` sin texto descriptivo.
- `crawlable-anchors`: `<a aria-hidden="true" class="glue-cookie-notification-bar-control">` sin `href`
  (viene de la libreria de cookies de Google, no es codigo propio).

---

## 9. Detalles de oficio

### 9.1 Video de YouTube: facade con `<dialog>` nativo — el patron esta bien hecho

**Verificado: cero requests a `youtube.com` / `ytimg.com` en la carga inicial** (0 de 59).

- El preview es un `<video>` **local** en autoplay silencioso:
  `<video autoplay loop muted playsinline width="1920" height="1080">` (`width`/`height` explicitos → CLS 0).
- El `<video>` se pausa fuera de viewport con ScrollTrigger:
  ```js
  ScrollTrigger.create({ trigger: n, start:'top bottom', end:'bottom top',
    onEnter: () => play(v), onLeave: () => v?.pause(),
    onEnterBack: () => play(v), onLeaveBack: () => v?.pause() });
  ```
  y el `play()` va con `.catch()` porque el autoplay puede estar bloqueado por politica del navegador.
- Al hacer click se instancia `ModalYoutubeHelper` (script inline, con guarda
  `if (!window.ModalYoutubeHelper)`), que **recien ahi** inyecta el iframe y llama `dialog.showModal()`.
- **Al cerrar, escucha el evento nativo `close` del `<dialog>` y hace `this.body.innerHTML = ''`** —
  destruye el iframe. Asi el video corta sin importar como se cerro (boton, Escape, click afuera).
  Es la misma regla que ya tenemos para el lightbox, resuelta destruyendo el nodo en vez de pausarlo.
- La URL se normaliza (`watch?v=` → `/embed/`) antes de inyectarla.
- El boton de cerrar esta **adentro** de la caja en mobile (`inset-block-start: -60px` con
  `padding-inline: 60px` en el `.dialog-inner`) y afuera solo desde 834px (`-40px`).

### 9.2 CTA dependiente del SO, con fallback sin JS

`deviceInfo.ts` parsea el UA y devuelve `{name, version, buttonText, links}`. El script de la home reemplaza
el contenido de `[data-os-cta-container]` con un CTA especifico (`Download for Windows` + icono
`desktop_windows`).

**Lo importante:** el HTML estatico ya trae un fallback usable —
verificado con `javaScriptEnabled: false`:
```html
<a href="/download" class="call-to-action button button-primary" aria-haspopup="false" aria-expanded="false">
  <span>Download</span>
</a>
```
Es decir: sniffing de UA como **mejora**, nunca como unica via. Eso si se copia.

### 9.3 Transiciones entre paginas

No hay. Navegacion tradicional con recarga completa. Sorprendente para un sitio con este nivel de animacion,
pero coherente: View Transitions mas ScrollSmoother mas 4 canvas WebGL habria requerido un cleanup en
`astro:before-swap` para cada uno de los 17 componentes.

### 9.4 Estados de hover y micro-detalles

- Transiciones cortas: `all .15s ease-out` en botones, `.2s` en links de subnav, `.3s ease-in-out` en el header.
- CTA principal: `border-radius: 9999px`, fondo `#121317`, `font-size: 14.5px`, `font-weight: 450`.
- Flecha de link: `transform: translate(2px,-2px)` en hover/focus — movimiento de 2px, no de 8.
- **Easter egg:** click derecho sobre el logo abre un menu contextual propio con "Copy Logo as SVG" /
  "Copy Wordmark", que escriben el SVG al portapapeles con `navigator.clipboard.writeText()` y muestran
  "Copied!" por 1200 ms. Cierra con `Escape`, con `pointerdown` afuera y con `scroll`.
- Todo lo decorativo lleva `pointer-events: none`: `#antigravity-footer-wrapper`, `.custom-cursor`,
  `.cursor-container`, `.landing-video`, `.grid-overlay`, `.dropdown-overlay` cuando esta cerrado
  (5 declaraciones en CSS, mas las que setean por JS).
- Queda en produccion un **overlay de grilla de debug** (`.grid-overlay` con `z-index:9999`,
  `background-color:#ff000014`), no montado en la home.
- Queda en produccion un **panel de debug del canvas** activable con `?gui=true`
  (`gui: new URLSearchParams(location.search).get('gui')==='true'`) que expone colores, densidad y
  desplazamiento del anillo. Truco util y barato.

### 9.5 Cookies

`cookienotificationbar.min.js` + `.css` de `gstatic.com` (28,6 KB gz + 1,7 KB gz), inicializado por un script
inline que arma `window.dataLayer` antes. Es una libreria interna de Google (glue). En la medicion no se
mostro banner (depende de region/IP); solo quedo el control "Manage cookies" del footer.

---

## 10. Resumen: que copiar y que no

### Copiar

1. `data-*` como unico canal frontmatter → script de cliente, y como unico selector de comportamiento.
2. Un `<script>` por componente, sin bundle global.
3. Tokens de dos niveles (`--palette-*` crudo → `--theme-*` semantico) con escalas cerradas de espacio y radio.
4. `scopedStyleStrategy: 'where'` (especificidad 0, el CSS del sitio siempre puede ganar).
5. Facade de YouTube con `<dialog>` nativo + destruir el iframe en el evento `close`.
6. Pausar `<video>` fuera de viewport por ScrollTrigger, con `.catch()` en el `play()`.
7. Texto animado con par `aria-hidden` + `.visually-hidden` sincronizado, mas `translate="no"` y `data-nosnippet`.
8. Canvas apagado por `IntersectionObserver`, verificado hasheando pixeles.
9. Sniffing de UA solo como mejora, con el HTML estatico trayendo un fallback usable.
10. ScrollSmoother: apagado total en touch, navbar fixed fuera del wrapper, guard de `scroll` del wrapper,
    `scrollTo(target, true, 'top 80px')` para anchors.
11. Movimiento de hover chico (2px) y transiciones de 150-200 ms.
12. Panel de debug gateado por query param.

### No copiar

1. Fuente de iconos por `<link>` de Google Fonts — **12,75 MB de TTF con `font-display: block`**.
2. `<img>` crudos sin `srcset`, sin `loading="lazy"`, sin formato moderno — 9,5 MB de imagenes.
3. Ausencia total de `prefers-reduced-motion`.
4. `outline: none` sin reemplazo con 3:1 de contraste.
5. `Escape` que no cierra el dropdown y `aria-expanded` desincronizado en escritorio.
6. `<main>` como host del smoother (dos `<main>` en el documento).
7. `Cache-Control: max-age=600` sobre archivos con hash de contenido.
8. Three.js (166 KB gz) para un fondo decorativo en un sitio institucional.
9. Cursor propio.
10. `<div>` con `onclick` como unica via a una accion (el bloque de video no se abre con teclado).
11. `effects: true` en ScrollSmoother sin ningun `[data-speed]`.
12. Prefetch de Astro cargado sin ningun `data-astro-prefetch`.

---

## 11. Reproducir estas mediciones

Los scripts de sondeo se escribieron en un scratchpad temporal y no se versionaron. Para rehacerlos:

```bash
# Playwright: se reuso el playwright-core de C:/Sistemas/diercas-front
#   import { chromium } from 'file:///C:/Sistemas/diercas-front/node_modules/playwright-core/index.mjs';
#   (en Windows el import ESM necesita el prefijo file:/// o tira ERR_UNSUPPORTED_ESM_URL_SCHEME)
#   chromium.launch({ channel: 'chrome', headless: true })

npx lighthouse@12 "https://antigravity.google/" --preset=desktop --output=json --output-path=lh-desktop.json
npx lighthouse@12 "https://antigravity.google/"                  --output=json --output-path=lh-mobile.json

# axe: page.addScriptTag({ url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js' })
#      luego await window.axe.run(document, { resultTypes: ['violations'] })

# peso real de la fuente de iconos
curl -s -A "<UA de Chrome>" -o /dev/null -w "%{size_download}\n" \
  "https://fonts.gstatic.com/s/googlesymbols/v459/HhyNU5Ak9u-oMExPeInvcuEmPpEJ.ttf"
```

Verificacion del canvas (el metodo, no el resultado): hashear `canvas.toDataURL()` en dos momentos
separados por >500 ms y comparar. **No** contar `requestAnimationFrame`: en este sitio el rAF sigue
corriendo a 62 fps con el canvas congelado.
