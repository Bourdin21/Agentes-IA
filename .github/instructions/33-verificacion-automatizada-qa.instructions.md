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
5. Ante un FAIL, aplica el flujo de auto-fix obligatorio ya definido en `30-qa-regresiones.instructions.md` (mismo criterio, ahora con deteccion automatizada en vez de manual).

## Si no hay herramienta de automatizacion disponible en el entorno

No asumir que "no ejecutar nada" equivale a PASS. Si el entorno del agente QA no tiene una herramienta de automatizacion de navegador configurada/accesible en esa sesion:
- Declararlo explicitamente en la salida ("verificacion automatizada no disponible en este entorno").
- Caer al procedimiento manual (guia de pasos para el usuario) como red de seguridad, igual que antes de este cambio.
- No reportar un caso como PASS sin haberlo verificado de una forma u otra.

## Alcance de este cambio

Esta instruccion no reemplaza la verificacion manual del cliente antes de aceptar la entrega — la reduce. El cliente sigue siendo responsable de su propia aceptacion final, pero llega a esa instancia con una base mas solida: los patrones de bug ya conocidos del estudio quedaron chequeados por una herramienta antes de que el humano viera el sistema, no despues.
