using BlankProject.Domain.Entities;
using BlankProject.Domain.Enums;
using BlankProject.Infrastructure.Data;
using BlankProject.Web.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace BlankProject.Web.Controllers;

[Authorize(Policy = "RequireSuperUsuario")]
public class UsersController : Controller
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly ILogger<UsersController> _logger;

    public UsersController(UserManager<ApplicationUser> userManager, ILogger<UsersController> logger)
    {
        _userManager = userManager;
        _logger = logger;
    }

    // GET: Users
    public async Task<IActionResult> Index(string? search, string? rol, string? estado, int page = 1)
    {
        const int pageSize = 15;
        var query = _userManager.Users.AsQueryable();

        // Filtro busqueda
        if (!string.IsNullOrWhiteSpace(search))
        {
            var term = search.Trim().ToLower();
            query = query.Where(u =>
                u.FullName.ToLower().Contains(term) ||
                u.Email!.ToLower().Contains(term));
        }

        // Filtro estado
        if (!string.IsNullOrWhiteSpace(estado))
        {
            if (Enum.TryParse<EstadoUsuario>(estado, out var estadoEnum))
                query = query.Where(u => u.Estado == estadoEnum);
        }

        var allUsers = query.OrderBy(u => u.FullName).ToList();

        var usersWithRoles = new List<UserListItemViewModel>();
        foreach (var user in allUsers)
        {
            var roles = await _userManager.GetRolesAsync(user);
            var userRol = roles.FirstOrDefault() ?? "Sin rol";

            // No mostrar SuperUsuarios en el listado (no se gestionan a si mismos)
            if (userRol == SeedData.RolSuperUsuario)
                continue;

            // Filtro por rol
            if (!string.IsNullOrWhiteSpace(rol) && userRol != rol)
                continue;

            usersWithRoles.Add(new UserListItemViewModel
            {
                Id = user.Id,
                FullName = user.FullName,
                Email = user.Email!,
                Rol = userRol,
                Estado = user.Estado,
                CreatedAt = user.CreatedAt
            });
        }

        var totalCount = usersWithRoles.Count;
        var pagedUsers = usersWithRoles
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToList();

        var vm = new UserListViewModel
        {
            Users = pagedUsers,
            SearchTerm = search,
            RolFilter = rol,
            StatusFilter = estado,
            Page = page,
            PageSize = pageSize,
            TotalCount = totalCount
        };

        ViewBag.AvailableRoles = GetAssignableRoles();
        return View(vm);
    }

    // GET: Users/Details/id
    public async Task<IActionResult> Details(string id)
    {
        var user = await _userManager.FindByIdAsync(id);
        if (user == null) return NotFound();

        if (!await CanManageUser(user))
            return Forbid();

        var roles = await _userManager.GetRolesAsync(user);
        var vm = new UserDetailsViewModel
        {
            Id = user.Id,
            FullName = user.FullName,
            Email = user.Email!,
            Rol = roles.FirstOrDefault() ?? "Sin rol",
            Estado = user.Estado,
            CreatedAt = user.CreatedAt,
            UpdatedAt = user.UpdatedAt
        };
        return View(vm);
    }

    // GET: Users/Create
    public IActionResult Create()
    {
        var vm = new UserCreateViewModel
        {
            AvailableRoles = GetAssignableRoles(),
            Estado = EstadoUsuario.Activo
        };
        return View(vm);
    }

    // POST: Users/Create
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Create(UserCreateViewModel model)
    {
        model.AvailableRoles = GetAssignableRoles();

        if (!model.AvailableRoles.Contains(model.Rol))
        {
            ModelState.AddModelError("Rol", "No tiene permisos para asignar ese rol.");
        }

        if (!ModelState.IsValid)
            return View(model);

        var existingUser = await _userManager.FindByEmailAsync(model.Email);
        if (existingUser != null)
        {
            ModelState.AddModelError("Email", "Ya existe un usuario con ese email.");
            return View(model);
        }

        var user = new ApplicationUser
        {
            UserName = model.Email,
            Email = model.Email,
            FullName = model.FullName.Trim(),
            Estado = model.Estado,
            EmailConfirmed = true
        };

        var result = await _userManager.CreateAsync(user, model.Password);
        if (!result.Succeeded)
        {
            foreach (var error in result.Errors)
                ModelState.AddModelError(string.Empty, error.Description);
            return View(model);
        }

        await _userManager.AddToRoleAsync(user, model.Rol);
        _logger.LogInformation("Usuario creado: {Email} con rol {Rol} por {Admin}",
            user.Email, model.Rol, User.Identity?.Name);

        TempData["SuccessMessage"] = $"Usuario '{user.FullName}' creado correctamente.";
        return RedirectToAction(nameof(Index));
    }

    // GET: Users/Edit/id
    public async Task<IActionResult> Edit(string id)
    {
        var user = await _userManager.FindByIdAsync(id);
        if (user == null) return NotFound();

        if (!await CanManageUser(user))
            return Forbid();

        var roles = await _userManager.GetRolesAsync(user);
        var vm = new UserEditViewModel
        {
            Id = user.Id,
            FullName = user.FullName,
            Email = user.Email!,
            Rol = roles.FirstOrDefault() ?? SeedData.RolAdministrador,
            Estado = user.Estado,
            AvailableRoles = GetAssignableRoles()
        };
        return View(vm);
    }

    // POST: Users/Edit/id
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> Edit(UserEditViewModel model)
    {
        model.AvailableRoles = GetAssignableRoles();

        if (!model.AvailableRoles.Contains(model.Rol))
        {
            ModelState.AddModelError("Rol", "No tiene permisos para asignar ese rol.");
        }

        // Si no se ingresa nueva password, limpiar errores de validacion de password
        if (string.IsNullOrWhiteSpace(model.NewPassword))
        {
            ModelState.Remove("NewPassword");
            ModelState.Remove("ConfirmNewPassword");
        }

        if (!ModelState.IsValid)
            return View(model);

        var user = await _userManager.FindByIdAsync(model.Id);
        if (user == null) return NotFound();

        if (!await CanManageUser(user))
            return Forbid();

        // Verificar email unico
        var emailOwner = await _userManager.FindByEmailAsync(model.Email);
        if (emailOwner != null && emailOwner.Id != user.Id)
        {
            ModelState.AddModelError("Email", "Ya existe otro usuario con ese email.");
            return View(model);
        }

        user.FullName = model.FullName.Trim();
        user.Email = model.Email;
        user.UserName = model.Email;
        user.Estado = model.Estado;
        user.UpdatedAt = DateTime.UtcNow;

        var updateResult = await _userManager.UpdateAsync(user);
        if (!updateResult.Succeeded)
        {
            foreach (var error in updateResult.Errors)
                ModelState.AddModelError(string.Empty, error.Description);
            return View(model);
        }

        // Actualizar rol
        var currentRoles = await _userManager.GetRolesAsync(user);
        if (currentRoles.Count > 0)
            await _userManager.RemoveFromRolesAsync(user, currentRoles);
        await _userManager.AddToRoleAsync(user, model.Rol);

        // Cambiar password si se proporciono
        if (!string.IsNullOrWhiteSpace(model.NewPassword))
        {
            var token = await _userManager.GeneratePasswordResetTokenAsync(user);
            var passResult = await _userManager.ResetPasswordAsync(user, token, model.NewPassword);
            if (!passResult.Succeeded)
            {
                foreach (var error in passResult.Errors)
                    ModelState.AddModelError(string.Empty, error.Description);
                return View(model);
            }
        }

        _logger.LogInformation("Usuario editado: {Email} por {Admin}",
            user.Email, User.Identity?.Name);

        TempData["SuccessMessage"] = $"Usuario '{user.FullName}' actualizado correctamente.";
        return RedirectToAction(nameof(Index));
    }

    // POST: Users/ToggleEstado/id
    [HttpPost]
    [ValidateAntiForgeryToken]
    public async Task<IActionResult> ToggleEstado(string id)
    {
        var user = await _userManager.FindByIdAsync(id);
        if (user == null) return NotFound();

        if (!await CanManageUser(user))
            return Forbid();

        user.Estado = user.Estado == EstadoUsuario.Activo
            ? EstadoUsuario.Bloqueado
            : EstadoUsuario.Activo;
        user.UpdatedAt = DateTime.UtcNow;
        await _userManager.UpdateAsync(user);

        var estadoStr = user.Estado == EstadoUsuario.Activo ? "desbloqueado" : "bloqueado";
        _logger.LogInformation("Usuario {Estado}: {Email} por {Admin}",
            estadoStr, user.Email, User.Identity?.Name);

        TempData["SuccessMessage"] = $"Usuario '{user.FullName}' {estadoStr} correctamente.";
        return RedirectToAction(nameof(Index));
    }

    // --- Helpers ---

    /// <summary>
    /// Devuelve los roles que el SuperUsuario puede asignar (solo Administrador).
    /// </summary>
    private static List<string> GetAssignableRoles()
    {
        return [SeedData.RolAdministrador];
    }

    /// <summary>
    /// Verifica si el usuario actual puede gestionar al usuario objetivo.
    /// SuperUsuario puede gestionar Usuarios (no otros SuperUsuarios).
    /// </summary>
    private async Task<bool> CanManageUser(ApplicationUser targetUser)
    {
        var targetRoles = await _userManager.GetRolesAsync(targetUser);
        var targetRol = targetRoles.FirstOrDefault() ?? string.Empty;

        // No se pueden gestionar otros SuperUsuarios
        return targetRol != SeedData.RolSuperUsuario;
    }
}
