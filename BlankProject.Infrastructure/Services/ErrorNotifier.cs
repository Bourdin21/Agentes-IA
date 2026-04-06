using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using BlankProject.Application.Interfaces;

namespace BlankProject.Infrastructure.Services;

/// <summary>
/// Implementación de notificación de errores por email.
/// Fire-and-forget: no bloquea el request ni lanza excepciones.
/// </summary>
public class ErrorNotifier : IErrorNotifier
{
    private readonly IEmailService _emailService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<ErrorNotifier> _logger;

    public ErrorNotifier(IEmailService emailService, IConfiguration configuration, ILogger<ErrorNotifier> logger)
    {
        _emailService = emailService;
        _configuration = configuration;
        _logger = logger;
    }

    public void NotifyError(Exception ex, string? usuario = null, string? requestInfo = null)
    {
        _ = Task.Run(async () =>
        {
            try
            {
                var destinatarios = _configuration.GetSection("Olvidata_ErrorEmail:Destinatarios").Get<string[]>();
                if (destinatarios == null || destinatarios.Length == 0)
                {
                    _logger.LogWarning("No hay destinatarios en Olvidata_ErrorEmail:Destinatarios. Error no notificado.");
                    return;
                }

                var fecha = DateTime.Now;
                var ambiente = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Desconocido";
                var asunto = $"[BlankProject] Error - {ex.GetType().Name}: {Truncar(ex.Message, 80)}";

                var html = $@"
<html>
<body style='font-family: -apple-system, BlinkMacSystemFont, ""Segoe UI"", Roboto, Arial, sans-serif; color: #1e293b; margin: 0; padding: 0;'>
<div style='max-width: 700px; margin: 20px auto; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;'>

    <div style='background: #ef4444; color: white; padding: 16px 24px;'>
        <h2 style='margin: 0; font-size: 18px;'>Error en BlankProject</h2>
        <p style='margin: 4px 0 0; font-size: 13px; opacity: 0.9;'>{fecha:dd/MM/yyyy HH:mm:ss} - {ambiente}</p>
    </div>

    <div style='padding: 24px;'>

        <table style='width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;'>
            <tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600; width: 140px; border-bottom: 1px solid #e2e8f0;'>Usuario</td>
                <td style='padding: 8px 12px; border-bottom: 1px solid #e2e8f0;'>{Esc(usuario ?? "N/A")}</td>
            </tr>
            {(requestInfo != null ? $@"<tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600; border-bottom: 1px solid #e2e8f0;'>Request</td>
                <td style='padding: 8px 12px; border-bottom: 1px solid #e2e8f0;'><code>{Esc(requestInfo)}</code></td>
            </tr>" : "")}
        </table>

        <h3 style='color: #ef4444; margin: 0 0 8px; font-size: 15px;'>{Esc(ex.GetType().FullName ?? ex.GetType().Name)}</h3>
        <p style='margin: 0 0 16px; font-size: 14px;'>{Esc(ex.Message)}</p>

        <details style='margin-bottom: 16px;'>
            <summary style='cursor: pointer; font-weight: 600; font-size: 14px; color: #475569;'>Stack Trace</summary>
            <pre style='background: #f1f5f9; padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto; margin-top: 8px;'>{Esc(ex.StackTrace ?? "N/A")}</pre>
        </details>

        {(ex.InnerException != null ? $@"
        <details>
            <summary style='cursor: pointer; font-weight: 600; font-size: 14px; color: #475569;'>Inner Exception</summary>
            <p style='margin: 8px 0 4px; font-size: 13px; color: #ef4444;'>{Esc(ex.InnerException.GetType().Name)}: {Esc(ex.InnerException.Message)}</p>
            <pre style='background: #f1f5f9; padding: 12px; border-radius: 6px; font-size: 12px; overflow-x: auto;'>{Esc(ex.InnerException.StackTrace ?? "N/A")}</pre>
        </details>" : "")}

    </div>

    <div style='background: #f8fafc; padding: 12px 24px; font-size: 12px; color: #94a3b8; text-align: center;'>
        BlankProject — Notificación automática de errores
    </div>

</div>
</body>
</html>";

                await _emailService.SendEmailAsync(destinatarios, asunto, html);
            }
            catch (Exception emailEx)
            {
                _logger.LogError(emailEx, "Error al enviar email de notificación de error.");
            }
        });
    }

    private static string Truncar(string texto, int maxLen) =>
        texto.Length <= maxLen ? texto : texto[..maxLen] + "...";

    private static string Esc(string texto) =>
        System.Net.WebUtility.HtmlEncode(texto ?? string.Empty);
}
