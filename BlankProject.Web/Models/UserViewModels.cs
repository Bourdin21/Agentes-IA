using System.ComponentModel.DataAnnotations;
using BlankProject.Domain.Enums;

namespace BlankProject.Web.Models;

public class UserListViewModel
{
    public List<UserListItemViewModel> Users { get; set; } = new();
    public string? SearchTerm { get; set; }
    public string? RolFilter { get; set; }
    public string? StatusFilter { get; set; }
    public int Page { get; set; } = 1;
    public int PageSize { get; set; } = 15;
    public int TotalCount { get; set; }
    public int TotalPages => (int)Math.Ceiling((double)TotalCount / PageSize);
}

public class UserListItemViewModel
{
    public string Id { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Rol { get; set; } = string.Empty;
    public EstadoUsuario Estado { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class UserCreateViewModel
{
    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar los 200 caracteres.")]
    [Display(Name = "Nombre completo")]
    public string FullName { get; set; } = string.Empty;

    [Required(ErrorMessage = "El email es obligatorio.")]
    [EmailAddress(ErrorMessage = "El formato de email no es valido.")]
    [Display(Name = "Email")]
    public string Email { get; set; } = string.Empty;

    [Required(ErrorMessage = "La contrasena es obligatoria.")]
    [StringLength(100, MinimumLength = 6, ErrorMessage = "La contrasena debe tener al menos 6 caracteres.")]
    [DataType(DataType.Password)]
    [Display(Name = "Contrasena")]
    public string Password { get; set; } = string.Empty;

    [Required(ErrorMessage = "Confirme la contrasena.")]
    [DataType(DataType.Password)]
    [Display(Name = "Confirmar contrasena")]
    [Compare("Password", ErrorMessage = "Las contrasenas no coinciden.")]
    public string ConfirmPassword { get; set; } = string.Empty;

    [Required(ErrorMessage = "El rol es obligatorio.")]
    [Display(Name = "Rol")]
    public string Rol { get; set; } = string.Empty;

    [Display(Name = "Estado")]
    public EstadoUsuario Estado { get; set; } = EstadoUsuario.Activo;

    public List<string> AvailableRoles { get; set; } = new();
}

public class UserEditViewModel
{
    public string Id { get; set; } = string.Empty;

    [Required(ErrorMessage = "El nombre completo es obligatorio.")]
    [StringLength(200, ErrorMessage = "El nombre no puede superar los 200 caracteres.")]
    [Display(Name = "Nombre completo")]
    public string FullName { get; set; } = string.Empty;

    [Required(ErrorMessage = "El email es obligatorio.")]
    [EmailAddress(ErrorMessage = "El formato de email no es valido.")]
    [Display(Name = "Email")]
    public string Email { get; set; } = string.Empty;

    [StringLength(100, MinimumLength = 6, ErrorMessage = "La contrasena debe tener al menos 6 caracteres.")]
    [DataType(DataType.Password)]
    [Display(Name = "Nueva contrasena (dejar vacio para no cambiar)")]
    public string? NewPassword { get; set; }

    [DataType(DataType.Password)]
    [Display(Name = "Confirmar nueva contrasena")]
    [Compare("NewPassword", ErrorMessage = "Las contrasenas no coinciden.")]
    public string? ConfirmNewPassword { get; set; }

    [Required(ErrorMessage = "El rol es obligatorio.")]
    [Display(Name = "Rol")]
    public string Rol { get; set; } = string.Empty;

    [Display(Name = "Estado")]
    public EstadoUsuario Estado { get; set; }

    public List<string> AvailableRoles { get; set; } = new();
}

public class UserDetailsViewModel
{
    public string Id { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Rol { get; set; } = string.Empty;
    public EstadoUsuario Estado { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}
