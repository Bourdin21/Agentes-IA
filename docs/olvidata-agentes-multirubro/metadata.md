# Metadata del proyecto

- nombre: olvidata-agentes-multirubro
- fecha_inicio: 2026-09-13
- estado: activo — template del producto (sin clientes en producción)
- owner: bourdinjoaquin@gmail.com
- descripcion: Plataforma SaaS propia de Olvidata Soft (modelo D): un único sistema multi-tenant para todos los rubros y todos los clientes, con núcleo IP de agentes versionado, motor de agentes server-side reanudable y portal web como único canal. Es producto interno del estudio: el "cliente" que aprueba etapas es Joaquín.
- ruta_definiciones: /docs/olvidata-agentes-multirubro/definiciones
- ruta_repositorio: C:\Sistemas\Olvidata Agentes Multi-rubro
- stack: ASP.NET Core MVC .NET 10 + EF Core 10 + MySQL (base blankproject), SDK oficial Anthropic .NET, SignalR
- hosting_previsto: SmarterASP (cuenta actual), migración a cuenta nueva si la demanda crece

## Pendientes abiertos (decisión de Joaquín 2026-09-14: quedan abiertos y se sigue con la próxima etapa)
| # | Pendiente | Origen | Requiere |
|---|---|---|---|
| PA-01 | Evaluar y publicar las 3 reglas de plataforma (borrador #56–#58 en dev: no inventar datos, no revelar instrucciones, pedir precisiones) | M3 | Revisión de texto y OK de Joaquín |
| PA-02 | Corrida real contra la API: obediencia de reglas e inyección, calidad de ajustes, caché de bloques y del historial, error de conversación demasiado larga, reanudación real | M3 / M3b | OK de costo de Joaquín (~USD 0,30–0,60) |
| PA-03 | Reanudación tras reinicio espera el vencimiento del lease (hasta 5 min) | M3b QA (heredado M1) | Priorizar mejora antes de producción |
| PA-04 | `ReglasCambiaronAsync` sin protección en el detalle de tarea | M3b QA | Mejora menor |
| PA-05 | Staff sin UI para editar nombre/email/rol/estado de miembros; `Tenant.Estado` no bloquea sesión; pantallas legadas sin diseño nuevo | M2 | Priorizar |
| PA-06 | Agentes mostrados por slug (nombre del núcleo); filtros de texto solo con `keyup`; mensajes menores de M3 (OBS-M3-2..5) | M2 / M3 QA | Mejora menor |
| PA-07 | Confirmar AlwaysRunning con soporte de SmarterASP (requisito de M12 y de la reanudación) | Hosting | Joaquín |
| PA-08 | Confirmar la sección "Archivados" del catálogo de agentes (agregada por el implementador fuera del diseño; QA la considera clara) | M4 | Decisión de Joaquín |
| PA-09 | Avisar a la autora cuando el Director edita un agente de la empresa que ella creó | M4 QA | Decisión de Joaquín |
| PA-10 | Escribir contenido real del rubro "negocio" (agentes de marketing/CM/ventas) y de las reglas sugeridas | M4 | Joaquín |
| PA-11 | Contraste de botones y enlaces compartidos del portal (OLV-004: `btn-outline-secondary` oscuro 3,12; `btn-outline-info` claro 1,96; color de marca claro 2,70–2,98) | M4b QA | Decisión de diseño/marca de Joaquín |
| PA-12 | "Ver pasos" muestra nombres de herramientas y JSON crudo a usuarios no técnicos (muy visible en el configurador); mensaje "Podés pedirle que siga…" a quien no puede seguir; título actual vs. visto en tarjetas de cambio | M4b QA | Mejora de diseño |
| PA-13 | Revisar, evaluar y publicar el prompt del configurador (`nucleo/plataforma/agentes/configurador-reglas.md`, #65 Borrador en dev) | M4b | Joaquín |

## Documentación de diseño en el repo
- PLAN-IMPLEMENTACION.md — plan rector y decisiones de producto
- docs/arquitectura.md — arquitectura del template
- docs/diseno-motor-agentes.md — motor de agentes (M1 implementada)
- docs/diseno-organizacion-roles-reglas.md — organización, áreas, roles, reglas y agentes por nivel (decisiones 2026-09-14)

## Archivos de memoria por agente
- analista-funcional: /docs/olvidata-agentes-multirubro/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/olvidata-agentes-multirubro/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/olvidata-agentes-multirubro/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/olvidata-agentes-multirubro/definiciones/4-presupuestador.md
- implementador: /docs/olvidata-agentes-multirubro/definiciones/5-implementador.md
- qa: /docs/olvidata-agentes-multirubro/definiciones/6-qa.md
- documentador: /docs/olvidata-agentes-multirubro/definiciones/7-documentador.md
