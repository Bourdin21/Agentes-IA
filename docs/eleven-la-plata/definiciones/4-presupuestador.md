# Memoria - Presupuestador

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

## Definiciones vigentes

### Nota de contexto comercial
`eleven-la-plata` no opera bajo el ciclo comercial externo estándar (no hay negociación de presupuesto con el cliente final por cada item — Joaquín gestiona el proyecto y autoriza el trabajo directamente). Por eso este ciclo NO genera `presupuesto-cliente.md` ni tabla PERT/USD formal — se deja una estimación interna liviana solamente, y el gate de aprobación queda satisfecho por la instrucción explícita: *"solucionar bug crítico, el resto depende de definiciones con el usuario"* (2026-08-20).

### H1 — Estimación interna (2026-08-20)
- **Tipo de item:** ajuste puntual (fix de validación en un service existente, sin pantallas nuevas, sin migración).
- **Referencia histórica:** no hay un caso 1:1 en otros proyectos (lógica de negocio específica de facturación por contador). Se estima directamente por alcance de código: 1 archivo (`AlquilerService.cs`), 1 método nuevo extraído + 1 condicional agregado en `UpdateAsync`, sin cambios de capa Presentación/Datos.
- **Horas estimadas:** 1.5–2.5 h (implementación + build + verificación de las 5 pruebas funcionales definidas en Arquitectura). Riesgo: **Bajo**.
- **Aprobado para pasar a Implementación:** sí.

## Historial de ajustes
- 2026-08-20: Gate de Presupuesto satisfecho por autorización directa del owner del proyecto. Sin documento comercial generado (no aplica para este proyecto).
