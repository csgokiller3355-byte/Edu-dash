// static/js/dashboard-f/notifications.js
// Notifications tab module — fetches and displays admin replies to support messages.

export function initNotifications() {
    function getCsrfToken() {
        var name = 'csrftoken';
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function fetchNotifications() {
        fetch('/get-feedback-replies/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var list = document.getElementById('notifications-list');
                if (!list) return;

                if (data.status === 'ok' && data.count > 0) {
                    list.innerHTML = '';
                    data.replies.forEach(function(reply) {
                        var card = document.createElement('div');
                        card.className = 'card';
                        card.style.marginBottom = '12px';
                        card.style.borderLeft = '3px solid var(--accent-primary)';

                        var dateStr = '';
                        if (reply.replied_at) {
                            var d = new Date(reply.replied_at);
                            dateStr = d.toLocaleDateString('ru-RU', {
                                day: '2-digit', month: '2-digit', year: 'numeric'
                            }) + ' ' + d.toLocaleTimeString('ru-RU', {
                                hour: '2-digit', minute: '2-digit'
                            });
                        }

                        card.innerHTML =
                            '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">' +
                                '<span style="font-size:0.85em;color:var(--text-muted);">📩 Ответ на ваше обращение</span>' +
                                '<small style="color:var(--text-muted);">' + dateStr + '</small>' +
                            '</div>' +
                            '<p style="margin:0 0 6px 0;font-size:0.9em;color:var(--text-secondary);">Ваш вопрос: <em>' + reply.feedback_text + '...</em></p>' +
                            '<div style="padding:10px 14px;background:var(--bg-pill);border-radius:8px;border-left:3px solid var(--accent-primary);">' +
                                '<p style="margin:0;font-size:0.95em;"><b>Администратор:</b> ' + reply.admin_reply + '</p>' +
                            '</div>';
                        list.appendChild(card);
                    });
                } else {
                    list.innerHTML =
                        '<div class="card" style="opacity:0.6;text-align:center;padding:2rem;">' +
                            '<p style="font-size:2rem;margin-bottom:0.5rem;">🔔</p>' +
                            '<p>У вас пока нет уведомлений.</p>' +
                            '<p style="font-size:0.85em;color:var(--text-muted);">Ответы от поддержки появятся здесь.</p>' +
                        '</div>';
                }
            })
            .catch(function() {
                // Silently fail on poll
            });
    }

    // Fetch on init and poll every 30 seconds
    fetchNotifications();
    setInterval(fetchNotifications, 30000);
}
