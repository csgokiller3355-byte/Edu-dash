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

export function initHomework() {
    const hwTabButtons = document.querySelectorAll('.hw-tab-btn');
    const hwCards = document.querySelectorAll('.hw-card');
    const hwListView = document.getElementById('hwListView');
    const hwDetailView = document.getElementById('hwDetailView');
    const hwDetailBack = document.getElementById('hwDetailBack');
    const hwDetailTitle = document.getElementById('hwDetailTitle');
    const hwDetailStatus = document.getElementById('hwDetailStatus');
    const hwDetailGradeRow = document.getElementById('hwDetailGradeRow');
    const hwDetailGrade = document.getElementById('hwDetailGrade');
    const hwDetailSubmittedRow = document.getElementById('hwDetailSubmittedRow');
    const hwDetailSubmitted = document.getElementById('hwDetailSubmitted');
    const hwDetailDeadlineRow = document.getElementById('hwDetailDeadlineRow');
    const hwDetailDeadline = document.getElementById('hwDetailDeadline');
    const hwDetailDescription = document.getElementById('hwDetailDescription');

    if (!hwTabButtons.length || !hwCards.length) return;

    // --- Tab filtering ---
    hwTabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            hwTabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.getAttribute('data-filter');

            hwCards.forEach(card => {
                const category = card.getAttribute('data-category');

                if (category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });

    // --- Full-area detail view logic ---
    function openDetailView(card) {
        const title = card.getAttribute('data-title') || '';
        const description = card.getAttribute('data-description') || '';
        const status = card.getAttribute('data-status') || '';
        const grade = card.getAttribute('data-grade') || '';
        const submittedAt = card.getAttribute('data-submitted-at') || '';
        const deadline = card.getAttribute('data-deadline') || '';

        // Status labels
        const statusLabels = {
            'checking': 'На проверке',
            'graded': 'Оцененное',
            'process': 'В процессе'
        };

        hwDetailTitle.textContent = title;
        hwDetailStatus.textContent = statusLabels[status] || status;

        // Grade
        if (grade) {
            hwDetailGrade.textContent = grade;
            hwDetailGradeRow.style.display = 'flex';
        } else {
            hwDetailGradeRow.style.display = 'none';
        }

        // Submitted at
        if (submittedAt) {
            hwDetailSubmitted.textContent = submittedAt;
            hwDetailSubmittedRow.style.display = 'flex';
        } else {
            hwDetailSubmittedRow.style.display = 'none';
        }

        // Deadline
        if (deadline) {
            hwDetailDeadline.textContent = deadline;
            hwDetailDeadlineRow.style.display = 'flex';
        } else {
            hwDetailDeadlineRow.style.display = 'none';
        }

        // Description
        hwDetailDescription.textContent = description || 'Описание отсутствует.';

        // Hide list view, show detail view
        if (hwListView) hwListView.style.display = 'none';
        if (hwDetailView) hwDetailView.style.display = 'block';
    }

    function closeDetailView() {
        // Show list view, hide detail view
        if (hwListView) hwListView.style.display = 'block';
        if (hwDetailView) hwDetailView.style.display = 'none';

        // Restore the card filter based on the currently active tab button
        const activeFilterBtn = document.querySelector('.hw-tab-btn.active');
        if (activeFilterBtn) {
            const filter = activeFilterBtn.getAttribute('data-filter');
            hwCards.forEach(card => {
                const category = card.getAttribute('data-category');
                if (category === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    }

    // Click on card main area to open detail view (not on buttons)
    const clickableCards = document.querySelectorAll('.hw-card-clickable');
    clickableCards.forEach(card => {
        const cardMain = card.querySelector('.hw-card-main');
        if (cardMain) {
            cardMain.addEventListener('click', (e) => {
                // Don't open detail view if clicking a button
                if (e.target.closest('.hw-btn')) return;
                openDetailView(card);
            });
        }
    });

    // Back button
    if (hwDetailBack) {
        hwDetailBack.addEventListener('click', closeDetailView);
    }

    // Escape key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && hwDetailView && hwDetailView.style.display === 'block') {
            closeDetailView();
        }
    });

    // --- Submit / Replace buttons ---
    const submitBtns = document.querySelectorAll('.hw-btn-submit');
    const replaceBtns = document.querySelectorAll('.hw-btn-replace');

    submitBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const hwId = btn.getAttribute('data-id');
            const card = btn.closest('.hw-card');
            const title = card ? card.getAttribute('data-title') : '';

            // Show toast notification
            showToast(`Файл для "${title}" будет загружен (демо-режим, ID: ${hwId}).`);
        });
    });

    replaceBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const hwId = btn.getAttribute('data-id');
            const card = btn.closest('.hw-card');
            const title = card ? card.getAttribute('data-title') : '';

            // Show toast notification
            showToast(`Файл для "${title}" будет заменён (демо-режим, ID: ${hwId}).`);
        });
    });
}