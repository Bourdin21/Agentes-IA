using BlankProject.Application.DTOs;

namespace BlankProject.Application.Interfaces;

/// <summary>
/// Servicio de notificaciones in-app.
/// </summary>
public interface INotificationService
{
    Task CreateAsync(string userId, string title, string message, string? url = null, string icon = "fas fa-bell");
    Task<List<NotificationDto>> GetRecentAsync(string userId, int take = 10);
    Task<int> GetUnreadCountAsync(string userId);
    Task MarkAsReadAsync(int notificationId, string userId);
    Task MarkAllAsReadAsync(string userId);
}
