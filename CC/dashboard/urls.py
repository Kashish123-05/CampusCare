from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('maintenance/', views.maintenance_dashboard, name='maintenance_dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('export/', views.export_reports, name='export_reports'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/notifications/read/', views.mark_notification_read, name='mark_notification_read'),
]
