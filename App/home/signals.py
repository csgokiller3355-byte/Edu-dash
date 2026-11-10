from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Attendance, ProjectGrade, Homework, ProjectInitiative, Feedback, DiscussionQuestion

User = get_user_model()


def _determine_rank(total_xp):
    """Determine rank title based on total XP."""
    if total_xp >= 1000:
        return 'Мастер'
    elif total_xp >= 900:
        return 'Элитный разработчик'
    elif total_xp >= 700:
        return 'Старший разработчик'
    elif total_xp >= 500:
        return 'Разработчик'
    elif total_xp >= 300:
        return 'Практикант'
    elif total_xp >= 100:
        return 'Ученик'
    else:
        return 'Начинающий'


def seed_user_dashboard_data(user):
    """
    Seed default dashboard data (attendance + project grades) for a given user.
    Recalculates total XP and rank from seeded projects.
    Returns True if data was seeded, False if user already had records.
    """
    # Do not re-seed if user already has data
    if Attendance.objects.filter(user=user).exists() or ProjectGrade.objects.filter(user=user).exists():
        return False

    today = date.today()

    # --- Seed default attendance records (23 sessions) ---
    sessions = [
        (today - timedelta(days=64), 'present', 'Введение в Python'),
        (today - timedelta(days=57), 'present', 'Типы данных и переменные'),
        (today - timedelta(days=50), 'present', 'Условные конструкции'),
        (today - timedelta(days=43), 'late', 'Циклы и итерации'),
        (today - timedelta(days=36), 'present', 'Функции и модули'),
        (today - timedelta(days=29), 'present', 'Строки и списки'),
        (today - timedelta(days=22), 'present', 'Словари и множества'),
        (today - timedelta(days=15), 'late', 'Работа с файлами'),
        (today - timedelta(days=8), 'present', 'ООП: Классы и объекты'),
        (today - timedelta(days=1), 'present', 'ООП: Наследование'),
        (today - timedelta(days=77), 'present', 'Основы Django'),
        (today - timedelta(days=70), 'present', 'Модели и миграции'),
        (today - timedelta(days=63), 'absent', 'Виды и шаблоны'),
        (today - timedelta(days=56), 'present', 'Формы в Django'),
        (today - timedelta(days=49), 'present', 'Аутентификация'),
        (today - timedelta(days=42), 'present', 'REST API'),
        (today - timedelta(days=35), 'present', 'PostgreSQL основы'),
        (today - timedelta(days=28), 'present', 'Запросы и агрегация'),
        (today - timedelta(days=21), 'present', 'JavaScript основы'),
        (today - timedelta(days=14), 'present', 'AJAX и Fetch API'),
        (today - timedelta(days=7), 'present', 'CSS и Tailwind'),
        (today - timedelta(days=3), 'present', 'Тестирование'),
        (today, 'present', 'Финальный проект'),
    ]

    for session_date, status, session_name in sessions:
        Attendance.objects.create(
            user=user,
            date=session_date,
            status=status,
            session_name=session_name
        )

    # --- Seed default project grades (27 projects across sessions) ---
    projects = [
        (today - timedelta(days=64), 'Hello World App', 5, 30),
        (today - timedelta(days=57), 'Калькулятор', 4, 25),
        (today - timedelta(days=50), 'Генератор паролей', 5, 30),
        (today - timedelta(days=43), 'To-Do List (Console)', 5, 30),
        (today - timedelta(days=43), 'Числа Фибоначчи', 4, 20),
        (today - timedelta(days=36), 'Сортировка данных', 5, 30),
        (today - timedelta(days=29), 'Парсер CSV', 3, 15),
        (today - timedelta(days=22), 'Диаграммы слов', 5, 30),
        (today - timedelta(days=15), 'Работа с JSON API', 5, 30),
        (today - timedelta(days=8), 'Django Blog (Models)', 5, 40),
        (today - timedelta(days=8), 'Django Blog (Views)', 4, 25),
        (today - timedelta(days=1), 'Django Auth System', 5, 40),
        (today - timedelta(days=1), 'REST API Endpoint', 4, 25),
        (today - timedelta(days=77), 'База данных PostgreSQL', 5, 30),
        (today - timedelta(days=70), 'SQL Запросы', 3, 15),
        (today - timedelta(days=63), 'Миграции Django', 2, 10),
        (today - timedelta(days=56), 'Формы и валидация', 5, 30),
        (today - timedelta(days=49), 'Панель администратора', 4, 25),
        (today - timedelta(days=42), 'API с Django REST', 5, 40),
        (today - timedelta(days=35), 'PostgreSQL JOIN', 5, 30),
        (today - timedelta(days=28), 'Агрегация данных', 4, 20),
        (today - timedelta(days=21), 'JS Интерактив', 5, 30),
        (today - timedelta(days=14), 'AJAX Dashboard', 5, 40),
        (today - timedelta(days=14), 'Tailwind UI Kit', 3, 15),
        (today - timedelta(days=7), 'CSS Анимации', 5, 30),
        (today - timedelta(days=3), 'Юнит-тесты', 4, 25),
        (today, 'Финальный проект', 5, 50),
    ]

    for session_date, project_name, grade, xp_earned in projects:
        ProjectGrade.objects.create(
            user=user,
            project_name=project_name,
            grade=grade,
            session_date=session_date,
            xp_earned=xp_earned
        )

    # Recalculate total XP from all projects
    total_xp = ProjectGrade.objects.filter(user=user).aggregate(
        total=models.Sum('xp_earned')
    )['total'] or 0

    # Update user XP and rank based on projects
    user.xp = total_xp
    user.rank = _determine_rank(total_xp)
    user.max_xp = 1000
    user.save(update_fields=['xp', 'rank', 'max_xp'])

    return True


@receiver(post_save, sender=User)
def _seed_on_user_creation(sender, instance, created, **kwargs):
    """Signal: seed default dashboard data when a new user is created."""
    if created:
        seed_user_dashboard_data(instance)


def seed_homework_for_user(user):
    """
    Seed default homework records for a user if they have none.
    Also backfills missing descriptions on existing homework records.
    Returns True if seeded, False if already exists.
    """
    user_homeworks = Homework.objects.filter(user=user)

    # Backfill missing descriptions on existing homework records
    titles_map = {
        0: 'Парсер Telegram-бота на Aiogram',
        1: 'API интернет-магазина на Django REST',
        2: 'База данных PostgreSQL для CRM',
        3: 'Валидация форм на JavaScript',
        4: 'Django Auth система',
        5: 'REST API с сериализаторами',
        6: 'CSS Grid и Flexbox макет',
        7: 'Юнит-тесты с pytest',
        8: 'Docker контейнеризация',
        9: 'Redis кэширование',
        10: 'Celery асинхронные задачи',
        11: 'WebSocket чат',
        12: 'Финальный проект: часть 1',
        13: 'Финальный проект: часть 2',
    }

    descriptions_map = {
        0: 'Разработать парсер для Telegram-бота с использованием библиотеки Aiogram 3.x. Реализовать обработку команд /start, /help, /settings. Добавить inline-кнопки и обработку колбэков. Бот должен уметь сохранять данные пользователей в базу данных PostgreSQL и отправлять уведомления по расписанию через APScheduler.',
        1: 'Создать REST API для интернет-магазина с использованием Django REST Framework. Реализовать endpoints для товаров, категорий, корзины и заказов. Добавить пагинацию, фильтрацию и сортировку. Написать сериализаторы с валидацией данных и реализовать JWT-аутентификацию.',
        2: 'Спроектировать и реализовать базу данных PostgreSQL для CRM-системы. Создать таблицы для клиентов, сделок, контактов и активностей. Написать сложные SQL-запросы с JOIN, агрегацией и подзапросами. Реализовать индексы для оптимизации производительности.',
        3: 'Реализовать клиентскую валидацию форм на чистом JavaScript без использования библиотек. Создать систему валидации с поддержкой email, телефона, пароля и пользовательских правил. Добавить визуальную индикацию ошибок и динамическое обновление сообщений.',
        4: 'Разработать систему аутентификации и авторизации на Django. Реализовать регистрацию, вход, выход, восстановление пароля через email. Добавить защиту от CSRF-атак и реализацию ролевой модели (RBAC) с кастомными правами доступа.',
        5: 'Создать REST API с использованием Django REST Framework. Реализовать ModelSerializer, ListCreateAPIView, RetrieveUpdateDestroyAPIView. Добавить кастомные сериализаторы с вложенными полями и кастомную аутентификацию через токен.',
        6: 'Сверстать адаптивный макет страницы используя CSS Grid и Flexbox. Реализовать layout с sidebar, header, main content и footer. Макет должен корректно отображаться на экранах от 320px до 1920px. Использовать CSS-переменные для темизации.',
        7: 'Написать набор юнит-тестов с использованием pytest для модуля обработки данных. Реализовать тесты с фикстурами, параметризованными тестами и моками. Достичь покрытия не менее 80% кода. Использовать pytest-django для тестирования views.',
        8: 'Написать Dockerfile для Django-приложения и docker-compose.yml с сервисами: web, db (PostgreSQL), redis. Настроить multi-stage build для уменьшения размера образа. Добавить healthcheck и корректную обработку сигналов.',
        9: 'Реализовать кэширование часто запрашиваемых данных с использованием Redis. Настроить Django-Redis как бэкенд кэширования. Добавить кэширование на уровне views и шаблонов. Реализовать инвалидацию кэша при обновлении данных.',
        10: 'Настроить Celery для выполнения асинхронных задач в Django. Реализовать задачи для отправки email-уведомлений, генерации PDF-отчетов и обработки больших файлов. Настроить очереди с разными приоритетами и beat-планировщик.',
        11: 'Реализовать чат в реальном времени с использованием WebSocket через Django Channels. Создать Consumer для обработки сообщений, групповые комнаты и систему уведомлений о новых сообщениях. Добавить историю сообщений с хранением в базе данных.',
        12: 'Первая часть финального проекта: проектирование архитектуры, создание моделей данных, настройка маршрутизации и базовых views. Реализовать авторизацию, главную страницу и профиль пользователя. Подготовить техническую документацию.',
        13: 'Вторая часть финального проекта: реализация основной бизнес-логики, интеграция с внешними API, написание тестов и деплой. Добавить админ-панель для управления контентом и систему уведомлений. Провести код-ревью и оптимизацию.',
    }

    # Update existing homeworks that match seeded titles but have empty descriptions
    for hw in user_homeworks:
        if not hw.description or hw.description.strip() == '':
            # Find the matching index by title
            for idx, title in titles_map.items():
                if hw.title == title:
                    hw.description = descriptions_map[idx]
                    hw.save(update_fields=['description'])
                    break

    if user_homeworks.exists():
        return False

    from datetime import datetime
    today = date.today()
    homeworks = [
        (today - timedelta(days=1), 'checking', None, today - timedelta(days=1, hours=6)),
        (today - timedelta(days=3), 'graded', '5/5', today - timedelta(days=6)),
        (today - timedelta(days=5), 'graded', '4/5', today - timedelta(days=8)),
        (today - timedelta(days=7), 'graded', '5/5', today - timedelta(days=10)),
        (today - timedelta(days=10), 'graded', '3/5', today - timedelta(days=13)),
        (today - timedelta(days=12), 'graded', '5/5', today - timedelta(days=15)),
        (today - timedelta(days=14), 'graded', '4/5', today - timedelta(days=17)),
        (today - timedelta(days=17), 'graded', '5/5', today - timedelta(days=20)),
        (today - timedelta(days=20), 'graded', '5/5', today - timedelta(days=23)),
        (today - timedelta(days=22), 'graded', '4/5', today - timedelta(days=25)),
        (today - timedelta(days=25), 'graded', '5/5', today - timedelta(days=28)),
        (today - timedelta(days=28), 'graded', '5/5', today - timedelta(days=31)),
        (today + timedelta(days=1), 'process', None, today + timedelta(days=3)),
        (today + timedelta(days=4), 'process', None, today + timedelta(days=7)),
    ]

    titles = [
        'Парсер Telegram-бота на Aiogram',
        'API интернет-магазина на Django REST',
        'База данных PostgreSQL для CRM',
        'Валидация форм на JavaScript',
        'Django Auth система',
        'REST API с сериализаторами',
        'CSS Grid и Flexbox макет',
        'Юнит-тесты с pytest',
        'Docker контейнеризация',
        'Redis кэширование',
        'Celery асинхронные задачи',
        'WebSocket чат',
        'Финальный проект: часть 1',
        'Финальный проект: часть 2',
    ]

    descriptions = [
        'Разработать парсер для Telegram-бота с использованием библиотеки Aiogram 3.x. Реализовать обработку команд /start, /help, /settings. Добавить inline-кнопки и обработку колбэков. Бот должен уметь сохранять данные пользователей в базу данных PostgreSQL и отправлять уведомления по расписанию через APScheduler.',
        'Создать REST API для интернет-магазина с использованием Django REST Framework. Реализовать endpoints для товаров, категорий, корзины и заказов. Добавить пагинацию, фильтрацию и сортировку. Написать сериализаторы с валидацией данных и реализовать JWT-аутентификацию.',
        'Спроектировать и реализовать базу данных PostgreSQL для CRM-системы. Создать таблицы для клиентов, сделок, контактов и активностей. Написать сложные SQL-запросы с JOIN, агрегацией и подзапросами. Реализовать индексы для оптимизации производительности.',
        'Реализовать клиентскую валидацию форм на чистом JavaScript без использования библиотек. Создать систему валидации с поддержкой email, телефона, пароля и пользовательских правил. Добавить визуальную индикацию ошибок и динамическое обновление сообщений.',
        'Разработать систему аутентификации и авторизации на Django. Реализовать регистрацию, вход, выход, восстановление пароля через email. Добавить защиту от CSRF-атак и реализацию ролевой модели (RBAC) с кастомными правами доступа.',
        'Создать REST API с использованием Django REST Framework. Реализовать ModelSerializer, ListCreateAPIView, RetrieveUpdateDestroyAPIView. Добавить кастомные сериализаторы с вложенными полями и кастомную аутентификацию через токен.',
        'Сверстать адаптивный макет страницы используя CSS Grid и Flexbox. Реализовать layout с sidebar, header, main content и footer. Макет должен корректно отображаться на экранах от 320px до 1920px. Использовать CSS-переменные для темизации.',
        'Написать набор юнит-тестов с использованием pytest для модуля обработки данных. Реализовать тесты с фикстурами, параметризованными тестами и моками. Достичь покрытия не менее 80% кода. Использовать pytest-django для тестирования views.',
        'Написать Dockerfile для Django-приложения и docker-compose.yml с сервисами: web, db (PostgreSQL), redis. Настроить multi-stage build для уменьшения размера образа. Добавить healthcheck и корректную обработку сигналов.',
        'Реализовать кэширование часто запрашиваемых данных с использованием Redis. Настроить Django-Redis как бэкенд кэширования. Добавить кэширование на уровне views и шаблонов. Реализовать инвалидацию кэша при обновлении данных.',
        'Настроить Celery для выполнения асинхронных задач в Django. Реализовать задачи для отправки email-уведомлений, генерации PDF-отчетов и обработки больших файлов. Настроить очереди с разными приоритетами и beat-планировщик.',
        'Реализовать чат в реальном времени с использованием WebSocket через Django Channels. Создать Consumer для обработки сообщений, групповые комнаты и систему уведомлений о новых сообщениях. Добавить историю сообщений с хранением в базе данных.',
        'Первая часть финального проекта: проектирование архитектуры, создание моделей данных, настройка маршрутизации и базовых views. Реализовать авторизацию, главную страницу и профиль пользователя. Подготовить техническую документацию.',
        'Вторая часть финального проекта: реализация основной бизнес-логики, интеграция с внешними API, написание тестов и деплой. Добавить админ-панель для управления контентом и систему уведомлений. Провести код-ревью и оптимизацию.',
    ]

    for idx, (submitted_at, status, grade, deadline) in enumerate(homeworks):
        Homework.objects.create(
            user=user,
            title=titles[idx] if idx < len(titles) else f'Задание {idx + 1}',
            description=descriptions[idx] if idx < len(descriptions) else '',
            status=status,
            grade=grade,
            submitted_at=datetime.combine(submitted_at, datetime.min.time()) if submitted_at <= today else None,
            deadline=datetime.combine(deadline, datetime.min.time()) if deadline else None,
        )

    return True


def seed_project_initiatives():
    """
    Seed default project initiatives if the table is empty.
    """
    if ProjectInitiative.objects.exists():
        return False

    users = list(User.objects.filter(is_active=True)[:5])
    if not users:
        return False

    initiatives_data = [
        ('Разработка веб-игры на JS', 'Создаём 2D-игру с использованием Canvas API и JavaScript. Нужен бэкенд-разработчик и дизайнер.', 3, 5, users[0]),
        ('Telegram-бот для учёта задач', 'Бот на Aiogram с базой данных PostgreSQL. Требуется помощь с интеграцией расписания.', 2, 4, users[0]),
        ('Django Dashboard аналитика', 'Расширение дашборда с графиками Chart.js и экспортом в PDF.', 4, 6, users[1] if len(users) > 1 else users[0]),
        ('Мобильное приложение на Flutter', 'Кроссплатформенное приложение для отслеживания посещаемости.', 1, 4, users[2] if len(users) > 2 else users[0]),
        ('API микросервисов', 'Разработка микросервисной архитектуры с Docker и Kubernetes.', 2, 5, users[3] if len(users) > 3 else users[0]),
        ('Чат-бот с AI', 'Интеграция OpenAI API для создания умного чат-бота.', 3, 4, users[4] if len(users) > 4 else users[0]),
    ]

    for title, description, current, max_m, initiator in initiatives_data:
        ProjectInitiative.objects.create(
            user=initiator,
            title=title,
            description=description,
            current_members=current,
            max_members=max_m,
        )

    return True


def seed_feedbacks():
    """
    Seed default feedback records if the table is empty.
    """
    if Feedback.objects.exists():
        return False

    users = list(User.objects.filter(is_active=True)[:5])
    if not users:
        return False

    feedbacks_data = [
        ('Было бы круто добавить тёмную тему по умолчанию для всех!', users[0]),
        ('Хотелось бы больше примеров кода в домашних заданиях.', users[1] if len(users) > 1 else users[0]),
        ('Предлагаю добавить раздел с видеоуроками по Django.', users[2] if len(users) > 2 else users[0]),
        ('Нужно улучшить систему уведомлений о дедлайнах.', users[3] if len(users) > 3 else users[0]),
        ('Было бы полезно добавить возможность скачивать материалы.', users[4] if len(users) > 4 else users[0]),
        ('Хочу видеть рейтинг по группе в реальном времени.', users[0]),
        ('Добавьте возможность комментировать домашние задания.', users[1] if len(users) > 1 else users[0]),
    ]

    for text, user in feedbacks_data:
        Feedback.objects.create(user=user, text=text)

    return True


def seed_faqs():
    """
    Seed default FAQ entries if the table is empty.
    """
    if DiscussionQuestion.objects.exists():
        return False

    # Get an admin user to be the author of seeded questions
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.first()

    if not admin_user:
        return False

    faqs = [
        ('Как начисляются монетки?', 'Монетки автоматически капают на ваш баланс после проверки домашнего задания преподавателем.'),
        ('Что делать, если работа отправлена на доработку?', 'Исправьте указанные ошибки в коде и отправьте файл повторно во вкладке ДЗ.'),
        ('Как повысить свой ранг?', 'Выполняйте домашние задания, получайте высокие оценки и посещайте занятия. XP начисляется за каждый проект.'),
        ('Можно ли участвовать в нескольких проектах?', 'Да, вы можете присоединиться к нескольким совместным работам одновременно, если есть свободные места.'),
        ('Как создать свою инициативу?', 'Перейдите во вкладку "Совместные работы" и нажмите кнопку "+ Создать свою инициативу". Заполните название и описание.'),
        ('Как оставить отзыв?', 'Перейдите во вкладку "Советы и отзывы", напишите текст в поле и нажмите "Отправить отзыв". Все отзывы публикуются с вашим именем.'),
        ('Что такое XP и как его получить?', 'XP (опыт) начисляется за выполнение проектов и домашних заданий. Чем выше оценка, тем больше XP. XP определяет ваш ранг.'),
        ('Как работает система посещаемости?', 'Каждое занятие фиксируется: присутствовал, опоздал или отсутствовал. Посещаемость влияет на рейтинг группы.'),
    ]

    for title, content in faqs:
        DiscussionQuestion.objects.create(user=admin_user, title=title, content=content)

    return True
