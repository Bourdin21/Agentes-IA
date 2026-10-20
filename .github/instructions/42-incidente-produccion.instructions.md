---
description: Via rapida para incidentes de produccion — triage, contencion, fix minimo y cierre en frio. No reemplaza la secuencia Discovery->Cierre: la saltea a proposito, conservando las cuatro reglas que no se negocian.
applyTo: "**"
---

# 42 - Incidente de produccion (via rapida)

## Para que existe

La secuencia obligatoria (Discovery -> Analisis -> Diseño -> Arquitectura -> Presupuesto -> Implementacion -> QA
-> Documentacion -> Calibracion) esta optimizada para **no construir lo que no se entendio**. Con el cliente
parado no sirve: ninguna de las cuatro etapas de analisis mueve la aguja mientras el sistema esta caido, y los
gates duros de `00-operativa-global` obligarian a esperar un presupuesto aprobado para arreglar algo que ya se
pago y que hoy no funciona.

Hasta 2026-10-19 el estudio no tenia via formal para esto, asi que los incidentes se atendian por chat suelto,
fuera del harness. El costo quedo documentado en los proyectos: fixes que cambiaron el comportamiento sin aviso al
equipo del cliente (el formulario de contadores de eleven-la-plata paso a rechazar valores y no se anuncio), y
bugs de datos que recien se vieron semanas despues (441 movimientos invisibles por cuenta soft-deleted — el mismo
patron que ya habia pasado en agosto con los alquileres).

El problema de una emergencia no es la velocidad: es que **el apuro genera el segundo incidente**. Esta
instruccion saltea las etapas de analisis y conserva unicamente las cuatro reglas que no se negocian ni a las dos
de la mañana.

## Cuando aplica: clasificacion en el primer minuto

La urgencia la define el **sintoma tecnico**, no el tono del mensaje del cliente. Tres preguntas:

1. ¿Hay usuarios que **ahora** no pueden trabajar?
2. ¿Se estan escribiendo **ahora** datos o importes mal (plata, stock, contadores, comprobantes emitidos)?
3. ¿Existe workaround razonable para pasar el dia?

| Nivel | Sintoma | Via |
|---|---|---|
| **P1 — caida** | Sistema o modulo critico inaccesible para todos, o corrupcion de datos en curso | Esta instruccion, completa y sin ventana |
| **P2 — degradado** | Una operacion diaria bloqueada sin workaround, el resto del sistema en pie | Esta instruccion; deploy en ventana acordada, cierre en frio igual |
| **P3 — no es emergencia** | Todo lo demas, **incluido el pedido urgente sin caida** | Flujo normal como CR (`/agentes-ia-orquestador`) |

Si las preguntas 1 y 2 son las dos "no", es **P3**: entra por el flujo normal. Esta es la regla que sostiene a
todas las demas — una via rapida que acepta cualquier cosa deja de ser una via rapida y mata el harness, porque
todo pedido pasa a llegar envuelto en urgencia.

**Limite de reincidencia:** si un mismo proyecto abre mas de **2 P1 en un mes**, el problema dejo de ser el
incidente y es el sistema. Se abre un CR de estabilizacion por el flujo normal y se declara en `docs/indice.md`.

## Las cuatro reglas que no se negocian

### 1. Reversibilidad antes que velocidad

Antes de cualquier accion que escriba —deploy, migracion, UPDATE, borrado— hay dos cosas hechas: **backup de la
BD** (`mcp smarterasp database_create_backup`, o el mecanismo del hosting que corresponda) y el **plan de vuelta
atras escrito en una linea** dentro del `INC`. Un fix irreversible sobre datos convierte una caida de una hora en
una perdida permanente, y es el unico daño de un incidente que no se puede deshacer despues con calma.

### 2. No se escribe sobre datos sin medir primero

Todo `UPDATE`/`DELETE` masivo va precedido del `SELECT` que **cuenta las filas afectadas**, con el mismo `WHERE`.
Ese numero queda anotado en el `INC` antes de ejecutar, y la escritura corre dentro de transaccion. Despues se
vuelve a contar y se compara. Los dos casos donde esto importo de verdad fueron los 69 contadores y los 441
movimientos de eleven-la-plata: en ambos, el numero era el unico modo de saber si el fix habia alcanzado o se
habia pasado de largo.

### 3. El que arregla no cierra el incidente

La separacion de roles se **atenua, no se abole**:

- En P1 el implementador **si ejecuta smoke test** — excepcion explicita y acotada a la regla de
  `00-operativa-global` ("el Implementador nunca ejecuta smoke test funcional"), porque de madrugada no hay otro
  rol disponible y el sistema esta caido.
- Con ese smoke declara **servicio restablecido**, nunca **defecto cerrado**. Son dos estados distintos del `INC`
  a proposito.
- El cierre lo declara **QA independiente, en corrida aparte, con contexto fresco y Default-FAIL**
  (`30-qa-regresiones`), dentro de 48 h. Sin esa corrida el incidente no esta cerrado, por mas que el cliente ya
  este trabajando.

### 4. El aviso es parte del fix

Si el fix cambia lo que el usuario ve, lo que el sistema acepta o lo que una pantalla ahora rechaza, el **aviso al
equipo del cliente sale antes** de declarar servicio restablecido. Un fix silencioso que endurece una validacion es
un incidente nuevo con forma de ticket de soporte, y llega cuando ya nadie lo relaciona con el fix.

## Secuencia

| # | Paso | Caja de tiempo | Prohibido en este paso |
|---|---|---|---|
| 0 | **Triage** — clasificar P1/P2/P3, abrir `INC-NNN`, declarar cobertura comercial | 10 min | Empezar a mirar codigo antes de clasificar |
| 1 | **Contencion** — detener el daño | 30 min | Saltearla porque "el fix es facil" |
| 2 | **Diagnostico** con evidencia observada | sin caja | Pasar a fix con una hipotesis sin evidencia |
| 3 | **Fix minimo** quirurgico | sin caja | Cualquier cambio que no sea el sintoma |
| 4 | **Verificacion + deploy + aviso** | — | Deployar sin backup (regla 1) o sin aviso (regla 4) |
| 5 | **Cierre en frio** — QA independiente, catalogo, calibracion | 48 h | Dar el `INC` por cerrado sin la corrida de QA |

### Paso 1 — Contencion: primero revertir, despues entender

La primera pregunta del paso 1 no es "que pasa" sino **"¿hubo deploy en las ultimas 72 h?"**. Si hubo, revertir es
la primera hipotesis y se evalua **antes** de diagnosticar: devuelve el servicio en minutos y deja el diagnostico
para cuando nadie este esperando. Si no hubo deploy, evaluar igual la mitigacion — bajar el modulo, apagar el job,
quitar el acceso a la pantalla que corrompe — porque **mitigar no es arreglar y casi siempre es mas rapido**. Una
pantalla deshabilitada con un cartel es mejor que una pantalla que escribe mal.

### Paso 2 — Causa raiz observada, o fix declarado paliativo

El paso 3 no arranca sin una de estas dos cosas:

- **causa raiz observada** — log, fila de la BD, request reproducido, snapshot. "Debe ser por X" no es evidencia; es
  exactamente el razonamiento que produce el segundo incidente; o
- la declaracion explicita de que el fix es **paliativo**, que deja el `INC` con un **CR de causa raiz abierto** por
  el flujo normal. Un paliativo declarado es trabajo honesto; un paliativo disfrazado de fix vuelve.

Fuentes baratas antes de leer codigo: `mcp smarterasp website_get_logs`, la consulta directa a la BD, y el diff del
ultimo deploy.

### Paso 3 — Fix minimo: el limite es el sintoma

Nada fuera del sintoma. Ni refactor, ni mejora de paso, ni la deuda vecina que se ve desde ahi. Si la causa raiz
pide un cambio estructural (una migracion, un cambio de maquina de estados, tocar un servicio compartido), el fix
de emergencia es el **paliativo acotado** y el cambio estructural entra como CR al flujo normal, con su id.

Antes de escribir una linea: **indice de `32-estandares-qa-implementador`** filtrado a la familia del sintoma
(`python scripts/contexto.py indice 32`). Son 45 reglas y 100 KB: se leen las 2 o 3 de la familia que se toca. El
catalogo existe precisamente porque la mitad de los incidentes del estudio ya habia pasado en otro proyecto.

## Registro: `docs/<proyecto>/incidentes.md`

Archivo nuevo por proyecto (plantilla en `docs/templates/proyecto/incidentes.md`), con las mismas reglas de memoria
que el resto de `definiciones/`: **entradas con id**, nada de reescribir texto viejo (`29-trazabilidad-conversacion`),
techo de 150 KB y archivado con `scripts/archivar_memoria.py`.

El `INC` se **abre en el paso 0, no se escribe al final** — el informe que se deja para despues no se escribe nunca.
Arranca con cinco campos y se completa mientras avanza:

```markdown
### INC-007 — Listado de movimientos vacio para todas las cuentas  ·  estado: abierto
- **nivel:** P1
- **abierto:** 2026-10-19 02:10
- **sintoma observado:** el listado global devuelve 0 filas; la BD tiene 441 movimientos
- **alcance:** todos los usuarios, modulo Finanzas
- **cobertura:** mantenimiento vigente (PRO)
```

Campos que se agregan al avanzar: `contencion`, `plan de vuelta atras`, `backup`, `filas medidas` (regla 2),
`causa raiz` (observada | **paliativo**), `archivos del fix`, `migracion EF`, `aviso enviado` (a quien y cuando),
`restablecido` (fecha + evidencia del smoke), `cerrado` (fecha + corrida de QA), `horas reales`.

Estados, en orden y sin saltos: **`abierto` -> `restablecido` -> `cerrado`**. `restablecido` significa que el
cliente trabaja; `cerrado`, que paso la corrida de QA independiente. Mientras no este `cerrado`, el incidente es
**deuda abierta visible**: `scripts/doctor.py` avisa pasados 7 dias y lo marca como error pasados 30.

## Paso 5 — Cierre en frio (<= 48 h)

No es opcional y no es papeleo: es el unico paso que convierte el incidente en algo que el estudio no vuelve a
pagar dos veces.

1. **Corrida de QA independiente** (`agentes-ia-qa`, contexto fresco, Default-FAIL) sobre el modulo afectado + las
   regresiones de su familia. Hasta ese PASS el `INC` no se cierra.
2. **Catalogo de regresiones:** item nuevo en `docs/qa/regresiones-manuales.yml` si el bug es reproducible por
   pasos, y regla nueva en `32-estandares-qa-implementador` si la causa raiz generaliza a otros proyectos del
   baseline (criterio completo en `00-operativa-global`, seccion de memoria acumulativa).
3. **Horas reales al dataset** (`docs/calibracion/dataset.yml`): las horas de incidente son el dato mas honesto que
   produce el estudio sobre el costo real de un sistema en produccion, y es el que hoy no se mide.
4. **CR de causa raiz abierto** si el fix fue paliativo, por el flujo normal.
5. **Commit y deploy declarados** (en que rama, con que id), y la fila del proyecto actualizada en `docs/indice.md`
   si el estado visible cambio.
6. `python scripts/doctor.py` antes de dar el `INC` por cerrado.

## Carga de contexto (techo 25k tokens — el mas bajo del harness)

Un agente de incidente que arranca con medio presupuesto de contexto gastado en analisis funcional de hace seis
meses razona peor justo cuando menos se puede permitir. Se lee **solo**:

- `docs/<proyecto>/metadata.md` — `ruta_repositorio`, hosting, BD, URL productiva.
- `docs/<proyecto>/incidentes.md` — unicamente las entradas **no** `cerrado`. Un incidente abierto es la primera
  hipotesis de uno nuevo.
- `docs/<proyecto>/definiciones/5-implementador.md` — **solo el ultimo sprint/CR**. Lo que se toco hace poco es lo
  que mas probablemente rompio.
- `32-estandares-qa-implementador` **por indice**, la familia del sintoma.
- Esta instruccion (`42`) y `30-qa-regresiones` para el cierre.

**No se lee en un incidente:** `1-analista-funcional.md`, `2-disenador-funcional.md`, `4-presupuestador.md`, `27`,
`28`, ni `trazabilidad.md` completo.

## Lo que esta instruccion NO cubre

- **Caida de infraestructura** — servidor, application pool, SSL, DNS, mail, cuota de BD. Playbook distinto:
  `/olvidata-infra` y `docs/referencia/runbook-urgencias-viaje.md`. No es un bug del sistema y el diagnostico no
  pasa por el codigo.
- **Pedido urgente sin caida** — P3, flujo normal. Que el cliente escriba en mayusculas no cambia el nivel.
- **Soporte de usuario** — contraseña, permiso mal asignado, duda de uso. Se responde, no se abre `INC`.
- **Discusion de plata.** El triage declara la cobertura (dentro del plan de mantenimiento / fuera de plan) y sigue.
  La conversacion comercial va despues, con las horas reales ya medidas; **nunca frena el fix**.
