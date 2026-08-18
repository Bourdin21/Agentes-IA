---
description: Reglas de Web MVC (pipeline, middleware, controllers, viewmodels, auth, session).
applyTo: "**/Web/**/*.{cs,cshtml,json}"
---

# Pipeline HTTP en produccion (orden)
1. UseRequestLocalization (es-AR fija)
2. UseExceptionHandler
3. UseHsts
4. UseHttpsRedirection
5. UseResponseCompression
6. UseStatusCodePagesWithReExecute
7. UseSerilogRequestLogging
8. UseStaticFiles
9. UseRouting
10. UseAuthentication
11. UseAuthorization
12. UseRateLimiter
13. UseSession
14. MapControllerRoute().RequireRateLimiting("general")
15. MapHealthChecks("/health")

# Controllers
- Inyeccion por constructor, no FromServices.
- TempData["SuccessMessage"] y TempData["ErrorMessage"].
- DataTables server-side con DataTableRequest/DataTableResponse<T>.
- Exportaciones con File(bytes, contentType, fileName).

# ViewModels
- DataAnnotations en espanol argentino, con ortografia y acentuacion correctas (`Display`, mensajes de validacion) — ver `25-frontend-design-system.instructions.md`, seccion "Ortografia y acentuacion en texto de UI".
- No usar entidades de Domain en Views.

# Seguridad y sesion
- Policies: RequireSuperUsuario y RequireAdministracion.
- Login POST con rate limiter policy login.
- Session timeout: 60 minutos.

# jquery.maskMoney.js — nunca escuchar solo 'input' en un campo enmascarado
- Hallazgo real (marihogar, 15/08/2026): el plugin intercepta cada tecla con
  `preventDefault()` y escribe el valor via `$input.val(...)` a mano — nunca dispara el
  evento nativo `input` del browser. El unico evento que dispara es `change`, y unicamente
  al perder el foco (`blurEvent`, solo si el valor cambio desde que gano el foco). Un
  handler `$(document).on('input', '.money', ...)` para sincronizar el array JS con el
  campo NUNCA se ejecuta mientras el usuario tipea — el array queda "congelado" en su valor
  inicial aunque la pantalla muestre el numero recien tipeado, hasta que el campo pierda el
  foco. Causa real de bugs de perdida silenciosa de datos (ej.: formas de pago configuradas
  a mano que se guardaban con el monto default en vez del tipeado, porque el usuario
  clickeaba "Confirmar" sin que el campo llegase a hacer blur antes).
- **Regla**: todo handler que sincroniza un array JS desde un campo `.money` (maskMoney) debe
  escuchar `'input change'` (nunca solo `'input'`) — `change` es el evento real que el
  plugin dispara. Ademas, en el handler de submit/confirmar, releer explicitamente cada
  campo `.money` visible del DOM (via el mismo `leerMoney()`/`.maskMoney('unmasked')`) antes
  de armar el payload final, como defensa adicional por si el ultimo campo editado no llego
  a perder el foco antes del click.
- Mismo criterio para cualquier otro plugin de mascara que prevenga el evento nativo del
  browser — no asumir que `'input'` siempre captura los cambios, verificar que evento
  dispara realmente el plugin en cuestion.
