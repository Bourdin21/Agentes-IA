# Memoria - Disenador funcional

## Proyecto: kite-punta-lara
## Ultima actualizacion: 2026-09-01

## Definiciones vigentes

### 0. Resultado del escaneo de reutilizacion
- `docs/patrones/catalogo.yml`: sin match para el flujo completo (app PHP multiusuario con motor de scoring) — es el primer proyecto del estudio con este perfil. Dos matches puntuales reutilizables:
  - **PAT-007** (`SmtpMailer.php`, proyecto origen labipac-front, ya reutilizado en diercas-front): reutilizar tal cual para CU-05 (aviso proactivo por email), evita reinventar el envío SMTP en PHP.
  - **PAT-008** (regla normativa "cada columna visible del listado tiene su filtro"): aplicar el criterio a la pantalla de bitácora social (CU-06), aunque la implementación técnica no sea DataTables server-side .NET — el criterio de UX es independiente del stack.
- Escaneo de `docs/*/definiciones/2-disenador-funcional.md` de otros proyectos: sin flujo equivalente (dashboard público + área logueada con scoring propio). No se toma ningún diseño de pantalla existente como base.
- No se agrega patrón nuevo al catálogo: el motor de scoring (birazón/sudestada/equipo) es específico del dominio de pronóstico de viento, sin indicio de que otro proyecto del portfolio del estudio (rubros retail/servicios/salud) vaya a necesitarlo — se documenta acá, no en el catálogo cross-proyecto.

### 1. Alcance funcional resumido
Igual al definido en `1-analista-funcional.md` (Análisis cerrado 2026-09-01): dashboard público de pronóstico + área logueada con equipo personalizado, bitácora y aviso por email. Ver ese documento para el detalle de incluido/no incluido/dependencias — no se repite acá.

### 2. Flujo de pantallas y wireframe textual

**P1 — Home / Dashboard (público, sin login)**
```
[Header] Kite Punta Lara — Club Universitario, Ensenada        [Iniciar sesión] [Registrarme]

[Card destacada — HOY]
  Viento actual: 14 nudos, SE          [semáforo verde/amarillo/rojo]
  Recomendación (equipo genérico): kite 10-12m
  Badges si aplica: [⚠ Sudestada — con temporal, no recomendable] / [⚠ Sudestada — SE sostenido, oportunidad]
                    [🌬 Birazón — posible brisa de calma esta tarde] [🌊 Birazón — posible bajante]

[3 cards secundarias — Mañana / Pasado mañana / Día 3]
  mismo resumen compacto (viento, dirección, semáforo), confiabilidad decreciente día 3

[Bloque "Estaciones en vivo"]
  CARP  | XX nudos | dirección | hace X min      (o "no disponible")
  SHN   | ...                                     (o "no disponible")
  SMN   | ...                                     (o "no disponible")

[Banner] "Iniciá sesión para ver la recomendación con TU equipo y anotar tus sesiones"
```

**P2 — Login**
```
Email, Contraseña, [Ingresar]
¿Olvidaste tu contraseña? / ¿No tenés cuenta? Registrate
```

**P3 — Registro**
```
Email, Contraseña, Confirmar contraseña, [Crear cuenta]
Al crear la cuenta: se clona automáticamente la tabla de equipo default a "Mi equipo".
```

**P4 — Dashboard (logueado)**
```
Mismo layout que P1, pero:
- La recomendación de cada día usa la tabla de equipo del usuario (no la genérica).
- Cada día (hoy y pasados dentro de la ventana visible) muestra un link "Cargar esta sesión" → P6.
```

**P5 — Mi equipo (perfil)**
```
[Tabla editable]
  Desde (nudos) | Hasta (nudos) | Kite (metros)     [fila x cada tramo]
  12             | 15             | 12                [Editar] [Quitar]
  15             | 20             | 9                 [Editar] [Quitar]
  [+ Agregar tramo]
  [Guardar cambios]

[Checkbox] Recibir aviso por email cuando haya día de kite
```

**P6 — Cargar sesión (bitácora)**
```
Fecha: [selector, máximo hoy]
¿Fuiste a navegar? [Sí/No]
Nudos reales (opcional): [___]
Comentario (opcional): [___]
[Guardar]
```

**P7 — Bitácora social (logueado)**
```
[Listado, más reciente primero]
Fecha | Usuario | ¿Fue? | Nudos reales | Comentario
[Filtro por Fecha (rango)] [Filtro por Usuario] [Filtro por ¿Fue?]
```

### 3. ViewModels propuestos (campos y validaciones funcionales)

**PronosticoDiaViewModel** (P1/P4)
- Fecha (date)
- VientoNudosMin / VientoNudosMax (decimal)
- DireccionGrados (int 0-359) + DireccionTexto (ej. "SE")
- RecomendacionEquipo (texto, ej. "kite 10-12m" o "No navegable")
- SenalBirazonBrisaCalma (bool + texto explicativo)
- SenalBirazonBajante (bool + texto explicativo)
- SenalSudestada (enum: Ninguna / ConTemporal / SinTemporal)
- Confiabilidad (enum: Alta [hoy/estación en vivo] / Media [1-2 días] / Baja [día 3])

**EstacionEnVivoViewModel** (P1/P4)
- Organismo (enum: CARP / SHN / SMN)
- NombreEstacion (texto)
- VientoNudos (decimal, nullable)
- DireccionGrados (int, nullable)
- Timestamp (datetime, nullable)
- Disponible (bool) — false cuando la fuente no respondió; validación: si Disponible=false, el resto de los campos no se muestra (placeholder "no disponible"), nunca un 0 engañoso.

**EquipoQuiverItemViewModel** (P5)
- NudosDesde (decimal, requerido, >= 0)
- NudosHasta (decimal, requerido, > NudosDesde)
- MetrosKite (decimal, requerido, > 0)
- Validación de conjunto: los tramos de un mismo usuario no pueden solaparse; al menos 1 tramo cargado para que el usuario tenga recomendación personalizada (si la tabla queda vacía, el sistema usa la tabla default como fallback y lo indica en pantalla).

**PerfilUsuarioViewModel** (P5)
- Email (readonly en esta pantalla)
- RecibirAvisoEmail (bool)
- Equipo (List<EquipoQuiverItemViewModel>)

**SesionBitacoraViewModel** (P6/P7)
- Fecha (date, requerido, validación: <= fecha de hoy, nunca futura)
- Fue (bool, requerido)
- NudosReales (decimal, opcional; si se carga: >= 0 y < 60 como warning no bloqueante — valor fuera de rango típico, se guarda igual pero se avisa)
- Comentario (texto, opcional, máx. 280 caracteres)
- UsuarioEmail / UsuarioNombre (solo lectura, para P7)

### 4. Maquina de estados
No aplica — confirmado en Análisis (`1-analista-funcional.md`, bandera "Máquina de estados: NO"). Es un sistema de cálculo/scoring sin ciclo de vida de estados de negocio.

### 5. Reglas de negocio y permisos por pantalla/acción
| Pantalla/acción | Acceso |
|---|---|
| P1 Home (ver pronóstico + estaciones) | Público, sin login |
| P2 Login / P3 Registro | Público (solo para no logueados) |
| P4 Dashboard logueado | Requiere sesión |
| P5 Mi equipo (ver/editar) | Requiere sesión, solo el propio usuario (nunca editar equipo de otro) |
| P6 Cargar sesión | Requiere sesión, la sesión cargada queda asociada al usuario autenticado (nunca a un usuario elegido por parámetro) |
| P7 Bitácora social (ver) | Requiere sesión (cualquier usuario logueado ve las sesiones de todos) |
| Envío de aviso por email (CU-05) | Automático (job programado), solo a usuarios con `RecibirAvisoEmail = true` |

Regla de negocio central (motor de cálculo, vive en capa de Negocio, nunca en el equivalente a Controller):
1. Tomar viento en vivo (si el día es hoy) o pronóstico Open-Meteo (si es día 1-3), con degradado de confiabilidad por día.
2. Evaluar señal de birazón: brisa de calma y bajante se evalúan **de forma independiente** (dos reglas separadas, cada una con su propio umbral configurable — no una tabla hardcodeada, para poder calibrarlas con la bitácora a futuro).
3. Evaluar señal de sudestada: si el viento del sector SE supera el umbral Y hay indicio de mal tiempo asociado (lluvia/tormenta en el mismo pronóstico) → `ConTemporal` (riesgo). Si supera el umbral sin ese indicio → `SinTemporal` (oportunidad condicional).
4. Cruzar el viento resultante contra la tabla de equipo del usuario (o la tabla default si no está logueado o no cargó la suya) → `RecomendacionEquipo`.
5. Si `SenalSudestada = ConTemporal`, la recomendación final se fuerza a "No recomendable" aunque el cruce con la tabla de equipo diera un tramo válido (regla de riesgo prioritaria sobre la recomendación de equipo).

### 6. Impacto funcional por capa
- **Presentación**: 7 pantallas (P1-P7) + plantilla de email de aviso proactivo + plantilla de email de confirmación de registro (estándar, no pedida explícitamente pero necesaria para validar la cuenta — a confirmar con Arquitectura si aplica verificación de email o alta directa).
- **Negocio**: `ServicioConsolidadorEstaciones` (CARP/SHN/SMN, cada fuente falla aislada), `ServicioPronostico` (Open-Meteo), `MotorDeCalculo` (reglas de birazón/sudestada/equipo descriptas en punto 5, con umbrales configurables, no hardcodeados), `ServicioNotificaciones` (job diario que evalúa el score por usuario suscripto y dispara email), `ServicioBitacora` (alta/listado de sesiones).
- **Datos**: `Usuario` (email, password hash, RecibirAvisoEmail), `EquipoQuiverItem` (usuario_id, nudos_desde, nudos_hasta, metros_kite), `SesionBitacora` (usuario_id, fecha, fue, nudos_reales, comentario). Se recomienda además una capa de **caché de corta duración** (15-30 min) sobre las respuestas de CARP/SHN/SMN/Open-Meteo, para no pegarle a esas APIs en cada visita al dashboard público — decisión técnica de implementación, a confirmar en Arquitectura.

### 7. Riesgos y supuestos
Heredados de `1-analista-funcional.md` (re-expuestos, no asumidos en silencio):
- CARP, SHN y SMN sin API oficial documentada ni estabilidad garantizada — el diseño ya refleja esto en `EstacionEnVivoViewModel.Disponible` (cada fuente falla aislada, sin romper el resto del dashboard).
- Open-Meteo es la única fuente de pronóstico del MVP y puede tener menor resolución cerca de la costa que el promedio manual de Windguru — no bloquea el diseño, pero se recomienda la validación empírica corta (ya sugerida en Análisis) antes de calibrar los umbrales definitivos del `MotorDeCalculo`.
- Los umbrales de birazón/sudestada son una aproximación bibliográfica — por eso el diseño los deja como parámetros configurables (no constantes hardcodeadas) desde esta etapa, para que la bitácora (P6/P7) pueda alimentar un ajuste futuro sin rediseñar el motor.
- No hay agente implementador PHP en el catálogo del estudio — este documento no asume ningún framework/ORM PHP específico; queda para Arquitectura definir el enfoque técnico.
- Nuevo supuesto de esta etapa: se asume que el registro de usuario NO requiere verificación de email (alta directa) dado el contexto de bajo riesgo (grupo chico del club) ya confirmado en Análisis — a confirmar explícitamente con el cliente antes de Arquitectura, porque cambia si hace falta plantilla de email de verificación o no.

### 8. Plan funcional por etapas (para Arquitectura, no plan de código)
- **Etapa 1 — Núcleo de cálculo**: P1 (Home público) + estaciones en vivo + pronóstico Open-Meteo + `MotorDeCalculo` con tabla de equipo default (sin cuentas todavía). Objetivo: validar rápido que el modelo de cálculo y las fuentes de datos funcionan antes de invertir en cuentas de usuario.
- **Etapa 2 — Cuentas**: P2/P3 (login/registro) + P5 (mi equipo) + P4 (dashboard personalizado).
- **Etapa 3 — Bitácora y notificaciones**: P6 (cargar sesión) + P7 (bitácora social) + `ServicioNotificaciones` (aviso por email, reutilizando PAT-007).

## Historial de ajustes
- 2026-09-01: Diseño funcional cerrado sobre Análisis aprobado el mismo día. 7 pantallas, 5 ViewModels, motor de cálculo con reglas explícitas de birazón (2 señales independientes) y sudestada (riesgo prioritario sobre recomendación de equipo), plan funcional en 3 etapas para Arquitectura. Reutilización puntual de PAT-007 (email PHP) y criterio PAT-008 (filtro por columna visible) aplicado a bitácora social; sin patrón nuevo agregado al catálogo (motor de scoring específico del dominio, no generalizable a otros proyectos del estudio).
