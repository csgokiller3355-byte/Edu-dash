from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from .models import User, Attendance, ProjectGrade, CustomMiniGame, Homework, ProjectInitiative, ProjectInitiativeMember, Feedback, DiscussionQuestion, DiscussionAnswer


class AttendanceInline(admin.TabularInline):
    """Inline for editing attendance records directly from the User admin page."""
    model = Attendance
    extra = 1
    fields = ('date', 'status', 'session_name')
    readonly_fields = ('date',)


class ProjectGradeInline(admin.TabularInline):
    """Inline for editing project grades directly from the User admin page."""
    model = ProjectGrade
    extra = 1
    fields = ('project_name', 'grade', 'session_date', 'xp_earned')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model with dashboard fields."""
    list_display = (
        'username',
        'email',
        'get_full_name',
        'xp',
        'rank',
        'max_xp',
        'is_staff',
        'is_active',
        'date_joined',
    )
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'rank', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    inlines = (AttendanceInline, ProjectGradeInline)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        (
            'Dashboard stats',
            {
                'fields': (
                    'xp',
                    'rank',
                    'max_xp',
                )
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2',
                    'xp',
                    'rank',
                    'max_xp',
                    'is_active',
                    'is_staff',
                ),
            },
        ),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin interface for Attendance records."""
    list_display = ('user', 'user_full_name', 'date', 'status', 'session_name')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'session_name')
    ordering = ('-date',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Student'


@admin.register(ProjectGrade)
class ProjectGradeAdmin(admin.ModelAdmin):
    """Admin interface for Project Grade records."""
    list_display = ('user', 'user_full_name', 'project_name', 'grade', 'session_date', 'xp_earned')
    list_filter = ('grade', 'session_date')
    search_fields = ('user__username', 'project_name')
    ordering = ('-session_date',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Student'


@admin.register(CustomMiniGame)
class CustomMiniGameAdmin(admin.ModelAdmin):
    """Admin interface for Custom Mini-Game slots."""
    list_display = ('user', 'user_full_name', 'slot_number', 'title', 'updated_at')
    list_filter = ('slot_number', 'updated_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'title')
    ordering = ('user', 'slot_number')
    readonly_fields = ('updated_at', 'created_at')

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Student'


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """Admin interface for Homework records."""
    list_display = ('user', 'user_full_name', 'title', 'status', 'grade', 'submitted_at', 'deadline')
    list_filter = ('status', 'submitted_at', 'deadline')
    search_fields = ('user__username', 'title')
    ordering = ('-created_at',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Student'


@admin.register(ProjectInitiative)
class ProjectInitiativeAdmin(admin.ModelAdmin):
    """Admin interface for Project Initiatives."""
    list_display = ('title', 'user', 'user_full_name', 'current_members', 'max_members', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Initiator'


@admin.register(ProjectInitiativeMember)
class ProjectInitiativeMemberAdmin(admin.ModelAdmin):
    """Admin interface for Project Initiative Memberships."""
    list_display = ('initiative', 'user', 'user_full_name', 'created_at')
    list_filter = ('initiative',)
    search_fields = ('user__username', 'initiative__title')
    ordering = ('-created_at',)

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Member'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for Feedback records with admin reply support."""
    list_display = ('user', 'user_full_name', 'text_preview', 'has_reply_badge', 'created_at', 'replied_at')
    list_filter = ('created_at', 'replied_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'text', 'admin_reply')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'replied_at')

    fieldsets = (
        ('User & Feedback', {
            'fields': ('user', 'text', 'created_at'),
            'classes': ('wide',),
        }),
        ('Admin Reply', {
            'fields': ('admin_reply', 'replied_at'),
            'classes': ('wide',),
            'description': 'Type your reply below. It will be sent as a notification to the user.',
        }),
    )

    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    user_full_name.short_description = 'Author'

    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text

    text_preview.short_description = 'Text'

    def has_reply_badge(self, obj):
        if obj.has_reply():
            return '✓ Replied'
        return '— Pending'

    has_reply_badge.short_description = 'Status'
    has_reply_badge.admin_order_field = 'replied_at'

    def save_model(self, request, obj, form, change):
        """Auto-set replied_at when admin_reply is changed."""
        if change:
            # Only update replied_at if admin_reply was just added or changed
            old = Feedback.objects.get(pk=obj.pk)
            if old.admin_reply != obj.admin_reply:
                if obj.admin_reply.strip():
                    obj.replied_at = timezone.now()
                else:
                    obj.replied_at = None
        super().save_model(request, obj, form, change)


class DiscussionAnswerInline(admin.TabularInline):
    model = DiscussionAnswer
    extra = 1


@admin.register(DiscussionQuestion)
class DiscussionQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content', 'user__username')
    inlines = [DiscussionAnswerInline]


@admin.register(DiscussionAnswer)
class DiscussionAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username', 'question__title')
