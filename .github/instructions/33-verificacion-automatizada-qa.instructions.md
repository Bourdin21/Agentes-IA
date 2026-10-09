---
description: Metodologia de verificacion automatizada por navegador para el agente QA. Cierra el punto ciego de "nadie ejecuta la app antes de la entrega" detectado 2026-08-14.
applyTo: "**"
---

# 33 - Verificacion automatizada QA (obligatoria desde 2026-08-14)

## Motivo de esta instruccion

Hasta esta fecha, ni el Implementador ni el QA ejecutaban la aplicacion — el Implementador por diseño (separacion de roles, ver `00-operativa-global.instructions.md`), y el QA por una restriccion explicita ("no automatizar UI"). Resultado: la verificacion funcional real dependia 100% de que el usuario/cliente ejecutara a mano la guia de pasos, sin ningun paso automatizado que atajara los patrones de bug ya conocidos (`32-estandares-qa-implementador.instructions.md`) antes de la entrega. Se corrige acotando la automatizacion al agente QA (el Implementador sigue sin ejecutar nada, mantiene su rol de "solo escribe").

## Que se automatiza (obligatorio para el agente QA)

1. **Items del catalogo `docs/qa/regresiones-manuales.yml` con `deteccion_qa.tipo: ui`**: reproducir los `pasos` del item contra el sistema real (levantar la app localmente) y evaluar `condicion_falla` sobre el resultado observado, no sobre una descripcion.
2. **Patrones de `32-estandares-qa-implementador.instructions.md`**, chequeables como assertions objetivas sin juicio subjetivo:
   - Combo de Editar con relacion ya cargada → debe mostrar los valores seleccionados, no vacio.
   - Botones de accion visibles en una pantalla de detalle/listado → deben coincidir exactamente con las transiciones validas reales del estado actual (ni de mas ni de menos).
   - Cualquier listado nuevo/modificado con DataTable server-side → carga sin error 500, con al menos un filtro funcional.
   - Todo link de sidebar agregado/modificado → el usuario sin el rol correspondiente recibe 403/oculto, el usuario con el rol accede 200.
   - Formulario dinamico (grilla de pagos, detalle de venta) → escribir en un campo no debe perder el foco tras el recalculo.
   - Venta con pago dividido en multiples medios (ver "Venta con IVA + pago dividido en multiples metodos" en `32-estandares-qa-implementador.instructions.md`) → la suma de los importes de pago distinta al total (con IVA incluido) debe bloquear el guardado, tanto con datos validos como manipulando el request para saltear el bloqueo de UI.
3. **Criterios de aceptacion del analisis funcional marcados como verificables por UI** (`1-analista-funcional.md` de cada proyecto) — priorizar los que involucren estados/permisos/calculos, no los puramente esteticos.

## Que sigue siendo manual (no se automatiza)

- Casos que requieren credenciales reales de produccion (ej. emision real contra ARCA/AFIP en ambiente de produccion, no homologacion).
- Juicio subjetivo de UX/diseño visual (jerarquia, estetica, "se ve bien").
- Casos que dependen de un dato de negocio que solo el cliente puede proveer/validar (ej. "este calculo de comision coincide con lo que ustedes esperaban").
- Cualquier caso donde la herramienta de automatizacion disponible no pueda ejecutarse de forma confiable en el entorno del agente (ver "Si no hay herramienta disponible" abajo) — no se fuerza, se declara explicitamente.

## Metodologia

1. Levantar la aplicacion localmente (`dotnet run` o el comando equivalente del proyecto) antes de iniciar la matriz de pruebas.
2. Usar el servidor MCP `playwright` configurado en `.mcp.json` de este repo (herramientas `mcp__playwright__*`: navegacion, click, fill, screenshot, evaluacion de contenido) para ejecutar cada caso del alcance automatizable de arriba. Si el servidor MCP no esta disponible/conectado en la sesion actual (ver seccion "Si no hay herramienta disponible" abajo), caer al procedimiento manual.
3. Para cada caso: navegar, ejecutar la accion, capturar el resultado real (texto/estado/respuesta HTTP), compararlo contra el resultado esperado del criterio de aceptacion o de `condicion_falla`.
4. Registrar PASS/FAIL con evidencia (que se observo, no solo "paso"/"fallo") en `docs/<proyecto>/definiciones/6-qa.md`.
5. Ante un FAIL, emitir el **parte de defecto** definido en `30-qa-regresiones.instructions.md` (seccion "Parte de defecto obligatorio"). QA no aplica el parche: lo describe con evidencia y criterio de re-verificacion, y el Implementador lo aplica.
6. **Default-FAIL (2026-09-25):** cada caso de la matriz arranca marcado FAIL y solo pasa a PASS cuando la assertion se evaluo contra el resultado real. Un caso que no se pudo ejecutar es **BLOCKED**, nunca PASS. Si la herramienta de automatizacion no estaba disponible y tampoco se corrio el procedimiento manual, el caso queda BLOCKED y eso se reporta como riesgo de liberacion, no como cobertura.

## Si no hay herramienta de automatizacion disponible en el entorno

No asumir que "no ejecutar nada" equivale a PASS. Si el entorno del agente QA no tiene una herramienta de automatizacion de navegador configurada/accesible en esa sesion:
- Declararlo explicitamente en la salida ("verificacion automatizada no disponible en este entorno").
- Caer al procedimiento manual (guia de pasos para el usuario) como red de seguridad, igual que antes de este cambio.
- No reportar un caso como PASS sin haberlo verificado de una forma u otra.

## Chequeo de reglas nuevas desde la última corrida (obligatorio, 2026-09-08)

El catálogo de reglas cross-proyecto (`32-estandares-qa-implementador.instructions.md`, `docs/qa/regresiones-manuales.yml`, y las instructions de stack como `34-integracion-afip-arca` o `35-pantalla-control-stock`) crece con el tiempo, a medida que otros proyectos del estudio detectan bugs/patrones nuevos. Sin un chequeo explícito, un proyecto que ya pasó QA antes de que se agregara una regla nueva queda con ese patrón sin validar para siempre, aunque el bug pueda estar presente.

**Mecánica:**
1. Al iniciar QA, leer el campo "Última validación de reglas cross-proyecto: `<fecha>`" de `docs/<proyecto>/definiciones/6-qa.md` (sección "Reglas cross-proyecto validadas"). Si no existe (proyecto sin ese campo todavía, o primera corrida), tratar como si nunca se hubiera validado nada — todo el catálogo vigente es "a validar por primera vez".
2. Recorrer las reglas de `32-estandares-qa-implementador.instructions.md` y los items de `regresiones-manuales.yml` buscando las agregadas/modificadas con fecha posterior a esa "Última validación" (cada regla del 32 y cada item del yml lleva su fecha/origen — usarla como referencia; si una regla no tiene fecha explícita, tratarla como preexistente, no como nueva).
3. Para cada regla nueva identificada: ejecutarla contra el sistema bajo prueba (automatizada si es objetivamente chequeable por navegador, manual si no) igual que cualquier otro caso del catálogo — no se salta solo porque no hay un cambio de código de esta sprint que la dispare directamente; el objetivo es cerrar la brecha retroactiva.
4. Reportar el resultado en la salida mínima (punto 4b de `qa-mvc.agent.md`) y en `6-qa.md`.
5. Al cerrar, actualizar el campo "Última validación de reglas cross-proyecto" a la fecha de esta corrida — sin este paso, la próxima corrida no tiene desde dónde diferenciar y tendría que re-revisar todo el catálogo entero cada vez.

## Integridad de la medicion por mutacion (agregado 2026-10-09)

La medicion por mutacion —romper el codigo a proposito y verificar que una afirmacion lo detecta— es hoy la herramienta mas fuerte del estudio para distinguir un arnes que mide de uno que acompania. **El control que los agentes venian usando para no enganiarse con ella estaba solo en su memoria, no en ninguna instruccion**, asi que se perdia al archivar. Queda aca, con la trampa que lo derrota.

**El control, y por que hace falta.** Un mutante que no llega al binario produce el peor resultado posible: el arnes queda en verde y se interpreta como *"la afirmacion no detecta el bug"* o como *"el codigo esta bien"*, cuando en realidad **no se midio nada**. Por eso, antes de creerle a una corrida con mutante:

1. **Verificar que el mutante entro al binario**, no que entro al archivo. El chequeo es sobre el **DLL del proyecto del archivo mutado**: si la condicion vive en `Domain` y se chequea `Infrastructure.dll`, los mutantes **se descartan solos y en silencio** (medido en La Platense: `LP-056`, donde mover una guarda a `Domain` dejo nueve mutantes sin medir y el informe sin la unica medicion que importaba).
2. **Un mutante por arbol de build.** Un proceso vivo bloquea el DLL y el build del siguiente mutante falla sin que el resultado lo diga.
3. **No usar `--no-build` sobre un arnes que acaba de cambiar:** si no compilo, corre el EXE anterior. Medido en La Platense el 2026-10-09: una corrida dio **111 OK / 0 sobre codigo viejo** y se leyo como exito.
4. **Mirar la salida, no el total.** Un conteo agregado esconde exactamente el elemento que no corresponde (instruccion 39 seccion 4a).

**LA TRAMPA QUE EL CONTROL DE `md5` NO ATRAPA, y es la razon de esta seccion.** Medida en La Platense el 2026-10-09, en la fase 1 del token de submit:

> **Restaurar el archivo mutado con una copia que PRESERVA EL MTIME** (por ejemplo `shutil.copy2`, o `cp -p`) **hace que MSBuild no recompile. El mutante sigue vivo en la DLL, y el chequeo de `md5` del archivo fuente contra su backup pasa en VERDE**, porque el fuente si quedo restaurado. El control dice "todo en orden" y la siguiente medicion corre contra el binario mutado.

Es la unica forma de falla de la ronda que el control recomendado **no detecta**, y es especialmente peligrosa porque aparece al **final** del ciclo —al limpiar— y contamina las mediciones **siguientes**, no la propia.

**Reglas que salen de esto:**

- **Restaurar sin preservar el mtime** (`shutil.copy` en vez de `copy2`, `cp` sin `-p`), o tocar el archivo despues de restaurar.
- **El `md5` del FUENTE no es evidencia de que el BINARIO este sano.** Cuando el resultado importa, el control es sobre el artefacto que se ejecuta: hash del DLL, o un rebuild forzado antes de la medicion siguiente.
- **Una medicion por mutacion que sale en verde es sospechosa hasta que se demuestre que el mutante llego a ejecutarse.** La forma mas barata de demostrarlo es un **control negativo**: un mutante que *tiene* que tumbar una afirmacion conocida. Si ese tampoco tumba nada, el problema es el instrumento y no el codigo.

**Por que esta aca y no en la memoria de un agente:** porque la usan el QA y el Implementador por igual, porque se pierde al archivar, y porque un control de integridad en el que se confia sin conocer su punto ciego es peor que no tener control — da licencia para creerle a un verde que no midio nada.

## Por que el evaluador no puede ser el que arregla (2026-09-25)

La version original de esta instruccion (2026-08-14) cerraba el punto ciego de "nadie ejecuta la app antes de la entrega", pero dejaba abierto otro: el mismo agente que aplicaba el auto-fix era el que despues firmaba el PASS. Un generador que se autocalifica aprueba su propio trabajo aunque este mediocre — es un resultado medido, no una hipotesis.

Desde esta fecha la automatizacion **verifica y reporta**; no repara. Ver el contrato completo en `30-qa-regresiones.instructions.md`, seccion "Contrato de evaluacion independiente".

## Alcance de este cambio

Esta instruccion no reemplaza la verificacion manual del cliente antes de aceptar la entrega — la reduce. El cliente sigue siendo responsable de su propia aceptacion final, pero llega a esa instancia con una base mas solida: los patrones de bug ya conocidos del estudio quedaron chequeados por una herramienta antes de que el humano viera el sistema, no despues.
