# Prompt: Implementar Rate Limiting + Response Compression + Global Exception Handling mejorado

## Contexto
Proyecto ASP.NET Core MVC (.NET 8+) con Clean Architecture (Domain, Application, Infrastructure, Web).
Ya debe existir previamente:
- `IErrorNotifier` en Application/Interfaces
- `ErrorNotifier` en Infrastructure/Services (envía emails via `IEmailService`)
- `IEmailService` / `EmailService` con SMTP configurado
- `ErrorViewModel` con propiedades: `RequestId`, `StatusCode`, `Titulo`, `Mensaje`
- `HomeController` con acciones `Error()` y `StatusCode(int code)`
- Configuración en appsettings.Production.json:
  - `Olvidata_Email:Smtp` (Host, Port, User, Password, EnableSsl, FromAddress, FromName)
  - `Olvidata_ErrorEmail:Destinatarios` (array de emails)

---

## 1. CREAR: `Web/Middleware/GlobalExceptionHandler.cs`

```csharp
using {NombreProyecto}.Application.Interfaces;
using Microsoft.AspNetCore.Diagnostics;

namespace {NombreProyecto}.Web.Middleware;

/// <summary>
/// Handler global de excepciones usando IExceptionHandler (.NET 8+).
/// Registra errores con contexto enriquecido via Serilog, notifica por email
/// en producción y devuelve JSON para AJAX o redirige para MVC.
/// </summary>
public class GlobalExceptionHandler : IExceptionHandler
{
    private readonly ILogger<GlobalExceptionHandler> _logger;
    private readonly IErrorNotifier _errorNotifier;
    private readonly IHostEnvironment _environment;

    public GlobalExceptionHandler(
        ILogger<GlobalExceptionHandler> logger,
        IErrorNotifier errorNotifier,
        IHostEnvironment environment)
    {
        _logger = logger;
        _errorNotifier = errorNotifier;
        _environment = environment;
    }

    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        var userId = httpContext.User?.Identity?.Name ?? "Anónimo";
        var traceId = httpContext.TraceIdentifier;
        var method = httpContext.Request.Method;
        var path = $"{httpContext.Request.Path}{httpContext.Request.QueryString}";
        var fullRequest = $"{method} {httpContext.Request.Scheme}://{httpContext.Request.Host}{path}";

        _logger.LogError(exception,
            "Excepción no manejada | TraceId={TraceId} | Usuario={Usuario} | {Method} {Path}",
            traceId, userId, method, path);

        // Notificar por email en producción (fire-and-forget, no bloquea la respuesta)
        if (!_environment.IsDevelopment())
        {
            _errorNotifier.NotifyError(exception, userId, fullRequest);
        }

        // Si es una request AJAX / API, devolver JSON
        if (IsAjaxOrApiRequest(httpContext))
        {
            httpContext.Response.StatusCode = StatusCodes.Status500InternalServerError;
            httpContext.Response.ContentType = "application/json";

            var problemDetails = new
            {
                status = 500,
                title = "Error interno del servidor",
                detail = "Ocurrió un error inesperado al procesar su solicitud.",
                traceId
            };

            await httpContext.Response.WriteAsJsonAsync(problemDetails, cancellationToken);
            return true;
        }

        // Para requests MVC normales, dejar que UseExceptionHandler maneje la redirección
        return false;
    }

    private static bool IsAjaxOrApiRequest(HttpContext context)
    {
        var request = context.Request;

        if (string.Equals(request.Headers.XRequestedWith, "XMLHttpRequest", StringComparison.OrdinalIgnoreCase))
            return true;

        if (request.Path.StartsWithSegments("/api", StringComparison.OrdinalIgnoreCase))
            return true;

        var accept = request.Headers.Accept.ToString();
        if (accept.Contains("application/json", StringComparison.OrdinalIgnoreCase)
            && !accept.Contains("text/html", StringComparison.OrdinalIgnoreCase))
            return true;

        return false;
    }
}
```

---

## 2. MODIFICAR: `Program.cs` — Sección de servicios (builder.Services)

### 2a. Agregar usings al inicio del archivo

```csharp
using System.IO.Compression;
using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.AspNetCore.ResponseCompression;
using {NombreProyecto}.Web.Middleware;
```

### 2b. Después de `AddControllersWithViews()`, agregar estos tres bloques:

```csharp
builder.Services.AddControllersWithViews();

// Global Exception Handler
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();

// Response Compression: Brotli + Gzip
builder.Services.AddResponseCompression(options =>
{
    options.EnableForHttps = true;
    options.Providers.Add<BrotliCompressionProvider>();
    options.Providers.Add<GzipCompressionProvider>();
    options.MimeTypes = ResponseCompressionDefaults.MimeTypes.Concat(
    [
        "application/json",
        "application/javascript",
        "text/css",
        "image/svg+xml"
    ]);
});
builder.Services.Configure<BrotliCompressionProviderOptions>(options =>
    options.Level = CompressionLevel.Fastest);
builder.Services.Configure<GzipCompressionProviderOptions>(options =>
    options.Level = CompressionLevel.SmallestSize);

// Rate Limiting
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

    // Política general: 100 requests por minuto por IP
    options.AddPolicy("general", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1),
                QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                QueueLimit = 5
            }));

    // Política estricta para login: 10 intentos por minuto por IP
    options.AddPolicy("login", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            partitionKey: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            factory: _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 10,
                Window = TimeSpan.FromMinutes(1),
                QueueProcessingOrder = QueueProcessingOrder.OldestFirst,
                QueueLimit = 0
            }));
});
```

---

## 3. MODIFICAR: `Program.cs` — Pipeline de middleware (app.Use...)

### 3a. Exception handling (reemplazar bloque existente)

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    // GlobalExceptionHandler procesa la excepción (log + email + JSON para AJAX),
    // luego UseExceptionHandler redirige a /Home/Error para requests MVC.
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}
```

> **IMPORTANTE:** Si existía un `ErrorEmailNotifierMiddleware` registrado con
> `app.UseMiddleware<ErrorEmailNotifierMiddleware>()`, **eliminarlo del pipeline**.
> El `GlobalExceptionHandler` se ejecuta DENTRO de `UseExceptionHandler`, por lo que
> un middleware externo nunca vería la excepción (UseExceptionHandler la consume).

### 3b. Agregar Response Compression después de `UseHttpsRedirection()`

```csharp
app.UseHttpsRedirection();

// Response Compression (antes de static files para comprimir respuestas dinámicas)
app.UseResponseCompression();

app.UseStatusCodePagesWithReExecute("/Home/StatusCode", "?code={0}");
```

### 3c. Agregar Rate Limiter después de `UseAuthorization()`

```csharp
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter();
app.UseSession();
```

### 3d. Aplicar política general a las rutas MVC

```csharp
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}")
    .RequireRateLimiting("general");
```

---

## 4. MODIFICAR: `AccountController.cs` — Rate limit en Login

Agregar el using y el atributo `[EnableRateLimiting("login")]` al POST de Login:

```csharp
using Microsoft.AspNetCore.RateLimiting;

// ...

[HttpPost]
[AllowAnonymous]
[ValidateAntiForgeryToken]
[EnableRateLimiting("login")]
public async Task<IActionResult> Login(LoginViewModel model, string? returnUrl = null)
```

---

## 5. MODIFICAR: `HomeController.cs` — Agregar case 429 en StatusCode()

Dentro del `switch` de `StatusCode(int code)`, agregar:

```csharp
429 => new ErrorViewModel
{
    StatusCode = 429,
    Titulo = "Demasiadas solicitudes",
    Mensaje = "Realizaste demasiadas solicitudes en poco tiempo. Esperá un momento e intentá de nuevo."
},
```

---

## Orden del pipeline de middleware (referencia completa)

```
1. UseRequestLocalization
2. UseDeveloperExceptionPage / UseExceptionHandler  ← GlobalExceptionHandler aquí
3. UseHsts
4. UseHttpsRedirection
5. UseResponseCompression                            ← NUEVO
6. UseStatusCodePagesWithReExecute
7. UseSerilogRequestLogging
8. UseStaticFiles
9. UseRouting
10. UseAuthentication
11. UseAuthorization
12. UseRateLimiter                                    ← NUEVO
13. UseSession
14. MapControllerRoute.RequireRateLimiting("general") ← NUEVO
```

---

## Notas importantes

- **No se necesitan paquetes NuGet adicionales**: Rate Limiting, Response Compression y
  `IExceptionHandler` son parte del framework ASP.NET Core desde .NET 7/8.
- **Rate Limiting** usa `RemoteIpAddress` como partition key. Si el proyecto está detrás
  de un reverse proxy (nginx, Cloudflare), asegurar que `ForwardedHeaders` esté configurado
  para que la IP del cliente sea la real.
- **Response Compression** tiene `EnableForHttps = true` que puede ser un riesgo de seguridad
  (BREACH attack) en respuestas que mezclan datos sensibles con input del usuario. Para la
  mayoría de aplicaciones MVC internas es aceptable.
- **GlobalExceptionHandler** envía emails solo en producción (`!IsDevelopment()`). El envío
  es fire-and-forget via `IErrorNotifier.NotifyError()` — no bloquea la respuesta al usuario.
- **Reemplazar `{NombreProyecto}`** con el nombre del proyecto destino en todos los namespaces.
