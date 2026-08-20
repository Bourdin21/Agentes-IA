# Memoria - Analista funcional

## Proyecto: audifonos-bariloche
## Ultima actualizacion: 2026-08-19

## Definiciones vigentes

### Contexto del lead
Centro de fonoaudiologia/audifonos en Bariloche, con varias fonoaudiologas atendiendo. Entro por outbound (campana "Consultorio Bariloche", catalogo "Laboratorios / consultorios medicos"). Primer contacto via WhatsApp, cuestionario de calificacion de 3 preguntas (19/08, 14:43-14:44):

1. **Que es lo mas te complica hoy**: "los turnos y digitalizar la documentacion de los pacientes para subir en la historia clinica".
2. **Con que lo maneja hoy**: "tenemos un sistema de turnos con historias clinicas de cada paciente" — YA tiene un sistema, no parte de cero.
3. **Cuantas personas lo van a usar**: "6 aprox".

### Lectura del dolor real
El cliente no dice que el sistema actual de turnos+historias no funcione en absoluto — el dolor especifico nombrado es **digitalizar documentacion de pacientes para subir a la historia clinica** (probablemente pedidos medicos, estudios, ordenes escaneadas o fotografiadas) y la gestion de turnos en si (sin especificar que falla puntualmente: podria ser doble reserva, falta de recordatorios, dificultad para reprogramar, etc. — no confirmado). El mensaje de bienvenida automatico del negocio pide "foto del pedido medico + nombre completo, DNI y edad" para pacientes nuevos, y "nombre de la fonoaudiologa" para pacientes existentes — esto confirma que ya operan con documentos por foto/WhatsApp de forma manual (sin sistema), consistente con el pain point de "digitalizar y subir a la historia clinica".

### Modulos/features analizados
- Gestion de pacientes (alta, datos basicos: nombre, DNI, edad, telefono, obra social/particular).
- Turnos/agenda por profesional (una fonoaudiologa distinta por turno — sistema multi-profesional, no un unico calendario).
- Historia clinica digital por paciente (registro de consultas/notas por profesional que atendio).
- Documentos adjuntos en la historia clinica (foto/PDF de pedido medico, estudios, ordenes) — el pain point mas especifico mencionado.
- Panel/vista de turnos del dia para recepcion.
- Usuarios con 2 roles minimos: recepcion (agenda turnos, no necesariamente ve notas clinicas completas) y profesional (ve su propia agenda + historia clinica de sus pacientes).

### Reglas funcionales acordadas
- Cada turno se asocia a una fonoaudiologa especifica (no es agenda unica compartida).
- La historia clinica es por paciente, con entradas por consulta/visita, y cada entrada puede tener 0+ documentos adjuntos.
- Los documentos adjuntos deben poder subirse desde foto de celular (no solo PDF de escritorio) — dado que hoy reciben las fotos por WhatsApp.

### Criterios de aceptacion vigentes
- Una recepcionista puede dar de alta un turno nuevo para un paciente (nuevo o existente) asignado a una profesional concreta, en una fecha/hora, sin pisar otro turno ya tomado de esa misma profesional.
- Una profesional puede ver su agenda del dia y acceder a la historia clinica de cada paciente turnado.
- Se puede adjuntar una foto/PDF a la historia clinica de un paciente (pedido medico, estudio) y verlo despues asociado a esa consulta.

### Supuestos y dependencias
- **[CONFIRMADO por Joaquin, 2026-08-19]** El sistema actual de turnos+historias clinicas se **reemplaza** directamente por el nuevo (no conviven en paralelo). Migracion de datos historicos sigue siendo exclusion fija del estudio salvo acuerdo aparte.
- **[CONFIRMADO por Joaquin, 2026-08-19]** "6 aprox" personas = 3 profesionales (fonoaudiologas) + 3 recepcion/administrativo, cada una con su propio usuario/login. Numero exacto todavia a validar con el lead, pero el reparto de roles queda fijado 3+3 para diseno de accesos.
- **[SUPUESTO — pendiente, confirmar con el lead]** No hay obra social con liquidacion/facturacion automatica involucrada en el alcance (el cuestionario no lo menciona, Joaquin tampoco tiene el dato). Si el negocio necesita gestionar reintegros de obra social o facturacion, es alcance adicional no cotizado aqui — pregunta activa en la propuesta enviada.
- **[SUPUESTO — pendiente, confirmar con el lead]** El set de campos por paciente (nombre, DNI, edad, telefono, obra social/particular) es una aproximacion razonable, no confirmada contra los datos reales que cargan hoy — Joaquin no tiene el detalle exacto del sistema actual del lead. Pregunta activa en la propuesta enviada.
- **[SUPUESTO]** Los "estudios"/"audifonos"/"otras consultas" mencionados en el mensaje de bienvenida del negocio son tipos de motivo de consulta, no sistemas separados — se modelan como un campo de "tipo de consulta" en el turno/historia clinica, no como modulos distintos.
- Sin discovery por llamada/reunion todavia — este analisis se arma sobre 3 respuestas de un cuestionario automatico de calificacion, no una entrevista de relevamiento completa. La propuesta se presenta con alcance MVP + Etapa 2 y supuestos explicitos, a confirmar antes de firmar.

### Exclusiones confirmadas
- Migracion de datos del sistema actual (exclusion fija del estudio).
- Facturacion / integracion con obras sociales (no mencionado, no cotizado).
- Aplicacion movil nativa (exclusion fija del estudio — se accede via navegador web responsive).
- Portal de autogestion para pacientes (podria evaluarse a futuro, no en este alcance).

## Historial de ajustes
- 2026-08-19: primera version, a partir del cuestionario de calificacion outbound. Pendiente de confirmacion con el lead antes de iniciar implementacion.
