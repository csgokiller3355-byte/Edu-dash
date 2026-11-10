// static/js/qa.js

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

function getCsrfToken() {
    var name = 'csrftoken';
    var value = null;
    if (document.cookie) {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return value;
}

export function submitQuestion() {
    const titleInput = document.getElementById('newQuestionTitle');
    const contentInput = document.getElementById('newQuestionContent');

    if (!titleInput || !contentInput) return;

    const title = titleInput.value.trim();
    const content = contentInput.value.trim();

    if (!title || !content) {
        showToast('Пожалуйста, заполните все поля.');
        return;
    }

    const csrfToken = getCsrfToken();

    fetch('/api/qa/ask/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ title, content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showToast('Вопрос успешно опубликован!');
            document.getElementById('askQuestionModal').classList.add('hidden');
            titleInput.value = '';
            contentInput.value = '';
            location.reload();
        } else {
            showToast(data.message || 'Ошибка при публикации вопроса.');
        }
    })
    .catch(() => {
        showToast('Ошибка сети. Попробуйте позже.');
    });
}

export function submitAnswer(questionId) {
    const input = document.getElementById('answer-input-' + questionId);

    if (!input) return;

    const content = input.value.trim();

    if (!content) {
        showToast('Напишите текст ответа.');
        return;
    }

    const csrfToken = getCsrfToken();

    fetch('/api/qa/answer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ question_id: questionId, answer_text: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            showToast('Ответ добавлен!');
            input.value = '';
            // Append the new answer dynamically instead of full reload
            appendAnswer(questionId, data.answer);
        } else {
            showToast(data.message || 'Ошибка при добавлении ответа.');
        }
    })
    .catch(() => {
        showToast('Ошибка сети. Попробуйте позже.');
    });
}

function appendAnswer(questionId, answer) {
    const container = document.getElementById('answers-' + questionId);
    if (!container) return;

    // Remove "no answers" placeholder if present
    const noAnswers = document.getElementById('no-answers-' + questionId);
    if (noAnswers) noAnswers.remove();

    const wrapper = document.createElement('div');
    wrapper.className = 'flex gap-4 group';

    const dateStr = new Date(answer.created_at + ':00').toLocaleString('ru-RU', {
        day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });

    if (answer.is_official) {
        wrapper.innerHTML =
            '<div class="w-px bg-faq-item-border group-hover:bg-indigo-500/30 transition-colors ml-4 mr-2"></div>' +
            '<div class="flex-1 rounded-xl p-4 border-2 border-indigo-500/50 transition-colors" style="background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(168,85,247,0.05));">' +
                '<div class="flex items-center justify-between mb-2">' +
                    '<div class="flex items-center gap-2">' +
                        '<span class="text-sm font-bold text-indigo-400">' + answer.user + '</span>' +
                        '<span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">✓ Официальный ответ</span>' +
                    '</div>' +
                    '<span class="text-[10px]" style="color: var(--text-muted);">' + dateStr + '</span>' +
                '</div>' +
                '<p class="text-sm leading-relaxed" style="color: var(--text-faq-item-text);">' + answer.content + '</p>' +
            '</div>';
    } else {
        wrapper.innerHTML =
            '<div class="w-px bg-faq-item-border group-hover:bg-indigo-500/30 transition-colors ml-4 mr-2"></div>' +
            '<div class="flex-1 bg-faq-answer-bg rounded-xl p-4 border border-faq-item-border transition-colors">' +
                '<div class="flex items-center justify-between mb-2">' +
                    '<span class="text-sm font-bold text-indigo-400">' + answer.user + '</span>' +
                    '<span class="text-[10px]" style="color: var(--text-muted);">' + dateStr + '</span>' +
                '</div>' +
                '<p class="text-sm leading-relaxed" style="color: var(--text-faq-item-text);">' + answer.content + '</p>' +
            '</div>';
    }

    container.appendChild(wrapper);
}
