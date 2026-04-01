using BlankProject.Application.Interfaces;

namespace BlankProject.Web.Middleware;

/// <summary>
/// Middleware que captura excepciones no manejadas durante requests HTTP
/// y envia una notificacion por email con el detalle del error.
/// No reemplaza el manejo de errores existente: solo observa y notifica.
/// </summary>
public class ErrorEmailNotifierMiddleware
{
    private readonly RequestDelegate _next;

    public ErrorEmailNotifierMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context, IErrorNotifier errorNotifier)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            var usuario = context.User?.Identity?.Name ?? "Anónimo";
            var request = $"{context.Request.Method} {context.Request.Scheme}://{context.Request.Host}{context.Request.Path}{context.Request.QueryString}";
            errorNotifier.NotifyError(ex, usuario, request);
            throw;
        }
    }
}
