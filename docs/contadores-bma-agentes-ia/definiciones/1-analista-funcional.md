# Analista Funcional — contadores-bma-agentes-ia

Estado: EN CURSO — Discovery iniciado 2026-08-30

---

## Contexto

Cliente: Contadores BMA (estudio contable). Ya es cliente de Olvidata Soft — ver proyecto previo `contadores-bma-conversor` (conversor Excel Bejerman Web/Onvio → planilla cliente, entregado 2026-06-25, en producción desde entonces).

## Alcance funcional propuesto (hipótesis inicial, a validar con el cliente)

El estudio quiere instalar una plataforma de agentes IA para automatizar tareas operativas diarias del estudio: impuestos, conciliaciones bancarias, balances, sueldos, y asistencia con manuales de uso de Bejerman Onvio (para no depender de soporte técnico). Objetivo final del cliente: agentes de punta a punta que avisen solo ante excepciones, con arranque gradual — modo asistido/supervisado por tarea antes de pasar a autónomo.

Mecanismo de "entrenamiento": cada empleado documenta paso a paso la tarea que quiere automatizar, y eso configura al agente correspondiente; el empleado puede seguir corrigiendo/entrenando al agente después.

Arquitectura propuesta (research inicial, ver Google Doc en metadata.md): servidor central del estudio como orquestador (Claude Agent SDK) + agente liviano en la PC de cada empleado, que es quien interactúa con Bejerman Onvio.

**Alcance refinado por el usuario (2026-08-31)** — acota la hipótesis inicial a algo más concreto: Bejerman Web sigue siendo la herramienta principal que usa el empleado, no se reemplaza ni se automatiza "por dentro". El sistema se construye alrededor de tres piezas:
1. Un bot que responde las consultas/dudas de uso de **Bejerman Web/Onvio y de SOS Contador** — segunda herramienta muy usada por el estudio, agregada por el usuario el 2026-08-31 (ver sección "SOS Contador" más abajo) — con la documentación de ambas cargada (100% agente, ver mapa de la sección "Stack: agente vs. script determinístico").
2. Scripts para las conversiones de archivos que hoy se hacen a mano (capa de adaptadores, script determinístico — mismo patrón que `contadores-bma-conversor`), incluyendo el traslado de datos entre Bejerman Web y SOS Contador si el relevamiento confirma que hoy se hace a mano.
3. Automatización de los procesos que el estudio ya tiene definidos y siguen siempre los mismos pasos.

Esto es compatible 100% con la Opción A y con el plan de acción de 5 fases ya definido — no cambia la arquitectura en capas, la acota a un alcance más manejable para la Fase 0-1.

## Research de integración con Bejerman Onvio (hallazgos, pendientes de confirmar con el cliente/proveedor)

- **CONFIRMADO (2026-08-30, cruzado con `contadores-bma-conversor/documento-funcional.md` §1.1):** Contadores BMA usa **Bejerman Web + Onvio**, que es 100% SaaS en la nube de Thomson Reuters — sin instalación, sin base de datos local, solo navegador. Esto es distinto de la línea **Bejerman ERP/Premium** (esa sí es on-premise con SQL Server) que se había asumido en el research inicial. **No hay una base de datos de Bejerman en la red del estudio a la que conectarse por VPN** para este cliente — corrige la Opción B original.
- No se encontró API pública documentada para la suite Bejerman Web/Onvio Argentina. Existe una Onvio BR Accounting API pública (Brasil/Domínio Contábil) con OAuth2, pero es un producto distinto — no aplica directamente.
- **BLOQUEO CONTRACTUAL (2026-08-30):** los "Onvio Full Terms" de Thomson Reuters (`tax.thomsonreuters.com/en/full-terms/onvio`, sección "Unauthorized Technology") prohíben explícitamente, salvo autorización previa de Thomson Reuters: (i) instalar o correr software/hardware sobre sus productos/servicios/red; (ii) usar tecnología para descargar/minar/scrapear/indexar sus datos automáticamente; (iii) conectar automáticamente (por API o cualquier otro medio) sus datos con otro software/servicio/red. Esto cubre tanto la automatización de interfaz (computer-use) como cualquier integración de datos automatizada — no es un tema de madurez/riesgo del agente, es una prohibición contractual directa. No se confirmó el texto exacto de la versión argentina del contrato (las URLs de Onvio AR redirigen a selección de región) — se asume cláusula equivalente hasta confirmar contra el contrato real firmado por Contadores BMA.
- 2FA obligatorio en Onvio (Thomson Reuters Authenticator/Auth0 Guardian — push, TOTP, SMS o hardware key) + reCAPTCHA en login + timeout de sesión de 30 min de inactividad — fricciones técnicas adicionales para cualquier automatización de login, independientes del bloqueo contractual.
- Camino que sigue abierto sin necesitar autorización: automatizar lo que pasa **después** de que el empleado exporta un archivo a mano desde Bejerman Web (acción humana, no acceso automatizado al sistema de Thomson Reuters) — es lo que ya hace `contadores-bma-conversor` en producción.

## SOS Contador — research, complementariedad con Bejerman Web y puntos de dolor (agregado 2026-08-31)

### Qué es y qué hace

SOS Contador (`sos-contador.com`) es una suite contable-impositiva 100% en la nube, dirigida a estudios contables y profesionales independientes en Argentina. Módulos principales, por lo relevado en su base de ayuda pública:
- **Impositivo/ARCA**: liquidación de IVA (F2002/F2051), Libro IVA Digital, Ingresos Brutos Convenio Multilateral (CM03 mensual, CM05 anual), SIFERE, proyección de Ganancias, ajuste por inflación contable e impositivo.
- **Contabilidad**: generación automática de asientos y libro diario a partir de compras/ventas cargadas, estados contables, Sumas y Saldos, amortización de Bienes de Uso.
- **Gestión**: ventas, compras, cuenta corriente, cheques, clientes, proveedores, stock, cobros/pagos.
- **Sueldos v2**: liquidación de remuneraciones — módulo propio, superpuesto en función con el de Bejerman (ver pregunta abierta 7 más abajo).
- **Monotributo**, **Agro**, multimoneda, importación automática diaria de comprobantes desde AFIP/ARCA ("Mis Comprobantes").
- Integraciones ya existentes mencionadas por el proveedor: Mercado Libre, Mercado Pago, Tienda Nube, ARBA, LUA (no confirmado el alcance exacto de cada una).

### Documentación disponible para cargar en el bot

- Base de ayuda estructurada por módulo: `ayuda.sos-contador.com.ar` (organizada en menús — Inicio, Asistentes ARCA, Monotributo, Gestión, Contabilidad, Sueldos v2, Automatizaciones, Agro, Más funcionalidades — con secciones propias de Importar/Exportar datos y API).
- Blog con tutoriales (`sos-contador.com/blog`) y canal de YouTube con +30 videos tutoriales.

### Hallazgo clave — contraste directo con Bejerman/Onvio

**A diferencia de Bejerman/Onvio (bloqueado contractualmente sin autorización previa de Thomson Reuters), SOS Contador publica y ofrece activamente una API para integraciones de terceros**: documentación técnica pública vía Postman (`documenter.getpostman.com/view/1566360/SWTD6vnC`), pensada explícitamente para que estudios contables integren SOS con sus propias plataformas — hay un precedente citado por el propio proveedor (software "Mi Estudio Digital" integrado vía esta API para manejo de cartera de clientes) y hasta un grupo de WhatsApp de desarrolladores que la usan. Esto **reabre la puerta a integración automatizada real (equivalente a Opción B) para la porción del flujo que pasa por SOS Contador**, aunque Bejerman siga limitado a Opción A. En la arquitectura en capas ya definida, esto se traduce en un adaptador adicional ("API SOS Contador") en paralelo al adaptador de archivos exportados de Bejerman — ambos alimentando el mismo modelo canónico, sin tocar reglas de negocio ni orquestación.

*Nota de honestidad*: no se profundizó en el contenido técnico de la colección de Postman (alcance de endpoints, autenticación, límites) — es trabajo de la etapa de Arquitectura, no de Análisis. Tampoco se confirmó una referencia encontrada en el research sobre una posible suspensión de la integración AFIP/ARCA de SOS por una resolución "ARCA 74/2022" — es un dato de una sola fuente indirecta, no verificado, y no se lo debe dar por cierto sin confirmarlo directo con SOS Contador o con el estudio.

### Hipótesis de complementariedad con Bejerman Web — a validar con el cliente

**Variante A**: Bejerman Web es la herramienta de gestión/facturación/sueldos "puertas para adentro" de cada cliente que atiende el estudio (ya confirmado por `contadores-bma-conversor`: ahí se genera la liquidación de sueldos), y SOS Contador es la herramienta que el estudio usa específicamente para las presentaciones impositivas (IVA, IIBB, Ganancias) y los libros contables de esos mismos clientes — el flujo típico sería trasladar datos generados en Bejerman hacia SOS Contador para liquidar y presentar impuestos.

**Variante B**: ambos sistemas se usan en paralelo para distintos clientes/carteras del estudio (algunos clientes en Bejerman, otros en SOS Contador), sin traslado de datos entre uno y otro — cada sistema es autocontenido para el cliente que le corresponde.

La Variante A es la que generaría el mayor punto de dolor automatizable (carga manual repetida de los mismos datos en dos sistemas); la Variante B no tendría ese punto de dolor pero sí duplicaría el trabajo de construir el bot de consultas y los scripts para dos ecosistemas de documentación distintos sin sinergia entre ellos. Se agregó como pregunta abierta 6-7 (ver abajo) — debe confirmarse en la reunión de discovery o el cuestionario individual antes de diseñar el adaptador de SOS Contador.

### Puntos de dolor identificados que Olvidata podría atacar

1. **Traslado manual de datos entre Bejerman Web y SOS Contador** (si se confirma la Variante A) — automatizable con script de parseo del export de Bejerman + la API oficial de SOS Contador para la carga, sin depender de ninguna autorización especial (a diferencia de lo que pasaría del lado Bejerman).
2. **Doble carga de sueldos** — ambos sistemas tienen módulo de liquidación de sueldos; si el estudio usa los dos para esto, hay una duplicación de trabajo evidente a resolver primero (definir cuál es la fuente de verdad).
3. **Presentaciones impositivas repetitivas** (IVA, IIBB CM03/CM05) armadas hoy revisando datos de Bejerman y cargando a mano en SOS — automatizable vía la API de SOS Contador, en la capa de adaptadores.
4. **Bot de consultas combinado**: la base de ayuda de SOS Contador está bien estructurada por módulo (a diferencia de la documentación de Bejerman/Onvio, más dispersa) — buen candidato a cargar primero en el bot de soporte, junto con los manuales de Bejerman ya contemplados.

## Preguntas abiertas — bloquean el cierre de Discovery/Análisis

1. ~~¿Qué línea de Bejerman tiene instalada Contadores BMA?~~ **RESUELTA 2026-08-30**: Bejerman Web (cloud), no Premium/ERP on-premise.
2. **¿Existe algún canal de integración autorizada de Thomson Reuters para Bejerman Web/Onvio Argentina** (equivalente a la Onvio BR Accounting API que sí existe para Brasil)? Preguntar directamente al ejecutivo de cuenta de Contadores BMA — la cláusula de "Unauthorized Technology" habilita autorización previa de Thomson Reuters, lo que sugiere que el canal para pedirla existe.
3. Confirmar el texto exacto de la cláusula de uso/automatización en el contrato argentino real firmado por Contadores BMA (no solo los "Onvio Full Terms" globales usados como proxy).
4. Catálogo real de tareas a automatizar: relevar con el equipo del estudio (no solo con el owner) cuáles son las tareas manuales más repetitivas y de mayor volumen hoy, priorizando las que dependen de archivos que el empleado ya exporta (compatible con Opción A sin pedir autorización).
5. Cantidad de empleados/puestos de trabajo reales que usarían el sistema.
6. **¿Cómo se complementan Bejerman Web y SOS Contador en el flujo real del estudio?** Dos variantes a confirmar (ver sección "SOS Contador" arriba, marcadas como **hipótesis a validar**): (A) Bejerman genera los datos de gestión/sueldos y el estudio los traslada a mano hacia SOS Contador para liquidar y presentar impuestos — ej. "cargo las ventas del mes en Bejerman, después las vuelvo a tipear/importar en SOS para armar el IVA"; o (B) cada sistema es autocontenido para una cartera de clientes distinta, sin traslado de datos entre uno y otro — ej. "los clientes con Bejerman quedan en Bejerman, los que están en SOS quedan en SOS, no se mezclan". La respuesta define si corresponde construir el adaptador de traslado Bejerman→SOS como parte de la Fase 0-1.
7. **¿El estudio usa el módulo de Sueldos de Bejerman, el de SOS Contador (Sueldos v2), o ambos para el mismo cliente?** Ej. variante 1: "todo sueldo se liquida en Bejerman, SOS Contador no se usa para esto" (sin duplicación); variante 2: "liquidamos en Bejerman y después cargamos de nuevo en SOS para que quede en la contabilidad" (duplicación de carga, candidato directo a automatizar).

## Opciones de integración (stack + infraestructura) — para llevar a la reunión de discovery

Tres paquetes, de menor a mayor autonomía/riesgo. Las tres comparten la arquitectura base (servidor central orquestador + agente liviano por PC); lo que cambia es cómo llega el agente a los datos de Bejerman Onvio.

> **Actualizado 2026-08-30 tras confirmar que Contadores BMA usa Bejerman Web (cloud, sin SQL Server local) y tras encontrar el bloqueo contractual de Thomson Reuters — ver sección de research arriba.** Se mantienen las 3 opciones mapeadas pero con su estado real corregido.

**Opción A — Solo archivos exportados (mínimo riesgo) — ÚNICA VIABLE HOY SIN AUTORIZACIÓN DE THOMSON REUTERS**
- Integración: el agente nunca toca Bejerman/Onvio directamente. El empleado exporta a mano (acción humana, no un acceso automatizado al sistema de TR) y el agente procesa ese archivo después — mismo patrón que `contadores-bma-conversor`, extendido a más tareas.
- Infraestructura: 100% en la nube (VPS chico o hosting compartido tipo Ferozo), sin tocar la red del estudio ni el VPN.
- Stack: Claude Agent SDK (Node/TS) como servicio web; sin agente local instalado.
- Contras: el empleado sigue exportando a mano, no sirve para tareas que requieren escribir en Bejerman/Onvio. Se queda en agentes asistentes, no autónomos de punta a punta.
- Es el único camino que no depende de ningún permiso adicional de Thomson Reuters.

**Opción B — Acceso automatizado a datos (vía SQL local o vía integración a Bejerman Web/Onvio) — BLOQUEADA hasta autorización de Thomson Reuters**
- Ya no aplica como "SQL Server local vía VPN": Contadores BMA usa Bejerman Web (cloud), no hay base local a la que conectarse.
- Cualquier variante de acceso automatizado a los datos de Bejerman Web/Onvio (API no documentada, integración directa, etc.) cae bajo la cláusula de "Unauthorized Technology" de los términos de Onvio — requiere autorización previa explícita de Thomson Reuters (pregunta abierta 2).
- Si Thomson Reuters confirma un canal de integración autorizado (como existe para Onvio Brasil), esta opción se rediseña sobre esa API oficial en vez de sobre un acceso SQL directo.

**Opción C — Punta a punta con automatización de interfaz (computer-use) — BLOQUEADA contractualmente, no solo por riesgo/madurez**
- Un agente local controlando la interfaz web de Onvio (login, clicks, carga de datos) es técnicamente viable (es una app web, más automatizable que un desktop legacy) pero cae de lleno en la prohibición de "Unauthorized Technology" de los Términos de Onvio — no es un tema de madurez del agente, es un incumplimiento contractual que puede derivar en suspensión de la cuenta.
- Fricciones técnicas adicionales incluso si se autorizara: 2FA obligatorio (push/TOTP/SMS/hardware key), reCAPTCHA en login, timeout de sesión de 30 min.
- Solo queda habilitada si Thomson Reuters la autoriza explícitamente.

**Recomendación actualizada**: diseñar y presupuestar la Fase 1 completa sobre la Opción A (sin dependencias de autorización de terceros), en paralelo a que Contadores BMA le pregunte a su ejecutivo de cuenta de Thomson Reuters si existe un canal de integración autorizada. Si la respuesta es positiva, B y C se rediseñan sobre esa vía oficial — nunca sobre acceso no autorizado.

## Arquitectura en capas propuesta — insumo para Diseño/Arquitectura (Análisis aún no cerrado)

Pregunta del usuario: si se implementa la Opción A con arquitectura en capas, y sobre esa base se desarrollan las reglas de los agentes, ¿se puede migrar a futuro a B/C sin perder la infraestructura construida? Respuesta: sí, siempre que se construya como puertos y adaptadores (hexagonal), no como una implementación ad-hoc.

**Capas:**
1. **Orquestación** (Claude Agent SDK, chat web, memoria/entrenamiento, auditoría) — independiente del mecanismo de integración, no cambia entre A/B/C.
2. **Reglas de negocio / agentes** — escritas en términos de un **modelo de datos canónico** (movimientos bancarios, asientos, liquidaciones de sueldo, comprobantes) y de *tools de intención* ("obtener_movimientos_banco", "obtener_liquidacion_sueldos"), nunca en términos del mecanismo concreto ("leer_excel_grilla", "query_sql"). Es lo que el empleado "entrena" con su documento paso a paso.
3. **Adaptadores** — única capa que cambia según A/B/C: en A parsea el archivo exportado (reutiliza el mapeo de `contadores-bma-conversor`) y lo transforma al modelo canónico; en B reemplaza el parseo por la API/base que Thomson Reuters autorice, entregando el mismo modelo canónico; en C opera la interfaz (computer-use) traduciendo hacia/desde ese mismo modelo.

Si el contrato de salida del adaptador no cambia, agregar o reemplazar uno no obliga a tocar reglas de negocio ni orquestación.

**Matiz**: la migración es limpia para tareas de **lectura** (conciliaciones, balances, reportes) — en A ya hay algo que migrar. Para tareas de **escritura** (cargar un asiento, presentar una DDJJ) no existe hoy una "versión A" real — en A eso lo sigue haciendo el empleado a mano. Cuando C se habilite, esas reglas se escriben de cero, pero nacen conectadas al mismo modelo canónico y al mismo agente constructor — no hay arquitectura que reescribir, solo reglas nuevas que agregar.

## Plan de acción — proceso progresivo de integración

| Fase | Objetivo | Gate de salida |
|---|---|---|
| Fase 0 — Fundación | Definir modelo canónico + tools de intención; construir adaptador A (reutilizando mapeo de `contadores-bma-conversor`); levantar orquestación + auditoría; 1 agente piloto end-to-end sobre archivos exportados. En paralelo: consulta formal a Thomson Reuters sobre canal de integración autorizado (no bloquea esta fase). | Agente piloto validado por al menos un empleado real, con feedback incorporado. |
| Fase 1 — Expansión sobre A | Sumar 2-4 agentes más del catálogo priorizado, todos sobre el adaptador A. Formalizar el proceso de entrenamiento (documento del empleado → agente constructor → modo supervisado → feedback). Panel de auditoría básico. | 4-5 agentes en modo supervisado real; los de menor riesgo empiezan a graduarse a "avisa después". |
| Fase 2 — Adaptador B (condicional a autorización de TR) | Si Thomson Reuters confirma canal autorizado: construir adaptador B que alimenta el mismo modelo canónico. Agentes de Fase 0-1 no se reescriben. Si TR no autoriza: el estudio sigue operando estable en A, sin bloqueo. | Agentes de lectura graduados a autónomos de punta a punta para el tramo de lectura. |
| Fase 3 — Adaptador C (condicional a autorización de TR para escritura) | Construir adaptador de escritura (computer-use u otro mecanismo autorizado). Arranca con aprobación humana obligatoria por tarea. | Cada tarea se gradúa individualmente a autónomo con reporte posterior, según track record — nunca en bloque. |
| Fase 4 — Todo el estudio, punta a punta | Rollout a todos los empleados/roles. Revisión periódica de costo de tokens vs. ahorro real. | Objetivo final del cliente: agentes autónomos con aviso solo ante excepciones. |

Las Fases 2 y 3 quedan condicionadas a la respuesta de Thomson Reuters. Si nunca llega autorización, el sistema no queda a mitad de camino: la arquitectura en capas hace que B y C sean una mejora incremental sobre un producto ya completo en Fase 1, no una migración obligatoria.

## Stack: agente vs. script determinístico, por tarea

Pregunta del usuario: ¿hay un mejor stack que "un grupo de agentes" para este proyecto? Respuesta: sí — el mejor stack no es "agentes para todo", es un **híbrido**. Código determinístico tradicional (scripts/ETL, la capa de adaptadores ya definida) para todo lo que sea reglas fijas y estables, y agentes LLM reservados para lo que requiere lenguaje natural o juicio.

**Regla transversal, no negociable**: todo cálculo numérico, impositivo o legal (alícuotas, retenciones, fórmulas de sueldo, totales de balance) va siempre en código determinístico — nunca "calculado" por el LLM dentro del agente. El agente invoca ese cálculo como tool y explica el resultado, pero no hace la aritmética él mismo. Un número mal calculado por alucinación es el peor escenario posible en un estudio contable.

| Tarea | Script determinístico | Agente | Nota |
|---|---|---|---|
| Conciliación bancaria | Parseo/normalización de archivos + matching automático por monto/fecha/número de operación | Resolver y explicar diferencias que no calzan solas; aprender patrones que el empleado corrige | El grueso del volumen se resuelve con reglas; el agente entra solo en la cola de excepciones |
| Manuales / soporte Bejerman Onvio y SOS Contador | — | 100% agente (manuales + base de ayuda de ambas herramientas como contexto/RAG) | Es una tarea de lenguaje natural por definición |
| Traslado de datos Bejerman → SOS Contador (si se confirma pregunta abierta 6) | Parseo del export de Bejerman + carga vía API oficial de SOS Contador | Resolver casos que no matchean automáticamente entre ambos sistemas | Único adaptador candidato a nivel "Opción B" desde el arranque, porque SOS sí tiene API autorizada — no depende de Thomson Reuters |
| Carga de comprobantes/facturas | Extracción de campos si el formato es estructurado y estable | Extracción de entradas no estructuradas (PDF/foto variable) + clasificación de cuenta contable | Evaluar primero si conviene apoyarse en la IA que ya trae Bejerman antes de reconstruirlo |
| Balances / papeles de trabajo | Totales, ratios, cruces período a período | Señalar inconsistencias que no siguen una regla fija; redactar la explicación para el contador | El cálculo nunca sale del agente, solo la narrativa |
| Liquidación de impuestos (IVA, Ganancias) | El cálculo impositivo en sí | Armar el borrador explicativo, detectar datos faltantes, interpretar casos particulares | Máximo riesgo si se invierte el rol |
| Sueldos / RRHH | Cálculo de la liquidación (conceptos, aportes, contribuciones) | Detectar anomalías vs. mes anterior; responder preguntas del empleado | Mismo criterio que impuestos |

En la arquitectura en capas de la sección anterior, los scripts determinísticos viven en la capa de **adaptadores** (y en funciones de negocio fijas invocadas como tools), y el agente vive en la capa de **reglas/juicio**, consumiendo esas tools en vez de reimplementar la lógica.

## Próximo paso

Reunión de discovery con Contadores BMA para responder las preguntas abiertas antes de cerrar Análisis y pasar a Diseño.
