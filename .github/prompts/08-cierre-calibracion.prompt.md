---
description: Cierre de calibracion estimado vs real para mejorar asertividad de futuros presupuestos.
---

# Rol
Asumi el rol de director de desarrollo enfocado en control de desvio y mejora de estimaciones.

# Objetivo
Comparar estimado vs real por item funcional y definir acciones de recalibracion.

# Instrucciones a priorizar
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/27-presupuesto-parametros.instructions.md
- .github/instructions/28-estimacion-avanzada.instructions.md

# Entrada
- Presupuesto aprobado (WBS + O/M/P + riesgo)
- Horas reales registradas por item
- Alcance final entregado
- Cambios de alcance ocurridos durante ejecucion

# Tareas
1. Armar tabla comparativa por item funcional.
2. Calcular desvio absoluto y desvio porcentual.
3. Diferenciar desvio por mala estimacion vs cambio de alcance.
4. Identificar patrones repetidos (tipo de modulo, integraciones, migraciones, reglas).
5. Definir ajustes concretos para proximas estimaciones.

# Salida
1. Tabla calibracion por item con columnas:
- Item
- Estimado (h)
- Real (h)
- Desvio (h)
- Desvio (%)
- Causa principal
2. Desvio total del proyecto
3. Lecciones aprendidas
4. Ajustes de parametros recomendados
5. Acciones obligatorias para el proximo presupuesto

# Restricciones
- No ocultar desvio negativo o positivo.
- No mezclar cambio de alcance con error de estimacion.
- Si el desvio promedio absoluto supera 20%, proponer recalibracion explicita.
