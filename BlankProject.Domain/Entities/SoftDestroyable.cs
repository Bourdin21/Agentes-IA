namespace BlankProject.Domain.Entities;

/// <summary>
/// Clase base con auditoria y soft delete.
/// El soft delete se determina por DeletedAt != null.
/// </summary>
public abstract class SoftDestroyable
{
    public int Id { get; set; }

    // Auditoria
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string? CreatedByUserId { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public string? UpdatedByUserId { get; set; }

    // Soft Delete
    public DateTime? DeletedAt { get; set; }
    public string? DeletedByUserId { get; set; }
}
