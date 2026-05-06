# Trazabilidad del proyecto

Registro acumulativo de decisiones y ajustes por etapa y agente.

## Entradas

### 2026-04-22 17:58 - presupuestador
- Etapa: Presupuesto
- Cambio: se ejecuto la estimacion funcional del sistema ganaderia con WBS por modulos visibles, PERT por item, contingencia por tipo de modulo y autocorreccion contra historicos.
- Motivo: contar con una base presupuestaria trazable antes de implementacion.
- Impacto en capas: Presentacion, Negocio y Datos.
- Riesgos/supuestos: alcance estimado sobre analisis funcional v10, diseno funcional v1 y arquitectura tecnica v1; se contemplan 2 migraciones EF y reutilizacion de componentes ya resueltos de la solucion base.

### 2026-04-22 - implementador
- Etapa: 0 - Preparacion y fundaciones
- Cambio: creacion de estructura de carpetas Ganaderia en las 4 capas, alta de los 9 enums del dominio, constantes `RolesGanaderia` y `MatrizTransicionesCategoria`, y helpers Web `CalculoIvaHelper` y `FormatoCorrelativoHelper`.
- Motivo: dejar fundaciones tecnicas listas antes de modelar entidades y migraciones.
- Impacto en capas: Domain (enums + constantes), Web (helpers). Application e Infrastructure solo carpetas.
- Riesgos/supuestos: ninguno especifico de etapa. Solucion ya renombrada a `Ganaderia.*` y conexion `ganaderia_dev` configurada.