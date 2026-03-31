# Instrucciones para GitHub Copilot — OlvidataSoft

Este repositorio contiene configuraciones de agentes de IA para los proyectos de **OlvidataSoft**.

## Contexto del Proyecto

- **Organización:** OlvidataSoft
- **Repositorio:** Agentes-IA
- **Propósito:** Centralizar y estandarizar la configuración de agentes de IA utilizados en todos los proyectos de la organización.

## Directrices de Código

- Escribir comentarios y documentación en **español**.
- Seguir las convenciones de código existentes en cada proyecto.
- Preferir soluciones simples y mantenibles sobre soluciones complejas.
- Incluir manejo de errores en todas las integraciones con APIs de IA.
- No incluir claves de API ni credenciales en el código fuente.

## Estructura del Repositorio

```
Agentes-IA/
├── .github/
│   └── copilot-instructions.md   # Este archivo
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
