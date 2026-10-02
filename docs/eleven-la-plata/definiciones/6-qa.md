# Memoria - QA

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-10-01

## Definiciones vigentes

### Alcance funcional validado (ciclo H1)
Fix de validacion de contadores en `AlquilerService.UpdateAsync` (H1). Se valido el cambio puntual, no un
barrido general del sistema (el Discovery ya se hizo por separado el 2026-08-20).

**Entorno de prueba:** MySQL local (`localhost:3306`), base `eleven` con datos reales de sesiones anteriores
(487 alquileres, 473 maquinas, 6157 contadores, 239 clientes). Para no mutar la base local del owner, se
clono a `eleven_qa`, se ejecutaron todas las pruebas contra el clon y se elimino al cerrar. Base real
verificada intacta al final (487 alquileres, fixtures sin cambios, 0 filas con marca QA).

**Metodo de ejecucion:** el servidor MCP `playwright` **no estuvo disponible en esta sesion** (`.mcp.json` vive
en `C:/Sistemas/Agentes-IA`, que es working dir secundario; las herramientas `mcp__playwright__*` no se
cargaron). Declarado explicitamente segun `33-verificacion-automatizada-qa.instructions.md`. Se compenso con
dos mecanismos que **si** ejecutaron el sistema real (no descripciones):
1. Harness de ejecucion fuera del repo (scratchpad, NO es test unitario ni quedo en la solucion) que instancia
   el `AlquilerService` real contra el clon y ejercita Create/Update.
2. App levantada localmente (`dotnet run`, `http://localhost:5199`) y ejercitada por HTTP con curl
   (GET/POST reales, antiforgery incluido).

### Casos de prueba acordados y resultado

| # | Caso | Cubre | Resultado |
|---|---|---|---|
| T1 | Editar alquiler SIN cambiar maquina (solo Ubicacion/Observacion), sobre alquiler 44 con `ContadorBNInicial=0` (dato migrado inconsistente) | CA3, HU2, Prueba 1, CA4 | **PASS** |
| T2 | Editar CAMBIANDO maquina a una con contador anterior mayor al enviado (alq 327 -> maq 281, BN=1000 vs anterior 229805) | CA1, HU1, Prueba 2 | **PASS** |
| T3 | Editar CAMBIANDO maquina con contador valido (alq 341 -> maq 281, BN=250000 entre 229805 y 313897) | CA2, HU3, Prueba 3 | **PASS** |
| T4a | Alta nueva con contadores invalidos (maq 355, BN=500 vs anterior 290947) | Prueba 4 (regresion refactor) | **PASS** |
| T4b | Alta nueva con contadores validos (maq 355, BN=300000) | Prueba 4 (regresion refactor) | **PASS** |
| T5 | **Extra (pedido por implementador):** maquina COLOR (maq 15), BN valido + Color por debajo del anterior | Condicional `maquina.Color` | **PASS** |
| T6 | **Extra:** maquina B/N (maq 36) con `ContadorColor` sintetico=50000, se envia Color=0 | Condicional `maquina.Color` | **PASS** |
| P5 | Consulta de consistencia en base antes de cerrar | Prueba 5 | **PASS** (ver abajo) |

Evidencia clave por caso:
- **T1:** `Success=True`, `ContadorBNInicial` persistido sigue en 0 (no revalidado), contadores de la maquina
  2->2 (no se inserto historial). Confirma CA3/HU2 y de paso CA4: el dato migrado inconsistente no se toca.
- **T2:** `Success=False`, `Message='Error en la validación de contadores'`,
  `Errors=['El contador B/N debe ser mayor o igual a 229805']`. **La entidad no se toco**: `MaquinaId` en base
  sigue 352 (original) y contadores destino 6->6. Confirma que el early-return ocurre antes de asignar campos.
- **T3:** `Success=True`, `MaquinaId` persistida=281, contadores destino 6->7, `HistoriaContador` nuevo
  Id=6158 Fecha=2022-02-22 BN=250000. Confirma CA2/HU3 incluida la generacion del historial.
- **T4a/T4b:** el alta conserva el comportamiento exacto: mismo `Message` y mismo texto de error que antes del
  refactor; el alta valida crea alquiler (+1) y su historial (+1). **No hay regresion por la extraccion de metodo.**
- **T5:** el unico error devuelto es `'El contador color debe ser mayor o igual a 173839'` y **no** aparece
  error de B/N -> la rama de color se evalua solo por el valor de color, sobre maquina `Color=1`.
- **T6:** `Success=True`, sin error de color pese a enviar Color=0 contra un anterior de 50000, porque
  `maquina.Color == false`. **T5 + T6 forman el par A/B que prueba el condicional `maquina.Color`.**
- **P5 (consulta de consistencia):** confirmado lo que ya habia detectado Arquitectura — la mayoria de los
  alquileres tiene `ContadorBNInicial=0` por artefacto de migracion. Como la validacion solo corre cuando
  `MaquinaId` cambia, **ningun registro existente queda bloqueado retroactivamente** (demostrado por T1).
  Adicional: **0 filas** con `FechaDevolucion < Fecha` en la base real (relevante para ELV-002).

### Cobertura por criterio de aceptacion

| Criterio | Resultado | Evidencia |
|---|---|---|
| CA1 (rechaza contador inconsistente al cambiar maquina) | **PASS** | T2 + T5 |
| CA2 (guarda y crea HistoriaContador si corresponde) | **PASS** | T3 |
| CA3 (editar sin cambiar maquina no revalida) | **PASS** | T1 |
| CA4 (sin efecto retroactivo sobre datos existentes) | **PASS** | T1 + P5 |
| HU1 | **PASS** | T2, T5 |
| HU2 | **PASS** | T1 |
| HU3 | **PASS** | T3 |

### Maquina de estados
No aplica en sentido estricto: `Alquiler` no tiene enum de estado ni transiciones. Su unico estado implicito es
Activo (`FechaDevolucion == null`) vs Finalizado (`FechaDevolucion != null`). Transiciones verificadas por lectura
de codigo: Activo->Finalizado via `FinalizarAlquilerAsync` (valida no re-finalizar y fecha >= inicio);
Finalizado->Activo no existe como operacion. **Hueco detectado:** `UpdateAsync` puede escribir `FechaDevolucion`
directamente, saltando las guardas de `FinalizarAlquilerAsync` -> ver defecto ELV-002.

### Defectos activos

| Id | Severidad | Titulo | Introducido por H1? | Estado |
|---|---|---|---|---|
| ELV-001 | **blocker** | 13 controllers sin `[Authorize]` y sin `FallbackPolicy`: anonimo lee y **escribe** datos del negocio | **No** (preexistente) | Escalado, sin fix |
| ELV-002 | major | `UpdateAsync` no valida `FechaDevolucion >= Fecha` (Create si) | **No** (preexistente) | Escalado, sin fix |
| ELV-D3 | minor | `Eleven.Web/Views/Home/Index.cshtml` modificado fuera del alcance H1 declarado | **No** (cambio no declarado) | Reportado |
| ELV-D4 | minor | `appsettings.Development.json` versionado con credenciales reales de produccion | **No** (preexistente) | Reportado |

Ambos ELV-001 y ELV-002 quedaron catalogados en `C:/Sistemas/Agentes-IA/docs/qa/regresiones-manuales.yml`.

**ELV-001 (blocker) — evidencia reproducida:** sin cookie de sesion,
`POST /Alquileres/GetDataTable` devolvio JSON con los 459 alquileres (cliente, ubicacion, contacto, contadores);
`GET /Alquileres/Edit/327` devolvio 200 con el form poblado (`ContadorBNInicial=229852`) y antiforgery valido; y
`POST /Alquileres/Edit` con ese token respondio 302 y **persistio el cambio en base** (`Ubicacion` pasada a
`HACKEADO-ANONIMO`, `UpdatedByUserId = NULL`). Contraste de control: `/Cuentas` (que si tiene `[Authorize]`)
devuelve 302 al login. Causa: `AddAuthorization` en `Program.cs` define policies con nombre pero **no** define
`FallbackPolicy`, y 13 controllers no declaran guard.

### Auto-fixes aplicados
**Ninguno.** Decision deliberada, justificada caso por caso:
- El cambio bajo prueba (H1) **no tiene defectos**: 7/7 casos PASS. No habia nada que auto-corregir en el alcance.
- **ELV-001:** la causa raiz es clara, pero la remediacion correcta exige una **decision funcional previa**
  (que rol accede a que modulo: Administrador vs Tecnico, modulo por modulo). Eso es diseño de autorizacion
  nuevo, no "replicar una solucion ya validada" — que es el limite explicito del auto-fix del rol. Se escala.
- **ELV-002:** el fix si seria replicacion 1:1 de una guarda existente en `CreateAsync`, pero cae **fuera del
  alcance H1** que el owner acoto explicitamente para este ciclo, y cambia el comportamiento de **todos** los
  Edit (no solo los de cambio de maquina). Se escala con el parche exacto listo y el dato de riesgo medido
  (0 filas existentes lo violarian, o sea el fix no bloquearia nada preexistente).

### Riesgos de liberacion
1. **BLOQUEANTE — ELV-001.** No es del fix H1, pero hace que el objetivo de negocio de H1 sea parcialmente
   inutil: el fix protege la integridad de contadores contra el error de un tecnico autenticado, mientras
   cualquiera con acceso de red puede reescribir los mismos alquileres sin autenticarse. Mitigacion: definir la
   matriz de roles y aplicar `FallbackPolicy` + `[Authorize]` antes de la proxima publicacion a produccion.
2. **Friccion de UX esperada y deliberada.** La primera vez que alguien cambie la maquina de un alquiler migrado
   (con contadores en 0) la validacion lo obliga a cargar un contador real. Es correcto (CA1) pero sorprende.
   Mitigacion: avisar al cliente antes de publicar.
3. **Historial multi-maquina sigue sin existir** (excluido de H1 por Analisis). Al cambiar de maquina, el consumo
   del tramo anterior deja de vincularse a ese alquiler porque `GetDetailsAsync` filtra por la maquina *actual*.
   El fix garantiza que el dato guardado es consistente, no que el historico se preserve. Sin mitigacion en este
   ciclo — es alcance excluido, no defecto.
4. **`Home/Index.cshtml` sin declarar** (ELV-D3): el commit no es "un solo archivo" como dice la evidencia del
   implementador. Mitigacion: decidir si entra o se revierte antes del merge.

### Estado go/no-go
- **El fix H1 en si: GO.** Cumple CA1-CA4 y HU1-HU3, sin regresion en el alta, build limpio (0 errores).
- **La publicacion a produccion: NO-GO** hasta resolver ELV-001 (blocker de autorizacion, preexistente).
  Es decision del owner si se mergea H1 primero (no empeora nada) y ELV-001 se ataca como ciclo aparte.

### Checklist de salida para merge (H1)
- [x] Build `dotnet build Eleven.slnx` -> "Compilación correcta", 0 errores.
- [x] CA1-CA4 verificados con ejecucion real, no por lectura.
- [x] HU1-HU3 verificadas.
- [x] Pruebas 1-5 de `3-arquitecto-mvc.md` ejecutadas.
- [x] Caso extra Color/BN ejecutado (T5 + T6).
- [x] Regresion de alta (Prueba 4) sin diferencias respecto del comportamiento previo.
- [x] Sin migracion EF (confirmado: no hay cambios de entidad ni de configuracion).
- [x] Base real local intacta; clon de prueba eliminado; working tree sin residuos del QA.
- [ ] **Decidir `Eleven.Web/Views/Home/Index.cshtml`** (fuera del alcance declarado) — entra o se revierte.
- [ ] **ELV-001 escalado y agendado** antes de la proxima publicacion a produccion.
- [ ] **ELV-002 escalado** — parche listo, requiere OK del owner por ser fuera de alcance.

## Historial de ajustes
- 2026-10-01 (lote C): re-verificacion en contexto nuevo de los 4 fixes de los lotes A y B. **ELV-003, ELV-005,
  ELV-006 y ELV-007 CERRADOS** con evidencia de ejecucion real (mensaje leido en pantalla, escenario del
  movimiento anulado reproducido, 2.950 filas de cruce SQL sin mismatch, render servido ejecutado con node).
  Ningun defecto nuevo. **GO para el merge del lote completo.** Queda ELV-004 abierto por decision del owner y
  la causa de fondo de ELV-006 (columnas ordenables que el servicio no ordena) abierta en las otras 4 columnas.
- 2026-08-20: Primer ciclo de QA formal del proyecto. Validacion de H1 (fix de contadores en
  `AlquilerService.UpdateAsync`): 7/7 casos PASS, sin defectos en el alcance del cambio. Se detectaron 2
  defectos preexistentes fuera del alcance (ELV-001 blocker de autorizacion, ELV-002 asimetria Create/Update
  en FechaDevolucion), ambos catalogados en el playbook cross-proyecto y escalados sin auto-fix. Playwright MCP
  no disponible en la sesion: se sustituyo por harness de ejecucion contra clon de base + ejercicio HTTP real
  de la app levantada localmente.

---

---

## QA — Lote 2026-10-01 E: re-verificacion de ELV-008

**Ultima validacion de reglas cross-proyecto: 2026-10-01.** (`git log --since=2026-09-30` sobre
`32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`: sin commits. Los dos
archivos estan modificados sin commitear por los lotes A-D de hoy; el unico agregado de terceros es
MH-033/MH-034 (ledger de caja con varias cuentas reales), **no aplicable** a este alcance — el modulo bajo
prueba no tiene saldos ni conciliacion. Esta corrida **agrega** la regla ELV-008 al catalogo preventivo.)

**Veredicto: GO para el lote bis completo.** ELV-008 **cerrado con evidencia**: CA-4 pasa de FAIL a PASS y
el piso corregido sigue protegiendo los tres campos que debe, cada uno verificado por separado como
definidor del minimo. 0 defectos nuevos. 0 regresiones en la validacion de contadores del lote F1-F5.

### Entorno y metodo

- Repo del sistema **no modificado**: `git status --porcelain` al cierre identico al del arranque (los 8
  modificados del sprint + `ContadorValidator.cs` + `contadores_a_corregir.csv`, todo del Implementador).
  Cero `Edit`/`Write` sobre `C:\Sistemas\elevenlaplata`.
- `dotnet build Eleven.slnx` → **Compilacion correcta, 0 errores, 8 warnings** (NU1902 preexistentes). El
  primer intento fallo con MSB3027 por un `Eleven.Web` (PID 26836) que habia quedado vivo de un lote
  anterior; se bajo el proceso y recompilo limpio.
- Clon de trabajo `eleven_qa_e` (copia de la base local `eleven`: 10.396 movimientos, 6.157 contadores,
  2.150 repuestos, 473 maquinas). **Eliminado al cierre.** App en `http://localhost:5401` apuntada al clon
  por `ConnectionStrings__DefaultConnection`, sin tocar ningun `appsettings`. Login HTTP real con
  antiforgery y cookie jar como `no-reply@olvidata.com.ar` (Administrador + SuperUsuario); la password se
  fijo **solo en el clon**.
- Produccion (`db_a7251f_eleven2`): **solo lectura**, 4 consultas, 0 escrituras.
- **MCP de Playwright no usado.** Cobertura por HTTP real (POST + GET del redirect con la misma cookie jar
  para leer el TempData del SweetAlert) y snapshot SQL antes/despues de cada POST. Sin observar: el pixel
  que pinta SweetAlert y el click fisico en el boton.
- **Nota sobre el brief:** los `Durabilidad < 0` de la maquina 6 **no eran** artefacto del clon anterior —
  el clon fresco de hoy ya trae `min(Durabilidad) = -751.234` y el snapshot coincide dato por dato con el
  del lote D. Lo que produccion no tiene es **contadores** negativos, que es otra cosa.

### Fixtures (elegidos para que cada campo del piso sea, por separado, el minimo)

| Maquina | Color | min BN | min Color | min Asignacion | min Durabilidad | Piso esperado | Lo define |
|---|---|---|---|---|---|---|---|
| **6** | false | 537.895 | 0 (ignorado) | 4.864.578 | **-751.234** | -537.895 | `ContadorBN` |
| **425** | true | 181.161 | **95.736** | 96.384 | -13.985 | -95.736 | `ContadorColor` |
| **61** | true | 30.204 | 28.310 | **27.003** | -87.157 | -27.003 | `ContadorAsignacion` |

### Cobertura por criterio

| CA | Resultado | Evidencia observada |
|---|---|---|
| **CA-4 ajuste negativo legitimo en maquina con Durabilidad negativa** | **PASS** (era FAIL) | `POST /Maquinas/AjustarContadores id=6 cantidadAjustar=-100` → 302 + SweetAlert `icon:'success'`, *"Contadores e insumos ajustados correctamente."* Snapshot: `sumBN 192.275.215 → 192.268.415` (−6.800 = 100×68 contadores), `sumDurabilidad -99.561 → -100.361` (−800 = 100×8 repuestos), `sumContadorAsignacion 45.026.935 → 45.026.135` (−800). Se aplico a contadores **y** a repuestos, exacto. |
| **CA-3 nuevo — `ContadorBN` en el piso** | **PASS** | M6: `-537.896` → `icon:'error'`, *"El ajuste no puede ser menor a **-537.895**: dejaria contadores en negativo."* El minimo sale de `min(ContadorBN)=537.895`, no de `ContadorAsignacion` (4.864.578) ni de `Durabilidad` (-751.234). Borde exacto `-537.895` **se aplica** y deja `min(ContadorBN)=0`. |
| **CA-3 nuevo — `ContadorColor` en el piso (maquina color)** | **PASS** | M425 (`Color=true`): `-95.737` → rechazo *"no puede ser menor a **-95.736**"*; el minimo sale de `min(ContadorColor)=95.736`, por debajo de `min(ContadorBN)=181.161` y `min(ContadorAsignacion)=96.384`. Borde `-95.736` se aplica y deja `min(ContadorColor)=0`. |
| **CA-3 nuevo — `ContadorAsignacion` en el piso** | **PASS** | M61: `-27.004` → rechazo *"no puede ser menor a **-27.003**"*; el minimo sale de `min(ContadorAsignacion)=27.003`, por debajo de `ContadorColor` (28.310) y `ContadorBN` (30.204), y la `Durabilidad` de -87.157 **no lo tomo**. Borde `-27.003` se aplica y deja `min(ContadorAsignacion)=0`. Es el campo de repuestos que quedo en el piso y **se verifico como definidor del minimo**. |
| **CA-3 nuevo — `Durabilidad` EXCLUIDA del piso pero igual mutada** | **PASS** | En los 3 fixtures `Durabilidad` bajo con el ajuste sin limitarlo nunca. M425 es el caso mas claro: su `Durabilidad` **cruza de positiva a negativa** dentro de un ajuste aceptado (`sumDurabilidad +51.025 → -1.097.807`). |
| **`Durabilidad` puede hundirse mas** | **PASS** | M6: `min(Durabilidad) -751.234 → -751.334` con `-100`, y `→ -1.289.129` con el borde `-537.895`. Nada lo bloquea y no hay mensaje de advertencia. M61: `-87.157 → -114.160`. |
| **CA-1 rechazo entero, nada parcial** | **PASS** | Los 3 rechazos (`-537.896` en M6, `-95.737` en M425, `-27.004` en M61) dejan los **10 agregados** del snapshot identicos byte a byte (sumas y minimos de BN, Color, Durabilidad y ContadorAsignacion). 0 filas mutadas en los 3. |
| **CA-2 mensaje con el minimo en es-AR** | **PASS** | Los 3 textos servidos usan `.` de miles: `-537.895`, `-95.736`, `-27.003`. |
| **CA-5 ajuste positivo normal** | **PASS** | `+100` y `+537.895` en M6, `+95.736` en M425, `+27.003` en M61: toast de exito y **restauracion exacta** del snapshot de los 3 fixtures (verificado al cierre). |
| **CA-6 error visible con detalle** | **PASS** | `ArmarMensajeDeError` llega al layout: el HTML del GET post-redirect trae `Swal.fire({icon:'error', ... text:'El ajuste no puede ser menor a -X: ...'})`, con el numero, no un generico. |
| **Borde maquina B/N: `ContadorColor` fuera del piso si `Color=false`** | **PASS** | M6 es `Color=false` y tiene `min(ContadorColor)=0`. Si `ContadorColor` entrara al piso, el minimo seria 0 y **todo** ajuste negativo se rechazaria. Se aplicaron `-100` y `-537.895`, y `sumContadorColor` quedo en 0 sin tocarse en los dos casos. |

### Contraste contra produccion (solo lectura)

| Pregunta | Dato observado |
|---|---|
| Negativos en los **tres** campos que quedaron en el piso | `ContadorBN < 0`: **0**. `ContadorColor < 0`: **0**. `ContadorAsignacion < 0`: **0**. La premisa del CA-3 nuevo **se sostiene contra el parque real**: ningun dato existente la contradice, y el clamp `Math.Min(0, ...)` es hoy codigo defensivo inalcanzable, no un bloqueo. |
| `Durabilidad < 0` | **350 de 1.314** repuestos vivos, en **90 de 194** maquinas — sin cambios respecto del lote D. |
| De esas 90 maquinas, cuantas **se destraban** con el fix | **68 admiten ahora un ajuste negativo** (piso < 0). Las **22 restantes** siguen en piso 0, y **no por `Durabilidad`**: tienen un `ContadorBN` (21 casos), `ContadorColor` (3) o `ContadorAsignacion` (1) **exactamente en 0**. Es el piso funcionando como debe — un contador en 0 no puede bajar. Cae dentro de las 110 filas en 0 que el owner ya esta corrigiendo con valores reales (fuera de alcance). |

### Regresion obligatoria — validacion de contadores del lote F1-F5 (`ContadorValidator`)

| Caso | Resultado | Evidencia |
|---|---|---|
| Alta de contador regresivo | **PASS** | `POST /Maquinas/CreateContador MaquinaId=143 Fecha=2025-07-01 ContadorBN=4.000.000` (ultimo previo 4.875.825) → `icon:'error'`, *"El contador B/N debe ser mayor o igual a **4.875.825**"*. 0 filas insertadas (96 contadores antes y despues; 0 filas con `ContadorBN=4000000`). |
| Edicion regresiva (cota inferior) | **PASS** | `UpdateContador Id=5889 ContadorBN=4.000.000` (anterior 4.843.132) → *"debe ser mayor o igual a **4.843.132**"*. Valor en base sin cambios: 4.863.489. |
| Edicion por encima del siguiente (cota superior) | **PASS** | `UpdateContador Id=5889 ContadorBN=5.000.000` (siguiente 4.875.825) → *"debe ser menor o igual a **4.875.825**"*. Valor en base sin cambios. |
| Contador **color** regresivo en maquina color | **PASS** | `UpdateContador Id=6034 MaquinaId=347 ContadorColor=100` (anterior 505.361) → *"El contador color debe ser mayor o igual a **505.361**"*. Base: `196.432 / 517.825`, sin cambios. |
| Interaccion ajuste masivo ↔ validador | **PASS (por construccion + observado)** | El ajuste desplaza **todos** los contadores de la maquina por la misma cantidad, asi que la monotonia de la serie se preserva; verificado en M6 y M425, que siguieron aceptando altas/ediciones validas despues de cada ajuste. |
| Smoke de pantallas | **PASS** | `Maquinas`, `Maquinas/Details/6`, `Maquinas/Details/425`, `Movimientos`, `Cuentas/Details/1` → 200. **0 ERR/EXCEPTION** en el log de la app durante toda la corrida. |

### Cobertura del catalogo cross-proyecto

| Item | Aplica | Resultado |
|---|---|---|
| **ELV-008** | Si | **CERRADO.** CA-4 PASS con snapshot, y el piso corregido verificado campo por campo. |
| **ELV-004** | Si | **CERRADO del todo.** El sintoma original (ajuste negativo arbitrario con mensaje de exito) no se reproduce, y ya no sobre-restringe. |
| MH-001 / CRM-019 (`Contains`/`StartsWith` a MySQL) | No | No se agregaron consultas con colecciones locales. |
| LP-003 (decimales en cultura invariante) | Si | **PASS** — `cantidadAjustar` es `int`; el formateo es-AR es **solo de salida** (mensaje), no viaja de vuelta al servidor. |
| CRM-017 (un tope tiene que aplicarse en TODOS los caminos que lo consumen) | Si | **Observacion, no defecto.** `AjustarContadoresAsync` es el unico camino de ajuste masivo. `CambiarRepuesto` (`MaquinaService.cs:493-495`) tambien mueve `Durabilidad`, por diferencias de contador y **sin piso** — preexistente, fuera de alcance, y consistente con el criterio nuevo (es justamente la prueba de que `Durabilidad` es una magnitud relativa). |
| ELV-005 / ELV-006 / ELV-007 | No | Fuera de alcance: el fix no toca `MovimientoService` ni las grillas. Cerrados en el lote D. |
| **ELV-008 como regla preventiva** | — | **Agregada** a `32-estandares-qa-implementador.instructions.md`: *"Una validacion 'esto no puede ser negativo' se escribe sobre los campos que de verdad no pueden, no sobre todos los que el ajuste toca"*. El patron es generalizable y no estaba en el catalogo. |

### Cobertura de reglas nuevas/modificadas desde la corrida anterior

| Regla | Aplica | Resultado |
|---|---|---|
| MH-033 / MH-034 (ledger de caja: toda salida real de dinero; una cuenta por movimiento) | **No** | El modulo bajo prueba no tiene saldos, ledger ni conciliacion. Declarado, no ejecutado. |
| ELV-008 (agregada en esta corrida) | Si | Ejecutada contra el sistema: es el objeto de este lote. **PASS.** |

### Defectos

**Ninguno nuevo.** Observaciones sin severidad asignada, todas preexistentes y fuera de alcance:

1. **22 maquinas con un contador exactamente en 0** no admiten ningun ajuste negativo. Es el piso
   funcionando como debe, pero vale decirlo: el mensaje que ve el usuario sera *"no puede ser menor a 0"*,
   que es correcto pero poco explicativo. Se resuelve solo cuando el owner corrija las 110 filas en 0.
2. **`CambiarRepuesto` mueve `Durabilidad` sin piso** (`MaquinaService.cs:493-495`). Preexistente y
   coherente con el criterio nuevo; se deja anotado para que un fix futuro no le agregue un piso en 0 por
   simetria mal entendida.

### Estado de los defectos de la corrida anterior

| Item | Estado |
|---|---|
| **ELV-008** | **CERRADO.** Criterio de re-verificacion del lote D cumplido literalmente: en M6 (`min(Durabilidad)=-751.234`, `min(ContadorBN)=537.895`) el ajuste `-100` se aplica, las 3 sumas bajan exactamente `100 x cantidad_de_filas` (6.800 / 800 / 800) y la pantalla muestra el toast de exito; y en el borde el `-min` sigue aplicando y `-min-1` sigue rechazando, verificado en los 3 fixtures. |
| **ELV-004** | **CERRADO.** |
| ELV-009 | **ABIERTO, escalado al owner.** Preexistente, pendiente de decision. No re-reportado por indicacion del brief. |
| ELV-005 / ELV-006 / ELV-007 | **CERRADOS** en los lotes C/D. |

### Riesgos de liberacion

- **Bajo.** El fix es una sustraccion de una linea de una lista, con la mutacion intacta; el piso quedo
  sobre tres campos que produccion confirma que nunca son negativos.
- **A vigilar (no blocker):** el piso y la mutacion son **dos listas separadas en el mismo metodo** y nada
  las ata. Si manana se agrega un campo al bloque de mutacion, nadie avisa si corresponde o no al piso. Es
  exactamente el error que produjo ELV-008, ahora en la direccion opuesta.
- **Documental:** el comentario de `ELV-004` en el codigo (lineas 213-221) todavia afirma *"no existe un
  valor negativo valido"* para "la durabilidad/asignacion de un repuesto", que es la premisa que este fix
  refuto. El comentario de abajo (235-242) la corrige, pero el de arriba quedo contradiciendolo. No afecta
  el comportamiento; conviene limpiarlo cuando se toque el archivo.
- `Eleven.Web/keys/` puede reaparecer como untracked: lo escribe Data Protection al levantar la app.
  Verificado y limpio al cierre.

### Checklist de merge (lote bis completo: ELV-004 con el piso corregido + orden por columna)

- [x] `dotnet build Eleven.slnx` → 0 errores, 8 warnings preexistentes.
- [x] CA-4 PASS con snapshot de base antes/despues y toast de exito observado.
- [x] CA-3 nuevo verificado **campo por campo**: `ContadorBN`, `ContadorColor` (maquina color) y
      `ContadorAsignacion`, cada uno como definidor del minimo, con rechazo en `-min-1` y aplicacion en `-min`.
- [x] `Durabilidad` excluida del piso **y** mutada: verificado que baja y que puede cruzar/profundizar el negativo.
- [x] Borde B/N: `ContadorColor` no entra al piso con `Color=false` (M6, `min(ContadorColor)=0`, ajuste aplicado).
- [x] CA-1, CA-2, CA-5, CA-6 PASS con POST real y snapshot.
- [x] Regresion `ContadorValidator` (F1-F5): alta y edicion, cota inferior y superior, BN y color — 4/4 PASS.
- [x] Produccion contrastada en solo lectura: 0 negativos en los 3 campos del piso; 68 de 90 maquinas destrabadas.
- [x] Sin migracion EF ni cambios de esquema.
- [x] Orden por columna (CA-7 a CA-11): **no re-corrido**, paso limpio en el lote D y el fix no toca `MovimientoService`.
- [x] Clon `eleven_qa_e` eliminado; base local `eleven` intacta; produccion solo leida.
- [x] `git status --porcelain` del repo del sistema sin residuos de QA.
- [x] Regla preventiva ELV-008 agregada al catalogo cross-proyecto.
- [ ] ELV-009 a backlog (preexistente, decision del owner pendiente).
- [ ] Limpiar el comentario contradictorio de `MaquinaService.cs:213-221` cuando se toque el archivo.
- [x] **GO para mergear el lote bis completo.** No deployar hasta que el owner cierre la correccion de las
      110 filas en 0 / 69 regresivas, que es trabajo aparte.

---

## QA — Lote 2026-10-01 D: ELV-004 + orden por columna

**Ultima validacion de reglas cross-proyecto: 2026-10-01.** (Misma fecha que la corrida anterior:
`git log --since=2026-09-30` sobre `32-estandares-qa-implementador.instructions.md` y
`docs/qa/regresiones-manuales.yml` no devuelve commits; los dos archivos estan modificados sin commitear
por los lotes A/B/C de hoy, o sea no hay reglas nuevas de terceros desde entonces. No hubo que ejecutar
reglas nuevas fuera del alcance.)

**Veredicto: NO-GO condicional.** El orden por columna esta **aprobado sin reservas** (CA-7 a CA-11 PASS,
incluida la sospecha explicita sobre la replica SQL de `ImporteConSigno`, que resulto fiel). El piso del
ajuste masivo **cumple los 6 criterios como fueron redactados** pero el criterio CA-3 esta construido sobre
una premisa falsa, y por eso el fix bloquea un caso de uso legitimo en **90 maquinas de produccion**
(defecto nuevo **ELV-008**, severidad medium). Se puede mergear el orden por columna; el piso del ajuste
necesita una vuelta por Analisis antes de publicarse.

### Entorno y metodo

- Repo del sistema **no modificado** (`git status --porcelain` al cierre: solo los 8 archivos del lote +
  `ContadorValidator.cs` + `contadores_a_corregir.csv`, todo del Implementador).
- Clon de trabajo `eleven_qa_d` (copia de la base local `eleven`: 10.396 movimientos, 152 cuentas,
  473 maquinas, 6.157 contadores, 1.164 repuestos). **Eliminado al cierre.**
- App levantada desde el repo con la connection string sobreescrita por variable de entorno
  (`ConnectionStrings__DefaultConnection`), sin tocar ningun `appsettings`. Puerto 5199.
- Produccion (`db_a7251f_eleven2`): **solo lectura**, 5 consultas de conteo, 0 escrituras.
- **MCP de Playwright no usado.** Cobertura por HTTP real con cookie jar (POST + GET del redirect para
  leer el TempData), contraste SQL independiente y ejecucion con `node` de los `render` extraidos del
  **HTML servido**. Lo unico no cubierto por este camino es el pixel renderizado del SweetAlert y el
  click fisico en el `<th>`; el payload que el click produce se reprodujo exacto
  (`sortColumn = d.columns[d.order[0].column].data`, verificado en el HTML de las dos vistas).

### Cobertura por criterio

| CA | Resultado | Evidencia observada |
|---|---|---|
| CA-1 rechazo entero, nada parcial | **PASS** | `POST /Maquinas/AjustarContadores id=149 cantidadAjustar=-99999999` -> 302. Snapshot de base identico antes/despues: `sum(ContadorBN)=656.984.599`, `sum(ContadorColor)=0`, `min(ContadorBN)=3.609.513`, `sum(Durabilidad)=917.224`, `sum(ContadorAsignacion)=57.164.346`. 0 filas mutadas. |
| CA-2 mensaje con el minimo en es-AR | **PASS** | Texto servido en el SweetAlert: *"El ajuste no puede ser menor a **-57.826**: dejaria contadores en negativo."* Separador de miles `.` (es-AR). |
| CA-3 cubre Durabilidad y ContadorAsignacion | **PASS como criterio / premisa invalida** | En la maquina 149 el piso **-57.826 sale del repuesto** (`min(Durabilidad)=57.826`), no del contador (`min(ContadorBN)=3.609.513`): la regla cubre el repuesto. Pero incluir `Durabilidad` es incorrecto como regla de dominio -> **ELV-008**. |
| CA-4 ajuste negativo legitimo se aplica | **FAIL** | Maquina 149 (todos los valores positivos): `-57.826` se aplica y deja `min(Durabilidad)=0`. **Pero** maquina 6, con contadores de 537.895 a 5.915.812 y `min(Durabilidad)=-751.234` preexistente, rechaza un ajuste de **-100** con *"no puede ser menor a 0"*. En produccion hay **90 maquinas** en esa situacion (350 de 1.314 repuestos vivos con `Durabilidad<0`). **ELV-008**. |
| CA-5 ajuste positivo se aplica | **PASS** | `+57.826` en maquina 149 restaura el snapshot exacto. `+184.894` en maquina 347 (Color=true) restaura `sum(ContadorColor)` de 8.738.846 a 16.319.500. |
| CA-6 el error se ve en pantalla con detalle | **PASS** | `ArmarMensajeDeError` llega al layout: el HTML del GET post-redirect trae `Swal.fire({icon:'error', ..., text:'El ajuste no puede ser menor a -57.826: ...'})`. No es un generico. |
| CA-7 cada cabecera ordena asc y desc | **PASS** | 14 barridos completos (7 columnas x 2 direcciones) sobre cuenta 1 (2.039 filas): **0 inversiones** en `fecha`, `numeroComprobante`, `cuentaNombre`, `tipoMovimiento`, `importeConSigno`. En `motivoNombre` (3) y `notas` (18) las unicas "inversiones" son artefactos de la colacion `utf8mb4_..._ci` de MySQL contra la comparacion sensible de Python (`almacen`/`almacén`, `Cortinero`/`cortinero`): con comparacion insensible a caso y acento quedan **0 y 1**. |
| CA-8 ninguna cabecera promete un orden que no aplica | **PASS** | `Movimientos/Index`: 8 `<th>` / 8 `columns`; 7 ordenables, todas con rama (fecha por el default). `Cuentas/Details`: 8 `<th>` / 8 `columns`; 6 ordenables, todas con rama. Los unicos `orderable: false` **en el HTML servido** son `saldoAcumulado` y la de acciones. El bloque de `numeroComprobante` ya **no** trae `orderable`. |
| CA-9 desempate por Id en todos los ordenes | **PASS** | 14 barridos ida y vuelta: `total=2039 / rows=2039 / dup=0 / faltan=0` en los 14. Barrido global de `importeConSigno` asc y desc (9.307 filas, paginas de 500): **0 duplicadas** y, en los empates de valor, **0 casos** de `Id` fuera de orden. |
| CA-10 default Fecha descendente | **PASS** | `sortColumn` vacio asc -> primera fila `2023-01-27T10:22:50`; `sortColumn` no mapeado (`saldoAcumulado`) desc -> primera fila `2026-03-25T09:01:59`. La rama default respeta la direccion (sub-bug de MH-018 no presente). |
| CA-11 acumulado identico sea cual sea el orden | **PASS** | Para los 14 ordenes, `saldoAcumulado` por `Id` comparado contra el diccionario del orden por fecha: **0 filas con saldo distinto** en los 14. `GetSaldosAcumuladosAsync` no se toco y busca por `Id`. |

### La sospecha del brief sobre `importeConSigno`: descartada con evidencia

La replica SQL **coincide con la propiedad del dominio linea por linea**
(`Ingreso -> Abs(Importe)`, `Egreso -> -Abs(Importe)`, resto -> `Importe`), y el contraste empirico lo
confirma: el campo contra el que se midio la monotonia es el **mismo `importeConSigno` que la grilla
pinta** (lo calcula `MapToDto` en C#). Barrido global, 9.307 filas, asc y desc: **0 inversiones**, con
signos mezclados (de `-2.800.000` a `+2.500.000`) y las **83 transferencias** incluidas, todas con
`Importe` negativo y `ImporteConSigno` igual a `Importe` — el caso raro del `switch` queda cubierto. El
riesgo "Medio" que el Implementador declaro **no se materializo**; sigue siendo una duplicacion a vigilar
si alguien toca `Movimiento.ImporteConSigno`.

### Regresion obligatoria

| Regresion | Resultado | Evidencia |
|---|---|---|
| Acumulado de la 1a fila = saldo del encabezado (orden default) | **PASS** | `Cuentas/Details/1`: encabezado `$ 1.295.200,00`; primera fila (mov. 10396) `saldoAcumulado = 1295200.0`. |
| ELV-005: fila anulada pinta "—", no `$ 0,00`, **bajo cualquier orden** | **PASS** | Se anulo el mov. 5240 (`Importe` 2.500.000) en el clon. Con `importeConSigno desc` queda **primero** y devuelve `saldoAcumulado: null` -> el `render` servido lo pinta `<span class="text-muted">&mdash;</span>`. El encabezado paso a `$ -1.204.800,00` y la primera fila no anulada del orden default marca `-1.204.800,0`: siguen coincidiendo. |
| ELV-007: comprobante `0` como `0`, vacio como "—" | **PASS** | `render` extraido del HTML servido y corrido con `node`: `0 -> 0`, `null -> —`, `undefined -> —`, `'' -> —`, `18152 -> 18152`. |
| Filtros + orden combinados | **PASS** | `tipoMovimiento=1` + `importeConSigno asc` -> 1.335 filas, todas tipo 1, de `-2.800.000` hacia arriba. Buscador `combustible` + `motivoNombre desc` -> 92 filas. El orden no altera los filtros ni el buscador. |

### Cobertura del catalogo cross-proyecto

| Item | Aplica | Resultado |
|---|---|---|
| CRM-003 / MH-015 / MH-018 / ELV-006 (cabecera ordenable sin rama en el switch) | Si | **PASS** — cobertura vista <-> switch exacta en las 2 grillas, y la rama default respeta la direccion. |
| DN-001 / DN-002 (Include + OrderBy dinamico + Skip/Take -> 500) | Si | **PASS** — 16 barridos completos con OrderBy dinamico y Skip/Take, 0 respuestas no-200, 0 excepciones en el log. Los `Include` de esta grilla son de referencia, no de coleccion. |
| MH-025 (resultado dependiente del orden que devuelve la base ante empates) | Si | **PASS** — desempate por `Id` verificado en los empates reales de `importeConSigno`. |
| ELV-005 | Si | **PASS** (ver regresion). |
| ELV-007 | Si | **PASS** (ver regresion). |
| ELV-004 | Si | **PASS parcial** — el defecto original (ajuste negativo arbitrario que deja los contadores en negativo con mensaje de exito) **ya no se reproduce**. Queda abierto **ELV-008**. |
| LP-004 (buscador global que se pierde al volver) | No | Esta grilla no persiste el buscador en `Session`. |
| OLV-006 (columna visible no alcanzada por el buscador global) | Si | **Observacion preexistente, no defecto del lote**: el buscador cubre cuenta, cuenta destino, motivo, notas e `Id`, pero **no** `NumeroComprobante` ni el importe. En `Cuentas/Details` hay filtro dedicado de comprobante; en `Movimientos/Index` no. |
| OLV-007 (`data-select2` rompe la grilla) | No | No se agregaron selects en este lote. |

### Defectos

1. **ELV-008 — medium — NUEVO, introducido por este lote.** El piso del ajuste masivo mete
   `RepuestoMaquina.Durabilidad` en el calculo del minimo, y `Durabilidad` es **vida util restante**: su
   propio dominio admite valores negativos (`DurabilidadPorcentaje` devuelve 0 explicitamente para
   `Durabilidad <= 0`). Con el clamp `Math.Min(0, -min)`, cualquier maquina que ya tenga un repuesto
   vencido queda con `ajusteMinimoAdmitido = 0` y **rechaza todo ajuste negativo**, con un mensaje
   enganoso ("no puede ser menor a 0: dejaria contadores en negativo") cuando ningun contador quedaria en
   negativo. Produccion: **350 de 1.314 repuestos vivos con `Durabilidad < 0`, en 90 de 194 maquinas con
   repuestos (46%)**. No hay workaround por UI.
   **Esto no es dato corrupto por ELV-004**: el propio brief confirmo que produccion tiene 0 contadores
   negativos, y estos negativos son de `Durabilidad`, otro campo, con 350 ocurrencias repartidas — es
   estado de negocio normal.
2. **ELV-009 — minor — PREEXISTENTE, no del lote.** `recordsTotal`/`recordsFiltered` cuentan movimientos
   cuya `Cuenta` esta soft-deleted, pero el `INNER JOIN` que genera `Include(m => m.Cuenta)` sobre una
   navegacion requerida los descarta: `Movimientos/Index` declara **9.748** filas y un barrido completo
   sirve **9.307** (441 faltantes, 0 duplicadas). Se reproduce igual con `sortColumn=fecha`, o sea el
   orden por columna no lo introdujo ni lo agrava. `MapToDto` ya contempla `"Sin cuenta"`, lo que sugiere
   que la intencion era listarlos.

### Partes de defecto emitidos

**Parte ELV-008 -> Implementador** (catalogado en `docs/qa/regresiones-manuales.yml`).
- Reproduccion: maquina con `min(Durabilidad) < 0` y contadores altos (en el clon, la 6) ->
  `POST /Maquinas/AjustarContadores id=6 cantidadAjustar=-100`.
- Evidencia del fallo: 302 + snapshot de base identico (`sum(ContadorBN)=192.275.215`,
  `sum(Durabilidad)=-99.561`, `sum(ContadorAsignacion)=45.026.935`) + SweetAlert
  *"El ajuste no puede ser menor a 0: dejaria contadores en negativo."*
- `archivos_fix` sugerido (hipotesis): `Eleven.Infrastructure/Services/MaquinaService.cs` — separar los
  valores con piso real en 0 (`ContadorBN`, `ContadorColor` condicional, `ContadorAsignacion`) de
  `Durabilidad`, y para `Durabilidad` usar un piso relativo o excluirla. `migracion_ef`: ninguna.
- **Escalado a Analisis antes del fix:** CA-3 pide explicitamente cubrir `Durabilidad`, asi que el
  criterio esta mal especificado, no solo el codigo. **Criterio no testeable tal como esta -> BLOCKED
  funcional sobre CA-3.** Quien decide si un ajuste negativo puede empujar una `Durabilidad` ya vencida
  mas abajo es el analista, no el Implementador.
- **Criterio de re-verificacion (arranca en FAIL la proxima corrida):** sobre una maquina con al menos un
  repuesto de `Durabilidad < 0` y `min(ContadorBN) > 1.000`, un ajuste de `-100` **se aplica** (las 3 sumas
  del snapshot bajan exactamente `100 x cantidad_de_filas`) y la pantalla muestra el toast de exito; y en
  una maquina con todos los valores positivos el borde `-min` sigue aplicando y `-min-1` sigue rechazando.

**Parte ELV-009 -> Analisis + Implementador.** Preexistente, fuera del alcance del lote. Criterio de
re-verificacion: un barrido completo de `Movimientos/Index` sin filtros devuelve exactamente
`recordsFiltered` ids unicos, con cualquier orden.

### Estado de los defectos de la corrida anterior

| Item | Estado |
|---|---|
| ELV-004 | **Re-verificado / cerrado parcialmente.** El sintoma original no se reproduce; se abre ELV-008 por sobre-restriccion. |
| ELV-005 | **CERRADO.** Fila anulada devuelve `null` y pinta "—" bajo los 14 ordenes probados; encabezado y primera fila no anulada coinciden. |
| ELV-006 | **CERRADO en la causa de fondo.** Las 7 columnas ordenables de las 2 grillas ordenan de verdad, no solo la del parche. |
| ELV-007 | **CERRADO.** |

### Riesgos de liberacion

- **Alto si se publica el piso del ajuste tal cual:** 90 maquinas de produccion pierden la posibilidad de
  un ajuste negativo, que es justamente el caso de uso que el fix dice preservar ("corregir una lectura
  mal tomada"). El usuario ve un mensaje que no describe su situacion.
- **Bajo para el orden por columna.** Es el cambio mas limpio de los tres lotes: 16 barridos completos sin
  una sola fila duplicada o perdida, y el acumulado invariante al orden en los 14 casos.
- **Duplicacion a vigilar:** la replica SQL de `ImporteConSigno` esta correcta hoy y sin test que la ate a
  la propiedad del dominio. Un cambio futuro en `Movimiento.ImporteConSigno` miente el orden en silencio.
- ELV-009 pre-existente: la grilla global promete 441 filas que nunca sirve. No es blocker.
- **`docs/qa/regresiones-manuales.yml` tiene `KOI-016` duplicado** (preexistente, detectado al validar el
  YAML). No afecta a este lote; limpieza pendiente.

### Checklist de merge (lote D)

- [x] `dotnet build Eleven.slnx` -> 0 errores, 8 warnings (todos NU1902/CS preexistentes).
- [x] CA-7 a CA-11 verificados con 16 barridos completos de paginacion contra el endpoint real.
- [x] CA-1, CA-2, CA-3, CA-5 y CA-6 verificados con POST real + snapshot de base antes/despues.
- [x] Sospecha del brief sobre la replica de `ImporteConSigno`: descartada con 9.307 filas y 83 transferencias.
- [x] Regresiones de los lotes A/B/C re-corridas (encabezado vs acumulado, ELV-005, ELV-007, filtros).
- [x] Sin migracion EF ni cambios de esquema.
- [x] Alineacion `thead` / `columns` verificada sobre el **HTML servido**: 8/8 en las 2 grillas.
- [x] Clon `eleven_qa_d` eliminado; base local `eleven` intacta; produccion solo leida.
- [x] `git status --porcelain` del repo del sistema sin residuos de QA (ver seccion de entorno).
- [ ] **CA-4 en FAIL -> ELV-008 al Implementador, previa definicion del analista sobre `Durabilidad`.**
- [ ] **CA-3 a reescribir por Analisis** (hoy obliga a una regla de dominio incorrecta).
- [ ] ELV-009 a backlog (preexistente).
- [ ] **No deployar, no commitear.** El orden por columna se puede mergear; el piso del ajuste, no.

---

## QA — Lote 2026-10-01 C: re-verificacion de fixes

**Fecha de corrida:** 2026-10-01 · **Rama:** dev (cambios sin commitear, sin deployar) · **Alcance:** re-verificacion
de los 4 fixes aplicados tras los lotes A y B — ELV-003 (mensaje de error en pantalla), ELV-005 (acumulado de filas
anuladas), ELV-006 (columna ordenable que no ordena), ELV-007 (comprobante 0 como guion) — mas la regresion
obligatoria de paginacion y del alta de alquiler (fix H1).

**Ultima validacion de reglas cross-proyecto: 2026-10-01.**

**Veredicto: GO para el merge del lote completo (A + B + C).** Los 4 fixes PASAN con evidencia de ejecucion real.
Ningun defecto nuevo introducido. Queda ELV-004 abierto por decision del owner (fuera de alcance) y la causa de
fondo de ELV-006 abierta en las otras columnas de las dos grillas.

### Entorno y metodo

- **Base de trabajo:** clon `eleven_qa_c` de la base local real `eleven` (10.396 movimientos, 152 cuentas, 0 anulados),
  **eliminada al cerrar**. Base real re-verificada intacta al final: 10.396 movimientos, 0 anulados, 0 alquileres
  `QA-LOTE-C`, 114 contadores en M60, 152 cuentas. **Produccion nunca se toco.**
- **App:** `http://localhost:5392`, `dotnet run --no-build`, apuntando al clon por variable de entorno
  `ConnectionStrings__DefaultConnection`. El repo del sistema **no se edito** (`git status --porcelain` identico al
  del arranque: los 7 modificados del sprint + `ContadorValidator.cs` untracked; el `Eleven.Web/keys/` que genero
  Data Protection se elimino).
- **Build:** `dotnet build Eleven.slnx` → "Compilación correcta", 0 errores, 8 warnings NU1902 preexistentes.
- **Playwright MCP: NO disponible en la sesion** (busqueda de herramientas `mcp__playwright__*` sin resultados).
  Declarado segun `33-verificacion-automatizada-qa`. Sustituido por: login real por HTTP con antiforgery y cookie
  jar, POST a los endpoints reales, lectura del mensaje servido en el HTML del redirect, barrido del endpoint
  `GetDataTable`, contraste SQL independiente y ejecucion con `node` del render JS **extraido del HTML servido**
  (no del archivo fuente). Lo unico sin observacion es el pixel que pinta DataTables.
- **Fixtures:** M143 (B/N, ultimo contador 4.875.825; contador 5889 intermedio), M347 (`Color=true`, ultimos
  196.985 / 537.074), M60 (alquiler, ultimo 6.259.649, 114 filas de historial), cuenta 12 (911 movimientos),
  cuenta 1 (2.039 movimientos, 10 filas con acumulado genuinamente 0), cuenta 120 (movimientos **1706 y 1707**,
  `NumeroComprobante = 0` reales; 1707 tiene ademas acumulado genuino 0 — una sola fila real que ejercita los
  dos casos de borde del lote).

### Tabla fix × resultado

| Fix | Resultado | Evidencia observada |
|---|---|---|
| **ELV-003** — `ArmarMensajeDeError` en `CreateContador`/`UpdateContador` | **PASS** | **Alta:** `POST /Maquinas/CreateContador` (M143, `ContadorBN=0`) → 302 a `/Maquinas/Details/143`, y el HTML servido trae `icon: 'error', title: 'Error', text: 'El contador B/N debe ser mayor o igual a 4.875.825'`. **El minimo con separador de miles llega a la pantalla: CA-F5.6 cierra.** |
| **ELV-003 — camino de edicion** | **PASS** | `POST /Maquinas/UpdateContador` sobre el contador 5889 (M143, anterior 4.843.132 / siguiente 4.875.825): con `BN=0` → pantalla `"El contador B/N debe ser mayor o igual a 4.843.132"`; con `BN=9999999` → `"El contador B/N debe ser menor o igual a 4.875.825"`; sin cambiar el valor → `"Contador actualizado exitosamente."` (`excludeId` sigue funcionando). |
| **ELV-003 — borde `Errors` vacio + solo `Message`** | **PASS** | `UpdateContador` con `Id=999999` (`CreateError("Registro de contador no encontrado.")`, `Errors` vacia) → pantalla `"Registro de contador no encontrado."`. **No queda en blanco.** |
| **ELV-003 — multi-error** | **PASS** | M347 (`Color=true`) con `BN=0, Color=0` → pantalla con los dos errores: `"El contador B/N debe ser mayor o igual a 196.985 El contador color debe ser mayor o igual a 537.074"`. Alta valida de control (M143, `BN=5.100.000`) → `"Contador registrado exitosamente."`. |
| **ELV-005** — `TryGetValue` devolviendo `null` | **PASS** | **Escenario original reproducido:** se anulo el ultimo movimiento de la cuenta 12 (**10361**, por el endpoint real `POST /Movimientos/Anular`; `Anulado=1` confirmado en base). Grilla en orden descendente: fila `10361` → `saldoAcumulado = null` (la vista pinta `—`), **no `0`**. Primera fila **no anulada** (`10324`) → `59.374.538,03`, **exactamente igual** al Saldo del encabezado servido en `/Cuentas/Details/12` (`$ 59.374.538,03`, bajado de `$ 59.419.538,03` antes de anular). |
| **ELV-005 — borde: acumulado genuinamente 0 muestra `$ 0,00`** | **PASS** | **La distincion se mantiene.** Cuenta 1: **10 filas** con running sum real = 0 devueltas por el endpoint como `saldoAcumulado = 0`, no `null`. Cuenta 120: movimiento `1707` → `saldoAcumulado = 0.0`. Render `saldoAcumulado` extraido del HTML servido y ejecutado con node: `null → <span class="text-muted">—</span>`, `0 → <span class="text-dark">$ 0,00</span>`, `1295200 → $ 1.295.200,00`. |
| **ELV-005 — no se rompio lo que ya pasaba (running sum)** | **PASS** | Cuentas 1 y 12 completas (**2.950 filas**) comparadas fila por fila contra un running sum calculado aparte en SQL (`SUM(CASE TipoMovimiento …) OVER (PARTITION BY CuentaId ORDER BY Fecha, Id)`, replicando `ImporteConSigno` exactamente): **0 mismatch, 0 filas no anuladas con `null`, 0 filas anuladas con valor**. |
| **ELV-006** — `orderable: false` en Nro. Comprobante | **PASS en el alcance del fix** | `orderable: false` presente en la definicion de la columna **en el HTML servido** de las dos vistas (`/Cuentas/Details/120` y `/Movimientos`). La cabecera deja de ofrecer un orden que el servicio no sabe hacer. Sin Playwright no hay captura del click; lo determinante es la config servida, que si se observo. **Causa de fondo todavia abierta en las otras columnas:** ver "Observaciones". |
| **ELV-007** — comprobante `0` se muestra | **PASS** | Render `numeroComprobante` **extraido del HTML servido** de las dos vistas y ejecutado con node: `null → —`, `'' → —`, `0 → 0`, `99001 → 99001`. Contra datos reales: el endpoint devuelve `numeroComprobante: 0` para los movimientos `1706` y `1707` (cuenta 120) — las 2 filas que el lote A habia identificado como afectadas. |
| **No se corrio ninguna columna** | **PASS** | HTML servido: `/Cuentas/Details/120` → TH(8) = `Fecha, Nro. Comprobante, Tipo, Motivo, Notas, Importe, Saldo Acumulado, Acciones` y `columns`(8) = `fecha, numeroComprobante, tipoMovimiento, motivoNombre, notas, importeConSigno, saldoAcumulado, id`. `/Movimientos` → TH(8) = `Fecha, Nro. Comprobante, Cuenta, Tipo, Motivo, Notas, Importe, Acciones` y `columns`(8) = `fecha, numeroComprobante, cuentaNombre, tipoMovimiento, motivoNombre, notas, importeConSigno, id`. **8/8 y en el mismo orden en las dos.** |

### Regresion obligatoria

| Prueba | Resultado | Evidencia |
|---|---|---|
| **Paginacion de la grilla de movimientos (ida y vuelta)** — `GetDataTableAsync` se volvio a tocar | **PASS** | Barrido completo del endpoint real, paginas de 200, 2 cuentas × 2 direcciones: cuenta 1 desc/asc 2.039 filas, cuenta 12 desc/asc 911 filas. **5.900 filas paginadas, 0 duplicadas, 0 faltantes, secuencia de ida identica a la de vuelta en los 4 barridos.** El `ThenBy(Id)` de F1 sigue puesto y el `Skip/Take` sigue determinista. |
| **Alta de alquiler (regresion del fix H1)** — `MaquinasController` se toco | **PASS** | `POST /Alquileres/Create` sobre M60 con `ContadorBNInicial=0` → 200 al form con `"El contador B/N debe ser mayor o igual a 6.259.649"`. Alta valida (inicial 6.260.149) → 302 a `/Alquileres` con `"Alquiler creado exitosamente."`, alquiler 488 persistido y el historial de M60 paso de **114 a 115** filas: `AgregarHistoriaContadorSiCorresponde` sigue generando el contador inicial. **Sin regresion sobre H1.** |
| **CA-F4.3 — el filtro por comprobante sigue funcionando** | **PASS** | `POST /Movimientos/GetDataTable?numeroComprobante=0` → `recordsFiltered=2`, filas `(1707, 0)` y `(1706, 0)`: el filtro tampoco confunde 0 con ausente. Control con un valor sin coincidencias → `recordsFiltered=0`. |

### Maquina de estados

`Movimiento` sigue sin enum de estado. Estados implicitos: Vigente (`DeletedAt == null && !Anulado`) → Anulado →
Eliminado (soft delete). **El hallazgo del lote A queda resuelto en su efecto visible:** el conjunto que la grilla
lista y el que suma el acumulado siguen siendo distintos (por diseño), pero ahora la grilla lo **declara** en vez de
mentir un cero — un movimiento anulado no tiene acumulado y se muestra como `—`. Transicion `Anular` ejercitada de
punta a punta por el endpoint real en esta corrida (movimiento 10361). Sin cambios en las transiciones.

### Catalogo cross-proyecto

| Item | Aplica | Resultado |
|---|---|---|
| LIP-001 / **ELV-003** (errores del Service invisibles al usuario) | si | **PASS — cerrado.** El detalle accionable llega a la pantalla en alta y en edicion, y el fallback de `Message` esta cubierto. |
| MH-013 / MH-024 / LP-001 / **ELV-005** (lo anulado contamina totales o se lee como dato real) | si | **PASS — cerrado.** Reproducido el escenario original y ya no aparece; la distincion `null` vs `0` se verifico con las dos poblaciones reales. |
| MH-015 / MH-018 / CRM-003 / **ELV-006** (columna ordenable que el servidor no sabe ordenar) | si | **PASS en la columna del lote, FAIL en la causa de fondo.** Ver "Observaciones": `Importe`, `Motivo`, `Tipo` y `Cuenta` siguen clickeables y siguen sin ordenar. |
| **ELV-007** (falsy 0 tratado como ausente en un render) | si | **PASS — cerrado**, con datos reales (1706/1707). |
| MH-025 (orden no determinista con filas de la misma fecha) | si, como regresion | **PASS.** 5.900 filas paginadas sin duplicar ni perder. |
| MH-008 (mensaje de error desactualizado) | si | **PASS.** Los textos nombran el valor real leido de la base (`4.875.825`, `4.843.132`, `196.985`, `537.074`, `6.259.649`). |
| ELV-001 (controllers sin `[Authorize]`) | si, como regresion de control | **PASS en el alcance.** Hubo que autenticarse para todo el ejercicio; `MaquinasController`, `MovimientosController` y `CuentasController` siguen protegidos. |
| ELV-002 (asimetria Create/Update) | si | **PASS en contadores:** `UpdateContadorAsync` y `CreateContadorAsync` comparten `ContadorValidator`, mismo criterio y mismo texto, verificado lado a lado. El item original (`FechaDevolucion` en `AlquilerService.UpdateAsync`) no se re-abrio en este lote. |

**Items nuevos agregados al catalogo en esta corrida: ninguno.** No aparecio ningun defecto nuevo.

### Cobertura de reglas nuevas/modificadas desde la ultima corrida

Ultima validacion registrada: **2026-10-01** (lotes A y B de esta misma fecha).
`git log --since=2026-10-01 -- .github/instructions/32-estandares-qa-implementador.instructions.md docs/qa/regresiones-manuales.yml`
→ **sin cambios**. No hay reglas agregadas ni modificadas que ejecutar de nuevo; vale el chequeo del lote A.

### Defectos

**Defectos nuevos introducidos por los fixes: ninguno.** No se emitio ningun parte de defecto en esta corrida.

**Estado de los defectos de las corridas anteriores:**

| Id | Severidad | Estado al cierre de esta corrida |
|---|---|---|
| ELV-003 | major | **CERRADO.** Re-verificado en contexto nuevo, criterio arrancado en FAIL, 4 casos PASS (alta, edicion contra anterior y contra siguiente, borde de `Errors` vacia, multi-error). |
| ELV-005 | major | **CERRADO.** Re-verificado reproduciendo el escenario original (ultimo movimiento anulado) y el caso de borde inverso (acumulado genuino 0), mas 2.950 filas de cruce SQL sin mismatch. |
| ELV-006 | minor | **CERRADO en la columna del lote** (`orderable: false` servido en las dos vistas). La causa de fondo queda abierta como item generico — ver "Observaciones". |
| ELV-007 | trivial | **CERRADO.** `0` se muestra como `0`, ausente como `—`, verificado con las 2 filas reales. |
| ELV-004 | major | **ABIERTO por decision.** Fuera del alcance de esta corrida por indicacion explicita del brief: preexistente, escalado al owner y deliberadamente sin corregir. **No se re-probo ni se toco.** |
| ELV-001 / ELV-002 | blocker / major | Sin cambios respecto de los lotes A y B: resueltos para los modulos probados, el barrido completo de los 13 controllers y la asimetria de `FechaDevolucion` siguen pendientes fuera de este alcance. |
| CA-F3.3 | — | **Cerrado como criterio**, anulado por el Analista (escenario inalcanzable, rama de fallback = codigo muerto). No es defecto abierto. |

### Observaciones (no son defectos de este lote, no se corrigieron)

1. **Causa de fondo de ELV-006 todavia abierta, ahora es el unico resto.** `GetDataTableAsync` sigue ignorando
   `sortColumn` para **todas** las columnas: `sortColumn=importeConSigno`, `motivoNombre` y `tipoMovimiento`
   devuelven los tres la misma secuencia, que es `Fecha` ascendente (`2828 (0007-05-07), 7105 (0053-06-03),
   3360 (2023-01-17), 63 (2023-01-27)`). `Importe`, `Motivo`, `Tipo` y `Cuenta` se siguen renderizando clickeables
   y siguen sin ordenar. El fix cerro la instancia que el lote A reporto, no la clase. **Decision para Analisis:**
   implementar el switch de `SortColumn` (conservando el `ThenBy(Id)` de F1 en **cada** rama) o poner
   `orderable: false` en las columnas restantes. Es recurrencia de MH-015/MH-018/CRM-003 y no lo introdujo este fix.
2. **El criterio de re-verificacion de ELV-005 quedo mal redactado y hay que reescribirlo.** Decia "`data[0].saldoAcumulado`
   del endpoint en orden descendente es exactamente igual al Saldo del encabezado". Con el fix aplicado, si la
   primera fila esta anulada `data[0].saldoAcumulado` es **`null`** y no puede ser igual al encabezado — y eso es
   justamente el comportamiento correcto. La redaccion correcta es la que se uso en esta corrida: *la primera fila
   **no anulada** coincide con el encabezado, y ninguna fila anulada devuelve 0*. Anotado para que la proxima
   corrida no lo lea como FAIL.
3. **El multi-error se concatena con un espacio simple** (`"…mayor o igual a 196.985 El contador color debe…"`),
   asi que los dos mensajes se leen como una sola frase corrida. Cosmetico, no pierde informacion; si se quiere
   mejorar, un separador (`" · "` o `"\n"`) en el `string.Join` alcanza. No se reporta como defecto.
4. **`DeleteContador` y las otras 9 ramas de error de `MaquinasController` siguen usando `result.Message` pelado.**
   Hoy ninguna de ellas produce `Errors` poblado, asi que no hay perdida de informacion observable. Vale como
   deuda: si alguna de esas operaciones empieza a devolver `Errors`, vuelve LIP-001. El helper ya existe.
5. **Preexistentes ya declarados en el lote A, sin cambio:** `recordsTotal` se calcula despues de los filtros de
   pantalla; hay datos migrados con fechas imposibles (`0007-05-07`, `0053-06-03`).

### Riesgos de liberacion

1. **Riesgo bajo en lo verificado.** Los 4 fixes son de presentacion o de mapeo, sin migracion EF y sin cambio de
   datos persistidos. **Nada que revertir en base** si hay que volver atras.
2. **ELV-004 sigue siendo el riesgo de mas peso del sprint** (medio-alto, preexistente): mientras
   `Maquinas/AjustarContadores` no tenga piso, la garantia de F5 cubre las inserciones y no las mutaciones.
   Decision pendiente del owner. **No bloquea este merge** por indicacion de alcance.
3. **Resto de ELV-006 (bajo).** Cuatro cabeceras siguen prometiendo un orden que el servidor no hace. Molesta,
   no corrompe. Conviene cerrarlo en el mismo pase que ya toco estas dos vistas, antes de que el cliente lo use.
4. **Sin observacion visual del navegador** (Playwright MCP no disponible). El unico punto donde pesa es la
   cabecera no clickeable y la grilla pintada: la config servida se verifico en el HTML y los dos renders se
   ejecutaron con node sobre el JS **servido**, pero no hay captura del DataTables renderizado.
5. **El lote se verifico sobre la base local real, no sobre produccion.** Produccion tiene las 110 filas de
   contadores en 0 (validacion prospectiva, decision de alcance) y, por lo que se observa en el clon, 0 anulados:
   el sintoma de ELV-005 nunca se hizo visible en produccion y ahora no puede hacerse.

### Checklist de merge (lote C)

- [x] `dotnet build Eleven.slnx` → "Compilación correcta", 0 errores.
- [x] ELV-003 re-verificado leyendo el mensaje **en pantalla**: alta, edicion contra anterior y contra siguiente,
      multi-error, borde de `Errors` vacia y happy path.
- [x] ELV-005 re-verificado reproduciendo el escenario original (movimiento 10361 anulado por el endpoint real) y
      el caso de borde inverso (10 filas con acumulado genuino 0 en la cuenta 1 → `$ 0,00`).
- [x] Running sum re-corrido en SQL sobre 2.950 filas (cuentas 1 y 12): 0 mismatch.
- [x] ELV-006 / ELV-007 verificados sobre el **HTML servido** de las dos vistas + render ejecutado con node.
- [x] Alineacion thead / `columns` de DataTables: 8/8 y en el mismo orden en las dos grillas.
- [x] Regresion de paginacion ida y vuelta: 4 barridos, 5.900 filas, 0 duplicadas, 0 faltantes.
- [x] Regresion del alta de alquiler (fix H1): rechazo con minimo + alta valida + historial 114 → 115.
- [x] Sin migracion EF en los 4 fixes.
- [x] Base real local intacta (10.396 movimientos, 0 anulados, 152 cuentas, 114 contadores en M60, 0 marcas
      `QA-LOTE-C`); clon `eleven_qa_c` eliminado; produccion sin tocar.
- [x] `git status --porcelain` del repo del sistema **identico al del arranque**, sin ningun residuo de QA
      (`Eleven.Web/keys/` generado por Data Protection eliminado).
- [ ] **ELV-004: decision del owner** (validar el ajuste, restringir por rol, o aceptar el riesgo por escrito).
- [ ] **Resto de ELV-006 al Implementador**: `orderable: false` en las columnas restantes, o el switch de
      `SortColumn` con `ThenBy(Id)` en cada rama.

---

## QA - Lote 2026-10-01 B: Contadores (F5)

**Fecha de corrida:** 2026-10-01 - **Rama:** dev, cambios sin commitear - **Veredicto: GO condicionado** (merge habilitado; ELV-003 queda como defecto abierto a corregir en el mismo sprint).

### Metodo de verificacion (evidencia real, no lectura de codigo)

- MCP de Playwright **no disponible** en la sesion (no hay herramientas `mcp__playwright__*`). Se cubrio por los dos caminos del metodo del estudio: runner de consola y HTTP con `curl` + cookie jar.
- Base de trabajo `eleven_qa_b`, clon completo de la base de desarrollo local `eleven` (6.076 contadores activos, 40 en 0). **Eliminada al cerrar la corrida.** Produccion no se toco.
- Runner de consola fuera del repo (`scratchpad/qaf5`), referencia `Eleven.Infrastructure.csproj` e instancia `MaquinaService` / `AlquilerService` directamente: 17 asserts, **15 PASS / 2 FAIL** (los 2 FAIL son los agujeros, ver abajo).
- App levantada en `http://localhost:5199` contra `eleven_qa_b`, login real por HTTP con usuario **rol Tecnico**, y POST a los endpoints reales (`/Maquinas/CreateContador`, `/Alquileres/Create`, `/Maquinas/AjustarContadores`) leyendo el mensaje servido en el HTML.
- Fixtures: **M143** y **M60** (B/N, historial largo), **M347** (`Color=true`, 41 contadores), **M371 / M447** (sin contadores).

### Cobertura por criterio de aceptacion

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| CA-F5.1 - alta: rechaza menor al ultimo anterior; igual o mayor acepta | **PASS** | M143 (ultimo 4.875.825): `BN=0` -> `Success=False`, error `"El contador B/N debe ser mayor o igual a 4.875.825"`. `BN=4.875.825` -> acepta. `BN=5.100.000` -> acepta. |
| CA-F5.2 - misma validacion en edicion, tambien contra el siguiente | **PASS** | Editar el contador de M143 sin cambiarle el valor -> `"Contador actualizado exitosamente."` (`excludeId` funciona). Editarlo por encima del siguiente (5.100.000) -> `"El contador B/N debe ser menor o igual a 5.100.000"`. |
| CA-F5.3 - misma regla en el alta de alquiler | **PASS** | Alta de alquiler M60 con `ContadorBNInicial=0` -> rechazada por HTTP con `"El contador B/N debe ser mayor o igual a 6.259.649"`. Alta normal (ultimo + 500) -> `"Alquiler creado exitosamente."` y el historial paso de 99 a 100 filas: `AgregarHistoriaContadorSiCorresponde` del fix H1 sigue generando el contador inicial. **Sin regresion sobre H1.** |
| CA-F5.4 - maquina sin contadores acepta cualquier valor, 0 incluido | **PASS** | M371 (0 contadores): `BN=0` -> `"Contador registrado exitosamente."`. Alquiler sobre M447 (0 contadores) con inicial 0 -> `"Alquiler creado exitosamente."`. |
| CA-F5.5 - el color se valida solo si `Color = true` | **PASS** | M143 (`Color=false`): contador con `Color=0` y BN valido -> acepta, ningun error de color. M347 (`Color=true`, ultimo color 537.074): BN valido y `Color=0` -> `"El contador color debe ser mayor o igual a 537.074"`. |
| CA-F5.6 - el mensaje nombra el minimo con separador de miles | **FAIL en pantalla** / PASS en el Service | El formato `N0` es-AR es correcto (`4.875.825`, `6.259.649`, `537.074`), pero en la **carga manual de contadores** ese texto no llega a la pantalla: el usuario ve solo `"Error en la validacion de contadores"`. Ver **ELV-003**. |

### Pruebas funcionales de Arquitectura (7 a 12) y casos de borde

| # | Caso | Resultado |
|---|---|---|
| 7 | ultimo contador: 0 rechaza nombrando el minimo / igual acepta / mayor acepta | PASS (con M143, ultimo 4.875.825) |
| 8 | maquina sin contadores: 0 acepta | PASS |
| 9 | editar sin cambiar el valor guarda (`excludeId`) | PASS |
| 10 | editar por encima del siguiente rechaza | PASS |
| 11 | maquina B/N: el color no se valida | PASS |
| 12 | alta de alquiler: inicial regresivo rechaza / alta normal igual que antes | PASS (verificado por HTTP y por conteo de filas del historial) |
| B1 | insercion **retroactiva** en el medio del historial (anterior 4.863.489 / siguiente 4.875.825) | PASS: 0 rechaza contra el anterior, `siguiente+1` rechaza contra el siguiente, valor intermedio acepta. **Valida contra los adyacentes de esa fecha, no contra el ultimo absoluto.** |
| B2 | valor negativo (`BN=-5`) sobre maquina con un 0 previo | PASS: rechaza con `"debe ser mayor o igual a 0"` |

### Respuesta a la pregunta del brief: queda algun camino para insertar un contador en 0 regresivo?

**Los dos caminos de INSERCION estan cerrados.** Son los unicos del sistema (`MaquinaService.CreateContadorAsync` y `AlquilerService.AgregarHistoriaContadorSiCorresponde`; el `Migration-Legacy` esta excluido de la compilacion por `Compile Remove="Migration-Legacy\**"`). Los dos pasan por `ContadorValidator`.

**Queda abierto un camino de MUTACION, y es el hallazgo del lote: `Maquinas/AjustarContadores` (ELV-004).** No inserta, pero deja contadores en 0 o negativos sin pasar por la validacion, que es exactamente el dano que F5 vino a impedir. Reproducido por HTTP como **rol Tecnico**: `cantidadAjustar=-99999999` sobre M6 respondio 302 con `"Contadores e insumos ajustados correctamente."` y los **68 contadores de la maquina quedaron en negativo** (minimo -99.462.104). La UI lo invita explicitamente: el prompt dice *"Ingrese la cantidad a ajustar (puede ser negativo)"*.

Camino menor, de riesgo bajo: borrar (soft delete) todo el historial de una maquina y cargar 0 queda aceptado, porque sin historial activo rige CA-F5.4. Es coherente con la regla acordada y requiere una accion deliberada por fila; se deja declarado, no se reporta como defecto.

### Defectos y partes de defecto emitidos

**ELV-003 - major - Maquinas / Historia de Contadores (alta y edicion) - ABIERTO, parte emitido al Implementador.**
El controller descarta `result.Errors` y manda solo `result.Message` al `TempData`, asi que el minimo nunca llega a la pantalla. Asimetria probada lado a lado sobre la **misma maquina y el mismo dato**: Alquileres muestra `"El contador B/N debe ser mayor o igual a 6.259.649"`, la carga manual muestra `"Error en la validacion de contadores"`.
Hipotesis de fix: `Eleven.Web/Controllers/MaquinasController.cs`, componer el `TempData["ErrorMessage"]` con `result.Errors` igual que hace `AlquileresController`. Sin migracion EF.
Criterio de re-verificacion: POST a `/Maquinas/CreateContador` con `BN=0` sobre una maquina con historial, y el HTML del `Details` siguiente contiene el minimo con separador de miles.

**ELV-004 - major - Maquinas / Ajustar Contadores - ABIERTO, fuera del alcance de F5, escalado al analista/owner.**
Preexistente, no lo introdujo este lote, pero anula su intencion.
Hipotesis de fix: validar en `AjustarContadoresAsync` que ningun contador quede bajo 0 antes del `SaveChanges`, y decidir si el endpoint debe exigir rol administrativo (hoy solo tiene `[Authorize]` de clase).
Criterio de re-verificacion: POST a `/Maquinas/AjustarContadores` con `cantidadAjustar` negativo que llevaria algun contador bajo 0 -> rechazo con detalle, y `select sum(ContadorBN<0) from Contadores where MaquinaId=<m>` devuelve 0.

No se reportaron como defectos las tres decisiones cerradas del brief (regla `>=` y no `> 0`; `AgregarHistoriaContadorSiCorresponde` sin tocar; validacion prospectiva sobre las 110 filas en 0 existentes). Las 110 filas siguen ahi, como estaba previsto.

### Catalogo cross-proyecto

| id | aplica | resultado |
|---|---|---|
| ELV-002 (asimetria Create/Update) | si | **Cubierto por F5 en contadores:** el `Update` ahora aplica el mismo criterio que el `Create` y con el mismo texto. El item original (FechaDevolucion en `AlquilerService.UpdateAsync`) sigue abierto, fuera de este lote. |
| LIP-001 (errores del Service invisibles al usuario) | si | **FAIL - variante nueva.** Aca el error se ve pero truncado, perdiendo justo el dato accionable. Registrado como **ELV-003**. |
| MH-008 (mensaje de error desactualizado) | si | PASS: los textos nombran el valor real leido de la base, no una lista hardcodeada. |
| ELV-001 (controllers sin `[Authorize]`) | si | PASS en el alcance: `MaquinasController` tiene `[Authorize]` de clase. Observacion derivada en ELV-004: `[Authorize]` sin rol deja el ajuste masivo al alcance de cualquier usuario autenticado. |

Items nuevos agregados al catalogo cross-proyecto en esta corrida: **ELV-003** y **ELV-004** (`docs/qa/regresiones-manuales.yml` + `docs/qa/cat_resumen.txt`, YAML validado).

### Cobertura de reglas nuevas/modificadas desde la ultima corrida

El chequeo de reglas cross-proyecto de esta corrida corresponde al **lote 1 (lote A, Finanzas)**, segun la mecanica de una vez por corrida. Este lote reutiliza su resultado. La ultima validacion registrada en este archivo era del **2026-08-20** (ciclo H1).

### Riesgos de liberacion

1. **ELV-003 (medio).** La validacion rechaza bien pero no le dice al operador contra que valor rebota. En la carga diaria de contadores eso se traduce en reintentos a ciegas y, muy probablemente, en un pedido de soporte. Es el unico defecto propio del lote y se arregla en el controller, sin tocar la validacion.
2. **ELV-004 (medio-alto, preexistente).** Mientras el ajuste masivo siga sin piso, la garantia que da F5 es parcial: se cierran las inserciones, no las mutaciones.
3. **Riesgo bajo de regresion sobre H1.** La validacion cambio de archivo pero no de comportamiento: alta de alquiler normal y alta con inicial regresivo se verificaron por HTTP con el resultado esperado, y `AgregarHistoriaContadorSiCorresponde` sigue generando el historial inicial (99 -> 100 filas).
4. **Sin migracion EF** en el lote: nada que revertir en base si hay que volver atras.

### Checklist de merge (lote B)

- [x] Los 6 criterios de aceptacion ejercitados con datos reales; 5 PASS, CA-F5.6 PASS en el Service y FAIL en pantalla (ELV-003).
- [x] Pruebas funcionales 7 a 12 de Arquitectura: PASS.
- [x] Caso de borde de insercion retroactiva: PASS (valida contra los adyacentes de la fecha).
- [x] Regresion del fix H1 (alta de alquiler) verificada por HTTP: sin cambio de comportamiento.
- [x] Compila sin errores (build implicito en la ejecucion del runner y el arranque de la app).
- [x] Base de trabajo `eleven_qa_b` eliminada; produccion sin tocar.
- [x] `git status --porcelain` del repo del sistema sin ningun cambio de QA: los 7 archivos del lote estan igual que al arranque. El `Eleven.Web/keys/` que genero el arranque de mi app se elimino; reaparecio a las 11:30 por el proceso `Eleven.Web` del lote A, que seguia corriendo (untrackeado y generado, no es un cambio de codigo).
- [ ] **ELV-003 corregido y re-verificado en corrida nueva** (no se cierra en la misma corrida que lo encontro).
- [ ] **ELV-004 decidido por el owner** (validar el ajuste, restringir por rol, o aceptar el riesgo por escrito).

---

## QA — Lote 2026-10-01 A: Finanzas (F1-F4)

**Fecha de corrida:** 2026-10-01 · **Rama:** dev (cambios sin commitear) · **Alcance:** F1 (desempate por `Id` en
`MovimientoService.GetDataTableAsync`), F2 (Egreso preseleccionado), F3 (redirect al detalle de la cuenta origen),
F4 (columna Nro. Comprobante). F5/contadores corrio en el lote B, en paralelo, y no se toca aca.

**Ultima validacion de reglas cross-proyecto: 2026-10-01** (reemplaza al 2026-08-20 del ciclo H1).

**Veredicto: GO para el merge del lote A**, con ELV-005 abierto como condicion para dar F1 por terminado.

### Entorno y metodo de ejecucion

- **Base:** clon `eleven_qa_a` de la base local real `eleven` (10.396 movimientos, 152 cuentas), creado y
  **eliminado al cerrar**. Base real verificada intacta: 10.396 movimientos, 152 cuentas, 0 filas con marca
  `QA-LOTE-A%`, 0 anulados. **Produccion no se toco en ningun momento.**
- **App:** levantada localmente (`dotnet run --no-build`, `http://localhost:5291`) apuntando al clon por
  **variable de entorno** `ConnectionStrings__DefaultConnection` — el repo del sistema no se edito.
  Build previo: `dotnet build Eleven.slnx` -> "Compilación correcta", 0 errores, 8 warnings NU1902
  preexistentes (MailKit/MimeKit).
- **Playwright MCP: NO disponible en la sesion** (las herramientas `mcp__playwright__*` no se cargaron;
  verificado por busqueda de herramientas). Declarado segun `33-verificacion-automatizada-qa`. Se sustituyo por
  **ejercicio HTTP real** de la app autenticada (login real con antiforgery y cookie de sesion), lectura del
  HTML servido, llamadas reales a `POST /Movimientos/GetDataTable`, contraste en base por SQL y ejecucion del
  render JS del view con `node`. Lo unico sin observacion es el pixel que pinta DataTables en el navegador.

### Cobertura por criterio de aceptacion

| Criterio | Resultado | Evidencia observada |
|---|---|---|
| CA-F1.1 (desempate por Id, desc y asc) | **PASS** | Cuenta 12, 26/06/2023, 22 movimientos el mismo dia. desc: `1342, 1339, 1336, ..., 1259`. asc: `1259, 1262, ..., 1342`. Secuencias exactamente inversas: Id mas alto arriba en desc, mas bajo arriba en asc. |
| CA-F1.2 (acumulado de la 1ra fila == saldo del encabezado) | **PASS** | 3 cuentas: c1 header `$ 1.295.200,00` vs fila 10396 `acum=1295200.0`; c11 `$ 791.071,73` vs 10345 `791071.73`; c12 `$ 59.419.538,03` vs 10361 `59419538.03`. Re-verificado tras dar de alta 5 movimientos (incluida una transferencia): c11 `$ 792.571,73` vs `792571.73`; c12 `$ 59.415.638,47` vs `59415638.47`. **Condicionado por ELV-005.** |
| CA-F1.3 (no altera importes ni acumulados) | **PASS** | Cuenta 12 completa (911 filas) comparada fila por fila contra un running sum calculado aparte en SQL (`SUM(...) OVER (ORDER BY Fecha, Id)`): **0 filas** con importe o acumulado distinto, y el orden del API coincide 1:1 con el orden SQL `(Fecha, Id)`. |
| CA-F2.1 (abre en Egreso) | **PASS** | `GET /Movimientos/Create?cuentaId=12` -> 200; HTML servido: `<option selected="selected" value="1">Egreso</option>`, y `CuentaId` preseleccionada en 12 (`La Cardeusse`). Idem sin `cuentaId`. |
| CA-F2.2 (se puede cambiar, sin validacion nueva) | **PASS** | Las tres opciones presentes y habilitadas. POST con `TipoMovimiento=0` (Ingreso) -> 302 y persistio `TipoMovimiento=0` (movimiento 10398). POST con `TipoMovimiento=2` (Transferencia) -> 302 (10401/10402). |
| CA-F2.3 (`CreateUnificado` sin cambios) | **PASS** | `GET /Movimientos/CreateUnificado?cuentaId=7&tipoCuentaCorriente=1` -> 200. Usa `MovimientoUnificadoCreateViewModel` y **no tiene campo `TipoMovimiento`** (campos servidos: CuentaCorrienteId, CuentaDestinoId, Dolares, Fecha, ImporteCuenta, ImporteFactura, Notas, NumeroComprobante, TipoCuentaCorriente). El default de Egreso no puede alcanzarlo; el diff no lo toca. |
| CA-F3.1 (vuelve al detalle de esa cuenta) | **PASS** | POST egreso con `CuentaId=12` -> `302 -> http://localhost:5291/Cuentas/Details/12`. Idem ingreso. |
| CA-F3.2 (movimiento visible y mensaje de exito ahi) | **PASS** | Siguiendo el redirect en la misma cadena de cookies, `/Cuentas/Details/12` -> 200 con `Swal.fire({ icon: 'success', title: 'Exito', text: 'Egreso registrado exitosamente.' })`, el movimiento como primera fila (10400, 2026-04-03) y el saldo del encabezado ya actualizado. |
| CA-F3.3 (sin cuenta de contexto, vuelve al listado) | **BLOCKED** | **No es alcanzable.** Con `CuentaId=0` el POST devuelve 200 (vuelve al form) con el error del servicio `"La cuenta seleccionada no existe."`; `[Required]` sobre un `int` no dispara para 0, asi que el `ModelState` es valido y el rechazo viene del servicio. Entonces `result.Success` implica `vm.CuentaId > 0` y la rama `RedirectToAction(nameof(Index))` es **codigo muerto**: no existe forma de crear un movimiento sin cuenta. El criterio describe un escenario inexistente. Vuelve a Analisis. |
| CA-F3.4 (transferencia vuelve al origen) | **PASS** | POST transferencia 12 -> 11: `302 -> /Cuentas/Details/12` (origen). En base: 10401 (CuentaId=12, Egreso) + espejo 10402 (CuentaId=11, Ingreso, `MovimientoOrigenId=10401`). |
| CA-F4.1 (las grillas muestran Nro. Comprobante) | **PASS** | HTML servido de `/Cuentas/Details/12`: TH = `Fecha, Nro. Comprobante, Tipo, Motivo, Notas, Importe, Saldo Acumulado, Acciones` (8) y 8 entradas en `columns`. `/Movimientos`: TH = `Fecha, Nro. Comprobante, Cuenta, Tipo, Motivo, Notas, Importe, Acciones` (8) y 8 columnas. **8/8 en las dos** — sin desalineacion thead/columns. El endpoint devuelve `numeroComprobante` en el JSON. |
| CA-F4.2 (sin comprobante muestra guion gris) | **PASS (con reserva de render visual)** | El JSON devuelve `numeroComprobante: null` para 10398 y valores para 10397/10399/10400. Render del view ejecutado con node: `null -> <span class="text-muted">&mdash;</span>`, `99001 -> 99001`. Sin Playwright no hay captura del pixel. **Con el defecto ELV-007:** el `0` tambien cae en el guion. |
| CA-F4.3 (el filtro por comprobante sigue funcionando) | **PASS** | `POST /Movimientos/GetDataTable?cuentaId=12&numeroComprobante=99001` -> `recordsFiltered=1`, unica fila `(10397, 99001)`. |

### Prueba prioritaria de Arquitectura: paginacion sin orden total

Es la parte de mayor valor del lote. Barrido completo de paginas hacia adelante y relectura de las mismas
paginas hacia atras, contra el endpoint real, 3 cuentas x 2 direcciones, paginas de 200:

| Cuenta | Dir | Total | Leidas | Unicas | Duplicadas | Faltantes | Ida == vuelta |
|---|---|---|---|---|---|---|---|
| 1 | desc | 2039 | 2039 | 2039 | 0 | 0 | si |
| 1 | asc | 2039 | 2039 | 2039 | 0 | 0 | si |
| 11 | desc | 1039 | 1039 | 1039 | 0 | 0 | si |
| 11 | asc | 1039 | 1039 | 1039 | 0 | 0 | si |
| 12 | desc | 911 | 911 | 911 | 0 | 0 | si |
| 12 | asc | 911 | 911 | 911 | 0 | 0 | si |

**7.978 filas paginadas, 0 duplicadas, 0 perdidas, orden identico en ida y vuelta.** El `Skip/Take` quedo
determinista. **PASS.**

### Maquina de estados

`Movimiento` no tiene enum de estado. Estados implicitos: Vigente (`DeletedAt == null && !Anulado`) ->
Anulado (`MovimientoService.AnularAsync`, expuesto en `MovimientosController.Anular`) -> Eliminado (soft
delete). **Hallazgo:** el conjunto que la grilla lista (`DeletedAt == null`, por el query filter global) y el
conjunto que suman el acumulado y `Cuenta.Saldo` (`DeletedAt == null && !Anulado`) **no son el mismo**; esa
asimetria es ELV-005. Las transiciones no se modificaron en este lote.

### Cobertura del catalogo cross-proyecto

| Item | Aplica | Resultado |
|---|---|---|
| MH-025 (orden no determinista con filas de la misma fecha) | si — es exactamente la clase de bug que F1 remedia | **PASS**: el orden ahora es total `(Fecha, Id)`, verificado fila por fila contra SQL. |
| DN-001 / DN-002 (Include de coleccion + OrderBy dinamico + Skip/Take -> NRE al paginar) | parcial | **PASS / no aplica**: los `Include` son navegaciones de referencia (`Cuenta`, `CuentaDestino`, `Motivo`), no colecciones. 7.978 filas paginadas sin excepcion ni fila perdida. |
| MH-015 / MH-018 / CRM-003 (columna ordenable que el servidor no sabe ordenar) | **si** | **FAIL -> ELV-006.** Reproducido: `sortColumn=numeroComprobante` devuelve orden por Fecha. |
| MH-013 / MH-024 / LP-001 (lo anulado contamina totales o se lee como dato real) | **si** | **FAIL -> ELV-005.** Reproducido con el ultimo movimiento de la cuenta anulado. |
| OLV-016 (el aviso de exito nunca aparece porque solo se calcula en la rama de validacion fallida) | si — F3 cambia el destino del redirect | **PASS**: el toast de exito se observo en el destino del redirect. |
| OLV-007 (`data-select2` rompe la init de la grilla) | no | No hay `data-select2` ni Select2 en las dos vistas tocadas. |
| LP-004 (el buscador global se pierde por carreras de Session) | no | Estas grillas no guardan el search en Session. |
| MH-014 (desfase de un dia por UTC en una columna nueva) | no | La columna nueva es numerica, no una fecha. |
| MH-017 (filtro sin la columna correspondiente) | no | F4 agrega justamente la columna del filtro que ya existia: cierra la asimetria en vez de abrirla. |
| ELV-001 (blocker de autorizacion del ciclo H1) | si, como regresion de control | **Resuelto para estos modulos**: `MovimientosController` y `CuentasController` llevan `[Authorize(Policy = "RequireAdministracion")]`; sin cookie, `/Cuentas` devuelve 302 al login y hubo que autenticarse para todo el ejercicio. El barrido de los 13 controllers no se hizo en este lote. |

### Cobertura de reglas nuevas/modificadas desde la ultima corrida (2026-08-20)

Chequeo de la corrida (se hace una vez, en el lote 1 = este). Se comparo el estado vigente contra la fecha de
la ultima validacion, con `git log --since=2026-08-20` sobre
`.github/instructions/32-estandares-qa-implementador.instructions.md` y `docs/qa/regresiones-manuales.yml`.
Entre esa fecha y hoy se agregaron ~58 items (MH-012 a MH-041, LP-003 a LP-005, LIP-001, CRM-015/016/023,
GAN-005/006, DN-003/004, KOI-009 a KOI-017, OLV-001 a OLV-027) mas la instruccion 38. De ese conjunto, los
que tienen superficie en este lote son los de la tabla anterior y **se ejecutaron todos contra el sistema**.
El resto pertenece a modulos que este lote no toca (comprobantes AFIP, multi-tenant, portal del cliente,
proyeccion financiera, auditoria de consistencia) y queda como dato para los lotes siguientes, no como
cobertura declarada. El lote B reutiliza este resultado.

### Defectos y partes de defecto emitidos

**No se aplico ningun parche:** el repo del sistema es read-only para QA. Los tres defectos quedan catalogados
en `docs/qa/regresiones-manuales.yml` + `docs/qa/cat_resumen.txt` (YAML validado) con pasos, evidencia
observada, `archivos_fix` como hipotesis, `migracion_ef: null` y criterio de re-verificacion.

| Id | Severidad | Titulo | Lo introdujo este lote? |
|---|---|---|---|
| ELV-005 | **major** | Una fila anulada muestra Saldo Acumulado 0,00; si es el ultimo movimiento de la cuenta, el acumulado de la primera fila deja de coincidir con el saldo del encabezado | **No** (preexistente), pero **invalida la garantia que F1 viene a dar**. Reproducido: cuenta 12 con el movimiento 10401 marcado `Anulado=1` -> header `$ 59.417.138,47` y primera fila en desc `saldoAcumulado = 0`. Causa: `GetDataTableAsync` no filtra `Anulado` (el query filter global es solo `DeletedAt == null`), `GetSaldosAcumuladosAsync` si lo excluye, y `GetValueOrDefault` devuelve `0m` para la clave ausente en vez de null. Hoy la base real tiene 0 anulados, asi que no es visible — y la accion Anular esta expuesta en la UI. |
| ELV-006 | minor | `Nro. Comprobante` se renderiza ordenable pero el servicio ignora `sortColumn` y ordena siempre por Fecha | **Si en esa columna** (la causa de fondo es preexistente y afecta a todas las columnas ordenables de las dos grillas). Recurrencia de MH-015/MH-018/CRM-003. Reproducido: `sortColumn=numeroComprobante&sortDirection=asc` devuelve `2828 (0007-05-07), 7105 (0053-06-03), 3360 (2023-01-17), 63/66/73 (2023-01-27)`, todos con comprobante null: es Fecha ascendente. |
| ELV-007 | trivial | `NumeroComprobante = 0` se muestra como guion gris igual que un comprobante ausente | **Si.** El render usa `data \|\|`, falsy para 0. Ejecutado con node: `f(null) -> guion`, `f(0) -> guion`, `f(99001) -> 99001`. Hay 2 filas reales afectadas: movimientos 1706 y 1707, cuenta 120. |

**Criterios de re-verificacion** (arrancan en FAIL en la proxima corrida, en contexto nuevo):

- **ELV-005:** con el ultimo movimiento de una cuenta anulado, `data[0].saldoAcumulado` del endpoint en orden
  descendente sin filtros es exactamente igual al Saldo del encabezado, y ninguna fila con `anulado=true`
  devuelve `saldoAcumulado = 0`.
- **ELV-006:** `sortColumn=numeroComprobante` ordena por comprobante, o la columna no es clickeable. Si se
  implementa el switch de `SortColumn`, **cada rama** debe conservar el `ThenBy(Id)` de F1 o vuelve el riesgo
  de `Skip/Take` sin orden total.
- **ELV-007:** una fila con `NumeroComprobante = 0` muestra `0`; una sin comprobante muestra el guion.

**Estado de los defectos de la corrida anterior:** ELV-001 (blocker de autorizacion) **cerrado para los
modulos de este lote** — `[Authorize]` presente y verificado por 302 al login sin cookie; el barrido completo
de los 13 controllers sigue pendiente. ELV-002 (asimetria `FechaDevolucion` Create/Update en
`AlquilerService`) **fuera de este lote** — ese archivo lo toca el lote B.

**Decisiones cerradas del brief que no se reportaron como defectos:** F4 sobre 2 vistas y no 3
(`Clientes/Details` linkea a `/Cuentas/Details/{id}`, misma grilla); desempate por `Id` y no por `CreatedAt`;
`Movimientos/Index` sigue existiendo a proposito.

### Observaciones fuera de alcance (no son defectos de este lote, no se corrigieron)

- `recordsTotal` del endpoint se calcula **despues** de aplicar los filtros de pantalla (solo excluye el search
  box), asi que con un filtro activo informa el total filtrado y no el total de la cuenta. Semanticamente no es
  lo que DataTables espera; hoy no cambia nada visible. Preexistente.
- Datos migrados con fechas imposibles: el movimiento mas antiguo de la cuenta 12 tiene `Fecha = 0007-05-07`
  y otro `0053-06-03`. Preexistente y ajeno al lote, pero ensucia cualquier orden o rango por fecha.

### Riesgos de liberacion

1. **ELV-005 es el riesgo real del lote.** F1 se vende como "el acumulado de la primera fila coincide con el
   saldo de la cuenta", y eso deja de valer en cuanto alguien anule un movimiento. La ventana esta abierta
   (0 anulados hoy, pero Anular esta en la UI) y el sintoma — un saldo de $0,00 arriba de una cuenta con
   millones — es la clase de pantalla que hace desconfiar de todo el modulo. Mitigacion: cerrar ELV-005 en el
   ciclo inmediato siguiente, o avisar al cliente que no use Anular hasta entonces.
2. **CA-F3.3 describe un escenario inexistente.** No es un bug, pero deja una rama de codigo que nadie puede
   ejercitar y un criterio que no se puede verificar; toda corrida futura lo va a volver a marcar BLOCKED.
   Decidir con Analisis: reescribir el criterio o sacar la rama.
3. **`Movimientos/Index` queda sin camino de llegada.** Ya no se aterriza ahi al guardar y no tiene entrada por
   menu. Es decision cerrada, pero conviene confirmar con el cliente que no la usaba como listado de control.
4. **Lote B en paralelo.** Durante esta corrida aparecio `Eleven.Web/Controllers/MaquinasController.cs`
   modificado, ajeno a este lote. El veredicto cubre **solo** F1-F4; el merge conjunto depende tambien del
   lote B.
5. **Sin observacion visual del navegador** (Playwright MCP no disponible). El unico punto donde pesa es el
   render de la columna nueva: la alineacion thead/columns se verifico 8/8 en el HTML servido y el render se
   ejecuto con node, pero no hay captura de la grilla pintada.

### Veredicto GO / NO-GO

- **F1 (desempate por Id): GO.** Es el cambio de mas valor del lote y el mejor verificado: 7.978 filas
  paginadas sin duplicar ni perder, orden total confirmado fila por fila contra SQL, acumulados intactos.
  Con la salvedad de que su promesa funcional queda incompleta hasta ELV-005.
- **F2 (Egreso preseleccionado): GO.** CA-F2.1 a CA-F2.3 PASS, sin tocar `CreateUnificado`.
- **F3 (redirect al detalle de la cuenta origen): GO con reserva.** CA-F3.1, CA-F3.2 y CA-F3.4 PASS con
  evidencia HTTP. CA-F3.3 BLOCKED por criterio no testeable: no bloquea el merge, bloquea el cierre del criterio.
- **F4 (columna Nro. Comprobante): GO con dos defectos abiertos** (ELV-006 minor, ELV-007 trivial). Ninguno
  pierde ni corrompe datos; los dos son de presentacion.
- **Merge del lote A a dev: GO.** Ningun defecto introducido por el lote supera severidad minor, y nada de lo
  que el lote toca empeora el estado previo.
- **Publicacion a produccion: condicionada a ELV-005.** No es blocker de merge; si es blocker de "F1 esta
  terminado". Decision del owner.

### Checklist de merge (lote A)

- [x] `dotnet build Eleven.slnx` -> "Compilación correcta", 0 errores.
- [x] CA-F1.1, CA-F1.2 y CA-F1.3 verificados con ejecucion real contra el endpoint y contraste SQL independiente.
- [x] Prueba prioritaria de paginacion ida y vuelta: 6 barridos, 7.978 filas, 0 duplicadas, 0 faltantes.
- [x] CA-F2.1 a CA-F2.3 verificados sobre el HTML servido y con altas reales persistidas.
- [x] CA-F3.1, CA-F3.2 y CA-F3.4 verificados por redirect HTTP real + toast de exito en el destino.
- [x] CA-F4.1 y CA-F4.3 verificados; CA-F4.2 verificado salvo el pixel renderizado.
- [x] Alineacion thead / `columns` de DataTables: 8/8 en las dos grillas.
- [x] Sin migracion EF (no hay cambios de entidad ni de configuracion en el lote).
- [x] Base real local intacta (10.396 movimientos, 152 cuentas, 0 marcas QA); clon `eleven_qa_a` eliminado.
- [x] `git status --porcelain` del repo del sistema sin residuos de QA: se borro el `Eleven.Web/keys/` que
      genero Data Protection al levantar la app; los archivos modificados son los del lote A y los del lote B.
- [ ] **CA-F3.3: decidir con Analisis** — reescribir el criterio o sacar la rama muerta del redirect.
- [ ] **ELV-005 agendado** antes de dar F1 por terminado y antes de publicar.
- [ ] **ELV-006 y ELV-007** al Implementador (presentacion, pueden ir en el mismo pase).
- [ ] **Veredicto del lote B** (contadores / F5) antes del merge conjunto.
