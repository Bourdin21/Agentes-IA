# Metadata del proyecto

- nombre: KOI
- fecha_inicio: 2026-06-11
- estado: activo
- owner: Joaquín Bourdin
- descripcion: Sistema web de gestión para inversores de la franquicia gastronómica KOI. Dashboard con métricas del local (ingresos, gastos, resultado, rentabilidad, valores en USD), estado de resultados mensual, esquema de puntos de inversión y reparto de utilidades por inversor, indicadores de venta (Ayres POS, carga manual) y visualización de cámaras IP (Hik-Connect embebido). Reemplaza dos Excel operativos: "Estado de Resultados KOI (Inversores)" y "Reparto de Utilidades Inversores".
- ruta_definiciones: /docs/koi/definiciones

## Archivos de memoria por agente
- analista-funcional: /docs/koi/definiciones/1-analista-funcional.md
- disenador-funcional: /docs/koi/definiciones/2-disenador-funcional.md
- arquitecto-mvc: /docs/koi/definiciones/3-arquitecto-mvc.md
- presupuestador: /docs/koi/definiciones/4-presupuestador.md
- implementador: /docs/koi/definiciones/5-implementador.md
- qa: /docs/koi/definiciones/6-qa.md
- documentador: /docs/koi/definiciones/7-documentador.md

## Fuentes del relevamiento
- /docs/Estado de Resultados KOI (Inversores).xlsx — hojas 2024/2025/2026, estado de resultados mensual del local.
- /docs/Reparto de Utilidades Inversores .xlsx — hojas Puntos, GENERAL y una hoja por inversor (15 inversores).
- Sistema de ventas actual: Ayres POS (totalizadores mensuales cargados a mano; integración directa = etapa 2).
- Cámaras: Hikvision vía Hik-Connect (datos de acceso se entregan en la implementación).
