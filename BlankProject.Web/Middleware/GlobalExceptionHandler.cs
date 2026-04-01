using BlankProject.Application.Interfaces;
using Microsoft.AspNetCore.Diagnostics;

namespace BlankProject.Web.Middleware;

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
