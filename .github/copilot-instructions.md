# Instrucciones para GitHub Copilot — OlvidataSoft

Este repositorio contiene configuraciones de agentes de IA para los proyectos de **OlvidataSoft** y utiliza un marco modular de instrucciones por etapa y capa.

## Contexto del Proyecto

- **Organización:** OlvidataSoft
- **Repositorio:** Agentes-IA
- **Propósito:** Centralizar y estandarizar la configuración de agentes de IA utilizados en todos los proyectos de la organización.

## Secuencia operativa obligatoria

Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas -> Documentacion

## Mapa de instrucciones modulares

- .github/instructions/00-operativa-global.instructions.md
- .github/instructions/01-fronteras-por-capa.instructions.md
- .github/instructions/10-blankproject-base.instructions.md
- .github/instructions/20-domain.instructions.md
- .github/instructions/21-application.instructions.md
- .github/instructions/22-infrastructure.instructions.md
- .github/instructions/23-web.instructions.md
- .github/instructions/24-config-paquetes.instructions.md
- .github/instructions/25-frontend-design-system.instructions.md
- .github/instructions/26-checklists.instructions.md

## Directrices de Código

- Escribir comentarios y documentación en **español**.
- Seguir las convenciones de código existentes en cada proyecto.
- Preferir soluciones simples y mantenibles sobre soluciones complejas.
- Incluir manejo de errores en todas las integraciones con APIs de IA.
- No incluir claves de API ni credenciales en el código fuente.

## Reglas base que siempre aplican

- No colocar lógica de negocio compleja en Controllers.
- Los Controllers coordinan request/response y delegan en Services.
- La lógica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificación debe indicar capas afectadas y motivo.
- Si hay migración EF, debe explicitarse.
- Si hay impacto en permisos, estados o validaciones, debe listarse.
- Preservar comportamiento legacy salvo indicación contraria.
- Siempre proponer pruebas mínimas.

## Estructura del Repositorio

```
Agentes-IA/
├── .github/
│   ├── copilot-instructions.md   # Este archivo
│   └── instructions/             # Instrucciones modulares por etapa/capa
├── configs/
│   ├── github-copilot/           # Configuraciones para GitHub Copilot
│   ├── openai/                   # Configuraciones para la API de OpenAI
│   └── general/                  # Configuraciones generales de agentes
└── README.md
```

## Agentes Disponibles

- **GitHub Copilot:** Asistente de codificación integrado en el editor.
- **OpenAI API:** Integración con modelos GPT para automatización de tareas.

## Convenciones de Commits

Usar prefijos descriptivos en español o inglés:
- `feat:` — nueva funcionalidad
- `fix:` — corrección de errores
- `docs:` — cambios en documentación
- `config:` — cambios en configuración

## Formato mínimo de respuestas técnicas

1. Alcance funcional resumido.
2. Impacto técnico por capa.
3. Riesgos y supuestos.
4. Pruebas mínimas requeridas.
5. Checklist de salida para merge.
