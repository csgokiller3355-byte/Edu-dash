// static/js/feedback.js
export function initFeedback() {
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

    function showToast(message, type) {
        var toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText = 'position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;color:#fff;z-index:10000;font-size:14px;box-shadow:0 4px 12px rgba(0,0,0,0.15);';
        toast.style.background = type === 'error' ? '#e74c3c' : '#27ae60';
        document.body.appendChild(toast);
        setTimeout(function() { toast.remove(); }, 3000);
    }

    // Fetch and display admin replies
    function fetchAdminReplies() {
        fetch('/get-feedback-replies/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.status === 'ok' && data.count > 0) {
                    var section = document.getElementById('admin-replies-section');
                    var list = document.getElementById('admin-replies-list');
                    if (section && list) {
                        section.style.display = 'block';
                        list.innerHTML = '';
                        data.replies.forEach(function(reply) {
                            var card = document.createElement('div');
                            card.className = 'card';
                            card.style.marginBottom = '10px';
                            card.style.borderLeft = '3px solid var(--accent-primary)';
                            var dateStr = reply.replied_at ? new Date(reply.replied_at).toLocaleString('ru-RU') : '';
                            card.innerHTML =
                                '<p style="margin:0 0 4px 0;font-size:0.85em;color:var(--text-muted);">Ваш отзыв: ' + reply.feedback_text + '</p>' +
                                '<p style="margin:0;"><b>Администратор:</b> ' + reply.admin_reply + '</p>' +
                                '<small style="color:var(--text-muted);">' + dateStr + '</small>';
                            list.appendChild(card);
                        });
                    }
                }
            })
            .catch(function() { /* silently fail on poll */ });
    }

    const sendBtn = document.getElementById('send-feedback');
    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            var input = document.getElementById('feedback-input');
            var text = input.value.trim();
            if (!text) {
                showToast('Введите текст отзыва', 'error');
                return;
            }
            fetch('/submit-feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ text: text })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.status === 'ok') {
                    showToast(data.message, 'success');
                    input.value = '';
                    // Add the new feedback to the list
                    var list = document.getElementById('feedback-list');
                    if (list) {
                        var now = new Date();
                        var dateStr = now.toLocaleDateString('ru-RU') + ' ' + now.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});
                        var card = document.createElement('div');
                        card.className = 'card';
                        card.style.marginBottom = '10px';
                        card.innerHTML = '<p><b>' + data.user_name + ':</b> ' + data.text + '</p><small class="feedback-meta">' + dateStr + '</small>';
                        list.insertBefore(card, list.firstChild);
                    }
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(function() { showToast('Ошибка сети', 'error'); });
        });
    }

    // Fetch replies on init and poll every 30 seconds
    fetchAdminReplies();
    setInterval(fetchAdminReplies, 30000);
}