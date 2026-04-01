using BlankProject.Infrastructure.Data;
using Microsoft.Extensions.Diagnostics.HealthChecks;

namespace BlankProject.Infrastructure.Services;

/// <summary>
/// Health check para verificar conectividad con la base de datos MySQL.
/// </summary>
public class DatabaseHealthCheck : IHealthCheck
{
    private readonly AppDbContext _context;

    public DatabaseHealthCheck(AppDbContext context)
    {
        _context = context;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        try
        {
            var canConnect = await _context.Database.CanConnectAsync(cancellationToken);
            return canConnect
                ? HealthCheckResult.Healthy("Base de datos MySQL accesible.")
                : HealthCheckResult.Unhealthy("No se pudo conectar a la base de datos.");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Error al verificar base de datos.", ex);
        }
    }
}
