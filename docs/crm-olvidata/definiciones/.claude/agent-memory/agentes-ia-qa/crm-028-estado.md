---
name: crm-028-estado
description: CRM-028 (Web Push) está GO de código desde el 2026-10-16; CRM-029 cerrado, CRM-030 abierto como minor conocido; faltan certificado, privada VAPID y un chequeo manual del service worker
metadata:
  type: project
---

CRM-028 (Web Push para chats derivados a mano) pasó QA el **2026-10-15** (19 criterios PASS) y la
re-verificación del fix de CRM-029 el **2026-10-16**. Estado al 2026-10-16: **GO para subir en lo que
depende del código.**

- **CRM-029 cerrado** (el anti-ruido se re-armaba por el polling de `Chats/HiloParcial`). El fix
  agregó `Contacto.FechaUltimaLecturaDeliberadaAgente` + `RegistrarLecturaDeliberada`, y el guard
  cuelga solo de la fecha nueva. Medido: pestaña abierta + 3 mensajes → 1 aviso; tras abrir el
  detalle, el siguiente sí avisa.
- **CRM-030 abierto, minor, sin fix.** `EstadosManualesPermitidos` es `Enum.GetValues<EstadoEmbudo>()`,
  así que un contacto puede volver a `DerivadoManual` a mano: avisado → Descartado → DerivadoManual
  deja el guard con el aviso viejo puesto y 0 avisos. Degrada sin perder nada (el chat sigue visible
  en la bandeja de no leídos). Hipótesis de fix: limpiar `FechaUltimoAvisoDerivado` cuando el
  contacto sale de `DerivadoManual`.
- Pendientes que **no** son del código: el certificado de `portal.olvidata.com.ar` vencía el
  **2026-10-19** y el owner decidió no renovarlo entonces; la privada VAPID la carga el coordinador
  en el deploy. Sin HTTPS válido el push no existe.
- **Sigue pendiente un chequeo manual de 5 minutos** en un navegador real: activar los avisos,
  recargar 3 veces, confirmar que el botón sigue en "activados" y que llega un globo con el CRM
  cerrado. Nunca se pudo verificar por [[entorno-sin-navegador]].

**Why:** el riesgo de esta feature es de infraestructura, no de implementación; si no queda separado
se lee como si el código estuviera mal.

**How to apply:** si vuelve a aparecer CRM-028 o CRM-030, verificar primero contra el estado actual
(certificado, privada, y si el chequeo manual ya se hizo) antes de volver a probar código. Un defecto
no se cierra en la corrida que lo encontró: el criterio arranca en FAIL.

**Límite del arnés que hay que saber de entrada:** los 3 puntos de lectura deliberada que son envíos
(`EnviarMensaje`, `EnviarPresupuestoPdf`, `EnviarImagen`) **no son ejecutables** en QA — estampan
recién después de un envío exitoso a Meta y la URL de la Graph API está hardcodeada en
`WhatsAppClient`, así que no admite un doble local ni hay destinatario seguro. Se cubren con un
invariante mecánico (una sola escritura directa de `FechaUltimaLecturaAgente` en `ChatsController`,
la del tick; las otras 4 por `RegistrarLecturaDeliberada`) y se declaran **no ejecutados**, no PASS.
