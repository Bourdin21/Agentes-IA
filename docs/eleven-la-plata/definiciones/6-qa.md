# Memoria - QA

## Proyecto: eleven-la-plata
## Ultima actualizacion: 2026-08-20

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
- 2026-08-20: Primer ciclo de QA formal del proyecto. Validacion de H1 (fix de contadores en
  `AlquilerService.UpdateAsync`): 7/7 casos PASS, sin defectos en el alcance del cambio. Se detectaron 2
  defectos preexistentes fuera del alcance (ELV-001 blocker de autorizacion, ELV-002 asimetria Create/Update
  en FechaDevolucion), ambos catalogados en el playbook cross-proyecto y escalados sin auto-fix. Playwright MCP
  no disponible en la sesion: se sustituyo por harness de ejecucion contra clon de base + ejercicio HTTP real
  de la app levantada localmente.
