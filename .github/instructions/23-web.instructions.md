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
- DataAnnotations en espanol argentino.
- No usar entidades de Domain en Views.

# Seguridad y sesion
- Policies: RequireSuperUsuario y RequireAdministracion.
- Login POST con rate limiter policy login.
- Session timeout: 60 minutos.
