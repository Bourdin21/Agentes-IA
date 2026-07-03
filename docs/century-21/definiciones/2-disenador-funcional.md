# Memoria - Diseñador funcional

## Proyecto: century-21
## Ultima actualizacion: 2026-07-02

## Definiciones vigentes

### 1. Alcance funcional resumido
Diseño funcional para la plataforma SaaS multi-agencia sobre la base del Análisis (etapa 1) vigente. Cubre 3 módulos:
- **Módulo 1** — CRM + Chatbot WhatsApp (consultas, clientes, alertas de fechas clave)
- **Módulo 2** — Agregador de portales (cache global + búsqueda unificada)
- **Módulo 3** — Plataforma multi-agencia (SuperAdmin, Agencias, Grupos, Planes, Catálogo propio CRUD)

**Cambio de modelo de roles (2026-07-02):** se elimina el rol `Gerente`. El sistema pasa a tener solo **2 roles**: `SuperAdmin` (plataforma, uso interno de Olvidata) y `Asesor` (único rol de negocio, operación distribuida por grupo). Lo que antes hacía el Gerente se reparte así:
- **Gestión de usuarios** (alta/baja de asesores, alta/baja de grupos, asignación de plan): pasa a `SuperAdmin`.
- **Operación diaria** (tomar consultas, reasignar entre compañeros, gestionar catálogo y clientes): se vuelve **peer-to-peer dentro del grupo** — cualquier asesor del grupo tiene los mismos permisos operativos que sus compañeros.
- El **plan (Básico/Pro/Enterprise) se contrata por Grupo**, no por Agencia — una Agencia puede tener varios Grupos, cada uno con su propio plan y su propio cupo de asesores.

No incluido en este diseño (confirmado en Análisis): bot con IA/LLM, self-service de alta de agencia, app móvil, publicación automática en portales.

### 2. Flujo de pantallas y wireframe textual por pantalla

**Plataforma — rol SuperAdmin** (gestión administrativa completa, invisible para el cliente final)
| # | Pantalla | Wireframe textual |
|---|---|---|
| SA-01 | Listado de Agencias | DataTable server-side: Nombre, Cantidad de grupos, Fecha alta. Botón "Nueva agencia". |
| SA-02 | Alta/Edición de Agencia | Form: Nombre, Razón social. Es un contenedor liviano — el plan y el cupo viven en cada Grupo, no acá. |
| SA-03 | Detalle de Agencia | Cabecera con datos de agencia + listado de sus Grupos (cada uno con su plan, cupo usado/límite y estado). |
| SA-04 | Gestión de Grupos | DataTable de grupos de una agencia (Nombre, Plan, Asesores usados/límite, Estado). Alta/edición/baja (soft delete), asignación de Plan por grupo, suspender/reactivar grupo. |
| SA-05 | Gestión de Asesores | DataTable de asesores de un grupo (Nombre, Email, Estado). Alta de asesor con validación de `CantidadAsesoresActivos < Grupo.Plan.LimiteAsesores` antes de permitir guardar. Baja (soft delete). |
| SA-06 | Gestión de Planes | Tabla fija de 3 planes (Básico/Pro/Enterprise) con límite de asesores editable por plan. Sin alta/baja de planes en Fase 1. |
| SA-07 | Configuración de WhatsApp por grupo | Form: número de WhatsApp Business, credenciales/token Meta (cifrado), estado de verificación (informativo). Configurado por grupo, no por agencia — cada grupo puede tener su propio número. |

**Asesor** (único rol de negocio, operación peer-to-peer dentro de su grupo)
| # | Pantalla | Wireframe textual |
|---|---|---|
| A-01 | Mi perfil | Datos propios editables (nombre, contacto) + estadísticas personales: consultas cerradas, consultas activas, tiempo promedio de gestión. |
| A-02 | Perfil de grupo | Estadísticas agregadas del grupo completo: consultas por estado, actividad por asesor, total del equipo. Visible para todos los asesores del grupo (reemplaza el dashboard que antes veía solo el Gerente). |
| A-03 | Bandeja de consultas del grupo | DataTable con **todas** las consultas del grupo: las libres (sin asesor asignado, disponibles para tomar) y las ya tomadas por cualquier compañero. Filtros: estado, asesor. Botón "Tomar" en las libres; botón "Reasignar a compañero" en las propias o de un compañero. |
| A-04 | Detalle de Consulta | Historial de conversación (solo lectura, mensajes bot), categorización, selector de estado (respetando máquina de estados), selector de asesor para reasignar (cualquier compañero del grupo). |
| A-05 | Perfil de Cliente | Datos de contacto, preferencias, fechas clave, historial de consultas. Compartido dentro del grupo — cualquier asesor lo ve y edita. Botón "Buscar con estas preferencias" (deep-link a A-08). |
| A-06 | Catálogo propio — Listado | DataTable de propiedades del grupo. Botón "Nueva propiedad". **Hipótesis a validar:** gestión compartida entre todos los asesores del grupo (no se especificó un dueño único por propiedad). |
| A-07 | Catálogo propio — Alta/Edición | Form: Título, Tipo, Operación, Precio, Moneda, Zona, Ambientes, Superficie, Descripción, Carga de fotos (multi-file). |
| A-08 | Búsqueda unificada | Filtros: tipo, zona, precio, ambientes, operación, origen (Propio/ZonaProp/ArgenProp/MercadoLibre/etc.). Resultados en grid con tag de fuente. Botón "Actualizar ahora" (fuerza scraping on-demand), disponible para cualquier asesor. |

**Backend sin pantalla**
| # | Proceso | Descripción |
|---|---|---|
| WH-01 | Webhook entrante WhatsApp | Recibe mensaje de Meta, resuelve el **Grupo** directamente por el número de destino (ya no resuelve Agencia primero), crea/actualiza Cliente + Consulta **sin asignar** (queda en la bandeja compartida del grupo), ejecuta flujo de menú (detalle en 2.1). |

#### 2.1 Flujo conversacional del bot (detalle — hipótesis a validar con el cliente antes de implementar)

**Primer contacto** (número desconocido): mensaje de bienvenida con menú de 4 opciones — Comprador / Alquiler / Vendedor / Valuación. Se crea el registro de `Cliente` en estado inicial apenas responde la primera opción.

**Preguntas de calificación por categoría** (motor de flujo simple, sin IA — secuencia fija de preguntas cerradas/de opción múltiple por `CategoriaConsulta`):

| Categoría | Campos que captura (mapean a `ClientePerfilViewModel`) |
|---|---|
| Comprador | TipoPropiedad, Zona, PrecioMin/PrecioMax, Ambientes |
| Alquiler | TipoPropiedad, Zona, Presupuesto mensual (→ PrecioMax), Ambientes |
| Vendedor | TipoPropiedad, Zona, Precio de referencia (opcional), Documentación en regla (booleano — **campo nuevo, no estaba en el ViewModel original, agregar si se confirma**) |
| Valuación | TipoPropiedad, Zona, Metros cuadrados (**campo nuevo — agregar `Superficie` a `ClientePerfilViewModel` si se confirma**) |

**Cierre de flujo:** al completar las preguntas, crea/actualiza `Cliente` (identificado por `Telefono` único dentro del `GrupoId`), crea `Consulta` en estado `Categorizada` (salta `Nueva` porque el flujo ya asigna la categoría), la deja sin `AsesorId` en la bandeja compartida del grupo, y responde con mensaje de confirmación al cliente.

**Casos especiales:**
- Número ya conocido (Cliente existente): el bot reconoce el perfil, no repregunta datos ya guardados, crea una `Consulta` nueva asociada al `Cliente` existente.
- Respuesta fuera del menú (texto libre en vez de elegir opción numérica): crea `Consulta` en estado `Nueva` sin `CategoriaConsulta`, queda en bandeja para categorización manual por un asesor.

**Pendiente de confirmar con el cliente antes de Implementación:** el set exacto de preguntas por categoría (arriba) es una propuesta del equipo de diseño basada en el flujo estándar de calificación de leads inmobiliarios — no fue relevado explícitamente en Análisis. Si el cliente confirma o ajusta las preguntas, puede implicar 1-2 campos nuevos en `ClientePerfilViewModel`/`Cliente` (ej. `DocumentacionEnRegla`, `Superficie`) — cambio menor, no dispara reestimación salvo que agregue lógica condicional compleja.
| JOB-01 | ScrapingDiarioJob | 3am, corre una sola vez para toda la plataforma (cache global, sin cambios). |
| JOB-02 | AlertasFechasJob | 9am, itera **grupos activos** (antes iteraba agencias) y clientes con fecha clave hoy, envía plantilla Meta con las credenciales de ese grupo. |

### 3. ViewModels propuestos

**GrupoViewModel**
| Campo | Tipo | Validación |
|---|---|---|
| Nombre | string | Requerido, máx 100, único por agencia |
| AgenciaId | int (implícito) | — |
| PlanId | int (select) | Requerido — el plan ahora se asigna acá, no en Agencia |
| Estado | enum (Activo/Suspendido) | Requerido, solo editable por SuperAdmin |
| WhatsAppNumero | string | Formato E.164, requerido antes de activar alertas |

**AsesorAltaViewModel**
| Campo | Tipo | Validación |
|---|---|---|
| Nombre / Email | string | Requerido, email válido y único |
| GrupoId | int (select) | Requerido — gestionado exclusivamente por SuperAdmin |
| Rol | fijo "Asesor" | No editable desde UI |

**PerfilAsesorViewModel** *(nuevo)*
| Campo | Tipo | Notas |
|---|---|---|
| Nombre / Email / Contacto | editable por el propio asesor | — |
| ConsultasActivas / ConsultasCerradas / TiempoPromedioGestion | solo lectura, calculado | Estadísticas personales |

**PerfilGrupoViewModel** *(nuevo)*
| Campo | Tipo | Notas |
|---|---|---|
| ConsultasPorEstado | Dictionary<Estado, int> | Agregado de todo el grupo |
| ActividadPorAsesor | lista | Consultas cerradas/activas por cada compañero del grupo |

**ConsultaViewModel**
| Campo | Tipo | Validación |
|---|---|---|
| ClienteId | int | Requerido |
| Categoria | enum (Comprador/Alquiler/Vendedor/Valuacion) | Requerido para pasar a Categorizada |
| GrupoId | int | Resuelto automáticamente por el webhook (número de WhatsApp) |
| AsesorId | int (nullable) | Se completa por **self-assign** (el asesor se la asigna a sí mismo) o por reasignación entre compañeros |
| Estado | enum | Solo transiciones válidas (ver máquina de estados) |

**ClientePerfilViewModel** — sin cambios respecto a la versión anterior, ahora scoped por `GrupoId` en vez de `AgenciaId`.

**PropiedadPropiaViewModel** — sin cambios de campos, ahora scoped por `GrupoId`.

**BusquedaUnificadaViewModel** — sin cambios.

### 4. Máquina de estados

**Consulta** (revisada — self-assign en vez de asignación por Gerente)
| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| Nueva | Categorizar | Categorizada | Categoria != null | Registra categoría | "Debe seleccionar una categoría" |
| Categorizada | Tomar (self-assign) | Asignada | Usuario actual pertenece al `GrupoId` de la consulta | Asigna `AsesorId` = usuario actual, notifica al grupo | "Solo un asesor del mismo grupo puede tomar la consulta" |
| Asignada | Iniciar gestión | En gestion | Usuario actual = asesor asignado (o cualquier compañero del grupo, ver regla de reasignación) | Registra timestamp de inicio | "Solo un asesor del grupo puede iniciar gestión" |
| En gestion | Cerrar | Cerrada | Motivo de cierre informado | Registra motivo y timestamp | "Debe indicar motivo de cierre" |
| Cualquiera excepto Cerrada | Reasignar | Asignada (a otro compañero) | Usuario actual pertenece al mismo `GrupoId`; nuevo asesor también pertenece al grupo | Reasigna `AsesorId`, mantiene historial | "Solo un asesor del mismo grupo puede reasignar" |

**Grupo** (reemplaza la máquina de estados de Agencia — el estado ahora vive acá porque acá vive el plan/pago)
| Estado origen | Evento | Estado destino | Guarda | Acción | Error esperado |
|---|---|---|---|---|---|
| — | Alta por SuperAdmin | Activo | Plan asignado | Crea grupo dentro de una agencia, sin asesores | — |
| Activo | Suspender | Suspendido | Solo SuperAdmin | Bloquea login de los asesores del grupo, conserva datos | "Solo SuperAdmin puede suspender" |
| Suspendido | Reactivar | Activo | Solo SuperAdmin | Restaura acceso | "Solo SuperAdmin puede reactivar" |

**Agencia:** ya no tiene máquina de estados propia — pasa a ser un contenedor liviano de Grupos sin ciclo de vida propio (se elimina/soft-delete directamente si hace falta).

### 5. Reglas de negocio y permisos por pantalla/acción
- SA-01 a SA-07: exclusivo `SuperAdmin`. No visible para ningún asesor.
- A-01 a A-08: requieren grupo activo; bloqueadas si `Grupo.Estado = Suspendido` (redirect a pantalla de aviso).
- **No existe distinción de permisos entre asesores de un mismo grupo** — todos pueden: tomar consultas libres, reasignar entre sí, editar clientes, gestionar catálogo propio, configurar búsquedas. La única jerarquía del sistema es `SuperAdmin` vs. `Asesor`.
- A-03 (bandeja): una consulta sin `AsesorId` es visible y "tomable" por cualquier asesor del grupo; no hay cola ni prioridad — el primero que la toma la toma (optimistic concurrency recomendado para evitar doble-toma simultánea, a validar en Arquitectura).
- Botón "Actualizar ahora" (A-08): disponible para cualquier asesor, sin distinción de rol dentro del grupo (ya no hay flag `PuedeForzarScraping` diferenciado por rol de negocio, dado que ya no hay Gerente vs. Asesor).
- SA-07 (config. WhatsApp): exclusivo `SuperAdmin`, credenciales cifradas en reposo, nunca mostradas en texto plano tras guardadas.
- Todas las pantallas de Asesor: el query de consultas/clientes/catálogo filtra siempre por `GrupoId` del asesor autenticado.

### 6. Impacto funcional por capa
- **Presentación:** 2 áreas de navegación por rol (SuperAdmin / Asesor, ya no 3), 15 pantallas (7 SuperAdmin + 8 Asesor), componente de carga de fotos reutilizable, DataTables server-side en 4 listados.
- **Negocio:** máquina de estados de Consulta revisada (self-assign en vez de asignación jerárquica) + máquina de estados de Grupo (reemplaza a Agencia); reglas de límite de plan ahora evaluadas contra `Grupo.Plan`, no `Agencia.Plan`; reglas de concurrencia para evitar doble-toma de una consulta libre; cifrado de credenciales WhatsApp ahora por grupo.
- **Datos:** `PlanId` y `WhatsAppNumero`/`WhatsAppTokenCifrado` se mueven de `Agencia` a `Grupo`. `Agencia` pasa a ser un contenedor sin estado propio ni plan propio. `AgenciaId` deja de ser el filtro de tenant principal — pasa a serlo `GrupoId`.

### 7. Riesgos y supuestos
- **Cambio de modelo de roles (2026-07-02):** se reemplaza `Gerente` por un modelo plano peer-to-peer dentro del grupo, con `SuperAdmin` asumiendo la gestión de usuarios. Esto simplifica el modelo de permisos (2 roles en vez de 3) pero elimina cualquier control jerárquico intermedio dentro de una agencia/grupo — cualquier asesor puede reasignar el trabajo de un compañero sin aprobación.
- **Hipótesis a validar antes de Implementación:** la gestión de catálogo propio y de clientes es compartida entre todos los asesores del grupo (sin dueño único por registro) — el cliente no lo especificó explícitamente, se infiere del modelo peer-to-peer general.
- **Riesgo de concurrencia:** con self-assign en bandeja compartida, dos asesores pueden intentar tomar la misma consulta al mismo tiempo — requiere control de concurrencia optimista (ver Arquitectura) para que solo uno la tome.
- **Riesgo operativo:** sin un rol con visión jerárquica, una consulta puede quedar "flotando" en la bandeja sin que nadie la tome. Fuera de alcance de este diseño una alerta automática por consulta sin tomar — se deja como mejora futura a evaluar.
- El botón "Actualizar ahora" (scraping on-demand) sigue siendo global (afecta a todas las agencias/grupos porque el cache es compartido).

### 8. Plan funcional por etapas (para Arquitectura)
- **Etapa 1 (MVP):** Módulo 3 completo (SuperAdmin, Agencia, Grupo, Plan, Asesor) + Módulo 1 completo (CRM + bot + alertas) — es lo mínimo para que un grupo opere y para poder dar de alta agencias/grupos nuevos.
- **Etapa 2:** Módulo 2 completo (agregador de portales + catálogo propio CRUD + búsqueda unificada).

## Historial de ajustes
- 2026-06-25: Archivo creado en bootstrap del proyecto.
- 2026-07-02: Diseño funcional completo sobre la base del pivot SaaS multi-agencia. 14 pantallas definidas en 3 roles (SuperAdmin/Gerente/Asesor), 6 ViewModels, 2 máquinas de estados (Consulta + Agencia nueva). Pendiente confirmar con cliente: multi-grupo por asesor y modo de ruteo de Consulta a Grupo. Entregado a Arquitectura.
- 2026-07-02: **Cambio de modelo de roles.** Se elimina el rol Gerente. Ahora 2 roles: SuperAdmin (gestión de usuarios/grupos/agencias/planes) y Asesor (único rol de negocio, operación peer-to-peer dentro del grupo, sin jerarquía). Plan pasa de Agencia a Grupo (cada grupo contrata su propio plan). Consultas se reparten por bandeja compartida con self-assign, no por asignación manual de un Gerente. WhatsApp se configura por Grupo, no por Agencia. Pantallas rediseñadas: 7 SuperAdmin + 8 Asesor (perfil propio y perfil de grupo nuevos). Riesgo de concurrencia en self-assign documentado para Arquitectura. Reenviado a Arquitectura y Presupuesto para reestimación (gatillo de reestimación: cambio de reglas de negocio y permisos).
