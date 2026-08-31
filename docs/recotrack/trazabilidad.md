# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-28 - arquitecto-mvc / implementador (incidente reactivo)
- Etapa: Implementacion (diagnostico y fix directo, sin Analisis/Diseno/Arquitectura previos — incidente de produccion)
- Cambio: (1) `VencimientoCronJob` reescrito de un unico `Task.Delay` calculado al arrancar a un sondeo periodico (cada 20 min) contra una marca persistida (`CronJobEstados`, tabla nueva) que evita reenviar en el mismo mes y se autorecupera si el proceso estuvo caido en el momento del disparo. (2) `Notificaciones:DestinatariosTaller` en produccion paso de `[""]` (placeholder desde jun-2026) a `["personal@esur.com.ar"]`, confirmado por el cliente.
- Motivo: el cliente pidio verificar que el envio mensual de vencimientos funcionara en produccion. La tabla `EmailNotificationLogs` no tenia ningun registro desde el 1-jul-2026 (el disparo del 1-ago nunca ocurrio). Causa raiz: hosting compartido (site4now.net/IIS) recicla el app pool por inactividad, matando el `BackgroundService` y su temporizador en memoria; al reiniciar, el calculo del proximo disparo saltaba directo al mes siguiente sin enviar ni dejar rastro de error.
- Impacto en capas: Datos (nueva tabla `CronJobEstados`, migracion `AddCronJobEstado`), Infraestructura (`VencimientoCronJob`), Configuracion (`appsettings.Production.json`). Migracion EF: si, aplicada en local y produccion.
- Verificacion: al desplegar, el mecanismo de recuperacion disparo de inmediato (proceso recien arrancado, disparo de agosto ya vencido) y envio con exito ambos tipos de notificacion a `personal@esur.com.ar` — la primera vez que el envio de camiones funciona de punta a punta (antes fallaba silenciosamente por falta de destinatarios). Tambien se probo el SMTP de forma independiente con un envio de prueba a `bourdinjoaquin@gmail.com`, exitoso.
- Riesgos/supuestos: el sondeo cada 20 min agrega carga minima (una consulta SQL) pero no elimina el riesgo de reciclado en si — si el proceso esta caido varios dias seguidos, el envio se dispara recien cuando vuelve a levantar, pudiendo llegar tarde en vez de exactamente el dia 1. No se investigo si existe forma de evitar el reciclado del app pool en el hosting compartido (fuera de alcance de este fix).

### 2025-07 - analista-funcional / disenador-funcional / arquitecto-mvc / presupuestador / implementador
- Etapa: Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion (pipeline completo)
- Cambio: Iteracion 1 — Duplicado masivo de Trabajos, Estado de Empleado (enum + badge), formato de Legajo con CodigoRazonSocial + autocomplete.
- Motivo: pedido explicito del cliente (ver `1-analista-funcional.md`).
- Impacto en capas: Presentacion, Negocio, Datos (migracion EF: columna EstadoEmpleado).
- Riesgos/supuestos: ninguno abierto al cierre.

### 2026-06 (fecha exacta no registrada) - implementador
- Etapa: Implementacion (sin Analisis/Diseno/Arquitectura formales previos — salteo explicito del pipeline)
- Cambio: Iteracion 2 — Separacion de notificaciones de vencimientos por rol (Operador/Taller/Admin), con filtrado en pantalla y 2 flujos de envio por email.
- Motivo: requerimiento funcional recibido en conversacion directa con el cliente.
- Impacto en capas: Negocio (NotificacionVencimientoService), Presentacion (NotificacionesController, vista). Sin migracion EF.
- Riesgos/supuestos: `DestinatariosTaller` quedo con placeholder `""` en produccion, pendiente que el cliente confirme el email real.

### 2026-06-28 - presupuestador
- Etapa: Presupuesto (retroactivo, cierre de calibracion)
- Cambio: cuantificada la "iteracion evolutiva Junio 2026" — Estado de camiones, Rol Taller + ABM usuarios Taller, Cron mensual de vencimientos, Tipo de camion, Reporte de Disponibilidad de Camiones (Excel), Division de vencimientos por rol. Total M=26.0h / PERT=26.5h / USD 537 (dev + tokens IA). Cierre de calibracion: real 4.5h, factor IA observado 4.78x.
- Motivo: cierre de sprint, calibracion estimado vs. real.
- Impacto en capas: N/A (solo presupuesto).
- Riesgos/supuestos: horas reales reportadas sin desglose por item (distribuidas proporcionalmente). Commits `20c8f1a` (migracion de empleados, 08-jun) y `de3013c` (arreglo fecha de vencimiento, 09-jun) no quedaron claramente mapeados a ningun item de este dataset — posible trabajo tecnico no cuantificado por separado.

### 2026-08-11 10:00 (aprox) - arquitecto-mvc / implementador (incidente reactivo)
- Etapa: Implementacion (diagnostico y fix directo, sin Analisis/Diseno/Arquitectura previos — incidente de produccion)
- Cambio: (1) Corregida la clave de configuracion leida por `ErrorEmailNotifierMiddleware` (`Notificaciones:ErrorEmail:Destinatarios` -> `Olvidata_ErrorEmail:Destinatarios`). (2) Agregado `HasConversion` explicito `TimeOnly? <-> TimeSpan?` para `MultaChofer.Hora` y `AccidenteChofer.Hora` en `RecoTrackDbContext`, con migracion `FixHoraTimeOnlyMapping` generada localmente.
- Motivo: el cliente reporto "DataTables warning ... Ajax error" en la tabla de Multas de choferes en produccion (recotrack.com.ar), no reproducible en local. Diagnostico via log de produccion descargado por FTP (`Logs/recotrack-errors-20260811.log`): `InvalidCastException` al leer columnas `TIME` de MySQL como `TimeOnly` nativo, especifico del driver `MySql.EntityFrameworkCore` 10.0.1 contra el MySQL de produccion (site4now.net). De paso se detecto que el mecanismo de alerta por email de errores nunca funciono, por la clave de config mal escrita.
- Impacto en capas: Datos (mapeo EF, migracion pendiente de aplicar), Web (middleware). Migracion EF: si, generada (`20260811202007_FixHoraTimeOnlyMapping`), **no aplicada aun en produccion**.
- Riesgos/supuestos: fix verificado solo por `dotnet build`, sin QA funcional contra datos reales. Cambios sin commitear al cierre de la sesion. Ver detalle completo en `definiciones/5-implementador.md` y `definiciones/6-qa.md` (DEF-01, DEF-02).

### 2026-08-11 (mas tarde el mismo dia) - documentador / arquitecto-mvc (sincronizacion documental)
- Etapa: Documentacion (retroactiva, sincronizacion de memoria)
- Cambio: migrado el contenido real de `1-analista-funcional.md`, `2-disenador-funcional.md`, `3-arquitecto-mvc.md`, `5-implementador.md` desde `C:\Sistemas\recotrack\docs\recotrack\definiciones\` (unica copia existente hasta entonces) a esta ubicacion centralizada (`C:\Sistemas\Agentes-IA\docs\recotrack\definiciones\`), que estaba con las plantillas vacias sin completar. Creadas por primera vez `6-qa.md` y `7-documentador.md` (roles que no existian cuando se trabajaron las iteraciones 1 y 2).
- Motivo: pedido explicito de revisar el proyecto contra las definiciones vigentes del sistema de agentes y detectar que faltaba antes de actualizar arquitectura y stack.
- Impacto en capas: ninguno (solo documentacion).
- Riesgos/supuestos: el repo local (`C:\Sistemas\recotrack\docs\recotrack\definiciones\`) queda como copia legacy/duplicada — considerar eliminarlo o dejarlo como referencia historica para no generar ambiguedad sobre cual es la fuente de verdad.
