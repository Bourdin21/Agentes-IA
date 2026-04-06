using BlankProject.Application.Interfaces;
using BlankProject.Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace BlankProject.Web.Controllers;

/// <summary>
/// Herramientas del sistema accesibles solo para SuperUsuario.
/// Permite verificar que los servicios de infraestructura funcionan correctamente.
/// </summary>
[Authorize(Policy = "RequireSuperUsuario")]
public class SystemController : Controller
{
    private readonly IEmailService _emailService;
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly ILogger<SystemController> _logger;

    public SystemController(
        IEmailService emailService,
        UserManager<ApplicationUser> userManager,
        ILogger<SystemController> logger)
    {
        _emailService = emailService;
        _userManager = userManager;
        _logger = logger;
    }

    public IActionResult Index()
    {
        return View();
    }

    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> TestEmail(string destinatario)
    {
        if (string.IsNullOrWhiteSpace(destinatario))
        {
            TempData["ErrorMessage"] = "Ingresá un email destinatario.";
            return RedirectToAction(nameof(Index));
        }

        destinatario = destinatario.Trim();

        try
        {
            var user = await _userManager.GetUserAsync(User);
            var ambiente = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Desconocido";
            var fecha = DateTime.Now;

            var html = $@"
<html>
<body style='font-family: -apple-system, BlinkMacSystemFont, ""Segoe UI"", Roboto, Arial, sans-serif; color: #1e293b; margin: 0; padding: 0;'>
<div style='max-width: 600px; margin: 20px auto; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;'>

    <div style='background: #2b9de4; color: white; padding: 16px 24px;'>
        <h2 style='margin: 0; font-size: 18px;'>✅ Test de Email — BlankProject</h2>
        <p style='margin: 4px 0 0; font-size: 13px; opacity: 0.9;'>{fecha:dd/MM/yyyy HH:mm:ss}</p>
    </div>

    <div style='padding: 24px;'>
        <p style='margin: 0 0 16px; font-size: 14px;'>
            Este email confirma que el servicio de correo electrónico está funcionando correctamente.
        </p>

        <table style='width: 100%; border-collapse: collapse; font-size: 14px;'>
            <tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600; width: 140px; border-bottom: 1px solid #e2e8f0;'>Ambiente</td>
                <td style='padding: 8px 12px; border-bottom: 1px solid #e2e8f0;'>{ambiente}</td>
            </tr>
            <tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600; border-bottom: 1px solid #e2e8f0;'>Enviado a</td>
                <td style='padding: 8px 12px; border-bottom: 1px solid #e2e8f0;'>{System.Net.WebUtility.HtmlEncode(destinatario)}</td>
            </tr>
            <tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600; border-bottom: 1px solid #e2e8f0;'>Solicitado por</td>
                <td style='padding: 8px 12px; border-bottom: 1px solid #e2e8f0;'>{System.Net.WebUtility.HtmlEncode(user!.FullName)} ({System.Net.WebUtility.HtmlEncode(destinatario)})</td>
            </tr>
            <tr>
                <td style='padding: 8px 12px; background: #f8fafc; font-weight: 600;'>Servidor</td>
                <td style='padding: 8px 12px;'>{System.Net.WebUtility.HtmlEncode(Environment.MachineName)}</td>
            </tr>
        </table>
    </div>

    <div style='background: #f8fafc; padding: 12px 24px; font-size: 12px; color: #94a3b8; text-align: center;'>
        BlankProject — Email de prueba automático
    </div>

</div>
</body>
</html>";

            await _emailService.SendEmailAsync(destinatario, $"[BlankProject] Test de email — {ambiente}", html);

            _logger.LogInformation("Email de prueba enviado a {Destinatario} por {Admin}", destinatario, user?.FullName);
            TempData["SuccessMessage"] = $"Email de prueba enviado correctamente a {destinatario}. Revisá la bandeja de entrada (y spam).";
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error al enviar email de prueba.");
            TempData["ErrorMessage"] = $"Error al enviar email de prueba: {ex.Message}";
        }

        return RedirectToAction(nameof(Index));
    }
}
