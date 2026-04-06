using System.ComponentModel.DataAnnotations;
using BlankProject.Domain.Enums;

namespace BlankProject.Web.Models;

public class PerfilViewModel
{
    public string NombreCompleto { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Rol { get; set; } = string.Empty;
    public EstadoUsuario Estado { get; set; }
    public DateTime CreadoEl { get; set; }
}

public class CambiarPasswordViewModel
{
    [Required(ErrorMessage = "La contraseña actual es obligatoria.")]
    [DataType(DataType.Password)]
    [Display(Name = "Contraseña actual")]
    public string PasswordActual { get; set; } = string.Empty;

    [Required(ErrorMessage = "La nueva contraseña es obligatoria.")]
    [StringLength(100, MinimumLength = 6, ErrorMessage = "La contraseña debe tener al menos 6 caracteres.")]
    [DataType(DataType.Password)]
    [Display(Name = "Nueva contraseña")]
    public string NuevaPassword { get; set; } = string.Empty;

    [Required(ErrorMessage = "Confirme la nueva contraseña.")]
    [DataType(DataType.Password)]
    [Display(Name = "Confirmar nueva contraseña")]
    [Compare("NuevaPassword", ErrorMessage = "Las contraseñas no coinciden.")]
    public string ConfirmarPassword { get; set; } = string.Empty;
}
