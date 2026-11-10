"""
URL configuration for App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    # Admin panel AJAX endpoints
    path('admin-panel/update-user/', views.admin_update_user, name='admin_update_user'),
    path('admin-panel/update-attendance/', views.admin_update_attendance, name='admin_update_attendance'),
    path('admin-panel/delete-attendance/', views.admin_delete_attendance, name='admin_delete_attendance'),
    path('admin-panel/update-grade/', views.admin_update_grade, name='admin_update_grade'),
    path('admin-panel/delete-grade/', views.admin_delete_grade, name='admin_delete_grade'),
    path('admin-panel/user/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    # Custom mini-game save/load endpoints
    path('save-custom-game/', views.save_custom_game, name='save_custom_game'),
    path('load-custom-games/', views.load_custom_games, name='load_custom_games'),
    path('load-custom-game-slot/', views.load_custom_game_slot, name='load_custom_game_slot'),
    # Feedback endpoints
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('get-feedback-replies/', views.get_feedback_replies, name='get_feedback_replies'),
    # Project initiative endpoints
    path('join-project/', views.join_project_initiative, name='join_project_initiative'),
    path('create-project/', views.create_project_initiative, name='create_project_initiative'),
    # Support chat
    path('support-chat/', views.support_chat_view, name='support_chat'),
    # Calendar events API
    path('calendar-events/', views.calendar_events, name='calendar_events'),
    path('api/calendar/add/', views.add_calendar_task, name='add_calendar_task'),
    path('api/qa/ask/', views.ask_question, name='ask_question'),
    path('api/qa/answer/', views.answer_question, name='answer_question'),
    # Admin feedback endpoints
    path('admin-panel/get-feedback/', views.admin_get_all_feedback, name='admin_get_all_feedback'),
    path('admin-panel/reply-feedback/', views.admin_reply_to_feedback, name='admin_reply_to_feedback'),
    # Cursor style endpoints
    path('save-cursor-style/', views.save_cursor_style, name='save_cursor_style'),
    path('my-cursor-styles/', views.get_my_cursor_styles, name='get_my_cursor_styles'),
    path('public-cursor-styles/', views.get_public_cursor_styles, name='get_public_cursor_styles'),
    path('apply-cursor-style/', views.apply_cursor_style, name='apply_cursor_style'),
    path('delete-cursor-style/', views.delete_cursor_style, name='delete_cursor_style'),
    # Public mini-games gallery endpoints
    path('public-games/', views.get_public_games, name='get_public_games'),
    path('load-public-game/', views.load_public_game, name='load_public_game'),
]
