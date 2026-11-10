from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser for full auth integration."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True, verbose_name='active')

    # Dashboard XP & Rank fields
    xp = models.IntegerField(default=0, verbose_name='Опыт (XP)')
    rank = models.CharField(max_length=100, default='Начинающий', verbose_name='Ранг')
    max_xp = models.IntegerField(default=1000, verbose_name='Макс. XP для следующего ранга')

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    def get_xp_percentage(self):
        """Calculate XP progress percentage toward next rank."""
        if self.max_xp == 0:
            return 100
        return min(int((self.xp / self.max_xp) * 100), 100)

    def get_next_rank_name(self):
        """Return the name of the next rank."""
        ranks = [
            (0, 'Начинающий'),
            (100, 'Ученик'),
            (300, 'Практикант'),
            (500, 'Разработчик'),
            (700, 'Старший разработчик'),
            (900, 'Элитный разработчик'),
            (1000, 'Мастер'),
        ]
        current_idx = 0
        for idx, (threshold, name) in enumerate(ranks):
            if self.xp >= threshold:
                current_idx = idx
        if current_idx < len(ranks) - 1:
            return ranks[current_idx + 1][1]
        return 'Максимальный ранг'


class BaseModel(models.Model):
    """Abstract base model with common fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} (ID: {self.id})"


class Post(BaseModel):
    """Post model for storing blog posts or articles."""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(BaseModel):
    """Comment model for storing comments on posts."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()

    class Meta:
        db_table = 'comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Attendance(BaseModel):
    """Attendance record for tracking user presence at sessions."""
    ATTENDANCE_STATUS_CHOICES = [
        ('present', 'Присутствовал'),
        ('late', 'Опоздал'),
        ('absent', 'Отсутствовал'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(verbose_name='Дата')
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='present')
    session_name = models.CharField(max_length=200, blank=True, verbose_name='Название занятия')

    class Meta:
        db_table = 'attendance'
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.get_status_display()} on {self.date}"


class ProjectGrade(BaseModel):
    """Grade record for project submissions."""
    GRADE_CHOICES = [
        (5, 'Отлично'),
        (4, 'Хорошо'),
        (3, 'Удовлетворительно'),
        (2, 'Доработать'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_grades'
    )
    project_name = models.CharField(max_length=200, verbose_name='Название проекта')
    grade = models.IntegerField(choices=GRADE_CHOICES, verbose_name='Оценка')
    session_date = models.DateField(verbose_name='Дата занятия')
    xp_earned = models.IntegerField(default=0, verbose_name='Полученный XP')

    class Meta:
        db_table = 'project_grades'
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.user} - {self.project_name}: {self.grade}"


class CustomMiniGame(BaseModel):
    """Saved custom mini-game slot for a user (dynamic, unlimited slots)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_minigames'
    )
    slot_number = models.IntegerField(verbose_name='Номер слота')
    title = models.CharField(max_length=200, default='Моя игра', verbose_name='Название игры')
    html_code = models.TextField(default='', verbose_name='HTML-код')
    css_code = models.TextField(default='', verbose_name='CSS-код')
    js_code = models.TextField(default='', verbose_name='JS-код')
    is_public = models.BooleanField(default=False, verbose_name='Публичная (видна в галерее сообщества)')

    class Meta:
        db_table = 'custom_minigames'
        unique_together = ('user', 'slot_number')
        ordering = ['slot_number']

    def __str__(self):
        return f"{self.user} - Слот {self.slot_number}: {self.title}"


class CursorStyle(BaseModel):
    """User-created custom mouse cursor CSS style that can be shared publicly."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cursor_styles'
    )
    name = models.CharField(max_length=200, verbose_name='Название курсора')
    css_code = models.TextField(verbose_name='CSS-код для курсора')
    is_public = models.BooleanField(default=False, verbose_name='Публичный (виден в галерее)')

    class Meta:
        db_table = 'cursor_styles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.name}"


class Homework(BaseModel):
    """Homework assignment for a user with status tracking."""
    STATUS_CHOICES = [
        ('checking', 'На проверке'),
        ('graded', 'Оцененное'),
        ('process', 'В процессе'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='homeworks'
    )
    title = models.CharField(max_length=300, verbose_name='Название задания')
    description = models.TextField(blank=True, verbose_name='Описание задания')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='process', verbose_name='Статус')
    grade = models.CharField(max_length=10, blank=True, null=True, verbose_name='Оценка')
    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата сдачи')
    deadline = models.DateTimeField(blank=True, null=True, verbose_name='Дедлайн')

    class Meta:
        db_table = 'homework'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.title} ({self.get_status_display()})"


class ProjectInitiative(BaseModel):
    """Collaborative project initiative created by a user."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_initiatives'
    )
    title = models.CharField(max_length=300, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание')
    current_members = models.IntegerField(default=1, verbose_name='Текущие участники')
    max_members = models.IntegerField(default=10, verbose_name='Макс. участников')

    class Meta:
        db_table = 'project_initiatives'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} (Инициатор: {self.user})"


class InitiativeSection(BaseModel):
    """Dynamic section for a project initiative (e.g., Tech Stack, Goals)."""
    initiative = models.ForeignKey(
        ProjectInitiative,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    title = models.CharField(max_length=200, verbose_name='Заголовок секции')
    content = models.TextField(verbose_name='Содержание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        db_table = 'initiative_sections'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} for {self.initiative.title}"


class ProjectInitiativeMember(BaseModel):
    """Membership link between a user and a project initiative."""
    initiative = models.ForeignKey(
        ProjectInitiative,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )

    class Meta:
        db_table = 'project_initiative_members'
        unique_together = ('initiative', 'user')

    def __str__(self):
        return f"{self.user} in {self.initiative}"


class Feedback(BaseModel):
    """User feedback/suggestion (named, public) with admin reply support."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    admin_reply = models.TextField(blank=True, default='', verbose_name='Ответ администратора')
    replied_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата ответа')

    class Meta:
        db_table = 'feedback'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feedback by {self.user}: {self.text[:50]}"

    def has_reply(self):
        """Check if an admin has replied to this feedback."""
        return bool(self.admin_reply)


class DiscussionQuestion(BaseModel):
    """Dynamic Q&A question asked by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=300, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')

    class Meta:
        db_table = 'discussion_questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DiscussionAnswer(BaseModel):
    """Answer to a specific discussion question."""
    question = models.ForeignKey(DiscussionQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField(verbose_name='Текст ответа')
    is_official = models.BooleanField(default=False, verbose_name='Официальный ответ (преподаватель/админ)')

    class Meta:
        db_table = 'discussion_answers'
        ordering = ['-is_official', 'created_at']

    def __str__(self):
        return f"Answer to {self.question.title} by {self.user}"


class CalendarTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_tasks')
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    date = models.DateField(verbose_name="Дата")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Задача в календаре"
        verbose_name_plural = "Задачи в календаре"

    def __str__(self):
        return f"{self.title} ({self.date})"


class UserDocument(models.Model):
    title = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255, blank=True, null=True)  # ID файла на Google Диске
    file_url = models.URLField(blank=True, null=True)                    # Ссылка для скачивания/просмотра

    def __str__(self):
        return self.title
    uploaded_at = models.DateTimeField(auto_now_add=True)