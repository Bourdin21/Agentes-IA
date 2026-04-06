using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using MimeKit;
using BlankProject.Application.Interfaces;

namespace BlankProject.Infrastructure.Services;

/// <summary>
/// Implementacion de envio de emails via SMTP usando MailKit.
/// Soporta SSL implicito (puerto 465) y STARTTLS (puerto 587).
/// </summary>
public class EmailService : IEmailService
{
    private readonly SmtpSettings _settings;
    private readonly ILogger<EmailService> _logger;

    public EmailService(IOptions<SmtpSettings> settings, ILogger<EmailService> logger)
    {
        _settings = settings.Value;
        _logger = logger;
    }

    public async Task SendEmailAsync(string to, string subject, string htmlBody)
    {
        await SendEmailAsync([to], subject, htmlBody);
    }

    public async Task SendEmailAsync(IEnumerable<string> to, string subject, string htmlBody)
    {
        if (string.IsNullOrWhiteSpace(_settings.Host))
        {
            _logger.LogWarning("SMTP Host no configurado. Email no enviado: {Subject}", subject);
            return;
        }

        try
        {
            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(_settings.FromName, _settings.FromAddress));

            foreach (var address in to)
            {
                if (!string.IsNullOrWhiteSpace(address))
                    message.To.Add(MailboxAddress.Parse(address));
            }

            if (message.To.Count == 0)
            {
                _logger.LogWarning("No hay destinatarios validos para el email: {Subject}", subject);
                return;
            }

            message.Subject = subject;
            message.Body = new TextPart("html") { Text = htmlBody };

            using var client = new SmtpClient();

            // Puerto 465 = SSL implicito (SslOnConnect), Puerto 587 = STARTTLS
            var secureOption = _settings.Port == 465
                ? SecureSocketOptions.SslOnConnect
                : (_settings.EnableSsl ? SecureSocketOptions.StartTls : SecureSocketOptions.None);

            await client.ConnectAsync(_settings.Host, _settings.Port, secureOption);

            if (!string.IsNullOrWhiteSpace(_settings.User))
                await client.AuthenticateAsync(_settings.User, _settings.Password);

            await client.SendAsync(message);
            await client.DisconnectAsync(true);

            _logger.LogInformation("Email enviado a {To}: {Subject}",
                string.Join(", ", to), subject);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error enviando email: {Subject}", subject);
        }
    }
}
