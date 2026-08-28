# Memoria - Documentador

## Proyecto: crm-olvidata — CRM interno de OlvidataSoft
## Ultima actualizacion: 2026-08-27

## Definiciones vigentes

### Alcance entregado al cliente

**Sprint: corrección de bugs/gaps de auditoría completa + 3 mejoras — en producción desde el 27/08/2026.**

Se auditó el CRM completo (13 pantallas) buscando errores reales y funcionalidad a medio construir, y se corrigió todo lo encontrado en una sola pasada. En criollo, esto es lo que cambia para el uso diario:

- **Los chats dejan de mostrarte cosas raras.** Antes podías ver, dentro de una conversación, una burbuja "tuya" con texto interno del sistema (tipo "Rubro" o un aviso de bot ajeno) como si se lo hubieras escrito vos al prospecto. Ya no pasa.
- **"No leído" ahora es confiable.** Si dejabas un chat abierto en otra pestaña, el sistema lo marcaba leído solo, aunque el contacto te hubiera vuelto a escribir. Corregido — ahora sólo se marca leído cuando de verdad lo viste.
- **Los números de "Respuesta → Presupuesto" dejan de ser distintos según la pantalla.** Bot/Outbound, Contactos/Pipeline y Campañas/Dashboard ahora muestran el mismo número, calculado una sola vez.
- **El canal "Referido" ya funciona de punta a punta.** Podés cargar un contacto que te llegó por referido de un cliente, decir quién lo mandó, y ese contacto entra al circuito de prioridad y al template dedicado que ya existían pero nunca se podían usar.
- **Eliminar una industria del catálogo ahora te avisa el impacto real** — cuántos contactos se quedan sin ninguna campaña que los alcance — y te deja reasignarlos a otra industria en el mismo paso, en vez de tener que hacerlo por script.
- **Renombrar un template ya no puede romper una campaña en silencio** — si está en uso, el sistema te avisa y no te deja hasta que la desactives.
- **Un mensaje entrante largo ya no puede tirar abajo el envío de toda una campaña.**
- **Nueva pantalla `/Bot/Salud`**: un chequeo rápido del estado del pipeline outbound (templates sin campaña, campañas mal configuradas, contactos sin alcance) sin tener que pedir una auditoría completa cada vez.
- Más un puñado de ajustes menores: la corrida manual del pipeline ya no puede duplicar envíos con el scheduler automático, "marcar todos los chats como leídos" ya no es lento, el primer año gratis de un cliente se puede marcar desde el alta (no solo editando después), y el presupuesto cotizado de un contacto ya es editable a mano.

### Pendientes o fuera de alcance

- **17 inconsistencias menores** detectadas en la misma auditoría quedaron documentadas pero fuera de este sprint (no eran bugs ni gaps, cosas más chicas — ej. zona horaria de 2 lugares puntuales, filtros de vencimiento solapados en Clientes). Disponibles para una ronda futura si se pide.
- **4 hallazgos nuevos del propio proceso de QA de este sprint** (CRM-009, 011, 013, 014 — ver `6-qa.md`), todos menores, ninguno bloqueante: un caso límite del fix de "No leído" con la pestaña en foco, el tope de reintentos de un template de catálogo que no resetea, comentarios de código con referencias desactualizadas, y una protección incidental (no una regla explícita) que evita tocar contactos con conversación en curso al reasignar una industria.
- **G1 (templates de catálogo dinámicos) con alcance reducido a propósito**: soporta N placeholders de texto, no botones QUICK_REPLY dinámicos — un template de catálogo con botones sigue sin poder darse de alta por UI.
- El "camino de respaldo" para campañas cuya industria de catálogo no tiene la FK poblada no se ejerció en las pruebas (en dev todas las campañas la tienen) — vale la pena mirar el primer resultado real en producción si alguna vez aparece ese caso.
- Ninguno de los 3 hallazgos escalados (CRM-007/010/012, ya corregidos) ni los 4 nuevos del re-test quedaron dados de alta en el catálogo cross-proyecto (`docs/qa/regresiones-manuales.yml`/`32-estandares-qa-implementador.instructions.md`) — decisión pendiente del cliente sobre si cargarlos ahora o dejarlos solo documentados en este proyecto.

### Beneficios comunicados

Sistema propio más confiable para el trabajo diario de calificación y seguimiento de leads — menos "¿por qué el número no cierra?" entre pantallas, menos texto raro en los chats, y una función que antes estaba construida pero inalcanzable (Referido) ahora se puede usar de verdad. Sin downtime — el deploy no requirió ninguna migración de base de datos.

### Proximo paso sugerido

1. Decidir si cargar los patrones nuevos (vocabulario de rubro duplicado sin FK, `ExecuteUpdateAsync` sin auditoría automática) al catálogo cross-proyecto — quedaron redactados por QA pero no dados de alta.
2. Revisar en vivo `/Bot/Salud` una vez que haya actividad real post-deploy, para confirmar que el semáforo de "alineadas" se comporta como se espera.
3. Si en algún momento se quiere retomar G1 completo (botones dinámicos en templates de catálogo) o las 17 inconsistencias menores, son la base natural del próximo sprint.

## Historial de ajustes
- 2026-08-27: Primera ficha de documentación real de este proyecto (plantilla nunca se había completado). Cierre del sprint "corrección de bugs/gaps de auditoría + 3 mejoras": 17 items + 3 correcciones post-QA (CRM-007/010/012), deployado a producción sin downtime ni migraciones, verificado 200 OK. QA final: GO.
