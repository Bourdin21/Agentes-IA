---
description: Reglas globales de operacion para todo trabajo tecnico y funcional en BlankProject.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Secuencia operativa obligatoria
Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

# Reglas obligatorias
- No colocar logica de negocio compleja en Controllers.
- Los Controllers solo coordinan request/response y delegan en Services.
- La logica de negocio vive en Services.
- El acceso a datos vive en DbContext, repositorios o infraestructura.
- Toda modificacion debe indicar que capas afecta y por que.
- Si un cambio requiere migracion EF, debe indicarse explicitamente.
- Si un cambio afecta permisos, estados o validaciones, debe listarse.
- No hacer refactors cosmeticos salvo pedido expreso.
- Preservar comportamiento legacy salvo indicacion contraria.
- Las pruebas requeridas son funcionales.
- **El agente Implementador nunca ejecuta smoke test funcional** (no levanta la app, no prueba flujos por navegador ni por API/curl, no simula requests reales). Su evidencia de cierre es build limpio + revision de codigo propia. Separacion de roles deliberada: quien escribe el codigo no es quien lo verifica (evita el sesgo de confirmacion de "lo escribi yo, seguro funciona").
- **El agente QA (2026-08-14, cambio de politica) SI ejecuta verificacion automatizada por navegador** para los casos objetivamente chequeables (catalogo de regresiones + patrones de `32-estandares-qa-implementador.instructions.md` + criterios de aceptacion criticos) — ver `33-verificacion-automatizada-qa.instructions.md` para el detalle de que se automatiza y que sigue siendo manual. La verificacion exploratoria/subjetiva (UX, casos que requieren credenciales de produccion reales, juicio de negocio) sigue siendo responsabilidad manual del usuario/cliente.
- La documentacion requerida es de alcance para el cliente.
- El cierre de calibracion estimado vs real es obligatorio para mejorar la asertividad del presupuesto.

# Memoria acumulativa de errores cross-proyecto (obligatoria, cualquier modo de trabajo)
- Antes de implementar cualquier cambio de codigo — sin importar si el trabajo entra por el flujo formal de subagentes (orquestador -> implementador -> QA) o por una sesion de chat directa sobre un proyecto ya en produccion — consultar `.github/instructions/32-estandares-qa-implementador.instructions.md`. Ese archivo es la memoria incremental acumulativa de errores ya encontrados y corregidos en cualquier proyecto del estudio: evita repetir el mismo bug en un proyecto distinto.
- Despues de encontrar y corregir un bug funcional (propio o reportado por el cliente), evaluar si la causa raiz es generalizable a otros proyectos del baseline (no especifica de una sola entidad/pantalla de un solo proyecto):
  - Si es reproducible por pasos concretos (UI/API/datos) y generalizable: agregar un item nuevo a `docs/qa/regresiones-manuales.yml` (ver `30-qa-regresiones.instructions.md` para el formato) y una seccion nueva en `32-estandares-qa-implementador.instructions.md` resumiendo la regla preventiva.
  - Si es una regla preventiva generalizable pero sin una reproduccion UI/API formal (ej. un patron de diseño de datos, una desincronizacion de configuracion): agregar igual la seccion a `32-estandares-qa-implementador.instructions.md`, marcando explicitamente en "Origen" que no tiene item YAML asociado (mismo criterio ya usado en la regla PAT-003 de ese archivo).
  - Si es especifico de un solo proyecto (no reutilizable en otro): alcanza con documentarlo en `trazabilidad.md` y `definiciones/5-implementador.md`/`6-qa.md` de ese proyecto — no corresponde al catalogo cross-proyecto.
- Esta regla no depende de que la sesion haya invocado al subagente `agentes-ia-implementador`/`agentes-ia-qa` — cualquier agente (incluida una sesion de Claude Code trabajando directo sobre el repo de un proyecto) tiene la misma obligacion de leer antes y escribir despues.

# Trazabilidad documental obligatoria en /docs
- Toda referencia a rutas /docs corresponde a la ruta absoluta C:/Sistemas/Agentes-IA/docs. Siempre usar esa ruta completa al leer o escribir archivos de documentacion.
- Este repositorio (Agentes-IA) centraliza la memoria de trabajo de todos los proyectos.
- Cada proyecto tiene su carpeta propia en C:/Sistemas/Agentes-IA/docs/<proyecto>/.
- Cada agente tiene un unico archivo de memoria por proyecto en C:/Sistemas/Agentes-IA/docs/<proyecto>/definiciones/.
- Al trabajar sobre un proyecto, leer primero la version vigente del agente y luego editar ese mismo archivo.
- No crear archivos nuevos para el mismo agente y proyecto: siempre editar el existente.
- Editar significa actualizar la seccion de definiciones vigentes IN-PLACE (reemplazar el dato viejo, no dejarlo al lado con una nota de correccion) — nunca agregar una seccion nueva fechada por cada ronda de trabajo sobre el mismo tema. El unico lugar que crece por append es `## Historial de ajustes`, y ahi solo una linea corta por cambio. Ver `29-trazabilidad-conversacion.instructions.md` para el detalle completo de esta regla.
- Cada ajuste relevante debe registrarse en C:/Sistemas/Agentes-IA/docs/<proyecto>/trazabilidad.md.
- El indice consolidado de proyectos vive en C:/Sistemas/Agentes-IA/docs/indice.md.

# Definicion minima por etapa
- Discovery/Relevamiento: alcance inicial, supuestos, exclusiones y dependencias.
- Analisis: problema de negocio, casos de uso y criterios de aceptacion.
- Diseno: propuesta funcional de flujo, datos y validaciones.
- Arquitectura: impacto por capa, riesgos tecnicos y necesidad de migraciones EF.
- Presupuesto: WBS funcional, O/M/P por item, riesgo, contingencia y rango final.
- Implementacion: cambios por capa segun fronteras definidas.
- Pruebas funcionales: validacion de flujos y reglas de negocio con evidencia.
- Documentacion de alcance (cliente): incluido/no incluido, supuestos y condiciones.
- Cierre de calibracion estimado vs real: desvio por item y acciones de recalibracion.

# Modo de trabajo recomendado
- Ask mode: Discovery/Relevamiento, Analisis, Diseno, Arquitectura y Presupuesto.
- Agent mode: Implementacion, pruebas funcionales, correccion de build, documentacion de alcance y cierre de calibracion.

# Gates de aprobacion entre etapas
- Cada etapa debe cerrar su archivo en C:/Sistemas/Agentes-IA/docs/<proyecto>/definiciones/ antes de pasar a la siguiente.
- No iniciar Diseno sin Analisis aprobado.
- No iniciar Arquitectura sin Diseno aprobado.
- No iniciar Presupuesto sin Arquitectura aprobada.
- No iniciar Implementacion sin Presupuesto aprobado por el cliente.
- No iniciar Documentacion al cliente sin QA aprobado.
- El Cierre de calibracion lo ejecuta el agente 4 al finalizar el sprint.

# Formato minimo de respuestas tecnicas
Este formato es el contrato de salida del orquestador hacia el cliente. Cada agente entrega su Salida minima propia (definida en su .agent.md), y el orquestador consolida estos puntos:
1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales minimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.
