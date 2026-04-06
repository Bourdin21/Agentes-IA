// SweetAlert2: confirmación reutilizable para botones con clase .btn-swal-confirm
document.addEventListener('click', function (e) {
    var btn = e.target.closest('.btn-swal-confirm');
    if (!btn) return;

    e.preventDefault();
    var message = btn.getAttribute('data-message') || '¿Está seguro?';

    Swal.fire({
        title: 'Confirmar',
        text: message,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#2b9de4',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'Sí, continuar',
        cancelButtonText: 'Cancelar'
    }).then(function (result) {
        if (result.isConfirmed) {
            var form = btn.closest('form');
            if (form) {
                form.submit();
            }
        }
    });
});

(function () {
    function scrollActiveSidebarLinkIntoView() {
        var sidebarNav = document.querySelector('.ov-sidebar-nav');
        if (!sidebarNav) return;

        var activeLink = sidebarNav.querySelector('.ov-sidebar-link.active');
        if (!activeLink) return;

        window.requestAnimationFrame(function () {
            var navRect = sidebarNav.getBoundingClientRect();
            var linkRect = activeLink.getBoundingClientRect();
            var targetScrollTop = sidebarNav.scrollTop + (linkRect.top - navRect.top) - ((sidebarNav.clientHeight - activeLink.offsetHeight) / 2);

            sidebarNav.scrollTo({
                top: Math.max(targetScrollTop, 0),
                behavior: 'smooth'
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', scrollActiveSidebarLinkIntoView, { once: true });
        return;
    }

    scrollActiveSidebarLinkIntoView();
})();
