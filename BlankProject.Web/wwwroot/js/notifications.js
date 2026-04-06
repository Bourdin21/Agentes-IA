// Notification polling para el dropdown del navbar
(function () {
    var bell = document.getElementById('notifBell');
    if (!bell) return;

    var badge = document.getElementById('notifBadge');
    var list = document.getElementById('notifList');
    var markAllBtn = document.getElementById('markAllRead');

    function loadNotifications() {
        $.get('/Notifications/GetRecent', function (res) {
            // Badge
            if (res.unreadCount > 0) {
                badge.textContent = res.unreadCount > 99 ? '99+' : res.unreadCount;
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }

            // List
            if (!res.notifications || res.notifications.length === 0) {
                list.innerHTML = '<p class="text-center text-muted small py-3">Sin notificaciones</p>';
                return;
            }

            var html = '';
            res.notifications.forEach(function (n) {
                var readClass = n.isRead ? 'opacity-50' : '';
                var bg = n.isRead ? '' : 'style="background:#f0f7ff;"';
                var href = n.url ? n.url : '#';
                html += '<a href="' + href + '" class="dropdown-item py-2 px-3 border-bottom ' + readClass + '" ' + bg + ' data-notif-id="' + n.id + '">'
                    + '<div class="d-flex align-items-start">'
                    + '<i class="' + n.icon + ' me-2 mt-1 text-primary"></i>'
                    + '<div class="flex-grow-1">'
                    + '<div class="small fw-semibold">' + escapeHtml(n.title) + '</div>'
                    + '<div class="small text-muted text-truncate" style="max-width:250px;">' + escapeHtml(n.message) + '</div>'
                    + '<div class="text-muted" style="font-size:.7rem;">' + n.timeAgo + '</div>'
                    + '</div></div></a>';
            });
            list.innerHTML = html;

            // Click: marcar como leida
            list.querySelectorAll('[data-notif-id]').forEach(function (el) {
                el.addEventListener('click', function () {
                    var id = el.getAttribute('data-notif-id');
                    $.post('/Notifications/MarkAsRead', { id: id });
                });
            });
        });
    }

    // Marcar todas como leidas
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function (e) {
            e.preventDefault();
            $.post('/Notifications/MarkAllAsRead', function () {
                loadNotifications();
            });
        });
    }

    // Cargar al inicio y cada 30 segundos
    loadNotifications();
    setInterval(loadNotifications, 30000);

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text || ''));
        return div.innerHTML;
    }
})();
