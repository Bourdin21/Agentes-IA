---
name: metodo-qa-datos-reales
description: El metodo que encuentra los defectos de verdad en las pantallas de reporte de este estudio (runner de consola de solo lectura contra produccion + SQL cruzado), y las trampas operativas de levantar la app en Windows.
metadata:
  type: project
---

Para validar una pantalla de reporte/metrica, los tres caminos se combinan siempre en este orden, y el segundo es el que encuentra los defectos:

1. **Runner de consola de solo lectura contra la base REAL de produccion.** Un `.csproj` que referencia `<Proyecto>.Infrastructure`, instancia el `AppDbContext` con la connection string de `appsettings.Production.json` y llama al Service directamente. No levanta la app web, asi que **ningun BackgroundService corre** — importante donde los hosted services escriben notificaciones al arrancar. Un `DbCommandInterceptor` de 15 lineas cronometra cada comando y da la evidencia de round-trips.
2. **Recalcular cada numero importante por SQL, por otro camino.** No alcanza con que el service de un numero: hay que llegar al mismo numero con una consulta independiente (y, para busquedas en memoria, con una implementacion distinta — lineal contra binaria). Los defentos de CR-79 y CR-80 aparecieron **todos** en esta comparacion, ninguno en la lectura de codigo.
3. **Pantallas por HTTP con `curl -k` + cookie jar** contra la base de desarrollo, nunca produccion: codigos de respuesta, HTML servido, estados vacios, panel de filtros, sesion y matriz de roles (login real por rol, no lectura del `[Authorize]`).

**Why:** los defectos de una pantalla de reporte no dan error, compilan y cada consulta por separado da bien. Solo se ven cuando el mismo numero se calcula dos veces por caminos distintos, o cuando se lo enfrenta con el numero de al lado. Y necesitan volumen e historia real: con la base de desarrollo no aparecen.

**How to apply:** en cualquier CR de reporte/KPI/dashboard, antes de escribir el informe. Ademas, probar **todas** las ventanas/rangos que ofrece la pantalla, no solo el default: en CR-80 la diferencia era 0 con 60 y 90 dias y aparecia solo con 180.

Trampas operativas (Windows, todos los proyectos del estudio):

- La app corriendo **bloquea** `<Proyecto>.Infrastructure.dll`: un `dotnet build` durante la corrida falla con MSB3027. Bajar el proceso (`Stop-Process -Name "<Proyecto>.Web" -Force`) antes de recompilar, y volver a levantarla si hacen falta mas pruebas HTTP.
- `Invoke-WebRequest` de PowerShell **no conecta a localhost** (proxy del sistema). Usar `curl -k` con `-c/-b` para la cookie de sesion.
- Para el login por `curl` hay que leer el `__RequestVerificationToken` del HTML de `/Account/Login` y postearlo junto a las credenciales.
- Heredoc de bash con contenido largo en castellano se rompe seguido: escribir el bloque con la herramienta Write a un archivo del scratchpad y despues `cat archivo >> destino`.
- Validar el YAML del catalogo con `python -c "import yaml; yaml.safe_load(...)"` despues de agregar items, y contar los ids para confirmar que entraron.

**El MCP de Playwright puede no estar disponible en la sesion** (verificarlo buscando herramientas `mcp__playwright__*`). Cuando no esta: declararlo explicitamente en el informe, cubrir por HTTP todo lo que se pueda (status, HTML servido, roles, estados vacios) y dejar como procedimiento manual solo lo que exige un navegador de verdad — consola de JS limpia, breakpoints de ancho, interaccion de graficos, simular la caida de un endpoint. Nunca dar una verificacion por hecha sin decir por que camino se cubrio.
