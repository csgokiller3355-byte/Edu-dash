// static/js/projects.js
export function initProjects() {
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

    // Join project buttons
    document.querySelectorAll('.join-project-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var projectId = this.getAttribute('data-project-id');
            var self = this;
            fetch('/join-project/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ initiative_id: projectId })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.status === 'ok') {
                    showToast(data.message, 'success');
                    var card = self.closest('.card');
                    var membersText = card.querySelector('.pill');
                    if (membersText) {
                        membersText.textContent = data.current_members + '/' + data.max_members;
                    }
                    self.outerHTML = '<button class="btn-sm" disabled style="margin-top: 10px; opacity: 0.6; cursor: default;">✓ Вы участвуете</button>';
                    window.userJoinedInitiatives = window.userJoinedInitiatives || [];
                    window.userJoinedInitiatives.push(projectId);
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(function() { showToast('Ошибка сети', 'error'); });
        });
    });

    // Create project modal
    var modal = document.getElementById('createProjectModal');
    var sectionsContainer = document.getElementById('dynamicSectionsContainer');
    
    if (modal) {
        function createSectionElement() {
            var div = document.createElement('div');
            div.className = 'dynamic-section';
            div.style.cssText = 'padding: 10px; border: 1px solid var(--border-card); border-radius: 8px; margin-bottom: 10px; position: relative; background: var(--bg-card);';
            div.innerHTML = `
                <input type="text" placeholder="Заголовок (например: Технологии)" class="theme-input section-title" style="width: calc(100% - 30px); margin-bottom: 5px;">
                <textarea placeholder="Описание..." rows="2" class="theme-input section-content" style="width: 100%;"></textarea>
                <button class="remove-section-btn" style="position: absolute; top: 5px; right: 5px; background: none; border: none; color: #e74c3c; cursor: pointer; font-size: 18px;">&times;</button>
            `;
            div.querySelector('.remove-section-btn').onclick = function() { div.remove(); };
            return div;
        }

        const addSectionBtn = document.getElementById('addSectionBtn');
        if (addSectionBtn) {
            addSectionBtn.addEventListener('click', function() {
                sectionsContainer.appendChild(createSectionElement());
            });
        }

        const createProjBtn = document.getElementById('create-proj-btn');
        if (createProjBtn) {
            createProjBtn.addEventListener('click', function() {
                modal.style.display = 'flex';
            });
        }

        const cancelBtn = document.getElementById('cancelCreateProject');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                modal.style.display = 'none';
                sectionsContainer.innerHTML = '';
            });
        }

        const confirmBtn = document.getElementById('confirmCreateProject');
        if (confirmBtn) {
            confirmBtn.addEventListener('click', function() {
                var title = document.getElementById('newProjectTitle').value.trim();
                var desc = document.getElementById('newProjectDesc').value.trim();
                var maxMembers = document.getElementById('newProjectMaxMembers').value;
                
                var sections = [];
                document.querySelectorAll('.dynamic-section').forEach(function(el) {
                    var sTitle = el.querySelector('.section-title').value.trim();
                    var sContent = el.querySelector('.section-content').value.trim();
                    if (sTitle && sContent) {
                        sections.push({ title: sTitle, content: sContent });
                    }
                });

                if (!title) {
                    showToast('Введите название проекта', 'error');
                    return;
                }

                fetch('/create-project/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({ 
                        title: title, 
                        description: desc, 
                        max_members: maxMembers,
                        sections: sections
                    })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.status === 'ok') {
                        showToast(data.message, 'success');
                        modal.style.display = 'none';
                        document.getElementById('newProjectTitle').value = '';
                        document.getElementById('newProjectDesc').value = '';
                        sectionsContainer.innerHTML = '';
                        location.reload();
                    } else {
                        showToast(data.message, 'error');
                    }
                })
                .catch(function() { showToast('Ошибка сети', 'error'); });
            });
        }
    }
}
