# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-08-26 - orquestador (Discovery + Analisis + Diseno + Arquitectura + Presupuesto — reutilizando desborder-sin-gluten)
- Etapa: Discovery, Analisis, Diseno, Arquitectura, Presupuesto (pasada consolidada).
- Cambio: creado el proyecto `dietetica-mitre` (Av. Godoy Cruz 394, Mendoza) a partir de la misma calificacion outbound que desborder-sin-gluten (mismo pitch, mismo rubro). Discovery limpio, sin el problema de respuestas fuera de orden del lead anterior: pain point identico ("facturo todo a mano"), manejan hoy con "Papel" (mas simple que "otro sistema" de desborder), 1 sola persona sin ambiguedad. A pedido explicito de Joaquin ("armar un presupuesto con el mismo concepto y precio"), se reutilizo integramente el WBS, PERT y los numeros finales YA CERRADOS de `desborder-sin-gluten` — Propuesta B USD 400, Propuesta A USD 650, primer año de mantenimiento gratis en ambas, sin recalcular de cero. Unica diferencia de diseño: Identity simplificado a 1 rol de negocio (Administracion) por no haber ambiguedad de usuarios; mantenimiento sin upsell en ninguna opcion (STARTER/PRO cubren exacto a 1 persona).
- Motivo: pedido explicito del cliente.
- Impacto en capas: ninguno de codigo — documento de propuesta. Sin repo creado todavia.
- Riesgos/supuestos: mismos supuestos que desborder-sin-gluten (condicion fiscal AFIP no confirmada, certificado .p12 dependencia del cliente). Al ser numeros reutilizados de otro proyecto (no recalculados con PERT propio), si Dietetica Mitre pide un alcance distinto en la demo, se necesita una reestimacion real, no un ajuste menor. **Gate cliente pendiente**: propuesta lista para revision de Joaquin antes de enviarse al lead real.

## Historial de ajustes
- 2026-08-26: primera version.
