from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """Decorator for role-based access control."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('accounts:profile_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def student_required(view_func):
    return login_required(role_required('student')(view_func))


def admin_required(view_func):
    return login_required(role_required('admin')(view_func))


def maintenance_required(view_func):
    return login_required(role_required('maintenance')(view_func))
