# 0 - Indice de definiciones (entrada del Agente principal)

Este directorio contiene la memoria estructurada del proyecto **VirtualWallet** generada por agentes IA. El Agente principal debe leer estos documentos en orden para construir contexto antes de tomar decisiones.

## Convencion de uso para agentes IA

- Cada doc es **autonomo y autoritativo** sobre su scope. Si hay conflicto, manda el doc mas especifico.
- Los docs `5-implementador.md` y `6-qa.md` son **memoria viva** (se actualizan por etapa). Los demas son **definiciones estables**.
- No editar codigo a partir de estos docs sin antes leer el archivo fuente referenciado: los docs reflejan el estado conocido pero el codigo es la verdad.

## Mapa de documentos

| # | Documento | Proposito | Audiencia |
|---|-----------|-----------|-----------|
| 0 | `0-indice.md` | Indice y reglas de uso | Agente principal |
| 1 | `1-vision-arquitectura.md` | Vision de producto y arquitectura por capas | Todos los agentes |
| 2 | `2-dominio.md` | Modelo de dominio, entidades, enums e invariantes | Implementador / QA |
| 3 | `3-aplicacion-infraestructura.md` | Casos de uso, DTOs, servicios, persistencia | Implementador |
| 4 | `4-web-ui.md` | Controllers MVC, vistas Razor, JS y assets | Implementador / QA |
| 5 | `5-implementador.md` | Memoria acumulativa de etapas de implementacion | Implementador |
| 6 | `6-qa.md` | Memoria acumulativa de QA y defectos | QA |
| 7 | `7-operaciones.md` | Deploy, migraciones, configuracion y secretos | DevOps / Implementador |
| 8 | `8-convenciones.md` | Reglas de codigo, naming, estilo, idioma | Todos los agentes |

## Datos rapidos

- **Repo**: `https://gitlab.com/olvidata/virtualwallet` (rama `main`).
- **Ruta local**: `C:\Sistemas\virtualwallet\`.
- **TFM**: `net10.0` en las 4 capas.
- **Solucion**: `VirtualWallet.sln` con proyectos `Domain`, `Application`, `Infrastructure`, `Web`.
- **DB**: MySQL via Pomelo + EF Core 10.0.x.
- **Auth**: ASP.NET Core Identity con roles `SuperUsuario` y `Usuario`.
- **Idioma del codigo y UI**: espaniol (sin tildes en identificadores), comentarios en espaniol.

## Flujo recomendado para el Agente principal

1. Leer `1-vision-arquitectura.md` para entender capas y dependencias.
2. Leer `2-dominio.md` antes de cualquier cambio que toque entidades o reglas de negocio.
3. Consultar `3-` o `4-` segun la capa afectada.
4. Revisar `5-` y `6-` para conocer la etapa en curso y defectos abiertos.
5. Cualquier deploy o migracion: `7-operaciones.md`.
6. Antes de codificar, validar contra `8-convenciones.md`.
