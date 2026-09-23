# Arquitecto — contadores-bma-agentes-ia

Estado: **BORRADOR para revisión** — 2026-09-23, actualizado el mismo día con el research de ARCA, ARBA y SOS. Se apoya
en [1-analista-funcional.md](1-analista-funcional.md) (relevamiento estructural),
[2-disenador-funcional.md](2-disenador-funcional.md) (esquema de agentes y §3 bis, el contraste contra lo que ya existe)
y [research-arca-arba-sos-2026-09.md](../research-arca-arba-sos-2026-09.md).

**A3 resuelto y aplicado. Preguntas 8, 9 y 12 cerradas.** La 8 **en contra de lo esperado** (el conector de ARCA no
existe) y la **12 a favor**: la API de SOS sí lista los comprobantes recibidos, así que el cruce necesita un solo
archivo. Queda por verificar solo Convenio Multilateral por COMARB (riesgo A7).

---

## 1. La decisión de arquitectura

**No hay repositorio nuevo.** Contadores BMA es una **organización (tenant)** del producto
`olvidata-agentes-multirubro` (`C:\Sistemas\Olvidata Agentes Multi-rubro`), con licencia del rubro `contable`. Todo lo
que se construye vive en ese repo, en el núcleo, y **sirve para cualquier estudio contable** — no solo para BMA.

Eso mantiene la regla rectora del producto: *rubros son datos, no código*. No se crean controllers ni entidades para
BMA. Lo específico de BMA vive en **su** organización: sus reglas, sus instructivos, sus agentes derivados y sus
programaciones, que carga el propio estudio.

El proyecto `contadores-bma-conversor` (conversor de sueldos Bejerman→plantilla, en producción) **queda como está**. No
se migra ni se absorbe: resuelve una conversión puntual y sigue sirviendo.

## 2. Lo que se construye, capa por capa

### 2.1. Núcleo — rubro `contable` (lo único que es desarrollo)

| Pieza | Qué es | Por qué |
|---|---|---|
| **Agente `cont-control-arca`** | Compara lo declarado en ARCA contra lo importado en SOS y devuelve **las diferencias** (duplicados, faltantes, montos que no coinciden) | Es el dolor nuclear y no hay nada que lo cubra |
| **Agente `cont-arba`** | Constata convenio multilateral, locales y demás padrones en ARBA | `cont-iibb` liquida, no constata |
| **Agente `cont-soporte-sistemas`** | Contesta dudas de uso de SOS, Onvio, ARCA y ARBA | El conocimiento ya está cargado; falta el agente que lo use para el **empleado** (no para el cliente, que es `cont-atencion`) |
| **Conocimiento `60-arca.md` y `61-arba.md`** | Qué se puede consultar, con qué habilitación, qué significa cada dato | Es lo que **acota el alcance** de lo que cada usuario define (pedido explícito del relevamiento) |
| **`40-calendario-alicuotas-escalas.md`** | Hoy existe **a propósito sin cifras** | Decisión pendiente: BMA necesita el calendario real. Ver §5 |

Los otros 10 agentes del rubro **no se tocan**: se usan como están y BMA les suma sus instructivos.

> **A3 — HECHO el 2026-09-23.** El manifiesto declaraba que `contable` era autocontenido *porque nació como modelo de
> pruebas*, y que al pasar a producción su contenido se mudaba al repo fuente. BMA es lo que lo convierte en rubro de
> producción, así que se mudó **antes** de escribir los agentes nuevos: el contenido vive en
> `C:/Sistemas/Agente Contable-IA` y en el núcleo queda solo el manifiesto con `raiz:`, igual que `inmobiliario`.
> La reimportación dio **0 versiones nuevas y 24 sin cambios** — los hashes son idénticos, así que ninguna tarea ya
> guardada se ve afectada. Efecto colateral atendido: el test que importa los manifiestos reales ahora avisa con un
> mensaje claro si el repo fuente no está clonado, en vez de fallar con un "archivo no encontrado".

### 2.2. Conectores (M11) — el salto que cambia el proyecto

Hoy **los diez agentes del rubro usan solo documentos y conocimiento**: trabajan sobre lo que la persona sube. Los
conectores son trabajo nuevo, y cada uno es un `IConectorTipo` con su `HerramientaConector`, bajo el guardia de destinos
(credenciales de la organización cifradas, lista blanca de dominios por conexión, ninguna dirección interna, aprobación
humana salvo lo que el Director habilite).

**Actualizado 2026-09-23 con el research de los tres sistemas** (ver
[research-arca-arba-sos-2026-09.md](../research-arca-arba-sos-2026-09.md)).

| Conector | Estado | Qué destraba |
|---|---|---|
| ~~**ARCA**~~ | **SE CAE DEL ALCANCE.** No existe el web service: el catálogo oficial de ARCA (50+ servicios) no tiene ninguno que liste los comprobantes recibidos de un contribuyente. "Mis Comprobantes" es **portal web**, no servicio | — |
| **SOS Contador** | **VERIFICADO 2026-09-23: `GET /compra/listado/:periodo` lista los comprobantes RECIBIDOS.** También `POST /compra/consulta`, `/compra/detalle/:id` y `PUT`/`DELETE /compra/:id`. **No hay endpoint de ventas** | ⭐ **El cruce necesita UN solo archivo** (el de ARCA): el lado SOS entra por API. Y lo que el cruce detecte **se puede corregir por API**, con aprobación humana |
| **ARBA** | **Regímenes generales: sí** (alícuotas y padrón por CUIT y período, sin operador). **Convenio Multilateral: va por COMARB**, a verificar | Automatiza la parte provincial de la constatación de Sueldos |

**El control ARCA↔SOS queda así, y es mejor de lo que parecía:** la persona baja **un solo archivo** —el export de Mis
Comprobantes de ARCA, hasta 365 días por consulta— y **el otro lado lo trae el agente por la API de SOS**
(`GET /compra/listado/:periodo`). Acción humana de un paso, sin problema contractual y sin credenciales de clientes en
el sistema. Además, como la API expone `PUT`/`DELETE /compra/:id`, **lo que el cruce detecte se puede corregir por API**
en vez de a mano — con la aprobación humana que el producto exige para toda acción que escribe.

**El límite que queda:** no hay endpoint de **ventas**. Para cruzar comprobantes **emitidos** hay que exportar de SOS.
No es donde está el dolor —los emitidos los genera el propio cliente y llegan en hora—, pero hay que decirlo.

Y hay algo que el research dio de regalo: **se sabe por qué faltan comprobantes.** Autoimpo de SOS solo trae los de los
últimos 12-15 días —está documentado por el proveedor—, así que todo lo que un proveedor carga tarde en ARCA no entra
nunca solo. El agente ahora sabe qué está buscando y por qué aparece.

> Queda descartada también la advertencia anterior sobre WSFEv1: era correcta —la experiencia previa es de emisión— pero
> ya no importa, porque el servicio de consulta directamente no existe.

### 2.3. Configuración de la organización (no es desarrollo)

| Qué | Cómo |
|---|---|
| Alta del tenant y licencia del rubro `contable` | Consola de Olvidata |
| **Etapa de entrega** | Arrancar en *"Tu forma de trabajar"* — deja Reglas, Instructivos y **Automatizar lo que repetís** a la vista, y esconde Programaciones/Aprobaciones/Consumo hasta que el estudio esté listo |
| Áreas | Una por rama: Contabilidad, Impuestos, Sueldos |
| Reglas de la empresa | Las dos no negociables (§4 del Diseño) el día uno |
| Cartera de clientes | Las empresas que atiende el estudio |
| Todo lo demás | **Lo carga el estudio**, conversando con el analista de automatizaciones |

## 3. Cómo corre una tarea de punta a punta

El motor ya resuelve esto; se documenta para que se vea dónde entra cada pieza.

```
Persona → "Automatizar lo que repetís" → analista (M15) → propone instructivo + prueba + programación
                                                                      ↓ (la persona aplica)
Programación (M12) → cada vuelta crea una tarea → agente del rubro (cont-control-arca)
                                                    ↓
                            reglas del estudio + instructivo + conocimiento ARCA
                                                    ↓
                        documentos del cliente  o  conector ARCA/SOS  (M11, con guardia)
                                                    ↓
                                    resultado → bandeja de Resultados → lo revisa una persona
```

Nada se presenta ni se paga en ese recorrido: el último paso es siempre humano.

## 4. Lo que NO se construye

- **Nada a medida para BMA fuera del núcleo.** Si algo solo le sirve a BMA, va en su organización como instructivo o
  agente propio, no en el código.
- **Ningún acceso automatizado a Bejerman/Onvio.** Sigue en pie el bloqueo contractual de Thomson Reuters (preguntas 2 y
  3). Onvio queda acotado a Sueldos y lo que se automatiza de esa rama es la constatación **contra ARBA**.
- **Ningún cálculo impositivo en el modelo.** Va en código determinístico invocado como herramienta, o lo hace el sistema
  de origen.
- **Los archivos reales del estudio no entran al repo del producto.** Los extractos y mayores de `archivos/` se usan como
  material de prueba del proyecto, nunca se versionan en el núcleo (plan §7: confidencial de terceros).

## 5. Riesgos y decisiones abiertas

| # | Riesgo / decisión | Impacto si sale mal |
|---|---|---|
| A1 | ~~El conector de ARCA puede no existir~~ **CONFIRMADO 2026-09-23: no existe.** | Resuelto sacándolo del alcance. El control se hace con el export de Mis Comprobantes y la persona sigue bajando el archivo. **No cotizar ese conector** |
| A2 | ~~Delegación de clave fiscal~~ **Ya no aplica al conector** (no hay conector). Sigue valiendo si algún día se usa un servicio de terceros que automatice el portal — camino **no recomendado** | — |
| A3 | ~~Mudanza del rubro `contable`~~ **HECHA 2026-09-23.** El contenido vive en `C:/Sistemas/Agente Contable-IA` y el manifiesto apunta con `raiz:`. La reimportación dio **0 versiones nuevas** (hashes idénticos): ninguna tarea guardada se ve afectada | Cerrado |
| A7 | **Convenio Multilateral va por COMARB**, no por ARBA | Sin verificar, la constatación de CM de Sueldos queda sin automatizar. Es la verificación que sigue |
| A4 | **El calendario y las alícuotas reales** | Hoy el rubro los omite a propósito. Si se cargan, alguien los tiene que mantener: un vencimiento viejo dicho con seguridad es peor que no tenerlo |
| A5 | **Costo por token** con varias personas relevando y programando | El producto ya trae tope de gasto por organización y por miembro (M6) y aviso cuando una programación se lleva buena parte del tope. Hay que fijarlos al configurar, no después del primer susto |
| A6 | **Adopción**: el modelo depende de que cada persona releve lo suyo | Si no lo hacen, el estudio queda con agentes genéricos y sin lineamiento. El piloto de conciliación es la prueba de que el modelo prende |

## 6. Orden de construcción

| # | Qué | Depende de |
|---|---|---|
| 1 | ~~Decidir A3~~ **HECHO** | — |
| 2 | Alta del tenant, licencia, áreas, reglas del estudio | — |
| 3 | `cont-soporte-sistemas` + conocimiento `60-arca.md` / `61-arba.md` (con el límite de 12-15 días de Autoimpo adentro) | 1 |
| 4 | **Piloto: conciliación bancaria** con `cont-registracion` y una persona, sobre los archivos reales | 2 |
| 5 | **`cont-control-arca` sobre el export de Mis Comprobantes** | 1, 3 |
| 6 | ~~Conector ARCA~~ **cancelado** · **Conector SOS: verde**, `/compra/listado` y `/compra/consulta` verificados | — |
| 7 | `cont-arba` + conector ARBA (regímenes generales). Convenio Multilateral, según COMARB | A7 |
| 8 | Rollout por rama, cada persona con su analista | 4, 5 |

**Los pasos 1 a 5 no dependen de ninguna respuesta de terceros y ahora el 5 tampoco**: el control ARCA↔SOS pasó de
"esperar a ver si existe el web service" a "trabajo que se puede hacer ya". Es el tramo cotizable.
