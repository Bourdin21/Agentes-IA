# Metadata del proyecto

- nombre: yaghan-rental
- fecha_inicio: 2026-08-12
- estado: presupuesto cerrado 2026-08-13 — precio único de desarrollo USD 850 (sistema completo, CRM de WhatsApp incluido) + mantenimiento USD 600/año (primer año sin cargo) + Etapa 2 opcional USD 185 — pendiente de envío y aprobación del cliente; sin aprobación del cliente aún, no se inicia Implementación
- owner: Yaghan Rental (Ushuaia, Tierra del Fuego) — agencia de alquiler/venta de ropa de nieve/térmica
- descripcion: Sistema de gestión de ventas y alquileres de indumentaria de nieve (camperas, botas, pantalones térmicos, accesorios) con CRM de WhatsApp (consultas entrantes, cotización, reserva), control de vencimientos, checklist operativo diario, comisiones por referido, compras a proveedores/talleres, caja diaria y devoluciones por escaneo de QR con aviso automático por WhatsApp.
- ruta_definiciones: /docs/yaghan-rental/definiciones
- ruta_repositorio: <pendiente — se crea en Implementación, ver 32-estandares-qa-implementador y precedente de copiar+sanear un proyecto reciente>
- referencia_web_cliente: https://yaghanrental.com.ar/tienda/

## Archivos de memoria por agente
- analista-funcional: /docs/yaghan-rental/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/yaghan-rental/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/yaghan-rental/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/yaghan-rental/definiciones/4-presupuestador.md
- implementador: /docs/yaghan-rental/definiciones/5-implementador.md
- qa: /docs/yaghan-rental/definiciones/6-qa.md
- documentador: /docs/yaghan-rental/definiciones/7-documentador.md

## Reutilización cross-proyecto detectada (Discovery)
- **CRM WhatsApp (envío/recepción, webhook, deduplicación)**: `crm-olvidata` (`C:\Sistemas\olvidatasoft-crm`) — `WhatsAppClient`, webhook `/webhook/whatsapp`, `IWhatsAppClient.SendTextAsync/SendTemplateAsync`. Reutilizable para envíos automáticos (recordatorio de reseña, aviso de atraso) y para la bandeja de consultas entrantes, adaptando el flujo (acá es atención humana desde el sistema, no un bot conversacional automático).
- **Caja diaria / cierre de caja**: `la-platense` (`C:\Sistemas\Ferreteria La Platense`, ver `docs/la-platense/definiciones/1-analista-funcional.md` PF7/PF8 — cierre de caja diario y mensual, cuenta corriente consolidada del negocio).
- **Sin precedente en el estudio**: comisión por referido sobre venta/alquiler, devolución por escaneo de QR desde dispositivo móvil, pricing escalonado por cantidad de días de alquiler, gestión de talleres de reparación — se diseñan desde cero en este proyecto (quedan como nueva referencia para futuros proyectos con alquiler/turismo).
