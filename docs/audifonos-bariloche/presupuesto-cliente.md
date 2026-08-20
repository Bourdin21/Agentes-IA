# Olvidata**Soft**

---

**Propuesta de desarrollo — Sistema de Turnos e Historia Clínica**
**OlvidataSoft · Agosto 2026**

---

## Sobre el sistema

Un sistema para que tu equipo maneje los turnos de cada profesional y la historia clínica de cada paciente en un solo lugar, con los estudios y pedidos médicos ya digitalizados y a mano en cada consulta.

- Tu recepción carga un turno nuevo eligiendo paciente, profesional y horario, y el sistema no te deja pisar un turno ya tomado de esa misma profesional.
- Cada profesional entra y ve su propia agenda del día, sin mezclarse con la de las demás.
- Al atender a un paciente, la profesional carga su nota en la historia clínica y puede subir ahí mismo la foto del pedido médico o el estudio, sacada con el celular — nada de tener que buscarlo después en WhatsApp.
- Tu recepción tiene un panel con todos los turnos del día de todo el centro, para organizar la sala de espera de un vistazo.
- Cada usuario entra con su propio acceso: recepción gestiona turnos y pacientes, cada profesional ve y carga solo lo suyo.

---

## Rol de usuario

| Rol | Accesos |
|---|---|
| Recepción | Alta de pacientes, gestión de turnos de todas las profesionales, panel de turnos del día. No edita notas clínicas. |
| Profesional | Su propia agenda, historia clínica y documentos de sus pacientes atendidos. |

*El alta de usuarios y la configuración inicial del sistema las gestionamos nosotros como parte del servicio.*

---

## Etapa 1 (MVP) — por módulo

Así queda el costo abierto módulo por módulo, para que veas exactamente qué cubre cada parte del sistema. Los primeros cinco módulos están encadenados (turnos y pacientes necesitan usuarios y accesos; la historia clínica necesita pacientes; los documentos adjuntos necesitan la historia clínica) — por eso conforman el MVP funcional mínimo. Panel del día y puesta en marcha son parte del mismo paquete pero se muestran aparte para que veas el detalle completo.

| Módulo | USD |
|---|---:|
| Usuarios y accesos por rol (recepción / profesional) | USD 34 |
| Gestión de pacientes | USD 84 |
| Turnos y agenda por profesional | USD 134 |
| Historia clínica digital | USD 151 |
| Documentos adjuntos en la historia clínica (fotos y PDF desde el celular) | USD 17 |
| Panel de turnos del día | USD 34 |
| Puesta en marcha (dominio, hosting) | USD 34 |
| **Subtotal Etapa 1** | **USD 488** |

## Etapa 2 (opcionales — sumalos cuando quieras)

Estos dos módulos son independientes entre sí y del resto del sistema — se pueden agregar al arrancar o más adelante, sin tocar lo ya construido.

| Módulo | USD |
|---|---:|
| Recordatorio de turno por WhatsApp | USD 67 |
| Reportes de turnos por profesional y ausentismo | USD 34 |
| **Subtotal Etapa 2** | **USD 101** |

*El recordatorio por WhatsApp requiere dar de alta una cuenta de WhatsApp Business propia del centro — el trámite de verificación lo hacemos con vos, pero el tiempo de aprobación depende de Meta (de días a un par de semanas).*

## Total del proyecto

| Concepto | USD |
|---|---:|
| Subtotal Etapa 1 | USD 488 |
| Subtotal Etapa 2 | USD 101 |
| **Subtotal desarrollo (sin Tokens IA)** | **USD 589** |
| Optimización de desarrollo (componentes ya probados) | -USD 177 |
| **Tokens IA (25% del subtotal desarrollo)** | **USD 147** |
| **Total proyecto** | **USD 559** |

---

## Mantenimiento anual

| Plan | USD/año |
|---|---:|
| PREMIUM + 3 usuarios adicionales | USD 800 |

*Incluye hosting, actualizaciones de seguridad, soporte prioritario y 2 rondas de ajuste al año, más 3 usuarios adicionales sobre el plan base para cubrir el equipo de ~6 personas. Cambios funcionales nuevos se cotizan aparte. Si el equipo crece en cantidad de profesionales con el tiempo, el plan SCALE (USD 850/año, usuarios ilimitados) puede convenir más — lo conversamos cuando haga falta.*

---

## Qué incluye el proyecto

- Desarrollo funcional del alcance detallado por etapas.
- Pruebas funcionales internas y entrega operativa.
- Ajustes menores de puesta en marcha dentro del alcance acordado.

## Qué no está incluido

- Migración de datos desde tu sistema actual.
- Facturación o integración con obras sociales.
- Aplicación móvil (se accede desde el navegador, funciona bien en celular).
- Cambios de alcance posteriores al inicio (se cotizan aparte).

---

## Lo que necesitamos de tu parte

- Confirmar si además de las 6 personas manejan algo de obra social o facturación en el día a día, o es 100% particular.
- Un listado o ejemplo de los datos que cargan hoy por paciente, para no dejar ningún campo importante afuera.

---

## Condiciones comerciales

- Forma de pago: 50% al inicio y 50% a la entrega de cada etapa.
- Moneda: USD.
- El cargo de Tokens IA equivale al 25% del subtotal de desarrollo y se informa como ítem individual, separado del mantenimiento anual.
- Cambio de alcance disponible en cualquier momento si el proyecto crece (se cotiza aparte).

---

**Olvidata Soft — olvidatasoft@gmail.com — www.olvidata.com.ar**
