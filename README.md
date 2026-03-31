# Agentes-IA

Repositorio centralizado de configuración de agentes de IA para los proyectos de **OlvidataSoft**.

## Descripción

Este repositorio contiene las configuraciones, plantillas y directrices para integrar y estandarizar el uso de agentes de inteligencia artificial en todos los proyectos de la organización.

## Estructura

```
Agentes-IA/
├── .github/
│   └── copilot-instructions.md   # Instrucciones personalizadas para GitHub Copilot
├── configs/
│   ├── github-copilot/           # Configuración de GitHub Copilot
│   │   ├── README.md
│   │   └── settings.json         # Configuración recomendada para VS Code
│   ├── openai/                   # Configuración de la API de OpenAI
│   │   ├── README.md
│   │   ├── agent-config.json     # Parámetros del agente (modelo, temperatura, etc.)
│   │   └── .env.example          # Variables de entorno necesarias
│   └── general/                  # Directrices y configuraciones generales
│       ├── README.md
│       ├── agent-guidelines.md   # Directrices generales de uso
│       └── .gitignore-ai         # Patrones de .gitignore recomendados
└── README.md
```

## Agentes Disponibles

| Agente | Directorio | Descripción |
|--------|------------|-------------|
| GitHub Copilot | `configs/github-copilot/` | Asistente de codificación integrado en el editor |
| OpenAI API | `configs/openai/` | Integración con modelos GPT para automatización |

## Cómo Agregar Configuración de IA a un Proyecto

1. **GitHub Copilot:** Copiar `.github/copilot-instructions.md` al repositorio del proyecto y adaptarlo.
2. **VS Code:** Copiar `configs/github-copilot/settings.json` a `.vscode/settings.json`.
3. **OpenAI API:** Copiar `configs/openai/.env.example` y `configs/openai/agent-config.json` al proyecto.
4. **`.gitignore`:** Agregar los patrones de `configs/general/.gitignore-ai` al `.gitignore` del proyecto.

## Directrices de Uso

Consultar [`configs/general/agent-guidelines.md`](configs/general/agent-guidelines.md) para las directrices generales de uso de agentes de IA en OlvidataSoft.

## Seguridad

- **Nunca** incluir claves de API ni credenciales en el código fuente.
- Usar siempre variables de entorno para gestionar secretos.
- Revisar el código generado por IA antes de integrarlo.
