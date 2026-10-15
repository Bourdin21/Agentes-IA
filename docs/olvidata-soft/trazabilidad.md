# Trazabilidad — memoria de negocio de Olvidata Soft

Registro de cambios de `docs/olvidata-soft/`. Una línea por decisión o cambio; el detalle vive en el archivo que corresponde.

### 2026-10-15 - olvidata-ceo
- **Se separa la memoria del negocio del rol del agente.** Antes todo vivía dentro de `.claude/agents/olvidata-ceo.md` (67 KB, cargado entero en cada consulta). Pasa a `precios.md`, `plan.md`, `negocio.md` y `clientes.md`; el agente queda con el rol y una tabla de punteros.
- **Precios centralizados en `precios.md`** (decisión de Joaquín). Fijados hoy: Landing 3D USD 1.000 + 400/año; 2D autogestionable renueva a 375; upgrade a 3D +500/+100; upsell módulo nuevo vigente; combo con 10% sobre setup; pilotos 30% sobre setup, máximo 3 por frente; reglas de volumen de Chatbots; montos de AI Agents (rediseño 2026-10-13) incluido mensual Organización S/M/L 90/150/250.
- La tabla "Lista 2027" de AI Agents por tier quedó superada con su base: la lista 2027 se recalculó como ×1,20 sobre la lista vigente.

### 2026-10-15 - olvidata-marketing
- **Reglas de comunicación consolidadas en `comunicacion.md`** (COM-01..11), con `olvidata-marketing` como dueño. Estaban copiadas en `ceo`, `marketing` y `cm` y desincronizadas: `ceo` y `marketing` seguían prohibiendo abrir por el dolor en Agentes IA cuando `cm` ya tenía la derogación del 2026-10-14. Queda vigente la derogación (COM-04).
- Regla nueva COM-09: ChatGPT, Claude y Copilot son el motor, no competencia.
