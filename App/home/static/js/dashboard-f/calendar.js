const MONTH_NAMES = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
];

const DAY_NAMES = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

let currentYear;
let currentMonth;

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

export function initCalendar() {
    const grid = document.getElementById('calendarGrid');
    const monthYearLabel = document.getElementById('calMonthYear');
    const prevBtn = document.getElementById('calPrevBtn');
    const nextBtn = document.getElementById('calNextBtn');
    const taskForm = document.getElementById('addCalendarTaskForm');

    if (!grid) return;

    const today = new Date();
    currentYear = today.getFullYear();
    currentMonth = today.getMonth();

    function renderCalendar() {
        grid.innerHTML = '';

        // Render day names header
        DAY_NAMES.forEach(name => {
            const el = document.createElement('div');
            el.className = 'cal-day-name';
            el.textContent = name;
            grid.appendChild(el);
        });

        // First day of the month (0=Sun, 1=Mon, ... 6=Sat)
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        // Convert to Monday-based index: Mon=0, Tue=1, ..., Sun=6
        const startOffset = (firstDay + 6) % 7;

        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

        // Update month/year label
        if (monthYearLabel) {
            monthYearLabel.textContent = `${MONTH_NAMES[currentMonth]} ${currentYear}`;
        }

        // Empty filler cells for the start of the month (no previous month days shown)
        for (let i = 0; i < startOffset; i++) {
            const el = document.createElement('div');
            el.className = 'cal-day empty';
            el.textContent = '';
            grid.appendChild(el);
        }

        // Current month days
        for (let d = 1; d <= daysInMonth; d++) {
            const el = document.createElement('div');
            el.className = 'cal-day';

            const isToday = (
                d === today.getDate() &&
                currentMonth === today.getMonth() &&
                currentYear === today.getFullYear()
            );

            if (isToday) {
                el.classList.add('today');
            }

            el.textContent = d;

            // Tooltip for today
            if (isToday) {
                const tooltip = document.createElement('div');
                tooltip.className = 'cal-tooltip';
                tooltip.textContent = 'Сегодня';
                el.appendChild(tooltip);
            }

            grid.appendChild(el);
        }

        // Empty filler cells to complete the last row (no next month days shown)
        const totalCells = startOffset + daysInMonth;
        const remaining = totalCells % 7 === 0 ? 0 : 7 - (totalCells % 7);
        for (let i = 0; i < remaining; i++) {
            const el = document.createElement('div');
            el.className = 'cal-day empty';
            el.textContent = '';
            grid.appendChild(el);
        }
    }

    function prevMonth() {
        currentMonth--;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear--;
        }
        renderCalendar();
    }

    function nextMonth() {
        currentMonth++;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear++;
        }
        renderCalendar();
    }

    if (prevBtn) prevBtn.addEventListener('click', prevMonth);
    if (nextBtn) nextBtn.addEventListener('click', nextMonth);

    if (taskForm) {
        taskForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const titleInput = document.getElementById('taskTitle');
            const dateInput = document.getElementById('taskDate');
            const descInput = document.getElementById('taskDescription');

            if (titleInput && dateInput) {
                const title = titleInput.value.trim();
                const date = dateInput.value;
                const description = descInput ? descInput.value.trim() : '';

                if (title && date) {
                    showToast(`Задача "${title}" на ${date} сохранена (демо-режим).`);
                    taskForm.reset();
                }
            }
        });
    }

    renderCalendar();
}
