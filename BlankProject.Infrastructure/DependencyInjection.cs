using BlankProject.Application.Interfaces;
using BlankProject.Infrastructure.Data;
using BlankProject.Infrastructure.Repositories;
using BlankProject.Infrastructure.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace BlankProject.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection");
        if (string.IsNullOrWhiteSpace(connectionString))
            throw new InvalidOperationException("ConnectionStrings:DefaultConnection no encontrada o vacía.");

        services.AddDbContext<AppDbContext>(options =>
            options.UseMySQL(connectionString));

        services.AddHttpContextAccessor();

        // Repositorio generico
        services.AddScoped(typeof(IRepository<>), typeof(Repository<>));

        // SMTP
        services.Configure<SmtpSettings>(configuration.GetSection("Olvidata_Email:Smtp"));
        services.AddScoped<IEmailService, EmailService>();
        services.AddScoped<IErrorNotifier, ErrorNotifier>();

        // Notificaciones
        services.AddScoped<INotificationService, NotificationService>();

        // Exportacion Excel/PDF
        services.AddScoped<IExportService, ExportService>();

        // Health checks
        services.AddHealthChecks()
            .AddCheck<DatabaseHealthCheck>("mysql", tags: ["db", "ready"])
            .AddCheck<SmtpHealthCheck>("smtp", tags: ["email"]);

        return services;
    }
}
