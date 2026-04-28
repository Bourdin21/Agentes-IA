# Agentes-IA

Repositorio centralizado de configuracion de agentes de IA para los proyectos de **OlvidataSoft**.

Repositorio centralizado de configuracion de agentes de IA para proyectos de OlvidataSoft, con una arquitectura de instrucciones modular y orientada a MVC + EF Core + MySQL.

## Objetivo

Estandarizar como se analizan, disenan e implementan cambios tecnicos y funcionales usando agentes, separando reglas globales de reglas por capa para reducir ambiguedad y facilitar reutilizacion.

## Secuencia Operativa Obligatoria

Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

## Arquitectura Establecida

### Capas y responsabilidades

- Presentacion: Controllers, Views, ViewModels, validaciones de pantalla.
- Negocio: Services, reglas de negocio, estados, permisos y procesos.
- Datos: DbContext, entidades, configuraciones EF, migraciones y acceso MySQL.

### Reglas base transversales

- No colocar logica de negocio compleja en Controllers.
- Controllers coordinan request/response y delegan en Services.
- La logica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Preservar comportamiento legacy salvo indicacion contraria.

## Estructura del Repositorio

```
Agentes-IA/
|-- .github/
|   |-- copilot-instructions.md
|   |-- instructions/
|   |   |-- 00-operativa-global.instructions.md
|   |   |-- 01-fronteras-por-capa.instructions.md
|   |   |-- 10-blankproject-base.instructions.md
|   |   |-- 20-domain.instructions.md
|   |   |-- 21-application.instructions.md
|   |   |-- 22-infrastructure.instructions.md
|   |   |-- 23-web.instructions.md
|   |   |-- 24-config-paquetes.instructions.md
|   |   |-- 25-frontend-design-system.instructions.md
|   |   |-- 26-checklists.instructions.md
|   |   |-- 27-presupuesto-parametros.instructions.md
|   |   |-- 28-estimacion-avanzada.instructions.md
|   |   `-- 29-trazabilidad-conversacion.instructions.md
|   |-- agents/
|   `-- prompts/
|-- docs/
|   |-- README.md
|   |-- conversaciones/
|   `-- templates/
|-- configs/
|   |-- general/
|   |   |-- README.md
|   |   |-- agent-guidelines.md
|   |   `-- .gitignore-ai
|   |-- github-copilot/
|   |   |-- README.md
|   |   `-- settings.json
|   `-- openai/
|       |-- README.md
|       |-- agent-config.json
|       `-- .env.example
`-- README.md
```

## Mapa de Instrucciones Modulares

- `.github/instructions/00-operativa-global.instructions.md`: marco comun de trabajo y formato de salida.
- `.github/instructions/01-fronteras-por-capa.instructions.md`: limites arquitectonicos por capa.
- `.github/instructions/10-blankproject-base.instructions.md`: baseline tecnico de plataforma.
- `.github/instructions/20-domain.instructions.md`: reglas de Domain.
- `.github/instructions/21-application.instructions.md`: reglas de Application.
- `.github/instructions/22-infrastructure.instructions.md`: reglas de Infrastructure.
- `.github/instructions/23-web.instructions.md`: reglas de Web MVC.
- `.github/instructions/24-config-paquetes.instructions.md`: configuracion y paquetes.
- `.github/instructions/25-frontend-design-system.instructions.md`: lineamientos UI.
- `.github/instructions/26-checklists.instructions.md`: checklists de implementacion.
- `.github/instructions/27-presupuesto-parametros.instructions.md`: parametros base de tarifa y calibracion historica.
- `.github/instructions/28-estimacion-avanzada.instructions.md`: metodo PERT, contingencia por riesgo y calibracion periodica.
- `.github/instructions/29-trazabilidad-conversacion.instructions.md`: trazabilidad por conversacion en `/docs` y definiciones por agente en archivos individuales.

## Trazabilidad de Conversaciones en /docs

Cada proyecto persiste su memoria de trabajo en `/docs/<proyecto>/`, con un archivo por agente.

Estructura oficial:

```
/docs/
  indice.md
  <proyecto>/
    metadata.md
    trazabilidad.md
    definiciones/
      1-analista-funcional.md
      2-disenador-funcional.md
      3-arquitecto-mvc.md
      4-presupuestador.md
      5-implementador.md
      6-qa.md
      7-documentador.md
```

Reglas obligatorias:
- Cada agente edita su unico archivo de definicion en `/docs/<proyecto>/definiciones/`.
- Si el archivo no existe, se crea desde `/docs/templates/proyecto/definiciones/`.
- No duplicar archivos para el mismo agente y proyecto.
- Cada ajuste relevante se registra tambien en `/docs/<proyecto>/trazabilidad.md`.
- El indice consolidado de proyectos vive en `/docs/indice.md`.

## Mapa de Prompts por Etapa

- `.github/prompts/00-discovery.prompt.md`: discovery y relevamiento formal.
- `.github/prompts/01-analisis.prompt.md`: analisis funcional trazable.
- `.github/prompts/02-diseno.prompt.md`: diseno funcional de pantallas y validaciones.
- `.github/prompts/03-arquitectura.prompt.md`: arquitectura tecnica por capas.
- `.github/prompts/04-presupuesto.prompt.md`: presupuesto con WBS, PERT y riesgo.
- `.github/prompts/05-implementacion.prompt.md`: ejecucion de cambios en codigo.
- `.github/prompts/06-pruebas.prompt.md`: pruebas funcionales.
- `.github/prompts/07-documentacion.prompt.md`: documentacion de alcance para cliente.
- `.github/prompts/08-cierre-calibracion.prompt.md`: cierre de calibracion estimado vs real.
- `.github/prompts/09-orquestador-flujo-completo.prompt.md`: orquestador maestro de la secuencia completa por etapas.

## Como Aplicar Esta Arquitectura en un Proyecto

1. Copiar `.github/copilot-instructions.md` y la carpeta `.github/instructions/` al repositorio destino.
2. Configurar editor con `configs/github-copilot/settings.json` en `.vscode/settings.json`.
3. Usar la secuencia operativa obligatoria para cada feature o cambio.
4. Para cada cambio, explicitar capas afectadas, riesgos y pruebas funcionales.
5. Si hay impacto en permisos, estados, validaciones o migraciones EF, declararlo de forma explicita.
6. La documentacion final debe ser de alcance para el cliente.
7. Cerrar cada presupuesto con calibracion estimado vs real para recalibrar parametros.

## Formato Minimo de Respuesta Tecnica

1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales minimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.

## Agentes Disponibles

Flujo funcional por etapa, definidos en `.github/agents/`:

| # | Agente | Archivo | Etapa que cubre |
|---|--------|---------|-----------------|
| 1 | Analista funcional | `analista-funcional.agent.md` | Discovery + Analisis |
| 2 | Disenador funcional | `disenador-funcional.agent.md` | Diseno funcional + maquina de estados |
| 3 | Arquitecto MVC | `arquitecto-mvc.agent.md` | Arquitectura tecnica + permisos + EF |
| 4 | Presupuestador | `presupuesto-mvc.agent.md` | Presupuesto + cierre de calibracion |
| 5 | Implementador .NET | `implementador-dotnet.agent.md` | Implementacion + build + pruebas minimas |
| 6 | QA | `qa-mvc.agent.md` | Pruebas funcionales + criterios de aceptacion |
| 7 | Documentador | `documentador.agent.md` | Documentacion de alcance al cliente |

Gates de aprobacion: ninguna etapa puede iniciar sin el cierre de la anterior en `/docs/<proyecto>/definiciones/`.

## Directrices de Uso

Consultar [`configs/general/agent-guidelines.md`](configs/general/agent-guidelines.md) para las directrices generales de uso de agentes de IA en OlvidataSoft.

## Seguridad

- Nunca incluir claves de API ni credenciales en el codigo fuente.
- Usar siempre variables de entorno para gestionar secretos.
- Revisar y validar todo codigo generado por IA antes de integrar.
