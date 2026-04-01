using System.Text.Json;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.ChangeTracking;
using BlankProject.Domain.Entities;

namespace BlankProject.Infrastructure.Data;

/// <summary>
/// DbContext principal de la aplicacion.
/// Hereda de IdentityDbContext para soporte de ASP.NET Core Identity.
/// Incluye: auditoria automatica, soft delete global y audit trail.
/// </summary>
public class AppDbContext : IdentityDbContext<ApplicationUser>
{
    private readonly IHttpContextAccessor? _httpContextAccessor;

    public AppDbContext(
        DbContextOptions<AppDbContext> options,
        IHttpContextAccessor? httpContextAccessor = null)
        : base(options)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public DbSet<AuditLog> AuditLogs { get; set; }
    public DbSet<Notification> Notifications { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<ApplicationUser>(entity =>
        {
            entity.Property(e => e.FullName).HasMaxLength(200).IsRequired();
            entity.Property(e => e.Estado).HasConversion<int>().HasDefaultValue(Domain.Enums.EstadoUsuario.Activo);
        });

        // Soft Delete: query filter global para todas las entidades que heredan de SoftDestroyable
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(SoftDestroyable).IsAssignableFrom(entityType.ClrType))
            {
                var method = typeof(AppDbContext)
                    .GetMethod(nameof(ApplySoftDeleteFilter),
                        System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
                    .MakeGenericMethod(entityType.ClrType);
                method.Invoke(null, [modelBuilder]);
            }
        }

        // AuditLog config
        modelBuilder.Entity<AuditLog>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Action).HasMaxLength(20).IsRequired();
            entity.Property(e => e.EntityName).HasMaxLength(200).IsRequired();
            entity.Property(e => e.EntityId).HasMaxLength(50);
            entity.Property(e => e.UserId).HasMaxLength(450);
            entity.Property(e => e.UserName).HasMaxLength(256);
            entity.Property(e => e.IpAddress).HasMaxLength(50);
            entity.HasIndex(e => e.Timestamp);
            entity.HasIndex(e => new { e.EntityName, e.EntityId });
        });

        // Notification config
        modelBuilder.Entity<Notification>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.UserId).HasMaxLength(450).IsRequired();
            entity.Property(e => e.Title).HasMaxLength(200).IsRequired();
            entity.Property(e => e.Message).HasMaxLength(1000).IsRequired();
            entity.Property(e => e.Url).HasMaxLength(500);
            entity.Property(e => e.Icon).HasMaxLength(50);
            entity.HasIndex(e => new { e.UserId, e.IsRead });
        });
    }

    private static void ApplySoftDeleteFilter<T>(ModelBuilder modelBuilder) where T : SoftDestroyable
    {
        modelBuilder.Entity<T>().HasQueryFilter(e => e.DeletedAt == null);
    }

    public override async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        var userId = GetCurrentUserId();
        var userName = GetCurrentUserName();
        var ip = GetCurrentIpAddress();
        var now = DateTime.UtcNow;

        var auditEntries = OnBeforeSaveChanges(userId, userName, ip, now);

        var result = await base.SaveChangesAsync(cancellationToken);

        await OnAfterSaveChanges(auditEntries, cancellationToken);

        return result;
    }

    public override int SaveChanges()
    {
        var userId = GetCurrentUserId();
        var userName = GetCurrentUserName();
        var ip = GetCurrentIpAddress();
        var now = DateTime.UtcNow;

        var auditEntries = OnBeforeSaveChanges(userId, userName, ip, now);

        var result = base.SaveChanges();

        OnAfterSaveChanges(auditEntries, CancellationToken.None).GetAwaiter().GetResult();

        return result;
    }

    private List<AuditEntry> OnBeforeSaveChanges(string? userId, string? userName, string? ip, DateTime now)
    {
        ChangeTracker.DetectChanges();
        var auditEntries = new List<AuditEntry>();

        foreach (var entry in ChangeTracker.Entries())
        {
            if (entry.Entity is AuditLog || entry.State == EntityState.Detached || entry.State == EntityState.Unchanged)
                continue;

            // Auditoria automatica en SoftDestroyable
            if (entry.Entity is SoftDestroyable softDestroyable)
            {
                if (entry.State == EntityState.Added)
                {
                    softDestroyable.CreatedAt = now;
                    softDestroyable.CreatedByUserId = userId;
                }
                else if (entry.State == EntityState.Modified)
                {
                    softDestroyable.UpdatedAt = now;
                    softDestroyable.UpdatedByUserId = userId;
                }
            }

            // Audit trail
            var auditEntry = new AuditEntry(entry)
            {
                UserId = userId,
                UserName = userName,
                IpAddress = ip,
                EntityName = entry.Entity.GetType().Name,
                Timestamp = now
            };

            foreach (var property in entry.Properties)
            {
                if (property.IsTemporary)
                {
                    auditEntry.TemporaryProperties.Add(property);
                    continue;
                }

                var propertyName = property.Metadata.Name;
                if (propertyName == "Id" && entry.State == EntityState.Added)
                {
                    auditEntry.TemporaryProperties.Add(property);
                    continue;
                }

                switch (entry.State)
                {
                    case EntityState.Added:
                        auditEntry.Action = "Create";
                        auditEntry.NewValues[propertyName] = property.CurrentValue;
                        break;

                    case EntityState.Deleted:
                        auditEntry.Action = "Delete";
                        auditEntry.OldValues[propertyName] = property.OriginalValue;
                        break;

                    case EntityState.Modified:
                        if (property.IsModified && !Equals(property.OriginalValue, property.CurrentValue))
                        {
                            auditEntry.Action = "Update";
                            auditEntry.AffectedColumns.Add(propertyName);
                            auditEntry.OldValues[propertyName] = property.OriginalValue;
                            auditEntry.NewValues[propertyName] = property.CurrentValue;
                        }
                        break;
                }
            }

            if (auditEntry.Action != null)
                auditEntries.Add(auditEntry);
        }

        foreach (var entry in auditEntries.Where(e => !e.HasTemporaryProperties))
        {
            AuditLogs.Add(entry.ToAuditLog());
        }

        return auditEntries.Where(e => e.HasTemporaryProperties).ToList();
    }

    private async Task OnAfterSaveChanges(List<AuditEntry> auditEntries, CancellationToken cancellationToken)
    {
        if (auditEntries.Count == 0) return;

        foreach (var entry in auditEntries)
        {
            foreach (var prop in entry.TemporaryProperties)
            {
                if (prop.Metadata.IsPrimaryKey())
                    entry.EntityId = prop.CurrentValue?.ToString();
                else
                    entry.NewValues[prop.Metadata.Name] = prop.CurrentValue;
            }
            AuditLogs.Add(entry.ToAuditLog());
        }

        await base.SaveChangesAsync(cancellationToken);
    }

    private string? GetCurrentUserId() =>
        _httpContextAccessor?.HttpContext?.User?.FindFirst(
            System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;

    private string? GetCurrentUserName() =>
        _httpContextAccessor?.HttpContext?.User?.Identity?.Name;

    private string? GetCurrentIpAddress() =>
        _httpContextAccessor?.HttpContext?.Connection.RemoteIpAddress?.ToString();
}

/// <summary>
/// Helper interno para construir registros de auditoria durante SaveChanges.
/// </summary>
internal class AuditEntry
{
    public AuditEntry(EntityEntry entry) { Entry = entry; }

    public EntityEntry Entry { get; }
    public string? UserId { get; set; }
    public string? UserName { get; set; }
    public string? Action { get; set; }
    public string EntityName { get; set; } = string.Empty;
    public string? EntityId { get; set; }
    public string? IpAddress { get; set; }
    public DateTime Timestamp { get; set; }
    public Dictionary<string, object?> OldValues { get; } = new();
    public Dictionary<string, object?> NewValues { get; } = new();
    public List<string> AffectedColumns { get; } = new();
    public List<PropertyEntry> TemporaryProperties { get; } = new();

    public bool HasTemporaryProperties => TemporaryProperties.Count > 0;

    public AuditLog ToAuditLog()
    {
        var entityId = EntityId ?? Entry.Properties
            .FirstOrDefault(p => p.Metadata.IsPrimaryKey())?.CurrentValue?.ToString();

        return new AuditLog
        {
            UserId = UserId,
            UserName = UserName,
            Action = Action!,
            EntityName = EntityName,
            EntityId = entityId,
            OldValues = OldValues.Count > 0 ? JsonSerializer.Serialize(OldValues) : null,
            NewValues = NewValues.Count > 0 ? JsonSerializer.Serialize(NewValues) : null,
            AffectedColumns = AffectedColumns.Count > 0 ? JsonSerializer.Serialize(AffectedColumns) : null,
            Timestamp = Timestamp,
            IpAddress = IpAddress
        };
    }
}
