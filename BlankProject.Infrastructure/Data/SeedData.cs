using BlankProject.Domain.Entities;
using BlankProject.Domain.Enums;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

namespace BlankProject.Infrastructure.Data;

public static class SeedData
{
    public const string RolSuperUsuario = "SuperUsuario";
    public const string RolAdministrador = "Administrador";

    public static async Task InitializeAsync(IServiceProvider serviceProvider)
    {
        var logger = serviceProvider.GetRequiredService<ILogger<AppDbContext>>();
        var roleManager = serviceProvider.GetRequiredService<RoleManager<IdentityRole>>();
        var userManager = serviceProvider.GetRequiredService<UserManager<ApplicationUser>>();
        var configuration = serviceProvider.GetRequiredService<IConfiguration>();

        // Crear roles
        string[] roles = [RolSuperUsuario, RolAdministrador];
        foreach (var role in roles)
        {
            if (!await roleManager.RoleExistsAsync(role))
            {
                var result = await roleManager.CreateAsync(new IdentityRole(role));
                if (result.Succeeded)
                    logger.LogInformation("Rol '{Role}' creado.", role);
                else
                    logger.LogError("Error creando rol '{Role}': {Errors}", role,
                        string.Join(", ", result.Errors.Select(e => e.Description)));
            }
        }

        // Crear SuperUsuario inicial (configurable por appsettings o variables de entorno)
        var superEmail = configuration["Seed:SuperUser:Email"] ?? "no-reply@olvidata.com.ar";
        var superPassword = configuration["Seed:SuperUser:Password"] ?? "Super123!";
        var superName = configuration["Seed:SuperUser:Name"] ?? "Super Usuario";

        var superUser = await userManager.FindByEmailAsync(superEmail);
        if (superUser == null)
        {
            superUser = new ApplicationUser
            {
                UserName = superEmail,
                Email = superEmail,
                FullName = superName,
                Estado = EstadoUsuario.Activo,
                EmailConfirmed = true
            };

            var result = await userManager.CreateAsync(superUser, superPassword);
            if (result.Succeeded)
            {
                await userManager.AddToRoleAsync(superUser, RolSuperUsuario);
                logger.LogInformation("SuperUsuario creado: {Email}", superEmail);
            }
            else
            {
                logger.LogError("Error creando SuperUsuario: {Errors}",
                    string.Join(", ", result.Errors.Select(e => e.Description)));
            }
        }
    }
}
