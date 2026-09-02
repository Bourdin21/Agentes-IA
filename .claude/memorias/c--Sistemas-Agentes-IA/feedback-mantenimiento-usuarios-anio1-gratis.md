---
name: feedback-mantenimiento-usuarios-anio1-gratis
description: "Reglas de mantenimiento vigentes desde 2026-08-27: usuarios NUNCA modifican el precio del plan (solo mencion de detalle pasado 10), primer año siempre gratis por defecto sin trackear costo aparte, y facturacion AFIP/ARCA ya no es exclusion fija"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2bb59244-3415-45d6-9052-8072386118cb
  modified: 2026-09-01T17:29:40.569Z
---

Tres reglas de presupuesto/mantenimiento cambiaron el 2026-08-27, todas ya aplicadas en `.github/instructions/27-presupuesto-parametros.instructions.md` y `.github/agents/presupuesto-mvc.agent.md` del repo Agentes-IA — esta memoria es el resumen rapido para no tener que releer el archivo completo (400+ lineas) en cada presupuesto nuevo.

**1. Usuarios ya NO son un factor de precio, en ningun sentido.** El plan de mantenimiento (STARTER/PRO/PREMIUM/SCALE) se determina EXCLUSIVAMENTE por cantidad de tablas de negocio del sistema entregado. La cantidad de usuarios del cliente no se calcula, no se suma como cargo, y no debe usarse para elegir el plan (error real cometido una vez: clasificar Peras del Olmo como PREMIUM razonando desde 4 usuarios cuando por tablas correspondia PRO). Lo unico permitido es una mencion de detalle en el documento cliente, sin cifra: "a partir de mas de 10 usuarios pueden aplicar valores extra a acordar en su momento" — nunca calcular ni exponer un numero de upsell por usuario dentro del presupuesto.

**2. El primer año de mantenimiento va SIEMPRE gratis por defecto**, en todo Build inicial de cliente nuevo — ya no es una promocion excepcional reservada para cuando el cliente objeta el precio (ese era el criterio vigente hasta el mismo dia 2026-08-27, ver `27-presupuesto-parametros.instructions.md` seccion "aclaracion sobre objecion de precio", ahora marcada Superseded). Comunicar al cliente solo: el plan definido + que el año 1 es gratis. **El costo de regalar ese año ya esta contemplado dentro del presupuesto general — no crear ninguna linea, calculo interno ni tracking de "costo del año gratis" en ningun lado** (Joaquin lo rechazo explicitamente cuando se lo propuse como mejora — el margen ya lo absorbe, no hace falta visibilidad adicional).

**Excepcion a ambas reglas:** si hay una recomendacion estrategica explicita de `olvidata-ceo` para un cliente puntual con perfil atipico (ver [[feedback-consulta-ceo-perfil-atipico]], caso FABINCO — B2B de 50 años con capacidad de pago establecida), esa recomendacion puntual prevalece sobre el default — declararlo explicitamente como excepcion, no asumir que sigue vigente sin volver a confirmarla en cada proyecto nuevo.

**3. Facturacion electronica AFIP/ARCA dejo de ser "exclusion fija".** Desde que `marihogar` la tiene funcionando en produccion real con CAE, es un modulo cotizable estandar (PAT-006 en `docs/patrones/catalogo.yml`, circuito documentado en `34-integracion-afip-arca.instructions.md`) — se ofrece u omite segun lo que el cliente confirme, no se excluye por default. Ya se cotizo activamente en varios proyectos nuevos (desborder-sin-gluten, dietetica-mitre, Peras del Olmo Opcion Full).

**Como aplicar:** al armar cualquier presupuesto nuevo en Agentes-IA, dar por vigentes estas 3 reglas sin tener que releer todo el historial de cambios de precio de la sesion — solo re-verificar si alguna nota `Superseded` mas reciente aparecio en `27-presupuesto-parametros.instructions.md` (las reglas de precio de este estudio cambian seguido).

**4. Al dar un precio "de arranque" verbal a un prospecto (WhatsApp/mail, todavia sin presupuesto formal), anclar en USD 400/año (PRO), no en USD 300/año (STARTER).** Confirmado 2026-09-01 (lead Orígenes Almacén Natural, dietética Córdoba): el borrador decia "arranca en USD 300/año", Joaquin lo corrigio a "arranca en USD 400/año". Motivo implicito: un sistema real de stock+ventas (no solo facturacion simple) casi nunca entra en el rango de tablas de STARTER (1-5) — citar 300 como piso genera expectativa de un plan que en la practica casi nunca aplica a este tipo de sistema. Usar USD 400/año como ancla conversacional de "arranca en" salvo que el alcance ya confirmado sea deliberadamente minimo (ej. Opcion B solo-facturacion de las dietéticas, ahi si puede ser STARTER/300).

**5. Nunca mencionar "usuarios" como driver de precio, ni siquiera de pasada en una respuesta conversacional.** El mismo mensaje corregido cambio "El plan exacto depende de cuánto necesites (productos, usuarios)" por "...(desde productos / catálogo / ventas, hasta pedidos / caja mensual / facturas y proyección financiera)" — el rango de precio se explica por ALCANCE FUNCIONAL (cuanto del sistema completo se necesita: solo catalogo/ventas vs. tambien caja/facturas/proyeccion), nunca por cantidad de usuarios. Coherente con la regla 1 de arriba (usuarios no modifican precio) — pero esta confirma que ni siquiera debe aparecer como ejemplo ilustrativo en una respuesta informal.
