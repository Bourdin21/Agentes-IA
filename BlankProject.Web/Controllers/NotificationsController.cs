using BlankProject.Application.Interfaces;
using BlankProject.Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;

namespace BlankProject.Web.Controllers;

[Authorize]
public class NotificationsController : Controller
{
    private readonly INotificationService _notificationService;
    private readonly UserManager<ApplicationUser> _userManager;

    public NotificationsController(
        INotificationService notificationService,
        UserManager<ApplicationUser> userManager)
    {
        _notificationService = notificationService;
        _userManager = userManager;
    }

    // GET: Notifications (pagina completa)
    public async Task<IActionResult> Index()
    {
        var userId = _userManager.GetUserId(User)!;
        var notifications = await _notificationService.GetRecentAsync(userId, 50);
        return View(notifications);
    }

    // GET: api para el dropdown del navbar (AJAX)
    [HttpGet]
    public async Task<IActionResult> GetRecent()
    {
        var userId = _userManager.GetUserId(User)!;
        var notifications = await _notificationService.GetRecentAsync(userId, 8);
        var unreadCount = await _notificationService.GetUnreadCountAsync(userId);
        return Json(new { unreadCount, notifications });
    }

    // POST: marcar una como leida
    [HttpPost]
    public async Task<IActionResult> MarkAsRead(int id)
    {
        var userId = _userManager.GetUserId(User)!;
        await _notificationService.MarkAsReadAsync(id, userId);
        return Ok();
    }

    // POST: marcar todas como leidas
    [HttpPost]
    public async Task<IActionResult> MarkAllAsRead()
    {
        var userId = _userManager.GetUserId(User)!;
        await _notificationService.MarkAllAsReadAsync(userId);
        return Ok();
    }
}
