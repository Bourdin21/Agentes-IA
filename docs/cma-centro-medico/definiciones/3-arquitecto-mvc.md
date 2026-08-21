# Memoria - Arquitecto MVC

## Proyecto: cma-centro-medico
## Ultima actualizacion: 2026-08-21

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisados `docs/patrones/catalogo.yml` y `docs/*/definiciones/` del historial. Sin match de dominio con codigo YA ENTREGADO (audifonos-bariloche es el precedente de diseno mas cercano pero sigue sin implementar). Reutilizables confirmados:
- `AdjuntoService` (PAT-002) — tal cual, adaptado a `HistoriaClinicaEntry`/`Paciente`.
- ASP.NET Identity (roles) — patron estandar del estudio, aca con 3 roles: `Administracion`, `Profesional`, `Paciente`.
- PAT-008 (DataTables server-side + filtro por columna) para los listados de staff (Pacientes, Turnos, Profesionales).

**[DECISION 2026-08-21, Joaquin]: alcance acotado a UNA sola sede (La Plata)** — se elimina toda la dimension multi-sede de esta arquitectura: entidad `Sede`, tabla de union `ProfesionalSede`, campo `SedeId`/`SedeReferenciaId` en Paciente/Turno/HistoriaClinicaEntry, filtro de sede en el panel del dia. La arquitectura queda calcada de audifonos-bariloche salvo por `Especialidad`/`ProfesionalEspecialidad` (catalogo nuevo, ver diseno) y el Portal de autogestion del paciente (`PortalPacienteService`, sin precedente en el estudio).

**Patron nuevo identificado — candidato a catalogar (PAT-017):** portal de autogestion para el usuario final (no-staff) de un sistema BlankProject, con rol dedicado de acceso minimo y scoping forzado por Id de usuario autenticado (nunca por parametro de URL). Sin precedente en el estudio — audifonos-bariloche lo excluyo explicitamente de su alcance. Se agrega a `docs/patrones/catalogo.yml` al cierre de esta etapa (ver seccion "Patron nuevo" abajo) para que quede disponible si otro proyecto (ej. audifonos-bariloche si retoma su Etapa 2, o cualquier sistema con usuario final propio) lo necesita.

### Componentes por capa
- **Domain**: `Especialidad`, `Profesional` (extiende `ApplicationUser` via relacion 1:1), `ProfesionalEspecialidad` (N:N), `Paciente` (con `ApplicationUserId` nullable — se vincula a un login solo si tiene acceso de autogestion), `Turno`, `HistoriaClinicaEntry`, `Adjunto`.
- **Application**: DTOs de listado/detalle por entidad, `ITurnoService`, `IHistoriaClinicaService`, `IAdjuntoService` (reuso PAT-002), `IPortalPacienteService` (scoping forzado).
- **Infrastructure**: `TurnoService` (valida superposicion de horario por profesional), `AdjuntoService` (adaptacion del ya existente), `PortalPacienteService` (resuelve siempre `pacienteId` desde `User.Identity`, nunca desde la URL), `AppDbContext` con las 6 entidades nuevas + Identity.
- **Web**: `ProfesionalesController`, `PacientesController`, `TurnosController` (+ vista agenda), `HistoriaClinicaController`, `PortalController` (area separada o controller dedicado para el rol Paciente — vistas "Mis turnos"/"Mi historia", sin acciones de escritura), Identity scaffolding (login, roles).

### Entidades y configuraciones EF
- `Especialidad`: Id, Nombre, CreatedAt.
- `Profesional`: Id, ApplicationUserId (FK, unique), Nombre, CreatedAt.
- `ProfesionalEspecialidad`: ProfesionalId (FK), EspecialidadId (FK) — clave compuesta.
- `Paciente`: Id, Nombre, DNI (unique index), Edad, Telefono, ObraSocial?, ApplicationUserId? (FK nullable, unique cuando no es null — vinculo al login de autogestion), Notas?, CreatedAt.
- `Turno`: Id, PacienteId (FK), ProfesionalId (FK), FechaHora, DuracionMinutos, Estado (enum), TipoConsulta?, CreatedAt.
- `HistoriaClinicaEntry`: Id, PacienteId (FK), TurnoId? (FK nullable), ProfesionalId (FK), Fecha, Nota, CreatedAt.
- `Adjunto`: Id, HistoriaClinicaEntryId? (FK nullable), PacienteId? (FK nullable, adjuntos generales pre-consulta), Path/Url, TipoArchivo, FechaSubida, SubidoPorUserId.
- Roles Identity: `Administracion`, `Profesional`, `Paciente` (+ `SuperUsuario` interno del estudio para soporte, no expuesto al cliente).

### Migraciones requeridas
- Migracion inicial: crea las 6 tablas de negocio + tablas estandar de Identity.
- Index unico en `Paciente.DNI`.
- Index unico en `Paciente.ApplicationUserId` (cuando no es null).
- Index en `Turno.ProfesionalId + FechaHora` (soporte al chequeo de superposicion, igual patron que audifonos-bariloche).

### Riesgos tecnicos activos
- **Chequeo de superposicion de horario** atomico (transaccion + revalidacion antes de commit) — mismo patron que audifonos-bariloche.
- **Seguridad del portal de paciente (IDOR)**: el riesgo mas nuevo de este proyecto. Toda accion del rol `Paciente` debe resolver su propio `PacienteId` desde `User.Identity` server-side — nunca aceptar un id de paciente como parametro de request sin validar que coincide con el usuario logueado. Cubrir con prueba QA especifica (ver nota para `6-qa.md` cuando se llegue a esa etapa).
- **Alta de credenciales de paciente**: pendiente definir en la demo (autoregistro vs. alta manual por recepcion) — afecta el flujo de `PortalController`/registro, no solo el precio.
- **Adjuntos por foto de celular**: mismo limite que audifonos-bariloche (10MB, JPG/PNG/PDF).
- **Cantidad de usuarios real ("5", dato levantado ANTES de acotar a una sola sede — podria estar sobreestimado si el lead contaba staff de las 4 sedes)**: revisar plan de mantenimiento antes de la entrega si el numero real de la sede La Plata difiere (ver `4-presupuestador.md`).

### Patron nuevo — PAT-017 (registrar en catalogo.yml al cerrar esta etapa)
- **Nombre**: Portal de autogestion para usuario final (no-staff) con scoping forzado por identidad.
- **Categoria**: dominio.
- **Descripcion**: rol de Identity dedicado para el usuario final del negocio (paciente, cliente, inquilino, etc. segun el dominio), con controllers/services separados de los de staff que SIEMPRE resuelven el id de la entidad de negocio (paciente, cliente...) desde `User.Identity` en el server, nunca desde un parametro de la request. Acceso normalmente de solo lectura sobre un subconjunto acotado de datos propios.
- **Cuando usar**: cualquier sistema BlankProject donde el usuario final (no empleado del cliente) necesite ver su propia informacion sin pasar por el staff (turnos, pedidos, facturas, historial).
- **Proyecto origen**: cma-centro-medico (a confirmar cuando se implemente — todavia en etapa de propuesta).
- **Nota**: agregar a `docs/patrones/catalogo.yml` con `pendiente_verificar: true` en los archivos de referencia hasta que exista implementacion real.

## Historial de ajustes
- 2026-08-21: primera version. Arquitectura anclada en el diseno de audifonos-bariloche (mismo nucleo), con Sede como dimension nueva transversal y PortalPacienteService como pieza de seguridad nueva (scoping forzado, sin precedente exacto en el estudio).
- 2026-08-21: **acotado a UNA sola sede (La Plata)** a pedido explicito de Joaquin — eliminadas las entidades `Sede` y `ProfesionalSede`, y todo campo `SedeId`/`SedeReferenciaId` de Paciente/Turno/HistoriaClinicaEntry. De 8 a 6 entidades de negocio. `PortalPacienteService` (PAT-017) se mantiene sin cambios — es independiente de la dimension sede.
