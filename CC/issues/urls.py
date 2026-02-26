from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('create/', views.issue_create, name='issue_create'),
    path('<int:pk>/', views.issue_detail, name='issue_detail'),
    path('<int:pk>/assign/', views.issue_assign, name='issue_assign'),
    path('<int:pk>/update-status/', views.issue_update_status, name='issue_update_status'),
]
