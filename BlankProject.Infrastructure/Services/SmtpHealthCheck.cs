using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;

namespace BlankProject.Infrastructure.Services;

/// <summary>
/// Health check para verificar conectividad con el servidor SMTP.
/// </summary>
public class SmtpHealthCheck : IHealthCheck
{
    private readonly SmtpSettings _settings;

    public SmtpHealthCheck(IOptions<SmtpSettings> settings)
    {
        _settings = settings.Value;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_settings.Host))
            return HealthCheckResult.Degraded("SMTP Host no configurado.");

        try
        {
            using var client = new SmtpClient();
            var secureOption = _settings.Port == 465
                ? SecureSocketOptions.SslOnConnect
                : (_settings.EnableSsl ? SecureSocketOptions.StartTls : SecureSocketOptions.None);

            await client.ConnectAsync(_settings.Host, _settings.Port, secureOption, cancellationToken);
            await client.DisconnectAsync(true, cancellationToken);
            return HealthCheckResult.Healthy("Servidor SMTP accesible.");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Error al conectar con servidor SMTP.", ex);
        }
    }
}
