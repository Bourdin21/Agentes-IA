---
description: Reglas globales de operacion para todo trabajo tecnico y funcional en BlankProject.
applyTo: "**/*.{md,prompt.md,agent.md,instructions.md}"
---

# Secuencia operativa obligatoria
Discovery/Relevamiento -> Analisis -> Diseno -> Arquitectura -> Presupuesto -> Implementacion -> Pruebas funcionales -> Documentacion de alcance (cliente) -> Cierre de calibracion estimado vs real

# Presupuesto de contexto (leer antes de cargar cualquier otra cosa)
- Todo agente respeta el techo de arranque y la carga por indice de `39-presupuesto-contexto.instructions.md`. Medido el 2026-09-25: el arranque literal del QA sobre un proyecto maduro eran ~510k tokens de historia antes de abrir el sistema, y eso degrada el razonamiento de la etapa entera.
- Los archivos grandes (`25`, `27`, `32`, `34`, `35`, `37`, los catalogos y las memorias de proyecto) se leen **por indice y por seccion**: `python scripts/contexto.py indice <alias>`. Las reglas no se relajan; lo que baja es cuanto se carga para llegar a ellas.
- La memoria de proyecto se lee por su bloque `## Definiciones vigentes` + el ultimo sprint. Lo cerrado vive en `definiciones/historial/` y se abre solo si el trabajo lo toca.

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
- Antes de implementar cualquier cambio de codigo — sin importar si el trabajo entra por el flujo formal de subagentes (orquestador -> implementador -> QA) o por una sesion de chat directa sobre un proyecto ya en produccion — consultar `.github/instructions/32-estandares-qa-implementador.instructions.md`. Ese archivo es la memoria incremental acumulativa de errores ya encontrados y corregidos en cualquier proyecto del estudio: evita repetir el mismo bug en un proyecto distinto. **Se consulta por indice** (`python scripts/contexto.py indice 32` o `grep -n '^## '`) leyendo solo las reglas de la familia de lo que se toca: son 45 reglas y 67 KB, y cargarlas todas en cada cambio es lo que hace que el agente despues no razone bien sobre el cambio en si.
- Despues de encontrar y corregir un bug funcional (propio o reportado por el cliente), evaluar si la causa raiz es generalizable a otros proyectos del baseline (no especifica de una sola entidad/pantalla de un solo proyecto):
  - Si es reproducible por pasos concretos (UI/API/datos) y generalizable: agregar un item nuevo a `docs/qa/regresiones-manuales.yml` (ver `30-qa-regresiones.instructions.md` para el formato) y una seccion nueva en `32-estandares-qa-implementador.instructions.md` resumiendo la regla preventiva.
  - Si es una regla preventiva generalizable pero sin una reproduccion UI/API formal (ej. un patron de diseño de datos, una desincronizacion de configuracion): agregar igual la seccion a `32-estandares-qa-implementador.instructions.md`, marcando explicitamente en "Origen" que no tiene item YAML asociado (mismo criterio ya usado en la regla PAT-003 de ese archivo).
  - Si es especifico de un solo proyecto (no reutilizable en otro): alcanza con documentarlo en `trazabilidad.md` y `definiciones/5-implementador.md`/`6-qa.md` de ese proyecto — no corresponde al catalogo cross-proyecto.
- Esta regla no depende de que la sesion haya invocado al subagente `agentes-ia-implementador`/`agentes-ia-qa` — cualquier agente (incluida una sesion de Claude Code trabajando directo sobre el repo de un proyecto) tiene la misma obligacion de leer antes y escribir despues.
- Si el proyecto integra (o va a integrar) facturacion electronica AFIP/ARCA, leer ademas `.github/instructions/34-integracion-afip-arca.instructions.md` ANTES de tocar codigo — circuito completo (WSAA, certificado, WSFEv1, Notas de Credito) depurado en vivo contra AFIP produccion real, evita repetir gotchas ya resueltos (carga de certificado, alta de Punto de Venta, orden de campos XML).
- Si el proyecto necesita (o va a refactorizar) una pantalla de control de stock/inventario, leer ademas `.github/instructions/35-pantalla-control-stock.instructions.md` ANTES de disenarla — patron de listado editable inline vs. formulario de ajuste (semantica reemplaza-vs-delta, guardado por fila vs. en lote, motivo opcional con generacion automatica, identificacion univoca de fila, riesgo de `RowVersion` generico contra procesos batch), ya resuelto en produccion.

# Trazabilidad documental obligatoria en /docs
- Toda referencia a rutas /docs corresponde a la ruta absoluta C:/Sistemas/Agentes-IA/docs. Siempre usar esa ruta completa al leer o escribir archivos de documentacion.
- Este repositorio (Agentes-IA) centraliza la memoria de trabajo de todos los proyectos.
- Cada proyecto tiene su carpeta propia en C:/Sistemas/Agentes-IA/docs/<proyecto>/.
- Cada agente tiene un unico archivo de memoria por proyecto en C:/Sistemas/Agentes-IA/docs/<proyecto>/definiciones/.
- Al trabajar sobre un proyecto, leer primero la version vigente del agente (el bloque `## Definiciones vigentes` + el ultimo sprint/CR, no el archivo entero) y luego editar ese mismo archivo.
- No crear archivos nuevos para el mismo agente y proyecto: siempre editar el existente.
- Ese archivo no pasa de 150 KB: al cerrar la etapa, los sprints/CR/modulos ya cerrados se archivan con `python scripts/archivar_memoria.py <archivo> --aplicar`, que los mueve a `definiciones/historial/` y deja un puntero de una linea por grupo.
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

# Brevedad en el chat (regla general de Joaquin, 2026-09-17)
Aplica a **todos los agentes y todas las conversaciones**, por encima de cualquier formato de salida.
- Responder **lo mas resumido posible**: por defecto 2 a 5 lineas.
- Al volver de un subagente o de una tarea larga: **que quedo, si paso o fallo, y que decision hace falta**. Nada mas.
- Sin tablas, sin encabezados de seccion y sin resumenes de arquitectura en el chat, salvo pedido expreso.
- Un hallazgo importante va en **una linea**, no en una seccion.
- El detalle vive en `/docs`, en las definiciones por rol y en los mensajes de commit: **no se repite en el chat**.
- Motivo: un informe largo no se lee, asi que lo importante se pierde adentro.
- **No aplica** a lo que Joaquin pida explicitamente (manuales, especificaciones, documentos de cliente, artifacts) ni a lo que se escribe en archivos.

# Formato minimo de respuestas tecnicas
Este formato es el contrato de salida del orquestador hacia el cliente **en los documentos de `/docs`, no en el chat**. Cada agente entrega su Salida minima propia (definida en su .agent.md), y el orquestador consolida estos puntos:
1. Alcance funcional resumido.
2. Impacto tecnico por capa.
3. Riesgos y supuestos.
4. Pruebas funcionales minimas requeridas.
5. Checklist de salida para merge.
6. Cierre de calibracion estimado vs real.
