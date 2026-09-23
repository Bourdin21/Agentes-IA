# Diseñador Funcional — contadores-bma-agentes-ia

Estado: **BORRADOR para revisión** — esquema de agentes diseñado 2026-09-23, sobre el relevamiento estructural de la
misma fecha. Análisis **no cerrado**: depende de la pregunta abierta 10 (modelo de entrega) y de las 8, 9 y 12
(servicios de ARCA, ARBA y SOS). Ver [1-analista-funcional.md](1-analista-funcional.md).

---

## 1. La idea en una frase

El estudio no compra agentes hechos: compra **un lineamiento**. Olvidata publica los agentes base y la documentación de
ARCA y ARBA; el estudio fija en reglas e instructivos **cómo se trabaja acá**; y cada persona, conversando con el
analista de automatizaciones, convierte su propio día a día en tareas que se hacen solas.

Lo que estandariza no es el agente: es **el instructivo**. El agente lo sigue igual lo pida quien lo pida.

## 2. Las tres ramas y su circuito

```
CONTABILIDAD ─┐
              ├─→ SOS Contador ──(importa de)──→ ARCA ──→ corroborar SOS vs ARCA  ← el dolor nuclear
IMPUESTOS ────┘

SUELDOS ──────→ ONVIO (Bejerman) ──(constata contra)──→ ARBA (convenio multilateral, locales)
```

Dos rutas separadas, sin traslado de datos entre ellas. Cada una tiene su sistema, su organismo de contraste y su
cadencia (mensual con picos de vencimiento).

## 3. El esquema de agentes

Cuatro grupos. Los tres primeros son **agentes base del rubro contable**, que publica Olvidata y de los que cada persona
deriva el suyo; el cuarto ya es de plataforma y existe hoy.

### 3.1. Contabilidad

| Agente | Para qué sirve | Qué entrega |
|---|---|---|
| **Conciliación bancaria** | Cruzar el extracto del banco con el mayor contable de SOS | Los movimientos que calzan, y **la cola de los que no**, con la diferencia explicada |
| **Balances y papeles de trabajo** | Revisar el balance antes de cerrarlo | Inconsistencias señaladas y la explicación redactada para el contador |

> La conciliación es la que tiene **material real ya cargado** en el proyecto: `archivos/conciliar movimientos extracto -
> sos contador/` (mayor de SOS en .xls + 5 extractos Credicoop en PDF). Es el mejor candidato a piloto: hay con qué
> probar el día uno.

### 3.2. Impuestos

| Agente | Para qué sirve | Qué entrega |
|---|---|---|
| **Control ARCA ↔ SOS** ⭐ | La tarea nuclear: comparar lo que ARCA tiene declarado contra lo que SOS importó | Las **diferencias**: duplicados en SOS, comprobantes que están en ARCA y faltan en SOS, montos que no coinciden |
| **IVA** | Preparar la liquidación mensual (F2002/F2051, Libro IVA Digital) | El borrador armado y **qué datos faltan** para poder presentarlo |
| **Ingresos Brutos / Convenio Multilateral** | CM03 mensual y CM05 anual, SIFERE | Ídem, con los coeficientes y jurisdicciones a revisar |
| **Vencimientos, retenciones y pagos** | El calendario del mes por cliente | Qué vence, qué falta, qué hay que pagar — antes de que sea tarde |

El **Control ARCA ↔ SOS** es el que ordena la prioridad de todo el proyecto: es la tarea más repetida, la más mecánica y
la que hoy se hace a ojo. Es también la que más gana con el conector de ARCA (§5).

### 3.3. Sueldos

| Agente | Para qué sirve | Qué entrega |
|---|---|---|
| **Control de liquidación** | Revisar la liquidación de ONVIO contra el mes anterior | Anomalías: altas y bajas, conceptos nuevos, variaciones fuera de lo normal |
| **Constatación ARBA** | Verificar convenio multilateral, locales y demás datos en ARBA | Qué coincide y qué no, por empleado y por local |

### 3.4. Transversales

| Agente | Para qué sirve |
|---|---|
| **Soporte de sistemas** | Contesta dudas de uso de SOS Contador, ONVIO, ARCA y ARBA, con la documentación de los cuatro cargada. Es el que saca al estudio de la dependencia del soporte técnico del proveedor |
| **Analista de automatizaciones** (ya existe, M15) | Conversa con cada persona, encuentra lo que repite y le deja propuesto el instructivo, la regla, la prueba, la tarea programada y el agente propio |

## 3 bis. Contraste con el rubro contable que YA existe en el producto (2026-09-23)

Antes de proponer agentes nuevos se revisó `nucleo/rubros/contable/` del producto. **El rubro ya está construido**: 10
agentes publicables, 8 etapas, capas, coordinador, y conocimiento de SOS Contador y Bejerman Onvio ya cargado. El
esquema de §3 no hay que construirlo de cero — hay que **completarlo**.

| Lo que necesita BMA (§3) | Qué hay hoy en el núcleo | Falta |
|---|---|---|
| Conciliación bancaria | `cont-registracion` — *"ordena y registra los comprobantes del período, **concilia bancos** y deja el período listo para liquidar"* | Nada nuevo: se usa y se ajusta con instructivos del estudio |
| Balances y papeles de trabajo | `cont-balance` | Nada nuevo |
| **Control ARCA ↔ SOS** ⭐ | **— no existe —** | **Agente nuevo.** Es el dolor nuclear y no hay nada que lo cubra |
| IVA | `cont-impuestos` (IVA y Ganancias) | Nada nuevo |
| IIBB / Convenio Multilateral | `cont-iibb` (incluye CM y retenciones/percepciones sufridas) | Nada nuevo |
| Vencimientos, retenciones y pagos | `cont-vencimientos` — *"pensado para correr solo, todos los meses"* | Nada nuevo |
| Control de liquidación de sueldos | `cont-sueldos` + `cont-cargas-sociales` (F.931, altas y bajas) | Nada nuevo |
| **Constatación ARBA** | **— no existe —** | **Agente nuevo.** `cont-iibb` liquida, no constata padrones |
| **Soporte de uso de los sistemas** | `cont-atencion` es para escribirle **al cliente**, no para el empleado | **Agente nuevo** (el conocimiento ya está cargado) |
| — | `cont-monotributo`, `cont-orquestador` | Ya existen y suman |

**Dos observaciones que cambian la estimación:**

1. **El trabajo real son 3 agentes, no 9.** Control ARCA↔SOS, constatación ARBA y soporte de sistemas. El resto ya está
   escrito y lo que BMA necesita encima es **su** instructivo y **sus** reglas — que es precisamente lo que cada usuario
   arma con el analista de automatizaciones, sin Olvidata en el medio.
2. **Hoy ningún agente del rubro tiene conectores.** Los diez usan solo documentos + conocimiento: trabajan sobre lo que
   la persona sube. Es coherente con la "Opción A" del Análisis, y confirma que el salto a conectores (ARCA, ARBA, SOS)
   es trabajo nuevo de Olvidata, no una configuración.

**Conocimiento que falta cargar:** ARCA y ARBA. Están `50-sos-contador.md` y `51-bejerman-onvio.md`, y
`40-calendario-alicuotas-escalas.md` existe pero **a propósito sin cifras** (escalas, topes, alícuotas y vencimientos no
se cargan porque un dato viejo dicho con seguridad es peor que no tenerlo). Para BMA eso hay que resolverlo: el estudio
necesita el calendario real, y mantenerlo actualizado es trabajo de Olvidata.

## 4. La regla que no se negocia

**Ningún cálculo impositivo, contable o de sueldos lo hace el modelo.** El agente compara, señala, redacta y explica;
la aritmética la hace código determinístico invocado como herramienta, o la hace el sistema de origen (SOS, ONVIO). Un
número alucinado en un estudio contable es el peor escenario posible, y es el único error que el cliente no perdona.

Y la de siempre, que ya es de plataforma: **nada se presenta, se paga ni se manda solo.** Los agentes preparan; el
envío y la presentación son de una persona.

Las dos van como **reglas de la empresa** cargadas el día uno, antes que cualquier agente.

## 5. De dónde saca los datos cada agente

Tres mecanismos, de menos a más automático. La arquitectura en capas del Análisis sigue valiendo: cambiar de mecanismo
no reescribe al agente.

| Mecanismo | Cómo llega el dato | Estado |
|---|---|---|
| **Archivo exportado** | La persona exporta de SOS/ONVIO y lo sube al espacio del cliente | Disponible hoy, sin depender de nadie |
| **Conector SOS Contador** | API oficial y pública del proveedor | Viable: SOS publica la API y la promueve. Falta confirmar que cubre los comprobantes importados (pregunta 12) |
| **Conector ARCA / ARBA** | Web services de los organismos | **A verificar** (preguntas 8 y 9). Es el que más cambia el proyecto: con la consulta a ARCA automatizada, la tarea nuclear pasa de "revisar a ojo" a "leer las diferencias" |

Todo conector entra por el **guardia de destinos** del producto: credenciales de la organización cifradas, lista blanca
de dominios por conexión, y aprobación humana salvo lo que el Director habilite.

## 6. La documentación cargada, y para qué sirve de verdad

Se carga como **base de conocimiento del rubro contable**: ARCA, ARBA, SOS Contador y ONVIO.

No es sólo para que el agente conteste dudas. Es lo que **acota el alcance de lo que cada usuario define**: cuando
alguien le pide al analista de automatizaciones algo que el organismo no permite, o que el sistema no expone, la
documentación es lo que permite decirlo en el momento — en vez de descubrirlo tres semanas después, con una
automatización a medio construir.

## 7. Quién hace qué

| | El estudio | Olvidata |
|---|---|---|
| **Relevar** qué automatizar | **Sí**, cada persona la suya, con el analista de automatizaciones | No |
| Escribir instructivos y reglas | Sí (el Director, lo que vale para todos) | Los propone el agente |
| Crear sus agentes y programaciones | Sí, cada uno los suyos | No |
| Agentes base del rubro | No | **Sí**, publicados en el núcleo |
| Documentación de ARCA/ARBA/SOS/ONVIO | No | **Sí**, cargada y actualizada |
| Conectores (ARCA, ARBA, SOS) | No | **Sí** |
| **Destrabar un problema técnico puntual** | Lo reporta | **Sí**: script, conector o agente base nuevo |

Olvidata es **soporte de segundo nivel**, no implementador de tareas. Entra cuando la configuración del usuario choca
con un límite técnico — un formato que no parsea, una consulta que necesita un conector que no existe — y deja la pieza
que lo resuelve. Nunca releva por el usuario.

## 8. Por dónde se arranca

| Paso | Qué | Por qué primero |
|---|---|---|
| 1 | Reglas del estudio + documentación de los cuatro sistemas | Sin esto, cada uno automatiza distinto y el lineamiento no existe |
| 2 | **Conciliación bancaria** como piloto, con una persona | Hay material real cargado y el resultado se ve en una vuelta |
| 3 | **Control ARCA ↔ SOS** sobre archivo exportado | Es la tarea nuclear; probarla a mano antes de conectar nada |
| 4 | Conector de ARCA, si las preguntas 8 y 12 dan verde | Es el salto de "revisar a ojo" a "leer las diferencias" |
| 5 | El resto de las ramas, cada persona con su analista | Ya con el lineamiento puesto y el circuito probado |

El orden no es por importancia: es por **cuánto se aprende por vuelta**. La conciliación enseña cómo trabaja el estudio
con poco riesgo; el control de ARCA es donde está el ahorro real.

## 9. Lo que falta definir antes de implementar

1. **Pregunta 10 del Análisis** — que el proyecto se entrega como configuración del producto. Es el gate.
2. **Preguntas 8, 9 y 12** — qué exponen ARCA, ARBA y SOS por servicio. Definen cuánto se automatiza de verdad.
3. **Pregunta 11** — cuántas personas por rama. Define licencias y volumen de relevamientos.
4. ~~Qué agentes base del rubro contable ya existen~~ **RESUELTO 2026-09-23** (ver §3 bis): existen 10, faltan 3
   (control ARCA↔SOS, constatación ARBA, soporte de sistemas) y falta el conocimiento de ARCA y ARBA.
5. **El calendario y las alícuotas reales.** El rubro los deja a propósito sin cargar; BMA los necesita. Definir quién
   los mantiene actualizados y con qué cadencia — es compromiso de Olvidata, no del estudio.
