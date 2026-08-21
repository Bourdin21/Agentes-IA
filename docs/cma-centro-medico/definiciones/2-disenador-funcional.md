# Memoria - Disenador funcional

## Proyecto: cma-centro-medico
## Ultima actualizacion: 2026-08-21

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisado `docs/patrones/catalogo.yml` y `docs/*/definiciones/` del historial. El precedente mas cercano de dominio es **audifonos-bariloche** (turnos + historia clinica + pacientes + adjuntos, multi-profesional) — mismo nucleo funcional, pero ese proyecto sigue en estado de propuesta (no aprobado, sin implementacion), por lo que no hay CODIGO YA ENTREGADO para reutilizar todavia, solo diseno ya validado como referencia de enfoque. `labipac` (mismo catalogo de industria "Laboratorios/consultorios medicos") es una calculadora de costo por practica, dominio funcional distinto, sin entidades reutilizables.

**[DECISION 2026-08-21, Joaquin]: alcance acotado a UNA sola sede (La Plata)** — se cae la dimension multi-sede completa (entidad `Sede`, N:N Profesional-Sede, scoping por sede en Pacientes/Turnos/Panel del dia). El diseno queda practicamente calcado de audifonos-bariloche, con una sola diferencia estructural real:
- **Portal de autogestion del paciente**: audifonos-bariloche lo listo explicitamente como EXCLUSION ("Portal de autogestion para pacientes — podria evaluarse a futuro, no en este alcance"). Aca es, al reves, el pain point nombrado por el lead — pasa a ser nucleo del MVP, no un futuro. Sin precedente de codigo en el estudio — se disena y se cataloga como patron nuevo (`PAT-017` en `docs/patrones/catalogo.yml`).
- **Especialidades + Profesionales** como catalogo propio (audifonos-bariloche no lo tenia como entidad separada, solo un campo `TipoConsulta` en el turno) — CMA explicita "Especialidad" en su propio formulario de intake, señal de que maneja varios profesionales/especialidades aun en una sola sede.
- **Turnos ya resueltos externamente** (Bot Silvio WhatsApp + AgendaPro): el modulo de turnos interno de este sistema es un registro/agenda propio para el staff, sin integrar ni reemplazar esas herramientas.

Reutilizables por patron tecnico (via `catalogo.yml`):
- `IAdjuntoService` (PAT-002) — subida/asociacion de archivos a la historia clinica, igual que audifonos-bariloche.
- ASP.NET Identity + roles (patron estandar en todo el estudio) — aca con 3 roles en vez de 2.
- PAT-008 (DataTables server-side + filtro por columna) para todos los listados nuevos.

### Historias de usuario

**HU-01 — Alta de paciente**
Como recepcionista, quiero cargar un paciente nuevo (nombre, DNI, edad, telefono, obra social/particular) para poder asignarle turnos e iniciar su historia clinica.
- Criterio: no permite guardar sin nombre y DNI. DNI unico por paciente.

**HU-02 — Catalogo de especialidades y profesionales**
Como administrador, quiero cargar profesionales con su(s) especialidad(es) para poder asignarles turnos.
- Criterio: Especialidad es un catalogo simple (ej. Clinica Medica, Pediatria, etc. — sin lista cerrada predefinida, la carga el administrador). Un profesional puede tener mas de una especialidad.

**HU-03 — Turno por profesional**
Como recepcionista, quiero asignar un turno a un profesional concreto en una fecha/hora para organizar la agenda del centro.
- Criterio: el sistema no permite crear un turno que se superponga con otro turno ya existente del mismo profesional. Estados minimos: Pendiente, Confirmado, Atendido, Ausente, Cancelado.

**HU-04 — Agenda del dia**
Como recepcionista, quiero ver la agenda del dia de todos los profesionales para gestionar la sala de espera.
- Criterio: un profesional ve su propia agenda; recepcion ve la de todos.

**HU-05 — Historia clinica por consulta**
Como profesional, quiero registrar una nota en la historia clinica del paciente despues de cada consulta para llevar el seguimiento clinico.
- Criterio: cada entrada queda asociada al turno/consulta, fecha y profesional que la cargo. Solo lectura para otros profesionales.

**HU-06 — Adjuntar documentos**
Como profesional o recepcionista, quiero subir una foto o PDF a la historia clinica del paciente para tener la documentacion digitalizada.
- Criterio: acepta imagen (JPG/PNG) y PDF. Igual criterio que audifonos-bariloche (patron ya validado).

**HU-07 — Portal de autogestion del paciente**
Como paciente, quiero entrar con mi propio usuario y ver mis turnos (pasados y futuros) y mi historia clinica basica, sin depender de llamar o escribir por WhatsApp.
- Criterio: el paciente ve SOLO sus propios datos (nunca los de otro paciente). Acceso de solo lectura — no edita nada. Login separado del staff (mismo sistema de Identity, rol distinto).
- *Hipotesis a validar con el cliente: como se entrega la credencial al paciente (autoregistro con validacion de DNI, o alta manual por recepcion con envio de contraseña temporal por email/WhatsApp) — a definir en la demo, impacta el diseno del alta.*

**HU-08 — Roles y accesos**
Como administrador, quiero que cada usuario tenga un rol (Administracion/Recepcion, Profesional, Paciente) para que cada quien vea solo lo que le corresponde.
- Criterio: Administracion/Recepcion administra turnos y pacientes pero no edita notas clinicas; Profesional ve y edita su propia agenda e historias clinicas de sus pacientes atendidos; Paciente ve solo sus propios datos, solo lectura.

*(Etapa 2)* **HU-09 — Reportes basicos**
Como administrador, quiero ver turnos por profesional y tasa de ausentismo en un rango de fechas para entender la ocupacion del centro.

### Flujos de pantalla acordados
1. Login → segun rol: Panel de turnos del dia (recepcion), Mi agenda (profesional), o Mis turnos/Mi historia (paciente).
2. Panel de turnos (recepcion) → Nuevo turno (buscar/crear paciente → elegir profesional → fecha/hora → guardar).
3. Turno → Ver paciente → Historia clinica (lista de consultas anteriores + boton "Nueva entrada" + boton "Adjuntar documento").
4. Portal paciente → Mis turnos (lista simple, proximo turno destacado) / Mi historia (lista de consultas, solo lectura, sin boton de edicion).

### ViewModels definidos
- `ProfesionalViewModel` (Nombre, Especialidades[]).
- `PacienteListItemViewModel` / `PacienteFormViewModel` (Nombre, DNI, Edad, Telefono, ObraSocial, Notas).
- `TurnoListItemViewModel` / `TurnoFormViewModel` (PacienteId, ProfesionalId, FechaHora, Estado, TipoConsulta).
- `HistoriaClinicaEntryViewModel` (PacienteId, TurnoId?, ProfesionalId, Fecha, Nota, Adjuntos[]).
- `AdjuntoViewModel` (Url/Path, TipoArchivo, FechaSubida, SubidoPor) — reutilizado igual que audifonos-bariloche.
- `MisTurnosViewModel` / `MiHistoriaViewModel` (vistas de solo lectura scoped al paciente logueado, sin acciones de edicion).

### Validaciones de UI acordadas
- No permitir guardar turno sin Paciente + Profesional + FechaHora.
- Validar superposicion de horario por profesional antes de guardar (server-side).
- DNI unico por paciente.
- Adjuntos: mismo criterio que audifonos-bariloche (tipo imagen/PDF, tamano maximo ~10MB).
- Portal paciente: toda query de datos propios filtra SIEMPRE por el Id del paciente logueado — nunca por parametro de la URL sin validar contra el usuario en sesion (evitar IDOR: un paciente no debe poder ver la historia de otro cambiando un id en la URL).

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas; dejar secundario en segundo plano
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema

### Contratos funcionales para Services
- `ITurnoService.HayConflicto(profesionalId, fechaHora, duracion, turnoIdExcluir?) : bool` — igual patron que audifonos-bariloche.
- `IAdjuntoService` — reutilizado tal cual del catalogo (PAT-002).
- `IPortalPacienteService` — nuevo: `ObtenerMisTurnosAsync(pacienteId)`, `ObtenerMiHistoriaAsync(pacienteId)`, siempre resolviendo `pacienteId` desde el usuario autenticado (nunca desde parametro externo) — service dedicado en vez de reusar los services de staff directamente, para forzar el scoping de seguridad en un solo lugar.

## Historial de ajustes
- 2026-08-21: primera version. Diseno anclado en audifonos-bariloche (mismo nucleo turnos+historia clinica+adjuntos) con 2 diferencias estructurales: multi-sede y portal de autogestion del paciente como nucleo del MVP (no Etapa 2 opcional).
- 2026-08-21: **acotado a UNA sola sede (La Plata)** a pedido explicito de Joaquin — eliminada la entidad `Sede`, el ViewModel `SedeViewModel`, todo campo/filtro `SedeId`/`SedeReferenciaId`, y la HU de catalogo de sedes. HUs renumeradas (HU-07/08/09). Unica diferencia estructural remanente frente a audifonos-bariloche: el Portal de autogestion del paciente (HU-07) como nucleo del MVP.
