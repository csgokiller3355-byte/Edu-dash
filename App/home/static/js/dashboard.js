import { initNavigation } from './dashboard-f/navigation.js';
import { initMiniGames } from './dashboard-f/minigames.js';
import { initCustomCursor } from './dashboard-f/cursor.js';
import { initShop } from './dashboard-f/shop.js';
import { initFeedback } from './dashboard-f/feedback.js';
import { initSettings } from './dashboard-f/settings.js';
import { initHomework } from './dashboard-f/homework.js'; // Подключаем логику ДЗ
import { initCalendar } from './dashboard-f/calendar.js'; // Подключаем календарь
import { initProjects } from './dashboard-f/projects.js'; // Подключаем проекты
import { initNotifications } from './dashboard-f/notifications.js'; // Подключаем уведомления
import { submitQuestion, submitAnswer } from './dashboard-f/qa.js';

window.submitQuestion = submitQuestion;
window.submitAnswer = submitAnswer;

function showToast(message) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    // Если элементов тоста нет на странице, просто выходим и не ломаем код
    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;
    toast.classList.remove('hidden');

    // Автоматическое скрытие через 3 секунды
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}
window.showToast = showToast;

document.addEventListener('DOMContentLoaded', () => {
    // Запускаем все модули интерфейса
    initNavigation();
    initHomework();     // <--- Вот здесь заработают вкладки ДЗ!
    initMiniGames();
    initCustomCursor();
    initShop();
    initFeedback();
    initSettings();
    initCalendar();     // <--- Динамический календарь с навигацией по месяцам
    initProjects();     // <--- Совместные работы по инициативе
    initNotifications(); // <--- Уведомления с ответами от поддержки
});