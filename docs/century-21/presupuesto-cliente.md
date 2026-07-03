# Suscripción — CRM, Chatbot WhatsApp y Buscador de Propiedades
**OlvidataSoft · Julio 2026**

---

## Sobre el sistema

Un sistema de gestión comercial para tu equipo que centraliza todo el proceso de atención a clientes, desde el primer contacto hasta el cierre, y unifica en un solo buscador las propiedades de los principales portales del mercado junto con tu propio catálogo.

El sistema cubre todo el ciclo:

- Un cliente escribe al WhatsApp de la inmobiliaria y el sistema responde automáticamente con un menú guiado, captura sus preferencias y crea su perfil (ver detalle abajo)
- La consulta queda visible para todo tu equipo en una bandeja compartida: cualquier asesor disponible la toma, con estado claro (Nueva → Categorizada → Asignada → En gestión → Cerrada) y puede pasársela a un compañero si hace falta
- Cada asesor tiene su propio perfil con sus estadísticas (consultas cerradas, tiempo promedio) y un perfil de equipo con las estadísticas de todo el grupo
- El sistema recuerda fechas importantes de cada cliente (cumpleaños, aniversario de compra) y envía un saludo automático por WhatsApp
- Un buscador único combina las propiedades de tu catálogo propio con las publicadas en MercadoLibre, ZonaProp y ArgenProp, identificando de qué fuente viene cada resultado (ver detalle abajo)
- Desde el perfil de un cliente se puede lanzar una búsqueda con sus preferencias ya cargadas como filtro

Todos los planes incluyen las mismas funciones completas — la diferencia entre planes es la cantidad de asesores de tu equipo.

---

## Cómo funciona el chatbot de WhatsApp — paso a paso

**1. Primer contacto.** Un número de teléfono que escribe por primera vez activa el mensaje de bienvenida automático con el menú principal:

> ¡Hola! 👋 Bienvenido/a a [tu inmobiliaria]. Contame qué estás buscando:
> 1️⃣ Quiero comprar una propiedad
> 2️⃣ Busco alquilar
> 3️⃣ Quiero vender mi propiedad
> 4️⃣ Quiero una valuación

**2. Preguntas de calificación según la opción elegida.** El bot sigue con 3 o 4 preguntas puntuales, distintas para cada categoría:

| Categoría | Preguntas del bot |
|---|---|
| **Comprador** | Tipo de propiedad (depto / casa / PH / local / terreno) · Zona o barrio · Rango de precio · Cantidad de ambientes |
| **Alquiler** | Tipo de propiedad · Zona · Presupuesto mensual · Cantidad de ambientes |
| **Vendedor** | Tipo de propiedad · Zona · Precio de referencia (si lo tiene) · Si ya cuenta con la documentación en regla |
| **Valuación** | Tipo de propiedad · Zona · Metros cuadrados aproximados |

*Las preguntas exactas por categoría son una propuesta inicial (hipótesis a validar con vos antes de implementar) — se pueden ajustar o agregar/quitar campos según cómo trabaje hoy tu equipo comercial.*

**3. Cierre automático de la conversación.** Con las respuestas completas, el sistema:
- Crea (o actualiza, si ya es un cliente conocido) el perfil del cliente con sus datos de contacto y preferencias
- Genera la consulta ya categorizada y la deja en la bandeja compartida de tu equipo
- Responde al cliente confirmando que un asesor lo va a contactar a la brevedad

**4. Casos especiales contemplados:**
- **Cliente ya conocido** (mismo número escribe de nuevo): el bot lo identifica por su perfil existente y arranca una consulta nueva sin volver a pedir todos los datos desde cero
- **Respuesta libre en vez de elegir una opción del menú:** la consulta queda registrada igual, sin categoría automática, visible en la bandeja para que un asesor la categorice manualmente al tomarla

Todas las preferencias capturadas (zona, tipo, precio, ambientes) quedan disponibles después como filtro de un clic para buscar propiedades que coincidan, desde el perfil del cliente.

---

## Cómo funciona el buscador unificado

**Fuentes que combina:**

| Fuente | Cómo se conecta |
|---|---|
| Tu catálogo propio | Siempre al día — lo cargás vos desde el sistema |
| MercadoLibre | Conexión directa a su buscador de propiedades |
| ZonaProp | A través de un servicio externo especializado que sortea las protecciones anti-robots de ese sitio (no se puede acceder de forma directa) |
| ArgenProp | Mismo mecanismo que ZonaProp |

**Actualización de los datos externos:** el sistema trae las propiedades de MercadoLibre, ZonaProp y ArgenProp automáticamente todas las madrugadas. Además, cualquier asesor tiene un botón "Actualizar ahora" para forzar una actualización en el momento si necesita datos más frescos antes de una búsqueda puntual. *(Aclaración: la búsqueda en sí es instantánea porque consulta esta base ya actualizada — no vuelve a consultar los portales externos en cada clic, salvo que se use el botón de actualización manual.)*

**Cómo se filtra:** tipo de propiedad, zona, rango de precio, cantidad de ambientes y tipo de operación (venta / alquiler). Cada resultado muestra una etiqueta con su origen (Propio / MercadoLibre / ZonaProp / ArgenProp), así tu equipo sabe siempre de dónde salió cada propiedad antes de ofrecérsela a un cliente.

**Caso de uso típico:** un asesor abre el perfil de un cliente que ya completó el menú del bot (por ejemplo, busca un departamento de 2 ambientes en una zona y rango de precio determinado) y con un clic lanza la búsqueda unificada con esos datos precargados como filtro — sin tener que volver a tipearlos.

---

## Rol de usuario

| Rol | Accesos |
|---|---|
| **Asesor** | Todas las consultas de su equipo en la bandeja compartida (puede tomarlas y reasignarlas entre compañeros sin restricciones), clientes, catálogo propio, buscador, su perfil individual y el perfil de estadísticas del equipo |

> El alta de tu equipo, la organización del grupo y la configuración del WhatsApp de la inmobiliaria las gestionamos nosotros como parte del servicio — no requiere que nadie de tu equipo administre usuarios dentro del sistema.

---

## Planes disponibles

El servicio es exactamente el mismo en los tres planes — lo único que cambia es la cantidad de asesores incluidos. Y a mayor cantidad de asesores, **más barato sale por asesor** (precio por volumen).

Facturación exclusivamente anual.

| Plan | Asesores incluidos | Plan anual | Equivalente mensual | USD/asesor por mes (al tope del plan) |
|---|---|---:|---:|---:|
| **Básico** | Hasta 3 | **USD 600/año** | ~USD 50/mes | ~USD 16,67 |
| **Pro** | Hasta 10 | **USD 1.850/año** | ~USD 154/mes | ~USD 15,42 |
| **Enterprise** | 11 o más | **USD 1.850/año** + USD 150/año por asesor extra sobre 10 (ej. 11 asesores = USD 2.000/año, 15 asesores = USD 2.600/año) | desde ~USD 167/mes | desde ~USD 15,15, bajando con cada asesor extra |

---

## Qué incluye el plan

- Chatbot de WhatsApp con menú automático de atención y alertas automáticas de fechas clave
- CRM de consultas con bandeja compartida entre los asesores del equipo
- Perfil individual de cada asesor + perfil de estadísticas del equipo
- Buscador unificado de propiedades (MercadoLibre, ZonaProp, ArgenProp)
- Catálogo propio de propiedades con fotos
- Puesta en marcha, configuración inicial y soporte técnico continuo a cargo de Olvidata
- Actualizaciones de seguridad y mantenimiento del servicio

## Qué no está incluido

- Bot conversacional con inteligencia artificial (evolución futura a evaluar)
- Publicación automática de propiedades en los portales externos
- Aplicación móvil nativa (iOS / Android)
- Integración con sistemas contables o de firma digital
- Conexión de solo lectura a una base de datos de propiedades existente (se releva y cotiza aparte si se requiere)
- Costo variable de las conversaciones de WhatsApp Business ante Meta, según el consumo de tu equipo (factura directa de Meta, no de Olvidata)
- Migración de datos desde sistemas anteriores
- Cambios de alcance fuera de lo descripto (se cotizan aparte)

---

## Lo que necesitamos de tu parte

**Para dar de alta el grupo:**
1. Listado del equipo de asesores que va a usar el sistema
2. Cuenta de Meta Business verificada y número de WhatsApp Business dedicado — el proceso de verificación de Meta puede tardar 1 a 3 semanas, conviene iniciarlo apenas se confirme el plan
3. Plantillas de mensajes para las alertas de fechas clave, aprobadas por Meta
4. Confirmar qué portales externos activar además de MercadoLibre (ZonaProp / ArgenProp)

---

## Condiciones comerciales

- **Forma de pago:** 100% al confirmar el alta (primer año de plan)
- **Renovación:** anual, mismo valor salvo ajuste de tasa informado con anticipación
- **Moneda:** USD
- Cambio de plan disponible en cualquier momento si el equipo crece (se ajusta la diferencia proporcional)
