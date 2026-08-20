# Memoria - Disenador funcional

## Proyecto: audifonos-bariloche
## Ultima actualizacion: 2026-08-19

## Definiciones vigentes

### Historias de usuario

**HU-01 — Alta de paciente**
Como recepcionista, quiero cargar un paciente nuevo (nombre, DNI, edad, telefono, obra social/particular) para poder asignarle turnos e iniciar su historia clinica.
- Criterio: no permite guardar sin nombre y DNI. DNI unico por paciente (evita duplicados).

**HU-02 — Turno por profesional**
Como recepcionista, quiero asignar un turno a una fonoaudiologa concreta en una fecha/hora para organizar la agenda del centro.
- Criterio: el sistema no permite crear un turno que se superponga con otro turno ya existente de la misma profesional. Estados minimos: Pendiente, Confirmado, Atendido, Ausente, Cancelado.

**HU-03 — Agenda del dia**
Como profesional, quiero ver mi agenda del dia (o de un rango de fechas) para saber a quien atiendo y cuando.
- Criterio: la vista solo muestra los turnos de la profesional logueada (no ve la agenda de otras), salvo rol recepcion que ve todas.

**HU-04 — Historia clinica por consulta**
Como profesional, quiero registrar una nota en la historia clinica del paciente despues de cada consulta para llevar el seguimiento clinico.
- Criterio: cada entrada de historia clinica queda asociada al turno/consulta, la fecha y la profesional que la cargo. No editable por otras profesionales (solo lectura).

**HU-05 — Adjuntar documentos**
Como profesional o recepcionista, quiero subir una foto o PDF (pedido medico, estudio, orden) a la historia clinica del paciente para tener la documentacion digitalizada y accesible sin depender de WhatsApp/papel.
- Criterio: acepta imagen (JPG/PNG, tipico de foto de celular) y PDF. Cada adjunto queda asociado a una entrada de historia clinica o directamente al paciente (para documentos generales, ej. pedido medico inicial antes de la primera consulta).

**HU-06 — Panel de turnos del dia**
Como recepcionista, quiero ver de un vistazo los turnos del dia de todas las profesionales para gestionar la sala de espera y reprogramaciones.
- Criterio: lista ordenada por hora, con nombre de paciente, profesional, hora y estado.

**HU-07 — Roles y accesos**
Como administrador del centro, quiero que cada usuario tenga un rol (recepcion / profesional) para que cada quien vea solo lo que le corresponde.
- Criterio: recepcion administra turnos y pacientes pero no edita notas clinicas; profesional ve y edita solo su propia agenda e historias clinicas de sus pacientes atendidos.

*(Etapa 2)* **HU-08 — Recordatorio de turno por WhatsApp**
Como paciente, quiero recibir un recordatorio de mi turno por WhatsApp para no olvidarme ni tener que llamar para confirmar.
*Hipotesis a validar con el cliente: requiere numero de WhatsApp Business propio del centro dado de alta en Meta — tramite de verificacion de negocio, tiempo variable (dias a semanas), fuera del control del estudio.*

*(Etapa 2)* **HU-09 — Reportes basicos**
Como administrador, quiero ver turnos por profesional y tasa de ausentismo en un rango de fechas para entender la ocupacion del centro.

### Flujos de pantalla acordados
1. Login → Panel de turnos del dia (recepcion) o Mi agenda (profesional).
2. Panel de turnos → Nuevo turno (buscar/crear paciente → elegir profesional → fecha/hora → guardar).
3. Turno → Ver paciente → Historia clinica (lista de consultas anteriores + boton "Nueva entrada" + boton "Adjuntar documento").
4. Historia clinica → Adjuntar documento → subir desde galeria/camara (mobile) o archivo (desktop).

### ViewModels definidos
- `PacienteListItemViewModel` / `PacienteFormViewModel` (Nombre, DNI, Edad, Telefono, ObraSocial, Notas).
- `TurnoListItemViewModel` / `TurnoFormViewModel` (PacienteId, ProfesionalId, FechaHora, Estado, TipoConsulta).
- `HistoriaClinicaEntryViewModel` (PacienteId, TurnoId?, ProfesionalId, Fecha, Nota, Adjuntos[]).
- `AdjuntoViewModel` (Url/Path, TipoArchivo, FechaSubida, SubidoPor).

### Validaciones de UI acordadas
- No permitir guardar turno sin Paciente + Profesional + FechaHora.
- Validar superposicion de horario por profesional antes de guardar (chequeo server-side, no solo UI).
- Adjuntos: validar tipo de archivo (imagen/PDF) y tamano maximo razonable (a definir en arquitectura, ej. 10MB) antes de subir.

### Logica de distribucion de elementos en pantalla
- priorizar simplicidad visual y comprension inmediata del flujo
- ubicar primero informacion y acciones criticas; dejar secundario en segundo plano
- mantener jerarquia consistente (titulo, contexto, formulario, acciones)
- reducir ruido visual: evitar bloques redundantes y opciones duplicadas
- reutilizar este criterio de distribucion en todas las pantallas del sistema

### Contratos funcionales para Services
- `ITurnoService.HayConflicto(profesionalId, fechaHora, duracion, turnoIdExcluir?) : bool` — chequeo de superposicion, reutilizable en alta y edicion.
- `IAdjuntoService` — **candidato fuerte de reutilizacion**: Olvidata ya tiene un `AdjuntoService` generico usado en otros proyectos del estudio (ver `docs/vinosefue/definiciones/`) para subida/asociacion de archivos a una entidad — adaptar en vez de construir desde cero.

## Historial de ajustes
- 2026-08-19: primera version.
