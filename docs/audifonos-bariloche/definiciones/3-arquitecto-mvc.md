# Memoria - Arquitecto MVC

## Proyecto: audifonos-bariloche
## Ultima actualizacion: 2026-08-19

## Definiciones vigentes

### Escaneo de reutilizacion cross-proyecto (obligatorio antes de disenar)
Revisados `docs/*/definiciones/` del historial. No existe un proyecto previo de turnos+historia clinica multi-profesional en el estudio — `labipac` (Laboratorios/consultorios medicos, mismo catalogo de industria) es en realidad una **calculadora de costo/precio por practica medica**, dominio funcional distinto (no turnos ni historia clinica), sin entidades reutilizables directamente. Candidatos de reutilizacion de **patron tecnico** (no de dominio):
- `AdjuntoService` (subida/asociacion de archivos a una entidad) — ya construido y usado en `vinosefue` (adjuntos de comprobantes) y otros proyectos. Reutilizable tal cual, adaptado a `HistoriaClinicaEntry`/`Paciente`.
- `WhatsAppClient` + patron de `BackgroundService` con HMAC/webhook (recordatorios, Etapa 2) — patron ya construido y probado extensamente en `crm-olvidata` (este mismo estudio lo opera en produccion). Reutilizable en su estructura, pero cada cliente necesita su propia cuenta de WhatsApp Business/Meta configurada — no es reuse 100%.
- ASP.NET Identity (roles Recepcion/Profesional) — patron estandar ya usado en todos los proyectos MVC del estudio.

Sin match de dominio (Paciente/Turno/HistoriaClinica son entidades nuevas) — el nucleo del sistema se construye desde cero.

### Componentes por capa
- **Domain**: `Paciente`, `Profesional` (o `ApplicationUser` extendido con rol), `Turno`, `HistoriaClinicaEntry`, `Adjunto`.
- **Application**: DTOs de listado/detalle por entidad, `ITurnoService`, `IHistoriaClinicaService`, `IAdjuntoService` (interface, reutilizando contrato ya validado en el estudio).
- **Infrastructure**: `TurnoService` (valida superposicion de horario), `AdjuntoService` (adaptacion del ya existente — storage en disco/hosting compartido, sin necesidad de blob storage externo dado el volumen esperado de un centro chico), `AppDbContext` con las 5 entidades nuevas + Identity.
- **Web**: `PacientesController`, `TurnosController` (+ vista calendario/agenda), `HistoriaClinicaController`, Identity scaffolding (login, roles).

### Entidades y configuraciones EF
- `Paciente`: Id, Nombre, DNI (unique index), Edad, Telefono, ObraSocial?, Notas?, CreatedAt.
- `Turno`: Id, PacienteId (FK), ProfesionalId (FK a ApplicationUser), FechaHora, DuracionMinutos, Estado (enum), TipoConsulta?, CreatedAt.
- `HistoriaClinicaEntry`: Id, PacienteId (FK), TurnoId? (FK nullable — puede haber entradas sin turno asociado), ProfesionalId (FK), Fecha, Nota, CreatedAt.
- `Adjunto`: Id, HistoriaClinicaEntryId? (FK nullable), PacienteId? (FK nullable, para adjuntos generales pre-consulta como el pedido medico inicial), Path/Url, TipoArchivo, FechaSubida, SubidoPorUserId.
- Roles Identity: `Recepcion`, `Profesional` (+ `SuperUsuario` interno del estudio para soporte, no expuesto al cliente).

### Migraciones requeridas
- Migracion inicial: crea las 5 tablas de negocio + tablas estandar de Identity (AspNet*).
- Index unico en `Paciente.DNI`.
- Index en `Turno.ProfesionalId + FechaHora` (soporte al chequeo de superposicion).

### Riesgos tecnicos activos
- **Chequeo de superposicion de horario** debe ser atomico (transaccion o constraint) para evitar condicion de carrera si 2 recepcionistas cargan turnos simultaneos para la misma profesional — mitigar con transaccion + revalidacion antes de commit, patron ya usado en otros ABMs del estudio con validacion de unicidad.
- **Adjuntos por foto de celular**: definir limite de tamano (propuesto 10MB) y formatos aceptados (JPG/PNG/PDF) antes de implementar, para no saturar el hosting compartido.
- **Cantidad de usuarios real (6 aprox, sin confirmar)**: si termina siendo mayor, revisar plan de mantenimiento antes de la entrega (ver 4-presupuestador.md).

## Historial de ajustes
- 2026-08-19: primera version. Sin match de dominio cross-proyecto; reuso limitado a patrones tecnicos (AdjuntoService, WhatsAppClient, Identity).
