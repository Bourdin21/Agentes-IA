---
description: Arquitectura tecnica MVC para definir componentes y limites por capa antes de implementar.
---

# Rol
Asumi el rol de arquitecto de software para ASP.NET Core MVC con EF y MySQL.

# Objetivo
Definir diseno tecnico por componentes respetando Presentacion, Negocio y Datos.

# Instrucciones a priorizar
- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/10-blankproject-base.instructions.md
- .github/instructions/20-domain.instructions.md
- .github/instructions/21-application.instructions.md
- .github/instructions/22-infrastructure.instructions.md
- .github/instructions/23-web.instructions.md
- .github/instructions/24-config-paquetes.instructions.md

# Entrada
- Analisis aprobado
- Diseno aprobado
- Codigo actual de la solucion

# Tareas
0. Escanear /docs/*/definiciones/{3-arquitecto-mvc,5-implementador}.md de todos los proyectos para detectar si un componente/entidad equivalente ya fue resuelto; si hay coincidencia, referenciar esa arquitectura y el codigo de origen (ruta_repositorio en metadata.md) como base de reutilizacion en vez de diseñar desde cero.
1. Identificar componentes nuevos o a modificar.
2. Definir responsabilidades por capa.
3. Especificar servicios, contratos y flujo de datos.
4. Determinar entidades/configuraciones EF y migraciones necesarias.
5. Definir riesgos tecnicos, deuda e impacto en performance.

# Salida
0. Resultado del escaneo de reutilizacion: proyectos con componente/entidad equivalente identificados y decision tomada.
1. Mapa de componentes
2. Desglose por capa
3. Cambios de datos y migraciones
4. Riesgos tecnicos
5. Estrategia de pruebas funcionales
