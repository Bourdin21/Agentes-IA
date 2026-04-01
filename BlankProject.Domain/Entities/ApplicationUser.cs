using BlankProject.Domain.Enums;
using Microsoft.AspNetCore.Identity;

namespace BlankProject.Domain.Entities;

/// <summary>
/// Usuario de la aplicación (hereda de IdentityUser para autenticación).
/// Roles gestionados via ASP.NET Core Identity (SuperUsuario, Usuario).
/// </summary>
public class ApplicationUser : IdentityUser
{
    public string FullName { get; set; } = string.Empty;
    public EstadoUsuario Estado { get; set; } = EstadoUsuario.Activo;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? UpdatedAt { get; set; }
}
