# Memoria - Implementador (backend PHP sin subagente dedicado + front Astro con `implementador-astro-front`)

## Proyecto: kite-punta-lara
## Ultima actualizacion: 2026-09-02

## Definiciones vigentes

### Repositorios
**MONOREPO desde el 2026-09-02 (segunda mitad del dia).** Backend y front viven en un solo repo:
- `C:\Sistemas\kite-punta-lara` — raiz: backend PHP (API JSON). Remoto en GitLab: `https://gitlab.com/bourdinjoaquin/kite-punta-lara.git`.
- `C:\Sistemas\kite-punta-lara\front` — subcarpeta: front Astro estatico. **Es la unica ruta de trabajo del front.**
- ~~`C:\Sistemas\kite-punta-lara-front`~~ **ABANDONADO**: era el repo hermano de la primera version. Quedo trabado por un lock de archivos — no se usa, no se borra, no se le commitea.

### Front Astro (`kite-punta-lara/front`) — P1 implementada
- **Stack**: Astro 7.2 `output: 'static'` + CSS plano con tokens (**sin Tailwind**, a diferencia de diercas-front) + Inter self-hosted (`@fontsource/inter`) + `astro-icon`/`@iconify-json/fa6-solid` + GSAP. Se adopto el sistema de diseño del sitio propio del estudio (`olvidatasoft-new`), que usa CSS plano — por eso la desviacion respecto del default Tailwind del rol.
- **Consumo de la API**: todo el fetch corre **en el navegador**, nunca en el frontmatter de Astro — el sitio es estatico y un fetch en build congelaria el pronostico al momento de compilar. Es la decision estructural mas importante de este repo.
- **Proxy de dev**: `astro.config.mjs` reescribe `/api/*` → `http://localhost:8000/*` (Vite), replicando el layout de produccion (Astro en la raiz de `club.olvidata.com.ar`, PHP bajo `/api/*`, mismo origen). Asi el codigo pide siempre `fetch('/api/pronostico')` y es identico en dev y prod. **`astro preview` no aplica este proxy** (no usa el dev server de Vite) — documentado en el README del repo.
- **Archivos clave**: `src/lib/api.ts` (contrato tipado + validacion de forma), `src/lib/rango.ts` (rango navegable en localStorage), `src/lib/navegabilidad.ts` (horas navegables y rachas), `src/lib/semaforo.ts` (criterio del semaforo), `src/lib/formato.ts` (numeros/fechas/metros es-AR), `src/scripts/dashboard.ts` (orquesta fetch → render), `src/scripts/grafico-horas.ts` (construye el SVG de la grilla horaria), `src/components/PanelHoy.astro` (card destacada), `ProximosDias.astro`, `EstacionesEnVivo.astro`, `DialogoRango.astro`.
- **Criterio del semaforo — definido en Implementacion, no venia de Diseño**: rojo = dia bloqueado por sudestada (`ConTemporal` o valor desconocido) **o** ninguna hora del dia dentro del rango elegido por el usuario; amarillo = hay horas navegables pero con birazon activa o sudestada `SinTemporal`; verde = el resto. Vive en `src/lib/semaforo.ts` + `src/lib/navegabilidad.ts` con el razonamiento escrito.
- **Alcance**: solo P1. Los botones "Iniciar sesion"/"Registrarme" del header, del CTA de la card de hoy y del banner son placeholders declarados (`aria-disabled` + `title`), no links muertos. El rango navegable NO espera a las cuentas: es anonimo, en localStorage.

### Archivos y capas modificadas (scaffold inicial)
- **Presentacion**: `public/index.php` (front controller, ruteo `GET /` → `HomeController::index`), `public/assets/css/style.css`, `templates/home.php` (placeholder de P1, muestra solo estado de conexion a datos), `src/Controllers/HomeController.php`.
- **Negocio**: `src/Support/SmtpMailer.php` (PAT-007, reutilizado literal de labipac-front, solo se le agrego `namespace App\Support`), `src/Support/Csrf.php` (helper centralizado, ver riesgo de seguridad de Arquitectura). Services del motor de calculo (`MotorDeCalculoService`, `ConsolidadorEstacionesService`, `PronosticoService`, `NotificacionesService`, `BitacoraService`, `AuthService`) **todavia no implementados** — son el siguiente paso.
- **Datos**: `src/Data/Db.php` (PDO singleton, lee `config/db.php`), `config/db.php` + `config/db.local.php.example`, `config/mail.php` + `config/mail.local.php.example`, `config/umbrales.php` (umbrales iniciales del motor de calculo, ver nota abajo), `config/equipo_default.php` (**placeholder generico, no es el quiver real de Joaquin todavia**), `sql/migrations/001_usuarios.sql`, `002_equipo_quiver_items.sql`, `003_sesiones_bitacora.sql` (sin aplicar todavia contra `olvidata_club`).
- `bin/enviar_avisos.php`: stub del cron con logging a `storage/logs/cron.log`, llama a un `NotificacionesService` que todavia no existe (comentado).
- `composer.json` (PSR-4 `App\` → `src/`), `.gitignore` (excluye `vendor/`, `config/db.local.php`, `config/mail.local.php`, contenido de `storage/`), `README.md`.

### Migraciones SQL generadas (equivalente EF)
Si — 3 migraciones creadas en `sql/migrations/` (ver arriba), **no aplicadas todavia** contra la base real `olvidata_club`. Aplicar en orden antes de poder registrar el primer usuario.

### Riesgos residuales
- `config/equipo_default.php` tiene valores placeholder genericos (rango de tamanos de kite tipico), no el quiver real de Joaquin — reemplazar antes de que la recomendacion le sirva a un usuario real.
- `config/umbrales.php` son umbrales iniciales de research bibliografico (ya documentados como hipotesis en `1-analista-funcional.md`), no calibrados con datos reales del spot.
- Smoke test local (`php -S localhost:8091 -t public`) confirma que el ruteo + template + manejo de error de conexion funcionan; el error mostrado localmente (`could not find driver`) es porque el PHP local de este entorno no tiene `pdo_mysql` habilitado — no es un bug de la app, en DonWeb (PHP 8.4 lsphp) deberia estar disponible, a confirmar en el primer deploy real.
- No se aplico ninguna migracion SQL todavia, no se creo `config/db.local.php` ni `config/mail.local.php` reales (las credenciales viven solo en `docs/credenciales.local.md`, nunca copiadas al repo del proyecto).

### Proximos pasos pendientes
1. ~~Aplicar las 3 migraciones contra `olvidata_club`.~~ Hecho 2026-09-02, contra una base MySQL local de desarrollo (no la de DonWeb).
2. ~~Implementar `ConsolidadorEstacionesService` (CARP/SMN) + `PronosticoService` (Open-Meteo) + `CacheService`.~~ Hecho 2026-09-02.
3. ~~Implementar `MotorDeCalculoService`.~~ Hecho 2026-09-02.
4. ~~Completar P1 (Home) real.~~ Hecho como API (`GET /pronostico`, `PronosticoController`) + pantalla Astro en `kite-punta-lara-front` (hecho 2026-09-02).
5. `AuthService` + P2/P3 (login/registro) + P4 (dashboard logueado) + P5 (mi equipo) — Etapa 2, incluye resolver CSRF sobre API (`GET /csrf` + header `X-CSRF-Token`). Del lado del front, la Etapa 2 tambien reemplaza los placeholders de cuenta (header + banner de `kite-punta-lara-front`) por pantallas reales.
6. `BitacoraService` + P6/P7.
7. `NotificacionesService` + activar el cron real en el panel de DonWeb.
8. **Deploy**: `kite-punta-lara-front` todavia no tiene `scripts/deploy.sh` ni `.env.deploy.example` (el rol los pide) — se agregan cuando se defina el metodo de subida a DonWeb para el subdominio.

### Contrato de la API — historial de revisiones
El contrato se revisó dos veces el mismo dia, las dos a partir de lo que salio de construir P1.

**Revision 1 (manana):** se agrego `pronostico[].navegable`, `estaciones[].direccionTexto` y
`estaciones[].timestamp` en ISO 8601 con offset; se corrigio el bug de `confiabilidad` (Media
para manana/pasado, Baja solo para el dia 3). Saco tres fragilidades del front de golpe.

**Revision 2 (tarde):** rediseno grande de P1 pedido por Joaquin.
- **`pronostico[].horas[]`** (nuevo): 24 entradas por dia (00:00→23:00) con viento, direccion y
  marea por hora. Es la base de toda la pantalla nueva.
- **`estaciones[].rafagaNudos` y `estaciones[].mareaMetros`** (nuevos): CARP es mareografo ademas
  de anemometro.
- **`pronostico[].mareaMetrosMin/Max`** (nuevos).
- **`config.rangoNavegableDefault`** (nuevo): punto de partida del rango de cada persona.
- **`recomendacionEquipo` y `navegable` SE FUERON.** El `navegable` que se habia pedido en la
  revision 1 duro medio dia: dejo de tener sentido cuando la navegabilidad paso a depender del
  rango que elige cada usuario, que el backend no conoce. Ahora la calcula el front.

**Revision 3 (tarde, despues del rediseno):** Joaquin detecto que el pronostico horario marcaba
7,4 kt mientras Norden media 15,4. El backend valido los modelos contra 19 h de mediciones reales
de CARP/Norden y cambio de `best_match` (que resolvia a ECMWF: MAE 4,67 kt, sesgo -4,56) a
**GDPS 15 km** (MAE 1,87, sesgo +0,14), con `cell_selection=sea` porque la celda anterior era de
tierra firme y la friccion hundia el viento. Campos nuevos en el contrato:
- **`horas[].rafagaNudos`** (puede venir null).
- **`pronostico[].rafagaNudosMin/Max`**.
- **`vientoNudosMin/Max` cambiaron de significado**: antes eran de la franja mediodia-tarde, ahora
  del DIA COMPLETO (24 h), que es lo que cubre la grilla horaria. Las señales del motor siguen
  usando la franja internamente, pero eso ya no viaja en el payload.

**Revision 4 (cierre del dia):** campo **`senalRacheado`** en cada dia de `pronostico[]`, con
`{ activa, texto, diferenciaNudos }`. `diferenciaNudos` viene SIEMPRE (null solo si el modelo no da
rafagas), este activa o no, y es el despegue maximo entre racha y sostenido **dentro de la franja
mediodia-tarde** — no del dia completo, porque una racha fuerte a las 4 AM no dice nada sobre como
va a estar para navegar. El umbral (9 kt) vive en `config/umbrales.php`, calibrable.

**Revision 5 (cierre del dia, segunda):** **`horas[]` pasa de 24 a 16 entradas (06:00-21:00)** —
"de 22hs a 5am descartar porque es el horario donde todos estan durmiendo y no se puede navegar de
noche". Los min/max del dia se recalculan solo sobre esa franja y **cambiaron de verdad**: el 03/09
paso de 3,5-15,6 a 3,5-12,1, porque ese maximo de 15,6 era de madrugada. La ventana vive en
`config/pronostico.php` (`hora_navegable_desde`/`hasta`) y es recalibrable. Efecto lateral bueno:
las rachas contiguas ya no pueden cruzar la medianoche.

**Endpoint nuevo `GET /modelos` (mismo dia):** evaluacion de acertividad de los 4 modelos contra
las mediciones de la estacion. **Separado de `/pronostico` a proposito**: el dashboard no toca la
base de datos y esto si, asi que si la base se cae el pronostico sigue andando y lo unico que falta
es ese panel. Devuelve `modelos[]` (ordenados de mejor a peor, con `enUso`, `acertividadPct`,
`errorMedioNudos`, `sesgoNudos`) y `metodo` (`toleranciaNudos`, `estacion`, `distanciaAlSpotKm`,
`horasEvaluadas`, `desde`/`hasta`).

**Revision 6 (cierre del dia, tercera):** correccion conceptual arrastrada desde el Analisis.
**"Birazon" no existe como termino** — se documento asi (con B) y se le invento una definicion
encima. El termino correcto es **virazon**: la brisa termica de tarde que entra desde el agua.
Ademas la implementacion estaba al reves: "brisa de calma" detectaba la PRECONDICION (viento de
fondo flojo a la tarde) y se apagaba justo cuando la virazon entraba de verdad, ademas de usar la
hora del reloj del servidor para los 4 dias. Cambios en `/pronostico`:
- **Se fueron** `senalBirazonBrisaCalma` y `senalBirazonBajante`.
- **Nuevas por dia**: `senalVirazon`, `senalTerral`, `senalOffshore` (con `horas`), `senalBajante`.
- **Nuevas por hora**: `offshore` (bool), `nubosidadPct`, `temperaturaC` (estas dos las usa el
  motor para detectar la virazon; el front las recibe y no las muestra).

**Revision 7 (cierre del dia, cuarta):** condiciones meteorologicas y verdad de lo transcurrido.
Campos nuevos por hora: `precipitacionPct`, `condicionCodigo` (**codigo WMO crudo** de Open-Meteo,
sin traducir — la decision de icono y texto es de Presentacion), y **`vientoMedidoNudos` /
`rafagaMedidaNudos`**, que son lo que efectivamente midio Pilote Norden en esa hora (`null` donde
no hubo reporte). `nubosidadPct` y `temperaturaC` ya venian pero nunca se habian mostrado.

**Revision 8 (cierre del dia, quinta):** **`config.margenAlLimiteNudos`** (hoy 3), calibrable en el
backend. Habilita el tercer estado de navegabilidad del front (ver decision 4bis).

**Revision 9 (cierre del dia, sexta):** el offshore pasa de avisar a **BLOQUEAR**. Textual de
Joaquin: "el viento de tierra es condicion justa y necesaria para no navegar". Sin cambio de
payload — `horas[].offshore` ya venia; cambia la interpretacion del front.

**Revision 10 (cierre del dia, septima):** cuatro correcciones de campo aportadas por Joaquin.
- **`senalBajante` cambio de significado**: antes disparaba con viento del **O/NO**, un sector que
  habia inventado el propio sistema. La bajante la causa el **NORTE**, y depende de la DURACION del
  viento sostenido, no de un promedio del dia. Suma `horasSostenidas`.
- **`senalCreciente`** (nueva): la contracara — sudestada sostenida hace crecer el rio.
- **`senalVientoDesparejo`** (nueva): con cualquier sudestada el viento no entra parejo cerca de la
  costa.
- **`senalRacheado` puede dispararse por SECTOR**: el SE de este spot entra arrachado por
  naturaleza y un modelo global no resuelve esa turbulencia, asi que se activa con SE >=10 kt
  aunque el despegue medido sea chico. El front NO distingue los dos disparos: el texto lo dice.

**Revision 11 (cierre del dia, octava):** calibracion de Norden al spot. Joaquin: "el pilote
siempre marca 2 o 3 nudos mas de lo que realmente hay en la tierra" — tiene sentido fisico, la
estacion esta a 20 km, en el medio del rio y sin rugosidad de superficie que frene el viento.
**Destapo un error silencioso del backend**: el motor venia usando la lectura cruda como "el viento
de hoy" para calcular las señales, asi que sudestada y demas umbrales disparaban con 2-3 kt de mas.
Ya corregido del lado del servidor. Campos nuevos:
- `estaciones[]`: **`vientoNudosSpot`** y **`rafagaNudosSpot`**.
- `horas[]`: **`vientoMedidoSpotNudos`**.
Los `*Spot` son `null` sin medicion y vienen clampeados a 0 (no hay vientos negativos).

### Decisiones de front que hay que respetar (P1, version 2)

**1. Las dos mareas NO son comparables — nunca mezclarlas.**
`estaciones[].mareaMetros` es una MEDICION del mareografo de CARP en Pilote Norden.
`horas[].mareaMetros` es un MODELO (Open-Meteo Marine) con el cero en el nivel medio del mar y
un punto de grilla a ~20 km al NE del spot. Ceros de referencia distintos, lugares distintos: es
normal que CARP diga 1,04 m y el modelo 0,11 m a la misma hora. Resolucion aplicada: viven en
bloques separados, cada uno con su etiqueta de origen visible en pantalla ("medida" / "modelo"),
la grilla presenta la marea como tendencia, y hay una nota explicita en la card. **Prohibido
aplicar un offset a una para acercarla a la otra** — eso seria fabricar un dato.

**2. Sin recomendacion de tamano de kite hasta que haya cuentas.**
Se saco el bloque "Recomendacion · equipo generico". Salia de una tabla de quiver generica de
config, no del usuario — Joaquin lo marco textual y tenia razon. En su lugar hay un CTA de login
(placeholder declarado de Etapa 2). No volver a mostrar un tamano de kite sin quiver real cargado.

**3. Rango navegable: anonimo, en localStorage, sin login.**
`lib/rango.ts`. Se pide la primera vez con un `<dialog>`, arranca en `config.rangoNavegableDefault`
(nunca hardcodeado en el front) y se puede cambiar despues desde el chip del header o el link de
la seccion de proximos dias. Todo acceso al storage va en try/catch (en modo privado el mero
`window.localStorage` puede tirar excepcion): si no hay storage se cae a una copia en memoria y la
UI avisa que la preferencia dura solo la sesion. Cambiar el rango re-renderiza con los datos que ya
estan en memoria, **sin volver a pegarle a la API**.

**4. Navegabilidad de TRES estados, fail-safe (`lib/navegabilidad.ts`).**
Desde el 2026-09-02 la navegabilidad dejo de ser booleana. Con `s` = sostenido, `r` = rafaga,
`[min, max]` = rango de la persona y `M` = `config.margenAlLimiteNudos`:
- **`navegable`**: `s` dentro de `[min, max]`.
- **`limite`**: `s < min` **y** `r >= min` **y** `(min - s) <= M`.
- **`no`**: el resto.

Viene del caso de Joaquin: "si mi rango es 16 a 28 y el viento actual es 14 con rafagas a 18-19, lo
considero un dia navegable (al limite)". Con navegabilidad booleana esos dias se perdian enteros.
El margen es lo que evita que un dia muerto de 5 kt con una racha aislada de 16 cuente como
navegable. **Aplica solo por abajo**: quedarse corto es una molestia, pasarse es un riesgo, asi que
`s > max` sigue siendo `no` y el techo no se estira.

`rango` y `margenAlLimite` viajan juntos en un objeto `Criterio` y no como dos argumentos sueltos:
el rango es de la persona (localStorage) y el margen del backend, pero a partir de la evaluacion
son una sola cosa.

**La disciplina fail-safe no se aflojo — al contrario.** El estado nuevo es mas permisivo por
diseño, asi que los caminos defensivos siguen cerrando hacia el lado seguro: dato faltante o no
numerico → `no`; dia bloqueado → ninguna hora cuenta; y **`rafagaNudos: null` NO puede dar
`limite`**, porque ese estado se sostiene enteramente sobre la racha. Ademas el fallback de
`margenAlLimiteDe()` es **0**, que desactiva el estado "al limite" por completo: ante un contrato
recortado se cae al comportamiento estricto de antes, no a un margen inventado.

**La navegabilidad se calcula sobre el viento SOSTENIDO, nunca sobre la rafaga sola.** Un dia de
12 kt sostenidos con rachas de 24 sigue marcando "sopla" / "se navega" y avisa aparte que esta
racheado. Es decision explicita de Joaquin (2026-09-02): el dia racheado se avisa, no se bloquea.
Tocar esto es un cambio de criterio de dominio, no un ajuste tecnico.

**5. Tags de racha.** "sopla" (hoy) y "se navega" (proximos dias) son la misma logica con etiqueta
distinta — un solo helper (`textoRacha`). El tag va sobre la racha CONTIGUA de horas navegables,
no repetido en cada hora suelta. Un dia puede tener varias rachas (caso real verificado: sabado
10-19 h, corte a las 20, y 21-22 h otra vez).

**6. Escalas del grafico.** Viento: escala compartida por los 4 dias (si no, un dia flojo y uno
bueno se dibujan igual y el grafico miente al compararlos). Marea: escala por dia (con escala
compartida, un dia de amplitud chica quedaba plano y se perdia lo unico que importa mirar ahi, si
sube o baja); la amplitud real del dia va en texto al lado del grafico.

**7. Layout de los proximos dias: una fila por dia, no 3 cards en grilla.** Con 24 horas de viento
+ 24 de marea por dia, una grilla de esa densidad dentro de una card de ~310px obligaba a
scrollear horizontalmente en tres lugares distintos incluso en desktop. En fila el grafico entra
entero; en mobile se apila y solo ahi scrollea.

**8. Tooltip propio en la grilla horaria (no el `<title>` nativo de SVG).**
El nativo tardaba ~1 s, no se podia estilar, apelmazaba los tres datos en una linea sin jerarquia
y —lo mas grave— en touch no existia, justo en el dispositivo con el que se mira el pronostico
antes de salir. El propio (`scripts/tooltip-horas.ts`) es un unico nodo colgado de `<body>` con
`position: fixed`: adentro del contenedor de la grilla quedaria recortado por el `overflow` en las
horas de los extremos. Se ancla al rect sensible de la hora, que abarca **todo el alto del
grafico**, asi por construccion nunca tapa la barra que se esta mirando; se ubica arriba y hace
flip a abajo si no entra, con clamp horizontal contra el viewport y una punta que sigue a la
columna aunque el cuerpo se haya clampeado. Interaccion: hover solo con mouse (en touch el
navegador emite un pointerover sintetico que lo abriria sin que nadie lo pida), tap para
mostrar/cerrar en touch, y teclado con **tabindex rotativo** — solo la hora activa es tabulable y
las flechas recorren el resto, asi los 96 puntos de datos de la pagina suman 4 paradas de
tabulacion en vez de 96. El tooltip es `aria-hidden` + `pointer-events: none`; la info para
lectores de pantalla viaja en el `aria-label` de cada hora, para no anunciarla dos veces.

**9. Viento sostenido y rafaga son DOS series, no un dato y su nota al pie.**
En la grilla la barra solida es el sostenido y la extension translucida de arriba llega hasta la
racha, con una tapa fina en el tope. Lo que hay que poder leer no es la racha sola sino la
DIFERENCIA: un dia de 12 kt con rachas de 14 no es el mismo dia que uno de 12 con rachas de 24, y
con una sola serie los dos se dibujaban identicos. Los rotulos que se usan en la UI
(`Velocidad viento` / `Rafagas`) son los de la tabla de CARP, para que se lean igual en el sitio
que en la fuente. El tope de la escala de viento contempla las rafagas, que son la serie mas alta
(23,7 kt contra 15,6 de sostenido en datos reales).

**10. Nombres de modelo en la UI: son dos modelos distintos.**
Viento y rafagas salen de **GDPS 15 km**; la marea, de **Open-Meteo Marine**. No decir
"Open-Meteo" a secas para el viento: el backend cambio de `best_match`/ECMWF a GDPS el 2026-09-02
tras validar contra 19 h de mediciones reales de CARP/Norden (MAE 4,67 → 1,87 kt).

**11. Badge de viento racheado: avisa, no bloquea.**
`senalRacheado` NO entra en el calculo de navegabilidad (ver decision 4). Se muestra como badge con
**tono propio (`racha`) y borde punteado**: el punteado lo emparenta con la extension de rafaga del
grafico —el dato que lo origina— y lo separa del rojo solido de `ConTemporal`, que si bloquea. El
requisito era explicito: que nadie lea "racheado" y crea que el dia esta cerrado. Verificado en el
caso donde conviven los dos badges en la misma card.
El umbral que decide `activa` vive en el backend (`config/umbrales.php`) y es calibrable: el front
no lo conoce ni lo replica. `diferenciaNudos` viene siempre (salvo modelo sin rafagas) y se muestra
aunque la señal NO dispare, en la card de hoy y en cada fila de dia — un dia con 8,3 kt de despegue
justo debajo del umbral conviene mirarlo con esa expectativa. Es el maximo de la franja
mediodia-tarde, no del dia completo, asi que se muestra a nivel DIA y no dentro del tooltip por
hora: mezclar ahi dos numeros de alcance distinto se prestaba a confusion.

**12. Nada de constantes de "24 horas": el ancho del grafico sale de `horas.length`.**
Habia un `const W = PAD_X * 2 + 24 * COL` que hubiera roto la grilla al pasar a 16 horas. Se
elimino: ancho, paso de rotulos (`Math.round(n / 7)`, apuntando a ~7 etiquetas) y el `min-width`
inline del SVG salen todos de la cantidad de horas que manda el backend. **No se cambio el 24 por
un 16** — la ventana es recalibrable desde `config/pronostico.php`. Verificado con series de 0, 1,
5, 16 y 20 horas: con 0 devuelve un SVG vacio pero valido en vez de dividir por cero.
`indiceHoraActual` ya devolvia -1 fuera de rango; confirmado que de noche (hora en curso fuera de
la ventana) no se dibuja la marca "ahora" y no rompe nada.

**13. El grafico tiene escala numerica y banda del rango.**
Los graficos compactos de los proximos dias no tenian ningun numero: se veia la forma de las barras
pero no si eran 5 o 25 kt — una silueta. Se agregaron guias horizontales con su valor en un gutter
izquierdo (dentro del SVG, no como columna aparte: el SVG escala con `width:100%` y una columna
externa se desalinearia en cada resize) mas la banda del rango de cada persona, que se re-renderiza
al cambiar el rango sin refetch. Las dos cosas se leen como FONDO, sin competir con las barras ni
con la extension de rafaga, que son el dato.
Caso delicado: la escala de viento es compartida entre los 4 dias, asi que el techo del rango puede
caer fuera del tope (maximo 30 kt sobre un grafico que llega a 25). Se clampea el rectangulo al tope
**y se omite la linea punteada superior** — sin linea se lee "sigue mas arriba"; dibujada en el
borde mentiria diciendo que el limite esta ahi. Si el rango entero queda por encima de la escala no
se dibuja banda, que es honesto: ninguna barra puede alcanzarlo.

**14. El panel de modelos no puede parecer mas seguro de lo que es.**
Es la restriccion que manda sobre el diseño de esa seccion, por encima de lo visual. Hoy la
evaluacion tiene **17 horas: un solo dia, una sola situacion sinoptica**, y los numeros salen
brutales (ECMWF 0,0 %, GDPS 82,4 %). Cada numero es correcto; presentarlos con un diseño confiado
y redondo seria mentir por presentacion. Implementado:
- el tamaño de la muestra es una stat-card del **mismo cuerpo tipografico** que los porcentajes
  (26px contra 22px, medido), nunca letra chica al pie;
- pildora de madurez + explicacion en prosa (`lib/madurez.ts`) de que tan en serio tomarse el
  ranking, con el rango de fechas al lado;
- mientras la muestra es chica las barras se dibujan **con trama** en vez de solidas: señal no
  verbal de "esto todavia se mueve", que desaparece sola cuando la muestra crece;
- **la distancia de la estacion al spot (20 km) va como stat**, no escondida: es un dato incomodo
  y es parte de la verdad. La estacion es la unica medicion real disponible (CARP publica solo 24 h
  y no se puede reconstruir historia hacia atras), y eso se dice en el detalle del metodo.
Los umbrales de la escala de madurez (72 h / 336 h) son una decision de PRESENTACION, no un
criterio estadistico — documentado como tal en el propio modulo, y el numero crudo de horas se
muestra siempre. **El mismo diseño tiene que aguantar con 17 horas y con 3.000**: verificado con
ambos extremos mockeados.
El hallazgo del sesgo compartido ("3 de los 4 modelos subestiman, por eso promediarlos da peor")
se **calcula sobre los datos**, no se escribe a mano, asi deja de mostrarse solo si deja de ser
cierto — verificado con un caso sin sesgo dominante, donde no aparece.

**15. El panel de modelos se pide aparte y sin bloquear.**
`scripts/modelos.ts` tiene ciclo de vida propio, separado de `dashboard.ts`, por la misma razon por
la que el backend separo el endpoint. Se dispara en `requestIdleCallback` **despues** del render
del pronostico y nadie lo espera (verificado el orden real de requests: `pronostico` antes que
`modelos`). Si falla, el dashboard ni se entera y la seccion muestra un aviso chico. La seccion
arranca `hidden` en el HTML y solo aparece cuando hay algo concreto que mostrar: nunca un esqueleto
colgado.

**16. El viento de tierra es la unica advertencia de riesgo FISICO del sitio.**
Todo lo demas —sudestada, racheado, virazon— habla de condiciones o de calidad de sesion.
`senalOffshore` habla de que te pasa si te quedas sin potencia: el viento te lleva rio adentro en
vez de devolverte a la orilla. Por eso NO es un badge mas en la fila de pildoras: va en un bloque
propio (`avisoSeguridad` en `lib/semaforo.ts`) con barra lateral, icono y kicker "Seguridad".
Su color es **ambar de advertencia y no el rojo** de "no se navega": el rojo ya significa otra cosa
en esta pantalla y reusarlo seria ambiguo.
**No bloquea la navegabilidad** — misma decision que el racheado: avisa, no prohibe. Verificado
que un dia con 11 horas offshore sigue en verde con su tag "sopla". Pendiente que Joaquin decida
si algun dia debe bloquear.
El **terral es un caso particular de offshore** (la brisa de tierra de la mañana): cuando los dos
estan activos se muestran como UN aviso con dos niveles, no como dos bloques diciendo casi lo mismo.
Ademas del badge del dia, **cada hora offshore se marca en la grilla** con una tira fina bajo la
linea base — no cambiando la barra, porque el dato de la barra es el viento y pisarlo con un
segundo significado lo volveria ilegible. Sirve para ver que la mañana esta offshore y la tarde no,
que es lo que decide a que hora ir. El tooltip de esa hora tambien lo dice.

**17. Virazon, no "birazon".**
El termino correcto es virazon y es la BUENA noticia del dia: la termica que hace navegable una
tarde que a la mañana parecia muerta. Se muestra como badge de oportunidad (tono `info`, la misma
familia que usaban las viejas señales). No quedan referencias vivas a `birazon` en el codigo — solo
la nota historica en `lib/api.ts`, deliberada, para que nadie vuelva a introducir el termino.

**18. La serie medida de Norden: tres trampas de datos, las tres visibles.**
Se dibuja lo que realmente paso encima del pronostico, en el grafico de hoy. Cada cuidado tiene
consecuencia visual concreta:
- **Los huecos NO se interpolan.** La serie tiene horas sin reporte (hoy faltan 09 y 10). Se dibuja
  como VARIOS tramos que cortan en cada hueco; una recta cruzandolo inventaria una medicion que no
  existio. Cada punto medido lleva su marca, asi un dato aislado entre dos huecos igual se ve
  (verificado con un caso de una sola medicion suelta: 1 punto, 0 polilineas).
- **Termina antes que la lectura "ahora"** del bloque de arriba (hoy la serie llega a las 11:00 y
  la lectura puntual es de las 14:06). Es una rareza de CARP —lectura puntual fresca, historial
  atrasado— y no una falla. La nota bajo el grafico dice hasta que hora llega, para que no se lea
  como que se rompio algo.
- **Norden esta a 20 km del spot**, mas adentro del rio y mas expuesto: lee sistematicamente mas
  alto. **Esa diferencia es REAL, no error del modelo** (hoy +3 a +6 kt en las horas de la mañana).
  Sin decirlo, las dos series juntas se leen como "el modelo le erra feo", conclusion equivocada.
  Mismo cuidado que con las dos mareas. La comparacion justa vive en el panel de acertividad, que
  le pide a cada modelo el pronostico en las coordenadas de Norden.
Si un dia no tiene ninguna medicion, **no queda ningun rastro**: ni linea, ni puntos, ni entrada de
leyenda, ni nota.

**19. El cielo va en el grafico; el detalle, en el tooltip.**
El grafico ya cargaba viento, rafaga, marea, banda de rango, offshore y ahora la serie medida. El
cielo entra como un carril de iconos arriba (uno por hora) mas la temperatura cada dos horas, en
tono apagado: es contexto, no el dato que se viene a buscar. Nubosidad, probabilidad de lluvia y
temperatura puntual quedan en el tooltip, que tiene lugar para decirlo con palabras. La traduccion
del codigo WMO a icono y texto vive en `lib/clima.ts` —un solo lugar— para que grafico y tooltip
digan exactamente lo mismo; los iconos se declaran como primitivas geometricas (circulos, paths,
lineas) en vez de SVG suelto, asi el grafico los dibuja con `createElementNS` sin innerHTML.

**20. Verde solido = pleno, verde hueco = al limite. El ambar esta tomado.**
Las horas `limite` se dibujan como barra verde con contorno y relleno tenue, y las pildoras de
racha que entran enteras al limite van huecas y punteadas. **No se uso ambar** aunque fuera la
eleccion intuitiva: el ambar ya significa viento de tierra / seguridad, que es un riesgo de otra
naturaleza, y reusarlo confundiria "el viento apenas alcanza" con "el viento te aleja de la costa".
Vocabulario final del grafico: verde solido = hora plena, verde hueco = entra por las rachas, gris
= fuera del rango, ambar = viento de tierra.
Una racha puede mezclar horas plenas y al limite; la pildora lo dice con un chip (`al limite` /
`parte al limite`) para que "sopla · 12 a 18 h" no se lea como si las siete horas fueran iguales.
El tooltip explica el porque y no solo la etiqueta: "Al limite: el sostenido no llega a tu minimo
de 16 kt, pero las rachas si". En el semaforo, un dia que entra SOLO al limite cae en amarillo
("Al limite"), no en verde.

**21. El viento de tierra BLOQUEA, a nivel hora.**
Desde el 2026-09-02 una hora con `offshore: true` es `no`, cortocircuitando el criterio de rango:
el viento puede estar impecable dentro del rango y la hora igual no cuenta. Es hermano de
`diaBloqueado` pero **a nivel HORA** — el offshore varia dentro del dia y esa granularidad es
justamente lo util (mañana descartada + tarde limpia = dia para ir a la tarde).
**El motivo tiene que distinguirse siempre.** Hay cuatro razones de "no se navega" (falta viento /
se pasa del maximo / dia bloqueado / viento de tierra) y confundir la ultima con "fuera de tu
rango" seria lo peor: alguien podria creer que ampliando su rango la desbloquea, cuando el rango no
tiene nada que ver. `motivoSinHoras` (en `lib/semaforo.ts`) es la unica fuente de ese texto y la
usan tanto la pildora del semaforo como el tag de racha vacia, para que no digan cosas distintas
del mismo dia. Ojo: la pildora decia "Fuera de tu rango" incluso con el dia caido por offshore —
se detecto verificando y se corrigio.
El ambar dejo de significar "ojo pero se navega" y paso a ser el "no" de esta causa. La tira ambar
bajo la linea base se mantuvo como **segundo canal**: ambar contra gris puede costar con vision
cromatica reducida. **El racheado sigue avisando sin bloquear** — ya no son equivalentes, y el
docblock de `SenalOffshore` que los equiparaba se actualizo.

**22. Los avisos del dia van agrupados por categoria, en orden fijo.**
Con cuatro señales nuevas encima del bloqueo, un dia malo junta seis avisos y una pila
indiferenciada no la lee nadie. Orden y tono hacen el trabajo:
1. **Seguridad** (viento de tierra): bloque aparte, ambar, arriba de todo. Innegociable que no
   quede sepultado — es el unico que descarta horas. Verificado por geometria que queda por encima
   de los badges.
2. **Riesgo de condiciones**: sudestada con temporal (rojo).
3. **Estado del RIO**: creciente y bajante (cian, familia del agua). Tercera categoria, distinta de
   las de viento: no hablan del viento sino de cuanta profundidad vas a encontrar. En Punta Lara el
   agua es poco profunda, asi que la bajante es informacion practica real. Mutuamente excluyentes.
4. **Calidad del viento**: racheado y viento desparejo (violeta punteado). Comparten tono a
   proposito — los dos dicen "el viento no va a ser lo que parece", y leerlos como una familia en
   vez de dos alarmas distintas es lo que evita el ruido.
5. **Oportunidades**: sudestada sin temporal, virazon. Al final.
`horasSostenidas` se muestra como chip **solo cuando la señal esta activa**: por debajo del umbral
el backend ya decidio que no vale la pena marcarlo, y sumarlo igual iria en contra de lo unico que
importa en esa seccion, que es que la lista siga siendo legible. Decision consciente contra el
criterio que se uso para `diferenciaNudos` del racheado, donde si hay un lugar natural (la
stat-card de rafagas) y no compite con nada.

**23. Medicion cruda vs. equivalente en el spot: son cosas distintas, y las dos se muestran.**
`vientoNudos` es un DATO MEDIDO; `vientoNudosSpot` es una INFERENCIA nuestra. Mismo criterio que
con las dos mareas — con una diferencia importante: aca **si hay una relacion conocida y declarada**
entre las dos cifras, asi que se pueden mostrar juntas siempre que quede claro cual es cual.
- **"Ahora en el rio"**: el numero grande es el ESTIMADO EN LA COSTA, porque para decidir si salir
  importa el viento del spot y no el de 20 km rio adentro. Lleva la leyenda "estimado en la costa"
  debajo y la rafaga el badge "ESTIMADA" — el mismo vocabulario de `MEDIDA` / `MODELO` que ya
  existia. La lectura cruda queda visible como respaldo ("Pilote Norden mide 14,9 kt · rafaga 17,3
  kt"): es la fuente, y su credibilidad viene de ser una medicion real.
- **Grafico**: se dibuja el EQUIVALENTE, no la cruda. Es el cambio con beneficio concreto — las dos
  series pasan a ser del mismo lugar y por lo tanto **comparables**, asi que la nota paso de
  defender la diferencia ("es real, no es error del modelo") a lo contrario: lo que quede de
  diferencia **si es error del modelo**, sin el sesgo de ubicacion tapandolo. Se aclara que es una
  estimacion y no una medicion.
- **Tooltip**: las dos, etiquetadas ("Estimado en la costa 8,7 kt" / "Medido en Norden 11,2 kt").
La magnitud de la correccion que aparece en la nota se **deriva de los datos** (diferencia entre las
dos series), no esta escrita a mano: si el backend la recalibra, el texto se actualiza solo.
Camino defensivo: sin equivalente, el bloque cae a la lectura cruda ETIQUETADA COMO TAL y el grafico
no dibuja la linea — mejor no dibujarla que dibujar una serie incomparable bajo una nota que afirma
que si lo es.


**24. El veredicto de HOY se recalcula siempre contra la hora actual, y el pasado no se borra.**
El bug que lo destapo: a las 22:30 el sitio seguia diciendo "Dia de kite" porque las horas
navegables existian en el dia, aunque ya hubieran pasado todas. `indiceHoraActual` devolvia `-1`
para dos situaciones OPUESTAS — reloj antes de la ventana (queda el dia entero por delante) y reloj
despues (no queda nada) — y quien lo consumia no podia distinguirlas. Se agrego
`desdeAhora(dia, ahora)`, que devuelve `0` antes de la ventana, el indice adentro y `horas.length`
despues; ese indice se enhebra hasta `evaluarEstado`, `rachasNavegables` y la grilla.
Tres reglas que salieron de ahi:
- **Solo HOY mira el reloj.** Los proximos dias se evaluan completos (`DIA_COMPLETO = 0`), porque
  para ellos "ya paso" no significa nada.
- **Recortar, no descartar.** Una racha empezada (reloj 15:40, racha 10-21) se muestra como
  `15 a 21`, no desaparece: sigue habiendo agua por delante.
- **El pasado se atenua, no se borra.** Las barras de horas idas llevan `.gh-pasado`, pero la serie
  MEDIDA nunca se atenua: es lo unico realmente observado del dia y sirve para calibrar el ojo
  contra el modelo. Verificado: `medidoAtenuado` da 0 en todos los relojes.
Caso nuevo que antes no existia: el dia que **se quedo sin horas**. Semaforo rojo "Hoy ya paso" y
tag "Las horas navegables de hoy ya pasaron — mira los proximos dias". Se distingue a proposito de
"Fuera de tu rango": no es que el dia fuera malo, es que llegaste tarde.
El refresco periodico entra por el mismo camino, asi que la pagina abierta se corrige sola al cruzar
la ultima hora navegable — no hace falta recargar.

**25. Un solo lugar decide POR QUE no se navega, y todas las superficies lo repiten.**
Auditoria de consistencia. Aparecio un caso concreto y peligroso: un dia con todas las horas
offshore mostraba "Fuera de tu rango", cuando el viento estaba perfectamente dentro del rango y lo
que lo descartaba era el viento de tierra. Se unifico en `motivoSinHoras(dia, criterio, desdeIdx)`,
que hoy alimenta **la pildora del semaforo, el tag de racha vacia y el `aria-label` del grafico**.
Los tres tienen que decir lo mismo o alguien decide con media informacion.
El `aria-label` ademas **recalcula sus rachas desde la hora actual**, a diferencia del dibujo: el
grafico pinta el dia completo (atenuando el pasado, ver 24) porque se ve de un vistazo cual tramo ya
paso, pero un texto leido en voz alta no tiene esa pista visual — anunciar "sopla de 06 a 21" a las
22:30 manda al agua a quien no ve la pantalla.
Otros hallazgos de la misma pasada, en orden de gravedad:
- **Colision de ambar cerrada.** La sudestada sin temporal usaba el tono `atencion` (ambar), el
  mismo del bloque de seguridad. Un aviso que es una OPORTUNIDAD estaba pintado con el color que
  significa "no se navega". Paso a `info` (azul) y el tono `atencion` se elimino del vocabulario:
  **el ambar hoy es exclusivamente seguridad**.
- **Texto en pantalla que contradecia el comportamiento** en "Como viene la semana": decia que se
  marcan navegables "las horas entre 9 y 30 nudos", cuando ya hay barras verdes huecas POR DEBAJO
  del minimo (al limite) y barras dentro del rango que se descartan por viento de tierra.
- Comentario de `semaforo.ts` que afirmaba que el offshore no bloquea (quedo de antes de la
  undecima pasada) y comentario equivalente en `global.css`.
- CSS muerto (`.ght-offshore*`, elemento borrado hace dos pasadas) y una regla `.gh-key--offshore`
  declarada dos veces con valores distintos.
Nota de metodo: las suites de regresion pasaron a **fijar el reloj** (`FIJAR_RELOJ` a las 05:00 del
dia de prueba). Desde que el veredicto depende de la hora, una suite sin reloj fijo cambia de
resultado segun cuando se corra, que es exactamente lo que una regresion no puede hacer.


**26. La direccion se dibuja en TODAS las horas, en los cuatro graficos.**
Antes salia una flecha cada `pasoEtiquetas` horas y en los tres dias siguientes ninguna
(`conFlechas: false`). Justificacion del cambio: desde que el viento de tierra BLOQUEA, la direccion
dejo de ser un adorno. Lo que se lee en esa fila no es el valor de una hora suelta — para eso esta
el tooltip con los grados exactos — sino el PATRON: cuando rota el viento a lo largo del dia. Una
flecha cada tres horas no muestra una rotacion, muestra tres muestras.
El problema real era de legibilidad, no de dibujar flechitas. Se resolvio asi:
- **Fila propia**, debajo de los rotulos de hora y encima del carril de marea, en el mismo lugar en
  los cuatro graficos. Al no superponerse a las barras, 16 flechas no le sacan forma al perfil.
- **Chicas y tenues.** Donde la direccion es constante quedan como textura pareja; donde rota, la
  rotacion salta sola. El tono sobre oscuro subio de .42 a .52 en la misma pasada: con una flecha
  cada tres horas era un detalle secundario, ahora tiene que poder leerse — sin competir con el
  verde de las barras.
- **La flecha offshore va en ambar**, apareada con la tira de esa misma hora. Son el mismo hecho
  dicho dos veces; pintarla gris obligaria a cruzar dos filas para entender una sola cosa. Encaja
  con el vocabulario consolidado en la decision 25: el ambar es seguridad y nada mas.
- **El atenuado del pasado tambien les aplica** (decision 24).
Costo: el compacto crecio de 120 a 130 px. Las tres filas de dias siguen entrando.
La flecha apunta HACIA DONDE sopla, no de donde viene (`anguloFlecha` suma 180 a la convencion
meteorologica de la API). **Ya no es un supuesto**: Joaquin lo confirmo el 2026-09-02 mirando la
pantalla contra el viento real. Era el ultimo supuesto abierto del proyecto.


**27. El peso del JS estaba en ScrollTrigger, no en el fondo animado ni en GSAP duplicado.**
Se pidieron tres mejoras de performance con una condicion explicita de Joaquin: "me gusta el fondo
animado, conservarlo pero mejor rendimiento". Medidas una por una, DOS DE LAS TRES no movian la
aguja, y conviene que quede escrito para no volver a intentarlas:
- **GSAP duplicado: falso positivo.** La evidencia era que `quickSetter` aparecia en los dos
  bundles. Pero ScrollTrigger LLAMA a `gsap.quickSetter`, asi que el string aparece sin que el core
  este copiado. Con marcadores exclusivos del core (`staggerTo`, `globalTimeline`, `registerEffect`)
  quedo claro: aparecen UNA sola vez, en el chunk compartido. Rollup ya deduplicaba. Forzar
  `manualChunks` para GSAP subio el total de 177.248 a 177.812 bytes, complejidad de config por
  -564 bytes. **Revertido.**
- **Diferir el canvas: sin beneficio.** `wind-bg.js` pesaba 69,8 KB con 5,4 KB de codigo propio
  porque es el chunk COMPARTIDO donde Rollup hoisteo el core de GSAP (lo necesitan las dos entradas:
  reveal/tilt en BaseLayout, dashboard en index). Separar `setWindAngle` del loop no bajaria nada:
  el core sigue haciendo falta para el dashboard. El fondo nunca fue lo pesado, el bundle solo
  llevaba su nombre.
- **Fuentes: real, pero el costo es de DEPLOY, no del visitante.** Ver decision 25 del README.
El costo real estaba en otro lado: **ScrollTrigger, ~42 KB, el 24% de todo el JS, con un unico
consumidor** (`reveal.ts`) para un fade-in que IntersectionObserver hace nativo. Se reemplazo
conservando GSAP para la animacion, asi que el easing y la consistencia con el resto del sitio no
cambian. JS total: 177.248 a 134.679 bytes. Lighthouse performance 79 a 83, Speed Index 3,6 s a
2,7 s. El fondo animado quedo intacto, como se pidio.
Trampa documentada en la decision 24 del README: un elemento por ENCIMA del viewport no intersecta,
asi que un IntersectionObserver ingenuo lo dejaria en `opacity: 0` para siempre. ScrollTrigger lo
cubria gratis porque compara scroll, no visibilidad.


**28. La card se reordeno alrededor de la pregunta que contesta.**
Joaquin cambio la prioridad del producto: "no me importa que los min/max de viento y rafagas sean
del dia que ves en el grafico. Me importa mas el detalle de hora a hora del viento y estado actual.
Sobre todo los dias navegables". No era un ajuste cosmetico sino una reordenacion de jerarquia.
La medicion que justifica el cambio, en 390x844 (mobile, que es donde se decide):

| | antes | despues |
|---|---|---|
| veredicto (que horas se navega) | y=1065 (fuera de pantalla) | **y=371** |
| grafico hora por hora | y=875 | **y=537** |
| estado actual del rio | y=371 | y=772 |
| min/max del dia | y=767 | y=1212 |

O sea: lo que menos le importa estaba 300px POR ENCIMA de la respuesta que la pantalla existe para
dar, y la respuesta no entraba en la primera pantalla.
El veredicto (`veredictoDelDia`) dice tres cosas en tamaño decreciente: kicker ("Hoy se navega" /
"Se navega ahora" / "Hoy no se navega"), titular con EL HORARIO ("14 a 19 h") o el motivo corto, y
una linea de contexto ("6 horas - pico 17 kt - 2 ventanas"). Las ventanas en detalle se listan solo
si hay MAS DE UNA. No decide nada nuevo: se apoya en `rachasNavegables` y `motivoSinHoras`, las
mismas fuentes de la pildora y del `aria-label` (decision 25), asi que las cuatro superficies no
pueden contradecirse. Hereda gratis el recorte por reloj de la decision 24: dentro de una ventana el
kicker pasa a "Se navega ahora" y el titular se recorta a lo que queda.
**Vocabulario de color respetado sin excepciones:** el veredicto tiene dos estados y ninguno es
ambar. `ok` verde; `no` NEUTRO a proposito, porque el ambar es viento de tierra y nada mas, y un
"no" puede ser por falta de viento. El bloque de seguridad quedo pegado al veredicto: la posicion
mas visible que tuvo nunca.
**Nada se borro.** Los min/max bajaron de stat-cards con borde a una tira rotulo+valor; la leyenda
(nueve claves, cuatro renglones) paso a `<details>` plegable; la nota de la serie medida se movio
debajo del bloque del rio, donde explica las dos cifras que ese bloque muestra.
En la semana la fila arranca por el veredicto en vez de por la fecha y el rango: se recorre por la
izquierda leyendo solo "que dia sirve". La columna de info crecio de 232 a 320px porque a 232 el
bloque de seguridad se partia en renglones de tres palabras.


**29. El despegue pasa a mezclar medicion y pronostico; los min/max salen de pantalla.**
Pedido de Joaquin: "Velocidad viento / Rafagas: no mostrar. Mostrar solo el despegue de viento que
viene teniendo el dia y promediarlo con lo pronosticado para las proximas horas".
`despegueDelDia(dia, desdeIdx)` promedia, hora por hora:
- horas ya transcurridas CON medicion → `rafagaMedidaNudos - vientoMedidoNudos`;
- horas por delante → `rafagaNudos - vientoNudos`.
Vive en el front porque el corte entre las dos fuentes es el reloj del visitante.
**Ponderado por cantidad de horas, no 50/50 entre fuentes**: con 10 medidas y 2 por delante,
promediar los dos promedios le daria a esas 2 el mismo peso que a las 10. Como cada hora entra como
una muestra suelta, el promedio de todas las muestras YA es el ponderado — no hay aritmetica de
pesos que mantener.
**Una hora pasada SIN medicion no aporta nada.** No es "lo que vino pasando" ni "lo que queda", y
rellenarla con pronostico seria colar pronostico viejo en la mitad observada del numero. Por eso el
`title` declara cuantas horas entraron de cada lado: sin eso, un dia con la estacion caida daria un
numero mas flaco sin que se note. Misma disciplina que con las dos mareas y con la correccion al
spot — el numero mezcla fuentes y eso tiene que poder saberse.
Tres casos salen sin ramas especiales: dia futuro (`desdeIdx = 0`) da puro pronostico; hoy sin
mediciones, lo mismo; hoy ya pasado (`desdeIdx = horas.length`) da puro observado. Sin rafagas en el
modelo el item se esconde entero, rotulo incluido.
Verificado con un dia armado para que el despegue medido sea 2 kt y el pronosticado 8 kt: da
8,0 → 5,8 → 3,5 → 2,0 segun avanza el reloj.
**Los min/max de viento y rafagas salieron de pantalla** (un paso mas que la decision 27, que solo
los habia bajado de rango). Direccion y marea se quedan. **Efecto colateral a registrar:
`despegueMaximoNudos` se quedo SIN CONSUMIDOR en el front** — sigue en el payload y sigue siendo
valido, pero ya no se dibuja. `textoDespegue` se reescribio sobre el promedio nuevo y
`extremosRafaga` se borro por quedar sin uso.


**30. Cambio de BASE de comparacion en el panel de modelos: el lado "medido" dejo de ser medido.**
Revision de contrato del 2026-09-02. Antes se le pedia a cada modelo el pronostico en las
coordenadas de Norden y se comparaba contra la lectura CRUDA de Norden. Ahora se le pide en las
coordenadas DEL SPOT y se compara contra el equivalente estimado en la costa (Norden - 2,5 kt).
Consecuencia de fondo: **no hay sensor en Punta Lara, asi que el lado de referencia es una
INFERENCIA**, igual que `vientoNudosSpot` en `estaciones[]`. Todo el copy que decia "lo que midio la
estacion", "del viento medido" o "es la unica medicion real" quedo incorrecto. Peor: el primer
parrafo del metodo afirmaba exactamente lo contrario de lo que ahora pasa ("las coordenadas exactas
de la estacion, no las del spot"), asi que se rehizo entero.
Tres campos nuevos en `metodo`:
- `compara` — frase del backend con que se compara contra que. **Se muestra tal cual.** Tenerla
  escrita a mano en el markup fue lo que dejo el panel mintiendo cuando cambio la base; ahora la
  fuente de verdad de lo que el panel puede afirmar viene con el dato.
- `medicionEsEstimada` — bandera de COMPORTAMIENTO. El dia que haya sensor en el spot pasa a
  `false` y el panel dice "medido" solo. Ausente ⇒ se asume `true`: llamar "estimado" a una
  medicion subvende el dato, llamar "medido" a una inferencia lo falsea.
- `correccionEstacionNudos` — los nudos que se restan. NO es un valor medido y el panel lo dice.
El `<details>` cuenta la cadena completa y aclara que los 2,5 kt son conocimiento de campo. Hay DOS
versiones del parrafo de la cadena, elegidas por dato: sin correccion que explicar la larga imprimia
"se le restan — —" y, con un sensor propio, habria afirmado algo falso. Se encontro probando el
contrato recortado y el caso `medicionEsEstimada: false`.
**Matiz que si se conto y matiz que no.** SI: comparar contra un estimado agrega algo que validar —
si la correccion estuviera mal calibrada, TODOS los modelos mostrarian sesgo del mismo lado Y de
tamaño parecido (las dos condiciones importan: mismo signo con magnitudes distintas apunta a error
de los modelos). NO: que la correccion estrecho los sesgos respecto de la base vieja. Es cierto,
pero son dos muestras de tamaño y periodo distintos, y afirmarlo con 25 horas es justo lo que este
panel existe para no hacer; ademas hardcodear los valores viejos los congelaria en el copy.
La serie arranco de nuevo, el panel volvio a 25 horas y a "Muestra inicial". La madurez lo maneja
sola. Con esa muestra GDPS dejo de ser el mas acertado y el panel NO editorializa sobre eso.


## Historial de ajustes
- 2026-09-01: Scaffold inicial del repo PHP creado en `C:\Sistemas\kite-punta-lara` (estructura de carpetas, composer, conexion a datos, mailer PAT-007 reutilizado, helper CSRF, migraciones SQL sin aplicar, config de umbrales/equipo con placeholders declarados explicitamente). `composer install` corrido y smoke test local exitoso (`GET /` responde 200, maneja el error de conexion sin datos configurados). Git inicializado, sin commits todavia.
- 2026-09-02: Migraciones aplicadas contra MySQL local de desarrollo, `pdo_mysql` habilitado en el PHP local. Cambio de arquitectura a pedido del cliente: Presentacion pasa a Astro (repo `kite-punta-lara-front`, pendiente de generar con el agente astro-front), este repo pasa a exponer solo `GET /pronostico` como JSON. Implementada la Etapa 1 completa del backend: `CacheService`, `PronosticoService` (Open-Meteo), `ConsolidadorEstacionesService` (CARP funcionando de verdad — estacion Pilote Norden via `meteo.comisionriodelaplata.org`, requirio CA bundle propio y desactivar verificacion TLS solo para ese host por su certificado roto/TLS legacy, confirmado con Joaquin; SMN sigue bloqueado por Cloudflare), `MotorDeCalculoService`, `PronosticoController`. Verificado end-to-end con `curl` — respuesta real con viento en vivo, recomendacion de equipo y señales de birazon/sudestada funcionando.
- 2026-09-02 (implementador-astro-front): Creado el repo `C:\Sistemas\kite-punta-lara-front` (Astro 7.2 estatico, CSS plano con tokens, Inter, astro-icon, GSAP) con **P1 completa** consumiendo `GET /api/pronostico` del backend PHP. Sistema de diseño heredado de `olvidatasoft-new` (sitio propio del estudio) por pedido explicito, extendido con la escala del semaforo, `tabular-nums` en todo dato numerico y superficies glass sobre la banda oscura del hero. Fondo de canvas adaptado del `network-bg.ts` del estudio a rachas de viento que se orientan con la direccion real del dia. Criterio del semaforo definido aca (no venia de Diseño) y documentado en `lib/semaforo.ts`. Verificacion real con Playwright: datos reales del backend, click real en "Actualizar" (confirmado un request nuevo a la API), hit-test de `elementFromPoint` en los 3 botones (nada decorativo tapa clicks), badges de sudestada/birazon y caida de estacion/API ejercitados via intercepcion de ruta, mobile 390px sin desborde horizontal, `prefers-reduced-motion`, cero errores de consola y cero requests fallidas. Lighthouse sobre el build servido con proxy prod-like: performance 91 / accesibilidad 100 / best practices 100 / SEO 100 (los dos fallos iniciales — contraste del semaforo y falta de robots.txt — se corrigieron midiendo los ratios, no a ojo). Repo agregado al workspace y commiteado.
- 2026-09-02 (implementador-astro-front, segunda pasada): Adaptado el front a la revision del contrato de la API (`navegable`, `estaciones[].direccionTexto`, `timestamp` ISO 8601 con offset). Se borro `sectorDesdeGrados()` de `lib/formato.ts` (ya no hace falta duplicar la conversion grados→sector) y `esNoRecomendable()` de `lib/semaforo.ts` (ya no hace falta parsear el texto de la recomendacion); `parseTimestampLocal()` paso a ser `parseTimestamp()` con parser nativo. Verificado con Playwright contra datos reales y con 4 escenarios mockeados: (a) `navegable: false` con un texto de recomendacion que NO dice "No recomendable" ("Sin viento util") ahora da rojo correctamente — con el parser viejo hubiera dado verde, que era exactamente el riesgo reportado; (b) contrato sin el campo `navegable` da rojo (fallo ruidoso), nunca un falso "Dia de kite"; (c) `navegable: true` contradicho por `senalSudestada: 'ConTemporal'` da rojo con su badge; (d) estacion disponible pero sin direccion oculta la flecha en vez de apuntar al norte por default. **Test de zona horaria** (el que prueba que el offset se respeta): la misma medicion rinde "hace 16 min" identico en America/Argentina/Buenos_Aires, Europe/Madrid y Asia/Tokyo, mientras la hora local mostrada en el tooltip se corre correctamente (00:36 / 05:36 / 12:36) — con el parser viejo el "hace" se hubiera corrido tantas horas como la diferencia de zona. Cero errores de consola, cero requests fallidas, `astro check` y `npm run build` limpios. Sin cambios visuales (Lighthouse no se repitio, no habia motivo).
- 2026-09-02 (implementador-astro-front, tercera pasada — rediseno de P1): Front migrado a `kite-punta-lara/front` (monorepo con remoto GitLab; el repo hermano viejo quedo abandonado por un lock de archivos). Adaptado al contrato nuevo (`config`, `horas[]` de 24 entradas x 4 dias, `rafagaNudos`/`mareaMetros` en estaciones, marea min/max por dia; se fueron `recomendacionEquipo` y `navegable`). Nuevo en el front: `lib/rango.ts` (rango navegable anonimo en localStorage, con fallback en memoria y aviso en UI si el storage esta bloqueado), `lib/navegabilidad.ts` (horas navegables + rachas contiguas, todo fail-safe), `scripts/grafico-horas.ts` (SVG de 24 h con barras de viento + linea de marea, construido con createElementNS, sin colores propios — se pinta por clase desde global.css para rendir sobre oscuro y sobre claro), `components/DialogoRango.astro`. Card de HOY reestructurada: bloque "ahora en el rio" con viento + rafaga + direccion + marea medida + hora de CARP, grilla horaria debajo con tags "sopla" sobre las rachas, y CTA de login en lugar de la vieja recomendacion generica. Proximos dias pasaron de 3 cards en grilla a una fila por dia (la densidad de 48 series por dia no entraba en una card de 310px sin scroll anidado). Verificado con Playwright contra datos reales + casos borde: primera visita abre el dialogo, cambiar el rango re-renderiza sin refetch (medido: 1 request antes y despues), rango invalido no cierra el dialogo, rango sin match deja los 4 dias en rojo con 0 barras navegables, persistencia entre recargas, localStorage bloqueado (render intacto + aviso), ConTemporal bloquea horas con viento en rango, senalSudestada desconocida bloquea igual y muestra badge explicativo, sin estaciones cae al pronostico del dia sin inventar medicion, API 503 muestra error sin skeleton colgado y el chip de rango sigue accesible si habia uno guardado, mobile 390px sin desborde de pagina con la grilla scrolleando dentro de su caja. Cero errores de consola y cero requests fallidas (el unico error visto bajo storage bloqueado sale del dev toolbar de Astro, no del codigo: verificado ausente en el build de produccion). `astro check` y `npm run build` limpios. **Sin commitear a pedido: los cambios quedan en el working tree para que Joaquin revise (es el repo con remoto).**
- 2026-09-02 (implementador-astro-front, cuarta pasada — tooltip propio + rafagas): (1) **Tooltip propio de la grilla horaria** (`scripts/tooltip-horas.ts`), reemplaza al `<title>` nativo de SVG: nodo unico en `<body>` con `position: fixed`, anclado a la columna completa (nunca tapa la barra), flip arriba/abajo y clamp contra el viewport con punta que sigue a la columna; hover con mouse, tap en touch (toggle + cierre al tocar afuera), teclado con tabindex rotativo (4 paradas de tab para 96 horas, flechas/Home/End para recorrer, Escape para cerrar); `aria-hidden` + `pointer-events:none`, con la info accesible en el `aria-label` de cada hora. Jerarquia: hora como encabezado, viento sostenido como dato protagonista, rafaga, direccion con grados exactos, marea etiquetada como modelo con tendencia sube/baja, y estado de navegabilidad que ahora distingue tres motivos distintos de "no se navega" (dia bloqueado por riesgo / falta viento / se pasa del maximo) donde antes decia un unico "fuera de tu rango". (2) **Rafagas como serie de primera clase**: extension translucida sobre la barra de sostenido con tapa en el tope, en los 4 graficos; minima y maxima del dia visibles en la card de hoy (dos stat-cards con los rotulos de CARP "Velocidad viento" / "Rafagas") y en cada fila de los proximos dias; rafaga sumada al tooltip y al aria-label; escala del grafico ampliada para contemplarlas. (3) Nombres de modelo corregidos en UI: viento/rafagas = GDPS 15 km, marea = Open-Meteo Marine. (4) **Bug de contraste preexistente corregido**: `.btn-primary` era blanco sobre `#2B9DE4` = 2,98:1, por debajo de AA — venia desde que se agrego el dialogo de rango y no se habia detectado porque no se habia vuelto a correr Lighthouse. Se agrego el token `--accent-fuerte` (#0f72b8, 5,10:1 medido) para los usos del acento que llevan texto sobre superficie clara, conservando el `#2B9DE4` de marca en todo lo decorativo y sobre fondo oscuro, donde ya cumplia. Verificado con Playwright: hover/tap/teclado, bordes de la grilla (horas 00 y 23 dentro del viewport), dia bloqueado por ConTemporal y por señal desconocida, hora con `mareaMetros` null, dia entero con `rafagaNudos` null (extremos dicen "sin dato", no se dibuja extension, el tooltip oculta la fila), mobile 390px sin desborde, cero errores de consola. Lighthouse sobre el build: **a11y 100 / BP 100 / SEO 100**, performance 88 estable (era 89-90 antes de la segunda serie; el resto de la variacion es ruido de maquina, medido en 5 corridas). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, quinta pasada — aviso de viento racheado): Joaquin decidio sobre la pregunta que el propio agente habia levantado en la pasada anterior (si la rafaga debia afectar la navegabilidad): **avisa pero no bloquea**. Implementado: campo `senalRacheado` en el tipo del contrato; badge nuevo con **tono propio `racha` y borde punteado** (el punteado lo emparenta con la extension de rafaga del grafico y lo separa del rojo solido de `ConTemporal`, que si bloquea), icono `fa6-solid:wave-square` — "irregular", no "peligro"; `diferenciaNudos` mostrado a nivel dia en la card de hoy (bajo la stat-card de Rafagas) y en cada fila de dia, tambien cuando la señal NO dispara. **El criterio de navegabilidad no se toco**: se verifico explicitamente que un dia con la señal activa sigue en verde "Dia de kite" con su tag "sopla". Verificado con Playwright los tres escenarios pedidos (`activa: true`, `activa: false` con `diferenciaNudos` presente, `diferenciaNudos: null`) mas el caso de convivencia racheado + `ConTemporal`, donde los dos badges aparecen juntos y se distinguen (rojo solido vs. violeta punteado) — mas regresion completa de las tres suites anteriores (tooltip, rafagas/extremos, rango/persistencia/storage/API caida). Contraste del badge nuevo medido, no estimado: 6,48:1 en claro y 9,82:1 sobre la card glass; se corrigio de paso el texto de despegue sobre oscuro, que a `.4` de alpha daba 3,82:1 (subido a `.55` → 6,11:1). Cero errores de consola en todas las corridas. Lighthouse sobre el build: **a11y 100 / BP 100 / SEO 100**, performance 86 (dentro del ruido habitual de 82-90 medido en esta maquina). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, sexta pasada — franja 06-21 + escala y banda en el grafico): (1) **`horas[]` paso de 24 a 16 entradas (06:00-21:00)**, pedido de Joaquin ("de noche no se puede navegar"). Se elimino la constante `const W = PAD_X * 2 + 24 * COL` que hubiera roto la grilla: ancho, paso de rotulos y `min-width` inline del SVG salen ahora de `horas.length`. **No se reemplazo el 24 por un 16** — la ventana vive en `config/pronostico.php` y es recalibrable. Verificado con series de 0, 1, 5, 16 y 20 horas; con 0 devuelve un SVG vacio pero valido. Confirmado que de noche (hora en curso fuera de la ventana) `indiceHoraActual` da -1 y no se dibuja la marca "ahora" sin romper nada. Geometria reajustada aprovechando las 8 columnas liberadas: COL 32→44, barras 17→24, gutter izquierdo de 30px para el eje. (2) **Escala numerica y banda del rango en el grafico** ("Como viene la semana debe mostrar rango de viento en el grafico", que al preguntarle resulto ser las dos cosas): guias horizontales con su valor + unidad en el gutter, y banda del rango de la persona pintada como fondo, en los 4 graficos. La banda se re-renderiza al cambiar el rango sin refetch (medido: 1 request antes y despues, y la banda se mueve de y=12/alto=32 a y=38/alto=16 al pasar de 9-30 a 4-12). Techo fuera de escala resuelto clampeando al tope y omitiendo la linea superior; rango entero fuera de escala no dibuja banda. Se agrego leyenda a la seccion de proximos dias, que no tenia ninguna. (3) Se corrigio un bug propio de los scripts de verificacion (no del sitio): `addInitScript` serializa la funcion y corre en la pagina, asi que el closure con el rango no viajaba y el dialogo quedaba abierto interceptando los clicks. Regresion completa de las cuatro suites (tooltip, rafagas, racheado, general) — el test de tooltip tambien se despego del indice 23 hardcodeado. Cero errores de consola. Lighthouse sobre el build: **a11y 100 / BP 100 / SEO 100**, performance **90** (subio desde 86-88: 8 columnas menos por grafico son ~200 nodos SVG menos en la pagina). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, septima pasada — panel de acertividad de modelos): Feature nueva pedida por Joaquin: "quiero poder ver desde la web la acertividad en % de los distintos modelos, para que el usuario vea que modelos se evaluan, cual es el utilizado y por que". Construido `components/PanelModelos.astro` + `scripts/modelos.ts` + `lib/madurez.ts`, consumiendo el endpoint nuevo `GET /api/modelos`. **La restriccion que mando sobre el diseño fue de honestidad, no visual**: con 17 horas de evidencia (un solo dia) y numeros brutales (ECMWF 0,0 %, GDPS 82,4 %), un diseño confiado hubiera mentido por presentacion. Resuelto con: stat-card de horas evaluadas del mismo cuerpo que los porcentajes (26px vs 22px, medido), pildora de madurez con explicacion en prosa, barras con trama mientras la muestra es chica (desaparece sola al crecer), y la distancia de la estacion al spot (20 km) como stat visible y no como letra chica. El hallazgo del sesgo compartido se calcula sobre los datos en vez de escribirse a mano. Metodo explicado en lenguaje llano dentro de un `<details>`: por que se pide a cada modelo las coordenadas exactas de la estacion y no las del spot, que significa la acertividad (± tolerancia, margen elegido por nosotros, dicho explicitamente), y que significa el sesgo. Carga asincrona en `requestIdleCallback` despues del pronostico, con ciclo de vida propio: si la base se cae el dashboard ni se entera. Verificado con Playwright: datos reales, orden real de requests (`pronostico` antes que `modelos`), `modelos: []` (aviso claro, sin tabla vacia), endpoint 503 (aviso, dashboard intacto), `acertividadPct: 0` (track visible, se lee como cero legitimo y no como dato faltante), muestra de 180 h y de 3.120 h (el mismo diseño aguanta: pildora verde, barras solidas, hallazgo que desaparece), caso sin sesgo dominante, mobile 390px sin desborde. Regresion completa de las suites anteriores. Cero errores de consola. Lighthouse sobre el build: **a11y 100 / BP 100 / SEO 100**, performance 87. Hallazgo tecnico reutilizable: **el CSS scoped de un componente Astro NO alcanza a nodos creados con `createElement` en runtime** (el scoping es por un atributo `data-astro-cid-*` inyectado en build), asi que todo nodo que necesite los estilos del componente tiene que salir del `<template>`, no del script. `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, octava pasada — virazon, terral y offshore): Correccion conceptual del backend arrastrada desde el Analisis ("birazon" no existe; el termino es **virazon**) mas dos señales nuevas de viento de tierra. Del lado del front: (1) tipos actualizados — se fueron `senalBirazonBrisaCalma`/`senalBirazonBajante`, entraron `senalVirazon`, `senalTerral`, `senalOffshore` (con `horas`) y `senalBajante`, mas `offshore`/`nubosidadPct`/`temperaturaC` por hora. (2) **Virazon como oportunidad**: badge de tono `info`, la misma familia visual que usaban las viejas señales, ubicado al final de la lista de badges para no arrancar en tono optimista si el dia tiene reparos que leer primero. (3) **Offshore/terral como advertencia de SEGURIDAD**, no como badge: bloque propio con barra lateral, icono y kicker "Seguridad", en ambar y no en rojo (el rojo ya significa "no se navega" en esta pantalla y reusarlo seria ambiguo). El terral entra como sub-linea del offshore cuando ambos estan activos, no como segundo aviso. (4) **Marca por hora en la grilla**: tira fina ambar bajo la linea base en las horas offshore, mas la linea correspondiente en el tooltip y en el `aria-label` — permite ver que la mañana esta offshore y la tarde no, que es lo que decide a que hora ir. (5) El bloque de seguridad se movio **antes** del CTA comercial: una advertencia de riesgo fisico no puede leerse despues de un llamado a la accion. **El criterio de navegabilidad no se toco**: verificado que un dia con 11 horas offshore sigue en verde con su tag "sopla". Verificado con Playwright: datos reales (dia 0 sin offshore, dia 1 con 7/16 horas, dia 2 con 2/16 + terral, dia 3 con 11/16 + terral), virazon activa mockeada (badge + semaforo "Con reservas"), offshore parcial (mañana marcada, tarde limpia), offshore + terral + sudestada + racheado juntos (cuatro cosas que se leen distinto: badge rojo, badge violeta, bloque ambar de seguridad, y el terral como sub-linea), `horas: 0` con `activa: false` (sin aviso ni marcas), terral solo, tooltip en hora offshore vs. hora limpia, mobile 390px sin desborde. Regresion de las suites anteriores con mocks de la forma vieja: pasan, ejercitando los caminos defensivos (`?.activa` sobre señales ausentes). Cero errores de consola. Lighthouse: **a11y 100 / BP 100 / SEO 100**, performance 81 (dentro del ruido 81-90 medido en esta maquina). Sin referencias muertas a las señales viejas — solo queda la nota historica deliberada en `lib/api.ts`. `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, novena pasada — cielo por hora + serie medida de Norden): (1) **Condiciones meteorologicas en el grafico**, pedido de Joaquin ("¿estas consultando si va a estar soleado, nublado? deberiamos mostrarlas"). `nubosidadPct` y `temperaturaC` ya venian sin mostrarse; se sumaron `precipitacionPct` y `condicionCodigo` (codigo WMO crudo). Nuevo `lib/clima.ts` traduce el codigo a categoria + etiqueta + icono, con los iconos declarados como primitivas geometricas para que el grafico los dibuje con `createElementNS` sin innerHTML y el tooltip reuse lo mismo. Carril de iconos arriba del grafico (uno por hora) + temperatura cada dos horas, en tono apagado; el detalle (nubosidad, lluvia, temperatura puntual) va al tooltip. Verificado que renderizan las 7 categorias (despejado, parcial, nublado, niebla, lluvia, nieve, tormenta) y que con `condicionCodigo: null` no se dibuja ningun icono. (2) **Serie medida de Pilote Norden superpuesta al pronostico** en el grafico de hoy, con las tres trampas del dato resueltas y visibles: huecos sin interpolar (tramos cortados + punto por medicion; verificado con hueco real 09-10 → tramos [3] con el punto de las 11 suelto, y con un caso mockeado de hueco al medio → tramos [3,2]), serie que termina antes que la lectura "ahora" (la nota dice hasta que hora llega, para que no parezca una falla), y la aclaracion de que Norden esta a 20 km y lee sistematicamente mas alto — **esa diferencia es real, no error del modelo**, mismo cuidado que con las dos mareas. Dia sin ninguna medicion no deja rastro: ni linea, ni puntos, ni leyenda, ni nota (verificado). (3) Ajuste de geometria: el grafico paso de 156 a 180px de alto para el carril de cielo, con aire explicito entre la temperatura y las etiquetas de valor de barra —que con la barra mas alta posible caen en `vientoTop - 5`— porque se tocaban en dias de viento fuerte, que es justo cuando mas se miran los numeros. Verificado con Playwright: datos reales, hueco + corte, sin medicion alguna, medicion aislada, `condicionCodigo: null`, tooltips en hora con medicion / en hueco / futura, mobile 390px sin desborde. Regresion completa de las suites anteriores (general, tooltip, señales). Cero errores de consola. Lighthouse: **a11y 100 / BP 100 / SEO 100**, performance 80 (dentro del ruido 80-90 medido en esta maquina). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, decima pasada — navegabilidad de tres estados): Cambio de nucleo pedido por Joaquin: "si mi rango de viento es de 16 a 28 nudos y el viento actual es de 14 con rafagas a 18-19 nudos, lo considero un dia navegable (al limite)". La navegabilidad dejo de ser booleana y paso a `navegable` / `limite` / `no`, con `limite` = sostenido por debajo del minimo pero rachas que si llegan y faltante dentro de `config.margenAlLimiteNudos` (hoy 3, calibrable). **Solo por abajo**: `s > max` sigue siendo `no`. Refactor asociado: `rango` + `margen` viajan juntos en un objeto `Criterio` que reemplaza al `RangoNavegable` suelto en `evaluarEstado`, `rachasNavegables`, `construirGrafico` y el resto de la cadena — eran dos parametros que siempre iban de a pares. `mascaraNavegable` (boolean[]) paso a `estadosDelDia` (EstadoHora[]), y `Racha` gano el campo `composicion` ('plena' | 'mixta' | 'al-limite'). **Disciplina fail-safe reforzada, no aflojada**: `rafagaNudos: null` no puede dar `limite` (ese estado se sostiene entero sobre la racha), dia bloqueado sigue anulando todo, y el fallback de `margenAlLimiteDe()` es 0 — ante contrato recortado se cae al comportamiento estricto anterior, no a un margen inventado. UI: barra verde HUECA para "al limite" (no ambar: el ambar ya significa viento de tierra/seguridad y reusarlo confundiria "apenas alcanza" con "te aleja de la costa"), chip de composicion en la pildora de racha, tono propio en el tooltip con el porque explicito, y semaforo amarillo "Al limite" para un dia que entra solo por las rachas. Verificado con Playwright los cinco bordes exactos que dio el coordinador con el rango 16-28 y margen 3: 14/18,5 entra; 14/15 no (rachas cortas); 10/17 no (sostenido muy abajo); 13/19 entra justo (faltante = margen); 12,9/20 ya no. Mas: rafaga null en hora que si calificaria (no entra), sostenido sobre el maximo (no entra), dia entero al limite (amarillo, 16 barras huecas), racha mixta (3 huecas + 3 solidas contiguas, verde, chip "parte al limite"), dia bloqueado con horas que calificarian (0 y 0), y config sin `margenAlLimiteNudos` (fallback estricto). Con datos reales y rango 9-30 aparecen 12 horas plenas + 4 al limite; cambiar a 16-28 en vivo re-renderiza sin refetch. Regresion completa de las cuatro suites anteriores. Cero errores de consola. Lighthouse: **a11y 100 / BP 100 / SEO 100**, performance 79 (dentro del ruido 79-90 medido en esta maquina). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, undecima pasada — el offshore bloquea + señales de rio): Dos lotes encadenados. **(A) El viento de tierra pasa de avisar a BLOQUEAR** (textual de Joaquin: "el viento de tierra es condicion justa y necesaria para no navegar"). `estadoDeHora` gana un cuarto estado `offshore` que cortocircuita el criterio de rango antes de evaluarlo; es hermano de `diaBloqueado` pero a nivel HORA. Impacto real medido: el sabado paso de 16 horas navegables a 0 y el 03/09 de 12 a 3. El ambar dejo de significar "ojo pero se navega" y paso a ser el "no" de esa causa (barra ambar solida), distinto del gris de "falta viento", conservando la tira bajo la linea base como segundo canal para vision cromatica reducida. Se unifico el motivo del "no" en `motivoSinHoras` (semaforo.ts), usado por la pildora del semaforo y por el tag de racha vacia — **se detecto verificando que la pildora decia "Fuera de tu rango" en un dia caido enteramente por offshore**, que era exactamente la confusion a evitar (alguien podria creer que ampliando el rango lo desbloquea), y se corrigio a "Viento de tierra" / "Sin horas utiles". Se actualizo el copy del bloque de seguridad (linea de consecuencia nueva) y los docblocks de `SenalOffshore`, que documentaban la señal como equivalente al racheado cuando ya no lo es. **(B) Cuatro señales nuevas**: `senalBajante` corregida (la causa el NORTE, no el O/NO que habia inventado el sistema, y depende de la duracion), `senalCreciente`, `senalVientoDesparejo`, y `senalRacheado` que ahora puede dispararse por sector (SE arrachado) ademas de por despegue medido. Se agruparon los avisos por categoria en orden fijo con tono propio por grupo — seguridad / riesgo / rio (cian) / calidad (violeta) / oportunidad — porque con seis avisos una pila indiferenciada no la lee nadie. Verificado con Playwright: bloqueo total y parcial, offshore sobre hora plena y sobre hora al limite, mezcla de causas, racheado que sigue sin bloquear, creciente y bajante activas e inactivas con `horasSostenidas`, racheado por sector vs. por despegue, desparejo con los dos tipos de sudestada, y un dia cargado con bloqueo + 5 badges donde se comprobo por geometria que el bloque de seguridad queda por encima. Contraste del tono de rio medido: 5,15:1 claro / 12,51:1 oscuro. Regresion completa de las suites anteriores. Cero errores de consola. Lighthouse: **a11y 100 / BP 100 / SEO 100**, performance 80. `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, duodecima pasada — calibracion Norden→spot): Joaquin aporto que "el pilote siempre marca 2 o 3 nudos mas de lo que realmente hay en la tierra"; el backend expuso `vientoNudosSpot`/`rafagaNudosSpot` en estaciones y `vientoMedidoSpotNudos` por hora. Del lado del front: (1) el bloque "ahora en el rio" pasa a mostrar el ESTIMADO EN LA COSTA como cifra principal, con la leyenda "estimado en la costa", el badge "ESTIMADA" en la rafaga (reusando el vocabulario `MEDIDA`/`MODELO` ya establecido) y la lectura cruda visible como respaldo etiquetado. (2) La serie del grafico pasa de la lectura cruda al equivalente: es el cambio con beneficio real, porque ahora las dos series son del mismo lugar y **comparables**, asi que la nota se reescribio por completo — de "esta diferencia es real, no es error del modelo" a "lo que quede de diferencia si es error del modelo". (3) El tooltip muestra las dos cifras etiquetadas. (4) La magnitud de la correccion en la nota se **deriva de los datos** (delta entre las dos series) en vez de hardcodearse: hoy da 2,5 kt y si el backend recalibra, el texto se actualiza solo. Verificado con Playwright: estacion con ambos valores, estacion no disponible (cae al pronostico del dia sin rastro de crudo ni serie), medicion cruda por debajo de la correccion (el estimado muestra 0 y no un negativo, con el crudo 1,4 visible al lado), y contrato recortado sin equivalente (cae a la lectura cruda etiquetada como tal, sin linea ni nota — deliberado: mejor no dibujarla que dibujar una serie incomparable). Se actualizaron los mocks de la suite de clima, que habian dejado de ejercitar la logica de huecos al cambiar el campo que alimenta la serie. Regresion completa de las seis suites. Cero errores de consola. Lighthouse: **a11y 100 / BP 100 / SEO 100**, performance 77 (dentro del ruido 77-90 de esta maquina). `astro check` y build limpios. **Sin commitear a pedido.**
- 2026-09-02 (implementador-astro-front, decimotercera pasada — el reloj manda + auditoria de consistencia): Bug reportado por Joaquin: "el estado actual del rio marca que ya paso la hora de kite y no hay mas el resto del dia, pero el sistema informa dia de kite". La causa era `indiceHoraActual` devolviendo `-1` para dos casos opuestos (antes / despues de la ventana); se agrego `desdeAhora()` y se enhebro hasta el semaforo, las rachas y la grilla — solo HOY mira el reloj, las rachas empezadas se RECORTAN en vez de descartarse, el pasado se atenua pero la serie medida nunca, y aparece el caso nuevo "Hoy ya paso" distinguido de "Fuera de tu rango". Segundo lote, auditoria de consistencia: se unifico el motivo de "no se navega" en `motivoSinHoras()` — el hallazgo mas grave fue un dia enteramente offshore que decia "Fuera de tu rango", y el `aria-label` del grafico que anunciaba rachas ya pasadas a lectores de pantalla. Se cerro la colision de ambar (sudestada sin temporal era del mismo color que el bloque de seguridad; ahora el ambar es exclusivamente seguridad), se corrigio el texto de "Como viene la semana" que contradecia las barras al limite y las descartadas por offshore, y se limpiaron dos comentarios desactualizados y CSS muerto/duplicado. Ver decisiones 24 y 25.
- 2026-09-02 (implementador-astro-front, decimocuarta pasada — direccion hora por hora): Pedido de Joaquin: "mostrar direccion del viento en cada hora de cada grafico". Las flechas pasaron de salir cada `pasoEtiquetas` horas (y de no salir en los tres dias siguientes) a dibujarse en las 16 horas de los cuatro graficos. El desafio era de legibilidad: se resolvio con fila propia debajo de los rotulos (no se superponen a las barras), flechas mas chicas y tenues, y la flecha de una hora offshore en ambar apareada con su tira, para que la direccion y el motivo del descarte se lean juntos. El compacto crecio de 120 a 130 px. Ver decision 26. En la misma pasada se cerro el ultimo supuesto abierto del proyecto: Joaquin confirmo contra el viento real que la flecha apunta bien (convencion meteorologica + 180 grados para mostrar el flujo).
- 2026-09-02 (implementador-astro-front, decimoquinta pasada - performance con el fondo intacto): Se pidieron tres mejoras de rendimiento. Medidas por separado, dos eran falsas: la duplicacion de GSAP era un falso positivo (ScrollTrigger llama a `gsap.quickSetter`, de ahi el string en los dos bundles; los marcadores exclusivos del core aparecen una sola vez) y forzar `manualChunks` empeoraba el total en 564 bytes, asi que se revirtio; diferir el canvas tampoco servia, porque `wind-bg.js` pesa lo que pesa por ser el chunk compartido donde vive el core de GSAP, que el dashboard necesita igual. La tercera si: los subsets `latin` de Inter bajaron `dist` de 69 a 21 archivos. El costo real estaba fuera de la lista, ScrollTrigger con 42 KB y un solo consumidor, y se reemplazo por IntersectionObserver conservando GSAP para la animacion. JS 177.248 a 134.679 bytes (-24%), Lighthouse 79 a 83. El fondo animado quedo igual, verificado. Ver decision 27.
- 2026-09-02 (implementador-astro-front, decimosexta pasada - rediseño de cards por jerarquia): Joaquin reordeno la prioridad del producto (las horas navegables y el detalle hora a hora primero, los min/max al fondo). Se agrego `veredictoDelDia` en `semaforo.ts` —que no decide nada nuevo, se apoya en `rachasNavegables` y `motivoSinHoras`— y se reordeno la card de HOY y las filas de la semana alrededor de el. Medido en 390x844, el veredicto paso de y=1065 (fuera de pantalla) a y=371 y el grafico de y=875 a y=537; los min/max, que eran dos stat-cards con borde por encima de la respuesta, bajaron a una tira de texto. La leyenda de nueve claves paso a plegable y la nota de la serie medida se movio junto al bloque del rio, que es lo que explica. El veredicto usa verde para 'se navega' y NEUTRO para 'no' —nunca ambar, que sigue reservado al viento de tierra— y el bloque de seguridad quedo pegado al veredicto. Accesibilidad se mantuvo en 100. Ver decision 28.
- 2026-09-02 (implementador-astro-front, decimoseptima pasada - despegue mezclado y salida de los min/max): Continuacion del rediseño. Los min/max de viento y rafagas salieron de la tira de contexto por pedido explicito (direccion y marea se quedan), y el despegue paso de ser `despegueMaximoNudos` —un pico del pronostico calculado en el backend— a `despegueDelDia`, un promedio ponderado por cantidad de horas que mezcla lo medido de las horas ya transcurridas con lo pronosticado para las que faltan. El ponderado sale solo porque cada hora entra como una muestra suelta. Las horas pasadas sin medicion no aportan (rellenarlas con pronostico ensuciaria la mitad observada) y el `title` declara cuantas horas vienen de cada fuente. Verificado con un dia calibrado a 2 kt medido y 8 kt pronosticado: 8,0 → 5,8 → 3,5 → 2,0 segun avanza el reloj. Queda registrado que `despegueMaximoNudos` ya no tiene consumidor en el front. Ver decision 29.
- 2026-09-02 (implementador-astro-front, decimoctava pasada - nueva base de comparacion en el panel de modelos): El backend paso a comparar el pronostico en las coordenadas del spot contra el equivalente estimado en la costa (Norden - 2,5 kt), en vez de modelo-en-Norden contra lectura cruda de Norden. El lado de referencia dejo de ser una medicion, asi que se reescribio todo el copy que decia 'lo que midio la estacion' / 'del viento medido' / 'la unica medicion real'; el primer parrafo del metodo afirmaba lo contrario de lo que ahora pasa y se rehizo entero. Se agregaron `compara`, `medicionEsEstimada` y `correccionEstacionNudos` al contrato: la frase de que se compara la manda el backend y la bandera decide el vocabulario, de modo que el dia que haya sensor en el spot el panel diga 'medido' sin tocar el copy. Se detecto probando el contrato recortado que el parrafo de la cadena era incondicional e imprimia 'se le restan — —'; se partio en dos versiones elegidas por dato. La serie arranco de nuevo (25 horas) y vuelve a 'Muestra inicial', verificado que se lee como estado y no como error. Ver decision 30.
