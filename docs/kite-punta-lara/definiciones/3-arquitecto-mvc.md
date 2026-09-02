# Memoria - Arquitecto (adaptado a stack PHP, ver nota de stack en metadata.md)

## Proyecto: kite-punta-lara
## Ultima actualizacion: 2026-09-01

> Nota: el rol "arquitecto-mvc" del estudio esta escrito para ASP.NET Core MVC + EF Core + MySQL. Este proyecto es PHP/DonWeb — no hay agente arquitecto PHP en el catalogo todavia. Este documento traduce el mismo objetivo (componentes por capa, permisos, migraciones, riesgos) al stack real del proyecto, respetando igual la separacion Presentacion/Negocio/Datos de `01-fronteras-por-capa.instructions.md` (esa regla es agnostica de stack).

## Componentes que se sumaron en Implementacion (2026-09-02)

No estaban en el diseno original de esta etapa. Se listan aca para que el mapa
de componentes no quede incompleto:

- **`EvaluacionModelosService` + `ModeloObservacionRepository`** — evaluacion
  continua de modelos de pronostico contra las mediciones reales de CARP. Es
  el **primer repositorio del proyecto**: la arquitectura los preveia desde el
  principio pero ningun caso de uso los habia necesitado hasta ahora. Guarda
  los pares crudos medicion-vs-modelo (no la metrica calculada), asi cambiar
  la definicion de "acertividad" no obliga a empezar el historial de cero.
- **`GET /modelos`** — panel publico que muestra que modelos se evaluan, cual
  se usa y por que. Endpoint aparte de `/pronostico` a proposito: el dashboard
  no toca la base y este si, asi que una caida de MySQL deja sin panel pero no
  sin pronostico.
- **`bin/evaluar_modelos.php`** — cron de la evaluacion (a programar en
  DonWeb). El endpoint tambien la dispara si esta vieja, asi que el panel se
  alimenta aunque el cron no este configurado.
- **`config/pronostico.php`** — modelo, coordenadas, seleccion de celda y
  franjas horarias, con la tabla de errores que justifica cada eleccion.
- **`sql/migrations/004_modelo_observaciones.sql`** — cuarta migracion.
- **`scripts/deploy.sh` + `scripts/migrar.php`** — deploy reproducible por
  FTP. Incluye un corredor de migraciones con token de un solo uso, porque
  este hosting **no tiene SSH ni cliente MySQL** y no habia otra via de
  aplicar una migracion contra la base de produccion. Ver el README del repo
  para las dos trampas del hosting (la cuenta FTP esta enjaulada en el
  docroot; `Require all denied` no se aplica y hay que bloquear por
  `mod_rewrite`).

## Definiciones vigentes

### 0. Resultado del escaneo de reutilizacion
- `docs/patrones/catalogo.yml`: **PAT-007 confirmado y reutilizado literalmente** — `SmtpMailer.php` (cliente SMTP/SSL sin dependencias, `stream_socket_client` + protocolo SMTP a mano) ya en produccion real en labipac-front y diercas-front (`C:\Sistemas\labipac-front\server\SmtpMailer.php`). Se reutiliza tal cual, sin modificar, para el envio de avisos (CU-05). Grado de reuso: **literal, codigo ya entregado**.
- Escaneo de `docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md` de todo el portfolio: sin otro proyecto PHP con backend de datos/sesiones/autenticacion (labipac-front/diercas-front son sitios Astro estaticos, la unica pieza PHP es el formulario de contacto ya cubierto por PAT-007). **Sin precedente de codigo para el resto de la arquitectura** (routing, capa de datos PDO, autenticacion por sesion, cache de APIs externas) — se disena desde cero.
- No se agrega componente nuevo al catalogo mas alla de confirmar PAT-007: el resto de los componentes (MotorDeCalculoService, ConsolidadorEstacionesService) son especificos del dominio de pronostico de viento, sin indicio de reuso en otros proyectos del estudio (mismo criterio que uso el disenador funcional en la etapa anterior).

### 1. Alcance funcional resumido
Igual al definido en `2-disenador-funcional.md` (Diseño cerrado 2026-09-01): 7 pantallas, motor de calculo con reglas de birazon/sudestada/equipo, bitacora y aviso por email. Ver ese documento — no se repite aca.

### 2. Impacto tecnico por capa (equivalente PHP de Domain/Application/Infrastructure/Web)

**Restricciones de hosting confirmadas por el cliente (2026-09-01):** SSH + Composer disponibles en DonWeb, cron/tareas programadas disponibles. Base de datos MySQL **ya creada** (`olvidata_club`) y credenciales FTP recibidas — ver `docs/credenciales.local.md` (nunca en este archivo tracked por git). Host de conexion MySQL (tipicamente `localhost` en DonWeb) a confirmar en el panel al empezar Implementacion.

**Subdominio confirmado (2026-09-01):** `club.olvidata.com.ar` — el proyecto NO se aloja en un dominio propio nuevo, sino bajo el dominio `olvidata.com.ar` en DonWeb, mismo esquema que otros bots/subdominios de Olvidata Soft (usuario FTP `club@olvidata.com.ar` ya confirma este alcance). Implicancia tecnica: el certificado SSL y el registro DNS del subdominio son responsabilidad de la infraestructura ya existente de Olvidata Soft, no de un alta de dominio nueva — si al momento de deploy el subdominio no resuelve o no tiene SSL, es un tema de configuracion DNS/panel DonWeb (fuera del alcance de este documento de arquitectura de aplicacion), no de la app en si.

**Presentacion — ACTUALIZADO 2026-09-02 (pedido explicito del cliente a mitad de Implementacion, ver trazabilidad):**
Se abandona el enfoque original de templates PHP server-side. La Presentacion pasa a ser un repo Astro separado (`kite-punta-lara-front`, patron `diercas-front`/`labipac-front`, construido con el agente `agentes-ia-implementador-astro-front`), compilado a estatico y desplegado en la raiz del mismo subdominio (`club.olvidata.com.ar`). Este repo (`kite-punta-lara`) pasa a exponer **solo una API JSON** bajo `/api/*` en produccion (mismo subdominio, mismo origen — sin CORS ni en dev, gracias al proxy de Vite del lado Astro). `templates/` y `HomeController` (version original) se eliminaron.
- `public/index.php`: front controller unico, tabla de rutas simple (array `ruta => [Controller, accion]`) que devuelve JSON (`Content-Type: application/json`), sin framework completo (Slim/Laravel). Las rutas definidas aca NO llevan el prefijo `/api` (lo aporta el subpath de deploy en produccion y el proxy de Vite en dev).
- `src/Controllers/`: cada uno arma el JSON de respuesta (ViewModel serializado) orquestando los Services correspondientes — nunca contienen las reglas de `MotorDeCalculoService`. `PronosticoController` (P1/P4, `GET /pronostico`) ya implementado (Etapa 1). Pendientes: `AuthController` (P2/P3), `PerfilController` (P5), `BitacoraController` (P6/P7) — Etapas 2/3.
- Sesion nativa de PHP (`session_start()`) para login — se activa recien en Etapa 2 (Etapa 1 no tiene cuentas). CSRF sobre API: patron a implementar en Etapa 2 (`GET /csrf` + header `X-CSRF-Token` en vez de campo de formulario, reutilizando el mismo helper `Csrf::token()/Csrf::validate()` ya existente) — los 4 formularios (login, registro, guardar equipo, cargar sesion) ahora viven en Astro y postean a la API.

**Negocio (`src/Services/`)**
- `ConsolidadorEstacionesService`: pega a CARP, SHN y SMN; cada llamada en su propio try/catch — si una fuente falla, las otras dos igual se muestran (ya definido como criterio de diseño en `EstacionEnVivoViewModel.Disponible`).
- `PronosticoService`: consume Open-Meteo (fuente confirmada del MVP), arma la ventana hoy+3 dias.
- `MotorDeCalculoService`: implementa las reglas ya definidas en Diseño — señales de birazon (brisa de calma / bajante) independientes, sudestada con prioridad de riesgo sobre la recomendacion de equipo, cruce contra la tabla de equipo del usuario (o la tabla default). Umbrales como **constantes de configuracion** (`config/umbrales.php`), no hardcodeados en el Service — ya pedido en Diseño para poder calibrarlos con la bitacora real sin tocar codigo de logica.
- `NotificacionesService`: evalua el score de cada usuario con `RecibirAvisoEmail = true` contra el horizonte de 3 dias; si corresponde, dispara el email via `SmtpMailer` (PAT-007).
- `BitacoraService`: alta/listado de sesiones.
- `AuthService`: registro (hash con `password_hash()`, nunca MD5/SHA1 a mano) y login (`password_verify()`); al registrar, clona la tabla de equipo default hacia `equipo_quiver_items` del usuario nuevo.
- `CacheService`: cache de archivo JSON con TTL 15-30 min sobre las respuestas de CARP/SHN/SMN/Open-Meteo (en `storage/cache/`, fuera del webroot) — evita pegarle a esas APIs en cada visita al dashboard publico, que no requiere login y por lo tanto puede recibir trafico repetido sin control de usuario.

**Datos (`src/Repositories/` + `src/Data/Db.php` + `sql/migrations/`)**
- `Db.php`: conexion PDO unica (singleton), MySQL, prepared statements en todo el acceso — nunca concatenar SQL con input de usuario.
- `UsuarioRepository`, `EquipoQuiverRepository`, `SesionBitacoraRepository`: un metodo por consulta necesaria (sin ORM — el volumen de datos y de queries de este proyecto no lo justifica).
- Tabla default de equipo (P5, "Default clonable"): **no es una tabla de BD**, vive como array de configuracion (`config/equipo_default.php`, los valores reales de Joaquin) — se clona a `equipo_quiver_items` del usuario en el momento del registro (`AuthService::registrar()`), no se lee en vivo desde la config en cada request.

**Cron (`bin/enviar_avisos.php`)**
- Script CLI standalone (no pasa por `public/index.php`), programado 1x/dia en el panel de tareas de DonWeb, usa `NotificacionesService`. Loguea cada corrida (fecha, cantidad de avisos enviados, errores) a un archivo simple (`storage/logs/cron.log`) — un cron en hosting compartido puede fallar silenciosamente (cambio de version de PHP-CLI, timeout), y sin log no hay forma de diagnosticarlo.

### 3. Modelo de permisos
No hay roles — todos los usuarios registrados tienen el mismo nivel de acceso ("socios del club"). Unico eje: sesion activa vs. anonimo.
| Recurso | Anonimo | Sesion activa |
|---|---|---|
| P1 Home / estaciones en vivo / pronostico generico | Lectura | Lectura |
| P4 Dashboard personalizado, P5 Mi equipo | — | Lectura/escritura, **solo el propio usuario** |
| P6 Cargar sesion | — | Escritura, asociada siempre al usuario de la sesion activa (nunca a un `usuario_id` recibido por parametro/POST) |
| P7 Bitacora social | — | Lectura de **todos** los usuarios (deliberado, es bitacora compartida del club) |

Riesgo de **IDOR** (mismo principio que PAT-017, aunque ese patron es de .NET Identity y aca no hay codigo que portar): en P5 (editar equipo) y P6 (cargar sesion), el `usuario_id` que escribe en la base **nunca** se toma de un campo del formulario — se resuelve siempre server-side desde `$_SESSION['usuario_id']`. La bitacora social (P7) es la unica pantalla donde ver datos de otro usuario es intencional, no un bug.

### 4. Migraciones de esquema requeridas
**Si, requeridas** — base de datos MySQL `olvidata_club` ya creada en DonWeb (credenciales recibidas, ver `docs/credenciales.local.md`). Sin ORM/EF Core: se gestionan como scripts SQL numerados en `sql/migrations/`, aplicados a mano via el panel de DonWeb o `mysql` CLI por SSH (ya confirmado disponible).

```sql
-- 001_usuarios.sql
CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(190) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  recibir_aviso_email TINYINT(1) NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 002_equipo_quiver_items.sql
CREATE TABLE equipo_quiver_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  nudos_desde DECIMAL(4,1) NOT NULL,
  nudos_hasta DECIMAL(4,1) NOT NULL,
  metros_kite DECIMAL(4,1) NOT NULL,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 003_sesiones_bitacora.sql
CREATE TABLE sesiones_bitacora (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL,
  fecha DATE NOT NULL,
  fue TINYINT(1) NOT NULL,
  nudos_reales DECIMAL(4,1) NULL,
  comentario VARCHAR(280) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
```
Validacion `fecha <= CURDATE()` y solapamiento de tramos de `equipo_quiver_items` quedan en `AuthService`/`PerfilController` (capa de Negocio), no como constraint de base — MySQL no expresa bien "no solapamiento entre filas" como CHECK portable.

### 5. Riesgos y supuestos
Heredados de las etapas anteriores (re-expuestos, no asumidos en silencio):
- CARP, SHN y SMN sin API oficial documentada ni estabilidad garantizada — ya resuelto a nivel de diseño (`ConsolidadorEstacionesService` aisla cada fuente).
- Open-Meteo puede rendir peor que el promedio manual de Windguru cerca de la costa — pendiente la validacion empirica corta ya recomendada en Analisis, antes de dar los umbrales de `config/umbrales.php` por definitivos.
- Registro sin verificacion de email (alta directa) — aprobado en la etapa de Diseño.

Nuevos riesgos identificados en esta etapa:
- **Sin framework**, la seguridad (CSRF, sesiones, sanitizacion de salida) depende de que el helper `Csrf` y el escapado con `htmlspecialchars()` se usen de forma consistente en las 4 pantallas con formulario y en la bitacora social — a incluir explicitamente en el checklist de QA de este proyecto (no hay un framework que lo garantice por default como si pasaria en ASP.NET Core con Identity/Razor).
- **Cron en hosting compartido** puede fallar silenciosamente — mitigado con logging propio (`storage/logs/cron.log`), pero sigue siendo un punto a monitorear manualmente (no hay alerta automatica si el cron deja de correr).
- ~~Version exacta de PHP~~ **Confirmada: PHP 8.4 (lsphp, LiteSpeed PHP)** — habilita sintaxis moderna sin restriccion (enums, readonly properties, match, etc.). Gotcha tipico de hosting LiteSpeed a verificar en Implementacion: el binario de PHP que corre el cron/CLI (`bin/enviar_avisos.php`) puede NO ser el mismo `lsphp` que sirve las paginas web (a veces el CLI del panel apunta a otra version/instalacion de PHP) — confirmar con `php -v` dentro de la tarea programada de DonWeb, no asumir que coincide con la version del panel.

### 6. Gate de aprobacion para pasar a presupuesto
Arquitectura tecnica completa: capas definidas, modelo de permisos simple (sesion vs. anonimo) sin brechas de IDOR identificadas sin mitigar, 3 migraciones de esquema especificadas, reutilizacion de PAT-007 confirmada. **Listo para Presupuesto** — con la salvedad de que este es un proyecto personal sin cliente externo, por lo que el presupuesto es informativo (horas estimadas / costo interno de referencia), no una propuesta comercial a enviar.

## Historial de ajustes
- 2026-09-01: Arquitectura tecnica cerrada, adaptada a PHP/DonWeb (sin agente arquitecto PHP en el catalogo, se tradujo el rol .NET al stack real). Confirmado con el cliente: SSH/Composer disponible, cron disponible, BD todavia no creada. Stack definido: PHP plano sin framework (front controller + Services + Repositories PDO), 3 tablas nuevas, reutilizacion literal de PAT-007 (SmtpMailer.php) para avisos, umbrales del motor de calculo como configuracion editable. Riesgo nuevo identificado: seguridad (CSRF/XSS) depende de disciplina manual al no haber framework, a reforzar en QA.
