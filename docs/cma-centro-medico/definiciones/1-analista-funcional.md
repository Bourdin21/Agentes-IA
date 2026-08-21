# Memoria - Analista funcional

## Proyecto: cma-centro-medico
## Ultima actualizacion: 2026-08-21

## Definiciones vigentes

### Contexto del lead
Centro Medico CMA La Plata — consultorio medico que opera con **4 sedes** (La Plata, Claypole, Malvinas Argentinas y R. Calzada), pero **[DECISION 2026-08-21, Joaquin]: alcance de esta propuesta acotado SOLO a la sede La Plata** — no multi-sede. Entro por outbound (mensaje frio generico de stock/ventas/operacion diaria, no especifico de salud). Primer contacto automatizado de CMA ya muestra que operan con herramientas externas: bot de WhatsApp 24hs ("Bot Silvio") para turnos y un sistema de turnos online por AgendaPro (`cmacentromedico.site.agendapro.com`) — validos para las 4 sedes, sin cambios. Cuestionario de calificacion (3 preguntas, 21/08):

1. **Que es lo mas te complica hoy**: "Portal de pacientes" (respuesta de una sola frase, sin desarrollar).
2. **Con que lo maneja hoy**: "Otro" (no especifica cual — dato mas debil que audifonos-bariloche, que al menos nombro "un sistema de turnos con historias clinicas").
3. **Cuantas personas lo van a usar**: "5".

### Lectura del dolor real
Este es el discovery **mas debil del historial hasta la fecha** — una sola frase sin desarrollar como respuesta al dolor principal, y "Otro" sin especificar como respuesta a la herramienta actual. A diferencia de audifonos-bariloche (que nombro explicitamente "sistema de turnos con historias clinicas" como lo que ya usan), aca no sabemos si "Otro" significa Excel, papel, un sistema legado, o simplemente las herramientas externas que ya se ven en su primer contacto automatizado (Bot Silvio + AgendaPro).

**Hipotesis de trabajo (a confirmar en la demo, no asumida como cerrada):** "Portal de pacientes" se interpreta como DOS necesidades combinadas, no una sola:
1. **Lado interno**: CMA no tiene un sistema propio de gestion de pacientes/historia clinica unificado entre sus 4 sedes — Bot Silvio y AgendaPro resuelven la reserva de turnos, pero no la ficha del paciente ni la historia clinica ni la vista consolidada entre sedes.
2. **Lado externo**: el paciente mismo no tiene una forma de ver sus propios turnos/historia sin llamar o escribir por WhatsApp — de ahi el nombre literal "portal de pacientes" (acceso propio del paciente, no solo herramienta de staff).

Esta lectura es una interpretacion razonable sobre datos minimos, no un hecho confirmado — la propuesta se arma con esta hipotesis explicita y una pregunta abierta para la demo.

### Modulos/features analizados
- Gestion de pacientes de la sede La Plata (alta, datos basicos).
- Catalogo de especialidades + profesionales (el propio formulario de intake de CMA pide "Especialidad" al paciente que escribe, lo que confirma que la sede maneja mas de un profesional/especialidad, aun siendo una sola ubicacion).
- Turnos/agenda interna por profesional (registro propio del sistema — NO reemplaza ni se integra con Bot Silvio/AgendaPro en este alcance, ver exclusiones).
- Historia clinica digital por paciente (consultas/notas por profesional).
- Documentos adjuntos en la historia clinica.
- Panel de turnos del dia (staff).
- **Portal de autogestion del paciente**: login propio del paciente, ve sus propios turnos e historia clinica basica (solo lectura) — el modulo que responde literalmente al pain point nombrado.
- Usuarios con 3 roles: administracion/recepcion, profesional, paciente (acceso acotado a sus propios datos).

**Nota sobre las otras 3 sedes:** quedan fuera de este alcance. Si el sistema funciona bien en La Plata, extenderlo a Claypole/Malvinas Argentinas/R. Calzada es un proyecto de expansion aparte (agregar entidad Sede + scoping — trabajo real pero acotado, no un rewrite) — no cotizado aqui.

### Reglas funcionales acordadas (hipotesis, a confirmar)
- Sistema de una sola sede (La Plata) — sin entidad Sede ni scoping multi-ubicacion.
- Cada turno se asocia a un profesional y un paciente especifico.
- El acceso del rol Paciente es de solo lectura sobre sus propios datos (no edita su historia clinica, no ve la de otros pacientes).
- Bot Silvio (WhatsApp) y AgendaPro (turnos online) siguen operando como estan para las 4 sedes — el sistema nuevo no los reemplaza ni se integra con ellos en este alcance (integrarlos seria alcance adicional no cotizado, ver exclusiones).

### Criterios de aceptacion vigentes
- Una recepcionista puede dar de alta un paciente, sin duplicar DNI.
- Una recepcionista puede cargar un turno para un paciente con un profesional concreto, sin pisar otro turno ya tomado de ese profesional.
- Un profesional puede ver su agenda y la historia clinica de sus pacientes.
- Un paciente puede iniciar sesion con su propio usuario y ver (solo lectura) sus turnos pasados/futuros y su historia clinica basica.

### Supuestos y dependencias
- **[SUPUESTO — pregunta abierta activa para la demo]** Que significa exactamente "Portal de pacientes" para el lead: ¿gestion interna de pacientes por parte del staff, acceso de autogestion para el paciente mismo, o ambos? Esta propuesta cotiza AMBOS bajo la hipotesis de arriba — si en la demo el lead aclara que solo necesita uno de los dos, el alcance (y el precio) se ajusta.
- **[SUPUESTO — pendiente confirmar, mas fragil ahora que se acoto a 1 sede]** "5 personas" fue la respuesta del lead ANTES de acotar el alcance a una sola sede — no sabemos si esas 5 personas son solo de La Plata o el total entre las 4 sedes. Se mantiene 5 como numero de trabajo (unico dato disponible) para el plan de mantenimiento, pero es el supuesto mas debil de esta version — confirmar en la demo cuantas personas trabajan especificamente en la sede La Plata.
- **[SUPUESTO]** El campo "Especialidad" que CMA ya pide en su propio formulario de intake confirma multiples especialidades/profesionales aun dentro de una sola sede — no se sabe la cantidad exacta de profesionales ni de especialidades distintas; se disena el catalogo generico (sin limite fijo).
- **[SUPUESTO — pendiente confirmar]** No hay obra social con liquidacion/facturacion automatica en el alcance (no mencionado, igual que audifonos-bariloche). Si CMA necesita gestionar reintegros o facturacion por obra social, es alcance adicional no cotizado.
- Sin discovery por llamada/reunion todavia — este analisis se arma sobre 3 respuestas de un cuestionario automatico de calificacion, la mas debil registrada hasta ahora en el historial del estudio. La propuesta se presenta con alcance MVP + Etapa 2, hipotesis explicitas, y una pregunta abierta central (que es "portal de pacientes" en concreto) — a confirmar antes de firmar.

### Exclusiones confirmadas
- **Las otras 3 sedes (Claypole, Malvinas Argentinas, R. Calzada)** — quedan fuera de este alcance. Expansion a mas sedes es un proyecto aparte, no cotizado aqui.
- Integracion o reemplazo de Bot Silvio (WhatsApp) o AgendaPro (turnos online) — siguen operando como canal externo, fuera de este alcance.
- Migracion de datos de cualquier sistema/planilla actual (exclusion fija del estudio).
- Facturacion / integracion con obras sociales (no mencionado, no cotizado).
- Aplicacion movil nativa (exclusion fija del estudio — se accede via navegador web responsive, el portal de pacientes incluido funciona bien desde el celular).

## Historial de ajustes
- 2026-08-21: primera version, a partir del cuestionario de calificacion outbound (el mas debil del historial: 1 frase sin desarrollar + "Otro" sin especificar). Pendiente de confirmacion con el lead en la demo antes de iniciar implementacion — pregunta abierta central: alcance real de "Portal de pacientes".
- 2026-08-21: **acotado a pedido explicito de Joaquin a UNA sola sede (La Plata)** — se cae la dimension multi-sede completa (Sede como entidad, filtros por sede, N:N Profesional-Sede). El resto del alcance (Pacientes, Turnos, Historia clinica, Adjuntos, Portal de autogestion del paciente, Especialidades/Profesionales) se mantiene sin cambios. Reestimado en `4-presupuestador.md`.
