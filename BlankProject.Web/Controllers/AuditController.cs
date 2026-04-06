using System.Security.Claims;
using BlankProject.Application.DTOs;
using BlankProject.Infrastructure.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BlankProject.Web.Controllers;

[Authorize(Policy = "RequireAdministracion")]
public class AuditController : Controller
{
    private readonly AppDbContext _context;

    public AuditController(AppDbContext context)
    {
        _context = context;
    }

    private string GetUsuarioId() =>
        User.FindFirstValue(ClaimTypes.NameIdentifier)!;

    private bool EsSuperUsuario() =>
        User.IsInRole("SuperUsuario");

    // GET: Audit (vista con DataTables)
    public IActionResult Index()
    {
        return View();
    }

    // POST: DataTables server-side
    [HttpPost]
    public async Task<IActionResult> GetData()
    {
        var request = new DataTableRequest
        {
            Draw = int.TryParse(Request.Form["draw"], out var d) ? d : 1,
            Start = int.TryParse(Request.Form["start"], out var s) ? s : 0,
            Length = int.TryParse(Request.Form["length"], out var l) ? l : 15,
            SearchValue = Request.Form["search[value]"].ToString(),
            SortColumn = GetSortColumn(),
            SortDirection = Request.Form["order[0][dir]"].ToString()
        };

        var query = _context.AuditLogs.AsNoTracking().AsQueryable();

        // Administradores solo ven sus propios registros de auditoria
        if (!EsSuperUsuario())
        {
            var userId = GetUsuarioId();
            query = query.Where(a => a.UserId == userId);
        }

        // Busqueda
        if (!string.IsNullOrWhiteSpace(request.SearchValue))
        {
            var term = request.SearchValue.ToLower();
            query = query.Where(a =>
                a.EntityName.ToLower().Contains(term) ||
                (a.UserName != null && a.UserName.ToLower().Contains(term)) ||
                a.Action.ToLower().Contains(term) ||
                (a.EntityId != null && a.EntityId.Contains(term)));
        }

        // Total: respetar filtro de usuario
        var baseQuery = _context.AuditLogs.AsNoTracking().AsQueryable();
        if (!EsSuperUsuario())
            baseQuery = baseQuery.Where(a => a.UserId == GetUsuarioId());
        var totalRecords = await baseQuery.CountAsync();
        var filteredRecords = await query.CountAsync();

        // Ordenamiento
        query = request.SortColumn switch
        {
            "timestamp" => request.SortDirection == "asc" ? query.OrderBy(a => a.Timestamp) : query.OrderByDescending(a => a.Timestamp),
            "userName" => request.SortDirection == "asc" ? query.OrderBy(a => a.UserName) : query.OrderByDescending(a => a.UserName),
            "action" => request.SortDirection == "asc" ? query.OrderBy(a => a.Action) : query.OrderByDescending(a => a.Action),
            "entityName" => request.SortDirection == "asc" ? query.OrderBy(a => a.EntityName) : query.OrderByDescending(a => a.EntityName),
            _ => query.OrderByDescending(a => a.Timestamp)
        };

        var data = await query
            .Skip(request.Start)
            .Take(request.Length)
            .Select(a => new
            {
                a.Id,
                a.UserName,
                a.Action,
                a.EntityName,
                a.EntityId,
                Timestamp = a.Timestamp.ToString("dd/MM/yyyy HH:mm:ss"),
                a.AffectedColumns,
                a.OldValues,
                a.NewValues,
                a.IpAddress
            })
            .ToListAsync();

        return Json(new DataTableResponse<object>
        {
            Draw = request.Draw,
            RecordsTotal = totalRecords,
            RecordsFiltered = filteredRecords,
            Data = data.Cast<object>().ToList()
        });
    }

    private string GetSortColumn()
    {
        var colIndex = Request.Form["order[0][column]"].ToString();
        var colName = Request.Form[$"columns[{colIndex}][data]"].ToString();
        return colName;
    }
}
