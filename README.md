# Agentes-IA

Repositorio centralizado de configuracion de agentes de IA para proyectos de OlvidataSoft, con una arquitectura de instrucciones modular y orientada a MVC + EF Core + MySQL.

## Objetivo

Estandarizar como se analizan, disenan e implementan cambios tecnicos y funcionales usando agentes, separando reglas globales de reglas por capa para reducir ambiguedad y facilitar reutilizacion.

## Secuencia Operativa Obligatoria

Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas -> Documentacion

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
|   |   `-- 26-checklists.instructions.md
|   |-- agents/
|   `-- prompts/
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

## Como Aplicar Esta Arquitectura en un Proyecto

1. Copiar `.github/copilot-instructions.md` y la carpeta `.github/instructions/` al repositorio destino.
2. Configurar editor con `configs/github-copilot/settings.json` en `.vscode/settings.json`.
3. Usar la secuencia operativa obligatoria para cada feature o cambio.
4. Para cada cambio, explicitar capas afectadas, riesgos y pruebas minimas.
5. Si hay impacto en permisos, estados, validaciones o migraciones EF, declararlo de forma explicita.

## Formato Minimo de Respuesta Tecnica

1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas minimas requeridas.
5. Checklist de salida para merge.

## Seguridad

- Nunca incluir claves de API ni credenciales en el codigo fuente.
- Usar siempre variables de entorno para gestionar secretos.
- Revisar y validar todo codigo generado por IA antes de integrar.
