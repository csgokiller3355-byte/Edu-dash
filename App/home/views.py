from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from datetime import date, timedelta
from django.utils import timezone
import json
from .forms import RegisterForm, LoginForm
from .models import User, Attendance, ProjectGrade, CustomMiniGame, Homework, ProjectInitiative, ProjectInitiativeMember, Feedback, DiscussionQuestion, DiscussionAnswer, CalendarTask, UserDocument, InitiativeSection, CursorStyle
from .signals import seed_user_dashboard_data, seed_homework_for_user, seed_project_initiatives, seed_feedbacks, seed_faqs


def home(request):
    """Render the home page and handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None
    success_message = None

    if request.method == 'POST':
        # Determine which form was submitted based on the action
        if 'login_action' in request.POST:
            # Login flow
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Добро пожаловать, {user.username}!')
                    if user.is_staff or user.is_superuser:
                        return redirect('admin_panel')
                    else:
                        return redirect('dashboard')
                else:
                    error_message = "Неверный логин или пароль"
            else:
                error_message = "Пожалуйста, заполните все поля корректно."
        elif 'register_action' in request.POST:
            # Registration flow
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f'Аккаунт "{user.username}" успешно создан! Теперь вы можете войти.')
                return render(request, 'index.html', {'success': 'Аккаунт успешно создан! Теперь вы можете войти.'})
            else:
                error_message = "Ошибка при регистрации. Проверьте данные и попробуйте снова."
                return render(request, 'index.html', {'register_form': form, 'error': error_message, 'active_tab': 'register'})

    if request.method == 'GET':
        login_form = LoginForm()
        register_form = RegisterForm()
        return render(request, 'index.html', {
            'login_form': login_form,
            'register_form': register_form,
            'error': error_message,
            'success': success_message,
        })

    return render(request, 'index.html', {
        'login_form': LoginForm(),
        'register_form': RegisterForm(),
        'error': error_message,
        'success': success_message,
    })


def register(request):
    """Handle user registration via dedicated URL."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Аккаунт "{user.username}" успешно создан! Теперь вы можете войти.')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка при регистрации. Проверьте данные.')
    else:
        form = RegisterForm()

    return render(request, 'index.html', {'register_form': form, 'active_tab': 'register'})


def user_logout(request):
    """Log out the current user."""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')

@login_required
@ensure_csrf_cookie
def dashboard_view(request):
    """Render the student dashboard page with real data from the database."""
    user = request.user

    # --- Auto-seed data if user has no attendance or grade records ---
    # This ensures users registered before signals were added (or whose data
    # was deleted) still see fully populated dashboard charts on visit.
    seed_user_dashboard_data(user)
    seed_homework_for_user(user)
    seed_project_initiatives()
    seed_feedbacks()
    seed_faqs()

    # Refresh user instance from database in case seeding updated XP/rank
    user = User.objects.get(pk=user.pk)

    # --- XP & Rank data ---
    user_xp = user.xp
    user_rank = user.rank
    user_max_xp = user.max_xp
    xp_percentage = user.get_xp_percentage()
    next_rank_name = user.get_next_rank_name()

    # --- Attendance statistics ---
    attendances = Attendance.objects.filter(user=user)
    total_sessions = attendances.count()
    present_count = attendances.filter(status='present').count()
    late_count = attendances.filter(status='late').count()
    absent_count = attendances.filter(status='absent').count()

    if total_sessions > 0:
        present_pct = round((present_count / total_sessions) * 100)
        late_pct = round((late_count / total_sessions) * 100)
        absent_pct = round((absent_count / total_sessions) * 100)
        attendance_rate = present_pct  # main ring percentage
    else:
        present_pct = 0
        late_pct = 0
        absent_pct = 0
        attendance_rate = 0

    # --- Project grades analytics ---
    grades = ProjectGrade.objects.filter(user=user).order_by('session_date')
    total_grades = grades.count()

    # Grade distribution
    grade_5_count = grades.filter(grade=5).count()
    grade_4_count = grades.filter(grade=4).count()
    grade_3_count = grades.filter(grade=3).count()
    grade_2_count = grades.filter(grade=2).count()

    if total_grades > 0:
        grade_5_pct = round((grade_5_count / total_grades) * 100)
        grade_4_pct = round((grade_4_count / total_grades) * 100)
        grade_3_pct = round((grade_3_count / total_grades) * 100)
        grade_2_pct = round((grade_2_count / total_grades) * 100)
    else:
        grade_5_pct = 0
        grade_4_pct = 0
        grade_3_pct = 0
        grade_2_pct = 0

    # Group grades by session date for bar chart
    grade_by_session = []
    for g in grades:
        grade_by_session.append({
            'date': g.session_date,
            'project_name': g.project_name,
            'grade': g.grade,
            'xp_earned': g.xp_earned,
        })

    # Build chart data: group by date, each date may have 1-2 projects
    chart_data = {}
    for item in grade_by_session:
        d = str(item['date'])
        if d not in chart_data:
            chart_data[d] = {'date': item['date'], 'grades': []}
        chart_data[d]['grades'].append(item['grade'])

    chart_columns = list(chart_data.values())

    # --- Stream Ranking (Рейтинг потока) — top users by XP ---
    # Fetch all active users sorted by XP descending, excluding the current user
    stream_ranking_others = []
    for u in User.objects.filter(is_active=True).order_by('-xp', 'id').exclude(id=user.id)[:2]:
        att_total = Attendance.objects.filter(user=u).count()
        att_present = Attendance.objects.filter(user=u, status='present').count()
        att_rate = round((att_present / att_total) * 100) if att_total > 0 else 0
        stream_ranking_others.append({
            'user': u,
            'full_name': u.get_full_name() or u.username,
            'xp': u.xp,
            'rank': u.rank,
            'attendance_rate': att_rate,
        })

    # --- Group Ranking (Рейтинг группы) — top users by attendance rate ---
    # Compute attendance rate for all active users, sorted by rate descending
    group_ranking_others = []
    all_users_for_group = User.objects.filter(is_active=True).exclude(id=user.id)
    user_attendance_rates = []
    for u in all_users_for_group:
        att_total = Attendance.objects.filter(user=u).count()
        att_present = Attendance.objects.filter(user=u, status='present').count()
        rate = round((att_present / att_total) * 100) if att_total > 0 else 0
        user_attendance_rates.append({
            'user': u,
            'full_name': u.get_full_name() or u.username,
            'rank': u.rank,
            'attendance_rate': rate,
            'xp': u.xp,
        })
    # Sort by attendance rate descending, then by XP descending as tiebreaker
    user_attendance_rates.sort(key=lambda x: (x['attendance_rate'], x['xp']), reverse=True)
    group_ranking_others = user_attendance_rates[:2]

    # --- Homework data ---
    homeworks = Homework.objects.filter(user=user)
    homework_checking = homeworks.filter(status='checking')
    homework_graded = homeworks.filter(status='graded')
    homework_process = homeworks.filter(status='process')

    # --- Project Initiatives data ---
    project_initiatives = ProjectInitiative.objects.all().prefetch_related('sections')
    user_joined_initiative_ids = list(
        ProjectInitiativeMember.objects.filter(user=user).values_list('initiative_id', flat=True)
    )

    # --- Feedback data ---
    feedbacks = Feedback.objects.all()[:20]

    # --- Q&A Discussion data ---
    questions = DiscussionQuestion.objects.all().prefetch_related('answers', 'answers__user', 'user')

    context = {
        'user': user,
        # XP & Rank
        'user_xp': user_xp,
        'user_rank': user_rank,
        'user_max_xp': user_max_xp,
        'xp_percentage': xp_percentage,
        'next_rank_name': next_rank_name,
        # Attendance
        'total_sessions': total_sessions,
        'present_count': present_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'present_pct': present_pct,
        'late_pct': late_pct,
        'absent_pct': absent_pct,
        'attendance_rate': attendance_rate,
        # Grades
        'grades': grades,
        'total_grades': total_grades,
        'grade_5_count': grade_5_count,
        'grade_4_count': grade_4_count,
        'grade_3_count': grade_3_count,
        'grade_2_count': grade_2_count,
        'grade_5_pct': grade_5_pct,
        'grade_4_pct': grade_4_pct,
        'grade_3_pct': grade_3_pct,
        'grade_2_pct': grade_2_pct,
        'chart_columns': chart_columns,
        # Rankings
        'stream_ranking_others': stream_ranking_others,
        'group_ranking_others': group_ranking_others,
        # Homework
        'homework_checking': homework_checking,
        'homework_graded': homework_graded,
        'homework_process': homework_process,
        'homework_checking_count': homework_checking.count(),
        'homework_graded_count': homework_graded.count(),
        'homework_process_count': homework_process.count(),
        # Project Initiatives
        'project_initiatives': project_initiatives,
        'user_joined_initiative_ids': user_joined_initiative_ids,
        # Feedback
        'feedbacks': feedbacks,
        # Q&A
        'questions': questions,
    }
    return render(request, 'dashboard.html', context)


@staff_member_required
def admin_panel_view(request):
    """Render the custom admin panel with all users and their dashboard stats."""
    users = User.objects.all().prefetch_related('attendances', 'project_grades')

    # Build user data with stats
    user_list = []
    for u in users:
        attendances = u.attendances.all()
        grades = u.project_grades.all()
        total_att = attendances.count()
        present_count = attendances.filter(status='present').count()
        late_count = attendances.filter(status='late').count()
        absent_count = attendances.filter(status='absent').count()
        attendance_rate = round((present_count / total_att) * 100) if total_att > 0 else 0

        total_grades = grades.count()
        avg_grade = round(grades.aggregate(avg=Sum('grade'))['avg'] / total_grades, 1) if total_grades > 0 else 0
        total_xp_earned = grades.aggregate(total=Sum('xp_earned'))['total'] or 0

        user_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'full_name': u.get_full_name() or u.username,
            'xp': u.xp,
            'rank': u.rank,
            'max_xp': u.max_xp,
            'is_staff': u.is_staff,
            'is_active': u.is_active,
            'date_joined': u.date_joined.strftime('%Y-%m-%d'),
            'attendance_rate': attendance_rate,
            'present_count': present_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'total_attendances': total_att,
            'total_grades': total_grades,
            'avg_grade': avg_grade,
            'total_xp_earned': total_xp_earned,
        })

    # KPI stats
    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    total_attendance_records = Attendance.objects.count()
    total_grade_records = ProjectGrade.objects.count()

    context = {
        'users': user_list,
        'total_users': total_users,
        'active_users': active_users,
        'total_attendance_records': total_attendance_records,
        'total_grade_records': total_grade_records,
    }
    return render(request, 'admin_panel.html', context)


@staff_member_required
@require_POST
def admin_update_user(request):
    """Update a user's XP, rank, max_xp, is_active, is_staff via AJAX."""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        if 'xp' in data:
            user.xp = int(data['xp'])
        if 'rank' in data:
            user.rank = data['rank']
        if 'max_xp' in data:
            user.max_xp = int(data['max_xp'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        if 'is_staff' in data:
            user.is_staff = bool(data['is_staff'])
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']

        user.save()
        return JsonResponse({'status': 'ok', 'message': f'User {user.username} updated successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
@require_POST
def admin_update_attendance(request):
    """Create or update an attendance record via AJAX."""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        if 'attendance_id' in data and data['attendance_id']:
            # Update existing
            attendance = get_object_or_404(Attendance, id=data['attendance_id'], user=user)
        else:
            # Create new
            attendance = Attendance(user=user)

        if 'date' in data:
            attendance.date = data['date']
        if 'status' in data:
            attendance.status = data['status']
        if 'session_name' in data:
            attendance.session_name = data['session_name']

        attendance.save()
        return JsonResponse({'status': 'ok', 'message': 'Attendance record updated.', 'id': attendance.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
@require_POST
def admin_delete_attendance(request):
    """Delete an attendance record via AJAX."""
    try:
        data = json.loads(request.body)
        attendance = get_object_or_404(Attendance, id=data.get('attendance_id'))
        attendance.delete()
        return JsonResponse({'status': 'ok', 'message': 'Attendance record deleted.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
@require_POST
def admin_update_grade(request):
    """Create or update a project grade record via AJAX."""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        user = get_object_or_404(User, id=user_id)

        if 'grade_id' in data and data['grade_id']:
            # Update existing
            grade = get_object_or_404(ProjectGrade, id=data['grade_id'], user=user)
        else:
            # Create new
            grade = ProjectGrade(user=user)

        if 'project_name' in data:
            grade.project_name = data['project_name']
        if 'grade' in data:
            grade.grade = int(data['grade'])
        if 'session_date' in data:
            grade.session_date = data['session_date']
        if 'xp_earned' in data:
            grade.xp_earned = int(data['xp_earned'])

        grade.save()
        return JsonResponse({'status': 'ok', 'message': 'Grade record updated.', 'id': grade.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
@require_POST
def admin_delete_grade(request):
    """Delete a project grade record via AJAX."""
    try:
        data = json.loads(request.body)
        grade = get_object_or_404(ProjectGrade, id=data.get('grade_id'))
        grade.delete()
        return JsonResponse({'status': 'ok', 'message': 'Grade record deleted.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
def admin_user_detail(request, user_id):
    """Return detailed data for a specific user (attendance + grades) as JSON."""
    try:
        user = get_object_or_404(User, id=user_id)
        attendances = Attendance.objects.filter(user=user).order_by('-date').values(
            'id', 'date', 'status', 'session_name'
        )
        grades = ProjectGrade.objects.filter(user=user).order_by('-session_date').values(
            'id', 'project_name', 'grade', 'session_date', 'xp_earned'
        )
        return JsonResponse({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'xp': user.xp,
                'rank': user.rank,
                'max_xp': user.max_xp,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            },
            'attendances': list(attendances),
            'grades': list(grades),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def save_custom_game(request):
    """Save a custom mini-game to a specific slot for the logged-in user (dynamic slots).
    Supports is_public flag for community sharing."""
    try:
        data = json.loads(request.body)
        slot_number = int(data.get('slot_number', 1))
        if slot_number < 1:
            return JsonResponse({'status': 'error', 'message': 'Номер слота должен быть положительным числом.'}, status=400)

        title = data.get('title', 'Моя игра')
        html_code = data.get('html_code', '')
        css_code = data.get('css_code', '')
        js_code = data.get('js_code', '')
        is_public = bool(data.get('is_public', False))

        game, created = CustomMiniGame.objects.update_or_create(
            user=request.user,
            slot_number=slot_number,
            defaults={
                'title': title,
                'html_code': html_code,
                'css_code': css_code,
                'js_code': js_code,
                'is_public': is_public,
            }
        )

        visibility = 'публичная' if is_public else 'частная'
        return JsonResponse({
            'status': 'ok',
            'message': f'Игра "{title}" сохранена в слот {slot_number}! ({visibility})',
            'slot_number': slot_number,
            'is_public': is_public,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def load_custom_games(request):
    """Return all saved custom mini-game slots for the current user as JSON."""
    try:
        games = CustomMiniGame.objects.filter(user=request.user).order_by('slot_number')
        slots = {}
        for game in games:
            slots[str(game.slot_number)] = {
                'slot_number': game.slot_number,
                'title': game.title,
                'html_code': game.html_code,
                'css_code': game.css_code,
                'js_code': game.js_code,
                'is_public': game.is_public,
                'updated_at': game.updated_at.isoformat(),
            }
        return JsonResponse({'status': 'ok', 'slots': slots})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def load_custom_game_slot(request):
    """Load a specific slot's code into the editor via AJAX (dynamic slots)."""
    try:
        data = json.loads(request.body)
        slot_number = int(data.get('slot_number', 1))
        if slot_number < 1:
            return JsonResponse({'status': 'error', 'message': 'Неверный номер слота.'}, status=400)

        game = CustomMiniGame.objects.filter(user=request.user, slot_number=slot_number).first()
        if not game:
            return JsonResponse({'status': 'empty', 'message': f'Слот {slot_number} пуст.'})

        return JsonResponse({
            'status': 'ok',
            'slot_number': game.slot_number,
            'title': game.title,
            'html_code': game.html_code,
            'css_code': game.css_code,
            'js_code': game.js_code,
            'is_public': game.is_public,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def submit_feedback(request):
    """Submit a new feedback entry via AJAX."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
        if not text:
            return JsonResponse({'status': 'error', 'message': 'Текст отзыва не может быть пустым.'}, status=400)

        feedback = Feedback.objects.create(user=request.user, text=text)
        return JsonResponse({
            'status': 'ok',
            'message': 'Отзыв успешно отправлен!',
            'id': feedback.id,
            'user_name': request.user.get_full_name() or request.user.username,
            'text': text,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def get_feedback_replies(request):
    """Get admin replies for the current user's feedback items."""
    try:
        feedbacks = Feedback.objects.filter(
            user=request.user
        ).exclude(admin_reply='').exclude(admin_reply__isnull=True).order_by('-replied_at')

        replies = []
        for fb in feedbacks:
            replies.append({
                'id': fb.id,
                'feedback_text': fb.text[:100],
                'admin_reply': fb.admin_reply,
                'replied_at': fb.replied_at.isoformat() if fb.replied_at else None,
            })

        return JsonResponse({
            'status': 'ok',
            'count': len(replies),
            'replies': replies,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def join_project_initiative(request):
    """Join a project initiative via AJAX."""
    try:
        data = json.loads(request.body)
        initiative_id = data.get('initiative_id')
        initiative = get_object_or_404(ProjectInitiative, id=initiative_id)

        # Check if already a member
        if ProjectInitiativeMember.objects.filter(initiative=initiative, user=request.user).exists():
            return JsonResponse({'status': 'error', 'message': 'Вы уже участвуете в этом проекте.'}, status=400)

        # Check if full
        if initiative.current_members >= initiative.max_members:
            return JsonResponse({'status': 'error', 'message': 'В проекте нет свободных мест.'}, status=400)

        # Add membership
        ProjectInitiativeMember.objects.create(initiative=initiative, user=request.user)
        initiative.current_members += 1
        initiative.save(update_fields=['current_members'])

        return JsonResponse({
            'status': 'ok',
            'message': f'Вы присоединились к проекту "{initiative.title}"!',
            'current_members': initiative.current_members,
            'max_members': initiative.max_members,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def create_project_initiative(request):
    """Create a new project initiative via AJAX."""
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        max_members = int(data.get('max_members', 10))
        sections_data = data.get('sections', [])

        if not title:
            return JsonResponse({'status': 'error', 'message': 'Название проекта не может быть пустым.'}, status=400)

        initiative = ProjectInitiative.objects.create(
            user=request.user,
            title=title,
            description=description,
            current_members=1,
            max_members=max_members,
        )

        # Create sections
        for index, s in enumerate(sections_data):
            s_title = s.get('title', '').strip()
            s_content = s.get('content', '').strip()
            if s_title and s_content:
                InitiativeSection.objects.create(
                    initiative=initiative,
                    title=s_title,
                    content=s_content,
                    order=index
                )

        return JsonResponse({
            'status': 'ok',
            'message': f'Проект "{title}" успешно создан!',
            'id': initiative.id,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def add_calendar_task(request):
    """Add a new custom task to the user's calendar."""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        task_date = data.get('date')
        description = data.get('description', '')

        if not title or not task_date:
            return JsonResponse({'status': 'error', 'message': 'Название и дата обязательны.'}, status=400)

        CalendarTask.objects.create(
            user=request.user,
            title=title,
            date=task_date,
            description=description
        )
        return JsonResponse({'status': 'ok', 'message': 'Задача успешно добавлена!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def calendar_events(request):
    """Return calendar events (attendance, homework deadlines, project grades) for a given month/year as JSON."""
    try:
        year = int(request.GET.get('year', 0))
        month = int(request.GET.get('month', 0))  # 1-based month

        if not year or not month or month < 1 or month > 12:
            return JsonResponse({'status': 'error', 'message': 'Неверные параметры даты.'}, status=400)

        # Date range for the selected month
        from datetime import date as date_obj
        month_start = date_obj(year, month, 1)
        if month == 12:
            month_end = date_obj(year + 1, 1, 1)
        else:
            month_end = date_obj(year, month + 1, 1)

        events = []

        # 1. Attendance records for this month
        attendances = Attendance.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lt=month_end
        ).order_by('date')

        for att in attendances:
            events.append({
                'date': att.date.isoformat(),
                'type': 'attendance',
                'status': att.status,  # 'present', 'late', 'absent'
                'title': att.session_name or 'Занятие',
            })

        # 2. Homework deadlines for this month
        homeworks = Homework.objects.filter(
            user=request.user,
            deadline__gte=month_start,
            deadline__lt=month_end
        ).order_by('deadline')

        for hw in homeworks:
            events.append({
                'date': hw.deadline.date().isoformat(),
                'type': 'homework',
                'title': hw.title,
                'status': hw.status,  # 'checking', 'graded', 'process'
                'grade': hw.grade,
            })

        # 3. Project grades (session dates) for this month
        grades = ProjectGrade.objects.filter(
            user=request.user,
            session_date__gte=month_start,
            session_date__lt=month_end
        ).order_by('session_date')

        for g in grades:
            events.append({
                'date': g.session_date.isoformat(),
                'type': 'grade',
                'title': g.project_name,
                'grade': g.grade,
                'xp_earned': g.xp_earned,
            })

        # 4. Custom Calendar Tasks for this month
        tasks = CalendarTask.objects.filter(
            user=request.user,
            date__gte=month_start,
            date__lt=month_end
        ).order_by('date')

        for task in tasks:
            events.append({
                'date': task.date.isoformat(),
                'type': 'custom_task',
                'title': task.title,
                'description': task.description,
            })

        return JsonResponse({'status': 'ok', 'events': events})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def support_chat_view(request):
    """Render the support chat page for users to contact the developer."""
    return render(request, 'support_chat.html', {'user': request.user})


import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from google_drive import upload_file_to_drive


@login_required
@require_POST
def ask_question(request):
    """API endpoint to submit a new question."""
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')

        if not title or not content:
            return JsonResponse({'status': 'error', 'message': 'Title and content are required'}, status=400)

        question = DiscussionQuestion.objects.create(
            user=request.user,
            title=title,
            content=content
        )
        return JsonResponse({
            'status': 'ok',
            'question': {
                'id': question.id,
                'title': question.title,
                'content': question.content,
                'user': question.user.get_full_name() or question.user.username,
                'created_at': question.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def answer_question(request):
    """API endpoint to submit an answer to a question.
    Staff/teacher answers are automatically marked as official (pinned at top)."""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        content = data.get('answer_text')

        if not question_id or not content:
            return JsonResponse({'status': 'error', 'message': 'Question ID and answer text are required'}, status=400)

        question = DiscussionQuestion.objects.get(id=question_id)
        answer = DiscussionAnswer.objects.create(
            question=question,
            user=request.user,
            content=content,
            is_official=request.user.is_staff
        )
        return JsonResponse({
            'status': 'ok',
            'answer': {
                'id': answer.id,
                'content': answer.content,
                'user': answer.user.get_full_name() or answer.user.username,
                'is_official': answer.is_official,
                'created_at': answer.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })
    except DiscussionQuestion.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@staff_member_required
def admin_get_all_feedback(request):
    """Return all feedback entries for the admin inbox as JSON.
    NOTE: This endpoint queries ONLY the Feedback model (support chat messages).
    Q&A items (DiscussionQuestion/DiscussionAnswer) are intentionally excluded
    and belong to the dashboard 'Вопросы и ответы' section, not this inbox."""
    try:
        feedbacks = Feedback.objects.all().select_related('user').order_by('-created_at')
        items = []
        for fb in feedbacks:
            items.append({
                'id': fb.id,
                'user_id': fb.user.id,
                'user_name': fb.user.get_full_name() or fb.user.username,
                'user_email': fb.user.email,
                'text': fb.text,
                'admin_reply': fb.admin_reply,
                'replied_at': fb.replied_at.isoformat() if fb.replied_at else None,
                'created_at': fb.created_at.isoformat(),
                'has_reply': bool(fb.admin_reply),
            })
        return JsonResponse({'status': 'ok', 'count': len(items), 'feedbacks': items})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@staff_member_required
@require_POST
def admin_reply_to_feedback(request):
    """Admin replies to a feedback entry. Updates admin_reply and replied_at."""
    try:
        data = json.loads(request.body)
        feedback_id = data.get('feedback_id')
        reply_text = data.get('reply_text', '').strip()

        if not feedback_id:
            return JsonResponse({'status': 'error', 'message': 'feedback_id is required.'}, status=400)

        feedback = get_object_or_404(Feedback, id=feedback_id)

        if reply_text:
            feedback.admin_reply = reply_text
            feedback.replied_at = timezone.now()
            feedback.save(update_fields=['admin_reply', 'replied_at'])
            return JsonResponse({
                'status': 'ok',
                'message': f'Ответ отправлен пользователю {feedback.user.get_full_name() or feedback.user.username}!',
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Текст ответа не может быть пустым.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def upload_view(request):
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        uploaded_file = request.FILES['pdf_file']

        # Загружаем на Google Диск
        drive_res = upload_file_to_drive(
            file_obj=uploaded_file,
            filename=uploaded_file.name,
            mime_type=uploaded_file.content_type
        )

        # Сохраняем информацию в базу данных Django
        UserDocument.objects.create(
            title=uploaded_file.name,
            file_id=drive_res.get('id'),
            file_url=drive_res.get('webViewLink')
        )

        return redirect('success_url')

    return render(request, 'upload_template.html')


# =============================================================================
# Cursor Style API Endpoints
# =============================================================================

@login_required
@require_POST
def save_cursor_style(request):
    """Save a custom cursor CSS style for the logged-in user."""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        css_code = data.get('css_code', '').strip()
        is_public = bool(data.get('is_public', False))

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Название курсора не может быть пустым.'}, status=400)
        if not css_code:
            return JsonResponse({'status': 'error', 'message': 'CSS-код не может быть пустым.'}, status=400)

        cursor = CursorStyle.objects.create(
            user=request.user,
            name=name,
            css_code=css_code,
            is_public=is_public,
        )
        return JsonResponse({
            'status': 'ok',
            'message': f'Курсор "{name}" сохранён!',
            'id': cursor.id,
            'is_public': is_public,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def get_my_cursor_styles(request):
    """Return all cursor styles created by the current user."""
    try:
        cursors = CursorStyle.objects.filter(user=request.user).order_by('-created_at')
        items = []
        for c in cursors:
            items.append({
                'id': c.id,
                'name': c.name,
                'css_code': c.css_code,
                'is_public': c.is_public,
                'created_at': c.created_at.isoformat(),
            })
        return JsonResponse({'status': 'ok', 'count': len(items), 'cursors': items})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def get_public_cursor_styles(request):
    """Return all publicly shared cursor styles from the community."""
    try:
        cursors = CursorStyle.objects.filter(is_public=True).select_related('user').order_by('-created_at')
        items = []
        for c in cursors:
            items.append({
                'id': c.id,
                'name': c.name,
                'css_code': c.css_code,
                'creator': c.user.get_full_name() or c.user.username,
                'created_at': c.created_at.isoformat(),
            })
        return JsonResponse({'status': 'ok', 'count': len(items), 'cursors': items})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def apply_cursor_style(request):
    """Apply a cursor style (own or from community) — saves a copy to user's styles."""
    try:
        data = json.loads(request.body)
        cursor_id = data.get('cursor_id')

        if not cursor_id:
            return JsonResponse({'status': 'error', 'message': 'ID курсора не указан.'}, status=400)

        cursor = get_object_or_404(CursorStyle, id=cursor_id)
        # Save a copy to the user's styles so they can edit it
        user_cursor = CursorStyle.objects.create(
            user=request.user,
            name=f"{cursor.name} (копия)",
            css_code=cursor.css_code,
            is_public=False,
        )
        return JsonResponse({
            'status': 'ok',
            'message': f'Курсор "{cursor.name}" применён!',
            'id': user_cursor.id,
            'css_code': user_cursor.css_code,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def delete_cursor_style(request):
    """Delete a cursor style owned by the current user."""
    try:
        data = json.loads(request.body)
        cursor_id = data.get('cursor_id')

        if not cursor_id:
            return JsonResponse({'status': 'error', 'message': 'ID курсора не указан.'}, status=400)

        cursor = get_object_or_404(CursorStyle, id=cursor_id, user=request.user)
        cursor.delete()
        return JsonResponse({'status': 'ok', 'message': 'Курсор удалён!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# =============================================================================
# Public Mini-Games Gallery Endpoints
# =============================================================================

@login_required
def get_public_games(request):
    """Return all publicly shared mini-games from the community."""
    try:
        games = CustomMiniGame.objects.filter(is_public=True).select_related('user').order_by('-created_at')
        items = []
        for g in games:
            items.append({
                'id': g.id,
                'slot_number': g.slot_number,
                'title': g.title,
                'html_code': g.html_code,
                'css_code': g.css_code,
                'js_code': g.js_code,
                'creator': g.user.get_full_name() or g.user.username,
                'created_at': g.created_at.isoformat(),
            })
        return JsonResponse({'status': 'ok', 'count': len(items), 'games': items})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def load_public_game(request):
    """Load a public community game into the editor for playing/editing."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')

        if not game_id:
            return JsonResponse({'status': 'error', 'message': 'ID игры не указан.'}, status=400)

        game = get_object_or_404(CustomMiniGame, id=game_id, is_public=True)
        return JsonResponse({
            'status': 'ok',
            'title': game.title,
            'html_code': game.html_code,
            'css_code': game.css_code,
            'js_code': game.js_code,
            'creator': game.user.get_full_name() or game.user.username,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)