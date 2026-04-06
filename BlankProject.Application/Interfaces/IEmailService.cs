namespace BlankProject.Application.Interfaces;

/// <summary>
/// Servicio de envio de emails via SMTP.
/// </summary>
public interface IEmailService
{
    Task SendEmailAsync(string to, string subject, string htmlBody);
    Task SendEmailAsync(IEnumerable<string> to, string subject, string htmlBody);
}
