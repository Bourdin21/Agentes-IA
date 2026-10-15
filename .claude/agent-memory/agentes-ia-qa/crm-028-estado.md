---
name: crm-028-estado
description: CRM-028 (Web Push) quedó NO-GO el 2026-10-15 por el certificado que vence el 2026-10-19 y la privada VAPID sin cargar en producción, no por el código
metadata:
  type: project
---

CRM-028 (Web Push para chats derivados a mano) pasó QA el **2026-10-15** con 19 criterios PASS y
1 defecto minor (**CRM-029**), y quedó en **NO-GO para producción**. Lo que bloquea no es el código:

1. El certificado de `portal.olvidata.com.ar` vence el **2026-10-19** y sin HTTPS válido el push no
   existe. Deployar antes de resolverlo es publicar algo que se apaga en días.
2. `Push:PrivateKey` no está cargada en el sitio (va en `appsettings.Secrets.json` del directorio del
   sitio o en la variable `Push__PrivateKey`). Sin ella el canal queda inerte: degrada bien, pero no
   avisa nada.
3. R1 (que `push-sw.js` sobreviva a las recargas con el `unregister` selectivo del `_Layout`) y la
   llegada real del globo a un navegador quedaron **NO VERIFICADOS** por [[entorno-sin-navegador]].

**Why:** el reporte de QA es la pieza con la que se toma la decisión de deploy, y el riesgo real de
esta feature es de infraestructura, no de implementación — si eso no queda separado, se lee como si
el código estuviera mal.

**How to apply:** si vuelve a aparecer CRM-028 (re-verificación de CRM-029, o el deploy), chequear
primero el estado del certificado y si la privada ya está en el sitio **antes** de volver a probar el
código, y confirmar contra el estado actual (estas tres cosas pueden haberse resuelto). El chequeo
manual que falta es de 5 minutos en el navegador de Joaquín: activar los avisos, recargar 3 veces,
confirmar que el botón sigue en "activados" y que llega un globo con el CRM cerrado.

CRM-029, para la re-verificación: el anti-ruido "un aviso por chat hasta que alguien lo lea" se cae a
"un aviso por mensaje" cuando la pestaña del chat queda abierta, porque `Chats/HiloParcial` estampa
`FechaUltimaLecturaAgente` en cada tick que trae mensajes nuevos. **Un defecto no se cierra en la
corrida que lo encontró**: el criterio arranca de nuevo en FAIL y la assertion es 3 mensajes seguidos
con la pantalla de detalle abierta en background → **1** aviso.
