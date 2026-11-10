// static/js/dashboard-f/settings.js
// Settings tab module — uses event delegation for reliable binding regardless of tab visibility.

function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    if (!toast || !toastMessage) {
        alert(message);
        return;
    }
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function applyTheme(theme) {
    const body = document.body;
    body.classList.remove('theme-dark', 'theme-light');

    if (theme === 'light') {
        body.classList.add('theme-light');
    } else if (theme === 'dark') {
        body.classList.add('theme-dark');
    } else if (theme === 'auto') {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        body.classList.add(prefersDark ? 'theme-dark' : 'theme-light');
    }
}

function applyCustomCursor(enabled) {
    const cursor = document.getElementById('customCursor');
    if (cursor) {
        cursor.style.display = enabled ? 'block' : 'none';
    }
}

function restorePreferences() {
    // Restore saved preferences from localStorage to DOM elements
    const savedPrivacy = localStorage.getItem('settings_privacy');
    const savedNotifications = localStorage.getItem('settings_notifications');
    const savedTheme = localStorage.getItem('settings_theme');
    const savedCustomCursor = localStorage.getItem('customCursorEnabled');

    if (savedPrivacy !== null) {
        const el = document.getElementById('togglePrivacy');
        if (el) el.checked = savedPrivacy === 'true';
    }
    if (savedNotifications !== null) {
        const el = document.getElementById('toggleNotifications');
        if (el) el.checked = savedNotifications === 'true';
    }
    if (savedTheme) {
        const el = document.getElementById('selectTheme');
        if (el) {
            el.value = savedTheme;
            applyTheme(savedTheme);
        }
    } else {
        // Default to dark theme if no preference saved
        const el = document.getElementById('selectTheme');
        if (el) el.value = 'dark';
        applyTheme('dark');
    }
    if (savedCustomCursor !== null) {
        const el = document.getElementById('toggleCustomCursor');
        if (el) el.checked = savedCustomCursor === 'true';
        // Apply cursor visibility immediately on restore
        applyCustomCursor(savedCustomCursor === 'true');
    }
}

export function initSettings() {
    // Restore saved preferences immediately on init
    restorePreferences();

    // --- Event delegation: CLICK events on document ---
    document.addEventListener('click', (e) => {
        const target = e.target;
        const id = target.id;

        // 1. Profile change button
        if (id === 'btnProfile' || target.closest('#btnProfile')) {
            e.preventDefault();
            const name = prompt('Введите ваше полное имя:');
            if (name && name.trim()) {
                showToast('Профиль обновлён!');
            }
            return;
        }

        // 5. Support button — redirect to support chat
        if (id === 'btnSupport' || target.closest('#btnSupport')) {
            e.preventDefault();
            window.location.href = '/support-chat/';
            return;
        }

        // 6. Reset settings button
        if (id === 'btnResetSettings' || target.closest('#btnResetSettings')) {
            e.preventDefault();
            if (confirm('Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?')) {
                // Clear localStorage
                localStorage.removeItem('settings_privacy');
                localStorage.removeItem('settings_notifications');
                localStorage.removeItem('settings_theme');
                localStorage.removeItem('customCursorEnabled');

                // Reset DOM elements to defaults
                const privacy = document.getElementById('togglePrivacy');
                const notifications = document.getElementById('toggleNotifications');
                const theme = document.getElementById('selectTheme');

                if (privacy) privacy.checked = true;
                if (notifications) notifications.checked = true;
                if (theme) theme.value = 'dark';
                const customCursor = document.getElementById('toggleCustomCursor');
                if (customCursor) customCursor.checked = true;
                applyTheme('dark');
                applyCustomCursor(true);

                showToast('Настройки сброшены к значениям по умолчанию');
            }
            return;
        }
    });

    // --- Event delegation: CHANGE events on document ---
    document.addEventListener('change', (e) => {
        const target = e.target;
        const id = target.id;

        // 2. Privacy toggle
        if (id === 'togglePrivacy') {
            const value = target.checked;
            localStorage.setItem('settings_privacy', String(value));
            showToast(value ? 'Конфиденциальность включена' : 'Конфиденциальность выключена');
            return;
        }

        // 3. Notifications toggle
        if (id === 'toggleNotifications') {
            const value = target.checked;
            localStorage.setItem('settings_notifications', String(value));
            showToast(value ? 'Уведомления включены' : 'Уведомления выключены');
            return;
        }

        // 4. Theme selection
        if (id === 'selectTheme') {
            const theme = target.value;
            localStorage.setItem('settings_theme', theme);
            applyTheme(theme);
            const labels = { dark: 'Тёмная тема', light: 'Светлая тема', auto: 'Системная тема' };
            showToast(`Тема: ${labels[theme] || theme}`);
            return;
        }

        // 4b. Custom cursor toggle
        if (id === 'toggleCustomCursor') {
            const value = target.checked;
            localStorage.setItem('customCursorEnabled', String(value));
            applyCustomCursor(value);
            showToast(value ? 'Кастомный курсор включён' : 'Кастомный курсор выключён');
            return;
        }
    });

    // --- Cursor Style Management ---

    // 4c. Create cursor button — open modal with CSS editor
    document.addEventListener('click', (e) => {
        if (e.target.id === 'btnCreateCursor' || e.target.closest('#btnCreateCursor')) {
            e.preventDefault();
            showCreateCursorModal();
            return;
        }

        // 4d. My cursors button — show list of user's cursors
        if (e.target.id === 'btnMyCursors' || e.target.closest('#btnMyCursors')) {
            e.preventDefault();
            showMyCursorsModal();
            return;
        }

        // 4e. Browse cursors button — show public cursor gallery
        if (e.target.id === 'btnBrowseCursors' || e.target.closest('#btnBrowseCursors')) {
            e.preventDefault();
            showPublicCursorsModal();
            return;
        }
    });
}

// --- Cursor Modal Helpers ---

function removeCursorModal() {
    const existing = document.getElementById('cursorModalOverlay');
    if (existing) existing.remove();
}

function showCreateCursorModal() {
    removeCursorModal();
    const overlay = document.createElement('div');
    overlay.id = 'cursorModalOverlay';
    overlay.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/60';
    overlay.innerHTML = `
        <div class="bg rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto shadow-2xl" style="background: var(--bg-setting-card); border: 1px solid var(--border-setting-card);">
            <h3 class="text-xl font-bold mb-4" style="color: var(--text-heading);">✨ Создать свой курсор</h3>
            <p class="text-sm mb-4" style="color: var(--text-secondary);">Напишите CSS для стилизации курсора. Используйте <code class="px-1 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-xs">body { cursor: url(...) }</code> или другие свойства.</p>
            <label class="block text-sm font-semibold mb-1" style="color: var(--text-secondary);">Название</label>
            <input type="text" id="cursorNameInput" class="w-full px-3 py-2 rounded-xl mb-3 text-sm focus:outline-none focus:border-indigo-500" style="background: var(--bg-input); color: var(--text-primary); border: 1px solid var(--border-input);" placeholder="Мой крутой курсор">
            <label class="block text-sm font-semibold mb-1" style="color: var(--text-secondary);">CSS-код</label>
            <textarea id="cursorCssInput" rows="8" class="w-full px-3 py-2 rounded-xl mb-3 text-xs font-mono focus:outline-none focus:border-indigo-500 leading-relaxed" style="background: var(--bg-input); color: var(--text-primary); border: 1px solid var(--border-input);" placeholder="body {&#10;  cursor: url('data:image/svg+xml,...'), auto;&#10;}"></textarea>
            <label class="flex items-center gap-2 mb-4 cursor-pointer">
                <input type="checkbox" id="cursorPublicToggle" class="rounded">
                <span class="text-sm" style="color: var(--text-secondary);">Опубликовать в галерею</span>
            </label>
            <div class="flex gap-3">
                <button id="cursorSaveBtn" class="flex-1 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 text-white font-bold rounded-xl shadow transition">💾 Сохранить</button>
                <button id="cursorPreviewBtn" class="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow transition">👁 Предпросмотр</button>
                <button id="cursorCloseBtn" class="px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white font-bold rounded-xl shadow transition">✕</button>
            </div>
            <div id="cursorPreviewArea" class="mt-4 p-4 rounded-xl border-2 border-dashed hidden" style="border-color: var(--border-card);">
                <p class="text-sm mb-2" style="color: var(--text-secondary);">Предпросмотр курсора:</p>
                <div id="cursorPreviewBox" class="h-32 flex items-center justify-center rounded-lg" style="background: var(--bg-sub-btn);">
                    <span style="color: var(--text-muted);">Наведите мышкой сюда</span>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) removeCursorModal();
    });

    // Close button
    document.getElementById('cursorCloseBtn').addEventListener('click', removeCursorModal);

    // Preview button
    document.getElementById('cursorPreviewBtn').addEventListener('click', () => {
        const css = document.getElementById('cursorCssInput').value;
        const previewArea = document.getElementById('cursorPreviewArea');
        const previewBox = document.getElementById('cursorPreviewBox');
        if (!css.trim()) {
            showToast('Введите CSS-код для предпросмотра');
            return;
        }
        previewArea.classList.remove('hidden');
        previewBox.style.cssText += ';' + css;
        // Also apply to the preview box itself
        const styleEl = document.createElement('style');
        styleEl.id = 'cursorPreviewStyle';
        const old = document.getElementById('cursorPreviewStyle');
        if (old) old.remove();
        styleEl.textContent = css.replace(/body/g, '#cursorPreviewBox').replace(/html/g, '#cursorPreviewBox');
        document.head.appendChild(styleEl);
        showToast('Предпросмотр активен');
    });

    // Save button
    document.getElementById('cursorSaveBtn').addEventListener('click', () => {
        const name = document.getElementById('cursorNameInput').value.trim();
        const cssCode = document.getElementById('cursorCssInput').value.trim();
        const isPublic = document.getElementById('cursorPublicToggle').checked;

        if (!name) {
            showToast('Введите название курсора');
            return;
        }
        if (!cssCode) {
            showToast('Введите CSS-код');
            return;
        }

        fetch('/save-cursor-style/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ name, css_code: cssCode, is_public: isPublic }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'ok') {
                showToast(data.message);
                removeCursorModal();
                // Apply the cursor CSS
                applyCustomCursorCss(cssCode);
            } else {
                showToast(data.message || 'Ошибка');
            }
        })
        .catch(err => {
            showToast('Ошибка сети');
            console.error(err);
        });
    });
}

function showMyCursorsModal() {
    removeCursorModal();
    const overlay = document.createElement('div');
    overlay.id = 'cursorModalOverlay';
    overlay.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/60';
    overlay.innerHTML = `
        <div class="bg rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto shadow-2xl" style="background: var(--bg-setting-card); border: 1px solid var(--border-setting-card);">
            <h3 class="text-xl font-bold mb-4" style="color: var(--text-heading);">🖱 Мои курсоры</h3>
            <div id="myCursorsList" class="space-y-3">
                <p class="text-sm text-center py-4" style="color: var(--text-muted);">Загрузка...</p>
            </div>
            <div class="flex justify-end mt-4">
                <button id="cursorCloseBtn" class="px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white font-bold rounded-xl shadow transition">Закрыть</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) removeCursorModal(); });
    document.getElementById('cursorCloseBtn').addEventListener('click', removeCursorModal);

    // Fetch cursors
    fetch('/my-cursor-styles/')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('myCursorsList');
            if (data.status === 'ok' && data.count > 0) {
                list.innerHTML = data.cursors.map(c => `
                    <div class="p-3 rounded-xl border flex items-center justify-between" style="background: var(--bg-sub-btn); border-color: var(--border-card);">
                        <div>
                            <p class="text-sm font-bold" style="color: var(--text-primary);">${escapeHtml(c.name)}</p>
                            <p class="text-xs" style="color: var(--text-muted);">${c.is_public ? '🌐 Публичный' : '🔒 Частный'}</p>
                        </div>
                        <div class="flex gap-2">
                            <button class="apply-cursor-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-500" data-css="${escapeHtml(c.css_code)}">Применить</button>
                            <button class="delete-cursor-btn px-3 py-1.5 rounded-lg text-xs font-bold bg-red-600 text-white hover:bg-red-500" data-id="${c.id}">✕</button>
                        </div>
                    </div>
                `).join('');

                // Apply buttons
                list.querySelectorAll('.apply-cursor-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        applyCustomCursorCss(btn.dataset.css);
                        showToast('Курсор применён!');
                    });
                });

                // Delete buttons
                list.querySelectorAll('.delete-cursor-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        if (!confirm('Удалить этот курсор?')) return;
                        fetch('/delete-cursor-style/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken(),
                            },
                            body: JSON.stringify({ cursor_id: btn.dataset.id }),
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                showToast(data.message);
                                showMyCursorsModal();
                            } else {
                                showToast(data.message || 'Ошибка');
                            }
                        });
                    });
                });
            } else {
                list.innerHTML = '<p class="text-sm text-center py-4" style="color: var(--text-muted);">У вас пока нет сохранённых курсоров.</p>';
            }
        })
        .catch(() => {
            document.getElementById('myCursorsList').innerHTML = '<p class="text-sm text-center py-4 text-red-400">Ошибка загрузки</p>';
        });
}

function showPublicCursorsModal() {
    removeCursorModal();
    const overlay = document.createElement('div');
    overlay.id = 'cursorModalOverlay';
    overlay.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/60';
    overlay.innerHTML = `
        <div class="bg rounded-2xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto shadow-2xl" style="background: var(--bg-setting-card); border: 1px solid var(--border-setting-card);">
            <h3 class="text-xl font-bold mb-4" style="color: var(--text-heading);">🌐 Галерея курсоров</h3>
            <p class="text-sm mb-4" style="color: var(--text-secondary);">Опубликованные мышки от других пользователей</p>
            <div id="publicCursorsList" class="space-y-3">
                <p class="text-sm text-center py-4" style="color: var(--text-muted);">Загрузка...</p>
            </div>
            <div class="flex justify-end mt-4">
                <button id="cursorCloseBtn" class="px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white font-bold rounded-xl shadow transition">Закрыть</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) removeCursorModal(); });
    document.getElementById('cursorCloseBtn').addEventListener('click', removeCursorModal);

    // Fetch public cursors
    fetch('/public-cursor-styles/')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('publicCursorsList');
            if (data.status === 'ok' && data.count > 0) {
                list.innerHTML = data.cursors.map(c => `
                    <div class="p-3 rounded-xl border" style="background: var(--bg-sub-btn); border-color: var(--border-card);">
                        <div class="flex items-center justify-between mb-2">
                            <p class="text-sm font-bold" style="color: var(--text-primary);">${escapeHtml(c.name)}</p>
                            <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300">${escapeHtml(c.creator)}</span>
                        </div>
                        <p class="text-xs mb-2 font-mono truncate" style="color: var(--text-muted);">${escapeHtml(c.css_code.substring(0, 80))}...</p>
                        <button class="apply-public-cursor-btn w-full py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:opacity-90" data-id="${c.id}">
                            ✨ Применить к себе
                        </button>
                    </div>
                `).join('');

                list.querySelectorAll('.apply-public-cursor-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        fetch('/apply-cursor-style/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken(),
                            },
                            body: JSON.stringify({ cursor_id: btn.dataset.id }),
                        })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                showToast(data.message);
                                applyCustomCursorCss(data.css_code);
                                removeCursorModal();
                            } else {
                                showToast(data.message || 'Ошибка');
                            }
                        });
                    });
                });
            } else {
                list.innerHTML = '<p class="text-sm text-center py-4" style="color: var(--text-muted);">Пока нет опубликованных курсоров.</p>';
            }
        })
        .catch(() => {
            document.getElementById('publicCursorsList').innerHTML = '<p class="text-sm text-center py-4 text-red-400">Ошибка загрузки</p>';
        });
}

function applyCustomCursorCss(cssCode) {
    // Remove old custom cursor style
    const old = document.getElementById('customCursorStyle');
    if (old) old.remove();

    // Add new style
    const style = document.createElement('style');
    style.id = 'customCursorStyle';
    style.textContent = cssCode;
    document.head.appendChild(style);

    // Save to localStorage
    localStorage.setItem('customCursorCss', cssCode);
}

function getCsrfToken() {
    let token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    if (token) return token.split('=')[1];
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}