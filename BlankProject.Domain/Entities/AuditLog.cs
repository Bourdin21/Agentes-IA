namespace BlankProject.Domain.Entities;

/// <summary>
/// Registro de auditoria de cambios en entidades.
/// </summary>
public class AuditLog
{
    public long Id { get; set; }
    public string? UserId { get; set; }
    public string? UserName { get; set; }
    public string Action { get; set; } = string.Empty;        // Create, Update, Delete
    public string EntityName { get; set; } = string.Empty;
    public string? EntityId { get; set; }
    public string? OldValues { get; set; }                     // JSON
    public string? NewValues { get; set; }                     // JSON
    public string? AffectedColumns { get; set; }               // JSON array
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string? IpAddress { get; set; }
}
