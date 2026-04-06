using BlankProject.Application.DTOs;
using BlankProject.Application.Interfaces;
using BlankProject.Domain.Entities;
using BlankProject.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace BlankProject.Infrastructure.Services;

public class NotificationService : INotificationService
{
    private readonly AppDbContext _context;

    public NotificationService(AppDbContext context)
    {
        _context = context;
    }

    public async Task CreateAsync(string userId, string title, string message, string? url = null, string icon = "fas fa-bell")
    {
        _context.Notifications.Add(new Notification
        {
            UserId = userId,
            Title = title,
            Message = message,
            Url = url,
            Icon = icon
        });
        await _context.SaveChangesAsync();
    }

    public async Task<List<NotificationDto>> GetRecentAsync(string userId, int take = 10)
    {
        var notifications = await _context.Notifications
            .Where(n => n.UserId == userId)
            .OrderByDescending(n => n.CreatedAt)
            .Take(take)
            .Select(n => new NotificationDto
            {
                Id = n.Id,
                Title = n.Title,
                Message = n.Message,
                Url = n.Url,
                Icon = n.Icon,
                IsRead = n.IsRead,
                CreatedAt = n.CreatedAt
            })
            .ToListAsync();

        foreach (var n in notifications)
            n.TimeAgo = GetTimeAgo(n.CreatedAt);

        return notifications;
    }

    public async Task<int> GetUnreadCountAsync(string userId)
    {
        return await _context.Notifications
            .CountAsync(n => n.UserId == userId && !n.IsRead);
    }

    public async Task MarkAsReadAsync(int notificationId, string userId)
    {
        var notification = await _context.Notifications
            .FirstOrDefaultAsync(n => n.Id == notificationId && n.UserId == userId);

        if (notification != null && !notification.IsRead)
        {
            notification.IsRead = true;
            notification.ReadAt = DateTime.UtcNow;
            await _context.SaveChangesAsync();
        }
    }

    public async Task MarkAllAsReadAsync(string userId)
    {
        var unread = await _context.Notifications
            .Where(n => n.UserId == userId && !n.IsRead)
            .ToListAsync();

        var now = DateTime.UtcNow;
        foreach (var n in unread)
        {
            n.IsRead = true;
            n.ReadAt = now;
        }

        await _context.SaveChangesAsync();
    }

    private static string GetTimeAgo(DateTime date)
    {
        var span = DateTime.UtcNow - date;
        if (span.TotalMinutes < 1) return "ahora";
        if (span.TotalMinutes < 60) return $"hace {(int)span.TotalMinutes}m";
        if (span.TotalHours < 24) return $"hace {(int)span.TotalHours}h";
        if (span.TotalDays < 30) return $"hace {(int)span.TotalDays}d";
        return date.ToString("dd/MM/yyyy");
    }
}
