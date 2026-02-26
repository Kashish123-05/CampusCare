from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .decorators import login_required, student_required, admin_required, maintenance_required
from .models import UserActivity
from issues.models import Issue
from dashboard.models import Notification


def home(request):
    """Public home page."""
    return render(request, 'home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile_redirect')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserActivity.objects.create(user=user, action='registration', details='User registered')
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('accounts:profile_redirect')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        UserActivity.objects.create(
            user=user,
            action='login',
            details='User logged in',
            ip_address=self.get_client_ip()
        )
        return super().form_valid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')


def logout_view(request):
    if request.user.is_authenticated:
        UserActivity.objects.create(user=request.user, action='logout', details='User logged out')
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:home')


@login_required
def profile_redirect(request):
    """Redirect user to appropriate dashboard based on role."""
    if request.user.role == 'admin':
        return redirect('dashboard:admin_dashboard')
    elif request.user.role == 'maintenance':
        return redirect('dashboard:maintenance_dashboard')
    else:
        return redirect('dashboard:student_dashboard')
