from django.contrib import admin
from .models import Issue, IssueHistory


class IssueHistoryInline(admin.TabularInline):
    model = IssueHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'notes', 'created_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'priority', 'status', 'reported_by', 'assigned_to', 'created_at']
    list_filter = ['category', 'priority', 'status', 'created_at']
    search_fields = ['title', 'description', 'location_building', 'location_room']
    inlines = [IssueHistoryInline]
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']


@admin.register(IssueHistory)
class IssueHistoryAdmin(admin.ModelAdmin):
    list_display = ['issue', 'old_status', 'new_status', 'changed_by', 'created_at']
