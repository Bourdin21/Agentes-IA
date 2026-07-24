# Olvidata**Soft**
---

**Labipac — Resumen de sprint: Producción Mensual por Centro de Salud**
**OlvidataSoft · Julio 2026**

## Sobre el proyecto

Este sprint suma a Labipac la posibilidad de organizar tu producción mensual por Centro de Salud (privado o mutual), en lugar de llevar un único total general por mes. Ya está implementado, con la base de datos actualizada en desarrollo y listo para que lo pruebes.

## Cambios entregados

- **Catálogo de Centros de Salud:** nueva pantalla para dar de alta tus centros (privados o mutuales) con nombre y tipo, igual de simple que el resto de tus catálogos.
- **Producción Mensual por centro:** al crear un período, ahora podés elegir opcionalmente a qué Centro de Salud corresponde. Podés cargar varios períodos para el mismo mes, uno por cada centro (y seguir usando un período "global" sin centro si no lo necesitás).
- **Historial con Centro de Salud:** el listado de períodos ahora muestra a qué centro corresponde cada uno.
- **PDF con Centro de Salud:** cuando un período tiene centro asignado, el PDF lo muestra en el encabezado.

## Qué gana tu equipo con esto

- Podés llevar la producción separada por cada centro privado o mutual con el que trabajás, sin mezclar todo en un solo total mensual.
- Los períodos que ya cargaste siguen funcionando exactamente igual (quedan como "período global", sin centro asignado) — no hace falta que hagas nada con ellos.
- Es totalmente opcional: si preferís seguir cargando todo junto como hasta ahora, podés seguir haciéndolo.

## Pendientes de tu parte

- Dar de alta tus Centros de Salud (privados y mutuales) en el catálogo nuevo antes de empezar a usarlos en la carga mensual.
- Confirmarnos si tu cantidad actual de tablas en el sistema hace que corresponda pasar del Plan PRO al Plan PREMIUM de mantenimiento anual (te lo confirmamos nosotros al cierre, es solo un aviso).

## Consideraciones

- El catálogo de Centro de Salud es independiente de tus Mutuales ya sincronizadas desde FABA — son dos listas separadas, así que si un nombre (ej. "IOMA") existe en ambas, no están vinculadas entre sí.

## Próximo paso sugerido

Te pedimos que pruebes el flujo completo: dar de alta un Centro de Salud, crear un período de Producción Mensual eligiéndolo, y descargar el PDF para confirmar que se ve como esperás.

**Olvidata Soft — contacto@olvidatasoft.com — olvidatasoft.com**
