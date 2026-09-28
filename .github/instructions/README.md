# Instrucciones Modulares BlankProject

Esta carpeta divide las reglas en modulos reutilizables por etapa y por capa.

## Antes que todo: cuanto de esto cargar
**39-presupuesto-contexto.instructions.md** define el techo de contexto de arranque por agente y como leer los
archivos grandes (por indice, no por cuerpo). Se lee completa y primero: los archivos de abajo suman 280 KB, y
cargarlos todos es exactamente lo que degrada el razonamiento del agente. `python scripts/contexto.py indice <alias>`
da el indice de cualquiera de ellos.

## Orden sugerido de lectura
1. 00-operativa-global.instructions.md
2. 01-fronteras-por-capa.instructions.md
3. 10-blankproject-base.instructions.md
4. 20-domain.instructions.md
5. 21-application.instructions.md
6. 22-infrastructure.instructions.md
7. 23-web.instructions.md
8. 24-config-paquetes.instructions.md
9. 25-frontend-design-system.instructions.md
10. 26-checklists.instructions.md
11. 27-presupuesto-parametros.instructions.md
12. 28-estimacion-avanzada.instructions.md

## Memoria tecnica por dominio (se lee cuando el proyecto la toca, no en orden)
- 30-qa-regresiones · 32-estandares-qa-implementador · 33-verificacion-automatizada-qa — QA
- 31-formato-documento-cliente — entregables al cliente
- **34-integracion-afip-arca** — circuito de facturacion electronica (WSAA + WSFEv1). Obligatorio antes de facturar
- 35-pantalla-control-stock — patron de pantalla de stock
- 36-metodologia-pacs
- **37-servicios-externos-fiscales** — que expone ARCA, ARBA, COMARB, SOS Contador y Onvio, que tarea acorta cada
  servicio y **que NO existe**. Obligatorio **antes de cotizar cualquier conector** de un proyecto contable/impositivo
- **38-diseno-pantallas-portal** — decisiones de diseño de pantallas del portal (listados con filtros plegados,
  conversaciones como expediente, grillas de tarjetas, estados vacíos). Leer ANTES de maquetar una pantalla nueva.
- **39-presupuesto-contexto** — techo de arranque por agente, carga por indice, reset de contexto entre etapas,
  techo de 150 KB por archivo de memoria, hand-off comprimido, QA por lotes y traza de corrida. Se lee siempre.
- **40-evals-del-harness** — como saber si un cambio a una instruction mejoro o empeoro al agente. Casos sacados
  de fallos reales, graders, `pass@k` vs `pass^k`. **Obligatoria antes de commitear un cambio a `32`, `27`, `39`,
  `30`, `33` o a cualquier `.agent.md`** — corriendo solo los casos del rol afectado.

## Como usar
- Las reglas globales definen marco comun de trabajo y formato de salida.
- Las reglas de capa definen limites tecnicos y responsabilidades.
- Los agentes y prompts deben referenciar explicitamente los modulos que priorizan, **y si los cargan completos o
  por indice** (seccion "Carga de contexto" de cada `.agent.md`).
- Las grandes (`25`, `27`, `32`, `34`, `35`, `37`) se leen por seccion, nunca enteras.
- **Tocar un archivo de esta carpeta cambia el comportamiento de un sistema en produccion.** Antes de commitear
  un cambio a una instruction grande o a un `.agent.md`, correr los evals del rol afectado (`40`): el catalogo
  que el agente no aplica es peor que uno chico que si, porque ocupa contexto y da falsa seguridad.

## Nota
Evitar reglas globales con applyTo demasiado amplio salvo que sea estrictamente necesario.
