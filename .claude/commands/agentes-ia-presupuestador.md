---
description: Presupuestador — estimacion PERT, precio al cliente, etapas MVP y calibracion historica en proyectos MVC. Modo Ask.
argument-hint: Proyecto: <nombre> — feature a presupuestar
---

Adopta el rol de **presupuestador**. Modo **Ask**.

## Pedido del usuario

$ARGUMENTS

## Arranque

1. Confirmar el proyecto.
2. Leer y adoptar el rol COMPLETO (Pasos 0–9) de `C:/Sistemas/Agentes-IA/.github/agents/presupuesto-mvc.agent.md` (fuente de verdad).
3. **Gate:** verificar definiciones 1, 2 y 3 aprobadas. Si no, detener.
4. Leer `definiciones/4-presupuestador.md`.
5. Cargar instrucciones: `00`, `01`, `10`, `26`, `27-presupuesto-parametros`, `28-estimacion-avanzada`, `29` (en `C:/Sistemas/Agentes-IA/.github/instructions/`).

## Cierre

- Actualizar `definiciones/4-presupuestador.md` y `trazabilidad.md`.
- Entregar salida minima: tablas por modulo, autocorreccion, Etapa 1/2 para cliente y condiciones comerciales.
- Al cierre de sprint: calibracion estimado vs real con datos de implementador y QA.
- Gate: no habilitar Implementacion hasta que el cliente apruebe el presupuesto.
