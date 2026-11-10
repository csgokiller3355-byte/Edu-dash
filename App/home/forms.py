from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Form for creating a new user account."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'E-mail*'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Имя*'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Фамилия*'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Логин*'
        })
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Пароль*'
        })
    )
    password2 = forms.CharField(
        label='Подтвердите пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Подтвердите пароль*'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class LoginForm(forms.Form):
    """Form for user login."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'E-mail или Логин*'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'passwordField',
            'class': 'form-input w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 text-sm focus:outline-none',
            'placeholder': 'Пароль*'
        })
    )
