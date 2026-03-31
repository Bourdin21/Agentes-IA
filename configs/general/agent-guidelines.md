# Directrices Generales para el Uso de Agentes de IA — OlvidataSoft

## Principios

1. **Revisión humana obligatoria:** Todo código generado por IA debe ser revisado por un desarrollador antes de ser integrado.
2. **Seguridad:** Nunca proporcionar datos sensibles (contraseñas, claves, datos de clientes) a agentes de IA externos.
3. **Atribución:** Documentar qué partes del código fueron generadas con ayuda de IA.
4. **Responsabilidad:** El desarrollador que integra el código generado por IA es responsable de su corrección y calidad.

## Agentes Aprobados

| Agente | Proveedor | Uso Permitido |
|--------|-----------|---------------|
| GitHub Copilot | GitHub / Microsoft | Asistencia en codificación, sugerencias en el editor |
| GPT-4o (API) | OpenAI | Automatización de tareas, generación de contenido |

## Flujo de Trabajo Recomendado

1. El desarrollador describe la tarea al agente de IA.
2. El agente genera una propuesta de solución.
3. El desarrollador revisa, ajusta y prueba el código.
4. Se integra al proyecto siguiendo el proceso estándar de revisión de código (PR / code review).

## Configuración por Proyecto

Para agregar la configuración de agentes de IA a un nuevo proyecto:

1. Copiar `.github/copilot-instructions.md` al repositorio del proyecto y adaptar el contenido.
2. Copiar `configs/github-copilot/settings.json` a `.vscode/settings.json` del proyecto.
3. Si se usa la API de OpenAI, copiar `configs/openai/.env.example` a `.env.example` y `configs/openai/agent-config.json`.
4. Agregar los patrones de `.gitignore` recomendados del archivo `configs/general/.gitignore-ai`.

## Métricas de Uso

Se recomienda registrar el uso de IA por proyecto para evaluar su impacto:
- Porcentaje de código asistido por IA
- Tiempo ahorrado en tareas repetitivas
- Incidencias relacionadas con código generado por IA
