from django.core.management.base import BaseCommand
from django.db import models
from datetime import date, timedelta
from home.models import User, Attendance, ProjectGrade


class Command(BaseCommand):
    help = 'Seed attendance, project grades, and XP/rank for all existing users who have no data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-seed data even for users who already have records (will clear existing data first).',
        )

    def handle(self, *args, **options):
        force = options['force']
        today = date.today()

        # Define the session/attendance data
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

        # Define the project grades data
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

        def determine_rank(total_xp):
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

        # Get all users
        all_users = User.objects.all()
        seeded_count = 0
        skipped_count = 0

        for user in all_users:
            has_attendance = Attendance.objects.filter(user=user).exists()
            has_grades = ProjectGrade.objects.filter(user=user).exists()

            if has_attendance and has_grades and not force:
                skipped_count += 1
                continue

            if force:
                # Clear existing data
                Attendance.objects.filter(user=user).delete()
                ProjectGrade.objects.filter(user=user).delete()

            # Seed attendance records
            for session_date, status, session_name in sessions:
                Attendance.objects.create(
                    user=user,
                    date=session_date,
                    status=status,
                    session_name=session_name,
                )

            # Seed project grade records
            for session_date, project_name, grade, xp_earned in projects:
                ProjectGrade.objects.create(
                    user=user,
                    project_name=project_name,
                    grade=grade,
                    session_date=session_date,
                    xp_earned=xp_earned,
                )

            # Recalculate total XP
            total_xp = ProjectGrade.objects.filter(user=user).aggregate(
                total=models.Sum('xp_earned')
            )['total'] or 0

            user.xp = total_xp
            user.rank = determine_rank(total_xp)
            user.max_xp = 1000
            user.save(update_fields=['xp', 'rank', 'max_xp'])

            seeded_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Seeded data for user: {user.username} (XP: {total_xp}, Rank: {user.rank})'
                )
            )

        self.stdout.write(self.style.SUCCESS(
            f'Done. Seeded: {seeded_count} users, Skipped: {skipped_count} users.'
        ))
