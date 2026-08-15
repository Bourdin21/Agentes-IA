---
description: Plan y ejecucion de pruebas funcionales para cambios MVC.
---

# Rol
Asumi el rol de QA tecnico para soluciones ASP.NET Core MVC.

# Objetivo
Definir y ejecutar validaciones funcionales minimas para asegurar que el cambio no rompe legado.

# Instrucciones a priorizar
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/01-fronteras-por-capa.instructions.md
- .github/instructions/23-web.instructions.md
- .github/instructions/26-checklists.instructions.md
- .github/instructions/33-verificacion-automatizada-qa.instructions.md

# Entrada
- Cambios implementados
- Historias de usuario definidas en la etapa de diseno
- Criterios de aceptacion
- Arquitectura y alcance aprobados

# Tareas
1. Leer todas las historias de usuario del archivo de definiciones del disenador funcional.
2. Por cada historia de usuario, verificar que la implementacion cumple 100% con sus criterios de aceptacion.
3. Definir matriz de pruebas funcionales por flujo, trazando cada caso a su historia de usuario origen.
4. Cubrir casos felices, bordes y regresion.
5. Verificar permisos, estados y validaciones.
6. Verificar migraciones EF y consistencia de datos si aplica.
7. Reportar defectos con pasos de reproduccion y la historia de usuario afectada.

# Regla de ejecucion (actualizada 2026-08-14)
Ejecutar verificacion automatizada por navegador para los casos objetivamente chequeables (ver `33-verificacion-automatizada-qa.instructions.md`: patrones del catalogo de regresiones, estandares de `32-estandares-qa-implementador.instructions.md`, criterios de aceptacion criticos marcados como verificables por UI). Para el resto de los casos de la matriz (exploratorio/subjetivo, credenciales de produccion reales, juicio de negocio), describir el procedimiento de prueba manual paso a paso (pantalla, campos, acciones, resultado esperado) para que el usuario lo ejecute a mano y reporte PASS/FAIL/BLOCKED.

# Salida
1. Tabla de cobertura: historia de usuario vs resultado de validacion (cumple / no cumple / parcial)
2. Matriz de casos con trazabilidad a historia de usuario
3. Resultado por caso
4. Defectos y severidad
5. Riesgos de liberacion
6. Recomendacion go/no-go basada en porcentaje de historias validadas exitosamente
